---
name: mutation-test
description: "Trigger: mutation test, mutation testing, test quality, surviving mutants. Mutate a repo or modules by hand and report which mutants the tests miss."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to measure test quality by injecting manual mutants into a whole repo (global) or given paths/modules (targeted) and checking whether the tests detect them. Not for writing tests, reviewing PRs, or hunting bugs (use `bug-scan`).

## Hard Rules

- NEVER leave production code modified: apply one mutant at a time in a temporary `git worktree` (else `git checkout -- {file}`), revert after each run; `git status` must show only the report at the end.
- NEVER edit or add tests in the repo; suggested tests live only in the report (temp files are deleted).
- Require a green baseline for the scope before mutating; if red, stop and report.
- One mutant = one atomic change; cite `file:line`, operator, and exact diff.
- Previous reports are leads, never evidence: re-run every inherited survivor.
- Delegate reconnaissance to an exploration subagent when available; verdicts stay with you.
- ALWAYS state what was not reviewed.
- Write the report only to `docs/mutation-test/{YYYY-MM-DD}.md` (suffix `-2`, `-3` if it exists); never overwrite one.

## Decision Gates

| Condition                                 | Action                                                      |
| ----------------------------------------- | ----------------------------------------------------------- |
| No paths given                            | Global: read memory first, risk-map modules, cap per module |
| Paths/modules given                       | Targeted: read overlapping reports, mutate only those flows |
| No test framework or module without tests | Do not mutate; list as not covered                          |
| Baseline red                              | Abort with the failing output                               |
| Tests fail on the mutant (or time out)    | **Killed**                                                  |
| Tests pass on the mutant                  | **Survived**: write and validate a suggested test           |
| Mutant invalid or provably equivalent     | Discard; count it in the summary                            |
| No previous report                        | First scan; say so in the summary                           |

## Execution Steps

1. Set mode and scope; for targeted, record the paths.
2. Load memory (`references/05-scan-memory.md`): mandatory for global.
3. Run reconnaissance: modules or flows, test framework, command to run the tests of one file/module, code→test mapping.
4. Run the baseline for the scope.
5. Generate mutants from `references/02-mutation-catalog.md`, prioritized and capped (`references/01-scan-modes.md`).
6. Apply, run, and revert each mutant (`references/03-execution-protocol.md`).
7. For each survivor, write and validate a test that kills it (`references/04-survivor-tests.md`).
8. Take `requested_by` from `git config user.name` (ask if empty), then write the report from `assets/mutation-test-report.md`.

## Output Contract

Return the report path plus a chat summary: mutation score (global and per module), top survivors, and unreviewed areas. The report follows `assets/mutation-test-report.md`: frontmatter, summary, delta vs previous, per-module table, and survivors ordered `[Critical]` / `[Major]` / `[Minor]` with mutant diff and suggested test.

## References

- `references/01-scan-modes.md` — global vs targeted, risk map, caps
- `references/02-mutation-catalog.md` — mutation operators, exclusions
- `references/03-execution-protocol.md` — apply/run/revert, verdicts
- `references/04-survivor-tests.md` — suggested tests for survivors
- `references/05-scan-memory.md` — previous reports, delta
- `assets/mutation-test-report.md` — report template
