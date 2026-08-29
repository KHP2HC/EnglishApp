import json
import os
import re
from data.database import get_session
from data.models import VocabularyCard, ExamType, BandLevel

try:
    from wordfreq import top_n_list
except Exception:  # pragma: no cover - dependency guard for startup resilience
    top_n_list = None


TARGET_VOCAB_COUNT = 50000


def _normalize_word(word):
    if not word:
        return None
    normalized = word.strip().lower()
    if not re.fullmatch(r"[a-z]+(?:-[a-z]+)?", normalized):
        return None
    if len(normalized) < 3:
        return None
    return normalized


def _parse_enum(enum_cls, value):
    if not value:
        return None
    if isinstance(value, enum_cls):
        return value
    try:
        return enum_cls[value.upper()]
    except Exception:
        return None


def _load_curated_vocab(seed_dir):
    vocab_file = os.path.join(seed_dir, 'vocab.json')
    if not os.path.exists(vocab_file):
        return []

    with open(vocab_file, 'r', encoding='utf-8') as f:
        items = json.load(f)

    curated = []
    seen = set()
    for item in items:
        word = _normalize_word(item.get('word'))
        if not word or word in seen:
            continue
        seen.add(word)
        curated.append({
            'word': word,
            'phonetic': item.get('phonetic'),
            'synonym': item.get('synonym'),
            'antonym': item.get('antonym'),
            'meaning_en': item.get('meaning_en') or 'Common English vocabulary word.',
            'meaning_vi': item.get('meaning_vi') or 'Từ vựng tiếng Anh thông dụng.',
            'example_sentence': item.get('example_sentence') or f'Use {word} in a sentence.',
            'exam_type': item.get('exam_type'),
            'difficulty_level': item.get('difficulty_level'),
            'category': item.get('category') or 'general',
        })
    return curated


def _generate_vocab_pool(target_count, existing_words):
    if top_n_list is None:
        return []

    generated = []
    seen = {word.lower() for word in existing_words if word}
    for word in top_n_list('en', max(target_count * 2, target_count)):
        normalized = _normalize_word(word)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        generated.append({
            'word': normalized,
            'phonetic': None,
            'synonym': None,
            'antonym': None,
            'meaning_en': f'Common English vocabulary word: {normalized}.',
            'meaning_vi': 'Từ vựng tiếng Anh thông dụng.',
            'example_sentence': f'Practice using {normalized} in a simple sentence.',
            'exam_type': None,
            'difficulty_level': None,
            'category': 'generated',
        })
        if len(existing_words) + len(generated) >= target_count:
            break
    return generated


def _build_vocab_items(seed_dir, target_count=TARGET_VOCAB_COUNT):
    curated = _load_curated_vocab(seed_dir)
    existing_words = [item['word'] for item in curated]
    if len(curated) >= target_count:
        return curated[:target_count]

    generated = _generate_vocab_pool(target_count, existing_words)
    combined = curated + generated
    return combined[:target_count]


def _build_vocab_cards(items):
    cards = []
    for index, item in enumerate(items):
        difficulty = item.get('difficulty_level')
        if not difficulty:
            if len(item.get('word', '')) <= 4:
                difficulty = 'B1'
            elif len(item.get('word', '')) <= 6:
                difficulty = 'B2'
            elif len(item.get('word', '')) <= 8:
                difficulty = 'C1'
            else:
                difficulty = 'C2'
        exam_type = item.get('exam_type')
        if not exam_type:
            exam_type = ['IELTS', 'TOEIC', 'TOEFL', 'VSTEP'][index % 4]

        cards.append(VocabularyCard(
            word=item.get('word'),
            phonetic=item.get('phonetic'),
            synonym=item.get('synonym'),
            antonym=item.get('antonym'),
            meaning_en=item.get('meaning_en'),
            meaning_vi=item.get('meaning_vi'),
            example_sentence=item.get('example_sentence'),
            exam_type=_parse_enum(ExamType, exam_type),
            difficulty_level=_parse_enum(BandLevel, difficulty),
            category=item.get('category'),
        ))
    return cards


def load_seed_data():
    db = get_session()
    try:
        seed_dir = os.path.join(os.path.dirname(__file__))
        items = _build_vocab_items(seed_dir, TARGET_VOCAB_COUNT)
        existing_words = {
            row[0].lower()
            for row in db.query(VocabularyCard.word).all()
            if row and row[0]
        }
        missing_items = [item for item in items if item['word'] not in existing_words]
        if missing_items:
            db.add_all(_build_vocab_cards(missing_items))

        # --- Backfill existing cards with curated synonym/antonym/phonetic ---
        curated = _load_curated_vocab(seed_dir)
        for curated_item in curated:
            w = curated_item['word']
            if w in existing_words:
                card = db.query(VocabularyCard).filter_by(word=w).first()
                if card:
                    updated = False
                    if not card.synonym and curated_item.get('synonym'):
                        card.synonym = curated_item['synonym']
                        updated = True
                    if not card.antonym and curated_item.get('antonym'):
                        card.antonym = curated_item['antonym']
                        updated = True
                    if not card.phonetic and curated_item.get('phonetic'):
                        card.phonetic = curated_item['phonetic']
                        updated = True
                    if curated_item.get('meaning_en') and (
                        not card.meaning_en
                        or 'common english vocabulary' in (card.meaning_en or '').lower()
                    ):
                        card.meaning_en = curated_item['meaning_en']
                        updated = True
                    if curated_item.get('example_sentence') and (
                        not card.example_sentence
                        or 'practice using' in (card.example_sentence or '').lower()
                    ):
                        card.example_sentence = curated_item['example_sentence']
                        updated = True
                    if curated_item.get('category') and not card.category:
                        card.category = curated_item['category']
                        updated = True
                    if updated:
                        db.commit()
        # -------------------------------------------------------------------

        db.commit()
    finally:
        db.close()
