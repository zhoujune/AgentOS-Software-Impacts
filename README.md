# AgentOS — Software Impacts companion

**Working journal title:** *AgentOS: A Compact, Auditable Execution and Evaluation Testbed for LLM Agents*.

AgentOS executes typed filesystem, SQLite, and network requests behind a Verified Toolchain Reference Monitor (VTRM). A separate host-side World Effect Judge (WEJ) checks observed state changes rather than relying on the agent's textual claim of success.

This repository is a **review-stage software-publication candidate, not a tagged release**. Its source is reconstructed from a pinned upstream commit and seven integrity-checked companion components.

## Prior research

Jun Zhou and Tao Jia, *Introducing Safe LLM-Agent Execution via Typed Tool Mediation and World-Effect Evaluation*, ASE 2026, DOI [10.1145/3832783.3834637](https://doi.org/10.1145/3832783.3834637). Existing source: [zhoujune/AgentOS](https://github.com/zhoujune/AgentOS); prior archive: [10.5281/zenodo.20046861](https://doi.org/10.5281/zenodo.20046861).

The ASE paper's 24 benign and 48 adversarial live-model tasks are **prior results**, not new journal experiments. Its TLA+ model is an abstract check, not an end-to-end correctness proof.

## One-checkout release-candidate reproduction

**Version candidate:** `0.1.0-rc.1` (branch label only, not a tag). **License clearance and immutable archive pending**. See [release candidate instructions](docs/RELEASE_CANDIDATE.md) before reusing or redistributing the source.

On Ubuntu 24.04 x86_64, install Python 3, Git, QEMU x86_64, and e2fsprogs. From a fresh directory:

~~~bash
git clone -b release-candidate/v0.1.0-rc1 \
  https://github.com/zhoujune/AgentOS-Software-Impacts.git agentos-rc
cd agentos-rc
python3 scripts/verify_split_sources.py

# Output destination must not already exist.
bash scripts/run_public_reproduction.sh "$PWD/../agentos-rc-reproduction"
~~~

This single script reconstructs the pinned upstream source, runs the six-task offline suite, and checks both a real world effect and a deliberately false completion claim. It generates a machine-readable `reproduction_summary.json`. The input responses are **hand-authored fixtures**, not live model outputs, and the script does **not** demonstrate independent human reproduction.

The script checks both Git object and SHA-256 integrity for **three complete source patches and four separately published builder/test files**, clones upstream AgentOS commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`, and runs unit tests. The QEMU scripts construct a disposable image without modifying the original rootfs and disable guest networking. No model API key is required for these hand-authored deterministic replay fixtures.

## Verified evidence

A [fresh Ubuntu 24.04 GitHub Actions run](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41271397622) passed **17/17 unit tests**, **1/1 QEMU smoke**, **6/6 representative replay tasks**, and **2/2 expected new-task outcomes**.

In the new task, a real authorized `fs.write` produced the required file (completion PASS); the control trace falsely claimed success but made no change (completion FAIL, intentionally). Safety and exact replay passed in both traces. [Validation summary](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/work/world-effect-reuse-demo/examples/world-effect-reuse/results/20261101-ci-summary.json).

See `docs/CLEAN_HOST_VALIDATION_20261101.md`, `patches/README.md`, and `examples/world-effect-reuse/README.md`.

## Reusable research components

The candidate includes the [World Effect Judge extensibility example](examples/world-effect-reuse/README.md), the [24-task WEJBench v0.1](benchmarks/wejbench/v0.1/README.md), and the [CPU-only constrained-memory study](benchmarks/resource-footprint/README.md). The resource study found 90/90 selected deterministic-replay task outcomes passed across guest-memory caps from 128 to 512 MiB. The 216-episode local-model data are a **distinct study** and do not imply the LLM itself runs on a 128 MiB device.

The independent-user reproduction instructions are in [docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md](docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md). No non-maintainer trial is completed yet. All images, model weights and private trace data stay outside the public source archive.

## Publication limitations

These results validate a small **synthetic replay regression**, not the original 72-task live-model study, a security proof, or adoption by an independent researcher. The initial oversized patch was replaced by a newly validated split-source revision; it is not claimed byte-identical to the unpublished server patch.

Before publication, complete the explicit source license and copyright notice, Buildroot/dependency locks, independent human reproduction, a versioned tag, and an immutable archive/capsule. Track these in [release issue #2](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/2) and [independent-user issue #6](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/6).
