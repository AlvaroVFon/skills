---
name: tdd
description: "Trigger: implement, implementar, add feature, change behavior, write code, TDD, red-green-refactor. Doc-first, test-first implementation, then refactor."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill for any request to implement or change behavior in code. Skip only for docs-only, config-only, or mechanical edits with no behavior change (say so; apply `refactor` only if code shape changes). Not for latent-bug scans (`bug-scan`) or module redesign (`module-design`).

## Hard Rules

- ALWAYS write the pre-implementation doc first to `docs/implementations/{YYYY-MM-DD}-{slug}.md` from `assets/implementation-doc.md` (sections: Goal & problem, Acceptance criteria, Test plan); never overwrite an existing doc (suffix `-2`, `-3`).
- NEVER write production code before a failing test: red, then green, then refactor, one behavior per cycle.
- The test plan covers happy, edge, and error cases; every acceptance criterion maps to a test. If a test must change to pass, the doc is wrong: fix the doc, never weaken the test.
- After green, load the `refactor` skill for the refactor phase before the next cycle.
- Detect language, test framework, and run command from the repo; ask if ambiguous. Stack-agnostic.
- Run the full relevant suite plus lint and typecheck before claiming done.

## Decision Gates

| Condition                             | Action                                                            |
| ------------------------------------- | ----------------------------------------------------------------- |
| Docs/config/mechanical only           | Skip tdd; report why; apply `refactor` only if code shape changes |
| No test framework or no tests         | Ask the user; propose the minimal harness before coding           |
| Acceptance criteria missing/ambiguous | Update the doc first; never guess                                 |
| Test fails for the wrong reason       | Fix the test or setup before implementing                         |
| Test fails as expected (red)          | Implement the minimal code to pass                                |
| Green for one criterion               | Refactor phase (`refactor` skill), then the next criterion        |
| All criteria green                    | Full suite + lint + typecheck; update the doc                     |

## Execution Steps

1. Recon: detect language, test framework, and the command to run a single test and the whole suite; read conventions and neighboring tests.
2. Write the doc (`assets/implementation-doc.md`) to `docs/implementations/`; derive acceptance criteria and test plan.
3. Red: write the smallest test for the next criterion; watch it fail for the predicted reason (`references/02-test-design.md`).
4. Green: implement the minimal code to pass; run the scoped tests.
5. Refactor: load the `refactor` skill and clean up with tests staying green (`references/01-red-green-refactor.md`).
6. Repeat steps 3–5 for each acceptance criterion.
7. Run the full relevant suite plus lint and typecheck; update the doc status; report.

## Output Contract

Return: doc path; acceptance criteria and their tests; files changed; final test/lint/typecheck output; confirmation the refactor phase was applied; what was not covered.

## References

- `references/01-red-green-refactor.md` — the cycle and its discipline
- `references/02-test-design.md` — test plan, case selection, naming
- `assets/implementation-doc.md` — pre-implementation doc template
