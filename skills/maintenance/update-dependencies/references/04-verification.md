# 04 — Verification

Run the project's real commands, not invented ones. Detect the scripts from the manifest (`package.json` scripts, `Makefile`, `Taskfile`, CI config) and reuse them.

## Phase order

1. **Install/reinstall** — the manager's install so the lockfile and tree match.
2. **Format** — formatter check (e.g. `npm run fmt:check`, `prettier --check`).
3. **Lint** — linter.
4. **Typecheck** — if the ecosystem has one (tsc, mypy, go vet).
5. **Tests** — unit/integration suite; prefer the full relevant suite over scoped once per batch.
6. **Build / check** — compile or bundle if the project has a build step.

Run them after every batch. Keep the output; report the command and result per step.

## Fixing

- Read the actual error; fix the root cause in code, config, or types.
- A deprecation warning is a lead: fix it while you are here, but never change behavior beyond what the update requires.
- Re-run the full phase after each fix; do not declare success on a partial run.

## Revert policy

- If a failure comes from the bump and cannot be fixed safely, revert the whole batch (manifest, lockfile, and code) to the branch base and report the failing output.
- Never leave the tree half-updated or the lockfile inconsistent.
- A reverted update stays in the report as "held", with the reason.
