import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("evidence", Path(__file__).resolve().parents[1] / "scripts/build_evidence.py")
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def test_line_shift_is_not_new_but_message_change_is(self):
        base = {"file": "a.al", "line": 1, "column": 2, "rule": "AA0001", "severity": "warning", "message": "old"}
        shifted = {**base, "line": 50}
        changed = {**shifted, "message": "new"}
        self.assertEqual(evidence.new_diagnostics([shifted], [base]), [])
        self.assertEqual(evidence.new_diagnostics([changed], [base]), [changed])

    def test_duplicate_diagnostic_is_counted(self):
        diagnostic = {"raw": "warning AA0001: issue"}
        self.assertEqual(evidence.new_diagnostics([diagnostic, diagnostic], [diagnostic]), [diagnostic])

    def test_parser_retains_location_and_rule(self):
        parsed = evidence.diagnostics('/app/src/a.al(2,3): warning AA0001: message', Path('/app'))
        self.assertEqual(parsed[0]["file"], "src/a.al")
        self.assertEqual(parsed[0]["line"], 2)
        self.assertEqual(parsed[0]["rule"], "AA0001")
