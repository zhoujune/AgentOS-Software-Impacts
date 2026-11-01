#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="${PYTHON:-python3}"
REPETITIONS="${REPETITIONS:-3}"
STUDY_ROOT="${STUDY_ROOT:-$ROOT_DIR/runtime/offline-repeated/$(date +%Y%m%d-%H%M%S)}"
CLEAN_ROOTFS="${CLEAN_ROOTFS:-$ROOT_DIR/runtime/offline-eval/rootfs.eval.offline.ext2}"

[[ "$REPETITIONS" =~ ^[1-9][0-9]*$ ]] || { echo "Invalid REPETITIONS" >&2; exit 2; }
if [[ ! -f "$CLEAN_ROOTFS" ]]; then
  "$PYTHON" "$ROOT_DIR/scripts/build/make_offline_eval_image.py" --output "$CLEAN_ROOTFS"
fi
export CLEAN_ROOTFS
mkdir -p "$STUDY_ROOT"
printf 'study_root=%s\nrepetitions=%s\n' "$STUDY_ROOT" "$REPETITIONS" > "$STUDY_ROOT/study_manifest.txt"

"$PYTHON" - "$ROOT_DIR" "$STUDY_ROOT" "$REPETITIONS" <<'PYENV'
import hashlib,json,os,platform,subprocess,sys
from datetime import datetime
from pathlib import Path
repo,study,reps = Path(sys.argv[1]),Path(sys.argv[2]),int(sys.argv[3])
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
try: qemu=subprocess.check_output(['qemu-system-x86_64','--version'],text=True).splitlines()[0]
except Exception: qemu='unavailable'
data={
 'created_at':datetime.now().astimezone().isoformat(),
 'repetitions_requested':reps,'platform':platform.platform(),'kernel':platform.release(),
 'machine':platform.machine(),'logical_cpu_count':os.cpu_count(),'cpu_model':'not recorded',
 'python_version':platform.python_version(),'qemu_version':qemu,
 'memory_mb':int(os.getenv('MEMORY_MB','512')),'vm_boot_timeout_seconds':int(os.getenv('VM_BOOT_TIMEOUT','60')),
 'task_timeout_seconds':int(os.getenv('TASK_TIMEOUT','90')),'reset_strategy':'copy-image',
 'agent_loop_script':os.getenv('AGENT_LOOP_SCRIPT','/home/agent/agent_main_loop.sh'),
 'agent_loop_poll_interval_seconds':float(os.getenv('AGENT_LOOP_POLL_INTERVAL','5')),
 'agent_llm_poll_interval_seconds':float(os.getenv('AGENT_LLM_POLL_INTERVAL','1')),
 'result_poll_interval_seconds':float(os.getenv('RESULT_POLL_INTERVAL','1')),
 'llm_proxy_poll_interval_seconds':float(os.getenv('LLM_PROXY_POLL_INTERVAL','2')),
 'kernel_sha256':sha(repo/'artifacts/images/bzImage'),
 'clean_rootfs_path':str(Path(os.environ['CLEAN_ROOTFS']).resolve()),
 'clean_rootfs_sha256':sha(Path(os.environ['CLEAN_ROOTFS'])),
 'cassette_sha256':sha(repo/'judge/replays/representative-offline.json'),
}
(study/'study_environment.json').write_text(json.dumps(data,indent=2)+'\n')
PYENV

failures=0
for ((i=1; i<=REPETITIONS; i++)); do
  printf -v run_name 'run-%02d' "$i"
  run_root="$STUDY_ROOT/$run_name"
  mkdir -p "$run_root"
  if OUTPUT_ROOT="$run_root" PYTHON="$PYTHON" \
     bash "$ROOT_DIR/scripts/test/run_offline_representative_suite.sh" > "$run_root/run.log" 2>&1; then
    echo "[$(date -Is)] PASS $run_name" | tee -a "$STUDY_ROOT/study.log"
  else
    failures=$((failures + 1))
    echo "[$(date -Is)] FAIL $run_name" | tee -a "$STUDY_ROOT/study.log"
  fi
done
"$PYTHON" "$ROOT_DIR/judge/aggregate_repeated_benchmark.py" \
  --study-root "$STUDY_ROOT" --expected-repetitions "$REPETITIONS"
mkdir -p "$ROOT_DIR/runtime/offline-repeated"
printf '%s\n' "$STUDY_ROOT" > "$ROOT_DIR/runtime/offline-repeated/latest_run.txt"
if (( failures > 0 )); then exit 1; fi
