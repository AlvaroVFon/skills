# 05 — Design Finding Ledger

## Definition

`docs/module-design/ledger.json` is the durable memory between analyses: one entry per design
finding, with its lifecycle. Dated briefs are snapshots; the ledger carries a finding forward, so a
leakage closed by a later refactor, or a shallow verdict that improves, is reflected instead of
re-derived.

Artifacts, written to `docs/module-design/`:

| File                                 | Role                                               |
| ------------------------------------ | -------------------------------------------------- |
| `ledger.json`                        | Canonical, evolving index of every finding         |
| `{YYYY-MM-DD}-{module}.json`         | Canonical brief of one analysis (`validate_brief`) |
| `{YYYY-MM-DD}-{module}.md`           | Rendered human view (`render_brief.py`)            |
| `module-design-ledger.template.json` | Shape of a ledger                                  |

## Identity

`update_ledger.py` derives a stable id from `design + type + file + slug(title)`, excluding the
line, so the id survives code moving down a file. On re-locate it matches by exact id, then by
`file + type` with a title-word overlap ≥ 0.6. Module-level findings (no `location`) use the empty
file in the id and match by `type + title`.

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

| Status      | Meaning                                                 |
| ----------- | ------------------------------------------------------- |
| `open`      | Present in the current design; still unaddressed        |
| `stale`     | Module files changed since `commit`, not re-checked     |
| `resolved`  | A later analysis shows it fixed, or resolved explicitly |
| `regressed` | A `resolved`/`wontfix` entry reappeared                 |
| `wontfix`   | Explicitly accepted, with a reason in `notes`           |

Report finding `status` values map as: `new`/`persists` → `open` (or `regressed` if the entry was
closed), `resolved` → `resolved`.

## Reconciliation (every analysis)

1. Read `ledger.json`; if absent, treat the newest legacy `.md` as leads and start a new ledger.
2. Re-evaluate the module's findings in scope; set each report `status` (`new`/`persists`/`resolved`).
3. Run `update_ledger.py --ledger docs/module-design/ledger.json --report <brief.json>`: it folds
   the findings in, computes the delta, and rewrites `delta` into the brief.
4. Out-of-scope open entries are marked `stale` when their file changed since `commit`, else counted
   `not re-checked`.

## Resolving outside an analysis

When a refactor fixes a tracked finding:

```sh
python3 assets/update_ledger.py --ledger docs/module-design/ledger.json \
  --resolve <id> --status resolved --commit <sha> --note "extracted tax policy in PR #123"
```

Use `--status wontfix --note <reason>` to accept a finding. The next analysis still re-checks a
resolved entry; if it reappears it becomes `regressed`.

## Edge cases

- **Inline output**: `inline` writes no brief and no ledger entry; the finding is not tracked.
- **Module renamed or moved**: the id survives line drift but not a file/module move; expect a new
  id plus a fuzzy match.
- **Missing `commit`**: skip the git check for that entry and record the reason.
- **Ledger grows large**: closed entries are kept; filter by `status`, do not prune silently.
