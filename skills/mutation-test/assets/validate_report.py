#!/usr/bin/env python3
"""Validate a mutation-test report against assets/mutation-test-report.md.

Usage:
    validate_report.py --file <path>

Reads the report from --file, or stdin if omitted. Exits 0 and prints OK when
the report is structurally valid and its counters agree, otherwise exits 1
printing one concise parseable `ERROR:` line per problem. Warnings do not
change the exit code.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR lines reported

Checks:
    E01 Missing or unterminated YAML frontmatter
    E02 Missing frontmatter key (date, scan_type, requested_by, commit, baseline)
    E03 scan_type not 'global' or 'targeted'
    E04 date is not YYYY-MM-DD
    E05 scan_type 'targeted' but 'scope' is missing or empty
    E06 Missing required section (Summary, By module, Delta vs previous, Survivors)
    E07 Summary missing the 'Mutation score:' line
    E08 Declared mutation score disagrees with Killed/Survived
    E09 Declared Survived count disagrees with the survivor blocks
    E10 A survivor block is missing its Location or an unknown Operator
    E11 'Not reviewed' line absent from Summary
    E12 Unresolved '{...}' placeholder remains
    W13 scan_type 'global' but a 'scope' key is present
    W14 By-module Killed/Survived totals disagree with the summary
"""

import argparse
import re
import sys

REQUIRED_KEYS = ("date", "scan_type", "requested_by", "commit", "baseline")
SECTIONS = ("Summary", "By module", "Delta vs previous", "Survivors")
OPERATORS = (
    "boundary",
    "conditional",
    "logical",
    "arithmetic",
    "statement-removal",
    "return",
    "literal",
    "branch",
    "argument",
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
PLACEHOLDER_RE = re.compile(r"\{[^{}\n]+\}")
SCORE_RE = re.compile(r"Mutation score:\s*(\d+)%\s*\((\d+)\s*Killed\s*[·•*]\s*(\d+)\s*Survived\)")
MODULE_ROW_RE = re.compile(r"^\|\s*`[^`]+`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)%\s*\|\s*$")
SURVIVOR_RE = re.compile(r"^###\s+\[(Critical|Major|Minor)\]")


def split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i], "\n".join(lines[i + 1 :])
    return None, None


def top_level(fm_lines):
    values = {}
    for line in fm_lines:
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if m:
            values[m.group(1)] = m.group(2).strip()
    return values


def parse_sections(body):
    sections, current = {}, None
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+)", line)
        if m:
            current = m.group(1).strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {k: "\n".join(v) for k, v in sections.items()}


def survivor_blocks(section_body):
    blocks, current = [], None
    for line in section_body.splitlines():
        if re.match(r"^#{1,3}\s", line):
            if current is not None:
                blocks.append("\n".join(current))
            current = [line] if re.match(r"^###\s", line) else None
        elif current is not None:
            current.append(line)
    if current is not None:
        blocks.append("\n".join(current))
    return [b for b in blocks if SURVIVOR_RE.match(b.splitlines()[0])]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="-")
    args = parser.parse_args()

    if args.file == "-":
        text = sys.stdin.read()
    else:
        try:
            text = open(args.file, encoding="utf-8").read()
        except OSError as e:
            print(f"ERROR: E01 cannot read file: {e}")
            sys.exit(1)

    errors, warnings = [], []

    fm_lines, body = split_frontmatter(text)
    if fm_lines is None:
        print("ERROR: E01 missing or unterminated YAML frontmatter ('---' block)")
        sys.exit(1)

    fm = top_level(fm_lines)
    for key in REQUIRED_KEYS:
        if not fm.get(key):
            errors.append(f"ERROR: E02 missing frontmatter key '{key}'")

    scan_type = fm.get("scan_type", "").strip().strip("\"'")
    if scan_type and scan_type not in ("global", "targeted"):
        errors.append(f"ERROR: E03 scan_type {scan_type!r} not 'global' or 'targeted'")

    date = fm.get("date", "").strip().strip("\"'")
    if date and not DATE_RE.match(date):
        errors.append(f"ERROR: E04 date {date!r} is not YYYY-MM-DD")

    scope = fm.get("scope", "")
    if scan_type == "targeted" and not scope.strip().strip("\"'[]"):
        errors.append("ERROR: E05 scan_type 'targeted' requires a non-empty 'scope' list")
    if scan_type == "global" and scope:
        warnings.append("WARNING: W13 scan_type 'global' has a 'scope' key; remove it")

    sections = parse_sections(body)
    for name in SECTIONS:
        if name not in sections:
            errors.append(f"ERROR: E06 missing required section '## {name}'")

    if "Summary" in sections and "not reviewed" not in sections["Summary"].lower():
        errors.append("ERROR: E11 Summary has no 'Not reviewed:' line")

    m = SCORE_RE.search(body)
    if not m:
        errors.append("ERROR: E07 Summary has no 'Mutation score: N% (N Killed · N Survived)' line")
        killed = survived = 0
    else:
        killed, survived = int(m.group(2)), int(m.group(3))
        if killed + survived > 0:
            expected = round(killed * 100 / (killed + survived))
            if abs(int(m.group(1)) - expected) > 1:
                errors.append(
                    f"ERROR: E08 score {m.group(1)}% but {killed} Killed/{survived} Survived => {expected}%"
                )

    blocks = survivor_blocks(sections.get("Survivors", ""))
    if m and len(blocks) != survived:
        errors.append(
            f"ERROR: E09 declared {survived} Survived but found {len(blocks)} survivor block(s)"
        )

    for block in blocks:
        head = block.splitlines()[0]
        if not re.search(r"^-\s+Location:\s*`[^`]+`", block, re.MULTILINE):
            errors.append(f"ERROR: E10 survivor '{head.strip()}' has no '- Location: `file:line`'")
        op = re.search(r"^-\s+Operator:\s*(\S+)", block, re.MULTILINE)
        if not op:
            errors.append(f"ERROR: E10 survivor '{head.strip()}' has no '- Operator:'")
        elif op.group(1).strip().strip("\"'`") not in OPERATORS:
            errors.append(
                f"ERROR: E10 survivor '{head.strip()}' Operator {op.group(1)!r} not in {', '.join(OPERATORS)}"
            )

    rows = [MODULE_ROW_RE.match(ln) for ln in sections.get("By module", "").splitlines()]
    rows = [r for r in rows if r]
    if m and rows:
        mod_killed = sum(int(r.group(2)) for r in rows)
        mod_survived = sum(int(r.group(3)) for r in rows)
        if (mod_killed, mod_survived) != (killed, survived):
            warnings.append(
                f"WARNING: W14 by-module totals {mod_killed} Killed/{mod_survived} Survived "
                f"differ from summary {killed}/{survived}"
            )

    probe = FENCE_RE.sub("", body)
    leftover = PLACEHOLDER_RE.findall(probe)
    if leftover:
        sample = ", ".join(sorted(set(leftover))[:5])
        errors.append(f"ERROR: E12 {len(leftover)} unresolved placeholder(s) remain: {sample}")

    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    if errors:
        sys.exit(1)
    print("OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
