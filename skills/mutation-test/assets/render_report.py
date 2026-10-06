#!/usr/bin/env python3
"""Render a mutation-test report JSON into the Markdown view for the chat.

Usage:
    render_report.py --json <report.json>

Prints to stdout: the skill never writes a .md file, it shows this output in the
chat when the chosen output format is `markdown`. The output follows
assets/mutation-test-report.md and is deterministic.

Exit codes:
    0  rendered
    1  `ERROR:` line reported
"""

import argparse
import json
import sys

SEVERITY_RANK = {"Critical": 0, "Major": 1, "Minor": 2}
STATUS_LABEL = {"new": "New", "persists": "Persists", "regressed": "Regressed", "killed": "Killed"}
SURVIVOR = {"new", "persists", "regressed"}


def yaml_list(values):
    if not values:
        return "[]"
    return "[" + ", ".join(json.dumps(v) for v in values) + "]"


def render(report):
    out = []
    out.append("---")
    out.append(f'date: "{report["date"]}"')
    out.append(f'scan_type: "{report["scan_type"]}"')
    out.append(f'requested_by: "{report["requested_by"]}"')
    out.append(f'commit: "{report["commit"]}"')
    out.append(f'baseline: "{report["baseline"]}"')
    if report["scan_type"] == "targeted":
        out.append(f"scope: {yaml_list(report.get('scope'))}")
    out.append("---")
    out.append("")
    out.append(f"# Mutation Test — {report.get('target') or 'repository'}")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- Mode: {report['scan_type']}")
    summary = report["summary"]
    out.append(f"- Mutation score: {summary['score']}% ({summary['killed']} Killed · {summary['survived']} Survived)")
    out.append(
        f"- Mutants: {summary['generated']} generated · {summary['invalid']} Invalid · "
        f"{summary['equivalent']} Equivalent · {summary['not_run']} Not run · {summary['inconclusive']} Inconclusive"
    )
    if report.get("cap"):
        out.append(f"- Cap used: {report['cap']}")
    for item in (report.get("coverage") or {}).get("reviewed") or []:
        out.append(f"- Reviewed: {item['target']} — mutants: {item['mutants']}")
    for group in ("not_reviewed", "not_covered"):
        for item in (report.get("coverage") or {}).get(group) or []:
            label = "Not reviewed" if group == "not_reviewed" else "Not covered"
            out.append(f"- {label}: {item['target']} — {item['reason']}")
    out.append("")
    out.append("## By module")
    out.append("")
    out.append("| Module | Mutants | Killed | Survived | Score |")
    out.append("| ------ | ------- | ------ | -------- | ----- |")
    for row in report.get("by_module") or []:
        out.append(
            f"| `{row['module']}` | {row['mutants']} | {row['killed']} | {row['survived']} | {row['score']}% |"
        )
    out.append("")
    out.append("## Delta vs previous")
    out.append("")
    out.append(f"Baseline: {report['baseline']}")
    out.append("")
    delta = report["delta"]
    line = f"- {delta['persists']} Persists · {delta['killed']} Killed now · {delta['new']} New · {delta['not_rechecked']} Not re-checked"
    if delta.get("regressed"):
        line += f" · {delta['regressed']} Regressed"
    out.append(line)
    for item in delta.get("killed_items") or []:
        out.append(f"- Killed now: `{item['location']}` — {item['title']}")
    for item in delta.get("not_rechecked_items") or []:
        out.append(f"- Not re-checked: `{item['location']}` — {item['reason']}")
    out.append("")
    out.append("## Survivors")
    out.append("")
    findings = [f for f in report.get("findings", []) if f.get("status") in SURVIVOR]
    findings.sort(key=lambda f: SEVERITY_RANK.get(f.get("severity"), 9))
    if not findings:
        out.append("_No surviving mutants._")
        out.append("")
    for finding in findings:
        loc = finding["location"]
        out.append(f"### [{finding['severity']}] {finding['title']}")
        out.append("")
        out.append(f"- Status: {STATUS_LABEL.get(finding['status'], finding['status'])}")
        out.append(f"- Location: `{loc['file']}:{loc['line']}`")
        out.append(f"- Operator: {finding['operator']}")
        out.append(f"- Gap: {finding['gap']}")
        out.append("")
        if finding.get("mutant_diff"):
            out.append("**Mutant**")
            out.append("")
            out.append("```diff")
            out.append(finding["mutant_diff"].rstrip())
            out.append("```")
            out.append("")
        evidence = finding.get("evidence") or {}
        if evidence.get("code"):
            lang = evidence.get("lang") or ""
            out.append("**Suggested test** (temporary, not kept in the repo)")
            out.append("")
            out.append(f"```{lang}")
            out.append(evidence["code"].rstrip())
            out.append("```")
            out.append("")
            out.append(f"Output: {evidence.get('output') or 'not runnable: (no output)'}")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    args = parser.parse_args()
    try:
        with open(args.json, encoding="utf-8") as fh:
            report = json.load(fh)
    except OSError as e:
        print(f"ERROR: cannot read {args.json}: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {args.json}: {e}")
        sys.exit(1)
    sys.stdout.write(render(report))


if __name__ == "__main__":
    main()
