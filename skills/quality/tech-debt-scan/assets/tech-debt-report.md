# Tech Debt Scan Report Format

Each scan writes exactly one artifact: `docs/tech-debt/{YYYY-MM-DD}.json`, authored from `assets/tech-debt-report.template.json`, reconciled by `assets/reconcile.py` (which derives `priority` and `severity` from `scores`), and validated by `assets/validate_report.py`. There is no ledger and no rendered file; the dated JSON is the history. See `references/07-baseline-history.md`.

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

# Tech Debt Scan — {repo or module name}

## Summary

- Mode: {global | targeted}
- Reviewed: {module/path — depth: deep | shallow}
- Not reviewed: {modules/paths skipped and why}
- Open debt: {n} Critical · {n} Major · {n} Minor · {n} discarded

## Delta vs previous

Baseline: {previous report path or "none"}

- {n} Persists · {n} Fixed · {n} New · {n} Not re-checked

## Findings

### [{Critical | Major | Minor}] {short title} — priority {impact × frequency × reach / effort}

- Status: {New | Persists | Regressed}
- Category: {code | tests | architecture | docs | infra}
- Complexity: {change-amplification | cognitive-load | unknown-unknowns} / {dependency | obscurity}
- Scores: I{1-5} · F{1-5} · R{1-5} · E{1-5}
- Location: `{file}:{line}`
- Debt: {what it is and why it is debt}
- Impact: {cost it imposes now}
- Evidence: `{command or files read}` → {measured result}
- Remediation: {one-line direction}
```
