---
name: update-dependencies
description: "Trigger: update dependencies, bump deps, outdated packages, dependency upgrade. Update deps safely by mode with vulnerability and breaking-change checks."
license: Apache-2.0
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Use this skill when asked to update, upgrade, or bump project dependencies, resolve outdated packages, or fix vulnerable dependencies. Not for adding a brand-new dependency, and not for unrelated refactors (use `refactor`).

## Hard Rules

- ALWAYS detect the package manager(s) and ecosystem from lockfiles/manifests first; if several apply or none is found, ask; never guess.
- ALWAYS ask for the update mode (`major` | `minor` | `patch`) before touching any file; never infer it from the request.
- ALWAYS ask before applying ANY major or breaking update; never auto-apply a major/breaking bump.
- Auto-apply only safe updates for the chosen mode (patch, or patch+minor); never hand-edit lockfiles.
- Before updating, list outdated packages AND run the vulnerability audit with the manager's own commands.
- For every non-patch jump, look up breaking changes first: use the Context7 MCP server when available, otherwise official changelogs/migration guides.
- Work on a dedicated branch; NEVER commit or push unless the user asks.
- After each batch: reinstall, fix what it breaks, then run the verification phase before the next batch.
- If verification fails and cannot be fixed safely, revert the batch and report it.

## Decision Gates

| Condition                                  | Action                          |
| ------------------------------------------ | ------------------------------- |
| Package manager ambiguous or missing       | Ask; do not proceed             |
| Mode not stated                            | Ask; require an explicit answer |
| Update is patch (or minor in `minor` mode) | Apply automatically             |
| Update is major or breaking                | Ask before applying             |
| Vulnerability fix needs a major bump       | Treat as major: ask             |
| Breaking change needs a code migration     | Apply migration, then verify    |
| Verification fails                         | Fix if safe, else revert batch  |

## Execution Steps

1. Detect package manager(s), ecosystem, lockfiles, and version strategy (see `references/01-package-managers.md`).
2. Ask for the update mode (see `references/02-update-modes.md`); require an explicit answer.
3. List available updates and run the vulnerability audit; collect current → latest and severities.
4. Classify each update as patch, minor, or major.
5. For major/breaking candidates, research breaking changes (see `references/03-breaking-changes.md`), present them with a recommendation, and get approval.
6. Apply the safe updates for the mode plus any approved majors, in small batches.
7. Fix code, config, and types broken by the updates.
8. Run the verification phase (see `references/04-verification.md`): format, lint, typecheck, tests, build.
9. Report per the Output Contract.

## Output Contract

Return: detected package manager and chosen mode; updates applied (name `from → to`, per batch); majors/breaking updates skipped or awaiting approval and why; vulnerabilities found and their status; breaking changes encountered and migrations done; per-step verification results; files changed. State "no commit/push performed" unless asked.

## References

- `references/01-package-managers.md` — detection and commands per ecosystem
- `references/02-update-modes.md` — semver modes and per-manager flags
- `references/03-breaking-changes.md` — finding breaking changes (Context7 MCP, changelogs)
- `references/04-verification.md` — verification phase and revert policy
