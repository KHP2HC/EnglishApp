from pathlib import Path
import importlib
import unittest


class SeedDataTests(unittest.TestCase):
    def test_seed_vocab_builder_reaches_target_size(self):
        module = importlib.import_module('data.seed')
        items = module._build_vocab_items('data/seed', target_count=50000)

        self.assertEqual(len(items), 50000)
        self.assertEqual(len({item['word'] for item in items}), 50000)
        self.assertTrue(any(item.get('phonetic') for item in items[:3]))

    def test_seed_vocab_json_exists(self):
        self.assertTrue(Path('data/seed/vocab.json').exists(), 'Seed vocabulary file should exist')


def test_seed_loader_imports():
    module = importlib.import_module('data.seed')
    assert hasattr(module, 'load_seed_data')
