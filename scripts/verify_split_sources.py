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
sha_manifest = root / "patches/expected_sha256.txt"
if not sha_manifest.is_file():
    raise SystemExit("missing expected_sha256.txt")
sha_entries = [line.split(None, 1) for line in sha_manifest.read_text().splitlines()
               if line.strip() and not line.startswith("#")]
if len(sha_entries) != len(entries):
    raise SystemExit("SHA-256 manifest entry count differs from Git-object manifest")
if {name.strip() for _, name in sha_entries} != {name.strip() for _, name in entries}:
    raise SystemExit("SHA-256 and Git blob manifest paths differ")
for expected_sha, rel in sha_entries:
    got_sha = hashlib.sha256((root / rel.strip()).read_bytes()).hexdigest()
    if got_sha != expected_sha:
        raise SystemExit(f"SHA-256 mismatch: {rel}: {got_sha}")
print("Seven split source inputs match pinned Git object and SHA-256 checksums.")
