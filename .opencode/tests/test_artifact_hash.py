"""Regression tests for the approval digest byte contract and CLI."""

import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


HELPER = Path(__file__).resolve().parents[1] / "skills/sdd/scripts/artifact_hash.py"
SPEC = importlib.util.spec_from_file_location("artifact_hash", HELPER)
HASH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HASH)


class ArtifactHashTests(unittest.TestCase):
    def test_checkbox_only_equality(self):
        pending = b"- [ ] First\r\n  * [ ] Nested\n+ [ ] Other\n1. [ ] Ordered\n2) [ ] Last"
        checked = pending.replace(b"[ ]", b"[x]", 2).replace(b"[ ]", b"[X]")
        self.assertEqual(HASH.normalize_tasks(pending), HASH.normalize_tasks(checked))

    def test_substantive_bytes_preserved(self):
        data = b"- [x] text [x] and `- [x] literal`\r\nparagraph - [X]\n- [x]suffix\n\xff\v\f\r"
        expected = data.replace(b"- [x] text", b"- [ ] text", 1)
        self.assertEqual(HASH.normalize_tasks(data), expected)
        for changed in (data.replace(b"text", b"changed"),
                        data.replace(b"literal", b"other"),
                        data.replace(b"text [x]", b"text [ ]"),
                        data.replace(b"\r\n", b"\n")):
            self.assertNotEqual(HASH.normalize_tasks(data), HASH.normalize_tasks(changed))

    def test_fenced_examples_preserved(self):
        for fence in (b"```", b"~~~~"):
            data = (fence + b"markdown\r\n- [x] example\r\n"
                    + fence[:2] + b"\n- [X] still example\n"
                    + fence + b"\n- [x] real\n")
            self.assertEqual(HASH.normalize_tasks(data), data.replace(b"- [x] real", b"- [ ] real"))
            self.assertNotEqual(HASH.normalize_tasks(data), HASH.normalize_tasks(data.replace(b"[x] example", b"[ ] example")))
        unclosed = b"  ```al\n- [x] example\n"
        self.assertEqual(HASH.normalize_tasks(unclosed), unclosed)

    def test_indented_examples_preserved(self):
        for indent in (b"    ", b"\t", b"        "):
            data = b"Expected literal output:\n\n" + indent + b"- [ ] disabled\n"
            changed = data.replace(b"[ ]", b"[x]")
            self.assertEqual(HASH.normalize_tasks(changed), changed)
            self.assertNotEqual(HASH.normalize_tasks(data), HASH.normalize_tasks(changed))
        shallow = b"   - [x] shallow task\n"
        self.assertEqual(HASH.normalize_tasks(shallow), shallow.replace(b"[x]", b"[ ]"))

    def test_raw_hashing_and_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("spec.md", "plan.md", "tasks.md")]
            data = b"- [X] substantive\r\n\xff\n"
            for path in paths:
                path.write_bytes(data)
            result = subprocess.run([sys.executable, str(HELPER), *map(str, paths)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = [hashlib.sha256(data).hexdigest()] * 2 + [hashlib.sha256(data.replace(b"[X]", b"[ ]")).hexdigest()]
            self.assertEqual(result.stdout.splitlines(), [f"{digest}  {path}" for digest, path in zip(expected, paths)])
            self.assertEqual([path.read_bytes() for path in paths], [data] * 3)

    def test_digest_progress_and_substantive_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tasks.md"
            for ending in (b"\n", b"\r\n", b"\r"):
                pending = ending.join((b"- [ ] first", b"- [ ] last"))
                path.write_bytes(pending)
                original = HASH.artifact_digest(path)
                path.write_bytes(pending.replace(b"[ ]", b"[X]"))
                self.assertEqual(HASH.artifact_digest(path), original)
                path.write_bytes(pending.replace(b"last", b"changed"))
                self.assertNotEqual(HASH.artifact_digest(path), original)

    def test_fence_boundaries_and_empty_input(self):
        self.assertEqual(HASH.normalize_tasks(b""), b"")
        data = b"```\r- [x] protected\r~~~~\r- [X] protected\r````\r- [x] real"
        self.assertEqual(HASH.normalize_tasks(data), data.replace(b"[x] real", b"[ ] real"))
        data = b"  ~~~\n- [X] protected\n  ~~~~  \n- [X] real"
        self.assertEqual(HASH.normalize_tasks(data), data.replace(b"[X] real", b"[ ] real"))

    def test_version_and_mixed_error(self):
        version = subprocess.run([sys.executable, str(HELPER), "--version"], capture_output=True, text=True)
        self.assertEqual(version.returncode, 0)
        self.assertEqual(version.stdout.strip(), "sdd-artifact-v1")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.md"
            path.write_bytes(b"plan")
            result = subprocess.run([sys.executable, str(HELPER), str(path), str(path.parent / "missing")], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(len(result.stdout.splitlines()), 1)
            self.assertIn("missing", result.stderr)

    def test_cli_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            for args in ([], [str(Path(directory) / "missing.md")], [directory]):
                result = subprocess.run([sys.executable, str(HELPER), *args], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
