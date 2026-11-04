#!/usr/bin/env python3
"""Build a validated, idempotent PR review payload and report.

This script is pure: it never calls GitHub. The skill collects data with `gh`,
writes an input JSON, and this script turns it into a review payload plus a
report that is validated separately by validate_review_report.py.

Usage:
    prepare_review.py --input <input.json> [--report <report.json>]
                      [--payload <payload.json>] [--check-payload <check.json>]
                      [--dry-run] [--verdict-exit]

Exit codes:
    0  input processed (inspect the report's exit_code for the verdict)
    1  invalid input or unreadable file
    2  --verdict-exit was requested and the report verdict is an error

Input contract (all paths relative to the repository root):

    {
      "repo": "owner/name",
      "pr": 123,
      "state": "open",
      "is_draft": false,
      "author": "login",
      "bot_login": "ai-reviewer[bot]",
      "title": "...",
      "url": "https://github.com/owner/name/pull/123",
      "head_sha": "40 hex chars",
      "base_sha": "40 hex chars",
      "skipped_run": null,
      "files": [{"filename": "src/a.py", "status": "modified", "patch": "@@ ..."}],
      "findings": [{"severity": "blocking", "path": "src/a.py", "line": 2,
                    "side": "RIGHT", "start_line": null, "rule": "correctness",
                    "confidence": "high", "body": "..."}],
      "existing_comments": [{"body": "... <!-- ai-review-fingerprint:... -->",
                             "user_login": "ai-reviewer[bot]"}],
      "config": {"blocking_gate": false, "inline_severities": ["blocking", "should"]},
      "errors": []
    }

Raw GitHub comments with {"user": {"login": "..."}} are also accepted.

Output contract: see assets/review-report.schema.json and
references/automation-contract.md.
"""

import argparse
import fnmatch
import hashlib
import json
import re
import sys
from datetime import datetime, timezone

SCHEMA_VERSION = "1.0"
MARKER = "<!-- ai-review -->"
FINGERPRINT_RE = re.compile(r"ai-review-fingerprint:([0-9a-f]{12})")
INLINE_FINGERPRINT_RE = re.compile(r"ai-review-fingerprint:[0-9a-f]{12}")
HUNK_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")
SEVERITIES = ("blocking", "should", "nit")
SEVERITY_RANK = {"blocking": 0, "should": 1, "nit": 2}
CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
STATUSES = ("inline", "file", "summary", "deduped", "truncated")

DEFAULT_IGNORE = [
    "*.lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "poetry.lock",
    "go.sum",
    "**/dist/**",
    "**/build/**",
    "**/vendor/**",
    "**/node_modules/**",
    "**/*.min.js",
    "**/*.min.css",
    "**/*.snap",
    "**/*.map",
    "**/__snapshots__/**",
]

DEFAULT_CONFIG = {
    "version": 1,
    "language": "en",
    "blocking_gate": False,
    "inline_severities": ["blocking", "should"],
    "max_findings": 50,
    "max_inline": 30,
    "drop_confidence_below": "medium",
    "ignore": DEFAULT_IGNORE,
    "skip_title_markers": ["[skip ai-review]", "[skip review]"],
    "skip_authors": ["dependabot[bot]", "renovate[bot]"],
    "check_run": True,
    "max_summary_chars": 60000,
}


def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def read_json(path, label):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        fail(f"cannot read {label}: {exc}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {label}: {exc}")


def as_int(value, default):
    return value if isinstance(value, int) and not isinstance(value, bool) else default


def as_bool(value, default):
    return value if isinstance(value, bool) else default


def as_list(value, default):
    return value if isinstance(value, list) else default


def normalise_config(raw, warnings):
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        warnings.append("config is not an object; using defaults")
        raw = {}
    config = dict(DEFAULT_CONFIG)
    for key, value in raw.items():
        if key not in DEFAULT_CONFIG:
            warnings.append(f"unknown config key ignored: {key}")
            continue
        if key == "version":
            if value != 1:
                warnings.append(f"unsupported config version {value!r}; using defaults")
            continue
        if key in ("max_findings", "max_inline", "max_summary_chars"):
            parsed = as_int(value, -1)
            minimum = 0 if key == "max_inline" else 1
            if parsed < minimum:
                warnings.append(
                    f"config {key} must be an integer >= {minimum}; using default"
                )
            else:
                config[key] = parsed
        elif key in ("blocking_gate", "check_run"):
            config[key] = as_bool(value, DEFAULT_CONFIG[key])
        elif key in ("inline_severities", "ignore", "skip_title_markers", "skip_authors"):
            parsed = as_list(value, None)
            if parsed is None:
                warnings.append(f"config {key} must be a list; using default")
            else:
                config[key] = [str(item) for item in parsed]
        elif key == "language":
            config[key] = str(value) if value else DEFAULT_CONFIG[key]
        elif key == "drop_confidence_below":
            if value in CONFIDENCE_RANK:
                config[key] = value
            else:
                warnings.append(
                    f"config drop_confidence_below must be low|medium|high; using "
                    f"{DEFAULT_CONFIG[key]}"
                )
    config["inline_severities"] = [
        item
        for item in config["inline_severities"]
        if item in SEVERITIES
    ] or list(DEFAULT_CONFIG["inline_severities"])
    merged_ignore = []
    for pattern in DEFAULT_IGNORE + config["ignore"]:
        if pattern not in merged_ignore:
            merged_ignore.append(pattern)
    config["ignore"] = merged_ignore
    return config


def is_ignored(path, patterns):
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
        if pattern.endswith("/") and path.startswith(pattern):
            return True
        if fnmatch.fnmatch(path, pattern.rstrip("/") + "/*"):
            return True
    return False


def parse_patch(patch):
    """Return the valid old (LEFT) and new (RIGHT) line numbers of a patch."""
    left, right = set(), set()
    old_line = new_line = 0
    in_hunk = False
    for raw in (patch or "").splitlines():
        match = HUNK_RE.match(raw)
        if match:
            old_line, new_line = int(match.group(1)), int(match.group(2))
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if raw.startswith("\\"):
            continue
        if raw.startswith("+"):
            right.add(new_line)
            new_line += 1
        elif raw.startswith("-"):
            left.add(old_line)
            old_line += 1
        elif raw.startswith(" "):
            left.add(old_line)
            right.add(new_line)
            old_line += 1
            new_line += 1
        elif raw == "":
            continue
        else:
            in_hunk = False
    return left, right


def build_file_index(files, ignore, skipped):
    index = {}
    for entry in files:
        if not isinstance(entry, dict):
            continue
        path = entry.get("filename")
        if not isinstance(path, str) or not path:
            continue
        if is_ignored(path, ignore):
            skipped.append({"path": path, "reason": "ignored-pattern"})
            continue
        left, right = parse_patch(entry.get("patch"))
        index[path] = {
            "left": left,
            "right": right,
            "has_patch": bool(entry.get("patch")),
            "status": entry.get("status", "modified"),
        }
    return index


def fingerprint(path, line, side, rule):
    raw = f"{path}\0{line}\0{side}\0{rule}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]


def normalise_finding(raw, index, ignore, drop_below):
    if not isinstance(raw, dict):
        return None, "finding is not an object"
    severity = str(raw.get("severity", "")).lower()
    if severity not in SEVERITIES:
        return None, f"invalid severity {raw.get('severity')!r}"
    path = raw.get("path")
    if not isinstance(path, str) or not path:
        return None, "finding has no path"
    if is_ignored(path, ignore):
        return None, "ignored-path"
    rule = str(raw.get("rule") or "general")
    confidence = str(raw.get("confidence", "high")).lower()
    if confidence not in CONFIDENCE_RANK:
        confidence = "high"
    if CONFIDENCE_RANK[confidence] < CONFIDENCE_RANK[drop_below]:
        return None, "low-confidence"
    body = raw.get("body")
    if not isinstance(body, str) or not body.strip():
        return None, "finding has no body"
    side = str(raw.get("side", "RIGHT")).upper()
    if side not in ("RIGHT", "LEFT"):
        side = "RIGHT"
    line = raw.get("line")
    if line is not None:
        line = as_int(line, -1)
        if line <= 0:
            return None, "invalid line"
    start_line = raw.get("start_line")
    if start_line is not None:
        start_line = as_int(start_line, -1)
        if start_line <= 0:
            start_line = None
    return {
        "severity": severity,
        "path": path,
        "line": line,
        "side": side,
        "start_line": start_line,
        "rule": rule,
        "confidence": confidence,
        "body": body.strip(),
        "fingerprint": fingerprint(path, line, side, rule),
    }, None


def anchor_status(finding, index):
    info = index.get(finding["path"])
    if not info or not info["has_patch"] or finding["line"] is None:
        return "file" if info else "summary"
    valid = info["right"] if finding["side"] == "RIGHT" else info["left"]
    if finding["line"] not in valid:
        return "file" if info else "summary"
    if finding["start_line"] is not None:
        start_valid = finding["start_line"] in valid
        if not start_valid or finding["start_line"] > finding["line"]:
            return "file"
    return "inline"


def existing_fingerprints(comments, bot_login):
    found = set()
    for comment in comments or []:
        if not isinstance(comment, dict):
            continue
        author = comment.get("user_login")
        if not author and isinstance(comment.get("user"), dict):
            author = comment["user"].get("login")
        if bot_login and author != bot_login:
            continue
        body = comment.get("body") or ""
        found.update(FINGERPRINT_RE.findall(body))
    return found


def comment_body(finding):
    label = finding["severity"].capitalize()
    body = INLINE_FINGERPRINT_RE.sub("", finding["body"])
    return (
        f"**[{label}] {finding['rule']}** — {body}\n\n"
        f"<!-- ai-review-fingerprint:{finding['fingerprint']} -->"
    )


def check_payload(report, config, index):
    conclusion = {
        "clean": "success",
        "findings": "neutral",
        "skipped": "neutral",
        "error": "failure",
    }.get(report["verdict"], "neutral")
    if report["verdict"] == "blocking":
        conclusion = "failure" if config["blocking_gate"] else "neutral"
    level = {"blocking": "failure", "should": "warning", "nit": "notice"}
    annotations = []
    for finding in report["findings"]:
        # Only inline findings have a line validated against the diff. A
        # file/summary finding can carry an arbitrary line, and GitHub rejects
        # the whole check run when an annotation points outside the file.
        if finding["status"] != "inline" or finding["line"] is None:
            continue
        if finding["path"] not in index or len(annotations) >= 50:
            continue
        line = finding["line"]
        start = finding["start_line"] or line
        annotations.append(
            {
                "path": finding["path"],
                "start_line": start,
                "end_line": line,
                "annotation_level": level[finding["severity"]],
                "title": f"[{finding['severity'].capitalize()}] {finding['rule']}",
                "message": finding["body"][:65000],
            }
        )
    return {
        "name": "AI review",
        "head_sha": report["head_sha"],
        "status": "completed",
        "conclusion": conclusion,
        "output": {
            "title": f"AI review: {report['verdict']}",
            "summary": (
                f"Verdict {report['verdict']}: {report['counts']['blocking']} blocking, "
                f"{report['counts']['should']} should, {report['counts']['nit']} nit "
                f"at {report['head_sha']}."
            ),
            "annotations": annotations,
        },
    }


def summary_body(report, policy, config):
    lines = [MARKER, "## Automated review", ""]
    lines.append(f"**Verdict:** {report['verdict']}")
    lines.append(f"**Head:** `{report['head_sha']}`")
    counts = report["counts"]
    lines.append(
        "**Counts:** "
        f"Blocking {counts['blocking']} · Should {counts['should']} · Nit {counts['nit']} · "
        f"Inline {counts['inline']} · File {counts['file']} · Summary {counts['summary']} · "
        f"Deduped {counts['deduped']} · Truncated {counts['truncated']} · "
        f"Discarded {counts['discarded']}"
    )
    if report.get("skip_reason"):
        lines.extend(["", f"**Skipped:** {report['skip_reason']}"])

    fallback = [
        item for item in report["findings"] if item["status"] in ("file", "summary")
    ]
    if fallback:
        lines.extend(["", "### Findings not posted inline"])
        for item in fallback:
            where = f"`{item['path']}`" if item["line"] is None else f"`{item['path']}:{item['line']}`"
            lines.append(f"- **[{item['severity'].capitalize()}] {where}** — {item['body']}")

    if report["skipped"]:
        lines.extend(["", "### Skipped files"])
        for item in report["skipped"]:
            lines.append(f"- `{item['path']}` — {item['reason']}")

    if report["discarded"]:
        lines.extend(["", "### Discarded findings"])
        for item in report["discarded"]:
            where = f"`{item['path']}`" if item["line"] is None else f"`{item['path']}:{item['line']}`"
            lines.append(f"- {where} — {item['reason']}")

    lines.extend(
        [
            "",
            "_Automated review. Human approval is required; this bot never approves or merges._",
        ]
    )
    body = "\n".join(lines)
    limit = config["max_summary_chars"]
    if len(body) > limit:
        body = body[: limit - 80] + "\n\n_…summary truncated; see the report artifact._"
    return body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--report", default="code-review-report.json")
    parser.add_argument("--payload")
    parser.add_argument("--check-payload")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verdict-exit", action="store_true")
    args = parser.parse_args()

    data = read_json(args.input, "input")
    if not isinstance(data, dict):
        fail("input must be a JSON object")

    for key in ("repo", "pr", "head_sha", "base_sha"):
        if key not in data:
            fail(f"input is missing required key {key!r}")
    if not re.match(r"^[^/\s]+/[^/\s]+$", str(data["repo"])):
        fail("repo must be owner/name")
    if not isinstance(data["pr"], int) or data["pr"] <= 0:
        fail("pr must be a positive integer")
    for key in ("head_sha", "base_sha"):
        if not re.match(r"^[0-9a-f]{40}$", str(data[key])):
            fail(f"{key} must be a 40-character lowercase hex SHA")

    warnings = []
    config = normalise_config(data.get("config"), warnings)
    errors = [str(item) for item in as_list(data.get("errors"), [])]
    skipped = []
    files = as_list(data.get("files"), [])
    index = build_file_index(files, config["ignore"], skipped)

    skip_reason = data.get("skipped_run")
    state = str(data.get("state", "open"))
    author = data.get("author")
    if isinstance(author, dict):
        author = author.get("login")
    author = str(author) if author else None
    title = str(data.get("title") or "")
    bot_login = data.get("bot_login")
    if skip_reason is None:
        if state != "open":
            skip_reason = f"state:{state}"
        elif as_bool(data.get("is_draft"), False):
            skip_reason = "draft"
        elif bot_login and author == bot_login:
            skip_reason = "self-review"
        elif author and author in config["skip_authors"]:
            skip_reason = f"author:{author}"
        elif any(marker.lower() in title.lower() for marker in config["skip_title_markers"]):
            skip_reason = "title-marker"
        elif not index:
            skip_reason = "nothing-to-review"

    findings, discarded = [], []
    if not skip_reason and not errors:
        for raw in as_list(data.get("findings"), []):
            finding, reason = normalise_finding(
                raw,
                index,
                config["ignore"],
                config["drop_confidence_below"],
            )
            if reason:
                if reason == "ignored-path":
                    continue
                elif reason == "low-confidence":
                    discarded.append(
                        {
                            "path": str(raw.get("path", "")),
                            "line": raw.get("line") if isinstance(raw.get("line"), int) else None,
                            "reason": reason,
                        }
                    )
                elif reason == "invalid line":
                    discarded.append(
                        {
                            "path": str(raw.get("path", "")),
                            "line": None,
                            "reason": reason,
                        }
                    )
                else:
                    errors.append(reason)
                continue
            findings.append(finding)

        findings.sort(
            key=lambda item: (
                SEVERITY_RANK[item["severity"]],
                item["path"],
                item["line"] or 0,
            )
        )

        unique, seen = [], set()
        for finding in findings:
            if finding["fingerprint"] in seen:
                discarded.append(
                    {
                        "path": finding["path"],
                        "line": finding["line"],
                        "reason": "duplicate",
                    }
                )
                continue
            seen.add(finding["fingerprint"])
            unique.append(finding)
        findings = unique

        known = existing_fingerprints(data.get("existing_comments"), bot_login)
        for finding in findings:
            finding["status"] = "deduped" if finding["fingerprint"] in known else "pending"

        limit = config["max_findings"]
        for position, finding in enumerate(findings):
            if position >= limit and finding["status"] != "deduped":
                finding["status"] = "truncated"

        inline_count = 0
        inline_severities = set(config["inline_severities"])
        for finding in findings:
            if finding["status"] != "pending":
                continue
            if finding["severity"] not in inline_severities:
                finding["status"] = "summary"
                continue
            status = anchor_status(finding, index)
            if status == "inline" and inline_count >= config["max_inline"]:
                status = "summary"
            finding["status"] = status
            if status == "inline":
                inline_count += 1

        for finding in findings:
            if finding["status"] == "pending":
                finding["status"] = "summary"

    counts = {severity: 0 for severity in SEVERITIES}
    for finding in findings:
        counts[finding["severity"]] += 1
    for status in ("inline", "file", "summary", "deduped", "truncated"):
        counts[status] = sum(1 for item in findings if item["status"] == status)
    counts["discarded"] = len(discarded)

    if errors:
        verdict = "error"
    elif skip_reason:
        verdict = "skipped"
    elif counts["blocking"]:
        verdict = "blocking"
    elif counts["should"] or counts["nit"]:
        verdict = "findings"
    else:
        verdict = "clean"

    if verdict in ("error", "skipped"):
        event = None
        exit_code = 2 if verdict == "error" else 0
    else:
        event = (
            "REQUEST_CHANGES"
            if counts["blocking"] and config["blocking_gate"]
            else "COMMENT"
        )
        exit_code = 1 if counts["blocking"] else 0

    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": str(data["repo"]),
        "pr": data["pr"],
        "url": str(data.get("url") or f"https://github.com/{data['repo']}/pull/{data['pr']}"),
        "head_sha": str(data["head_sha"]),
        "base_sha": str(data["base_sha"]),
        "verdict": verdict,
        "skip_reason": skip_reason,
        "event": event,
        "review_id": None,
        "exit_code": exit_code,
        "dry_run": bool(args.dry_run),
        "stale": False,
        "check_run_id": None,
        "check_run_url": None,
        "counts": counts,
        "policy": {
            "blocking_gate": config["blocking_gate"],
            "inline_severities": config["inline_severities"],
            "language": config["language"],
        },
        "skipped": skipped,
        "findings": [
            {
                "fingerprint": finding["fingerprint"],
                "severity": finding["severity"],
                "path": finding["path"],
                "line": finding["line"],
                "side": finding["side"],
                "start_line": finding["start_line"],
                "rule": finding["rule"],
                "confidence": finding["confidence"],
                "status": finding["status"],
                "body": finding["body"],
            }
            for finding in findings
        ],
        "discarded": discarded,
        "config_warnings": warnings,
        "errors": errors,
    }

    body = summary_body(report, report["policy"], config) if verdict not in ("error", "skipped") else None

    with open(args.report, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    payload = None
    if verdict not in ("error", "skipped"):
        comments = []
        for finding in findings:
            if finding["status"] == "inline":
                comment = {
                    "path": finding["path"],
                    "line": finding["line"],
                    "side": finding["side"],
                    "body": comment_body(finding),
                }
                if finding["start_line"] is not None:
                    comment["start_line"] = finding["start_line"]
                    comment["start_side"] = finding["side"]
                comments.append(comment)
            elif finding["status"] == "file":
                comments.append(
                    {
                        "path": finding["path"],
                        "subject_type": "file",
                        "body": comment_body(finding),
                    }
                )
        payload = {
            "commit_id": report["head_sha"],
            "body": body,
            "event": event,
            "comments": comments,
        }

    if args.payload and payload is not None:
        with open(args.payload, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    if args.check_payload:
        with open(args.check_payload, "w", encoding="utf-8") as handle:
            json.dump(check_payload(report, config, index), handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    print(
        f"OK verdict={verdict} findings={len(findings)} "
        f"inline={counts['inline']} file={counts['file']} "
        f"summary={counts['summary']} report={args.report}"
    )
    if args.verdict_exit:
        sys.exit(exit_code)
    return 0


if __name__ == "__main__":
    main()
