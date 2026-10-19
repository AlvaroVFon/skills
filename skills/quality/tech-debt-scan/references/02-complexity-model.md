# 02 — Complexity Model

## Definition

**Complexity** is anything in the structure of a system that makes it hard to understand and modify. **Technical debt** is complexity accumulated by tactical shortcuts. A finding is debt only if a **symptom** can be named in the current code; otherwise discard it.

Total complexity of a system is `C = Σ (cₚ × tₚ)`: the complexity of each part weighted by the time developers spend in it. This is why scoring multiplies `impact` (cₚ) by `frequency` (tₚ), and why `reach` counts how many parts pay the cost (`06`).

## Symptoms (pick one per finding)

| Symptom                | Observed as                                 | Facts to measure                                                      |
| ---------------------- | ------------------------------------------- | --------------------------------------------------------------------- |
| `change-amplification` | A simple change forces edits in many places | Co-change in git, duplicated blocks, count of importers or call sites |
| `cognitive-load`       | Too much must be known to touch it          | Size, branches, parameter count, shallow or pass-through modules      |
| `unknown-unknowns`     | Unclear what to change or what will break   | Implicit coupling, shared mutable state, docs that lie, missing tests |

When several apply, choose the one that costs most today; mention the others in `description`.

## Causes (pick one per finding)

| Cause        | Signals                                                                                              |
| ------------ | ---------------------------------------------------------------------------------------------------- |
| `dependency` | Cross-layer imports, cycles, information leaking across modules, temporal decomposition, god modules |
| `obscurity`  | Vague names, outdated docs, undocumented config, special cases and sentinel values, hidden order     |

## Co-change Evidence

```bash
git log --since="6 months ago" --name-only --pretty=format:'--' -- <path> | awk '/^--$/{n++; next} NF{c[$0]++} END{for(f in c) print c[f], f}' | sort -rn | head
```

Files that change together without a visible import between them indicate hidden dependency (`unknown-unknowns`).

## Next Step

For the top `architecture` findings (leaky boundaries, shallow modules, god modules), suggest running `module-design` on that module. This skill never designs the fix.
