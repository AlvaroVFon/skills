#!/usr/bin/env python3
"""Render a tech-debt-scan report JSON into the Markdown view for the chat.

Usage:
    render_report.py --json <report.json>

Prints to stdout: the skill never writes a .md file, it shows this output in the
chat when the chosen output format is `markdown`. The output follows
assets/tech-debt-report.md and is deterministic. Only open findings
(new/persists/regressed) appear in Findings, ordered by priority descending.

Exit codes:
    0  rendered
    1  `ERROR:` line reported
"""

import argparse
import json
import sys

STATUS_LABEL = {"new": "New", "persists": "Persists", "regressed": "Regressed", "fixed": "Fixed"}
LISTED = {"new", "persists", "regressed"}


def yaml_list(values):
    if not values:
        return "[]"
    return "[" + ", ".join(json.dumps(v) for v in values) + "]"


def render(report):
    out = ["---"]
    out.append(f'date: "{report["date"]}"')
    out.append(f'scan_type: "{report["scan_type"]}"')
    out.append(f'requested_by: "{report["requested_by"]}"')
    out.append(f'commit: "{report["commit"]}"')
    out.append(f'baseline: "{report["baseline"]}"')
    if report["scan_type"] == "targeted":
        out.append(f"scope: {yaml_list(report.get('scope'))}")
    out += ["---", "", f"# Tech Debt Scan — {report.get('target') or 'repository'}", ""]
    out += ["## Summary", "", f"- Mode: {report['scan_type']}"]
    coverage = report.get("coverage") or {}
    for item in coverage.get("reviewed") or []:
        out.append(f"- Reviewed: {item['target']} — depth: {item['depth']}")
    for item in coverage.get("not_reviewed") or []:
        out.append(f"- Not reviewed: {item['target']} — {item['reason']}")
    c = report["counters"]
    out.append(
        f"- Open debt: {c['critical']} Critical · {c['major']} Major · {c['minor']} Minor · {c['discarded']} discarded"
    )
    out += ["", "## Delta vs previous", "", f"Baseline: {report['baseline']}", ""]
    d = report["delta"]
    line = f"- {d['persists']} Persists · {d['fixed']} Fixed · {d['new']} New · {d['not_rechecked']} Not re-checked"
    if d.get("regressed"):
        line += f" · {d['regressed']} Regressed"
    out.append(line)
    for item in d.get("fixed_items") or []:
        out.append(f"- Fixed: `{item['location']}` — {item['title']}")
    for item in d.get("not_rechecked_items") or []:
        out.append(f"- Not re-checked: `{item['location']}` — {item['reason']}")
    out += ["", "## Findings", ""]
    findings = [f for f in report.get("findings", []) if f.get("status") in LISTED]
    findings.sort(key=lambda f: -f.get("priority", 0))
    if not findings:
        out += ["_No open findings._", ""]
    for f in findings:
        loc = f["location"]
        ev = f["evidence"]
        sc = f["scores"]
        out += [f"### [{f['severity']}] {f['title']} — priority {f['priority']}", ""]
        out.append(f"- Status: {STATUS_LABEL.get(f['status'], f['status'])}")
        out.append(f"- Category: {f['category']}")
        out.append(f"- Complexity: {f['symptom']} / {f['cause']}")
        out.append(f"- Scores: I{sc['impact']} · F{sc['frequency']} · R{sc['reach']} · E{sc['effort']}")
        out.append(f"- Location: `{loc['file']}:{loc['line']}`")
        out.append(f"- Debt: {f['description']}")
        out.append(f"- Impact: {f['impact']}")
        out.append(f"- Evidence: `{ev['method']}` → {ev['result']}")
        if f.get("remediation"):
            out.append(f"- Remediation: {f['remediation']}")
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
