---
name: create-pr
description: "Trigger: create a PR, open a pull request, publish a PR, hacer un PR, GitHub pull request. Create validated standardized PR descriptions via the gh CLI."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.1"
---

## Activation Contract

Use this skill when asked to create, open, or publish a pull request. It produces a standardized PR description and posts it via the `gh` CLI.

## Hard Rules

- ALWAYS use the `gh` CLI for the whole flow: `gh pr create`, `gh pr view`, `gh repo view`.
- NEVER run a merge. Never merge, squash-merge, or rebase a PR under any circumstance.
- ALWAYS build the body from `references/pr-template.md` and write it in English.
- ALWAYS validate the final body with `python3 assets/validate_pr_description.py`; fix every `ERROR` until exit 0, then create the PR.
- Do not create the PR until the current branch is pushed and the working tree is clean of relevant uncommitted changes.

## Decision Gates

| Condition                                 | Action                               |
| ----------------------------------------- | ------------------------------------ |
| Script output has `ERROR:` lines          | Fix the reported issues, re-validate |
| Script exits 0                            | `gh pr create` with body file        |
| Branch unpushed or `gh` not authenticated | Abort; report the blocker            |
| No base branch resolved                   | Abort; ask for the base branch       |

## Execution Steps

1. Detect the repo, current branch, and base branch with `gh repo view` and `git branch --show-current`; resolve the base (e.g. `main`/`master`).
2. Read `git diff <base>...HEAD` to derive the objective and relevant context.
3. Draft the body following `references/pr-template.md`; keep the title to 72 chars max.
4. Write the body to a temp file and run `python3 assets/validate_pr_description.py --body <file> --title "<title>"`.
5. Fix any `ERROR:` lines and re-run until exit 0 (warnings may remain but are explained).
6. Create the PR: `gh pr create --base <base> --head <branch> --title "<title>" --body-file <file>`.
7. Return the PR URL and confirm explicitly that no merge was performed.

## Output Contract

Return:

- The created PR URL and its title.
- The validation result (script exit 0, any warnings).
- Confirmation: "no merge performed".

## References

- `references/pr-template.md` — standardized PR description template.
- `assets/validate_pr_description.py` — validation script for the PR body.
