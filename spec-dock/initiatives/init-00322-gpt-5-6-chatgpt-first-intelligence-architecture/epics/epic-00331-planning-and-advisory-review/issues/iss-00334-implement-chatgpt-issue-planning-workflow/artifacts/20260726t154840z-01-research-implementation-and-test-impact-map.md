---
種別: research
ID: "20260726t154840z-research-implementation-and-test-impact-map"
タイトル: "iss-00334 Direct Implementation and Test Impact Map"
状態: "package-evidence"
作成者: "Blue Team"
最終更新: "2026-07-27"
親: ["iss-00334", "epic-00331", "init-00322"]
authority: "evidence-only"
adoption_status: "unreviewed"
canonical_status: "non-authoritative"
reflected_to: []
---

# iss-00334 Direct Implementation and Test Impact Map

## Provider-first implementation

| Surface | Direct paths | Purpose |
|---|---|---|
| Independent CLI | `src/spec_dock/assets/spec_dock/scripts/spec-dock-chatgpt`, `.../chatgpt_app.py`, `.../cli/chatgpt_parser.py`, `.../commands/planning.py` | three public planning/review commands |
| Application/domain | `.../application/issue_planning.py`, `.../domain/issue_planning_contracts.py` | Planner response validation, create/revise/review/adoption/readiness orchestration and contracts |
| Runtime Candidate packaging | `.../application/issue_planning.py`, `.../infra/issue_planning_io.py` | three-document response to mandatory-control immutable ZIP, one identity owner, atomic final publication |
| Shared archive primitive | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py` | bounded named Issue Candidate contract while preserving the existing generic default |
| Infra/presentation | `.../infra/issue_planning_io.py`, `.../presentation/issue_planning.py` | external output, Git/Oracle integration, safe rendering |
| Prompt | `src/spec_dock/assets/spec_dock/system/prompts/issue-planning/*.md` | closed provider-managed Prompt inventory |
| Human entrypoint | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | official Skill route |
| Installer/docs | `src/spec_dock/cli.py`, provider docs | wheel/sdist/init/update projection and public reference |

## Focused verification

| Risk | Focused verification path |
|---|---|
| CLI and target resolution | `tests/cli_runtime/test_chatgpt_planning.py` |
| generic authoring-pack default compatibility | `tests/cli_runtime/test_authoring.py`, `tests/manual_tests/test_review_chatgpt_authoring_pack.py` |
| application conjunction | `tests/unit/application/test_issue_planning.py` |
| identity／readiness／PA-NF | `tests/unit/domain/test_issue_planning_contracts.py` |
| Issue Candidate packaging／archive safety | `tests/unit/infra/test_issue_planning_archive.py` |
| create final ZIP → archive Review direct handoff | `tests/integration/test_chatgpt_planning_fake_oracle.py` |
| rendering | `tests/unit/presentation/test_issue_planning.py` |
| wheel/sdist/init/update | `tests/unit/infra/test_init_update.py` |
| Human-selected real use | `tests/integration/test_chatgpt_planning_dogfood.py` |

## Projection rule

Provider paths are edited first. Installed and dogfood bytes are produced by build／init／update and compared; workers do not directly implement against the generated root `spec-dock/` tree. The shared archive change is additive and data-bounded; it does not create a second validator or change the current authoring-pack default.
