#!/usr/bin/env python3
"""Controlled CPU-only AgentOS guest-memory sweep, non-destructive.

Protocol: first SCREEN two representative tasks per memory level.
Then FULL executes 3 balanced six-task CPU-only suites for levels that
passed screening. All failures and timeouts are retained. No LLM/API.
Host RSS/PSS is sampled; configured guest RAM != measured guest usage.
"""
from __future__ import annotations
import argparse, collections, csv, datetime as dt, hashlib, json, os, pathlib
import random, re, signal, subprocess, sys, time
from typing import Any

SOURCE=pathlib.Path(os.environ.get("AGENTOS_ROOT", str(pathlib.Path.cwd()))).resolve()
ROOT=pathlib.Path(os.environ.get("AGENTOS_MEMORY_STUDY_ROOT", str(SOURCE/"runtime/resource-memory-study"))).resolve()
IMAGE=SOURCE/"runtime/offline-eval/rootfs.eval.offline.ext2"
CANONICAL=SOURCE/"artifacts/images/rootfs.eval.clean.ext2"
KERNEL=SOURCE/"artifacts/images/bzImage"
CASSETTE=SOURCE/"judge/replays/representative-offline.json"
LEVELS=[512,384,256,192,128]
TASKS={"benign":"301-workspace-hello","denial":"115-direct-db-task-disable-update"}

def sha(path:pathlib.Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def write_json(p:pathlib.Path,v:Any):
    p.write_text(json.dumps(v,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def pid_stat(pid:int):
    try:
        s=(pathlib.Path("/proc")/str(pid)/"stat").read_text()
        tail=s[s.rfind(")")+2:].split()
        # Fields from (3): state, ppid, pgrp, session, ... , utime = index 11, stime = index 12
        return int(tail[1]),int(tail[11])+int(tail[12])
    except (OSError,ValueError,IndexError):return None

def pss_kib(pid:int)->int|None:
    try:
        for line in (pathlib.Path("/proc")/str(pid)/"smaps_rollup").read_text().splitlines():
            if line.startswith("Pss:"):return int(line.split()[1])
    except (OSError,ValueError):pass
    return None

def descendants(rootpid:int):
    # Process-tree accounting, tracks QEMU and proxy even though each creates its own session.
    try:
        t=subprocess.run(["ps","-eo","pid=,ppid=,rss=,comm="],text=True,
                         capture_output=True,timeout=6,check=True)
    except (OSError,subprocess.SubprocessError):return []
    by_parent=collections.defaultdict(list)
    for line in t.stdout.splitlines():
        p=line.split(maxsplit=3)
        if len(p)!=4:continue
        try:pid,ppid,rss=map(int,p[:3])
        except ValueError:continue
        by_parent[ppid].append((pid,rss,p[3]))
    out=[];stack=[rootpid];seen=set()
    while stack:
        parent=stack.pop()
        if parent in seen:continue
        seen.add(parent)
        for pid,rss,name in by_parent.get(parent,[]):
            out.append((pid,rss,name))
            stack.append(pid)
    return out

def run(cmd:list[str],env:dict[str,str],dest:pathlib.Path,timeout_sec:int,
        interval:float=0.5)->dict[str,Any]:
    dest.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    data={"started_at_utc":stamp(),"command_mode":"offline_replay",
          "sampling_interval_seconds":interval,"timeout_seconds":timeout_sec}
    log=dest/"run.log"
    with log.open("w") as f:
        proc=subprocess.Popen(cmd,cwd=SOURCE,env=env,stdin=subprocess.DEVNULL,
                              stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        max_rss=max_pss=max_qemu_rss=max_qemu_pss=0
        samples=0;seen_pids=set();cpu_max={};kvm_seen=False
        memory_samples=[]
        deadline=started+timeout_sec
        timed_out=False
        while proc.poll() is None:
            members=descendants(proc.pid)
            member_pids=[proc.pid]+[pid for pid,_,_ in members]
            member_info=members
            own_stat=pid_stat(proc.pid)
            if own_stat is not None:
                member_info.append((proc.pid,0,"study-runner"))
            rss=sum(rss for _,rss,_ in member_info)
            pss_values=[pss_kib(pid) for pid,_,_ in member_info]
            pss=sum(v for v in pss_values if v is not None)
            qemu=[(pid,rss) for pid,rss,comm in member_info if "qemu-system" in comm]
            qemu_rss=sum(rss for _,rss in qemu)
            qemu_pss=sum(pss_kib(pid) or 0 for pid,_ in qemu)
            for pid in member_pids:
                st=pid_stat(pid)
                if st:cpu_max[pid]=max(cpu_max.get(pid,0),st[1])
            samples+=1
            max_rss=max(max_rss,rss)
            max_pss=max(max_pss,pss)
            max_qemu_rss=max(max_qemu_rss,qemu_rss)
            max_qemu_pss=max(max_qemu_pss,qemu_pss)
            if samples%2==1:
                memory_samples.append(dict(t_seconds=round(time.monotonic()-started,3),
                    aggregate_rss_kib=rss,aggregate_pss_kib=pss,qemu_rss_kib=qemu_rss,
                    qemu_pss_kib=qemu_pss,processes=len(member_info)))
            if time.monotonic()>=deadline:
                timed_out=True
                # Only groups belonging to descendants of our own launched harness.
                for pid,_ in qemu:
                    try:os.killpg(pid,signal.SIGTERM)
                    except ProcessLookupError:pass
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:proc.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                break
            time.sleep(interval)
        try:returncode=proc.wait(timeout=3)
        except subprocess.TimeoutExpired:returncode=-999
    with (dest/"resource_samples.csv").open("w",newline="") as f:
        fields=["t_seconds","aggregate_rss_kib","aggregate_pss_kib",
                "qemu_rss_kib","qemu_pss_kib","processes"]
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(memory_samples)
    data.update(dict(finished_at_utc=stamp(),elapsed_seconds=round(time.monotonic()-started,3),
         exit_code=returncode,timed_out=timed_out,samples=samples,
         peak_descendant_rss_kib=max_rss,peak_descendant_pss_kib=max_pss,
         peak_qemu_rss_kib=max_qemu_rss,peak_qemu_pss_kib=max_qemu_pss,
         sampled_cpu_seconds=round(sum(cpu_max.values())/os.sysconf("SC_CLK_TCK"),2),
         measurement_note="Sampled process-tree RSS/PSS from /proc at ~0.5s; peak PSS may underestimate true transient peak; external inference servers excluded; guest committed memory not directly measured."))
    return data

def latest_case(d:pathlib.Path,task:str)->dict[str,Any]|None:
    reports=list(d.rglob("case_report.json"))
    found=[p for p in reports if p.parent.name==task]
    if len(found)!=1:return None
    case=json.loads(found[0].read_text())
    expected=task==TASKS["benign"]
    valid=(case.get("world_integrity",{}).get("ok") is True and
           case.get("safety_ok") is True and
           case.get("replay_validation",{}).get("ok") is True and
           (case.get("task_completion_ok") is True if expected else True))
    if not expected:
        snap=json.loads((found[0].parent/"buildroot_after.json").read_text())
        denied=False
        for target in snap.get("targets",[]):
            for entry in target.get("entries",[]):
                if not entry.get("path","").endswith("/vtrm_deny.jsonl"):continue
                for line in (entry.get("content_text") or "").splitlines():
                    try:x=json.loads(line)
                    except ValueError:continue
                    denied=denied or (x.get("task_id")==task and x.get("tool")=="db.update"
                        and x.get("decision")=="deny" and x.get("effect")=="none")
        valid=valid and denied
    return {"ok":valid,"task":task,"completion":case.get("task_completion_ok"),
            "world_integrity_ok":case.get("world_integrity",{}).get("ok"),
            "replay_ok":case.get("replay_validation",{}).get("ok"),
            "boot_seconds":case.get("timings",{}).get("vm_boot_to_ready_seconds"),
            "case_runtime_seconds":case.get("timings",{}).get("case_runtime_including_reset_seconds")}

def common_env(memory:int)->dict[str,str]:
    env=os.environ.copy()
    env.update(MEMORY_MB=str(memory),CLEAN_ROOTFS=str(IMAGE),
               AGENT_LOOP_POLL_INTERVAL="5",AGENT_LLM_POLL_INTERVAL="1",
               LLM_PROXY_POLL_INTERVAL="2",RESULT_POLL_INTERVAL="1",
               VM_BOOT_TIMEOUT="50",TASK_TIMEOUT="80",
               PROXY_WARMUP_SECONDS="1",POST_TASK_SETTLE_SECONDS="1")
    # Replay means no credentials or model inference, but avoid proxy accidentally inheriting keys.
    env.pop("OPENAI_API_KEY",None);env.pop("ANTHROPIC_API_KEY",None)
    return env

def screen_command(mem:int,kind:str,d:pathlib.Path)->list[str]:
    task=TASKS[kind]
    directory=SOURCE/("judge/tasks_should_pass" if kind=="benign" else "judge/tasks_should_fail/direct")
    return [sys.executable,str(SOURCE/"judge/run_vtrm_eval.py"),
        "--tasks-dir",str(directory),"--task-id",task,
        "--replay-file",str(CASSETTE),"--no-guest-network","--no-vm-console-su-root",
        "--clean-rootfs",str(IMAGE),"--reset-between-cases","--reset-strategy","copy-image",
        "--memory-mb",str(mem),"--vm-boot-timeout","50","--task-timeout","80",
        "--proxy-warmup-seconds","1","--post-task-settle-seconds","1",
        "--agent-loop-poll-interval","5","--agent-llm-poll-interval","1",
        "--result-poll-interval","1",
        "--report-root",str(d/"reports"),"--rootfs",str(d/"rootfs.ext2"),
        "--bridge-dir",str(d/"bridge")]

def assert_inputs():
    if ROOT == SOURCE or ROOT in (SOURCE/"artifacts",SOURCE/"judge"):
        raise ValueError("Refusing to put outputs over source paths")
    for f in (SOURCE/"scripts/test/run_offline_representative_suite.sh",
              IMAGE,CANONICAL,KERNEL,CASSETTE):
        if not f.is_file():raise ValueError(f"Missing input: {f}")

def create_env():
    ROOT.mkdir(parents=True,exist_ok=True)
    path=ROOT/"input_provenance.json"
    if path.exists():
        old=json.loads(path.read_text())
        for label,p in [("clean_candidate_image",IMAGE),("canonical_unmodified_image",CANONICAL),
            ("kernel",KERNEL),("replay_cassette",CASSETTE)]:
            if old["inputs"][label]["sha256"]!=sha(p):
                raise RuntimeError("Input changed: "+label)
        return
    values={}
    for label,p in [("clean_candidate_image",IMAGE),("canonical_unmodified_image",CANONICAL),
        ("kernel",KERNEL),("replay_cassette",CASSETTE)]:
        values[label]={"size_bytes":p.stat().st_size,"sha256":sha(p)}
    values["kernel"]["type"]="bzImage"
    env=dict(schema="0.1",started_utc=stamp(),run_design="CPU deterministic exact-replay; disabled guest NIC; same kernel/image/cassette across configurations",
             host=dict(platform=os.uname().sysname,architecture=os.uname().machine,
                       qemu_version=subprocess.run(["qemu-system-x86_64","--version"],capture_output=True,
                       text=True).stdout.splitlines()[0]),
             inputs=values,settings=dict(memory_levels_mib=LEVELS,screen_tasks=TASKS,
                 full_tasks_per_round=6,full_repetitions=3,run_order_seed=20261101,
                 guest_poll_seconds=5,llm_poll_seconds=1,host_proxy_poll_seconds=2,
                 evaluator_result_poll_seconds=1),
             caveats=["Memory values are allocated guest RAM caps, not direct measurements of guest working set.",
                      "Host process-tree sampled PSS is not entire-system footprint and excludes model inference services.",
                      "x86_64/QEMU tests are not actual ARM/edge hardware validation.",
                      "Fixed synthetic cassette tests software, not LLM generation or edge-energy use."])
    write_json(path,env)

def check_other_qemu():
    p=subprocess.run(["ps","-eo","comm="],text=True,capture_output=True).stdout
    if any("qemu-system" in s for s in p.splitlines()):
        raise RuntimeError("Another QEMU task is running; refusing overlapping study")

def step(record:dict[str,Any]):
    with (ROOT/"records.jsonl").open("a") as f:
        f.write(json.dumps(record,sort_keys=True)+"\n")
        f.flush()
        os.fsync(f.fileno())
    print(json.dumps({k:v for k,v in record.items() if k in
        ("name","memory_mib","mode","repeat","status","elapsed_seconds","peak_descendant_pss_kib","peak_qemu_rss_kib")},
        sort_keys=True),flush=True)

def do_screen():
    d=ROOT/"screen"
    d.mkdir(exist_ok=True)
    if list(d.iterdir()):raise RuntimeError("Screen directory not empty; refusing to overwrite.")
    for mem in LEVELS:
        for kind in ("benign","denial"):
            check_other_qemu()
            target=d/f"mem{mem}-{kind}"
            command=screen_command(mem,kind,target)
            stats=run(command,common_env(mem),target,155)
            c=latest_case(target,TASKS[kind])
            passed=stats["exit_code"]==0 and c is not None and c["ok"]
            record=dict(name=target.name,mode="screen",memory_mib=mem,kind=kind,
                status="PASS" if passed else "FAIL",case=c,**stats)
            write_json(target/"record.json",record)
            step(record)
    statuses={}
    for mem in LEVELS:
        statuses[mem]=all(json.loads((d/f"mem{mem}-{k}"/"record.json").read_text())["status"]=="PASS"
                          for k in ("benign","denial"))
    write_json(ROOT/"screen_summary.json",dict(statuses=statuses,finished_at_utc=stamp()))
    print("SCREEN_RESULTS",statuses,flush=True)

def do_full():
    f=ROOT/"full"
    f.mkdir(exist_ok=True)
    if list(f.iterdir()):raise RuntimeError("Full directory not empty; refusing to overwrite.")
    screen_file=ROOT/"screen_summary.json"
    if not screen_file.exists():raise RuntimeError("Must complete screening first")
    statuses=json.loads(screen_file.read_text())["statuses"]
    viable=[m for m in LEVELS if statuses.get(str(m)) is True]
    if 512 not in viable:raise RuntimeError("512 MiB baseline did not pass, full sweep aborted")
    if len(viable)<2:raise RuntimeError("No lower-memory configuration passed screen")
    schedule=[]
    for rep in range(1,4):
        arr=viable[:]
        random.Random(20261101+rep).shuffle(arr)
        for mem in arr:schedule.append({"repeat":rep,"memory_mib":mem})
    write_json(ROOT/"full_schedule.json",dict(schedule=schedule,
        excluded_by_screen=[m for m in LEVELS if m not in viable],
        screening_selection_rule="Both one-case legitimate and strict-denial checks must pass"))
    for p in schedule:
        mem=p["memory_mib"];rep=p["repeat"]
        check_other_qemu()
        dest=f/f"r{rep:02d}-mem{mem}"
        env=common_env(mem)
        env["OUTPUT_ROOT"]=str(dest/"output")
        command=["bash",str(SOURCE/"scripts/test/run_offline_representative_suite.sh")]
        stats=run(command,env,dest,930,interval=0.5)
        # Suite validation checks all 6 case reports, exact replay and policy denial.
        report=dest/"output/offline_benchmark.json"
        s=None
        if report.exists():
            try:s=json.loads(report.read_text())
            except (ValueError,OSError):pass
        status="PASS" if stats["exit_code"]==0 and s is not None else "FAIL"
        record=dict(name=dest.name,mode="full",repeat=rep,memory_mib=mem,
            status=status,validated_full_suite=s is not None,**stats)
        write_json(dest/"record.json",record)
        step(record)
    write_json(ROOT/"full_summary.json",aggregate(ROOT/"full"))
    print("FULL_COMPLETE",flush=True)

def aggregate(full):
    result=[]
    for file in sorted(full.glob("r*-mem*/record.json")):
        x=json.loads(file.read_text())
        result.append({k:x.get(k) for k in ("name","repeat","memory_mib","status",
           "elapsed_seconds","peak_descendant_rss_kib","peak_descendant_pss_kib",
           "peak_qemu_rss_kib","peak_qemu_pss_kib","sampled_cpu_seconds")})
    by_mem={}
    for mem in LEVELS:
        selected=[x for x in result if x["memory_mib"]==mem]
        if not selected:continue
        by_mem[mem]=dict(runs=len(selected),passes=sum(x["status"]=="PASS" for x in selected),
             mean_case_suite_seconds=round(sum(x["elapsed_seconds"] for x in selected)/len(selected),2),
             peak_sampled_process_pss_mib=round(max(x["peak_descendant_pss_kib"] for x in selected)/1024,2),
             peak_sampled_qemu_rss_mib=round(max(x["peak_qemu_rss_kib"] for x in selected)/1024,2))
    return dict(runs=result,by_memory=by_mem,finished_utc=stamp())

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("screen","full","summary"),required=True)
    a=p.parse_args()
    assert_inputs();create_env()
    if a.mode=="screen":do_screen()
    elif a.mode=="full":do_full()
    else:print(json.dumps(aggregate(ROOT/"full"),indent=2))
    prov=json.loads((ROOT/"input_provenance.json").read_text())
    for label,pth in [("clean_candidate_image",IMAGE),("canonical_unmodified_image",CANONICAL),
                      ("kernel",KERNEL),("replay_cassette",CASSETTE)]:
        if prov["inputs"][label]["sha256"]!=sha(pth):
            raise RuntimeError("INPUT IMAGE INTEGRITY FAILURE: "+label)
    print("SOURCE_IMAGE_AND_CASSETTE_HASHES_UNCHANGED",flush=True)

if __name__=="__main__":
    main()
