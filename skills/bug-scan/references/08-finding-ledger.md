# 08 — Finding Ledger

## Definition

`docs/bug-scan/ledger.json` is the durable memory between scans: one entry per finding, with its
lifecycle. Dated reports are snapshots; the ledger is what carries a finding forward, so a fix
discovered in any later scan (or applied outside a scan) is reflected instead of re-derived.

Artifacts, written to `docs/bug-scan/`:

| File                            | Role                                                       |
| ------------------------------- | ---------------------------------------------------------- |
| `ledger.json`                   | Canonical, evolving index of every finding                 |
| `{YYYY-MM-DD}.json`             | Canonical report of one scan (`validate_report`).          |
| `{YYYY-MM-DD}.md`               | Rendered human view (`render_report.py`)                   |
| `bug-scan-ledger.template.json` | Shape of a ledger (`assets/bug-scan-ledger.template.json`) |

## Identity

`update_ledger.py` derives a stable id from `kind + category + file + slug(title)`, excluding the
line, so the id survives code moving down a file. On re-locate it matches by exact id, then by
`file + category` with a title-word overlap ≥ 0.6, so a renamed finding reuses its entry instead of
duplicating. A report finding may carry `id`; a wrong id is ignored in favor of the fuzzy match.

## Lifecycle

| Status      | Meaning                                                     |
| ----------- | ----------------------------------------------------------- |
| `open`      | Reproduces or was never re-checked; still expected present  |
| `stale`     | File changed since its `commit` and it was not re-checked   |
| `fixed`     | A later scan re-verified it as gone, or resolved explicitly |
| `regressed` | A `fixed`/`wontfix` entry reappeared                        |
| `wontfix`   | Explicitly accepted, with a reason in `notes`               |

Report finding `status` values map as: `new`/`persists` → `open` (or `regressed` if the entry was
closed), `fixed` → `fixed`. The entry keeps `first_seen`, updates `last_seen` and `commit`, and sets
`fixed_at`/`fixed_commit` when it closes.

## Baseline report

The ledger is the primary memory; the baseline report supplies the delta's prose. Locate it from
`docs/bug-scan/*.json` by frontmatter-equivalent fields (`date`, `scan_type`, `scope`):

1. List the reports; read only their metadata.
2. **Global scan**: baseline = the latest `scan_type: global`; supplements = targeted reports newer
   than it. **Targeted scan**: the latest report, global or targeted, whose `scope` (or a global's
   reviewed modules) overlaps the given paths.
3. No reports: first scan; set `baseline: "none"` and say so in the summary.

Legacy `docs/bug-scan/*.md` reports have no ledger entry; read them as leads only and note it.

## Reconciliation (every scan)

1. Read `ledger.json`; if absent, treat the newest legacy `.md` as leads and start a new ledger.
2. For each finding in scope, re-verify and set its report `status` (`new`/`persists`/`fixed`).
3. Run `update_ledger.py --ledger docs/bug-scan/ledger.json --report <report.json>`: it folds the
   findings in, computes the delta, and rewrites `delta` into the report.
4. For open entries out of scope it marks `stale` when `git diff --name-only <commit>..HEAD -- <file>`
   shows a change, else counts them `not re-checked`. If git is unavailable, all become not re-checked
   with the reason recorded.

## Resolving a fix outside a scan

When a fix is merged and you are asked to update the records:

```sh
python3 assets/update_ledger.py --ledger docs/bug-scan/ledger.json \
  --resolve <id> --status fixed --commit <sha> --note "PR #123"
```

Use `--status wontfix --note <reason>` to accept a finding. The next scan still re-verifies a fixed
entry; if it reproduces again it becomes `regressed`.

## Edge cases

- **Code moved or renamed**: search by symbol/behavior before marking fixed; the id survives line
  drift but not a file move, so expect a new id plus a fuzzy match.
- **Missing `commit`**: skip the git check for that entry and record the reason.
- **Ledger grows large**: closed entries are kept; filter by `status` when reading, do not prune
  silently.
- **Two findings collapse**: keep the oldest id, note the merge in `notes`.
