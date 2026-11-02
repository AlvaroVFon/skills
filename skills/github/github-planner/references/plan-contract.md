# Plan contract

One issue per run. Return only JSON, with no prose and no code fence. Never persist the plan.

## Inputs

- `mode`: `scope` or `implementation`.
- Issue: reference, title, body, acceptance criteria, comments, and the triage comment (task type, factor scores, original estimate).
- In `scope` mode, the rubric result that triggered the call.

## Reading the code

- Read every file the issue names or implies before deciding anything.
- If the working tree is dirty or on another branch, plan against `origin/<default>` (`git show origin/<default>:<path>`) and say so in `notes`.
- Never plan a change to a file you have not read.

## scope mode

Answer one question: **is this issue one deliverable or several?**

| Verdict   | When                                                        |
| --------- | ----------------------------------------------------------- |
| `single`  | One deliverable, even when it needs many steps.             |
| `split`   | Two to six deliverables, each independently shippable.      |
| `spike`   | The approach is unknown and research must come first.       |
| `blocked` | The issue is ambiguous in a way that prevents any decision. |

Rules:

- A subtask is a deliverable, not a step. "Añadir la migración" is a step; "Persistir suscripciones" is a deliverable.
- Each subtask must be independently verifiable and scorable at 8h or less with the estimation rubric.
- Order subtasks so dependencies come first. `dependsOn` lists earlier 0-based positions only, never itself or a later one.
- Each subtask carries enough content for someone who never read the parent: objective, scope, changes, acceptance criteria and tests.
- Do not invent scope. If the parent does not cover it, leave it out.
- If the parent cannot be split below 8h, return `spike` or `blocked`, never a fake split.

Triage renders these fields into its `assets/subtask-description.md` template: `objective` → Objetivo, `scope` → Alcance, `changes` → Cambios Técnicos, `acceptance` → Criterios de Aceptación, `tests` → Pruebas, `notes` → Notas.

```json
{
  "mode": "scope",
  "verdict": "split",
  "reason": "<why this verdict, in Spanish>",
  "subtasks": [
    {
      "summary": "<short imperative title>",
      "objective": "<max three sentences>",
      "scope": ["<included change>", "<relevant limit>"],
      "changes": ["<component, flow or contract to modify>"],
      "acceptance": [
        {
          "id": "AC-1",
          "given": "<initial condition>",
          "when": "<action>",
          "then": "<expected result>"
        }
      ],
      "tests": ["<test to add or update>"],
      "notes": "<dependencies, risks, or empty>",
      "type": "Documentación | Análisis | Mantenimiento | Deuda técnica | Funcionalidad",
      "dependsOn": [],
      "estimate": "1h | 2h | 3h | 5h | 8h"
    }
  ]
}
```

`single` and `spike` return `"subtasks": []`. `blocked` adds `"questions": ["<question>"]`.

## implementation mode

Plan the ordered steps for one deliverable that is already decided.

Rules:

- Each step names the files to change and the test that proves it.
- `files` lists only paths that already exist; every new path goes in `creates`.
- TDD: the failing test comes first, unless the issue is Documentación or Análisis.
- Cover only what the issue asks; list the rest in `outOfScope`.
- Flag data, API, security or rollback decisions in `notes`.
- If a decision blocks the work, return `blocked` with the questions.

```json
{
  "mode": "implementation",
  "blocked": false,
  "steps": [
    {
      "title": "<short imperative title>",
      "files": ["<existing path>"],
      "creates": ["<new path>"],
      "test": "<test that proves the step>",
      "notes": "<risks or decisions, or empty>"
    }
  ],
  "outOfScope": ["<observation>"],
  "questions": []
}
```

When blocked: `"blocked": true`, `"steps": []`, and a non-empty `questions` list.

## Validation

Run `python3 assets/validate_plan.py --file <plan.json>` and fix every `ERROR:` until it prints `OK`.
