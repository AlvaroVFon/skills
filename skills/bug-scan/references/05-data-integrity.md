# 05 — Data Integrity

## Definition

Data that is stored, read, or transformed can become invalid, inconsistent, or wrongly selected: missing validation, queries that match the wrong records, writes that can half-apply.

## Signals

| Signal                       | Probe                                                                                       |
| ---------------------------- | ------------------------------------------------------------------------------------------- |
| Unvalidated input to storage | Request data written or queried without type/shape/range validation                         |
| Wrong query filter           | Missing tenant/owner/status condition; `find` with an undefined value that drops the filter |
| Non-atomic multi-write       | Related documents/rows updated separately with no transaction or ordering guarantee         |
| Lost update                  | Whole-document save overwriting concurrent changes; no version check                        |
| Missing constraint           | Uniqueness or referential rule enforced only in application code                            |
| Schema/code drift            | Field renamed or retyped in code but not in persisted data or migrations                    |
| Orphaned references          | Delete or soft-delete leaving dependents pointing at nothing                                |
| Precision and encoding       | Money as float, integer overflow, truncation, timezone-naive timestamps                     |

## Mongoose / MongoDB Traps

- A query object with an `undefined` field: Mongoose strips it and the filter widens (`findOne({ email: undefined })` matches any document). Probe every filter built from request data.
- `updateOne` without a filter on ownership, or `$set` with unvalidated user keys (operator/key injection).
- `save()` on a stale document instead of an atomic update operator (`$inc`, `$push`, `findOneAndUpdate`).
- `lean()` results compared or mutated as if they were documents (no getters, defaults, or virtuals).
- Unique rules without a unique index; multi-document writes without a transaction where consistency matters.

## Probe

Follow one record from the entry point to storage and back: what is trusted, what is filtered, what could another request change in between.

## Test to Confirm

Use an in-memory or test database when the repo already has one. Seed two records, run the operation with the hostile or edge input, and assert the other record is untouched or the invalid record is rejected. If only a real database or data shape shows it, mark **Unconfirmed** with steps.

## False-Positive Traps

- Validation happens upstream (DTO, schema, gateway) and the data cannot arrive malformed.
- The schema enforces the rule (required, enum, strict mode, index defined in a migration).
- The "wide" filter is the intended behavior (admin or global query).
