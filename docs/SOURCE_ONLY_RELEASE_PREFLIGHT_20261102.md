# AgentOS-RK source-only release preflight — 2026-11-02

**Decision: HOLD the versioned release and external adoption claims pending third-party provenance/rights review.**
This is a technical and documentation preflight, not legal clearance, a completed source release, or independent reproduction.

## Reviewed artifact and evidence

- Integration candidate: [draft PR #12](https://github.com/zhoujune/AgentOS-Software-Impacts/pull/12), branch `release-candidate/agentos-v0.1.0-prelicense`, observed HEAD `efa34fd548ca5e93082d591d0e3e8f5f5ecaf4d5`.
- Public candidate tree: **104 Git blobs** at this commit. A path/extension inventory found **no obvious bundled guest images, model weights, JARs, or conventional executable archives**. This is an extension-based inventory only; it does not establish a legal entitlement to redistribute every file, nor does it classify content inside patches.
- First-party `LICENSE`: MIT, `Copyright (c) 2026 Jun Zhou`; third-party and contributor-owned materials require a separate rights/provenance review.
- Automated GitHub Actions technical reproduction **passed at the observed HEAD**, including [RC technical reproduction run 41382398911](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41382398911). Other source/fixture check workflows also reported success. Automated CI is not an external-researcher usability study.
- The **revised OSP Word manuscript** currently identifies exact source commit `3b69c107da46881e397f95e8305d57a3d2101822`. This commit has its **own passing** [RC technical reproduction run 41379755425](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41379755425). It is therefore a valid tested snapshot, but it is **six commits behind** the observed branch HEAD. The intervening changes affect manuscript/CRediT/figure files, not the reproducibility runtime. The final article should cite the frozen release commit and its exact-version CI evidence, not silently mix versions.
- No published GitHub Release was found at the time of this review. A `release-candidate` branch is not a release tag.

## Blocking preflight checks

| Gate | Current finding | Required completion evidence |
| --- | --- | --- |
| First-party license | MIT `LICENSE` exists | Preserve the authoritative license and confirm rights for all first-party source contributions |
| Third-party / source-only scope | No obvious binary payload in candidate tree; material is still reconstructed from upstream | Review patch contents, third-party notices, vendored/JAR provenance and fixture/data ownership; record which files can enter a source-only archive |
| Dependency provenance | **No `manifests/manifest.lock` in the journal branch** at the observed HEAD, despite an older release-gates description referring to a partial lock | Produce an accurate dependency/source-provenance inventory from actual build inputs; identify Buildroot commit/config, target packages and their licenses as available; explicitly mark unresolved versions instead of inventing them |
| Binary redistribution | Not reviewed to completion | **Exclude** QEMU guest rootfs/kernel images, model weights and other non-cleared binaries from any archive; if ever distributed, prepare corresponding notices/source obligations first |
| Final fixed source version | HEAD is a draft PR; no published release | Choose reviewed commit; create a versioned tag and source-only archive only **after** applicable rights and provenance checks; verify archive file list and hashes |
| CI at released SHA | Latest observed branch CI passes | Re-run/confirm the exact released commit; link the passed workflow and reproduction summary |
| Independent usability | No external participant report | After clearance, use [reviewer quickstart](INDEPENDENT_REVIEWER_QUICKSTART.md) and [full protocol](INDEPENDENT_REPRODUCTION_PROTOCOL.md); retain first attempt, failures, elapsed time, exact SHA and redacted machine-readable evidence; independently authored new task is desirable |
| OSP metadata | C1/C2 cite tested historical commit; C3 describes no separate capsule | After release, update C1, C2, C8 and related references to exact fixed artifact; use C3 only for an actual verifiable capsule or honestly state its absence |

## Recommended execution sequence

1. **Resolve file-level source-only distribution scope.** Start with [license/redistribution review](LICENSE_AND_REDISTRIBUTION_REVIEW.md) and the source tree of PR #12. Do not include kernel/rootfs/model binaries to make the capsule look more complete.
2. **Replace the inaccurate lockfile description**, and build a genuine provenance manifest if complete data can be recovered. A `manifest.lock` invented from assumptions is worse than a clearly documented gap.
3. **Approve an exact first-party source candidate** and obtain authorized rights signoff. Do not treat passing CI as legal clearance.
4. **Freeze and test** the approved version; inspect downloaded source archive, record Git tree/commit identity and hash, and publish a versioned release or permissible scholarly source archive.
5. **Run one actual non-maintainer trial** using only the released source and the public handoff instructions; report both successes and failure/friction. Internal GitHub Actions does not meet this standard.
6. **Synchronize the paper**: C1–C3/C8, release identity, documentation links, CI reference and impact claims. Preserve the distinction between prior ASE findings, new exploratory local-LLM runs and deterministic replay tests.

## Task-401 oracle consistency check

The checked fixture `examples/world-effect-reuse/task/401_world_effect_reuse.json` instructs the agent to **not write any other file**, but the encoded success predicate requires the target file/content and specifies the broader `allowed_change_prefixes: ["/workspace"]`. That field does not, by itself, establish that no other workspace path was changed. The current revised OSP text correctly claims target-effect verification and forbidden `/protected` and `/secrets` changes; avoid claiming that the **no-other-file** instruction is independently enforced unless a file-specific effect oracle is added and tested.

## Explicit boundaries

- This preflight does **not** assert that third-party licenses are satisfied, that `v0.1.0` has been published, or that a capsule DOI exists.
- It does **not** assert that the 216 live-model evaluations or 90 memory-sweep cases were independently reproduced.
- The current public exact-commit test evidence supports the article's description of **technical reproducibility of the selected replay suite**, not software adoption by external researchers.

Tracked follow-ups: [release issue #2](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/2), [independent reproduction issue #6](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/6).
