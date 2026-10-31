# Estimation rubric

Deterministic: same issue → same estimate. Follow the three steps in order. Never estimate by feel.

## 1. Task type (base score)

Classify into exactly one type. If it fits several, pick the one that describes the main deliverable.

| Type          | Base |
| ------------- | ---- |
| Documentación | 0    |
| Análisis      | 0    |
| Mantenimiento | 1    |
| Deuda técnica | 1    |
| Funcionalidad | 2    |

## 2. Complexity factors (0–5 each)

Score each factor with the highest level whose criteria the issue meets.

| Level | Complejidad técnica                 | Riesgo de los cambios                                      | Terceros                                             | Tiempo estimado  |
| ----- | ----------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------- | ---------------- |
| 0     | Mechanical change, no decisions     | None                                                       | None                                                 | < 2 h            |
| 1     | Trivial tweak of existing code      | Negligible, trivially reverted                             | Known library or SDK already in use                  | Up to half a day |
| 2     | Known pattern, minor adaptation     | Low: isolated change                                       | New library or dependency                            | Up to 1 day      |
| 3     | Design decisions needed             | Medium: alters existing behavior                           | Another internal team to coordinate with             | Up to 2 days     |
| 4     | New pattern or architecture         | High: data, security, or public API                        | External service or API integration                  | 3–5 days         |
| 5     | Unknown approach, research or spike | Critical: billing, data loss possible, or hard to rollback | New vendor, unknown API, or contract/approval needed | More than 5 days |

### Líneas de código estimadas

Estimated lines added or modified (production and tests; exclude generated code and lockfiles).

| Level | Lines   |
| ----- | ------- |
| 0     | < 10    |
| 1     | 10–50   |
| 2     | 51–150  |
| 3     | 151–400 |
| 4     | 401–500 |
| 5     | > 500   |

### Módulos implicados (número y criticidad)

`n` = modules touched, `c` = critical modules among them. Critical module = auth, payments, data persistence, public API, or anything the team marks critical.

| Level | Criteria                                         |
| ----- | ------------------------------------------------ |
| 0     | n = 1, c = 0                                     |
| 1     | n = 2, c = 0                                     |
| 2     | n = 3, c = 0, or n = 1, c = 1                    |
| 3     | n ≥ 4, c = 0, or c = 2                           |
| 4     | c = 3, or n ≥ 5 with c ≥ 1                       |
| 5     | c ≥ 4, or cross-cutting change across the system |

## 3. Score → original estimate

`score = base + sum(factors)` (range 0–32)

| Score | Original estimate |
| ----- | ----------------- |
| 0–3   | 1h                |
| 4–6   | 2h                |
| 7–9   | 3h                |
| 10–13 | 5h                |
| 14–17 | 8h                |
| 18–22 | 13h               |
| 23+   | 21h               |

21h = very high complexity → delegate to a subagent for sub-issues.

Split trigger: Líneas = 5 (> 500 lines) → delegate to a subagent for sub-issues even if the score is below 23. The estimate comes from the score and overrides.

## Rules

- Score every factor. If the issue lacks the information to score one, score it 3 and list it as `assumed` in the report.
- Overrides (apply the highest minimum that matches; never lower the score-based estimate):
  - Riesgo = 4 → estimate never below 5h. Riesgo = 5 → estimate never below 8h.
  - Any factor = 5 → estimate never below 13h.
  - Three or more factors at level 4 or above → estimate never below 13h.
  - Two or more factors at level 5 → 21h (delegate to subagent).
- Never assign values outside the scale.
- The report MUST include type, each factor score, total score, and original estimate so the result can be audited.
