"""Documented SSE transport for long model responses; never persists auth headers."""
from collections import Counter
from datetime import datetime,timezone
import json
import time
from urllib import request,error
from run_reset_study import NoRedirect,text_output
from reset_button import digest


def invoke_stream(key,payload):
    started=time.monotonic()
    result={'request_hash':digest(payload),'request':payload,'started_utc':datetime.now(timezone.utc).isoformat()}
    req=request.Request('https://api.prod.adaptionlabs.ai/api/v1/responses',method='POST',data=json.dumps(payload).encode(),
                        headers={'Content-Type':'application/json','Accept':'text/event-stream','Authorization':'Bearer '+key})
    events=[];final=None;total=0
    try:
        with request.build_opener(NoRedirect()).open(req,timeout=180) as response:
            result['http_status']=response.status
            if 'text/event-stream' not in response.headers.get('Content-Type',''):
                final=json.loads(response.read(3000000))
            else:
                for line in response:
                    total+=len(line)
                    if total>10000000:raise ValueError('stream size cap')
                    if not line.startswith(b'data:'):continue
                    raw=line[5:].strip()
                    if not raw or raw==b'[DONE]':continue
                    event=json.loads(raw);events.append(event)
                    if event.get('type') in ('response.completed','response.incomplete','response.failed'):
                        final=event.get('response')
        if not isinstance(final,dict):
            result.update({'error':'stream_missing_final_response','text':''})
        else:
            result.update({'response':final,'text':text_output(final),
                           'error':None if final.get('status')=='completed' else 'incomplete_output'})
    except error.HTTPError as exc:
        result.update({'http_status':exc.code,'error':'http_error','text':''})
    except Exception as exc:
        result.update({'http_status':result.get('http_status'),'error':type(exc).__name__,'text':''})
    result.update({'stream_events':events,'stream_event_counts':dict(Counter(e.get('type','unknown') for e in events)),
                   'elapsed_seconds':round(time.monotonic()-started,3)})
    return result
