# 02 — Characterization Tests

## Definition

Tests that pin the current observable behavior of untested code so a refactor can prove it changed nothing. They record what the code does, not what it should do.

## Protocol

1. Identify the narrowest public entry point and the outputs/side effects that matter.
2. Feed representative inputs: happy path, boundaries, error paths.
3. Assert the observed result on the current code; it must pass immediately.
4. Name by behavior; keep deterministic (control time, randomness, ordering).
5. Keep them in the repo as the refactor's safety net.

## Rules

- Never assert implementation details (private calls, internal order).
- If observed behavior looks wrong, do not fix it here: record it in the doc and open a `tdd` task.
- Prefer a few high-value cases over exhaustive coverage.
