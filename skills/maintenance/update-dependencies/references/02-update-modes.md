# 02 — Update Modes

The user always picks the mode. Never infer it, never default to `major`.

## Semver

`MAJOR.MINOR.PATCH` for `1.2.3`:

- **patch** — `1.2.3 → 1.2.4`: backwards-compatible fixes. Safe to auto-apply.
- **minor** — `1.2.3 → 1.3.0`: backwards-compatible additions. Usually safe; still check the changelog.
- **major** — `1.2.3 → 2.0.0`: may break. Always ask before applying.

The declared range also matters: `^1.2.3` allows minor+patch, `~1.2.3` allows patch only, an exact pin allows nothing. "Latest" can cross a major through the range even when the mode is `minor`; respect the chosen mode over the range.

## Mode meaning

| Mode    | Apply                                      | Ask before                              |
| ------- | ------------------------------------------ | --------------------------------------- |
| `patch` | patch bump only                            | anything minor/major                    |
| `minor` | patch + minor                              | anything major                          |
| `major` | all updates, including majors and breaking | every major/breaking update, one by one |

## Applying a mode

- Prefer the manager's own flag to scope the bump; otherwise update within the range and verify the resulting versions.
- Do not widen a range to force a newer version unless the user approved that major.
- Reinstall after each batch so the lockfile and installed tree stay consistent; never edit the lockfile by hand.
