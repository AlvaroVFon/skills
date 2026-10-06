#!/usr/bin/env python3
"""Render a module-design brief JSON into the Markdown view for the chat.

Usage:
    render_brief.py --json <brief.json>

Prints to stdout: the skill never writes a .md file, it shows this output in the
chat when the chosen output format is `markdown`. The output follows
assets/module-design-brief.md and is deterministic.

Exit codes:
    0  rendered
    1  `ERROR:` line reported
"""

import argparse
import json
import sys

LEAKAGE = {"leakage-interface", "leakage-back-door"}
STATUS_LABEL = {"new": "New", "persists": "Persists", "resolved": "Resolved", "regressed": "Regressed"}


def render(brief):
    out = []
    out.append(f"# Module Design Brief — {brief['module']}")
    out.append("")
    out.append("## Responsibility")
    out.append("")
    out.append(brief["responsibility"])
    out.append("")
    out.append("## Public Interface")
    out.append("")
    out.append(f"```{brief['public_interface'].get('language', '')}")
    out.append(brief["public_interface"].get("code", "").rstrip())
    out.append("```")
    out.append("")
    out.append("## Hidden Knowledge")
    out.append("")
    for item in brief.get("hidden_knowledge") or []:
        out.append(f"- {item}")
    out.append("")
    out.append("## Complexity Absorbed")
    out.append("")
    for item in brief.get("complexity_absorbed") or []:
        out.append(f"- {item}")
    out.append("")
    out.append("## Failure Contract")
    out.append("")
    out.append("| Failure | How the caller sees it | Caller action |")
    out.append("| ------- | ---------------------- | ------------- |")
    for row in brief.get("failure_contract") or []:
        out.append(f"| {row['failure']} | {row['caller_sees']} | {row['caller_action']} |")
    out.append("")
    out.append("## Split or Merge Decision")
    out.append("")
    split = brief.get("split_merge") or {}
    out.append(f"- Decision: {split.get('decision', 'keep')}")
    out.append(f"- Rationale (net complexity): {split.get('rationale', '')}")
    out.append("")
    out.append("## Depth Verdict")
    out.append("")
    depth = brief["depth_verdict"]
    out.append("| Granularity | Verdict | Evidence |")
    out.append("| ----------- | ------- | -------- |")
    out.append(f"| Macro (module boundary) | {depth['macro']} | {depth.get('macro_evidence', '')} |")
    out.append(f"| Micro (artifacts) | {depth['micro']} | {depth.get('micro_evidence', '')} |")
    out.append("")
    snippet = brief.get("caller_snippet") or {}
    if snippet.get("code"):
        out.append("### Caller Snippet")
        out.append("")
        out.append(f"```{snippet.get('language', '')}")
        out.append(snippet["code"].rstrip())
        out.append("```")
        out.append("")
    findings = brief.get("findings") or []
    out.append("## Leakage Flags")
    out.append("")
    leakage = [f for f in findings if f.get("type") in LEAKAGE]
    if not leakage:
        out.append("- None.")
    for finding in leakage:
        loc = finding.get("location") or {}
        where = f" `{loc.get('file')}:{loc.get('line')}`" if loc.get("file") else ""
        out.append(f"- [{finding['severity']}] {finding['type']}: {finding['title']} — {finding['detail']}{where}")
    out.append("")
    out.append("## Improvements")
    out.append("")
    others = [f for f in findings if f.get("type") not in LEAKAGE]
    if not others:
        out.append("- None.")
    for finding in others:
        out.append(f"- [{finding['severity']}] {finding['title']} — {finding['detail']}")
    out.append("")
    out.append("## Delta vs previous")
    out.append("")
    out.append(f"Baseline: {brief.get('baseline', 'none')}")
    out.append("")
    delta = brief.get("delta") or {}
    line = (
        f"- {delta.get('persists', 0)} Persists · {delta.get('resolved', 0)} Resolved · "
        f"{delta.get('new', 0)} New · {delta.get('not_rechecked', 0)} Not re-checked"
    )
    if delta.get("regressed"):
        line += f" · {delta['regressed']} Regressed"
    out.append(line)
    for item in delta.get("resolved_items") or []:
        out.append(f"- Resolved: `{item['location']}` — {item['title']}")
    for item in delta.get("not_rechecked_items") or []:
        out.append(f"- Not re-checked: `{item['location']}` — {item['reason']}")
    out.append("")
    out.append("## Before / After Interface")
    out.append("")
    out.append(brief.get("before_after_interface") or "Not applicable: verdict is deep/acceptable.")
    return "\n".join(out).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    args = parser.parse_args()
    try:
        with open(args.json, encoding="utf-8") as fh:
            brief = json.load(fh)
    except OSError as e:
        print(f"ERROR: cannot read {args.json}: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {args.json}: {e}")
        sys.exit(1)
    sys.stdout.write(render(brief))


if __name__ == "__main__":
    main()
