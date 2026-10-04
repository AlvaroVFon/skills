---
name: bug-scan
description: "Trigger: bug scan, find bugs, hunt latent bugs, scan repo or modules for defects. Scan code for latent bugs and prove each with a repro test."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "2.0"
---

## Activation Contract

Use this skill to scan a whole repo (global) or given paths/modules (targeted) for **latent bugs** and prove each one. Not for investigating an already-reported bug, reviewing a PR, or security audits.

## Hard Rules

- NEVER modify production code and NEVER propose or apply fixes; repro tests are throwaway (temp file, run, delete unless the user asks to keep them).
- ALWAYS open with the scan-type selector (question tool) before any work: mode (Global/Targeted) plus categories; never infer either from the prompt.
- Cite `file:line` and a concrete failure scenario (input/state → wrong result); no speculation.
- The ledger and previous reports are leads, never evidence: re-verify every inherited finding with a test.
- Maintain `docs/bug-scan/ledger.json` as the memory: update it and the report in the same run; never hand-edit the rendered `.md`.
- Delegate reconnaissance to an exploration subagent when available; hypotheses and verdicts stay with you.
- Run repro tests in parallel when available, one write-capable subagent per finding, capped; each returns facts, not verdicts.
- ALWAYS state what was not reviewed.
- ALWAYS render the report and validate both the report and the ledger (`validate_report.py`, `validate_ledger.py`); fix every `ERROR` until exit 0. Never overwrite an existing report.

## Decision Gates

| Condition                                 | Action                                                                      |
| ----------------------------------------- | --------------------------------------------------------------------------- |
| Scan type not chosen                      | Ask via selector: mode + categories; require an answer before scanning      |
| Global chosen                             | Read ledger first, risk-map modules, deepen high risk within the categories |
| Targeted chosen                           | Record paths, read overlapping reports, trace only those flows              |
| No ledger or previous report              | First scan; say so in the summary                                           |
| Repro test fails as predicted             | **Confirmed**                                                               |
| Not testable (infra, timing, environment) | **Unconfirmed** + manual verification steps                                 |
| Repro test passes                         | Discard; count it in the summary                                            |

## Execution Steps

1. Ask the scan type via the selector (`references/01-scan-modes.md`): mode plus categories; for targeted, also request the paths.
2. Load memory (`references/08-finding-ledger.md`): read `docs/bug-scan/ledger.json` and the baseline report; re-verify open entries in scope.
3. Run reconnaissance, passing the ledger result: global returns modules ranked by risk, targeted returns the flows of the given paths; both return the test framework and run command.
4. Scan only the chosen categories, loading just the reference under evaluation.
5. Dispatch one write-capable subagent per finding to write and run its repro test in parallel, capped (`references/06-verification.md`, `assets/verify-finding-subagent.md`).
6. Collect the returned facts, assign verdicts, and confirm no temp tests remain.
7. Take `requested_by` from `git config user.name` (ask if empty), then write the report from `assets/bug-scan-report.template.json` to `docs/bug-scan/{YYYY-MM-DD}.json` (suffix `-2`, `-3` if it exists).
8. Update memory: `python3 assets/update_ledger.py --ledger docs/bug-scan/ledger.json --report <report.json>`.
9. Render the human view: `python3 assets/render_report.py --json <report.json> --out <report.md>`.
10. Validate with `python3 assets/validate_report.py --file <report.json>` and `python3 assets/validate_ledger.py --file docs/bug-scan/ledger.json`; fix every `ERROR:` until exit 0.

## Output Contract

Return the report JSON and Markdown paths, the ledger transition summary (new · persists · fixed · regressed · not re-checked), and a chat summary. The report follows `assets/bug-scan-report.schema.json`; the Markdown view follows `assets/bug-scan-report.md`.

## References

- `references/01-scan-modes.md` — scan-type selector, global vs targeted, risk map
- `references/02-logic-edge-cases.md` — boundaries, nulls, conditions
- `references/03-concurrency-async.md` — races, missing await
- `references/04-errors-resources.md` — swallowed errors, leaks
- `references/05-data-integrity.md` — validation, transactions, Mongoose
- `references/06-verification.md` — repro test protocol, parallel verification
- `references/08-finding-ledger.md` — ledger lifecycle, reconciliation, resolve
- `assets/verify-finding-subagent.md` — verification subagent prompt
- `assets/bug-scan-report.template.json` — canonical report template
- `assets/bug-scan-ledger.template.json` — ledger template
- `assets/bug-scan-report.md` — rendered Markdown format
- `assets/update_ledger.py` — merge report into ledger, reconcile, resolve
- `assets/render_report.py` — render report JSON to Markdown
- `assets/validate_report.py` — report validator (structure + counters)
- `assets/validate_ledger.py` — ledger validator (structure + lifecycle)
