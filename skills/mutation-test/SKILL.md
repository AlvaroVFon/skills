---
name: mutation-test
description: "Trigger: mutation test, mutation testing, test quality, surviving mutants. Mutate a repo or modules by hand and report which mutants the tests miss."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.1"
---

## Activation Contract

Use this skill to measure test quality by injecting manual mutants into a whole repo (global) or given paths/modules (targeted) and checking whether the tests detect them. Not for writing tests, reviewing PRs, or hunting bugs (use `bug-scan`).

## Hard Rules

- NEVER leave production code modified: each mutant lives only in its own temporary `git worktree` (fallback: mutate in place and `git checkout -- {file}`); `git status` and `git worktree list` clean at the end.
- NEVER edit or add tests in the repo; suggested tests live only in the report (temp files are deleted).
- ALWAYS open with the scan-type selector (question tool) before any work: mode (Global/Targeted) plus mutation categories; never infer either from the prompt.
- Require a green baseline for the scope before mutating; abort and report if red.
- One mutant = one atomic change; cite `file:line`, operator, and exact diff.
- Previous reports are leads, never evidence: re-run every inherited survivor.
- Delegate reconnaissance to an exploration subagent when available; verdicts stay with you.
- Run mutants in parallel when available, one write-capable subagent per mutant in its own worktree, capped; each returns facts, not verdicts.
- ALWAYS state what was not reviewed.
- ALWAYS validate the final report with `python3 assets/validate_report.py --file <report>`; fix every `ERROR` (score and counters must match the blocks) until exit 0; never overwrite one.

## Decision Gates

| Condition                                 | Action                                                                 |
| ----------------------------------------- | ---------------------------------------------------------------------- |
| Scan type not chosen                      | Ask via selector: mode + categories; require an answer before mutating |
| Global chosen                             | Read memory first, risk-map modules, cap per module                    |
| Targeted chosen                           | Read overlapping reports, mutate only those flows                      |
| No test framework or module without tests | Do not mutate; list as not covered                                     |
| Baseline red                              | Abort with the failing output                                          |
| Tests fail on the mutant (or time out)    | **Killed**                                                             |
| Tests pass on the mutant                  | **Survived**: write and validate a suggested test                      |
| Mutant invalid or provably equivalent     | Discard; count it in the summary                                       |
| No previous report                        | First scan; say so in the summary                                      |

## Execution Steps

1. Ask the scan type via the selector (`references/01-scan-modes.md`): mode plus mutation categories; for targeted, also request the paths.
2. Load memory (`references/05-scan-memory.md`): mandatory for global.
3. Run reconnaissance: modules or flows, test framework, command to run one file's tests, code→test mapping.
4. Run the baseline for the scope.
5. Generate mutants from the chosen categories of `references/02-mutation-catalog.md`, prioritized and capped.
6. Dispatch one write-capable subagent per mutant, each in its own temp worktree, capped (`references/03-execution-protocol.md`, `assets/verify-mutant-subagent.md`); collect facts and assign verdicts.
7. For each survivor, write and validate a test that kills it (`references/04-survivor-tests.md`).
8. Take `requested_by` from `git config user.name` (ask if empty), then write the report from `assets/mutation-test-report.md` to `docs/mutation-test/{YYYY-MM-DD}.md` (suffix `-2`, `-3` if it exists).
9. Validate with `python3 assets/validate_report.py --file <report>`; fix every `ERROR:` until exit 0.

## Output Contract

Return the report path plus a chat summary: mutation score (global and per module), top survivors, and unreviewed areas. The report follows `assets/mutation-test-report.md`: frontmatter, summary, delta vs previous, per-module table, and survivors ordered `[Critical]` / `[Major]` / `[Minor]` with mutant diff and suggested test.

## References

- `references/01-scan-modes.md` — scan-type selector, global vs targeted, risk map, caps
- `references/02-mutation-catalog.md` — mutation operators, exclusions
- `references/03-execution-protocol.md` — worktree isolation, parallel runs, verdicts
- `references/04-survivor-tests.md` — suggested tests for survivors
- `references/05-scan-memory.md` — previous reports, delta
- `assets/verify-mutant-subagent.md` — mutation subagent prompt
- `assets/mutation-test-report.md` — report template
- `assets/validate_report.py` — report validator (structure + score/counter coherence)
