# Skills

[![skills.sh](https://skills.sh/b/AlvaroVFon/skills?style=for-the-badge)](https://skills.sh/AlvaroVFon/skills)

A collection of **LLM-first skills**: reusable instruction packs that teach AI coding agents how to perform a specific task consistently.

Each skill is a folder under `skills/{category}/` with a `SKILL.md` (the runtime contract) plus optional `references/` and `assets/`.

## Available skills

### Authoring

| Skill                                                      | Command                                              | What it does                                        |
| ---------------------------------------------------------- | ---------------------------------------------------- | --------------------------------------------------- |
| [skill-creator](skills/authoring/skill-creator/SKILL.md)   | `npx skills add AlvaroVFon/skills -s skill-creator`  | Create new LLM-first skills with valid frontmatter. |
| [skill-improver](skills/authoring/skill-improver/SKILL.md) | `npx skills add AlvaroVFon/skills -s skill-improver` | Audit and upgrade existing skills.                  |

### Design

| Skill                                                 | Command                                             | What it does                                                |
| ----------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------------------- |
| [module-design](skills/design/module-design/SKILL.md) | `npx skills add AlvaroVFon/skills -s module-design` | Design and analyze domain module boundaries and interfaces. |
| [adr](skills/design/adr/SKILL.md)                     | `npx skills add AlvaroVFon/skills -s adr`           | Write architecture and design decision records (MADR).      |

### Implementation

| Skill                                               | Command                                        | What it does                                                            |
| --------------------------------------------------- | ---------------------------------------------- | ----------------------------------------------------------------------- |
| [tdd](skills/implementation/tdd/SKILL.md)           | `npx skills add AlvaroVFon/skills -s tdd`      | Implement doc-first and test-first (red-green-refactor), then refactor. |
| [refactor](skills/implementation/refactor/SKILL.md) | `npx skills add AlvaroVFon/skills -s refactor` | Restructure code in small, test-verified behavior-preserving steps.     |

### Quality

| Skill                                                  | Command                                             | What it does                                                          |
| ------------------------------------------------------ | --------------------------------------------------- | --------------------------------------------------------------------- |
| [code-review](skills/quality/code-review/SKILL.md)     | `npx skills add AlvaroVFon/skills -s code-review`   | Review pull requests and diffs; requests changes, never merges.       |
| [bug-scan](skills/quality/bug-scan/SKILL.md)           | `npx skills add AlvaroVFon/skills -s bug-scan`      | Scan a repo or modules for latent bugs and prove each with a test.    |
| [mutation-test](skills/quality/mutation-test/SKILL.md) | `npx skills add AlvaroVFon/skills -s mutation-test` | Mutate a repo or modules by hand and report which mutants tests miss. |

### Git

| Skill                                              | Command                                             | What it does                                                   |
| -------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------- |
| [create-commit](skills/git/create-commit/SKILL.md) | `npx skills add AlvaroVFon/skills -s create-commit` | Write validated Conventional Commits (`type(scope): subject`). |
| [create-pr](skills/git/create-pr/SKILL.md)         | `npx skills add AlvaroVFon/skills -s create-pr`     | Open standardized pull requests via the `gh` CLI.              |

### Learning

| Skill                                                         | Command                                                | What it does                                                             |
| ------------------------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------ |
| [learning-profile](skills/learning/learning-profile/SKILL.md) | `npx skills add AlvaroVFon/skills -s learning-profile` | Build and update the learner's structured profile.                       |
| [mentor](skills/learning/mentor/SKILL.md)                     | `npx skills add AlvaroVFon/skills -s mentor`           | Design and deliver profile-based sessions (requires `learning-profile`). |

`mentor` depends on `learning-profile`: it loads it to create the profile when none exists, and again after every session to update the profile from the logged evidence.

## Usage

Skills are loaded by compatible agents such as [opencode](https://opencode.ai), Claude Code, and Codex. Install them with the open [`skills`](https://skills.sh) CLI:

```sh
# every skill in this repo, global scope, detected agents
npx skills add AlvaroVFon/skills -g

# specific agents
npx skills add AlvaroVFon/skills -g -a opencode -a claude-code -a codex

# a single skill by name
npx skills add AlvaroVFon/skills -s bug-scan

# list what the repo offers without installing
npx skills add AlvaroVFon/skills --list

# project scope instead of global (installs into ./.<agent>/skills/)
npx skills add AlvaroVFon/skills -a opencode
```

The CLI detects the coding agents you have installed. `-g` installs globally (`~/.config/opencode/skills/`, `~/.claude/skills/`, `~/.codex/skills/`, ...); without `-g` it installs into the current project. Update installed skills later with `npx skills update`.

<details>
<summary>Manual install (fallback)</summary>

```sh
git clone https://github.com/AlvaroVFon/skills.git

# opencode
mkdir -p ~/.config/opencode/skills
cp -r skills/*/* ~/.config/opencode/skills/

# Claude Code
mkdir -p ~/.claude/skills
cp -r skills/*/* ~/.claude/skills/

# Codex
mkdir -p ~/.codex/skills
cp -r skills/*/* ~/.codex/skills/
```

</details>

Once installed, an agent picks the right skill automatically from your request — for example, "create a PR" loads `create-pr`.

## Repository layout

```
skills/
  {category}/
    {name}/
      SKILL.md        # the contract the agent follows
      references/     # optional deep-dive docs, loaded on demand
      assets/         # optional templates and scripts
```

Categories: `authoring/`, `design/`, `implementation/`, `quality/`, `git/`, `learning/`.

## Contributing

See [`AGENTS.md`](./AGENTS.md) for the skill format rules, style guide, and validation commands. Markdown is formatted with `oxfmt`:

```sh
npm install     # once, enables the pre-commit hook
npm run fmt     # format the repository
```
