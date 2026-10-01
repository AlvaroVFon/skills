---
name: module-design
description: "Trigger: module design, analyze module, module architecture, deep modules, information hiding. Design or refactor domain module boundaries and interfaces."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill to design, modify, or analyze the design of a **module**: a group of artifacts under one domain (NestJS-style, OOP). Apply when creating a module, changing its public interface, reviewing coupling or leakage, or deciding whether to split or merge artifacts. Not for implementation details or one-off code.

## Hard Rules

**Deep modules** — only the public/exported surface counts; every public element needs a real consumer or justified contract; the common case has no friction (no params or sane domain defaults); one abstraction level per operation, no exposed intermediate steps; name by interface nature (domain → ubiquitous, technical → technical), never mixed; no internal types cross the boundary; prefer one general operation with a domain default over near-duplicates, never a toggle/bag.

**Information hiding** — Tell, Don't Ask; report _interface_ and _back-door_ leakage separately; check leakage across modules and internal artifacts; shared domain primitives only as a stable, explicit contract; temporal decomposition is forbidden as a split criterion.

**Pull complexity downwards** — every parameter justifies why it cannot be a default or auto-detected; normalize internal errors into domain failures; absorb only the module's responsibility and decide variable policy once at a high point (DI/strategy); always define the failure contract.

**Split or merge** — split only if it reduces total complexity, else combine; when in doubt, one class; never mix a general mechanism with specific policy; applies to boundaries and method extraction.

**Cross-cutting** — always write the caller snippet (smallest realistic external usage); state responsibility in one sentence or the boundary is wrong; ALWAYS ask the output format (`{module}.md`, `adr`, `inline`); write the brief in the conversation language and code in the repo language.

**Reconnaissance** — when the module spans many files, delegate exploration (artifacts, callers, duplicated knowledge) to an exploration subagent when available; keep the gate judgments yourself.

## Decision Gates

| Principle                 | Reference                                    | Observable signal                                                             |
| ------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------- |
| Deep modules              | `references/01-deep-modules.md`              | Caller orchestrates calls; pass-through exports; signature ≈ body             |
| Information hiding        | `references/02-information-hiding.md`        | Same knowledge in 2+ places; representation revealed; implicit assumptions    |
| Pull complexity downwards | `references/03-pull-complexity-downwards.md` | Parameter that could default; internal error taxonomy; caller derives data    |
| Split or merge            | `references/04-split-merge.md`               | Conjoined/duplicated (merge) vs general/specific or mixed abstraction (split) |

Load only the reference for the principle under evaluation.

## Execution Steps

1. Confirm scope (create / modify / analyze), module boundary, and destination repo language.
2. State the module responsibility in one sentence.
3. Write the caller snippet (smallest realistic external usage).
4. Evaluate the four gates, loading references on demand; emit a verdict per granularity (macro and micro): deep / acceptable / shallow.
5. Detect leakages (interface vs back-door), over-configuration, and temporal decomposition.
6. Apply the split-or-merge gate by net complexity.
7. ALWAYS ask the output format: `{module}.md`, `adr`, or `inline`.
8. Emit the brief from `assets/module-design-brief.md`; a full before/after interface only when shallow.

## Output Contract

Return the Module Design Brief (or inline equivalent): responsibility; public interface signatures; encapsulated decisions; complexity absorbed and failure contract; split-or-merge decision; depth verdict macro/micro with the caller snippet; leakage flags; improvements, with a full before/after interface only when shallow.

## References

- `references/01-deep-modules.md`
- `references/02-information-hiding.md`
- `references/03-pull-complexity-downwards.md`
- `references/04-split-merge.md`
- `assets/module-design-brief.md`
