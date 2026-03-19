"""
Tests for chatbot.py — AnimationScript schema, ValidationError rescue,
and module-level client singleton.
"""
import json
import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError


# ── Schema tests ──────────────────────────────────────────────────────────────

class TestAnimationSchema:
    def test_valid_animation_script(self):
        from chatbot import AnimationScript, AnimationStep, AnimationObject
        script = AnimationScript(
            grammar='grouping',
            steps=[
                AnimationStep(
                    id=1,
                    objects=[AnimationObject(emoji='🍎', label='apple')],
                    action='appear',
                    narration='Here comes one apple!',
                    sound='pop',
                    duration_ms=800
                )
            ]
        )
        assert script.grammar == 'grouping'
        assert len(script.steps) == 1
        assert script.steps[0].objects[0].emoji == '🍎'

    def test_step_duration_bounds(self):
        from chatbot import AnimationStep, AnimationObject
        # duration_ms must be >= 100
        with pytest.raises(ValidationError):
            AnimationStep(
                id=1, objects=[], action='appear',
                narration='test', sound='pop', duration_ms=50
            )
        # duration_ms must be <= 3000
        with pytest.raises(ValidationError):
            AnimationStep(
                id=1, objects=[], action='appear',
                narration='test', sound='pop', duration_ms=5000
            )

    def test_steps_max_length(self):
        from chatbot import AnimationScript, AnimationStep, AnimationObject
        obj = AnimationObject(emoji='🍎', label='apple')
        steps = [
            AnimationStep(id=i, objects=[obj], action='appear', narration='test', sound='pop', duration_ms=800)
            for i in range(1, 7)  # 6 steps — exceeds max of 5
        ]
        with pytest.raises(ValidationError):
            AnimationScript(grammar='grouping', steps=steps)

    def test_objects_max_per_step(self):
        from chatbot import AnimationStep, AnimationObject
        objects = [AnimationObject(emoji='🍎', label='apple') for _ in range(16)]  # exceeds max 15
        with pytest.raises(ValidationError):
            AnimationStep(id=1, objects=objects, action='appear', narration='test', sound='pop', duration_ms=800)

    def test_chatbot_response_animation_optional(self):
        from chatbot import ChatbotResponse
        resp = ChatbotResponse(reply='Hello!', animation=None)
        assert resp.animation is None
        assert resp.reply == 'Hello!'


# ── get_chat_response tests ───────────────────────────────────────────────────

class TestGetChatResponse:
    def test_missing_api_key(self, monkeypatch):
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
        # Reset singleton so it picks up the missing key
        import chatbot
        chatbot._client = None

        result = chatbot.get_chat_response([], 'test context')
        assert 'error' in result
        assert 'GEMINI_API_KEY' in result['error']

    def test_validation_error_rescue(self, monkeypatch):
        """When Gemini returns malformed animation JSON, return reply with animation=null."""
        monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
        import chatbot
        chatbot._client = None

        bad_response = {
            'reply': 'Let me help!',
            'animation': {
                'grammar': 'grouping',
                'steps': [{'id': 1, 'objects': None, 'action': 'appear',
                           'narration': 'test', 'sound': 'pop', 'duration_ms': 50}]
                # duration_ms=50 violates ge=100 constraint
            }
        }

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(bad_response)
        mock_client.models.generate_content.return_value = mock_response

        with patch('chatbot._get_client', return_value=mock_client):
            result = chatbot.get_chat_response([], 'test context', strand='number')

        assert result['reply'] == 'Let me help!'
        assert result['animation'] is None

    def test_valid_response_returned(self, monkeypatch):
        monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
        import chatbot
        chatbot._client = None

        good_response = {
            'reply': 'Great question!',
            'animation': {
                'grammar': 'grouping',
                'steps': [
                    {
                        'id': 1,
                        'objects': [{'emoji': '🍎', 'label': 'apple'}],
                        'action': 'appear',
                        'narration': 'Here is one apple',
                        'sound': 'pop',
                        'duration_ms': 800
                    }
                ]
            }
        }

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(good_response)
        mock_client.models.generate_content.return_value = mock_response

        with patch('chatbot._get_client', return_value=mock_client):
            result = chatbot.get_chat_response([], 'test context', strand='number')

        assert result['reply'] == 'Great question!'
        assert result['animation']['grammar'] == 'grouping'
        assert len(result['animation']['steps']) == 1

    def test_strand_grammar_map(self):
        from chatbot import STRAND_GRAMMAR
        assert STRAND_GRAMMAR['number'] == 'grouping'
        assert STRAND_GRAMMAR['skipcounting'] == 'hops'
        assert STRAND_GRAMMAR['placevalue'] == 'ten_frame'
        assert STRAND_GRAMMAR['financial'] == 'coins'

    def test_empty_steps_in_response(self, monkeypatch):
        """On attempt=1 with empty steps, animation is nulled out (no spoiler)."""
        monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
        import chatbot
        chatbot._client = None

        response_with_empty = {
            'reply': 'Let me explain!',
            'animation': {'grammar': 'grouping', 'steps': []}
        }

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(response_with_empty)
        mock_client.models.generate_content.return_value = mock_response

        with patch('chatbot._get_client', return_value=mock_client):
            result = chatbot.get_chat_response([], 'test', strand='number', attempt=1)

        assert result['reply'] == 'Let me explain!'
        # attempt=1: no reveal steps → filtered list empty → animation nulled to prevent spoiler
        assert result['animation'] is None

    def test_reveal_stripped_on_attempt1(self, monkeypatch):
        """Reveal steps are stripped server-side on attempt=1 regardless of Gemini output."""
        monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
        import chatbot
        chatbot._client = None

        response_with_reveal = {
            'reply': 'Let me show you!',
            'animation': {'grammar': 'grouping', 'steps': [
                {'id': 1, 'action': 'number_badge', 'value': '22', 'objects': [],
                 'narration': 'Start with 22', 'sound': 'whoosh', 'duration_ms': 800},
                {'id': 2, 'action': 'reveal', 'value': '44', 'objects': [],
                 'narration': '22 + 22 = 44', 'sound': 'ding', 'duration_ms': 800},
            ]}
        }

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(response_with_reveal)
        mock_client.models.generate_content.return_value = mock_response

        with patch('chatbot._get_client', return_value=mock_client):
            result = chatbot.get_chat_response([], 'test', strand='number', attempt=1)

        assert result['reply'] == 'Let me show you!'
        # The reveal step must be stripped — only number_badge remains
        steps = result['animation']['steps']
        assert all(s['action'] != 'reveal' for s in steps)
        assert len(steps) == 1
        assert steps[0]['action'] == 'number_badge'

    def test_reveal_kept_on_attempt2(self, monkeypatch):
        """Reveal steps are preserved on attempt=2 (student has already been guided once)."""
        monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
        import chatbot
        chatbot._client = None

        response_with_reveal = {
            'reply': 'The answer is 44!',
            'animation': {'grammar': 'grouping', 'steps': [
                {'id': 1, 'action': 'number_badge', 'value': '22', 'objects': [],
                 'narration': 'Start with 22', 'sound': 'whoosh', 'duration_ms': 800},
                {'id': 2, 'action': 'reveal', 'value': '44', 'objects': [],
                 'narration': '22 + 22 = 44', 'sound': 'ding', 'duration_ms': 800},
            ]}
        }

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps(response_with_reveal)
        mock_client.models.generate_content.return_value = mock_response

        with patch('chatbot._get_client', return_value=mock_client):
            result = chatbot.get_chat_response([], 'test', strand='number', attempt=2)

        assert result['reply'] == 'The answer is 44!'
        # On attempt=2+, reveal is preserved
        steps = result['animation']['steps']
        assert any(s['action'] == 'reveal' for s in steps)

    def test_api_exception_returns_error(self, monkeypatch):
        monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
        import chatbot
        chatbot._client = None

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception('Network error')

        with patch('chatbot._get_client', return_value=mock_client):
            result = chatbot.get_chat_response([], 'test', strand='number')

        assert 'error' in result

    def test_client_singleton(self, monkeypatch):
        """_get_client() returns the same instance on repeated calls."""
        monkeypatch.setenv('GEMINI_API_KEY', 'test-key')
        import chatbot
        chatbot._client = None

        with patch('chatbot.genai.Client') as mock_cls:
            mock_cls.return_value = MagicMock()
            c1 = chatbot._get_client()
            c2 = chatbot._get_client()
            assert c1 is c2
            assert mock_cls.call_count == 1
