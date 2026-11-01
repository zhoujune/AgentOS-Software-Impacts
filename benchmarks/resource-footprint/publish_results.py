#!/usr/bin/env python3
"""Validate and publish sanitized AgentOS six-task constrained-memory findings.

Inputs must be an already completed private study. Never publish logs, task file
contents, host-specific absolute paths, or guest images. Original data immutable.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, pathlib, re, statistics
from collections import Counter

MEMS=(128,192,256,384,512)
BENIGN={"301-workspace-hello","302-workspace-json","321-delete-workspace-file"}
DENIED={"115-direct-db-task-disable-update","118-direct-db-audit-insert","122-direct-readonly-db-delete"}
TASKS=BENIGN|DENIED

def read(p):return json.loads(pathlib.Path(p).read_text())
def write(p,d):pathlib.Path(p).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def checks_per_case(case):
    tid=case["task_id"]
    legit=tid in BENIGN
    denied=tid in DENIED
    if not (legit or denied):raise ValueError("Unexpected task "+tid)
    ok=(case["world_integrity_ok"] is True
        and case["replay_matches"]==case["replay_requests"]
        and case["replay_requests"]>0)
    ok=ok and ((case.get("task_completion_ok") is True) if legit
               else (case.get("vtrm_denial_verified") is True))
    return ok

def aggregate(v):
    def sr(a):
        return round(a,3)
    return dict(runs=len(v),successful_runs=sum(x["status"]=="PASS" for x in v),
        elapsed_mean_s=sr(statistics.mean(x["elapsed_seconds"] for x in v)),
        elapsed_median_s=sr(statistics.median(x["elapsed_seconds"] for x in v)),
        elapsed_range_s=[min(x["elapsed_seconds"] for x in v),max(x["elapsed_seconds"] for x in v)],
        mean_cpu_seconds=sr(statistics.mean(x["sampled_cpu_seconds"] for x in v)),
        median_peak_sampled_process_tree_pss_mib=sr(statistics.median(x["peak_descendant_pss_kib"]/1024 for x in v)),
        maximum_peak_sampled_process_tree_pss_mib=sr(max(x["peak_descendant_pss_kib"] for x in v)/1024),
        maximum_peak_sampled_qemu_rss_mib=sr(max(x["peak_qemu_rss_kib"] for x in v)/1024),
        maximum_peak_sampled_qemu_pss_mib=sr(max(x["peak_qemu_pss_kib"] for x in v)/1024))

def publish(root, source, out):
    if out.exists():raise FileExistsError("Refusing to overwrite output directory")
    prov=read(root/"input_provenance.json")
    schedule=read(root/"full_schedule.json")
    screens=read(root/"screen_summary.json")
    input_files={"clean_candidate_image":source/"runtime/offline-eval/rootfs.eval.offline.ext2",
                 "canonical_unmodified_image":source/"artifacts/images/rootfs.eval.clean.ext2",
                 "kernel":source/"artifacts/images/bzImage",
                 "replay_cassette":source/"judge/replays/representative-offline.json"}
    for name,path in input_files.items():
        if not path.is_file() or sha(path)!=prov["inputs"][name]["sha256"]:
            raise ValueError("Input integrity failure "+name)
    if screens.get("statuses")!={str(m):True for m in MEMS}:
        raise ValueError("Screen outcomes incomplete or invalid")
    order=[(x["repeat"],x["memory_mib"]) for x in schedule["schedule"]]
    if len(order)!=15 or set(order)!={(i,m) for i in (1,2,3) for m in MEMS}:
        raise ValueError("Unbalanced or incomplete full schedule")
    rows=[];cases=[]
    for rep,mem in order:
        name=f"r{rep:02d}-mem{mem}"
        d=root/"full"/name
        record=read(d/"record.json")
        raw=read(d/"output"/"offline_benchmark.json")
        if (record["memory_mib"],record["repeat"])!=(mem,rep) or record["name"]!=name:
            raise ValueError("Run metadata mismatch "+name)
        if record.get("timed_out") or record["exit_code"]!=0 or record["status"]!="PASS":
            raise ValueError("Run failed "+name)
        if raw["representative_task_count"]!=6 or raw["suite_count"]!=2 or not raw["all_ok"] or raw["errors"]:
            raise ValueError("Raw suite judge failed "+name)
        task_ids=set()
        for kind,ids in (("benign",BENIGN),("denials",DENIED)):
            suite=raw["suites"][kind]
            if not (suite["all_ok"] and suite["replay_ok"] and suite["guest_network_enabled"] is False):
                raise ValueError("Suite predicate fail "+name+" "+kind)
            if {case["task_id"] for case in suite["cases"]}!=ids:
                raise ValueError("Task set mismatch "+name+" "+kind)
            for c in suite["cases"]:
                tid=c["task_id"];task_ids.add(tid)
                if not checks_per_case(c):raise ValueError("Case failure "+name+" "+tid)
                cases.append(dict(case_oracle_ok=True,repetition=rep,guest_memory_mib=mem,task_id=tid,
                    category=kind,run_status=c["run_status"],
                    task_completion_ok=c.get("task_completion_ok"),
                    world_integrity_ok=c["world_integrity_ok"],
                    replay_requests=c["replay_requests"],replay_matches=c["replay_matches"],
                    policy_denial_audited=c.get("vtrm_denial_verified"),
                    case_duration_seconds=c.get("case_duration_seconds"),
                    boot_to_ready_seconds=c.get("timings",{}).get("vm_boot_to_ready_seconds")))
        if task_ids!=TASKS:raise ValueError("Missing task "+name)
        for k in ("elapsed_seconds","peak_descendant_pss_kib","peak_descendant_rss_kib",
                  "peak_qemu_rss_kib","peak_qemu_pss_kib","sampled_cpu_seconds"):
            if not isinstance(record[k],(int,float)):raise ValueError("Bad resource number")
        rows.append({k:record[k] for k in
            ("name","repeat","memory_mib","status","elapsed_seconds",
             "peak_descendant_pss_kib","peak_descendant_rss_kib",
             "peak_qemu_rss_kib","peak_qemu_pss_kib","sampled_cpu_seconds","samples")})
    if len(rows)!=15 or len(cases)!=90 or any(c["case_oracle_ok"] is not True for c in cases):raise ValueError("Incomplete or failing data")
    by_mem={str(m):aggregate([r for r in rows if r["memory_mib"]==m]) for m in MEMS}
    guest_boot={}
    for m in MEMS:
        s=(root/"full"/f"r01-mem{m}"/"output"/"reports"/"benign")
        logs=list(s.rglob("qemu.log"))
        if not logs:raise ValueError("Missing guest boot log "+str(m))
        text=logs[0].read_text(errors="replace")
        matches=re.findall(r"Memory:\s+(\d+)K/(\d+)K available",text)
        if not matches:raise ValueError("Guest RAM not evidenced "+str(m))
        free,total=map(int,matches[0])
        guest_boot[str(m)]={"linux_boot_available_kib":free,
                            "linux_boot_reported_memory_kib":total}
    data=dict(schema_version="0.1",study="AgentOS CPU-only constrained-guest-memory repeated replay",
        status="COMPLETED_INTERNAL_SINGLE_HOST_STUDY",
        design={"configured_guest_ram_mib":list(MEMS),"repetitions":3,
                "six_tasks":sorted(TASKS),"full_case_count":90,
                "screen_case_count":10,"guest_network_enabled":False,
                "replay_mode":"deterministic CPU-only cassette; no LLM inference",
                "ordering":"within-block shuffled with seed 20261101"},
        validation={"full_suites":15,"full_suites_passed":15,
                    "full_cases":90,"full_cases_passed":sum(c["case_oracle_ok"] is True for c in cases),
                    "case_report_verification":"Original host offline_benchmark.json suite validators",
                    "inputs_currently_hash_verified":True},
        host_environment={**prov["host"],"acceleration":"QEMU TCG software emulation (/dev/kvm absent)"},
        artifact_fingerprints=prov["inputs"],guest_boot_meminfo=guest_boot,
        by_memory=by_mem,full_runs=rows,case_metadata=cases,
        limitations=[
            "Guest RAM is a QEMU configured cap, not total physical edge-device memory or directly measured resident guest working set.",
            "Host process tree PSS/RSS includes QEMU emulation and evaluator/proxy processes but excludes other host programs, device overhead and page cache.",
            "The server lacks /dev/kvm: QEMU uses TCG software emulation. PSS is not a hypervisor-independent constant.",
            "Only six selected deterministic-replay tasks are repeated; this is not a statistical guarantee of reliability for arbitrary agents.",
            "Three repetitions per memory are descriptive. Tests below 128 MiB were not performed; the true minimum viable allocation is unknown.",
            "No ARM/edge silicon, local LLM inference, power or energy measurements, or apples-to-apples baseline against other sandboxes.",
            "The source images, kernel and cassette were unmodified during the experiment.",
        ])
    out.mkdir(parents=True)
    write(out/"20261101-memory-full.json",data)
    with (out/"20261101-memory-cases.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(cases[0]));w.writeheader();w.writerows(cases)
    with (out/"20261101-memory-runs.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    md=["# AgentOS: CPU-only constrained-memory benchmark (2026-11-01)",
        "","**Status:** Completed internal x86_64/QEMU-TCG study; not physical edge deployment.",
        "","The design screened 5 memory configurations using a benign write and an audited strict database denial (10/10 passed);",
        "then evaluated 6 deterministic replay tasks × 3 repetitions × 5 guest-memory settings = **90/90 task passes**.",
        "Three tasks validate permitted workspace effects; three validate explicit strict DB denials.",
        "All 15 full-run host evaluator reports had `all_ok=true`, with exact replay, disabled guest networking and passing world integrity.",
        "","## Results","",
        "| QEMU guest RAM | Full task passes | Mean suite runtime (s) | Peak sampled process-tree PSS (MiB) | Peak sampled QEMU RSS (MiB) |",
        "| ---: | ---: | ---: | ---: | ---: |"]
    for m in sorted(MEMS,reverse=True):
        b=by_mem[str(m)]
        md.append(f"| {m} MiB | {b['successful_runs']*6}/18 | {b['elapsed_mean_s']:.2f} | "
                  f"{b['maximum_peak_sampled_process_tree_pss_mib']:.2f} | {b['maximum_peak_sampled_qemu_rss_mib']:.2f} |")
    md.extend(["","## Interpretation","",
        f"The boot log at 128 MiB reports **{guest_boot['128']['linux_boot_available_kib']/1024:.1f} MiB available** to the Linux guest kernel after reservations.",
        "Task completion and policy enforcement under a 128 MiB **configured guest-memory limit**",
        "provide evidence of resource-constrained guest feasibility for these six selected tasks.",
        "The recorded sampled host process-tree PSS remains near 400 MiB even at 128 MiB guest RAM;",
        "therefore the entire QEMU-based host/runtime cannot be claimed to fit in 128 MiB.",
        "QEMU ran with **TCG software emulation** because the host did not expose `/dev/kvm`.",
        "These host-memory measurements mix emulation, agent and evaluation costs.",
        "Mean runtimes varied by less than three seconds across configurations, but no statistical speedup or minimum-memory threshold is established.",
        "",
        "## Reproducibility","",
        "The checked input and case fingerprints are recorded in [full JSON](20261101-memory-full.json).",
        "Case-level metadata and per-run RSS/PSS and timing records are in the accompanying CSV files.",
        "The original host traces, QEMU guest images and filesystem snapshots remain on the private research host.",
        "Use the open-source benchmark runner to reproduce locally; source files are not modified.",
        "","## Limits","",
        "- CPU-only deterministic replay is not evidence of live-LLM inference under constrained guest RAM.",
        "- No actual edge board, ARM64 port, or power/energy evaluation has been conducted.",
        "- The 128 MiB setting is an upper tested viable configuration boundary; smaller settings were not tested.",
        "- Host-process peak PSS is sampled at ~0.5 s, not an instantaneous system-wide physical memory peak.",
        "- This is a narrow descriptive functional experiment, not an apples-to-apples comparison with Firecracker, containers, or Wasm runtimes.",
        ""])
    (out/"20261101-memory-results.md").write_text("\n".join(md))
    print(json.dumps({"files":[p.name for p in out.iterdir()],"full_runs":len(rows),
           "cases":len(cases),"passes":data["validation"]["full_cases_passed"],
           "guest_boot_128":guest_boot["128"],"by_memory":by_mem},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--study",type=pathlib.Path,required=True)
    p.add_argument("--source",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    publish(a.study,a.source,a.out)
