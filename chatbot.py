import os
import logging
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List

# Module-level singleton — created once, reused for all requests
_client: Optional[genai.Client] = None


def _get_client() -> Optional[genai.Client]:
    global _client
    if _client is None:
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return None
        _client = genai.Client(api_key=api_key)
    return _client


class AnimationObject(BaseModel):
    emoji: str = Field(description="A single emoji character representing the object")
    label: str = Field(description="Short accessible label, e.g. 'apple'")


class AnimationStep(BaseModel):
    id: int = Field(description="Step number starting at 1")
    objects: List[AnimationObject] = Field(
        description="Individual emoji objects to display (use only for quantities 1-10). For larger numbers use action='number_badge' with value field instead.",
        max_length=10
    )
    action: str = Field(
        description=(
            "Animation action: "
            "'appear' — individual objects pop in one by one (use for quantities 1-10 only); "
            "'fly_in' — objects fly in from the right (quantities 1-10 only); "
            "'number_badge' — show a single large number badge (use for any quantity > 10, e.g. value='25'); "
            "'merge' — combine two groups; "
            "'reveal' — show the final answer as a big gold number (always use value field here); "
            "'cross_out' — cross out objects; "
            "'hop' — hop along number line"
        )
    )
    value: Optional[str] = Field(
        description=(
            "For 'number_badge': the number to display as a badge, e.g. '25'. "
            "For 'reveal': the final answer to display large, e.g. '26'. "
            "Always set this for 'reveal' steps."
        ),
        default=None
    )
    narration: str = Field(description="Short narration for this step (spoken aloud, max 20 words)")
    sound: str = Field(
        description="Sound cue: 'pop', 'whoosh', or 'ding'",
        default="pop"
    )
    duration_ms: int = Field(
        description="How long this step takes in milliseconds",
        ge=100,
        le=3000,
        default=800
    )


class AnimationScript(BaseModel):
    grammar: str = Field(
        description="Animation grammar: 'grouping', 'ten_frame', 'number_line', 'removal', 'coins', 'hops', 'show'"
    )
    steps: List[AnimationStep] = Field(
        description="Ordered animation steps, max 5",
        max_length=5
    )


class ChatbotResponse(BaseModel):
    reply: str = Field(description="The grade-1 appropriate textual reply from the teacher")
    animation: Optional[AnimationScript] = Field(
        description="Optional animation script to render",
        default=None
    )


# Map each curriculum strand to its preferred animation grammar
STRAND_GRAMMAR = {
    'number': 'grouping',
    'wordproblems': 'grouping',
    'algebra': 'grouping',
    'comparing': 'grouping',
    'data': 'grouping',
    'skipcounting': 'hops',
    'placevalue': 'ten_frame',
    'spatial': 'show',
    'measurement': 'show',
    'time': 'show',
    'financial': 'coins',
    'coding': 'show',
}


def get_chat_response(messages, context="", strand="number", attempt=1):
    """
    Sends a conversation thread to the Gemini model to help a student
    with a math concept they struggled with.

    attempt=1  → first wrong answer: show concept animation, NO reveal, ask guiding question.
    attempt=2+ → student has tried again: may now reveal the answer if still stuck.

    Returns a dict with 'reply' and optional 'animation' (AnimationScript).
    On Pydantic validation failure, returns {reply, animation: null}.
    """
    client = _get_client()
    if not client:
        return {"error": "GEMINI_API_KEY is not set. Please set it in your environment."}

    grammar = STRAND_GRAMMAR.get(strand, 'grouping')

    if attempt == 1:
        reveal_rule = (
            "PEDAGOGY — THIS IS THE STUDENT'S FIRST ATTEMPT: "
            "Do NOT reveal the final answer yet. Do NOT use action='reveal' in the animation. "
            "Instead show a conceptual animation that breaks the problem into smaller, simpler pieces "
            "— e.g. for '22 + 22', show the tens (20+20) as two number_badges, then show the ones (2+2) "
            "as fly_in objects, but stop BEFORE combining them. "
            "End your 'reply' with ONE simple guiding question the student can answer "
            "(e.g. 'Can you tell me: what is 2 + 2?'). "
            "Do NOT include a 'reveal' step. The last step should be 'fly_in' or 'appear', not 'reveal'. "
        )
        reveal_example = (
            "Example for attempt=1 on '22 + 22': "
            "  Step 1: action='number_badge', value='20', objects=[], narration='22 has 2 tens, that is 20!', sound='whoosh' "
            "  Step 2: action='number_badge', value='20', objects=[], narration='The other 22 also has 20!', sound='whoosh' "
            "  Step 3: action='fly_in', objects=[{emoji:'⭐',label:'one'},{emoji:'⭐',label:'one'}], narration='Now, what is 2 plus 2?', sound='pop' "
            "reply: 'Great try! Let us break it down. 22 has 20 and 2. Can you tell me: what is 2 + 2?' "
        )
    else:
        reveal_rule = (
            "The student has already tried a guiding question. "
            "If they just answered CORRECTLY, confirm enthusiastically and use 'reveal' to show the final answer. "
            "If they are still struggling after attempt 2, gently show the full answer using 'reveal' "
            "and explain step by step. "
            "The LAST step must be action='reveal' with value='<the exact final answer>' and objects=[]. "
            "CRITICAL: value must be the complete numeric answer. For '22 + 22 = 44', value must be '44'. "
        )
        reveal_example = (
            "Example for attempt=2+ on '22 + 22' when student got it wrong again: "
            "  Step 1: action='number_badge', value='22', objects=[], narration='We start with 22!', sound='whoosh' "
            "  Step 2: action='number_badge', value='22', objects=[], narration='We add another 22!', sound='whoosh' "
            "  Step 3: action='reveal', value='44', objects=[], narration='22 plus 22 equals 44!', sound='ding' "
        )

    system_instruction = (
        "You are a friendly, encouraging, and highly interactive Grade 1 math teacher. "
        "You are currently chatting with a student who struggled with a math question. "
        f"Here is the original question they missed: {context} "
        "Keep your language very simple (Grade 1 level). "
        "Read the conversation history CAREFULLY. "
        "1. If the user just answered your previous guiding question CORRECTLY, enthusiastically confirm "
        "they are right, explain how it connects to the original question, and conclude! Do NOT ask another question. "
        "2. If the user answered INCORRECTLY, gently explain why, and ask a VERY simple, DIFFERENT guiding question. "
        "Do NOT repeat the exact same question. "
        "3. You have magic tools! You can make objects appear on screen to help explain math. "
        f"For this math topic, always use the '{grammar}' animation grammar. "
        + reveal_rule +
        "ANIMATION RULES — read carefully: "
        f"- grammar must be '{grammar}' "
        "- max 5 steps total "
        "- For quantities 1-10: use 'appear' or 'fly_in' with individual emoji objects (max 10 objects). "
        "- For quantities > 10: use action='number_badge' with value='<number>' and objects=[]. "
        "  Example: to show 22, use action='number_badge', value='22', objects=[]. "
        "- narration is spoken aloud, keep it to 20 words max per step "
        "- use simple emoji like 🍎 🌟 🐸 🟦 🪙 for individual objects "
        "- sound: 'pop' for objects appearing, 'whoosh' for badges/movement, 'ding' for the reveal only "
        + reveal_example +
        "Always align your textual 'reply' with the animation you provide."
    )

    formatted_messages = [
        {'role': 'user', 'parts': [{'text': f"I need help with this question: {context}"}]}
    ]
    for msg in messages:
        role = 'user' if msg['role'] == 'user' else 'model'
        formatted_messages.append({'role': role, 'parts': [{'text': msg['content']}]})

    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=formatted_messages,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                response_mime_type="application/json",
                response_schema=ChatbotResponse,
            )
        )
        parsed = json.loads(response.text)

        # On attempt 1: enforce no reveal — strip it regardless of what Gemini returned.
        # LLMs don't reliably follow "don't use X" instructions, so we enforce in code.
        if attempt == 1 and isinstance(parsed.get('animation'), dict):
            steps = parsed['animation'].get('steps', [])
            filtered = [s for s in steps if s.get('action') != 'reveal']
            if filtered:
                parsed['animation']['steps'] = filtered
            else:
                # All steps were reveals (shouldn't happen) — drop the animation
                parsed['animation'] = None

        # Validate with Pydantic — catch schema mismatches from the model
        try:
            ChatbotResponse(**parsed)
        except ValidationError as ve:
            logging.warning(f"Chatbot animation schema mismatch: {ve}")
            # Return reply but null out the animation rather than 500-ing
            return {"reply": parsed.get("reply", "Let me help you with that!"), "animation": None}

        return parsed

    except Exception as e:
        logging.error(f"Chatbot error: {e}")
        return {"error": "Oops! I'm having trouble thinking right now. Please tell my developer to check my connection!"}
