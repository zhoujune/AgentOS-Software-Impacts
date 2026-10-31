# DRAFT — Software Impacts Original Software Publication

> **Not for submission:** Working manuscript content based on the original ASE 2026 paper and local reproducibility audit. The current code-version, release license, permanent reproducible capsule, and support contact still need confirmation. Do not reuse the original ASE contribution as if it were a new research result.

## AgentOS: A Reproducible Execution and Evaluation Platform for Safe LLM Agents

**Authors / main developers (provisional, from ASE):** Jun Zhou and Tao Jia. Verify final affiliations, author list, corresponding author, and current email addresses before submission.

### Abstract (approximately 100 words)

AgentOS is a Buildroot-based environment for executing and evaluating tool-using large language model agents. Its Verified Toolchain Reference Monitor mediates typed filesystem, SQLite, and network requests using capability- and label-aware decisions. An independent host-side World Effect Judge assesses task outcomes from observed filesystem, database, audit, and network state. This software publication documents the runtime and evaluation profiles and an offline deterministic replay workflow for selected tasks without live model inference. Six representative replay tasks validate permitted file effects and database denials with world-integrity checks. We describe the software’s reproducibility features, research applications, and explicit security and evaluation limits, extending its previously published ASE framework through artifact-focused documentation.

**Keywords:** LLM agents; execution safety; reference monitor; software reproducibility; world-effect evaluation; offline replay.

## Code metadata (OSP template C1–C9)

| Field | Draft entry / outstanding action |
| --- | --- |
| **C1 Current code version** | **TBD**: create an immutable tagged software version; do not label this staging branch a release |
| **C2 Permanent code/repository link for that version** | [AgentOS-Software-Impacts](https://github.com/zhoujune/AgentOS-Software-Impacts); replace with an immutable tag or release URL |
| **C3 Permanent reproducible capsule link** | **TBD**: publicly accessible, independently validated capsule/source archive |
| **C4 Legal code license** | **TBD**: ASE described original work as MIT, but neither inspected tree contained a top-level LICENSE file; confirm authority and publish complete license terms |
| **C5 Code versioning** | Git/GitHub for this journal repository; original experimental source snapshot still requires commit reconciliation |
| **C6 Languages / tools / services** | Python 3, Bash, Buildroot, QEMU, SQLite, and TLA+ (formal model scope only) |
| **C7 Compilation and execution** | Linux host, QEMU x86_64, Python 3, `debugfs`, `e2fsck`; Buildroot 2026.02 tree required only to rebuild compatible guest images; exact version matrix pending |
| **C8 Documentation link** | This repository's `docs/` directory (in preparation); source software [AgentOS](https://github.com/zhoujune/AgentOS) |
| **C9 Support email** | **TBD**: confirm the appropriate contact and consent to publish it |

## 1. Software description

Large language model agents can propose file edits, database operations, and network actions. AgentOS provides an execution boundary that separates generated requests from authorized effects. The software consists of a small Buildroot-based guest runtime, a typed request frontend, the Verified Toolchain Reference Monitor (VTRM), restricted effect adapters, a host-side proxy, and the World Effect Judge (WEJ).

A tool request is extracted from model output, validated, classified by object and sink, and checked against derived capabilities and confidentiality labels. VTRM returns an allow, approval-required, or deny decision before an adapter performs an effect. Unlike a self-reported task success, a WEJ result is determined through configured observations of filesystem, SQLite, audit, and network state. The original ASE paper provides the underlying design and security evaluation; this manuscript documents software usage and reproducibility rather than reintroducing the same framework as novel research.

AgentOS-Prod is intended as the execution-oriented guest profile. AgentOS-Eval runs the guest under QEMU with host-controlled reset and effect observations. The available host interface and test harness orchestrate guest startup, task transfer, model interaction through the bridge, and evaluation reports.

## 2. Software impact and reuse

AgentOS supports two concrete research activities. First, investigators can formulate allowed and forbidden effects and evaluate an agent against observed world-state changes, separating task completion from security violations. Second, the deterministic replay workflow can replay selected request/response exchanges without live model access, allowing repeated testing of the guest bridge, typed enforcement pipeline, permission boundaries, and evaluator on CPU-only hosts.

The verified representative replay cassette currently contains 13 exact responses spanning six tasks: three legitimate workspace-file tasks and three unsafe database operations. The experiment has demonstrated exact replay matching and world-integrity validation across these cases. This is useful for debugging and regression testing of software changes, but it is **not** a substitute for an LLM evaluation of the full 24 benign and 48 adversarial tasks in the ASE paper.

The offline benchmarking work also records per-case latency stages, machine settings, image hashes, and replay provenance, enabling controlled analysis of polling choices. Any measured reduction is descriptive and limited to this fixed task selection until repeated, controlled observations and broader workload tests are available. These software facilities can reduce dependency on external model APIs for systems validation while keeping claims about real agent behavior clearly separate.

## 3. Limitations, future development, and prior publication

VTRM's modeled enforcement scope includes typed filesystem, SQLite, and network operations. Arbitrary shell commands, unrestricted SQL, graphical interfaces, and other unmediated channels remain outside the claimed boundary. The available TLA+ check concerns an abstract typed decision path and is not an end-to-end implementation proof. WEJ observes only configured surfaces and task-specific effects. Offline replay does not test generation-time model robustness, adaptive prompting, or live-model latency.

Before submission, this artifact must acquire a versioned source release, a clear license, a permanent reproducible capsule, complete developer instructions, and a successful independent reproduction check. Longer traces, broader exact replay coverage, additional models and effect adapters, and tests across more host environments remain potential extensions.

**Prior research publication:** Jun Zhou and Tao Jia, *Introducing Safe LLM-Agent Execution via Typed Tool Mediation and World-Effect Evaluation*, Proceedings of ASE 2026, DOI [10.1145/3832783.3834637](https://doi.org/10.1145/3832783.3834637).

**Prior software archive:** Jun Zhou, *System Images and Benchmark Tasks for AgentOS*, Zenodo, DOI [10.5281/zenodo.20046861](https://doi.org/10.5281/zenodo.20046861).

---

**Editorial preparation:** The Software Impacts Original Software Publication template (version 2, July 2021) requests approximately 100 words for the abstract, up to six keywords, code metadata C1–C9, and up to three pages of article body (excluding metadata, tables, figures, and references). Confirm the current Guide for Authors before submission: https://legacyfileshare.elsevier.com/promis_misc/SIMPAC_Article_Template.pdf
