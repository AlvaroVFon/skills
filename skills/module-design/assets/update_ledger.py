#!/usr/bin/env python3
"""Merge a scan report into the finding ledger and reconcile statuses.

Usage:
    update_ledger.py --ledger <ledger.json> --report <report.json> [--repo-root <dir>]
    update_ledger.py --ledger <ledger.json> --resolve <id> --status <s>
                     [--commit <sha>] --note <text>

Merge mode folds every report finding into the ledger (adding new entries,
reopening regressions, closing fixed ones) and marks unreviewed open entries
`stale` when their file changed since the entry commit. The computed delta is
written back into the report JSON unless --no-write-report is given.

Resolve mode applies an out-of-scan fix or acceptance to one entry.

Exit codes:
    0  ledger updated
    1  one or more `ERROR:` lines reported (nothing written)

Checks:
    E01 cannot read/write a file
    E02 report is not valid JSON or lacks required keys
    E03 finding lacks title/severity/discriminator/status/location
    E04 unknown --status or --resolve id not found
    E05 ledger skill/version does not match this skill
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

SPEC = {
    "skill": "module-design",
    "kind": "design",
    "discriminator": "type",
    "open": "open",
    "fixed": "resolved",
    "regressed": "regressed",
    "stale": "stale",
    "wontfix": "wontfix",
    "report_new": "new",
    "report_persists": "persists",
    "report_fixed": "resolved",
    "report_regressed": "regressed",
    "closed": ["resolved", "wontfix"],
    "terminal": [],
    "resolve": ["resolved", "wontfix"],
    "copy_fields": ["title", "severity", "type", "module", "location", "detail"],
    "delta_closed_label": "resolved",
    "delta_fixed": "resolved",
    "delta_fixed_items": "resolved_items",
    "location_required": False,
}

CORE_FIELDS = (
    "title",
    "severity",
    "verdict",
    "scenario",
    "gap",
    "category",
    "operator",
    "type",
    "module",
    "location",
    "mutant_diff",
    "tests",
)
SEVERITY_RANK = {"Critical": 0, "Major": 1, "Minor": 2}


def die(msg):
    print(f"ERROR: {msg}")
    sys.exit(1)


def load_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError as e:
        die(f"E01 cannot read {path}: {e}")
    except json.JSONDecodeError as e:
        die(f"E02 invalid JSON in {path}: {e}")


def write_json(path, obj):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    except OSError as e:
        die(f"E01 cannot write {path}: {e}")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-") or "item"


def make_id(spec, finding):
    disc = slug(finding.get(spec["discriminator"], ""))
    file = (finding.get("location") or {}).get("file", "")
    raw = "|".join([spec["kind"], disc, file, slug(finding["title"])])
    return f"{disc}-{hashlib.sha1(raw.encode()).hexdigest()[:12]}"


def title_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", str(text).lower()) if len(w) > 2}


def fuzzy_match(entries, taken, finding):
    disc = slug(finding.get(SPEC["discriminator"], ""))
    file = (finding.get("location") or {}).get("file", "")
    target = title_words(finding["title"])
    best, best_score = None, 0.0
    for entry in entries:
        if entry["id"] in taken or entry.get("kind") != SPEC["kind"]:
            continue
        if slug(entry.get(SPEC["discriminator"], "")) != disc:
            continue
        if (entry.get("location") or {}).get("file", "") != file:
            continue
        other = title_words(entry["title"])
        union = target | other
        score = len(target & other) / len(union) if union else 0.0
        if score > best_score:
            best, best_score = entry, score
    return best if best_score >= 0.6 else None


def git_changed(repo, commit, head, path):
    if not commit or commit in ("none", "null") or not repo:
        return None
    try:
        out = subprocess.run(
            ["git", "-C", repo, "diff", "--name-only", f"{commit}..{head}", "--", path],
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return bool(out.stdout.strip())


def repo_root_hint(repo_root):
    try:
        out = subprocess.run(
            ["git", "-C", repo_root, "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return repo_root if os.path.isdir(repo_root) else None


def repo_name(repo):
    if not repo:
        return "unknown"
    remote = subprocess.run(
        ["git", "-C", repo, "remote", "get-url", "origin"], capture_output=True, text=True
    )
    if remote.returncode == 0 and remote.stdout.strip():
        name = remote.stdout.strip().removesuffix(".git")
        return re.sub(r"^.*[:/]([^/]+/[^/]+)$", r"\1", name)
    return os.path.basename(repo)


def new_entry(entry_id, finding, report):
    entry = {"id": entry_id, "kind": SPEC["kind"]}
    for key in CORE_FIELDS:
        if finding.get(key) is not None:
            entry[key] = finding[key]
    entry.update(
        {
            "status": SPEC["open"],
            "first_seen": report["date"],
            "last_seen": report["date"],
            "fixed_at": None,
            "fixed_commit": None,
            "commit": report["commit"],
            "evidence": finding.get("evidence"),
            "notes": [],
        }
    )
    return entry


def update_fields(entry, finding, report, status):
    entry["status"] = status
    for key in SPEC["copy_fields"]:
        if finding.get(key) is not None:
            entry[key] = finding[key]
    entry["last_seen"] = report["date"]
    entry["commit"] = report["commit"]
    if finding.get("evidence"):
        entry["evidence"] = finding["evidence"]
    if status == SPEC["fixed"]:
        entry["fixed_at"] = report["date"]
        entry["fixed_commit"] = report["commit"]
    return entry


def merge(ledger, report, repo):
    entries = ledger.setdefault("entries", [])
    by_id = {e["id"]: e for e in entries}
    taken = set()
    delta = {
        "persists": 0,
        SPEC["delta_fixed"]: 0,
        "new": 0,
        "regressed": 0,
        "not_rechecked": 0,
        SPEC["delta_fixed_items"]: [],
        "not_rechecked_items": [],
    }

    for finding in report.get("findings", []):
        required = ["title", "severity", "status"]
        if SPEC.get("location_required"):
            required.append("location")
        for key in required:
            if not finding.get(key):
                die(f"E03 finding missing '{key}': {finding.get('title', '?')}")
        if not finding.get(SPEC["discriminator"]):
            die(f"E03 finding missing '{SPEC['discriminator']}': {finding['title']}")

        entry_id = finding.get("id") or make_id(SPEC, finding)
        entry = by_id.get(entry_id)
        if entry is None:
            entry = fuzzy_match(entries, taken, finding)
            if entry is not None:
                entry_id = entry["id"]
        report_status = finding["status"]
        if report_status not in (
            SPEC["report_new"],
            SPEC["report_persists"],
            SPEC["report_fixed"],
            SPEC["report_regressed"],
        ):
            die(f"E03 unknown finding status {report_status!r}")

        if entry is None:
            entry = new_entry(entry_id, finding, report)
            entries.append(entry)
            by_id[entry_id] = entry

        if report_status == SPEC["report_fixed"]:
            update_fields(entry, finding, report, SPEC["fixed"])
            delta[SPEC["delta_fixed"]] += 1
            loc = finding.get("location") or {}
            delta[SPEC["delta_fixed_items"]].append(
                {
                    "id": entry["id"],
                    "location": f"{loc.get('file', '')}:{loc.get('line', 0)}",
                    "title": finding["title"],
                }
            )
        elif report_status == SPEC["report_regressed"] or (
            report_status == SPEC["report_persists"]
            and entry.get("status") in SPEC["closed"]
        ):
            update_fields(entry, finding, report, SPEC["regressed"])
            delta["regressed"] += 1
        elif report_status == SPEC["report_persists"]:
            update_fields(entry, finding, report, SPEC["open"])
            delta["persists"] += 1
        else:
            was_closed = (
                entry.get("status") in SPEC["closed"]
                and entry.get("last_seen") != report["date"]
            )
            update_fields(entry, finding, report, SPEC["regressed"] if was_closed else SPEC["open"])
            delta["regressed" if was_closed else "new"] += 1

        finding["id"] = entry["id"]
        taken.add(entry["id"])

    head = report.get("commit") or "HEAD"
    for entry in entries:
        if entry["id"] in taken or entry.get("status") not in (SPEC["open"], SPEC["stale"]):
            continue
        path = entry.get("location", {}).get("file")
        changed = git_changed(repo, entry.get("commit"), head, path) if path else None
        if changed:
            entry["status"] = SPEC["stale"]
            reason = f"file changed since {entry.get('commit')}"
        else:
            reason = "out of scan scope"
        delta["not_rechecked"] += 1
        delta["not_rechecked_items"].append(
            {
                "id": entry["id"],
                "location": f"{path}:{entry.get('location', {}).get('line', 0)}",
                "reason": reason,
            }
        )

    entries.sort(
        key=lambda e: (
            0 if e.get("status") in (SPEC["open"], SPEC["regressed"], SPEC["stale"]) else 1,
            SEVERITY_RANK.get(e.get("severity"), 9),
            e["id"],
        )
    )
    ledger["updated"] = report["date"]
    ledger["repo"] = repo_name(repo)
    report["delta"] = delta
    return ledger, report


def resolve(ledger, args):
    target = next((e for e in ledger.get("entries", []) if e["id"] == args.resolve), None)
    if target is None:
        die(f"E04 no ledger entry with id {args.resolve!r}")
    if args.status not in SPEC["resolve"]:
        die(f"E04 --status must be one of {SPEC['resolve']}")
    target["status"] = args.status
    if args.status == SPEC["fixed"]:
        target["fixed_at"] = args.date or target.get("fixed_at")
        target["fixed_commit"] = args.commit or target.get("fixed_commit")
    if args.note:
        target.setdefault("notes", []).append(f"{args.date or ''} {args.note}".strip())
    return ledger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--report")
    parser.add_argument("--resolve")
    parser.add_argument("--status")
    parser.add_argument("--commit")
    parser.add_argument("--note")
    parser.add_argument("--date")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--no-write-report", action="store_true")
    args = parser.parse_args()

    if not os.path.exists(args.ledger):
        ledger = {
            "version": 1,
            "skill": SPEC["skill"],
            "repo": repo_name(repo_root_hint(args.repo_root)),
            "updated": args.date or "",
            "entries": [],
        }
    else:
        ledger = load_json(args.ledger)
        if ledger.get("skill") != SPEC["skill"] or ledger.get("version") != 1:
            die(f"E05 ledger is not a {SPEC['skill']} v1 ledger")

    if args.resolve:
        if not args.status:
            die("E04 --resolve requires --status")
        ledger = resolve(ledger, args)
        write_json(args.ledger, ledger)
        print(f"OK resolved {args.resolve} -> {args.status}")
        return

    if not args.report:
        die("E02 --report is required unless --resolve is used")
    report = load_json(args.report)
    for key in ("schema", "date", "commit"):
        if not report.get(key):
            die(f"E02 report missing '{key}'")
    if not isinstance(report.get("findings"), list):
        die("E02 report missing 'findings' list")
    repo = repo_root_hint(args.repo_root)
    ledger, report = merge(ledger, report, repo)
    write_json(args.ledger, ledger)
    if not args.no_write_report:
        write_json(args.report, report)
    delta = report["delta"]
    print(
        f"OK ledger updated: {delta['new']} new, {delta['persists']} persists, "
        f"{delta[SPEC['delta_fixed']]} {SPEC['delta_closed_label']}, {delta['regressed']} regressed, "
        f"{delta['not_rechecked']} not re-checked"
    )


if __name__ == "__main__":
    main()
