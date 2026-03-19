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
        description="Objects to display in this step",
        max_length=15
    )
    action: str = Field(
        description="Animation action: 'appear', 'fly_in', 'merge', 'hop', 'fill', 'reveal', 'cross_out'"
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


def get_chat_response(messages, context="", strand="number"):
    """
    Sends a conversation thread to the Gemini model to help a student
    with a math concept they struggled with.

    Returns a dict with 'reply' and optional 'animation' (AnimationScript).
    On Pydantic validation failure, returns {reply, animation: null}.
    """
    client = _get_client()
    if not client:
        return {"error": "GEMINI_API_KEY is not set. Please set it in your environment."}

    grammar = STRAND_GRAMMAR.get(strand, 'grouping')

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
        "Rules for animations: "
        f"- grammar must be '{grammar}' "
        "- max 5 steps, max 15 objects per step "
        "- narration is spoken aloud so keep it to 20 words max per step "
        "- use simple emoji like 🍎 🌟 🐸 🟦 🪙 for objects "
        "- sound: 'pop' for objects appearing, 'whoosh' for movement, 'ding' for the final reveal "
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
            model='gemini-2.0-flash-lite',
            contents=formatted_messages,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                response_mime_type="application/json",
                response_schema=ChatbotResponse,
            )
        )
        parsed = json.loads(response.text)

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
