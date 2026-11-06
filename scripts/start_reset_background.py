"""Start an immediate detached worker with a hidden key and durable status/log."""
from datetime import datetime, timezone
import getpass
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/reset-main-20261106"


def main():
    status_path = OUT / "worker-status.json"
    if status_path.exists():
        status = json.loads(status_path.read_text())
        if status.get("state") == "running":
            try:
                os.kill(status["pid"], 0)
            except ProcessLookupError:
                pass
            else:
                raise SystemExit("An existing worker is still running; no duplicate started.")
    key = getpass.getpass("Adaption API key (hidden; anonymous pipe only): ")
    if not key:
        raise SystemExit("No key supplied")
    OUT.mkdir(parents=True, exist_ok=True)
    read_fd, write_fd = os.pipe()
    with (OUT / "worker.log").open("ab", buffering=0) as log:
        process = subprocess.Popen([sys.executable, "-u", str(ROOT / "scripts/reset_background_worker.py"), str(read_fd)],
                                   cwd=ROOT, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                   pass_fds=(read_fd,), start_new_session=True)
    os.close(read_fd)
    os.write(write_fd, key.encode())
    os.close(write_fd)
    key = None
    record = {"pid": process.pid, "started_utc": datetime.now(timezone.utc).isoformat(),
              "mode": "immediate detached finite continuation", "automatic_chat_notification": False,
              "note": "Uses the frozen runner and existing request cache; no recorded request is resent."}
    (OUT / "background-start.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2), flush=True)


if __name__ == "__main__":
    main()
