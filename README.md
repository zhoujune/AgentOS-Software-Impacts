# AgentOS — Software Impacts companion

**Working journal title:** *AgentOS: An Open Testbed for World-Effect Evaluation of LLM Agents*.

AgentOS executes typed filesystem, SQLite, and network requests behind a Verified Toolchain Reference Monitor (VTRM). A separate host-side World Effect Judge (WEJ) checks observed state changes rather than relying on the agent's textual claim of success.

This repository is a **review-stage software-publication candidate, not a tagged release**. Its source is reconstructed from a pinned upstream commit and seven integrity-checked companion components.

## Prior research

Jun Zhou and Tao Jia, *Introducing Safe LLM-Agent Execution via Typed Tool Mediation and World-Effect Evaluation*, ASE 2026, DOI [10.1145/3832783.3834637](https://doi.org/10.1145/3832783.3834637). Existing source: [zhoujune/AgentOS](https://github.com/zhoujune/AgentOS); prior archive: [10.5281/zenodo.20046861](https://doi.org/10.5281/zenodo.20046861).

The ASE paper's 24 benign and 48 adversarial live-model tasks are **prior results**, not new journal experiments. Its TLA+ model is an abstract check, not an end-to-end correctness proof.

## Quick start — fresh Linux checkout

Requires Python 3, Git, QEMU x86_64, `debugfs`, and `e2fsck`.

~~~bash
git clone -b work/controlled-polling-benchmark \
  https://github.com/zhoujune/AgentOS-Software-Impacts.git osp-core
bash osp-core/scripts/reconstruct_agentos_overlay.sh "$PWD/AgentOS-candidate"
bash "$PWD/AgentOS-candidate/scripts/test/run_offline_representative_suite.sh"

git clone -b work/world-effect-reuse-demo \
  https://github.com/zhoujune/AgentOS-Software-Impacts.git osp-demo
bash osp-demo/examples/world-effect-reuse/run_demo.sh \
  "$PWD/AgentOS-candidate" "$PWD/world-effect-results"
~~~

The script checks both Git object and SHA-256 integrity for **three complete source patches and four separately published builder/test files**, clones upstream AgentOS commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`, and runs unit tests. The QEMU scripts construct a disposable image without modifying the original rootfs and disable guest networking. No model API key is required for these hand-authored deterministic replay fixtures.

## Verified evidence

A [fresh Ubuntu 24.04 GitHub Actions run](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41271397622) passed **17/17 unit tests**, **1/1 QEMU smoke**, **6/6 representative replay tasks**, and **2/2 expected new-task outcomes**.

In the new task, a real authorized `fs.write` produced the required file (completion PASS); the control trace falsely claimed success but made no change (completion FAIL, intentionally). Safety and exact replay passed in both traces. [Validation summary](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/work/world-effect-reuse-demo/examples/world-effect-reuse/results/20261101-ci-summary.json).

See `docs/CLEAN_HOST_VALIDATION_20261101.md`, `patches/README.md`, and `examples/world-effect-reuse/README.md`.

## Publication limitations

These results validate a small **synthetic replay regression**, not the original 72-task live-model study, a security proof, or adoption by an independent researcher. The initial oversized patch was replaced by a newly validated split-source revision; it is not claimed byte-identical to the unpublished server patch.

Before publication, complete the explicit source license and copyright notice, Buildroot/dependency locks, independent human reproduction, a versioned tag, and an immutable archive/capsule. Track these in [release issue #2](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/2) and [independent-user issue #6](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/6).
