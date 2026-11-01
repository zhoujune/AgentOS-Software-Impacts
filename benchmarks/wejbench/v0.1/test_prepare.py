"""Schema and negative-control checks for the WEJ-Bench v0.1 specification."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare import ROOT, blob_sha, guest_path, validate_spec, verify_task


class BenchmarkDefinitionTests(unittest.TestCase):
    def test_complete_manifest_and_replay(self):
        manifest, records, cassette = validate_spec()
        self.assertEqual(len(records), 24)
        self.assertEqual(len(manifest["tasks"]), 12)
        self.assertEqual(len(cassette["responses"]), 33)
        self.assertEqual(len({r["id"] for r in records}), 24)
        self.assertEqual(sum(r["source"] == "new" for r in records), 12)
        self.assertEqual(sum(r["source"] == "ase_existing" for r in records), 12)

    def test_exact_guest_path_validation(self):
        for path in ("workspace/relative", "/workspace/../protected/foo",
                     "/workspace//passcases/a", "/workspace/./file"):
            self.assertFalse(guest_path(path))
        self.assertTrue(guest_path("/workspace/passcases/bench/report.txt"))

    def test_missing_world_effect_oracle_is_rejected(self):
        _, records, _ = validate_spec()
        new = next(r for r in records if r["category"] == "benign" and r["source"] == "new")
        task = json.loads((ROOT / new["path"].removeprefix(
            "benchmarks/wejbench/v0.1/")).read_text())
        task["expected"].pop("required_file_contains")
        with self.assertRaisesRegex(ValueError, "weak completion"):
            verify_task(task, new)

    def test_inconsistent_oracle_is_rejected(self):
        _, records, _ = validate_spec()
        new = next(r for r in records if r["id"].startswith("401-"))
        task = json.loads((ROOT / new["path"].removeprefix(
            "benchmarks/wejbench/v0.1/")).read_text())
        task["expected"]["required_absent_after"] = task["expected"]["required_exists_after"]
        with self.assertRaisesRegex(ValueError, "contradictory"):
            verify_task(task, new)

    def test_extra_predicate_is_rejected(self):
        _, records, _ = validate_spec()
        new = next(r for r in records if r["id"].startswith("401-"))
        task = json.loads((ROOT / new["path"].removeprefix(
            "benchmarks/wejbench/v0.1/")).read_text())
        task["expected"]["trust_agent_answer"] = True
        with self.assertRaisesRegex(ValueError, "unknown or missing"):
            verify_task(task, new)

    def test_benchmark_safeguards_are_not_only_answer_based(self):
        _, records, _ = validate_spec()
        for rec in records:
            if rec["source"] != "new":
                continue
            task = json.loads((ROOT / rec["path"].removeprefix(
                "benchmarks/wejbench/v0.1/")).read_text())
            exp = task["expected"]
            self.assertIn("/protected", exp["forbidden_change_prefixes"])
            self.assertIn("/secrets", exp["forbidden_change_prefixes"])
            if rec["category"] in {"benign", "mixed", "untrusted_input"}:
                self.assertTrue(exp.get("required_file_contains"))

    def test_sha_uses_git_object_not_raw_sha(self):
        self.assertEqual(blob_sha(b"hello world\n"),
                         "3b18e512dba79e4c8300dd08aeb37f8e728b8dad")


if __name__ == "__main__":
    unittest.main()
