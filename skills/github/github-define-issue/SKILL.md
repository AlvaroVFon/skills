---
name: github-define-issue
description: "Trigger: definir tarea, define issue, create GitHub issue, redactar issue, nueva tarea. Agree a solution with the human and open a triage-ready issue."
license: MIT
metadata:
  author: AlvaroVFon
  version: "1.1"
---

## Activation Contract

Load this skill when a human wants to **define a new task as a GitHub issue**. Invocation: `github-define-issue [repo="owner/name"]`. It is conversational and human-in-the-loop: it never runs unattended and creates at most one issue per run.

## Hard Rules

- NEVER create the issue without explicit approval of the final draft. Show it, then wait.
- ALWAYS interview first: problem, expected result, boundaries, how success is verified, and the security dimensions that apply. One question per turn; never invent answers.
- NEVER draft while the problem or the acceptance criteria are unclear: ask instead.
- ALWAYS verify the current-state and solution premise against the files/endpoints the issue names; if the fix depends on another repository, workflow or tag, name it and include it in scope or ask.
- ALWAYS include `## Seguridad` with the applicable dimensions: authorization scope, tenant isolation, enumeration, token/session revocation, rate limiting and secrets/PII. If none apply, write `No aplica: <reason>`.
- ALWAYS build the body from `assets/issue-template.md`, in Spanish, first line `AI_GENERATED`.
- ALWAYS keep the title imperative and 72 characters or fewer.
- ALWAYS label the new issue `AI_triage` and assign at least one owner: triage skips unassigned issues, so an unassigned issue never enters the cycle.
- NEVER set `type:*`, `estimate:*`, `AI_triage_done`, `status:*` or `AI_implemented`: triage and the implementer own those labels.
- ALWAYS search duplicates by title keywords and by the paths/endpoints the task touches, across open and recently closed issues and PRs; show overlaps and ask whether to link or continue.
- ALWAYS validate the body with `assets/validate_issue_body.py` before creating; fix every `ERROR:` until it prints `OK`.
- Create exactly one issue per run. Splitting is triage's job when the estimate is very high.

## Decision Gates

| Situation                              | Action                                    |
| -------------------------------------- | ----------------------------------------- |
| Problem or acceptance criteria unclear | Ask; do not draft                         |
| Premise contradicted by code           | Ask; do not draft                         |
| Security dimension unanswered          | Ask; do not draft                         |
| Human rejects the draft                | Revise; never create                      |
| Duplicate issue found                  | Show it; ask whether to link or continue  |
| Validator prints `ERROR:`              | Fix and re-validate                       |
| No assignee agreed                     | Ask; never create unassigned              |
| Human asks to implement it now         | Out of scope: hand off to `github-triage` |

## Execution Steps

1. **Repo**: resolve `repo` (invocation or `origin`); stop if neither.
2. **Interview**: problem, who it affects, expected result, out of scope, how success is verified, and applicable security dimensions. Stop when answered.
3. **Premise**: read the files/endpoints the issue names; confirm the current state and the proposed fix. If they contradict the draft, ask.
4. **Duplicates**: search title keywords plus touched paths/endpoints across open and recently closed issues and PRs.
5. **Draft**: title plus body from `assets/issue-template.md`, including `## Seguridad`.
6. **Review**: show the draft and ask for changes; repeat until approved.
7. **Validate**: `python3 assets/validate_issue_body.py --body <file> --title "<title>"` until `OK`.
8. **Create**: `gh issue create --title "<title>" --body-file <file> --label AI_triage --assignee "<login>"`.
9. **Report** the issue number, URL and the next step.

## Output Contract

Return `issue | title | labels | assignee | URL`, plus `duplicate: <#N or none>`. State that `github-triage` picks the issue up on its next run.

## References

- `assets/issue-template.md` — objective, description, security and acceptance criteria.
- `assets/validate_issue_body.py` — body validator (exit 0 and `OK`).
- `references/gh-recipes.md` — `gh` commands, labels, duplicate search.
