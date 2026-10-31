---
name: github-triage
description: "Trigger: GitHub triage, triar issues, backlog triage, estimate issues, AI_triage. Triages labelled GitHub issues and applies the deterministic estimate."
license: MIT
metadata:
  author: AlvaroVFon
  version: "1.1"
---

## Activation Contract

Load this skill when asked to **triage GitHub issues**, or on a recurring `/loop` or `/schedule` run. Invocation: `/github-triage repo="owner/name" [milestone="..."]`; without `repo`, use the `origin` remote.

## Hard Rules

- NEVER work outside the resolved repo; if it cannot be resolved, STOP before any `gh` call and show the usage line.
- ONLY triage issues that are open, have a body, at least one assignee, label `AI_triage`, and none of `AI_triage_done`, `status:in-progress`, `status:blocked`, a linked pull request. Ignore the rest: no comment, no edit, no label.
- ALWAYS estimate with `references/estimation-scale.md`: task type, then the six factors. Never by feel, never outside the scale.
- ALWAYS leave a triaged issue with `type:<value>`, `estimate:<value>`, zero assignees, and `AI_triage` replaced by `AI_triage_done`.
- ALWAYS write `type:*` from the rubric classification, replacing any previous `type:*`; it is the only source the implementer trusts for TDD and branch naming.
- ALWAYS write estimate, then unassign, then comment, then labels. A failure marks that issue `failed` and keeps `AI_triage`: `AI_triage_done` is NEVER applied to a partial result, and one issue failing NEVER stops the batch.
- ALWAYS comment once, only on triaged issues, from `assets/triage-comment.md`, first line `AI_GENERATED`.
- Sub-issues meet the same initial conditions; the subagent only proposes, this skill creates them, and they are NEVER triaged in the same run.
- ALWAYS record dependencies as `blocked by` links, never only in a comment; create only missing links, never edit or remove existing ones.

## Decision Gates

| Situation                                | Action                                               |
| ---------------------------------------- | ---------------------------------------------------- |
| No `repo`, no `origin` remote, no access | Do not run; report                                   |
| Initial conditions not met               | Ignore; count `skipped`                              |
| Score 23+ or Líneas 5                    | Split via subagent, create sub-issues, triage parent |
| Subagent returns `splittable: false`     | Triage the parent; report why                        |
| A write fails                            | Stop that issue; report `failed`                     |

## Execution Steps

1. **Repo**: `repo`, else `git remote get-url origin`; abort if neither yields `owner/name`. Create missing labels per `references/gh-recipes.md`.
2. **Candidates**: `gh issue list --state open --label AI_triage` for the repo and milestone; re-check every condition after fetching.
3. **Assess**: read body, comments and links. Classify the type, score the six factors, map the score to an estimate, mark `assumed`. Resolve dependencies; if a prerequisite has no issue, do not link it and say so in the report.
4. **Split** when triggered: subagent with `assets/subtask-splitter-prompt.md`; create each sub-issue from `assets/subtask-description.md` with `AI_triage` and the parent's assignees, attach it, add `blocked by` links and `Depende de: #N` in Notas.
5. **Apply**: type and estimate labels, remove assignees, comment, swap labels.
6. **Report**: write the table to `${TMPDIR:-/tmp}/opencode/github-triage-report.md`, run `python3 assets/validate_triage_report.py --file <report>` until `OK`, return it.

## Output Contract

One row per issue: `issue | outcome (triaged/split/skipped/failed) | type | factors | score | estimate | links | reason`, with the six factors as `n/5` and `*` on any `assumed` one, closing with `Totals: triaged=N split=N skipped=N failed=N`. Read unattended: compact, no prose.

## References

- `references/estimation-scale.md` — rubric: task types, six factors, score→estimate.
- `references/gh-recipes.md` — `gh` commands, labels, report path.
- `assets/subtask-splitter-prompt.md` — subagent prompt for oversized issues.
- `assets/subtask-description.md` — sub-issue description structure.
- `assets/triage-comment.md` — triage comment template.
- `assets/validate_triage_report.py` — report validator.
