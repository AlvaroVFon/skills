---
name: adr
description: "Trigger: ADR, decision record, documentar decision, architecture decision, design decision. Write architecture/design decision records."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to record an architecturally or design-significant decision, create an ADR, or extract decisions already made from a conversation, PR, diff, or module-design brief. Do not use it for trivial, reversible, or purely local code choices.

## Hard Rules

- One decision per ADR; never bundle unrelated choices.
- Every ADR carries frontmatter: `title`, `status`, `date`, `authors` (see `assets/adr-template.md`). Add `supersedes`/`superseded-by` only when relevant.
- Context, considered options, and justification are mandatory; a record without rationale is invalid.
- Append-only: NEVER edit an accepted ADR. Create a new record that supersedes it and link both.
- ALWAYS ask the destination before writing (`docs/decisions/`, `docs/adr/`, Confluence, Jira, or inline) unless the repo convention is unambiguous.
- Write in the destination's language; keep records concise, assertive, and factual.

## Decision Gates

| Fork                                  | Action                                                                  |
| ------------------------------------- | ----------------------------------------------------------------------- |
| Not architecturally significant       | Omit; do not create an ADR                                              |
| New decision vs change to an existing | New `NNNN` record vs new record with `supersedes` link                  |
| Destination                           | Detect `docs/decisions`/`docs/adr`, else ask; or Confluence/Jira/inline |
| Options need deep analysis            | Minimal template by default; add per-option pros/cons on request        |

## Execution Steps

1. Confirm the decision, its scope, and the destination.
2. For a repo target, detect `docs/decisions/` or `docs/adr/`; compute the next `NNNN` and file name `NNNN-title-with-dashes.md`.
3. Fill `assets/adr-template.md`; load `references/adr-anatomy.md` only if significance is unclear.
4. Validate context, options, justification, and consequences; load `references/adr-lifecycle.md` for status/supersede rules.
5. Write via the destination: local file, the available Confluence/Jira integration, or an inline block for manual paste.
6. Return the destination reference and confirm no existing ADR was modified.

## Output Contract

Return: destination (path, URL, or inline block); ADR number; chosen option; status; confirmation that no existing ADR was edited.

## References

- `references/adr-anatomy.md`
- `references/adr-lifecycle.md`
- `assets/adr-template.md`
