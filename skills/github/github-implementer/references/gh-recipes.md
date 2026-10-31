# gh recipes

Every GitHub write goes through the `gh` CLI. Set `R="owner/name"` once resolved; every command takes `--repo "$R"`.

## Labels

Shared contract with `github-triage`. This skill reads `AI_triage_done`, `type:*` and `estimate:*`; it only writes `status:in-progress` and `AI_implemented`. It never writes `AI_triage`, `AI_triage_done`, `type:*` or `estimate:*`: those have a single owner, triage.

| Name                             | Colour | Description                                  |
| -------------------------------- | ------ | -------------------------------------------- |
| `AI_triage`                      | FBCA04 | Candidate for AI triage                      |
| `AI_triage_done`                 | 0E8A16 | Triaged: estimate set, ready to implement    |
| `status:in-progress`             | 1D76DB | Claimed by a run; triage must skip it        |
| `status:blocked`                 | D93F0B | Blocked; triage and implementation must skip |
| `AI_implemented`                 | 6F42C1 | Implemented: branch pushed and PR open       |
| `estimate:1h` ... `estimate:21h` | 5319E7 | Original estimate from triage                |
| `type:feature`                   | 0E8A16 | Rubric type: Funcionalidad                   |
| `type:docs`                      | 0075CA | Rubric type: Documentación                   |
| `type:analysis`                  | 7057FF | Rubric type: Análisis                        |
| `type:maintenance`               | 5319E7 | Rubric type: Mantenimiento                   |
| `type:tech-debt`                 | B60205 | Rubric type: Deuda técnica                   |

Bootstrap idempotently:

```sh
gh label list --repo "$R" --limit 200 --json name --jq '.[].name'
gh label create "AI_implemented" --repo "$R" --color 6F42C1 --description "Implemented: branch pushed and PR open" --force
```

## Resolve repo and user

```sh
git remote get-url origin                 # invocation wins over this
gh repo view "$R" --json nameWithOwner,defaultBranchRef
gh api user --jq .login
```

If the remote is not a GitHub host or `gh repo view` fails, stop: no repo, no run.

## Candidates

```sh
gh issue list --repo "$R" --state open --assignee @me --label AI_triage_done \
  --search "sort:created-asc" --limit 50 \
  --json number,title,labels,assignees,url
```

Gate each candidate before claiming it:

```sh
gh issue view "$N" --repo "$R" --json number,title,body,author,assignees,labels,blockedBy,comments

gh issue view "$N" --repo "$R" --json labels \
  --jq '.labels[].name | select(startswith("estimate:"))'         # empty = no estimate

gh issue view "$N" --repo "$R" --json labels \
  --jq '.labels[].name | select(startswith("type:"))'             # empty = no type

gh issue view "$N" --repo "$R" --json blockedBy --jq '.blockedBy.nodes[].number'
gh issue view "<blocker>" --repo "$R" --json state --jq '.state'  # OPEN = unresolved

gh issue view "$N" --repo "$R" --json comments --jq '.comments[-1].body'
```

Stop at the first candidate that passes. Never skip the estimate or blocker gate because the issue "looks easy".

## Claim

Skip the candidate when `status:in-progress` is already on it: another run owns it. Otherwise claim, then check the branch:

```sh
gh issue edit "$N" --repo "$R" --add-label "status:in-progress"
git ls-remote --heads origin "<branch>"     # empty output = branch is free
```

If the branch already exists, a previous run died mid-flight: remove the label this run just added (`--remove-label status:in-progress`) and move to the next candidate. The branch is the only copy of that work; never reuse or delete it.

## Branch and worktree

```sh
git fetch origin
git symbolic-ref refs/remotes/origin/HEAD   # refs/remotes/origin/main
git worktree add "<parent>/<repo>-worktrees/<N>-<slug>" -b "<prefix>/<N>-<slug>" "origin/<main>"
git worktree list
```

Prefix from the `type:*` label: `type:feature` → `feature`, `type:docs` → `docs`, `type:analysis` → `docs`, `type:maintenance` → `chore`, `type:tech-debt` → `refactor`. Repo conventions win over this table.

Labels are the contract: read `type:*` and `estimate:*` from them. The triage comment is context for the plan, never a source of truth.

## Verification

Discover the commands from the repo, never assume: `package.json` scripts, `Makefile`, `pyproject.toml`, `go.mod`, and the CI workflow files. Run lint, format check, typecheck and tests, in that order, and re-run after every fix.

## Deliver

```sh
git push -u origin "<branch>"
gh pr create --repo "$R" --base "<main>" --head "<branch>" --title "<title>" --body-file <body>
```

The body follows the `create-pr` template and ends with a bare `Closes #N` line. Title 72 characters max.

## Close out

```sh
gh issue edit "$N" --repo "$R" --add-label "AI_implemented"
gh issue comment "$N" --repo "$R" --body-file /tmp/opencode/implementation-comment.md
```

`--add-label` keeps the existing labels; never replace them.

## Clean up

Always from the main repository, never from inside the worktree:

```sh
git worktree remove "<path>"
```

If it refuses because of uncommitted changes, report it and leave it. Never `--force`, never delete the branch.
