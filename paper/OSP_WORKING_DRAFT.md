# DRAFT — Software Impacts Original Software Publication

> **Not for submission:** Working manuscript content based on the original ASE 2026 paper and local reproducibility audit. The first-party MIT license is now committed (Copyright 2026 Jun Zhou), but a tagged release, third-party redistribution audit, permanent reproducible capsule, independent human reproduction, and support contact are still pending. Do not reuse the original ASE contribution as if it were a new research result.

## AgentOS: A Compact, Auditable Execution and Evaluation Testbed for LLM Agents

**Authors / main developers (provisional, from ASE):** Jun Zhou and Tao Jia. Verify final affiliations, author list, corresponding author, and current email addresses before submission.

### Abstract (approximately 100 words)

AgentOS is a compact Buildroot-based execution and evaluation environment for tool-using large language model agents. Its typed filesystem, SQLite, and network actions are mediated by a capability- and label-aware reference monitor, supported by a small abstract TLA+ model. A host-side World Effect Judge validates outcomes from observable effects rather than agent declarations. The software supports CPU-only deterministic replay and local-model evaluation. In controlled x86_64 QEMU experiments, 90/90 selected replay tasks passed across 128–512 MiB configured guest RAM, although the complete host evaluation stack required substantially more memory. We describe extensibility, reproducibility, applications, and explicit assurance and deployment limits.

**Keywords:** LLM agents; execution safety; reference monitor; software reproducibility; world-effect evaluation; offline replay.

## Code metadata (OSP template C1–C9)

| Field | Draft entry / outstanding action |
| --- | --- |
| **C1 Current code version** | Technical candidate: [`release-candidate/agentos-v0.1.0-prelicense`](https://github.com/zhoujune/AgentOS-Software-Impacts/tree/release-candidate/agentos-v0.1.0-prelicense), combining the original AgentOS commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`, three SHA-256 checked patches, four pinned standalone files, WEJ-Bench v0.1, resource study and reuse demo. The candidate branch is mutable; a definitive release commit/tag is still required. |
| **C2 Permanent code/repository link for that version** | [GitHub staging PR #12](https://github.com/zhoujune/AgentOS-Software-Impacts/pull/12) (not permanent); replace with an authorized immutable tag and verified archive before submission |
| **C3 Permanent reproducible capsule link** | **TBD**: publicly accessible, independently validated capsule/source archive |
| **C4 Legal code license** | **MIT** for first-party AgentOS/journal software: [LICENSE](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/release-candidate/agentos-v0.1.0-prelicense/LICENSE), Copyright (c) 2026 Jun Zhou (per project owner). Original upstream LICENSE was merged in [AgentOS PR #1](https://github.com/zhoujune/AgentOS/pull/1). Third-party software and guest binary components retain their own licenses and require separate review. |
| **C5 Code versioning** | Git/GitHub with immutable original upstream commit and a checksum-verified seven-component source overlay; a journal version tag is still pending |
| **C6 Languages / tools / services** | Python 3, Bash, Buildroot, QEMU, SQLite, and TLA+ (formal model scope only) |
| **C7 Compilation and execution** | Linux host, QEMU x86_64, Python 3, `debugfs`, `e2fsck`; Buildroot 2026.02 tree required only to rebuild compatible guest images; exact version matrix pending |
| **C8 Documentation link** | [One-checkout candidate and reproducibility guide](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/release-candidate/agentos-v0.1.0-prelicense/README.md), [independent reproduction protocol](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/release-candidate/agentos-v0.1.0-prelicense/docs/INDEPENDENT_REPRODUCTION_PROTOCOL.md), [release gates](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/release-candidate/agentos-v0.1.0-prelicense/docs/RELEASE_CANDIDATE_GATES.md); final tagged links pending |
| **C9 Support email** | **TBD**: confirm the appropriate contact and consent to publish it |

## 1. Software description

Large language model agents can propose file edits, database operations, and network actions. AgentOS provides an execution boundary that separates generated requests from authorized effects. The software consists of a small Buildroot-based guest runtime, a typed request frontend, the Verified Toolchain Reference Monitor (VTRM), restricted effect adapters, a host-side proxy, and the World Effect Judge (WEJ).

A tool request is extracted from model output, validated, classified by object and sink, and checked against derived capabilities and confidentiality labels. VTRM returns an allow, approval-required, or deny decision before an adapter performs an effect. Unlike a self-reported task success, a WEJ result is determined through configured observations of filesystem, SQLite, audit, and network state. The original ASE paper provides the underlying design and security evaluation; this manuscript documents software usage and reproducibility rather than reintroducing the same framework as novel research.

AgentOS-Prod is intended as the execution-oriented guest profile. AgentOS-Eval runs the guest under QEMU with host-controlled reset and effect observations. The available host interface and test harness orchestrate guest startup, task transfer, model interaction through the bridge, and evaluation reports. The current measured x86_64 evaluation artifacts consist of a 6.0 MB kernel image and a provisioned 60 MiB ext2 guest filesystem; these are static artifact sizes, not resident RAM or full-host footprint. The design supports separating the local execution guest from a computationally expensive model-serving process.

## 2. Software impact and reuse

AgentOS supports two concrete research activities. First, investigators can formulate allowed and forbidden effects and evaluate an agent against observed world-state changes, separating task completion from security violations. Second, the deterministic replay workflow can replay selected request/response exchanges without live model access, allowing repeated testing of the guest bridge, typed enforcement pipeline, permission boundaries, and evaluator on CPU-only hosts.

The verified representative replay cassette currently contains 13 exact responses spanning six tasks: three legitimate workspace-file tasks and three unsafe database operations. The experiment has demonstrated exact replay matching and world-integrity validation across these cases. This is useful for debugging and regression testing of software changes, but it is **not** a substitute for an LLM evaluation of the full 24 benign and 48 adversarial tasks in the ASE paper.

A separate extensibility example introduces a previously unseen task with an explicit filesystem-effect oracle. Two hand-authored replay traces both claim completion; only one executes the required `fs.write`. In a clean GitHub-hosted QEMU run, WEJ accepted the observed write and rejected the unsupported textual success claim, while both traces passed replay and safety checks. This shows how researchers can add a task and inspect machine-readable world-effect evidence without a model API. It is an integration test, **not** an independent-user study or a live-model success-rate measurement. [Evidence](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41271397622).

The constrained-memory study extends this use case. It executed three legitimate effect tasks and three strict-denial tasks, repeated three times at each of five QEMU guest-memory allocations (128–512 MiB), for **90/90 validated replay cases**. The 128 MiB guest booted with approximately 105 MiB available to Linux, but measured peak host process-tree PSS remained roughly 401 MiB because the measurement includes QEMU software emulation and the host evaluator. All input-image hashes remained unchanged. A separate, single-task TCG translation-cache probe localized a large part of this overhead to emulator configuration; it is not an embedded-device or full-suite result. [Measurement protocol and per-case evidence](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/work/constrained-memory-footprint-20261101/benchmarks/resource-footprint/results/20261101-memory-results.md).

A separate three-family local-model evaluation exercised 24 selected and newly authored tasks under the same world-effect evaluation framework (216 completed episodes). Its configured world-integrity/safety checks passed in all 216 cases, while the original completion oracle succeeded in 75 of 135 completion-eligible cases. These task- and model-specific results are reported descriptively and separately from deterministic replay and the earlier ASE evaluation. [Audited live-model evidence](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/work/wej-bench-v0.1/benchmarks/wejbench/v0.1/results/20261101-live-216-audit-summary.md).

The offline benchmarking work also records per-case latency stages, machine settings, image hashes, and replay provenance, enabling controlled analysis of polling choices. Any measured reduction is descriptive and limited to this fixed task selection until repeated, controlled observations and broader workload tests are available. These software facilities can reduce dependency on external model APIs for systems validation while keeping claims about real agent behavior clearly separate.

## 3. Limitations, future development, and prior publication

VTRM's modeled enforcement scope includes typed filesystem, SQLite, and network operations. Arbitrary shell commands, unrestricted SQL, graphical interfaces, and other unmediated channels remain outside the claimed boundary. The available TLA+ check concerns an abstract typed decision path and is not an end-to-end implementation proof. WEJ observes only configured surfaces and task-specific effects. Offline replay does not test generation-time model robustness, adaptive prompting, or live-model latency. The constrained-memory results demonstrate compatibility with selected tasks at 128 MiB *configured guest RAM*, not the minimum possible configuration, total physical edge-device footprint, hardware energy efficiency, native ARM deployment, or a fair cross-sandbox performance advantage. The test host lacked KVM and used QEMU TCG.

A **single-branch candidate with MIT-licensed first-party source code** now supplies a clean-host reconstruction script and host-side baseline/demo result validator. The third-party packages and guest binary distribution remain under separate licenses and review. Automated clean-host CI, even if successful, is not evidence of a non-maintainer reproducing and extending the software. Before submission, this artifact must acquire an immutable versioned source release, a properly licensed reproducible capsule, final support metadata, and a successful independent reproduction check. Longer traces, broader exact replay coverage, additional models and effect adapters, and tests across more host environments remain potential extensions.

**Prior research publication:** Jun Zhou and Tao Jia, *Introducing Safe LLM-Agent Execution via Typed Tool Mediation and World-Effect Evaluation*, Proceedings of ASE 2026, DOI [10.1145/3832783.3834637](https://doi.org/10.1145/3832783.3834637).

**Prior software archive:** Jun Zhou, *System Images and Benchmark Tasks for AgentOS*, Zenodo, DOI [10.5281/zenodo.20046861](https://doi.org/10.5281/zenodo.20046861).

---

**Editorial preparation:** The Software Impacts Original Software Publication template (version 2, July 2021) requests approximately 100 words for the abstract, up to six keywords, code metadata C1–C9, and up to three pages of article body (excluding metadata, tables, figures, and references). Confirm the current Guide for Authors before submission: https://legacyfileshare.elsevier.com/promis_misc/SIMPAC_Article_Template.pdf
