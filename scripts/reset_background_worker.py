"""Durable, finite main-study worker; credentials arrive over an anonymous pipe.

The frozen scientific runner is unchanged. This wrapper supplies its hidden-input
provider in memory, records worker lifecycle, and runs saved-data analysis after
the inference phase. It does not schedule a future assistant conversation.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import uuid

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/reset-main-20261106"
sys.path.insert(0, str(ROOT / "scripts"))


def main():
    key_fd = int(sys.argv[1])
    with os.fdopen(key_fd) as pipe:
        key = pipe.read().strip()
    if not key:
        raise SystemExit("No in-memory API credential supplied")
    OUT.mkdir(parents=True, exist_ok=True)
    os.chdir(ROOT)
    state = {"pid": os.getpid(), "started_utc": datetime.now(timezone.utc).isoformat(),
             "state": "running", "phase": "inference", "scientific_plan": "sources/reset-study-plan-20261106-v4.json",
             "credential_storage": "process memory only; anonymous input pipe closed"}
    stop = threading.Event()

    def save():
        value = {**state, "heartbeat_utc": datetime.now(timezone.utc).isoformat(),
                 "recorded_requests": len(list((OUT / "responses").glob("*.json")))}
        temp = OUT / "worker-status.tmp"
        temp.write_text(json.dumps(value, indent=2) + "\n")
        temp.replace(OUT / "worker-status.json")

    def heartbeat():
        while not stop.wait(30):
            save()

    save()
    thread = threading.Thread(target=heartbeat, daemon=True)
    thread.start()
    try:
        import run_reset_study as study
        # Replace only the interactive secret-input provider. Request generation,
        # frozen source checks, caching, budgets and analysis rules are unchanged.
        study.getpass.getpass = lambda _prompt: key
        study.run("main", True, False)
        key = None
        state["phase"] = "analysis"
        save()
        for script in ("analyze_reset_study.py", "check_reset_budget_controls.py", "build_reset_report.py"):
            subprocess.run([sys.executable, str(ROOT / "scripts" / script), "--results",
                            "results/reset-main-20261106"], cwd=ROOT, check=True)
        state["phase"] = "pdf"
        save()
        subprocess.run(["libreoffice", "-env:UserInstallation=file:///tmp/reset-main-" + uuid.uuid4().hex,
                        "--headless", "--convert-to", "pdf", "--outdir", "report",
                        "report/reset-button-main-report-draft.docx"], cwd=ROOT, check=True)
        state.update({"state": "completed", "phase": "draft_ready", "finished_utc": datetime.now(timezone.utc).isoformat(),
                      "submission_sent": False, "draft_review_required": True})
    except BaseException as exc:
        # Record exception type and source location without arbitrary exception
        # text, headers, locals or credentials.
        frames = []
        tb = exc.__traceback__
        while tb:
            frames.append({"file": Path(tb.tb_frame.f_code.co_filename).name, "line": tb.tb_lineno})
            tb = tb.tb_next
        state.update({"state": "failed", "error_type": type(exc).__name__, "frames": frames,
                      "finished_utc": datetime.now(timezone.utc).isoformat()})
        print(json.dumps({"worker_failed": type(exc).__name__, "frames": frames}), flush=True)
    finally:
        stop.set()
        thread.join(timeout=2)
        save()


if __name__ == "__main__":
    main()
