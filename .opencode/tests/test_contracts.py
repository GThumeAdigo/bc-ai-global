import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


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


if __name__ == "__main__":
    unittest.main()
