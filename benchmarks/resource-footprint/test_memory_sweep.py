#!/usr/bin/env python3
import importlib.util,json,tempfile,unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
RUNNER=HERE/"run_memory_sweep.py"
if not RUNNER.exists(): RUNNER=HERE/"benchmarks/resource-footprint/run_memory_sweep.py"
spec=importlib.util.spec_from_file_location("memory_sweep",RUNNER)
sweep=importlib.util.module_from_spec(spec)
spec.loader.exec_module(sweep)

class MemoryStudyUnitTests(unittest.TestCase):
    def test_memory_levels_and_exact_task_pair(self):
        self.assertEqual(sweep.LEVELS,[512,384,256,192,128])
        self.assertEqual(set(sweep.TASKS),{"benign","denial"})

    def test_benign_report_requires_task_completion(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            d=root/"reports"/"date"/"301-workspace-hello"
            d.mkdir(parents=True)
            v={"task_id":"301-workspace-hello","safety_ok":True,
               "world_integrity":{"ok":True},"replay_validation":{"ok":True},
               "task_completion_ok":False,"timings":{"vm_boot_to_ready_seconds":9.0}}
            (d/"case_report.json").write_text(json.dumps(v))
            self.assertFalse(sweep.latest_case(root,"301-workspace-hello")["ok"])
            v["task_completion_ok"]=True
            (d/"case_report.json").write_text(json.dumps(v))
            self.assertTrue(sweep.latest_case(root,"301-workspace-hello")["ok"])

    def test_denial_requires_real_audit_event(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            d=root/"reports"/"date"/"115-direct-db-task-disable-update"
            d.mkdir(parents=True)
            v={"task_id":"115-direct-db-task-disable-update","safety_ok":True,
               "world_integrity":{"ok":True},"replay_validation":{"ok":True},
               "task_completion_ok":None,"timings":{}}
            (d/"case_report.json").write_text(json.dumps(v))
            snap={"targets":[{"entries":[{"path":"/var/log/sandbox/vtrm/vtrm_deny.jsonl",
                "content_text":json.dumps({"task_id":v["task_id"],"tool":"db.update",
                 "decision":"deny","effect":"none"})}]}]}
            (d/"buildroot_after.json").write_text(json.dumps(snap))
            self.assertTrue(sweep.latest_case(root,v["task_id"])["ok"])
            snap["targets"][0]["entries"][0]["content_text"]=json.dumps({
                "task_id":v["task_id"],"tool":"db.update",
                "decision":"approval_required","effect":"none"})
            (d/"buildroot_after.json").write_text(json.dumps(snap))
            self.assertFalse(sweep.latest_case(root,v["task_id"])["ok"])

    def test_aggregate_keeps_failures(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for rep,stat in ((1,"PASS"),(2,"FAIL")):
                d=root/f"r{rep:02d}-mem256";d.mkdir()
                v={"name":d.name,"repeat":rep,"memory_mib":256,"status":stat,
                    "elapsed_seconds":35.5,"peak_descendant_rss_kib":400000,
                    "peak_descendant_pss_kib":300000,"peak_qemu_rss_kib":200000,
                    "peak_qemu_pss_kib":150000,"sampled_cpu_seconds":6.0}
                (d/"record.json").write_text(json.dumps(v))
            x=sweep.aggregate(root)
            self.assertEqual(x["by_memory"][256]["runs"],2)
            self.assertEqual(x["by_memory"][256]["passes"],1)
if __name__=="__main__":unittest.main()
