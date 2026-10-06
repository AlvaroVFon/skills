---
name: bug-scan
description: "Trigger: bug scan, find bugs, hunt latent bugs, scan repo or modules for defects. Scan code for latent bugs and prove each with a repro test."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "3.0"
---

## Activation Contract

Use this skill to scan a whole repo (global) or given paths/modules (targeted) for **latent bugs** and prove each one. Not for investigating an already-reported bug, reviewing a PR, or security audits.

## Hard Rules

- NEVER modify production code and NEVER propose or apply fixes; repro tests are throwaway (temp file, run, delete unless the user asks to keep them).
- ALWAYS open with the one selector (question tool) before any work: mode, categories, and output format (`chat` | `markdown`); never infer any of them from the prompt.
- Cite `file:line` and a concrete failure scenario (input/state → wrong result); no speculation.
- Previous reports are leads, never evidence: re-verify every inherited finding with a test.
- `docs/bug-scan/{YYYY-MM-DD}.json` is the only artifact: it is the report and the history. Never write a ledger or a rendered file.
- Delegate reconnaissance to an exploration subagent when available; hypotheses and verdicts stay with you.
- Run repro tests in parallel when available, one write-capable subagent per finding, **at most 4 concurrent**; each returns facts, not verdicts.
- ALWAYS state what was not reviewed.
- ALWAYS run `assets/reconcile.py`, then validate the JSON (`validate_report.py`); fix every `ERROR:` until exit 0. Never overwrite an existing report.

## Decision Gates

| Condition                                 | Action                                                                    |
| ----------------------------------------- | ------------------------------------------------------------------------- |
| Selector not answered                     | Ask: mode + categories + output format; require an answer before scanning |
| Global chosen                             | Read the previous report first, risk-map modules, deepen high risk        |
| Targeted chosen                           | Record paths, read overlapping reports, trace only those flows            |
| No previous report                        | First scan; set `baseline` to `none` and say so                           |
| Repro test fails as predicted             | **Confirmed**                                                             |
| Not testable (infra, timing, environment) | **Unconfirmed** + manual verification steps                               |
| Repro test passes                         | Discard; count it in the summary                                          |

## Execution Steps

1. Ask the selector (`references/01-scan-modes.md`): mode, categories, and output format; for targeted, also request the paths.
2. Load history (`references/08-baseline-history.md`): find the baseline report in `docs/bug-scan/*.json` and re-verify its open findings in scope.
3. Run reconnaissance: global returns modules ranked by risk, targeted returns the flows of the given paths; both return the test framework and run command.
4. Scan only the chosen categories, loading just the reference under evaluation.
5. Dispatch one write-capable subagent per finding to write and run its repro test, **at most 4 concurrent** (`references/06-verification.md`, `assets/verify-finding-subagent.md`).
6. Collect the returned facts, assign verdicts, and confirm no temp tests remain.
7. Take `requested_by` from `git config user.name` (ask if empty), then write the report from `assets/bug-scan-report.template.json` to `docs/bug-scan/{YYYY-MM-DD}.json` (suffix `-2`, `-3` if it exists).
8. Reconcile: `python3 assets/reconcile.py --report <report.json>` — assigns ids and writes the delta against the previous report.
9. Validate: `python3 assets/validate_report.py --file <report.json>`; fix every `ERROR:` until exit 0.
10. Present the human view in chat per the chosen format: `chat` returns the concise summary; `markdown` runs `python3 assets/render_report.py --json <report.json>` and pastes its stdout. Never both, never a file.

## Output Contract

Return the report JSON path, the transition summary (new · persists · fixed · regressed · not re-checked), the Confirmed/Unconfirmed counts, and the human view in the chosen format (chat or markdown). Only the JSON is written; the report follows `assets/bug-scan-report.schema.json` and the view follows `assets/bug-scan-report.md`.

## References

- `references/01-scan-modes.md` — selector, global vs targeted, risk map, output format
- `references/02-logic-edge-cases.md` — boundaries, nulls, conditions
- `references/03-concurrency-async.md` — races, missing await
- `references/04-errors-resources.md` — swallowed errors, leaks
- `references/05-data-integrity.md` — validation, transactions, Mongoose
- `references/06-verification.md` — repro test protocol, parallel verification
- `references/08-baseline-history.md` — baseline lookup, ids, delta, transitions
- `assets/verify-finding-subagent.md` — verification subagent prompt
- `assets/bug-scan-report.template.json` — canonical report template
- `assets/bug-scan-report.schema.json` — report schema
- `assets/bug-scan-report.md` — chat markdown view format
- `assets/reconcile.py` — assign ids, compute delta vs previous report
- `assets/render_report.py` — render report JSON to chat markdown
- `assets/validate_report.py` — report validator (structure + counters)
