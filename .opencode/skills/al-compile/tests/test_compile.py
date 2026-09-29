"""Fixture builds exercise the real wrapper without BC or installed analyzers."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/compile.sh"
ANALYZERS = [
    "Microsoft.Dynamics.Nav.CodeCop.dll", "Microsoft.Dynamics.Nav.UICop.dll",
    "Microsoft.Dynamics.Nav.PerTenantExtensionCop.dll",
    *[f"ALCops.{name}.dll" for name in (
        "ApplicationCop", "DocumentationCop", "FormattingCop", "LinterCop",
        "PlatformCop", "TestAutomationCop", "Common")],
]


class CompileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="compile-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.app = self.root / "repo/apps/My App"
        self.write(self.app / "app.json", "{}")
        self.home = self.root / "home"
        self.bin = self.home / ".vscode/extensions/ms-dynamics-smb.al-1.0/bin"
        compiler = self.bin / "linux/alc"
        self.write(compiler, '#!/usr/bin/env bash\nprintf "%s\\n" "$@" > "$CAPTURE"\n'
                   'printf "%s\\n" "${FAKE_DIAGNOSTICS:-}"\nexit "${FAKE_EXIT:-0}"\n')
        compiler.chmod(0o755)
        for name in ANALYZERS:
            self.write(self.bin / "Analyzers" / name, "")
        self.capture = self.root / "args"
        self.env = {**os.environ, "HOME": str(self.home), "CAPTURE": str(self.capture)}

    def write(self, path, text="{}"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def local(self, value):
        self.write(self.app / ".vscode/settings.json", json.dumps({"al.ruleSetPath": value}))

    def workspace(self, name="main", folders=None, value="workspace.ruleset.json"):
        return self.write(self.root / "repo" / f"{name}.code-workspace", json.dumps({
            "folders": folders if folders is not None else [{"name": "Repo", "path": "."}],
            "settings": {"al.ruleSetPath": value},
        }))

    def run_compile(self, *args, success=True, app=None):
        result = subprocess.run(["bash", str(SCRIPT), str(app or self.app), *args],
                                cwd=self.root, env=self.env, capture_output=True, text=True)
        # The production wrapper intentionally puts logs outside the fixture tree.
        for line in result.stdout.splitlines():
            if line.startswith("log:    /tmp/alcompile."):
                shutil.rmtree(Path(line.removeprefix("log:    ")).parent)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def assert_ruleset(self, path):
        args = self.capture.read_text().splitlines()
        self.assertIn(f"/ruleset:{path.resolve()}", args)
        self.assertEqual(sum(arg.startswith("/analyzer:") for arg in args), 10)
        self.assertIn(f"/project:{self.app}", args)

    def test_local_jsonc_beats_workspace_and_convention(self):
        expected = self.write(self.root / "repo/rules // folder/local.ruleset.json")
        self.write(self.app / ".vscode/settings.json", '''{
          // comment
          "al.ruleSetPath": "${workspaceFolder}/rules // folder/local.ruleset.json",
          "ignored": ["literal ,} /* text */",], /* block */
        }''')
        self.write(self.app.parent / ".codeAnalysis/ADIGO.ruleset.json")
        self.workspace(value="missing.ruleset")
        self.run_compile()
        self.assert_ruleset(expected)

    def test_explicit_beats_local_and_is_relative_to_cwd(self):
        expected = self.write(self.root / "override.ruleset")
        self.local("missing")
        self.run_compile("override.ruleset")
        self.assert_ruleset(expected)

    def test_workspace_ruleset_is_app_relative_not_workspace_file_relative(self):
        expected = self.write(self.app / "workspace.ruleset.json")
        self.write(self.root / "repo/workspace.ruleset.json")  # Wrong-root decoy.
        self.write(self.app.parent / ".codeAnalysis/ADIGO.ruleset.json")
        self.workspace()
        self.workspace("unrelated", [{"path": "Other"}], "missing")
        self.run_compile()
        self.assert_ruleset(expected)

    def test_inherited_parent_relative_ruleset(self):
        expected = self.write(self.app.parent / ".codeAnalysis/custom.ruleset.json")
        self.write(self.root / ".codeAnalysis/custom.ruleset.json")
        self.workspace(value="../.codeAnalysis/custom.ruleset.json")
        self.run_compile()
        self.assert_ruleset(expected)

    def test_nested_app_inherits_selected_folder_settings_before_workspace(self):
        expected = self.write(self.app.parent / ".codeAnalysis/folder.ruleset.json")
        self.workspace(value="missing-workspace.ruleset")
        self.write(self.root / "repo/.vscode/settings.json", '''{
          "al.ruleSetPath": "../.codeAnalysis/folder.ruleset.json", // inherited
        }''')
        self.write(self.app / ".vscode/settings.json", '{"other.setting": true}')
        self.run_compile()
        self.assert_ruleset(expected)
        local = self.write(self.app / "local.ruleset")
        self.local("local.ruleset")
        self.run_compile()
        self.assert_ruleset(local)

    def test_inherited_folder_variable_is_selected_folder_not_app(self):
        expected = self.write(self.root / "repo/folder.ruleset")
        self.workspace()
        self.write(self.root / "repo/.vscode/settings.json",
                   '{"al.ruleSetPath": "${workspaceFolder}/folder.ruleset"}')
        self.run_compile()
        self.assert_ruleset(expected)

    def test_workspace_variable_is_selected_folder_not_app_or_workspace_file(self):
        expected = self.write(self.app.parent / "folder.ruleset")
        self.workspace(folders=[{"path": "apps"}], value="${workspaceFolder}/folder.ruleset")
        self.write(self.root / "repo/folder.ruleset")
        self.write(self.app / "folder.ruleset")
        self.run_compile()
        self.assert_ruleset(expected)

    def test_single_folder_workspace_settings_without_workspace_file(self):
        expected = self.write(self.app.parent / ".codeAnalysis/folder.ruleset")
        self.write(self.root / "repo/.vscode/settings.json",
                   '{"al.ruleSetPath": "../.codeAnalysis/folder.ruleset"}')
        self.run_compile()
        self.assert_ruleset(expected)

    def test_multiple_containing_folder_settings_fail_explicitly(self):
        for parent in (self.root / "repo", self.app.parent):
            self.write(parent / ".vscode/settings.json", '{"al.ruleSetPath": "folder.ruleset"}')
        self.assertIn("ambiguous containing folder settings", self.run_compile(success=False).stderr)
        self.assertFalse(self.capture.exists())

    def test_missing_inherited_folder_ruleset_does_not_fall_back(self):
        self.workspace(value="valid.ruleset")
        self.write(self.app / "valid.ruleset")
        self.write(self.app.parent / ".codeAnalysis/ADIGO.ruleset.json")
        self.write(self.root / "repo/.vscode/settings.json", '{"al.ruleSetPath": "missing.ruleset"}')
        self.assertIn("ruleset missing", self.run_compile(success=False).stderr)
        self.assertFalse(self.capture.exists())

    def test_local_relative_path_uses_app_not_settings_directory(self):
        expected = self.write(self.app / "local.ruleset")
        self.local("local.ruleset")
        self.run_compile()
        self.assert_ruleset(expected)

    def test_override_workspace_variables(self):
        expected = self.write(self.app / "local.ruleset")
        self.workspace(folders=[{"name": "Application", "path": "apps/My App"}])
        for value in ("${workspaceFolder}/local.ruleset", "${workspaceFolder:Application}/local.ruleset"):
            self.run_compile(value)
            self.assert_ruleset(expected)

    def test_workspace_variables_and_jsonc(self):
        expected = self.write(self.app / "ruleset.json")
        for value in ("${workspaceFolder}/ruleset.json", "${workspaceFolder:Application}/ruleset.json"):
            self.write(self.root / "repo/main.code-workspace", '''{
              "folders": [{"path": "."}, {"name": "Application", "path": "apps/My App",},],
              "settings": {"al.ruleSetPath": ''' + json.dumps(value) + ''',}, // comment
            }''')
            self.run_compile()
            self.assert_ruleset(expected)

    def test_local_named_workspace_variable(self):
        expected = self.write(self.root / "repo/shared.ruleset")
        self.workspace()
        self.local("${workspaceFolder:Repo}/shared.ruleset")
        self.run_compile()
        self.assert_ruleset(expected)

    def test_convention_fallback(self):
        expected = self.write(self.app.parent / ".codeAnalysis/ADIGO.ruleset.json")
        self.run_compile()
        self.assert_ruleset(expected)

    def test_multiple_applicable_workspaces_fail_but_override_disambiguates(self):
        self.workspace("one")
        self.workspace("two")
        expected = self.write(self.root / "override.ruleset")
        result = self.run_compile(success=False)
        self.assertIn("ambiguous workspaces", result.stderr)
        self.assertFalse(self.capture.exists())
        self.run_compile(str(expected))
        self.assert_ruleset(expected)

    def test_missing_paths_never_fall_back(self):
        self.write(self.app.parent / ".codeAnalysis/ADIGO.ruleset.json")
        for args in (("missing",), ("",)):
            self.run_compile(*args, success=False)
        self.local("missing")
        self.run_compile(success=False)
        (self.app / ".vscode/settings.json").unlink()
        self.workspace(value="missing")
        self.run_compile(success=False)
        self.assertFalse(self.capture.exists())

    def test_missing_fallback_fails(self):
        self.assertIn("ruleset missing", self.run_compile(success=False).stderr)

    def test_unsupported_or_ambiguous_variables_fail(self):
        for value in ("${env:HOME}/ruleset", "${workspaceFolder:Unknown}/ruleset"):
            self.local(value)
            self.assertIn("unsupported or ambiguous", self.run_compile(success=False).stderr)
        self.workspace(folders=[{"name": "same", "path": "."}, {"name": "same", "path": "apps"}])
        self.local("${workspaceFolder:same}/ruleset")
        self.assertIn("unsupported or ambiguous", self.run_compile(success=False).stderr)

    def test_invalid_app_fails_before_compiler_discovery(self):
        shutil.rmtree(self.home)
        for app in (self.root / "missing", self.root / "repo", self.app / "app.json"):
            result = self.run_compile(app=app, success=False)
            self.assertIn("invalid app folder", result.stderr)
            self.assertNotIn("compiler", result.stderr)
        self.write(self.app / "app.json", "not json")
        self.assertNotIn("compiler", self.run_compile(success=False).stderr)

    def test_full_analyzer_set_still_required(self):
        self.write(self.app.parent / ".codeAnalysis/ADIGO.ruleset.json")
        (self.bin / "Analyzers/ALCops.LinterCop.dll").unlink()
        self.assertIn("analyzer missing", self.run_compile(success=False).stderr)

    def test_actual_summary_and_compiler_failure(self):
        self.write(self.app.parent / ".codeAnalysis/ADIGO.ruleset.json")
        self.env.update(FAKE_EXIT="1", FAKE_DIAGNOSTICS="x: error AL0001\nx: warning AA0001\nx: info XX0001")
        result = self.run_compile(success=False)
        self.assertEqual(result.returncode, 1)
        self.assertIn("exit=1 errors=1 warnings=1 infos=1", result.stdout)


if __name__ == "__main__":
    unittest.main()
