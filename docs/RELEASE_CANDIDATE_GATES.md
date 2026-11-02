# AgentOS v0.1.0 — release-candidate gates (November 1, 2026)

**Candidate ref:** `release-candidate/agentos-v0.1.0-prelicense`.

**State: MIT-LICENSED FIRST-PARTY SOURCE CANDIDATE; NO VERSIONED RELEASE.**

For the verified source-only inventory, exact-revision CI checks, and outstanding gates, see [2026-11-02 release preflight](SOURCE_ONLY_RELEASE_PREFLIGHT_20261102.md). This ref is neither a version tag nor a redistributable binary release. The [LICENSE](../LICENSE) grants MIT rights for first-party software; third-party components retain separate licenses and obligations.

## What is ready

- One Git branch includes the pinned original AgentOS reconstruction, reviewed three-patch/seven-input overlay, CPU-only baseline replay suite, independent world-effect demonstration, WEJ-Bench v0.1, and 128–512 MiB guest-memory study.
- One-command reproduction (see `scripts/reproduce_release_candidate.sh`) creates a **new** checkout of upstream commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`, verifies the seven inputs, and runs six replay tasks plus the positive/negative world-effect example.
- `.github/workflows/release-candidate-repro.yml` runs the same command on a clean Ubuntu 24.04 runner; a passing workflow is **developer-maintained CI**, not independent human reproduction.
- The separate internal 216 live-model cases and 90 constrained-guest-memory replay cases have sanitized summaries. They are not claims of model-general security or physical edge performance.

## Blocking gates (must all pass before a public release or acceptance claim)

| Gate | State | Required action / evidence |
| --- | --- | --- |
| First-party MIT license | **COMPLETED IN STAGING** | Project owner confirmed MIT licensing and the copyright notice **Copyright (c) 2026 Jun Zhou**. [LICENSE](../LICENSE) is committed to the journal candidate; the corresponding [upstream original repo PR](https://github.com/zhoujune/AgentOS/pull/1) has been merged (`09326969884e35d0a3cd8633f94bb28eb90bc378`). Continue auditing any other contributor-owned files. |
| Third-party and binary redistribution | **BLOCKED** | Review Buildroot, Linux/uClibc, QEMU, model weights, prepared images, third-party datasets, and generated binary licensing using the [inventory](LICENSE_AND_REDISTRIBUTION_REVIEW.md). Do not automatically redistribute pretrained models or built images. Respect source/notice obligations. |
| Immutable version and archive | **BLOCKED** | After license clearance and clean CI, agree release version, create immutable annotated tag `v0.1.0`, check release commit/tree identities, archive authorized source/capsule (e.g. Zenodo version DOI), and retain SHA-256 checksums. Branch name is not a release identifier. |
| Complete dependency provenance | **PARTIAL** | The journal candidate currently has **no** `manifests/manifest.lock`; the dependency/source provenance inventory remains incomplete. Record the exact Buildroot source/configuration and package versions, review licenses/notices and verify the artifact rebuild procedure. Do not fabricate unknown dependency pins. |
| Clean-host technical CI | **PASSED AT TESTED COMMIT** | [GitHub workflow 41312785790](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41312785790) reconstructed the source and passed 6/6 baseline tasks plus the 2/2 world-effect fixture outcomes at commit `c7f3d640d865594681daaa0219d92441bb32f3c6`. Final release commit must also pass. |
| Non-maintainer independent reproduction | **NOT DONE** | Recruit a person outside the project. Provide only the one-branch public instructions. Collect first unaided attempt, environmental details, retries, setup time, completed six-task baseline, new-task positive and false-success controls and any additional participant-authored task. Retain consented, redacted artifact hashes. |
| Manuscript and metadata | **PARTIAL** | C4 now identifies **MIT first-party code**. Complete C1–C3 (tag and capsule), C9 (approved support contact), author list/affiliations, and third-party notices; distinguish ASE results, exploratory live evaluation and the memory study. |

### First-party license versus downstream redistribution

The project owner has now specified MIT licensing in the name Jun Zhou, and the authoritative [LICENSE](../LICENSE) was committed to the staging branch. The original upstream commit pinned for reproducibility predates the license addition, so the reconstruction script includes the same approved notice in its output, without changing the pinned source hash. **MIT does not relicense Linux, BusyBox, Buildroot, QEMU, TLA+ tools, model weights, or any other independently licensed component.** Binary/archive release still requires package-specific legal compliance and dependency verification.

### Why clean CI is not an independent-user study

The CI runner executes developer-written instructions without secret files on a fresh host, which is technical reproducibility evidence. It cannot measure first-use friction or show that a genuinely independent researcher can extend AgentOS without intervention. Issue #6 tracks that distinct study.

## After the gates pass

1. Freeze a reviewed release-candidate commit and pass a clean-host technical workflow.
2. **MIT first-party license committed.** Finish third-party/binary copyright notices and exact dependency revision metadata.
3. Have a non-maintainer complete the written protocol, including documenting failures.
4. Create the licensed source tag and permanent repository/archive links, with an inspectable reproducibility capsule.
5. Update code metadata, manuscript, and tracking issues. Only then consider merging the release branch into `main`.

**Do not claim:** a finished licensed release, third-party uptake, full formal verification, 128 MiB total edge-device footprint, or original ASE 72-task reproduction.
