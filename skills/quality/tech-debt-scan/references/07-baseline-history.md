# 06 — Baseline and Delta

## Definition

Every scan writes exactly one artifact: `docs/tech-debt/{YYYY-MM-DD}.json` (suffix `-2`, `-3` if it already exists). That dated report is both the snapshot and the durable history; there is no ledger and no rendered file.

The **baseline** is the previous report. `assets/reconcile.py` reads it, assigns a stable id to every finding, and writes the `delta` back into the new report.

## Baseline lookup

`reconcile.py` uses `report["baseline"]` when it points to an existing file; otherwise it picks the most recent `docs/tech-debt/*.json` (excluding the report being written). No candidate means a first scan: `baseline` is `none`.

A global scan compares against the latest global report plus newer targeted ones; a targeted scan compares against the latest report whose `scope` overlaps its paths.

## Identity

The id derives from `kind + category + file + slug(title)`, excluding the line, so it survives code moving within a file. On re-locate it matches by exact id, then by `file + category` with title-word overlap ≥ 0.6.

## Lifecycle

| Status      | Meaning                                             |
| ----------- | --------------------------------------------------- |
| `new`       | Not present in the baseline                         |
| `persists`  | Present in the baseline and still measurable        |
| `fixed`     | Re-measured below the debt threshold since baseline |
| `regressed` | Present again after the baseline had it closed      |

`reconcile.py` normalizes drift: a baseline match reported `new` becomes `persists`; a finding reappearing after `fixed` becomes `regressed`.

## Re-measuring

Re-run the inherited `evidence.method` and compare. Record the new `evidence.result`; a worse number keeps `persists`, a number under the threshold is `fixed`.

## Edge Cases

- **File moved or renamed**: search by symbol before marking fixed; expect a new id plus a fuzzy match.
- **Missing `commit`**: skip the git check for that entry and record the reason.
- **Out-of-scope baseline items**: they stay `not_rechecked`, never silently dropped.
