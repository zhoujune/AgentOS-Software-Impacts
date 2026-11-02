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
python3 "$SCRIPT_DIR/verify_split_sources.py"

git clone "$UPSTREAM_URL" "$DESTINATION"
git -C "$DESTINATION" checkout --detach "$UPSTREAM_COMMIT"
actual="$(git -C "$DESTINATION" rev-parse HEAD)"
if [[ "$actual" != "$UPSTREAM_COMMIT" ]]; then
  echo "Unexpected upstream commit: $actual" >&2
  exit 1
fi

for patch in \
  0001-agentos-offline-replay-overlay.patch \
  0002-offline-aggregation-and-fixtures.patch \
  0003-offline-tests-and-validation.patch
do
  git -C "$DESTINATION" apply --check "$SCRIPT_DIR/../patches/$patch"
  git -C "$DESTINATION" apply "$SCRIPT_DIR/../patches/$patch"
done
for file in \
  scripts/build/make_offline_eval_image.py \
  scripts/test/run_offline_smoke.sh \
  scripts/test/run_offline_representative_suite.sh \
  scripts/test/run_offline_repeated_benchmark.sh
do
  [[ ! -e "$DESTINATION/$file" ]] || { echo "Unexpected existing $file" >&2; exit 1; }
  mkdir -p "$DESTINATION/$(dirname "$file")"
  cp "$SCRIPT_DIR/../overlay-files/$file" "$DESTINATION/$file"
done

# The upstream Git commit used for reproducibility predates the now-approved
# first-party MIT notice. Include the companion release's authoritative
# LICENSE in the reconstructed working tree without modifying the upstream Git
# revision or existing patch hashes. Third-party materials retain their licenses.
if [[ -e "$DESTINATION/LICENSE" ]]; then
  cmp -s "$SCRIPT_DIR/../LICENSE" "$DESTINATION/LICENSE" || {
    echo "Conflicting upstream LICENSE; review license scope" >&2
    exit 1
  }
else
  cp "$SCRIPT_DIR/../LICENSE" "$DESTINATION/LICENSE"
fi
cmp -s "$SCRIPT_DIR/../LICENSE" "$DESTINATION/LICENSE"

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
echo "Overlay: three patches and four pinned standalone files"
echo "Destination: $DESTINATION"
