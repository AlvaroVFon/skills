---
name: code-review
description: "Trigger: code review, review a PR, review a diff, review changes, request changes, approve PR, GitHub review. Review pull requests and diffs via the gh CLI."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.2"
---

## Activation Contract

Use this skill when asked to review a pull request, review a diff, review changes on a branch, post GitHub review comments, request changes, or approve a PR. Review is read-only; it never modifies the author's code.

## Hard Rules

- ALWAYS use the `gh` CLI for every GitHub interaction: reading PR/diff, inline comments, `request changes`, and `approve`.
- ALWAYS post every finding as an inline comment anchored to its diff line (`path` + `line`). The review body carries only the summary and counters; a finding that exists only in the body is an incomplete review.
- NEVER run linter, typecheck, or test commands (`eslint`, `tsc`, `mypy`, `npm test`, `pytest`, `go test`, …). Execution belongs to CI; review the code statically and read the tests, never run them.
- NEVER run a merge. Never merge, squash-merge, or rebase a PR under any circumstance.
- If any Blocking/high-severity finding exists, post `request changes`; never approve until it is fixed.
- Review the diff against its base branch; do not audit the whole codebase.
- Flag only issues introduced by or directly affected by the diff; skip pre-existing untouched code.
- Cite `file:line` with concrete code and verify claims before reporting; no speculation.
- Communicate the review in English.

## Decision Gates

| Severity                 | `event` in the reviews API call |
| ------------------------ | ------------------------------- |
| Any Blocking finding     | `REQUEST_CHANGES`               |
| Only Should/Nit findings | `COMMENT`                       |
| No findings              | `APPROVE`                       |

| Context                          | Diff source               |
| -------------------------------- | ------------------------- |
| PR number known / gh repo active | `gh pr diff <n>`          |
| Local branch vs remote base      | `git diff <base>...HEAD`  |
| Uncommitted changes              | `git diff` or staged diff |

## Execution Steps

1. Identify the PR or branch and its base with `gh pr view <n>` (or `git`); confirm the working repo.
2. Read the full diff and, for each file, the surrounding context (imports, callers, related functions) to understand intent.
3. Classify each finding by severity — Blocking (bug, security, correctness, broken contract → must fix), Should (maintainability, best practice), Nit (style, optional) — and record `[Severity] file:line — issue + suggested fix`, keeping the line as an added/context line present in the diff.
4. Run holistic checks across the whole change: missing tests, security, performance, and consistency with the PR's stated intent. Read the relevant test code; do not execute any suite.
5. Post the review in ONE `gh api --method POST repos/{owner}/{repo}/pulls/<n>/reviews --input <file>` call: `event` (`COMMENT`|`REQUEST_CHANGES`|`APPROVE`), `body` (summary + counters only), optional `commit_id` (head SHA), and `comments`: one `{path, line, body}` entry per finding, with `line` taken from the diff. Never fall back to a body-only review. The `event` field is required — omitting it creates a PENDING review that silently blocks subsequent reviews (discard it with `gh api -X DELETE .../reviews/<id>`).
6. Confirm the action taken, that every finding was posted inline, that no merge was performed, and that no linter, typecheck, or test command was executed.

## Output Contract

Return:

- One-line summary of the change and the verdict (approve / needs changes).
- Findings grouped by file in `[Severity] file:line — issue + suggested fix`, ordered Blocking → Should → Nit, mirroring the inline comments.
- Counters: Blocking, Should, Nit, plus the number of inline comments posted.
- The exact `gh` command executed and its result, plus the phrases "no merge performed" and "no linter, typecheck, or test command executed".

## References

- `references/review-checklist.md` — detailed categories to scan during the review.
