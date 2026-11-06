"""Temporary loopback-only Adaption API connection. No credential persistence.

Created before the sprint, 2026-11-05. Only read-only upstream requests supported.
The key is held in this process's memory, never returned in responses or logs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import secrets
import threading
import time
from urllib import error, parse, request

API_ROOT = "https://api.prod.adaptionlabs.ai/api/v1"
READ_PATHS = {"models": "/models", "training_models": "/autoscientist/models",
              "datasets": "/datasets", "runs": "/autoscientist"}
PAGE = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Connect Adaption — Swarm Hackathon</title>
<style>body{background:#f4f5f7;color:#17202a;font:17px/1.55 system-ui;margin:0;padding:40px 20px}
main{max-width:650px;margin:24px auto;background:white;padding:32px;border:1px solid #d9dee5;border-radius:12px}
h1{font-size:28px;line-height:1.2}label{display:block;font-weight:650;margin-top:24px}
input{display:block;box-sizing:border-box;width:100%;font:inherit;padding:12px;margin:8px 0 16px;border:1px solid #8b97a4;border-radius:6px}
button{background:#175a42;color:white;border:0;border-radius:6px;padding:12px 18px;font:inherit;cursor:pointer}
button:disabled{opacity:.6}a{color:#175a42}.note{color:#52606d;font-size:14px}
#status{padding-top:18px;font-weight:600}code{font-size:14px}</style>
<main><p class="note">Swarm Alignment Hackathon · Inioluwa Atanda</p>
<h1>Connect your funded Adaption account</h1>
<p>This connects the research runtime directly to Adaption. No ChatGPT plugin is used.</p>
<ol><li>Open <a href="https://adaptionlabs.ai/app/settings?tab=api_keys" target="_blank" rel="noopener noreferrer">Adaption API keys</a> in your own browser.</li>
<li>Sign in to the account where you saw 1,000 credits.</li>
<li>Create a key named <strong>Swarm Hackathon</strong>, then paste it below.</li></ol>
<form id="form" autocomplete="off"><label for="key">Adaption API key</label>
<input id="key" name="api_key" type="password" autocomplete="off" spellcheck="false" required maxlength="4096">
<button id="connect" type="submit">Connect and check access</button></form>
<p id="status" role="status" aria-live="polite"></p>
<p class="note">The key is sent to this project's local connection process. It is held only in that process's memory, never written to project files or returned to chat. Closing the preview does not disconnect it; the process expires after its stated lifetime. This setup can only list models and other read-only resources. It cannot launch training or generate model responses.</p>
<p class="note">Do not paste the key into the chat. You can revoke it later in Adaption's API key settings.</p>
</main><script>
document.getElementById('form').addEventListener('submit',async(e)=>{
e.preventDefault();const field=document.getElementById('key'),button=document.getElementById('connect'),status=document.getElementById('status');
const key=field.value;field.value='';button.disabled=true;status.textContent='Checking read-only access…';
try{const response=await fetch('/connect',{method:'POST',headers:{'Content-Type':'application/json','X-Connection-CSRF':'__CSRF__'},body:JSON.stringify({api_key:key})});
const result=await response.json();status.textContent=result.message;if(result.connected){document.getElementById('form').hidden=true;}}
catch{status.textContent='Connection check failed. No training job was launched.';}finally{button.disabled=false;}});
</script></html>"""


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def api_get(key: str, path: str) -> dict:
    req = request.Request(API_ROOT + path, headers={"Authorization": "Bearer " + key,
                                                  "Accept": "application/json"}, method="GET")
    opener = request.build_opener(NoRedirect())
    with opener.open(req, timeout=25) as response:
        raw = response.read(2_000_000)
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("unexpected catalogue format")
    return result


class ConnectionServer(ThreadingHTTPServer):
    def __init__(self, address, ttl):
        super().__init__(address, Handler)
        self.csrf = secrets.token_urlsafe(32)
        self.key: str | None = None
        self.model_count = 0
        self.deadline = time.monotonic() + ttl
        self.lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    server: ConnectionServer

    def log_message(self, *_args):
        pass

    def respond(self, status, payload, content_type="application/json; charset=utf-8"):
        body = payload.encode() if isinstance(payload, str) else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = parse.urlsplit(self.path).path
        if time.monotonic() > self.server.deadline:
            self.respond(410, {"message": "Connection session expired. Ask the assistant to reopen it."})
        elif path == "/":
            self.respond(200, PAGE.replace("__CSRF__", self.server.csrf), "text/html; charset=utf-8")
        elif path == "/status":
            self.respond(200, {"connected": self.server.key is not None,
                               "model_count": self.server.model_count, "mode": "read_only",
                               "credential_persisted": False})
        else:
            self.respond(404, {"message": "Not found"})

    def do_POST(self):
        if time.monotonic() > self.server.deadline:
            return self.respond(410, {"message": "Session expired."})
        if not hmac.compare_digest(self.headers.get("X-Connection-CSRF", ""), self.server.csrf):
            return self.respond(403, {"message": "Open the connection form in this preview."})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length < 8192:
                return self.respond(400, {"message": "Invalid request size."})
            data = json.loads(self.rfile.read(length))
            if not isinstance(data, dict):
                raise ValueError()
        except (ValueError, TypeError):
            return self.respond(400, {"message": "Invalid request."})
        path = parse.urlsplit(self.path).path
        if path == "/connect":
            key = data.pop("api_key", "")
            if not isinstance(key, str) or not key.strip() or not key.isascii() or len(key) > 4096 or any(c.isspace() for c in key.strip()):
                return self.respond(400, {"message": "Paste a valid Adaption API key."})
            key = key.strip()
            try:
                result = api_get(key, READ_PATHS["models"])
                models = result.get("data")
                if not isinstance(models, list):
                    raise ValueError()
                with self.server.lock:
                    self.server.key = key
                    self.server.model_count = len(models)
            except error.HTTPError as exc:
                # Do not echo upstream bodies or request headers: either can contain secrets.
                return self.respond(400, {"message": f"Adaption returned HTTP {exc.code}. Check key access and organization; no paid job was started."})
            except Exception:
                return self.respond(400, {"message": "Could not verify read-only model access. No paid job was started."})
            return self.respond(200, {"connected": True,
                                      "message": f"Connected. {len(models)} model entries are accessible. No credits were spent on inference or training. You can return to the chat."})
        if path == "/read":
            operation = data.get("operation")
            if operation not in READ_PATHS:
                return self.respond(400, {"message": "Only listed read-only operations are supported."})
            key = self.server.key
            if not key:
                return self.respond(409, {"message": "Adaption is not connected."})
            try:
                result = api_get(key, READ_PATHS[operation])
            except error.HTTPError as exc:
                return self.respond(400, {"message": f"Adaption returned HTTP {exc.code}."})
            except Exception:
                return self.respond(400, {"message": "Adaption read failed."})
            return self.respond(200, result)
        self.respond(404, {"message": "Not found"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--ttl-minutes", type=int, default=60)
    args = parser.parse_args()
    if not 1 <= args.ttl_minutes <= 120:
        parser.error("lifetime must be 1–120 minutes")
    server = ConnectionServer(("127.0.0.1", args.port), args.ttl_minutes * 60)
    expiry = threading.Timer(args.ttl_minutes * 60, server.shutdown)
    expiry.daemon = True
    expiry.start()
    print(f"Adaption connection form ready on loopback port {args.port}; lifetime {args.ttl_minutes} minutes; no credential persistence.", flush=True)
    try:
        server.serve_forever()
    finally:
        server.key = None
        server.server_close()


if __name__ == "__main__":
    main()
