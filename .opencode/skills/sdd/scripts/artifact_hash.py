#!/usr/bin/env python3
"""Read-only SDD artifact SHA-256 CLI, recipe sdd-artifact-v1.

Only files named tasks.md normalize task checkbox state after 0-3 spaces.
All other bytes, including line endings and fenced examples, are preserved.
"""

import argparse
import hashlib
from pathlib import Path
import re
import sys


RECIPE_VERSION = "sdd-artifact-v1"
TASK = re.compile(rb"^( {0,3}(?:[-+*]|[0-9]+[.)])[ \t]+\[)[ xX](\](?=[ \t]|$))")
FENCE = re.compile(rb"^[ \t]*(`{3,}|~{3,})(.*)$")


def normalize_tasks(data: bytes) -> bytes:
    """Normalize shallow task markers, preserving indented/fenced examples."""
    result = []
    fence_char = None
    fence_length = 0
    # Recognize line endings without splitting substantive control bytes.
    for match in re.finditer(rb"([^\r\n]*)(\r\n|\r|\n|$)", data):
        body, ending = match.groups()
        fence = FENCE.match(body)
        if fence_char is not None:
            if (fence and fence[1][:1] == fence_char
                    and len(fence[1]) >= fence_length
                    and not fence[2].strip(b" \t")):
                fence_char = None
        elif fence and not (fence[1].startswith(b"`") and b"`" in fence[2]):
            fence_char = fence[1][:1]
            fence_length = len(fence[1])
        else:
            body = TASK.sub(rb"\1 \2", body, count=1)
        result.append(body + ending)
    return b"".join(result)


def artifact_digest(path: Path) -> str:
    data = path.read_bytes()
    if path.name == "tasks.md":
        data = normalize_tasks(data)
    return hashlib.sha256(data).hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=RECIPE_VERSION)
    parser.add_argument("paths", nargs="+", type=Path, help="artifact paths; tasks.md is normalized")
    args = parser.parse_args(argv)
    failed = False
    for path in args.paths:
        try:
            digest = artifact_digest(path)
        except OSError as exc:
            print(f"artifact_hash: {path}: {exc}", file=sys.stderr)
            failed = True
            continue
        # Use sha256sum's escaped filename convention for unambiguous output.
        name = str(path)
        escaped = any(char in name for char in "\\\n\r")
        name = name.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
        prefix = "\\" if escaped else ""
        print(f"{prefix}{digest}  {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
