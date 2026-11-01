# Release candidate v0.1.0-rc.1 — source and reproduction checklist

**Status: UNTAGGED, NOT LICENSE-CLEARED, NOT A FINAL SOFTWARE RELEASE.** This branch consolidates otherwise separate draft workstreams to make review and automated reproducibility possible. Do **not** treat the branch name as a Git tag, an immutable capsule identifier, or a license grant.

## Software scope

This source candidate includes:

- Reconstructable AgentOS based on upstream commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`, plus **three patches and four separately pinned files**. `scripts/verify_split_sources.py` verifies seven Git blob IDs and SHA-256 values before reconstruction.
- Six deterministic CPU-only representative replay cases, with three authorized workspace operations and three explicit DB policy denials.
- The independently observable world-effect reuse demonstration: one real authorized write and one false completion claim, each validated against host state.
- WEJBench v0.1: task manifest, replay fixtures, local-model runner and sanitized historical evaluation results, **not** model weights.
- A separate constrained-memory study: **90/90** replay task outcomes passed across configured guest RAM of 128–512 MiB, with the host memory and QEMU-TCG limitations clearly documented.
- An abstract TLA+ formal model in the reconstructed upstream code; **no end-to-end verified implementation** is claimed.

The candidate deliberately **does not ship raw private LLM outputs, API tokens, guest snapshots, large images, model checkpoints, or private server files**. Model serving requires separate user-provided checkpoints and appropriate licenses.

## One-checkout automated reproduction

On a **fresh Ubuntu 24.04 x86_64 Linux machine** with public GitHub access, Python 3.12, Git, QEMU x86_64 and e2fsprogs:

```bash
sudo apt-get update
sudo apt-get install -y git python3 qemu-system-x86 e2fsprogs

git clone --branch release-candidate/v0.1.0-rc1 \
  https://github.com/zhoujune/AgentOS-Software-Impacts.git agentos-rc
cd agentos-rc
python3 scripts/verify_split_sources.py

# The destination MUST NOT already exist. The script writes only disposable outputs.
bash scripts/run_public_reproduction.sh "$PWD/../agentos-rc-reproduction"
```

The helper clones the original upstream pinned commit into a new directory, applies integrity-checked overlays, runs source unit tests, executes six CPU-only replay tasks, runs both positive and negative world-effect controls, and writes a fail-closed `reproduction_summary.json` with hashes. Neither LLM access nor an API key is required. The negative trace is expected to *fail task completion*; a successful helper verifies that this false-success claim is not accepted by the host judge.

The clean-host GitHub Actions job uses the **same one-checkout public source**, rather than fetching the demo from a separate internal branch. This is automated reproduction only.

## Formal metadata and reproducibility limits

| Field | Candidate | Gap |
| --- | --- | --- |
| Version | `0.1.0-rc.1` **candidate label** | Needs signed-off immutable Git tag and actual archive |
| Source | Upstream pinned commit + seven checksummed overlays | Full source release review, Buildroot transitive pinning |
| Build | Ubuntu 24.04 x86_64 / QEMU 8.2.2 / Python 3.12 / e2fsprogs 1.47.0 observed | Not independently rebuild-verified from exact Buildroot commit |
| Licenses | **Pending** | Verify copyright holders and right to license upstream and journal overlays; publish actual LICENSE/NOTICE |
| Data | Committed sanitized replay and analysis summaries | Private raw model/VM artifacts not public; do not claim full reanalysis |
| Independent use | Protocol and fresh-clone CI implemented | Real non-maintainer, separate host and report still required |
| DOI / capsule | Existing *prior ASE* Zenodo archive is not a new journal version | New versioned source archive + immutable DOI required |
| Support | Existing project issue tracker | Corresponding author/support address must be confirmed |

The reconstructed guest image includes components governed by their own upstream licenses. An MIT statement in the prior ASE paper cannot substitute for verifying the actual copyright holders or their redistribution permissions. **Do not publish a final `LICENSE` under somebody else's authority.**

No measured deployment on ARM, actual edge hardware or power-constrained devices is claimed. The 128 MiB result is the **configured guest RAM limit**; the full QEMU evaluation stack on the tested host consumed substantially more process memory. TCG translation-cache tuning is a separately recorded single-task experiment.

## Final release gates

1. **Legal**: copyright holders approve the licensing terms for both the original AgentOS repository and this companion; add `LICENSE`, `NOTICE` and third-party notices as needed.
2. **Dependencies**: audit and pin the required source and Buildroot revisions, system packages, Python and optional model-serving dependencies; publish limitations where exact pins are unavailable.
3. **Reproduction**: clean-host CI must pass against the exact commit to tag. A genuinely independent person must complete the published protocol on a separate machine and provide redacted, attributable evidence; GitHub Actions is **not** a substitute.
4. **Release**: review all public files for secrets or proprietary assets; create immutable tag and source archive *after* validation; obtain and verify a separate archival DOI/record for this release.
5. **Publication**: fill C1–C9 metadata, confirm authors and support contact, and cite the prior ASE paper separately. The original ASE data are not republished as a new result.

### Source branches incorporated

This branch is based on `work/constrained-memory-footprint-20261101`, which builds upon `work/controlled-polling-benchmark`. World-effect reuse and WEJBench v0.1 have been copied into this candidate so the **complete public source and fixtures can be checked from one Git checkout**. The original drafts remain open for review.

**Candidate decision:** ready for automated integration testing and license review. Not yet ready for redistribution claims, formal citation as a released version, or independent-use completion claims.
