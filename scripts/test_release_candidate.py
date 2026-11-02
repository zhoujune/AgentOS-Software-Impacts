#!/usr/bin/env python3
"""Fail-closed unit tests for AgentOS RC result validation."""
import importlib.util
import pathlib
import unittest

SCRIPT = pathlib.Path(__file__).with_name("validate_release_candidate.py")
spec = importlib.util.spec_from_file_location("rc_verify", SCRIPT)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)

def baseline():
    def entry(task,denied):
        return dict(task_id=task,world_integrity_ok=True,
                    replay_requests=2,replay_matches=2,
                    task_completion_ok=None if denied else True,
                    vtrm_denial_verified=True if denied else None)
    return dict(all_ok=True,errors=[],representative_task_count=6,suite_count=2,
                suites={
                    "benign": dict(all_ok=True,replay_ok=True,guest_network_enabled=False,
                                   cases=[entry(t,False) for t in sorted(rc.BENIGN)]),
                    "denials":dict(all_ok=True,replay_ok=True,guest_network_enabled=False,
                                   cases=[entry(t,True) for t in sorted(rc.DENIALS)])})

def demo():
    def c(label,ok,n):
        return dict(label=label,observed_task_completion=ok,
                    safety_ok=True,replay_ok=True,world_integrity_ok=True,
                    replay_requests=n,matched_replay_requests=n,
                    target_path_changed=ok,
                    authorized_write_audit_count=1 if ok else 0)
    return dict(validation="PASS",errors=[],cases=[
        c("performed-write",True,2),
        c("unsupported-success",False,1)])

class RCValidationTests(unittest.TestCase):
    def test_valid_baseline(self):
        self.assertEqual(len(rc.verify_baseline(baseline())),6)
    def test_missing_denial_fails(self):
        b=baseline()
        b["suites"]["denials"]["cases"][0]["vtrm_denial_verified"]=False
        with self.assertRaises(ValueError):rc.verify_baseline(b)
    def test_network_enabled_fails(self):
        b=baseline();b["suites"]["benign"]["guest_network_enabled"]=True
        with self.assertRaises(ValueError):rc.verify_baseline(b)
    def test_invalid_replay_fails(self):
        b=baseline();b["suites"]["benign"]["cases"][0]["replay_matches"]=1
        with self.assertRaises(ValueError):rc.verify_baseline(b)
    def test_valid_demo(self):
        self.assertEqual(len(rc.verify_demo(demo())),2)
    def test_false_success_with_effect_fails(self):
        d=demo();d["cases"][1]["target_path_changed"]=True
        with self.assertRaises(ValueError):rc.verify_demo(d)
    def test_missing_positive_audit_fails(self):
        d=demo();d["cases"][0]["authorized_write_audit_count"]=0
        with self.assertRaises(ValueError):rc.verify_demo(d)

if __name__=="__main__":unittest.main()
