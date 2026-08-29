"""IELTS-style reading test logic: loading, grading and band conversion.

A reading test is composed of several passages, each containing a list of
questions. Question types mirror the IELTS Academic Reading paper:

    mcq         - multiple choice, one correct option
    tfng        - TRUE / FALSE / NOT GIVEN
    ynng        - YES / NO / NOT GIVEN
    matching    - matching headings / information (choose one option)
    completion  - sentence / summary / short-answer completion (typed)
"""

import json
import os
import re

_SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed", "reading_tests.json")

TFNG_OPTIONS = ["TRUE", "FALSE", "NOT GIVEN"]
YNNG_OPTIONS = ["YES", "NO", "NOT GIVEN"]

# IELTS Academic Reading raw-score (out of 40) to band conversion.
# Each tuple is (minimum_raw_score, band). Checked from highest to lowest.
_BAND_TABLE = [
    (39, 9.0),
    (37, 8.5),
    (35, 8.0),
    (33, 7.5),
    (30, 7.0),
    (27, 6.5),
    (23, 6.0),
    (19, 5.5),
    (15, 5.0),
    (13, 4.5),
    (10, 4.0),
    (8, 3.5),
    (6, 3.0),
    (4, 2.5),
    (3, 2.0),
    (2, 1.5),
    (1, 1.0),
]


def load_tests(path=None):
    """Return the list of reading tests defined in the seed file."""
    seed_path = path or _SEED_PATH
    with open(seed_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_test(test_id=None, path=None):
    """Return a single test by id, or the first test if *test_id* is None."""
    tests = load_tests(path)
    if not tests:
        return None
    if test_id is None:
        return tests[0]
    for test in tests:
        if test.get("id") == test_id:
            return test
    return tests[0]


def iter_questions(test):
    """Yield every question in a test, in passage order."""
    for passage in test.get("passages", []):
        for question in passage.get("questions", []):
            yield question


def total_questions(test):
    return sum(len(p.get("questions", [])) for p in test.get("passages", []))


def _normalise_text(value):
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_correct(question, user_answer):
    """Return True if *user_answer* is acceptable for *question*."""
    if user_answer is None or str(user_answer).strip() == "":
        return False

    answer = question.get("answer")
    qtype = question.get("type", "mcq")

    if qtype == "completion":
        accepted = answer if isinstance(answer, list) else [answer]
        normalised_user = _normalise_text(user_answer)
        return any(_normalise_text(a) == normalised_user for a in accepted)

    # mcq / matching / tfng / ynng: exact match, case-insensitive for the
    # true/false/yes/no families where the UI supplies fixed labels.
    if isinstance(answer, list):
        return any(_normalise_text(a) == _normalise_text(user_answer) for a in answer)
    return _normalise_text(answer) == _normalise_text(user_answer)


def grade(test, answers):
    """Grade a mapping of {question_id: user_answer} against *test*.

    Returns a dict with the raw score, total, band and a per-question review.
    """
    review = []
    raw = 0
    for question in iter_questions(test):
        qid = question.get("id")
        user_answer = answers.get(qid)
        correct = is_correct(question, user_answer)
        if correct:
            raw += 1
        review.append({
            "id": qid,
            "number": question.get("number"),
            "type": question.get("type"),
            "text": question.get("text"),
            "user_answer": user_answer,
            "correct_answer": question.get("answer"),
            "is_correct": correct,
            "explanation": question.get("explanation"),
        })
    total = total_questions(test)
    return {
        "raw": raw,
        "total": total,
        "band": raw_to_band(raw, total),
        "review": review,
    }


def raw_to_band(raw, total=40):
    """Convert a raw score to an IELTS band.

    Scores are scaled to the standard 40-question paper before conversion so
    that shorter practice tests still map onto the official band table.
    """
    if total <= 0:
        return 0.0
    scaled = round(raw * 40 / total)
    for minimum, band in _BAND_TABLE:
        if scaled >= minimum:
            return band
    return 0.0
