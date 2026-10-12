# 04 — Errors and Resources

## Definition

Failures are lost, mislabeled, or leave the system in a bad state; or a resource is acquired and not released on every path.

## Signals

| Signal               | Probe                                                                                     |
| -------------------- | ----------------------------------------------------------------------------------------- |
| Swallowed error      | Empty `catch`, `catch` that logs and continues as if success, `.catch(() => {})`          |
| Wrong error surface  | Internal error leaked to the caller, or every failure mapped to the same generic status   |
| Lost cause           | Rethrow without the original error; error replaced by a string                            |
| Missing release      | Connection, handle, stream, timer or listener not closed on the error path (no `finally`) |
| No timeout           | Outbound call, query or lock wait without a deadline                                      |
| Unbounded retry      | Retry without a cap or backoff; retry on non-retryable errors                             |
| Partial side effects | Step 2 fails after step 1 already wrote, with no compensation or rollback                 |
| Unhandled rejection  | Fire-and-forget promise or event handler that can throw outside any handler               |
| Listener/timer leak  | `on(...)`, `setInterval` or subscription created per call and never removed               |

## Probe

Walk each exit of the function, including the thrown ones: what has been acquired, what has been written, and who is told.

## Test to Confirm

Stub the dependency to fail (reject, throw, time out) at the suspect step. Assert the observable consequence: the error reaches the caller with the right type, the resource spy was released, no partial write remains, the retry count is bounded.

## False-Positive Traps

- A framework or middleware handles the error centrally (global filter, process handler).
- The resource is managed by a pool, `using`/context manager, or a library that releases on its own.
- Swallowing is deliberate (best-effort cleanup, optional telemetry) and documented.
