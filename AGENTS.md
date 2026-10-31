# AGENTS.md

Skills repository. Each skill is a directory under `skills/{category}/{name}/` containing a `SKILL.md` plus optional `assets/` and `references/`. Categories: `authoring/`, `design/`, `implementation/`, `quality/`, `git/`, `github/`, `maintenance/`, `learning/`.

## Repo Facts

- No build, test, or lint suite: `package.json` only wires `oxfmt` + `husky`. Verification is `npm run fmt:check` plus the validator(s) for the skills you touched.
- Validators are stdlib-only Python 3 scripts run from the repo root. No venv, no `pip install`.
- `.atl/` is a local, gitignored agent cache (skill registry). Never commit it.

## Skills

### authoring

| Skill          | Path                                       | Purpose                            |
| -------------- | ------------------------------------------ | ---------------------------------- |
| skill-creator  | `skills/authoring/skill-creator/SKILL.md`  | Create new LLM-first skills        |
| skill-improver | `skills/authoring/skill-improver/SKILL.md` | Audit and refactor existing skills |

### design

| Skill         | Path                                   | Purpose                                                |
| ------------- | -------------------------------------- | ------------------------------------------------------ |
| module-design | `skills/design/module-design/SKILL.md` | Design/analyze domain module boundaries and interfaces |
| adr           | `skills/design/adr/SKILL.md`           | Write architecture/design decision records (MADR)      |

### implementation

| Skill    | Path                                      | Purpose                                                   |
| -------- | ----------------------------------------- | --------------------------------------------------------- |
| tdd      | `skills/implementation/tdd/SKILL.md`      | Implement doc-first and test-first (red-green-refactor)   |
| refactor | `skills/implementation/refactor/SKILL.md` | Behavior-preserving restructuring in small verified steps |

### quality

| Skill             | Path                                        | Purpose                                                           |
| ----------------- | ------------------------------------------- | ----------------------------------------------------------------- |
| code-review       | `skills/quality/code-review/SKILL.md`       | Review PRs/diffs via `gh`; request changes, never merge           |
| bug-scan          | `skills/quality/bug-scan/SKILL.md`          | Scan repo/modules for latent bugs, prove each with a test         |
| mutation-test     | `skills/quality/mutation-test/SKILL.md`     | Manual mutation testing of repo/modules; report survivors         |
| api-security-scan | `skills/quality/api-security-scan/SKILL.md` | Scan HTTP APIs for vulnerabilities, prove with exploit tests      |
| tech-debt-scan    | `skills/quality/tech-debt-scan/SKILL.md`    | Scan repo/modules for technical debt, rank by priority score      |
| performance-scan  | `skills/quality/performance-scan/SKILL.md`  | Scan repo/modules for performance hotspots, prove with benchmarks |

### git

| Skill         | Path                                | Purpose                                             |
| ------------- | ----------------------------------- | --------------------------------------------------- |
| create-pr     | `skills/git/create-pr/SKILL.md`     | Create standardized PRs with validated descriptions |
| create-commit | `skills/git/create-commit/SKILL.md` | Create conventional commits `type(scope): subject`  |

### github

| Skill              | Path                                        | Purpose                                                        |
| ------------------ | ------------------------------------------- | -------------------------------------------------------------- |
| define-issue       | `skills/github/define-issue/SKILL.md`       | Agree one task with the human and open a triage-ready issue    |
| github-triage      | `skills/github/github-triage/SKILL.md`      | Triage labelled GitHub issues and apply the original estimate  |
| github-implementer | `skills/github/github-implementer/SKILL.md` | Implement one triaged issue in a worktree and open a linked PR |
| github-workflow    | `skills/github/github-workflow/SKILL.md`    | Run github-triage then github-implementer in one cycle         |

### maintenance

| Skill               | Path                                              | Purpose                                                       |
| ------------------- | ------------------------------------------------- | ------------------------------------------------------------- |
| update-dependencies | `skills/maintenance/update-dependencies/SKILL.md` | Update deps by mode with vulnerability/breaking-change checks |

### learning

| Skill            | Path                                        | Purpose                                                              |
| ---------------- | ------------------------------------------- | -------------------------------------------------------------------- |
| learning-profile | `skills/learning/learning-profile/SKILL.md` | Build and update the learner's structured profile                    |
| mentor           | `skills/learning/mentor/SKILL.md`           | Design/deliver profile-based sessions; depends on `learning-profile` |

## Skill Dependencies

- `mentor` depends on `learning-profile`: it MUST load `learning-profile` to create the profile when none exists, and again after every session to update the profile from the logged evidence. `mentor` never writes `profile.md` or the evidence log directly.
- `github-implementer` depends on `create-commit` and `create-pr` (it defers commit format and PR body to them) and reads the triage comment written by `github-triage`. Each GitHub skill ships its own copy of the label contract so it can be installed alone.
- `github-workflow` orchestrates `github-triage` then `github-implementer`; it requires both to be installed and never adds, changes or relaxes their rules. It is not auto-invoked (`disable-model-invocation: true`): the cycle starts only when a human asks for it.
- `define-issue` is the human entry point: it writes only `AI_triage` plus the assignee. `github-triage` is the single writer of `type:*` and `estimate:*`; `github-implementer` reads them and never infers the type from comments.

## Hard Rules

- `SKILL.md` is the normative runtime contract; follow `skills/authoring/skill-creator/references/skill-style-guide.md` when creating or updating skills. The guide is duplicated in `skill-creator` and `skill-improver` — update every copy.
- Required sections in this exact order (validator errors if missing or out of order): `Activation Contract`, `Hard Rules`, `Decision Gates`, `Execution Steps`, `Output Contract`, `References`.
- Skill body target 180–450 tokens, recommended max 700, hard max 1000 (validator error). Move detail to `references/` and scripts/templates to `assets/`.
- `description` MUST be one quoted YAML-safe line starting with `Trigger:`, <=160 chars (max 250), no `Keywords`.
- Frontmatter MUST include `name`, `description`, `license`, `metadata.author`, and `metadata.version`; `name` must match the directory name.
- References must point to local files that exist.
- Adding, renaming, or removing a skill means updating its row in **both** the `README.md` skills table (with the `npx skills add` command) and the tables in the Skills section above.
- Skills with GitHub workflow rules (create-pr, code-review, github-triage) MUST use the `gh` CLI and NEVER merge.
- Skills whose output has objectively checkable structure (commit, PR, ADR, scan report, SKILL.md) MUST ship a validator in `assets/` and run it before finishing: exit 0 with `OK`, or exit 1 with `ERROR:` lines (fix all). See the Output Validation section in `skill-style-guide.md`.

## Formatting

- Format Markdown (and other supported files) with `npm run fmt`; verify with `npm run fmt:check`.
- A husky pre-commit hook runs `lint-staged` → `oxfmt` on staged `*.md` files. Run `npm install` once to enable it.

## Testing

Contract for every validator: `--file`/`--body`/`--message` input (or stdin), exit 0 printing `OK` when valid, else exit 1 with one parseable `ERROR:` line per problem; `WARNING:` lines do not change the exit code.

`validate_skill.py` (below) is the gate for any `SKILL.md` edit: it checks frontmatter keys/quoting, description length, required section presence and order, body budget, and that every referenced `references/`/`assets/` file exists.

- `create-pr`: `python3 skills/git/create-pr/assets/validate_pr_description.py --body <file> [--title "<title>"]`
- `create-commit`: `python3 skills/git/create-commit/assets/validate_commit_message.py --message "<subject>"`
- `adr`: `python3 skills/design/adr/assets/validate_adr.py --file <adr> [--allow-placeholders]`
- `bug-scan`: `python3 skills/quality/bug-scan/assets/reconcile.py --report <report.json>` then `python3 skills/quality/bug-scan/assets/validate_report.py --file <report.json>`
- `mutation-test`: `python3 skills/quality/mutation-test/assets/reconcile.py --report <report.json>` then `python3 skills/quality/mutation-test/assets/validate_report.py --file <report.json>`
- `api-security-scan`: `python3 skills/quality/api-security-scan/assets/reconcile.py --report <report.json>` then `python3 skills/quality/api-security-scan/assets/validate_report.py --file <report.json>`
- `tech-debt-scan`: `python3 skills/quality/tech-debt-scan/assets/reconcile.py --report <report.json>` then `python3 skills/quality/tech-debt-scan/assets/validate_report.py --file <report.json>`
- `performance-scan`: `python3 skills/quality/performance-scan/assets/reconcile.py --report <report.json>` then `python3 skills/quality/performance-scan/assets/validate_report.py --file <report.json>`
- `module-design`: `python3 skills/design/module-design/assets/reconcile.py --report <brief.json>` then `python3 skills/design/module-design/assets/validate_brief.py --file <brief.json>`
- `github-triage`: `python3 skills/github/github-triage/assets/validate_triage_report.py --file <report.md>`
- `define-issue`: `python3 skills/github/define-issue/assets/validate_issue_body.py --body <file> [--title "<title>"]`
- `skill-creator` / `skill-improver`: `python3 skills/authoring/skill-creator/assets/validate_skill.py --file <SKILL.md>`
- Validate every skill against `skill-style-guide.md` after edits using `skill-improver`.
