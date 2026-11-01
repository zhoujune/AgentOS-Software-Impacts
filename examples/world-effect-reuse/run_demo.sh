#!/usr/bin/env bash
# End-to-end researcher reuse demonstration: one new task, two model-output traces.
# Case A performs an allowed file write; case B reports success without an effect.
# Both cassettes are HAND-AUTHORED test fixtures, not real LLM runs.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: bash $0 /path/to/reconstructed-AgentOS [fresh-output-directory]" >&2
  exit 2
fi

AGENTOS="$(cd "$1" && pwd)"
OUT="${2:-$AGENTOS/runtime/world-effect-reuse/$(date +%Y%m%d-%H%M%S)-$$}"
if [[ -e "$OUT" ]]; then
  echo "Output directory already exists; refusing to reuse results: $OUT" >&2
  exit 2
fi
if [[ ! -f "$AGENTOS/judge/run_vtrm_eval.py" ||
      ! -f "$AGENTOS/scripts/build/make_offline_eval_image.py" ]]; then
  echo "This demo requires the AgentOS offline-replay source overlay; see README.md." >&2
  exit 2
fi

IMAGE="$AGENTOS/runtime/offline-eval/rootfs.eval.offline.ext2"
if [[ ! -f "$IMAGE" ]]; then
  echo "[setup] Preparing a disposable evaluation image from the clean rootfs."
  python3 "$AGENTOS/scripts/build/make_offline_eval_image.py" --output "$IMAGE"
fi
mkdir -p "$OUT"
printf 'example=%s\nagentos=%s\nimage=%s\n' "$HERE" "$AGENTOS" "$IMAGE" > "$OUT/inputs.txt"

run_case() {
  local label="$1"
  local cassette="$2"
  local root="$OUT/$label"
  mkdir -p "$root"
  echo "[$(date -Is)] Starting $label"

  # A valid negative control may cause the evaluator to return nonzero.
  # Preserve both its return code and the report; validate actual world state later.
  local status=0
  (
    cd "$AGENTOS"
    python3 judge/run_vtrm_eval.py \
      --tasks-dir "$HERE/task" \
      --task-id 401-world-effect-reuse \
      --replay-file "$HERE/cassettes/$cassette" \
      --no-guest-network \
      --no-vm-console-su-root \
      --clean-rootfs "$IMAGE" \
      --reset-between-cases \
      --reset-strategy copy-image \
      --report-root "$root/reports" \
      --rootfs "$root/rootfs.eval.ext2" \
      --bridge-dir "$root/bridge" \
      --memory-mb 512 \
      --vm-boot-timeout "${VM_BOOT_TIMEOUT:-120}" \
      --task-timeout "${TASK_TIMEOUT:-180}" \
      --proxy-warmup-seconds 1 \
      --post-task-settle-seconds 1 \
      --agent-loop-poll-interval 5 \
      --agent-llm-poll-interval 1 \
      --result-poll-interval 1
  ) > "$root/runner.log" 2>&1 || status=$?
  printf '%s\n' "$status" > "$root/evaluator_exit_code.txt"
  echo "[$(date -Is)] Completed $label (evaluator exit=$status); details: $root"
}

run_case performed-write performed-write.json
run_case unsupported-success unsupported-success.json

python3 "$HERE/validate_results.py" \
  --output-root "$OUT" \
  --example-dir "$HERE"

echo "Results: $OUT/impact_validation.json and $OUT/impact_validation.md"
