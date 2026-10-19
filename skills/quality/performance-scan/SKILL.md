---
name: performance-scan
description: "Trigger: performance scan, find slow code, N+1, memory leaks, hotspots, scan repo or modules for perf issues. Scan for hotspots and prove each with a benchmark."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to scan a whole repo (global) or given paths/modules (targeted) for **performance hotspots** and prove each one by measurement. Not for correctness bugs (use `bug-scan`), technical debt (use `tech-debt-scan`), or security audits (use `api-security-scan`).

## Hard Rules

- NEVER modify production code and NEVER propose or apply fixes; benchmarks are throwaway (temp file, run, delete unless the user asks to keep them).
- ALWAYS open with the one selector (question tool) before any work: mode, categories, and output format (`chat` | `markdown`); never infer any of them from the prompt.
- Cite `file:line`, the input sizes, and the measured metric; no speculation, no "looks slow".
- Run benchmarks locally only; never start services or hit real databases, networks, or production.
- Previous reports are leads, never evidence: re-measure every inherited finding.
- `docs/performance-scan/{YYYY-MM-DD}.json` is the only artifact: it is the report and the history. Never write a ledger or a rendered file.
- Delegate reconnaissance to an exploration subagent when available; hypotheses and verdicts stay with you.
- One write-capable subagent per finding, **at most 4 concurrent**; serialize time-based benchmarks.
- ALWAYS state what was not reviewed.
- ALWAYS run `assets/reconcile.py`, then `validate_report.py`; fix every `ERROR:` until exit 0. Never overwrite an existing report.

## Decision Gates

| Condition                                 | Action                                                                    |
| ----------------------------------------- | ------------------------------------------------------------------------- |
| Selector not answered                     | Ask: mode + categories + output format; require an answer before scanning |
| Global chosen                             | Read the previous report first, rank hot paths, deepen high rank          |
| Targeted chosen                           | Record paths, read overlapping reports, trace only those flows            |
| No previous report                        | First scan; set `baseline` to `none` and say so                           |
| Metric meets the threshold                | **Confirmed**                                                             |
| Needs real infra, or measurement is noisy | **Unconfirmed** + manual verification steps                               |
| Scales as expected                        | Discard; count it in the summary                                          |

## Execution Steps

1. Ask the selector (`references/01-scan-modes.md`): mode, categories, output format; for targeted, also the paths.
2. Load history (`references/04-baseline-history.md`): find the baseline in `docs/performance-scan/*.json`, re-measure its open findings in scope.
3. Run reconnaissance: global returns modules ranked by hot-path likelihood, targeted returns the flows; both return the runtime and run command.
4. Scan only the chosen categories (`references/02-categories-signals.md`).
5. Dispatch one subagent per finding to benchmark it (`references/03-measurement-and-thresholds.md`, `assets/measure-finding-subagent.md`).
6. Collect the facts, assign verdicts and severity, confirm no temp files remain.
7. Take `requested_by` from `git config user.name` (ask if empty); write the report from `assets/performance-scan-report.template.json` to `docs/performance-scan/{YYYY-MM-DD}.json` (suffix `-2`, `-3` if it exists).
8. Reconcile: `python3 assets/reconcile.py --report <report.json>`.
9. Validate: `python3 assets/validate_report.py --file <report.json>`; fix every `ERROR:`.
10. Present the view in the chosen format: `chat` returns the concise summary; `markdown` runs `python3 assets/render_report.py --json <report.json>` and pastes stdout. Never both, never a file.

## Output Contract

Return the report JSON path, the transition summary (new · persists · fixed · regressed · not re-checked), the Confirmed/Unconfirmed counts, and the view in the chosen format. Only the JSON is written; it follows `assets/performance-scan-report.schema.json` and the view follows `assets/performance-scan-report.md`.

## References

- `references/01-scan-modes.md` — selector, global vs targeted, hot-path map
- `references/02-categories-signals.md` — signals per category
- `references/03-measurement-and-thresholds.md` — benchmark protocol, thresholds, severity
- `references/04-baseline-history.md` — baseline, ids, delta, transitions
- `assets/measure-finding-subagent.md` — measurement subagent prompt
- `assets/performance-scan-report.template.json` — report template
- `assets/performance-scan-report.schema.json` — report schema
- `assets/performance-scan-report.md` — chat markdown view format
- `assets/reconcile.py` — assign ids, compute delta
- `assets/render_report.py` — render report JSON to markdown
- `assets/validate_report.py` — report validator
