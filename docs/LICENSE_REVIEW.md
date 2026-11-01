# License and attribution review — release blocker

**Status: NOT CLEARED.** This file is a checklist, **not** a license or authorization to redistribute code or binary images.

## Verified facts

- The published ASE 2026 description of AgentOS states that the original source is MIT licensed. The inspected original `zhoujune/AgentOS` source tree and this journal companion do **not** contain a matching top-level `LICENSE` file.
- The journal candidate incorporates original AgentOS files, maintenance overlays, new benchmarks, example tasks, reports and documentation. The contributors/owners of every component have not yet been legally confirmed.
- A narrow replay-based clean-host demonstration does **not** require distributing VM binary images or model weights: the scripts reconstruct the source and use existing pinned inputs. Whether these artifacts may be repackaged for a permanent archive requires separate third-party analysis.
- QEMU, Linux, Buildroot packages, model weights and other upstream packages have their **own** licenses. A single MIT notice on our repository would not supersede those conditions.

## Human decisions required before final software release

1. **Copyright authority.** Identify all rights holders for the original AgentOS source and the new companion software. Confirm that the corresponding maintainer is authorized to license both, including changes by collaborators.
2. **License selection and sign-off.** Verify whether MIT is intended for the original source and new journal contributions. Obtain explicit approval from the relevant rights holders. If different components require different licensing, document their boundaries.
3. **Publish legal files.** Add a top-level `LICENSE` text, a truthful `NOTICE` and a third-party attributions/dependency list, all reviewed by the copyright owner(s). Do not manufacture copyright years or omit applicable contributors.
4. **Guest and model assets.** Verify redistribution terms for any kernel/rootfs, Buildroot packages, datasets, public model snapshots and optional media **before** uploading them to a release archive. Default release candidate excludes these assets.
5. **Document exact approved scope.** Make clear whether the software grant applies to benchmark definitions/results and examples, not merely the runtime code.

## Suggested decision form for the maintainer

- Confirmed original AgentOS copyright owner(s): `[pending]`
- Confirmed journal-overlay copyright owner(s): `[pending]`
- Right-holder authorization to publish under MIT (yes/no): `[pending]`
- Separate benchmark/data license, if any: `[pending]`
- Third-party source/binary redistribution reviewed (yes/no): `[pending]`
- Public support/corresponding author contact approved: `[pending]`

## What remains possible before approval

It is appropriate to test, review, and hash the public repository's **existing** draft content and prepare an untagged RC branch. However, the candidate must **not** claim that all integrated software is licensed, fully redistributable, or permanently archived. Independent researchers should only be invited to a release trial once licensing is sufficiently clear for their intended use.

After clearance, update the code metadata C4 in the Software Impacts manuscript and create a pinned release identifier/immutable archive *from the exact approved commit*.
