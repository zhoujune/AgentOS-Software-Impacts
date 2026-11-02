#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="${PYTHON:-python3}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$ROOT_DIR/runtime/offline-representative}"
CASSETTE="$ROOT_DIR/judge/replays/representative-offline.json"
CLEAN_ROOTFS="${CLEAN_ROOTFS:-$ROOT_DIR/runtime/offline-eval/rootfs.eval.offline.ext2}"

if [[ ! -f "$CLEAN_ROOTFS" ]]; then
  "$PYTHON" "$ROOT_DIR/scripts/build/make_offline_eval_image.py" --output "$CLEAN_ROOTFS"
fi
mkdir -p "$OUTPUT_ROOT"
export CLEAN_ROOTFS
export LLM_PROXY_POLL_INTERVAL="${LLM_PROXY_POLL_INTERVAL:-2}"

common_args=(
  --replay-file "$CASSETTE"
  --no-guest-network --no-vm-console-su-root
  --clean-rootfs "$CLEAN_ROOTFS"
  --reset-between-cases --reset-strategy copy-image
  --memory-mb "${MEMORY_MB:-512}"
  --vm-boot-timeout "${VM_BOOT_TIMEOUT:-60}"
  --task-timeout "${TASK_TIMEOUT:-90}"
  --proxy-warmup-seconds "${PROXY_WARMUP_SECONDS:-1}"
  --post-task-settle-seconds "${POST_TASK_SETTLE_SECONDS:-1}"
  --agent-loop-poll-interval "${AGENT_LOOP_POLL_INTERVAL:-5}"
  --agent-llm-poll-interval "${AGENT_LLM_POLL_INTERVAL:-1}"
  --agent-loop-script "${AGENT_LOOP_SCRIPT:-/home/agent/agent_main_loop.sh}"
  --result-poll-interval "${RESULT_POLL_INTERVAL:-1}"
)

"$PYTHON" "$ROOT_DIR/judge/run_vtrm_eval.py" \
  --tasks-dir "$ROOT_DIR/judge/tasks_should_pass" \
  --task-id 301-workspace-hello \
  --task-id 302-workspace-json \
  --task-id 321-delete-workspace-file \
  --report-root "$OUTPUT_ROOT/reports/benign" \
  --rootfs "$OUTPUT_ROOT/rootfs.benign.ext2" \
  --bridge-dir "$OUTPUT_ROOT/bridge-benign" \
  "${common_args[@]}"

"$PYTHON" "$ROOT_DIR/judge/run_vtrm_eval.py" \
  --tasks-dir "$ROOT_DIR/judge/tasks_should_fail/direct" \
  --task-id 115-direct-db-task-disable-update \
  --task-id 118-direct-db-audit-insert \
  --task-id 122-direct-readonly-db-delete \
  --report-root "$OUTPUT_ROOT/reports/denials" \
  --rootfs "$OUTPUT_ROOT/rootfs.denials.ext2" \
  --bridge-dir "$OUTPUT_ROOT/bridge-denials" \
  "${common_args[@]}"

"$PYTHON" "$ROOT_DIR/judge/validate_offline_suite.py" \
  --output-root "$OUTPUT_ROOT" \
  --cassette "$CASSETTE"
