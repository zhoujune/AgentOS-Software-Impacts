#!/usr/bin/env python3
"""Compare two validated AgentOS offline repeated-benchmark JSON reports.

Only Python's standard library is required. This utility rejects incomplete
or failed benchmark reports rather than interpreting their timings as results.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

PHASES = {
    "task_enqueue_and_wait_seconds": "Task enqueue/wait",
    "case_runtime_including_reset_seconds": "End-to-end case incl. reset",
    "vm_boot_to_ready_seconds": "VM boot-to-ready",
    "image_reset_seconds": "Image reset",
}
SAME_ENV = (
    "cassette_sha256", "kernel_sha256", "platform", "kernel", "machine",
    "cpu_model", "qemu_version", "memory_mb", "vm_boot_timeout_seconds",
    "task_timeout_seconds", "reset_strategy",
    "llm_proxy_poll_interval_seconds", "result_poll_interval_seconds",
)
EXPECTED_TASKS = {
    ("benign", "301-workspace-hello"),
    ("benign", "302-workspace-json"),
    ("benign", "321-delete-workspace-file"),
    ("denials", "115-direct-db-task-disable-update"),
    ("denials", "118-direct-db-audit-insert"),
    ("denials", "122-direct-readonly-db-delete"),
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def load_validated(path: Path) -> dict:
    report = json.loads(path.read_text(encoding="utf-8"))
    label = str(path)
    repetitions = report.get("expected_repetitions")
    require(isinstance(repetitions, int) and repetitions >= 3,
            f"{label}: need >=3 requested repetitions")
    require(report.get("all_ok") is True and not report.get("errors"),
            f"{label}: incomplete or failing aggregate")
    require(report.get("completed_repetitions") == repetitions,
            f"{label}: incomplete repetition count")
    reps = report.get("repetitions", [])
    require(len(reps) == repetitions and all(r.get("all_ok") is True for r in reps),
            f"{label}: failed or missing run")
    require(report.get("task_count_per_repetition") == len(EXPECTED_TASKS),
            f"{label}: unexpected task count")
    records = report.get("case_records", [])
    require(len(records) == repetitions * len(EXPECTED_TASKS),
            f"{label}: unexpected case record count")
    counts = Counter((int(r["repetition"]), r["suite"], r["task_id"]) for r in records)
    for rep in reps:
        index = int(rep["repetition"])
        found = {(suite, task) for (i, suite, task), count in counts.items()
                 if i == index and count == 1}
        require(found == EXPECTED_TASKS, f"{label}: incorrect task set in run {index}")
    require(sorted(int(r["repetition"]) for r in reps) ==
            list(range(1, repetitions + 1)), f"{label}: run indices incomplete")
    for phase in PHASES:
        entry = report.get("phase_timing_summary", {}).get(phase)
        require(isinstance(entry, dict), f"{label}: missing {phase}")
        require(entry.get("sample_count") == len(records),
                f"{label}: missing {phase} samples")
        for key in ("median", "p95", "mean"):
            require(isinstance(entry.get(key), (int, float)),
                    f"{label}: missing {phase}.{key}")
    return report


def compare(a: dict, b: dict) -> dict:
    require(a["completed_repetitions"] == b["completed_repetitions"],
            "Repetition counts differ")
    ea, eb = a.get("environment", {}), b.get("environment", {})
    for key in SAME_ENV:
        require(key in ea and key in eb and ea[key] == eb[key],
                f"Unmatched environment setting: {key}: {ea.get(key)} vs {eb.get(key)}")
    require(ea.get("clean_rootfs_sha256") != eb.get("clean_rootfs_sha256"),
            "Profiles must use distinct experimental images")
    metrics = {}
    for field, label in PHASES.items():
        av = a["phase_timing_summary"][field]
        bv = b["phase_timing_summary"][field]
        median_a, median_b = float(av["median"]), float(bv["median"])
        metrics[field] = {
            "name": label,
            "sample_count_each": int(av["sample_count"]),
            "a_median_s": median_a,
            "a_p95_s": float(av["p95"]),
            "b_median_s": median_b,
            "b_p95_s": float(bv["p95"]),
            "median_difference_s": round(median_b - median_a, 6),
            "median_reduction_pct": round(100.0 * (median_a - median_b) / median_a, 3)
            if median_a > 0 else None,
        }
    per_run_wait = {}
    for label, report in (("A", a), ("B", b)):
        per_run_wait[label] = [
            {"repetition": int(rep["repetition"]),
             "task_wait_median_s": rep["phase_timing_summary"]
                ["task_enqueue_and_wait_seconds"]["median"]}
            for rep in report["repetitions"]
        ]
    return {
        "validation": "PASS",
        "repetitions_each": a["completed_repetitions"],
        "cases_each": len(a["case_records"]),
        "controls": {k: ea[k] for k in SAME_ENV},
        "a_image_sha256": ea["clean_rootfs_sha256"],
        "b_image_sha256": eb["clean_rootfs_sha256"],
        "a_guest_poll_s": [ea.get("agent_loop_poll_interval_seconds"),
                           ea.get("agent_llm_poll_interval_seconds")],
        "b_guest_poll_s": [eb.get("agent_loop_poll_interval_seconds"),
                           eb.get("agent_llm_poll_interval_seconds")],
        "metrics": metrics,
        "per_run_wait": per_run_wait,
        "limitations": [
            "A runs precede B runs; not randomized/interleaved.",
            "Six exact-replay tasks only; no live LLM inference.",
            "Pooled case-level medians are descriptive, not independent samples "
            "suitable for a significance test.",
            "A/B image difference was separately verified in two embedded guest scripts.",
        ],
    }


def render(result: dict) -> str:
    lines = [
        "# AgentOS controlled guest-polling comparison", "",
        f"**Validation: {result['validation']}**; "
        f"{result['repetitions_each']} complete repetitions and "
        f"{result['cases_each']} passed cases per profile.", "",
        "| Metric | A median (s) | B median (s) | A p95 (s) | B p95 (s) | Median reduction |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for m in result["metrics"].values():
        reduction = m["median_reduction_pct"]
        reduction_str = "n/a" if reduction is None else f"{reduction:+.2f}%"
        lines.append(
            f"| {m['name']} | {m['a_median_s']:.3f} | {m['b_median_s']:.3f}"
            f" | {m['a_p95_s']:.3f} | {m['b_p95_s']:.3f} | {reduction_str} |"
        )
    lines += ["", "## Per-repetition task-wait medians", "",
              "| Repetition | A (s) | B (s) |", "| --- | ---: | ---: |"]
    av = result["per_run_wait"]["A"]
    bv = result["per_run_wait"]["B"]
    for left, right in zip(av, bv):
        lines.append(f"| {left['repetition']} | {left['task_wait_median_s']:.3f} "
                     f"| {right['task_wait_median_s']:.3f} |")
    lines += ["", "## Interpretation constraints", ""]
    lines += [f"- {item}" for item in result["limitations"]]
    lines += ["", "The comparison is descriptive; no statistical significance "
              "or full-task-suite security claim is established.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--a", required=True, type=Path, help="A repeated_benchmark.json")
    parser.add_argument("--b", required=True, type=Path, help="B repeated_benchmark.json")
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    args = parser.parse_args()
    a = load_validated(args.a)
    b = load_validated(args.b)
    result = compare(a, b)
    args.markdown.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.markdown.write_text(render(result), encoding="utf-8")
    args.json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"VALIDATED {result['cases_each']} cases per profile; outputs: "
          f"{args.markdown}, {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
