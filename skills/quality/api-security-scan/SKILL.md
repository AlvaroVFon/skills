---
name: api-security-scan
description: "Trigger: API security scan, find vulnerabilities, audit HTTP endpoints, OWASP. Scan HTTP API code for vulnerabilities, prove each with an exploit test."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to scan a whole HTTP API (global) or given routes/modules (targeted) for **security vulnerabilities**, including information leaks, and prove each one. Not for PR review, dependency CVE audits, infra/cloud config, or live pentesting.

## Hard Rules

- NEVER modify production code and NEVER write fixes; give at most a one-line `remediation_hint`. Exploit tests are throwaway.
- NEVER send requests to a running server, staging, production, or third-party host: exploit the app **in-process** with the repo's test harness and stub outbound HTTP.
- ALWAYS open with the one selector (question tool): mode, categories, and output format (`chat` | `markdown`); never infer them.
- Cite `file:line`, the endpoint, and a concrete attack (identity + request → impact); no speculation.
- NEVER print real secrets, tokens, or PII: synthetic fixtures only, redact to the first 4 chars.
- Previous reports are leads, never evidence: re-verify every inherited finding.
- `docs/api-security-scan/{YYYY-MM-DD}.json` is the only artifact; never overwrite one.
- Delegate reconnaissance to an exploration subagent; verify with one write-capable subagent per finding, **at most 4 concurrent**; they return facts, verdicts stay with you.
- ALWAYS state what was not reviewed and which controls live outside the repo (gateway, WAF).
- ALWAYS run `assets/reconcile.py`, then `assets/validate_report.py`; fix every `ERROR:` until exit 0.

## Decision Gates

| Condition                              | Action                                                           |
| -------------------------------------- | ---------------------------------------------------------------- |
| Selector not answered                  | Ask mode + categories + output format; wait                      |
| Global chosen                          | Read the previous report, rank routes by risk, deepen High       |
| Targeted chosen                        | Record targets, read overlapping reports, trace only those flows |
| No previous report                     | First scan; `baseline` = `none`, say so                          |
| Exploit test succeeds as predicted     | **Confirmed**                                                    |
| Needs real infra, gateway, or provider | **Unconfirmed** + manual steps for a local instance              |
| Attack rejected / leaked field absent  | Discard; count it in the summary                                 |

## Execution Steps

1. Ask the selector (`references/01-scan-modes.md`); for targeted, also request the targets.
2. Load history (`references/11-baseline-history.md`) and re-verify open findings in scope.
3. Reconnaissance: endpoint inventory (method, path, handler, middleware chain, inputs, data owner), global middleware, outbound calls, test harness and run command.
4. Scan only the chosen categories, loading just the reference under evaluation (`02`–`08`); rate and tag with `references/10-severity.md` (OWASP API 2023 + Top 10:2025).
5. Verify each finding with an in-process exploit test via subagents (`references/09-verification.md`, `assets/verify-exploit-subagent.md`).
6. Assign verdicts and confirm `git status` shows no temp tests.
7. Take `requested_by` from `git config user.name` (ask if empty); write the report from `assets/api-security-scan-report.template.json` (suffix `-2`, `-3` if the date exists).
8. Reconcile: `python3 assets/reconcile.py --report <report.json>`.
9. Validate: `python3 assets/validate_report.py --file <report.json>`; fix every `ERROR:`, resolve every W15.
10. Present the view: `chat` → concise summary; `markdown` → paste the stdout of `python3 assets/render_report.py --json <report.json>`. Never both, never a file.

## Output Contract

Return the report JSON path, the transition summary (new · persists · fixed · regressed · not re-checked), Confirmed/Unconfirmed counts by severity, and the view in the chosen format. The report follows `assets/api-security-scan-report.schema.json`; the view follows `assets/api-security-scan-report.md`.

## References

- `references/01-scan-modes.md` — selector, endpoint inventory, risk ranking
- `references/02-authn-sessions.md` — authentication, JWT, sessions (API2)
- `references/03-authz-access.md` — BOLA, mass assignment, BFLA (API1/3/5)
- `references/04-injection-input.md` — NoSQL/SQL/command injection, SSRF, traversal
- `references/05-info-leak.md` — internal detail leaks, improper data exposure
- `references/06-config-exposure.md` — CORS, headers, secrets, inventory (API8/9/10)
- `references/07-resource-business.md` — rate limits, pagination, business flows (API4/6)
- `references/08-error-handling.md` — fail-open, crashes, partial state (A10:2025)
- `references/09-verification.md` — in-process exploit protocol, verdicts, redaction
- `references/10-severity.md` — severity matrix, OWASP API 2023 + Top 10:2025 mapping
- `references/11-baseline-history.md` — baseline, ids, delta, transitions
- `assets/verify-exploit-subagent.md` — verification subagent prompt
- `assets/api-security-scan-report.template.json` — report template
- `assets/api-security-scan-report.schema.json` — report schema
- `assets/api-security-scan-report.md` — markdown view format
- `assets/reconcile.py` — ids and delta vs previous report
- `assets/render_report.py` — render report JSON to markdown
- `assets/validate_report.py` — report validator
