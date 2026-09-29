#!/usr/bin/env python3
"""Write build inputs and diagnostics without claiming semantic correctness."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diagnostics(text, app):
    result = []
    for line in text.splitlines():
        match = re.search(r"^(.*?)\((\d+),(\d+)\):\s*(error|warning|info)\s+(\w+):\s*(.*)$", line)
        if match:
            path, row, column, severity, rule, message = match.groups()
            path = path.removeprefix(str(app) + os.sep)
            result.append({"file": path, "line": int(row), "column": int(column), "severity": severity, "rule": rule, "message": message})
        elif re.search(r"\b(error|warning|info)\s+[A-Z]+\d+:", line):
            result.append({"raw": line.replace(str(app), "<app>")})
    return result


def identity(item):
    # Line shifts do not make the same diagnostic new; messages/paths do.
    return json.dumps({k: v for k, v in item.items() if k not in {"line", "column"}}, sort_keys=True)


def new_diagnostics(current, baseline):
    from collections import Counter
    existing = Counter(identity(item) for item in baseline)
    new = []
    for item in current:
        key = identity(item)
        if existing[key]:
            existing[key] -= 1
        else:
            new.append(item)
    return new


def main():
    app, out, compiler, ruleset, exit_code, *analyzers = sys.argv[1:]
    app, out = Path(app), Path(out)
    files = {}
    for directory, dirs, names in os.walk(app):
        dirs[:] = [d for d in dirs if d not in {".git", ".alpackages", ".agent-state", ".opencode", "node_modules"}]
        for name in names:
            path = Path(directory) / name
            if path.suffix == ".al" or path == app / "app.json":
                files[path.relative_to(app).as_posix()] = file_hash(path)
    try:
        revision = subprocess.check_output(["git", "-C", str(app), "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
    except subprocess.CalledProcessError:
        revision = None
    packages = {p.name: file_hash(p) for p in sorted((app / ".alpackages").glob("*.app"))}
    log = (out / "compile.log").read_text(errors="replace")
    current = diagnostics(log, app)
    evidence = {
        "version": 1, "app": str(app), "revision": revision, "source_files": files,
        "source_sha256": hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest(),
        "compiler": {"path": compiler, "sha256": file_hash(Path(compiler))},
        "analyzers": {Path(p).name: file_hash(Path(p)) for p in analyzers},
        "ruleset": {"path": ruleset, "sha256": file_hash(Path(ruleset))},
        "packages": packages, "compiler_exit": int(exit_code), "diagnostics": current,
        "log": str(out / "compile.log"), "verification_status": "not-requested",
    }
    evidence["command"] = (["dotnet", compiler] if compiler.endswith(".dll") else [compiler]) + [f"/project:{app}", f"/packagecachepath:{app / '.alpackages'}", *[f"/analyzer:{p}" for p in analyzers], f"/ruleset:{ruleset}", f"/out:{out / (app.name + '.app')}"]
    baseline_path = os.environ.get("AL_BASELINE_EVIDENCE")
    if baseline_path:
        baseline = json.loads(Path(baseline_path).read_text())
        parity = (baseline["compiler"]["sha256"] == evidence["compiler"]["sha256"] and baseline["analyzers"] == evidence["analyzers"] and baseline["ruleset"]["sha256"] == evidence["ruleset"]["sha256"] and baseline["packages"] == packages)
        evidence["baseline"] = baseline_path
        evidence["baseline_comparable"] = parity
        if parity:
            evidence["new_diagnostics"] = new_diagnostics(current, baseline["diagnostics"])
    if os.environ.get("AL_VERIFY_NEW_DIAGNOSTICS") == "1":
        if int(exit_code):
            evidence["verification_status"] = "failed"
        elif baseline_path and not evidence.get("baseline_comparable"):
            evidence["verification_status"] = "incomparable"
        else:
            evidence["verification_status"] = "failed" if evidence.get("new_diagnostics", current) else "pass"
    (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"evidence: {out / 'evidence.json'}")
    return 3 if evidence["verification_status"] in {"failed", "incomparable"} else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as error:
        print(f"evidence error: {error}", file=sys.stderr)
        sys.exit(2)
