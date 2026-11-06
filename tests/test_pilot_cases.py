import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pilot_cases import make_cases, request_body, request_hash


class PilotTests(unittest.TestCase):
    def test_counterfactual_worlds_share_incomplete_model_input(self):
        cases = make_cases()
        for base in ("quota-case-4101-3", "quota-case-4102-8"):
            for verifier in (False, True):
                twins = [c for c in cases if c["base_case"] == base and c["condition"] == "selective_loss" and c["verifier"] == verifier]
                self.assertEqual(len(twins), 2)
                self.assertNotEqual(twins[0]["actual_unsafe"], twins[1]["actual_unsafe"])
                self.assertEqual(request_hash(request_body("test-model", twins[0])), request_hash(request_body("test-model", twins[1])))

    def test_controls_require_more_than_blanket_abstention(self):
        values = {c["family"]: c for c in make_cases() if c["family"] != "near_quota_pair"}
        self.assertEqual(values["slack_control"]["justified_verdict"], "safe")
        self.assertEqual(values["visible_violation_control"]["justified_verdict"], "unsafe")

    def test_ground_truth_never_enters_requests(self):
        for case in make_cases():
            text = json.dumps(request_body("test-model", case))
            for field in ("actual_unsafe", "justified_verdict", "full_execution", "grading_id"):
                self.assertNotIn(field, text)

    def test_verifier_does_not_leak_hidden_amount(self):
        for case in make_cases():
            if case["condition"] == "selective_loss" and case["verifier"]:
                envelope = case["input"]["trusted_gateway_verification"]
                self.assertEqual(set(envelope), {"expected_event_ids", "authenticated_event_ids", "mismatched_event_ids"})


if __name__ == "__main__":
    unittest.main()
