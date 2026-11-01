#!/usr/bin/env python3
"""Run the 12 hand-authored WEJ-Bench task traces through real QEMU+VTRM+WEJ.

This is an integration check, NOT a test of LLM behavior. A successful report
requires host-observed expected effects and an audited deny for every expected
unauthorized tool call (attempts and denials are distinct from non-attempts).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from prepare import ROOT, materialize, validate_spec

CASSETTE = ROOT / "cassettes/new-tasks-hand-authored.json"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_audit(snapshot: Path) -> list[dict]:
    value = read_json(snapshot)
    events = []
    for surface in value.get("targets", []):
        for entry in surface.get("entries", []):
            name = str(entry.get("path", ""))
            if name.startswith("/var/log/sandbox/vtrm/") and name.endswith(".jsonl"):
                for line in (entry.get("content_text") or "").splitlines():
                    try:
                        event = json.loads(line)
                        if isinstance(event, dict):
                            events.append(event)
                    except json.JSONDecodeError:
                        continue
    return events


def denied(event: dict) -> bool:
    return (str(event.get("decision", "")).lower() in {"deny", "denied", "blocked"}
            or str(event.get("status", "")).lower() in {"deny", "denied", "blocked"}
            or "invalid_object_action" in str(event.get("reason", "")).lower())


def validate_case(root: Path, rec: dict, cassette_sha: str) -> tuple[dict, list[str]]:
    import hashlib
    errors = []
    summaries = list((root / "reports").rglob("summary.json"))
    if len(summaries) != 1:
        return {"id": rec["id"], "status": "MISSING_REPORT"}, [f"{rec['id']}: {len(summaries)} summaries"]
    summary_path = summaries[0]
    run_dir = summary_path.parent
    summary = read_json(summary_path)
    case = read_json(run_dir / rec["id"] / "case_report.json")
    manifest = read_json(run_dir / "run_manifest.json")
    world = case.get("world_integrity") or {}
    replay = case.get("replay_validation") or {}
    audit_path = run_dir / rec["id"] / "buildroot_after.json"
    audit = [event for event in read_audit(audit_path) if event.get("task_id") == rec["id"]] \
        if audit_path.is_file() else []
    expected_denials = []
    for tool in rec.get("expected_denials", []):
        indices = [i for i, x in enumerate(rec["required_tool_sequence"], start=1) if x == tool]
        index = indices[-1]  # For mixed fs.write, first occurrence is permitted.
        request = f"req-{rec['id']}-{index:03d}"
        matches = [x for x in audit if x.get("request_id") == request and x.get("tool") == tool]
        verified = any(denied(x) for x in matches) and not any(
            x.get("status") == "success" for x in matches)
        if not verified:
            errors.append(f"missing audited denial: {rec['id']} {tool} {request}")
        expected_denials.append({"tool": tool, "request_id": request,
                                 "attempt_recorded": bool(matches), "denied": verified})

    completed = case.get("task_completion_ok")
    should_skip = rec["category"] == "direct_denial"
    if should_skip and completed is not None:
        errors.append(f"{rec['id']}: direct-denial case was mistakenly judged as completion")
    if not should_skip and completed is not True:
        errors.append(f"{rec['id']}: legitimate world-effect completion did not pass")
    if world.get("ok") is not True or world.get("forbidden_hits") or world.get("unexpected_changes"):
        errors.append(f"{rec['id']}: world-integrity/safety failure")
    if case.get("safety_ok") is not True:
        errors.append(f"{rec['id']}: safety check failed")
    if replay.get("ok") is not True or (
        replay.get("matched_count") != rec["replay_steps"] or
        replay.get("request_count") != rec["replay_steps"]):
        errors.append(f"{rec['id']}: cassette did not replay with exact request matching")
    if manifest.get("guest_network_enabled") is not False:
        errors.append(f"{rec['id']}: guest network was enabled")
    if manifest.get("replay_file_sha256") != cassette_sha:
        errors.append(f"{rec['id']}: wrong replay cassette recorded in run manifest")
    if not audit:
        errors.append(f"{rec['id']}: no guest audit evidence captured")
    task = read_json(ROOT / rec["path"].removeprefix("benchmarks/wejbench/v0.1/"))
    changed = world.get("changed_paths", [])
    for p in task["expected"].get("required_file_contains", {}):
        if p not in changed:
            errors.append(f"{rec['id']}: expected effect absent from changed-path evidence: {p}")
    read_verified = None
    if rec.get("required_read"):
        read_events = [x for x in audit if x.get("tool") == "fs.read"
                       and x.get("request_id") == f"req-{rec['id']}-001"]
        read_verified = any(x.get("status") == "success" for x in read_events)
        if not read_verified:
            errors.append(f"{rec['id']}: untrusted source was not successfully read")
    log_path = Path(case.get("llm_proxy_log", ""))
    proxy_log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""
    if "Strict replay mode; no model API calls will be made" not in proxy_log or "API call completed" in proxy_log:
        errors.append(f"{rec['id']}: strict no-API replay was not established")
    result = {
        "id": rec["id"], "category": rec["category"], "run_status": case.get("run_status"),
        "task_completion_ok": completed, "safety_ok": case.get("safety_ok"),
        "replay_ok": replay.get("ok"), "matched_replay_requests": replay.get("matched_count"),
        "expected_replay_requests": rec["replay_steps"], "world_integrity_ok": world.get("ok"),
        "changed_paths": changed, "denial_checks": expected_denials,
        "required_untrusted_read_verified": read_verified,
        "source_case_report": str(run_dir / rec["id"] / "case_report.json"),
    }
    return result, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agentos-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--task-id", action="append", help="restrict to selected new task IDs")
    parser.add_argument("--task-timeout", type=int, default=180)
    parser.add_argument("--boot-timeout", type=int, default=120)
    args = parser.parse_args()
    agentos, output = args.agentos_root.resolve(), args.output.resolve()
    _, all_records, _ = validate_spec()
    new_records = [r for r in all_records if r["source"] == "new"]
    if args.task_id:
        unknown = set(args.task_id) - {r["id"] for r in new_records}
        if unknown:
            parser.error(f"unknown new task IDs: {sorted(unknown)}")
        new_records = [r for r in new_records if r["id"] in args.task_id]
    if output.exists():
        parser.error(f"output already exists: {output}")
    output.mkdir(parents=True)
    prepared = output / "prepared"
    materialize(agentos, prepared, all_records)
    clean_image = agentos / "runtime/offline-eval/rootfs.eval.offline.ext2"
    if not clean_image.exists():
        subprocess.run([sys.executable, str(agentos / "scripts/build/make_offline_eval_image.py"),
                        "--output", str(clean_image)], cwd=agentos, check=True)
    import hashlib
    cassette_sha = hashlib.sha256(CASSETTE.read_bytes()).hexdigest()
    results = []
    errors = []
    for rec in new_records:
        case_root = output / "cases" / rec["id"]
        case_root.mkdir(parents=True)
        task_dir = prepared / ("tasks_should_fail" if rec["category"] == "direct_denial"
                               else "tasks_should_pass")
        command = [
            sys.executable, str(agentos / "judge/run_vtrm_eval.py"),
            "--tasks-dir", str(task_dir), "--task-id", rec["id"],
            "--replay-file", str(CASSETTE), "--no-guest-network",
            "--no-vm-console-su-root", "--reset-between-cases",
            "--reset-strategy", "copy-image", "--clean-rootfs", str(clean_image),
            "--rootfs", str(case_root / "guest.ext2"),
            "--bridge-dir", str(case_root / "bridge"), "--report-root", str(case_root / "reports"),
            "--memory-mb", "512", "--vm-boot-timeout", str(args.boot_timeout),
            "--task-timeout", str(args.task_timeout),
            "--proxy-warmup-seconds", "1", "--post-task-settle-seconds", "1",
            "--agent-loop-poll-interval", "5", "--agent-llm-poll-interval", "1",
            "--result-poll-interval", "1",
        ]
        print(f"RUN {rec['id']}", flush=True)
        with (case_root / "command.log").open("w", encoding="utf-8") as log:
            completed = subprocess.run(command, cwd=agentos, stdout=log, stderr=subprocess.STDOUT)
        try:
            row, issues = validate_case(case_root, rec, cassette_sha)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            row, issues = {"id": rec["id"], "status": "INSPECTION_FAILED"}, [str(exc)]
        row["evaluator_exit_code"] = completed.returncode
        results.append(row)
        errors.extend(issues)
        print(f"{'PASS' if not issues else 'FAIL'} {rec['id']} {issues}", flush=True)
    report = {"status": "PASS" if not errors and len(results) == len(new_records) else "FAIL",
              "fixture_type": "HAND_AUTHORED_STRICT_REPLAY_NOT_LIVE_MODEL",
              "live_model_episodes": 0, "new_tasks_checked": len(results),
              "cases": results, "errors": errors}
    (output / "fixture_validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "cases": len(results), "errors": errors}, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
