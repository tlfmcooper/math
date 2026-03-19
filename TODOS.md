# TODOS

## Sound Design Pass
**What:** Replace Web Audio API synthesized tones (pop/whoosh/ding) with short recorded sound files.
**Why:** Synthesized tones sound like beeps. Recorded sounds (like Duolingo's) create memorable, joyful audio cues that reinforce learning associations.
**Pros:** Meaningfully improves delight and audio-visual coherence. Small files (<50KB each).
**Cons:** Requires sourcing/licensing free sounds. Adds static file serving.
**Context:** The animation engine (shipped in gemini-animations PR) uses Web Audio oscillator synthesis as a placeholder. Three sounds needed: `pop` (object appears), `whoosh` (fly-in), `ding` (reveal/confetti).
**Effort:** M human / S CC
**Priority:** P2
**Depends on:** Animation engine shipped (gemini-animations PR)
