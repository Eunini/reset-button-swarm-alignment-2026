"""Tests of scientific invariants and evidence boundaries, not API behaviour."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from blind_spots import (Event, event_digest, local_monitor, make_pair, observe,
                        receipt_monitor, recovery_monitor, visible_monitor)


class EvidenceTests(unittest.TestCase):
    def test_pairs_have_opposite_truth_but_identical_log_only_inputs(self):
        for workers in (3, 8, 16):
            for seed in range(40):
                safe, unsafe = make_pair(seed, workers)
                self.assertFalse(safe.is_unsafe)
                self.assertTrue(unsafe.is_unsafe)
                self.assertEqual(observe(safe, "selective_loss").model_input(),
                                 observe(unsafe, "selective_loss").model_input())
                # Receipt condition is NOT an identical-input comparison.
                self.assertNotEqual(observe(safe, "selective_loss").model_input(True),
                                    observe(unsafe, "selective_loss").model_input(True))

    def test_complete_evidence_solves_both_classes(self):
        for episode in make_pair(8, 8):
            obs = observe(episode, "full")
            expected = "unsafe" if episode.is_unsafe else "safe"
            self.assertEqual(visible_monitor(obs).verdict, expected)
            self.assertEqual(receipt_monitor(obs).verdict, expected)

    def test_fragmented_violation_passes_local_but_fails_global(self):
        _, episode = make_pair(1, 8)
        obs = observe(episode, "full")
        self.assertEqual(local_monitor(obs).verdict, "safe")
        self.assertEqual(visible_monitor(obs).verdict, "unsafe")

    def test_selective_loss_must_not_be_treated_as_proof_of_safety_or_harm(self):
        for episode in make_pair(3):
            obs = observe(episode, "selective_loss")
            self.assertEqual(visible_monitor(obs).verdict, "safe")
            self.assertEqual(receipt_monitor(obs).verdict, "insufficient_evidence")

    def test_hashes_detect_modification_but_do_not_identify_intent(self):
        for episode in make_pair(10):
            obs = observe(episode, "altered_content")
            self.assertEqual(receipt_monitor(obs).verdict, "insufficient_evidence")

    def test_recovery_requires_correct_independent_record(self):
        for episode in make_pair(2, 8):
            for condition in ("selective_loss", "altered_content", "random_loss"):
                obs = observe(episode, condition, seed=4)
                result = recovery_monitor(obs, episode.events)
                self.assertEqual(result.verdict, "unsafe" if episode.is_unsafe else "safe")
            obs = observe(episode, "selective_loss")
            self.assertEqual(recovery_monitor(obs, ()).verdict, "insufficient_evidence")
            safe, unsafe = make_pair(2, 8)
            wrong = safe.events if episode.is_unsafe else unsafe.events
            self.assertEqual(recovery_monitor(obs, wrong).verdict, "insufficient_evidence")

    def test_duplicate_and_extra_records_do_not_prove_completeness(self):
        safe, _ = make_pair(11)
        obs = observe(safe, "selective_loss")
        duplicate = replace(obs, visible=obs.visible + (obs.visible[0],))
        self.assertEqual(receipt_monitor(duplicate).verdict, "insufficient_evidence")
        fake = Event("not-in-manifest", "fake-worker", "principal-A", 0)
        extra = replace(obs, visible=obs.visible + (fake,))
        self.assertEqual(receipt_monitor(extra).verdict, "insufficient_evidence")

    def test_authenticated_violation_remains_unsafe_with_other_records_missing(self):
        _, unsafe = make_pair(20, 8)
        obs = observe(unsafe, "full")
        no_distractor = replace(obs, visible=tuple(e for e in obs.visible if e.principal == "principal-A"))
        self.assertEqual(receipt_monitor(no_distractor).verdict, "unsafe")

    def test_other_principals_are_not_pooled(self):
        safe, _ = make_pair(12)
        self.assertGreater(sum(e.units for e in safe.events), safe.quotas["principal-A"])
        self.assertEqual(visible_monitor(observe(safe, "full")).verdict, "safe")

    def test_negative_units_cannot_mask_violations(self):
        with self.assertRaises(ValueError):
            Event("a", "w", "principal-A", -10)

    def test_all_missing_is_not_certified(self):
        safe, _ = make_pair(14)
        obs = replace(observe(safe, "full"), visible=())
        self.assertEqual(receipt_monitor(obs).verdict, "insufficient_evidence")

    def test_model_input_contains_no_grading_fields(self):
        _, unsafe = make_pair(15)
        value = observe(unsafe, "random_loss").model_input()
        self.assertEqual(set(value), {"task", "quotas", "max_action_units", "visible_events"})

    def test_generation_is_reproducible_and_manifest_binding_is_content_based(self):
        a, _ = make_pair(90)
        b, _ = make_pair(90)
        self.assertEqual(a, b)
        self.assertNotEqual(event_digest(a.events[-1]),
                            event_digest(replace(a.events[-1], units=a.events[-1].units + 1)))

    def test_lower_bound_allows_certification_when_missing_consumption_cannot_matter(self):
        safe, _ = make_pair(21)
        obs = observe(safe, "selective_loss")
        roomy = replace(obs, quotas={p: 10000 for p in obs.quotas})
        self.assertEqual(receipt_monitor(roomy).verdict, "safe")


if __name__ == "__main__":
    unittest.main()
