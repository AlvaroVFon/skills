# 06 — Verification

## Definition

A finding is only reported with a verdict earned by evidence. The default evidence is a **repro test** that fails on the current code for the predicted reason.

## Protocol

1. State the prediction: "Calling X with Y must return/throw Z, but returns W".
2. Use the repo's own test framework, conventions, and run command (from reconnaissance).
3. Write the test in a temporary file next to the repo's tests (name it `*.bug-scan.*` so it is easy to find and delete). Never edit existing tests or production code.
4. Run only that file. Capture the output.
5. Compare with the prediction and assign the verdict.
6. Delete every temporary test; check `git status` shows no leftovers besides the report.

## Verdicts

| Result                                         | Verdict     | Report                                       |
| ---------------------------------------------- | ----------- | -------------------------------------------- |
| Fails with the predicted assertion/error       | Confirmed   | Test code and its failing output             |
| Fails for another reason (setup, import, stub) | Retry once  | Fix the test, not the code; else Unconfirmed |
| Passes                                         | Discarded   | Counted in the summary, not listed           |
| Cannot be run (infra, timing, environment)     | Unconfirmed | Test sketch if useful, plus manual steps     |

## Writing a Good Repro Test

- Assert the domain behavior, not the implementation.
- Smallest input and fewest stubs that show the bug.
- Name it by the failure: `rejects_duplicate_concurrent_signup`.
- Deterministic: control time, randomness, and interleaving with stubs.

## Manual Verification Steps

For Unconfirmed findings give numbered, runnable steps: preconditions and data, exact action (request, command, or sequence), expected vs observed result, and what to watch (log line, row count, metric).

## Edge Cases

- **Test needs infrastructure** (real DB, queue, network): mark Unconfirmed; do not start services unasked.
- **Existing tests already cover it and pass**: re-read the test; if it covers the scenario, discard.
- **Flaky result**: run three times; if inconsistent, report as Unconfirmed and say it is nondeterministic.
