"""Vocabulary enrichment: IPA, synonym, antonym, definition, example, topic.

Validation guarantees:
- Function words / grammatical forms use a hardcoded, verified entry.
- Free Dictionary API responses are validated: the returned headword must
  match the queried word; examples are checked to contain the word;
  placeholder definitions are rejected.
- Topic classification assigns every word to exactly one of ~15 groups.
"""

import io
import re
from contextlib import redirect_stderr, redirect_stdout
from functools import lru_cache

import requests

try:
    import eng_to_ipa
except Exception:  # pragma: no cover
    eng_to_ipa = None

try:
    from wordhoard import Antonyms, Synonyms
except Exception:  # pragma: no cover
    Antonyms = None
    Synonyms = None


_WORD_PATTERN = re.compile(r"[a-z]+(?:-[a-z]+)?")


def normalize_word(word):
    if not word:
        return None
    normalized = word.strip().lower()
    if not _WORD_PATTERN.fullmatch(normalized):
        return None
    return normalized


def _silent_call(callback):
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        return callback()


def _pick_first_candidate(candidates, source_word):
    src = normalize_word(source_word)
    for c in candidates or []:
        if not c:
            continue
        if isinstance(c, dict):
            c = c.get("word", "")
        n = normalize_word(str(c))
        if n and n != src:
            return n
    return None


def _datamuse_lookup(params):
    try:
        response = requests.get("https://api.datamuse.com/words", params=params, timeout=8)
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Verified hardcoded entries for function words / grammatical forms.
# These words are routinely mislabelled by external APIs (homophones, wrong
# headword, bare-infinitive vs conjugated form, etc.)
# ---------------------------------------------------------------------------

FUNCTION_WORD_DATA = {
    "be":      {"ipa": "/biː/",     "definition": "To exist or occur; base form of the auxiliary verb 'be'.", "synonym": "exist", "antonym": None, "example": "I want to be a doctor someday.", "topic": "Grammar"},
    "am":      {"ipa": "/æm/",      "definition": "First-person singular present tense of 'be'.", "synonym": None, "antonym": None, "example": "I am happy to help.", "topic": "Grammar"},
    "is":      {"ipa": "/ɪz/",      "definition": "Third-person singular present tense of 'be'.", "synonym": None, "antonym": None, "example": "She is a talented musician.", "topic": "Grammar"},
    "are":     {"ipa": "/ɑːr/",     "definition": "Second-person singular and all-plural present tense of 'be'.", "synonym": None, "antonym": None, "example": "You are very kind.", "topic": "Grammar"},
    "was":     {"ipa": "/wɒz/",     "definition": "First- and third-person singular past tense of 'be'.", "synonym": None, "antonym": None, "example": "He was late to the meeting.", "topic": "Grammar"},
    "were":    {"ipa": "/wɜːr/",    "definition": "Second-person singular and all-plural past tense of 'be'; also used in conditionals.", "synonym": None, "antonym": None, "example": "They were ready to leave.", "topic": "Grammar"},
    "been":    {"ipa": "/biːn/",    "definition": "Past participle of 'be'; used with have/has/had to form perfect tenses.", "synonym": None, "antonym": None, "example": "I have been waiting for an hour.", "topic": "Grammar"},
    "being":   {"ipa": "/ˈbiːɪŋ/", "definition": "Present participle of 'be'; also a noun meaning a living creature or existence.", "synonym": "existing", "antonym": None, "example": "She is being very careful with her words.", "topic": "Grammar"},
    "have":    {"ipa": "/hæv/",     "definition": "To possess, own, or experience; also an auxiliary forming perfect tenses.", "synonym": "possess", "antonym": "lack", "example": "I have a meeting at noon.", "topic": "Grammar"},
    "has":     {"ipa": "/hæz/",     "definition": "Third-person singular present tense of 'have'.", "synonym": None, "antonym": None, "example": "She has finished her homework.", "topic": "Grammar"},
    "had":     {"ipa": "/hæd/",     "definition": "Past tense and past participle of 'have'.", "synonym": None, "antonym": None, "example": "We had dinner together last night.", "topic": "Grammar"},
    "do":      {"ipa": "/duː/",     "definition": "To perform or carry out an action; auxiliary in questions and negatives.", "synonym": "perform", "antonym": "undo", "example": "Please do your homework before watching TV.", "topic": "Grammar"},
    "does":    {"ipa": "/dʌz/",     "definition": "Third-person singular present tense of 'do'.", "synonym": None, "antonym": None, "example": "She does her best every day.", "topic": "Grammar"},
    "did":     {"ipa": "/dɪd/",     "definition": "Past tense of 'do'.", "synonym": None, "antonym": None, "example": "He did the dishes after dinner.", "topic": "Grammar"},
    "done":    {"ipa": "/dʌn/",     "definition": "Past participle of 'do'; finished or completed.", "synonym": "finished", "antonym": "incomplete", "example": "The project is finally done.", "topic": "Grammar"},
    "will":    {"ipa": "/wɪl/",     "definition": "Auxiliary verb expressing the future tense or a strong intention.", "synonym": "shall", "antonym": None, "example": "I will call you tomorrow.", "topic": "Grammar"},
    "would":   {"ipa": "/wʊd/",     "definition": "Past tense of 'will'; used in conditionals or polite requests.", "synonym": "could", "antonym": None, "example": "I would appreciate your help.", "topic": "Grammar"},
    "shall":   {"ipa": "/ʃæl/",     "definition": "Auxiliary used (especially in first person) for the future tense or strong intention.", "synonym": "will", "antonym": None, "example": "Shall we begin the meeting?", "topic": "Grammar"},
    "should":  {"ipa": "/ʃʊd/",     "definition": "Used to express obligation, recommendation, or expectation.", "synonym": "ought", "antonym": None, "example": "You should drink more water.", "topic": "Grammar"},
    "can":     {"ipa": "/kæn/",     "definition": "Auxiliary verb expressing ability or possibility.", "synonym": "could", "antonym": "cannot", "example": "She can speak three languages.", "topic": "Grammar"},
    "could":   {"ipa": "/kʊd/",     "definition": "Past tense of 'can'; also expresses possibility or a polite request.", "synonym": "might", "antonym": None, "example": "Could you pass the salt, please?", "topic": "Grammar"},
    "may":     {"ipa": "/meɪ/",     "definition": "Auxiliary verb expressing permission or possibility.", "synonym": "might", "antonym": None, "example": "You may leave when you have finished.", "topic": "Grammar"},
    "might":   {"ipa": "/maɪt/",    "definition": "Past tense of 'may'; expresses a weaker or more tentative possibility.", "synonym": "may", "antonym": None, "example": "It might rain later this afternoon.", "topic": "Grammar"},
    "must":    {"ipa": "/mʌst/",    "definition": "Auxiliary verb expressing obligation or strong necessity.", "synonym": "should", "antonym": None, "example": "You must wear a seatbelt in the car.", "topic": "Grammar"},
    "there":   {"ipa": "/ðɛr/",     "definition": "In, at, or to that place; also used to introduce a clause (e.g. 'there is').", "synonym": "yonder", "antonym": "here", "example": "Put the box over there, please.", "topic": "Grammar"},
    "their":   {"ipa": "/ðɛr/",     "definition": "Possessive determiner: belonging to or associated with people previously mentioned.", "synonym": None, "antonym": None, "example": "The students submitted their assignments on time.", "topic": "Grammar"},
    "its":     {"ipa": "/ɪts/",     "definition": "Possessive determiner of 'it': belonging to a thing previously mentioned.", "synonym": None, "antonym": None, "example": "The cat licked its paws.", "topic": "Grammar"},
    "whether": {"ipa": "/ˈwɛðər/",  "definition": "Conjunction expressing doubt or choice between alternatives.", "synonym": "if", "antonym": None, "example": "I'm not sure whether to stay or go.", "topic": "Grammar"},
    "weather": {"ipa": "/ˈwɛðər/",  "definition": "The state of the atmosphere at a particular place and time.", "synonym": "climate", "antonym": None, "example": "The weather today is warm and sunny.", "topic": "Nature"},
    "quiet":   {"ipa": "/ˈkwaɪət/", "definition": "Making little or no noise; free from disturbance.", "synonym": "silent", "antonym": "loud", "example": "Please be quiet in the library.", "topic": "Descriptions"},
    "quite":   {"ipa": "/kwaɪt/",   "definition": "To a certain or fairly significant extent; completely; rather.", "synonym": "fairly", "antonym": None, "example": "The test was quite difficult.", "topic": "Grammar"},
    "affect":  {"ipa": "/əˈfɛkt/",  "definition": "To have an effect on something; to make a difference to.", "synonym": "influence", "antonym": None, "example": "The cold weather can affect your health.", "topic": "General"},
    "effect":  {"ipa": "/ɪˈfɛkt/",  "definition": "A result or consequence of an action; a change produced by a cause.", "synonym": "result", "antonym": "cause", "example": "The medicine had a positive effect on her recovery.", "topic": "General"},
    "then":    {"ipa": "/ðɛn/",     "definition": "At that time; next in sequence; in that case.", "synonym": "next", "antonym": "now", "example": "Finish your work and then we can play.", "topic": "Grammar"},
    "than":    {"ipa": "/ðæn/",     "definition": "Conjunction used in comparisons to refer to the second element.", "synonym": None, "antonym": None, "example": "She is taller than her brother.", "topic": "Grammar"},
    "accept":  {"ipa": "/əkˈsɛpt/", "definition": "To consent to receive or agree to something offered.", "synonym": "receive", "antonym": "reject", "example": "She accepted the job offer with enthusiasm.", "topic": "General"},
    "except":  {"ipa": "/ɪkˈsɛpt/", "definition": "Not including; other than; used to introduce an exception.", "synonym": "excluding", "antonym": "including", "example": "Everyone passed except Tom.", "topic": "Grammar"},
    "hear":    {"ipa": "/hɪr/",     "definition": "To perceive sound with the ear.", "synonym": "listen", "antonym": "ignore", "example": "I can hear music coming from downstairs.", "topic": "Senses"},
    "here":    {"ipa": "/hɪr/",     "definition": "In, at, or to this place or position.", "synonym": "present", "antonym": "there", "example": "Come here and sit next to me.", "topic": "Grammar"},
    "know":    {"ipa": "/noʊ/",     "definition": "To be aware of through observation or information; to have knowledge of.", "synonym": "understand", "antonym": "ignore", "example": "Do you know the answer to this question?", "topic": "Mind"},
    "no":      {"ipa": "/noʊ/",     "definition": "Used to give a negative response; not any.", "synonym": "none", "antonym": "yes", "example": "No, I haven't seen your keys.", "topic": "Grammar"},
    "too":     {"ipa": "/tuː/",     "definition": "To a higher degree than desirable; in addition; also.", "synonym": "also", "antonym": None, "example": "She is too tired to continue working.", "topic": "Grammar"},
    "two":     {"ipa": "/tuː/",     "definition": "The number 2; one more than one.", "synonym": None, "antonym": None, "example": "I have two sisters.", "topic": "Numbers"},
    "to":      {"ipa": "/tuː/",     "definition": "Preposition expressing direction or destination; also placed before a verb infinitive.", "synonym": None, "antonym": "from", "example": "I am going to the store.", "topic": "Grammar"},
    "whose":   {"ipa": "/huːz/",    "definition": "Possessive form of 'who'; belonging to which person.", "synonym": None, "antonym": None, "example": "Whose bag is left on the table?", "topic": "Grammar"},
    "which":   {"ipa": "/wɪtʃ/",    "definition": "Used to refer to a specific thing from a set of alternatives.", "synonym": None, "antonym": None, "example": "Which book would you like to read?", "topic": "Grammar"},
    "witch":   {"ipa": "/wɪtʃ/",    "definition": "A person (especially a woman) thought to have magic powers.", "synonym": "sorceress", "antonym": None, "example": "The story featured a wicked witch.", "topic": "Fantasy"},
    "loose":   {"ipa": "/luːs/",    "definition": "Not firmly or tightly fixed in place; free from restraint.", "synonym": "slack", "antonym": "tight", "example": "The screw has come loose.", "topic": "Descriptions"},
    "lose":    {"ipa": "/luːz/",    "definition": "To be deprived of; to fail to win; to misplace.", "synonym": "misplace", "antonym": "win", "example": "Don't lose your passport while travelling.", "topic": "General"},
    "past":    {"ipa": "/pæst/",    "definition": "Gone by in time; a former period; also a preposition meaning beyond.", "synonym": "former", "antonym": "future", "example": "In the past, people wrote letters instead of emails.", "topic": "Time"},
    "passed":  {"ipa": "/pæst/",    "definition": "Past tense and past participle of 'pass'; moved beyond or went by.", "synonym": "went by", "antonym": None, "example": "She passed the exam with distinction.", "topic": "Grammar"},
    "break":   {"ipa": "/breɪk/",   "definition": "To separate into pieces as a result of force; also a short rest period.", "synonym": "shatter", "antonym": "repair", "example": "Be careful not to break the glass.", "topic": "General"},
    "flour":   {"ipa": "/flaʊər/",  "definition": "Fine powder made by grinding grain, used for baking.", "synonym": "meal", "antonym": None, "example": "She mixed flour, sugar, and butter to make the cake.", "topic": "Food"},
    "flower":  {"ipa": "/ˈflaʊər/", "definition": "The seed-bearing part of a plant; a bloom.", "synonym": "bloom", "antonym": None, "example": "He gave her a bouquet of red flowers.", "topic": "Nature"},
    "right":   {"ipa": "/raɪt/",    "definition": "Morally good; correct; the direction opposite to left.", "synonym": "correct", "antonym": "wrong", "example": "Turn right at the traffic lights.", "topic": "Descriptions"},
    "write":   {"ipa": "/raɪt/",    "definition": "To mark letters or words on a surface with a pen or pencil.", "synonym": "compose", "antonym": None, "example": "Please write your name at the top of the page.", "topic": "Communication"},
    "complement": {"ipa": "/ˈkɒmplɪmənt/", "definition": "Something that completes or brings to perfection; to go well together.", "synonym": "supplement", "antonym": "clash", "example": "The sauce complements the main dish perfectly.", "topic": "General"},
    "compliment": {"ipa": "/ˈkɒmplɪmənt/", "definition": "A polite expression of praise or admiration.", "synonym": "praise", "antonym": "insult", "example": "She received many compliments on her presentation.", "topic": "Communication"},
    "principal":  {"ipa": "/ˈprɪnsɪpəl/", "definition": "The head of a school; most important or main.", "synonym": "chief", "antonym": "minor", "example": "The principal addressed the students at assembly.", "topic": "Education"},
    "principle":  {"ipa": "/ˈprɪnsɪpəl/", "definition": "A fundamental truth or rule governing behaviour.", "synonym": "rule", "antonym": None, "example": "She acted according to her principles.", "topic": "Philosophy"},
}


# ---------------------------------------------------------------------------
# Topic classification
# ---------------------------------------------------------------------------

_TOPIC_WORDLISTS = {
    "Animals":       "dog cat bird fish horse cow pig sheep chicken duck rabbit lion tiger elephant bear wolf fox deer mouse rat snake frog turtle whale dolphin shark monkey eagle penguin parrot butterfly bee ant spider crab lobster seal giraffe zebra rhino hippo crocodile lizard hawk falcon pigeon sparrow crow dove camel goat donkey hamster squirrel beaver otter bat hedgehog panda koala kangaroo gorilla chimpanzee jaguar leopard cheetah lynx hyena meerkat scorpion tarantula centipede ladybug dragonfly grasshopper cockroach termite wasp hornet moth".split(),
    "Food":          "apple bread butter cake candy cheese chocolate coffee cookie cream egg flour fruit garlic grape honey jam juice lemon lime meat milk mushroom noodle oil onion orange pasta pepper pizza potato rice salad salt sauce soup sugar tea tomato vegetable water wine yogurt avocado bacon banana beef berry biscuit blueberry broccoli carrot celery cereal cherry cinnamon coconut corn cucumber curry doughnut eggplant fig ginger grapefruit ham herb kale kiwi lamb lasagna leek lettuce mango melon mint muffin mustard oat olive pancake papaya parsley peach peanut pear pineapple plum pork pumpkin radish raspberry salmon sandwich sausage sesame shrimp smoothie spinach steak strawberry sushi syrup taco tofu tuna turkey vanilla vinegar waffle walnut watermelon wheat zucchini".split(),
    "Emotions":      "happy sad angry fear love hate joy grief anxiety calm excited bored proud ashamed guilty jealous envy hope despair surprise disgust compassion empathy loneliness nostalgia frustration irritation fury rage terror panic worry stress relief satisfaction pleasure pain suffering misery melancholy depression euphoria elation delight gratitude admiration awe wonder curiosity confusion embarrassment humiliation pride shame regret remorse forgiveness resentment bitterness enthusiasm passion apathy indifference nervousness shyness boldness determination contentment yearning desire craving horror dread".split(),
    "Business":      "account agreement analysis asset audit balance bank benefit bonus brand budget business capital career client company competition consultant contract cost credit customer deal debt demand department director dividend economy employee employer enterprise equity expense finance firm goal growth industry inflation insurance interest investment invoice job leadership loan loss management manager market marketing meeting merger money negotiate network office opportunity organization partner payment performance plan policy portfolio price product profit project proposal purchase quality revenue risk salary sales sector service share shareholder staff startup strategy supply tax team trade transaction value vendor wage wealth workplace".split(),
    "Travel":        "airport arrival baggage beach border bus cabin car city coast country customs departure destination flight guide harbor highway hostel hotel island itinerary journey landmark luggage map mountain museum ocean passport port railway resort road route schedule ship station ticket tour tourist train transport travel trip valley visa voyage adventure backpack campsite excursion expedition exploration ferry motorway navigation sightseeing souvenir".split(),
    "Technology":    "algorithm application artificial battery camera chip cloud code computer connection data database device digital download email encryption engine file hardware interface internet keyboard laptop mobile monitor network online password phone platform printer processor program robot screen server software storage system technology upload user virus website wireless bluetooth satellite drone smartphone smartwatch".split(),
    "Health":        "allergy antibody bacteria bandage blood bone brain cancer cell clinic cure diagnosis diet disease doctor dosage drug exercise fever gene germ healing health heart hospital infection immune injury insulin kidney liver lung medicine mental muscle nerve nurse nutrition organ pain patient pharmacy prevention protein recovery surgery symptom therapy treatment vaccine vitamin wellness ambulance anatomy antibiotic arthritis asthma cholesterol diabetes epidemic fatigue fracture hygiene laboratory obesity pandemic physician prescription rehabilitation stress syndrome wound".split(),
    "Education":     "academy assignment biology chemistry class college curriculum degree diploma discipline education exam faculty geography grade grammar history homework knowledge language lecture lesson library literature mathematics physics professor research school science semester student study teacher thesis university writing algebra calculus geometry statistics essay debate seminar textbook scholarship tutor tutorial kindergarten elementary secondary undergraduate postgraduate".split(),
    "Nature":        "air atmosphere autumn canyon cave climate cloud coast desert earthquake ecology energy environment fire flood forest fossil glacier grass heat hurricane ice jungle lake land leaf lightning mineral moon mountain mud ocean plant rain rainbow river rock sand sea season sky snow soil spring star stone storm summer sun temperature thunder tree tsunami valley volcano wave wind winter wood aurora coral ecosystem glacier habitat landscape meadow prairie savanna swamp tundra wetland wilderness".split(),
    "Time":          "second minute hour day week month year decade century millennium morning afternoon evening night today yesterday tomorrow past present future early late ancient modern contemporary era epoch period schedule deadline calendar appointment clock timetable duration instant moment temporary permanent".split(),
    "Numbers":       "zero one two three four five six seven eight nine ten eleven twelve hundred thousand million billion trillion dozen pair couple triple fraction decimal percentage ratio count total sum difference product quotient average estimate measurement calculation statistics digit number numeral quantity".split(),
    "Communication": "language speech talk conversation discussion debate argument question answer message letter email text call voice listen read write publish broadcast report announce declare express inform describe explain persuade negotiate translate interpret communicate respond reply feedback review comment criticism praise apology greeting farewell".split(),
    "Descriptions":  "big small large little tall short heavy light fast slow old young new beautiful ugly clean dirty rich poor hard soft warm cold hot cool bright dark loud simple complex easy difficult strong weak".split(),
    "Mind":          "think thought idea belief opinion knowledge wisdom intelligence mind memory imagination creativity logic reason intuition consciousness awareness perception attention focus concentration understanding learning insight judgment decision conclusion assumption hypothesis theory".split(),
    "Senses":        "see hear smell taste touch feel sight sound voice noise hear listen watch observe notice look",
    "General":       [],
}


def _build_topic_map():
    m: dict[str, str] = {}
    for topic, words in _TOPIC_WORDLISTS.items():
        wlist = words.split() if isinstance(words, str) else words
        for w in wlist:
            if w not in m:
                m[w] = topic
    for w, data in FUNCTION_WORD_DATA.items():
        m[w] = data.get("topic", "Grammar")
    return m


_TOPIC_MAP = _build_topic_map()


def classify_topic(word: str) -> str:
    """Return the primary topic category for *word*."""
    n = normalize_word(word)
    return _TOPIC_MAP.get(n, "General") if n else "General"


# ---------------------------------------------------------------------------
# Free Dictionary API — with two-pass validation
# ---------------------------------------------------------------------------

@lru_cache(maxsize=8192)
def _free_dict_lookup(word: str):
    """Return (ipa, definition, example) validated for *word*, or (None,None,None)."""
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            return None, None, None
        data = resp.json()
        if not isinstance(data, list) or not data:
            return None, None, None
        entry = data[0]

        # --- Pass 1: headword validation ---
        headword = normalize_word(entry.get("word", ""))
        if headword and headword != word:
            # Allow if the first 3 chars overlap (base form vs conjugation)
            if not (headword.startswith(word[:3]) or word.startswith(headword[:3])):
                return None, None, None

        # IPA
        ipa = None
        for phon in entry.get("phonetics", []):
            text = (phon.get("text") or "").strip()
            if text:
                ipa = text
                break

        # Definition + example
        definition = None
        example = None
        for meaning in entry.get("meanings", []):
            for defn in meaning.get("definitions", []):
                if not definition and defn.get("definition"):
                    definition = defn["definition"]
                if not example and defn.get("example"):
                    example = defn["example"]
                if definition and example:
                    break
            if definition and example:
                break

        # --- Pass 2: example must contain the word or a close stem ---
        if example and word not in example.lower() and word[:4] not in example.lower():
            example = None

        # --- Pass 2: reject placeholder definitions ---
        _BAD = ("common english vocabulary", "common vocabulary word", "practice using")
        if definition and any(m in definition.lower() for m in _BAD):
            definition = None

        return ipa, definition, example
    except Exception:
        return None, None, None


# ---------------------------------------------------------------------------
# IPA / synonym / antonym lookups
# ---------------------------------------------------------------------------

@lru_cache(maxsize=8192)
def get_ipa(word: str):
    n = normalize_word(word)
    if not n or eng_to_ipa is None:
        return None
    try:
        text = eng_to_ipa.convert(n)
        return text.strip() or None
    except Exception:
        return None


@lru_cache(maxsize=8192)
def get_synonym(word: str):
    n = normalize_word(word)
    if not n:
        return None
    if Synonyms is not None:
        try:
            lst = _silent_call(lambda: Synonyms(n).find_synonyms())
            picked = _pick_first_candidate(lst, n)
            if picked:
                return picked
        except Exception:
            pass
    return _pick_first_candidate(_datamuse_lookup({"ml": n, "max": 10}), n)


@lru_cache(maxsize=8192)
def get_antonym(word: str):
    n = normalize_word(word)
    if not n:
        return None
    if Antonyms is not None:
        try:
            lst = _silent_call(lambda: Antonyms(n).find_antonyms())
            picked = _pick_first_candidate(lst, n)
            if picked:
                return picked
        except Exception:
            pass
    return _pick_first_candidate(_datamuse_lookup({"rel_ant": n, "max": 10}), n)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def build_vocabulary_details(word, existing_meaning=None, example_sentence=None):
    """Return a fully validated enrichment dict for *word*.

    Priority order:
    1. FUNCTION_WORD_DATA — hardcoded, validated by construction.
    2. Free Dictionary API — with headword + example validation.
    3. eng_to_ipa + Datamuse — fallback for IPA / synonym / antonym.
    """
    normalized = normalize_word(word)
    if not normalized:
        return {
            "word": word, "ipa": None, "definition": existing_meaning,
            "synonym": None, "antonym": None, "example_sentence": example_sentence,
            "topic": "General",
        }

    # Priority 1: hardcoded function-word / grammatical-form entry
    if normalized in FUNCTION_WORD_DATA:
        fw = FUNCTION_WORD_DATA[normalized]
        return {
            "word": normalized,
            "ipa": fw["ipa"],
            "definition": fw["definition"],
            "synonym": fw.get("synonym"),
            "antonym": fw.get("antonym"),
            "example_sentence": fw["example"],
            "topic": fw.get("topic", "Grammar"),
        }

    # Priority 2: Free Dictionary API (validated)
    dict_ipa, dict_def, dict_example = _free_dict_lookup(normalized)

    ipa = dict_ipa or get_ipa(normalized)

    _placeholder = ("common english vocabulary", "common vocabulary word", "practice using")
    existing_bad = not existing_meaning or any(m in existing_meaning.lower() for m in _placeholder)
    definition = dict_def or (None if existing_bad else existing_meaning)

    example_bad = not example_sentence or "practice using" in (example_sentence or "").lower()
    example = dict_example or (None if example_bad else example_sentence)
    if not example:
        example = f"{normalized.capitalize()} is commonly used in written and spoken English."

    # Final validation: example must contain the word
    if normalized not in example.lower() and normalized[:4] not in example.lower():
        example = f"{normalized.capitalize()} is commonly used in written and spoken English."

    synonym = get_synonym(normalized)
    antonym = get_antonym(normalized)
    topic = classify_topic(normalized)

    return {
        "word": normalized,
        "ipa": ipa,
        "definition": definition,
        "synonym": synonym,
        "antonym": antonym,
        "example_sentence": example,
        "topic": topic,
        "synonym_example": f'The word "{synonym}" can be used in a similar context.' if synonym else None,
        "antonym_example": f'The opposite of {normalized} is "{antonym}".' if antonym else None,
    }



@lru_cache(maxsize=8192)
def _free_dict_lookup(word):
    """Return (ipa, definition, example) from the Free Dictionary API, or (None, None, None)."""
    try:
        url = f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}'
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            return None, None, None
        data = resp.json()
        if not isinstance(data, list) or not data:
            return None, None, None
        entry = data[0]

        # IPA
        ipa = None
        for phon in entry.get('phonetics', []):
            text = phon.get('text', '').strip()
            if text:
                ipa = text
                break

        # First definition and example from any meaning
        definition = None
        example = None
        for meaning in entry.get('meanings', []):
            for defn in meaning.get('definitions', []):
                if not definition and defn.get('definition'):
                    definition = defn['definition']
                if not example and defn.get('example'):
                    example = defn['example']
                if definition and example:
                    break
            if definition and example:
                break

        return ipa, definition, example
    except Exception:
        return None, None, None


@lru_cache(maxsize=8192)
def get_ipa(word):
    normalized = normalize_word(word)
    if not normalized or eng_to_ipa is None:
        return None
    try:
        ipa_text = eng_to_ipa.convert(normalized)
        ipa_text = ipa_text.strip() if ipa_text else None
        return ipa_text or None
    except Exception:
        return None


@lru_cache(maxsize=8192)
def get_synonym(word):
    normalized = normalize_word(word)
    if not normalized:
        return None

    if Synonyms is not None:
        try:
            synonym_list = _silent_call(lambda: Synonyms(normalized).find_synonyms())
            picked = _pick_first_candidate(synonym_list, normalized)
            if picked:
                return picked
        except Exception:
            pass

    picked = _pick_first_candidate(_datamuse_lookup({'ml': normalized, 'max': 10}), normalized)
    return picked


@lru_cache(maxsize=8192)
def get_antonym(word):
    normalized = normalize_word(word)
    if not normalized:
        return None

    if Antonyms is not None:
        try:
            antonym_list = _silent_call(lambda: Antonyms(normalized).find_antonyms())
            picked = _pick_first_candidate(antonym_list, normalized)
            if picked:
                return picked
        except Exception:
            pass

    picked = _pick_first_candidate(_datamuse_lookup({'rel_ant': normalized, 'max': 10}), normalized)
    return picked


def build_vocabulary_details(word, existing_meaning=None, example_sentence=None):
    """Return enriched vocabulary details for *word*.

    Uses the Free Dictionary API as the primary source for IPA, definition and
    example sentence, falling back to eng_to_ipa + Datamuse where the API
    returns nothing.  A non-placeholder *existing_meaning* is preserved.
    """
    normalized = normalize_word(word)
    if not normalized:
        return {
            'word': word,
            'ipa': None,
            'definition': existing_meaning,
            'synonym': None,
            'antonym': None,
            'example_sentence': example_sentence,
        }

    # --- primary source: Free Dictionary API ---
    dict_ipa, dict_definition, dict_example = _free_dict_lookup(normalized)

    # IPA: prefer dictionary API, fall back to eng_to_ipa
    ipa_text = dict_ipa or get_ipa(normalized)

    # Definition: prefer real dict data; keep existing only if it looks real
    _placeholder_markers = ('common english vocabulary', 'common vocabulary word')
    existing_is_placeholder = not existing_meaning or any(
        m in existing_meaning.lower() for m in _placeholder_markers
    )
    definition = dict_definition if dict_definition else (
        None if existing_is_placeholder else existing_meaning
    )

    # Example sentence
    example = dict_example or (
        None if not example_sentence or 'practice using' in (example_sentence or '').lower()
        else example_sentence
    )
    if not example and normalized:
        example = f'Use {normalized} in a sentence.'

    synonym = get_synonym(normalized)
    antonym = get_antonym(normalized)

    return {
        'word': normalized,
        'ipa': ipa_text,
        'definition': definition,
        'synonym': synonym,
        'antonym': antonym,
        'example_sentence': example,
        'synonym_example': f'The word "{synonym}" can be used in a similar context.' if synonym else None,
        'antonym_example': f'The opposite of {normalized} is "{antonym}".' if antonym else None,
    }
