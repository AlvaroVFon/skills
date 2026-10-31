---
name: define-issue
description: "Trigger: definir tarea, define issue, create GitHub issue, redactar issue, nueva tarea. Agrees a solution with the human and opens a triage-ready issue."
license: MIT
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Load this skill when a human wants to **define a new task as a GitHub issue**: `/define-issue [repo="owner/name"]`. It is conversational and human-in-the-loop: it never runs unattended and creates at most one issue per run.

## Hard Rules

- NEVER create the issue without explicit approval of the final draft. Show it, then wait.
- ALWAYS interview first: problem, expected result, boundaries, how success is verified. One question per turn; never invent answers.
- NEVER draft while the problem or the acceptance criteria are unclear: ask instead.
- ALWAYS build the body from `assets/issue-template.md`, in Spanish, first line `AI_GENERATED`.
- ALWAYS keep the title imperative and 72 characters or fewer.
- ALWAYS label the new issue `AI_triage` and assign at least one owner: triage skips unassigned issues, so an unassigned issue never enters the cycle.
- NEVER set `type:*`, `estimate:*`, `AI_triage_done`, `status:*` or `AI_implemented`: triage and the implementer own those labels.
- ALWAYS search for duplicates before creating; if one exists, show it and ask whether to link or continue.
- ALWAYS validate the body with `assets/validate_issue_body.py` before creating; fix every `ERROR:` until it prints `OK`.
- Create exactly one issue per run. Splitting is triage's job when the estimate is very high.

## Decision Gates

| Situation                              | Action                                    |
| -------------------------------------- | ----------------------------------------- |
| Problem or acceptance criteria unclear | Ask; do not draft                         |
| Human rejects the draft                | Revise; never create                      |
| Duplicate issue found                  | Show it; ask whether to link or continue  |
| Validator prints `ERROR:`              | Fix and re-validate                       |
| No assignee agreed                     | Ask; never create unassigned              |
| Human asks to implement it now         | Out of scope: hand off to `github-triage` |

## Execution Steps

1. **Repo**: resolve `repo` (invocation or `origin`); stop if neither.
2. **Interview**: problem, who it affects, expected result, what is out of scope, how success is verified. Stop as soon as those are answered.
3. **Duplicates**: `gh issue list --state open --search "<keywords>"`.
4. **Draft**: title plus body from `assets/issue-template.md`.
5. **Review**: show the draft and ask for changes; repeat until approved.
6. **Validate**: `python3 assets/validate_issue_body.py --body <file> --title "<title>"` until `OK`.
7. **Create**: `gh issue create --title "<title>" --body-file <file> --label AI_triage --assignee "<login>"`.
8. **Report** the issue number, URL and the next step.

## Output Contract

Return `issue | title | labels | assignee | URL`, plus `duplicate: <#N or none>`. State that `github-triage` picks the issue up on its next run.

## References

- `assets/issue-template.md` — objective, description and acceptance criteria.
- `assets/validate_issue_body.py` — body validator (exit 0 and `OK`).
- `references/gh-recipes.md` — `gh` commands, labels, duplicate search.
