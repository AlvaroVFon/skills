---
name: github-triage
description: "Trigger: GitHub triage, triar issues, backlog triage, estimate issues, AI_triage. Triages labelled GitHub issues and applies the deterministic estimate."
license: MIT
metadata:
  author: AlvaroVFon
  version: "1.2"
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
- ALWAYS plan before splitting: `github-planner` in `scope` mode when installed, else `assets/subtask-splitter-prompt.md`. It never sets labels or estimates.
- NEVER let the planner change the rubric result: it only returns `single`, `split`, `spike` or `blocked`; the estimate stays triage's.
- ALWAYS record dependencies as `blocked by` links, never only in a comment; create only missing links, never edit or remove existing ones.

## Decision Gates

| Situation                                                | Action                                        |
| -------------------------------------------------------- | --------------------------------------------- |
| No `repo`, no `origin` remote, no access                 | Do not run; report                            |
| Initial conditions not met                               | Ignore; count `skipped`                       |
| Planner installed and score 14+, factor 4+, or Líneas 4+ | Planner `scope` mode; act on its verdict      |
| Planner not installed and score 23+ or Líneas 5          | Split via `assets/subtask-splitter-prompt.md` |
| Verdict `split`                                          | Create sub-issues; triage parent              |
| Verdict `single`                                         | Triage the parent; discard the plan           |
| Verdict `spike`                                          | Create one research sub-issue; triage parent  |
| Verdict `blocked`, or splitter `splittable: false`       | Triage the parent; report why                 |
| A write fails                                            | Stop that issue; report `failed`              |

## Execution Steps

1. **Repo**: `repo`, else `git remote get-url origin`; abort if neither yields `owner/name`. Create missing labels per `references/gh-recipes.md`.
2. **Candidates**: `gh issue list --state open --label AI_triage` for the repo and milestone; re-check every condition after fetching.
3. **Assess**: read body, comments and links. Classify the type, score the six factors, map the score to an estimate, mark `assumed`. Resolve dependencies; if a prerequisite has no issue, do not link it and say so in the report.
4. **Plan** when triggered: subagent with `../github-planner/SKILL.md`, `mode="scope"`, the issue and the rubric result; it validates its own JSON. Without the planner, use `assets/subtask-splitter-prompt.md`.
5. **Act** on the verdict: `split` → create each sub-issue from `assets/subtask-description.md` with `AI_triage` and the parent's assignees, attach it, add `blocked by` links and `Depende de: #N` in Notas; `spike` → create one research sub-issue the same way; `single` or `blocked` → no sub-issues.
6. **Apply**: type and estimate labels, remove assignees, comment, swap labels.
7. **Report**: write the table to `${TMPDIR:-/tmp}/opencode/github-triage-report.md`, run `python3 assets/validate_triage_report.py --file <report>` until `OK`, return it.

## Output Contract

One row per issue: `issue | outcome (triaged/split/skipped/failed) | type | factors | score | estimate | links | reason`, with the six factors as `n/5` and `*` on any `assumed` one, closing with `Totals: triaged=N split=N skipped=N failed=N`. `reason` carries the planner verdict or the skip/fail cause. Read unattended: compact, no prose.

## References

- `references/estimation-scale.md` — rubric: task types, six factors, score→estimate.
- `references/gh-recipes.md` — `gh` commands, labels, report path.
- `../github-planner/SKILL.md` — scope planner for the split decision.
- `assets/subtask-splitter-prompt.md` — fallback when the planner is not installed.
- `assets/subtask-description.md` — sub-issue description structure.
- `assets/triage-comment.md` — triage comment template.
- `assets/validate_triage_report.py` — report validator.
