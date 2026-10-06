# Bug Scan Report Format

Each scan writes exactly one artifact: `docs/bug-scan/{YYYY-MM-DD}.json`, authored from `assets/bug-scan-report.template.json`, reconciled by `assets/reconcile.py`, and validated by `assets/validate_report.py`. There is no ledger and no rendered file; the dated JSON is the history. See `references/08-baseline-history.md`.

When the chosen output format is `markdown`, `assets/render_report.py` prints the following view to the chat (`chat` prints a concise summary instead; never both).

## Rendered Markdown

```markdown
---
date: "{YYYY-MM-DD}"
scan_type: "{global | targeted}"
requested_by: "{git config user.name}"
commit: "{git rev-parse --short HEAD}"
baseline: "{previous report path | none}"
scope: ["{path or module}"] # targeted scans only
---

# Bug Scan — {repo or module name}

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

### [{Critical | Major | Minor}] {short title} — {Confirmed | Unconfirmed}

- Status: {New | Persists | Regressed}
- Category: {logic | concurrency | errors-resources | data-integrity}
- Location: `{file}:{line}`
- Scenario: {input/state → wrong result}

**Repro test** (temporary, not kept in the repo)

    {test code}

Output: {failing assertion/error as run, or "not runnable: {reason}"}

**Manual verification** (Unconfirmed only)

1. {step to reproduce}
2. {expected vs observed}
```
