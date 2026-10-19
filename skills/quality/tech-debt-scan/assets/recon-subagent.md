# Reconnaissance Subagent Prompt

Fill the placeholders and pass as the subagent task. Run once, before any measurement.

---

You are mapping a codebase to prepare a technical-debt scan. Return facts, not verdicts or scores.

## Scan

- Mode: `{global | targeted}`
- Scope: `{whole repo | paths}`
- Categories: `{code | tests | architecture-docs-infra}`
- Churn window: `{6 months}`

## Hard constraints

- Read-only: NEVER modify or create files in the repo, install tools, or start services.
- Use only `git`, `wc`, `grep`, file reads, and analyzers already installed.
- Run the test suite only if its command is known, needs no external services, and is safe; otherwise report it as not run.
- Skip generated, vendored, and build output; list them.

## Return

1. Module map: path, LOC, commits in the window, distinct authors.
2. Churn distribution of the repo: the commit counts at percentiles 50, 75, 90, and 97 (anchors for `frequency`).
3. Top 10 modules by `churn × size`, each with its most co-changed files and the command used.
4. Languages, frameworks, and analyzers available (linter, complexity, duplicates, coverage).
5. Test framework, test location, the command to run one file and the full suite, and whether the full suite is safe to run.
6. Generated or vendored paths excluded.
7. Whether git history is sufficient for churn (shallow clone, no git, fewer commits than the window).
8. Anything you could not determine, with the reason.
