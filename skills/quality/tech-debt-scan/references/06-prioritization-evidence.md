# 06 — Prioritization and Evidence

## Formula

```
priority = round(impact × frequency × reach / effort, 1)
```

You author only `scores` (integers 1–5). `assets/reconcile.py` computes `priority` and derives `severity`; never write either by hand.

| Severity | Priority band |
| -------- | ------------- |
| Critical | ≥ 20          |
| Major    | ≥ 6 and < 20  |
| Minor    | < 6           |

## Anchors

Scores 2 and 4 are intermediate. Cite the measured fact behind every score ≥ 4 in `evidence.result`.

| Factor      | 1                    | 3                                               | 5                                               |
| ----------- | -------------------- | ----------------------------------------------- | ----------------------------------------------- |
| `impact`    | Cosmetic             | Moderate cognitive load or change amplification | Unknown unknowns: changes break without warning |
| `frequency` | No churn in 6 months | Churn in repo percentile 75–90                  | Churn in repo percentile ≥ 97                   |
| `reach`     | One file             | 3–5 dependent modules                           | Cross-cutting or every consumer                 |
| `effort`    | Hours                | Days                                            | Weeks or a migration                            |

- `impact` is `cₚ` in `02`: how hard the part is to understand or change, by symptom.
- `frequency` is `tₚ`: churn percentile from the recon (2 = percentile 50–75, 4 = 90–97). Without git history use `3` and say so in `evidence.result`.
- `reach`: dependents counted by the measurement subagent, or co-change breadth.

## Priority Order

Sort by `priority` descending. Report the top items as quick wins when `effort` ≤ 2.

## Churn Evidence

```bash
git log --since="6 months ago" --name-only --pretty=format: -- <path> | sort | uniq -c | sort -rn | head
git log --since="6 months ago" --format=%an -- <path> | sort -u | wc -l
git blame -L <start>,<end> --date=short <file>
```

## Evidence Rules

- `method`: the command or files read, short enough to rerun.
- `result`: the number or quoted fact. "Looks complex" is not evidence.
- Quote at most a few lines of code; prefer counts and `file:line`.
- When a tool is missing, say so in `result` and fall back to a file-read fact.

## Discard When

- No symptom (`02`) can be named in the current code.
- The pattern is enforced by the framework or generated.
- The code is stable, isolated, and covered by passing tests.
