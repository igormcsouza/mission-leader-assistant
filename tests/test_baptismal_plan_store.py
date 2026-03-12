"""Tests for the BaptismalPlan storage backends."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from core.store import (  # noqa: E402  # pylint: disable=wrong-import-position
    BaptismalPlanJsonStore,
    _new_plan_skeleton,
    _sanitize_baptismal_plan,
)


class TestSanitizeBaptismalPlan(unittest.TestCase):
    """Tests for _sanitize_baptismal_plan."""

    def test_returns_empty_dict_for_non_dict(self):
        self.assertEqual(_sanitize_baptismal_plan(None), {})
        self.assertEqual(_sanitize_baptismal_plan("bad"), {})

    def test_sanitizes_top_level_fields(self):
        data = {
            "serviceDate": "2026-03-23",
            "serviceTime": "10:00",
            "ward": "Ala Teste",
            "location": "Chapel",
            "conductingLeader": "Bispo",
            "status": "Scheduled",
            "notes": "Some note",
            "candidates": [],
            "ordinances": [],
            "witnesses": [],
            "program": [],
        }
        result = _sanitize_baptismal_plan(data)
        self.assertEqual(result["serviceDate"], "2026-03-23")
        self.assertEqual(result["status"], "Scheduled")
        self.assertEqual(result["notes"], "Some note")

    def test_sanitizes_candidates(self):
        data = {
            "candidates": [
                {"id": "c1", "fullName": "João Silva", "birthDate": "2000-01-01",
                 "age": "26", "candidateType": "Convert",
                 "interviewCompleted": True, "interviewedBy": "Bispo"},
            ],
        }
        result = _sanitize_baptismal_plan(data)
        self.assertEqual(len(result["candidates"]), 1)
        c = result["candidates"][0]
        self.assertEqual(c["fullName"], "João Silva")
        self.assertTrue(c["interviewCompleted"])

    def test_skips_invalid_candidates(self):
        data = {"candidates": ["not a dict", None, {"id": "c1", "fullName": "Ok"}]}
        result = _sanitize_baptismal_plan(data)
        self.assertEqual(len(result["candidates"]), 1)

    def test_default_status_is_draft(self):
        result = _sanitize_baptismal_plan({})
        self.assertEqual(result["status"], "Draft")


class TestNewPlanSkeleton(unittest.TestCase):
    """Tests for _new_plan_skeleton."""

    def test_has_expected_keys(self):
        plan = _new_plan_skeleton()
        for key in ("serviceDate", "serviceTime", "ward", "location",
                    "conductingLeader", "status", "candidates", "ordinances",
                    "witnesses", "program", "notes"):
            self.assertIn(key, plan)

    def test_default_status_is_draft(self):
        plan = _new_plan_skeleton()
        self.assertEqual(plan["status"], "Draft")

    def test_program_has_14_items(self):
        plan = _new_plan_skeleton()
        self.assertEqual(len(plan["program"]), 14)

    def test_first_program_item_is_prelude(self):
        plan = _new_plan_skeleton()
        self.assertEqual(plan["program"][0]["item"], "Prelúdio")


class TestBaptismalPlanJsonStore(unittest.TestCase):
    """Tests for BaptismalPlanJsonStore."""

    def setUp(self):
        fd, self.tmp = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        self.store = BaptismalPlanJsonStore(self.tmp)
        self.user_id = "user_abc"

    def tearDown(self):
        for path in (self.tmp, self.store.path):
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass

    def test_list_plans_empty_initially(self):
        plans = self.store.list_plans(self.user_id)
        self.assertEqual(plans, [])

    def test_create_plan_returns_plan_with_id(self):
        plan_id, plan = self.store.create_plan(self.user_id)
        self.assertIsNotNone(plan_id)
        self.assertEqual(plan["id"], plan_id)
        self.assertEqual(plan["status"], "Draft")
        self.assertIn("createdAt", plan)
        self.assertIn("updatedAt", plan)

    def test_create_plan_has_default_program(self):
        _, plan = self.store.create_plan(self.user_id)
        self.assertEqual(len(plan["program"]), 14)

    def test_get_plan_returns_created_plan(self):
        plan_id, _ = self.store.create_plan(self.user_id)
        fetched = self.store.get_plan(self.user_id, plan_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["id"], plan_id)

    def test_get_plan_returns_none_for_missing_plan(self):
        result = self.store.get_plan(self.user_id, "non-existent-id")
        self.assertIsNone(result)

    def test_update_plan_persists_changes(self):
        plan_id, _ = self.store.create_plan(self.user_id)
        updated = self.store.update_plan(self.user_id, plan_id, {
            "serviceDate": "2026-03-23",
            "serviceTime": "10:00",
            "ward": "Ala Test",
            "status": "Scheduled",
        })
        self.assertIsNotNone(updated)
        self.assertEqual(updated["serviceDate"], "2026-03-23")
        self.assertEqual(updated["status"], "Scheduled")

        # Verify persisted
        fetched = self.store.get_plan(self.user_id, plan_id)
        self.assertEqual(fetched["serviceDate"], "2026-03-23")

    def test_update_plan_returns_none_for_missing_plan(self):
        result = self.store.update_plan(self.user_id, "missing-id", {})
        self.assertIsNone(result)

    def test_list_plans_ordered_by_service_date_descending(self):
        plan_id1, _ = self.store.create_plan(self.user_id)
        plan_id2, _ = self.store.create_plan(self.user_id)
        self.store.update_plan(self.user_id, plan_id1, {"serviceDate": "2026-01-01"})
        self.store.update_plan(self.user_id, plan_id2, {"serviceDate": "2026-03-23"})

        plans = self.store.list_plans(self.user_id)
        self.assertEqual(len(plans), 2)
        self.assertEqual(plans[0]["serviceDate"], "2026-03-23")
        self.assertEqual(plans[1]["serviceDate"], "2026-01-01")

    def test_list_plans_includes_candidate_names(self):
        plan_id, _ = self.store.create_plan(self.user_id)
        self.store.update_plan(self.user_id, plan_id, {
            "candidates": [{"id": "c1", "fullName": "João Silva"}],
        })
        plans = self.store.list_plans(self.user_id)
        self.assertEqual(plans[0]["candidates"], ["João Silva"])

    def test_multiple_users_isolated(self):
        """Plans from user A should not appear for user B."""
        plan_id, _ = self.store.create_plan("user_a")
        self.assertEqual(self.store.list_plans("user_b"), [])
        self.assertIsNone(self.store.get_plan("user_b", plan_id))
