# 01 — Deep Modules

## Definition

A module is any unit with an interface and an implementation (function, class, service, package, or a whole domain module). Depth = **benefit provided / cost of the interface**. The cost of the interface is the concepts a caller must learn: names, types, parameters, ordering rules, and state.

- **Deep**: powerful functionality behind a small interface (`open/read/write/close` hides filesystems, buffers, and devices).
- **Shallow**: the interface is nearly as complex as the implementation (1:1 wrappers, accessor explosions, an operation that only forwards).

Evaluate this at two granularities:

- **Macro (module boundary)**: what the module exports to other modules (services/use-cases, public DTOs, events, ports).
- **Micro (artifact)**: the interface of each class or function.

Only the public/exported surface counts. Internal artifacts may be as complex as they need to be.

## Signals

**Macro — module boundary**

| Signal                | Test                                                                                            |
| --------------------- | ----------------------------------------------------------------------------------------------- |
| Orchestration leak    | For one external use case, must the caller invoke >1 exported service in an implicit order?     |
| Breadth without value | How many symbols does one consumer import for a single task? ≥4 means a diffuse boundary.       |
| Data plumbing         | Does the caller fetch/assemble data from the module and pass it back in?                        |
| Pass-through export   | Is something exported that only delegates with no boundary value (test seam, port, decoupling)? |

**Micro — artifact**

| Signal                      | Test                                                              |
| --------------------------- | ----------------------------------------------------------------- |
| 1:1 wrapper                 | The body is a single delegation with an identical signature.      |
| Signature ≈ body            | The interface requires as many concepts as the implementation.    |
| Stateful/ordered contract   | The caller must call A→B→C or know the lifecycle.                 |
| Flag/bag as the common path | The common case requires passing booleans or an options bag.      |
| Docs longer than value      | Documenting the interface costs more than what it delivers.       |
| Accessor anemia             | An explosion of getters/setters exposing internal representation. |

## Design Moves

1. Combine low-level operations into one high-level operation that does the common case.
2. Absorb orchestration internally; the caller must not sequence steps.
3. Replace N parameters with a sane default plus an optional override.
4. Remove pass-through layers unless they provide a real abstraction boundary (test seam, port, decoupling).
5. Write the **caller snippet** — the smallest realistic external usage — and read its complexity: short and direct means deep; orchestration and assembly mean shallow.

## Edge Cases

- **Pass-through wrapper**: flag it only when it adds no boundary value. A wrapper that defines a port, enables testing, or decouples a dependency is legitimate.
- **Depth is not size**: never apply "fewer methods is better". Over-splitting into small shallow classes (classitis) is itself the disease.
- **Single responsibility**: depth does not conflict with one clear responsibility. A deep module still has one reason to exist.
- **Documentation cost**: if a short call requires a paragraph of documentation, the interface is too complex.

## Mini-Checklist

- [ ] Every public element has a real consumer or a justified public contract.
- [ ] The common case resolves without parameters, or with domain defaults.
- [ ] One abstraction level per operation; no exposed intermediate steps.
- [ ] Names match the interface nature (domain → ubiquitous, technical → technical).
- [ ] No internal types cross the boundary.
- [ ] One general operation with a domain default, not N near-duplicates or a toggle.
- [ ] The caller snippet is short and free of orchestration.
