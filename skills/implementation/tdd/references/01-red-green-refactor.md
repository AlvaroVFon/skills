# 01 — Red, Green, Refactor

## Cycle

| Phase    | Goal                                            | Rule                                                  |
| -------- | ----------------------------------------------- | ----------------------------------------------------- |
| Red      | A failing test that specifies the next behavior | Must fail for the predicted reason, not a setup error |
| Green    | The minimal code to pass                        | No extra behavior; no speculative generality          |
| Refactor | Remove the mess the green step created          | Tests stay green; load the `refactor` skill           |

## Discipline

- One behavior per cycle; write the smallest test that expresses it.
- Do not write production code until a test demands it.
- Do not refactor while red; revert to green first.
- Keep cycles commit-sized: each red→green→refactor is a reviewable unit.
- If the next test is hard to write, the interface is wrong; adjust the design before coding.

## Anti-Patterns

| Pattern                            | Problem                                          |
| ---------------------------------- | ------------------------------------------------ |
| Test after code                    | Tests fit the implementation instead of the spec |
| Assertion on implementation detail | Breaks on refactor; tests the how, not the what  |
| Multiple behaviors per cycle       | A failing test no longer points to one cause     |
| Weakening a test to pass           | Hides the defect the test exists to catch        |
