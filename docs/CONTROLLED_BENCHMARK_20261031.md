# Controlled offline polling benchmark (2026-10-31)

## Question

Does replacing legacy guest polling with 0.2-second inbox and LLM-response polling reduce **observed task-enqueue/wait time**, with bridge and workspace permissions already fixed?

This is a *performance ablation*, **not** a security efficacy study or a test of real model inference.

## Profiles and controls

| Variable | A: permissions-fixed legacy | B: guest 0.2 s |
| --- | --- | --- |
| Guest image | `smoke-perms/rootfs.profile2.ext2` | `20261029-software-impacts-prep/rootfs.poll020.ext2` |
| Agent inbox poll | 5.0 s | 0.2 s |
| Guest LLM-response poll | 1.0 s | 0.2 s |
| Host proxy poll | 2.0 s | 2.0 s |
| Evaluator result poll | 1.0 s | 1.0 s |
| QEMU memory | 512 MiB | 512 MiB |
| VM boot timeout | 60 s | 60 s |
| Per-task timeout | 90 s | 90 s |
| Replay cassette | `judge/replays/representative-offline.json` | same |
| LLM calls | Exact deterministic replay only | same |
| Guest NIC | Disabled | Disabled |
| Repetitions | 3 full six-task rounds | 3 full six-task rounds |

The selected cassette SHA-256 is `ca11bf6e0ce71ab28e55803a47dec7b0d48ea8cf015134517f6c489e9d033ede`; it holds **13 request-ID responses for six tasks**. The original ASE task collection contains 24 benign and 48 adversarial tasks, which this small performance study does not reproduce.

Image SHA-256:
- Canonical clean image (reference, unchanged): `d61a40dc7f2090b19505886020593674cdf2b5dd2f85fbcb9c02c523745a5f61`
- Optimized B candidate: `d6bd8f99b6b897eca5b84da2dcc52b82aeb3d0d2d790cf226fc04bc2cf2bbc0f`
- Legacy A: recorded by its per-profile `study_environment.json`.

## Representative tasks and acceptance criteria

Benign: `301-workspace-hello`, `302-workspace-json`, `321-delete-workspace-file`.

Security denials: `115-direct-db-task-disable-update`, `118-direct-db-audit-insert`, `122-direct-readonly-db-delete`.

For each task, require the expected host-observed world effect or verified VTRM denial, exact matched replay requests, valid world-integrity checks, and no guest network interface. No elapsed-time comparison counts as a success if correctness fails.

## Commands (from the *local experimental source tree*)

```bash
cd /workspace/agentos-journal/repo/AgentOS-main
ROOT="$PWD/runtime/offline-repeated/20261031-osp-controlled-ab"
COMMON='RESULT_POLL_INTERVAL=1 LLM_PROXY_POLL_INTERVAL=2'
# Execute one profile at a time; do not parallelize VM runs.
REPETITIONS=3 STUDY_ROOT="$ROOT/profile-A-legacy" \
  CLEAN_ROOTFS="$PWD/runtime/offline-repeated/smoke-perms/rootfs.profile2.ext2" \
  AGENT_LOOP_POLL_INTERVAL=5 AGENT_LLM_POLL_INTERVAL=1 \
  RESULT_POLL_INTERVAL=1 LLM_PROXY_POLL_INTERVAL=2 \
  bash scripts/test/run_offline_repeated_benchmark.sh

REPETITIONS=3 STUDY_ROOT="$ROOT/profile-B-guest020" \
  CLEAN_ROOTFS="$PWD/runtime/offline-repeated/20261029-software-impacts-prep/rootfs.poll020.ext2" \
  AGENT_LOOP_POLL_INTERVAL=0.2 AGENT_LLM_POLL_INTERVAL=0.2 \
  RESULT_POLL_INTERVAL=1 LLM_PROXY_POLL_INTERVAL=2 \
  bash scripts/test/run_offline_repeated_benchmark.sh
```

The actual server launch script is `runtime/offline-repeated/20261031-osp-controlled-ab/run_profiles.sh`. It runs **all three A repetitions before all three B repetitions**. This order is not randomized or paired by iteration, so background-load and temporal drift are limitations; repeat using interleaving if seeking strong causal inference.

## Reporting rules

Report each profile's per-case timing distribution, sample count, median, p95, and boot-to-ready and case-runtime measurements, with individual run results and error counts. Distinguish `task_enqueue_and_wait_seconds` from full case latency (including VM boot and image reset). Avoid inferring model inference speed, broad-suite security, or generalized multi-hardware reproducibility. Record exact source snapshot and host load; one image comparison cannot isolate effects of unrelated source changes without source-level equivalence verification.

Preserve raw outputs and their hashes. Keep guest `.ext2` disks out of the Git repository; publish redistributable binaries through a release/archive with explicit provenance instead.

## Work still required

1. Confirm *all* 36 expected case results pass before computing a comparative estimate.
2. Hash and version the actual source tree. The server's experiment tree does not contain `.git` metadata.
3. Repeat with interleaved run ordering or fresh randomized blocks and controlled CPU contention if the observed effect is small.
4. Add a live-LLM/full-suite regression separately when suitable replay cassettes or model access are available.
