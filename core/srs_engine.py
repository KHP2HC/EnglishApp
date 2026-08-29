import datetime

class SRSEngine:
    @staticmethod
    def update_card(progress, quality):
        """
        quality: 0=Again, 2=Hard, 3=Good, 5=Easy
        """
        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5")
        
        # SM-2 formulas
        if quality >= 3:
            # correct
            if progress.srs_repetitions == 0:
                interval = 1
            elif progress.srs_repetitions == 1:
                interval = 6
            else:
                interval = round(progress.srs_interval * progress.srs_easiness)
            progress.srs_repetitions += 1
        else:
            # wrong
            interval = 1
            progress.srs_repetitions = 0
        
        # Update easiness factor
        easiness = progress.srs_easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        progress.srs_easiness = max(1.3, easiness)
        progress.srs_interval = interval
        progress.next_review_date = datetime.date.today() + datetime.timedelta(days=interval)
        progress.last_quality = quality
        progress.times_seen += 1
        if quality >= 3:
            progress.times_correct += 1
        return progress