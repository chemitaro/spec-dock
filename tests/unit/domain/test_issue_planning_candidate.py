from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))


def _candidate():
    return __import__(
        "spec_dock_runtime.domain.issue_planning_candidate",
        fromlist=["parse_planner_payload"],
    )


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


def _payload(documents: dict[str, bytes] | None = None) -> bytes:
    docs = documents or _documents()
    chunks: list[bytes] = []
    names = ("requirement.md", "design.md", "plan.md")
    for index, name in enumerate(names):
        chunks.extend(
            (
                f"<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={name}>>>\n".encode(),
                docs[name],
                f"<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={name}>>>".encode()
                + (b"\n" if index < len(names) - 1 else b""),
            )
        )
    return b"".join(chunks)


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
    payload = _payload(documents)
    return module.build_candidate_material(
        planner_documents=module.parse_planner_payload(payload),
        baseline=baseline,
        context=context,
        source_evidence=evidence,
        planner_payload=payload,
        operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
    )


def test_revision_candidate_uses_prior_version_plus_one() -> None:
    module = _candidate()
    documents = _documents()
    baseline = module.parse_current_front_matter_baseline(documents)
    context, evidence = _source()
    payload = _payload(documents)
    material = module.build_candidate_material(
        planner_documents=module.parse_planner_payload(payload),
        baseline=baseline,
        context=context,
        source_evidence=evidence,
        planner_payload=payload,
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
    payload = _payload(documents)
    with pytest.raises(ValueError, match="version"):
        module.build_candidate_material(
            planner_documents=module.parse_planner_payload(payload),
            baseline=baseline,
            context=context,
            source_evidence=evidence,
            planner_payload=payload,
            operation_time=datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc),
            version=version,
        )


def test_mechanical_revision_replaces_one_target_body_match_with_utf8_budget() -> None:
    module = _candidate()
    documents = _documents()
    old = "Substantive"
    new = "具体的"
    cost = len(old.encode()) + len(new.encode())
    revised = module.apply_mechanical_revision(
        documents,
        target_file="plan.md",
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
            documents,
            target_file="plan.md",
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
            documents,
            target_file="plan.md",
            old_text=old_text,
            new_text="replacement",
            diff_budget=100,
        )


def test_parse_planner_payload_accepts_exact_three_document_grammar() -> None:
    parsed = _candidate().parse_planner_payload(_payload())
    assert tuple(parsed) == ("requirement.md", "design.md", "plan.md")
    assert parsed == _documents()


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "extra", "unknown", "reordered"])
def test_parse_planner_payload_rejects_missing_duplicate_extra_and_reordered_documents(
    mutation: str,
) -> None:
    payload = _payload()
    requirement = (
        b"<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name=requirement.md>>>\n"
        + _documents()["requirement.md"]
        + b"<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name=requirement.md>>>\n"
    )
    if mutation == "missing":
        payload = payload.replace(requirement, b"")
    elif mutation == "duplicate":
        payload = requirement + payload
    elif mutation == "extra":
        payload += b"outside"
    elif mutation == "unknown":
        payload = payload.replace(b"name=requirement.md", b"name=notes.md", 1)
    else:
        payload = payload.replace(requirement, b"") + requirement
    with pytest.raises(ValueError, match="planner"):
        _candidate().parse_planner_payload(payload)


@pytest.mark.parametrize(
    "payload",
    [
        b"\xef\xbb\xbf" + _payload(),
        _payload().replace(b"\n", b"\r\n", 1),
        _payload() + b"\0",
        b"\xff",
        _payload().replace(b"Substantive content.", b"<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 nope"),
    ],
)
def test_parse_planner_payload_rejects_bom_cr_nul_invalid_utf8_and_reserved_marker_body(
    payload: bytes,
) -> None:
    with pytest.raises(ValueError, match="planner"):
        _candidate().parse_planner_payload(payload)


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
    payload = _payload()
    assert len(baseline) == 17
    assert baseline["canonical_issue_paths"] == list(context.canonical_issue_paths)
    assert baseline["remote_head_disposition"] == evidence.remote_head_disposition
    assert baseline["planner_payload_sha256"] == hashlib.sha256(payload).hexdigest()
    assert baseline["planner_payload_size"] == len(payload)


def test_v1_naming_uses_one_utc_second_instant() -> None:
    material = _material()
    assert material.created_at_utc == "2026-07-28T12:00:00Z"
    assert material.candidate_id == "iss-00003-v1-20260728t120000z"
    assert material.logical_filename == (
        "20260728t120000z-iss-00003-issue-planning-candidate-v1.zip"
    )
    assert material.internal_root == material.logical_filename.removesuffix(".zip")


def test_manifest_has_exact_seven_sorted_entries() -> None:
    material = _material()
    manifest = json.loads(material.files["MANIFEST.json"])
    paths = [entry["path"] for entry in manifest["entries"]]
    assert paths == sorted(material.files, key=lambda value: value.encode())
    assert len(paths) == 7


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
    placeholder = module.canonical_control_json_bytes(
        {
            "files": 1,
            "schema_version": "spec-dock.issue-candidate-placeholder-map.v1",
        }
    )
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
    return "".join(
        f"{hashlib.sha256(files[path]).hexdigest()}  {path}\n"
        for path in module.CHECKSUM_PATHS
    ).encode("ascii")
