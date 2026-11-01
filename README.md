# AgentOS-RK — AgentOS Research Kit

**Working journal title:** *AgentOS-RK: A Compact and Auditable Research Kit for LLM-Agent Execution*.

**Manuscript for author review:** [Software Impacts Original Software Publication draft](paper/AGENTOS_RK_OSP_AUTHOR_REVIEW.md), including the [editable architecture schematic](paper/figures/agentos_rk_architecture.svg). The journal-format Word/PDF proofs are author-review artifacts, not an approved submission. The software tag, reproducible-capsule DOI, corresponding email and author declarations remain to be completed.

**AgentOS-RK is the reproducible research-software distribution of AgentOS, not a second-generation operating system.** The underlying AgentOS runtime (introduced at ASE 2026) executes typed filesystem, SQLite, and network requests behind a Verified Toolchain Reference Monitor (VTRM). A separate host-side World Effect Judge (WEJ) checks observed state changes rather than relying on the agent's textual claim of success.

This branch is the **MIT-licensed AgentOS-RK first-party source release candidate, not a tagged or archived published release**. Its source is reconstructed from a pinned upstream commit and seven integrity-checked companion components.

**Source license:** First-party AgentOS and journal-specific code is licensed under the [MIT License](LICENSE), **Copyright (c) 2026 Jun Zhou**, as confirmed by the project copyright holder. The same notice has been merged into the [original AgentOS repository](https://github.com/zhoujune/AgentOS/blob/main/LICENSE) through [upstream PR #1](https://github.com/zhoujune/AgentOS/pull/1) (merge commit `09326969884e35d0a3cd8633f94bb28eb90bc378`). The pinned historical upstream commit predates that license file; the reconstruction script carries the reviewed LICENSE into the resulting checkout. **Third-party dependencies, Linux/Buildroot components, model weights and generated guest images are not automatically covered by MIT**. Do not redistribute binary images or publish a release capsule until those notices and dependencies are reviewed; see [release gates](docs/RELEASE_CANDIDATE_GATES.md).

## Prior research

Jun Zhou and Tao Jia, *Introducing Safe LLM-Agent Execution via Typed Tool Mediation and World-Effect Evaluation*, ASE 2026, DOI [10.1145/3832783.3834637](https://doi.org/10.1145/3832783.3834637). Existing source: [zhoujune/AgentOS](https://github.com/zhoujune/AgentOS); prior archive: [10.5281/zenodo.20046861](https://doi.org/10.5281/zenodo.20046861).

The ASE paper's 24 benign and 48 adversarial live-model tasks are **prior results**, not new journal experiments. Its TLA+ model is an abstract check, not an end-to-end correctness proof.

## Release candidate: one-checkout CPU-only reproduction

This staging branch combines the original clean-source reconstruction, world-effect reuse demo, WEJ-Bench v0.1, and constrained-guest-memory study in **one Git tree**. It is designed for a reviewer to reproduce the technical baseline without private server access or model API keys. Install Git, Python 3, QEMU x86_64, `e2fsprogs` and `sha256sum` on an x86_64 Linux host.

```bash
git clone --branch release-candidate/agentos-v0.1.0-prelicense \
  https://github.com/zhoujune/AgentOS-Software-Impacts.git agentos-rc
cd agentos-rc
bash scripts/reproduce_release_candidate.sh "$PWD/../agentos-rc-results"
python3 -m json.tool ../agentos-rc-results/reproduction_summary.json
```

The script verifies seven patch/file hashes, clones the pinned upstream AgentOS commit, reconstructs the compatible source tree, runs the six-task baseline (three authorized effects plus three strict denials), and executes the positive/unsupported-success world-effect demo. Output folders must not exist in advance. The validator checks host-observed effects, exact replay and disabled guest networking. It labels the result **technical reproduction**, not independent human adoption.

For a non-maintainer trial and feedback form see [independent reproduction protocol](docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md). The public [clean-host CI workflow](.github/workflows/release-candidate-repro.yml) demonstrates automation from an empty Ubuntu runner, but cannot substitute for an independent researcher.

Detailed evidence: [216 live local-LLM episodes](benchmarks/wejbench/v0.1/results/20261101-live-216-audit-summary.md) (private-host, descriptive); [90 CPU replay task executions at 128–512 MiB guest RAM](benchmarks/resource-footprint/results/20261101-memory-results.md) (configured guest RAM, **not** total edge-device memory).


## Verified evidence

A [fresh Ubuntu 24.04 GitHub Actions run](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41271397622) passed **17/17 unit tests**, **1/1 QEMU smoke**, **6/6 representative replay tasks**, and **2/2 expected new-task outcomes**.

In the new task, a real authorized `fs.write` produced the required file (completion PASS); the control trace falsely claimed success but made no change (completion FAIL, intentionally). Safety and exact replay passed in both traces. [Validation summary](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/work/world-effect-reuse-demo/examples/world-effect-reuse/results/20261101-ci-summary.json).

See `docs/CLEAN_HOST_VALIDATION_20261101.md`, `patches/README.md`, and `examples/world-effect-reuse/README.md`.

## Publication limitations

These results validate a small **synthetic replay regression**, not the original 72-task live-model study, a security proof, or adoption by an independent researcher. The initial oversized patch was replaced by a newly validated split-source revision; it is not claimed byte-identical to the unpublished server patch.

The first-party MIT license file is now present. Before publication, complete third-party/binary notices and Buildroot/dependency locks, obtain non-maintainer reproduction, pin the release SHA in an immutable tag, and archive an authorized reproducible capsule. The current candidate is not the released artifact. Track these in [release issue #2](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/2) and [independent-user issue #6](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/6).
