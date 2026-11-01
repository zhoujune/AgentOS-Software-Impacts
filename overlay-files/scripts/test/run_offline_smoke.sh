#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="${PYTHON:-python3}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$ROOT_DIR/runtime/offline-smoke}"
CLEAN_ROOTFS="${CLEAN_ROOTFS:-$ROOT_DIR/runtime/offline-eval/rootfs.eval.offline.ext2}"

if [[ ! -f "$CLEAN_ROOTFS" ]]; then
  "$PYTHON" "$ROOT_DIR/scripts/build/make_offline_eval_image.py" --output "$CLEAN_ROOTFS"
fi
mkdir -p "$OUTPUT_ROOT"
exec "$PYTHON" "$ROOT_DIR/judge/run_vtrm_eval.py" \
  --tasks-dir "$ROOT_DIR/judge/tasks_should_pass" \
  --task-id 301-workspace-hello \
  --replay-file "$ROOT_DIR/judge/replays/offline-smoke.json" \
  --no-guest-network --no-vm-console-su-root \
  --report-root "$OUTPUT_ROOT/reports" \
  --rootfs "$OUTPUT_ROOT/rootfs.eval.ext2" \
  --clean-rootfs "$CLEAN_ROOTFS" \
  --bridge-dir "$OUTPUT_ROOT/agent_bridge" \
  --reset-between-cases --reset-strategy copy-image \
  --memory-mb "${MEMORY_MB:-512}" \
  --vm-boot-timeout "${VM_BOOT_TIMEOUT:-60}" \
  --task-timeout "${TASK_TIMEOUT:-90}" \
  --proxy-warmup-seconds "${PROXY_WARMUP_SECONDS:-1}" \
  --post-task-settle-seconds "${POST_TASK_SETTLE_SECONDS:-1}"
