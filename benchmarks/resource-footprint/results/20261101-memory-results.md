# AgentOS: CPU-only constrained-memory benchmark (2026-11-01)

**Status:** Completed internal x86_64/QEMU-TCG study; not physical edge deployment.

The design screened 5 memory configurations using a benign write and an audited strict database denial (10/10 passed);
then evaluated 6 deterministic replay tasks × 3 repetitions × 5 guest-memory settings = **90/90 task passes**.
Three tasks validate permitted workspace effects; three validate explicit strict DB denials.
All 15 full-run host evaluator reports had `all_ok=true`, with exact replay, disabled guest networking and passing world integrity.

## Results

| QEMU guest RAM | Full task passes | Mean suite runtime (s) | Peak sampled process-tree PSS (MiB) | Peak sampled QEMU RSS (MiB) |
| ---: | ---: | ---: | ---: | ---: |
| 512 MiB | 18/18 | 157.89 | 407.19 | 386.84 |
| 384 MiB | 18/18 | 158.08 | 405.14 | 384.77 |
| 256 MiB | 18/18 | 157.16 | 403.25 | 382.93 |
| 192 MiB | 18/18 | 158.41 | 401.18 | 380.84 |
| 128 MiB | 18/18 | 158.09 | 401.15 | 380.86 |

## Interpretation

The boot log at 128 MiB reports **105.3 MiB available** to the Linux guest kernel after reservations.
Task completion and policy enforcement under a 128 MiB **configured guest-memory limit**
provide evidence of resource-constrained guest feasibility for these six selected tasks.
The recorded sampled host process-tree PSS remains near 400 MiB even at 128 MiB guest RAM;
therefore the entire QEMU-based host/runtime cannot be claimed to fit in 128 MiB.
QEMU ran with **TCG software emulation** because the host did not expose `/dev/kvm`.
These host-memory measurements mix emulation, agent and evaluation costs.
Mean runtimes varied by less than three seconds across configurations, but no statistical speedup or minimum-memory threshold is established.

## Reproducibility

The checked input and case fingerprints are recorded in [full JSON](20261101-memory-full.json).
Case-level metadata and per-run RSS/PSS and timing records are in the accompanying CSV files.
The original host traces, QEMU guest images and filesystem snapshots remain on the private research host.
Use the open-source benchmark runner to reproduce locally; source files are not modified.

## Limits

- CPU-only deterministic replay is not evidence of live-LLM inference under constrained guest RAM.
- No actual edge board, ARM64 port, or power/energy evaluation has been conducted.
- The 128 MiB setting is an upper tested viable configuration boundary; smaller settings were not tested.
- Host-process peak PSS is sampled at ~0.5 s, not an instantaneous system-wide physical memory peak.
- This is a narrow descriptive functional experiment, not an apples-to-apples comparison with Firecracker, containers, or Wasm runtimes.
