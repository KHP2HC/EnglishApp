import unittest
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from ui.screens.vocabulary import VocabularyScreen


class VocabularyScreenTests(unittest.TestCase):
    def test_filter_due_cards_keeps_due_and_new_cards(self):
        screen = VocabularyScreen.__new__(VocabularyScreen)

        cards = [
            SimpleNamespace(next_review_date=date.today() + timedelta(days=3)),
            SimpleNamespace(next_review_date=date.today()),
            SimpleNamespace(next_review_date=None),
        ]

        due_cards = screen._filter_due_cards(cards)

        self.assertEqual(len(due_cards), 2)
        self.assertEqual(due_cards[0].next_review_date, date.today())
        self.assertIsNone(due_cards[1].next_review_date)

    def test_filter_due_cards_accepts_iso_date_strings(self):
        screen = VocabularyScreen.__new__(VocabularyScreen)

        cards = [
            SimpleNamespace(next_review_date=(date.today() + timedelta(days=1)).isoformat()),
            SimpleNamespace(next_review_date=date.today().isoformat()),
            SimpleNamespace(next_review_date=None),
        ]

        due_cards = screen._filter_due_cards(cards)

        self.assertEqual(len(due_cards), 2)
        self.assertEqual(due_cards[0].next_review_date, date.today().isoformat())

    def test_practice_queue_prioritizes_new_cards_before_reviews(self):
        screen = VocabularyScreen.__new__(VocabularyScreen)
        screen.progress_by_card_id = {
            2: SimpleNamespace(times_seen=1, next_review_date=date.today()),
            3: SimpleNamespace(times_seen=20, next_review_date=date.today() + timedelta(days=7)),
        }

        cards = [
            SimpleNamespace(id=1, word='alpha'),
            SimpleNamespace(id=2, word='beta'),
            SimpleNamespace(id=3, word='gamma'),
        ]

        with patch('ui.screens.vocabulary.random.shuffle', side_effect=lambda items: items.reverse()):
            queue = screen._build_practice_queue(cards, screen.progress_by_card_id)

        self.assertEqual([card.word for card in queue[:1]], ['alpha'])
        self.assertCountEqual([card.word for card in queue[1:]], ['beta', 'gamma'])

    def test_card_status_text_marks_learned_words(self):
        screen = VocabularyScreen.__new__(VocabularyScreen)
        screen.progress_by_card_id = {
            1: SimpleNamespace(times_seen=20, next_review_date=date.today() + timedelta(days=3)),
        }

        status = screen._card_status_text(SimpleNamespace(id=1, word='alpha'))

        self.assertIn('Learned', status)
        self.assertIn('random review', status)

    def test_enrich_card_bg_persists_ipa_synonym_and_antonym(self):
        screen = VocabularyScreen.__new__(VocabularyScreen)
        screen.cards = [SimpleNamespace(id=1, word='benefit', phonetic=None, synonym=None,
                                        antonym=None, example_sentence=None, _enriched=False)]
        screen.current_index = 0
        screen.show_back = False
        screen.after = lambda delay, fn: fn()

        stored = SimpleNamespace(
            id=1, word='benefit',
            phonetic=None, synonym=None, antonym=None,
            meaning_en='Common English vocabulary word: benefit.',
            example_sentence='Practice using benefit in a simple sentence.',
            category=None,
        )

        with patch('ui.screens.vocabulary.get_session') as get_session_mock, patch(
            'ui.screens.vocabulary.build_vocabulary_details',
            return_value={
                'ipa': 'ˈbenɪfɪt',
                'synonym': 'advantage',
                'antonym': 'disadvantage',
                'definition': 'A helpful or good effect.',
                'example_sentence': 'The benefit of practice is steady progress.',
            },
        ):
            db = SimpleNamespace(
                query=lambda model: SimpleNamespace(
                    filter_by=lambda **kwargs: SimpleNamespace(first=lambda: stored)
                ),
                commit=lambda: None,
                close=lambda: None,
            )
            get_session_mock.return_value = db
            screen._do_enrich_card(screen.cards[0])

        card = screen.cards[0]
        self.assertEqual(card.phonetic, 'ˈbenɪfɪt')
        self.assertEqual(card.synonym, 'advantage')
        self.assertEqual(card.antonym, 'disadvantage')
        self.assertTrue(getattr(card, '_enriched', False))
        self.assertEqual(card.meaning_en, 'A helpful or good effect.')
