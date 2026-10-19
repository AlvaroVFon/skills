# 03 — Measurement and Thresholds

## Definition

A finding gets a verdict only from a measurement. The default evidence is a throwaway **benchmark** that runs the suspect code at two or more input sizes and compares the median of three runs.

## Protocol

1. State the prediction: "Metric M at size N1 vs N2 grows as G".
2. Use the repo's runtime and conventions (from reconnaissance). Prefer counting operations (queries, calls, allocations) over wall time: counts are deterministic.
3. Write the benchmark in a temp file named `*.performance-scan.*` next to the repo tests. Never edit existing tests or production code.
4. Stub I/O (database, network) with counting fakes; never start services unasked.
5. Run only that file, three times per size; keep the median. Capture raw output.
6. Compare with the thresholds and assign the verdict.
7. Delete every temp file; check `git status` shows no leftovers besides the report.

## Parallel Verification

Same model as the other scans: one write-capable subagent per finding (`assets/measure-finding-subagent.md`), **at most 4 concurrent**. Serialize findings that share infrastructure or CPU-sensitive timing: parallel wall-clock benchmarks distort each other, so run time-based ones one at a time. Verdicts stay with the main agent. No subagent available: run sequentially.

## Default Thresholds

Overridable in the selector.

| Metric kind            | Confirmed when                                                           |
| ---------------------- | ------------------------------------------------------------------------ |
| Operation count        | Grows with input size where it should be constant (N+1, per-item calls)  |
| Time                   | Large-input median ≥ 5× the size ratio on a linear path, or superlinear  |
| Memory                 | Heap grows monotonically across repeated runs of the same operation      |
| Payload / bundle bytes | Measured size exceeds what the consumer uses by ≥ 50%, with sizes quoted |

## Verdicts

| Result                                               | Verdict     | Report                               |
| ---------------------------------------------------- | ----------- | ------------------------------------ |
| Metric meets the threshold                           | Confirmed   | Benchmark code, raw output, `metric` |
| Measures fine (scales as expected)                   | Discarded   | Counted in the summary, not listed   |
| Needs real infra (DB, network, production-size data) | Unconfirmed | Sketch if useful, plus manual steps  |
| Noisy: runs differ by more than 25%                  | Unconfirmed | Say it is noisy; give manual steps   |

`Confirmed` requires `evidence.type = benchmark` with `code` and a numeric `metric` where `large > small`; the validator enforces it (E13).

## Severity Rubric

| Severity | Criteria                                                                   |
| -------- | -------------------------------------------------------------------------- |
| Critical | Superlinear or unbounded growth on a hot path (request, consumer, render)  |
| Major    | Linear overhead per item on a hot path, or unbounded growth on a warm path |
| Minor    | Measurable but bounded cost, or a cold path                                |

## Manual Verification Steps

For Unconfirmed findings give numbered, runnable steps: environment and data size, exact action, expected vs observed metric, and what to watch (query log, profiler, heap snapshot).

## Edge Cases

- **Microbenchmark noise**: warm up once, never compare single runs.
- **Existing benchmark covers it**: reuse its harness; still record the metric.
- **Result depends on data volume**: state the sizes used in `scenario`.
