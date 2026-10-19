# 01 — Scan Modes

## Definition

- **Global**: cover the whole repo by hot-path likelihood, not uniformly.
- **Targeted**: cover only the selected paths/modules and their direct callers/callees.

Coverage must always be declared: what was reviewed, in what depth, and what was skipped.

## Choosing the Scan Type (Mandatory)

Ask with the option selector (question tool) before any work, every run — never infer from the prompt:

1. **Mode**: `Global` (whole repo) or `Targeted` (named paths/modules). If `Targeted`, request the paths in the same round.
2. **Categories** (multi-select): `algorithmic`, `io-db`, `memory`, `concurrency`, `payload-render` (sections of `02`), or `all`. Load only the chosen sections in step 4.
3. **Output format**: `chat` (concise summary) or `markdown` (full rendered report) — never both. The JSON report is written either way.
4. **Thresholds** (optional): override the defaults in `references/03-measurement-and-thresholds.md`.

If the question tool is unavailable, ask in chat and wait for the answer.

## Output Format

The report is always persisted as `docs/performance-scan/{YYYY-MM-DD}.json`. The human view is shown in the chat only: `chat` returns the concise summary; `markdown` runs `assets/render_report.py --json <report.json>` and pastes its stdout. Never write a `.md` file and never show both views.

## Global — Hot-Path Map

Reconnaissance returns every module with a hot-path rank. Rank by the highest signal present.

| Signal                                                      | Rank   |
| ----------------------------------------------------------- | ------ |
| Request handlers, queue consumers, render loops             | High   |
| Data access: queries, ORM calls, repositories, aggregations | High   |
| Loops over collections that grow with data or users         | High   |
| Caches, singletons, long-lived state                        | High   |
| Serialization, parsing, file and network I/O                | Medium |
| Startup, CLI commands, cron jobs                            | Medium |
| Pure transforms on bounded input, config, DTOs              | Low    |

Deepen High modules first, then Medium while budget remains. Low modules are listed as **not reviewed**. The previous report adjusts the ranking (`references/04-baseline-history.md`).

## Targeted — Flow Tracing

1. Resolve each path to its public entry points.
2. Trace one level up (callers) to learn real input sizes, and down (dependencies) to learn cost per call.
3. Stop at the module boundary; note crossings as out of scope.

## Reconnaissance Output

Facts, not verdicts: module or flow map, entry points, callers, data-access points, runtime, benchmark or test framework, and the command to run one file.

## Edge Cases

- **Monorepo**: treat each package as a module; rank packages first.
- **No runnable harness**: every finding becomes Unconfirmed with manual steps; say so in the summary.
- **Generated or vendored code**: skip and list under not reviewed.
- **Cold paths**: a slow function that runs once at startup is not a finding unless the user asked for startup time.
