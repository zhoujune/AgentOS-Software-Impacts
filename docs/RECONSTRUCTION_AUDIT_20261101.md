# Source reconstruction audit — 2026-11-01

## Baseline identity

- Repository: [zhoujune/AgentOS](https://github.com/zhoujune/AgentOS)
- Immutable upstream commit: `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`
- Upstream Git tree SHA: `a19299570fa796795c8e0cf787f29c41718ae960`
- Commit message: `Fix Streamlit model and endpoint state persistence`
- The recursive tree contains 340 entries, including 279 blobs (239,002,958 bytes); GitHub reports the tree as complete (`truncated=false`).

The source tree and blob hashes are captured in `benchmarks/provenance/upstream-tree-4147c7f.json`. The local comparison is captured in `benchmarks/provenance/source-blob-audit-4147c7f.json`.

## Exact blob comparison

Every one of the 279 upstream blob paths was present in the experimental server tree. After restoring file modes from the upstream tree:

| Status | Count |
| --- | ---: |
| Byte-identical upstream blobs | 248 |
| Content-different blobs | 31 |
| Missing upstream blobs | 0 |
| Mode-only mismatches | 0 |

The 31 content differences consist of:
- 21 generated `__pycache__/*.pyc` files. These are build/runtime cache artifacts and are not part of the source overlay.
- Ten tracked text/source/manifest files: `README.md`, `br2-external/board/agentos/x86_64/overlay/etc/autologin-agent.sh`, `br2-external/board/agentos/x86_64/overlay/home/agent/agent_main_loop.sh`, `br2-external/board/agentos/x86_64/overlay/home/agent/agent_runner.py`, `docs/ARTIFACT.md`, `docs/DESIGN.md`, `docs/THREAT_MODEL.md`, `judge/run_vtrm_eval.py`, `llm_proxy.py`, and `manifests/manifest.lock`. The four documentation/manifest files were empty in the upstream baseline and are filled by this overlay.

The server-side staging copy had originally lost the executable bit on 29 upstream executable files. Those mode bits were restored to match the immutable upstream tree. This did not change file contents or either VM image.

## Reproducible overlay

The public reconstruction consists of three verified patches (ten tracked modifications plus eight added evaluator/replay/test files), followed by four standalone builder/runner files under `overlay-files/`. See `patches/README.md` and both checksum manifests for exact component identities.

The split source bundle also adds a reproducible post-build Eval image builder. It injects the updated guest startup/agent scripts into a copy of the clean rootfs, keeps the workspace parent root-owned, and makes only the two benign fixture roots agent-writable. A six-task unprivileged QEMU run passed all six cases with this image; a post-boot inode probe confirmed the workspace parent and failcases remained root-owned. Six new regression tests check that the task corpus stays within this permission boundary.

The split source bundle deliberately excludes:
- The 21 changed Python bytecode caches and all other generated caches.
- The separate `judge/run_vtrm_eval_local_model.py` experiment and the local-model bootstrap patch, which are documented in [PR #3](https://github.com/zhoujune/AgentOS-Software-Impacts/pull/3).
- The 1,255 files under the server's `runtime/` directory, which are generated VM copies, raw reports, logs, and experiment outputs rather than a source release.

### Patch validation

The six modified non-empty upstream blobs were retrieved by their exact Git blob SHA from the pinned commit; the four empty placeholders were verified against the empty-blob SHA. A pristine test tree was created with original executable modes. The earlier complete server-side patch passed `git apply --check` and recreated all 22 files in its original experiment tree. The new public split-source revision independently passed a clean GitHub-hosted reconstruction and QEMU regression, but is not claimed byte-identical to that historical patch.

**Historical blocker (resolved by split-source reconstruction on 2026-11-01):** The public patch upload was initially truncated to 131,072 bytes instead of the verified server-side 145,745 bytes; see [issue #4](https://github.com/zhoujune/AgentOS-Software-Impacts/issues/4). The public source is now delivered as three verified patches and four individually pinned files. This is a verified *server-side* patch-application test, **not** a full clone-and-rebuild on the server. Direct `git ls-remote https://github.com/zhoujune/AgentOS.git` from the server fails with a connection reset. The included `scripts/reconstruct_agentos_overlay.sh` is the user-side full-clone procedure: it clones the public repository, checks out the pinned commit, applies the patch, and runs the Python unit tests. The clean clone and full QEMU workflow passed on a GitHub-hosted Ubuntu runner.

Original unpublished server patch SHA-256 (historical, not the public release identity):

`dcae1c4abdf821dd357d0004ea0b4adf9376cac16879e21c1746d35c9f82488d`

## License evidence and remaining legal action

The official ASE 2026 conference artifact page describes the AgentOS source code and documentation as publicly available under the **MIT License**: [ASE 2026 paper/artifact page](https://conf.researchr.org/details/ase-2026/ase-2026-tools-and-data-sets/45/Introducing-Safe-LLM-Agent-Execution-via-Typed-Tool-Mediation-and-World-Effect-Evalua).

However, the pinned upstream GitHub tree contains no root-level `LICENSE` file. The license statement is therefore supported by the official conference page, but the software release still needs an explicit standard MIT license text and a verified copyright notice from the rights holder(s). Do not invent or infer a different copyright owner or apply this license to third-party dependencies, Buildroot, QEMU, model weights, or other separately licensed materials.

## Packaging gaps that remain

- `docs/ARTIFACT.md`, `docs/DESIGN.md`, `docs/THREAT_MODEL.md`, and `manifests/manifest.lock` are empty in the upstream baseline.
- The README says the full `buildroot-2026.02` source checkout is external and must be obtained separately; it is not vendored.
- The repository has no top-level `requirements.txt` or `pyproject.toml`; only `packages/requirements-streamlit-ui.txt` is present.
- The six-task offline cassette is a deterministic software regression fixture, not a substitute for the full 24-benign/48-adversarial ASE evaluation.
- The source patch and this companion repository are review materials, not a tagged release or permanent reproducibility capsule.

## Reconstruct locally

From this companion repository, run:

```bash
bash scripts/reconstruct_agentos_overlay.sh /path/to/AgentOS-reconstructed
```

This clones the exact upstream commit and applies the overlay in a new directory. It refuses to overwrite an existing destination. Set `RUN_QEMU_SMOKE=1` to additionally run the offline QEMU smoke test (requires a Linux host with the documented QEMU and filesystem utilities).

The resulting checkout is a reconstruction of the current experimental overlay. It should still undergo source review, dependency locking, license-file completion, clean-host reproduction, and a tagged release before journal submission.
