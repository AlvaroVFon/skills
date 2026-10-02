---
date: "{YYYY-MM-DD}"
scan_type: "{global | targeted}"
requested_by: "{git config user.name}"
commit: "{git rev-parse --short HEAD}"
baseline: "{previous report file, or none}"
scope: ["{path or module}"] # targeted scans only; remove for global
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

Baseline: {previous report file, or "first scan"}

- {n} Persists · {n} Killed now · {n} New · {n} Not re-checked
- Score: `{module}` {old}% → {new}%
- Killed now: `{file}:{line}` — {operator}
- Not re-checked: `{file}:{line}` — {reason}

## Survivors

### [{Critical | Major | Minor}] {short title}

- Status: {New | Persists}
- Location: `{file}:{line}`
- Operator: {boundary | conditional | logical | arithmetic | statement-removal | return | literal | branch | argument}
- Gap: {what no test asserts}

**Mutant**

```diff
{before/after}
```

**Suggested test** (temporary, not kept in the repo)

```{lang}
{test code}
```

Output: {passes on original; fails on mutant with ..., or "not runnable: {reason}"}
