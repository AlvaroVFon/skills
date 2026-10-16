# 01 — Package Managers

Detect the ecosystem and the exact package manager before running anything. The lockfile decides when several managers are possible; a `packageManager` field or equivalent wins over file presence.

## Detection

| Ecosystem    | Manifest             | Manager signals                                                                     |
| ------------ | -------------------- | ----------------------------------------------------------------------------------- |
| JS/TS        | `package.json`       | `pnpm-lock.yaml` → pnpm; `yarn.lock` → yarn; `bun.lockb`/`bun.lock` → bun; else npm |
| Python       | `pyproject.toml`     | `poetry.lock` → poetry; `uv.lock` → uv; `Pipfile.lock` → pipenv; else pip           |
| Rust         | `Cargo.toml`         | `Cargo.lock` → cargo                                                                |
| Go           | `go.mod`             | `go.sum` → go modules                                                               |
| Java         | `pom.xml`            | Maven; `build.gradle(.kts)` → Gradle                                                |
| Ruby         | `Gemfile`            | `Gemfile.lock` → bundler                                                            |
| PHP          | `composer.json`      | `composer.lock` → composer                                                          |
| .NET         | `*.csproj` / `*.sln` | `packages.lock.json` → nuget                                                        |
| Dart/Flutter | `pubspec.yaml`       | `pubspec.lock` → pub                                                                |
| Elixir       | `mix.exs`            | `mix.lock` → mix                                                                    |

If more than one manager is detected in independent workspaces, handle each workspace separately and report both.

## Commands

| Manager  | Outdated                                  | Update                                     | Audit / vulnerabilities      |
| -------- | ----------------------------------------- | ------------------------------------------ | ---------------------------- |
| npm      | `npm outdated --json`                     | `npm update` / `npm install <pkg>@<range>` | `npm audit --json`           |
| pnpm     | `pnpm outdated`                           | `pnpm update` / `pnpm up --latest`         | `pnpm audit`                 |
| yarn     | `yarn outdated`                           | `yarn upgrade` / `yarn up`                 | `yarn npm audit`             |
| bun      | `bun outdated`                            | `bun update`                               | `bun audit`                  |
| pip      | `pip list --outdated --format=json`       | `pip install -U <pkg>`                     | `pip-audit`                  |
| poetry   | `poetry show --outdated`                  | `poetry update` / `poetry add <pkg>@<ver>` | `poetry audit` (plugin)      |
| uv       | `uv pip list --outdated`                  | `uv lock --upgrade` / `uv sync --upgrade`  | `uv pip audit`               |
| cargo    | `cargo outdated`                          | `cargo update`                             | `cargo audit`                |
| go       | `go list -u -m all`                       | `go get -u ./...` / `go get pkg@ver`       | `govulncheck ./...`          |
| maven    | `mvn versions:display-dependency-updates` | `mvn versions:use-latest-releases`         | OWASP dependency-check       |
| gradle   | `gradle dependencyUpdates`                | edit versions / `gradle dependencyUpdate`  | OWASP dependencyCheckAnalyze |
| bundler  | `bundle outdated`                         | `bundle update [gem]`                      | `bundle audit`               |
| composer | `composer outdated`                       | `composer update [pkg]`                    | `composer audit`             |

Treat a missing audit tool (e.g. `cargo audit`, `pip-audit`, `govulncheck`) as a gap: suggest installing it, and never claim "no vulnerabilities" when no audit ran.
