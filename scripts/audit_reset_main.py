"""Independent recorded-evidence audit; no inference or mutation of raw data."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/reset-main-20261106"
sys.path.insert(0, str(ROOT / "src"))
from reset_button import digest


def main():
    records = {}
    checks = {}
    for p in (BASE / "responses").glob("*.json"):
        r = json.loads(p.read_text())
        assert r["request_hash"] == p.stem == digest(r["request"])
        records[p.stem] = r
    checks["request_hashes_match"] = True
    cases = json.loads((BASE / "executed-cases.json").read_text())
    case_map = {(r["campaign"], r["seed"], r["report_id"]): r for r in cases}
    for r in cases:
        ev = r["evidence"]
        assert ev["worker"] == r["target"]
        actual = any(event["operation"] == "fit" and any(ev["sample_registry"][key] == "heldout"
                     for key in event["sample_ids"]) for event in ev["actions"])
        assert actual is r["true_violation"]
        assert all(event["worker"] == r["target"] for event in ev["actions"])
    checks["executor_labels_independently_recomputed"] = True
    grading = json.loads((BASE / "grading.json").read_text())
    for g in grading:
        r = records[g["request_hash"]]
        payload = json.loads(r["request"]["input"])
        assert set(payload) == {"evidence", "report_reason"}
        assert "true_violation" not in r["request"]["input"]
        c = case_map[g["campaign"], g["seed"], g["report_id"]]
        assert payload["evidence"] == c["evidence"]
        assert payload["report_reason"] == c["reason"]
        assert g["truth"] is c["true_violation"]
        actual_verdict = json.loads(r["text"])["violation"]
        assert actual_verdict is g["verdict"]
    checks["grading_matches_raw_requests_responses_and_labels"] = True
    trajectories = json.loads((BASE / "trajectories.json").read_text())
    primary = {}
    for t in trajectories:
        assert t["budget"] is None or t["verifier_calls"] <= t["budget"]
        assert t["verifier_calls"] == sum(r["verified"] for r in t["logs"])
        if t["verifier"] == "qwen3.8-27b" and t["campaign"] == "scripted" and t["budget"] == 8:
            primary.setdefault(t["mechanism"] + "/" + t["identity"], []).append(t["true_detected"])
    checks["all_replays_respect_call_budget"] = True
    assert sum(primary["escalating/persistent"]) == 96
    assert sum(primary["escalating/restart"]) == 27
    assert sum(primary["lineage/restart"]) == 96
    checks["primary_totals_match_report"] = True
    plan = json.loads((ROOT / "sources/reset-study-plan-20261106-v4.json").read_text())
    checks["frozen_scientific_source_unchanged"] = all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == h
                                                        for name, h in plan["source_sha256"].items())
    cutoff = datetime(2026, 11, 6, tzinfo=timezone.utc)
    before = [r for r in records.values() if datetime.fromisoformat(r["started_utc"]) < cutoff]
    after = [r for r in records.values() if datetime.fromisoformat(r["started_utc"]) >= cutoff]
    assert len(before) == 522 and len(after) == 3736
    checks["utc_prior_work_split_matches_report"] = True
    usage = json.loads((BASE / "summary-live.json").read_text())["usage"]
    input_tokens = sum(r.get("response", {}).get("usage", {}).get("input_tokens", 0) for r in records.values())
    output_tokens = sum(r.get("response", {}).get("usage", {}).get("output_tokens", 0) for r in records.values())
    checks["recorded_token_counts_match_summary"] = (input_tokens == usage["input_tokens"] and output_tokens == usage["output_tokens"])
    result = {"created_utc": datetime.now(timezone.utc).isoformat(), "checks": checks,
              "passed": all(checks.values()), "recorded_requests": len(records),
              "completed": sum(r.get("error") is None for r in records.values()),
              "failures": dict(Counter(r.get("error") for r in records.values() if r.get("error"))),
              "utc_cutoff_prior_requests": len(before), "utc_cutoff_later_requests": len(after),
              "primary_totals": {k: sum(v) for k,v in primary.items()},
              "limits": "No human review, real-world transfer, organizer eligibility ruling or complete account-debit reconciliation is established."}
    (BASE / "evidence-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
