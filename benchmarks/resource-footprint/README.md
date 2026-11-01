# AgentOS constrained-memory and host-footprint study

**Experimental software artifact — CPU-only deterministic replay, not physical edge hardware.**

This study tests the systems hypothesis that the compact agent-specialized guest can execute legitimate typed tool effects and reliably mediate restricted operations under smaller *configured guest RAM allocations*. It does **not** benchmark local LLM inference, ARM64 hardware, energy, minimum embedded-system memory, or end-to-end production deployment.

## Protocol

The input is one reconstructed AgentOS source tree built from the pinned public source/overlay; its prepared evaluation rootfs and kernel are treated as immutable. The fixed **five** QEMU guest-RAM configurations are 512, 384, 256, 192 and 128 MiB.

1. **Screen:** for every RAM configuration, independently run `301-workspace-hello` (required authorized `fs.write`) and `115-direct-db-task-disable-update` (an attempted `db.update` with explicit deny/no-effect audit). Each test uses exact CPU-only replay, a fresh disposable guest rootfs and disabled guest networking. A configuration is viable only if **both** cases pass.
2. **Full matrix:** run the existing six-case representative suite three times at each viable configuration. The suite contains three legitimate workspace actions and three direct database denial cases. The memory order is deterministically shuffled within each repetition using a fixed seed to reduce monotonic host drift. Every failure and timeout is retained.
3. **Resource collection:** sample process-descendant PSS and RSS (including the evaluator, QEMU and local replay proxy) approximately every 0.5 seconds from `/proc`; capture a separate QEMU process RSS/PSS peak, sampled CPU seconds, elapsed time and case-level timings. Host process-tree peak PSS is an approximate **host-side memory figure**, not measured guest working set or total device RAM.

Input hashes (kernel, canonical rootfs, prepared rootfs, replay cassette) and runtime settings are saved in `input_provenance.json` and rechecked after every stage. No canonical image or original replay report is overwritten. Model API tokens are removed from the test harness's subprocess environment. The screening and full-study output directories must be new; the runner refuses to overwrite a previous run.

## Prerequisites and commands

Linux x86_64 host with Python 3.10+, QEMU, `ps`, `debugfs`, `e2fsck` and enough filesystem space for separate disposable rootfs copies. Build or obtain a verified AgentOS checkout with the existing CPU-only replay harness and prepared guest image at `runtime/offline-eval/rootfs.eval.offline.ext2`.

From the **journal repository** checkout:

```bash
export AGENTOS_ROOT=/path/to/reconstructed-AgentOS
export AGENTOS_MEMORY_STUDY_ROOT=/path/to/new/resource-results

python3 -m unittest benchmarks/resource-footprint/test_memory_sweep.py -v
python3 benchmarks/resource-footprint/run_memory_sweep.py --mode screen

# Inspect screen_summary.json; do not substitute an unverified success claim.
python3 benchmarks/resource-footprint/run_memory_sweep.py --mode full
python3 benchmarks/resource-footprint/run_memory_sweep.py --mode summary

# Independently validate and sanitize the completed study:
python3 benchmarks/resource-footprint/publish_results.py \
  --study "$AGENTOS_MEMORY_STUDY_ROOT" \
  --source "$AGENTOS_ROOT" \
  --out /path/to/new/sanitized-results
```

Use no parallel QEMU evaluators. The runner checks for overlapping QEMU instances and refuses to run in their presence. It refuses the full matrix if the 512 MiB baseline fails, or if no lower-memory configuration passes screening. A failed low-memory screen remains an informative boundary observation and is *not* promoted to a successful full-suite result.

## Evaluation criteria

A screen PASS requires the evaluator to exit successfully, exact replay, no unexpected world mutation and the task-specific oracle. The denial case additionally requires an actual guest VTRM audit event with `decision=deny`, `effect=none` for the expected database mutation. `approval_required` and a missing attack are **not** counted as strict denials.

A full six-case suite PASS requires the existing `validate_offline_suite.py` script to succeed. This verifies all benign effects, all three VTRM denials, exact cassette matches, no guest networking and host-world integrity.

## Completed results (November 1, 2026)

All **10/10 two-case screening checks** passed. All **15/15 repeated six-task suites** (90/90 task cases, comprising 45 benign task-completion checks and 45 explicit database-policy denials) passed the existing host-side judge. Repetitions were interleaved by memory setting. Full data are available in:

- [Human-readable results](results/20261101-memory-results.md)
- [Machine-readable aggregate, 15 runs and 90 case metadata rows](results/20261101-memory-full.json)
- [Per-run resource measurements](results/20261101-memory-runs.csv)
- [Task-level case metadata](results/20261101-memory-cases.csv)
- [Initial 10-case screen](results/20261101-memory-screen.json)
- [Separate QEMU TCG-cache attribution probe](results/20261101-tcg-cache-probe.json)

| Guest allocation | Repeated task passes | Mean full-suite runtime | Maximum sampled process-tree PSS |
| ---: | ---: | ---: | ---: |
| 512 MiB | 18/18 | 157.89 s | 407.19 MiB |
| 384 MiB | 18/18 | 158.08 s | 405.14 MiB |
| 256 MiB | 18/18 | 157.16 s | 403.25 MiB |
| 192 MiB | 18/18 | 158.41 s | 401.18 MiB |
| **128 MiB** | **18/18** | **158.09 s** | **401.15 MiB** |

The 128 MiB guest Linux boot log independently reports **105.3 MiB available** to its kernel after reservations. This establishes *viability at a configured RAM cap* for the selected replay tasks, not total-device memory use or the minimum viable RAM level. No lower cap was attempted.

### Why the host PSS remains near 400 MiB

The measured host has no `/dev/kvm`; the evaluation therefore runs under QEMU's **TCG software emulation**. A separate mapping diagnostic captured a large anonymous executable mapping at the default TCG configuration: approximately 1 GiB virtual size, 226 MiB resident PSS, for either 128 or 512 MiB configured guest RAM.

To test attribution rather than speculate, we ran the **same single benign task** under `-accel tcg,tb-size=32`, without changing the guest RAM limit, kernel, or task. The 128 MiB QEMU process peak sampled PSS changed from **367.15 MiB** (default TCG) to **144.46 MiB** (32 MiB TCG translation cache). At 512 MiB, the corresponding comparison was **381.09 MiB** to **154.57 MiB**. Both variants passed the same one-task host-world checks.

QEMU documents `tb-size` as controlling the TCG translation-block cache ([QEMU invocation documentation](https://www.qemu.org/docs/master/system/qemu-manpage.html)). This supports attribution of much of the original host footprint to emulator configuration, rather than to the agent alone. The cache probe is **one task per condition**, not a repeated six-task or physical edge measurement, and has its own separate dataset.

Neither the guest cap nor the optimized QEMU process PSS is a demonstrated total-edge-device memory requirement. The public manuscript retains the untuned baseline as its primary reported run.

## Measurement and publication caveats

- The 60 MiB rootfs file and ~6 MB kernel are static artifacts, not guest resident memory.
- Configured guest RAM is an allocation limit. It does not by itself establish peak or minimum guest working-set usage.
- Sampled host process-tree peak PSS is affected by sampling interval, virtualization and shared mappings. RSS sums can double-count shared memory. Host OS, unrelated services, model servers, page cache, and device overhead are **not** included.
- QEMU x86_64 emulation with constrained RAM is not a physical ARM64/embedded test. No battery or power claim is supported.
- Workloads are six exact deterministic replay tasks, not the original ASE 72-task live benchmark or the WEJ-Bench 216 live-model study.
- Results are descriptive. Small repeated samples do not justify statistical significance or population-level hardware claims.
- Any conventional Linux comparison should use the **same functional workload and measured process boundary**; a container comparison cannot be represented as isolation-equivalent without a separate threat-model analysis.

The legitimate question is whether AgentOS continues to deliver correct tool effects and strict audited denials at lower memory allocations. A secondary observation is the amount of host-process memory and boot latency required in the QEMU test configuration. Both success and failure are publishable evidence, provided they are reported accurately.
