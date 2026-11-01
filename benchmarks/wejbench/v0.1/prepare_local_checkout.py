#!/usr/bin/env python3
"""Apply/review the minimal AgentOS guest model-selector propagation fix.

The original evaluator passes --model only to the host proxy. The guest loop
otherwise uses its default AGENT_MODEL. A multi-model experiment MUST make
those names match. Operates on the reconstructed candidate, never upstream.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re

TARGET = '            f"AGENT_MODE={shlex.quote(args.agent_mode)} "'
INSERTED = '            f"AGENT_MODEL={shlex.quote(args.model)} "'
LOOP = '            f"AGENT_LOOP_POLL_INTERVAL={shlex.quote(str(args.agent_loop_poll_interval))} "'


def check_or_apply(path: Path, apply: bool) -> str:
    if not path.is_file():
        raise ValueError(f"evaluator missing: {path}")
    text = path.read_text(encoding="utf-8")
    if text.count(INSERTED) == 1:
        return "ALREADY_PRESENT"
    if INSERTED in text:
        raise ValueError("unexpected duplicate AGENT_MODEL propagation")
    needle = TARGET + "\n" + LOOP
    if text.count(needle) != 1:
        raise ValueError("expected guest bootstrap anchor not present exactly once")
    if not apply:
        raise ValueError("guest model name is NOT propagated; run prepare_local_checkout.py --apply")
    text = text.replace(needle, TARGET + "\n" + INSERTED + "\n" + LOOP)
    path.write_text(text, encoding="utf-8")
    return "PATCHED"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agentos-root", type=Path, required=True)
    ap.add_argument("--apply", action="store_true", help="explicitly patch reconstructed local checkout")
    args = ap.parse_args()
    path = args.agentos_root / "judge/run_vtrm_eval.py"
    outcome = check_or_apply(path, args.apply)
    print(outcome + ": " + str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
