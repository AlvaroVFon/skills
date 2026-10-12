---
name: refactor
description: "Trigger: refactor, refactoring, restructure code, clean up code, behavior-preserving change. Restructure code in small test-verified steps."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to restructure existing code without changing its observable behavior, whether requested directly or as the refactor phase delegated by `tdd`. Not for adding features or fixing bugs (use `tdd`), and not for redesigning module boundaries (use `module-design`).

## Hard Rules

- Behavior preservation is the contract: never change observable behavior; a required behavior change stops the refactor and returns to `tdd`.
- ALWAYS write the pre-implementation doc first to `docs/implementations/{YYYY-MM-DD}-{slug}.md` from `assets/refactor-doc.md` (sections: Goal & problem, Acceptance criteria as invariants, Test plan); never overwrite an existing doc (suffix `-2`, `-3`).
- Require a green test baseline for the scope before touching code; if tests are missing, write characterization tests first.
- One structural step at a time; run the scoped tests after every step; a red step is reverted, never carried forward.
- NEVER mix behavior changes with restructuring in the same step.
- Delete code only when proven unused; cite the evidence.
- Detect language, test framework, and run command from the repo; ask if ambiguous. Stack-agnostic.

## Decision Gates

| Condition                     | Action                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------ |
| No tests for the target       | Write characterization tests first (`references/02-characterization-tests.md`) |
| Baseline red                  | Stop; report the failing output; do not refactor                               |
| Step turns tests red          | Revert the step; split it smaller                                              |
| Behavior change required      | Stop; hand back to `tdd`                                                       |
| Structural flaw spans modules | Escalate to `module-design` / `adr`                                            |
| Scope is docs/config only     | No refactor; report why                                                        |

## Execution Steps

1. Recon: detect language, test framework, and the command to run the scoped tests; locate the target and its existing tests.
2. Write the refactor doc (`assets/refactor-doc.md`) to `docs/implementations/`.
3. Ensure a green baseline; add characterization tests if absent.
4. Apply one structural step from `references/01-refactoring-steps.md`; run the scoped tests; keep them green.
5. Repeat step 4 until the goal is met; keep every step a reviewable diff.
6. Run the full relevant suite plus lint and typecheck.
7. Update the doc status, then report.

## Output Contract

Return: doc path; target and steps applied; invariants preserved; tests added (`file:line`); final test/lint/typecheck output; what was not covered.

## References

- `references/01-refactoring-steps.md` — step catalog and selection
- `references/02-characterization-tests.md` — safety net for untested code
- `assets/refactor-doc.md` — pre-implementation doc template
