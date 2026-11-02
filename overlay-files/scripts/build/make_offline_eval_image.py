#!/usr/bin/env python3
"""Build a disposable offline guest image; never modify the canonical base."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
CLEAN = ROOT / "artifacts/images/rootfs.eval.clean.ext2"
CLEAN_SHA = "d61a40dc7f2090b19505886020593674cdf2b5dd2f85fbcb9c02c523745a5f61"
GUEST = ROOT / "br2-external/board/agentos/x86_64/overlay"
FILES = [
    (GUEST / "etc/autologin-agent.sh", "/etc/autologin-agent.sh", 0, 0),
    (GUEST / "home/agent/agent_main_loop.sh", "/home/agent/agent_main_loop.sh", 1000, 1000),
    (GUEST / "home/agent/agent_runner.py", "/home/agent/agent_runner.py", 1000, 1000),
]


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cmd(*args):
    completed = subprocess.run(args, text=True, capture_output=True)
    output = completed.stdout + completed.stderr
    if completed.returncode or "file not found" in output.lower():
        raise RuntimeError(f"failed: {args}: {output}")
    return output


def debug(image, command, write=False):
    return cmd("debugfs", *(["-w"] if write else []), "-R", command, str(image))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, default=CLEAN)
    ap.add_argument("--output", type=Path,
                    default=ROOT / "runtime/offline-eval/rootfs.eval.offline.ext2")
    args = ap.parse_args()
    base, output = args.base.resolve(), args.output.resolve()
    if not base.is_file() or base == output or output.exists():
        raise SystemExit("base missing or output would overwrite an existing file")
    before = digest(base)
    if base == CLEAN.resolve() and before != CLEAN_SHA:
        raise SystemExit("canonical image hash mismatch")
    policy = FILES[0][0].read_text()
    required_policy = [
        "chown root:root /workspace",
        "mkdir -p /workspace/passcases /workspace/passcases_hard",
        "chown -R 1000:1000 /workspace/passcases /workspace/passcases_hard",
    ]
    if not all(x in policy for x in required_policy):
        raise SystemExit("missing least-privilege workspace policy")
    if re.search(r"chown\s+-R\s+1000:1000\s+/workspace(?:\s|$)", policy):
        raise SystemExit("refusing broad recursive chown")
    output.parent.mkdir(parents=True, exist_ok=True)
    work = output.with_name(output.name + ".building")
    if work.exists():
        raise SystemExit("unfinished build exists")
    try:
        shutil.copyfile(base, work)
        with tempfile.TemporaryDirectory() as scratch:
            for source, guest, uid, gid in FILES:
                if not source.is_file():
                    raise SystemExit(f"missing source: {source}")
                debug(work, f"rm {guest}", True)
                debug(work, f"write {source} {guest}", True)
                debug(work, f"sif {guest} mode 0100755", True)
                debug(work, f"sif {guest} uid {uid}", True)
                debug(work, f"sif {guest} gid {gid}", True)
                retrieved = Path(scratch) / source.name
                debug(work, f"dump {guest} {retrieved}")
                if digest(retrieved) != digest(source):
                    raise RuntimeError(f"guest content mismatch: {guest}")
                stat = debug(work, f"stat {guest}")
                if not all(re.search(pattern, stat) for pattern in [
                    r"Mode:\s*0?755\b",
                    rf"User:\s*{uid}\b",
                    rf"Group:\s*{gid}\b",
                ]):
                    raise RuntimeError(f"guest mode/owner mismatch: {guest}")
        cmd("e2fsck", "-fn", str(work))
        if digest(base) != before:
            raise RuntimeError("canonical image changed during preparation")
        work.rename(output)
        manifest = {
            "base_sha256": before, "image_sha256": digest(output),
            "updated_guest_files": [entry[1] for entry in FILES],
            "scope": "post-build overlay only; not a full Buildroot rebuild",
        }
        output.with_name(output.name + ".manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n")
        print(json.dumps(manifest, indent=2))
    finally:
        if work.exists():
            work.unlink()


if __name__ == "__main__":
    main()
