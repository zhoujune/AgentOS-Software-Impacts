#!/usr/bin/env bash
# Launch exactly two genuinely live (not replayed) AgentOS tasks against one
# already running loopback LLM server. No server is started or credentials copied.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

if [[ "$#" -ne 4 ]]; then
  echo "Usage: bash $0 /path/to/reconstructed-AgentOS /path/to/prepared-24-tasks /new/output/dir {llama3-8b|qwen3-14b|mistral7b-v03}" >&2
  exit 2
fi
AGENTOS="$(realpath "$1")"
PREPARED="$(realpath "$2")"
OUTPUT="$3"
PROFILE="$4"
case "$PROFILE" in
  llama3-8b|qwen3-14b|mistral7b-v03) ;;
  *) echo "Unknown profile: $PROFILE" >&2; exit 2 ;;
esac
[[ ! -e "$OUTPUT" ]] || { echo "Refusing to overwrite output: $OUTPUT" >&2; exit 2; }
[[ -f "$AGENTOS/judge/run_vtrm_eval.py" ]] || { echo "Reconstructed AgentOS missing" >&2; exit 2; }
[[ -f "$PREPARED/prepared.json" ]] || { echo "Prepared 24-task corpus missing" >&2; exit 2; }

"$PYTHON" "$SCRIPT_DIR/prepare_local_checkout.py" --agentos-root "$AGENTOS" --apply
"$PYTHON" "$SCRIPT_DIR/run_live.py" --execute   --agentos-root "$AGENTOS"   --prepared-root "$PREPARED"   --output "$OUTPUT"   --models "$PROFILE"   --task-id 401-wejbench-benign   --task-id 404-wejbench-direct-denial   --repetitions 1   --task-timeout "${AGENTOS_LIVE_TASK_TIMEOUT:-240}"   --boot-timeout "${AGENTOS_LIVE_BOOT_TIMEOUT:-120}"
echo "Only count the two episodes as live when episodes.json contains model_api_call_count > 0 and local_preflight.json reports a successful local generation."
