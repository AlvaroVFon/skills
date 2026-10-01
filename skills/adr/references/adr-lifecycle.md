# ADR Lifecycle

## Statuses

| Status       | Meaning                                                            |
| ------------ | ------------------------------------------------------------------ |
| `proposed`   | Drafted, not yet agreed.                                           |
| `accepted`   | Agreed and in effect.                                              |
| `rejected`   | Considered but not adopted.                                        |
| `deprecated` | No longer relevant, but not replaced.                              |
| `superseded` | Replaced by a newer ADR (link via `superseded-by`).                |

## Append-only rule

An ADR is a log, not a living document. Once `accepted`, do NOT rewrite it. If the decision changes, write a new ADR and:

1. Set `status: superseded` and `superseded-by: "NNNN-title"` on the old record.
2. Set `supersedes: "NNNN-title"` on the new record.
3. Keep both files so the history of reasoning is preserved.

The same rule applies when the record lives in Confluence or Jira: create a new page/issue and link the old one.

## Numbering and file naming

- Pattern: `NNNN-title-with-dashes.md`, e.g. `0007-adopt-madr.md`.
- `NNNN` is the next free sequence number (assume fewer than 10,000 ADRs).
- Title is lowercase with dashes, mirroring the frontmatter `title`.
- One decision per file.

## Where records live

- Repository: prefer an existing `docs/decisions/` or `docs/adr/` folder; if the repo already uses one, follow it. If neither exists, ask the user.
- Confluence / Jira: only when no repo convention exists or the user chooses it; use the available integration and keep the same frontmatter-derived metadata in the page/issue fields.
- Inline: produce the full record so the user can paste it into the chosen system.
