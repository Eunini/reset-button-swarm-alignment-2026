"""Regenerate summaries and figures from saved receipts, with no API calls."""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import random
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def bootstrap_mean(values, seed=819, draws=5000):
    """Only used for the frozen main study; development has two seeds and no CIs."""
    rng = random.Random(seed)
    samples = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(draws))
    return [samples[int(.025 * draws)], samples[int(.975 * draws)]]


def analyze(path):
    summary = json.loads((path / "summary-live.json").read_text())
    trajectories = json.loads((path / "trajectories.json").read_text())
    grading = json.loads((path / "grading.json").read_text())
    controls = json.loads((path / "honest-control.json").read_text())
    calibration = []
    for model in ["qwen3.8-27b", "deepseek-v4-flash"]:
        rows = list({r["request_hash"]: r for r in grading if r["model"] == model}.values())
        valid = [r for r in rows if r["error"] is None and r["verdict"] is not None]
        calibration.append({"model": model, "unique_requests": len(rows), "usable": len(valid),
                            "correct": sum(r["verdict"] is r["truth"] for r in valid),
                            "false_positive": sum(r["verdict"] is True and not r["truth"] for r in valid),
                            "false_negative": sum(r["verdict"] is False and r["truth"] for r in valid),
                            "positive_cases": sum(r["truth"] for r in rows),
                            "error_counts": dict(Counter(r["error"] or "none" for r in rows))})
    pairs = defaultdict(dict)
    for r in trajectories:
        if r["budget"] == 8:
            pairs[r["verifier"], r["campaign"], r["seed"]][r["mechanism"], r["identity"]] = r
    comparisons = []
    grouped = defaultdict(list)
    for (verifier, campaign, seed), p in pairs.items():
        stable = p["escalating", "persistent"]["true_detected"]
        reset = p["escalating", "restart"]["true_detected"]
        fixed = p["lineage", "restart"]["true_detected"]
        row = {"verifier": verifier, "campaign": campaign, "seed": seed,
               "stable_detected": stable, "reset_detected": reset, "lineage_detected": fixed,
               "restart_difference": reset - stable, "repair_difference": fixed - reset}
        comparisons.append(row)
        grouped[verifier, campaign].append(row)
    effects = []
    for (verifier, campaign), rows in grouped.items():
        effect = {"verifier": verifier, "campaign": campaign, "independent_task_seeds": len(rows)}
        for field in ("restart_difference", "repair_difference"):
            vals = [r[field] for r in rows]
            effect[field] = statistics.mean(vals)
            if summary["stage"] == "main":
                effect[field + "_bootstrap_95"] = bootstrap_mean(vals)
        effects.append(effect)
    physical = []
    for folder in ([ROOT / "results/reset-development-20261105", path]
                   if summary["stage"] == "development" else [path]):
        if folder in physical:
            continue
        physical.append(folder)
    usage = {"physical_calls": 0, "computed_credits": 0., "provider_reported_cost": 0.,
             "note": "For development, totals include v1 failures and v2 new calls, excluding reused receipts. Not a balance audit."}
    for folder in physical:
        sfile = folder / "summary-live.json"
        if not sfile.exists():
            continue
        s = json.loads(sfile.read_text())["usage"]
        for field in ("physical_calls", "computed_credits", "provider_reported_cost"):
            usage[field] += s[field]
    output = {"stage": summary["stage"], "preexisting": summary["preexisting"],
              "seed_n": summary["seed_n"], "calibration": calibration, "effects": effects,
              "campaign_status": summary["campaign_status"], "usage": usage,
              "honest_control": [{k: r[k] for k in ("seed", "mechanism", "identity", "true_detected", "verifier_calls")}
                                 for r in controls],
              "caveats": ["two development seeds do not support an efficacy or generalization claim",
                          "oracle controls are constructed mechanism checks, not observations of model behaviour",
                          "LLMs author batched allegations; workers and restarts are scripted",
                          "identity-invariance of the lineage implementation is structural, not a discovery",
                          "the objective sample policy could instead be enforced directly by code",
                          "arrival order, target diversity and shared budgets are modelling assumptions"]}
    (path / "analysis.json").write_text(json.dumps(output, indent=2) + "\n")
    with (path / "paired-effects.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(comparisons[0]))
        writer.writeheader(); writer.writerows(comparisons)
    figs = path / "figures"
    figs.mkdir(exist_ok=True)
    labels = {"qwen3.8-27b": "Qwen 3.8 27B", "deepseek-v4-flash": "DeepSeek V4 Flash"}
    fig, axes = plt.subplots(1, 2, figsize=(8, 2.65), sharey=True)
    for ax, model in zip(axes, labels):
        for mechanism, identity, label, color, ls in [
            ("escalating", "persistent", "Escalating / stable ID", "#385D91", "--"),
            ("escalating", "restart", "Escalating / restart", "#B84335", "-"),
            ("lineage", "restart", "Lineage / restart", "#22816D", ":"),
            ("checked", "restart", "Check every report", "#8E8E8E", "-.")]:
            groups = [g for g in summary["groups"] if g["verifier"] == model and g["campaign"] == "scripted"
                      and g["mechanism"] == mechanism and g["identity"] == identity]
            ax.plot([g["budget"] if g["budget"] is not None else 27 for g in groups],
                    [g["true_detected"] / 3 for g in groups], label=label, color=color,
                    linestyle=ls, marker="o", markersize=4, linewidth=2)
        ax.set_title(labels[model], fontsize=10)
        ax.set_xlabel("Verification-call budget", fontsize=9)
        ax.set_xticks([4, 8, 12, 16, 27], ["4", "8", "12", "16", "All"])
        ax.set_ylim(-.04, 1.05)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.15)
    axes[0].set_ylabel("Genuine incidents detected (fraction)", fontsize=9)
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="lower center", bbox_to_anchor=(.5, -.04),
               ncol=2, fontsize=8, frameon=False)
    fig.suptitle(f"{'Development only' if summary['stage']=='development' else 'Main study'}: {summary['seed_n']} task seeds, scripted allegations", fontsize=10, y=1.04)
    fig.tight_layout(rect=(0, .12, 1, 1))
    fig.savefig(figs / "budget-curves.png", dpi=180, bbox_inches="tight")
    fig.savefig(figs / "budget-curves.svg", bbox_inches="tight")
    plt.close(fig)
    print(json.dumps({"analysis": str(path / "analysis.json"), "calibration": calibration, "usage": usage}, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", default="results/reset-development-v2-20261105")
    args = parser.parse_args()
    analyze(ROOT / args.results)
