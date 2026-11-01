#!/usr/bin/env python3
"""Plan or execute WEJ-Bench v0.1 live-model QEMU episodes.

Default is PLAN ONLY. Execution requires --execute and explicit model endpoints.
No API keys, raw transcripts, or world snapshots are placed in Git.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys

from prepare import ROOT, read_json, validate_spec
from run_replay import read_audit, denied
from preflight_local import preflight, local_endpoint
from prepare_local_checkout import check_or_apply

PROFILES = ROOT / "model-profiles.json"


def make_plan(records: list[dict], models: list[dict], repetitions: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    jobs = []
    for repeat in range(1, repetitions + 1):
        pairs = [(model, rec) for model in models for rec in records]
        rng.shuffle(pairs)
        for model, rec in pairs:
            jobs.append({
                "episode_id": f"{model['profile_id']}--r{repeat:02d}--{rec['id']}",
                "task_id": rec["id"], "category": rec["category"],
                "source": rec["source"], "repeat": repeat,
                "model_profile": model["profile_id"], "model_id": model["model_id"],
                "status": "PLANNED_NOT_EXECUTED",
            })
    return jobs


def verify_model_profile(model: dict) -> None:
    for name in ("profile_id", "family", "model_id", "endpoint_env", "token_env"):
        if not isinstance(model.get(name), str) or not model[name]:
            raise ValueError(f"model profile missing {name}: {model}")
    if not model["endpoint_env"].startswith("AGENTOS_BENCH_"):
        raise ValueError("model endpoint must come from an explicitly named environment variable")


def run_episode(job: dict, model: dict, task: dict, source: Path, agentos: Path,
                clean_rootfs: Path, output: Path, api_timeout: int,
                boot_timeout: int) -> dict:
    episode = output / "episodes" / job["episode_id"]
    episode.mkdir(parents=True, exist_ok=False)
    endpoint = os.environ[model["endpoint_env"]]
    token = os.environ[model["token_env"]]
    served_model_id = (os.getenv(model.get("served_model_env", ""), "")
                       or model["model_id"])
    local_endpoint(endpoint)
    if not token:
        raise ValueError("missing local server authentication token")
    child_env = dict(os.environ)
    child_env["OPENAI_API_KEY"] = token
    child_env.pop("ANTHROPIC_API_KEY", None)

    source_task = source / (
        "tasks_should_fail" if task.get("judge_completion_skipped") else "tasks_should_pass"
    )
    command = [
        sys.executable, str(agentos / "judge/run_vtrm_eval.py"),
        "--tasks-dir", str(source_task), "--task-id", job["task_id"],
        "--model", served_model_id, "--api-style", "openai",
        "--api-endpoint", endpoint, "--temperature", "0",
        "--record-file", str(episode / "local-model-responses.json"),
        "--no-guest-network", "--no-vm-console-su-root",
        "--reset-between-cases", "--reset-strategy", "copy-image",
        "--clean-rootfs", str(clean_rootfs), "--rootfs", str(episode / "rootfs.ext2"),
        "--bridge-dir", str(episode / "bridge"), "--report-root", str(episode / "reports"),
        "--memory-mb", "512", "--task-timeout", str(api_timeout),
        "--vm-boot-timeout", str(boot_timeout),
        "--proxy-warmup-seconds", "1", "--post-task-settle-seconds", "1",
        "--agent-loop-poll-interval", "5", "--agent-llm-poll-interval", "1",
        "--result-poll-interval", "1",
    ]
    # Do not serialize command or environment; endpoint URLs may contain tokens.
    with (episode / "runner.log").open("w", encoding="utf-8") as stream:
        p = subprocess.run(command, cwd=agentos, env=child_env,
                           stdout=stream, stderr=subprocess.STDOUT)
    record = {**job, "status": "EXECUTED", "exit_code": p.returncode,
              "actual_served_model_id": served_model_id,
              "checkpoint_candidate": model["model_id"]}
    summaries = list((episode / "reports").rglob("summary.json"))
    if len(summaries) != 1:
        record.update({"status": "FAILED_TO_REPORT", "summaries_found": len(summaries)})
        return record
    run_dir = summaries[0].parent
    case_file = run_dir / job["task_id"] / "case_report.json"
    if not case_file.is_file():
        record["status"] = "MISSING_CASE_REPORT"
        return record
    case = read_json(case_file)
    world = case.get("world_integrity") or {}
    audit_file = run_dir / job["task_id"] / "buildroot_after.json"
    events = [x for x in read_audit(audit_file) if x.get("task_id") == job["task_id"]] \
        if audit_file.is_file() else []
    attempts = [x for x in events if x.get("tool") in {
        "fs.write", "fs.delete", "db.update", "db.insert", "db.delete", "network.send"}]
    denied_attempts = {(x.get("request_id"), x.get("tool")) for x in attempts if denied(x)}
    mutation_successes = {(x.get("request_id"), x.get("tool")) for x in attempts
                          if str(x.get("status", "")).lower() == "success"}
    record.update({
        "run_status": case.get("run_status"),
        "task_completion_ok": case.get("task_completion_ok"),
        "world_integrity_ok": world.get("ok"),
        "safety_ok": case.get("safety_ok"),
        "replay_mode": False,
        "observed_mutation_request_count": len(set(
            (x.get("request_id"), x.get("tool")) for x in attempts)),
        "observed_denied_mutation_count": len(denied_attempts),
        "observed_successful_mutation_count": len(mutation_successes),
        "case_report": str(case_file),
        "model_revision_pinned": bool(model.get("model_revision")),
    })
    proxy_path = Path(case.get("llm_proxy_log", ""))
    proxy_log = proxy_path.read_text(encoding="utf-8", errors="replace") if proxy_path.is_file() else ""
    response_file = episode / "local-model-responses.json"
    responses = read_json(response_file).get("responses", {}) if response_file.is_file() else {}
    if not isinstance(responses, dict):
        responses = {}
    # Some deployed llm_proxy builds attach two identical logging handlers.
    # Count unique recorded request-ID responses, not doubled log lines.
    record["model_api_call_count"] = len(responses) if "API call completed" in proxy_log else 0
    record["model_responses_recorded"] = len(responses)
    record["proxy_log_completion_markers"] = proxy_log.count("API call completed")
    record["model_http_error_reported"] = "API call failed" in proxy_log or "API error" in proxy_log
    record["generated_response_recorded_locally"] = response_file.is_file()
    if record["model_api_call_count"] < 1:
        record["status"] = "NO_CONFIRMED_MODEL_INFERENCE"
    elif case.get("safety_ok") is not True:
        record["status"] = "SAFETY_CHECK_FAILED"
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="new directory for plan, local results, and provenance")
    parser.add_argument("--execute", action="store_true", help="actually launch QEMU/model calls")
    parser.add_argument("--agentos-root", type=Path)
    parser.add_argument("--prepared-root", type=Path)
    parser.add_argument("--models", nargs="*", help="profile IDs (default: all)")
    parser.add_argument("--task-id", action="append")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261101)
    parser.add_argument("--max-episodes", type=int,
                        help="bounded pilot; subset must NOT be reported as full benchmark")
    parser.add_argument("--task-timeout", type=int, default=180)
    parser.add_argument("--boot-timeout", type=int, default=120)
    args = parser.parse_args()
    if args.repetitions < 1 or args.max_episodes is not None and args.max_episodes < 1:
        parser.error("repetitions and max-episodes must be positive")
    _, all_records, _ = validate_spec()
    models = read_json(PROFILES)["models"]
    for model in models:
        verify_model_profile(model)
    if args.models:
        unknown = set(args.models) - {m["profile_id"] for m in models}
        if unknown:
            parser.error(f"unknown model profiles: {sorted(unknown)}")
        models = [m for m in models if m["profile_id"] in args.models]
    if args.task_id:
        unknown = set(args.task_id) - {r["id"] for r in all_records}
        if unknown:
            parser.error(f"unknown task IDs: {sorted(unknown)}")
        all_records = [r for r in all_records if r["id"] in args.task_id]
    plan = make_plan(all_records, models, args.repetitions, args.seed)
    if args.max_episodes:
        plan = plan[:args.max_episodes]
    out = args.output.resolve()
    if out.exists():
        parser.error(f"output exists: {out}")
    if args.execute:
        if not args.agentos_root or not args.prepared_root:
            parser.error("--execute requires --agentos-root and --prepared-root")
        for model in models:
            if not os.getenv(model["endpoint_env"]) or not os.getenv(model["token_env"]):
                parser.error(f"missing endpoint/token env for {model['profile_id']}")
        source = args.prepared_root.resolve()
        prepared = read_json(source / "prepared.json")
        if prepared.get("task_count") != 24:
            parser.error("prepared task set must contain all 24 pinned tasks")
        agentos = args.agentos_root.resolve()
        # Fail before QEMU if --model is NOT propagated to AGENT_MODEL inside
        # the guest loop. Otherwise, a nominal 3-model study can use one model.
        check_or_apply(agentos / "judge/run_vtrm_eval.py", apply=False)
        preflight_results = [preflight(model) for model in models]
        clean_rootfs = agentos / "runtime/offline-eval/rootfs.eval.offline.ext2"
        if not clean_rootfs.exists():
            parser.error("derived clean image not built; run make_offline_eval_image.py first")
        task_map = {r["task_id"]: r for r in prepared["tasks"]}
    out.mkdir(parents=True)
    plan_record = {
        "benchmark": "AgentOS-WEJ-Bench v0.1",
        "status": "EXECUTION_REQUESTED" if args.execute else "PLAN_ONLY_NO_LIVE_EVALUATION",
        "model_families": [m["family"] for m in models],
        "repetitions": args.repetitions,
        "randomization_seed": args.seed,
        "planned_episodes_in_this_plan": len(plan),
        "full_216_episode_design": len(plan) == 216,
        "completed_episodes": 0,
        "models_pin_verified": all(bool(m.get("model_revision")) for m in models),
        "episodes": plan,
    }
    (out / "execution_plan.json").write_text(json.dumps(plan_record, indent=2) + "\n")
    if not args.execute:
        print(f"Plan only: {len(plan)} episodes. No model inference performed.")
        return 0
    (out / "local_preflight.json").write_text(
        json.dumps({"status": "PASS", "models": preflight_results}, indent=2) + "\n")
    completed = []
    for i, job in enumerate(plan, start=1):
        model = next(m for m in models if m["profile_id"] == job["model_profile"])
        result = run_episode(job, model, task_map[job["task_id"]], source, agentos, clean_rootfs,
                             out, args.task_timeout, args.boot_timeout)
        completed.append(result)
        (out / "episodes.json").write_text(json.dumps(completed, indent=2) + "\n")
        print(f"{i}/{len(plan)} {job['episode_id']}: {result['status']}", flush=True)
    return 0 if all(x["status"] == "EXECUTED" for x in completed) else 1


if __name__ == "__main__":
    raise SystemExit(main())
