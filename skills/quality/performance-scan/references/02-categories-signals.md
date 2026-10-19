# 02 — Categories and Signals

Load only the sections for the chosen categories. A signal is a lead; it becomes a finding only after measurement.

## algorithmic

- Nested loops or repeated `find`/`includes`/`indexOf` over the same growing collection (quadratic).
- Sorting, regex compilation, or JSON parsing repeated inside a loop.
- Recomputation of an invariant per iteration or per request; missing memoization.
- Wrong data structure: array used as a set or map, string concatenation in a loop.

## io-db

- N+1: a query, HTTP call, or file read inside a loop over results.
- Unbounded reads: no limit or pagination, `SELECT *`, loading a whole collection to filter in memory.
- Missing index for a filtered or sorted field (only provable with a real database; otherwise Unconfirmed).
- Sequential awaits for independent calls; synchronous file or network I/O on a hot path.

## memory

- Caches, maps, or listener lists that only grow (no eviction, no removal).
- Reading entire files, streams, or payloads into memory instead of streaming.
- Closures or timers retaining large objects; handlers never unregistered.
- Large copies per call: spread or clone of big structures in a loop.

## concurrency

- Blocking the event loop or main thread with CPU-bound or sync work.
- Coarse locks or serialized sections around independent work.
- Unbounded fan-out (`Promise.all` over thousands of items) or missing backpressure.
- Missing parallelism for independent, awaited calls.

## payload-render

- Responses that return full records when a handful of fields is used.
- Large bundles, unused imports of heavy libraries on the client.
- Re-renders on every state change, unmemoized heavy computations in render, unvirtualized long lists.
- Missing compression or caching headers on large static or repeated responses.

Apply `payload-render` only when the repo has a client or HTTP surface; otherwise list it under not reviewed.
