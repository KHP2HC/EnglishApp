import random


class AdaptiveTest:
    LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]

    def __init__(self, question_bank):
        # question_bank: list of dicts or tuples: {'level': 'B1', 'question': '..', 'answer': '..'}
        self.question_bank = question_bank
        self.current_level_index = 2  # start at B1
        self.correct_count = 0
        self.total_questions = 0

    def next_question(self):
        """Return a question dict for the current level or None if none available."""
        level = self.LEVELS[self.current_level_index]
        # support either tuple/list or dict entries
        candidates = []
        for item in self.question_bank:
            if isinstance(item, dict):
                if item.get('level') == level:
                    candidates.append(item)
            else:
                # tuple/list expected as (level, question, answer)
                try:
                    if item[0] == level:
                        candidates.append({'level': item[0], 'question': item[1], 'answer': item[2]})
                except Exception:
                    continue
        if not candidates:
            return None
        return random.choice(candidates)
    
    def record_answer(self, correct):
        self.total_questions += 1
        if correct:
            self.correct_count += 1
            # move up if enough correct
            if self.correct_count >= 3 and self.current_level_index < len(self.LEVELS)-1:
                self.current_level_index += 1
                self.correct_count = 0
        else:
            # move down after 2 wrong in a row
            if self.correct_count <= -2 and self.current_level_index > 0:
                self.current_level_index -= 1
                self.correct_count = 0
            else:
                self.correct_count -= 1
        # stop after ~20 questions or level stable