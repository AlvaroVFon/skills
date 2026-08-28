---
name: create-commit
description: "Trigger: commit, git commit, make a commit, write a commit message, crear un commit, conventional commit. Create conventional commit messages as type(scope): subject and commit via git."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill when asked to commit changes or write a commit message. It produces a Conventional Commits subject `type(scope): subject`, validates it, stages the relevant files, and commits.

## Hard Rules

- ALWAYS use the strict Conventional Commits format: `<type>(<scope>): <subject>`.
- Use ONLY the valid types listed in `references/conventional-commits.md` (feat, fix, refactor, perf, test, docs, chore, ci, style, build).
- Keep the full subject line <=72 chars: lowercase, imperative, no trailing period; scope is a short descriptive module/area name with no spaces.
- ALWAYS validate the message with `python3 assets/validate_commit_message.py` and fix every `ERROR` until exit 0, then commit.
- Stage only relevant changes with `git add`; never stage secrets, junk, or unrelated changes.
- Commit messages and skill output are in English.
- NEVER run `git push` unless the user explicitly asks.

## Decision Gates

| Change in the working tree                    | type token |
| --------------------------------------------- | ---------- |
| New feature or behavior                       | feat       |
| Bug fix                                       | fix        |
| Code restructure, no behavior change          | refactor   |
| Performance improvement                       | perf       |
| Tests only                                    | test       |
| Docs / comments only                          | docs       |
| Build tooling, formatting, chores, dependencies | chore/ci/style/build |

| Validation output                 | Action                            |
| --------------------------------- | --------------------------------- |
| `ERROR:` lines present            | Fix reported issues, re-validate   |
| `WARNING:` only / script exits 0  | `git commit`                      |
| No changes or nothing to commit   | Abort; report clean tree          |

## Execution Steps

1. Run `git status` and `git diff` (staged and unstaged) to understand the changes; pick the files to include.
2. Derive type, scope, and subject from those changes; file paths hint at the scope (module, component, area).
3. Redact the subject `<type>(<scope>): <subject>` — imperative, lowercase, <=72 chars.
4. Validate with `python3 assets/validate_commit_message.py --message "<subject>"`; fix errors until exit 0.
5. Run `git add <files>` and commit with `git commit -m "<subject>"` (or `-F` message file).
6. Confirm with `git log -1 --oneline` and confirm explicitly that no push was performed.

## Output Contract

Return:

- The commit hash and subject line created.
- Validation result (script exit 0, any warnings).
- Confirmation: "no push performed".

## References

- `references/conventional-commits.md` — spec: allowed types, scope and subject rules, examples.
- `assets/validate_commit_message.py` — validation script for the commit message.