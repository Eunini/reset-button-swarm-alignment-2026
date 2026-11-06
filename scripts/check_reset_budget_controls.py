"""Existing-style quota baselines, using saved judgments only (no API calls).

Fixed quotas are prespecified controls, not proposed novel mechanisms.
"""
import argparse
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from reset_button import make_scenario
from run_reset_study import honest_control


def quota_replay(reports, verdicts, budget, quota, identity, scope, restart_roots=("reporter-root",)):
    used = defaultdict(int)
    stopped, logs = set(), []
    calls = 0
    for report in reports:
        actor = (report["root"] + "/" + report["report_id"] if identity == "restart" and
                 report["root"] in restart_roots else report["actor"])
        key = report["root"] if scope == "root" else actor
        outcome = "already_stopped" if report["target"] in stopped else "filtered"
        if report["target"] not in stopped and used[key] < quota and (budget is None or calls < budget):
            used[key] += 1; calls += 1
            verdict = verdicts.get(report["report_id"])
            outcome = "stop" if verdict is True else "reject" if verdict is False else "uncertain"
            if verdict is True:
                stopped.add(report["target"])
        logs.append({"report_id": report["report_id"], "outcome": outcome})
    bad = {r["target"] for r in reports if r["true_violation"]}
    safe = {r["target"] for r in reports if not r["true_violation"]}
    return {"calls": calls, "true_detected": len(bad & stopped), "true_total": len(bad),
            "false_stops": len(safe & stopped), "logs": logs}


def run(path):
    summary = json.loads((path / "summary-live.json").read_text())
    cases = json.loads((path / "executed-cases.json").read_text())
    grading = json.loads((path / "grading.json").read_text())
    streams = defaultdict(list)
    for report in cases:
        streams[report["campaign"], report["seed"]].append(report)
    verdict_sets = defaultdict(dict)
    for r in grading:
        verdict_sets[r["model"], r["campaign"], r["seed"]][r["report_id"]] = r["verdict"]
    rows = []
    for (model, campaign, seed), verdicts in verdict_sets.items():
        for scope in ("identity", "root"):
            for quota in (1, 2, 4):
                for budget in (4, 8, 12, 16, None):
                    for identity in ("persistent", "restart"):
                        result = quota_replay(streams[campaign, seed], verdicts, budget, quota, identity, scope)
                        rows.append({"verifier": model, "campaign": campaign, "seed": seed,
                                     "scope": scope, "quota": quota, "budget": budget,
                                     "identity": identity, **result})
    controls = []
    for seed in sorted({r["seed"] for r in cases}):
        scenario = honest_control(seed)
        reports = [asdict(r) for r in scenario["reports"]]
        verdicts = {r["report_id"]: r["true_violation"] for r in reports}
        for scope in ("identity", "root"):
            for quota in (1, 2, 4):
                result = quota_replay(reports, verdicts, None, quota, "restart", scope, ("honest-root",))
                controls.append({"seed": seed, "scope": scope, "quota": quota, **result})
    output = {"stage": summary["stage"], "rows": rows, "honest_control": controls,
              "interpretation": "A matching simple quota limits novelty of the reputation repair; report it explicitly.",
              "direct_enforcement_diagnostic": "The typed executor can block heldout-fit actions exactly, requiring zero LLM verification calls. This is preferable for this specific policy."}
    (path / "budget-controls.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"path": str(path / "budget-controls.json"), "replays": len(rows), "new_api_calls": 0}))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/reset-development-v2-20261105")
    args = parser.parse_args()
    run(ROOT / args.results)
