"""Inspect the temporary local connection without reading or displaying its key."""
import json
import re
from urllib import request, error

ROOT = "http://127.0.0.1:8765"

try:
    with request.urlopen(ROOT + "/status", timeout=5) as response:
        status = json.load(response)
    print(json.dumps(status))
    if not status.get("connected"):
        raise SystemExit("Waiting for the user to enter the key on the connection page.")
    with request.urlopen(ROOT + "/", timeout=5) as response:
        page = response.read().decode()
    csrf = re.search(r"'X-Connection-CSRF':'([^']+)'", page).group(1)
    payload = json.dumps({"operation": "models"}).encode()
    req = request.Request(ROOT + "/read", data=payload,
                          headers={"Content-Type": "application/json", "X-Connection-CSRF": csrf},
                          method="POST")
    with request.urlopen(req, timeout=35) as response:
        catalog = json.load(response)
    # Display only model identifiers and public display names, not arbitrary response fields.
    print(json.dumps({"models": [{"id": m.get("id"), "display_name": m.get("display_name")}
                                 for m in catalog.get("data", []) if isinstance(m, dict)]}, indent=2))
except (error.URLError, OSError):
    raise SystemExit("Connection is unavailable or expired; reopen the temporary connection service.")
