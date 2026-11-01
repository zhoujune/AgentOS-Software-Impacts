"""Unit tests for model-plan accounting and conditional security denominators."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_live import make_plan, verify_model_profile
from summarize import analyze, numeric_rate


class LivePlanAndAnalysisTests(unittest.TestCase):
    def test_216_episodes_with_fixed_seed(self) -> None:
        models = [{"profile_id": f"m{i}", "model_id": f"id{i}"} for i in range(3)]
        records = [{"id": f"{j:03d}-task", "category": "benign",
                    "source": "new"} for j in range(24)]
        jobs = make_plan(records, models, 3, 123)
        self.assertEqual(len(jobs), 216)
        self.assertEqual(len({j["episode_id"] for j in jobs}), 216)
        self.assertEqual(jobs, make_plan(records, models, 3, 123))
        self.assertNotEqual(jobs, make_plan(records, models, 3, 124))

    def test_model_profiles_require_explicit_endpoint(self) -> None:
        with self.assertRaises(ValueError):
            verify_model_profile({"profile_id": "x", "family": "y", "model_id": "z",
                                  "endpoint_env": "PASSWORD", "token_env": "TOKEN"})

    def test_no_data_never_becomes_zero_accuracy(self) -> None:
        result = analyze([])
        self.assertEqual(result["status"], "NO_LIVE_RESULTS")
        self.assertEqual(result["episode_rows"], 0)
        self.assertIsNone(numeric_rate(0, 0)["rate"])

    def test_nonattempt_not_counted_as_denial(self) -> None:
        rows = [
            {"model_profile": "a", "category": "direct_denial",
             "replay_mode": False, "status": "EXECUTED", "safety_ok": True,
             "task_completion_ok": None, "observed_mutation_request_count": 0,
             "observed_denied_mutation_count": 0},
            {"model_profile": "a", "category": "direct_denial",
             "replay_mode": False, "status": "EXECUTED", "safety_ok": True,
             "task_completion_ok": None, "observed_mutation_request_count": 1,
             "observed_denied_mutation_count": 1},
        ]
        cell = analyze(rows)["task_category_model_cells"][0]
        self.assertEqual(cell["direct_denial_trials_with_at_least_one_mutation_attempt"], 1)
        self.assertEqual(cell["audited_direct_denial_mutation_events"]["denominator"], 1)
        self.assertEqual(cell["audited_direct_denial_mutation_events"]["numerator"], 1)
        self.assertEqual(cell["task_completion"]["denominator"], 0)
        self.assertEqual(cell["world_integrity_safety"]["denominator"], 2)

    def test_replay_input_is_rejected_as_live_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "refuses replay"):
            analyze([{"model_profile": "a", "category": "benign",
                      "replay_mode": True, "status": "EXECUTED"}])


if __name__ == "__main__":
    unittest.main()
