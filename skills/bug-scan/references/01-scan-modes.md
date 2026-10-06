# 01 — Scan Modes

## Definition

- **Global**: cover the whole repo by risk, not uniformly.
- **Targeted**: cover only the selected paths/modules and their direct callers/callees.

Coverage must always be declared: what was reviewed, in what depth, and what was skipped.

## Choosing the Scan Type (Mandatory)

Ask with the option selector (question tool) before any work, every run — never infer the mode from the prompt:

1. **Mode**: `Global` (whole repo) or `Targeted` (named paths/modules). If `Targeted`, request the paths in the same round.
2. **Categories** (multi-select): `logic` (`02`), `concurrency` (`03`), `errors-resources` (`04`), `data-integrity` (`05`), or `all`. Load only the chosen references in step 4.
3. **Output format**: `chat` (concise summary) or `markdown` (full rendered report) — never both. The JSON report is written either way.

If the question tool is unavailable, ask in chat and wait for the answer.

## Output Format

The report is always persisted as `docs/bug-scan/{YYYY-MM-DD}.json`. The human view is shown in the chat only: `chat` returns the concise summary; `markdown` runs `assets/render_report.py --json <report.json>` and pastes its stdout. Never write a `.md` file and never show both views.

## Global — Risk Map

Reconnaissance returns every module with a risk rank. Rank by the highest signal present.

| Signal                                      | Risk   |
| ------------------------------------------- | ------ |
| Money, billing, balances, quotas            | High   |
| Auth, permissions, tokens, sessions         | High   |
| Persistence writes, migrations, queues      | High   |
| Shared mutable state, caches, singletons    | High   |
| External I/O (HTTP, files, third parties)   | Medium |
| Parsing, serialization, date/time handling  | Medium |
| Pure transforms, DTOs, config, presentation | Low    |

Deepen High modules first, then Medium while budget remains. Low modules are listed as **not reviewed** unless trivially covered.

The previous report adjusts this ranking: unreviewed or shallowly reviewed modules and files changed since its commit move up (`references/08-baseline-history.md`).

## Targeted — Flow Tracing

1. Resolve each path to its public entry points.
2. Trace one level up (callers) to learn real inputs, and down (dependencies) to learn failure modes.
3. Stop at the module boundary; note crossings as out of scope.

## Reconnaissance Output

The subagent returns facts, not verdicts: module map (global) or flow map (targeted), entry points, callers, external dependencies, test framework, test location, and the command to run one test file.

## Edge Cases

- **Monorepo**: treat each package as a module; rank packages first.
- **No test framework found**: every finding becomes Unconfirmed with manual steps; say so in the summary.
- **Generated or vendored code**: skip and list under not reviewed.
- **Huge module**: scan its public entry points first; list the remainder as not reviewed.
