# AgentOS-RK: Zenodo archival checklist (draft, **not published**)

**Purpose.** Make the *reviewed, versioned, source-only* AgentOS-RK snapshot citable with a Zenodo DOI before finalizing the Software Impacts OSP. **Zenodo specifically is not mandated by the supplied OSP template**. Public code is mandatory; C2 requests a permanent code-version link, whereas C3 requests a reproducible capsule link. A Zenodo source-code archive improves persistence and citation, but does not automatically constitute an executable reproducibility capsule.

## Current gate

At preparation time, the release candidate remains in draft [PR #12](https://github.com/zhoujune/AgentOS-Software-Impacts/pull/12). The legal/redistribution/provenance inventory is not complete, and no final GitHub release has been published. An initial Zenodo deposit (v1, review-branch ZIP) is documented below. See [release gates](RELEASE_CANDIDATE_GATES.md) and [source-only preflight PR #14](https://github.com/zhoujune/AgentOS-Software-Impacts/pull/14). Keep all first-party copyright and third-party rights checks independent of the technical CI status.

## Update after first published Zenodo deposit (2026-11-02)

The account owner has published [Zenodo record 23876102](https://zenodo.org/records/23876102), **version DOI [10.5281/zenodo.23876102](https://doi.org/10.5281/zenodo.23876102)**, all-versions DOI [10.5281/zenodo.23876101](https://doi.org/10.5281/zenodo.23876101). The record displays **v1**, names **Zhou, Jun** as creator, and provides a **259.7 KB ZIP named `AgentOS-Software-Impacts-review-zenodo-metadata-20261102.zip`**.

**Do not yet cite this deposited ZIP as the final AgentOS-RK v0.1.0 software release.** The filename refers to the still-open review branch, while the intended reviewed release/tag remains unpublished. The Zenodo page displays **CC BY 4.0**, whereas the repository states **MIT for first-party source**. Inspect the ZIP's exact contents and rights first; correct the published record's editable license metadata if appropriate, without falsely applying MIT to separately licensed components.

For the **final** v0.1.0 software article: complete release signoff, publish the exact reviewed code/tag, and create a **new Zenodo version** containing the finalized source. Cite **that version-specific DOI** and Git SHA in OSP C1/C2 and the software reference. Use C3 for a true computational capsule if one is provided; a Zenodo source archive alone is not necessarily a runnable capsule. Published Zenodo files cannot ordinarily be replaced in place: updating software bytes needs a new version rather than relabeling the old ZIP.

## Proposed method: Zenodo's GitHub integration

1. **Before publication:** confirm that the exact release contents are lawful to redistribute. Prefer source, original task definitions, tests, scripts, documentation and sanitized result summaries. Do not include unreviewed Linux/Buildroot guest images, model weights, third-party JARs, raw private logs, credentials or datasets without distribution rights. Review source patches/fixtures for copied third-party material rather than relying only on filename extensions.
2. Confirm final software creators in `CITATION.cff`. The draft lists **Jun Zhou**, the named first-party copyright holder, as the software creator. The manuscript's other coauthor **Li Yuan** is presently documented for *manuscript review and editing*; do not automatically infer software authorship from article authorship. Add anyone who materially created/maintained the released software after their contribution is verified.
3. After the legal inventory, merge the reviewed code and freeze one exact release commit on the intended public release branch. Verify source checksums and full replay CI at **that exact SHA**, not a previous branch head.
4. Sign into [Zenodo](https://zenodo.org/) with the account designated to administer the project, connect GitHub, open [Zenodo GitHub settings](https://zenodo.org/account/settings/github/), synchronize repositories, and **enable `zhoujune/AgentOS-Software-Impacts` before publishing the GitHub release**. Zenodo's integration archives subsequent releases and mints a DOI.
5. Create and **publish** the final reviewed GitHub release (e.g. tag `v0.1.0`) only after step 4 and authorized approval. Do not create a release just to test the connection; use Zenodo's [sandbox](https://sandbox.zenodo.org/) for non-publication tests if needed.
6. Inspect the Zenodo software record: title, creator(s), version, MIT first-party licensing scope, abstract, exact Git release identity, included files, resulting **version-specific DOI**, and Software Heritage archival status. Record the DOI **only after Zenodo issues it**. Avoid inventing a DOI from an unpublished draft.
7. Update the article with *the actual verified artifacts*: C1 = software version and exact Git SHA; C2 = release/tag or immutable revision; C3 = executable capsule link if an actual capsule is provided, otherwise accurately describe the source archive and the absence of a self-contained capsule; C8 = version-pinned README. Add a software-reference entry with the version-specific Zenodo DOI. Do not place a source-archive DOI in C3 as though it independently executes the experiments.
8. After these checks, invite a **non-maintainer** to run the documented reproduction from the frozen public release, with a first-attempt log and preferably a reviewer-authored additional task. The author's GitHub Actions workflow is technical CI, not evidence of independent user adoption.

## Official instructions

- Zenodo: [enable a GitHub repository](https://help.zenodo.org/docs/github/enable-repository/).
- Zenodo: [archive a GitHub release](https://help.zenodo.org/docs/github/archive-software/github-upload/).
- Zenodo: [CITATION.cff support](https://help.zenodo.org/docs/github/describe-software/citation-file/).
- GitHub: [archive and cite a repository with Zenodo](https://docs.github.com/en/repositories/archiving-a-github-repository/referencing-and-citing-content).
- Software Impacts: [official OSP template](https://legacyfileshare.elsevier.com/promis_misc/SIMPAC_Article_Template.pdf).

## Metadata note

The draft `CITATION.cff` intentionally has **no** `doi`, `version`, or `date-released` field: none should be asserted before publication. Adding a `.zenodo.json` file is unnecessary for basic software metadata; Zenodo currently prioritizes `.zenodo.json` over `CITATION.cff` when both exist. Maintain a single authoritative metadata source unless Zenodo-specific fields are genuinely required.

**Final v0.1.0 release decision: HOLD** until source distribution/provenance review and authorized approval are complete. The preliminary Zenodo v1 deposit already exists and must not be confused with the final release.
