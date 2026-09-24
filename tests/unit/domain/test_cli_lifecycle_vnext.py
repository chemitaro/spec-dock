"""Schema-three Scope lifecycle semantics."""

from dataclasses import replace
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS = Path(__file__).resolve().parents[3] / "src/spec_dock/assets/spec_dock/scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS))

from spec_dock_runtime.domain.lifecycle import (  # noqa: E402
    GithubBackend,
    LocalBackend,
    LocalLifecycle,
    SelectionState,
    decode_scope_metadata,
    encode_scope_metadata,
    observe_github_state,
)


def test_local_scope_round_trips_unrecognized_metadata() -> None:
    payload: dict[str, object] = {
        "schema_version": 3,
        "type": "epic",
        "id": "epic-local-00042",
        "title": "Plan delivery",
        "slug": "plan-delivery",
        "parent_id": "init-local-00001",
        "initiative_id": "init-local-00001",
        "epic_id": None,
        "depends_on": ["epic-local-00040"],
        "backend": "local",
        "github": None,
        "lifecycle": {"state": "not-planned", "revision": 2, "updated_at": "2026-09-24T12:00:00Z"},
        "revision": 4,
        "custom": {"owner": "me", "arbitrary": [1, 2]},
    }

    decoded = decode_scope_metadata(payload)

    assert isinstance(decoded.backend, LocalBackend)
    assert decoded.backend.lifecycle.state == "not-planned"
    assert decoded.revision == 4
    assert encode_scope_metadata(decoded) == payload


@pytest.mark.parametrize(
    ("remote_state", "reason", "expected"),
    [
        ("OPEN", None, "open"),
        ("CLOSED", "completed", "completed"),
        ("CLOSED", "not_planned", "not-planned"),
        ("CLOSED", None, "unknown"),
        ("CLOSED", "duplicate", "unknown"),
        ("CLOSED", "future_reason", "unknown"),
        ("SOMETHING_ELSE", "completed", "unknown"),
    ],
)
def test_github_reason_never_infers_completion_from_closed_alone(
    remote_state: str, reason: str | None, expected: str
) -> None:
    assert observe_github_state(remote_state, reason) == expected


def test_selection_rejects_focus_that_does_not_match_chain() -> None:
    with pytest.raises(ValueError, match="focus"):
        SelectionState(
            worktree_id="wt:123",
            revision=2,
            initiative_id="init-local-00001",
            epic_id="epic-local-00002",
            issue_id=None,
            focus_id="init-local-00001",
        )


def test_github_scope_keeps_remote_authority_exclusive() -> None:
    payload: dict[str, object] = {
        "schema_version": 3,
        "type": "issue",
        "id": "iss-00409",
        "title": "Redesign CLI",
        "slug": "redesign-cli",
        "parent_id": "epic-00356",
        "initiative_id": "init-local-00003",
        "epic_id": "epic-00356",
        "revision": 1,
        "backend": "github",
        "github": {"issue_number": 409, "repo_owner": "chemitaro", "repo_name": "spec-dock"},
        "lifecycle": None,
        "future-field": {"keep": True},
    }

    decoded = decode_scope_metadata(payload)

    assert isinstance(decoded.backend, GithubBackend)
    assert decoded.backend.issue_number == 409
    assert encode_scope_metadata(decoded) == payload


@pytest.mark.parametrize("kind", ["initiative", "epic", "issue"])
@pytest.mark.parametrize("state", ["open", "completed", "not-planned"])
def test_local_lifecycle_is_supported_for_each_scope_kind(kind: str, state: str) -> None:
    prefix = {"initiative": "init", "epic": "epic", "issue": "iss"}[kind]
    payload: dict[str, object] = {
        "schema_version": 3,
        "type": kind,
        "id": f"{prefix}-local-00001",
        "revision": 0,
        "backend": "local",
        "github": None,
        "lifecycle": {"state": state, "revision": 0, "updated_at": "2026-09-24T00:00:00Z"},
    }
    assert decode_scope_metadata(payload).backend.lifecycle.state == state


def test_metadata_codec_rejects_kind_and_id_mismatch() -> None:
    payload: dict[str, object] = {
        "schema_version": 3,
        "type": "epic",
        "id": "iss-local-00001",
        "revision": 0,
        "backend": "local",
        "github": None,
        "lifecycle": {"state": "open", "revision": 0, "updated_at": "2026-09-24T00:00:00Z"},
    }
    with pytest.raises(ValueError, match="ID"):
        decode_scope_metadata(payload)


def test_codec_updates_typed_lifecycle_without_losing_unknown_fields() -> None:
    payload: dict[str, object] = {
        "schema_version": 3,
        "type": "initiative",
        "id": "init-local-00001",
        "revision": 1,
        "backend": "local",
        "github": None,
        "lifecycle": {"state": "open", "revision": 1, "updated_at": "old", "extension": "kept"},
        "extension": {"arbitrary": "kept"},
    }
    decoded = decode_scope_metadata(payload)
    changed = replace(
        decoded,
        backend=LocalBackend(LocalLifecycle("completed", 2, "new")),
        revision=2,
    )

    encoded = encode_scope_metadata(changed)

    assert encoded["revision"] == 2
    assert encoded["lifecycle"] == {
        "state": "completed",
        "revision": 2,
        "updated_at": "new",
        "extension": "kept",
    }
    assert encoded["extension"] == payload["extension"]
    assert payload["lifecycle"] != encoded["lifecycle"]


def test_schema_three_writer_rejects_legacy_and_duplicate_authority() -> None:
    payload: dict[str, object] = {
        "schema_version": 3,
        "type": "issue",
        "id": "iss-00001",
        "revision": 0,
        "backend": "github",
        "github": {"issue_number": 1, "repo_owner": "example", "repo_name": "repo"},
        "lifecycle": {"state": "completed", "revision": 0, "updated_at": "now"},
    }
    with pytest.raises(ValueError, match="local lifecycle"):
        decode_scope_metadata(payload)
    payload["schema_version"] = 1
    with pytest.raises(ValueError, match="schema_version 3"):
        decode_scope_metadata(payload)
