"""Immediate detached extension launch; key in memory/anonymous pipe only."""
from datetime import datetime,timezone
import getpass
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sprint-report-load-20261106'


def main():
    p=OUT/'worker-status.json'
    if p.exists():
        x=json.loads(p.read_text())
        if x.get('state')=='running':
            try:os.kill(x['pid'],0)
            except ProcessLookupError:pass
            else:raise SystemExit('Worker already running; no duplicate started')
    key=getpass.getpass('Adaption API key (hidden; not saved): ')
    if not key:raise SystemExit('No key supplied')
    OUT.mkdir(parents=True,exist_ok=True)
    readfd,writefd=os.pipe()
    with (OUT/'worker.log').open('ab',buffering=0) as log:
        child=subprocess.Popen([sys.executable,'-u',str(ROOT/'scripts/run_report_load.py'),'--key-fd',str(readfd)],
                               cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                               pass_fds=(readfd,),start_new_session=True)
    os.close(readfd);os.write(writefd,key.encode());os.close(writefd);key=None
    state={'pid':child.pid,'launched_utc':datetime.now(timezone.utc).isoformat(),
           'state':'launched','scope':'bounded during-sprint extension','automatic_chat_notification':False}
    (OUT/'background-start.json').write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(state),flush=True)


if __name__=='__main__':main()
