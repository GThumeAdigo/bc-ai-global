#!/usr/bin/env python3
"""Snapshot approved intent and detect stale evidence. Does not authenticate users."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from datetime import datetime, timezone


def sha(data):
    return hashlib.sha256(data).hexdigest()


def record(target, artifacts, owner, approval_text):
    if not owner.strip() or not approval_text.strip():
        raise ValueError("owner and actual approval text are required")
    if target.exists():
        raise ValueError("approval record already exists; preserve it and use a new record")
    items = []
    for artifact in artifacts:
        data = artifact.read_bytes()
        items.append({"path": str(artifact.resolve()), "sha256": sha(data), "content": data.hex()})
    if not items:
        raise ValueError("no approved artifacts")
    result = {"version": 2, "owner": owner, "approval_text": approval_text,
              "date": datetime.now(timezone.utc).isoformat(), "artifacts": items}
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x") as output:
        json.dump(result, output, indent=2)
    return result


def check(target, artifacts):
    evidence = json.loads(target.read_text())
    if evidence.get("version") != 2 or not evidence.get("owner") or not evidence.get("approval_text"):
        raise ValueError("missing approval provenance")
    requested = {str(p.resolve()) for p in artifacts}
    recorded = {item["path"] for item in evidence["artifacts"]}
    if not requested or requested != recorded or len(recorded) != len(evidence["artifacts"]):
        raise ValueError("approved artifact set differs from requested scope")
    for item in evidence["artifacts"]:
        if sha(bytes.fromhex(item["content"])) != item["sha256"]:
            raise ValueError("approval snapshot integrity mismatch")
        if sha(Path(item["path"]).read_bytes()) != item["sha256"]:
            raise ValueError(f"stale approval: {item['path']}")
    return {"status": "pass", "artifacts": sorted(recorded), "owner": evidence["owner"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["record", "check"])
    parser.add_argument("record", type=Path)
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--owner", default="")
    parser.add_argument("--approval-text", default="")
    args = parser.parse_args()
    if args.action == "record":
        record(args.record, args.artifacts, args.owner, args.approval_text)
        print(json.dumps({"status": "recorded", "record": str(args.record)}))
    else:
        print(json.dumps(check(args.record, args.artifacts)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"status": "blocked", "reason": str(error)}))
        sys.exit(1)
