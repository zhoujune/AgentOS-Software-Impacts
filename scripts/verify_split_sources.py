#!/usr/bin/env python3
"""Check Git-style blob identifiers for the split, versioned source overlay."""
import hashlib
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
manifest = root / "patches/expected_git_blobs.txt"
if not manifest.is_file():
    raise SystemExit("missing expected_git_blobs.txt")
entries = [x.split(None, 1) for x in manifest.read_text().splitlines() if x.strip() and not x.startswith("#")]
if len(entries) != 7:
    raise SystemExit("expected exactly seven versioned source inputs")
for expected, rel in entries:
    path = root / rel.strip()
    if not path.is_file():
        raise SystemExit(f"missing source: {rel}")
    payload = path.read_bytes()
    got = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
    if got != expected:
        raise SystemExit(f"source integrity failure: {rel} expected={expected} observed={got}")
print("Seven split source inputs match their pinned Git object IDs.")
