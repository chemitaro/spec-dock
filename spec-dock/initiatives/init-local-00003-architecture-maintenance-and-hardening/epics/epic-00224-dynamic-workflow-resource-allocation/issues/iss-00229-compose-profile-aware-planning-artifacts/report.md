---
種別: 実装報告書（Issue）
ID: "iss-00229"
タイトル: "Compose Profile Aware Planning Artifacts"
関連GitHub: ["#229"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00229 Compose Profile Aware Planning Artifacts — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）
| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | scope | orchestrator | I03 の対象が planning artifact composition と stale source binding に集中する一方、I04 の step routing と重なりやすい | A: Step routing まで I03 に含める; B: I03 は artifact composition / stale binding に限定する | B を採用 | Epic plan が I03 と I04 を別 slice として定義し、I04 は step assurance / routing / context policy を閉じるため | applied | `requirement.md` Scope / `design.md` 禁止 / `plan.md` S01-S03 | none |
| D-002 | resolved | interpretation | orchestrator | `lite_candidate` を planning section 削減に使うか | A: candidate で Lite sections にする; B: `authorized_profile` だけで section set を決める | B を採用 | Accepted ADR が `authorized_profile` only を authority として固定しているため | applied | `requirement.md` 非交渉制約 / `design.md` invariant / `plan.md` tc-001 | none |
| D-003 | resolved | implementation | orchestrator | stale source binding を `assurance verify` だけで扱うか、`workflow next` でも block するか | A: verify only; B: verify + workflow block | B を採用 | fixed Skill kernel の first-read は `workflow next` であり、execution handoff をそこで止める必要があるため | promoted_to_design | `design.md` Interface contract / `plan.md` S03 | none |
| D-004 | resolved | interpretation | spec-reviewer | explicit `authorized_profile=lite` の扱いが曖昧 | A: Lite は I07 まで fail-closed; B: automatic default は禁止しつつ、明示 Lite authorization は I03 の profile preset として compose する | B を採用 | Accepted ADR は automatic Lite default を禁止しているが、`authorized_profile` を authority として固定しているため | applied | `requirement.md` AC-001 / `design.md` invariant / `plan.md` tc-001 | none |
| D-005 | resolved | plan | spec-reviewer | step-local delegation contract and concrete test cards were missing from implementation plan | A: keep compact plan; B: add required per-step schema sections | B を採用 | `docs/authoring/issue-plan.md` requires delegation contract and concrete test cards for implementation readiness | applied | `plan.md` S01-S03/S90/S99 delegation contracts and concrete tests | none |
| D-006 | resolved | test-strategy | spec-reviewer | stale source binding coverage did not explicitly include compose failure or design/plan stale hashes | A: requirement-only stale verify/workflow tests; B: compose/verify/workflow tests across requirement/design/plan stale cases | B を採用 | Requirement/design/plan stale authority must not produce planning sections or execution handoff | applied | `requirement.md` AC-004 / `design.md` Source binding / `plan.md` tc-s02-003 and tc-s03-001..004 | none |
| D-007 | resolved | plan | spec-reviewer | S02 and S03 both appeared to own stale compose blocking while S02 forbade stale policy changes | A: let S02 implement stale checker; B: keep S02 to compose vertical slice and assign stale compose/verify/workflow blocking to S03 | B を採用 | S03 is the explicit stale source binding integration step and can include compose command wiring without changing section content rules | applied | `plan.md` S02/S03 ownership and allowed paths | none |
| D-008 | resolved | plan | dev-coder | S02 allowed paths omitted CLI parser/bootstrap registration surfaces required for `assurance compose` | A: keep S02 limited and fail targeted CLI tests; B: amend S02 allowed paths to include `cli/parser.py` and `cli/bootstrap.py` | B を採用 | The requested user-facing CLI subcommand cannot be reachable without parser registration and UseCases wiring | promoted_to_plan | `plan.md` S02 allowed paths / amendment trigger | none |
| D-009 | resolved | plan | orchestrator | S03 requires persisted contract validation to accept design/plan source binding roles | A: keep validation requirement-only; B: amend S03 allowed paths to include `domain/assurance.py` role validation | B を採用 | Planning source binding cannot persist design/plan hashes while domain validation rejects those roles | promoted_to_plan | `plan.md` S03 allowed paths / `domain/assurance.py` | none |
| D-010 | resolved | compatibility | code-reviewer | pre-S03 partial source binding could omit design/plan and bypass stale detection | A: compare only persisted artifacts; B: require requirement/design/plan roles in persisted adaptive contracts | B を採用 | Fail-closed source authority requires all planning artifacts to be bound; partial legacy bindings are invalid schema rather than execution-ready authority | applied | `domain/assurance.py`; `tests/unit/infra/test_assurance_store.py` partial binding regression | none |
| D-011 | resolved | compose-idempotence | orchestrator | `assurance compose` mutates design/plan/report after classification and would otherwise stale its own next run | A: require manual re-classification after compose; B: after successful non-dry-run compose writes, refresh contract source binding to current planning artifact hashes | B を採用 | Compose-owned deterministic managed section writes are the same operation that changes planning artifacts; refreshing binding preserves idempotent second compose while human edits before compose still fail closed | applied | `application/assurance.py`; `tests/cli_runtime/test_assurance_compose.py` second-run and stale tests | none |
| D-012 | resolved | validation | code-reviewer | persisted contract could include all roles but bind a role to the wrong issue-local artifact path | A: only require role presence; B: require role-to-canonical-filename mapping for requirement/design/plan | B を採用 | Fail-closed stale detection must compare each role against its canonical planning artifact, not any issue-local file with a matching hash | applied | `domain/assurance.py`; `tests/unit/infra/test_assurance_store.py` role/path mismatch regression | none |
| D-013 | resolved | validation | code-reviewer | same basename under nested issue-local path could satisfy role-to-filename suffix validation | A: accept any issue-local `*/design.md`; B: require target-aware exact canonical path `issue_dir/<role>.md` | B を採用 | Canonical planning authority is the issue artifact itself; nested same-named files must not become source authority | applied | `infra/assurance_store.py`; `tests/unit/infra/test_assurance_store.py` nested same-name regression | none |
| D-014 | resolved | write-safety | code-reviewer | `assurance.json` symlink could be overwritten by classify/compose contract writes | A: rely on issue-local target resolution; B: reject symlinked contract paths before `write_bytes` | B を採用 | Contract writes are authority writes and must not follow symlink targets outside the issue/repo boundary | applied | `infra/assurance_store.py`; `tests/unit/infra/test_assurance_store.py` contract symlink regression | none |
| D-015 | resolved | test-coverage | qa-reviewer | `assurance compose --artifact design|plan|report` individual selections lacked direct CLI coverage | A: accept all-only coverage; B: add focused single-artifact compose test | B を採用 | The CLI contract exposes individual artifact selection and write scoping should be protected against regressions | applied | `tests/cli_runtime/test_assurance_compose.py` | none |
| D-016 | resolved | write-safety | code-reviewer | `assurance compose` could mutate planning artifacts before failing on symlinked `assurance.json` refresh | A: keep write guard inside `write_contract`; B: preflight contract write path before artifact writes when compose has changes | B を採用 | Compose must be fail-closed and non-partial when authority contract write would be rejected | applied | `application/assurance.py`; `infra/assurance_store.py`; `tests/cli_runtime/test_assurance_compose.py` | none |
| D-017 | resolved | pr-observation | code-reviewer | wait loop treated failed required `statusCheckRollup` as pending wait | A: any non-success rollup waits; B: distinguish failed rollup from pending rollup and return `failed/fix_ci` | B を採用 | Failed required checks are actionable CI failures, while pending required checks should continue wait/resume | applied | `pr_observation_wait.py`; `tests/unit/infra/test_init_update.py` | none |
| D-018 | resolved | pr-observation | code-reviewer | failed legacy status context with `state=FAILURE` and no conclusion still mapped to pending wait | A: only conclusion failures fail; B: state failures also map to `failed/fix_ci` | B を採用 | Legacy status contexts may express failure in `state`; wait should not time out on actionable CI failure | applied | `pr_observation_wait.py`; `tests/unit/infra/test_init_update.py` | none |

## 証跡採用台帳（Evidence Adoption Ledger）
| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | issue draft requirement | `requirement.md` | I03 の目的、scope、AC、依存が Epic plan と一致しているため | `discussions/20260623t033601z-draft-requirement-draft-requirement.md` | none |
| EAL-002 | adopted | issue draft design | `design.md` / `plan.md` | Artifact Composer、source binding stale、provider/mirror target が実装設計に必要な粒度で示されているため | `discussions/20260623t033605z-draft-design-draft-design.md` | none |
| EAL-003 | adopted | epic plan | `requirement.md` / `design.md` / `plan.md` | I03 の closes / dependencies / non-goals / tranche を canonical issue docs へ反映するため | `../plan.md` I03 / dependency commands | none |
| EAL-004 | adopted | accepted ADR | `requirement.md` / `design.md` | `authorized_profile` authority、generated Runbook non-authority、fixed Skill kernel と衝突しない artifact composition を固定するため | `../discussions/20260623t074443z-adr-adaptive-assurance-lite-authorization-monotonic-escalation.md`; `../discussions/20260623t074441z-adr-fixed-skill-kernel-compiled-runbook-authority.md` | none |
| EAL-005 | adopted | source inspection | `design.md` / `plan.md` | Current Assurance / Workflow runtime の既存責務境界を反映するため | `domain/assurance.py`; `infra/assurance_store.py`; `application/workflow.py`; `tests/cli_runtime/test_assurance.py` | none |

## 目的整合台帳（Objective Alignment Ledger）
| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| planning artifact composer | `assurance compose` / profile manifest / managed section rules が AC-001〜AC-003 を直接閉じる | stale source binding / mirror parity / final quality gates を S03/S90/S99 に配置 | low | spec-reviewer pass after stale compose ownership fix |

## 仕様 authoring ゲート（Spec Authoring Gate）
| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | issue draft requirement, Epic plan I03, accepted ADRs | explicit Lite authorized-profile handling clarified | adopted | passed | no | promote to implementation readiness |
| design | issue draft design, current assurance/workflow runtime, tests | explicit Lite preset invariant clarified | adopted | passed | no | promote to implementation readiness |
| plan | Epic dependency plan, issue design, existing verification lanes | per-step commit/no-op/report/amendment gates, concrete test cards, stale compose ownership and requirement/design/plan source coverage added | manual authoring from accepted sources | passed | no | promote to implementation readiness |

## 委任ドラフト証跡（Delegated Draft Evidence）
- 委任 authoring の使用:
  - not used for canonical docs in this session.
- 未使用理由:
  - canonical requirement / design / plan は issue planning skill の authority rule に従い、main orchestrator が draft evidence を採用して作成した。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| orchestrator/imported draft | iss-00229 | `discussions/20260623t033601z-draft-requirement-draft-requirement.md` | Epic plan / ADRs | `requirement.md` | adopted | `requirement.md` | manual diff guard | integrated | none | none | pending | promoted to canonical candidate |
| orchestrator/imported draft | iss-00229 | `discussions/20260623t033605z-draft-design-draft-design.md` | Epic plan / ADRs / runtime inspection | `design.md`, `plan.md` | adopted | `design.md`, `plan.md` | manual diff guard | integrated | none | none | pending | promoted to canonical candidate |

## 実装サマリー
- S01 で profile manifest と pure domain composer を追加した。
- S02 で `assurance compose` CLI と issue-local artifact write path を追加した。
- S03 で requirement/design/plan の source binding stale detection を `assurance compose` / `assurance verify` / `workflow next issue-execution` に接続した。
- S90 / S99 の実行結果、worker evidence、reviewer evidence、commit gates は後続ステップで追記する。
- 実装前の Assurance classification は `authorized_profile=standard` / `status=provisional` / `verify=valid` で作成済み。

## ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock` | iss-00229 | current session | spec-reviewer / code-reviewer / qa-reviewer / dev-coder / doc-writer | same repo, active issue, workflow-required bounded delegation; no destructive action, publishing, credentialed external action, or scope expansion | issue complete / session end / scope change / user revocation | none | proceed through workflow gates |

## 実装委任ゲート（Implementation Delegation Gate）
| ステップ | 判断 | 必須理由 | 委任ロール | 委任範囲 | 正本 | 許可変更 | 禁止変更 | 必須検証 | 停止条件 | 必須出力 | 観測結果 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | domain / template / tests slice | dev-coder | profile manifest and domain composer | `plan.md` S01 | domain composer, template manifest, unit tests | CLI wiring / workflow state / GitHub review | targeted pytest | marker safety cannot be guaranteed | changed files, tests, ledger note | pass |
| S02 | delegated | CLI vertical slice | dev-coder | compose command and artifact store | `plan.md` S02 | assurance command/application/presentation/infra, parser/bootstrap registration, and CLI tests | step routing / GitHub review / auto Lite default / stale policy | targeted pytest | compose would overwrite substantive content | changed files, tests, ledger note | pass |
| S03 | local execution | stale binding integration slice | orchestrator + reviewers | compose/verify/workflow blocking | `plan.md` S03 | assurance application/store/workflow/domain validation and compose/workflow tests | compose section content rules / GitHub review | targeted pytest | legacy compatibility breaks | changed files, tests, ledger note | pass |
| S90 | local verification | provider/mirror sync | orchestrator | dogfooding update and parity checks | `plan.md` S90 | dogfooding mirror | provider source beyond sync | update / parity / validate | parity mismatch unresolved | evidence | pass |
| S99 | in progress final gate | issue-wide quality | orchestrator + reviewers | final validation and review | `plan.md` S99 | final report / reviewer fixes | new feature scope | full validation | final reviewer fail | final evidence | pending re-review |

## レビューゲート状態（Reviewer Gate Status）
| ステップ | ゲート名 | レビュアーロール | 鮮度 | 状態 | リスク受容 | 昇格 / 完了判断 | メモ |
|---|---|---|---|---|---|---|---|
| planning | spec authoring review | spec-reviewer | initial candidate | failed | no | re-review required | P1 explicit Lite handling and per-step gates fixed |
| planning | spec authoring re-review | spec-reviewer | second candidate | failed | no | re-review required | P1 step-local delegation contracts and concrete test cards fixed |
| planning | spec authoring re-review | spec-reviewer | third candidate | failed | no | re-review required | P1 stale compose and requirement/design/plan source coverage fixed |
| planning | spec authoring re-review | spec-reviewer | fourth candidate | failed | no | re-review required | P1 stale compose ownership between S02 and S03 fixed |
| planning | spec authoring re-review | spec-reviewer | fifth candidate | passed | no | proceed to implementation | no findings; S02/S03 ownership conflict resolved |
| planning | assurance readiness | local command | after planning commit | passed | no | proceed to implementation | `assurance classify --stage requirement`, `assurance verify`, `workflow next issue-execution` succeeded |
| S01 | step code review | code-reviewer | initial S01 diff | failed | no | fix required | P1 malformed managed marker detection fixed |
| S01 | step code re-review | code-reviewer | after malformed marker fix | passed with P2 | no | P2 fix applied before commit | marker token outside HTML comments false positive fixed |
| S01 | step code final re-review | code-reviewer | after P2 fix | passed | no | commit S01 | no findings |
| S02 | plan amendment | spec-reviewer | during S02 implementation | passed with P2 | no | P2 traceability fixes applied | command registration requires `cli/parser.py` and `cli/bootstrap.py` |
| S02 | step code review | code-reviewer | initial S02 diff | failed | no | fix required | P1 symlink artifact write safety fixed; P2 report evidence fixed |
| S02 | step code re-review | code-reviewer | after P1/P2 fixes | passed | no | commit S02 | no findings |
| S03 | plan amendment | spec-reviewer | during S03 implementation | passed | no | proceed with amended path | D-009 adds `domain/assurance.py` for requirement/design/plan source binding role validation |
| S03 | step code review | code-reviewer | initial S03 diff | failed | no | fix required | P1 partial legacy source binding bypass fixed; P2 report evidence fixed |
| S03 | step code re-review | code-reviewer | after partial binding fix | failed | no | fix required | P1 role/path mismatch bypass fixed |
| S03 | step code re-review | code-reviewer | after role/path mismatch fix | failed | no | fix required | P1 nested same-basename bypass fixed |
| S03 | step code final re-review | code-reviewer | after canonical path fix | passed | no | commit S03 | no findings |
| S90 | docs impact review | spec-reviewer | after mirror update | failed | no | fix required | P1 AC-006/tc-007 traceability and P2 exact mirror status evidence fixed |
| S90 | docs impact re-review | spec-reviewer | after traceability fix | passed | no | commit S90 | no findings |
| S99 | final QA review | qa-reviewer | after S99 validation | passed with P2 | no | P2 fix applied before final commit | individual artifact compose coverage added |
| S99 | final code review | code-reviewer | after S99 validation | failed | no | fix required | P1 symlinked `assurance.json` write safety fixed; P2 S90 commit ledger fixed |
| S99 | final spec review | spec-reviewer | after S99 validation | failed | no | fix required | P1 active assurance binding refreshed; P1 pending final gates remain until re-review; P2 S03 traceability fixed |
| S99 | final QA re-review | qa-reviewer | after reviewer fixes | passed | no | proceed to final review close | no findings |
| S99 | final spec re-review | spec-reviewer | after reviewer fixes | passed | no | proceed to final review close | no findings |
| S99 | final code re-review | code-reviewer | after reviewer fixes | passed with P2 | no | P2 fixes applied before final commit | compose contract preflight and failed rollup classification fixed |
| S99 | final code P2 follow-up | local verification | after final code re-review | passed | no | commit S99 | failed legacy status context regression added |

## ステップ commit ゲート（Step Commit Gate）
| ステップ | クロージャ状態 | コミット範囲 | コミットハッシュ / 最終台帳 | コミット後 clean 確認 | 差分なし根拠 | 差分なし確認済み契約 / ファイル | 差分なし diff-clean コマンド | 差分なし read-only 確認 |
|---|---|---|---|---|---|---|---|---|
| planning | committed | requirement/design/plan/report authoring evidence | `1eb09f9a` | `git status --short` -> clean before assurance classification | N/A | N/A | N/A | N/A |
| planning-assurance | committed | `assurance.json` and readiness evidence | `46345f81` | `git status --short` -> clean before S01 | N/A | N/A | N/A | N/A |
| S01 | committed | domain composer, profile manifest, unit tests, report evidence | `3d67f781` | `git status --short` -> clean before S02 | N/A | N/A | N/A | N/A |
| S02 | committed | compose CLI, artifact store, parser/bootstrap wiring, CLI runtime tests, report evidence | `23ae5ecb` | `git status --short` -> clean before S03 | N/A | N/A | N/A | N/A |
| S03 | committed | stale source binding verify/compose/workflow integration, domain contract validation, tests, report evidence | `b5e3140a` | `git status --short` -> clean before S90 | N/A | N/A | N/A | N/A |
| S90 | committed | dogfooding mirror runtime/template sync and report evidence | `b2a0c1d9` | `git status --short` -> clean before S99 formatter/fixes | N/A | N/A | N/A | N/A |
| S99 | pending final commit | final quality gate evidence and formatter follow-up | pending commit | pending post-commit check | N/A | N/A | N/A | N/A |

## 実装記録（セッションログ）
- Implementation not started during planning.

### セッションログ（2026-06-23 planning readiness）

#### 対象
- Step: planning readiness gate
- AC/EC: implementation handoff precondition

#### 実施内容
- `assurance classify --stage requirement --format json` で issue-local `assurance.json` を作成した。
- `assurance verify --format json` で current requirement binding が valid であることを確認した。
- `workflow next issue-execution --format json` で `state=ready` / `next_action=execution-ready` を確認した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock assurance classify --stage requirement --format json
# ok=true status=valid authorized_profile=standard written_path=.../iss-00229-compose-profile-aware-planning-artifacts/assurance.json

./spec-dock/scripts/spec-dock assurance verify --format json
# ok=true status=valid reason=ok

./spec-dock/scripts/spec-dock workflow next issue-execution --format json
# state=ready next_action=execution-ready reason_code=assurance-valid
```

### セッションログ（2026-06-23 S01）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, AC-005, EC-003
- Closure ids: tc-001, tc-002, tc-003, tc-005

#### 実施内容
- `profile-sections.json` に Lite / Standard / Strict / Critical の profile section manifest を追加した。
- `domain/artifact_composer.py` に pure composer、manifest loader、managed marker scanner、compose result model を追加した。
- `tests/unit/domain/test_artifact_composer.py` に profile selection、explicit Lite、idempotence、no-overwrite、downgrade no deletion、marker conflict、plain prose token の unit tests を追加した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_artifact_composer.py
# 7 passed

uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_composer.py tests/unit/domain/test_artifact_composer.py
# All checks passed!

git diff --check
# pass
```

#### TDD / review evidence
| step | phase | planned evidence | observed evidence | result | notes |
|---|---|---|---|---|---|
| S01 | Red / alternative | red-required | target test file absent before implementation (`pytest` file-not-found) | approved-no-op | new pure domain slice |
| S01 | Green | domain unit tests | `uv run pytest tests/unit/domain/test_artifact_composer.py` -> 7 passed | pass | includes P1/P2 reviewer fixes |
| S01 | Refactor | guardrail | targeted `ruff check` and `git diff --check` passed | pass | no further refactor needed |

#### Closure coverage
| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-001 | S01 | profile selection tests for Lite / Standard / Strict / Critical | pass | `authorized_profile` only; `lite_candidate` does not select Lite |
| tc-002 | S01 | compose twice idempotence test | pass | second compose has no changed output |
| tc-003 | S01 | existing managed section preservation and downgrade test | pass | stronger sections are not deleted |
| tc-005 | S01 | duplicated / unclosed / mismatched / malformed marker tests | pass | conflict returns `output_text=None` |

### セッションログ（2026-06-23 S02）

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002, AC-003, AC-005, EC-001, EC-003
- Closure ids: tc-002, tc-003, tc-004, tc-005

#### 実施内容
- `assurance compose --artifact {design,plan,report,all}` を CLI に追加した。
- `ArtifactStore` を追加し、issue-local planning artifacts の read/write と profile manifest loading を実装した。
- compose result の text / JSON 出力、dry-run、missing/schema-invalid assurance fail-closed、marker conflict fail-closed を実装した。
- S02 plan amendment として `cli/parser.py` / `cli/bootstrap.py` を allowed paths に追加し、design/report traceability を更新した。
- code-reviewer P1 を受け、symlinked planning artifact を read/write 前に拒否する guard と regression test を追加した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_assurance_compose.py
# 6 passed

uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/assurance.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/assurance_text.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py tests/cli_runtime/test_assurance_compose.py
# All checks passed!

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=148

git diff --check
# pass
```

#### TDD / review evidence
| step | phase | planned evidence | observed evidence | result | notes |
|---|---|---|---|---|---|
| S02 | Red / alternative | red-required | initial targeted CLI tests failed with `invalid choice: 'compose'`; plan amended to include parser/bootstrap registration | pass | D-008 |
| S02 | Green | CLI runtime tests | `uv run pytest tests/cli_runtime/test_assurance_compose.py` -> 6 passed | pass | includes symlink write-safety regression |
| S02 | Refactor | guardrail | targeted `ruff check`, `validate`, and `git diff --check` passed | pass | no further refactor needed |

#### Closure coverage
| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-002 | S02 | second compose returns unchanged and no changed paths | pass | idempotent CLI behavior |
| tc-003 | S02 | compose preserves existing artifact text and rejects unsafe symlink artifact | pass | non-destructive write safety |
| tc-004 | S02 | compose all materializes sections; missing/invalid assurance fail closed | pass | JSON output includes changed paths and artifacts |
| tc-005 | S02 | marker conflict test keeps artifacts unchanged | pass | `reason=marker_conflict` |

### セッションログ（2026-06-23 S03）

#### 対象
- Step: S03
- AC/EC: AC-004, EC-002
- Closure ids: tc-s03-001, tc-s03-002, tc-s03-003, tc-s03-004

#### 実施内容
- persisted Assurance Contract の source binding を requirement/design/plan の planning artifact set に拡張した。
- `assurance verify` / `assurance compose` / `workflow next issue-execution` が stale source binding を fail-closed に扱うようにした。
- `assurance compose` の deterministic managed-section 書き込み後は、成功した non-dry-run write に限り current planning artifact hashes へ source binding を更新するようにした。
- pre-S03 partial legacy binding が design/plan stale を見逃さないよう、persisted adaptive contract validation で requirement/design/plan roles を必須化した。
- role が存在していても別 artifact path を指す契約が stale 検出を迂回しないよう、requirement/design/plan role と canonical filename の対応を必須化した。
- nested same-named path が canonical artifact として扱われないよう、target-aware validation で `issue_dir/<role>.md` との完全一致を必須化した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_assurance_store.py tests/unit/domain/test_assurance.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py
# 39 passed

uv run ruff check src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/assurance.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py tests/unit/infra/test_assurance_store.py tests/unit/domain/test_assurance.py tests/cli_runtime/test_assurance_compose.py tests/cli_runtime/test_workflow.py
# All checks passed!

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=148

git diff --check
# pass
```

#### TDD / review evidence
| step | phase | planned evidence | observed evidence | result | notes |
|---|---|---|---|---|---|
| S03 | Red / alternative | stale source binding regression | initial tests exposed stale failures and reviewer exposed partial legacy binding bypass | pass | D-010 |
| S03 | Green | verify/compose/workflow stale tests | targeted pytest -> 39 passed | pass | requirement/design/plan stale cases, partial binding invalid schema, role/path mismatch invalid schema, nested canonical path invalid schema |
| S03 | Refactor | guardrail | targeted `ruff check`, `validate`, and `git diff --check` passed | pass | no further refactor needed before re-review |

#### Closure coverage
| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-s03-001 | S03 | `tests/unit/infra/test_assurance_store.py` stale requirement/design/plan cases | pass | `reason=stale_source_binding` |
| tc-s03-002 | S03 | `tests/cli_runtime/test_assurance_compose.py` stale requirement/design/plan cases | pass | compose keeps artifacts unchanged |
| tc-s03-003 | S03 | `tests/cli_runtime/test_workflow.py` stale requirement/design/plan cases | pass | workflow remains `classification-required` / `authority-invalid` |
| tc-s03-004 | S03 | partial legacy binding regression | pass | missing design/plan roles are `invalid_schema` |
| tc-s03-005 | S03 | role/path mismatch regression | pass | wrong canonical filename binding is `invalid_schema` |
| tc-s03-006 | S03 | nested same-name canonical path regression | pass | nested `design.md` binding is `invalid_schema` |

### セッションログ（2026-06-23 S90）

#### 対象
- Step: S90
- AC/EC: AC-006, EC-001, EC-003
- Closure ids: tc-007, tc-s90-001, tc-s90-002

#### 実施内容
- provider 側の runtime / assurance template 変更を dogfooding mirror へ `spec-dock update` で反映した。
- provider / mirror runtime parity と assurance template parity を確認した。
- generated runbook / active projection が ignored のままで、tracked authority として混入していないことを確認した。
- changed mirror files:
  - `spec-dock/scripts/spec_dock_runtime/application/{assurance.py,contracts.py,workflow.py}`
  - `spec-dock/scripts/spec_dock_runtime/cli/{bootstrap.py,parser.py}`
  - `spec-dock/scripts/spec_dock_runtime/commands/assurance.py`
  - `spec-dock/scripts/spec_dock_runtime/domain/{assurance.py,artifact_composer.py}`
  - `spec-dock/scripts/spec_dock_runtime/infra/{assurance_store.py,artifact_store.py}`
  - `spec-dock/scripts/spec_dock_runtime/presentation/assurance_text.py`
  - `spec-dock/templates/assurance/profile-sections.json`
- unresolved risks: none.

#### 実行コマンド / 結果
```bash
uv run python -m spec_dock.cli update .
# spec-dock: ok (update) -> ...

diff -ru -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime
# pass

diff -ru src/spec_dock/assets/spec_dock/templates/assurance spec-dock/templates/assurance
# pass

git status --short --ignored spec-dock/.agent/runbooks spec-dock/active/current-runbook.json spec-dock/active/current-runbook.md spec-dock/scripts/spec_dock_runtime spec-dock/templates/assurance
#  M spec-dock/scripts/spec_dock_runtime/application/assurance.py
#  M spec-dock/scripts/spec_dock_runtime/application/contracts.py
#  M spec-dock/scripts/spec_dock_runtime/application/workflow.py
#  M spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py
#  M spec-dock/scripts/spec_dock_runtime/cli/parser.py
#  M spec-dock/scripts/spec_dock_runtime/commands/assurance.py
#  M spec-dock/scripts/spec_dock_runtime/domain/assurance.py
#  M spec-dock/scripts/spec_dock_runtime/infra/assurance_store.py
#  M spec-dock/scripts/spec_dock_runtime/presentation/assurance_text.py
# ?? spec-dock/scripts/spec_dock_runtime/domain/artifact_composer.py
# ?? spec-dock/scripts/spec_dock_runtime/infra/artifact_store.py
# ?? spec-dock/templates/assurance/
# !! spec-dock/.agent/
# !! spec-dock/active/
# !! spec-dock/scripts/spec_dock_runtime/__pycache__/
# !! spec-dock/scripts/spec_dock_runtime/application/__pycache__/
# !! spec-dock/scripts/spec_dock_runtime/cli/__pycache__/
# !! spec-dock/scripts/spec_dock_runtime/commands/__pycache__/
# !! spec-dock/scripts/spec_dock_runtime/domain/__pycache__/
# !! spec-dock/scripts/spec_dock_runtime/infra/__pycache__/
# !! spec-dock/scripts/spec_dock_runtime/presentation/__pycache__/

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=148
```

#### Closure coverage
| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-007 | S90 | provider/mirror runtime and template parity diff; generated artifact status check | pass | closes AC-006 provider/mirror parity |
| tc-s90-001 | S90 | provider/mirror runtime and template parity diff | pass | `__pycache__` ignored from runtime diff |
| tc-s90-002 | S90 | ignored generated artifact status check | pass | generated runbook / active projection remained ignored |

### セッションログ（2026-06-23 S99）

#### 対象
- Step: S99
- AC/EC: all issue AC / EC
- Closure ids: tc-008, tc-s99-001, tc-s99-002

#### 実施内容
- issue-wide final validation と provider/mirror parity を実行した。
- 初回 `make lint` は Ruff format check で失敗したため、provider / mirror の対応ファイルと tests を `uv run ruff format` で整形した。
- formatter 後に lint / parity / validate / targeted tests を再実行した。
- final spec-reviewer P1 を受け、active issue の `assurance.json` を現行 requirement/design/plan source binding へ再分類し、`assurance verify` が valid であることを確認した。
- final code-reviewer P1/P2 を受け、`assurance.json` symlink contract write guard、compose artifact write 前の contract path preflight、regression tests を追加した。
- final qa-reviewer P2 を受け、`assurance compose --artifact design` が選択 artifact のみを変更する regression test を追加した。
- full unit で検出された既存 PR observation wait の required-check pending 判定不整合を修正し、wait loop の補助 rollup check と regression test を通した。
- final code-reviewer P2 を受け、failed required rollup は `pending/wait` ではなく `failed/fix_ci` に分類する regression test を追加した。
- final code-reviewer P2 follow-up として、legacy status context の `state=FAILURE` も `failed/fix_ci` に分類する regression test を追加した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit
# initial: 1 failed, 805 passed
# after PR observation wait fix: 806 passed
# after final P2 fixes: 807 passed

uv run pytest tests/cli_runtime
# 662 passed, 76 skipped
# after final P2 fixes: 663 passed, 76 skipped

make lint
# initial: ruff check pass, ruff format check fail, mypy pass

uv run ruff format src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/assurance.py src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifact_composer.py tests/cli_runtime/test_assurance_compose.py tests/unit/infra/test_assurance_store.py spec-dock/scripts/spec_dock_runtime/application/assurance.py spec-dock/scripts/spec_dock_runtime/domain/artifact_composer.py
# 6 files reformatted

make lint
# ruff check pass; ruff format check pass; mypy pass

diff -ru -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime
# pass

diff -ru src/spec_dock/assets/spec_dock/templates/assurance spec-dock/templates/assurance
# pass

uv run pytest tests/unit/infra/test_assurance_store.py tests/unit/domain/test_artifact_composer.py tests/cli_runtime/test_assurance_compose.py
# 27 passed

./spec-dock/scripts/spec-dock assurance classify --stage requirement --format json
# ok=true status=valid; source_binding includes design/plan/requirement

./spec-dock/scripts/spec-dock assurance verify --format json
# ok=true status=valid reason=ok

uv run pytest tests/cli_runtime/test_assurance_compose.py tests/unit/infra/test_assurance_store.py
# 22 passed

uv run pytest tests/cli_runtime/test_assurance_compose.py tests/unit/infra/test_assurance_store.py tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_keeps_required_checks_pending_as_wait tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_maps_failed_required_rollup_to_fix_ci
# 25 passed

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_keeps_required_checks_pending_as_wait
# 1 passed

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_keeps_required_checks_pending_as_wait tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_maps_failed_required_rollup_to_fix_ci tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_observation_wait_maps_failed_required_status_state_to_fix_ci
# 3 passed

make lint
# ruff check pass; ruff format check pass; mypy pass

diff -ru -x __pycache__ src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime spec-dock/scripts/spec_dock_runtime
# pass

diff -ru src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py .agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py
# pass

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=148

git diff --check
# pass
```

#### Closure coverage
| closure id | step | verification evidence | observed result | notes |
|---|---|---|---|---|
| tc-008 | S99 | full validation suite, lint, validate, parity diff, final reviewer gates | pending reviewer gates | command validation passed |
| tc-s99-001 | S99 | unit / CLI runtime / lint / validate / parity diff | pass | formatter follow-up, assurance refresh, symlink guard, individual compose test, and PR observation wait fix applied and rechecked |
| tc-s99-002 | S99 | qa-reviewer / code-reviewer / spec-reviewer | pending | final reviewers not yet completed |
