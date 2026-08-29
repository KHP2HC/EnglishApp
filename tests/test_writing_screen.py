import unittest
from types import SimpleNamespace

from ui.screens.writing import WritingScreen


class DummyTextBox:
    def __init__(self, text=""):
        self.text = text

    def get(self, start, end):
        return self.text


class DummyLabel:
    def __init__(self):
        self.text = None

    def configure(self, **kwargs):
        self.text = kwargs.get('text')


class WritingScreenTests(unittest.TestCase):
    def test_get_feedback_uses_local_feedback_when_ai_tutor_is_unavailable(self):
        screen = object.__new__(WritingScreen)
        screen.tutor = None
        screen.essay_entry = DummyTextBox("I have improved a lot in my English learning.")
        screen.feedback_label = DummyLabel()
        screen.save_session = lambda: None

        screen.get_feedback()

        self.assertIn("offline feedback", screen.feedback_label.text.lower())


if __name__ == '__main__':
    unittest.main()
