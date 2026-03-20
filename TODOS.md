# TODOS

## Migrate quiz.html to Material Design 3 / Tailwind Design System
**What:** Rewrite quiz.html to use Tailwind utility classes and MD3 CSS tokens (`--c-primary`, `bg-primary-container`, etc.) instead of the legacy CSS variable system (`--primary-blue`, `.container-card`, `style.css`).
**Why:** The home screen (index.html) uses MD3/Tailwind; the quiz page uses a legacy system. Users cross a visual boundary on every session. Fonts, shadows, border-radii, and color names are all different between the two pages.
**Pros:** Consistent visual language across the whole app. Enables reuse of Tailwind responsive utilities for easier future mobile work. Eliminates style.css complexity.
**Cons:** Large diff on one file (~637 lines). Requires QA pass on quiz animations, chatbot, mascot, and all interaction states after migration.
**Context:** Discovered during design review of mobile responsiveness PR (feat/gemini-animations branch, 2026-03-20). Both pages currently work, but the inconsistency is observable at a glance when navigating index → quiz.
**Effort:** L human / M CC
**Priority:** P1
**Depends on:** Mobile responsiveness fixes shipped

---

## Update DESIGN.md to Match Actual Fonts
**What:** DESIGN.md specifies Nunito as the primary font, but base.html loads Plus Jakarta Sans (headlines) and Lexend (body/labels) with Nunito only as a fallback. Update DESIGN.md typography table to reflect the actual font stack.
**Why:** The spec and implementation are out of sync. Future contributors will follow DESIGN.md and add Nunito — not what renders in production.
**Pros:** Eliminates spec drift. Small change.
**Cons:** None.
**Context:** Discovered during design review 2026-03-20.
**Effort:** XS human / XS CC
**Priority:** P3
**Depends on:** Nothing

---

## Sound Design Pass
**What:** Replace Web Audio API synthesized tones (pop/whoosh/ding) with short recorded sound files.
**Why:** Synthesized tones sound like beeps. Recorded sounds (like Duolingo's) create memorable, joyful audio cues that reinforce learning associations.
**Pros:** Meaningfully improves delight and audio-visual coherence. Small files (<50KB each).
**Cons:** Requires sourcing/licensing free sounds. Adds static file serving.
**Context:** The animation engine (shipped in gemini-animations PR) uses Web Audio oscillator synthesis as a placeholder. Three sounds needed: `pop` (object appears), `whoosh` (fly-in), `ding` (reveal/confetti).
**Effort:** M human / S CC
**Priority:** P2
**Depends on:** Animation engine shipped (gemini-animations PR)
