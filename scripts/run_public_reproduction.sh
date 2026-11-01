#!/usr/bin/env bash
# RC reproduction helper: reconstruct pinned AgentOS and exercise world effects.
# AUTOMATED clean-check, not independent human replication.
set -euo pipefail
ROOT="$(cd "$(dirname "\${BASH_SOURCE[0]}")/.." && pwd)"
if [[ $# -ne 1 ]]; then
  echo "Usage: bash $0 /path/to/new-output-directory" >&2
  exit 2
fi
OUTPUT="$1"
if [[ -e "$OUTPUT" ]]; then
  echo "Refusing to overwrite existing output: $OUTPUT" >&2
  exit 2
fi
mkdir -p "$OUTPUT"
OUTPUT="$(cd "$OUTPUT" && pwd)"
echo "[$(date -u +%FT%TZ)] Candidate reproduction: $OUTPUT"
python3 "$ROOT/scripts/verify_split_sources.py"
{
  echo "started_at_utc=$(date -u +%FT%TZ)"
  echo "candidate_commit=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo archive-without-git)"
  echo "python=$(python3 --version 2>&1)"
  echo "qemu=$(qemu-system-x86_64 --version | head -n 1)"
  echo "e2fsck=$(e2fsck -V 2>&1 | head -n 1)"
  echo "architecture=$(uname -m)"
  echo "kernel=$(uname -r)"
  if [[ -r /dev/kvm ]]; then echo "kvm=available"; else echo "kvm=unavailable"; fi
  echo "model_inference=disabled"
} > "$OUTPUT/environment.txt"
echo "[$(date -u +%FT%TZ)] Reconstruct pinned upstream and verified overlays"
bash "$ROOT/scripts/reconstruct_agentos_overlay.sh" "$OUTPUT/AgentOS"
echo "[$(date -u +%FT%TZ)] Run six offline replay tasks"
(
  cd "$OUTPUT/AgentOS"
  OUTPUT_ROOT="$OUTPUT/baseline-six" VM_BOOT_TIMEOUT=120 TASK_TIMEOUT=180 \
    bash scripts/test/run_offline_representative_suite.sh
)
echo "[$(date -u +%FT%TZ)] Run world-effect positive and false-success controls"
VM_BOOT_TIMEOUT=120 TASK_TIMEOUT=180 \
  bash "$ROOT/examples/world-effect-reuse/run_demo.sh" \
    "$OUTPUT/AgentOS" "$OUTPUT/world-effect-demo"
python3 - "$OUTPUT" <<'PY'
import hashlib,json,pathlib,sys,datetime
p=pathlib.Path(sys.argv[1])
base=json.loads((p/"baseline-six/offline_benchmark.json").read_text())
demo=json.loads((p/"world-effect-demo/impact_validation.json").read_text())
assert base["representative_task_count"]==6 and base["all_ok"] is True and not base["errors"]
assert demo["validation"]=="PASS" and not demo["errors"]
assert len(demo["cases"])==2 and demo["cases"][0]["task_completion_ok"] is True
assert demo["cases"][1]["task_completion_ok"] is False
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
summary={
 "scope":"automated public-source reproduction, NOT independent-user validation",
 "completed_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "baseline_six_task_validator":"PASS","world_effect_reuse_validator":"PASS",
 "positive_trace_completion":True,"false_success_negative_control_completion":False,
 "model_api_calls":0,
 "source_version_fingerprint_sha256":sha(p/"AgentOS/manifests/manifest.lock"),
 "baseline_validator_sha256":sha(p/"baseline-six/offline_benchmark.json"),
 "demo_validator_sha256":sha(p/"world-effect-demo/impact_validation.json"),
 "environment_details":"see environment.txt; raw model/task transcripts not included"
}
(p/"reproduction_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
PY
echo "[$(date -u +%FT%TZ)] REPRODUCTION_HELPER_PASS"
echo "Summary: $OUTPUT/reproduction_summary.json"
