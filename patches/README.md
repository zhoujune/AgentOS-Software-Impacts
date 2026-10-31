# AgentOS source overlay

The pinned upstream baseline is `zhoujune/AgentOS` commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`.

- `0001-agentos-offline-replay-overlay.patch`: ten tracked source/doc/manifest modifications and twelve new replay/benchmark/image-policy files.
- `../scripts/reconstruct_agentos_overlay.sh`: clone the pinned upstream source, apply the patch, and run the unit tests.
- `../docs/RECONSTRUCTION_AUDIT_20261101.md`: blob-level provenance, validation method, licensing evidence, and remaining release gaps.

The patch excludes generated Python bytecode, VM images, runtime reports, and the separate local-model experiment. It is a reviewable source delta, not a release tag.
