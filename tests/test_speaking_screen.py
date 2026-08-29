import asyncio
import importlib
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from ui.screens.speaking import SpeakingScreen


class DummyLabel:
    def __init__(self):
        self.text = None

    def configure(self, **kwargs):
        self.text = kwargs.get('text')


class DummyButton:
    def __init__(self):
        self.state = 'normal'

    def configure(self, **kwargs):
        self.state = kwargs.get('state', self.state)


class SpeakingScreenTests(unittest.TestCase):
    def test_evaluate_recording_uses_coach_when_model_is_not_preloaded(self):
        screen = object.__new__(SpeakingScreen)
        screen.audio_path = 'sample.wav'
        screen.target_sentence = 'The future belongs to those who prepare for it today.'
        screen.feedback_label = DummyLabel()
        screen.coach = SimpleNamespace(evaluate=AsyncMock(return_value={
            'spoken_text': 'hello',
            'accuracy': 0.95,
            'mismatches': [],
            'audio_file': None,
        }))
        expected_result = {
            'spoken_text': 'hello',
            'accuracy': 0.95,
            'mismatches': [],
            'audio_file': None,
        }
        screen._run_async = MagicMock(side_effect=lambda coro: asyncio.run(coro))
        screen._display_result = MagicMock()
        screen.save_session = MagicMock()

        screen.evaluate_recording()

        screen._run_async.assert_called_once()
        screen._display_result.assert_called_once_with(expected_result)
        screen.save_session.assert_called_once()

    def test_display_result_keeps_play_button_disabled_without_audio(self):
        screen = object.__new__(SpeakingScreen)
        screen.correct_audio_path = None
        screen.play_button = DummyButton()
        screen.feedback_label = DummyLabel()

        screen._display_result({
            'spoken_text': 'hello',
            'accuracy': 0.9,
            'mismatches': ['hello'],
            'audio_file': None,
            'detailed_feedback': 'Great effort.',
        })

        self.assertEqual(screen.play_button.state, 'disabled')

    def test_coach_import_is_safe_when_edge_tts_missing(self):
        sys.modules.pop('core.pronunciation', None)
        with patch.dict(sys.modules, {'edge_tts': None}):
            module = importlib.import_module('core.pronunciation')
            self.assertTrue(hasattr(module, 'PronunciationCoach'))


if __name__ == '__main__':
    unittest.main()