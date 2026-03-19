# Design System — Grade 1 Math Adventure

Last updated: 2026-03-18

## Philosophy

This is a **Grade 1 learning app**. Every design decision serves one goal: a 6-year-old who can barely read should feel confident, delighted, and capable. Design for:
- **Touch-first** — big targets, forgiving interactions
- **Motion as meaning** — animation explains concepts, not just decorates
- **Warmth over polish** — rounded, colorful, friendly. Not sterile.
- **Zero anxiety** — wrong answers are growth moments, not failures

---

## Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| Primary | Nunito | 700–800 | varies |
| Body | Nunito | 400–600 | 1.1rem |
| Labels/counts | Nunito | 800 | varies |
| Fallback | 'Segoe UI', Tahoma, sans-serif | — | — |

**Rule:** Never use system fonts for user-visible UI. Nunito's rounded letterforms are essential to the warm, kid-friendly aesthetic.

---

## Color Tokens

```css
--primary-blue:   #3498db   /* primary actions, links */
--primary-green:  #2ecc71   /* success, correct */
--primary-orange: #e67e22   /* warnings, attention */
--primary-purple: #9b59b6   /* brand, badges */
--primary-gold:   #f1c40f   /* streaks, rewards, reveal moments */
--primary-pink:   #ec4899
--primary-teal:   #14b8a6
--primary-indigo: #6366f1
--bg-light:       #f0f8ff   /* animation stage background */
--bg-white:       #ffffff
--text-dark:      #333
--text-light:     #666
```

**Gradient pattern:** All cards and buttons use `linear-gradient(135deg, lighter, darker)`.
**Wrong answer:** `#e74c3c` (brief flash only — never a persistent "wrong" label).

---

## Spacing & Shape

| Token | Value |
|-------|-------|
| `--radius` | 16px (cards, stages, containers) |
| `--radius-small` | 10px (buttons, badges) |
| `--shadow` | `0 4px 15px rgba(0,0,0,0.1)` |
| `--shadow-hover` | `0 8px 25px rgba(0,0,0,0.15)` |
| Base spacing unit | 8px (use multiples) |
| Touch target min | 44px height |

---

## Transitions

**Standard easing:** `cubic-bezier(0.4, 0, 0.2, 1)` — smooth, material-inspired.
**Spring easing:** `cubic-bezier(0.28, 0.84, 0.42, 1)` — used for mascot jump, reveals.
**Duration:** 200–300ms for hover/focus, 600–800ms for entrance animations.

---

## Component Patterns

### Buttons
- **Primary action:** `background: var(--primary-blue)`, `color: white`, `border-radius: var(--radius-small)`, `font: Nunito 700`, `min-height: 44px`
- **Pill buttons (toolbar):** `background: white`, `border: 2px solid <color>`, `border-radius: 20px`, `padding: 8px 16px`, `font: Nunito 700 0.9rem`
- **Card buttons (menu):** full gradient, min-height 70px, hover lifts with `translateY(-5px) scale(1.02)`

### Animation Objects (`.anim-object`)
- Circular: `border-radius: 50%`
- Size: 52×52px (mobile) / 60×60px (tablet+)
- Font-size: 2rem emoji
- Background: white with `box-shadow: 0 3px 10px rgba(0,0,0,0.12)`
- Tapped state: `scale(1.3)` + `box-shadow: 0 0 0 3px var(--primary-gold)`

### Animation Stage (`#animation-stage`)
- Background: `var(--bg-light)` (`#f0f8ff`)
- Border: `2px dashed var(--primary-blue)` → transitions to `2px solid var(--primary-green)` on complete
- Border-radius: `var(--radius)`
- Min-height: 180px (mobile) / 240px (tablet+)
- Entry: `animation: badgePop 0.3s ease-out`

---

## Animation Grammar

Each math strand uses a specific visual grammar so kids build mental models:

| Grammar | Strands | Visual Pattern |
|---------|---------|----------------|
| `grouping` | number, wordproblems, algebra, comparing | Objects appear in two groups, merge |
| `ten_frame` | placevalue | 10-frame grid fills left-to-right |
| `number_line` | skipcounting | Frog hops along a horizontal line |
| `removal` | subtraction patterns | Objects appear then cross out/fade |
| `coins` | financial | Canadian coin objects (styled divs) |
| `hops` | skipcounting, time | Numbered circles with arc connectors |
| `show` | spatial, measurement, time | Objects scale/position to show concept |

### Emoji map (override Gemini's choice):
```js
const GRAMMAR_EMOJI = {
  ten_frame: '🟦', number_line: '🐸', grouping: '🍎',
  removal: '🍎', coins: '🪙', hops: '🐸', show: '⭐'
};
```

---

## Motion Principles

1. **Purpose over decoration** — every animation teaches something or confirms an action
2. **Stagger for counting** — objects enter one-by-one (100ms apart) so kids can count them
3. **Sound + motion together** — `pop` on appear, `whoosh` on fly-in, `ding` on reveal
4. **Speed multiplier** — all durations multiply by `speedMultiplier` (1.0 normal / 0.4 slow)
5. **Confetti is earned** — only on the reveal step, not on every correct interaction

### Loading phrases (random pool):
```js
const LOADING_PHRASES = [
  'Let me show you! ✨', 'Watch this! 🌟', 'Here\'s a magic trick! 🎩',
  'I\'ll draw it out! 🎨', 'Let\'s count together! 🤝', 'I know just what to do! 💡'
];
```

### Reveal moment:
- Giant gold number at 3rem, Nunito 900, `var(--primary-gold)`, centered in stage
- `animation: revealPop` (scale 0 → 1.2 → 1)
- 12 confetti pieces spawn simultaneously
- Stage border: `var(--primary-blue)` → `var(--primary-green)` over 0.5s

### Draw canvas stroke:
- Width: 6px, `lineCap: 'round'`, `lineJoin: 'round'`
- Rotating colors per stroke: blue → green → orange → purple → pink (cycles)
- `touch-action: none` on canvas element (prevents scroll-while-drawing on iPad)

### Confetti spec:
- 12 `div` elements, 8×8px, `border-radius: 2px`
- Colors: gold, blue, green, pink, orange (varied)
- Spawned at center-top of animation stage
- `@keyframes confettiFall`: translateX(random ±60px) + translateY(100px) + rotate(random deg), opacity 1→0, over 1s
- Removed from DOM after animation

---

## Responsive Breakpoints

| Breakpoint | Behavior |
|------------|----------|
| <480px (mobile) | Mascot stays in corner (no choreography). Animation stage min-height: 180px. Toolbar wraps to 2×2 grid. |
| 480–768px (tablet) | Mascot choreography enabled. Stage min-height: 240px. Toolbar in one row. |
| 768px+ (desktop) | Full layout. Stage max-width: 600px centered. |

---

## Accessibility

- All interactive elements: `min-height: 44px` touch target
- Focus ring: `outline: 3px solid var(--primary-blue); outline-offset: 2px`
- Animation objects: `aria-label="[emoji name] number [count]"` (e.g. "apple number 3")
- Toolbar buttons: explicit `aria-label` (e.g. "Replay animation", "Slow motion", "Toggle sound", "Draw along")
- Animation stage: `role="region" aria-label="Math animation"`
- Draw canvas: `role="img" aria-label="Drawing canvas"`
- `prefers-reduced-motion`: wrap all `@keyframes` calls in `@media (prefers-reduced-motion: no-preference)`; fallback = instant state change

---

## Mascot (😸)

- Position: `fixed`, `bottom: 15px`, `right: 15px`, `z-index: 50`
- Idle: `animation: bounce 2s infinite ease-in-out`
- Correct: `mascot-jump` class → `mascotJump` keyframe
- Wrong: `mascot-shake` class → `mascotShake` keyframe
- Choreography (≥480px): `scrollIntoView` on animation start, then `transform: translate()` to edge of animation stage. Returns to corner on `onComplete()`.
- Speech bubble: max-width 140px, `border-radius: 15px 15px 0 15px`, white bg, `--shadow`
