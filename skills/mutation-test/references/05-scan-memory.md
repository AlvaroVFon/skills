# 05 — Scan Memory

## Definition

Reports in `docs/mutation-test/` are the memory between scans. A previous report tells where to look next and what to re-check. It is a **lead, never evidence**: code moves, tests get added, and `file:line` goes stale.

## Locate

1. List `docs/mutation-test/*.md`; read only the frontmatter (`date`, `scan_type`, `scope`, `commit`).
2. **Global scan**: baseline = the latest `scan_type: global`. Supplements = targeted reports newer than the baseline.
3. **Targeted scan**: take the latest report, global or targeted, whose `scope` (or a global's mutated modules) overlaps the given paths.
4. No reports, or no directory: first scan; say so in the summary.

Read the full body of the baseline and supplements only.

## Use

| Use            | How                                                                                  |
| -------------- | ------------------------------------------------------------------------------------ |
| Prioritize     | Rank modules with survivors, low scores, or not reviewed above equal-risk modules    |
| Follow changes | `git diff --name-only {commit}..HEAD` lists changed files; raise their modules' risk |
| Re-verify      | Re-locate each previous survivor, reapply its mutant, and rerun the mapped tests     |

If `commit` is missing or unreachable, use `git log --since={date} --name-only`; if that fails too, skip this criterion and note it.

## Status of Inherited Survivors

| Status         | Meaning                                                  |
| -------------- | -------------------------------------------------------- |
| Persists       | Mutant still survives; list as a normal finding          |
| Killed now     | A test now fails on it or the code is gone; counted only |
| Not re-checked | Out of this scan's scope or not runnable; say why        |
| New            | Not in any previous report                               |

Report the counters, the score change per module, and one line per Killed now / Not re-checked item under `## Delta vs previous`.

## Edge Cases

- **Code moved or renamed**: search by symbol and behavior before marking Killed now.
- **Previous mutant diff is stale**: recreate it against the current code.
- **Report with missing frontmatter**: treat as a lead without `commit`; note it.
- **Many supplements**: read the newest per module only.
