#!/usr/bin/env python3
"""Validate a SKILL.md against references/skill-style-guide.md.

Usage:
    validate_skill.py [--file <SKILL.md>] [--dir <skill-dir>]

Defaults to ./SKILL.md when neither is given. Exits 0 and prints OK when the
skill is structurally valid, otherwise exits 1 printing one concise parseable
`ERROR:` line per problem. Warnings do not change the exit code.

Token counts are a word-based estimate (whitespace-separated tokens); the hard
maximum is only errored when the estimate already exceeds it.

Exit codes:
    0  valid (warnings may have been printed)
    1  one or more ERROR lines reported

Checks:
    E01 SKILL.md not found or unreadable
    E02 Missing or unterminated YAML frontmatter
    E03 Missing required frontmatter key (name, description, license,
        metadata.author, metadata.version)
    E04 description must be a single quoted line
    E05 description exceeds 250 chars
    E06 Body exceeds the 1000-token hard maximum (estimated)
    E07 Missing required section
    E08 Required sections are out of order
    E09 A referenced local file does not exist
    E10 'Keywords' section or key is forbidden
    W11 description exceeds the 160-char recommendation
    W12 description does not start with 'Trigger:'
    W13 Body exceeds the 700-token recommended maximum
    W14 frontmatter 'name' differs from the skill directory name
"""

import argparse
import os
import re
import sys

ORDER = (
    "Activation Contract",
    "Hard Rules",
    "Decision Gates",
    "Execution Steps",
    "Output Contract",
    "References",
)
DESC_HARD = 250
DESC_WARN = 160
BODY_HARD = 1000
BODY_WARN = 700
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
LOCAL_REF_RE = re.compile(r"\b((?:references|assets)/[A-Za-z0-9._/-]+)")


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


def nested(fm_lines, parent):
    values, inside = {}, False
    for line in fm_lines:
        if re.match(rf"^{re.escape(parent)}:\s*$", line):
            inside = True
            continue
        if inside:
            if line and not line[0].isspace():
                inside = False
                continue
            m = re.match(r"^\s+([A-Za-z0-9_-]+):\s*(.*)$", line)
            if m:
                values[m.group(1)] = m.group(2).strip()
    return values


def section_order(body):
    found = []
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            found.append(m.group(1).strip())
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file")
    parser.add_argument("--dir")
    args = parser.parse_args()

    path = args.file
    if not path:
        base = args.dir if args.dir else "."
        path = os.path.join(base, "SKILL.md")
    skill_dir = os.path.dirname(os.path.abspath(path))

    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"ERROR: E01 cannot read SKILL.md: {e}")
        sys.exit(1)

    errors, warnings = [], []

    fm_lines, body = split_frontmatter(text)
    if fm_lines is None:
        print("ERROR: E02 missing or unterminated YAML frontmatter ('---' block)")
        sys.exit(1)

    fm = top_level(fm_lines)
    meta = nested(fm_lines, "metadata")
    required = {
        "name": fm.get("name"),
        "description": fm.get("description"),
        "license": fm.get("license"),
        "metadata.author": meta.get("author"),
        "metadata.version": meta.get("version"),
    }
    for key, value in required.items():
        if not value:
            errors.append(f"ERROR: E03 missing required frontmatter key '{key}'")

    desc = fm.get("description", "").strip()
    if desc:
        if desc in (">", "|", ">-", "|-", ">+", "|+"):
            errors.append("ERROR: E04 description must be a single quoted line, not a block scalar")
        elif not ((desc.startswith('"') and desc.endswith('"')) or (desc.startswith("'") and desc.endswith("'"))):
            errors.append("ERROR: E04 description must be wrapped in quotes")
        else:
            inner = desc[1:-1]
            if len(inner) > DESC_HARD:
                errors.append(f"ERROR: E05 description is {len(inner)} chars (max {DESC_HARD})")
            elif len(inner) > DESC_WARN:
                warnings.append(f"WARNING: W11 description is {len(inner)} chars (recommended <= {DESC_WARN})")
            if not inner.startswith("Trigger:"):
                warnings.append("WARNING: W12 description should start with 'Trigger:'")

    prose = FENCE_RE.sub("", body)
    if re.search(r"(?im)^(?:##\s*Keywords\b|Keywords\s*:)", prose):
        errors.append("ERROR: E10 'Keywords' is forbidden; put triggers in description")

    found = section_order(prose)
    for name in ORDER:
        if name not in found:
            errors.append(f"ERROR: E07 missing required section '## {name}'")
    positions = [found.index(name) for name in ORDER if name in found]
    if positions != sorted(positions):
        errors.append(f"ERROR: E08 required sections out of order; expected: {', '.join(ORDER)}")

    words = len(re.findall(r"\S+", body))
    if words > BODY_HARD:
        errors.append(f"ERROR: E06 body has ~{words} tokens (hard max {BODY_HARD})")
    elif words > BODY_WARN:
        warnings.append(f"WARNING: W13 body has ~{words} tokens (recommended max {BODY_WARN})")

    for ref in sorted(set(LOCAL_REF_RE.findall(body))):
        if not os.path.exists(os.path.join(skill_dir, ref)):
            errors.append(f"ERROR: E09 referenced local file not found: {ref}")

    name = (fm.get("name") or "").strip().strip("\"'")
    dir_name = os.path.basename(skill_dir)
    if name and dir_name and name != dir_name:
        warnings.append(f"WARNING: W14 frontmatter name {name!r} differs from directory {dir_name!r}")

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
