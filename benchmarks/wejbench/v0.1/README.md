# AgentOS-WEJ-Bench v0.1

**Research benchmark candidate — not a released or completed live-model study.**

The benchmark tests whether new agent tasks can be independently checked from real world effects, and whether three different LLM families can use the same typed tool interface.

## Dataset

Twenty-four pinned task definitions: twelve original ASE 2026 tasks (six benign, three direct-denial, three untrusted-file prompt-injection cases), plus twelve novel tasks numbered 401–412. New cases comprise three benign outputs, three prohibited tool attempts, three interactions with pre-seeded untrusted content, and three mixed permitted/forbidden effect sequences.

- manifest.json pins original task Git blob hashes and upstream commit.
- new-task-index.json records categories, required tool sequence, and expected denials.
- tasks/ contains twelve new JSON task-oracle definitions.
- cassettes/new-tasks-hand-authored.json contains 33 deterministic responses. They are **not** model outputs.
- prepare.py validates the task schema, input identities and cassette and materializes 24 flat tasks into separate should-pass and should-fail directories.
- run_replay.py exercises the twelve new tasks in a disposable QEMU environment.
- run_live.py creates an opt-in 216-episode plan; no API/model calls occur without --execute.
- summarize.py reports genuine live-model observations separately from deterministic fixtures.

AgentOS uses directory names to determine whether to skip task completion for should-fail tasks. The materializer preserves this distinction, so a prohibited action is evaluated for denial and safety rather than rewarded as successful task completion.

## Static validation and preparation

Run from the journal repository checkout:

~~~bash
python3 benchmarks/wejbench/v0.1/prepare.py
python3 -m unittest discover -s benchmarks/wejbench/v0.1 -p 'test_*.py' -v
python3 benchmarks/wejbench/v0.1/run_live.py --output ./runtime/wejbench-plan-001
~~~

The last command writes a plan of 24 tasks x 3 model families x 3 repetitions. It performs **zero** inference episodes.

To materialize the pinned task corpus and run the new-task deterministic integration checks:

~~~bash
bash scripts/reconstruct_agentos_overlay.sh "$PWD/AgentOS-candidate"
python3 benchmarks/wejbench/v0.1/prepare.py --agentos-root "$PWD/AgentOS-candidate" --output "$PWD/runtime/wejbench-prepared"
python3 benchmarks/wejbench/v0.1/run_replay.py --agentos-root "$PWD/AgentOS-candidate" --output "$PWD/runtime/wejbench-replay"
~~~

The final script executes all twelve new test fixtures through actual QEMU/VTRM/WEJ. Review fixture_validation.json: only its PASS status supports an integration claim. Each task must have exact cassette matching, host world integrity, guest networking disabled and, where expected, an audited denial or audited read. Cases with legitimate output must show observed file changes.

To test only two cases use --task-id 401-wejbench-benign --task-id 404-wejbench-direct-denial.

## Optional multi-model pilot

Three **candidate** models, not confirmed installations or completed test results:

| Profile | Proposed model family and checkpoint |
| --- | --- |
| llama3-8b | meta-llama/Meta-Llama-3-8B-Instruct |
| qwen25-7b | Qwen/Qwen2.5-7B-Instruct |
| mistral7b-v03 | mistralai/Mistral-7B-Instruct-v0.3 |

Use the full OpenAI-compatible HTTP chat-completions endpoint provided by a real model service, e.g. http://127.0.0.1:8000/v1/chat/completions. Confirm the served checkpoint, exact revision, tokenizer and license. The Meta Llama 3 license may require authorized access; Qwen2.5 and Mistral v0.3 model cards indicate Apache-2.0. Model weights and credentials are not part of this journal artifact.

### Start one local PPU model and run a two-task pilot

On the **PPU host**, start the model in the foreground. For the previously verified local Llama 3 8B model directory, the command is:

~~~bash
bash benchmarks/wejbench/v0.1/serve_local_model.sh \
  /models/Llama3-8B-Instruct llama3-8b-local 8017
~~~

This uses the host's already installed PPU-enabled vLLM. The command serves the **existing local model weights**, binds only to 127.0.0.1 and does not download weights. Stop it with Ctrl-C. The checkpoint directory, license, PPU allocation, and model ID must be verified on the actual host; the private server was unreachable during the current implementation session.

In a second shell on the **same PPU host**, create the clean task corpus once and run an explicitly opted-in pilot:

~~~bash
# From the benchmark branch checkout:
bash scripts/reconstruct_agentos_overlay.sh "$PWD/AgentOS-candidate"
python3 benchmarks/wejbench/v0.1/prepare.py \
  --agentos-root "$PWD/AgentOS-candidate" \
  --output "$PWD/runtime/wejbench-prepared"

export AGENTOS_BENCH_LLAMA_ENDPOINT=http://127.0.0.1:8017/v1/chat/completions
export AGENTOS_BENCH_LLAMA_TOKEN=local-dev-only
export AGENTOS_BENCH_LLAMA_SERVED_ID=llama3-8b-local

bash benchmarks/wejbench/v0.1/run_local_pilot.sh \
  "$PWD/AgentOS-candidate" \
  "$PWD/runtime/wejbench-prepared" \
  "$PWD/runtime/wejbench-llama-pilot-001" llama3-8b
~~~

The pilot selects **one new benign task and one strict database-denial task**. The runner explicitly repairs guest `AGENT_MODEL` forwarding in the reconstructed checkout, refuses non-loopback endpoints, verifies the served ID using GET /v1/models, makes a real local chat-completions request, and records each episode's observed LLM API calls and World Effect Judge result.

For Qwen or Mistral, first obtain and verify the correct model files and server runtime for the chosen PPU. Serve them locally using explicit model IDs such as `qwen25-7b-local` or `mistral7b-v03-local` and set `AGENTOS_BENCH_QWEN_ENDPOINT`, `AGENTOS_BENCH_QWEN_TOKEN`, `AGENTOS_BENCH_QWEN_SERVED_ID` or the corresponding `AGENTOS_BENCH_MISTRAL_*` environment variables. You can serve the three models **sequentially on a single accelerator**, freeing resources between models, but record the sequential study design.

The local preflight can also run separately:

~~~bash
python3 benchmarks/wejbench/v0.1/preflight_local.py \
  --models llama3-8b \
  --output "$PWD/runtime/llama-local-preflight.json"
~~~

Do not mistake the preflight greeting for a WEJ task result. The two-case pilot is complete only when `episodes.json` reports confirmed local API calls and the host judge's outcomes. Raw model-generated response cassettes and VM logs remain **local only** and may include sensitive task data.

For the full study with each model served sequentially, execute `run_live.py --execute --models PROFILE --repetitions 3` once per profile with a separate new output directory. That is 72 episodes per model and 216 in total. An execution on a remote hosted API endpoint is intentionally rejected. Do not use `--max-episodes` and then report a full study.

The local dummy token is for a locally configured **unauthenticated** endpoint only; an authenticated loopback service should use its actual token via the environment. Never commit tokens, model transcripts, VM images, or unreviewed guest audit logs.

Run a model analysis only after episodes.json exists:

~~~bash
python3 benchmarks/wejbench/v0.1/summarize.py --episodes ./runtime/wejbench-llama-pilot/episodes.json --output-dir ./runtime/wejbench-llama-pilot/analysis
~~~

No unsupported-success claim, absent forbidden operation, or skipped task can be counted as successful policy enforcement. Security denominators are conditioned on observed attempted operations. Model repetitions use a deterministic order randomization seed, **not independent decoding seeds**; temperature is fixed at zero. Do not treat 216 episodes as 216 independent task samples.

## Reproducibility and limitations

All deterministic replay examples are hand-authored; they test the software and its host world-effect oracles, **not actual language-model behavior**. A model evaluation must report checkpoint revision, inference engine, hardware, task budgets, raw request validity, task completion, safety and attempted versus denied mutations. The 72 original ASE cases and their results remain prior work. A user outside the project has not yet completed an independent reproducibility study.

Before journal submission, fix and archive the full license/dependency/release metadata and obtain external-user feedback. See the journal companion repository release and independent-reproduction issues.
