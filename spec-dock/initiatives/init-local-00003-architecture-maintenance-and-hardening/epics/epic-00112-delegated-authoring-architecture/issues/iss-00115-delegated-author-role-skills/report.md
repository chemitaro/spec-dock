---
種別: 実装報告書（Issue）
ID: "iss-00115"
タイトル: "Delegated Author Role Skills"
関連GitHub: ["#115"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-05-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00115 Delegated Author Role Skills — 実装報告（Observed Evidence Ledger）

## Spec Interpretation / Decision Ledger

| ID | Status | Type | Raised By | Trigger / Gap | Options Considered | Decision / Interpretation | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | implementation | orchestrator | role skills must be copied/visible as managed install_root assets, not only documented | skill files only; managed list + parity tests; host role registry | Add the two role skills to install_root, dogfooding mirror, managed skill names, and existing managed-asset parity/inventory tests. | Without the managed list, init/update would not ship the role skills even if provider files existed. This is installer asset registration, not a write-capable delegation registry. | applied | `src/spec_dock/cli.py`, `tests/cli_runtime/harness.py`, `tests/test_init_update.py`, targeted tests | none |

## 実装サマリー

- `spec-dock-system-architect` と `spec-dock-implementation-planner` の provider-first role skill を `src/spec_dock/assets/install_root/.agents/skills/` に追加した。
- dogfooding mirror `.agents/skills/` に同内容を反映し、hub skill から draft-only role skill として参照できるようにした。
- managed skill list、authoritative inventory、checked-in parity、routing/content assertions を更新し、init/update で role skills が shipped managed asset として扱われることを確認した。

## Delegated Draft Evidence

- delegated authoring use:
  - not used for this implementation report
- If not used:
  - manual implementation path; no delegated draft was used as promotion evidence.

| role | phase | scope | consent | source artifacts | draft artifact path | status | integration result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| N/A | implementation | iss-00115 | N/A | active issue docs and parent Epic docs | N/A | not used | manual implementation | N/A | none | code/QA/spec pass | no delegated draft promotion |

## 実装記録（セッションログ）

### 2026-05-23 S01 Provider Role Skill Contract

#### 対象
- Step: S01
- AC/EC: AC-001
- Planned source:
  - `plan.md` section: `S01 — Provider source update`
  - closure ids: tc-001

#### 実施内容
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md` を追加した。
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md` を追加した。
- `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` に draft-only role skill routing を追加した。
- `src/spec_dock/cli.py` の managed skill list に2つの role skill を追加した。

#### 実行コマンド / 結果
```bash
uv run python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_assets_cover_managed_manifest -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_install_root_tree_exists -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root -v
# OK
```

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S01 | alternative | inspect-only | Provider install_root did not contain the two role skill contracts before this issue. | pre-change file inventory | pass | docs/skill asset issue; no failing runtime behavior needed before adding files. |
| S01 | Green | provider source contains role skill contracts | Required output sections, blocker behavior, forbidden actions, and draft evidence fields are present in role skills; managed manifest includes both names. | bundled asset and routing tests | pass | Covers AC-001 and role-contract baseline. |
| S01 | Refactor | guardrail satisfied | Changes are limited to provider role skills, hub routing, and managed asset registration/tests. | diff inspection | pass | No write-capable delegation, runtime validation, `.github/agents`, or Copilot support added. |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | tc-001 | target provider source is updated and inspected | provider role skills and hub routing exist; managed list and content assertions pass | pass | code-reviewer, QA, and final spec-reviewer pass |

### 2026-05-23 S02 Dogfooding Parity and Verification

#### 対象
- Step: S02
- AC/EC: AC-002, EC-002
- Planned source:
  - `plan.md` section: `S02 — Dogfooding parity and verification`
  - closure ids: tc-002, tc-005

#### 実施内容
- `.agents/skills/spec-dock-system-architect/SKILL.md` を dogfooding mirror として追加した。
- `.agents/skills/spec-dock-implementation-planner/SKILL.md` を dogfooding mirror として追加した。
- `.agents/skills/spec-driven-tdd-workflow/SKILL.md` に provider と同じ routing 変更を反映した。
- `tests/cli_runtime/harness.py` と `tests/test_init_update.py` の managed skill / install_root / checked-in parity coverage を更新した。

#### 実行コマンド / 結果
```bash
uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_issue_70_build_plan_uses_install_root_recursive_inventory_including_workflow -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_update_migrates_legacy_single_skill_and_preserves_custom_skill -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_update_installs_full_skill_set_for_legacy_no_skill_repo -v
# OK

uv run python -m unittest tests.test_init_update.TestInitUpdate.test_update_skill_sync_converges_after_interrupted_run -v
# OK

python -m unittest \
  tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract \
  tests.test_init_update.TestInitUpdate.test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets \
  tests.test_init_update.TestInitUpdate.test_issue_68_install_root_tree_exists \
  tests.test_init_update.TestInitUpdate.test_issue_68_authoritative_inventory_paths_are_classified_under_install_root \
  tests.test_init_update.TestInitUpdate.test_update_installs_full_skill_set_for_legacy_no_skill_repo \
  -v
# Ran 5 tests in 0.155s
# OK

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=57

./spec-dock/scripts/spec-dock sync
# spec-dock: ok (sync) wrote generated index/tree/deps/dashboard artifacts

git diff --check
# pass for tracked working-tree diff before staging; staged diff-check recorded before commit

git diff --cached --check
# pass after staging new role skill files
```

#### Red/Green/Refactor Evidence
| step | phase | planned evidence requirement | observed evidence | command / inspection / manual record | result | notes |
|---|---|---|---|---|---|---|
| S02 | Green | dogfooding mirrors and managed asset parity reflect provider change | checked-in `.agents` mirrors match install_root; init/update install the full skill set including the new role skills; validate/sync pass. | parity, init, update, build-plan tests, validate, sync | pass | Covers AC-002 and EC-002. |
| S02 | Refactor | guardrail satisfied | No unrelated implementation refactor; role skills remain draft-only Markdown contracts. | `git diff --check` | pass | Scope remains provider-first role skill asset delivery. |

#### Step Contract Closure
| step | closure ids | close condition from plan | observed evidence | result | notes |
|---|---|---|---|---|---|
| S02 | tc-002, tc-005 | parity/verification evidence is recorded | checked-in parity and init/update tests pass; validate/sync/diff-check pass | pass | code-reviewer, QA, and final spec-reviewer pass |

## Closure Coverage

| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-001 | S01 | provider files, managed skill list, bundled asset/routing tests | pass | role skill contracts exist |
| tc-002 | S02 | checked-in parity, build-plan, init/update managed skill tests, validate, sync, diff-check | pass | dogfooding mirrors and managed delivery covered |
| tc-003 | S99 | final spec-reviewer | pass | no P0/P1 findings after validation evidence, reviewer gate, and planner SoT fixes |
| tc-004 | S90 | report exception evidence | pass | no host/path uncertainty; package artifact test limitation recorded below |
| tc-005 | S02 | checked-in provider/consumer parity test | pass | no unintended drift |

## Closure Delta

| change | closure id | test id alias | resolves to closure id | reason | plan amendment required | re-review required |
|---|---|---|---|---|---|---|
| none | tc-001..tc-005 | targeted asset/routing/parity tests | tc-001..tc-005 | no closure contract change | no | no |

## Workflow Delegation Consent

| consent source | repo/worktree | active issue | session | named roles | boundary | expires / invalidation condition | denied / unavailable reason | next action |
|---|---|---|---|---|---|---|---|---|
| user objective to execute all Epic issues with referenced issue-execution workflow | current repo/worktree | iss-00115 | current session | spec-reviewer, code-reviewer, qa-reviewer | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

## Implementation Delegation Gate

| step | decision | required reason | delegated role | delegated scope | source of truth | allowed changes | forbidden changes | required verification | stop conditions | output required | observed result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01/S02 | approved-local-execution | small coherent provider/mirror/test update | N/A | role skill assets and parity tests | active issue docs and parent Epic docs | provider role skills, dogfooding mirrors, managed skill list, tests, report | write-capable delegation, runtime validation, role registry, `.github/agents`, GitHub mutation | targeted tests, validate/sync, reviewer gates | test/review failure | changed files, verification, risks | pass |

## Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S01/S02 | step reviewer | code-reviewer | fresh | pass | N/A | proceed to final review | P2 requested validate/sync evidence in report; evidence is now recorded |
| S01/S02 | QA reviewer | qa-reviewer | fresh | pass | N/A | proceed to final review | no P0/P1 QA blockers; package artifact test limitation accepted as environment-only |
| S01/S02/S99 | final reviewer | spec-reviewer | fresh | pass | N/A | proceed to commit and issue finish | P3 requested diff-check qualification for untracked files; staged diff-check is recorded before commit |

## Step Commit Gate

| step | closure state | commit scope | commit hash / final ledger | post-commit clean check | no-op rationale | no-op checked contracts / files | no-op diff-clean command | no-op read-only confirmation |
|---|---|---|---|---|---|---|---|---|
| S01/S02 | pending commit | role skills, managed skill registration, mirrors, tests, report | pending | pending | N/A | N/A | N/A | N/A |

## 変更したファイル

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md` - system architect role skill.
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-implementation-planner/SKILL.md` - implementation planner role skill.
- `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md` - hub routing.
- `.agents/skills/spec-dock-system-architect/SKILL.md` - dogfooding mirror.
- `.agents/skills/spec-dock-implementation-planner/SKILL.md` - dogfooding mirror.
- `.agents/skills/spec-driven-tdd-workflow/SKILL.md` - dogfooding hub mirror.
- `src/spec_dock/cli.py` - managed skill registration.
- `tests/cli_runtime/harness.py` - expected managed skill names.
- `tests/test_init_update.py` - managed asset inventory, parity, and role contract assertions.
- `spec-dock/active/issue/report.md` - observed evidence ledger.

## Final Quality Gate

### S90 Docs Impact Resolution
| target | update required | owner | evidence | spec-reviewer result |
|---|---|---|---|---|
| role skills | yes | approved-local-execution | provider and dogfooding role skills added; implementation-planner SoT includes `workflow_issue.md` and `authoring/issue-plan.md` | pass |
| workflow hub skill | yes | approved-local-execution | draft-only routing added | pass |
| managed asset tests | yes | approved-local-execution | targeted tests, validate, sync, tracked diff-check pass; staged diff-check recorded before commit | pass |

### Final QA Gate
| reviewer | scope | integration test decision | evidence | result |
|---|---|---|---|---|
| qa-reviewer | role skill obligation coverage | targeted asset/routing/parity/init/update tests are proportionate | targeted tests listed above; package artifact limitation reviewed as non-blocking | pass |

### Final Code Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | P2 validate/sync report evidence gap fixed | 1 | pass |

### Final Spec Review Gate
| reviewer | scope | findings / fixes | re-review count | result |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | P1 findings fixed; re-review passed with non-blocking P3 diff-check evidence qualification | 2 | pass |

### Final Commit
| final report ledger | final commit scope | post-commit external evidence destination | result |
|---|---|---|---|
| S01/S02 evidence recorded; code/QA/spec pass | role skills, managed skill registration, mirrors, tests, report | final response / Epic PR / GitHub issue lifecycle | pending commit |

## 遭遇した問題と解決
- 問題: `test_issue_69_full_install_root_inventory_is_packaged_in_wheel_sdist_and_installed_resources` はローカル `.venv` に `pip` が無く、artifact package verification 前に停止した。
  - 解決: この Issue の closure は managed asset parity / init-update tests で閉じ、package artifact test limitation を記録した。失敗理由は `No module named pip` で、role skill 実装差分由来ではない。

## 学んだこと
- install_root role skill を追加するだけでは不十分で、managed skill list と checked-in parity coverage まで更新して初めて init/update delivery が保証される。

## 今後の推奨事項
- 後続 Issue では、この2つの draft-only role skill を host adapter から薄く呼び出すだけに留め、canonical edit や reviewer pass claim を role 側へ広げない。

## 省略/例外メモ
- `.github/agents` / Copilot support、write-capable delegation、runtime validation は親 Epic の non-scope のため実装していない。
