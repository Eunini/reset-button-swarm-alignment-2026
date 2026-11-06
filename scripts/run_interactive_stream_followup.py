"""Explicit calibration follow-up: same interactive protocol, 16,384 output tokens.

Original 4,096-token failures remain immutable. No model/workload selection or
prompt change, no automatic retries, no efficacy/model-ranking claim.
"""
from collections import Counter
from datetime import datetime,timezone
import argparse
import getpass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import run_report_load as original
from run_reset_study import RATES
from adaption_stream import invoke_stream

OUT=ROOT/'results/sprint-interactive-v3-20261106'
PLAN=ROOT/'sources/sprint-interactive-stream-plan-20261106.json'


def freeze():
    files=[Path(__file__).resolve(),ROOT/'scripts/adaption_stream.py',ROOT/'scripts/run_report_load.py',ROOT/'src/report_load.py',ROOT/'src/reset_button.py',ROOT/'scripts/run_reset_study.py']
    p={'frozen_utc':datetime.now(timezone.utc).isoformat(),'stage':'during-sprint calibration follow-up',
       'reason':'Original interactive calibration had 59 truncated outputs; the non-streaming 16384-token follow-up stopped on its first request with HTTP 504 after 60 seconds. Preserve both runs and test the documented SSE transport before proceeding.',
       'change':'Use stream=true and 16384 output tokens uniformly; same prompts, cases, checker, turns and grading. Stop immediately on incomplete or invalid actions rather than issuing a batch of failures.',
       'source_protocol':'sources/sprint-report-load-plan-20261106.json','expected_requests':96,'max_requests':96,'max_projected_credits':3,
       'automatic_retries':0,'same_cases_reused':True,'held_out_claim':False,'transport_reference':'https://docs.adaptionlabs.ai/api/resources/responses/methods/create',
       'interpretation':'Calibration on previously used cases; not a new held-out efficacy study. All failures retained and reported.',
       'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}}
    if PLAN.exists():
        old=json.loads(PLAN.read_text())
        if old['source_sha256']!=p['source_sha256']:raise ValueError('Frozen follow-up source changed')
        return old
    PLAN.write_text(json.dumps(p,indent=2)+'\n');return p


def worker(key):
    plan=freeze();OUT.mkdir(parents=True,exist_ok=True)
    state={'pid':os.getpid(),'state':'running','phase':'interactive_calibration','started_utc':datetime.now(timezone.utc).isoformat(),'submitted':False}
    def save():
        state['updated_utc']=datetime.now(timezone.utc).isoformat();state['recorded_requests']=len(list((OUT/'responses').glob('*.json')))
        temp=OUT/'worker-status.tmp';temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(OUT/'worker-status.json')
    save()
    original.OUT=OUT
    original.invoke=invoke_stream
    class BudgetClient(original.Client):
        def call(self,payload):
            value=super().call({**payload,'max_output_tokens':16384,'stream':True});save()
            if value.get('error'):raise RuntimeError('Streaming calibration error; stopped before more calls')
            try:
                action=json.loads(value['text'])
                if set(action)!={'restart','target','reason'} or type(action['restart']) is not bool or not isinstance(action['reason'],str) or not 1<=len(action['reason'])<=1000:raise ValueError()
            except (ValueError,KeyError,TypeError):raise RuntimeError('Invalid action; stopped before more calls')
            return value
    client=BudgetClient(key,plan)
    try:
        episodes=original.interactive(client)
        usage={'recorded_requests':len(client.records),'input_tokens':0,'output_tokens':0,'estimated_credits':0.0,'provider_reported_cost':0.0}
        for r in client.records.values():
            u=r.get('response',{}).get('usage',{});it=u.get('input_tokens',0);ot=u.get('output_tokens',0);ir,outr=RATES[r['request']['model']]
            usage['input_tokens']+=it;usage['output_tokens']+=ot;usage['estimated_credits']+=(it*ir+ot*outr)/1e6;usage['provider_reported_cost']+=u.get('cost',0) or 0
        summary={'stage':'interactive calibration follow-up','started_utc':state['started_utc'],'finished_utc':datetime.now(timezone.utc).isoformat(),
                 'episodes':len(episodes),'output_token_limit':16384,'stream':True,'usage':usage,
                 'completion_errors':dict(Counter(r.get('error') for r in client.records.values() if r.get('error'))),
                 'invalid_actions':sum(e['invalid_actions'] for e in episodes),'original_failures_preserved':True,'held_out_claim':False}
        (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
        state.update({'state':'completed','finished_utc':summary['finished_utc']})
    except BaseException as exc:
        state.update({'state':'failed','error_type':type(exc).__name__});print(json.dumps(state),flush=True)
    save()


def launch():
    freeze();OUT.mkdir(parents=True,exist_ok=True)
    p=OUT/'worker-status.json'
    if p.exists():
        s=json.loads(p.read_text())
        if s.get('state')=='running':
            try:os.kill(s['pid'],0)
            except ProcessLookupError:pass
            else:raise SystemExit('Existing worker alive; no duplicate started')
    key=getpass.getpass('Adaption API key (hidden; anonymous pipe only): ')
    if not key:raise SystemExit('No key supplied')
    readfd,writefd=os.pipe()
    with (OUT/'worker.log').open('ab',buffering=0) as log:
        child=subprocess.Popen([sys.executable,'-u',str(Path(__file__).resolve()),'--key-fd',str(readfd)],cwd=ROOT,
                               stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,pass_fds=(readfd,),start_new_session=True)
    os.close(readfd);os.write(writefd,key.encode());os.close(writefd);key=None
    print(json.dumps({'pid':child.pid,'launched_utc':datetime.now(timezone.utc).isoformat(),'scope':'explicit 96-request output-budget follow-up'}))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare-only',action='store_true');p.add_argument('--launch',action='store_true');p.add_argument('--key-fd',type=int);args=p.parse_args()
    if args.prepare_only:print(json.dumps(freeze(),indent=2))
    elif args.launch:launch()
    else:
        with os.fdopen(args.key_fd) as pipe:key=pipe.read().strip()
        worker(key)
