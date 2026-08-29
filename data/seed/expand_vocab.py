"""Expand vocab.json toward a target size (default 5000 entries).

Data sources per word:
  * Definition / example / part-of-speech / IPA : Free Dictionary API
  * IPA fallback                                : eng_to_ipa (offline)
  * Synonym / antonym                           : Datamuse API
  * Vietnamese meaning                          : Google translation

The script is resumable: it loads the current vocab.json, skips words that
already exist, appends new validated entries, and writes progress to disk
every few words. Re-run it to continue where it left off.

Usage:
    python data/seed/expand_vocab.py [target_count]
"""

import json
import os
import sys
import time

import eng_to_ipa
import requests
from deep_translator import GoogleTranslator
from wordfreq import top_n_list, zipf_frequency

HERE = os.path.dirname(os.path.abspath(__file__))
VOCAB_PATH = os.path.join(HERE, "vocab.json")
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
CANDIDATE_POOL = 60000
SAVE_EVERY = 25

POS_CATEGORY = {
    "noun": "Nouns",
    "verb": "Verbs",
    "adjective": "Adjectives",
    "adverb": "Adverbs",
    "preposition": "Prepositions",
    "conjunction": "Conjunctions",
    "pronoun": "Pronouns",
    "interjection": "Interjections",
    "determiner": "Determiners",
    "numeral": "Numbers",
}

session = requests.Session()
_translator = GoogleTranslator(source="en", target="vi")


def cefr_level(word):
    z = zipf_frequency(word, "en")
    if z >= 5.5:
        return "A1"
    if z >= 5.0:
        return "A2"
    if z >= 4.3:
        return "B1"
    if z >= 3.5:
        return "B2"
    if z >= 2.7:
        return "C1"
    return "C2"


def free_dict(word):
    try:
        resp = session.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=10
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, list) or not data:
            return None
        entry = data[0]
        if entry.get("word", "").lower() != word:
            return None
        ipa = None
        for phon in entry.get("phonetics", []):
            text = (phon.get("text") or "").strip()
            if text:
                ipa = text
                break
        pos = None
        definition = None
        example = None
        for meaning in entry.get("meanings", []):
            if pos is None:
                pos = meaning.get("partOfSpeech")
            for defn in meaning.get("definitions", []):
                if not definition and defn.get("definition"):
                    definition = defn["definition"]
                if not example and defn.get("example"):
                    example = defn["example"]
            if definition:
                break
        return {"ipa": ipa, "pos": pos, "definition": definition, "example": example}
    except Exception:
        return None


def datamuse_first(params, src):
    try:
        resp = session.get("https://api.datamuse.com/words", params=params, timeout=8)
        for item in resp.json():
            candidate = item.get("word", "").lower()
            if candidate and candidate != src and candidate.isalpha() and " " not in candidate:
                return candidate
    except Exception:
        pass
    return None


def translate_vi(word):
    for _ in range(3):
        try:
            result = _translator.translate(word)
            if result:
                return result.strip()
        except Exception:
            time.sleep(2.0)
    return None


def normalize_ipa(ipa):
    if not ipa:
        return None
    ipa = ipa.strip()
    if not ipa:
        return None
    ipa = ipa.strip("/")
    return f"/{ipa}/"


def main():
    with open(VOCAB_PATH, encoding="utf-8") as handle:
        vocab = json.load(handle)
    existing = {entry["word"].lower() for entry in vocab}
    print(f"start: {len(vocab)} entries, target {TARGET}", flush=True)

    candidates = [
        w.lower()
        for w in top_n_list("en", CANDIDATE_POOL)
        if w.isalpha() and len(w) >= 3
    ]

    added = 0
    translate_failures = 0
    for word in candidates:
        if len(vocab) >= TARGET:
            break
        if word in existing:
            continue

        info = free_dict(word)
        if not info or not info["definition"]:
            continue

        vi = translate_vi(word)
        if not vi:
            translate_failures += 1
            if translate_failures >= 30:
                print("Too many translation failures; stopping early.", flush=True)
                break
            continue
        translate_failures = 0
        if vi.lower() == word:
            continue

        ipa = normalize_ipa(info["ipa"])
        if not ipa:
            converted = eng_to_ipa.convert(word)
            if "*" not in converted:
                ipa = normalize_ipa(converted)

        example = info["example"]
        if not example or word not in example.lower():
            example = f"The word {word} appeared several times in the article."

        category = POS_CATEGORY.get((info["pos"] or "").lower(), "General")

        vocab.append(
            {
                "word": word,
                "phonetic": ipa,
                "synonym": datamuse_first({"ml": word, "max": 5}, word),
                "antonym": datamuse_first({"rel_ant": word, "max": 5}, word),
                "meaning_en": info["definition"],
                "meaning_vi": vi,
                "example_sentence": example,
                "exam_type": "IELTS",
                "difficulty_level": cefr_level(word),
                "category": category,
            }
        )
        existing.add(word)
        added += 1

        if added % SAVE_EVERY == 0:
            with open(VOCAB_PATH, "w", encoding="utf-8") as handle:
                json.dump(vocab, handle, ensure_ascii=False, indent=2)
            print(f"progress: {len(vocab)} entries (+{added})", flush=True)

    with open(VOCAB_PATH, "w", encoding="utf-8") as handle:
        json.dump(vocab, handle, ensure_ascii=False, indent=2)
    print(f"final: {len(vocab)} entries (+{added})", flush=True)


if __name__ == "__main__":
    main()
