# Local LLM pilot readiness — 2026-11-01

**Status: prepared; live three-model benchmark not executed.**

The intended private PPU host at 172.30.60.211 repeatedly timed out on SSH checks. The current fallback execution container has no PPU/GPU device and no installed model weights. Therefore no local model could be loaded or queried in the current session. Do not convert this into a model-performance result.

## Previously verified feasibility (separate experiment)

On 2026-10-31, draft PR #3 documented one PPU-ZW810E (96 GiB) with a PPU-enabled vLLM 0.20.1 build, the already-local directory /models/Llama3-8B-Instruct, and served model name llama3-8b-local. One benign and one restricted database task produced model responses and passed the relevant World Effect Judge safety/completion checks. Those results predate WEJ-Bench v0.1; they are not part of the new 216-episode study.

## Completed preparations

- 24 pinned benchmark tasks, including 12 newly designed world-effect cases.
- The new deterministic integration suite passed 12/12 cases in fresh QEMU on a GitHub-hosted runner. **This is hand-authored replay, not live LLM inference.**
- Three candidate model families are specified, but exact checkpoint revisions and installed files are unverified.
- prepare_local_checkout.py adds the previously required guest AGENT_MODEL forwarding to the reconstructed *candidate*, not the original AgentOS repository.
- preflight_local.py validates a loopback-only OpenAI-compatible model service, exact advertised model alias, and actual HTTP chat-completions generation. CI checks the API contract using a simulated local server; that unit test is **not a neural model**.
- run_local_pilot.sh runs a benign file-write and strict DB-denial task with one actual local model. It requires a live PPU-host endpoint, stores model-proxy traces locally, and verifies that the proxy made real API calls.
- serve_local_model.sh launches previously downloaded model weights through the installed PPU vLLM build, in the foreground on 127.0.0.1. It does not download weights or allocate an accelerator by itself.

## Next required verification

1. Restore SSH access to the PPU host; inspect model paths, available devices and processes before starting anything.
2. Revalidate the Llama-3-8B-Instruct checkpoint and the PPU vLLM executable. Start a local loopback service with the exact served ID.
3. Run preflight and the two-task live Llama pilot. Read per-case QEMU reports; do not count transport-only successes as valid tasks.
4. Install or confirm licensed Qwen2.5-7B-Instruct and Mistral-7B-Instruct-v0.3 local checkpoints with exact model revisions, tokenizer versions and weight hashes. Never assume they are installed.
5. Perform the two-task live pilot with each, then the balanced 24 × 3 × 3 study and independent output review.

Do not leave model services running after experiments. Original AgentOS, canonical guest image and journal main branch remain untouched. Reference: draft PR #7 and tracking issue #8.
