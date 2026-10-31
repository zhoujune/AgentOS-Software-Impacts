# AgentOS controlled guest-polling comparison

**Validation: PASS**; 3 complete repetitions and 18 passed cases per profile.

| Metric | A median (s) | B median (s) | A p95 (s) | B p95 (s) | Median reduction |
| --- | ---: | ---: | ---: | ---: | ---: |
| Task enqueue/wait | 10.006 | 8.005 | 12.008 | 10.007 | +20.00% |
| End-to-end case incl. reset | 25.258 | 23.230 | 27.263 | 25.307 | +8.03% |
| VM boot-to-ready | 10.003 | 10.004 | 10.005 | 10.005 | -0.01% |
| Image reset | 0.072 | 0.071 | 0.096 | 0.093 | +1.02% |

## Per-repetition task-wait medians

| Repetition | A (s) | B (s) |
| --- | ---: | ---: |
| 1 | 10.006 | 8.006 |
| 2 | 10.006 | 8.005 |
| 3 | 10.505 | 8.005 |

## Interpretation constraints

- A runs precede B runs; not randomized/interleaved.
- Six exact-replay tasks only; no live LLM inference.
- Pooled case-level medians are descriptive, not independent samples suitable for a significance test.
- A/B image difference was separately verified in two embedded guest scripts.

The comparison is descriptive; no statistical significance or full-task-suite security claim is established.
