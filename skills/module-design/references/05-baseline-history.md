# 05 — Baseline and Delta

## Definition

Every analysis writes exactly one artifact: `docs/module-design/{YYYY-MM-DD}-{module}.json` (suffix
`-2` if it already exists). That dated brief is both the snapshot and the durable history; there is
no ledger and no rendered file.

The **baseline** is the previous brief for the same module. `assets/reconcile.py` reads it, assigns a
stable id to every finding, and writes the `delta` back into the new brief. Only the new brief is
written.

## Baseline lookup

`reconcile.py` uses `brief["baseline"]` when it points to an existing file; otherwise it picks the
most recent `docs/module-design/*.json` for the **same module** (excluding the brief being written).
No candidate means a first analysis: `baseline` is set to `none`.

## Identity

`reconcile.py` derives a stable id from `design + type + file + slug(title)`, excluding the line, so
the id survives code moving down a file. On re-locate it matches by exact id, then by `file + type`
with a title-word overlap ≥ 0.6. Module-level findings (no `location`) use the empty file in the id
and match by `type + title`.

## Finding types

| Type                     | Meaning                                           |
| ------------------------ | ------------------------------------------------- |
| `leakage-interface`      | Interface leakage across the module boundary      |
| `leakage-back-door`      | Back-door leakage through internal artifacts      |
| `shallow`                | Depth verdict of shallow at macro or micro level  |
| `over-config`            | Parameter that should default or be auto-detected |
| `temporal-decomposition` | Split by execution order instead of by knowledge  |
| `improvement`            | Any other considered improvement                  |

## Lifecycle

| Report status | Meaning                                                 |
| ------------- | ------------------------------------------------------- |
| `new`         | Not present in the baseline                             |
| `persists`    | Present in the baseline and still unaddressed           |
| `resolved`    | A later analysis shows it fixed, or resolved explicitly |
| `regressed`   | Present again after the baseline had it resolved        |

`reconcile.py` normalizes drift: a baseline match reported `new` becomes `persists`, and a finding
that reappears after a `resolved` entry becomes `regressed`.

## Delta

The `delta` written into the brief counts `new`, `persists`, `resolved`, `regressed`, and
`not_rechecked`. Baseline findings that are not re-checked and are still open are carried forward as
`not_rechecked_items`, with the reason (`file changed since {commit}` or `out of scan scope`). Carried
items are re-listed on every later brief until they are re-checked.

## Edge cases

- **Module renamed or moved**: the id survives line drift but not a file/module move; expect a new id
  plus a fuzzy match.
- **Missing `commit`**: skip the git check for that entry and record the reason.
- **Out-of-scope baseline items**: they stay `not_rechecked`, never silently dropped.
