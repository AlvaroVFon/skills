#!/usr/bin/env python3
"""Validate a bug-scan report against assets/bug-scan-report.md.

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
    E06 Missing required section (Summary, Delta vs previous, Findings)
    E07 Summary missing the 'Findings:' counter line
    E08 Declared findings counters disagree with the finding blocks
    E09 A finding block is missing its Location or an unknown Category
    E10 'Not reviewed' line absent from Summary
    E11 Unresolved '{...}' placeholder remains
    W12 scan_type 'global' but a 'scope' key is present
    W13 Delta section missing a 'Baseline:' line
"""

import argparse
import re
import sys

REQUIRED_KEYS = ("date", "scan_type", "requested_by", "commit", "baseline")
SECTIONS = ("Summary", "Delta vs previous", "Findings")
CATEGORIES = ("logic", "concurrency", "errors-resources", "data-integrity")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
PLACEHOLDER_RE = re.compile(r"\{[^{}\n]+\}")
COUNTER_RE = re.compile(
    r"Findings:\s*(\d+)\s+Confirmed\s*[·•*]\s*(\d+)\s+Unconfirmed\s*[·•*]\s*(\d+)\s+discarded"
)
FINDING_RE = re.compile(r"^###\s+\[(Critical|Major|Minor)\]\s+(.+?)\s+[—–-]\s+(Confirmed|Unconfirmed)\s*$")


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


def finding_blocks(section_body):
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
    return [b for b in blocks if FINDING_RE.match(b.splitlines()[0])]


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
        warnings.append("WARNING: W12 scan_type 'global' has a 'scope' key; remove it")

    sections = parse_sections(body)
    for name in SECTIONS:
        if name not in sections:
            errors.append(f"ERROR: E06 missing required section '## {name}'")

    if "Summary" in sections and "not reviewed" not in sections["Summary"].lower():
        errors.append("ERROR: E10 Summary has no 'Not reviewed:' line")
    if "Delta vs previous" in sections and "baseline:" not in sections["Delta vs previous"].lower():
        warnings.append("WARNING: W13 'Delta vs previous' has no 'Baseline:' line")

    blocks = finding_blocks(sections.get("Findings", ""))
    actual_confirmed = sum(1 for b in blocks if FINDING_RE.match(b.splitlines()[0]).group(3) == "Confirmed")
    actual_unconfirmed = len(blocks) - actual_confirmed

    m = COUNTER_RE.search(body)
    if not m:
        errors.append("ERROR: E07 Summary has no 'Findings: N Confirmed · N Unconfirmed · N discarded' line")
    else:
        declared = (int(m.group(1)), int(m.group(2)))
        if declared != (actual_confirmed, actual_unconfirmed):
            errors.append(
                f"ERROR: E08 declared {declared[0]} Confirmed/{declared[1]} Unconfirmed "
                f"but found {actual_confirmed} Confirmed/{actual_unconfirmed} Unconfirmed blocks"
            )

    for block in blocks:
        head = block.splitlines()[0]
        if not re.search(r"^-\s+Location:\s*`[^`]+`", block, re.MULTILINE):
            errors.append(f"ERROR: E09 finding '{head.strip()}' has no '- Location: `file:line`'")
        cat = re.search(r"^-\s+Category:\s*(\S+)", block, re.MULTILINE)
        if not cat:
            errors.append(f"ERROR: E09 finding '{head.strip()}' has no '- Category:'")
        elif cat.group(1).strip().strip("\"'`") not in CATEGORIES:
            errors.append(
                f"ERROR: E09 finding '{head.strip()}' Category {cat.group(1)!r} not in {', '.join(CATEGORIES)}"
            )

    probe = FENCE_RE.sub("", body)
    leftover = PLACEHOLDER_RE.findall(probe)
    if leftover:
        sample = ", ".join(sorted(set(leftover))[:5])
        errors.append(f"ERROR: E11 {len(leftover)} unresolved placeholder(s) remain: {sample}")

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
