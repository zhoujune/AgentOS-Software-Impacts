# Independent reviewer one-page handoff — AgentOS

**HOLD: source licensing is not yet cleared. Do not use this as an external recruitment invitation until [release gates](RELEASE_CANDIDATE_GATES.md) are resolved.**

## What we would like you to test

Can a researcher unfamiliar with AgentOS use a public, pinned checkout to reproduce its six CPU-only replay cases and verify a deliberately incorrect agent completion claim using the host-side World Effect Judge? This tests software usability and reproducibility, **not live-LLM behavior, general security, or edge-device deployment**.

The test runs from a fresh Linux x86_64 host (preferably Ubuntu 24.04) with Git, Python 3, QEMU x86_64, `debugfs`, `e2fsck`, `sha256sum` and space for multiple disposable 60 MiB rootfs images. Model API accounts and accelerators are not required. A machine without `/dev/kvm` may run more slowly under TCG emulation.

## After approval: run once, without maintainer guidance

```bash
git clone --branch release-candidate/agentos-v0.1.0-prelicense \
  https://github.com/zhoujune/AgentOS-Software-Impacts.git agentos-rc
cd agentos-rc
git rev-parse HEAD
bash scripts/reproduce_release_candidate.sh "$PWD/../agentos-review-results"
cat ../agentos-review-results/reproduction_summary.json
```

Keep the initial attempt exactly as documented. If it fails, stop and record the first error, any missing tool, how long setup took, and whether you needed assistance. **Do not conceal failures or repeat until success without documenting the retries.**

If the script completes, verify that the JSON has `technical_reproduction_validation=PASS`, `baseline_task_count=6`, and `demo_trace_count=2`. The supplied positive trace must perform an authorized write; the supplied false-success trace must **not** produce the required file and must fail the completion oracle while passing replay and safety checks.

## Best additional evidence: create a different task

Design a *new* task with a new identifier and an expected filesystem effect. Use the existing task schema and judge without modifying VTRM. Record whether it works, whether docs were sufficient, and any limitations. This is distinct from running the author-supplied positive/false-success example.

## What to return

Only share the sanitized `reproduction_summary.json` and a short note with: pseudonymous reviewer ID, machine OS/architecture, Python/QEMU versions, exact repository SHA, setup duration, first error and retries, whether you needed maintainer help, baseline and demo outcome, and if applicable an independent new-task definition and result (review its contents before publishing).

Do **not** upload raw rootfs files, case snapshots, private console logs, model weights, credentials, API keys or personal identifiers. If an error log is essential, redact identifiers and secret content first.

**Success classification:** a completed GitHub Actions workflow is *automated technical reproduction*. Only a genuine non-maintainer's documented first-hand attempt qualifies as independent-user evidence, and only a truly new reviewer-designed task demonstrates independent extensibility.

Full method and reporting form: [independent reproduction protocol](INDEPENDENT_REPRODUCTION_PROTOCOL.md).
