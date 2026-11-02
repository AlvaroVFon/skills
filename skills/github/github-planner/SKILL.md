---
name: github-planner
description: "Trigger: plan a GitHub issue, assess issue scope, split decision, define deliverables. Defines an issue's deliverables or decides it must be split."
license: MIT
metadata:
  author: AlvaroVFon
  version: "2.0"
---

## Activation Contract

Load this skill when asked to **assess a GitHub issue** or **decide whether it must be split**, or when `github-triage` delegates to it. Invocation: `/github-planner issue="owner/repo#N"`. One issue per run.

## Hard Rules

- NEVER write: no `gh` mutation, no label, no issue, no assignee, no file edit, no state-changing command.
- NEVER set or change `type:*`, `estimate:*` or any triage label: you inform the decision, triage owns it.
- Read the code before deciding. Do not invent files, components or contracts.
- Cover only what the issue asks. List anything else in `notes`.
- Return deliverables, never implementation steps: each is independently shippable, verifiable and scorable at 8h or less.
- If the issue cannot be assessed without guessing, do not guess: return the blocking questions.

## Decision Gates

| Verdict   | When                                                      | Deliverables |
| --------- | --------------------------------------------------------- | ------------ |
| `single`  | One deliverable, even when it needs many steps.           | 1            |
| `split`   | Two to six deliverables, each independently shippable.    | 2–6          |
| `spike`   | The approach is unknown and research must come first.     | 0            |
| `blocked` | The issue is ambiguous in a way that prevents a decision. | 0            |

## Execution Steps

1. **Read** the issue, its acceptance criteria, comments, the triage comment and `references/plan-contract.md`.
2. **Read the code** the issue names or implies before deciding anything.
3. **Define** the deliverable or deliverables: objective, scope, changes, acceptance criteria, tests and estimate.
4. **Validate**: `python3 assets/validate_plan.py --file <plan.json>` until it prints `OK`.
5. **Return** only the JSON. Never persist it anywhere.

## Output Contract

Return ONLY the JSON defined in `references/plan-contract.md`. No prose, no markdown fence.

## References

- `references/plan-contract.md` — verdicts, JSON schema, reading rules.
- `assets/validate_plan.py` — plan validator (exit 0 and `OK`).
