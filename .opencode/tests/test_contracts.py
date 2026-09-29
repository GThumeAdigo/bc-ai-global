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


if __name__ == "__main__":
    unittest.main()
