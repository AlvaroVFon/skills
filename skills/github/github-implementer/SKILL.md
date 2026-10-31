---
name: github-implementer
description: "Trigger: implement GitHub issue, github implementer, implement triaged issue, AI_triage_done. Implements one triaged issue in a worktree and opens a linked PR."
license: MIT
metadata:
  author: AlvaroVFon
  version: "1.1"
---

## Activation Contract

Load this skill when asked to **implement triaged GitHub issues**, or on a recurring `/loop` or `/schedule` run, from inside the target repository. Invocation: `/github-implementer [repo="owner/name"]`; without `repo`, use the `origin` remote. One issue per run.

## Hard Rules

- NEVER work outside the resolved repo; if it cannot be resolved, STOP before any `gh` call.
- ONLY consider open issues with `AI_triage_done`, assigned to the token user (`gh api user`) and without `status:in-progress`. Ignore the rest silently: no comment, no label.
- NEVER comment on an issue not assigned to the current user; never repeat an unmet-requirements comment that matches the latest one.
- ALWAYS read `type:*` and `estimate:*` from labels, never from the triage comment: labels are the contract, the comment is context.
- ALWAYS claim with `status:in-progress` before working, and drop the candidate if the branch already exists in `origin`.
- ALWAYS work in a new worktree on a new branch from freshly fetched `origin/<main>`. NEVER touch the user's tree, push to `main`, force push, or merge.
- ALWAYS follow repo conventions (`AGENTS.md`, `CONTRIBUTING*`, recent branches); if `main` or the branch naming is undeterminable, STOP and comment.
- NEVER push or open a PR while lint, format, typecheck or tests fail.
- ALWAYS start AI-written text with `AI_GENERATED`; issue comments in Spanish, PR body in English.
- ALWAYS deliver with `AI_implemented` (keeping labels), a 2–3 line comment mentioning `@{assignee}` and `@{author}`, and a PR body ending in `Closes #N`.
- ALWAYS remove the worktree after delivery; NEVER after a failed verification or push, and NEVER delete the branch.
- Use `create-commit` and `create-pr` when installed, else follow their rules inline; answer the target-branch question with `main`.

## Decision Gates

| Situation                                            | Action                                            |
| ---------------------------------------------------- | ------------------------------------------------- |
| No `estimate:*`, no `type:*`, or an open blocker     | Comment once; next candidate                      |
| No candidate passes                                  | Report `nothing to do`                            |
| `estimate:1h` – `estimate:8h`                        | Implement directly                                |
| `estimate:13h` or `estimate:21h`                     | Planner subagent, then follow its plan            |
| Planner returns `blocked: true`                      | Comment; keep `status:in-progress`; stop          |
| `type:feature`, `type:maintenance`, `type:tech-debt` | TDD                                               |
| `type:docs`, `type:analysis`, untestable behavior    | Skip TDD; say why in `## Validation`              |
| Verification fails                                   | No push, no PR; comment; keep worktree and branch |

## Execution Steps

1. **Context**: resolve `repo` and the token login; bootstrap missing labels from `references/gh-recipes.md`.
2. **Candidates**: `gh issue list --assignee @me --label AI_triage_done --state open --search "sort:created-asc"`; gate each by estimate and open blockers.
3. **Claim**: add `status:in-progress`; abort the candidate if its branch exists in `origin`.
4. **Worktree**: `git fetch origin`; `git worktree add <path> -b <branch> origin/<main>`; work only inside it.
5. **Plan** at 13h+: subagent with `assets/planner-prompt.md`; on `blocked`, comment and stop.
6. **Implement** with TDD per the gate, until the issue's acceptance criteria are met.
7. **Verify**: discover and run lint, format, typecheck and tests; fix and re-run until all pass.
8. **Deliver**: `create-commit`, push, `create-pr` with base `main` and `Closes #N`.
9. **Close out**: `AI_implemented` plus the completion comment from `assets/comments.md`.
10. **Clean up** from the main repository: `git worktree remove <path>`; report and leave it if it refuses.
11. **Report** the run.

## Output Contract

One compact row: `issue | outcome (implemented / blocked / failed / nothing to do) | branch | worktree (path, removed yes/no) | PR | verification | reason`. The output is read unattended.

## References

- `references/gh-recipes.md` — labels, `gh` commands, worktree and verification commands.
- `assets/planner-prompt.md` — subagent prompt for issues of 13h or more.
- `assets/comments.md` — comment templates: unmet requirements, failure, completion.
