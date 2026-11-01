# Licensing approval and distribution review — AgentOS v0.1.0

**Review document, not a license grant.** Prepared 2026-11-01. No `LICENSE` file or copyright authorization has been established for this public repository, and no tagged licensed release should be created until signoff is documented.

## First-party code: proposed MIT terms

**Proposed SPDX identifier:** `MIT`, subject to documented approval from all relevant rightsholders.

**Standard license text to use only after approval:** [SPDX MIT License](https://spdx.org/licenses/MIT.html).

**Proposed copyright line:** `Copyright (c) 2026 [CONFIRMED COPYRIGHT HOLDER(S)]`. The actual year(s), legal names and scope must be determined from contributor/provenance records; the authors named in a research paper are not automatically all copyright holders.

**Rights and scope questions requiring explicit confirmation:**

- [ ] Does the person authorizing release own, or have permission from all owners to license, the original `zhoujune/AgentOS` code and documentation at commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c` under MIT?
- [ ] Is the same authorization available for the seven original-to-journal overlay inputs (three patches and four standalone source files) and the later benchmark/evaluation/documentation additions?
- [ ] Are there any institutional, employment, collaboration, or previously assigned rights requiring additional approval?
- [ ] What exact copyright holder names and years should appear in the final license and notices?
- [ ] Should any third-party files remain subject to their existing licenses instead of an MIT blanket statement?
- [ ] Is there written approval for distributing the source itself? Public GitHub visibility is not a license grant.

**Only after these checks:** add an authoritative top-level `LICENSE` with the unmodified standard MIT text and confirmed copyright line; make clear which portions are separately licensed; add relevant SPDX headers/notices where appropriate. Audit scope before making journal C4 claims.

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
| Grant authorized for original AgentOS source? | **Unconfirmed** |
| Grant authorized for journal companion code? | **Unconfirmed** |
| Intended license / scope | Proposed `MIT`; **not approved** |
| Name(s) of copyright holder(s) | **Unconfirmed** |
| Year(s) of copyright | **Unconfirmed** |
| Third-party files excluded from the grant | **Under review** |
| Binary redistribution approved? | **No; pending legal-info audit** |
| Authorized approver(s) and date | **Unconfirmed** |

Record final approval in an appropriate maintained repository review/issue or signed project document. Do not publish personal signatures, private emails or contractual details without consent.

## Next release sequence

1. Record rights-holder and MIT terms approval.
2. Add the real license and bounded third-party notices; complete package/source inventory and Buildroot pin.
3. Re-run a clean CI workflow against the *new commit*.
4. Recruit and document one non-maintainer independent reproduction (issue #6).
5. Tag only the approved and validated commit, create a compliant immutable archive/Zenodo version DOI, and update journal software metadata.

Until then, leave [release issue #2](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/2) open and the RC PR as draft.
