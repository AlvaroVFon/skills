# Verification Subagent Prompt

Fill the placeholders and pass as the subagent task. One finding per subagent.

---

You are verifying exactly one bug hypothesis. Return facts, not a verdict.

## Finding

- Location: `{file}:{line}`
- Category: `{logic | concurrency | errors-resources | data-integrity}`
- Prediction: calling `{X}` with `{Y}` must `{return/throw Z}`, but returns `{W}`.

## Recon facts

- Test framework: `{framework}`
- Test location: `{dir}`
- Run one test file with: `{command}`

## Hard constraints

- NEVER modify production code or existing tests. Create ONE new temp file named `{*.bug-scan.<id>.*}` next to the repo tests.
- Run only that file. Do not start services, databases, or queues.
- Delete the temp file before returning.

## Return

1. The test code.
2. The exact command run.
3. The raw output.
4. `failed-as-predicted: yes | no | cannot-run` plus one line why.
5. The temp file path and confirmation it was deleted.
