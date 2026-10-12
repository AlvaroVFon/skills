# Mutation Test Report Format

Each scan writes exactly one artifact: `docs/mutation-test/{YYYY-MM-DD}.json`, authored from `assets/mutation-test-report.template.json`, reconciled by `assets/reconcile.py`, and validated by `assets/validate_report.py`. There is no ledger and no rendered file; the dated JSON is the history. See `references/06-baseline-history.md`.

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

# Mutation Test — {repo or module name}

## Summary

- Mode: {global | targeted}
- Mutation score: {n}% ({n} Killed · {n} Survived)
- Mutants: {n} generated · {n} Invalid · {n} Equivalent · {n} Not run · {n} Inconclusive
- Cap used: {n per module / n total}
- Reviewed: {module/path — mutants: n, in order of risk}
- Not reviewed: {modules/paths skipped and why}
- Not covered: {modules without tests}

## By module

| Module     | Mutants | Killed | Survived | Score |
| ---------- | ------- | ------ | -------- | ----- |
| `{module}` | {n}     | {n}    | {n}      | {n}%  |

## Delta vs previous

Baseline: {previous report path or "first scan"}

- {n} Persists · {n} Killed now · {n} New · {n} Not re-checked
- Killed now: `{file}:{line}` — {operator}
- Not re-checked: `{file}:{line}` — {reason}

## Survivors

### [{Critical | Major | Minor}] {short title}

- Status: {New | Persists | Regressed}
- Location: `{file}:{line}`
- Operator: {boundary | conditional | logical | arithmetic | statement-removal | return | literal | branch | argument}
- Gap: {what no test asserts}

**Mutant**

    {before/after diff}

**Suggested test** (temporary, not kept in the repo)

    {test code}

Output: {passes on original; fails on mutant with ..., or "not runnable: {reason}"}
```
