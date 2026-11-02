# Source identity and release-readiness audit

Audit date: 2026-10-31.

## Public upstream

Original project: [zhoujune/AgentOS](https://github.com/zhoujune/AgentOS). Its `main` tip observed through the GitHub connector was `4147c7f780ccb59b83f3dba8da5f19e73a1d1a8c` (commit title: "Fix Streamlit model and endpoint state persistence"). This is an **upstream reference**, not a reconstructed commit for the server working tree.

## Experimental source tree

`/workspace/agentos-journal/repo/AgentOS-main/` has no `.git` metadata. The source inventory is in `runtime/offline-repeated/20261029-software-impacts-prep/selected_source_manifest.json`; SHA-256 inventories are not a substitute for verified Git history.

Comparisons using `git hash-object` on the experimental tree and GitHub blob SHA values from upstream `main`:

| Path | Status vs upstream |
| --- | --- |
| `streamlit_app.py` | identical Git blob SHA (`c4aa1358dda45d46cb2666d44e8c644f47348086`) |
| `README.md` | changed |
| `llm_proxy.py` | changed |
| `judge/run_vtrm_eval.py` | changed |
| `br2-external/board/agentos/x86_64/overlay/home/agent/agent_main_loop.sh` | changed |
| `br2-external/board/agentos/x86_64/overlay/home/agent/agent_runner.py` | changed |
| `br2-external/board/agentos/x86_64/overlay/etc/autologin-agent.sh` | changed |
| `judge/validate_offline_suite.py` | not present at the inspected upstream path |
| `judge/aggregate_repeated_benchmark.py` | not present at the inspected upstream path |
| `scripts/test/run_offline_repeated_benchmark.sh` | not present at the inspected upstream path |

The new guest image was built from a permissions-fixed experiment and replaces only `agent_main_loop.sh` and `agent_runner.py` with polling-configurable versions. A read-only `debugfs` comparison of the two images showed only polling-related source edits in these two files.

## Packaging blockers

- Neither inspected repository tree has a top-level `LICENSE` file, despite the ASE paper describing the original software as MIT-licensed. Confirm the copyright-holder(s), grant and exact license text before publishing a release. Do not infer the right to relicense from the paper alone.
- In the experimental tree, `docs/ARTIFACT.md`, `docs/DESIGN.md`, `docs/THREAT_MODEL.md`, and `manifests/manifest.lock` are zero-byte placeholders.
- The experimental source tree has not been reconciled against a reproducible upstream Git checkout. A server-side `git ls-remote` over HTTPS failed because its outbound connection was reset; the GitHub connector could inspect upstream files independently.
- The available offline replay contains 13 responses for six selected tasks; it does not cover all 72 task definitions or live-model behavior.

## Release procedure (not yet completed)

1. Acquire a clean upstream checkout or verified source archive at a recorded commit.
2. Apply the experiment-specific improvements as reviewed patches, with working tests and committed changelogs.
3. Restore explicit licensing and documentation, record kernel/QEMU/Buildroot/dependency versions and platform constraints.
4. Create minimal automated reproducibility instructions, verify hashes and security regression tests, and prepare redistributable release artifacts.
5. Tag a new version and archive its exact source and any permitted large artifacts, then update software metadata for the journal manuscript.

The separate journal repository is a staging location; this audit does **not** certify it as a release.
