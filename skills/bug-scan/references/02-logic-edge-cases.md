# 02 — Logic and Edge Cases

## Definition

The code compiles and handles the happy path but returns a wrong result at a boundary, for an empty or absent value, or for an unexpected combination of state.

## Signals

| Signal                    | Probe                                                                                          |
| ------------------------- | ---------------------------------------------------------------------------------------------- |
| Off-by-one                | `<` vs `<=`, slice/substring ends, pagination offsets, inclusive vs exclusive ranges           |
| Null/undefined/empty      | Property access on optional values, `[0]` on a possibly empty list, `0`/`""` treated as absent |
| Inverted or partial check | Negation errors, `&&`/`\|\|` precedence, a branch missing its `else`                           |
| Loose comparison          | `==`, string vs number, floating-point equality, money in floats                               |
| Time handling             | Time zones, DST, month ends, `Date` mutation, comparing dates as strings                       |
| Impossible state          | Two flags that can disagree, status transitions not validated                                  |
| Mutation of inputs        | Sorting/splicing a caller's array, shared default object or array                              |

## Probe

For each candidate, pick the smallest input that separates correct from incorrect behavior: empty, one element, exactly the limit, limit ± 1, negative, absent, duplicated.

## Test to Confirm

Call the function (or the narrowest public entry point) with the boundary input and assert the expected domain result. The test must fail on the current code for the predicted reason.

## False-Positive Traps

- A guard elsewhere (validation layer, type system, caller contract) makes the input unreachable. Check callers before reporting.
- The behavior is documented or intentional (clamping, truncation).
- The type guarantees non-null at runtime (validated at the boundary).
