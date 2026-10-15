# 08 — Mishandling of Exceptional Conditions (A10:2025)

## Definition

The API does not prevent, detect, or correctly respond to abnormal conditions: errors that **fail open**, crash the process, leave state half-written, or leak internals. Leaking details through errors is scanned in `05`; this reference covers the control-flow consequences.

## Signals

| Signal                            | Probe                                                                                                                                   |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Fail open in auth/authz           | Middleware `catch` that calls `next()` without the error, returns `true`, or skips the check when the token service/DB throws (CWE-636) |
| Permission check result unchecked | `await canAccess()` result ignored, or a `Promise` used as a boolean (always truthy) (CWE-252, CWE-280)                                 |
| Missing / extra parameters        | Absent field turns a filter into `undefined` and widens the query; unexpected params change behavior (CWE-234, CWE-235)                 |
| Uncaught exception / rejection    | Async handler without wrapper in Express 4 → unhandled rejection crashes the process or hangs the request (CWE-248, DoS)                |
| Generic catch                     | `catch (e) {}` or `catch` that maps every error to 200/empty success (CWE-390, CWE-391, CWE-396)                                        |
| Partial state on error            | Multi-step write (debit, credit, log) without transaction/rollback; retries duplicate effects (CWE-460, CWE-703)                        |
| Leaked resources on error         | Upload/stream/connection not released in the error path → exhaustion under repeated failures                                            |
| Unexpected status / value         | Third-party or internal call returns non-2xx/`null` and code proceeds as success (CWE-394, CWE-754)                                     |
| Missing default branch            | `switch` on role/state without `default` deny; unknown enum value grants access (CWE-478)                                               |
| Missing error handler             | No global error handler / custom error response; framework default page in prod (CWE-756)                                               |

## Test to Confirm

In-process, make a dependency throw (stub the token verifier, DB, or provider to reject) and assert the request is **denied** (401/403/5xx), not served. For crashes, assert the server keeps answering after the hostile request. For partial state, make step 2 fail and assert step 1 was rolled back (in-memory DB). For missing params, omit the field and assert the query does not return other users' records.

## False-Positive Traps

- A global async wrapper (`express-async-errors`, Express 5, Nest exception filters, Fastify) already routes rejections to a deny/500 handler.
- The catch re-throws or calls `next(err)`, which reaches a handler that denies.
- The multi-step write runs inside a transaction/session or is idempotent by design.
