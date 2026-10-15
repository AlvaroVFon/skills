# API Security Scan Report Format

Each scan writes exactly one artifact: `docs/api-security-scan/{YYYY-MM-DD}.json`, authored from `assets/api-security-scan-report.template.json`, reconciled by `assets/reconcile.py`, and validated by `assets/validate_report.py`. There is no ledger and no rendered file; the dated JSON is the history. See `references/11-baseline-history.md`.

When the chosen output format is `markdown`, `assets/render_report.py` prints the following view to the chat (`chat` prints a concise summary instead; never both). Secrets are redacted in every view.

## Rendered Markdown

```markdown
---
date: "{YYYY-MM-DD}"
scan_type: "{global | targeted}"
requested_by: "{git config user.name}"
commit: "{git rev-parse --short HEAD}"
baseline: "{previous report path | none}"
scope: ["{route prefix, path or module}"] # targeted scans only
---

# API Security Scan — {api or service name}

## Summary

- Mode: {global | targeted}
- Reviewed: {module/path — depth: deep | shallow, in order of depth}
- Not reviewed: {modules/paths skipped and why}
- Findings: {n} Confirmed · {n} Unconfirmed · {n} discarded

## Delta vs previous

Baseline: {previous report path or "first scan"}

- {n} Persists · {n} Fixed · {n} New · {n} Not re-checked
- Fixed: `{file}:{line}` — {title}
- Not re-checked: `{file}:{line}` — {reason}

## Findings

### [{Critical | High | Medium | Low}] {short title} — {Confirmed | Unconfirmed}

- Status: {New | Persists | Regressed}
- Category: {authn | authz | injection | info-leak | config-exposure | resource-business | error-handling}
- Classification: {APIn:2023} · {Ann:2025} · {CWE-n}
- Endpoint: `{METHOD} {/route/:param}`
- Location: `{file}:{line}`
- Attack: {attacker/request → impact}
- Remediation hint: {one line}

**Exploit test** (temporary, not kept in the repo)

    {test code, secrets redacted}

Output: {response proving the exploit, or "not runnable: {reason}"}

**Manual verification** (Unconfirmed only)

1. {step to reproduce against a local instance}
2. {expected vs observed}
```
