"""Audit classification must not conflate approvals with denials."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_replay import denied


class AuditSemanticsTests(unittest.TestCase):
    def test_approval_required_is_not_an_absolute_denial(self):
        event = {
            "tool": "fs.write", "decision": "approval_required",
            "status": "pending", "rule": "profile.approval_required",
            "reason": "Capability fs.write.protected requires approval",
        }
        self.assertFalse(denied(event))

    def test_readonly_database_denial(self):
        self.assertTrue(denied({"tool": "db.update", "decision": "deny",
                                "status": "skipped", "rule": "invalid_object_action"}))

    def test_permitted_effect_not_a_denial(self):
        self.assertFalse(denied({"tool": "fs.write", "decision": "auto",
                                 "status": "success", "effect": "fs_write"}))


if __name__ == "__main__":
    unittest.main()
