import sys
import unittest
from pathlib import Path


def _authority_module():
    runtime_scripts_dir = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "spec_dock"
        / "assets"
        / "spec_dock"
        / "scripts"
    )
    sys.path.insert(0, str(runtime_scripts_dir))
    try:
        from spec_dock_runtime.domain import authority
    finally:
        sys.path.pop(0)
    return authority


class TestAuthorityGate(unittest.TestCase):
    def _approved_record(self):
        authority = _authority_module()
        return authority.approved_runtime_promotion_record(node_id="iss-00101")

    def test_approved_authority_with_exact_grant_passes(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=self._approved_record(),
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.reason, "ok")

    def test_missing_authority_metadata_fails_closed(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority=None,
            grants=authority.approved_runtime_grants(),
            promotion_record=self._approved_record(),
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "missing_authority")

    def test_proposed_authority_cannot_satisfy_lifecycle_grant(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="proposed",
            grants=authority.approved_runtime_grants(),
            promotion_record=self._approved_record(),
            required_grant="implementation_start",
            purpose="implementation_start",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "authority_not_approved")

    def test_missing_exact_grant_fails_closed(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=("review_input", "planning_input"),
            promotion_record=self._approved_record(),
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "missing_required_grant")

    def test_wildcard_grant_fails_closed(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=("review_input", "grants.*"),
            promotion_record=self._approved_record(),
            required_grant="review_input",
            purpose="review_input",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "invalid_grants")

    def test_stale_promotion_record_fails_closed(self) -> None:
        authority = _authority_module()
        record = self._approved_record()
        record["reviewer_target_hash"] = "stale"
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=record,
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "stale_promotion_hash")

    def test_missing_promotion_decision_fails_closed(self) -> None:
        authority = _authority_module()
        record = self._approved_record()
        del record["promotion_decision"]
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=record,
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "incomplete_promotion_record")
        self.assertIn("missing=promotion_decision", result.details)

    def test_stale_promotion_revision_fails_closed(self) -> None:
        authority = _authority_module()
        record = self._approved_record()
        record["approved_revision"] = "stale"
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=record,
            required_grant="issue_finish",
            purpose="issue_finish",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "stale_promotion_revision")

    def test_promotion_record_must_match_expected_active_revision(self) -> None:
        authority = _authority_module()
        result = authority.evaluate_authority_gate(
            authority="approved",
            grants=authority.approved_runtime_grants(),
            promotion_record=self._approved_record(),
            required_grant="issue_finish",
            purpose="issue_finish",
            expected_revision="active:iss-00999",
        )
        self.assertFalse(result.ok)
        self.assertEqual(result.reason, "promotion_record_not_bound_to_active_entry")


if __name__ == "__main__":
    unittest.main()
