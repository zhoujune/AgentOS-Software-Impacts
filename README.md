# AgentOS — Software Impacts

Companion software-publication and reproducibility work for **AgentOS**, a Buildroot/QEMU-based environment for tool-using LLM agents. AgentOS mediates typed filesystem, SQLite, and network actions through the Verified Toolchain Reference Monitor (VTRM). The host-side World Effect Judge (WEJ) evaluates externally observed effects.

## Relationship to the published ASE paper

This repository is being prepared for a **Software Impacts Original Software Publication**. It is **not yet a tagged, reproducible software release**, and it must not be used to imply an independent new full-suite security evaluation.

- **Original paper:** Jun Zhou and Tao Jia, *Introducing Safe LLM-Agent Execution via Typed Tool Mediation and World-Effect Evaluation*, ASE 2026. DOI: [10.1145/3832783.3834637](https://doi.org/10.1145/3832783.3834637).
- **Existing software:** [zhoujune/AgentOS](https://github.com/zhoujune/AgentOS).
- **Original archived artifact:** [10.5281/zenodo.20046861](https://doi.org/10.5281/zenodo.20046861).

The ASE paper reports evaluation on 24 benign and 48 adversarial tasks with two LLMs. Its TLA+ checks concern the abstract typed mediation core, **not an end-to-end proof of the Python implementation**. Arbitrary shell execution, unrestricted SQL, and unmodeled effect channels remain outside the verified enforcement scope.

## Journal-software workstream

The emphasis here is on a usable and inspectable software artifact:

1. CPU-only deterministic LLM-request replay for selected end-to-end tasks without live model API calls;
2. host-observed world-effect validation, exact replay matching, VTRM denial evidence, and disabled guest networking;
3. reproducible experimental guest images, hashes, environment manifests, and controlled performance analysis;
4. installation, usage, security-boundary, and release documentation.

**Status (2026-10-31):** a previous six-task representative replay smoke passed all six cases (three benign and three direct database denials) with world-integrity checks. A guest image with 0.2-second polling defaults also passed one six-task smoke. These are **functional checks**, not evidence of full-suite replay support or a statistically reliable latency improvement. A matched repeated benchmark is being prepared.

## Layout planned for this repository

- `docs/` — deployment, security scope, benchmark protocol, and reproduction instructions.
- `benchmarks/` — compact manifests, aggregated measurements, and interpretation (not mutable VM disks).
- `paper/` — journal manuscript files and submission metadata.
- Software sources and suitable redistributable artifacts will be added only after their exact provenance and licensing are checked.

## Publication and release caveats

This new repository is a working publication project. **Do not cite it as a released code version** until a source snapshot, commit identity, explicit license, dependencies, runnable examples, and archival release are in place. Preliminary offline comparisons must remain distinct from the original ASE safety results.

## Development environment

The server-side experimental copy currently resides at `/workspace/agentos-journal/repo/AgentOS-main/`. Its source tree lacks `.git` metadata. The original GitHub repository above supplies a verifiable upstream reference, but a direct source-tree equivalence check remains to be completed.

> Manuscript title (working): **AgentOS: A Reproducible Execution and Evaluation Platform for Safe LLM Agents**.
