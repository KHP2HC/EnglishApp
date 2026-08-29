import unittest
from types import SimpleNamespace

from ui.screens.reading import ReadingScreen


class ReadingScreenTests(unittest.TestCase):
    def test_load_article_uses_fetched_content(self):
        screen = ReadingScreen.__new__(ReadingScreen)
        screen.app = SimpleNamespace(user=SimpleNamespace(id=1))
        screen.content_fetcher = SimpleNamespace(fetch_articles=lambda difficulty='B1': [{
            'title': 'Sample Article',
            'body': 'The sun rises in the east and sets in the west.',
            'level': 'B1',
            'url': 'https://example.test',
        }])

        article = screen._load_article()

        self.assertEqual(article['body'], 'The sun rises in the east and sets in the west.')
