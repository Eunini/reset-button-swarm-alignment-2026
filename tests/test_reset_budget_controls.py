"""Quota baselines must not obtain extra calls through aliases or stop all work."""
from dataclasses import asdict
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from check_reset_budget_controls import quota_replay
from reset_button import make_scenario


class QuotaTests(unittest.TestCase):
    def test_root_quota_and_global_budget_hold_under_restarts(self):
        reports = [asdict(r) for r in make_scenario(43)["reports"]]
        verdicts = {r["report_id"]: r["true_violation"] for r in reports}
        result = quota_replay(reports, verdicts, 8, 2, "restart", "root")
        self.assertLessEqual(result["calls"], 5)
        self.assertEqual(result["true_detected"], 3)
        self.assertEqual(result["false_stops"], 0)

    def test_identity_quota_is_resettable_at_fixed_report_count(self):
        reports = [asdict(r) for r in make_scenario(43)["reports"]]
        verdicts = {r["report_id"]: r["true_violation"] for r in reports}
        stable = quota_replay(reports, verdicts, None, 2, "persistent", "identity")
        reset = quota_replay(reports, verdicts, None, 2, "restart", "identity")
        self.assertEqual(stable["calls"], 5)
        self.assertEqual(reset["calls"], 27)


if __name__ == "__main__":
    unittest.main()
