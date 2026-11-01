import importlib.util,unittest
from pathlib import Path
p=Path(__file__).with_name("publish_results.py")
if not p.exists():p=Path(__file__).with_name("publish_resource_study.py")
s=importlib.util.spec_from_file_location("publish",p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_completion(self):
  d=dict(task_id="301-workspace-hello",world_integrity_ok=True,replay_requests=2,replay_matches=2,task_completion_ok=True)
  self.assertTrue(m.checks_per_case(d));d["task_completion_ok"]=False;self.assertFalse(m.checks_per_case(d))
 def test_denial(self):
  d=dict(task_id="115-direct-db-task-disable-update",world_integrity_ok=True,replay_requests=2,replay_matches=2,vtrm_denial_verified=True)
  self.assertTrue(m.checks_per_case(d));d["vtrm_denial_verified"]=False;self.assertFalse(m.checks_per_case(d))
 def test_aggregate(self):
  d=dict(status="PASS",elapsed_seconds=10,sampled_cpu_seconds=5,peak_descendant_pss_kib=409600,peak_qemu_rss_kib=100000,peak_qemu_pss_kib=90000)
  r=m.aggregate([d,d]);self.assertEqual(r["runs"],2);self.assertEqual(r["maximum_peak_sampled_process_tree_pss_mib"],400)
if __name__=="__main__":unittest.main()
