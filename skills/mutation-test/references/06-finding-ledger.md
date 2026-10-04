# 06 — Survivor Ledger

## Definition

`docs/mutation-test/ledger.json` is the durable memory between scans: one entry per mutant, with its
lifecycle. Dated reports are snapshots; the ledger carries a mutant forward, so a mutant killed by a
later test run — or one the analysis resolves outside a scan — is reflected instead of re-derived.

Artifacts, written to `docs/mutation-test/`:

| File                                 | Role                                              |
| ------------------------------------ | ------------------------------------------------- |
| `ledger.json`                        | Canonical, evolving index of every mutant         |
| `{YYYY-MM-DD}.json`                  | Canonical report of one scan (`validate_report`). |
| `{YYYY-MM-DD}.md`                    | Rendered human view (`render_report.py`)          |
| `mutation-test-ledger.template.json` | Shape of a ledger                                 |

## Identity

`update_ledger.py` derives a stable id from `mutant + operator + file + slug(title)`, excluding the
line, so the id survives code moving down a file. On re-locate it matches by exact id, then by
`file + operator` with a title-word overlap ≥ 0.6, so a reworded mutant reuses its entry.

## Lifecycle

| Status                                                | Meaning                                                      |
| ----------------------------------------------------- | ------------------------------------------------------------ |
| `survived`                                            | No test kills it; the mutant is the open finding             |
| `stale`                                               | Source or mapped test changed since `commit`, not re-checked |
| `killed`                                              | A test now kills it, or it was resolved explicitly           |
| `regressed`                                           | A `killed`/`wontfix` entry survived again                    |
| `wontfix`                                             | Explicitly accepted, with a reason in `notes`                |
| `equivalent` · `invalid` · `not-run` · `inconclusive` | Terminal results, counted, never open                        |

Report finding `status` values map as: `new`/`persists` → `survived` (or `regressed` if the entry
was closed), `killed` → `killed`. Invalid, equivalent, not-run and inconclusive mutants are counted
in `summary` but not listed as findings.

## Baseline report

The ledger is the primary memory; the baseline report supplies the delta's prose. Locate it from
`docs/mutation-test/*.json` by `date`, `scan_type` and `scope`: a global scan uses the latest
`scan_type: global`; a targeted scan uses the latest report whose `scope` (or a global's reviewed
modules) overlaps the given paths. No reports: first scan; set `baseline: "none"`. Legacy `.md`
reports have no ledger entry; read them as leads only and note it.

## Reconciliation (every scan)

1. Read `ledger.json`; if absent, treat the newest legacy `.md` as leads and start a new ledger.
2. Re-apply and re-run each in-scope survivor; set the report `status` (`new`/`persists`/`killed`).
3. Run `update_ledger.py --ledger docs/mutation-test/ledger.json --report <report.json>`: it folds
   the findings in, computes the delta, and rewrites `delta` into the report.
4. Out-of-scope survivors are marked `stale` when `git diff --name-only <commit>..HEAD -- <file>`
   (or any mapped test) shows a change, else counted `not re-checked`.

## Resolving outside a scan

When a test is added that kills a known survivor, without a new scan:

```sh
python3 assets/update_ledger.py --ledger docs/mutation-test/ledger.json \
  --resolve <id> --status killed --commit <sha> --note "test added in PR #123"
```

Use `--status equivalent` to retire a provably equivalent mutant, or `--status wontfix` to accept
it. The next scan still re-runs a killed mutant; if it survives again it becomes `regressed`.

## Edge cases

- **Mutant diff is stale**: recreate it against the current code before re-running; the id survives
  line drift but not a file move.
- **Module loses its tests**: survivors become `not-run` for that scan; record the reason.
- **Missing `commit`**: skip the git check for that entry and record the reason.
- **Ledger grows large**: closed entries are kept; filter by `status`, do not prune silently.
