# 01 — Refactoring Steps

## Definition

A refactoring step is the smallest structural change that keeps the scoped tests green. Compose steps; never batch them.

## Catalog

| Step                                  | Use when                                 | Note                    |
| ------------------------------------- | ---------------------------------------- | ----------------------- |
| Extract function / variable           | Expression needs a name or is reused     | Name by intent          |
| Inline                                | Indirection adds no meaning              | Opposite of extract     |
| Move                                  | Element sits in the wrong module / class | Recheck callers after   |
| Rename                                | Name no longer matches behavior          | Update all references   |
| Hide delegate                         | Caller reaches through an object         | Enforce Tell, Don't Ask |
| Replace conditional with polymorphism | Fork repeats on a type or flag           | Watch over-abstraction  |
| Remove duplication                    | Same knowledge in two or more places     | Single source of truth  |
| Delete dead code                      | Proven unused                            | Cite the proof          |

## Protocol

1. Confirm the baseline is green.
2. Apply exactly one step.
3. Run the scoped tests; if red, revert and split the step.
4. Optionally checkpoint (commit) before the next step.

## Selection

Pick the step that removes the most complexity per diff size. When two are equivalent, prefer the smaller. Stop when the next step would change behavior.
