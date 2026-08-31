"""Tests for the grammar screen."""

import unittest
from unittest.mock import patch, MagicMock


class GrammarScreenTests(unittest.TestCase):
    def test_grammar_lessons_are_defined(self):
        from ui.screens.grammar import GRAMMAR_LESSONS
        self.assertGreaterEqual(len(GRAMMAR_LESSONS), 5)
        for lesson in GRAMMAR_LESSONS:
            self.assertIn("title", lesson)
            self.assertIn("body", lesson)
            self.assertIn("exercises", lesson)
            self.assertGreaterEqual(len(lesson["exercises"]), 1)

    def test_grammar_exercises_have_correct_structure(self):
        from ui.screens.grammar import GRAMMAR_LESSONS
        for lesson in GRAMMAR_LESSONS:
            for ex in lesson["exercises"]:
                self.assertIn("question", ex)
                self.assertIn("options", ex)
                self.assertIn("answer", ex)
                self.assertIn("explanation", ex)
                self.assertIn(ex["answer"], ex["options"])

    def test_grammar_covers_key_topics(self):
        from ui.screens.grammar import GRAMMAR_LESSONS
        titles = [l["id"] for l in GRAMMAR_LESSONS]
        self.assertIn("present_simple", titles)
        self.assertIn("conditionals", titles)
        self.assertIn("passive_voice", titles)


if __name__ == "__main__":
    unittest.main()
