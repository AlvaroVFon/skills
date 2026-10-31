# gh recipes

Set `R="owner/name"` once resolved; every command takes `--repo "$R"`.

## Resolve the repo

```sh
git remote get-url origin                 # invocation wins over this
gh repo view "$R" --json nameWithOwner,hasIssuesEnabled
```

If the remote is not a GitHub host or `gh repo view` fails, stop: no repo, no run.

## Labels this skill writes

| Name        | Colour | Description             |
| ----------- | ------ | ----------------------- |
| `AI_triage` | FBCA04 | Candidate for AI triage |

That is the whole set. `type:*`, `estimate:*`, `AI_triage_done`, `status:*` and `AI_implemented` belong to `github-triage` and `github-implementer`; writing them here would create a second source of truth.

Bootstrap idempotently:

```sh
gh label list --repo "$R" --limit 200 --json name --jq '.[].name'
gh label create "AI_triage" --repo "$R" --color FBCA04 --description "Candidate for AI triage" --force
```

## Assignee

Triage skips unassigned issues, so an issue created without an assignee never enters the cycle. Confirm the owner with the human, then pass it explicitly:

```sh
gh api user --jq .login            # only when the human says "assign it to me"
```

## Duplicate search

```sh
gh issue list --repo "$R" --state open --search "<keywords> in:title,body" --limit 10 \
  --json number,title,url
```

Show the matches and ask before creating anything.

## Create

```sh
gh issue create --repo "$R" --title "<title>" --body-file <file> \
  --label AI_triage --assignee "<login>"
```

The command prints the issue URL. `--assignee` can be repeated for several owners.
