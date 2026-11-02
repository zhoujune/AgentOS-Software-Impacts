# AgentOS-RK — Software Impacts submission readiness

Status date: November 1, 2026. Intended article: **Original Software Publication (OSP)**, not a Software Update (AgentOS was previously introduced at ASE, not in a prior Software Impacts paper).

**Software name:** AgentOS-RK (AgentOS Research Kit). **Core runtime:** AgentOS (ASE 2026, DOI 10.1145/3832783.3834637). The kit extends reproducibility and uses the existing runtime; it is **not** AgentOS-2 or a new operating-system architecture.

**Recommended paper title:** *AgentOS-RK: A Compact and Auditable Research Kit for LLM-Agent Execution*.

## A. Actual submission blockers — finish these before clicking Submit

| Requirement | Current status | Concrete completion criterion |
| --- | --- | --- |
| Final manuscript in journal's OSP template | **DRAFT** | Prepare the provided short Software Impacts OSP template, verify all article sections and C1–C9 software metadata, add accurate figure/table/captions and references, and check the current Guide for Authors. |
| Novel software contribution relative to ASE | **NEEDS EDITORIAL REVIEW** | Explicitly state that VTRM/WEJ/TLA+ and basic AgentOS design were introduced at ASE. Emphasize AgentOS-RK as a usable research distribution, test-oracle extensibility, clean-host replay, audited 216-episode exploratory results and resource-footprint characterization. |
| Versioned public code | **OPEN** | After reviewing current CI and licensing boundaries, select a final commit, create an immutable `v0.1.0` tag / GitHub release for AgentOS-RK, and verify that reproduction instructions pin this version rather than a mutable branch. |
| Permanent software/capsule link (C2/C3) | **OPEN** | Archive the legal **source-only** release and its documentation/replay/test definitions to an immutable repository such as Zenodo; record a version-specific DOI and code SHA-256. Do not upload private VM images/model weights until third-party permission is established. |
| C4 license | **COMPLETE FOR FIRST-PARTY SOURCE** | First-party source is [MIT](../LICENSE), Copyright (c) 2026 Jun Zhou. The original upstream repository's corresponding MIT notice has also been merged. Separate third-party rights/attribution remain subject to review. |
| Third-party compliance and distribution scope | **OPEN** | Decide exactly which files will be distributed: preferably source and metadata only. Review any vendored JAR, original software patches, and dataset rights; exclude noncleared guest images/weights. If shipping Buildroot-derived images, complete per-package licenses, notices and source-availability requirements first. |
| Reproduction verified at final version | **PASS AT PRIOR TECHNICAL COMMITS; FINAL TAG NOT YET CHECKED** | Re-run clean Ubuntu reconstruction, six replay tasks and world-effect positive/negative controls at the intended release commit; ensure `LICENSE` copy and source-hash checks work. Five CI workflows passed on the prior integrated head. |
| Authors, affiliations and support (C9) | **SUPPLIED BY AUTHOR; JOURNAL CO-CORRESPONDING DISPLAY TO CONFIRM** | First author **Jun Zhou** (zhoujun@cqepc.edu.cn), now additionally designated co-corresponding; **Li Yuan** (yuanli@cqepc.edu.cn), also co-corresponding. Both at Chongqing Electric Power College, Chongqing, China. C9 software-support contact: **zhoujun@cqepc.edu.cn**. If Editorial Manager permits only one administrative corresponding author, select Li Yuan and keep both manuscript contact footnotes subject to journal acceptance. |
| Submission declarations and editorial checks | **PARTIAL** | Funding: **no specific grant**, per author confirmation; no-grant statement added. Competing-interest declaration and CRediT contributions still need author agreement; confirm AI-assistance disclosure and any submission metadata. |

## B. Highest-value polish (worth doing, but not new research)

1. **One architecture/research-workflow figure.** Distinguish model service, compact Buildroot guest, VTRM typed requests, external effects and host-side WEJ. Label formal analysis as *abstract model*, not implementation proof. Keep it editable/print-quality.
2. **One minimal real reuse example.** Show a permitted file write passes WEJ while an unsupported final-answer claim fails task completion. State both are developer-authored deterministic replay fixtures, not real LLM conversations.
3. **One compact evidence table.** 6/6 clean-host representative replay, 216 real local-model episodes (75/135 original completion-eligible tasks, configured safety/world checks all pass), 90/90 deterministic low-memory replay cases across 128–512 MiB QEMU guest RAM. Do not conflate safety, effectiveness, and memory caps.
4. **Citation/claim audit.** Verify dates, model version/fingerprint limits, abstract TLA+ scope, 128 MiB guest versus ~400 MiB QEMU+host process footprint, and absence of physical edge/energy testing. Cite original ASE paper explicitly.
5. **Usability handoff.** Keep the one-command clean-host reproduction and short non-maintainer quickstart obvious to a first-time researcher.

## C. Helpful extras — do not delay submission merely to pursue them

- One independent non-maintainer running the public instructions and creating a distinct task, with honest setup feedback (strong credibility benefit; not represented as mandatory by the OSP article template).
- Follow-up host-RSS measurement with tuned QEMU TCG, provided this is kept separately labeled as an emulator ablation.
- Other device architectures, edge boards or energy measurements: **future work**, not necessary to present the current evidence.
- More LLMs or more benchmarks: **not needed now**, unless the written manuscript exposes a precise missing control.

## Manuscript packaging plan

1. Edit the existing [working draft](../paper/OSP_WORKING_DRAFT.md), not a separate second paper.
2. Move dense experimental detail to public evidence files and retain just the most interpretable table in the article.
3. Format as an Original Software Publication using the journal's template and check article length after laying it out.
4. Freeze licensed **source-only** release candidate; pass CI and create an immutable source archive/DOI.
5. Complete actual author/declaration/C1–C9 metadata and submit after human review.

**Suggested stopping rule:** After the manuscript, one figure, one reuse example, immutable source release and required metadata are complete, stop feature development and submit. No new model matrix, ARM port or microVM benchmark is a prerequisite.

## Sources

- [Elsevier: Research Elements journals — Software Impacts](https://www.elsevier.com/researcher/author/tools-and-resources/research-elements-journals)
- [Software Impacts OSP template (version 2)](https://legacyfileshare.elsevier.com/promis_misc/SIMPAC_Article_Template.pdf)
- [Elsevier generative-AI declaration policy](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)
- [Existing AgentOS-RK RC PR #12](https://github.com/zhoujune/AgentOS-Software-Impacts/pull/12)
