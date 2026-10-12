# 02 — Mutation Catalog

## Definition

A mutant is a small, plausible, syntactically valid change to domain logic. Pick operators where a surviving mutant reveals a real test gap.

## Operators

| Operator           | Example                                         | Priority |
| ------------------ | ----------------------------------------------- | -------- |
| Boundary           | `<` → `<=`, `>=` → `>`                          | High     |
| Conditional        | condition → `true` / `false`                    | High     |
| Logical            | `&&` ↔ `\|\|`, remove `!`                       | High     |
| Arithmetic         | `+` ↔ `-`, `*` ↔ `/`, `+=` → `-=`               | High     |
| Statement removal  | delete a side-effect call (save, emit, `await`) | High     |
| Return value       | return `null` / empty / `0` / negated bool      | Medium   |
| Literal / constant | `0` ↔ `1`, `true` ↔ `false`, string → `""`      | Medium   |
| Branch removal     | drop an `else`, early `return`, or `case`       | Medium   |
| Argument           | swap or drop an argument in a domain call       | Low      |

## Selection Rules

- One operator per mutant; one mutant per distinct line of logic.
- Spread mutants across functions and entry points; do not stack them in one function.
- Prefer lines whose change alters observable behavior (return value, state, side effect).

## Exclusions

- Logging, metrics, comments, imports, type annotations, config, and pure presentation.
- Defensive code with no observable effect.
- Mutants that fail to compile or parse: discard as Invalid.

## Equivalent Mutants

Discard as Equivalent only when you can state why behavior is identical (for example `i < n` → `i != n` over a strict increment, or reordering commutative operations). If unsure, keep it and let the test result decide.
