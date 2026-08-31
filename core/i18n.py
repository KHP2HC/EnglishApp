"""Internationalization (i18n) hook for EnglishCoach Pro.

Provides bilingual labels (English / Vietnamese) for UI elements.
Usage:
    from core.i18n import t
    label = ctk.CTkLabel(text=t("dashboard"))
"""

import json
import os

# Default language — can be overridden by user settings
_current_lang = "en"

# Built-in translations
_TRANSLATIONS = {
    "en": {
        "app_title": "EnglishCoach Pro",
        "dashboard": "Dashboard",
        "vocabulary": "Vocabulary",
        "grammar": "Grammar",
        "reading": "Reading",
        "listening": "Listening",
        "writing": "Writing",
        "speaking": "Speaking",
        "mock_test": "Mock Test",
        "progress": "Progress",
        "planner": "Planner",
        "settings": "Settings",
        "placement": "Placement Test",
        "onboarding": "Getting Started",
        "welcome_back": "Welcome back",
        "days_to_exam": "days to exam",
        "streak": "Streak",
        "daily_goal": "Daily Goal",
        "todays_plan": "Today's Plan",
        "word_of_the_day": "Word of the Day",
        "words_learned": "Words Learned",
        "current_band": "Current Band",
        "xp_this_week": "XP This Week",
        "start_test": "Start Test",
        "submit": "Submit",
        "next": "Next",
        "back": "Back",
        "finish": "Finish",
        "save": "Save",
        "cancel": "Cancel",
        "correct": "Correct",
        "incorrect": "Incorrect",
        "again": "Again",
        "hard": "Hard",
        "good": "Good",
        "easy": "Easy",
        "show_meaning": "Click card to reveal meaning",
        "play_audio": "Play Audio",
        "get_feedback": "Get Feedback",
        "evaluate": "Evaluate",
        "generate_plan": "Generate Study Plan",
        "review_weak_areas": "Review Weak Areas",
        "error_journal": "Error Journal",
        "activity_heatmap": "Activity Heatmap",
        "skill_balance": "Skill Balance",
        "band_over_time": "Band Estimate Over Time",
        "time_per_skill": "Time Spent per Skill",
    },
    "vi": {
        "app_title": "EnglishCoach Pro",
        "dashboard": "Bảng điều khiển",
        "vocabulary": "Từ vựng",
        "grammar": "Ngữ pháp",
        "reading": "Đọc hiểu",
        "listening": "Nghe hiểu",
        "writing": "Viết",
        "speaking": "Nói",
        "mock_test": "Thi thử",
        "progress": "Tiến độ",
        "planner": "Lịch học",
        "settings": "Cài đặt",
        "placement": "Bài kiểm tra xếp hạng",
        "onboarding": "Bắt đầu",
        "welcome_back": "Chào mừng trở lại",
        "days_to_exam": "ngày đến kỳ thi",
        "streak": "Chuỗi ngày",
        "daily_goal": "Mục tiêu hàng ngày",
        "todays_plan": "Kế hoạch hôm nay",
        "word_of_the_day": "Từ vựng hôm nay",
        "words_learned": "Từ đã học",
        "current_band": "Trình độ hiện tại",
        "xp_this_week": "XP tuần này",
        "start_test": "Bắt đầu",
        "submit": "Nộp bài",
        "next": "Tiếp",
        "back": "Quay lại",
        "finish": "Hoàn thành",
        "save": "Lưu",
        "cancel": "Hủy",
        "correct": "Đúng",
        "incorrect": "Sai",
        "again": "Lặp lại",
        "hard": "Khó",
        "good": "Tốt",
        "easy": "Dễ",
        "show_meaning": "Nhấp thẻ để xem nghĩa",
        "play_audio": "Phát âm thanh",
        "get_feedback": "Nhận phản hồi",
        "evaluate": "Đánh giá",
        "generate_plan": "Tạo kế hoạch học",
        "review_weak_areas": "Ôn tập điểm yếu",
        "error_journal": "Nhật ký lỗi",
        "activity_heatmap": "Bản đồ hoạt động",
        "skill_balance": "Cân bằng kỹ năng",
        "band_over_time": "Tiến độ trình độ",
        "time_per_skill": "Thời gian theo kỹ năng",
    },
}


def set_language(lang: str):
    """Set the current language ('en' or 'vi')."""
    global _current_lang
    if lang in _TRANSLATIONS:
        _current_lang = lang


def get_language() -> str:
    return _current_lang


def t(key: str, lang: str = None) -> str:
    """Translate a key to the current (or specified) language.

    Falls back to English if the key is not found in the target language,
    and to the key itself if not found at all.
    """
    use_lang = lang or _current_lang
    translations = _TRANSLATIONS.get(use_lang, _TRANSLATIONS["en"])
    return translations.get(key, _TRANSLATIONS["en"].get(key, key))


def available_languages() -> dict:
    """Return available languages as {code: display_name}."""
    return {"en": "English", "vi": "Tiếng Việt"}
