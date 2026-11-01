#!/usr/bin/env bash
# Reproduce AgentOS from a fresh public checkout. CPU-only, no LLM API.
# For a real independent study, a non-maintainer must run this unaided.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/reproduce_release_candidate.sh /new/empty/output-dir" >&2
  exit 2
fi
OUT="$1"
if [[ -e "$OUT" ]]; then
  echo "Refusing to overwrite output: $OUT" >&2
  exit 2
fi
for tool in git python3 qemu-system-x86_64 debugfs e2fsck sha256sum; do
  command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool" >&2; exit 2; }
done
mkdir -p "$OUT"
printf '%s\n' "Release candidate is NOT legally cleared or an independent-user success."
python3 "$ROOT/scripts/verify_split_sources.py"
echo "Reconstructing pinned upstream + seven verified overlay inputs"
bash "$ROOT/scripts/reconstruct_agentos_overlay.sh" "$OUT/AgentOS" > "$OUT/reconstruction.log" 2>&1 || {
  echo "Reconstruction failed: $OUT/reconstruction.log" >&2
  exit 1
}
echo "Running offline six-task suite (3 permitted actions and 3 policy denials)"
(
  cd "$OUT/AgentOS"
  OUTPUT_ROOT="$OUT/baseline" VM_BOOT_TIMEOUT=120 TASK_TIMEOUT=180 \
    bash scripts/test/run_offline_representative_suite.sh
) > "$OUT/baseline.log" 2>&1 || {
  echo "Baseline failed: $OUT/baseline.log" >&2
  exit 1
}
echo "Running two-trace new-task demonstration (positive and false-success control)"
VM_BOOT_TIMEOUT=120 TASK_TIMEOUT=180 \
  bash "$ROOT/examples/world-effect-reuse/run_demo.sh" \
    "$OUT/AgentOS" "$OUT/new-task" > "$OUT/new-task.log" 2>&1 || {
  echo "World-effect demo failed: $OUT/new-task.log" >&2
  exit 1
}
python3 "$ROOT/scripts/validate_release_candidate.py" \
  --baseline "$OUT/baseline/offline_benchmark.json" \
  --demo "$OUT/new-task/impact_validation.json" \
  --output "$OUT/reproduction_summary.json"
echo "Reproduction finished; share only the sanitized $OUT/reproduction_summary.json"
echo "Private raw logs and guest images are not suitable for automatic upload."
