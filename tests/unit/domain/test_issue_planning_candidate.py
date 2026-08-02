from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import pytest

RUNTIME_SCRIPTS_DIR = Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))


def _candidate():
    return __import__(
        "spec_dock_runtime.domain.issue_planning_candidate",
        fromlist=["build_candidate_material"],
    )


COMPANION_PATH = "artifacts/20260729t044600z-guide-new-member-chatgpt-first-issue-planning.md"


def _document(filename: str, *, body: str | None = None, changes: dict[str, str] | None = None) -> bytes:
    kinds = {
        "requirement.md": "要件定義書（Issue）",
        "design.md": "設計書（Issue）",
        "plan.md": "実装計画書（Issue）",
    }
    values = {
        "種別": kinds[filename],
        "ID": '"iss-00003"',
        "タイトル": '"Issue Title"',
        "状態": '"approved"',
        "作成者": '"Author"',
        "最終更新": '"2026-07-27"',
        "親": '["epic-00002", "init-00001"]',
    }
    if filename == "design.md":
        values["依存"] = '["requirement.md"]'
    if filename == "plan.md":
        values["依存"] = '["requirement.md", "design.md"]'
    values.update(changes or {})
    order = ["種別", "ID", "タイトル", "状態", "作成者", "最終更新"]
    if filename != "requirement.md":
        order.append("依存")
    order.append("親")
    front_matter = "\n".join(f"{key}: {values[key]}" for key in order)
    content = body or "# iss-00003 Issue Title\n\n## Section\n\nSubstantive content.\n"
    return f"---\n{front_matter}\n---\n\n{content}".encode()


def _documents() -> dict[str, bytes]:
    return {name: _document(name) for name in ("requirement.md", "design.md", "plan.md")}


def _companion() -> bytes:
    return b"""# New-member guide

This guide is subordinate to requirement.md, design.md, and plan.md. Those canonical
documents have precedence. It covers the init-00001, epic-00002, and iss-00003 lineage.

## Initiative, Epic, and Issue lineage

The init-00001, epic-00002, and iss-00003 lineage establishes the planning target.

## Purpose and scope

Purpose and scope define the bounded onboarding material.

## System context

The system context identifies the planning actors and boundaries.

## Authority and responsibility boundary

Authority and responsibility remain with the Human and deterministic Runtime.

## Current architecture and target architecture

Current architecture and target architecture describe the bounded transition.

## ChatGPT First planning lifecycle

ChatGPT First governs the planning lifecycle.

## Direct Oracle and reference-only chatgpt-use

The Runtime uses Oracle directly; chatgpt-use is reference-only.

## Candidate, Review, Human, and apply lifecycle

Candidate, Review, Human approval, and apply form the controlled lifecycle.

## Exact current branch gate

The exact current branch is mandatory.

## Roadmap and operations

S01 through S07 are complete. S08 through S14 remain.

## Provider authority and projection

Provider authority precedes projection.

## Failure modes

Failure modes stop closed.

## First-day checklist

The first-day checklist directs the new member.

```plantuml
@startuml
title System Context
actor Human
@enduml
```

```plantuml
@startuml
title Responsibility Boundary
actor Human
@enduml
```

```plantuml
@startuml
title Planning Sequence
actor Human
@enduml
```

```plantuml
@startuml
title Implementation Roadmap
actor Human
@enduml
```
"""


def _exact_heading_companion() -> bytes:
    replacements = {
        b"## Initiative, Epic, and Issue lineage": b"## init-/epic-/iss- lineage",
        b"## Purpose and scope": b"## Purpose/scope",
        b"## Authority and responsibility boundary": b"## Authority/responsibility",
        b"## Current architecture and target architecture": (b"## Current architecture/target architecture"),
        b"## ChatGPT First planning lifecycle": b"## ChatGPT First planning workflow",
        b"## Direct Oracle and reference-only chatgpt-use": (
            b"## Provider-owned direct Oracle/reference-only chatgpt-use"
        ),
        b"## Candidate, Review, Human, and apply lifecycle": (b"## Candidate/Review/Human/apply lifecycle"),
        b"## Exact current branch gate": b"## Exact branch failure",
        b"## Roadmap and operations": b"## S01/S07/S08/S14 status/roadmap",
        b"## Provider authority and projection": b"## Provider/projection",
    }
    payload = _companion()
    for old, new in replacements.items():
        payload = payload.replace(old, new)
    return payload


def _source():
    contracts = __import__(
        "spec_dock_runtime.domain.issue_planning_contracts",
        fromlist=["PlanningContext", "PlanningSourceEvidence"],
    )
    context = contracts.PlanningContext(
        issue_id="iss-00003",
        repository="owner/repo",
        branch="feature/issue",
        source_head="a" * 40,
        parent_epic_id="epic-00002",
        parent_initiative_id="init-00001",
        dependency_summary=("iss-00001",),
        canonical_issue_paths=(
            "spec-dock/initiatives/i/epics/e/issues/x/design.md",
            "spec-dock/initiatives/i/epics/e/issues/x/plan.md",
            "spec-dock/initiatives/i/epics/e/issues/x/requirement.md",
        ),
        relevant_source_paths=("src/example.py",),
        operator_context=(),
        onboarding_companion_path=COMPANION_PATH,
    )
    evidence = contracts.PlanningSourceEvidence(
        repository="owner/repo",
        branch="feature/issue",
        upstream="origin/feature/issue",
        local_head="a" * 40,
        remote_head="a" * 40,
        source_manifest_hash="c" * 64,
        snapshot_id="b" * 64,
        remote_head_disposition="fetched_remote_tracking_ref",
    )
    return context, evidence


def _material():
    module = _candidate()
    documents = _documents()
    baseline = module.parse_current_front_matter_baseline(documents)
    context, evidence = _source()
    payload = b"exact authoring zip bytes"
    return module.build_candidate_material(
        planner_documents=documents,
        onboarding_companion_path=COMPANION_PATH,
        onboarding_companion_bytes=_companion(),
        baseline=baseline,
        context=context,
        source_evidence=evidence,
        source_payload_sha256=hashlib.sha256(payload).hexdigest(),
        source_payload_size=len(payload),
        operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
    )


def test_parse_canonical_control_json_normalizes_recursive_input_failure() -> None:
    module = _candidate()
    payload = (b'{"nested":' * 2000) + b"null" + (b"}" * 2000) + b"\n"

    with pytest.raises(ValueError, match="canonical control JSON"):
        module.parse_canonical_control_json(payload)


def test_revision_candidate_uses_prior_version_plus_one() -> None:
    module = _candidate()
    documents = _documents()
    baseline = module.parse_current_front_matter_baseline(documents)
    context, evidence = _source()
    payload = b"exact authoring zip bytes"
    material = module.build_candidate_material(
        planner_documents=documents,
        onboarding_companion_path=COMPANION_PATH,
        onboarding_companion_bytes=_companion(),
        baseline=baseline,
        context=context,
        source_evidence=evidence,
        source_payload_sha256=hashlib.sha256(payload).hexdigest(),
        source_payload_size=len(payload),
        operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
        version=2,
    )
    assert material.version == 2
    assert material.candidate_id == "iss-00003-v2-20260728t120000z"
    assert material.logical_filename.endswith("-candidate-v2.zip")
    assert module.verify_issue_candidate_files(material.files, material.internal_root) == ()


@pytest.mark.parametrize("version", [0, True])
def test_candidate_version_rejects_zero_and_bool(version: object) -> None:
    module = _candidate()
    documents = _documents()
    baseline = module.parse_current_front_matter_baseline(documents)
    context, evidence = _source()
    payload = b"exact authoring zip bytes"
    with pytest.raises(ValueError, match="version"):
        module.build_candidate_material(
            planner_documents=documents,
            onboarding_companion_path=COMPANION_PATH,
            onboarding_companion_bytes=_companion(),
            baseline=baseline,
            context=context,
            source_evidence=evidence,
            source_payload_sha256=hashlib.sha256(payload).hexdigest(),
            source_payload_size=len(payload),
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            version=version,
        )


def test_mechanical_revision_replaces_one_target_body_match_with_utf8_budget() -> None:
    module = _candidate()
    documents = _documents()
    old = "Substantive"
    new = "具体的"
    cost = len(old.encode()) + len(new.encode())
    payloads = {**documents, COMPANION_PATH: _companion()}
    revised = module.apply_mechanical_revision(
        payloads,
        target_file="plan.md",
        onboarding_companion_path=COMPANION_PATH,
        old_text=old,
        new_text=new,
        diff_budget=cost,
    )
    assert old.encode() not in revised["plan.md"]
    assert new.encode() in revised["plan.md"]
    assert revised["requirement.md"] == documents["requirement.md"]
    assert revised["design.md"] == documents["design.md"]
    with pytest.raises(ValueError, match="budget"):
        module.apply_mechanical_revision(
            payloads,
            target_file="plan.md",
            onboarding_companion_path=COMPANION_PATH,
            old_text=old,
            new_text=new,
            diff_budget=cost - 1,
        )


@pytest.mark.parametrize("old_text", ["missing", "Substantive content."])
def test_mechanical_revision_rejects_zero_or_multiple_body_matches(old_text: str) -> None:
    module = _candidate()
    documents = _documents()
    if old_text != "missing":
        documents["plan.md"] = documents["plan.md"].replace(
            b"Substantive content.",
            b"Substantive content. Substantive content.",
        )
    with pytest.raises(ValueError, match="exactly one"):
        module.apply_mechanical_revision(
            {**documents, COMPANION_PATH: _companion()},
            target_file="plan.md",
            onboarding_companion_path=COMPANION_PATH,
            old_text=old_text,
            new_text="replacement",
            diff_budget=100,
        )


def test_s10_authoring_payload_accepts_exact_four_file_inventory() -> None:
    files = {**_documents(), COMPANION_PATH: _companion()}
    assert (
        _candidate().validate_issue_authoring_files(
            files,
            "authoring",
            expected_companion_path=COMPANION_PATH,
        )
        == ()
    )


def test_s10_onboarding_accepts_exact_thirteen_heading_contract() -> None:
    files = {**_documents(), COMPANION_PATH: _exact_heading_companion()}

    _candidate().validate_onboarding_companion(COMPANION_PATH, files[COMPANION_PATH])
    assert (
        _candidate().validate_issue_authoring_files(
            files,
            "authoring",
            expected_companion_path=COMPANION_PATH,
        )
        == ()
    )


@pytest.mark.parametrize(
    "payload",
    [
        _exact_heading_companion().replace(
            b"## Purpose/scope\n\nPurpose and scope define the bounded onboarding material.",
            (
                b"## Purpose\n\nPurpose defines the bounded onboarding material.\n\n"
                b"## Scope\n\nScope defines the bounded onboarding material."
            ),
        ),
        _exact_heading_companion().replace(
            (
                b"## Current architecture/target architecture\n\n"
                b"Current architecture and target architecture describe the bounded transition."
            ),
            (
                b"## Current architecture\n\nCurrent architecture describes the bounded transition.\n\n"
                b"## Target architecture\n\nTarget architecture describes the bounded transition."
            ),
        ),
        _exact_heading_companion().replace(
            b"## ChatGPT First planning workflow\n\nChatGPT First governs the planning lifecycle.",
            b"## ChatGPT First planning sequence\n\nChatGPT First governs the planning sequence.",
        ),
        _exact_heading_companion()
        .replace(
            b"## System context\n\nThe system context identifies the planning actors and boundaries.\n\n",
            b"",
        )
        .replace(
            b"## Authority/responsibility",
            b"## System context and Authority/responsibility",
        ),
        _exact_heading_companion()
        .replace(b"title System Context", b"title system-context")
        .replace(b"title Planning Sequence", b"title planning-sequence")
        .replace(b"title Implementation Roadmap", b"title implementation-roadmap"),
    ],
    ids=(
        "split-purpose-scope",
        "split-current-target",
        "planning-sequence-without-workflow-or-lifecycle",
        "merged-required-sections",
        "hyphen-roles",
    ),
)
def test_s10_onboarding_rejects_nonassignable_required_sections(payload: bytes) -> None:
    expected_message = (
        "onboarding companion PlantUML role is missing"
        if b"title system-context" in payload
        else "onboarding companion"
    )
    with pytest.raises(ValueError, match=expected_message):
        _candidate().validate_onboarding_companion(COMPANION_PATH, payload)

    assert _candidate().validate_issue_authoring_files(
        {**_documents(), COMPANION_PATH: payload},
        "authoring",
        expected_companion_path=COMPANION_PATH,
    ) == ("authoring_payload_invalid",)


@pytest.mark.parametrize("mutation", ["empty", "bom", "nul", "cr", "no_lf", "invalid_utf8"])
def test_s10_authoring_payload_rejects_invalid_text_framing(mutation: str) -> None:
    files = {**_documents(), COMPANION_PATH: _companion()}
    payload = files["design.md"]
    files["design.md"] = {
        "empty": b"",
        "bom": b"\xef\xbb\xbf" + payload,
        "nul": payload + b"\0",
        "cr": payload.replace(b"\n", b"\r\n", 1),
        "no_lf": payload.rstrip(b"\n"),
        "invalid_utf8": b"\xff\n",
    }[mutation]
    assert _candidate().validate_issue_authoring_files(
        files,
        "authoring",
        expected_companion_path=COMPANION_PATH,
    ) == ("authoring_payload_invalid",)


def test_s10_current_v4_guide_satisfies_completeness_contract() -> None:
    repository_root = Path(__file__).resolve().parents[3]
    pack = (
        repository_root / "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/"
        "issues/iss-00334-implement-chatgpt-issue-planning-workflow/artifacts/"
        "20260729t-iss-00334-onboarding-companion-planning-amendment-v4.zip"
    )
    with zipfile.ZipFile(pack) as archive:
        guide_name = next(name for name in archive.namelist() if name.endswith(f"issue/{COMPANION_PATH}"))
        guide = archive.read(guide_name)
    _candidate().validate_onboarding_companion(COMPANION_PATH, guide)


def test_current_managed_guide_matches_current_milestone_state() -> None:
    repository_root = Path(__file__).resolve().parents[3]
    guide_path = (
        repository_root / "spec-dock/initiatives/"
        "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
        "epics/epic-00331-planning-and-advisory-review/"
        "issues/iss-00334-implement-chatgpt-issue-planning-workflow/"
        f"artifacts/{Path(COMPANION_PATH).name}"
    )
    guide = guide_path.read_text(encoding="utf-8")

    assert "status reconciliation source/review baseline" in guide
    assert 'source_head: "' in guide
    for step in ("S08", "S09", "S10", "S11"):
        assert f'rectangle "{step} Closed" as {step}' in guide
        assert f"| {step} | closed |" in guide
    assert 'rectangle "S12 Open: refreshed Human authorization' in guide
    assert "| S12 | open |" in guide
    assert "refreshed Human authorization" in guide
    assert "live acceptance chain" in guide
    for step in ("S13", "S14"):
        assert f'rectangle "{step} Not admitted" as {step}' in guide
        assert f"| {step} | not admitted |" in guide
    assert "S08〜S14のremaining roadmap" not in guide
    assert "S08 through S14 remain" not in guide
    assert "S07のhistorical evidenceはnew-boundary S12 evidenceを代替しない" in guide


def test_s10_guide_rejects_token_complete_content_without_required_sections() -> None:
    payload = _companion().replace(b"## ", b"")

    with pytest.raises(ValueError, match="onboarding companion"):
        _candidate().validate_onboarding_companion(COMPANION_PATH, payload)


def test_s10_guide_rejects_all_required_concepts_consolidated_in_one_section() -> None:
    payload = b"## Everything\n\n" + _companion().replace(b"## ", b"")

    with pytest.raises(ValueError, match="onboarding companion"):
        _candidate().validate_onboarding_companion(COMPANION_PATH, payload)


@pytest.mark.parametrize(
    ("path", "mutation"),
    [
        ("guide.md", "none"),
        (COMPANION_PATH, "authority"),
        (COMPANION_PATH, "section"),
        (COMPANION_PATH, "steps"),
        (COMPANION_PATH, "fewer_blocks"),
        (COMPANION_PATH, "wrong_fence"),
        (COMPANION_PATH, "missing_role"),
        (COMPANION_PATH, "unbalanced"),
    ],
)
def test_s10_guide_rejects_wrong_path_and_incomplete_contract(path: str, mutation: str) -> None:
    payload = _companion()
    replacements = {
        "none": payload,
        "authority": payload.replace(b"subordinate", b"additional"),
        "section": payload.replace(b"Failure modes", b"Incidents"),
        "steps": payload.replace(b"S08 through S14", b"later steps"),
        "fewer_blocks": payload.rsplit(b"```plantuml", 1)[0],
        "wrong_fence": payload.replace(b"```plantuml", b"```puml", 1),
        "missing_role": payload.replace(b"Implementation Roadmap", b"Future"),
        "unbalanced": payload.replace(b"@enduml", b"@end", 1),
    }
    with pytest.raises(ValueError, match="onboarding companion"):
        _candidate().validate_onboarding_companion(path, replacements[mutation])


def test_current_front_matter_baseline_is_closed_and_consistent() -> None:
    baseline = _candidate().parse_current_front_matter_baseline(_documents())
    assert baseline.issue_id == "iss-00003"
    assert baseline.title == "Issue Title"
    assert baseline.parents == ("epic-00002", "init-00001")


@pytest.mark.parametrize(
    "filename,changes",
    [
        ("requirement.md", {"ID": '"iss-99999"'}),
        ("design.md", {"依存": '["plan.md"]'}),
        ("plan.md", {"タイトル": '"Different"'}),
    ],
)
def test_planner_front_matter_rejects_wrong_issue_title_state_author_parent_or_dependency(
    filename: str,
    changes: dict[str, str],
) -> None:
    module = _candidate()
    baseline = module.parse_current_front_matter_baseline(_documents())
    documents = _documents()
    documents[filename] = _document(filename, changes=changes)
    with pytest.raises(ValueError, match="front matter"):
        module.normalize_planner_documents(
            documents,
            baseline,
            datetime(2026, 7, 28, tzinfo=timezone.utc),
        )


def test_runtime_normalizes_front_matter_and_utc_update_date() -> None:
    module = _candidate()
    baseline = module.parse_current_front_matter_baseline(_documents())
    normalized = module.normalize_planner_documents(
        _documents(),
        baseline,
        datetime(2026, 7, 27, 23, 30, tzinfo=timezone.utc),
    )
    assert b'\xe6\x9c\x80\xe7\xb5\x82\xe6\x9b\xb4\xe6\x96\xb0: "2026-07-27"\n' in normalized["plan.md"]
    assert b"\r" not in normalized["plan.md"]
    assert normalized["plan.md"].endswith(b"\n")
    assert not normalized["plan.md"].endswith(b"\n\n")


@pytest.mark.parametrize(
    "body",
    [
        "## Section\n\nText.\n",
        "# iss-00003 Issue Title\n\nText.\n",
        "# iss-00003 Issue Title\n\n## Empty\n\n### Child\n",
    ],
)
def test_document_completeness_rejects_missing_h1_missing_h2_and_empty_h2(body: str) -> None:
    documents = _documents()
    documents["plan.md"] = _document("plan.md", body=body)
    module = _candidate()
    baseline = module.parse_current_front_matter_baseline(_documents())
    with pytest.raises(ValueError, match="complete"):
        module.normalize_planner_documents(
            documents,
            baseline,
            datetime(2026, 7, 28, tzinfo=timezone.utc),
        )


def test_document_completeness_accepts_table_list_and_fenced_content() -> None:
    module = _candidate()
    baseline = module.parse_current_front_matter_baseline(_documents())
    bodies = (
        "# iss-00003 Issue Title\n\n## Table\n\n| a | b |\n| - | - |\n",
        "# iss-00003 Issue Title\n\n## List\n\n- item\n",
        "# iss-00003 Issue Title\n\n## Code\n\n```\nvalue\n```\n",
    )
    for body in bodies:
        documents = _documents()
        documents["plan.md"] = _document("plan.md", body=body)
        module.normalize_planner_documents(
            documents,
            baseline,
            datetime(2026, 7, 28, tzinfo=timezone.utc),
        )


def test_canonical_control_json_is_compact_utf8_sorted_and_lf_terminated() -> None:
    module = _candidate()
    encoded = module.canonical_control_json_bytes({"日本語": 1, "a": {"z": 2, "b": 1}})
    assert encoded == '{"a":{"b":1,"z":2},"日本語":1}\n'.encode()
    with pytest.raises(ValueError, match="float"):
        module.canonical_control_json_bytes({"value": 1.0})
    with pytest.raises(ValueError, match="canonical"):
        module.parse_canonical_control_json(b'{"a":1, "b":2}\n')


def test_source_baseline_binds_exact_s02_source_evidence_context_and_payload() -> None:
    material = _material()
    baseline = json.loads(material.files["SOURCE-BASELINE.json"])
    context, evidence = _source()
    payload = b"exact authoring zip bytes"
    assert len(baseline) == 17
    assert baseline["canonical_issue_paths"] == list(context.canonical_issue_paths)
    assert baseline["remote_head_disposition"] == evidence.remote_head_disposition
    assert baseline["planner_payload_sha256"] == hashlib.sha256(payload).hexdigest()
    assert baseline["planner_payload_size"] == len(payload)


def test_v1_naming_uses_one_utc_second_instant() -> None:
    material = _material()
    assert material.created_at_utc == "2026-07-28T12:00:00Z"
    assert material.candidate_id == "iss-00003-v1-20260728t120000z"
    assert material.logical_filename == ("20260728t120000z-iss-00003-issue-planning-candidate-v1.zip")
    assert material.internal_root == material.logical_filename.removesuffix(".zip")


def test_s10_manifest_has_exact_eight_sorted_entries_and_one_companion_role() -> None:
    material = _material()
    manifest = json.loads(material.files["MANIFEST.json"])
    paths = [entry["path"] for entry in manifest["entries"]]
    assert paths == sorted(material.files, key=lambda value: value.encode())
    assert len(paths) == 8
    companion_entries = [entry for entry in manifest["entries"] if entry["role"] == "onboarding-companion"]
    assert companion_entries == [
        {
            "checksum_covered": True,
            "content_mode": "static",
            "path": COMPANION_PATH,
            "role": "onboarding-companion",
        }
    ]


def test_manifest_does_not_contain_external_zip_sha_or_observed_filename() -> None:
    manifest = _material().files["MANIFEST.json"]
    assert b"zip_sha256" not in manifest
    assert b"observed_transport_filename" not in manifest


def test_checksums_cover_every_entry_except_self_in_utf8_order() -> None:
    material = _material()
    lines = material.files["CHECKSUMS.sha256"].decode("ascii").splitlines()
    expected = sorted(set(material.files) - {"CHECKSUMS.sha256"}, key=lambda value: value.encode())
    assert [line.split("  ", 1)[1] for line in lines] == expected
    for line in lines:
        digest, path = line.split("  ", 1)
        assert digest == hashlib.sha256(material.files[path]).hexdigest()


def test_placeholder_oracle_accepts_resolved_declared_dynamic_tokens() -> None:
    module = _candidate()
    findings = module.validate_placeholder_oracle(
        {"design.md": b"resolved\n"},
        {
            "files": [{"path": "design.md", "tokens": ["{{SPECDOCK_EXAMPLE_TOKEN}}"]}],
            "schema_version": "spec-dock.issue-candidate-placeholder-map.v1",
        },
    )
    assert findings == ()


def test_placeholder_oracle_rejects_remaining_and_undeclared_dynamic_tokens() -> None:
    module = _candidate()
    findings = module.validate_placeholder_oracle(
        {"design.md": b"{{SPECDOCK_EXAMPLE_TOKEN}} {{SPECDOCK_OTHER_TOKEN}}\n"},
        {
            "files": [{"path": "design.md", "tokens": ["{{SPECDOCK_EXAMPLE_TOKEN}}"]}],
            "schema_version": "spec-dock.issue-candidate-placeholder-map.v1",
        },
    )
    assert findings == ("remaining_placeholder", "undeclared_placeholder")


def test_placeholder_oracle_does_not_scan_static_literal_examples() -> None:
    assert (
        _candidate().validate_placeholder_oracle(
            {"design.md": b"{{SPECDOCK_LITERAL_EXAMPLE}}\n"},
            {
                "files": [],
                "schema_version": "spec-dock.issue-candidate-placeholder-map.v1",
            },
        )
        == ()
    )


def test_identity_is_derived_from_controls_and_actual_zip_bytes() -> None:
    module = _candidate()
    material = _material()
    identity = module.derive_candidate_identity(
        material,
        b"actual zip bytes",
        observed_transport_filename=material.logical_filename,
    )
    assert identity.candidate_id == material.candidate_id
    assert identity.internal_root == material.internal_root
    assert identity.zip_sha256 == hashlib.sha256(b"actual zip bytes").hexdigest()


def test_create_identity_observed_filename_equals_logical_filename() -> None:
    module = _candidate()
    material = _material()
    identity = module.derive_candidate_identity(
        material,
        b"zip",
        observed_transport_filename=material.logical_filename,
    )
    assert identity.observed_transport_filename == identity.logical_filename


def test_candidate_verifier_rejects_fuzzy_name_wrong_root_repack_and_hash_mismatch() -> None:
    module = _candidate()
    material = _material()
    with pytest.raises(ValueError, match="transport alias"):
        module.derive_candidate_identity(
            material,
            b"zip",
            observed_transport_filename="renamed.zip",
        )
    assert "manifest_identity_mismatch" in module.verify_issue_candidate_files(
        material.files,
        "wrong-root",
    )
    changed = dict(material.files)
    changed["plan.md"] = b"repacked\n"
    assert "checksum_mismatch" in module.verify_issue_candidate_files(changed, material.internal_root)


def test_candidate_verifier_rejects_non_array_placeholder_files_without_exception() -> None:
    module = _candidate()
    material = _material()
    changed = dict(material.files)
    placeholder = module.canonical_control_json_bytes({
        "files": 1,
        "schema_version": "spec-dock.issue-candidate-placeholder-map.v1",
    })
    manifest = json.loads(changed["MANIFEST.json"])
    manifest["placeholder_oracle_map_sha256"] = hashlib.sha256(placeholder).hexdigest()
    changed["PLACEHOLDER-ORACLE-MAP.json"] = placeholder
    changed["MANIFEST.json"] = module.canonical_control_json_bytes(manifest)
    changed["CHECKSUMS.sha256"] = _checksums(module, changed)
    findings = module.verify_issue_candidate_files(changed, material.internal_root)
    assert "invalid_placeholder_map" in findings


def test_candidate_verifier_rejects_boolean_manifest_version() -> None:
    module = _candidate()
    material = _material()
    changed = dict(material.files)
    manifest = json.loads(changed["MANIFEST.json"])
    manifest["candidate"]["version"] = True
    changed["MANIFEST.json"] = module.canonical_control_json_bytes(manifest)
    changed["CHECKSUMS.sha256"] = _checksums(module, changed)
    findings = module.verify_issue_candidate_files(changed, material.internal_root)
    assert "manifest_identity_mismatch" in findings


def _checksums(module, files: dict[str, bytes]) -> bytes:
    companion = next(path for path in files if path.startswith("artifacts/"))
    return "".join(
        f"{hashlib.sha256(files[path]).hexdigest()}  {path}\n" for path in module.checksum_paths(companion)
    ).encode("ascii")
