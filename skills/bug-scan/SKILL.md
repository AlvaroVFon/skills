---
name: bug-scan
description: "Trigger: bug scan, find bugs, hunt latent bugs, scan repo or modules for defects. Scan code for latent bugs and prove each with a repro test."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.1"
---

## Activation Contract

Use this skill to scan a whole repo (global) or given paths/modules (targeted) for **latent bugs** and prove each one. Not for investigating an already-reported bug, reviewing a PR, or security audits.

## Hard Rules

- NEVER modify production code and NEVER propose or apply fixes; repro tests are throwaway (temp file, run, delete unless the user asks to keep them).
- ALWAYS open with the scan-type selector (question tool) before any work: mode (Global/Targeted) plus categories; never infer either from the prompt.
- Cite `file:line` and a concrete failure scenario (input/state → wrong result); no speculation.
- Previous reports are leads, never evidence: re-verify every inherited finding with a test.
- Delegate reconnaissance to an exploration subagent when available; hypotheses and verdicts stay with you.
- Run repro tests in parallel when available, one write-capable subagent per finding, capped; each returns facts, not verdicts.
- ALWAYS state what was not reviewed.
- ALWAYS validate the final report with `python3 assets/validate_report.py --file <report>`; fix every `ERROR` (counters must match the finding blocks) until exit 0; never overwrite one.

## Decision Gates

| Condition                                 | Action                                                                      |
| ----------------------------------------- | --------------------------------------------------------------------------- |
| Scan type not chosen                      | Ask via selector: mode + categories; require an answer before scanning      |
| Global chosen                             | Read memory first, risk-map modules, deepen high risk within the categories |
| Targeted chosen                           | Record paths, read overlapping reports, trace only those flows              |
| No previous report                        | First scan; say so in the summary                                           |
| Repro test fails as predicted             | **Confirmed**                                                               |
| Not testable (infra, timing, environment) | **Unconfirmed** + manual verification steps                                 |
| Repro test passes                         | Discard; count it in the summary                                            |

## Execution Steps

1. Ask the scan type via the selector (`references/01-scan-modes.md`): mode plus categories; for targeted, also request the paths.
2. Load memory (`references/07-scan-memory.md`): mandatory for global.
3. Run reconnaissance, passing the memory result: global returns modules ranked by risk, targeted returns the flows of the given paths; both return the test framework and run command.
4. Scan only the chosen categories, loading just the reference under evaluation.
5. Dispatch one write-capable subagent per finding to write and run its repro test in parallel, capped (`references/06-verification.md`, `assets/verify-finding-subagent.md`).
6. Collect the returned facts, assign verdicts, and confirm no temp tests remain.
7. Take `requested_by` from `git config user.name` (ask if empty), then write the report from `assets/bug-scan-report.md` to `docs/bug-scan/{YYYY-MM-DD}.md` (suffix `-2`, `-3` if it exists).
8. Validate with `python3 assets/validate_report.py --file <report>`; fix every `ERROR:` until exit 0.

## Output Contract

Return the report path plus a chat summary. The report follows `assets/bug-scan-report.md`: frontmatter, coverage and unreviewed areas, verdict counters, delta vs previous, and findings ordered `[Critical]` / `[Major]` / `[Minor]` with test code and output (or manual steps).

## References

- `references/01-scan-modes.md` — scan-type selector, global vs targeted, risk map
- `references/02-logic-edge-cases.md` — boundaries, nulls, conditions
- `references/03-concurrency-async.md` — races, missing await
- `references/04-errors-resources.md` — swallowed errors, leaks
- `references/05-data-integrity.md` — validation, transactions, Mongoose
- `references/06-verification.md` — repro test protocol, parallel verification
- `references/07-scan-memory.md` — previous reports, delta
- `assets/verify-finding-subagent.md` — verification subagent prompt
- `assets/bug-scan-report.md` — report template
- `assets/validate_report.py` — report validator (structure + counter coherence)
