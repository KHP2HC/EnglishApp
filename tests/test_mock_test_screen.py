"""Tests for the mock test screen."""

import unittest


class MockTestScreenTests(unittest.TestCase):
    def test_mock_tests_are_defined_for_all_exams(self):
        from ui.screens.mock_test import MOCK_TESTS
        self.assertIn("TOEIC", MOCK_TESTS)
        self.assertIn("IELTS", MOCK_TESTS)
        self.assertIn("TOEFL", MOCK_TESTS)
        self.assertIn("VSTEP", MOCK_TESTS)

    def test_toeic_has_correct_format(self):
        from ui.screens.mock_test import MOCK_TESTS
        toeic = MOCK_TESTS["TOEIC"]
        self.assertEqual(toeic["total_questions"], 200)
        self.assertEqual(toeic["time_minutes"], 120)
        self.assertEqual(len(toeic["sections"]), 2)

    def test_ielts_has_four_sections(self):
        from ui.screens.mock_test import MOCK_TESTS
        ielts = MOCK_TESTS["IELTS"]
        self.assertEqual(len(ielts["sections"]), 4)
        section_names = [s["name"] for s in ielts["sections"]]
        self.assertIn("Listening", section_names)
        self.assertIn("Reading", section_names)
        self.assertIn("Writing", section_names)
        self.assertIn("Speaking", section_names)

    def test_sample_questions_have_answers(self):
        from ui.screens.mock_test import _SAMPLE_QUESTIONS
        self.assertGreaterEqual(len(_SAMPLE_QUESTIONS), 5)
        for q in _SAMPLE_QUESTIONS:
            self.assertIn("question", q)
            self.assertIn("options", q)
            self.assertIn("answer", q)
            self.assertIn(q["answer"], q["options"])


if __name__ == "__main__":
    unittest.main()
