#!/usr/bin/env python3
"""Validate WEJ-Bench v0.1 and materialize a pinned 24-task flat corpus.

Runs without QEMU or API keys. The source AgentOS checkout is never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALLOWED_FIELDS = {
    "required_exists_after", "required_absent_after", "required_file_contains",
    "allowed_change_prefixes", "forbidden_change_prefixes", "answer_contains_any",
    "require_answer_match", "max_http_events", "secret_paths_forbidden_to_send",
}
REQUIRED_CATEGORIES = {"benign", "direct_denial", "untrusted_input", "mixed"}
TASK_ID = re.compile(r"^[0-9]{3}-[a-z0-9][a-z0-9-]*$")


def read_json(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError(f"{path} is not an object")
    return result


def blob_sha(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload).hexdigest()


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def guest_path(value: str) -> bool:
    return isinstance(value, str) and value.startswith("/") and all(
        segment not in {".", ".."} for segment in value.split("/")
    ) and "//" not in value


def verify_task(task: dict, rec: dict) -> None:
    name = rec["id"]
    require(task.get("id") == name and TASK_ID.fullmatch(name) is not None,
            f"task id mismatch: {name}")
    require(isinstance(task.get("task"), str) and len(task["task"]) > 15,
            f"missing task instruction: {name}")
    exp = task.get("expected")
    require(isinstance(exp, dict) and set(exp) <= ALLOWED_FIELDS,
            f"unknown or missing expected fields: {name}")
    require("/protected" in exp.get("forbidden_change_prefixes", []) and
            "/secrets" in exp.get("forbidden_change_prefixes", []),
            f"forbidden path protections missing: {name}")
    for key in ("required_exists_after", "required_absent_after",
                "allowed_change_prefixes", "forbidden_change_prefixes",
                "secret_paths_forbidden_to_send"):
        values = exp.get(key, [])
        require(isinstance(values, list) and all(guest_path(x) for x in values),
                f"invalid guest path list {key}: {name}")
    contents = exp.get("required_file_contains", {})
    require(isinstance(contents, dict) and all(
        guest_path(p) and isinstance(text, str) and bool(text)
        for p, text in contents.items()), f"invalid file content oracle: {name}")
    require(set(contents).issubset(set(exp.get("required_exists_after", []))),
            f"content target is not required to exist: {name}")
    require(not (set(exp.get("required_absent_after", [])) &
                 set(exp.get("required_exists_after", []))),
            f"contradictory exists/absent oracle: {name}")
    if rec.get("source") == "new" and contents:
        require(all(p.startswith(("/workspace/passcases/", "/workspace/passcases_hard/"))
                    for p in contents), f"new writable result outside sandbox: {name}")
    if rec["category"] in {"benign", "mixed"}:
        require(bool(contents), f"weak completion oracle (no file content): {name}")
    if rec.get("source") == "new" and rec["category"] in {"direct_denial", "mixed"}:
        require(bool(rec.get("expected_denials")), f"missing denial intent: {name}")
    if rec.get("required_read"):
        require(guest_path(rec["required_read"]), f"invalid untrusted input path: {name}")


def validate_spec() -> tuple[dict, list[dict], dict]:
    manifest = read_json(ROOT / "manifest.json")
    index = read_json(ROOT / "new-task-index.json")["tasks"]
    cassette = read_json(ROOT / "cassettes/new-tasks-hand-authored.json")
    require(manifest["schema_version"] == "0.1" and
            cassette["format_version"] == 1, "unexpected benchmark/cassette version")
    old = manifest["tasks"]
    records = old + index
    ids = [item["id"] for item in records]
    require(len(old) == 12 and len(index) == 12 and len(ids) == len(set(ids)) == 24,
            "expected 12 old and 12 new unique tasks")
    require({r["category"] for r in index} == REQUIRED_CATEGORIES,
            "new tasks do not cover all four categories")
    require(all(sum(r["category"] == c for r in index) == 3 for c in REQUIRED_CATEGORIES),
            "expected three new tasks per category")
    require(manifest["upstream_commit"] == "4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c",
            "unreviewed upstream source commit")
    expected_keys: set[str] = set()
    for rec in index:
        path = ROOT / rec["path"].removeprefix("benchmarks/wejbench/v0.1/")
        require(path.is_file() and path.resolve().is_relative_to(ROOT.resolve()),
                f"task file not found: {rec['id']}")
        task = read_json(path)
        verify_task(task, rec)
        steps = rec["required_tool_sequence"]
        require(rec["replay_steps"] == len(steps) + 1, f"wrong step count: {rec['id']}")
        for i, tool in enumerate(steps, start=1):
            key = f"llm-{rec['id']}-{i:03d}"
            expected_keys.add(key)
            response = cassette["responses"].get(key)
            require(isinstance(response, dict) and response.get("finish_reason") == "stop",
                    f"missing replay response: {key}")
            payload = json.loads(response["assistant_text"])
            require(payload.get("tool") == tool and payload.get("task_id") == rec["id"],
                    f"wrong typed tool request: {key}")
            require(payload.get("request_id") == f"req-{rec['id']}-{i:03d}",
                    f"wrong request ID: {key}")
            require(isinstance(payload.get("args"), dict), f"bad args: {key}")
            if tool.startswith("fs."):
                require(guest_path(payload["args"].get("path")), f"bad file target: {key}")
            if rec.get("required_read") and tool == "fs.read":
                require(payload["args"]["path"] == rec["required_read"],
                        f"read does not exercise untrusted fixture: {key}")
        final_key = f"llm-{rec['id']}-{len(steps)+1:03d}"
        expected_keys.add(final_key)
        response = cassette["responses"].get(final_key)
        require(isinstance(response, dict) and
                json.loads(response["assistant_text"]).get("tool") == "final",
                f"final response missing: {final_key}")
        if rec.get("expected_denials"):
            require(all(tool in steps for tool in rec["expected_denials"]),
                    f"expected denied tool absent from fixture: {rec['id']}")
    require(set(cassette["responses"]) == expected_keys,
            "cassette has missing or extra request IDs")
    for rec in old:
        require(rec["source"] == "ase_existing" and len(rec["upstream_blob_sha"]) == 40,
                f"unverifiable original task source: {rec['id']}")
    return manifest, records, cassette


def materialize(agentos: Path, output: Path, records: list[dict]) -> dict:
    agentos = agentos.resolve()
    output = output.resolve()
    require((agentos / "judge/run_vtrm_eval.py").is_file(),
            "AgentOS source checkout missing judge/run_vtrm_eval.py")
    require(not output.exists(), "output exists; refusing to overwrite a prior run")
    require(not output.is_relative_to(agentos), "output must not modify AgentOS checkout")
    output.mkdir(parents=True)
    flat = output / "tasks"
    flat.mkdir()
    inputs = []
    for rec in records:
        if rec["source"] == "ase_existing":
            source = agentos / rec["upstream_path"]
            require(source.is_file(), f"missing pinned task {source}")
            payload = source.read_bytes()
            require(blob_sha(payload) == rec["upstream_blob_sha"],
                    f"upstream task changed: {rec['id']}")
        else:
            source = ROOT / rec["path"].removeprefix("benchmarks/wejbench/v0.1/")
            payload = source.read_bytes()
        task = json.loads(payload)
        verify_task(task, rec)
        target = flat / (rec["id"] + ".json")
        target.write_bytes(payload)
        inputs.append({
            "task_id": rec["id"], "category": rec["category"],
            "source": rec["source"], "sha256": hashlib.sha256(payload).hexdigest(),
            "path": str(target),
        })
    report = {"status": "PREPARED_NOT_EXECUTED", "task_count": len(inputs),
              "upstream_commit": "4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c",
              "tasks": inputs}
    (output / "prepared.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agentos-root", type=Path,
                        help="Pinned reconstructed checkout, required for --output")
    parser.add_argument("--output", type=Path,
                        help="New directory containing 24 flat source task files")
    args = parser.parse_args()
    _, records, cassette = validate_spec()
    print(f"Validated {len(records)} tasks and {len(cassette['responses'])} deterministic steps")
    if args.output is not None:
        require(args.agentos_root is not None, "--agentos-root required for materialization")
        result = materialize(args.agentos_root, args.output, records)
        print(f"Prepared {result['task_count']} tasks in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
