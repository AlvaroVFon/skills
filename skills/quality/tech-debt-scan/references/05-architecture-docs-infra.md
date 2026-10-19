# 05 — Architecture, Docs, Infra

Categories `architecture`, `docs`, `infra`. Classify each finding with a symptom/cause from `02`.

## Architecture (mostly `dependency`)

| Signal                   | How to measure                                                          | Debt when                                                  | Symptom              |
| ------------------------ | ----------------------------------------------------------------------- | ---------------------------------------------------------- | -------------------- |
| Layer violations         | Grep imports crossing declared layers (UI → DB, domain → I/O)           | Violates the layering the repo itself documents or implies | change-amplification |
| Circular dependencies    | Analyzer, else trace imports between module pairs                       | Cycle between modules                                      | change-amplification |
| Leaky boundaries         | Internals imported from outside the module; same decision in 2+ modules | Bypasses the module's public entry point                   | unknown-unknowns     |
| Shared mutable globals   | Grep singletons, module-level state, static caches                      | Written from many modules                                  | unknown-unknowns     |
| Parallel implementations | Two modules solving the same problem                                    | Both still wired in                                        | cognitive-load       |

## Docs (mostly `obscurity`)

| Signal                 | How to measure                                                 | Debt when                                            | Symptom          |
| ---------------------- | -------------------------------------------------------------- | ---------------------------------------------------- | ---------------- |
| Drift                  | Compare README/docs commands, paths, env vars against the code | Documented command, path, or variable does not exist | unknown-unknowns |
| Missing entry docs     | README lacks setup, run, test steps                            | A new contributor cannot start from it               | cognitive-load   |
| Undocumented decisions | Core design choice with no ADR or comment                      | Choice is non-obvious and hard to reverse            | unknown-unknowns |

## Infra (mostly `obscurity`)

| Signal             | How to measure                                                | Debt when                                        | Symptom              |
| ------------------ | ------------------------------------------------------------- | ------------------------------------------------ | -------------------- |
| Fragile build/CI   | Read pipeline files; unpinned tool versions, manual steps     | Build not reproducible or has undocumented steps | unknown-unknowns     |
| Config sprawl      | Count env vars/config files vs documented ones                | Undocumented or duplicated configuration         | change-amplification |
| Missing automation | Lint/format/test not run in CI or hooks                       | Checks exist locally but are not enforced        | unknown-unknowns     |
| Runtime EOL        | Compare pinned runtime/framework versions with supported ones | Runtime or framework past end of life            | unknown-unknowns     |

## Rules

- Report only violations of conventions the repo shows; do not impose an external architecture.
- Verify docs claims by running the safe, read-only part (`--help`, `ls`) or reading the referenced code.
- Dependency freshness belongs to `update-dependencies`; flag EOL runtimes only.
- For top architecture findings, suggest `module-design` as the next step (`02`).
