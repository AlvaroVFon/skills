# 02 — Test Design

## From Criteria to Cases

Map each acceptance criterion to tests before coding. For every behavior, cover:

| Type  | Focus                                                                    |
| ----- | ------------------------------------------------------------------------ |
| Happy | The intended use, one clear case                                         |
| Edge  | Boundaries: empty, one, limit, limit ± 1, negative, duplicate, absent    |
| Error | Invalid input, failed dependency, timeout — the defined failure contract |

## Anatomy

- Arrange: build the smallest state that exposes the behavior.
- Act: call the narrowest public entry point; one action per test.
- Assert: the domain outcome (return value, state, side effect), not internals.

## Rules

- Name by behavior: `rejects_order_when_total_equals_limit`.
- Deterministic: control time, randomness, ordering, and external I/O.
- One logical assertion per test; stub only where the boundary demands it.
- The test is part of the deliverable: keep it with the code, in the repo's framework and conventions.
