# 04 — Survivor Tests

## Definition

Every Survived mutant gets a **suggested test** that would kill it. The test is validated, reported, and never kept in the repo.

## Protocol

1. State the gap: "No test asserts X when Y; mutant Z goes unnoticed".
2. Write the test with the repo's framework and conventions, in a temporary file named `*.mutation-test.*` next to the existing tests.
3. Run it on the **original** code: it must pass.
4. Apply the mutant and run it: it must fail for the predicted reason.
5. Revert the mutant, delete the temporary test, and check `git status`.

## Verdicts

| Original | Mutant | Result                                               |
| -------- | ------ | ---------------------------------------------------- |
| Passes   | Fails  | Suggested test validated; include code and output    |
| Passes   | Passes | Test is too weak; rewrite once, else report gap only |
| Fails    | —      | Fix the test, not the code; else report gap only     |

## Writing a Good Test

- Assert domain behavior (return value, state, side effect), not implementation.
- Smallest input and fewest stubs that expose the mutant; target the boundary or branch it changed.
- Name it by the behavior: `rejects_order_when_total_equals_limit`.
- Deterministic: control time, randomness, and ordering.

## Grouping

When several survivors in one function share a gap, one test may kill them all; validate it against each mutant and list them together.

## Edge Cases

- **Not testable without infrastructure**: report the gap and manual verification steps, no test.
- **Survivor looks equivalent after a closer look**: reclassify as Equivalent and say why.
