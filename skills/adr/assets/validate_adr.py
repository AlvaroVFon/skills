#!/usr/bin/env python3
"""Validate an ADR against assets/adr-template.md.

Usage:
    validate_adr.py --file <path> [--allow-placeholders]

Reads the ADR from --file, or stdin if omitted. Exits 0 and prints OK when the
record is structurally valid, otherwise exits 1 printing one concise parseable
`ERROR:` line per problem. Warnings do not change the exit code.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR lines reported

Checks:
    E01 Missing or unterminated YAML frontmatter
    E02 Missing frontmatter key (title, status, date, authors)
    E03 status not one of proposed|accepted|rejected|deprecated|superseded
    E04 date is not YYYY-MM-DD
    E05 authors is not a non-empty list
    E06 Missing required section
    E07 Required section present but empty
    E08 Fewer than 2 considered options
    E09 'Decision Outcome' missing a 'Chosen option:' statement
    E10 Unresolved '{...}' placeholder remains
    W11 status 'superseded' without a 'superseded-by' pointer
    W12 'supersedes' present but status is not 'superseded'
"""

import argparse
import re
import sys

STATUSES = ("proposed", "accepted", "rejected", "deprecated", "superseded")
REQUIRED_KEYS = ("title", "status", "date", "authors")
SECTIONS = (
    "Context and Problem Statement",
    "Considered Options",
    "Decision Outcome",
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PLACEHOLDER_RE = re.compile(r"\{[^{}\n]+\}")
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


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


def is_nonempty_list(value):
    v = value.strip()
    if not (v.startswith("[") and v.endswith("]")):
        return False
    inner = v[1:-1].strip()
    return bool(inner.strip("\"', "))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="-")
    parser.add_argument("--allow-placeholders", action="store_true")
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

    status = fm.get("status", "").strip().strip("\"'")
    date = fm.get("date", "").strip().strip("\"'")
    placeholders_ok = args.allow_placeholders and (
        PLACEHOLDER_RE.search(status) or PLACEHOLDER_RE.search(date)
    )

    if status and status not in STATUSES and not placeholders_ok:
        errors.append(f"ERROR: E03 status {status!r} not allowed; valid: {', '.join(STATUSES)}")

    if date and not DATE_RE.match(date) and not placeholders_ok:
        errors.append(f"ERROR: E04 date {date!r} is not YYYY-MM-DD")

    if "authors" in fm and not is_nonempty_list(fm["authors"]):
        errors.append("ERROR: E05 authors must be a non-empty list, e.g. [\"name\"]")

    sections = parse_sections(body)
    for name in SECTIONS:
        if name not in sections:
            errors.append(f"ERROR: E06 missing required section '## {name}'")
        elif not sections[name].strip():
            errors.append(f"ERROR: E07 section '## {name}' is present but empty")

    if "Considered Options" in sections:
        options = [ln for ln in sections["Considered Options"].splitlines() if re.match(r"^\s*[-*]\s+\S", ln)]
        if len(options) < 2:
            errors.append(f"ERROR: E08 'Considered Options' lists {len(options)} option(s); need at least 2")

    if "Decision Outcome" in sections and not re.search(
        r"chosen option\s*:", sections["Decision Outcome"], re.IGNORECASE
    ):
        errors.append("ERROR: E09 'Decision Outcome' has no 'Chosen option:' statement")

    if not re.search(r"#{3}\s+Consequences\b", body, re.MULTILINE):
        errors.append("ERROR: E06 missing required section '### Consequences'")

    if not args.allow_placeholders:
        probe = FENCE_RE.sub("", body)
        leftover = PLACEHOLDER_RE.findall(probe)
        if leftover:
            sample = ", ".join(sorted(set(leftover))[:5])
            errors.append(f"ERROR: E10 {len(leftover)} unresolved placeholder(s) remain: {sample}")

    if status == "superseded" and not fm.get("superseded-by"):
        warnings.append("WARNING: W11 status 'superseded' has no 'superseded-by' pointer")
    if fm.get("supersedes") and status != "superseded":
        warnings.append("WARNING: W12 'supersedes' present but status is not 'superseded'")

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
