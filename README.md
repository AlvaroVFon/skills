# Skills

A collection of **LLM-first skills**: reusable instruction packs that teach AI coding agents how to perform a specific task consistently.

Each skill is a folder under `skills/` with a `SKILL.md` (the runtime contract) plus optional `references/` and `assets/`.

## Available skills

| Skill            | What it does                                                       |
| ---------------- | ------------------------------------------------------------------ |
| `skill-creator`  | Create new LLM-first skills with valid frontmatter.                |
| `skill-improver` | Audit and upgrade existing skills.                                 |
| `create-commit`  | Write validated Conventional Commits (`type(scope): subject`).     |
| `create-pr`      | Open standardized pull requests via the `gh` CLI.                  |
| `code-review`    | Review pull requests and diffs; requests changes, never merges.    |
| `module-design`  | Design and analyze domain module boundaries and interfaces.        |
| `adr`            | Write architecture and design decision records (MADR).             |
| `bug-scan`       | Scan a repo or modules for latent bugs and prove each with a test. |

## Usage

Skills are loaded by compatible agents (for example [opencode](https://opencode.ai)). To enable these skills, place them in your agent's skills directory:

```sh
git clone https://github.com/AlvaroVFon/skills.git
cp -r skills/* ~/.config/opencode/skills/
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
