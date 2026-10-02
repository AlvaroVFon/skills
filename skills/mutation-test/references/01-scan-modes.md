# 01 — Scan Modes

## Definition

- **Global**: no paths given. Cover the repo by risk, not uniformly.
- **Targeted**: the user names paths or modules. Mutate only those files and report their direct tests.

Coverage must always be declared: what was mutated, how many mutants, and what was skipped.

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

The previous report adjusts this ranking: modules with survivors, unreviewed modules, and files changed since its commit move up (`references/05-scan-memory.md`).

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
