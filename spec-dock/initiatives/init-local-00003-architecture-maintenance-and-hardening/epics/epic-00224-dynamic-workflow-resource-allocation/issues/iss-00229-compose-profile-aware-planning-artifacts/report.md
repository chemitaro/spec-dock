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
- S02-S03 / S90 / S99 の実行結果、worker evidence、reviewer evidence、commit gates は後続ステップで追記する。
- 実装前の Assurance classification は `authorized_profile=standard` / `status=provisional` / `verify=valid` で作成済み。

## ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock` | iss-00229 | current session | spec-reviewer / code-reviewer / qa-reviewer / dev-coder / doc-writer | same repo, active issue, workflow-required bounded delegation; no destructive action, publishing, credentialed external action, or scope expansion | issue complete / session end / scope change / user revocation | none | proceed through workflow gates |

## 実装委任ゲート（Implementation Delegation Gate）
| ステップ | 判断 | 必須理由 | 委任ロール | 委任範囲 | 正本 | 許可変更 | 禁止変更 | 必須検証 | 停止条件 | 必須出力 | 観測結果 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | domain / template / tests slice | dev-coder | profile manifest and domain composer | `plan.md` S01 | domain composer, template manifest, unit tests | CLI wiring / workflow state / GitHub review | targeted pytest | marker safety cannot be guaranteed | changed files, tests, ledger note | pass |
| S02 | planned delegated | CLI vertical slice | dev-coder | compose command and artifact store | `plan.md` S02 | assurance command/application/presentation/infra and CLI tests | step routing / GitHub review / auto Lite default / stale policy | targeted pytest | compose would overwrite substantive content | changed files, tests, ledger note | pending |
| S03 | planned delegated | stale binding integration slice | dev-coder | compose/verify/workflow blocking | `plan.md` S03 | assurance command/application/store/workflow and compose/workflow tests | compose section content rules / GitHub review | targeted pytest | legacy compatibility breaks | changed files, tests, ledger note | pending |
| S90 | planned local verification | provider/mirror sync | orchestrator | dogfooding update and parity checks | `plan.md` S90 | dogfooding mirror | provider source beyond sync | update / parity / validate | parity mismatch unresolved | evidence | pending |
| S99 | planned final gate | issue-wide quality | orchestrator + reviewers | final validation and review | `plan.md` S99 | final report / reviewer fixes | new feature scope | full validation | final reviewer fail | final evidence | pending |

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

## ステップ commit ゲート（Step Commit Gate）
| ステップ | クロージャ状態 | コミット範囲 | コミットハッシュ / 最終台帳 | コミット後 clean 確認 | 差分なし根拠 | 差分なし確認済み契約 / ファイル | 差分なし diff-clean コマンド | 差分なし read-only 確認 |
|---|---|---|---|---|---|---|---|---|
| planning | committed | requirement/design/plan/report authoring evidence | `1eb09f9a` | `git status --short` -> clean before assurance classification | N/A | N/A | N/A | N/A |
| planning-assurance | committed | `assurance.json` and readiness evidence | `46345f81` | `git status --short` -> clean before S01 | N/A | N/A | N/A | N/A |
| S01 | ready for commit | domain composer, profile manifest, unit tests, report evidence | pending commit | pending post-commit check | N/A | N/A | N/A | N/A |

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
