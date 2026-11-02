# Plan contract

One issue per run. Return only JSON, with no prose and no code fence. Never persist the plan.

## Inputs

- Issue: reference, title, body, acceptance criteria, comments, and the triage comment (task type, factor scores, original estimate).
- The rubric result that triggered the call.

## Reading the code

- Read every file the issue names or implies before deciding anything.
- If the working tree is dirty or on another branch, read against `origin/<default>` (`git show origin/<default>:<path>`) and say so in `notes`.
- Never define a change to a file you have not read.

## The question

**Is this issue one deliverable or several?**

| Verdict   | When                                                      | Deliverables |
| --------- | --------------------------------------------------------- | ------------ |
| `single`  | One deliverable, even when it needs many steps.           | 1            |
| `split`   | Two to six deliverables, each independently shippable.    | 2–6          |
| `spike`   | The approach is unknown and research must come first.     | 0            |
| `blocked` | The issue is ambiguous in a way that prevents a decision. | 0            |

Rules:

- A deliverable is not a step. "Añadir la migración" is a step; "Persistir suscripciones" is a deliverable.
- Each deliverable must be independently verifiable and scorable at 8h or less with the estimation rubric. A `single` deliverable above 8h is allowed only when its parts are not independently shippable, and `reason` must say why.
- Order deliverables so dependencies come first. `dependsOn` lists earlier 0-based positions only, never itself or a later one.
- Each deliverable carries enough content for someone who never read the parent: objective, scope, changes, acceptance criteria and tests.
- Do not invent scope. If the parent does not cover it, leave it out.
- If the parent cannot be split below 8h, return `spike` or `blocked`, never a fake split.

Triage renders these fields into its `assets/subtask-description.md` template: `objective` → Objetivo, `scope` → Alcance, `changes` → Cambios Técnicos, `acceptance` → Criterios de Aceptación, `tests` → Pruebas, `notes` → Notas.

```json
{
  "mode": "scope",
  "verdict": "split",
  "reason": "<why this verdict, in Spanish>",
  "deliverables": [
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

`single` returns exactly one deliverable with `"dependsOn": []`. `spike` and `blocked` return `"deliverables": []`; `blocked` adds `"questions": ["<question>"]`.

## Validation

Run `python3 assets/validate_plan.py --file <plan.json>` and fix every `ERROR:` until it prints `OK`.
