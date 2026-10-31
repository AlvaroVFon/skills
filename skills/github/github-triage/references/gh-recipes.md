# gh recipes

Every write goes through the `gh` CLI. `gh issue edit` (>= 2.90) has native sub-issue, dependency, label and assignee flags, so no GraphQL is needed.

Set `R="owner/name"` once resolved. Every command below takes `--repo "$R"`.

## Resolve the repo

```sh
git remote get-url origin                     # https://github.com/owner/name.git or git@github.com:owner/name.git
gh repo view "$R" --json nameWithOwner,hasIssuesEnabled
```

If the remote is not a GitHub host or `gh repo view` fails, stop: no repo, no run. GHES is out of scope for v1.

## Labels

| Name                 | Colour | Description                                |
| -------------------- | ------ | ------------------------------------------ |
| `AI_triage`          | FBCA04 | Candidate for AI triage                    |
| `AI_triage_done`     | 0E8A16 | Triaged: estimate set, ready to implement  |
| `status:in-progress` | 1D76DB | Someone is working on it; triage must skip |
| `status:blocked`     | D93F0B | Blocked; triage must skip                  |
| `estimate:1h`        | 5319E7 | Original estimate: 1 hour                  |
| `estimate:2h`        | 5319E7 | Original estimate: 2 hours                 |
| `estimate:3h`        | 5319E7 | Original estimate: 3 hours                 |
| `estimate:5h`        | 5319E7 | Original estimate: 5 hours                 |
| `estimate:8h`        | 5319E7 | Original estimate: 8 hours                 |
| `estimate:13h`       | 5319E7 | Original estimate: 13 hours                |
| `estimate:21h`       | 5319E7 | Original estimate: 21 hours                |

### Type labels

Triage is the only writer of these; `github-implementer` reads them for TDD and branch naming.

| Label              | Rubric type   | Branch prefix |
| ------------------ | ------------- | ------------- |
| `type:feature`     | Funcionalidad | `feature/`    |
| `type:docs`        | Documentación | `docs/`       |
| `type:analysis`    | Análisis      | `docs/`       |
| `type:maintenance` | Mantenimiento | `chore/`      |
| `type:tech-debt`   | Deuda técnica | `refactor/`   |

Colours: `type:feature` 0E8A16, `type:docs` 0075CA, `type:analysis` 7057FF, `type:maintenance` 5319E7, `type:tech-debt` B60205.

Replace any previous `type:*` before adding the new one:

```sh
gh issue view "$N" --repo "$R" --json labels --jq '.labels[].name | select(startswith("type:"))'
gh issue edit "$N" --repo "$R" --remove-label "type:<old>" --add-label "type:feature"
```

Bootstrap (idempotent; `--force` updates an existing label instead of failing):

```sh
gh label list --repo "$R" --limit 200 --json name --jq '.[].name'
gh label create "AI_triage" --repo "$R" --color FBCA04 --description "Candidate for AI triage" --force
```

## Candidates

```sh
gh issue list --repo "$R" ${MILESTONE:+--milestone "$MILESTONE"} \
  --state open --label AI_triage --limit 100 \
  --json number,title,body,assignees,labels,milestone,url
```

Re-check each issue after fetching it:

```sh
gh issue view "$N" --repo "$R" --json number,title,body,assignees,labels,milestone,url,comments,closedByPullRequestsReferences
```

Skip when `assignees` is empty, `body` is empty, `closedByPullRequestsReferences` is non-empty, or the labels contain `AI_triage_done`, `status:in-progress` or `status:blocked`.

## Estimate label

```sh
# remove any previous estimate label first
gh issue edit "$N" --repo "$R" --remove-label "estimate:<old>"
gh issue edit "$N" --repo "$R" --add-label "estimate:5h"
```

## Unassign

```sh
gh issue view "$N" --repo "$R" --json assignees --jq '.assignees[].login'
gh issue edit "$N" --repo "$R" --remove-assignee "<login>"   # one call per login
```

## Comment

```sh
gh issue comment "$N" --repo "$R" --body-file /tmp/opencode/triage-comment.md
```

## Sub-issues

Create the child first, then attach it to the parent:

```sh
gh issue create --repo "$R" --title "<summary>" --body-file <file> \
  --label AI_triage --assignee "<login>"          # repeat --assignee per login
gh issue edit "$PARENT_N" --repo "$R" --add-sub-issue "$CHILD_N"
```

Create every child before linking dependencies: a `blocked by` link needs issue numbers that do not exist yet when the subagent proposes the split.

## Dependencies

`A --add-blocked-by B` means A is blocked by B (B must be resolved first).

```sh
gh issue edit "$A" --repo "$R" --add-blocked-by "$B"
gh issue view "$N" --repo "$R" --json blockedBy,blocking   # current links, to avoid duplicates
```

## Finish

```sh
gh issue edit "$N" --repo "$R" --remove-label AI_triage --add-label AI_triage_done
```

## Report

Write the table to `${TMPDIR:-/tmp}/opencode/github-triage-report.md` (`mkdir -p` its directory) and validate it:

```sh
python3 assets/validate_triage_report.py --file "${TMPDIR:-/tmp}/opencode/github-triage-report.md"
```
