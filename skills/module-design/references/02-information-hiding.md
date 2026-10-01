# 02 — Information Hiding

## Definition

Each module encapsulates a few design decisions: its data representation, algorithms, mechanisms, protocols, and policies. The interface should hide those decisions so that other modules depend on **what** it does, not **how** it does it. The central enemy is **information leakage**: the same design decision is reflected in more than one module, creating a hidden dependency.

Two forms of leakage:

- **Interface leakage**: the decision is visible in the signature or the return value.
- **Back-door leakage**: the decision is not in the interface, but two modules **assume** the same thing (format, unit, ordering, global config).

A related anti-pattern is **temporal decomposition**: splitting work by order of execution instead of by knowledge, which guarantees leakage.

## Signals

| Signal                  | Test                                                                                            |
| ----------------------- | ----------------------------------------------------------------------------------------------- |
| Duplicated knowledge    | The same constant, rule, or validation appears in 2+ places.                                    |
| Interface leakage       | The signature or return exposes an internal representation.                                     |
| Format/order assumption | Another module assumes a format, unit, or order defined inside.                                 |
| Change amplification    | Changing one internal decision forces changes in another module or artifact.                    |
| Temporal decomposition  | The module is divided by execution steps, not by knowledge.                                     |
| Back-door coupling      | Implicit assumptions (global config, date format, enum values) are undeclared in the interface. |
| Tell-Don't-Ask broken   | The caller requests internal data and decides based on it.                                      |

Check leakage at both scopes: **across modules** (the boundary) and **across internal artifacts** of the same module.

## Design Moves

1. Give each decision a **single home** and expose an operation that expresses **intent**.
2. Apply **Tell, Don't Ask**: the module performs the behavior instead of returning data for the caller to act on.
3. Encapsulate the representation and expose domain operations.
4. Replace a temporal split with a split **by knowledge** (see `04-split-merge.md`).
5. Keep interfaces free of internal types: no ORM entities, internal DTOs, or framework types.

## Edge Cases

- **Shared domain primitives**: a shared value object or a shared kernel is legitimate only when it is a **stable, explicit contract** — not a filtered implementation detail.
- **Temporal decomposition**: forbidden as a split criterion. If a cut follows execution order, it will leak knowledge.
- **Events**: publishing an event can hide knowledge, but a poorly shaped event leaks internal state; the event payload is part of the interface.
- **Global configuration**: reading a global config inside a module is back-door coupling unless it is passed and declared.

## Mini-Checklist

- [ ] Every design decision has exactly one home.
- [ ] The interface expresses intent, not mechanism.
- [ ] No interface leakage (no internal representation in signatures or returns).
- [ ] No back-door leakage (no undeclared shared assumptions).
- [ ] Behavior is exposed, not raw data (Tell, Don't Ask).
- [ ] No internal types cross the boundary.
- [ ] The split, if any, follows knowledge rather than execution order.
