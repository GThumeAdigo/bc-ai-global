import json
from pathlib import Path
import re
import unittest
import fnmatch
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]


def frontmatter(path):
    return yaml.safe_load(path.read_text().split("---", 2)[1])


def tool_action(permissions, name):
    result = None
    for pattern, action in permissions.items():
        if fnmatch.fnmatchcase(name, pattern):
            result = action
    return result


class Contracts(unittest.TestCase):
    def test_native_command_agents_exist(self):
        for command in (ROOT / ".opencode/commands").glob("*.md"):
            match = re.search(r"^agent: (.+)$", command.read_text(), re.M)
            if match:
                self.assertTrue((ROOT / ".opencode/agents" / (match[1] + ".md")).is_file(), command)

    def test_exact_corpus_targets_exist(self):
        for directory in ("agents", "skills"):
            for file in (ROOT / ".opencode" / directory).rglob("*.md"):
                for target in re.findall(r"`(\.opencode/BCQuality-ADIGO/custom/skills/[^`]+\.md)`", file.read_text()):
                    self.assertTrue((ROOT / target).is_file(), (file, target))

    def test_json_config_and_schema_declaration(self):
        for config in (ROOT / "opencode.json", ROOT / "runtime/opencode.json"):
            if config.exists():
                self.assertEqual(json.loads(config.read_text())["$schema"], "https://opencode.ai/config.json")

    def test_model_policy_has_one_authority(self):
        policy = json.loads((ROOT / "runtime/model-policy.json").read_text())
        self.assertEqual(set(policy), {"model", "variant"})
        for agent in (ROOT / ".opencode/agents").glob("*.md"):
            self.assertNotRegex(agent.read_text().split("---", 2)[1], r"(?m)^(model|variant):")

    def test_core_reviewers_deny_writes_and_shell(self):
        import yaml
        for name in ("al-change-reviewer", "al-design-reviewer", "al-test-reviewer"):
            data = yaml.safe_load((ROOT / f".opencode/agents/{name}.md").read_text().split("---", 2)[1])
            permissions = data["permission"]
            self.assertEqual(permissions["*"], "deny")
            self.assertEqual(permissions.get("bash", "deny"), "deny")
            self.assertEqual(permissions.get("edit", "deny"), "deny")
            self.assertNotIn("serena_replace_symbol_body", permissions)

    def test_bootstrap_budget(self):
        for path, limit in (("runtime/AGENTS.md", 120), (".opencode/skills/sdd/SKILL.md", 150)):
            self.assertLessEqual(sum(bool(line.strip()) for line in (ROOT / path).read_text().splitlines()), limit)

    def test_sdd_keeps_current_primary_and_review_commands_use_child_tasks(self):
        sdd = frontmatter(ROOT / ".opencode/commands/sdd.md")
        self.assertNotIn("agent", sdd)
        self.assertNotIn("model", sdd)
        self.assertNotIn("subtask", sdd)
        for command in (ROOT / ".opencode/commands").glob("al-*.md"):
            data = frontmatter(command)
            agent = frontmatter(ROOT / ".opencode/agents" / (data["agent"] + ".md"))
            self.assertEqual(agent["mode"], "subagent")
            self.assertIsNot(data.get("subtask"), False)
            self.assertIn("legacy", data["description"].lower())

    def test_read_only_specialists_deny_mutating_tools_but_can_route(self):
        writable_roles = {"custom-al-implementer", "al-test-writer", "al-userguide-test-writer", "al-table-refactorer", "al-test-runner", "bc-webclient-runner"}
        mutation_tools = ("edit", "serena_replace_content", "serena_replace_in_files", "serena_replace_symbol_body", "serena_insert_after_symbol", "serena_insert_before_symbol", "serena_rename_symbol", "serena_safe_delete_symbol", "alcops_apply_fix", "nab-al-tools_saveTranslatedTexts", "al-mcp_al_publish", "task")
        for path in (ROOT / ".opencode/agents").glob("*.md"):
            if path.stem in writable_roles:
                continue
            data = frontmatter(path)
            self.assertEqual(data["mode"], "subagent")
            permissions = data["permission"]
            for tool in mutation_tools:
                self.assertEqual(tool_action(permissions, tool), "deny", (path.name, tool))
            if "reviewer-execution.md" not in path.read_text():
                continue
            self.assertEqual(permissions["bash"]["*"], "deny")
            self.assertEqual(permissions["bash"]["python3 .opencode/BCQuality-ADIGO/tools/route_entry.py *"], "allow")
            self.assertEqual(tool_action(permissions, "serena_find_symbol"), "allow")
            self.assertEqual(tool_action(permissions, "serena_search_for_pattern"), "allow")

    def test_specialists_route_with_stdin_without_writing_context(self):
        corpus = ROOT / ".opencode/BCQuality-ADIGO"
        for path in (ROOT / ".opencode/agents").glob("*.md"):
            text = path.read_text()
            if "reviewer-execution.md" not in text:
                continue
            skill_id = re.search(r"requested-skill-id: ([a-z0-9-]+)", text)[1]
            context = {"requested-skill-id": skill_id, "inputs-available": ["pr-diff", "file-path", "repository", "object-list", "deployment-context"]}
            result = subprocess.run([sys.executable, str(corpus / "tools/route_entry.py"), "--root", str(corpus), "--task-context", "/dev/stdin"], input=json.dumps(context), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, (path.name, result.stderr))
            self.assertEqual(json.loads(result.stdout)["outcome"], "routed", path.name)


if __name__ == "__main__":
    unittest.main()
