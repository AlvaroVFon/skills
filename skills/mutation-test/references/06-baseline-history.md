# 06 — Baseline and Delta

## Definition

Every scan writes exactly one artifact: `docs/mutation-test/{YYYY-MM-DD}.json` (suffix `-2`, `-3` if
it already exists). That dated report is both the snapshot and the durable history; there is no
ledger and no rendered file.

The **baseline** is the previous report. `assets/reconcile.py` reads it, assigns a stable id to every
mutant, and writes the `delta` back into the new report. Only the new report is written.

## Baseline lookup

`reconcile.py` uses `report["baseline"]` when it points to an existing file; otherwise it picks the
most recent `docs/mutation-test/*.json` (excluding the report being written). No candidate means a
first scan: `baseline` is set to `none`.

Locate the baseline conceptually by `date`, `scan_type`, and `scope`: a global scan compares against
the latest global report; a targeted scan compares against the latest report whose `scope` overlaps
its paths.

## Identity

`reconcile.py` derives a stable id from `mutant + operator + file + slug(title)`, excluding the line,
so the id survives code moving down a file. On re-locate it matches by exact id, then by
`file + operator` with a title-word overlap ≥ 0.6, so a reworded mutant reuses its id.

## Lifecycle

| Report status | Meaning                                                    |
| ------------- | ---------------------------------------------------------- |
| `new`         | Not present in the baseline                                |
| `persists`    | Present in the baseline and still survives                 |
| `killed`      | A mapped test now kills it, or it was resolved explicitly  |
| `regressed`   | Present (surviving) again after the baseline had it killed |

`reconcile.py` normalizes drift: a baseline match reported `new` becomes `persists`, and a mutant
that survives again after a `killed` entry becomes `regressed`. Invalid, Equivalent, Not run and
Inconclusive mutants are counted in `summary` but never listed as findings.

## Delta

The `delta` written into the report counts `new`, `persists`, `killed`, `regressed`, and
`not_rechecked`. Baseline survivors that are not re-run and still open are carried forward as
`not_rechecked_items`, with the reason (`file changed since {commit}` or `out of scan scope`).
Carried items are re-listed on every later report until they are re-run.

## Edge cases

- **Mutant diff is stale**: recreate it against the current code before re-running; the id survives
  line drift but not a file move.
- **Module loses its tests**: survivors become `not-run` for that scan; record the reason.
- **Missing `commit`**: skip the git check for that entry and record the reason.
- **Out-of-scope baseline items**: they stay `not_rechecked`, never silently dropped.
