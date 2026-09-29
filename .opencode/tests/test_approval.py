import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("approval", ROOT / ".opencode/skills/sdd/scripts/approval.py")
approval = importlib.util.module_from_spec(spec)
spec.loader.exec_module(approval)


class ApprovalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.artifact = self.root / "spec.md"
        self.artifact.write_text("approved behavior")
        self.record = self.root / "evidence/approval.json"

    def approve(self):
        approval.record(self.record, [self.artifact], "owner", "I approve this spec")

    def test_matching_content_and_scope(self):
        self.approve()
        self.assertEqual(approval.check(self.record, [self.artifact])["status"], "pass")

    def test_changed_spec_blocks(self):
        self.approve()
        self.artifact.write_text("different behavior")
        with self.assertRaisesRegex(ValueError, "stale"):
            approval.check(self.record, [self.artifact])

    def test_record_cannot_overwrite_prior_approval(self):
        self.approve()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.approve()

    def test_empty_owner_does_not_approve(self):
        with self.assertRaisesRegex(ValueError, "required"):
            approval.record(self.record, [self.artifact], "", "")

    def test_additional_plan_requires_approval(self):
        self.approve()
        plan = self.root / "plan.md"
        plan.write_text("design")
        with self.assertRaisesRegex(ValueError, "scope"):
            approval.check(self.record, [self.artifact, plan])

    def test_progress_outside_spec_does_not_invalidate(self):
        self.approve()
        (self.root / "validation.md").write_text("task complete")
        self.assertEqual(approval.check(self.record, [self.artifact])["status"], "pass")


if __name__ == "__main__":
    unittest.main()
