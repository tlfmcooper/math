/**
 * Unit tests for AnimationEngine.
 *
 * This file assumes AnimationEngine is already defined in the global scope
 * (load animation-engine.js before this file).
 *
 * Run in browser via: static/tests/animation-engine.test.html
 */

'use strict';

// ── Minimal test runner ───────────────────────────────────────────────────────

(function() {
  let passed = 0;
  let failed = 0;
  const results = [];

  function test(name, fn) {
    try {
      fn();
      passed++;
      results.push({ ok: true, name });
    } catch (e) {
      failed++;
      results.push({ ok: false, name, msg: e.message });
    }
  }

  function assert(cond, msg) {
    if (!cond) throw new Error(msg || 'Assertion failed');
  }

  function assertEqual(a, b, msg) {
    if (a !== b) throw new Error(msg || ('Expected ' + JSON.stringify(a) + ' === ' + JSON.stringify(b)));
  }

  // ── DOM helpers ─────────────────────────────────────────────────────────────

  function makeEl() {
    return document.createElement('div');
  }

  function makeEngine() {
    return new AnimationEngine(makeEl(), makeEl(), makeEl(), makeEl());
  }

  function makeScript(stepCount) {
    stepCount = stepCount || 1;
    const steps = [];
    for (let i = 0; i < stepCount; i++) {
      steps.push({
        id: i + 1,
        objects: [{ emoji: '\uD83C\uDF4E', label: 'apple' }],
        action: 'appear',
        narration: 'here is an apple',
        sound: 'pop',
        duration_ms: 100
      });
    }
    return { grammar: 'grouping', steps: steps };
  }

  // ── Tests ───────────────────────────────────────────────────────────────────

  test('play() with empty steps returns false', function() {
    const engine = makeEngine();
    assertEqual(engine.play({ grammar: 'grouping', steps: [] }), false);
  });

  test('play() with null returns false', function() {
    const engine = makeEngine();
    assertEqual(engine.play(null), false);
  });

  test('play() with missing steps returns false', function() {
    const engine = makeEngine();
    assertEqual(engine.play({ grammar: 'grouping' }), false);
  });

  test('play() with valid steps returns true', function() {
    const engine = makeEngine();
    const result = engine.play(makeScript(1));
    engine.cancel();
    assertEqual(result, true);
  });

  test('cancel() clears all pending timeouts', function() {
    const engine = makeEngine();
    engine.play(makeScript(3));
    assert(engine._timeouts.length > 0, 'timeouts should be queued after play');
    engine.cancel();
    assertEqual(engine._timeouts.length, 0, 'all timeouts cleared after cancel');
  });

  test('cancel() before play() is safe', function() {
    const engine = makeEngine();
    engine.cancel(); // should not throw
    assertEqual(engine._timeouts.length, 0);
  });

  test('replay() uses the previously played script', function() {
    const engine = makeEngine();
    const script = makeScript(1);
    engine.play(script);
    engine.cancel();
    engine.replay();
    assert(engine._script === script, 'replay uses stored _script');
    engine.cancel();
  });

  test('setSpeed() updates internal multiplier', function() {
    const engine = makeEngine();
    engine.setSpeed(0.4);
    assertEqual(engine._speed, 0.4);
    engine.setSpeed(1.0);
    assertEqual(engine._speed, 1.0);
  });

  test('play() shows stage (removes hidden class)', function() {
    const engine = makeEngine();
    engine._stage.classList.add('hidden');
    engine.play(makeScript(1));
    assert(!engine._stage.classList.contains('hidden'), 'stage should be visible');
    engine.cancel();
  });

  test('play() hides toolbar while playing', function() {
    const engine = makeEngine();
    engine._toolbar.classList.remove('hidden');
    engine.play(makeScript(1));
    assert(engine._toolbar.classList.contains('hidden'), 'toolbar hidden during play');
    engine.cancel();
  });

  test('showLoading() reveals stage', function() {
    const engine = makeEngine();
    engine._stage.classList.add('hidden');
    engine.showLoading();
    assert(!engine._stage.classList.contains('hidden'), 'stage visible after showLoading');
  });

  test('showLoading() appends a phrase element', function() {
    const engine = makeEngine();
    engine.showLoading();
    assert(engine._objects.childElementCount > 0, 'loading phrase appended');
  });

  test('null step guard — null steps are skipped without error', function() {
    const engine = makeEngine();
    const script = {
      grammar: 'grouping',
      steps: [
        null,
        { id: 2, objects: [{ emoji: '\uD83C\uDF4E', label: 'apple' }], action: 'appear', narration: 'hi', sound: 'pop', duration_ms: 100 }
      ]
    };
    const result = engine.play(script);
    engine.cancel();
    assertEqual(result, true, 'play returns true even when some steps are null');
  });

  test('play() then cancel() then play() again works cleanly', function() {
    const engine = makeEngine();
    engine.play(makeScript(2));
    engine.cancel();
    assertEqual(engine._timeouts.length, 0, 'clean after first cancel');
    const result = engine.play(makeScript(1));
    engine.cancel();
    assertEqual(result, true, 'second play succeeds');
  });

  // ── Report ──────────────────────────────────────────────────────────────────

  window.__animTestResults = { passed: passed, failed: failed, results: results };

  if (typeof document !== 'undefined') {
    const out = document.getElementById('test-output');
    if (out) {
      results.forEach(function(r) {
        const li = document.createElement('li');
        li.textContent = (r.ok ? '\u2713 ' : '\u2717 ') + r.name + (r.msg ? ': ' + r.msg : '');
        li.style.color = r.ok ? '#2ecc71' : '#e74c3c';
        li.style.fontFamily = 'monospace';
        li.style.padding = '2px 0';
        out.appendChild(li);
      });
      const summary = document.createElement('p');
      summary.textContent = passed + ' passed, ' + failed + ' failed';
      summary.style.fontWeight = 'bold';
      summary.style.color = failed > 0 ? '#e74c3c' : '#2ecc71';
      out.parentElement.appendChild(summary);
    }
  }

  console.log('AnimationEngine tests: ' + passed + ' passed, ' + failed + ' failed');
  results.filter(function(r) { return !r.ok; }).forEach(function(r) {
    console.error('  FAIL:', r.name, '-', r.msg);
  });
})();
