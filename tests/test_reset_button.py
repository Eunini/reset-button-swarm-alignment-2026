"""Scientific invariants and a differential check against the pinned baseline."""
import ast
from collections import defaultdict
from pathlib import Path
import random
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from reset_button import Lab, Oversight, make_scenario, parse_verdict, replay, reputation, verifier_input


class ResetButtonTests(unittest.TestCase):
    def test_heldout_evaluation_is_allowed_but_fitting_is_not(self):
        lab = Lab(11)
        key = next(k for k, v in lab.registry.items() if v == "heldout")
        lab.execute("w", "evaluate", [key])
        self.assertFalse(lab.violates("w"))
        lab.execute("w", "fit", [key])
        self.assertTrue(lab.violates("w"))
        self.assertEqual(len(lab.artifacts), 2)

    def test_executor_rejects_unknown_samples(self):
        with self.assertRaises(ValueError):
            Lab(1).execute("w", "fit", ["forged-id"])

    def test_labels_not_in_model_input(self):
        for report in make_scenario(11)["reports"]:
            self.assertNotIn("true_violation", verifier_input(report))
            self.assertEqual(report.true_violation,
                             any(e["operation"] == "fit" and any(report.evidence["sample_registry"][k] == "heldout"
                                 for k in e["sample_ids"]) for e in report.evidence["actions"]))

    def test_reports_are_matched_and_budget_is_enforced(self):
        scenario = make_scenario(12)
        runs = [replay(scenario, m, identity, 4)
                for m in ("checked", "escalating", "lineage")
                for identity in ("persistent", "restart")]
        self.assertEqual(len({tuple(x["report_id"] for x in r["logs"]) for r in runs}), 1)
        self.assertTrue(all(r["verifier_calls"] <= 4 for r in runs))

    def test_lineage_is_invariant_to_alias_restarts(self):
        for seed in range(11, 31):
            scenario = make_scenario(seed)
            a = replay(scenario, "lineage", "persistent", 8)
            b = replay(scenario, "lineage", "restart", 8)
            for key in ("verifier_calls", "true_detected", "false_stops", "legitimate_work_fraction"):
                self.assertEqual(a[key], b[key])

    def test_perfect_verifier_never_stops_honest_worker(self):
        for seed in range(11, 31):
            for m in ("checked", "escalating", "lineage"):
                result = replay(make_scenario(seed), m, "restart", None)
                self.assertEqual(result["false_stops"], 0)
                self.assertEqual(result["true_detected"], 3)
                self.assertEqual(result["legitimate_work_fraction"], 1)

    def test_no_calls_budget_means_no_claimed_detection(self):
        result = replay(make_scenario(13), "checked", "restart", 0)
        self.assertEqual(result["verifier_calls"], 0)
        self.assertEqual(result["true_detected"], 0)

    def test_invalid_verdict_does_not_reward_or_sanction(self):
        scenario = make_scenario(14)
        result = replay(scenario, "escalating", "restart", 8, verdicts={})
        self.assertEqual(result["true_detected"], 0)
        self.assertEqual(result["false_stops"], 0)
        self.assertEqual(result["uncertain_verifications"], 8)

    def test_strict_parser_rejects_numeric_or_multiple_answers(self):
        for text in ['{"violation":1,"reason":"x"}', '{}',
                     '{"violation":false,"reason":"x"}\n{"violation":true,"reason":"x"}',
                     '```json\n{"violation":false,"reason":"x"}\n```']:
            self.assertEqual(parse_verdict(text)[1], "invalid_output")
        self.assertEqual(parse_verdict('{"violation":false,"reason":"x"}'), (False, None))

    def test_published_reputation_matches_random_histories(self):
        path = ROOT / "sources/norm-enforcement/norm_enforcement/core/mechanisms.py"
        tree = ast.parse(path.read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "RepVoteMechanism")
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_compute_reputations")
        # Execute only this audited mathematical method; no provider or network code.
        for node in ast.walk(method):
            if isinstance(node, ast.arg):
                node.annotation = None
        method.returns = None
        env = {"defaultdict": defaultdict}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), str(path), "exec"), env)
        config = SimpleNamespace(rep_alpha_prior=2, rep_beta_prior=1, false_report_penalty=3, escalating_penalty=True)
        rng = random.Random(711)
        for _ in range(100):
            history = [SimpleNamespace(reporter_id=rng.randrange(4), verified=rng.choice([True, False, None]))
                       for _ in range(rng.randrange(1, 60))]
            actual = env["_compute_reputations"](config, history)
            for actor in range(4):
                v = sum(r.reporter_id == actor and r.verified is True for r in history)
                f = sum(r.reporter_id == actor and r.verified is False for r in history)
                self.assertAlmostEqual(actual.get(actor, 2/3), reputation(v, f))


if __name__ == "__main__":
    unittest.main()
