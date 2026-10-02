# 07 — Scan Memory

## Definition

Reports in `docs/bug-scan/` are the memory between scans. A previous report tells where to look next and what to re-check. It is a **lead, never evidence**: code moves, bugs get fixed, and `file:line` goes stale.

## Locate

1. List `docs/bug-scan/*.md`; read only the frontmatter (`date`, `scan_type`, `scope`, `commit`).
2. **Global scan**: baseline = the latest `scan_type: global`. Supplements = targeted reports newer than the baseline.
3. **Targeted scan**: take the latest report, global or targeted, whose `scope` (or a global's reviewed modules) overlaps the given paths. Light lookup only.
4. No reports, or no directory: first scan; say so in the summary.

Read the full body of the baseline and supplements only.

## Use

| Use            | How                                                                                                                     |
| -------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Prioritize     | Pass the baseline's "Not reviewed" and shallowly reviewed modules to reconnaissance; rank them above equal-risk modules |
| Follow changes | `git diff --name-only {commit}..HEAD` lists changed files; raise their modules' risk                                    |
| Re-verify      | For each previous finding, re-locate the code and rerun or rewrite its test                                             |

If `commit` is missing or unreachable, use `git log --since={date} --name-only`; if that fails too, skip this criterion and note it.

## Status of Inherited Findings

| Status         | Meaning                                              |
| -------------- | ---------------------------------------------------- |
| Persists       | Test still fails as before; list as a normal finding |
| Fixed          | Test passes or the code is gone; counted, not listed |
| Not re-checked | Out of this scan's scope or not runnable; say why    |
| New            | Not in any previous report                           |

Report the counters and one line per Fixed/Not re-checked item under `## Delta vs previous`.

## Edge Cases

- **Code moved or renamed**: search by symbol and behavior before marking Fixed.
- **Previous test code is stale**: rewrite it against the current code; do not trust it.
- **Report with missing frontmatter**: treat as a lead without `commit`; note it.
- **Many supplements**: read the newest per module only.
