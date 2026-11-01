# AgentOS-RK: A Compact and Auditable Research Kit for LLM-Agent Execution

**Article type:** Software Impacts — Original Software Publication (author-review draft; not yet submission-ready)

**Authors (provisional):** Jun Zhou; Tao Jia. **[Confirm current author order, affiliations, postal addresses, and corresponding email.]**

## Abstract

AgentOS-RK is a reproducible research kit for studying tool-using large language model agents. Built on the previously published AgentOS runtime, it combines a compact Buildroot guest, typed effect mediation, an abstract TLA+ policy model, and a host-side judge that checks observed state changes instead of agent claims. Researchers can replay recorded interactions without model APIs, add task-specific effect oracles, or evaluate local models. In controlled x86-64 QEMU tests, all 90 selected replay cases passed across 128–512 MiB configured guest RAM; the emulated host environment used substantially more memory. The kit supports reproducible investigations of task utility and policy enforcement.

**Keywords:** LLM agents; research software; typed tool mediation; world-effect evaluation; reproducibility; constrained execution.

## Code metadata

| Nr. | Code metadata description | Value |
| --- | --- | --- |
| C1 | Current code version | AgentOS-RK v0.1.0 release candidate (unreleased); immutable release tag pending. |
| C2 | Permanent repository link for the version | [AgentOS-Software-Impacts](https://github.com/zhoujune/AgentOS-Software-Impacts), current RC branch; **replace with version-tagged immutable link**. |
| C3 | Permanent reproducible capsule | **[PENDING: public source-only archive and capsule DOI]**. |
| C4 | Legal code license | MIT for first-party software; Copyright (c) 2026 Jun Zhou. Third-party components keep their own licenses. |
| C5 | Code versioning | Git; pinned upstream AgentOS SHA and verified companion patch inputs. |
| C6 | Software languages / tools | Python, Bash, Buildroot/Linux, QEMU, SQLite, TLA+ (abstract model). |
| C7 | Requirements and dependencies | Linux x86-64, Python 3, Git, QEMU x86-64, e2fsprogs; pinned upstream AgentOS. Full Buildroot recompilation requires a separately provisioned compatible Buildroot tree; dependency manifest partial. |
| C8 | Developer documentation | [AgentOS-RK candidate README](../README.md) (replace with tagged permalink). |
| C9 | Support email | **[PENDING: author-approved support address]**. |

## 1. Software description

Tool-using large language model (LLM) agents can alter files and databases or initiate network operations. A transcript alone cannot establish whether an intended action occurred or whether an unauthorized effect was prevented. **AgentOS-RK** (AgentOS Research Kit) packages an execution environment and effect-oriented test infrastructure for reproducible studies of these questions. It is a distribution of the AgentOS system introduced at ASE 2026 [1], not a new operating system or a newly introduced security mechanism.

The architecture (Fig. 1) separates model output or deterministic replay from a restricted Buildroot guest. Agent requests are converted into typed operations, including filesystem and SQLite operations, and passed to the Verified Toolchain Reference Monitor (VTRM). The monitor evaluates capability and confidentiality-label rules before effect adapters execute permitted actions. The host-side World Effect Judge (WEJ) then examines configured filesystem snapshots, database changes, audit records, and network observations independently of an agent's textual answer. A TLA+ specification checks selected properties of an abstract policy decision model; it is **not** a formal verification of the Linux guest, QEMU, bridge, or complete evaluator.

![Fig. 1. AgentOS-RK architecture](figures/agentos_rk_architecture.svg)

*Fig. 1. AgentOS-RK architecture. The TLA+ component models abstract policy decisions; the host judge inspects configured effects. Schematic was prepared programmatically with OpenAI ChatGPT (GPT-6) assistance; author verification pending.*

AgentOS-RK supplies a single-checkout source reconstruction, repeatable guest resets, fixed request/response replay cassettes, task-specific effect oracles, audit checks, and local-model evaluation drivers. The prepared x86-64 evaluator uses a 6.0 MB kernel image and a provisioned 60 MiB ext2 root filesystem; those are **artifact sizes**, not operating-memory measurements. Expensive model inference can run outside the constrained guest.

## 2. Software impact and researcher workflow

A researcher first defines a task with an observable success predicate and, where relevant, a forbidden-effect predicate. They can then choose deterministic replay to validate the mediation and judging stack without model API access, or evaluate a local LLM through the same typed interface. Finally, the host judge reports task completion, replay matching, policy-denial evidence, and unintended state changes separately. This supports reproducible debugging and enables comparisons that do not equate a fluent completion claim with a completed action.

The supplied reuse example illustrates the distinction directly. Two developer-authored traces both claim to have completed a file-write task. One performs an authorized `fs.write`; the other emits only a final success message. The first passes its effect oracle and the second fails task completion, while both retain valid replay and safety checks. The negative result is intentional. A clean GitHub-hosted workflow reproduces the six-task baseline (three legitimate effects and three explicit database denials) and these two demonstration outcomes [3]. This is **developer-maintained technical reproducibility**, not evidence of independent adoption.

Table 1 summarizes additional, separately scoped evidence. Across three local model families, a 24-task set repeated three times produced 216 completed episodes. All 216 passed the evaluator's configured safety and world-integrity checks; the original completion oracle passed in 75 of 135 completion-eligible episodes [4]. These figures must not be interpreted as a universal agent security or success rate. In a separate exact-replay resource sweep, all 90 selected task executions passed across five configurations of 128–512 MiB guest RAM [5]. At 128 MiB guest allocation, peak sampled host process-tree proportional set size remained approximately **401 MiB** because QEMU software emulation and the host evaluation components were also resident.

The software impact is practical rather than a claim of superior sandbox performance: task authors can reproduce enforcement behavior, inspect concrete world effects, and extend evaluations without changing the core policy implementation. Unlike benchmarks restricted to agent answers, this workflow makes observable changes part of the task oracle; unlike a general-purpose virtual machine alone, it supplies typed action mediation and an integrated outcome judge. AgentDojo [6] and specialized virtualization systems such as Firecracker [7] address complementary research needs rather than serving as directly comparable baselines.

**Table 1. Separate evidence streams; denominators and observation boundaries are not interchangeable.**

| Evaluation | Observed result | Scope / caveat |
| --- | --- | --- |
| Clean-host exact replay | 6/6 selected tasks | Three permitted effects, three strict DB denials; CI [3]. |
| World-effect negative control | One positive / one intentional rejection | Authorized write accepted; unsupported success rejected [3]. |
| Live local-LLM study | 216 episodes; 75/135 completion-eligible cases | 216/216 configured safety and world-integrity checks; task-specific [4]. |
| Constrained guest memory | 90/90 selected replay cases; 128–512 MiB | Three repetitions x five caps x six tasks; 128 MiB cap still ~401 MiB host process-tree peak PSS [5]. |

## 3. Availability, limitations and future work

First-party AgentOS-RK code is released under MIT terms, Copyright (c) 2026 Jun Zhou. The candidate repository contains documentation, source patches, benchmark fixtures, result summaries, and reconstruction scripts. The v0.1.0 source-only tag and permanent capsule identifier have **not** yet been issued; both must replace temporary C1–C3 entries before submission. Guest images, Buildroot-generated binaries, and external model weights are outside the intended source-only archive pending their respective licensing and source-notice checks.

The formal analysis covers only an abstract policy model, while the runtime boundary covers explicitly typed effect channels. The judge can only validate states and effects for which a task oracle and observation surface exist. Deterministic replay tests the execution/evaluation system but not model behavior. The low-memory results demonstrate six selected replay tasks under a 128 MiB configured guest cap on x86-64 QEMU with TCG, **not** a measured 128 MiB entire device, a minimum-memory threshold, ARM compatibility, energy efficiency, or an advantage over other virtualization systems. Independent non-maintainer reproduction and physical edge deployment remain future validation goals.

## Declaration of competing interest

**[PENDING: authors to confirm.]**

## Funding

**[PENDING: authors to confirm grant support or absence of specific funding.]**

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During preparation of this manuscript, the authors used OpenAI ChatGPT (GPT-6) to assist with literature checking, text organization, editing, and programmatic preparation of the explanatory architecture schematic. The authors must review and revise the material as needed and accept full responsibility for the final publication. **[Author review and confirmation pending.]**

## References

[1] J. Zhou and T. Jia, “Introducing Safe LLM-Agent Execution via Typed Tool Mediation and World-Effect Evaluation,” ASE 2026, Tools and Datasets. https://doi.org/10.1145/3832783.3834637

[2] J. Zhou, “System Images and Benchmark Tasks for AgentOS,” Zenodo (2026). https://doi.org/10.5281/zenodo.20046861

[3] AgentOS-RK, “Clean-host technical reproduction and world-effect reuse example,” GitHub Actions, run 41312785790 (2026). https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41312785790

[4] AgentOS-RK, “WEJ-Bench v0.1: audited 216-episode local-model evaluation,” research-software repository (2026). [Audited report](../benchmarks/wejbench/v0.1/results/20261101-live-216-audit-summary.md).

[5] AgentOS-RK, “CPU-only constrained-memory benchmark,” research-software repository (2026). [Results](../benchmarks/resource-footprint/results/20261101-memory-results.md).

[6] E. Debenedetti et al., “AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents,” NeurIPS 37 (2024). https://doi.org/10.52202/079017-2636

[7] A. Agache et al., “Firecracker: Lightweight Virtualization for Serverless Applications,” NSDI 2020, pp. 419–434. https://www.usenix.org/conference/nsdi20/presentation/agache

---

**Review-only checklist — remove before submission:** Confirm authors and correspondence; fill C1–C3/C9 with immutable tag, archive, and email; review third-party license scope; obtain human approval of figure and substantive AI declaration; audit all numbers and references; remove draft notices.
