# 03 — Concurrency and Async

## Definition

The result depends on the order or overlap of operations: promises that are not awaited, shared state mutated between awaits, check-then-act sequences that are not atomic.

## Signals

| Signal                     | Probe                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------ |
| Missing `await` / floating | Async call whose result or rejection is ignored; `forEach(async …)`; return without await inside `try` |
| Check-then-act             | Read, decide, then write with no lock, transaction or unique constraint                                |
| Read-modify-write          | Counter or balance updated from a stale read instead of an atomic operation                            |
| Shared mutable state       | Module-level variables, caches or singletons written by concurrent requests                            |
| Unbounded parallelism      | `Promise.all` over unbounded input; no concurrency limit on I/O                                        |
| Partial failure            | `Promise.all` abandoning siblings; first rejection leaves side effects half-applied                    |
| Ordering assumption        | Events, queue messages or callbacks assumed to arrive in order or exactly once                         |
| Non-idempotent retry       | Retried handler repeats a side effect (charge, email, insert)                                          |

## Probe

Draw the interleaving: two callers, the lines each executes, and the point where the second caller observes state the first has half-changed.

## Test to Confirm

Run the operations concurrently (`Promise.all` of two calls, or a deterministic stub that pauses between the read and the write) and assert the invariant (no duplicate, balance correct, one side effect). Prefer forcing the interleaving with a controllable stub over relying on timing.

## False-Positive Traps

- The datastore enforces atomicity (unique index, single atomic update operator, transaction).
- The runtime is single-threaded and there is no `await` between the check and the act.
- A queue or lock serializes the callers upstream.

If the race can only be shown under real load or infrastructure, mark it **Unconfirmed** with steps.
