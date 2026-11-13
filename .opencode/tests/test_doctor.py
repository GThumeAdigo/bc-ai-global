import importlib.machinery
import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader("doctor", str(Path(__file__).resolve().parents[2] / "scripts/doctor"))
spec = importlib.util.spec_from_loader(loader.name, loader)
doctor = importlib.util.module_from_spec(spec)
loader.exec_module(doctor)


class DoctorTests(unittest.TestCase):
    def test_prefixed_node_version(self):
        with patch.object(doctor.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "v24.18.1\n", "")):
            self.assertEqual(doctor.version(["node"])["version"], "24.18.1")

    def test_missing_is_not_available(self):
        self.assertEqual(doctor.version(None)["status"], "unavailable")
