---
title: "Planificación y split en el flujo de GitHub: github-planner"
status: "accepted"
date: "2026-11-02"
authors: ["AlvaroVFon"]
---

# Planificación y split en el flujo de GitHub: github-planner

## Context and Problem Statement

El flujo de GitHub encadena `define-issue`, `github-triage`, `github-implementer` y `github-workflow`. Triage estima de forma determinista con `references/estimation-scale.md` a partir del cuerpo del issue y solo parte cuando la puntuación llega a 23 o se estiman más de 500 líneas. El splitter que usa triage lee el issue, pero no el código. El implementer, a partir de 13h, delegaba la planificación en un subagente que sí lee código, pero que solo podía devolver pasos: no podía partir el issue.

El resultado era una asimetría: la fase que puede partir no tiene información, y la fase que lee código no tiene autoridad. La banda 18–22 (13h) se planificaba y nunca se partía, y es justo la banda a la que llegan los overrides de la rúbrica (riesgo 5, cualquier factor 5, tres factores 4 o más). La banda 14–17 (8h) quedaba completamente ciega. El síntoma observado: al llegar a implementer con una tarea compleja, la planificación descubría que el triaje se había quedado corto.

Una primera iteración mantuvo dos planificaciones: `scope` en triage para decidir el split y `implementation` en el implementer para ordenar los pasos. Se descartó porque duplicaba trabajo —el plan de triage se tiraba cuando el veredicto era `single`— y porque el plan de pasos es la parte que caduca: se escribe antes de tocar los tests y contra un `main` que se mueve.

## Decision Drivers

- Una sola autoridad de planificación: el planner, invocado desde triage.
- Mantener a triage como único escritor de `type:*`, `estimate:*` y de los sub-issues.
- Decidir el split con código leído, no solo con el texto del issue.
- No persistir un plan de pasos que caduque entre triage e implementación.
- No añadir labels, estados ni transiciones inversas al contrato actual.
- Que cada skill de GitHub siga funcionando instalada por separado.

## Considered Options

- `github-planner` en triage define los entregables; el implementer decide el cómo con TDD.
- Mantener la planificación de implementación en el implementer, con el planner como subagente.
- Tercera fase `github-planner` entre triage e implementer, con autoridad para partir.
- Planificar en `define-issue`, antes del triage y de la asignación.
- Escalado: el planner del implementer devuelve el issue a `AI_triage` para que se re-triagee.
- Ampliar solo el trigger de split (cualquier factor 5 o riesgo 5) sin planner.

## Decision Outcome

Chosen option: "`github-planner` en triage define los entregables; el implementer decide el cómo con TDD", because concentra la planificación en una sola fase, la que ya lee el issue y puede leer código, sin persistir un plan de pasos que caduque. El planner responde una sola pregunta: si el issue es uno o varios entregables, y en ambos casos devuelve la definición del entregable: objetivo, alcance, cambios, criterios de aceptación y pruebas. Triage conserva la autoridad de labels, estimación y sub-issues. El implementer consume esa definición y decide los pasos con TDD; no planifica ni vuelve a llamar al planner.

### Consequences

- Good, because el split y la definición del entregable se deciden con código leído, y los sub-issues heredan las dependencias del plan en vez de inventarlas desde el cuerpo.
- Good, because desaparece la replanificación: solo hay un planner y un artefacto estable, la definición del entregable.
- Good, because aparece un veredicto `spike` para los casos de enfoque desconocido (factor 5) que antes se convertían en implementación sin investigación previa.
- Good, because triage sigue siendo el único escritor de labels y estimación, y `github-workflow` no cambia.
- Bad, because triage deja de ser barato: leer código por cada issue de 8h o más alarga y encarece la fase batch.
- Bad, because triage no tiene worktree limpio; el planner debe leer contra `origin/<default>` o exigir árbol limpio.
- Bad, because en un entregable `single` grande el implementer decide los pasos sin una guía escrita; es el coste de no tener un plan que caduque.
- Bad, because el umbral solo mueve la frontera de mala clasificación: un issue de 8h que en realidad son tres tareas sigue siendo posible.
- Bad, because el fallback sin planner solo cubre el split, así que un issue de 8h o más sin planner llega al implementer sin definición refinada.

## Hipótesis y validación con datos

La decisión se toma antes de tener datos del flujo actual. Las implementaciones en curso con el flujo anterior son la línea base. Hipótesis a contrastar:

- H1: una parte relevante de los issues en la banda 14–22 (8h–13h) son en realidad varios entregables, y hoy solo se descubre al planificar en el implementer.
- H2: la definición del entregable coincide con lo que el planner del implementer habría descubierto, y reduce PRs sobredimensionados y retrabajo.
- H3: los casos con factor 5 (enfoque desconocido) se benefician de un `spike` y no de una implementación directa.
- H4: quitar el plan de pasos no aumenta el retrabajo ni el tamaño del PR, porque el implementer ya decidía los pasos al ejecutar.

Datos a recoger de la línea base y de las ejecuciones posteriores:

- Estimación original frente a esfuerzo real: tiempo, commits y tamaño del PR.
- Issues en los que la implementación excedió el alcance definido o necesitó cambios fuera de la definición.
- PRs que deberían haber sido varios, medidos por tamaño, comentarios de revisión y retrabajo.
- Splits hechos en triage frente a splits descubiertos tarde.
- Casos de factor 5 que llegaron a implementación sin spike.

Criterio de revisión: si el sobredimensionamiento descubierto tarde es raro, el planner añade coste sin beneficio y este ADR debe supersederse por la opción barata (ampliar solo el trigger de split). Si es frecuente, se mantiene y se evalúa bajar el trigger. Si H4 falla y el retrabajo sube, se reincorpora un plan de implementación, pero generado en el momento de implementar, no en triage. Cualquier cambio de decisión se registra en un ADR nuevo que supersede a este.

## Notas de implementación

- Nuevo skill `skills/github/github-planner/` con un único modo `scope`, contrato en `references/plan-contract.md` y validador `assets/validate_plan.py`.
- `github-triage` v1.2: trigger de planner con puntuación 14 o más, cualquier factor 4 o más, o Líneas 4 o más; veredictos `single`, `split`, `spike` y `blocked`; en `single` publica la definición del entregable como comentario; planner opcional con el splitter actual como fallback.
- `github-implementer` v1.4: consume la definición del entregable y no planifica; se elimina `assets/planner-prompt.md` y el gate de 13h/21h.
- `AGENTS.md` y `README.md` actualizados con el nuevo skill y su validador.

## Actualización 2026-11-03

El contrato del planner incorpora `files` y `estimatedLines` por entregable. Triage los usa como evidencia de código para puntuar `Líneas` y `Módulos`, marca `assumed` cuando falta evidencia y conserva la autoridad del label; la estimación del padre se eleva con la suma de entregables en un `split`. El implementer añade `Métricas:` al comentario de cierre para cerrar el bucle de calibración descrito en este ADR. Versiones: planner v2.1, triage v1.4, implementer v1.5.
