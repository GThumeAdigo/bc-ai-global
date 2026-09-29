import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
loader = importlib.machinery.SourceFileLoader("installer", str(ROOT / "scripts/install"))
spec = importlib.util.spec_from_loader(loader.name, loader)
installer = importlib.util.module_from_spec(spec)
loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.app = self.repo / 'apps' / 'An app "quoted"'
        self.app.mkdir(parents=True)
        (self.app / "app.json").write_text('{}')
        self.selected = self.root / "release"
        (self.selected / "runtime").mkdir(parents=True)
        for name in ("AGENTS.md", "CLAUDE.md"):
            (self.selected / "runtime" / name).write_text(name)
        (self.selected / "runtime/opencode.json").write_text(json.dumps({"path": "@APP@", "mcp": {"playwright": {"enabled": False}}}))
        for name in ("agents", "skills", "commands", "BCQuality-ADIGO", "serena-al"):
            (self.selected / ".opencode" / name).mkdir(parents=True)
        (self.selected / "templates/specs").mkdir(parents=True)
        (self.selected / "templates/specs/brief.md").write_text("template")
        (self.selected / "templates/APP_CONTEXT.md").write_text("context")

    def run_install(self, *options, apps=None):
        args = ["install", *(str(p) for p in (apps or [self.app])), "--backup-root", str(self.root / "backup"), *options]
        with patch.object(sys, "argv", args), patch.object(installer, "release", return_value=self.selected):
            installer.main()

    def test_local_runtime_and_quoted_config(self):
        self.run_install()
        self.assertFalse((self.app / ".opencode").is_symlink())
        self.assertTrue((self.app / ".opencode/skills").is_symlink())
        self.assertEqual(json.loads((self.app / "opencode.json").read_text())["path"], str(self.app))

    def test_permission_path_keys_are_rendered(self):
        value = {"permission": {"edit": {"@RELEASE@/**": "deny"}}}
        rendered = installer.render(value, {"@RELEASE@": "/isolated/release"})
        self.assertEqual(rendered["permission"]["edit"], {"/isolated/release/**": "deny"})

    def test_idempotence_and_private_files_preserved(self):
        self.run_install()
        (self.app / "specs/brief.md").write_text("owner decision")
        exclude = self.repo / ".git/info/exclude"
        before = exclude.read_text()
        self.run_install()
        self.assertEqual(before, exclude.read_text())
        self.assertEqual((self.app / "specs/brief.md").read_text(), "owner decision")

    def test_batch_preflight_does_not_touch_first_app(self):
        second = self.repo / "other"
        second.mkdir()
        (second / "app.json").write_text('{}')
        (second / "AGENTS.md").write_text("owner")
        with self.assertRaisesRegex(ValueError, "unmanaged"):
            self.run_install(apps=[self.app, second])
        self.assertFalse((self.app / "AGENTS.md").exists())

    def test_dry_run_does_not_install(self):
        self.run_install("--dry-run")
        self.assertFalse((self.app / ".agent-state").exists())

    def test_update_and_rollback(self):
        self.run_install()
        before = (self.app / "opencode.json").read_text()
        self.run_install("--profile", "browser")
        self.assertTrue(json.loads((self.app / "opencode.json").read_text())["mcp"]["playwright"]["enabled"])
        self.run_install("--rollback")
        self.assertEqual((self.app / "opencode.json").read_text(), before)

    def test_rollback_preserves_user_edit_by_refusing(self):
        self.run_install()
        (self.app / "opencode.json").write_text("user work")
        with self.assertRaisesRegex(ValueError, "conflict"):
            self.run_install("--rollback")
        self.assertEqual((self.app / "opencode.json").read_text(), "user work")

    def test_jsonc_workspace_and_unique_name(self):
        workspace = self.repo / "main.code-workspace"
        workspace.write_text('{//comment\n"folders": [], "settings": {"x": 1,},}')
        self.run_install("--workspace", str(workspace))
        output = list(self.repo.glob("SDD-*.code-workspace"))
        self.assertEqual(len(output), 1)
        self.assertEqual(json.loads(output[0].read_text())["settings"], {"x": 1})

    def test_template_symlink_refused(self):
        (self.app / "specs").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_install()

    def test_workspace_suffix_collision_is_avoided(self):
        second = self.repo / "other" / self.app.name
        second.mkdir(parents=True)
        (second / "app.json").write_text('{}')
        workspace = self.repo / "main.code-workspace"
        workspace.write_text('{"folders": []}')
        self.run_install("--workspace", str(workspace), apps=[self.app, second])
        self.assertEqual(len(list(self.repo.glob("SDD-*.code-workspace"))), 2)

    def test_failure_restores_already_applied_paths(self):
        original = (self.repo / ".git/info/exclude").read_bytes()
        real_put = installer.put
        def fail(path, state):
            if path.name == "CLAUDE.md" and state["kind"] == "link":
                raise OSError("injected write failure")
            real_put(path, state)
        with patch.object(installer, "put", side_effect=fail):
            with self.assertRaisesRegex(OSError, "injected"):
                self.run_install()
        self.assertEqual((self.repo / ".git/info/exclude").read_bytes(), original)
        self.assertFalse((self.app / "AGENTS.md").exists())
        self.assertFalse((self.app / ".agent-state/install.json").exists())

    def test_legacy_link_requires_explicit_migration(self):
        legacy = self.root / "legacy"
        (legacy / ".opencode").mkdir(parents=True)
        for name in ("AGENTS.md", "CLAUDE.md", "opencode.json"):
            (legacy / name).write_text("old")
            (self.app / name).symlink_to(legacy / name)
        (self.app / ".opencode").symlink_to(legacy / ".opencode")
        with self.assertRaisesRegex(ValueError, "migrate-legacy"):
            self.run_install()
        self.run_install("--migrate-legacy")
        self.run_install("--rollback")
        self.assertEqual((self.app / ".opencode").resolve(), legacy / ".opencode")

    def test_malformed_excludes_fail_before_install(self):
        (self.repo / ".git/info/exclude").write_text(installer.START)
        with self.assertRaisesRegex(ValueError, "malformed"):
            self.run_install()
        self.assertFalse((self.app / "AGENTS.md").exists())


if __name__ == "__main__":
    unittest.main()
