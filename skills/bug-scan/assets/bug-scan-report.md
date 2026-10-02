---
date: "{YYYY-MM-DD}"
scan_type: "{global | targeted}"
requested_by: "{git config user.name}"
commit: "{git rev-parse --short HEAD}"
baseline: "{previous report file, or none}"
scope: ["{path or module}"] # targeted scans only; remove for global
---

# Bug Scan — {repo or module name}

## Summary

- Mode: {global | targeted}
- Reviewed: {module/path — depth: deep | shallow, in order of depth}
- Not reviewed: {modules/paths skipped and why}
- Findings: {n} Confirmed · {n} Unconfirmed · {n} discarded

## Delta vs previous

Baseline: {previous report file, or "first scan"}

- {n} Persists · {n} Fixed · {n} New · {n} Not re-checked
- Fixed: `{file}:{line}` — {title}
- Not re-checked: `{file}:{line}` — {reason}

## Findings

### [{Critical | Major | Minor}] {short title} — {Confirmed | Unconfirmed}

- Status: {New | Persists}
- Category: {logic | concurrency | errors-resources | data-integrity}
- Location: `{file}:{line}`
- Scenario: {input/state → wrong result}

**Repro test** (temporary, not kept in the repo)

```{lang}
{test code}
```

Output: {failing assertion/error as run, or "not runnable: {reason}"}

**Manual verification** (Unconfirmed only)

1. {step to reproduce}
2. {expected vs observed}
