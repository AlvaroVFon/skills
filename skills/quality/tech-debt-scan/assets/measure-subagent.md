# Measurement Subagent Prompt

Fill the placeholders and pass as the subagent task. One subagent per chosen category, at most 3 concurrent.

---

You are collecting debt candidates for exactly one category. Return facts, not verdicts or scores.

## Category

- Category: `{code | tests | architecture-docs-infra}`
- Modules to deepen: `{modules from the recon, highest interest first}`
- Signals to measure: `{signal table rows from references/03, 04, or 05}`

## Recon facts

- Churn percentiles (50 / 75 / 90 / 97): `{values}`
- Analyzers available: `{list}`
- Test command and whether the suite is safe to run: `{command, safe | unsafe}`

## Hard constraints

- Read-only: NEVER modify or create files in the repo, install tools, or start services.
- Use only `git`, `wc`, `grep`, file reads, and analyzers already installed.
- Run tests only if marked safe above.
- Every candidate needs the exact command or files read that produced its result, so it can be re-run.
- Do not rate impact, assign scores, or decide severity.

## Return

For each candidate, one entry:

1. Location: `file:line` and symbol, if any.
2. Signal: the row measured.
3. Method: the exact command or files read.
4. Result: the raw number, count, or quoted fact.
5. Churn: commits in the window for the file and its module.
6. Dependents: importers or call sites counted, with the command.
7. Co-change: files that changed together with it, when relevant.

Then list signals or modules you could not measure, with the reason.
