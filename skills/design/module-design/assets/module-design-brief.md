# Module Design Brief Format

Each analysis writes exactly one artifact: `docs/module-design/{YYYY-MM-DD}-{module}.json`, authored from `assets/module-design-brief.template.json`, reconciled by `assets/reconcile.py`, and validated by `assets/validate_brief.py`. There is no ledger and no rendered file; the dated JSON is the history. See `references/05-baseline-history.md`.

The output format only controls how the human view is delivered: `chat` prints the brief inline, `markdown` prints the view below (`assets/render_brief.py` to the chat), and `adr` additionally delegates to the `adr` skill. Never show both chat and markdown.

## Rendered Markdown

````markdown
# Module Design Brief — {module}

## Responsibility

{One sentence. If you cannot state it in one sentence, the boundary is wrong.}

## Public Interface

```{language}
{signed public surface: exported services/use-cases, DTOs, events, ports}
```
````

## Hidden Knowledge

- {design decision encapsulated by the module, one per line}

## Complexity Absorbed

- {edge cases, derived data, defaults handled internally}

## Failure Contract

| Failure          | How the caller sees it  | Caller action       |
| ---------------- | ----------------------- | ------------------- |
| {domain failure} | {domain error / result} | {expected handling} |

## Split or Merge Decision

- Decision: {split / merge / keep}
- Rationale (net complexity): {why}

## Depth Verdict

| Granularity             | Verdict                       | Evidence                     |
| ----------------------- | ----------------------------- | ---------------------------- |
| Macro (module boundary) | {deep / acceptable / shallow} | {caller snippet observation} |
| Micro (artifacts)       | {deep / acceptable / shallow} | {observation}                |

### Caller Snippet

```{language}
{smallest realistic external usage}
```

## Leakage Flags

- [{severity}] {type}: {title} — {detail} `{file}:{line}`

## Improvements

- [{severity}] {title} — {detail}

## Delta vs previous

Baseline: {previous brief path or "first scan"}

- {n} Persists · {n} Resolved · {n} New · {n} Not re-checked
- Resolved: `{file}:{line}` — {title}
- Not re-checked: `{file}:{line}` — {reason}

## Before / After Interface

{Full alternative interface only when the verdict is shallow.}

```

```
