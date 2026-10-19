# 03 — Code Debt

Category `code`. Every signal needs a measurement in `evidence` and a symptom/cause from `02`.

| Signal                | How to measure                                                    | Debt when                                             | Symptom · cause                   |
| --------------------- | ----------------------------------------------------------------- | ----------------------------------------------------- | --------------------------------- |
| Oversized unit        | `wc -l`, function length via analyzer or reading                  | File > ~500 lines or function > ~60 with mixed duties | cognitive-load · obscurity        |
| Complexity            | Analyzer cyclomatic/cognitive score, else count branches          | Score > ~15 on a unit that changes often              | cognitive-load · obscurity        |
| Duplication           | Duplicate detector, else grep for repeated blocks                 | Same logic ≥ 3 places or one block ≥ ~15 lines copied | change-amplification · dependency |
| Coupling              | Count importers of a module and its outgoing imports; co-change   | God module: many dependents and many dependencies     | change-amplification · dependency |
| Shallow module        | Interface size vs body; pass-through wrappers; many tiny classes  | Caller orchestrates steps the module should absorb    | cognitive-load · dependency       |
| Dead code             | Unreferenced exports/symbols (grep callers, analyzer)             | No callers and not a public API                       | cognitive-load · obscurity        |
| Debt markers          | `grep -rnE "TODO\|FIXME\|HACK\|XXX"` + `git blame` age            | Marker older than ~6 months or on a hot path          | unknown-unknowns · obscurity      |
| Suppressions          | Count `eslint-disable`, `@ts-ignore`, `noqa`, `@SuppressWarnings` | Blanket or unexplained suppressions in hot modules    | unknown-unknowns · obscurity      |
| Type/contract erosion | Count `any`, untyped params, ignored return values                | Concentrated in core flows                            | unknown-unknowns · obscurity      |
| Inconsistent patterns | Two or more ways to do the same thing (HTTP, errors, config)      | Both still in active use                              | cognitive-load · obscurity        |

## Rules

- Cite the worst offender with `file:line`; put the count of similar ones in `evidence.result` rather than one finding each.
- Group repeated instances of one pattern into one finding with the total and top locations.
- Ignore style the formatter or linter already enforces.

## Edge Cases

- **Intentional complexity** (parsers, state machines, generated tables): discard unless churn is high and tests are weak.
- **Framework-mandated shape**: discard when the framework forces it.
