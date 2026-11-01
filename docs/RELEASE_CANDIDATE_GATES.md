# AgentOS v0.1.0 — release-candidate gates (November 1, 2026)

**Candidate ref:** `release-candidate/agentos-v0.1.0-prelicense`.

**State: TECHNICAL STAGING ONLY.** This ref is neither a version tag nor a legally authorized software release. No redistribution rights are granted merely by public repository visibility.

## What is ready

- One Git branch includes the pinned original AgentOS reconstruction, reviewed three-patch/seven-input overlay, CPU-only baseline replay suite, independent world-effect demonstration, WEJ-Bench v0.1, and 128–512 MiB guest-memory study.
- One-command reproduction (see `scripts/reproduce_release_candidate.sh`) creates a **new** checkout of upstream commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`, verifies the seven inputs, and runs six replay tasks plus the positive/negative world-effect example.
- `.github/workflows/release-candidate-repro.yml` runs the same command on a clean Ubuntu 24.04 runner; a passing workflow is **developer-maintained CI**, not independent human reproduction.
- The separate internal 216 live-model cases and 90 constrained-guest-memory replay cases have sanitized summaries. They are not claims of model-general security or physical edge performance.

## Blocking gates (must all pass before a public release or acceptance claim)

| Gate | State | Required action / evidence |
| --- | --- | --- |
| Authorized copyright and license | **BLOCKED** | Identify the original AgentOS code copyright holder(s), the contributors to the journal overlay, and confirm permission to use the intended SPDX license. The ASE paper mentions MIT but the upstream and journal trees have no top-level `LICENSE` file. Obtain approval and commit exact license/copyright notices without assuming that an author can license other contributors' code. |
| Third-party and binary redistribution | **BLOCKED** | Review Buildroot, Linux/uClibc, QEMU, model weights, prepared images, third-party datasets, and generated binary licensing using the [inventory](LICENSE_AND_REDISTRIBUTION_REVIEW.md). Do not automatically redistribute pretrained models or built images. Respect source/notice obligations. |
| Immutable version and archive | **BLOCKED** | After license clearance and clean CI, agree release version, create immutable annotated tag `v0.1.0`, check release commit/tree identities, archive authorized source/capsule (e.g. Zenodo version DOI), and retain SHA-256 checksums. Branch name is not a release identifier. |
| Complete dependency provenance | **PARTIAL** | Current `manifests/manifest.lock` is explicitly partial. Record Buildroot exact source commit/package versions, dependency constraints and license notices; verify artifact rebuild procedure. |
| Clean-host technical CI | **PASSED AT TESTED COMMIT** | [GitHub workflow 41312785790](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41312785790) reconstructed the source and passed 6/6 baseline tasks plus the 2/2 world-effect fixture outcomes at commit `c7f3d640d865594681daaa0219d92441bb32f3c6`. Final release commit must also pass. |
| Non-maintainer independent reproduction | **NOT DONE** | Recruit a person outside the project. Provide only the one-branch public instructions. Collect first unaided attempt, environmental details, retries, setup time, completed six-task baseline, new-task positive and false-success controls and any additional participant-authored task. Retain consented, redacted artifact hashes. |
| Manuscript and metadata | **PARTIAL** | Fill C1–C9 (especially C3 capsule, C4 legal license, C9 approved support contact); confirm author list/affiliations; distinguish prior ASE contribution, 216-episode exploratory results and small guest-memory study. |

### Why license review cannot be automated away

A paper's declaration that a project is MIT-licensed does not, by itself, supply the exact copyright notices or prove that all code/patches and binaries can be redistributed under those terms. The correct next action is an explicit decision by people with legal authority. We intentionally do **not** fabricate or commit a `LICENSE` file before that decision.

### Why clean CI is not an independent-user study

The CI runner executes developer-written instructions without secret files on a fresh host, which is technical reproducibility evidence. It cannot measure first-use friction or show that a genuinely independent researcher can extend AgentOS without intervention. Issue #6 tracks that distinct study.

## After the gates pass

1. Freeze a reviewed release-candidate commit and pass a clean-host technical workflow.
2. Commit authoritative license files, copyright/third-party notices, and exact revision metadata.
3. Have a non-maintainer complete the written protocol, including documenting failures.
4. Create the licensed source tag and permanent repository/archive links, with an inspectable reproducibility capsule.
5. Update code metadata, manuscript, and tracking issues. Only then consider merging the release branch into `main`.

**Do not claim:** a finished licensed release, third-party uptake, full formal verification, 128 MiB total edge-device footprint, or original ASE 72-task reproduction.
