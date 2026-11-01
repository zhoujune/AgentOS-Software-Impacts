# AgentOS clean-host verification (2026-11-01)

A GitHub-hosted Ubuntu 24.04 runner reconstructed upstream AgentOS commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c` from three separate patches and four standalone source files. The public reconstruction script verifies each input against recorded Git object IDs and SHA-256 digests.

**Results:** 17/17 unit tests, 1/1 QEMU smoke, and 6/6 representative offline tasks passed. The new workspace task passed when a real `fs.write` took place, with one successful VTRM audit event and two exact replay requests. A control trace claimed success but performed no write; the World Effect Judge correctly marked task completion as failed while safety, replay, and world integrity passed.

The [successful workflow](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41271397622), [raw JSON and Markdown reports](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41271397622/artifacts/13069671706), and [permanent result summary](https://github.com/zhoujune/AgentOS-Software-Impacts/blob/work/world-effect-reuse-demo/examples/world-effect-reuse/results/20261101-ci-summary.json) document the observation.

The first 128 KiB patch upload was incomplete; the split-source revision is a separately validated implementation, not a byte-identical recovery of the unpublished server patch. The canonical base image checksum remained unchanged. The generated disposable image is not claimed to be bit-for-bit reproducible.

**Limitations:** The examples use hand-authored replay responses, not a live LLM. The run was automated, not conducted by an independent researcher. License-file completion, full Buildroot locking, a tagged release, a permanent archive, and external-user reproduction remain outstanding.
