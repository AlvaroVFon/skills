# 03 — Execution Protocol

## Definition

Each mutant earns a verdict from a real test run. Production code is never left modified.

## Isolation

Each mutant is verified by one subagent inside its own temporary worktree, so mutants never share files.

1. Preferred: the subagent creates `git worktree add {tmp} HEAD`, mutates and tests there, then removes it. Reuse the repo's dependencies (symlink or install only if needed and allowed).
2. Fallback (no subagent): mutate in place and revert immediately with `git checkout -- {file}` after every run; never run two mutants at once.
3. Final check: `git status` shows no changes besides the report; `git worktree list` has no leftovers.

## Parallel Execution

1. List every mutant with `file:line`, operator, and exact diff.
2. Dispatch one write-capable subagent (e.g. `general`) per mutant in a single message, using `assets/verify-mutant-subagent.md`; cap concurrency at 3–4 and queue the rest.
3. Serialize mutants whose mapped tests share heavy resources (DB, ports, queues) or a single global build directory.
4. Each subagent returns facts: raw output, whether the mapped tests passed or failed, and confirmation its worktree was removed.
5. Collect the facts, assign verdicts, and confirm cleanup.

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
