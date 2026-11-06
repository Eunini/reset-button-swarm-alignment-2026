"""One-command guarded sprint pipeline; never schedules a future run."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
START = datetime(2026, 11, 5, 23, 0, tzinfo=timezone.utc)  # Friday 00:00 Europe/Berlin


def main():
    classification = ROOT / "sources/reset-study-classification-20261106.json"
    if classification.exists() and json.loads(classification.read_text()).get("all_completed_study_before_opening"):
        raise SystemExit("The completed protocol is preexisting validation. A substantive extension after the official countdown opening is needed; rerunning this cached study does not make its findings new.")
    if datetime.now(timezone.utc) < START:
        raise SystemExit("Sprint pipeline uses Friday November 6 in the supplied Europe/Berlin workspace timezone.")
    development = ROOT / "results/reset-development-v2-20261105/analysis.json"
    if not development.exists():
        raise SystemExit("Analyze and review the development run before launching the main study.")
    data = json.loads(development.read_text())
    for model in data["calibration"]:
        if (model["usable"] != model["unique_requests"] or model["usable"] < 20
                or model["correct"] / model["usable"] < .95 or model["false_positive"] > 0):
            raise SystemExit("Development competence/availability gate failed; inspect the records first.")
    if not all(row["valid"] for row in data["campaign_status"]):
        raise SystemExit("Development campaign format gate failed; inspect the records first.")
    def run(args):
        subprocess.run(args, cwd=ROOT, check=True)
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    run([sys.executable, "scripts/run_reset_study.py", "--stage", "main", "--live"])
    results = "results/reset-main-20261106"
    run([sys.executable, "scripts/analyze_reset_study.py", "--results", results])
    run([sys.executable, "scripts/check_reset_budget_controls.py", "--results", results])
    run([sys.executable, "scripts/build_reset_report.py", "--results", results])
    profile = "file:///tmp/reset-lo-" + uuid.uuid4().hex
    run(["libreoffice", "-env:UserInstallation=" + profile, "--headless", "--convert-to", "pdf",
         "--outdir", "report", "report/reset-button-main-report-draft.docx"])
    print("Main-study draft produced. Inspect receipts, inference intervals, claims and every PDF page before submission.")


if __name__ == "__main__":
    main()
