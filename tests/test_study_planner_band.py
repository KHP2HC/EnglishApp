import unittest
from datetime import date, timedelta
from types import SimpleNamespace

from core.study_planner import StudyPlanner
from data.models import ExamType


def test_study_planner_emphasizes_foundation_skills_for_low_band_users():
    user = SimpleNamespace(
        target_exam=ExamType.IELTS,
        current_band=1.0,
        daily_free_minutes={},
        exam_date=date.today() + timedelta(days=45),
    )

    planner = StudyPlanner(user)
    weights = planner._skill_weights()

    assert weights['vocabulary'] > weights['reading']
    assert weights['vocabulary'] >= 0.30


def test_study_planner_reads_granular_schedule_slots():
    user = SimpleNamespace(
        target_exam=ExamType.IELTS,
        current_band=4.0,
        daily_free_minutes={},
        exam_date=date.today() + timedelta(days=45),
        daily_schedule={
            'mon': {'morning': 30, 'afternoon': 20, 'evening': 10},
            'tue': {'morning': 15, 'afternoon': 0, 'evening': 15},
        },
    )

    planner = StudyPlanner(user)

    assert planner.daily_minutes['mon'] == 60
    assert planner.daily_minutes['tue'] == 30


def test_study_planner_handles_string_exam_types():
    user = SimpleNamespace(
        target_exam='IELTS',
        current_band=4.0,
        daily_free_minutes={},
        exam_date=date.today() + timedelta(days=45),
    )

    planner = StudyPlanner(user)

    weights = planner._skill_weights()

    assert weights['reading'] >= weights['vocabulary'] * 0.8


def test_study_planner_handles_string_exam_dates():
    user = SimpleNamespace(
        target_exam='IELTS',
        current_band=4.0,
        daily_free_minutes={},
        exam_date=(date.today() + timedelta(days=45)).isoformat(),
    )

    planner = StudyPlanner(user)

    assert planner.days_remaining == 45


class OnboardingNormalizationTests(unittest.TestCase):
    def test_onboarding_normalizes_string_exam_types(self):
        from ui.screens.onboarding import OnboardingWizard

        wizard = OnboardingWizard.__new__(OnboardingWizard)

        self.assertEqual(wizard._normalize_exam_type('IELTS'), ExamType.IELTS)
        self.assertEqual(wizard._normalize_exam_type(ExamType.TOEFL), ExamType.TOEFL)


def test_generate_plan_always_returns_at_least_one_week():
    user = SimpleNamespace(
        target_exam=ExamType.IELTS,
        current_band=5.0,
        daily_free_minutes={'mon': 30},
        exam_date=date.today(),
    )

    planner = StudyPlanner(user)

    plan = planner.generate_plan()

    assert plan, 'Expected a plan even when the exam is due today.'


def test_generate_plan_adds_lesson_counts_for_each_skill():
    user = SimpleNamespace(
        target_exam=ExamType.IELTS,
        current_band=4.0,
        daily_free_minutes={'mon': 60},
        exam_date=date.today() + timedelta(days=7),
    )

    planner = StudyPlanner(user)
    plan = planner.generate_plan()
    first_day_tasks = plan[next(iter(plan))][0]['tasks']

    assert all('lesson_count' in task for task in first_day_tasks)
    assert all(isinstance(task['lesson_count'], int) and task['lesson_count'] >= 1 for task in first_day_tasks)
