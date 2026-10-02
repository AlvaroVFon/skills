# 03 — Execution Protocol

## Definition

Each mutant earns a verdict from a real test run. Production code is never left modified.

## Isolation

1. Preferred: create a temporary worktree (`git worktree add {tmp} HEAD`), mutate and test there, remove it at the end. Reuse the repo's dependencies (symlink or install only if needed and allowed).
2. Fallback: mutate in place and revert immediately with `git checkout -- {file}` after every run. Never run two mutants at once.
3. Final check: `git status` shows no changes besides the report; `git worktree list` has no leftovers.

## Per-Mutant Protocol

1. Record `file:line`, operator, and the exact before/after diff.
2. Apply the single change.
3. Run only the mapped tests with the command from reconnaissance; apply a timeout (about 3× the baseline time for that command).
4. Capture the result, then revert.
5. Assign the verdict.

## Baseline

Run the scope's tests once before mutating. If any fail, abort and report the failing output; mutation results on a red suite are meaningless.

## Verdicts

| Result                                | Verdict      | Report                          |
| ------------------------------------- | ------------ | ------------------------------- |
| A test fails (assertion or error)     | Killed       | Counted, not listed             |
| Timeout or infinite loop              | Killed       | Counted as Timeout              |
| All tests pass                        | Survived     | Mutant diff plus suggested test |
| Does not compile/parse                | Invalid      | Discarded, counted              |
| Behavior provably identical           | Equivalent   | Discarded, counted              |
| Tests cannot run (infra, environment) | Not run      | Listed with the reason          |
| Inconsistent over 3 runs              | Inconclusive | Listed as nondeterministic      |

## Mutation Score

`killed / (killed + survived)`; Invalid, Equivalent, Not run, and Inconclusive are excluded. Report it globally and per module.

## Edge Cases

- **Tests need infrastructure** (real DB, queue, network): mark Not run; do not start services unasked.
- **Failure unrelated to the mutant** (setup, import): rerun once on the original code; if it fails there too, treat as Not run.
- **Mutant on code covered by no mapped test**: Survived; note "no covering test".
