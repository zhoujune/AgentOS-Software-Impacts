#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/zhoujune/AgentOS.git"
UPSTREAM_COMMIT="4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATCH_FILE="$SCRIPT_DIR/../patches/0001-agentos-offline-replay-overlay.patch"
DESTINATION="${1:-}"

if [[ -z "$DESTINATION" ]]; then
  echo "Usage: $0 /path/to/new-AgentOS-checkout" >&2
  exit 2
fi
if [[ -e "$DESTINATION" ]]; then
  echo "Refusing to overwrite existing destination: $DESTINATION" >&2
  exit 2
fi
if [[ ! -f "$PATCH_FILE" ]]; then
  echo "Missing overlay patch: $PATCH_FILE" >&2
  exit 2
fi

git clone "$UPSTREAM_URL" "$DESTINATION"
git -C "$DESTINATION" checkout --detach "$UPSTREAM_COMMIT"
actual="$(git -C "$DESTINATION" rev-parse HEAD)"
if [[ "$actual" != "$UPSTREAM_COMMIT" ]]; then
  echo "Unexpected upstream commit: $actual" >&2
  exit 1
fi

git -C "$DESTINATION" apply --check "$PATCH_FILE"
git -C "$DESTINATION" apply "$PATCH_FILE"

(
  cd "$DESTINATION"
  python3 -m unittest discover -s judge -p 'test_*.py' -v
  bash -n scripts/test/run_offline_smoke.sh
  bash -n scripts/test/run_offline_representative_suite.sh
  bash -n scripts/test/run_offline_repeated_benchmark.sh
)

if [[ "${RUN_QEMU_SMOKE:-0}" == "1" ]]; then
  bash "$DESTINATION/scripts/test/run_offline_smoke.sh"
fi

echo "Reconstruction complete."
echo "Upstream base: $UPSTREAM_COMMIT"
echo "Overlay patch: $PATCH_FILE"
echo "Destination: $DESTINATION"
