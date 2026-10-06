---
name: mutation-test
description: "Trigger: mutation test, mutation testing, test quality, surviving mutants. Mutate a repo or modules by hand and report which mutants the tests miss."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "3.0"
---

## Activation Contract

Use this skill to measure test quality by injecting manual mutants into a whole repo (global) or given paths/modules (targeted) and checking whether the tests detect them. Not for writing tests, reviewing PRs, or hunting bugs (use `bug-scan`).

## Hard Rules

- NEVER leave production code modified: each mutant lives only in its own temporary `git worktree` (fallback: mutate in place and `git checkout -- {file}`); `git status` clean at the end.
- NEVER edit or add tests in the repo; suggested tests live only in the report (temp files are deleted).
- ALWAYS open with one selector (question tool) before any work: mode, mutation categories, output format (`chat` | `markdown`); never infer them from the prompt.
- Require a green baseline before mutating; abort and report if red.
- One mutant = one atomic change; cite `file:line`, operator, exact diff.
- Previous reports are leads, never evidence: re-run every inherited survivor.
- `docs/mutation-test/{YYYY-MM-DD}.json` is the only artifact: it is the report and the history. Never write a ledger or a rendered file.
- Delegate reconnaissance to an exploration subagent when available; verdicts stay with you.
- Run mutants in parallel when available, one write-capable subagent per mutant in its own worktree, **at most 4 concurrent**; each returns facts, not verdicts.
- ALWAYS state what was not reviewed.
- ALWAYS run `assets/reconcile.py`, then validate (`validate_report.py`); fix every `ERROR:` until exit 0. Never overwrite an existing report.

## Decision Gates

| Condition                                 | Action                                                           |
| ----------------------------------------- | ---------------------------------------------------------------- |
| Selector not answered                     | Ask mode, categories, output format; require an answer first     |
| Global chosen                             | Read the previous report first, risk-map modules, cap per module |
| Targeted chosen                           | Read overlapping reports, mutate only those flows                |
| No test framework or module without tests | Do not mutate; list as not covered                               |
| Baseline red                              | Abort with the failing output                                    |
| Tests fail on the mutant (or time out)    | **Killed**                                                       |
| Tests pass on the mutant                  | **Survived**: write and validate a suggested test                |
| Mutant invalid or provably equivalent     | Discard; count it in the summary                                 |
| No previous report                        | First scan; set `baseline` to `none` and say so                  |

## Execution Steps

1. Ask the selector (`references/01-scan-modes.md`): mode, mutation categories, and output format; for targeted, also request the paths.
2. Load history (`references/06-baseline-history.md`): find the baseline report in `docs/mutation-test/*.json` and re-run its open survivors in scope.
3. Run reconnaissance: modules or flows, test framework, run command per test file, code→test mapping.
4. Run the baseline for the scope.
5. Generate mutants from the chosen categories (`references/02-mutation-catalog.md`), prioritized and capped.
6. Dispatch one write-capable subagent per mutant, each in its own temp worktree, **at most 4 concurrent** (`references/03-execution-protocol.md`, `assets/verify-mutant-subagent.md`); collect facts and assign verdicts.
7. For each survivor, write and validate a killing test (`references/04-survivor-tests.md`).
8. Take `requested_by` from `git config user.name` (ask if empty), then write the report from `assets/mutation-test-report.template.json` to `docs/mutation-test/{YYYY-MM-DD}.json` (suffix `-2`, `-3` if it exists).
9. Reconcile: `python3 assets/reconcile.py --report <report.json>` — assigns ids and writes the delta against the previous report.
10. Validate: `python3 assets/validate_report.py --file <report.json>`; fix every `ERROR:` until exit 0.
11. Present the human view per the chosen format: `chat` returns the concise summary; `markdown` runs `python3 assets/render_report.py --json <report.json>` and pastes its stdout. Never both, never a file.

## Output Contract

Return the report JSON path, the mutation score (global and per module), the transition summary (new · persists · killed · regressed · not re-checked), and the human view in the chosen format. Only the JSON is written; the report follows `assets/mutation-test-report.schema.json`, the view `assets/mutation-test-report.md`.

## References

- `references/01-scan-modes.md` — selector, risk map, caps, output format
- `references/02-mutation-catalog.md` — mutation operators, exclusions
- `references/03-execution-protocol.md` — worktree isolation, parallel runs, verdicts
- `references/04-survivor-tests.md` — suggested tests for survivors
- `references/06-baseline-history.md` — baseline lookup, ids, delta, transitions
- `assets/verify-mutant-subagent.md` — mutation subagent prompt
- `assets/mutation-test-report.template.json` — report template
- `assets/mutation-test-report.schema.json` — report schema
- `assets/mutation-test-report.md` — chat markdown view format
- `assets/reconcile.py` — assign ids, compute delta vs previous report
- `assets/render_report.py` — render report JSON to chat markdown
- `assets/validate_report.py` — report validator
