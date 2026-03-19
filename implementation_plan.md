# Animate Cat Mascot with Voice

The goal is to change the current Fox mascot into an animated, talking Cat that reads aloud words of encouragement to the student when they submit answers.

## Proposed Changes

### Frontend Changes (`quiz.html` & `style.css`)

#### [MODIFY] `templates/quiz.html`
1. **Mascot Emoji**: Change the hardcoded `🦊` emoji to a `😸` (Cat) in the `#mascot` div.
2. **Text-to-Speech (Web Speech API)**: Update the `updateMascot(state)` JavaScript function:
   - When a phrase is selected from the translations list, strip out any emojis using a simple regex so the synthesis engine doesn't accidentally read "Smiling face with open mouth".
   - Instantiate a `SpeechSynthesisUtterance(cleanedString)`.
   - Iterate through `window.speechSynthesis.getVoices()` to find a friendly, high-pitched voice (often Microsoft Zira or Google UK/US female voices work well for characters) if available, otherwise fallback to the default voice.
   - Call `window.speechSynthesis.speak()` to read the text aloud in the browser.
3. **Triggering Animations**: In `updateMascot`, toggle specific CSS classes on the mascot element depending on the state (e.g., add `mascot-jump` on correct answers, `mascot-shake` on wrong answers).

#### [MODIFY] `static/style.css`
1. **Keyframe Animations**: Add new CSS animations specifically tailored for the mascot:
   - `@keyframes mascotJump`: A bouncy upward vertical jump.
   - `@keyframes mascotShake`: A gentle side-to-side encouraging nod/shake.
2. **Utility Classes**: Add `.mascot-jump` and `.mascot-shake` classes to apply these keyframes so they can be added/removed dynamically via JavaScript.

## Verification Plan

### Manual Verification
- The user will open the quiz in their browser (with volume up).
- As answers are clicked, verify the Cat emoji animates appropriately (jumps vs shakes).
- Verify the words of encouragement are spoken aloud by the browser's TTS engine without reading out emojis literally.
