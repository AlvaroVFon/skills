---
name: code-review
description: "Trigger: code review, review a PR, review a diff, review changes, request changes, approve PR, GitHub review. Review pull requests and diffs via the gh CLI."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.1"
---

## Activation Contract

Use this skill when asked to review a pull request, review a diff, review changes on a branch, post GitHub review comments, request changes, or approve a PR. Review is read-only; it never modifies the author's code.

## Hard Rules

- ALWAYS use the `gh` CLI for every GitHub interaction: reading PR/diff, inline comments, `request changes`, and `approve`.
- NEVER run a merge. Never merge, squash-merge, or rebase a PR under any circumstance.
- If any Blocking/high-severity finding exists, post `request changes`; never approve until it is fixed.
- Review the diff against its base branch; do not audit the whole codebase.
- Flag only issues introduced by or directly affected by the diff; skip pre-existing untouched code.
- Cite `file:line` with concrete code and verify claims before reporting; no speculation.
- Communicate the review in English.

## Decision Gates

| Severity                      | gh action                                   |
| ----------------------------- | ------------------------------------------- |
| Any Blocking finding          | `gh pr review <n> --request-changes --body` |
| Only Should/Nit findings      | `gh pr review <n> --comment --body`         |
| No findings                   | `gh pr review <n> --approve --body`         |

| Context                          | Diff source                |
| -------------------------------- | -------------------------- |
| PR number known / gh repo active | `gh pr diff <n>`           |
| Local branch vs remote base      | `git diff <base>...HEAD`   |
| Uncommitted changes              | `git diff` or staged diff  |

## Execution Steps

1. Identify the PR or branch and its base with `gh pr view <n>` (or `git`); confirm the working repo.
2. Read the full diff and, for each file, the surrounding context (imports, callers, related functions) to understand intent.
3. Classify each finding by severity — Blocking (bug, security, correctness, broken contract → must fix), Should (maintainability, best practice), Nit (style, optional) — and record `[Severity] file:line — issue + suggested fix`.
4. Run holistic checks across the whole change: missing tests, security, performance, and consistency with the PR's stated intent.
5. Post the review with `gh`: build the body from the Output Contract, then call `gh pr review <n> --comment|--request-changes|--approve --body <file>`. For inline comments, POST JSON via `gh api --method POST repos/{owner}/{repo}/pulls/<n>/reviews --input <file>` with `event` (`COMMENT`|`REQUEST_CHANGES`|`APPROVE`), optional `body` and `commit_id` (head SHA), and `comments`: `[{path, line, body}]` with `line` numbers taken from the diff. The `event` field is required — omitting it creates a PENDING review that silently blocks subsequent reviews (discard it with `gh api -X DELETE .../reviews/<id>`).
6. Confirm the action taken and confirm that no merge was performed.

## Output Contract

Return:

- One-line summary of the change and the verdict (approve / needs changes).
- Findings grouped by file in `[Severity] file:line — issue + suggested fix`, ordered Blocking → Should → Nit.
- Counters: Blocking, Should, Nit.
- The exact `gh` command executed and its result, plus the phrase "no merge performed".

## References

- `references/review-checklist.md` — detailed categories to scan during the review.
