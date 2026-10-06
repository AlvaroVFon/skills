# 08 — Baseline and Delta

## Definition

Every scan writes exactly one artifact: `docs/bug-scan/{YYYY-MM-DD}.json` (suffix `-2`, `-3` if it
already exists). That dated report is both the snapshot and the durable history; there is no ledger
and no rendered file.

The **baseline** is the previous report. `assets/reconcile.py` reads it, assigns a stable id to every
finding, and writes the `delta` back into the new report. Only the new report is written.

## Baseline lookup

`reconcile.py` uses `report["baseline"]` when it points to an existing file; otherwise it picks the
most recent `docs/bug-scan/*.json` (excluding the report being written). No candidate means a first
scan: `baseline` is set to `none`.

Locate the baseline conceptually by `date`, `scan_type`, and `scope`: a global scan compares against
the latest global report (plus newer targeted reports); a targeted scan compares against the latest
report whose `scope` overlaps its paths.

## Identity

`reconcile.py` derives a stable id from `kind + category + file + slug(title)`, excluding the line,
so the id survives code moving down a file. On re-locate it matches by exact id, then by
`file + category` with a title-word overlap ≥ 0.6, so a renamed finding reuses its id.

## Lifecycle

| Report status | Meaning                                        |
| ------------- | ---------------------------------------------- |
| `new`         | Not present in the baseline                    |
| `persists`    | Present in the baseline and still reproduces   |
| `fixed`       | Re-verified as gone since the baseline         |
| `regressed`   | Present again after the baseline had it closed |

`reconcile.py` normalizes drift: a baseline match reported `new` becomes `persists`, and a finding
that reappears after a `fixed` entry becomes `regressed`.

## Delta

The `delta` written into the report counts `new`, `persists`, `fixed`, `regressed`, and
`not_rechecked`. Baseline findings that are not re-checked and are still open are carried forward as
`not_rechecked_items`, with the reason (`file changed since {commit}` or `out of scan scope`). Carried
items are re-listed on every later report until they are re-checked.

## Edge cases

- **Code moved or renamed**: search by symbol/behavior before marking fixed; the id survives line
  drift but not a file move, so expect a new id plus a fuzzy match.
- **Missing `commit`**: skip the git check for that entry and record the reason.
- **History grows large**: reports are kept; read metadata only when scanning for a baseline.
- **Out-of-scope baseline items**: they stay `not_rechecked`, never silently dropped.
