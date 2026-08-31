"""Tests for the i18n module."""

import unittest
from core.i18n import t, set_language, get_language, available_languages


class I18nTests(unittest.TestCase):
    def setUp(self):
        set_language("en")

    def test_default_language_is_english(self):
        self.assertEqual(get_language(), "en")

    def test_translate_returns_english_by_default(self):
        self.assertEqual(t("dashboard"), "Dashboard")

    def test_translate_returns_vietnamese_when_set(self):
        set_language("vi")
        self.assertEqual(t("dashboard"), "Bảng điều khiển")

    def test_translate_falls_back_to_key(self):
        self.assertEqual(t("nonexistent_key"), "nonexistent_key")

    def test_available_languages_includes_en_and_vi(self):
        langs = available_languages()
        self.assertIn("en", langs)
        self.assertIn("vi", langs)
        self.assertEqual(langs["en"], "English")
        self.assertEqual(langs["vi"], "Tiếng Việt")

    def test_set_language_ignores_invalid(self):
        set_language("fr")
        self.assertEqual(get_language(), "en")


if __name__ == "__main__":
    unittest.main()
