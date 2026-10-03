# Skills

A collection of **LLM-first skills**: reusable instruction packs that teach AI coding agents how to perform a specific task consistently.

Each skill is a folder under `skills/` with a `SKILL.md` (the runtime contract) plus optional `references/` and `assets/`.

## Available skills

| Skill                                                | What it does                                                             |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| [skill-creator](skills/skill-creator/SKILL.md)       | Create new LLM-first skills with valid frontmatter.                      |
| [skill-improver](skills/skill-improver/SKILL.md)     | Audit and upgrade existing skills.                                       |
| [create-commit](skills/create-commit/SKILL.md)       | Write validated Conventional Commits (`type(scope): subject`).           |
| [create-pr](skills/create-pr/SKILL.md)               | Open standardized pull requests via the `gh` CLI.                        |
| [code-review](skills/code-review/SKILL.md)           | Review pull requests and diffs; requests changes, never merges.          |
| [module-design](skills/module-design/SKILL.md)       | Design and analyze domain module boundaries and interfaces.              |
| [adr](skills/adr/SKILL.md)                           | Write architecture and design decision records (MADR).                   |
| [bug-scan](skills/bug-scan/SKILL.md)                 | Scan a repo or modules for latent bugs and prove each with a test.       |
| [mutation-test](skills/mutation-test/SKILL.md)       | Mutate a repo or modules by hand and report which mutants tests miss.    |
| [refactor](skills/refactor/SKILL.md)                 | Restructure code in small, test-verified behavior-preserving steps.      |
| [tdd](skills/tdd/SKILL.md)                           | Implement doc-first and test-first (red-green-refactor), then refactor.  |
| [learning-profile](skills/learning-profile/SKILL.md) | Build and update the learner's structured profile.                       |
| [mentor](skills/mentor/SKILL.md)                     | Design and deliver profile-based sessions (requires `learning-profile`). |

`mentor` depends on `learning-profile`: it loads it to create the profile when none exists, and again after every session to update the profile from the logged evidence.

## Usage

Skills are loaded by compatible agents such as [opencode](https://opencode.ai) and Claude Code. Install them by copying the skill folders into your agent's skills directory:

```sh
git clone https://github.com/AlvaroVFon/skills.git

# opencode
mkdir -p ~/.config/opencode/skills
cp -r skills/* ~/.config/opencode/skills/

# Claude Code
mkdir -p ~/.claude/skills
cp -r skills/* ~/.claude/skills/
```

Once installed, an agent picks the right skill automatically from your request — for example, "create a PR" loads `create-pr`.

## Repository layout

```
skills/
  {name}/
    SKILL.md        # the contract the agent follows
    references/     # optional deep-dive docs, loaded on demand
    assets/         # optional templates and scripts
```

## Contributing

See [`AGENTS.md`](./AGENTS.md) for the skill format rules, style guide, and validation commands. Markdown is formatted with `oxfmt`:

```sh
npm install     # once, enables the pre-commit hook
npm run fmt     # format the repository
```
