# 01 — Scan Modes

## Definition

- **Global**: cover the whole repo by interest (churn × complexity), not uniformly.
- **Targeted**: cover only the selected paths/modules and their direct callers/callees.

Coverage must always be declared: what was reviewed, at what depth, and what was skipped.

## Selector (Mandatory)

Ask with the option selector (question tool) before any work, every run — never infer from the prompt:

1. **Mode**: `Global` or `Targeted`. If `Targeted`, request the paths in the same round.
2. **Categories** (multi-select): `code` (`03`), `tests` (`04`), `architecture-docs-infra` (`05`: report categories `architecture`, `docs`, `infra`), or `all`. Load only the chosen references.
3. **Output format**: `chat` (concise summary) or `markdown` (full rendered report) — never both. The JSON is written either way.

If the question tool is unavailable, ask in chat and wait for the answer.

## Hotspot Map (Global)

Reconnaissance returns every module with: LOC, churn (commits touching it in the last 6 months), distinct authors, and complexity signals. Rank by `churn × complexity`; churn is also the evidence for the `frequency` score (`06`).

| Module profile                       | Interest |
| ------------------------------------ | -------- |
| High churn + high complexity or size | High     |
| High churn + weak tests              | High     |
| Low churn + high complexity          | Medium   |
| Stable, rarely touched, even if ugly | Low      |
| Generated, vendored, config, DTOs    | Skip     |

Deepen High modules first, then Medium while budget remains. Low modules are listed as **not reviewed** unless trivially covered. The previous report adjusts this ranking (`07`).

## Targeted — Flow Tracing

1. Resolve each path to its public entry points.
2. Trace one level up (callers) and down (dependencies) to measure coupling.
3. Stop at the module boundary; note crossings as out of scope.

## Reconnaissance

Delegate to read-only subagents: one recon (`assets/recon-subagent.md`), then one measurement subagent per chosen category (`assets/measure-subagent.md`), at most 3 concurrent. They return facts, never scores or verdicts.

## Edge Cases

- **Monorepo**: treat each package as a module; rank packages first.
- **Shallow git history or no git**: drop churn weighting, say so, and rank by size and complexity only.
- **No analyzer installed**: measure with `git`, `wc`, `grep`, and file reads; never install tools in the repo.
- **Huge module**: assess its public entry points first; list the remainder as not reviewed.
