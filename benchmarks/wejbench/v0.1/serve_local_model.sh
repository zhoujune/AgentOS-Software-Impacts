#!/usr/bin/env bash
# Serve one already downloaded local Hugging Face model in the foreground.
# Uses the installed vLLM build/device allocation; no model is downloaded.
set -euo pipefail
if [[ "$#" -ne 3 ]]; then
  echo "Usage: bash $0 /path/to/local-model served-model-id port" >&2
  echo "Example: bash $0 /models/Llama3-8B-Instruct llama3-8b-local 8017" >&2
  exit 2
fi
MODEL_DIR="$1"
SERVED_ID="$2"
PORT="$3"
[[ -f "$MODEL_DIR/config.json" ]] || { echo "Local model config missing: $MODEL_DIR/config.json" >&2; exit 1; }
[[ "$SERVED_ID" =~ ^[A-Za-z0-9._/-]+$ ]] || { echo "Invalid served model ID" >&2; exit 2; }
[[ "$PORT" =~ ^[0-9]{2,5}$ ]] || { echo "Invalid port" >&2; exit 2; }
command -v vllm >/dev/null || { echo "Installed PPU-compatible vllm binary not available" >&2; exit 1; }
echo "Starting loopback-only vLLM service: $SERVED_ID at http://127.0.0.1:$PORT/v1/chat/completions"
echo "Using current accelerator allocation; stop foreground service with Ctrl-C."
exec vllm serve "$MODEL_DIR" --served-model-name "$SERVED_ID" --host 127.0.0.1   --port "$PORT" --max-model-len "${VLLM_MAX_MODEL_LEN:-4096}"
