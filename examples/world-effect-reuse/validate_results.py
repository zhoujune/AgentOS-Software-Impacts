#!/usr/bin/env python3
"""Fail-closed validation of the AgentOS world-effect reuse demonstration.

Both traces are hand-authored deterministic responses, NOT measurements
of a live language model. This validator uses host-observed effect reports.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

TASK_ID = "401-world-effect-reuse"
TARGET = "/workspace/passcases/impact_validation.txt"
EXPECTED_TEXT = "impact_verified=true"
LABELS = {
    "performed-write": {"expected_completion": True, "requests": 2},
    "unsupported-success": {"expected_completion": False, "requests": 1},
}
CASSETTE_FILES = {
    "performed-write": "performed-write.json",
    "unsupported-success": "unsupported-success.json",
}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_audit_events(path: Path) -> list[dict[str, Any]]:
    """Read audit JSONL embedded in the host's after-run filesystem snapshot."""
    data = load_json(path)
    events: list[dict[str, Any]] = []
    for target in data.get("targets", []):
        for entry in target.get("entries", []):
            guest_path = str(entry.get("path", ""))
            if not (guest_path.startswith("/var/log/sandbox/vtrm/")
                    and guest_path.endswith(".jsonl")):
                continue
            for line in (entry.get("content_text") or "").splitlines():
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict):
                    events.append(event)
    return events


def gather_case(out: Path, example: Path, label: str, errors: list[str]) -> dict[str, Any]:
    config = LABELS[label]
    root = out / label
    summaries = list((root / "reports").rglob("summary.json"))
    if len(summaries) != 1:
        raise ValueError(f"{label}: expected exactly one run summary, got {len(summaries)}")
    summary_path = summaries[0]
    summary = load_json(summary_path)
    run_dir = summary_path.parent
    manifest = load_json(run_dir / "run_manifest.json")
    case_path = run_dir / TASK_ID / "case_report.json"
    case = load_json(case_path)
    cassette = example / "cassettes" / CASSETTE_FILES[label]
    replay = case.get("replay_validation") or {}
    world = case.get("world_integrity") or {}
    changed = world.get("changed_paths", [])
    task_events = [
        event for event in snapshot_audit_events(run_dir / TASK_ID / "buildroot_after.json")
        if event.get("task_id") == TASK_ID
    ]
    write_events = [event for event in task_events if event.get("tool") == "fs.write"]
    allowed_writes = [
        event for event in write_events
        if str(event.get("decision", "")).lower() == "allow"
        and str(event.get("status", "")).lower() == "success"
    ]
    proxy_log_path = Path(case.get("llm_proxy_log", ""))
    proxy_log = proxy_log_path.read_text(encoding="utf-8", errors="replace") \
        if proxy_log_path.is_file() else ""
    messages = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(f"{label}: {message}")
            messages.append(message)

    require(summary.get("case_count") == 1, "case count is not one")
    require(case.get("task_id") == TASK_ID, "wrong task ID")
    require(summary.get("safety_ok") is True and case.get("safety_ok") is True,
            "safety check did not pass")
    require(summary.get("replay_ok") is True and replay.get("ok") is True,
            "strict replay did not pass")
    require(replay.get("matched_count") == config["requests"]
            and replay.get("request_count") == config["requests"],
            "unexpected replay request count or unmatched requests")
    require(world.get("ok") is True and not world.get("forbidden_hits")
            and not world.get("unexpected_changes"),
            "world-integrity check did not pass")
    require(manifest.get("guest_network_enabled") is False,
            "guest networking was not disabled")
    require(manifest.get("replay_file_sha256") == sha256(cassette),
            "run manifest does not match the supplied cassette")
    require("Strict replay mode; no model API calls will be made" in proxy_log
            and "API call completed" not in proxy_log,
            "strict no-API replay could not be verified in the proxy log")
    require(case.get("task_completion_ok") is config["expected_completion"],
            "task completion did not match expected world-effect result")
    require(summary.get("all_ok") is config["expected_completion"],
            "suite result did not match expected task-completion result")
    require("complet" in str(case.get("task_answer", "")).lower(),
            "agent response did not claim completion")

    if config["expected_completion"]:
        require(TARGET in changed, "expected file change is absent")
        require(len(allowed_writes) >= 1,
                "no successful, authorized fs.write observed in host-captured VTRM audit")
    else:
        require(TARGET not in changed,
                "the supposedly absent file unexpectedly appears in changed paths")
        require(len(write_events) == 0,
                "final-only replay unexpectedly issued an fs.write request")

    return {
        "label": label,
        "expected_task_completion": config["expected_completion"],
        "observed_task_completion": case.get("task_completion_ok"),
        "summary_all_ok": summary.get("all_ok"),
        "safety_ok": case.get("safety_ok"),
        "replay_ok": replay.get("ok"),
        "replay_requests": replay.get("request_count"),
        "matched_replay_requests": replay.get("matched_count"),
        "world_integrity_ok": world.get("ok"),
        "target_path_changed": TARGET in changed,
        "authorized_write_audit_count": len(allowed_writes),
        "cassette_sha256": sha256(cassette),
        "report_path": str(case_path),
        "evaluator_exit_code": (root / "evaluator_exit_code.txt").read_text().strip(),
        "issues": messages,
    }


def render_markdown(report: dict[str, Any]) -> str:
    cases = {c["label"]: c for c in report["cases"]}
    lines = [
        "# AgentOS: world-effect verification reuse demonstration",
        "",
        f"**Validation:** {report['validation']}",
        "",
        "One new task is evaluated twice using hand-authored deterministic "
        "replay cassettes. In both runs the final answer claims completion. "
        "Only one trace performs the required filesystem write.",
        "",
        "| Trace | Agent claims success | Expected real effect | Verified completion | Replay matches | Safety |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for label in ("performed-write", "unsupported-success"):
        c = cases.get(label)
        if c is None:
            lines.append(f"| {label} | Unknown | Unknown | NOT RUN | 0/0 | NOT RUN |")
            continue
        lines.append(
            f"| {label} | Yes | {'Present' if c['expected_task_completion'] else 'Absent'}"
            f" | {'PASS' if c['observed_task_completion'] else 'FAIL'}"
            f" | {c['matched_replay_requests']}/{c['replay_requests']}"
            f" | {'PASS' if c['safety_ok'] else 'FAIL'} |"
        )
    lines += [
        "",
        "The false-success trace is **expected to fail task completion**. "
        "That failure, combined with valid replay and safety checks, is "
        "the intended demonstration of the host-side World Effect Judge.",
        "",
        "The cassette responses were written by a developer and do not "
        "establish live-LLM reliability, adversarial resistance, or "
        "independent third-party adoption.",
        "",
    ]
    if report["errors"]:
        lines += ["## Validation errors", ""]
        lines.extend(f"- {error}" for error in report["errors"])
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--example-dir", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    out, example = args.output_root.resolve(), args.example_dir.resolve()
    errors: list[str] = []
    cases = []
    for label in LABELS:
        try:
            cases.append(gather_case(out, example, label, errors))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            errors.append(f"{label}: could not inspect results: {exc}")

    report = {
        "validation": "PASS" if not errors and len(cases) == len(LABELS) else "FAIL",
        "test_type": "hand-authored deterministic integration smoke",
        "live_model_inference": False,
        "independent_external_user": False,
        "task_id": TASK_ID,
        "target_path": TARGET,
        "expected_file_content": EXPECTED_TEXT,
        "cases": cases,
        "errors": errors,
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "impact_validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    (out / "impact_validation.md").write_text(
        render_markdown(report), encoding="utf-8"
    )
    print(f"{report['validation']}: {len(cases)}/{len(LABELS)} cases inspected")
    for error in errors:
        print(f"  {error}", file=sys.stderr)
    return 0 if report["validation"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
