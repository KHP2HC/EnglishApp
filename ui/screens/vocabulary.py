import customtkinter as ctk
from datetime import date
import random
import threading
from data.database import get_session
from data.models import VocabularyCard, UserVocabularyProgress
from core.srs_engine import SRSEngine
from core.vocabulary_enrichment import build_vocabulary_details, classify_topic
from core.session_manager import record_session, start_session, end_session
from data.models import SessionType
from ui.components.timer_widget import TimerWidget

SESSION_NEW_LIMIT = 20
SESSION_REVIEW_LIMIT = 10


class VocabularyScreen(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.cards_reviewed = 0
        self.cards = []
        self.current_index = 0
        self.show_back = False
        self.current_progress = None
        self.build_ui()
        self.load_cards()

    def build_ui(self):
        self.card_frame = ctk.CTkFrame(self)
        self.card_frame.pack(expand=True, fill="both", padx=20, pady=20)
        # add a timer for the study session
        user_id = getattr(self.app.user, 'id', None)
        try:
            self._session_id = start_session(user_id=user_id, session_type=SessionType.VOCABULARY)
        except Exception:
            self._session_id = None
        self.timer = TimerWidget(self, minutes=25, on_finish=self._on_timer_finish)
        self.timer.pack(pady=6)
        try:
            # auto-start timer
            self.timer.start()
        except Exception:
            pass
        self.card_frame.bind("<Button-1>", self.flip_card)

        self.quality_frame = ctk.CTkFrame(self)
        self.quality_frame.pack(pady=10)
        for quality, label in [(0, "Again"), (2, "Hard"), (3, "Good"), (5, "Easy")]:
            btn = ctk.CTkButton(self.quality_frame, text=label, command=lambda q=quality: self.rate_card(q))
            btn.pack(side="left", padx=5)
        self.quality_frame.pack_forget()

    def _filter_due_cards(self, cards):
        today = date.today()
        due_cards = []
        for card in cards:
            review_date = getattr(card, 'next_review_date', None)
            if isinstance(review_date, str):
                try:
                    review_date = date.fromisoformat(review_date)
                except Exception:
                    review_date = None
            if review_date is None or review_date <= today:
                due_cards.append(card)
        return due_cards

    def _normalize_review_date(self, review_date):
        if isinstance(review_date, str):
            try:
                return date.fromisoformat(review_date)
            except Exception:
                return None
        return review_date

    def _is_learned(self, progress):
        return bool(progress and getattr(progress, 'times_seen', 0) > 0)

    def _is_review_due(self, progress):
        if not progress:
            return False
        if getattr(progress, 'times_seen', 0) >= 20:
            return True
        review_date = self._normalize_review_date(getattr(progress, 'next_review_date', None))
        return review_date is not None and review_date <= date.today()

    def _build_practice_queue(self, cards, progress_by_card_id):
        new_cards = []
        review_cards = []

        for card in cards:
            progress = progress_by_card_id.get(card.id)
            if not self._is_learned(progress):
                new_cards.append(card)
            elif self._is_review_due(progress):
                review_cards.append(card)

        random.shuffle(review_cards)
        return new_cards + review_cards

    def _card_status_text(self, card):
        progress = getattr(self, 'progress_by_card_id', {}).get(getattr(card, 'id', None))
        if not self._is_learned(progress):
            return 'New word'

        times_seen = getattr(progress, 'times_seen', 0) or 0
        review_date = self._normalize_review_date(getattr(progress, 'next_review_date', None))
        if times_seen >= 20:
            return 'Learned and due for random review'
        if review_date and review_date > date.today():
            return f'Learned • review again on {review_date.isoformat()}'
        return 'Learned and due for review'

    def load_cards(self):
        for w in self.card_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.card_frame, text='Loading vocabulary…', font=('Arial', 16)).pack(expand=True)
        threading.Thread(target=self._load_cards_bg, daemon=True).start()

    def _load_cards_bg(self):
        db = get_session()
        try:
            user_id = getattr(self.app.user, 'id', None)
            progress_rows = db.query(UserVocabularyProgress).filter_by(user_id=user_id).all()
            progress_map = {p.card_id: p for p in progress_rows}
            learned_ids = {pid for pid, p in progress_map.items() if self._is_learned(p)}

            new_cards = (
                db.query(VocabularyCard)
                .filter(~VocabularyCard.id.in_(learned_ids))
                .limit(SESSION_NEW_LIMIT)
                .all()
            )

            review_card_ids = [
                pid for pid, p in progress_map.items()
                if self._is_review_due(p)
            ]
            review_cards = []
            if review_card_ids:
                random.shuffle(review_card_ids)
                review_cards = (
                    db.query(VocabularyCard)
                    .filter(VocabularyCard.id.in_(review_card_ids[:SESSION_REVIEW_LIMIT]))
                    .all()
                )

            cards = new_cards + review_cards
        except Exception:
            cards = []
            progress_map = {}
        finally:
            db.close()

        self.after(0, lambda: self._on_cards_loaded(cards, progress_map))

    def _on_cards_loaded(self, cards, progress_map):
        self.progress_by_card_id = progress_map
        self.cards = cards
        self.current_index = 0
        self.show_back = False
        self.current_progress = None
        self.update_card_display()
        # Pre-fetch the next few cards in background while the user reviews card 0.
        for i in range(1, min(5, len(cards))):
            threading.Thread(
                target=self._do_enrich_card, args=(cards[i],), daemon=True
            ).start()

    def _do_enrich_card(self, card):
        """Fetch and persist enrichment data for *card* (safe to call from any thread)."""
        if getattr(card, '_enriched', False):
            return
        db = get_session()
        try:
            stored = db.query(VocabularyCard).filter_by(id=card.id).first()
            if not stored:
                return

            # --- Priority 1: Check hardcoded FUNCTION_WORD_DATA (verified, correct) ---
            from core.vocabulary_enrichment import FUNCTION_WORD_DATA
            fw_data = FUNCTION_WORD_DATA.get(stored.word.lower())
            updated = False
            if fw_data:
                if not stored.phonetic and fw_data.get('ipa'):
                    stored.phonetic = fw_data['ipa']
                    updated = True
                if not stored.synonym and fw_data.get('synonym'):
                    stored.synonym = fw_data['synonym']
                    updated = True
                if not stored.antonym and fw_data.get('antonym'):
                    stored.antonym = fw_data['antonym']
                    updated = True
                if fw_data.get('definition') and (
                    not stored.meaning_en
                    or 'common english vocabulary' in (stored.meaning_en or '').lower()
                ):
                    stored.meaning_en = fw_data['definition']
                    updated = True
                if fw_data.get('example') and (
                    not stored.example_sentence
                    or 'practice using' in (stored.example_sentence or '').lower()
                ):
                    stored.example_sentence = fw_data['example']
                    updated = True
                if fw_data.get('topic') and not stored.category:
                    stored.category = fw_data['topic']
                    updated = True

            # --- Priority 2: Check curated vocab.json for pre-validated data ---
            if not fw_data:
                curated_data = self._lookup_curated_word(stored.word)
                if curated_data:
                    if not stored.phonetic and curated_data.get('phonetic'):
                        stored.phonetic = curated_data['phonetic']
                        updated = True
                    if not stored.synonym and curated_data.get('synonym'):
                        stored.synonym = curated_data['synonym']
                        updated = True
                    if not stored.antonym and curated_data.get('antonym'):
                        stored.antonym = curated_data['antonym']
                        updated = True
                    if curated_data.get('meaning_en') and (
                        not stored.meaning_en
                        or 'common english vocabulary' in (stored.meaning_en or '').lower()
                    ):
                        stored.meaning_en = curated_data['meaning_en']
                        updated = True
                    if curated_data.get('example_sentence') and (
                        not stored.example_sentence
                        or 'practice using' in (stored.example_sentence or '').lower()
                    ):
                        stored.example_sentence = curated_data['example_sentence']
                        updated = True
                    if curated_data.get('category') and not stored.category:
                        stored.category = curated_data['category']
                        updated = True

            # --- Priority 3: Fall back to external API enrichment ---
            if not fw_data and (not curated_data or not all([stored.synonym, stored.antonym, stored.phonetic])):
                details = build_vocabulary_details(
                    stored.word,
                    existing_meaning=stored.meaning_en,
                    example_sentence=stored.example_sentence,
                )
                if not stored.phonetic and details.get('ipa'):
                    stored.phonetic = details['ipa']
                    updated = True
                if not stored.synonym and details.get('synonym'):
                    stored.synonym = details['synonym']
                    updated = True
                if not stored.antonym and details.get('antonym'):
                    stored.antonym = details['antonym']
                    updated = True
                if details.get('definition') and (
                    not stored.meaning_en
                    or 'common english vocabulary' in (stored.meaning_en or '').lower()
                ):
                    stored.meaning_en = details['definition']
                    updated = True
                if details.get('example_sentence') and (
                    not stored.example_sentence
                    or 'practice using' in (stored.example_sentence or '').lower()
                ):
                    stored.example_sentence = details['example_sentence']
                    updated = True
                if details.get('topic') and details['topic'] != 'General' and not stored.category:
                    stored.category = details['topic']
                    updated = True

            if updated:
                db.commit()
            card.phonetic = stored.phonetic
            card.synonym = stored.synonym
            card.antonym = stored.antonym
            card.meaning_en = stored.meaning_en
            card.example_sentence = stored.example_sentence
            card.category = stored.category
            card._enriched = True
        finally:
            db.close()

    
    def _lookup_curated_word(self, word):
        """Look up a word in the curated vocab.json data."""
        import json, os
        vocab_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'seed', 'vocab.json')
        try:
            with open(vocab_path, 'r', encoding='utf-8') as f:
                all_words = json.load(f)
            for entry in all_words:
                if entry.get('word', '').lower() == word.lower():
                    return entry
        except Exception:
            pass
        return None

    def _enrich_card_bg(self, card, card_index):
        """Background thread: enrich *card* then redraw if user is still on it."""
        self._do_enrich_card(card)

        def _redraw():
            if self.cards and self.current_index == card_index:
                self.update_card_display()

        self.after(0, _redraw)

    def flip_card(self, event=None):
        self.show_back = not self.show_back
        self.update_card_display()
        if self.show_back:
            self.quality_frame.pack()
        else:
            self.quality_frame.pack_forget()

    def update_card_display(self):
        for w in self.card_frame.winfo_children():
            w.destroy()
        if not self.cards:
            ctk.CTkLabel(self.card_frame, text="No due cards").pack(expand=True)
            return

        card = self.cards[self.current_index]
        card_index = self.current_index
        topic = getattr(card, 'category', None) or classify_topic(card.word)
        ctk.CTkLabel(self.card_frame, text=f'Topic: {topic}', font=("Arial", 11), text_color='#888888').pack(pady=(0, 2))
        ctk.CTkLabel(self.card_frame, text=self._card_status_text(card), font=("Arial", 12, "bold")).pack(pady=(0, 8))
        ctk.CTkLabel(self.card_frame, text=card.word, font=("Arial", 24)).pack(pady=10)
        ipa_text = getattr(card, 'phonetic', None) or ('…' if not getattr(card, '_enriched', False) else 'N/A')
        syn_text = getattr(card, 'synonym', None) or ('…' if not getattr(card, '_enriched', False) else 'N/A')
        ant_text = getattr(card, 'antonym', None) or ('…' if not getattr(card, '_enriched', False) else 'N/A')
        ctk.CTkLabel(self.card_frame, text=f"IPA: {ipa_text}", font=("Arial", 14)).pack(pady=4)
        ctk.CTkLabel(self.card_frame, text=f"Synonym: {syn_text}", wraplength=400, justify='left').pack(pady=2)
        ctk.CTkLabel(self.card_frame, text=f"Opposite: {ant_text}", wraplength=400, justify='left').pack(pady=2)
        if not getattr(card, '_enriched', False):
            threading.Thread(
                target=self._enrich_card_bg,
                args=(card, card_index),
                daemon=True,
            ).start()
        if self.show_back:
            meaning = getattr(card, 'meaning_en', '') or ''
            example = getattr(card, 'example_sentence', '') or ''
            ctk.CTkLabel(self.card_frame, text=meaning, font=("Arial", 18), wraplength=700).pack(pady=6)
            ctk.CTkLabel(self.card_frame, text=example, wraplength=400).pack(pady=6)
            synonym = getattr(card, 'synonym', None)
            antonym = getattr(card, 'antonym', None)
            if synonym:
                ctk.CTkLabel(self.card_frame, text=f'Synonym example: The word "{synonym}" can be used in a similar context.', wraplength=400, justify='left').pack(pady=2)
            if antonym:
                ctk.CTkLabel(self.card_frame, text=f'Opposite of {card.word}: "{antonym}".', wraplength=400, justify='left').pack(pady=2)

    def rate_card(self, quality):
        if not self.cards:
            return

        card = self.cards[self.current_index]
        db = get_session()
        try:
            progress = db.query(UserVocabularyProgress).filter_by(user_id=getattr(self.app.user, 'id', None), card_id=card.id).first()
            if not progress:
                progress = UserVocabularyProgress(
                    user_id=getattr(self.app.user, 'id', None),
                    card_id=card.id,
                    srs_interval=1,
                    srs_easiness=2.5,
                    srs_repetitions=0,
                    next_review_date=None,
                    last_quality=None,
                    times_seen=0,
                    times_correct=0,
                )
                db.add(progress)
            SRSEngine.update_card(progress, quality)
            db.commit()
            # record that a card was reviewed in this session
            try:
                self.cards_reviewed += 1
            except Exception:
                self.cards_reviewed = 1
        finally:
            db.close()

        self.current_index += 1
        # Pre-fetch the card that is now 4 ahead so it is ready before the user reaches it.
        prefetch_index = self.current_index + 3
        if prefetch_index < len(self.cards):
            threading.Thread(
                target=self._do_enrich_card,
                args=(self.cards[prefetch_index],),
                daemon=True,
            ).start()
        if self.current_index >= len(self.cards):
            for w in self.winfo_children():
                w.destroy()
            ctk.CTkLabel(self, text="Session complete").pack()
            # award aggregated XP for the session
            try:
                user_id = self.app.user.id if getattr(self.app, 'user', None) else None
                xp = int(5 * (self.cards_reviewed or 0))
                if getattr(self, '_session_id', None):
                    end_session(self._session_id, xp_earned=xp, items_studied=self.cards_reviewed, items_correct=self.cards_reviewed)
                else:
                    record_session(user_id=user_id, session_type=SessionType.VOCABULARY, xp_earned=xp, items_studied=self.cards_reviewed, items_correct=self.cards_reviewed)
            except Exception:
                pass
            try:
                if getattr(self, 'timer', None):
                    self.timer.stop()
            except Exception:
                pass
        else:
            self.show_back = False
            self.quality_frame.pack_forget()
            self.update_card_display()

    def _on_timer_finish(self):
        # called when the timer completes; finalize session and award XP
        try:
            user_id = self.app.user.id if getattr(self.app, 'user', None) else None
            xp = int(5 * (self.cards_reviewed or 0))
            if getattr(self, '_session_id', None):
                end_session(self._session_id, xp_earned=xp, items_studied=self.cards_reviewed, items_correct=self.cards_reviewed)
            else:
                record_session(user_id=user_id, session_type=SessionType.VOCABULARY, xp_earned=xp, items_studied=self.cards_reviewed, items_correct=self.cards_reviewed)
        except Exception:
            pass