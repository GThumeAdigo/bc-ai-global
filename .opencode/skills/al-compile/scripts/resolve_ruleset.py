#!/usr/bin/env python3
"""Resolve a required ruleset without third-party JSONC dependencies."""

import json
from pathlib import Path
import re
import sys


def read_jsonc(path):
    # Match strings first so comment markers and commas inside strings survive.
    tokens = r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/'
    text = re.sub(tokens, lambda m: m[0] if m[0].startswith('"') else ' ',
                  path.read_text(encoding="utf-8-sig"))
    text = re.sub(r'"(?:\\.|[^"\\])*"|,(?=\s*[}\]])',
                  lambda m: '' if m[0] == ',' else m[0], text)
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError(f"expected an object in {path}")
    return value


def expand_path(value, base, folder, names=None):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("ruleset/folder path must be a nonempty string")

    def variable(match):
        key = match[1]
        if key == "workspaceFolder" and folder is not None:
            return str(folder)
        if key.startswith("workspaceFolder:"):
            matches = (names or {}).get(key.split(":", 1)[1], [])
            if len(matches) == 1:
                return str(matches[0])
        raise ValueError(f"unsupported or ambiguous variable {match[0]}")

    value = re.sub(r'\$\{([^}]+)\}', variable, value)
    if "${" in value:
        raise ValueError(f"unsupported variable in {value}")
    path = Path(value)
    return (base / path).resolve()


def workspace_for(app):
    candidates = []
    for directory in (app, *app.parents):
        for path in sorted(directory.glob("*.code-workspace")):
            data = read_jsonc(path)
            if not isinstance(data.get("folders", []), list) or not isinstance(data.get("settings", {}), dict):
                raise ValueError(f"invalid workspace folders/settings in {path}")
            names = {}
            matches = []
            for entry in data.get("folders", []):
                if not isinstance(entry, dict):
                    raise ValueError(f"invalid workspace folder in {path}")
                if "path" not in entry:
                    continue
                folder = expand_path(entry["path"], path.parent, None)
                names.setdefault(entry.get("name", folder.name), []).append(folder)
                if app == folder or folder in app.parents:
                    matches.append(folder)
            if matches:
                # A nested app uses the most specific containing workspace folder.
                folder = max(matches, key=lambda p: len(p.parts))
                candidates.append((path, data, folder, names))
    if len(candidates) > 1:
        raise ValueError("ambiguous workspaces for app; pass an explicit ruleset: " +
                         ", ".join(str(item[0]) for item in candidates))
    return candidates[0] if candidates else None


def resolve(app, override=None):
    if not app.is_dir() or not (app / "app.json").is_file():
        raise ValueError(f"invalid app folder (requires app.json): {app}")
    # Validate before compiler discovery, including malformed manifests.
    read_jsonc(app / "app.json")
    if override is not None:
        workspace = workspace_for(app) if "${workspaceFolder" in override else None
        path = expand_path(override, Path.cwd(), workspace[2] if workspace else app,
                           workspace[3] if workspace else None)
    else:
        settings = app / ".vscode/settings.json"
        local = read_jsonc(settings) if settings.is_file() else {}
        if "al.ruleSetPath" in local:
            value = local["al.ruleSetPath"]
            workspace = workspace_for(app) if isinstance(value, str) and "${workspaceFolder" in value else None
            path = expand_path(value, app, workspace[2] if workspace else app,
                               workspace[3] if workspace else None)
        else:
            workspace = workspace_for(app)
            inherited = {}
            folder, names = app, {}
            if workspace:
                _, data, folder, names = workspace
                inherited = dict(data.get("settings", {}))
                settings = folder / ".vscode/settings.json"
                if settings.is_file():
                    inherited.update(read_jsonc(settings))
            else:
                # Without a workspace file, a containing folder may be the open
                # single-folder workspace. Do not guess between multiple roots.
                candidates = []
                for parent in app.parents:
                    settings = parent / ".vscode/settings.json"
                    if settings.is_file():
                        values = read_jsonc(settings)
                        if "al.ruleSetPath" in values:
                            candidates.append((parent, values))
                if len(candidates) > 1:
                    raise ValueError("ambiguous containing folder settings; pass an explicit ruleset: " +
                                     ", ".join(str(item[0]) for item in candidates))
                if candidates:
                    folder, inherited = candidates[0]
                    names = {folder.name: [folder]}
            if "al.ruleSetPath" in inherited:
                # AL resolves this setting relative to the project root even
                # when its value is inherited from folder/workspace settings.
                path = expand_path(inherited["al.ruleSetPath"], app, folder, names)
            else:
                path = (app.parent / ".codeAnalysis/ADIGO.ruleset.json").resolve()
    if not path.is_file():
        raise ValueError(f"ruleset missing (required for CI parity): {path}")
    return path


if __name__ == "__main__":
    try:
        if len(sys.argv) not in (2, 3):
            raise ValueError("usage: resolve_ruleset.py APP [RULESET]")
        print(resolve(Path(sys.argv[1]).resolve(), sys.argv[2] if len(sys.argv) == 3 else None))
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"error: {error}", file=sys.stderr)
        sys.exit(2)
