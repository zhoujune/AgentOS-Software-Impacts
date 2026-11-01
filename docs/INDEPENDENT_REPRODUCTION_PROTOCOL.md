# Independent reproduction protocol (draft; no participants yet)

## Objective

Evaluate whether a person who did not develop AgentOS can reconstruct the journal software, execute the baseline offline test, and **add and evaluate a new task** using the host-side World Effect Judge without private server access or paid model API access.

This is a usability and reproducibility study protocol, **not a human-subjects efficacy study, a live-model benchmark, or a claim of outside adoption**. The maintainers must not mark this protocol completed from internal tests.

## Before recruiting an independent reviewer

1. Repair and verify the public source overlay patch against its pinned checksum.
2. Provide a GitHub commit/tag and complete legal license notice.
3. Test the clean-clone instructions on a host that can access the upstream GitHub repository.
4. Confirm the participant has an x86_64 Linux machine with QEMU, Python 3, and e2fsprogs, or provide a documented supported VM environment.
5. Ensure prompts, cassettes, test files, and log artifacts are safe for public redistribution.

If these conditions are not met, report the attempted trial as a blocked setup, not as a successful reproduction.

## Research questions

**RQ1: Installability.** Can an external user reproduce the baseline toolchain with documented dependencies?

**RQ2: Extensibility.** Can the user add a previously unseen task and specify the expected host-observed effect without changing VTRM implementation code?

**RQ3: Independent verification.** Does the host judge distinguish an actual permitted file write from a final answer that falsely claims the work was done?

**RQ4: Documentation friction.** Which steps require undocumented knowledge, assumptions, or maintainer intervention?

## Suggested execution procedure

The independent reviewer:

1. Receives only the public repository links, this protocol, and the documented prerequisites.
2. Records a pseudonymous participant ID and the test machine's OS, CPU architecture, QEMU/Python/e2fsprogs versions, and hypervisor availability.
3. Records start time, setup blockers, deviations, retries, and any requests for maintainer assistance.
4. Runs the pinned reconstruction procedure from a **fresh directory**, without copying an already-configured AgentOS checkout.
5. Runs the baseline six-task offline representative suite and records the validator summary.
6. Runs examples/world-effect-reuse/run_demo.sh, which exercises one new task and two hand-authored replay traces.
7. Inspects impact_validation.json and case reports, explains why the unsupported-success trace is expected to fail task completion while passing replay and safety checks, and notes any ambiguous reports.
8. If time permits, creates a different original workspace task with a new task ID and outcome predicate, without modifying VTRM. Records any task-schema limitations.
9. Shares sanitized commands, outputs, hashes, notes, and the minimum steps necessary to reproduce any issue.

A maintainer may give troubleshooting assistance **after** the first unaided attempt; record when and why assistance was needed.

## Outcome recording

| Measure | Collection method |
| --- | --- |
| First-attempt installation success | Yes/no with first blocking error |
| Time to first passing baseline suite | Start/end timestamps or elapsed minutes |
| Number of undocumented setup steps | Count and exact description |
| Baseline suite outcome | Machine-readable validator PASS/FAIL, per-case outcomes |
| New-task positive outcome | Required file present; VTRM allowed write; WEJ completion PASS; replay and safety PASS |
| Unsupported-success outcome | No required file; WEJ completion FAIL; replay and safety PASS |
| Reproduction without external model API | Proxy strict-replay evidence and absence of live API calls |
| New independent task | Distinct task ID, schema, run report, and failure/success notes |
| Required maintainer assistance | Number and details of interventions |

### Acceptance threshold for the independent-user milestone

The milestone counts as independently reproduced only if the participant is not an AgentOS maintainer, runs a fresh checkout on a separate environment, provides a consistent baseline suite report, and demonstrates that the new-task world-effect result is based on observed effects rather than agent self-report. Partial or blocked attempts are still valuable findings but are **not recorded as successes**.

The two hand-authored cassettes must be described as test inputs. The result cannot be interpreted as observed behavior or success rate of a real LLM.

## Feedback report template

A participant can copy the following into a GitHub issue or Markdown file (avoid personal identifiers, private keys, secret data, or raw unrelated system logs):

~~~text
Study ID (pseudonym):
Test date and UTC offset:
Independent of AgentOS developers: yes/no
Host OS / architecture:
Python / QEMU / e2fsprogs versions:
Hardware virtualization available: yes/no/unknown
Repository commit(s) / overlay checksum:
Fresh checkout used: yes/no
Initial setup start/end or elapsed minutes:
First attempt completed without help: yes/no
Setup blockers, retries, and workaround steps:
Baseline six-task suite: PASS / FAIL / NOT RUN
New-task positive trace: PASS / FAIL / NOT RUN
Unsupported-success negative control: EXPECTED FAIL / UNEXPECTED PASS / NOT RUN
World-integrity and replay validation:
Impact demo JSON/Markdown location or hashes:
New task added beyond the provided example (optional):
Missing or confusing documentation:
Maintainer assistance required:
Overall status: independently reproduced / partial / blocked
Shareable artifact links (redacted):
~~~

## Privacy and ethics

Participation should be voluntary. Collect only technical environment and outcome data needed for reproducibility. Do not request real names, access tokens, model API keys, private prompts, credentials, or sensitive files. Ask reviewers to redact host paths/usernames from shared logs and to avoid uploading full rootfs images. Avoid presenting software-use feedback as an IRB-reviewed study or as external research adoption without appropriate evidence.

## Reporting in the journal paper

Before completion: "A documented independent reproduction protocol and a new-task example are available; external reproduction has not yet been demonstrated."

After verified completion: report the number of participants, hardware environments, exact successful/failed tasks, setup time distribution, intervention count, failure reasons, and public artifact identifiers. Do not claim broader adoption or productivity gains from one successful internal demonstration.
