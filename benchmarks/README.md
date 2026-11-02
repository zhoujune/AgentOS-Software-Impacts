# Repeated offline benchmarking

This directory contains a **standard-library** Python tool that compares two already-validated AgentOS repeated benchmark reports. The tool fails closed if any repetition or required task is missing, the two cassettes differ, or key host settings differ.

## Run unit tests

```bash
python3 -m unittest discover -s benchmarks/tests -p 'test_*.py' -v
```

## Compare two reports

The source AgentOS evaluation checkout produces one `repeated_benchmark.json` per profile via `scripts/test/run_offline_repeated_benchmark.sh`. After both profiles complete:

```bash
python3 benchmarks/compare_guest_polling.py \
  --a /path/to/profile-A-legacy/repeated_benchmark.json \
  --b /path/to/profile-B-guest020/repeated_benchmark.json \
  --markdown /path/to/comparison.md \
  --json /path/to/comparison.json
```

The input report format is produced by the **experimental evaluator**, which is not yet committed here as a versioned software release. The compatibility reference is `docs/CONTROLLED_BENCHMARK_20261031.md`.

The comparator checks: all repetitions and case records present; all six expected task IDs in each run; `all_ok` and no errors; complete timing samples; identical cassette, kernel, host configuration and host polling settings; and different guest image hashes. It reports pooled case medians and p95 values plus per-repetition medians.

**Scope:** these values describe deterministic replay and VM execution; they are not model inference latencies, a whole-suite regression, or statistical proof of general speedups. In the October 31 study all A runs preceded all B runs; comparisons are therefore subject to temporal drift.
