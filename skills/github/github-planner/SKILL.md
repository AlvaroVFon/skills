---
name: github-planner
description: "Trigger: plan a GitHub issue, plan implementation, assess issue scope, split decision. Plans an issue or decides whether it must be split."
license: MIT
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Load this skill when asked to **plan a GitHub issue** or **assess whether it must be split**, or when `github-triage` or `github-implementer` delegates to it. Invocation: `/github-planner mode="scope|implementation" issue="owner/repo#N"`. One issue per run.

## Hard Rules

- NEVER write: no `gh` mutation, no label, no issue, no assignee, no file edit, no state-changing command.
- NEVER set or change `type:*`, `estimate:*` or any triage label: you inform the decision, triage owns it.
- Read the code before planning. Name only files that exist; every new path goes in `creates`.
- Cover only what the issue asks. List anything else in `outOfScope`.
- In `scope` mode return deliverables, never implementation steps: each subtask is independently shippable, verifiable and scorable at 8h or less.
- If the issue cannot be planned without guessing, do not guess: return the blocking questions.

## Decision Gates

| Mode             | Question answered                              | Output                       |
| ---------------- | ---------------------------------------------- | ---------------------------- |
| `scope`          | Is this one deliverable or several?            | `single` / `split` / `spike` |
| `implementation` | In what order do I build this one deliverable? | ordered `steps`              |

| Situation                                  | Action                         |
| ------------------------------------------ | ------------------------------ |
| Scope is one deliverable                   | `verdict: single`, no subtasks |
| Scope is several deliverables              | `verdict: split`, 2–6 subtasks |
| Approach unknown; research must come first | `verdict: spike`, no subtasks  |
| Ambiguous in a way that blocks the work    | `verdict: blocked`, questions  |

## Execution Steps

1. **Read** the issue, its acceptance criteria, comments and triage comment, plus `references/plan-contract.md`.
2. **Read the code** the issue names or implies before deciding anything.
3. **Plan** at the granularity of the mode: deliverables in `scope`, ordered steps in `implementation`.
4. **Validate**: `python3 assets/validate_plan.py --file <plan.json>` until it prints `OK`.
5. **Return** only the JSON. Never persist it anywhere.

## Output Contract

Return ONLY the JSON for the requested mode, as `references/plan-contract.md` defines. No prose, no markdown fence.

## References

- `references/plan-contract.md` — modes, JSON schemas, reading rules.
- `assets/validate_plan.py` — plan validator (exit 0 and `OK`).
