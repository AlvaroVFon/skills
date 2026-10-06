# 01 — Scan Modes

## Definition

- **Global**: cover the whole repo by risk, not uniformly.
- **Targeted**: mutate only the selected files/modules and report their direct tests.

Coverage must always be declared: what was mutated, how many mutants, and what was skipped.

## Choosing the Scan Type (Mandatory)

Ask with the option selector (question tool) before any work, every run — never infer the mode from the prompt:

1. **Mode**: `Global` (whole repo) or `Targeted` (named paths/modules). If `Targeted`, request the paths in the same round.
2. **Mutation categories** (multi-select, from `02-mutation-catalog.md`): `high`, `medium`, `low` priority families, or `all`. Generate only the chosen operators in step 5.
3. **Output format**: `chat` (concise summary) or `markdown` (full rendered report) — never both. The JSON report is written either way.

If the question tool is unavailable, ask in chat and wait for the answer.

## Output Format

The report is always persisted as `docs/mutation-test/{YYYY-MM-DD}.json`. The human view is shown in the chat only: `chat` returns the concise summary; `markdown` runs `assets/render_report.py --json <report.json>` and pastes its stdout. Never write a `.md` file and never show both views.

## Global — Risk Map

Reconnaissance returns every module with a risk rank and its test status. Rank by the highest signal present.

| Signal                                      | Risk   |
| ------------------------------------------- | ------ |
| Money, billing, balances, quotas            | High   |
| Auth, permissions, tokens, sessions         | High   |
| Persistence writes, migrations, queues      | High   |
| Validation, state machines, business rules  | High   |
| Parsing, serialization, date/time handling  | Medium |
| External I/O wrappers, mappers              | Medium |
| Pure transforms, DTOs, config, presentation | Low    |

Deepen High modules first, then Medium while budget remains. Low modules are listed as **not reviewed**.

The previous report adjusts this ranking: modules with survivors, unreviewed modules, and files changed since its commit move up (`references/06-baseline-history.md`).

## Caps

| Scope    | Cap                                             |
| -------- | ----------------------------------------------- |
| Module   | 15 mutants, spread over its public entry points |
| Global   | 60 mutants in total, High modules first         |
| Targeted | 15 mutants per given module                     |

The user may raise or lower a cap; record the cap used in the report.

## Targeted — Flow Selection

1. Resolve each path to files containing domain logic.
2. Map each file to the tests that exercise it; those tests are the only ones run per mutant.
3. Stop at the module boundary; note crossings as out of scope.

## Reconnaissance Output

The subagent returns facts, not verdicts: module map, risk rank, files with logic, code→test mapping, test framework, command to run one test file, and baseline status if known.

## Edge Cases

- **Monorepo**: treat each package as a module; rank packages first.
- **Module without tests**: do not mutate; list under "not covered" (every mutant would survive trivially).
- **Generated or vendored code**: skip and list under not reviewed.
- **Slow suite**: run only the mapped tests per mutant; run the full scope suite once for the baseline.
