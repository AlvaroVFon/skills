---
title: "Planificación y split en el flujo de GitHub: github-planner"
status: "accepted"
date: "2026-11-02"
authors: ["AlvaroVFon"]
---

# Planificación y split en el flujo de GitHub: github-planner

## Context and Problem Statement

El flujo de GitHub encadena `define-issue`, `github-triage`, `github-implementer` y `github-workflow`. Triage estima de forma determinista con `references/estimation-scale.md` a partir del cuerpo del issue y solo parte cuando la puntuación llega a 23 o se estiman más de 500 líneas. El splitter que usa triage lee el issue, pero no el código. El implementer, a partir de 13h, delega la planificación en un subagente que sí lee código, pero que solo puede devolver pasos: no puede partir el issue.

El resultado es una asimetría: la fase que puede partir no tiene información, y la fase que lee código no tiene autoridad. La banda 18–22 (13h) se planifica y nunca se parte, y es justo la banda a la que llegan los overrides de la rúbrica (riesgo 5, cualquier factor 5, tres factores 4 o más). La banda 14–17 (8h) queda completamente ciega. El síntoma observado: al llegar a implementer con una tarea compleja, la planificación descubre que el triaje se quedó corto.

## Decision Drivers

- Mantener a triage como único escritor de `type:*`, `estimate:*` y de los sub-issues.
- Decidir el split con código leído, no solo con el texto del issue.
- No añadir labels, estados ni transiciones inversas al contrato actual.
- Que cada skill de GitHub siga funcionando instalada por separado.
- No convertir el plan en un contrato rígido que el implementer no pueda corregir.

## Considered Options

- `github-planner` read-only, delegado por triage en modo `scope` y por el implementer en modo `implementation`; triage conserva la autoridad de split y de labels.
- Tercera fase `github-planner` entre triage e implementer, con autoridad para partir.
- Escalado: el planner del implementer devuelve el issue a `AI_triage` para que se re-triagee.
- Ampliar solo el trigger de split (cualquier factor 5 o riesgo 5) sin planner.
- Extraer el planner a skill sin darle capacidad de split.

## Decision Outcome

Chosen option: "`github-planner` read-only, delegado por triage en modo `scope` y por el implementer en modo `implementation`; triage conserva la autoridad de split y de labels", because mueve la decisión de split a la fase que lee código sin sacar de triage la propiedad de los labels ni de los sub-issues, y no introduce estados nuevos. El planner informa; triage decide y sigue aplicando la rúbrica. El implementer usa el mismo contrato en modo `implementation` y mantiene su prompt embebido como fallback cuando el planner no está instalado.

### Consequences

- Good, because el split se decide con código leído y los sub-issues heredan las dependencias del plan, en vez de inventarlas desde el cuerpo.
- Good, because aparece un veredicto `spike` para los casos de enfoque desconocido (factor 5) que hoy se convierten en implementación sin investigación previa.
- Good, because triage sigue siendo el único escritor de labels y estimación, y `github-workflow` no cambia.
- Bad, because triage deja de ser barato: leer código por cada issue de 8h o más alarga y encarece la fase batch.
- Bad, because triage no tiene worktree limpio; el planner debe planificar contra `origin/<default>` o exigir árbol limpio.
- Bad, because el plan se descarta cuando el veredicto es `single`, así que el implementer vuelve a planificar: hay trabajo duplicado por diseño.
- Bad, because el umbral solo mueve la frontera de mala clasificación: un issue de 8h que en realidad son tres tareas sigue siendo posible.
- Bad, because conviven dos copias del prompt de planificación (planner y fallback) que deben mantenerse sincronizadas.

## Hipótesis y validación con datos

La decisión se toma antes de tener datos del flujo actual. Las implementaciones en curso con el flujo anterior son la línea base. Hipótesis a contrastar:

- H1: una parte relevante de los issues en la banda 14–22 (8h–13h) son en realidad varios entregables, y hoy solo se descubre al planificar en el implementer.
- H2: el veredicto `scope` coincide con lo que el planner del implementer habría descubierto, y reduce PRs sobredimensionados y retrabajo.
- H3: los casos con factor 5 (enfoque desconocido) se benefician de un `spike` y no de una implementación directa.

Datos a recoger de la línea base y de las ejecuciones posteriores:

- Estimación original frente a esfuerzo real: tiempo, commits y tamaño del PR.
- Issues en los que el plan del implementer excedió el alcance del issue o generó muchos pasos y ficheros.
- PRs que deberían haber sido varios, medidos por tamaño, comentarios de revisión y retrabajo.
- Splits hechos en triage frente a splits descubiertos tarde.
- Casos de factor 5 que llegaron a implementación sin spike.

Criterio de revisión: si el sobredimensionamiento descubierto tarde es raro, el planner añade coste sin beneficio y este ADR debe supersederse por la opción barata (ampliar solo el trigger de split). Si es frecuente, se mantiene y se evalúa bajar el trigger o añadir un veredicto de split explícito. Cualquier cambio de decisión se registra en un ADR nuevo que supersede a este.

## Notas de implementación

- Nuevo skill `skills/github/github-planner/` con modos `scope` e `implementation`, contrato en `references/plan-contract.md` y validador `assets/validate_plan.py`.
- `github-triage` v1.2: trigger de planner con puntuación 14 o más, cualquier factor 4 o más, o Líneas 4 o más; veredictos `single`, `split`, `spike` y `blocked`; planner opcional con el splitter actual como fallback; la estimación no cambia.
- `github-implementer` v1.3: planner en modo `implementation`; `assets/planner-prompt.md` queda como fallback.
- `AGENTS.md` y `README.md` actualizados con el nuevo skill y su validador.
