# Mutation Subagent Prompt

Fill the placeholders and pass as the subagent task. One mutant per subagent.

---

You are killing or confirming exactly one mutant in an isolated worktree. Return facts, not a verdict.

## Mutant

- Location: `{file}:{line}`
- Operator: `{operator}`
- Exact diff:
  ```diff
  {before/after}
  ```

## Recon facts

- Mapped tests: `{test files}`
- Run them with: `{command}`
- Timeout: `{3× baseline}`

## Hard constraints

- Work ONLY inside a fresh `git worktree add {tmp} HEAD`. Never touch the main checkout.
- Apply exactly this one change; do not edit or add tests.
- Run only the mapped tests. Do not start services, databases, or queues.
- Revert/remove the worktree before returning.

## Return

1. Raw test output.
2. `observed: tests-failed | tests-passed | did-not-compile | cannot-run` plus one line why.
3. The worktree path and confirmation it was removed.
