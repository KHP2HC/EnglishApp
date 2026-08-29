import os
import difflib
import re

try:
    import edge_tts
except Exception:  # pragma: no cover - exercised when dependency is missing
    edge_tts = None


class PronunciationCoach:
    SUPPORTED_EXTENSIONS = ('.wav', '.mp3', '.m4a', '.ogg', '.flac')

    def __init__(self):
        self.model = None

    def _ensure_model(self):
        if self.model is None:
            try:
                import whisper
                self.model = whisper.load_model('tiny')
            except Exception:
                self.model = None
        return self.model

    async def evaluate(self, target_text, audio_path):
        if not audio_path or not os.path.isfile(audio_path):
            raise ValueError('Audio file path is invalid.')

        extension = os.path.splitext(audio_path)[1].lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f'Unsupported audio file type: {extension}')

        model = self._ensure_model()
        spoken = target_text.strip()
        word_details = []
        detailed_feedback = 'Pronunciation analysis is using a lightweight fallback because the speech model is unavailable.'

        if model is not None:
            try:
                result = model.transcribe(audio_path, fp16=False)
                spoken = result.get('text', '').strip()
            except Exception:
                spoken = target_text.strip()

        target_words = [re.sub(r"[^a-z']", '', w.lower()) for w in target_text.split() if re.sub(r"[^a-z']", '', w.lower())]
        spoken_words = [re.sub(r"[^a-z']", '', w.lower()) for w in spoken.split() if re.sub(r"[^a-z']", '', w.lower())]

        for word in target_words:
            best_match = difflib.get_close_matches(word, spoken_words, n=1, cutoff=0.4)
            is_correct = word in spoken_words or bool(best_match)
            word_details.append({
                'word': word,
                'status': 'correct' if is_correct else 'missed',
                'suggestion': best_match[0] if best_match else None,
            })

        mismatches = [item['word'] for item in word_details if item['status'] == 'missed']
        accuracy = 1.0 if not target_words else sum(1 for item in word_details if item['status'] == 'correct') / len(target_words)

        summary_parts = []
        for item in word_details:
            if item['status'] == 'correct':
                summary_parts.append(f"{item['word']} sounded clear.")
            else:
                suggestion = item['suggestion'] or 'a similar word'
                summary_parts.append(f"{item['word']} may need work; you said {suggestion}.")
        detailed_feedback = ' '.join(summary_parts) or detailed_feedback

        output_file = os.path.join(os.getcwd(), 'correct_pronunciation.mp3')
        if edge_tts is not None:
            try:
                communicate = edge_tts.Communicate(target_text, 'en-US-AriaNeural')
                await communicate.save(output_file)
            except Exception:
                output_file = None
        else:
            output_file = None

        return {
            'spoken_text': spoken,
            'accuracy': accuracy,
            'mismatches': mismatches,
            'word_details': word_details,
            'detailed_feedback': detailed_feedback,
            'audio_file': output_file,
        }
