# Module Design Brief — {module}

## Responsibility

{One sentence. If you cannot state it in one sentence, the boundary is wrong.}

## Public Interface

```{language}
{signed public surface: exported services/use-cases, DTOs, events, ports}
```

## Hidden Knowledge

- {design decisions encapsulated by the module, one per line}

## Complexity Absorbed

- {edge cases, derived data, defaults handled internally}

## Failure Contract

| Failure          | How the caller sees it  | Caller action       |
| ---------------- | ----------------------- | ------------------- |
| {domain failure} | {domain error / result} | {expected handling} |

## Split or Merge Decision

- Decision: {split / merge / keep as is}
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

- Interface leakage: {none / list}
- Back-door leakage: {none / list}

## Improvements

- {improvement, always considered}

## Before / After Interface

{Full alternative interface only when the verdict is shallow.}
