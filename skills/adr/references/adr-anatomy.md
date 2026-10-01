# ADR Anatomy

An Architectural Decision (AD) is a justified design choice that addresses an architecturally significant requirement. Its record (ADR) captures the single decision and its rationale. Do not take "architecture" too strictly: any choice that shapes structure, key quality attributes, or is costly to reverse qualifies.

## When to record

- Technology, framework, or library selection.
- Module boundaries, interfaces, or responsibility splits (e.g. from a `module-design` brief).
- Data model, persistence, or integration strategy decisions.
- Choices that are hard to reverse or that future readers will question.

## When not to record

- Trivial, local, or trivially reversible code choices.
- Pure implementation detail with no cross-cutting impact.
- Decisions already captured and unchanged (reference the existing ADR instead).

## Required frontmatter

| Field     | Purpose                                                              |
| --------- | -------------------------------------------------------------------- |
| `title`   | Short, states solved problem + chosen solution; also the H1.         |
| `status`  | `proposed`, `accepted`, `rejected`, `deprecated`, or `superseded`.   |
| `date`    | `YYYY-MM-DD` of the last update.                                     |
| `authors` | Who made or wrote the decision (name or handle).                     |

Optional, add only when relevant: `supersedes` and `superseded-by` links, plus `deciders`, `consulted`, or `informed` when stakeholders must be tracked.

## Body elements

- **Context and Problem Statement** — traceability: which module, PR, or issue; the forces at play.
- **Considered Options** — real alternatives at the same abstraction level; no pseudo-options.
- **Decision Outcome** — chosen option by name plus justification tied to a driver.
- **Consequences** — `Good, because …` / `Bad, because …`; never hide tradeoffs.
