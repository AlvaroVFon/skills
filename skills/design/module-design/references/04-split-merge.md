# 04 — Split or Merge Artifacts

## Definition

The only criterion is **total complexity**: split only if it **reduces** complexity; otherwise combine. Splitting adds interface surface and coordination; it must buy more than it costs. Apply this at every granularity: module boundaries, classes, and method extraction (extract method).

## Decision Gate

| Direction | Signal                                                                   |
| --------- | ------------------------------------------------------------------------ |
| **Split** | The pieces can be understood and used independently.                     |
| **Split** | The pieces operate at different levels of abstraction.                   |
| **Split** | A general mechanism is mixed with specific policy.                       |
| **Merge** | Conjoined methods: one cannot be understood without the other.           |
| **Merge** | Splitting would duplicate knowledge (leakage).                           |
| **Merge** | The pieces share code or data.                                           |
| **Merge** | The cut follows execution order, not knowledge (temporal decomposition). |

When the evidence is genuinely ambiguous: **one class**.

## Design Moves

1. **Merge** conjoined methods into one; do not split what must be read together.
2. **Extract** specific policy out of a general mechanism (separate layers), rather than interleaving them.
3. If you split, split **by knowledge or abstraction level**, never by time.
4. At method level, apply the same gate before extracting: does extraction reduce complexity or only move it?

## Edge Cases

- **General vs specific**: a general mechanism and specific policy must not coexist in the same artifact. Separate them into layers, with specific policy building on the general one.
- **Abstraction levels**: mixing high-level policy and low-level mechanism in one artifact is a split signal.
- **Duplication vs shared primitive**: duplicated logic argues for merging; a stable, explicit shared primitive (see `02-information-hiding.md`) does not.
- **Conjoined methods**: if you must read A to understand B, keep them together even if each looks small.
- **Classitis**: many small shallow classes increase complexity and are a merge signal.

## Mini-Checklist

- [ ] The split reduces total complexity (fewer concepts, no leakage, no duplication).
- [ ] When ambiguous, the artifacts are kept together (one class).
- [ ] General mechanism and specific policy are not mixed.
- [ ] No artifact mixes different levels of abstraction.
- [ ] No conjoined methods were separated.
- [ ] The cut, if any, follows knowledge rather than execution order.
