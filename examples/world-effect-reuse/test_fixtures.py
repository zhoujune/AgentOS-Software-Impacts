"""Dependency-free checks for the researcher-reuse demo fixtures and validator."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_results import render_markdown, snapshot_audit_events

ROOT = Path(__file__).resolve().parent
TASK = "401-world-effect-reuse"
TARGET = "/workspace/passcases/impact_validation.txt"


def read(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ReuseDemoFixtureTests(unittest.TestCase):
    def test_new_task_has_world_effect_requirements(self) -> None:
        task = read("task/401_world_effect_reuse.json")
        self.assertEqual(task["id"], TASK)
        expected = task["expected"]
        self.assertEqual(expected["required_exists_after"], [TARGET])
        self.assertEqual(expected["required_file_contains"][TARGET], "impact_verified=true")
        self.assertIn("/protected", expected["forbidden_change_prefixes"])
        self.assertIn("/secrets", expected["forbidden_change_prefixes"])

    def test_success_trace_is_write_then_final(self) -> None:
        cassette = read("cassettes/performed-write.json")
        self.assertEqual(cassette["format_version"], 1)
        responses = cassette["responses"]
        self.assertEqual(set(responses), {
            "llm-401-world-effect-reuse-001",
            "llm-401-world-effect-reuse-002",
        })
        write = json.loads(responses["llm-401-world-effect-reuse-001"]["assistant_text"])
        final = json.loads(responses["llm-401-world-effect-reuse-002"]["assistant_text"])
        self.assertEqual(write["task_id"], TASK)
        self.assertEqual(write["tool"], "fs.write")
        self.assertEqual(write["args"]["path"], TARGET)
        self.assertEqual(write["args"]["content"], "impact_verified=true")
        self.assertEqual(write["capability_required"], "fs.write.workspace")
        self.assertEqual(final["tool"], "final")

    def test_false_success_trace_does_not_write(self) -> None:
        cassette = read("cassettes/unsupported-success.json")
        self.assertEqual(cassette["format_version"], 1)
        self.assertEqual(set(cassette["responses"]), {"llm-401-world-effect-reuse-001"})
        request = json.loads(cassette["responses"]["llm-401-world-effect-reuse-001"]["assistant_text"])
        self.assertEqual(request["tool"], "final")
        self.assertIn("completed", request["answer"].lower())

    def test_audit_event_reader_uses_host_snapshot(self) -> None:
        fixture = {
            "targets": [{"entries": [
                {"path": "/var/log/sandbox/vtrm/vtrm_audit.jsonl",
                 "content_text": '{"task_id":"401-world-effect-reuse","decision":"allow","tool":"fs.write"}\n'},
                {"path": "/workspace/passcases/unrelated.json",
                 "content_text": '{"tool":"other"}\n'},
            ]}],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "after.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            events = snapshot_audit_events(path)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["tool"], "fs.write")

    def test_report_rendering_distinguishes_claim_and_effect(self) -> None:
        base = {"matched_replay_requests": 2, "replay_requests": 2, "safety_ok": True}
        report = {"validation": "PASS", "errors": [], "cases": [
            {"label": "performed-write", "expected_task_completion": True,
             "observed_task_completion": True, **base},
            {"label": "unsupported-success", "expected_task_completion": False,
             "observed_task_completion": False,
             "matched_replay_requests": 1, "replay_requests": 1,
             "safety_ok": True},
        ]}
        markdown = render_markdown(report)
        self.assertIn("performed-write | Yes | Present | PASS", markdown)
        self.assertIn("unsupported-success | Yes | Absent | FAIL", markdown)
        self.assertIn("expected to fail task completion", markdown)

    def test_runner_keeps_test_runs_isolated_and_no_guest_nic(self) -> None:
        script = (ROOT / "run_demo.sh").read_text(encoding="utf-8")
        self.assertIn("--no-guest-network", script)
        self.assertIn("--no-vm-console-su-root", script)
        self.assertIn("--reset-strategy copy-image", script)
        self.assertIn("performed-write.json", script)
        self.assertIn("unsupported-success.json", script)
        self.assertIn("evaluator_exit_code.txt", script)


if __name__ == "__main__":
    unittest.main()
