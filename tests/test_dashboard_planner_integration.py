import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ui.screens.dashboard import DashboardScreen


class DummyLabel:
    def __init__(self):
        self.text = None

    def configure(self, **kwargs):
        self.text = kwargs.get('text')


class DummyFrame:
    def __init__(self):
        self.children = []

    def winfo_children(self):
        return self.children


class DummySession:
    def __init__(self, plan_record=None):
        self.plan_record = plan_record

    def query(self, model):
        return self

    def filter_by(self, **kwargs):
        return self

    def order_by(self, *args):
        return self

    def first(self):
        return self.plan_record

    def close(self):
        return None


class DummyPlanRecord:
    def __init__(self, plan=None):
        self.plan = plan
        self.created_at = SimpleNamespace(date=lambda: '2024-01-01')


class DashboardPlannerIntegrationTests(unittest.TestCase):
    def test_load_plan_summary_uses_generated_plan_when_no_saved_plan_exists(self):
        screen = object.__new__(DashboardScreen)
        screen.user = SimpleNamespace(id=1)
        screen._saved_plan = None

        generated_plan = {'2024-01-01': [{'date': '2024-01-01', 'tasks': [{'type': 'vocabulary', 'minutes': 30}]}]}

        session = DummySession(plan_record=None)
        with patch('ui.screens.dashboard.get_session', return_value=session), \
             patch('ui.screens.dashboard.StudyPlanner') as MockPlanner:
            MockPlanner.return_value.generate_plan.return_value = generated_plan

            screen._load_plan_summary()

        self.assertEqual(screen._saved_plan, generated_plan)

    def test_exam_label_handles_string_exam_values(self):
        screen = object.__new__(DashboardScreen)
        screen.user = SimpleNamespace(target_exam='IELTS')

        self.assertEqual(screen._exam_label(), 'IELTS')
