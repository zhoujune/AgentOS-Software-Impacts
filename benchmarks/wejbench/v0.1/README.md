# AgentOS-WEJ-Bench v0.1

**Research benchmark candidate — an internal 216-episode live-LLM study completed on 2026-11-01. The project is not a tagged software release or independently reproduced study.**

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

The private PPU-host study used the following locally installed models. Local checkpoint files were SHA-256-fingerprinted; exact upstream model revisions remain unverified:

| Profile | Proposed model family and checkpoint |
| --- | --- |
| llama3-8b | meta-llama/Meta-Llama-3-8B-Instruct |
| qwen3-14b | Qwen/Qwen3-14B (non-thinking adapter) |
| mistral7b-v03 | mistralai/Mistral-7B-Instruct-v0.3 |

Use the full OpenAI-compatible HTTP chat-completions endpoint provided by a real model service, e.g. http://127.0.0.1:8000/v1/chat/completions. Confirm the served checkpoint, exact revision, tokenizer and license. The Meta Llama 3 license may require authorized access. Qwen3-14B substituted for the initially proposed Qwen2.5-7B. Verify licenses, upstream revisions and tokenizer versions before publishing final model provenance. Model weights and credentials are not part of this journal artifact.

### Start one local PPU model and run a two-task pilot

On the **PPU host**, start the model in the foreground. For the previously verified local Llama 3 8B model directory, the command is:

~~~bash
bash benchmarks/wejbench/v0.1/serve_local_model.sh \
  /models/Llama3-8B-Instruct llama3-8b-local 8017
~~~

This uses the host's already installed PPU-enabled vLLM. The command serves the **existing local model weights**, binds only to 127.0.0.1 and does not download weights. Stop it with Ctrl-C. The checkpoint directory, license, PPU allocation, and model ID must be verified on the actual host; the internal live study later connected successfully to the PPU host.

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

For Qwen or Mistral, first obtain and verify the correct model files and server runtime for the chosen PPU. Serve them locally using explicit model IDs such as `qwen3-14b-local` or `mistral7b-v03-local` and set `AGENTOS_BENCH_QWEN_ENDPOINT`, `AGENTOS_BENCH_QWEN_TOKEN`, `AGENTOS_BENCH_QWEN_SERVED_ID` or the corresponding `AGENTOS_BENCH_MISTRAL_*` environment variables. You can serve the three models **sequentially on a single accelerator**, freeing resources between models, but record the sequential study design.

The local preflight can also run separately:

~~~bash
python3 benchmarks/wejbench/v0.1/preflight_local.py \
  --models llama3-8b \
  --output "$PWD/runtime/llama-local-preflight.json"
~~~

Do not mistake the preflight greeting for a WEJ task result. The two-case pilot is complete only when `episodes.json` reports confirmed local API calls and the host judge's outcomes. Raw model-generated response cassettes and VM logs remain **local only** and may include sensitive task data.

For the full study, either serve all three models on separate PPUs and execute `run_live.py --execute --models llama3-8b qwen3-14b mistral7b-v03 --repetitions 3` with a new output directory (the 2026-11-01 internal design), or serve models sequentially with separate outputs while documenting a changed run design. Three model profiles × 24 tasks × 3 repetitions is 216 episodes. Qwen3 requires the separately documented non-thinking adapter used in this study. An execution on a remote hosted API endpoint is intentionally rejected. Do not use `--max-episodes` and then report a full study.

The local dummy token is for a locally configured **unauthenticated** endpoint only; an authenticated loopback service should use its actual token via the environment. Never commit tokens, model transcripts, VM images, or unreviewed guest audit logs.

Run a model analysis only after episodes.json exists:

~~~bash
python3 benchmarks/wejbench/v0.1/summarize.py --episodes ./runtime/wejbench-llama-pilot/episodes.json --output-dir ./runtime/wejbench-llama-pilot/analysis
~~~

No unsupported-success claim, absent forbidden operation, or skipped task can be counted as successful policy enforcement. Security denominators are conditioned on observed attempted operations. Model repetitions use a deterministic order randomization seed, **not independent decoding seeds**; temperature is fixed at zero. Do not treat 216 episodes as 216 independent task samples.

## Completed internal local-LLM evaluation (2026-11-01)

The full **216/216-episode** evaluation ran on a PPU server with 24 tasks, three local model families, and three randomized repetitions per task/model. All 216 episodes produced host-evaluator reports and passed their configured WEJ world-integrity and safety checks; this is *not* a guarantee of security outside the modeled tool/effect channels.

Under the **unchanged primary task-completion oracle**, completion-eligible outcomes were Qwen3-14B **37/45**, Llama-3-8B **22/45**, and Mistral-7B-v0.3 **16/45**, for **75/135** total. The other 81 episodes were should-fail tasks without ordinary completion checks. A separately labeled semantic-JSON sensitivity identifies eight false-negative strict substring matches (tasks 312 and 402) without overwriting the primary verdicts, yielding 83/135 under that alternate metric.

Strict database-policy tasks (115 and 404–406) generated direct-denial evidence in **30/36** episodes; legacy protected-path tasks (107 and 121) generated **18/18 approval-required** outcomes, **not** strict hard denials. A model not attempting a forbidden action does not demonstrate policy enforcement.

The audit records **1,018** local inference calls and **zero reported model HTTP-error episodes**. Exact upstream checkpoint revisions are not established; however, local model files and source images have been fingerprinted. Mistral and Llama produced more non-single-JSON tool messages than Qwen under this configuration. These are descriptive single-host data on repeated tasks, not general model rankings.

**Sanitized evidence and code (no private guest disks, model transcripts, credentials or raw snapshots):**

- [Audited summary (human readable)](results/20261101-live-216-audit-summary.md)
- [Audited summary and per-task counts (JSON)](results/20261101-live-216-audit-summary.json)
- [216 episode metadata rows (CSV)](results/20261101-live-216-audit-episodes.csv)
- [Read-only re-audit program](audit_live_matrix.py) and [five regression tests](test_audit_live_matrix.py)

Run the audit on a private, already-completed study with retained case reports and snapshots:

~~~bash
python3 benchmarks/wejbench/v0.1/audit_live_matrix.py \
  --episodes /path/to/private/study/experiment/episodes.json \
  --provenance /path/to/private/study/provenance.json \
  --out /new/sanitized/report/directory
~~~

A study that lacks all 216 original cases or has mismatched audit events fails closed. The private evidence is not included in this publication branch; independent reproduction, source tagging, licensing and version-pinned model provenance remain open.

## Reproducibility and limitations

All deterministic replay examples are hand-authored; they test the software and its host world-effect oracles, **not actual language-model behavior**. A model evaluation must report checkpoint revision, inference engine, hardware, task budgets, raw request validity, task completion, safety and attempted versus denied mutations. The 72 original ASE cases and their results remain prior work. A user outside the project has not yet completed an independent reproducibility study.

Before journal submission, fix and archive the full license/dependency/release metadata and obtain external-user feedback. See the journal companion repository release and independent-reproduction issues.
