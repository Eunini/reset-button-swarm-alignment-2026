import sys
from pathlib import Path
from dataclasses import replace
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from report_load import make_load_case, replay_load, public_report


class LoadTests(unittest.TestCase):
    def test_honest_load_does_not_increase_attacker_allowance(self):
        for h in (1,4,8,12):
            for a in (1,3):
                c=make_load_case(901,h,1,a)
                self.assertEqual(sum(r.root.startswith('attacker') for r in c['reports']),24)
                self.assertEqual(sum(r.true_violation for r in c['reports']),h)
                self.assertEqual(sum(r.root=='honest-root' and not r.true_violation for r in c['reports']),1)

    def test_quota_caps_busy_honest_root(self):
        c=make_load_case(902,8,0,1)
        r=replay_load(c,'quota:4',16)
        self.assertEqual(r['detected'],4)
        self.assertEqual(r['false_stops'],0)

    def test_correct_reputation_handles_high_load_without_mistake(self):
        c=make_load_case(903,8,0,1)
        self.assertEqual(replay_load(c,'root_rep',16)['detected'],8)

    def test_initial_mistake_suppresses_distinct_truthful_reports(self):
        c=make_load_case(904,8,1,1)
        self.assertEqual(replay_load(c,'root_rep',16)['detected'],0)
        self.assertEqual(replay_load(c,'quota:4',16)['detected'],3)

    def test_root_policies_are_invariant_to_chosen_alias(self):
        c=make_load_case(905,12,1,3)
        for p in ('root_rep','quota:1','quota:2','quota:4','quota:8'):
            for budget in (8,16):
                x=replay_load(c,p,budget,'stable');y=replay_load(c,p,budget,'reset')
                self.assertEqual(x['detected'],y['detected']);self.assertEqual(x['calls'],y['calls'])

    def test_call_budget_and_ground_truth_hold(self):
        c=make_load_case(906,12,1,3,'attack_first')
        for p in ('checked','identity_rep','root_rep','quota:1','quota:4','quota:8'):
            r=replay_load(c,p,8,'reset')
            self.assertLessEqual(r['calls'],8);self.assertEqual(r['false_stops'],0)
        for r in c['reports']:
            self.assertNotIn('true_violation',public_report(r))


if __name__=='__main__':unittest.main()
