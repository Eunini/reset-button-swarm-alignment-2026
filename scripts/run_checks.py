"""Free preexisting construction checks. This is not the main model study."""
from __future__ import annotations
import argparse
from collections import defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from blind_spots import (local_monitor, make_pair, observe, receipt_monitor,
                        recovery_monitor, visible_monitor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["preexisting-smoke"], required=True)
    parser.add_argument("--cases", type=int, default=20)
    args = parser.parse_args()
    if not 1 <= args.cases <= 200:
        parser.error("construction-check case count must be between 1 and 200")
    out = ROOT / "results" / args.stage
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    # Sequential variants are clustered cases, not independent empirical samples.
    with (out / "episodes.jsonl").open("w") as handle:
        for workers in (3, 8, 16):
            for seed in range(args.cases):
                for episode in make_pair(seed, workers):
                    for condition in ("full", "random_loss", "selective_loss", "altered_content"):
                        obs = observe(episode, condition, seed=1000 + seed)
                        outcomes = {"per_worker": local_monitor(obs),
                                    "visible_global": visible_monitor(obs),
                                    "completeness_bounds": receipt_monitor(obs),
                                    "authoritative_recovery": recovery_monitor(obs, episode.events)}
                        handle.write(json.dumps({
                            "case": episode.case_id, "unsafe": episode.is_unsafe,
                            "condition": condition, "workers": workers,
                            "ground_truth_execution": [asdict(e) for e in episode.events],
                            "log_only_model_input": obs.model_input(),
                            "manifest_model_input": obs.model_input(True),
                            "outcomes": {k: asdict(v) for k, v in outcomes.items()},
                        }, sort_keys=True) + "\n")
                        for monitor, decision in outcomes.items():
                            rows.append({"case": episode.case_id, "workers": workers,
                                         "condition": condition, "unsafe": int(episode.is_unsafe),
                                         "monitor": monitor, "verdict": decision.verdict,
                                         "recovered_events": decision.recovered_events})
    with (out / "decisions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    groups = defaultdict(list)
    for row in rows:
        groups[row["workers"], row["condition"], row["monitor"]].append(row)
    summary = []
    for (workers, condition, monitor), items in sorted(groups.items()):
        unsafe = [r for r in items if r["unsafe"]]
        safe = [r for r in items if not r["unsafe"]]
        summary.append({"workers": workers, "condition": condition, "monitor": monitor,
                        "n_unsafe": len(unsafe), "n_safe": len(safe),
                        "false_safe_count": sum(r["verdict"] == "safe" for r in unsafe),
                        "unsafe_detected_count": sum(r["verdict"] == "unsafe" for r in unsafe),
                        "clean_certified_count": sum(r["verdict"] == "safe" for r in safe),
                        "clean_false_alarm_count": sum(r["verdict"] == "unsafe" for r in safe),
                        "abstention_count": sum(r["verdict"] == "insufficient_evidence" for r in items),
                        "recovered_events": sum(r["recovered_events"] for r in items)})
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    sources = [ROOT / "src/blind_spots.py", Path(__file__).resolve()]
    metadata = {"stage": args.stage, "created_utc": datetime.now(timezone.utc).isoformat(),
                "kind": "preexisting synthetic construction checks, NOT LLM results",
                "base_cases": 3 * args.cases, "episode_variants": len(rows) // 4,
                "decisions": len(rows), "model_calls": 0, "paid_jobs": 0,
                "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sources}}
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
