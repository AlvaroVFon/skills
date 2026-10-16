# 03 — Breaking Changes

For every major bump — and for any non-patch jump that looks risky — find out what breaks before applying it. A semver major means "assume breaking until proven otherwise".

## Sources, in order

1. **Context7 MCP (preferred when available).** If a Context7 MCP server is configured, use it to pull current, versioned library docs instead of guessing. Check the configured MCP servers/resources first; typical flow is resolve the library id, then fetch docs. Use the installed version as the anchor.
2. **Repository changelog.** `CHANGELOG.md`, `HISTORY.md`, or the project's release notes file.
3. **GitHub Releases / tags.** Release notes for the target version and every version in between.
4. **Migration / upgrade guide.** Usually linked from the release notes; follow it literally.
5. **Deprecation warnings.** Warnings emitted by the current version name what the next major removes.

## Per candidate, record

| Field            | Content                                                        |
| ---------------- | -------------------------------------------------------------- |
| Package          | name, `from → to`                                              |
| Breaking changes | the concrete API/behavior/config changes that affect this repo |
| Migration steps  | required code, config, or type changes                         |
| Risk             | low / medium / high, with the reason                           |
| Recommendation   | apply, apply with migration, or hold with rationale            |

Present majors with this table and ask before applying any of them. When a breaking change is only "theoretical" (not used by this repo), say so and cite where you checked; do not apply it silently.

If no changelog or docs can be found, treat the update as unverified, keep it in the ask list, and say the information was unavailable.
