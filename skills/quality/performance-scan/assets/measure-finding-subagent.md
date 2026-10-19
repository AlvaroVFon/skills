# Measurement Subagent Prompt

Fill the placeholders and pass as the subagent task. One finding per subagent.

---

You are measuring exactly one performance hypothesis. Return facts, not a verdict.

## Finding

- Location: `{file}:{line}`
- Category: `{algorithmic | io-db | memory | concurrency | payload-render}`
- Prediction: `{X}` with input size `{small}` vs `{large}` must show `{metric}` growing `{growth}`.

## Recon facts

- Language/runtime: `{runtime}`
- Test or benchmark framework: `{framework | none}`
- Run one file with: `{command}`

## Hard constraints

- NEVER modify production code or existing tests. Create ONE new temp file named `{*.performance-scan.<id>.*}` next to the repo tests.
- Run only that file, locally. Do not start services, databases, or queues; stub I/O and count calls instead.
- Measure at two or more input sizes; repeat each three times and keep the median.
- Delete the temp file before returning.

## Return

1. The benchmark code.
2. The exact command run.
3. The raw output.
4. Metric `name`, `unit`, median at `small`, median at `large`, and observed growth.
5. `degraded-as-predicted: yes | no | cannot-run` plus one line why.
6. The temp file path and confirmation it was deleted.
