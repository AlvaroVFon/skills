---
name: github-triage
description: "Trigger: GitHub triage, triar issues, backlog triage, estimate issues, AI_triage. Triages labelled GitHub issues and applies the deterministic estimate."
license: MIT
metadata:
  author: AlvaroVFon
  version: "1.4"
---

## Activation Contract

Load this skill when asked to **triage GitHub issues**, or on a recurring or scheduled run. Invocation: `github-triage repo="owner/name" [milestone="..."]`; without `repo`, use the `origin` remote.

## Hard Rules

- NEVER work outside the resolved repo; if it cannot be resolved, STOP before any `gh` call and show the usage line.
- ONLY triage issues that are open, have a body, at least one assignee, label `AI_triage`, and none of `AI_triage_done`, `status:in-progress`, `status:blocked`, a linked pull request. Ignore the rest: no comment, no edit, no label.
- ALWAYS estimate with `references/estimation-scale.md`: type, then six factors. When the planner runs, use its `files`, `estimatedLines` and `changes` as code evidence for `Líneas`/`Módulos`; the final score and labels are triage's. Mark `assumed` when a factor has no evidence.
- ALWAYS leave a triaged issue with `type:<value>`, `estimate:<value>`, zero assignees, and `AI_triage` replaced by `AI_triage_done`.
- ALWAYS write `type:*` from the rubric, replacing any previous one; it is the only source the implementer trusts for TDD and branch naming.
- ALWAYS write estimate, unassign, comment, labels. A failure marks that issue `failed` and keeps `AI_triage`; `AI_triage_done` is never applied to a partial result, and one failure never stops the batch.
- ALWAYS comment once, only on triaged issues, from `assets/triage-comment.md`, first line `AI_GENERATED`.
- Sub-issues share the initial conditions; the planner proposes, this skill creates them, and they are never triaged in the same run.
- ALWAYS assess with `github-planner`; without it, use `assets/subtask-splitter-prompt.md`. It never writes labels; reject a `single` above 500 lines or 8h without a reason; on `split`, sum deliverable estimates for the parent, never below the score band.
- ALWAYS record dependencies as `blocked by` links, never only in a comment; create missing links, never edit existing ones.

## Decision Gates

| Situation                                                | Action                                          |
| -------------------------------------------------------- | ----------------------------------------------- |
| No repo, no origin, no access                            | Do not run; report                              |
| Initial conditions not met                               | Ignore; count `skipped`                         |
| Planner installed and score 14+, factor 4+, or Líneas 4+ | Assess with the planner; act on its verdict     |
| Planner output lacks `files`/`estimatedLines`            | Ignore it; fall back; mark factors `assumed`    |
| Planner not installed and score 23+ or Líneas 5          | Split via `assets/subtask-splitter-prompt.md`   |
| Verdict `split`                                          | Create sub-issues; triage parent                |
| Verdict `single`                                         | Post the deliverable definition; triage parent  |
| Verdict `spike`                                          | Create one research sub-issue; block the parent |
| Verdict `blocked`, or splitter `splittable: false`       | Triage the parent; report why                   |
| A write fails                                            | Stop that issue; report `failed`                |

## Execution Steps

1. **Repo**: `repo`, else `git remote get-url origin`; abort if neither yields `owner/name`. Create missing labels per `references/gh-recipes.md`.
2. **Candidates**: `gh issue list --state open --label AI_triage` for the repo and milestone; re-check every condition and flag an open issue/PR covering the same paths/endpoints.
3. **Assess**: read body, comments and links; classify, score, map to estimate, mark `assumed`; resolve dependencies.
4. **Define** when triggered: planner (subagent/inline) with issue and rubric; require and validate `files`/`estimatedLines`; score `Líneas`/`Módulos` from them. Without planner, use the splitter and mark unsupported factors `assumed`.
5. **Act**: `split` → create sub-issues from `assets/subtask-description.md` with `AI_triage` and parent assignees, attach, add `blocked by` and `Depende de: #N`; `single` → post `deliverables[0]` as `## Definición del entregable`; `spike` → one research sub-issue, block parent; `blocked` → record questions.
6. **Apply**: estimate from the score band, raised by the planner sum when available; type label; remove assignees; comment; swap labels.
7. **Report**: write the table to `${TMPDIR:-/tmp}/skills/github-triage/report.md` (`mkdir -p` its directory), run `python3 assets/validate_triage_report.py --file <report>` until `OK`, return it.

## Output Contract

One row per issue: `issue | outcome (triaged/split/skipped/failed) | type | factors | score | estimate | links | reason`, with six `n/5` factors and `*` on any `assumed`, closing with `Totals: triaged=N split=N skipped=N failed=N`. `reason` carries the planner verdict or skip/fail cause.

## References

- `references/estimation-scale.md` — rubric and score→estimate.
- `references/gh-recipes.md` — `gh` commands, labels, report path.
- `../github-planner/SKILL.md` — deliverable and split decision.
- `assets/subtask-splitter-prompt.md` — planner fallback.
- `assets/subtask-description.md` — sub-issue description structure.
- `assets/triage-comment.md` — triage comment template.
- `assets/validate_triage_report.py` — report validator.
