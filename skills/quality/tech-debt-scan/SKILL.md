---
name: tech-debt-scan
description: "Trigger: tech debt, technical debt scan, code health audit, debt hotspots. Scan a repo or modules for technical debt (complexity) and rank it by priority score."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to scan a whole repo (global) or given paths/modules (targeted) for **technical debt**, meaning complexity with a nameable symptom (`references/02-complexity-model.md`), in code, tests, and architecture/docs/infra, and prioritize it. Not for latent bugs (`bug-scan`), test strength (`mutation-test`), security (`api-security-scan`), dependency upgrades (`update-dependencies`), or applying refactors (`refactor`).

## Hard Rules

- NEVER modify production code, tests, or config; NEVER apply fixes. `remediation` is one line of direction, not a patch.
- ALWAYS open with the one selector (question tool) before any work: mode, categories, and output format (`chat` | `markdown`); never infer any of them from the prompt.
- Every finding needs a `symptom`, a `cause`, `file:line`, and measured evidence: `evidence.method` (command or files read) and `evidence.result` (number, count, or quoted fact). No opinion-only findings; discard findings with no present symptom and count them in `discarded`.
- Author only `scores` (integers 1-5 per `references/06-prioritization-evidence.md`); `priority = impact × frequency × reach / effort` and `severity` are derived by `reconcile.py`, never written by hand.
- Previous reports are leads, never evidence: re-measure every inherited finding in scope.
- `docs/tech-debt/{YYYY-MM-DD}.json` is the only artifact; never write a ledger or a rendered file.
- Delegate reconnaissance and measurement to read-only subagents with `assets/recon-subagent.md` and `assets/measure-subagent.md`, **at most 3 concurrent**; they return facts, scoring and severity stay with you.
- ALWAYS state what was not reviewed.
- ALWAYS run `assets/reconcile.py`, then `assets/validate_report.py`; fix every `ERROR:` until exit 0. Never overwrite an existing report.

## Decision Gates

| Condition                      | Action                                                                |
| ------------------------------ | --------------------------------------------------------------------- |
| Selector not answered          | Ask: mode + categories + output format; require an answer first       |
| Global chosen                  | Read the previous report, rank modules by churn × complexity, go deep |
| Targeted chosen                | Record paths, read overlapping reports, assess only those paths       |
| No previous report             | First scan; set `baseline` to `none` and say so                       |
| No git history                 | Score `frequency` 3 and state it in `evidence.result`                 |
| Generated, vendored, or legacy | List under not reviewed unless the user included it                   |

## Execution Steps

1. Ask the selector (`references/01-scan-modes.md`): mode, categories (`code`, `tests`, `architecture-docs-infra`), output format; targeted also needs paths.
2. Load history (`references/07-baseline-history.md`): baseline from `docs/tech-debt/*.json`; re-measure its open findings in scope.
3. Run one recon subagent (`assets/recon-subagent.md`): module map, churn percentiles, tooling, test command.
4. Run one measurement subagent per chosen category (`assets/measure-subagent.md`), loading only its signals reference (`references/03-code-debt.md`, `references/04-test-debt.md`, or `references/05-architecture-docs-infra.md`).
5. Classify each candidate (symptom, cause) and score it; drop those with no symptom or evidence.
6. Take `requested_by` from `git config user.name` (ask if empty), then write the report from `assets/tech-debt-report.template.json` to `docs/tech-debt/{YYYY-MM-DD}.json` (suffix `-2`, `-3` if it exists).
7. Reconcile: `python3 assets/reconcile.py --report <report.json>`.
8. Validate: `python3 assets/validate_report.py --file <report.json>`; fix every `ERROR:` until exit 0.
9. Present the view in the chosen format: `chat` the concise summary; `markdown` pastes `python3 assets/render_report.py --json <report.json>` stdout. Never both, never a file.

## Output Contract

Return the report JSON path, the transition summary (new · persists · fixed · regressed · not re-checked), the open counts by severity, the top items by priority (quick wins first), and the view in the chosen format. For top `architecture` items, suggest `module-design`. Only the JSON is written; it follows `assets/tech-debt-report.schema.json` and the view follows `assets/tech-debt-report.md`.

## References

- `references/01-scan-modes.md` — selector, global vs targeted, hotspot map, output format
- `references/02-complexity-model.md` — complexity, symptoms, causes, co-change
- `references/03-code-debt.md` — complexity, duplication, coupling, dead code, markers
- `references/04-test-debt.md` — coverage gaps, flaky or brittle tests, slow suites
- `references/05-architecture-docs-infra.md` — layering, docs drift, CI/build/config
- `references/06-prioritization-evidence.md` — scores, formula, bands, evidence
- `references/07-baseline-history.md` — baseline lookup, ids, delta, transitions
- `assets/recon-subagent.md` — reconnaissance subagent prompt
- `assets/measure-subagent.md` — measurement subagent prompt
- `assets/tech-debt-report.template.json` — canonical report template
- `assets/tech-debt-report.schema.json` — report schema
- `assets/tech-debt-report.md` — chat markdown view format
- `assets/reconcile.py` — derive priority/severity, assign ids, compute delta
- `assets/render_report.py` — render report JSON to chat markdown
- `assets/validate_report.py` — report validator (structure, scores, counters, evidence)
