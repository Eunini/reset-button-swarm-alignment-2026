"""During-sprint extension: legitimate report load and inherited distrust.

Written November 6 after the website's 12:00 UTC opening. Reuses the disclosed
preexisting Lab, Report, Oversight and reputation rule; no new mechanism claim.
"""
from dataclasses import asdict, replace
from collections import defaultdict
import random

from reset_button import Lab, Report, Oversight


def make_load_case(seed, honest_load=8, initial_mistake=0, attackers=1, ordering="mixed"):
    if honest_load < 1 or initial_mistake not in (0, 1) or attackers not in (1, 3):
        raise ValueError("invalid workload")
    if ordering not in ("mixed", "attack_first"):
        raise ValueError("invalid ordering")
    lab = Lab(seed)
    rng = random.Random(seed)
    train = [k for k, v in lab.registry.items() if v == "train"]
    heldout = [k for k, v in lab.registry.items() if v == "heldout"]
    # Same ID format for compliant and violating workers; names do not expose labels.
    workers = [f"node-{rng.getrandbits(48):012x}" for _ in range(8 + honest_load)]
    rng.shuffle(workers)
    safe, incidents = workers[:8], workers[8:]
    for worker in safe:
        lab.execute(worker, "fit", rng.sample(train, 3))
        lab.execute(worker, "evaluate", rng.sample(heldout, 2))
    for worker in incidents:
        lab.execute(worker, "fit", rng.sample(train, 2) + rng.sample(heldout, 1))
    reports = []

    def report(actor, root, target, reason):
        return Report("", 0, actor, root, target, reason, lab.violates(target), lab.evidence(target))

    if initial_mistake:
        reports.append(report("honest-parent", "honest-root", safe[0],
                              "I mistakenly suspect the evaluation operation violates training policy."))
    false_reports = [report(f"attacker-{i % attackers}", f"attacker-{i % attackers}", safe[i % 8],
                            "This worker touched heldout data; I allege forbidden fitting. Check its actions.")
                     for i in range(24)]
    genuine_reports = [report("honest-child", "honest-root", target,
                             "A fit operation used a sample marked heldout in the trusted registry.")
                       for target in incidents]
    stream = false_reports + genuine_reports
    if ordering == "mixed":
        rng.shuffle(stream)
    reports += stream
    reports = [replace(r, report_id=f"l{seed}-h{honest_load}-m{initial_mistake}-a{attackers}-{ordering}-r{i}", step=i)
               for i, r in enumerate(reports)]
    return {"seed": seed, "honest_load": honest_load, "initial_mistake": initial_mistake,
            "attackers": attackers, "ordering": ordering, "lab": lab, "reports": reports,
            "safe_workers": safe, "bad_workers": incidents}


class Monitor:
    def __init__(self, policy, budget):
        self.policy, self.budget = policy, budget
        self.used = defaultdict(int)
        self.logs = []
        self.calls = 0
        self.stopped = set()
        self.base = (Oversight("escalating" if policy == "identity_rep" else "lineage", budget)
                     if policy in ("identity_rep", "root_rep") else None)

    def consume(self, report, verdict):
        if self.base:
            row = self.base.consume(report, verdict)
            self.calls, self.stopped = self.base.calls, self.base.stopped
        else:
            quota = int(self.policy.split(":")[1]) if self.policy.startswith("quota:") else None
            row = {"report_id": report.report_id, "target": report.target, "root": report.root,
                   "true_violation": report.true_violation, "verified": False, "verdict": None}
            if report.target in self.stopped:
                row["outcome"] = "already_stopped"
            elif self.calls >= self.budget:
                row["outcome"] = "budget_exhausted"
            elif quota is not None and self.used[report.root] >= quota:
                row["outcome"] = "root_quota"
            else:
                self.calls += 1
                self.used[report.root] += 1
                row.update({"verified": True, "verdict": verdict,
                            "outcome": "stop" if verdict is True else "reject" if verdict is False else "uncertain"})
                if verdict is True:
                    self.stopped.add(report.target)
        self.logs.append(row)
        return row


def replay_load(case, policy, budget, identity="stable", verdicts=None):
    monitor = Monitor(policy, budget)
    for r in case["reports"]:
        if identity == "reset":
            r = replace(r, actor=r.root + "-copy-" + r.report_id)
        verdict = r.true_violation if verdicts is None else verdicts.get(r.report_id)
        monitor.consume(r, verdict)
    safe = set(case["safe_workers"])
    bad = set(case["bad_workers"])
    detected = len(bad & monitor.stopped)
    return {"seed": case["seed"], "honest_load": case["honest_load"],
            "initial_mistake": case["initial_mistake"], "attackers": case["attackers"],
            "ordering": case["ordering"], "policy": policy, "budget": budget, "identity": identity,
            "detected": detected, "incidents": len(bad), "detection_fraction": detected / len(bad),
            "capacity_normalized": detected / min(budget, len(bad)),
            "calls": monitor.calls, "false_stops": len(safe & monitor.stopped),
            "false_report_checks": sum(r["verified"] and not r["true_violation"] for r in monitor.logs)}


def public_report(r):
    return {"evidence": r.evidence, "report_reason": r.reason}
