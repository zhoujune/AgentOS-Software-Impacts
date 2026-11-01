# Licensing approval and distribution review — AgentOS v0.1.0

**First-party license committed; binary/third-party redistribution review remains open.** Updated 2026-11-01 following the project owner's confirmation of MIT licensing in the name Jun Zhou. This document records remaining dependencies and does not replace the authoritative [LICENSE](../LICENSE) text. No versioned release tag or binary archive has been created.

## First-party code: MIT license (committed)

**SPDX identifier:** `MIT` for first-party AgentOS and journal-specific source code, per project-owner confirmation.

**Authoritative first-party license file:** [LICENSE](../LICENSE), consistent with [SPDX MIT](https://spdx.org/licenses/MIT.html).

**Copyright line:** `Copyright (c) 2026 Jun Zhou` (as explicitly specified by the project owner).

**Approval and remaining scope questions:**

- [x] The project owner specified MIT terms and the copyright notice `Jun Zhou` for original AgentOS and journal first-party code. Any unidentified contributor-owned material still requires a provenance check before release.
- [x] MIT terms were specified for the journal first-party changes as well as original AgentOS; the candidate includes a top-level LICENSE. The upstream repository's [license PR](https://github.com/zhoujune/AgentOS/pull/1) has been merged into `main`.
- [ ] Are there any institutional, employment, collaboration, or previously assigned rights requiring additional approval?
- [x] Copyright notice confirmed by the project owner: `Copyright (c) 2026 Jun Zhou`.
- [ ] Should any third-party files remain subject to their existing licenses instead of an MIT blanket statement?
- [x] First-party source license grant is present in [LICENSE](../LICENSE). Public visibility alone is not a substitute for that license.

**Next:** audit third-party file ownership and licenses separately, reconcile any additional contributor rights, and retain required notices for generated binaries. Journal C4 can identify MIT for first-party code while explicitly stating that third-party components keep their own licenses.

## Third-party and binary distribution inventory

| Item | Existing evidence | Outstanding action |
| --- | --- | --- |
| Buildroot guest build | Buildroot version `2026.02` is named in the test environment; the checked manifest explicitly says exact Buildroot commit and package revisions are **not pinned** | Pin source revision/configuration and run `make legal-info` on the actual build output; inspect its warnings, manifests, sources and license texts. Buildroot's legal-info output is a starting point, not proof of compliance. |
| Linux kernel `6.12.47` | Kernel image SHA-256 is recorded; the kernel is GPL-2.0-only with documented exceptions | Track kernel sources/configuration and redistribution obligations; do **not** label the entire compiled kernel MIT. |
| BusyBox, standard C library and target packages | Present within Buildroot-generated guest; full package license manifest not in the current journal release | Generate and review per-package license/source inventory. Retain source and notices required for binary redistribution. |
| QEMU host runtime | Ubuntu CI installed system QEMU `8.2.2` | QEMU is used as a system dependency, not distributed as an AgentOS binary in the current journal branch; document supported versions. |
| TLA+ tools `tla2tools.jar` | A third-party jar is present in the original source checkout | Verify third-party distribution terms, source/version and existing copyright/notice files; keep an explicit license exception or external download if necessary. |
| AgentOS guest kernel/ext2 rootfs | Guest image and kernel fingerprints recorded; no new guest images committed in the journal release candidate | Do not archive or attach the binaries until the third-party notices/source distribution analysis is complete. |
| Original task fixtures, evaluation data and cassettes | Some task definitions came from the prior ASE artifact; new journal WEJBench fixtures are authored in the companion repository | Confirm ownership, dataset/fixture rights and any test data redistribution conditions. |
| Llama 3 8B, Qwen3 14B, Mistral 7B v0.3 | Used locally for the private live evaluation; no weights were uploaded as journal artifacts | Independently verify each upstream model checkpoint revision and its license/acceptable uses. Keep weights excluded from the release unless specifically permitted and necessary. |
| Optional Streamlit / Python dependencies | `streamlit>=1.44,<2` is documented; transitive UI lock remains incomplete | Pin and inventory optional dependency versions/licenses separately from the CPU-only replay prerequisite path. |

Buildroot's [official legal-compliance instructions](https://buildroot.org/downloads/manual/manual.html#_legal_notice_and_licensing) recommend `make legal-info` and explicitly warn that generated metadata is not a complete compliance determination. The [Linux kernel's own licensing documentation](https://docs.kernel.org/process/license-rules.html) describes the kernel licensing boundary.

## Technical candidate evidence (does not resolve licensing)

The staging [PR #12](https://github.com/zhoujune/AgentOS-Software-Impacts/pull/12) has passed the integrated technical workflow at commit `c7f3d640d865594681daaa0219d92441bb32f3c6`. A separate later run on the branch head is tracked in GitHub Actions. The six baseline replay tasks and two positive/false-success traces are suitable as **technical reproducibility** evidence, not non-maintainer adoption evidence.

## Release authorization record — to be filled by authorized contributors

| Field | Required value |
| --- | --- |
| Grant authorized for original AgentOS first-party source? | **MIT confirmed by project owner; upstream LICENSE merged into `main`** |
| Grant authorized for journal companion first-party code? | **MIT specified and committed in staging LICENSE** |
| Intended license / scope | **MIT first-party code**, other components excluded from blanket grant |
| Name(s) of copyright holder(s) | **Jun Zhou** (per owner confirmation) |
| Year(s) of copyright | **2026** |
| Third-party files excluded from the grant | **Under review** |
| Binary redistribution approved? | **No; pending legal-info audit** |
| Authorized approver(s) and date | **Project owner confirmed MIT / Jun Zhou in conversation, 2026-11-01**; retain permanent project governance record if required |

Record final approval in an appropriate maintained repository review/issue or signed project document. Do not publish personal signatures, private emails or contractual details without consent.

## Next release sequence

1. **Completed for first-party code:** MIT license with 2026 Jun Zhou copyright notice committed to the journal candidate; upstream PR merged.
2. **Outstanding:** review other contributor rights and third-party/binary notices; complete package/source inventory and Buildroot pin.
3. Re-run a clean CI workflow against the *new commit*.
4. Recruit and document one non-maintainer independent reproduction (issue #6).
5. Tag only the approved and validated commit, create a compliant immutable archive/Zenodo version DOI, and update journal software metadata.

Until then, leave [release issue #2](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/2) open and the RC PR as draft.
