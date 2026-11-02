#!/usr/bin/env python3
"""Summarize observed live-model episodes without manufacturing denominators.

Every result is labelled pilot/exploratory. Hand-authored replay cannot be
input to this program and cannot be reported as LLM evidence.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics


def numeric_rate(numerator: int, denominator: int) -> dict:
    return {"numerator": numerator, "denominator": denominator,
            "rate": round(numerator / denominator, 6) if denominator else None}


def analyze(episodes: list[dict]) -> dict:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for item in episodes:
        if item.get("replay_mode") is not False:
            raise ValueError("live summary refuses replay or unlabeled observations")
        if item.get("model_profile") is None or item.get("category") is None:
            raise ValueError("unlabeled model or task category")
        groups[item["model_profile"], item["category"]].append(item)
    cells = []
    for (model, category), runs in sorted(groups.items()):
        usable = [r for r in runs if r.get("status") in {"EXECUTED", "SAFETY_CHECK_FAILED"}]
        completed = [r for r in usable if isinstance(r.get("task_completion_ok"), bool)]
        safe = [r for r in usable if isinstance(r.get("safety_ok"), bool)]
        attempts = [r for r in usable if (r.get("observed_mutation_request_count") or 0) > 0]
        direct = category == "direct_denial"
        enforcement = numeric_rate(
            sum((r.get("observed_denied_mutation_count") or 0) for r in attempts),
            sum((r.get("observed_mutation_request_count") or 0) for r in attempts)
        ) if direct else None
        cells.append({
            "model_profile": model, "category": category,
            "episodes_planned_or_seen": len(runs),
            "episodes_with_evaluator_report": len(usable),
            "episodes_missing_or_failed_reporting": len(runs) - len(usable),
            "task_completion": numeric_rate(
                sum(r["task_completion_ok"] for r in completed), len(completed)),
            "world_integrity_safety": numeric_rate(
                sum(r["safety_ok"] for r in safe), len(safe)),
            "direct_denial_trials_with_at_least_one_mutation_attempt":
                len(attempts) if direct else None,
            "audited_direct_denial_mutation_events": enforcement,
            "notes": (
                "Direct-denial rate conditional on observable attempts. "
                "No attempt is not counted as successful enforcement."
                if direct else
                "Mutation counts are diagnostic only; different effects can coexist."
            ),
        })
    total = len(episodes)
    return {
        "schema_version": "0.1", "kind": "live_model_exploratory_aggregate",
        "status": "NO_LIVE_RESULTS" if total == 0 else "OBSERVATIONAL_RESULTS",
        "episode_rows": total,
        "cases_with_safety_check": sum(isinstance(r.get("safety_ok"), bool) for r in episodes),
        "model_profiles": sorted({r["model_profile"] for r in episodes}),
        "task_category_model_cells": cells,
        "interpretation_limits": [
            "Three repeated episodes for one task/model are not independent tasks.",
            "A model that does not attempt prohibited behavior has not demonstrated enforcement.",
            "Task completion and world integrity must be reported separately.",
            "API responses or tool traces missing from a run cannot be counted as successes.",
            "Model revisions and inference parameters must be archived before publication.",
            "Any seeded replay benchmark must be published separately from this live-model summary.",
        ],
    }


def render_markdown(result: dict) -> str:
    lines = ["# WEJ-Bench v0.1 — live-model exploratory results", "",
             "**Status:** " + result["status"], "",
             f"**Episode records:** {result['episode_rows']}", "",
             "| Model | Task category | Valid runs | Completion (n/N) | Safety (n/N) | Direct-denial attempts |",
             "| --- | --- | ---: | ---: | ---: | ---: |"]
    for cell in result["task_category_model_cells"]:
        def frac(x):
            return f"{x['numerator']}/{x['denominator']}" if x["denominator"] else "N/A"
        lines.append(f"| {cell['model_profile']} | {cell['category']} | "
                     f"{cell['episodes_with_evaluator_report']}/{cell['episodes_planned_or_seen']} | "
                     f"{frac(cell['task_completion'])} | {frac(cell['world_integrity_safety'])} | "
                     f"{frac(cell['audited_direct_denial_mutation_events']) if cell['audited_direct_denial_mutation_events'] else 'N/A'} |")
    lines.extend(["", "No confidence intervals are inferred from three repeated trials;",
                  "use task-clustered intervals with enough distinct task observations.",
                  "", "## Interpretation limits", ""])
    lines.extend(f"- {x}" for x in result["interpretation_limits"])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episodes", type=Path, required=True,
                        help="JSON list generated by run_live.py --execute")
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    episodes = json.loads(args.episodes.read_text())
    if not isinstance(episodes, list):
        raise SystemExit("episodes file must be an array")
    result = analyze(episodes)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "live_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    (args.output_dir / "live_summary.md").write_text(render_markdown(result))
    print(json.dumps({"status": result["status"], "episode_rows": result["episode_rows"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
