"""Unit tests for the standard-library AgentOS A/B report comparator."""
import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import compare_guest_polling as target


def make_report(image_sha="image-A", wait=10.0):
    environment = {k: f"constant-{k}" for k in target.SAME_ENV}
    environment.update({
        "memory_mb": 512,
        "vm_boot_timeout_seconds": 60,
        "task_timeout_seconds": 90,
        "llm_proxy_poll_interval_seconds": 2,
        "result_poll_interval_seconds": 1,
        "clean_rootfs_sha256": image_sha,
        "agent_loop_poll_interval_seconds": 5 if image_sha == "image-A" else 0.2,
        "agent_llm_poll_interval_seconds": 1 if image_sha == "image-A" else 0.2,
    })
    cases = [{"repetition": idx, "suite": suite, "task_id": task}
             for idx in range(1, 4)
             for suite, task in sorted(target.EXPECTED_TASKS)]
    phases = {
        key: {"median": wait, "mean": wait, "p95": wait,
              "sample_count": 18}
        for key in target.PHASES
    }
    reps = [
        {"repetition": idx, "all_ok": True,
         "phase_timing_summary": {
             "task_enqueue_and_wait_seconds": {"median": wait}}}
        for idx in range(1, 4)
    ]
    return {
        "all_ok": True, "errors": [],
        "expected_repetitions": 3, "completed_repetitions": 3,
        "task_count_per_repetition": 6, "repetitions": reps,
        "case_records": cases, "phase_timing_summary": phases,
        "environment": environment,
    }


class ComparisonTests(unittest.TestCase):
    def test_valid_comparison(self):
        result = target.compare(make_report(), make_report("image-B", wait=8))
        self.assertEqual(result["validation"], "PASS")
        self.assertEqual(result["cases_each"], 18)
        self.assertEqual(result["metrics"]["task_enqueue_and_wait_seconds"]
                         ["median_reduction_pct"], 20.0)
        self.assertIn("20.00%", target.render(result))

    def test_host_poll_mismatch_rejected(self):
        a, b = make_report(), make_report("image-B")
        b["environment"]["llm_proxy_poll_interval_seconds"] = 0.2
        with self.assertRaisesRegex(ValueError, "llm_proxy_poll"):
            target.compare(a, b)

    def test_same_image_rejected(self):
        with self.assertRaisesRegex(ValueError, "distinct experimental images"):
            target.compare(make_report(), make_report())

    def test_failed_run_rejected(self):
        a = make_report()
        a["repetitions"][1]["all_ok"] = False
        # The production load validator is file-based; exercise its same
        # precondition here through a temporary JSON fixture.
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "failure.json"
            path.write_text(json.dumps(a))
            with self.assertRaisesRegex(ValueError, "failed or missing run"):
                target.load_validated(path)

    def test_missing_case_rejected(self):
        import json
        import tempfile
        a = make_report()
        a["case_records"].pop()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "missing.json"
            path.write_text(json.dumps(a))
            with self.assertRaisesRegex(ValueError, "record count"):
                target.load_validated(path)


if __name__ == "__main__":
    unittest.main()
