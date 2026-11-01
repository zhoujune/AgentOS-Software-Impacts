# AgentOS source reconstruction

Baseline: `zhoujune/AgentOS` commit `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c`.

The earlier oversized patch was split into:
- `0001-agentos-offline-replay-overlay.patch`: ten original tracked source/documentation changes;
- `0002-offline-aggregation-and-fixtures.patch`: offline reporting and cassette fixtures;
- `0003-offline-tests-and-validation.patch`: deterministic replay and policy regression tests;
- `../overlay-files/`: four individually versioned guest-image builder and test-runner scripts.

`expected_git_blobs.txt` and `expected_sha256.txt` pin all seven inputs. `../scripts/verify_split_sources.py` checks them before `../scripts/reconstruct_agentos_overlay.sh` clones and patches the upstream repository.

[Clean GitHub Actions reconstruction and QEMU validation](https://github.com/zhoujune/AgentOS-Software-Impacts/actions/runs/41271397622) passed: 17 unit tests, one smoke task, six baseline tasks, and the two-trace new-task demonstration.

This candidate is a deliberate split-source revision, **not** a byte-for-byte recovery of the unpublished server patch or a tagged release. No generated Python bytecode, VM images, runtime logs, Buildroot dependencies, model weights, or separately licensed assets are included.
