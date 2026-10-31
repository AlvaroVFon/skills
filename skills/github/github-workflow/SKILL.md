---
name: github-workflow
description: "Trigger: GitHub workflow, full GitHub cycle, triage and implement, run the GitHub workflow. Runs github-triage then github-implementer on one repo."
license: MIT
disable-model-invocation: true
metadata:
  author: AlvaroVFon
  version: "1.0"
---

## Activation Contract

Load this skill when asked to run the **full GitHub workflow**, or on a recurring `/loop` or `/schedule` run, from inside the target repository. Invocation: `/github-workflow [repo="owner/name"] [milestone="..."]`; without `repo`, use the `origin` remote. Typical use: `/loop 30m /github-workflow`.

## Hard Rules

- NEVER run without a repo: resolve it from the invocation first, then from `origin`; if neither works, STOP before invoking any skill and show the usage line.
- NEVER run a phase unless the Environment Requirements pass. If any fails, STOP, name each unmet requirement and how to fix it, and touch neither GitHub nor the repository.
- Pass the SAME repo, unchanged, to both skills. Do NOT add, change, or relax any rule of either.
- ALWAYS run `github-triage`, then `github-implementer`, strictly in sequence. PR review is out of scope: the repository CI and humans own it.
- A failure or an empty result in one phase MUST NOT stop the next one. Stop the run only when the repo is missing or inaccessible.
- Do NOT start a new cycle yourself: recurrence belongs to `/loop` or `/schedule`.

## Decision Gates

| Situation                                             | Action                                                 |
| ----------------------------------------------------- | ------------------------------------------------------ |
| No `repo` in the invocation and none in `origin`      | Do not run; ask for the repo                           |
| `github-triage` or `github-implementer` not installed | Do not run; give the `npx skills add` command for both |
| `gh auth status` fails or lacks `repo` scope          | Do not run; ask for `gh auth login`                    |
| Repo inaccessible or issues disabled                  | Do not run; report                                     |
| Verification needs Docker and `docker info` fails     | Do not run; ask to start Docker                        |
| Triage finds nothing, or fails                        | Report it; continue to the implementer                 |
| Implementer finds nothing, or fails                   | End the run and report                                 |

## Environment Requirements

| Requirement                   | How to check                                                                                                             |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `gh` authenticated for issues | `gh auth status` exits 0 with `repo` scope; `gh repo view "$R" --json nameWithOwner,hasIssuesEnabled`                    |
| Both phase skills installed   | Their `SKILL.md` resolve next to this one: `../github-triage`, `../github-implementer`                                   |
| Verification toolchain        | The repo's lint, format, typecheck and test commands are discoverable; if they run in Docker, `docker info` exits 0      |
| Write permission              | Cannot be confirmed without writing: never probe with a write. Proceed and STOP the whole run on the first refused write |

## Execution Steps

1. **Validate input**: resolve the repo (invocation, then `origin`); stop if neither.
2. **Check requirements**: run every check, then stop if any failed, listing all unmet requirements.
3. **Triage**: invoke `github-triage` with the same repo and milestone; wait for its report.
4. **Implement**: invoke `github-implementer` with the same repo; wait for its report.
5. **Report** both outcomes.

## Output Contract

Return `Triage` and `Implementer` sections, each with the report its skill returned (or the reason it did not run), then one line: `Triaged: N | Split: N | Implemented: owner/repo#N (<PR URL>) | none`.

Expect `nothing to do` from the implementer until a human assigns a triaged issue: that is the authorization gate, not a failure.

## References

- `../github-triage/SKILL.md` — triage phase.
- `../github-implementer/SKILL.md` — implementation phase.
