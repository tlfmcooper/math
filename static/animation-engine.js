/**
 * AnimationEngine — renders Gemini-authored AnimationScript objects as
 * interactive DOM animations for Grade 1 math learners.
 *
 * Usage:
 *   const engine = new AnimationEngine(stageEl, objectsEl, toolbarEl, mascotEl);
 *   engine.play(animationScript);
 *
 * Security: all user-visible text is set via textContent (never innerHTML).
 */

'use strict';

// ── Constants ────────────────────────────────────────────────────────────────

const LOADING_PHRASES = [
  'Let me show you! \u2728',
  'Watch this! \uD83C\uDF1F',
  "Here's a magic trick! \uD83C\uDFA9",
  "I'll draw it out! \uD83C\uDFA8",
  "Let's count together! \uD83E\uDD1D",
  'I know just what to do! \uD83D\uDCA1'
];

const GRAMMAR_EMOJI = {
  ten_frame:   '\uD83D\uDFE6',
  number_line: '\uD83D\uDC38',
  grouping:    '\uD83C\uDF4E',
  removal:     '\uD83C\uDF4E',
  coins:       '\uD83E\uDE99',
  hops:        '\uD83D\uDC38',
  show:        '\u2B50'
};

// Rotating stroke colors for draw-along canvas
const DRAW_COLORS = ['#3498db', '#2ecc71', '#e67e22', '#9b59b6', '#ec4899'];

// Confetti colors
const CONFETTI_COLORS = ['#f1c40f', '#3498db', '#2ecc71', '#ec4899', '#e67e22'];

// ── Audio (lazy Web Audio API) ───────────────────────────────────────────────

let _audioCtx = null;

function _getAudioCtx() {
  if (!_audioCtx) {
    try {
      _audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    } catch (_) {
      return null;
    }
  }
  return _audioCtx;
}

/**
 * Initialize the AudioContext on a user gesture (call from mood/start button).
 * Must be called from within a user-gesture handler.
 */
function initAudio() {
  _getAudioCtx();
}

/**
 * Play a synthesized tone.
 * @param {'pop'|'whoosh'|'ding'} type
 */
function playTone(type) {
  if (window.animSoundEnabled === false) return;
  const ctx = _getAudioCtx();
  if (!ctx) return;

  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.connect(gain);
  gain.connect(ctx.destination);

  const now = ctx.currentTime;

  if (type === 'pop') {
    osc.type = 'sine';
    osc.frequency.setValueAtTime(600, now);
    osc.frequency.exponentialRampToValueAtTime(200, now + 0.12);
    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
    osc.start(now);
    osc.stop(now + 0.15);
  } else if (type === 'whoosh') {
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(300, now);
    osc.frequency.exponentialRampToValueAtTime(80, now + 0.25);
    gain.gain.setValueAtTime(0.15, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
    osc.start(now);
    osc.stop(now + 0.28);
  } else if (type === 'ding') {
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, now);
    osc.frequency.setValueAtTime(1100, now + 0.05);
    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
    osc.start(now);
    osc.stop(now + 0.6);
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function _randomFrom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function _speakText(text) {
  if (!('speechSynthesis' in window)) return;
  if (window.animSoundEnabled === false) return;
  window.speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(text);
  utt.rate = 0.9;
  utt.pitch = 1.1;
  window.speechSynthesis.speak(utt);
}

// ── AnimationEngine ───────────────────────────────────────────────────────────

class AnimationEngine {
  /**
   * @param {HTMLElement} stageEl     - #animation-stage
   * @param {HTMLElement} objectsEl   - #animation-objects (inside stage)
   * @param {HTMLElement} toolbarEl   - #animation-toolbar
   * @param {HTMLElement} mascotEl    - the mascot element (for choreography)
   */
  constructor(stageEl, objectsEl, toolbarEl, mascotEl) {
    this._stage    = stageEl;
    this._objects  = objectsEl;
    this._toolbar  = toolbarEl;
    this._mascot   = mascotEl;
    this._timeouts = [];
    this._script   = null;
    this._speed    = 1.0;  // 1.0 = normal, 0.4 = slow
    this._drawCanvas = null;
  }

  // ── Public API ─────────────────────────────────────────────────────────────

  /**
   * Play an AnimationScript. Returns false if the script has no steps
   * (caller should fall back to legacy renderAnimation).
   * @param {Object} script  AnimationScript from Gemini
   * @returns {boolean}
   */
  play(script) {
    if (!script || !Array.isArray(script.steps) || script.steps.length === 0) {
      return false;
    }

    this.cancel();
    this._script = script;

    this._showStage();
    this._objects.textContent = '';
    this._stage.classList.remove('stage-complete');
    this._stage.classList.add('stage-playing');
    this._toolbar.classList.add('hidden');

    this._choreographMascotStart();

    let delay = 0;
    script.steps.forEach((step, i) => {
      if (!step || !Array.isArray(step.objects)) return; // null guard

      const stepDuration = (step.duration_ms || 800) / this._speed;
      const id = setTimeout(() => this._renderStep(step, i, script.steps.length), delay);
      this._timeouts.push(id);
      delay += stepDuration + 120; // brief gap between steps
    });

    // onComplete
    const completeId = setTimeout(() => this._onComplete(), delay);
    this._timeouts.push(completeId);

    return true;
  }

  /** Cancel any in-progress animation, clearing all pending timeouts. */
  cancel() {
    this._timeouts.forEach(id => clearTimeout(id));
    this._timeouts = [];
    if (this._drawCanvas) {
      this._drawCanvas.destroy();
      this._drawCanvas = null;
    }
    window.speechSynthesis && window.speechSynthesis.cancel();
  }

  /** Replay the last animation from the beginning. */
  replay() {
    if (this._script) {
      this.play(this._script);
    }
  }

  /** Toggle slow-motion (0.4x) vs normal (1.0x) speed. */
  setSpeed(multiplier) {
    this._speed = multiplier;
  }

  /** Show a loading/thinking state in the animation stage. */
  showLoading() {
    this._showStage();
    this._objects.textContent = '';
    this._toolbar.classList.add('hidden');
    this._stage.classList.remove('stage-complete', 'stage-playing');

    const phrase = _randomFrom(LOADING_PHRASES);
    const loader = document.createElement('div');
    loader.className = 'anim-loading-phrase';
    loader.textContent = phrase;
    this._objects.appendChild(loader);
  }

  /** Show the draw-along canvas overlay. */
  showDrawCanvas() {
    const wrapper = this._stage.querySelector('#draw-canvas-wrapper');
    if (!wrapper) return;
    wrapper.classList.remove('hidden');
    if (!this._drawCanvas) {
      const canvas = wrapper.querySelector('#draw-canvas');
      this._drawCanvas = new DrawAlongCanvas(canvas);
    }
  }

  // ── Private ────────────────────────────────────────────────────────────────

  _showStage() {
    this._stage.classList.remove('hidden');
  }

  /**
   * Render one animation step.
   * @param {Object} step
   * @param {number} index     - 0-based step index
   * @param {number} total     - total step count
   */
  _renderStep(step, index, total) {
    playTone(step.sound || 'pop');

    if (step.narration) {
      _speakText(step.narration);
    }

    const isLastStep = index === total - 1;
    const isReveal   = step.action === 'reveal';

    if (isReveal || isLastStep) {
      this._renderReveal(step);
    } else if (step.action === 'merge') {
      this._renderMerge(step);
    } else if (step.action === 'cross_out') {
      this._renderCrossOut(step);
    } else {
      this._renderObjects(step);
    }
  }

  _renderObjects(step) {
    const isFlyIn  = step.action === 'fly_in';
    const isHop    = step.action === 'hop';
    const isFill   = step.action === 'fill';

    step.objects.forEach((obj, i) => {
      if (!obj) return; // null object guard

      const delay = i * (100 / this._speed);
      const id = setTimeout(() => {
        const el = this._createObjectEl(obj, i + 1);
        if (isFlyIn) {
          el.classList.add('anim-fly-in');
        } else {
          el.classList.add('anim-pop-in');
        }
        this._objects.appendChild(el);
        playTone('pop');
      }, delay);
      this._timeouts.push(id);
    });
  }

  _renderMerge(step) {
    this._objects.textContent = '';
    this._renderObjects(step);
  }

  _renderCrossOut(step) {
    this._renderObjects(step);
    const crossDelay = (step.objects.length * 100 + 200) / this._speed;
    const id = setTimeout(() => {
      const els = this._objects.querySelectorAll('.anim-object');
      els.forEach((el, i) => {
        const cId = setTimeout(() => el.classList.add('crossed-out'), i * (80 / this._speed));
        this._timeouts.push(cId);
      });
    }, crossDelay);
    this._timeouts.push(id);
  }

  _renderReveal(step) {
    playTone('ding');

    const count = step.objects ? step.objects.length : 0;

    const revealEl = document.createElement('div');
    revealEl.className = 'anim-reveal-number';
    revealEl.textContent = count > 0 ? String(count) : (step.narration || '');

    this._objects.textContent = '';
    this._objects.appendChild(revealEl);

    this._stage.classList.remove('stage-playing');
    this._stage.classList.add('stage-complete');

    this._spawnConfetti();
  }

  _createObjectEl(obj, countNum) {
    const el = document.createElement('div');
    el.className = 'anim-object';
    el.setAttribute('aria-label', (obj.label || 'object') + ' number ' + countNum);
    el.setAttribute('role', 'button');
    el.setAttribute('tabindex', '0');

    const emojiSpan = document.createElement('span');
    emojiSpan.textContent = obj.emoji || '\uD83C\uDF4E';
    el.appendChild(emojiSpan);

    // Tap-to-count: speak the position of this object
    const speak = () => {
      if (el.classList.contains('tapped')) return; // debounce
      el.classList.add('tapped');
      playTone('pop');
      _speakText(String(countNum));
      this._showCountLabel(el, countNum);
      setTimeout(() => el.classList.remove('tapped'), 600);
    };
    el.addEventListener('click', speak);
    el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') speak(); });

    return el;
  }

  _showCountLabel(parentEl, num) {
    const existing = parentEl.querySelector('.tap-count-label');
    if (existing) existing.remove();

    const label = document.createElement('span');
    label.className = 'tap-count-label';
    label.textContent = String(num);
    parentEl.appendChild(label);
    setTimeout(() => label.remove(), 900);
  }

  _spawnConfetti() {
    const stageRect = this._stage.getBoundingClientRect();
    const centerX = stageRect.width / 2;

    for (let i = 0; i < 12; i++) {
      const piece = document.createElement('div');
      piece.className = 'confetti-piece';
      piece.style.backgroundColor = _randomFrom(CONFETTI_COLORS);
      piece.style.left = centerX + 'px';
      piece.style.setProperty('--tx', (Math.random() * 120 - 60) + 'px');
      piece.style.setProperty('--rot', (Math.random() * 360) + 'deg');
      this._stage.appendChild(piece);

      piece.addEventListener('animationend', () => piece.remove());
    }
  }

  _onComplete() {
    this._toolbar.classList.remove('hidden');
    this._choreographMascotEnd();
  }

  // ── Mascot choreography (tablet+ only) ────────────────────────────────────

  _choreographMascotStart() {
    if (!this._mascot || window.innerWidth < 480) return;
    this._stage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    const id = setTimeout(() => {
      const stageRect  = this._stage.getBoundingClientRect();
      const mascotRect = this._mascot.getBoundingClientRect();
      const tx = stageRect.left - mascotRect.left - mascotRect.width - 8;
      const ty = stageRect.top  - mascotRect.top;
      this._mascot.style.transition = 'transform 0.5s cubic-bezier(0.28, 0.84, 0.42, 1)';
      this._mascot.style.transform  = 'translate(' + tx + 'px, ' + ty + 'px)';
    }, 300);
    this._timeouts.push(id);
  }

  _choreographMascotEnd() {
    if (!this._mascot) return;
    this._mascot.style.transition = 'transform 0.5s cubic-bezier(0.28, 0.84, 0.42, 1)';
    this._mascot.style.transform  = 'translate(0, 0)';
  }
}

// ── DrawAlongCanvas ───────────────────────────────────────────────────────────

class DrawAlongCanvas {
  /**
   * @param {HTMLCanvasElement} canvas
   */
  constructor(canvas) {
    this._canvas  = canvas;
    this._ctx     = canvas ? canvas.getContext('2d') : null;
    if (!this._ctx) return;

    this._drawing   = false;
    this._colorIdx  = 0;
    this._points    = [];
    this._rafId     = null;

    this._resize();
    this._bindEvents();
    this._startLoop();
  }

  clear() {
    if (!this._ctx) return;
    this._ctx.clearRect(0, 0, this._canvas.width, this._canvas.height);
    this._points = [];
  }

  destroy() {
    if (this._rafId) cancelAnimationFrame(this._rafId);
    this._unbindEvents();
  }

  // ── Private ────────────────────────────────────────────────────────────────

  _resize() {
    const rect = this._canvas.parentElement.getBoundingClientRect();
    this._canvas.width  = rect.width  || 300;
    this._canvas.height = rect.height || 200;
  }

  _startLoop() {
    const draw = () => {
      this._rafId = requestAnimationFrame(draw);
      if (!this._drawing || this._points.length < 2) return;
      const ctx = this._ctx;
      ctx.strokeStyle = DRAW_COLORS[this._colorIdx % DRAW_COLORS.length];
      ctx.lineWidth   = 6;
      ctx.lineCap     = 'round';
      ctx.lineJoin    = 'round';

      ctx.beginPath();
      ctx.moveTo(this._points[0].x, this._points[0].y);
      for (let i = 1; i < this._points.length; i++) {
        ctx.lineTo(this._points[i].x, this._points[i].y);
      }
      ctx.stroke();
    };
    draw();
  }

  _getPos(e) {
    const rect = this._canvas.getBoundingClientRect();
    const src  = e.touches ? e.touches[0] : e;
    return {
      x: src.clientX - rect.left,
      y: src.clientY - rect.top
    };
  }

  _onStart(e) {
    e.preventDefault();
    this._drawing = true;
    this._points  = [this._getPos(e)];
    this._colorIdx++;
  }

  _onMove(e) {
    e.preventDefault();
    if (!this._drawing) return;
    this._points.push(this._getPos(e));
  }

  _onEnd(e) {
    e.preventDefault();
    this._drawing = false;
    this._points  = [];
  }

  _bindEvents() {
    const c = this._canvas;
    this._handlers = {
      mousedown:  this._onStart.bind(this),
      mousemove:  this._onMove.bind(this),
      mouseup:    this._onEnd.bind(this),
      touchstart: this._onStart.bind(this),
      touchmove:  this._onMove.bind(this),
      touchend:   this._onEnd.bind(this),
    };
    Object.entries(this._handlers).forEach(([evt, fn]) =>
      c.addEventListener(evt, fn, { passive: false })
    );
  }

  _unbindEvents() {
    if (!this._handlers) return;
    Object.entries(this._handlers).forEach(([evt, fn]) =>
      this._canvas.removeEventListener(evt, fn)
    );
  }
}

// ── Exports ───────────────────────────────────────────────────────────────────

window.AnimationEngine  = AnimationEngine;
window.DrawAlongCanvas  = DrawAlongCanvas;
window.playTone         = playTone;
window.initAudio        = initAudio;
