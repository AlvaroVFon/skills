#!/usr/bin/env python3
"""Render a bug-scan report JSON into the Markdown view for the chat.

Usage:
    render_report.py --json <report.json>

Prints to stdout: the skill never writes a .md file, it shows this output in the
chat when the chosen output format is `markdown`. The output follows
assets/bug-scan-report.md and is deterministic: the same JSON always renders
the same Markdown. Only findings still open (new/persists/regressed) appear in
the Findings section; fixed and not-re-checked items appear in the delta.

Exit codes:
    0  rendered
    1  `ERROR:` line reported
"""

import argparse
import json
import sys

SEVERITY_RANK = {"Critical": 0, "Major": 1, "Minor": 2}
STATUS_LABEL = {"new": "New", "persists": "Persists", "regressed": "Regressed", "fixed": "Fixed"}
LISTED = {"new", "persists", "regressed"}


def yaml_list(values):
    if not values:
        return "[]"
    return "[" + ", ".join(json.dumps(v) for v in values) + "]"


def render(report):
    out = []
    scope = report.get("scope")
    out.append("---")
    out.append(f'date: "{report["date"]}"')
    out.append(f'scan_type: "{report["scan_type"]}"')
    out.append(f'requested_by: "{report["requested_by"]}"')
    out.append(f'commit: "{report["commit"]}"')
    out.append(f'baseline: "{report["baseline"]}"')
    if report["scan_type"] == "targeted":
        out.append(f"scope: {yaml_list(scope)}")
    out.append("---")
    out.append("")
    out.append(f"# Bug Scan — {report.get('target') or 'repository'}")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- Mode: {report['scan_type']}")
    for item in (report.get("coverage") or {}).get("reviewed") or []:
        out.append(f"- Reviewed: {item['target']} — depth: {item['depth']}")
    for item in (report.get("coverage") or {}).get("not_reviewed") or []:
        out.append(f"- Not reviewed: {item['target']} — {item['reason']}")
    counters = report["counters"]
    out.append(f"- Findings: {counters['confirmed']} Confirmed · {counters['unconfirmed']} Unconfirmed · {counters['discarded']} discarded")
    out.append("")
    out.append("## Delta vs previous")
    out.append("")
    out.append(f"Baseline: {report['baseline']}")
    out.append("")
    delta = report["delta"]
    line = f"- {delta['persists']} Persists · {delta['fixed']} Fixed · {delta['new']} New · {delta['not_rechecked']} Not re-checked"
    if delta.get("regressed"):
        line += f" · {delta['regressed']} Regressed"
    out.append(line)
    for item in delta.get("fixed_items") or []:
        out.append(f"- Fixed: `{item['location']}` — {item['title']}")
    for item in delta.get("not_rechecked_items") or []:
        out.append(f"- Not re-checked: `{item['location']}` — {item['reason']}")
    out.append("")
    out.append("## Findings")
    out.append("")
    findings = [f for f in report.get("findings", []) if f.get("status") in LISTED]
    findings.sort(key=lambda f: SEVERITY_RANK.get(f.get("severity"), 9))
    if not findings:
        out.append("_No open findings._")
        out.append("")
    for finding in findings:
        loc = finding["location"]
        out.append(f"### [{finding['severity']}] {finding['title']} — {finding['verdict']}")
        out.append("")
        out.append(f"- Status: {STATUS_LABEL.get(finding['status'], finding['status'])}")
        out.append(f"- Category: {finding['category']}")
        out.append(f"- Location: `{loc['file']}:{loc['line']}`")
        out.append(f"- Scenario: {finding['scenario']}")
        out.append("")
        evidence = finding.get("evidence") or {}
        if evidence.get("type") == "test" and evidence.get("code"):
            lang = evidence.get("lang") or ""
            out.append("**Repro test** (temporary, not kept in the repo)")
            out.append("")
            out.append(f"```{lang}")
            out.append(evidence["code"].rstrip())
            out.append("```")
            out.append("")
            out.append(f"Output: {evidence.get('output') or 'not runnable: (no output)'}")
            out.append("")
        if finding.get("verdict") == "Unconfirmed" or evidence.get("type") == "manual":
            out.append("**Manual verification**")
            out.append("")
            for i, step in enumerate(finding.get("manual_steps") or [], start=1):
                out.append(f"{i}. {step}")
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
