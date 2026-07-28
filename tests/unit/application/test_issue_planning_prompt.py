import hashlib
from pathlib import Path
import sys

import pytest

RUNTIME_SCRIPTS_DIR = (
    Path(__file__).resolve().parents[3] / "src" / "spec_dock" / "assets" / "spec_dock" / "scripts"
)
sys.path.insert(0, str(RUNTIME_SCRIPTS_DIR))

from spec_dock_runtime.application import issue_planning_prompt  # noqa: E402
from spec_dock_runtime.domain.issue_planning_contracts import PlanningContext  # noqa: E402


def _context(**changes: object) -> PlanningContext:
    values: dict[str, object] = {
        "issue_id": "iss-00003",
        "repository": "owner/repo",
        "branch": "feature/issue",
        "source_head": "a" * 40,
        "parent_epic_id": "epic-00002",
        "parent_initiative_id": "init-00001",
        "dependency_summary": ("iss-00001",),
        "canonical_issue_paths": (
            "spec-dock/initiatives/i/epics/e/issues/x/design.md",
            "spec-dock/initiatives/i/epics/e/issues/x/plan.md",
            "spec-dock/initiatives/i/epics/e/issues/x/requirement.md",
        ),
        "relevant_source_paths": ("src/example.py",),
        "operator_context": ("preserve approved scope",),
    }
    values.update(changes)
    return PlanningContext(**values)  # type: ignore[arg-type]


def _write_context_files(repo_root: Path) -> None:
    for path in (*_context().canonical_issue_paths, *_context().relevant_source_paths):
        target = repo_root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"content:{path}\n", encoding="utf-8")


def test_synthesize_prompt_is_deterministic_and_contains_source_identity(tmp_path: Path) -> None:
    _write_context_files(tmp_path)
    synthesize = issue_planning_prompt.synthesize_issue_planning_prompt
    first = synthesize(
        role="planner",
        context=_context(),
        repo_root=tmp_path,
        upstream="origin/feature/issue",
        remote_head="a" * 40,
    )
    second = synthesize(
        role="planner",
        context=_context(),
        repo_root=tmp_path,
        upstream="origin/feature/issue",
        remote_head="a" * 40,
    )
    assert first == second
    assert "owner/repo" in first.prompt
    assert "origin/feature/issue" in first.prompt
    assert first.attachments == tuple(sorted(first.attachments, key=lambda item: item[0].encode("utf-8")))


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"dependency_summary": tuple(f"iss-{index:05d}" for index in range(1, 34))}, "dependencies"),
        ({"relevant_source_paths": tuple(f"src/f{index}.py" for index in range(17))}, "relevant"),
        ({"operator_context": tuple("x" for _ in range(17))}, "operator"),
        ({"operator_context": ("token=abc123secret",)}, "sensitive"),
        ({"operator_context": ("/Users/alice/private/file",)}, "private"),
    ],
)
def test_synthesize_prompt_rejects_unbounded_or_sensitive_dynamic_context(
    tmp_path: Path,
    changes: dict[str, object],
    message: str,
) -> None:
    _write_context_files(tmp_path)
    synthesize = issue_planning_prompt.synthesize_issue_planning_prompt
    with pytest.raises(ValueError, match=message):
        synthesize(
            role="planner",
            context=_context(**changes),
            repo_root=tmp_path,
            upstream="origin/feature/issue",
            remote_head="a" * 40,
        )


def test_reviewer_prompt_is_read_only_defect_only_and_denies_authority(tmp_path: Path) -> None:
    _write_context_files(tmp_path)
    synthesize = issue_planning_prompt.synthesize_issue_planning_prompt
    prompt = synthesize(
        role="reviewer",
        context=_context(),
        repo_root=tmp_path,
        upstream="origin/feature/issue",
        remote_head="a" * 40,
    ).prompt.lower()
    assert "read-only" in prompt
    assert "defect-only" in prompt
    assert "patch" in prompt
    assert "zip" in prompt


def test_synthesize_prompt_scans_complete_dynamic_identity_block(tmp_path: Path) -> None:
    _write_context_files(tmp_path)
    with pytest.raises(ValueError, match="sensitive"):
        issue_planning_prompt.synthesize_issue_planning_prompt(
            role="planner",
            context=_context(branch="token=abc123secret"),
            repo_root=tmp_path,
            upstream="origin/token=abc123secret",
            remote_head="a" * 40,
        )
    with pytest.raises(ValueError, match="private"):
        issue_planning_prompt.synthesize_issue_planning_prompt(
            role="planner",
            context=_context(),
            repo_root=tmp_path,
            upstream="/private/host/repository",
            remote_head="a" * 40,
        )


def test_planner_prompt_contains_exact_inner_document_contract(tmp_path: Path) -> None:
    _write_context_files(tmp_path)
    prompt = issue_planning_prompt.synthesize_issue_planning_prompt(
        role="planner",
        context=_context(),
        repo_root=tmp_path,
        upstream="origin/feature/issue",
        remote_head="a" * 40,
    ).prompt
    filenames = ("requirement.md", "design.md", "plan.md")
    positions: list[int] = []
    for filename in filenames:
        start = f"<<<SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={filename}>>>"
        end = f"<<<END-SPECDOCK-ISSUE-PLANNING-DOCUMENT-V1 name={filename}>>>"
        assert prompt.count(start) == 1
        assert prompt.count(end) == 1
        positions.append(prompt.index(start))
    assert positions == sorted(positions)
    assert "no prose" in prompt.lower()


def test_review_prompt_classifies_exact_targets_and_formal_evidence() -> None:
    attachment = issue_planning_prompt.PlanningPromptAttachment
    identity = b'{"mode":"archive-candidate"}\n'
    candidate = b"PK\x03\x04exact candidate bytes"
    synthesized = issue_planning_prompt.synthesize_planning_evidence_prompt(
        role="reviewer",
        source_head="a" * 40,
        repository="owner/repo",
        branch="feature/issue",
        exact_attachments=(
            attachment(
                name="target-candidate.zip",
                classification="review-target",
                source_label="candidate.zip",
                content=candidate,
            ),
            attachment(
                name="reviewed-identity.json",
                classification="formal-evidence",
                source_label="reviewed-identity.json",
                content=identity,
            ),
        ),
    )
    assert synthesized.exact_attachments[0].content == candidate
    assert "review-target" in synthesized.prompt
    assert hashlib.sha256(candidate).hexdigest() in synthesized.prompt


def test_semantic_revision_prompt_is_self_contained_without_session_locator() -> None:
    attachment = issue_planning_prompt.PlanningPromptAttachment
    synthesized = issue_planning_prompt.synthesize_planning_evidence_prompt(
        role="planner",
        source_head="a" * 40,
        repository="owner/repo",
        branch="feature/issue",
        exact_attachments=(
            attachment(
                name="prior-candidate.zip",
                classification="review-target",
                source_label="candidate.zip",
                content=b"candidate",
            ),
            attachment(
                name="planning-review-result.json",
                classification="formal-evidence",
                source_label="planning-review-result.json",
                content=b'{"verdict":"fail"}',
            ),
        ),
        instructions=("selected finding: F-1", "preserve assumption: boundary"),
    )
    assert "selected finding: F-1" in synthesized.prompt
    assert "preserve assumption: boundary" in synthesized.prompt
    assert "session_locator" not in synthesized.prompt
