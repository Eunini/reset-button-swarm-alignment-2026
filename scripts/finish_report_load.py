"""Wait for this finite experiment, then analyze and draft its report.

No credentials or inference calls; no chat notification or submission.
"""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sprint-report-load-20261106'


def main():
    state={'pid':os.getpid(),'state':'waiting_for_data','started_utc':datetime.now(timezone.utc).isoformat(),'submitted':False}
    def save():
        state['heartbeat_utc']=datetime.now(timezone.utc).isoformat()
        (OUT/'report-worker-status.json').write_text(json.dumps(state,indent=2)+'\n')
    save();deadline=time.monotonic()+7200
    try:
        while time.monotonic()<deadline:
            worker=json.loads((OUT/'worker-status.json').read_text())
            if worker['state']=='completed':break
            if worker['state']=='failed':raise RuntimeError('Experiment worker failed')
            save();time.sleep(15)
        else:raise TimeoutError('Finite wait elapsed')
        state['state']='analyzing';save()
        for script in ('analyze_report_load.py','build_report_load_report.py'):
            subprocess.run([sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT,check=True)
        state['state']='rendering';save()
        subprocess.run(['libreoffice','-env:UserInstallation=file:///tmp/report-load-'+uuid.uuid4().hex,
                        '--headless','--convert-to','pdf','--outdir','report','report/reset-button-sprint-report.docx'],cwd=ROOT,check=True)
        import pymupdf
        pdf=ROOT/'report/reset-button-sprint-report.pdf';d=pymupdf.open(pdf)
        text=' '.join(' '.join(p.get_text() for p in d).split())
        metadata=json.loads((ROOT/'report/report-load-metadata.json').read_text())
        main_pages=next(i for i,p in enumerate(d) if 'References\n[1]' in p.get_text())
        plan=json.loads((ROOT/'sources/sprint-report-load-plan-20261106.json').read_text())
        sources={**plan['source_sha256'],**plan['preexisting_source_sha256']}
        checks={'source_hashes_unchanged':all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in sources.items()),
                'main_pages_4_to_8':4<=main_pages<=8,'abstract_words_150_to_250':150<=metadata['abstract_words']<=250,
                'required_appendix':'Limitations and Dual-Use / Ethical Considerations' in text,
                'ai_use_disclosed':'LLM Usage Statement' in text,'prior_work_disclosed':'preexisting preparation' in text,
                'no_empty_pages':all(len(p.get_text())>300 for p in d),'no_author_placeholder':'affiliation not supplied' not in text,
                'within_25MB':pdf.stat().st_size<25*1024*1024,
                'text_inside_page':all(w[0]>=8 and w[1]>=8 and w[2]<=p.rect.width-8 and w[3]<=p.rect.height-8 for p in d for w in p.get_text('words'))}
        q={'checked_utc':datetime.now(timezone.utc).isoformat(),'checks':checks,'passed':all(checks.values()),
           'main_pages':main_pages,'total_pages':len(d),'abstract_words':metadata['abstract_words'],
           'visual_review_pending':True,'human_review_claimed':False,'submitted':False}
        (ROOT/'report/report-load-checks.json').write_text(json.dumps(q,indent=2)+'\n')
        for i,p in enumerate(d):p.get_pixmap(matrix=pymupdf.Matrix(.9,.9)).save(str(ROOT/f'report/report-load-page-{i+1}.png'))
        state.update({'state':'draft_ready' if q['passed'] else 'checks_failed','finished_utc':datetime.now(timezone.utc).isoformat(),
                      'pdf':'report/reset-button-sprint-report.pdf','visual_review_pending':True})
    except BaseException as exc:
        state.update({'state':'failed','error_type':type(exc).__name__})
        print(json.dumps(state),flush=True)
    save()


if __name__=='__main__':main()
