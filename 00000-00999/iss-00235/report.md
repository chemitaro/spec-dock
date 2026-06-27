---
種別: 実装報告書（Issue）
ID: "iss-00235"
タイトル: "Repair high level dependency source projection"
関連GitHub: ["#235"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00235 Repair high level dependency source projection — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- No material interpretation changes.
- No decision entries.

Ledger entry は次の契約値を使う。

- `Status`: `open` / `resolved` / `superseded`
- `Type`: `interpretation` / `scope` / `implementation` / `compatibility` / `test-strategy` / `operation` / `deviation` / `follow-up`
- `Disposition`: `applied` / `rejected` / `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` / `converted_to_followup` / `deferred` / `no_action` / `superseded`

完了時の意味論（completion semantics）:
- issue completion 前に `Status=open` の entry を残してはならない。
- `Status=resolved` は `Disposition`、evidence、必要な follow-up を持つ。
- `Status=superseded` または `Disposition=superseded` は置換先 entry ID を持つ。
- `Disposition=promoted_to_design` / `promoted_to_adr` / `promoted_to_plan` は昇格先 artifact と evidence を持つ。
- `Disposition=converted_to_followup` は follow-up issue / discussion / ADR candidate の参照を持つ。
- `Disposition=deferred` は scope 外である理由、blocking でない根拠、revisit 条件を持つ。
- `Disposition=no_action` は issue-local な判断で追加対応不要である理由を持つ。将来も効く durable decision を `report.md` だけに閉じ込めてはならない。

Disposition ごとの必須証跡:
- `applied`: 変更した artifact / 実装証跡と、issue-local 適用で十分な理由。
- `rejected`: 却下した選択肢、理由、blocking impact が残らない根拠。
- `promoted_to_design` / `promoted_to_adr` / `promoted_to_plan`: 昇格先 artifact 参照と証跡。
- `converted_to_followup`: follow-up issue / discussion / ADR candidate 参照と blocking / non-blocking の分類。
- `deferred`: scope-out 理由、non-blocking の根拠、revisit 条件。
- `no_action`: 判断が issue-local で durable ではない理由。
- `superseded`: 置換先 entry ID と置換理由。

| 識別子（ID） | 状態（Status） | 種別（Type） | 起票元（Raised By） | 契機 / 差分（Gap） | 検討した選択肢 | 判断 / 解釈 | 根拠（Rationale） | 処置（Disposition） | 証跡（Evidence） | フォローアップ（Follow-up） |
|---|---|---|---|---|---|---|---|---|---|---|
| D-001 | resolved | interpretation | orchestrator + deep-consultant | GitHub issue #235 は `iss-00207` と重複するか、別 edge case か。 | 重複として閉じる; `iss-00207` に吸収する; high-level source direct dependency の別 issue として扱う。 | #235 は high-level source 自体の direct dependency が issue-keyed projection で落ちる問題であり、issue source -> high-level target を扱う `iss-00207` とは別 scope。 | 手動再現で `.meta.json.depends_on` は保存されたが、`deps check --id init-00001` / `index-all` / `deps-issues` から消えた。既存 tests は source issue axis が中心。 | applied | `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md` | future requirement/design/plan に source-axis test matrix を反映する。 |
| D-002 | resolved | test-strategy | spec-reviewer | Initial plan S04/S05 bundled multiple observable surfaces in one step. | Keep bundled steps; split by observable surface and commit/review scope. | S04/S05 を `deps check` CLI、`sync` artifact、issue-source regression、non-goal boundary の separate step に分割する。 | `spec-dock-issue-execution` と `phase_plan_issue.md` は 1 implementation step = 1 observable behavior = 1 review scope = 1 commit を要求する。 | applied | `plan.md` S04-S07; plan reviewer finding 2026-06-27 | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | research + manual command | issue analysis | GitHub #235 の保存済み raw dependency が readiness/index projection から失われることを reduced reproduction で確認したため。 | `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md`; `/private/tmp/iss-00235-repro`; `deps check --id init-00001 --no-github --json` -> `ready: true`, empty dependency fields | future requirement/design/plan に受け入れ条件と test matrix を反映する。 |
| EAL-002 | `adopted` | sub-agent | issue analysis | runtime/domain、artifact/contract、issue-scope comparison の3観点が、raw storage ではなく issue-keyed projection loss を根本原因とする点で一致したため。 | `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md` deep-consultant synthesis | design で raw node dependency result と issue readiness result を分離する。 |
| EAL-003 | `adopted` | `system-architect` discussion draft | `design.md` | Draft の raw audit / issue readiness separation、`direct_node_dependencies`、`deps.raw_direct_edges` 方針が approved requirement と existing runtime structure に合っていたため。 | `discussions/20260626t054055z-disc-design-high-level-source-direct-deps.md`; diff guard pass: delegated write は discussion draft のみ | integrated into `design.md`; fresh spec-reviewer pass recorded in Spec Authoring Gate |
| EAL-004 | `adopted` | `implementation-planner` discussion draft | `plan.md` | Draft の closure index と S01-S05/S90/S99 は有用だったが、reviewer 指摘により S04/S05 を S04-S07 へ分割し non-goal closure と step-local delegation contracts を追加した。 | `discussions/20260626t055323z-disc-plan-high-level-source-direct-deps.md`; diff guard pass: delegated write は discussion draft のみ | integrated into `plan.md`; fresh spec-reviewer pass recorded in Spec Authoring Gate |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | GitHub #235 の再現確認と根本原因を research に記録した。 | issue scaffold 作成、issue start、deep-consultant 3系統の統合。 | low | provisional |
| OAL-002 | Approved requirement/design/plan は #235 の high-level source direct dependency false-ready と raw audit 欠落を primary objective として扱う。 | workflow 上の delegated draft / reviewer gates / per-step commit gate を plan に反映した。 | low | requirement/design/plan passed |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| research | `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md`; manual reproduction; code inspection; deep-consultant synthesis | `deps-raw.puml` の complete audit contract は design decision が必要。 | adopted | provisional | no | requirement/design/plan authoring |
| requirement | `requirement.md`; research discussion; GitHub #235 reproduction | AC-002 が `ready=false` を要求すること、AC-003 が `.agent/index-all.json` を required audit surface とすることを fixed。 | adopted | first review failed; second fresh `spec-reviewer` pass, confidence 0.91 | no | promoted to design |
| design | `design.md`; `discussions/20260626t054055z-disc-design-high-level-source-direct-deps.md`; runtime source inspection | `direct_node_dependencies` value schema は existing domain vocabulary に合わせる。 | adopted | first review pass with P2; schema vocabulary updated; second fresh `spec-reviewer` pass, confidence 0.90 | no | promoted to plan |
| plan | `plan.md`; `discussions/20260626t055323z-disc-plan-high-level-source-direct-deps.md`; phase_plan_issue / authoring docs | Delegated draft adoption evidence, single-surface step split, proposal-only draft metadata, and step-local delegation contracts were required. | adopted with revision | first two fresh `spec-reviewer` reviews failed; third fresh `spec-reviewer` pass, confidence 0.91 | no | execution handoff ready |
| execution-handoff | `requirement.md`; `design.md`; `plan.md`; `report.md`; active issue context | No unresolved requirement/design/plan gaps after reviewer pass. | approved | planning artifacts fresh-pass complete | no | start S01 under `spec-dock-issue-execution` |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used / not used
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `discussions/` direct child にある flat Markdown
  - filename: `<ts>-<kind>-<slug>.md` または same-second collision 用 `<ts>-<nn>-<kind>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
- 禁止 self-claim:
  - `authority: accepted`, `adoption_status: adopted`, non-empty `reflected_to`, reviewer pass, phase completion, implementation readiness
- 禁止 wildcard token:
  - `*`, `grants.*`, `all`
- 標準必須にしない field:
  - task manifest hash, Permission Profile hash, session invocation hash, probe run id, session hash
- historical note:
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（discussion draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00235 | `discussions/20260626t054055z-disc-design-high-level-source-direct-deps.md` | `requirement.md`; root-cause research; runtime source/tests | `design.md`, `plan.md`, `report.md` | adopted | `design.md` | pass | `direct_node_dependencies` / `deps.raw_direct_edges` / non-goal artifact boundary を canonical design に統合 | implementation step ordering details は plan phase へ送った | none | design spec-reviewer pass after schema clarification | promoted to design |
| implementation-planner | iss-00235 | `discussions/20260626t055323z-disc-plan-high-level-source-direct-deps.md` | `requirement.md`; `design.md`; design discussion; phase_plan_issue; authoring docs | `plan.md`, `report.md` | adopted with revision | `plan.md` | pass | closure index と step sequence を canonical plan に統合し、reviewer finding に基づき S04/S05 を S04-S07 へ分割し step-local delegation contracts を追加 | original bundled S04/S05 step shape | none | first/second plan spec-reviewer failed; third pass | promoted to plan / execution handoff ready |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| 同意なし（missing consent） | blocked / incomplete | 範囲付き同意を取得する、または手動 authoring に戻す | この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（Reviewer Gate Status / Final Spec Review Gate） | ineligible |

## 実装サマリー (任意)
- S01 では `check_deps` / domain inspection の application result contract に、checked target node 自体の direct node dependency status を追加した。
- S02-S07 では `deps check --json` / `.agent/index-all.json` の additive public contract、CLI reduced reproduction、sync artifact boundary、non-goal storage boundary を実装・検証した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-27 S01）

#### 対象
- Step: S01 Direct Node Dependency Status Contract
- AC/EC: AC-001, AC-002, EC-002
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S01 — Direct Node Dependency Status Contract`
  - closure ids: `cl-ac001-direct-check`, `cl-ac002-non-ready`, `cl-ec002-non-empty-source`

#### 実施内容
- `TargetDepsInspection.direct_node_dependencies` と `DepsCheckResult.direct_node_dependencies` を追加した。
- `check_deps` が raw direct node dependency map を読み、checked target node 自体の direct dependency status を `inspect_target_deps` に渡すようにした。
- unresolved direct node dependency は `evaluation.ready=false`、`evaluation.blockers` に target node id を追加する。
- Non-empty high-level source の direct status は `direct_node_dependencies` に残し、`effective_depends_on` には混ぜない。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py

41 passed in 0.05s
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ | red-required | dev-coder reported initial `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py` failed with 4 failed / 37 passed after adding focused tests. Failures matched missing `raw_node_depends_on_map`, missing `direct_node_dependencies`, and false-ready for empty high-level source direct dependency. | delegated worker record | pass | Red output was reported by worker; parent re-ran Green after implementation. |
| S01 | 緑フェーズ | direct node status contract passes targeted tests | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py` -> 41 passed in 0.05s | command | pass | Parent-run verification on current worktree. |
| S01 | リファクタリング | guardrail satisfied | Diff stayed within S01 allowed paths and did not touch presentation JSON, sync artifacts, storage format, or dogfooding generated runtime. | diff inspection | pass | No broader refactor recorded. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | `DepsCheckResult.direct_node_dependencies` property as additive access to inspection status | implementation | recorded | cl-ac001-direct-check | no | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | cl-ac001-direct-check | Direct node dependency status is available from application result. | `TargetDepsInspection.direct_node_dependencies`; `DepsCheckResult.direct_node_dependencies`; targeted tests passed. | pass | Rendering remains S02. |
| S01 | cl-ac002-non-ready | Unresolved direct node dependency makes application result non-ready and blockers include target node id. | Domain/application tests for empty source `init -> epic` passed. | pass | CLI surface remains S04. |
| S01 | cl-ec002-non-empty-source | Non-empty source keeps direct node status separate from descendant issue readiness. | Domain/application tests assert `effective_depends_on == []` while `direct_node_dependencies` records expanded target issues. | pass | Issue-source regression remains S06. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-ac001-direct-check | S01 | yes | red-required | delegated Red: 4 failed / 37 passed | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py` | pass, 41 passed in 0.05s | Parent-run Green. |
| cl-ac002-non-ready | S01 | yes | red-required | delegated Red: false-ready failure reported | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py` | pass, 41 passed in 0.05s | Application/domain level only. |
| cl-ec002-non-empty-source | S01 | yes | red-required | delegated Red: direct status missing reported | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py` | pass, 41 passed in 0.05s | `effective_depends_on` remains issue-readiness-only. |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-ac001-direct-check | S01 | targeted domain/application tests | pass | Rendering remains S02. |
| cl-ac002-non-ready | S01 | targeted domain/application tests | pass | CLI remains S04. |
| cl-ec002-non-empty-source | S01 | targeted domain/application tests | pass | Regression hardening remains S06. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S01 | N/A | N/A | Planned closure ids were used as-is. | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction invoking `spec-dock-issue-planning` and `spec-dock-issue-execution` | `/Users/iwasawayuuta/.codex/worktrees/c2a6/spec-dock` | iss-00235 | current session | spec-reviewer / system-architect / implementation-planner / dev-coder / code-reviewer / qa-reviewer | same repo, active issue, named roles, workflow-scoped; no destructive action, publishing, credentialed external mutation, or scope expansion | issue complete / scope change / user revocation | none | proceed through workflow gates |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | runtime/domain/application/test implementation | dev-coder | S01 Direct Node Dependency Status Contract | `plan.md` S01 | six allowed source/test files | storage migration, synthetic issue, `effective_depends_on` semantic change, presentation/sync artifact work | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py` | allowed paths outside scope or planned tests cannot run | changed files, Red/Green evidence, risks, Ledger Note/no-decision statement | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Added direct node dependency status to application/domain result; unresolved direct node dependencies make application result non-ready; `effective_depends_on` remains issue-readiness-only. | `domain/models.py`, `domain/deps.py`, `application/contracts.py`, `application/check_deps.py`, `tests/unit/domain/test_deps.py`, `tests/unit/application/test_check_deps.py` | delegated Red: 4 failed / 37 passed; parent Green: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py` -> 41 passed | pending after report update | JSON/sync surfaces intentionally pending for S02/S03 | accepted pending fresh code-reviewer pass |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | N/A | N/A | N/A | N/A | N/A | N/A | delegated path used | N/A |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit gate | First review failed on missing report evidence; report was updated and fresh re-review passed. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | S01 source/test/report files | S01 implementation commit, amended with this final commit-gate evidence | `git status --short --branch` -> clean after S01 commit before final evidence amendment; clean check must be rerun after amend | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py` - direct node dependency model and inspection field.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py` - direct node dependency evaluation and readiness merge.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - additive `DepsCheckResult.direct_node_dependencies` accessor.
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py` - raw node dependency map reuse for inspection.
- `tests/unit/domain/test_deps.py` - domain S01 coverage.
- `tests/unit/application/test_check_deps.py` - application S01 coverage.
- `spec-dock/active/issue/report.md` - S01 observed evidence ledger.

#### コミット
- S01 implementation commit amended with final commit-gate evidence.

#### メモ
- First S01 code review failed only on missing report evidence; after report update, fresh code-reviewer pass was obtained.

---

### セッションログ（2026-06-27 S02）

#### 対象
- Step: S02 `deps check --json` Additive JSON Contract
- AC/EC: AC-001, AC-002
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S02 — deps check --json Additive JSON Contract`
  - closure ids: `cl-ac001-direct-check`, `cl-ac002-non-ready`

#### 実施内容
- `render_deps_check_json()` に additive field `direct_node_dependencies` を追加した。
- S01 の `result.direct_node_dependencies` を presentation で再計算せず、そのまま payload 化する。
- Existing top-level keys、`node_blockers`、`dependency_contexts` は維持した。
- Direct dependency が空の場合は `direct_node_dependencies: []` を安定出力する。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py

87 passed in 0.42s
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S02 | 赤フェーズ | red-required | dev-coder reported focused test `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k direct_node_dependencies` failed with `KeyError: 'direct_node_dependencies'`. | delegated worker record | pass | Parent re-ran required Green command after implementation. |
| S02 | 緑フェーズ | renderer JSON contract passes required tests | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` -> 87 passed in 0.42s | command | pass | Parent-run verification on current worktree. |
| S02 | リファクタリング | guardrail satisfied | Diff stayed within S02 allowed paths and did not touch domain/application/sync artifacts/schema_version. | diff inspection | pass | `tests/cli_runtime/test_runtime_deps_s04.py` did not require changes. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02 | none | implementation | no new closure delta | N/A | no | worker reported no closure delta |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S02 | cl-ac001-direct-check | `deps check --json` exposes direct node dependency payload. | `render_deps_check_json()` payload includes `direct_node_dependencies` with source/target ids/kinds, expansion, lifecycle, disposition, and basis. | pass | CLI reduced reproduction remains S04. |
| S02 | cl-ac002-non-ready | JSON output preserves non-ready observation from application result. | Existing `ready` / `blockers` keys remain and no presentation recomputation was added. | pass | Public CLI behavior remains S04. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-ac001-direct-check | S02 | yes | red-required | delegated Red: `KeyError: 'direct_node_dependencies'` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 87 passed in 0.42s | Renderer contract. |
| cl-ac002-non-ready | S02 | yes | red-required | delegated Red: direct payload missing | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 87 passed in 0.42s | Non-ready status comes from S01 result. |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-ac001-direct-check | S02 | presentation/CLI runtime tests | pass | CLI reduced reproduction remains S04. |
| cl-ac002-non-ready | S02 | presentation/CLI runtime tests | pass | CLI reduced reproduction remains S04. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S02 | N/A | N/A | Planned closure ids were used as-is. | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02 | delegated | presentation/test implementation | dev-coder | S02 `deps check --json` Additive JSON Contract | `plan.md` S02 | `presentation/json_state.py`, `tests/unit/presentation/test_runtime_sync_s07.py`; optional CLI test was not needed | domain/application implementation, schema_version change, sync artifact behavior | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | renderer must infer unavailable status or files outside allowed paths are needed | changed files, Red/Green evidence, risks, no-decision statement | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S02 | dev-coder | Added additive `direct_node_dependencies` to `deps check --json` rendering without readiness recomputation. | `presentation/json_state.py`, `tests/unit/presentation/test_runtime_sync_s07.py` | delegated Red: `KeyError`; parent Green: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` -> 87 passed | pending | JSON uses S01 result model; sync/index-all remains S03 | accepted pending fresh code-reviewer pass |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit gate | Fresh code-reviewer pass, confidence 0.91. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S02 | committed | S02 presentation/test/report files | S02 implementation commit, amended with this final commit-gate evidence | `git status --short --branch` -> clean after S02 commit before final evidence amendment; clean check must be rerun after amend | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` - additive `direct_node_dependencies` payload.
- `tests/unit/presentation/test_runtime_sync_s07.py` - renderer S02 coverage.
- `spec-dock/active/issue/report.md` - S02 observed evidence ledger.

#### コミット
- S02 implementation commit amended with final commit-gate evidence.

#### メモ
- No material implementation decisions beyond the approved plan.

---

### セッションログ（2026-06-27 S03）

#### 対象
- Step: S03 `.agent/index-all.json` Raw Direct Edge Audit
- AC/EC: AC-003, EC-003
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S03 — .agent/index-all.json Raw Direct Edge Audit`
  - closure ids: `cl-ac003-index-all-raw`, `cl-ec003-satisfied-raw-audit`

#### 実施内容
- `.agent/index-all.json` の `deps.raw_direct_edges` に保存済み `depends_on` の direct node edge を追加した。
- Edge は `from`, `from_kind`, `to`, `to_kind`, `relation: raw_direct` を持つ監査用 payload とした。
- `.agent/index.json` には `raw_direct_edges` を出力しない契約をテストで固定した。
- Satisfied / closed な direct dependency も raw audit では除外しない契約をテストで固定した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py

89 passed in 0.53s
```

```bash
git diff --check

pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S03 | 赤フェーズ | red-required | dev-coder reported focused test `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py -k 'raw_direct_edges'` initially failed with `KeyError: 'raw_direct_edges'`. | delegated worker record | pass | Parent re-ran required Green command after implementation. |
| S03 | 緑フェーズ | sync full-history artifact contract passes required tests | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` -> 89 passed in 0.53s | command | pass | Parent-run verification after reviewer finding fix. |
| S03 | リファクタリング | guardrail satisfied | Diff stayed within S03 allowed paths; `.agent/index.json`, `.agent/tree-all.json`, `deps-issues.json`, and `deps-raw.puml` contracts were not expanded. | diff inspection | pass | `git diff --check` passed; test asserts tree artifacts do not include `raw_direct_edges`. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S03 | none | implementation | no new closure delta | N/A | no | worker reported no material implementation decisions beyond the approved plan |
| S03 | `raw_direct_edges` leaking into `.agent/tree-all.json` through shared full-history deps payload | code-reviewer | split index-all deps payload from shared tree deps payload; added assertion that tree artifacts do not include `raw_direct_edges` | cl-ac003-index-all-raw | no | reviewer P1 finding, fixed in S03 allowed files |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S03 | cl-ac003-index-all-raw | `.agent/index-all.json` exposes complete raw direct high-level edge audit. | `render_index_artifact()` all-json payload includes `deps.raw_direct_edges` with source/target kinds and deterministic ordering. | pass | Todo index remains filtered and does not include `raw_direct_edges`. |
| S03 | cl-ec003-satisfied-raw-audit | Raw audit retains satisfied / closed direct dependencies. | Focused test asserts closed high-level target still appears in `index-all` raw direct edges. | pass | Readiness projection remains separate from raw audit. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-ac003-index-all-raw | S03 | yes | red-required | delegated Red: `KeyError: 'raw_direct_edges'` | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 89 passed in 0.53s | Full-history index audit contract; tree artifacts remain outside raw audit contract. |
| cl-ec003-satisfied-raw-audit | S03 | yes | red-required | delegated Red: raw direct edge missing | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 89 passed in 0.53s | Satisfied/closed dependencies are retained in raw audit. |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-ac003-index-all-raw | S03 | presentation sync tests | pass | Public CLI reduced reproduction remains S04. |
| cl-ec003-satisfied-raw-audit | S03 | presentation sync tests | pass | Raw audit is separate from readiness projection. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S03 | N/A | N/A | Planned closure ids were used as-is. | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S03 | delegated | presentation/test implementation | dev-coder | S03 `.agent/index-all.json` Raw Direct Edge Audit | `plan.md` S03 | `presentation/json_state.py`, `tests/unit/presentation/test_runtime_sync_s07.py` | `.agent/index.json` expansion, `deps-issues.json`, `deps-raw.puml`, storage mutation, readiness recomputation | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | raw audit cannot be built from existing sync result or allowed paths are insufficient | changed files, Red/Green evidence, risks, no-decision statement | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S03 | dev-coder | Added full-history `deps.raw_direct_edges` audit payload for saved direct node dependencies; kept todo index and other graph artifacts unchanged. | `presentation/json_state.py`, `tests/unit/presentation/test_runtime_sync_s07.py` | delegated Red: `KeyError`; parent Green: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` -> 89 passed | fresh re-review passed | CLI reduced reproduction remains S04 | accepted for commit gate |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S03 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit gate | First review found P1 leak of raw audit into `.agent/tree-all.json`; implementation/test/report were updated and fresh re-review passed, confidence 0.91. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S03 | committed | S03 presentation/test/report files | S03 implementation commit, amended with this final commit-gate evidence | `git status --short --branch` -> clean after S03 commit before final evidence amendment; clean check must be rerun after amend | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` - `.agent/index-all.json` `deps.raw_direct_edges` payload.
- `tests/unit/presentation/test_runtime_sync_s07.py` - index-all raw direct edge coverage.
- `spec-dock/active/issue/report.md` - S03 observed evidence ledger.

#### コミット
- S03 implementation commit amended with final commit-gate evidence.

#### メモ
- No material implementation decisions beyond the approved plan.

---

### セッションログ（2026-06-27 S04）

#### 対象
- Step: S04 CLI `deps check --json` Reduced Reproduction
- AC/EC: AC-001, AC-002, EC-001
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S04 — CLI deps check --json Reduced Reproduction`
  - closure ids: `cl-ac001-direct-check`, `cl-ac002-non-ready`, `cl-ec001-empty-source`

#### 実施内容
- hermetic temp repo を `spec-dock init` で作成し、empty high-level source initiative が high-level epic に raw `depends_on` を持つ reduced fixture を追加した。
- public runtime script 経由で `deps check --id init-local-00001 --no-github --json` を実行し、`ready=false`、`blockers=["epic-local-00001"]`、`direct_node_dependencies` を assert した。
- S04 は test-only reproduction として完了し、runtime/source implementation は変更していない。

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_runtime_deps_s04.py

29 passed in 0.44s
```

```bash
git diff --check

pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S04 | 赤フェーズ | red-required / characterization allowed after S01-S02 | dev-coder reported the reduced scenario was already fixed by S01/S02 and currently returns returncode 3, `ready=false`, blocker `epic-local-00001`, and `direct_node_dependencies[0].expansion="empty"`. | delegated worker record | pass | No fabricated Red; S04 records public CLI characterization after earlier fix. |
| S04 | 緑フェーズ | public CLI reduced reproduction passes | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` -> 29 passed in 0.44s | command | pass | Parent-run verification on current worktree. |
| S04 | リファクタリング | guardrail satisfied | Diff stayed within `tests/cli_runtime/test_runtime_deps_s04.py`; no runtime/source implementation files changed. | diff inspection | pass | `git diff --check` passed. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S04 | none | implementation | no new closure delta | N/A | no | worker reported no material implementation decisions beyond the approved plan |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S04 | cl-ac001-direct-check | public CLI JSON exposes direct node dependency payload. | Test asserts `direct_node_dependencies` with source/target ids/kinds, empty expansion, and blocking disposition. | pass | Runtime implementation unchanged. |
| S04 | cl-ac002-non-ready | unresolved direct node dependency makes CLI JSON non-ready. | Test asserts returncode 3, `ready=false`, and blocker `epic-local-00001`. | pass | Public command surface. |
| S04 | cl-ec001-empty-source | empty high-level source does not collapse to dependency-free ready output. | Test asserts `effective_depends_on=[]` and `dependency_contexts=[]` while direct blocker remains. | pass | Separates raw direct blocker from issue readiness projection. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-ac001-direct-check | S04 | yes | characterization | delegated characterization: fixed by S01/S02 | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` | pass, 29 passed in 0.44s | Public CLI JSON payload. |
| cl-ac002-non-ready | S04 | yes | characterization | delegated characterization: fixed by S01/S02 | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` | pass, 29 passed in 0.44s | Public CLI non-ready behavior. |
| cl-ec001-empty-source | S04 | yes | characterization | delegated characterization: empty source remains blocked | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` | pass, 29 passed in 0.44s | Reduced reproduction for #235. |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-ac001-direct-check | S04 | CLI runtime test | pass | Direct payload visible publicly. |
| cl-ac002-non-ready | S04 | CLI runtime test | pass | Exit code and JSON ready state verified. |
| cl-ec001-empty-source | S04 | CLI runtime test | pass | No issue-projection false-ready. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S04 | N/A | N/A | Planned closure ids were used as-is. | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S04 | delegated | CLI runtime reproduction test | dev-coder | S04 CLI `deps check --json` Reduced Reproduction | `plan.md` S04 | `tests/cli_runtime/test_runtime_deps_s04.py`; optional `tests/cli_runtime/test_deps.py` was not needed | runtime/source implementation, live GitHub, external repo mutation, broad fixture rewrite | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` | implementation file change required or fixture rewrite broadens scope | changed files, characterization evidence, verification, no-decision statement | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S04 | dev-coder | Added hermetic public CLI reduced reproduction for empty high-level source direct dependency; no implementation files changed. | `tests/cli_runtime/test_runtime_deps_s04.py` | delegated: `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` -> 29 passed; parent: same command -> 29 passed | fresh review passed | S05 sync artifact reproduction remains pending | accepted for commit gate |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S04 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit gate | Fresh code-reviewer pass, confidence 0.90. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S04 | committed | S04 test/report files | S04 test commit, amended with this final commit-gate evidence | `git status --short --branch` -> clean after S04 commit before final evidence amendment; clean check must be rerun after amend | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/cli_runtime/test_runtime_deps_s04.py` - public CLI reduced reproduction.
- `spec-dock/active/issue/report.md` - S04 observed evidence ledger.

#### コミット
- S04 test commit amended with final commit-gate evidence.

#### メモ
- No material implementation decisions beyond the approved plan.

---

### セッションログ（2026-06-27 S05）

#### 対象
- Step: S05 CLI `sync --no-github` Raw Audit Reproduction
- AC/EC: AC-003, EC-003
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S05 — CLI sync --no-github Raw Audit Reproduction`
  - closure ids: `cl-ac003-index-all-raw`, `cl-ec003-satisfied-raw-audit`

#### 実施内容
- hermetic temp repo を `spec-dock init` で作成し、high-level source initiative が high-level epic に raw `depends_on` を持つ reduced fixture を追加した。
- public runtime script 経由で `sync --no-github --no-update-active` を実行し、`.agent/index-all.json` の `deps.raw_direct_edges` を assert した。
- Non-goal artifact guard として `.agent/index.json` と `.agent/deps-issues.json` top-level / nested `deps` へ `raw_direct_edges` を追加しないことを assert した。
- 初回 sync 後の cache を closed high-level target に加工して再度 `sync --no-github --no-update-active` を実行し、closed target でも `.agent/index-all.json` の raw direct edge が残ることを assert した。
- S05 は test-only reproduction として完了し、runtime/source implementation は変更していない。

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_runtime_deps_s04.py

30 passed in 0.99s
```

```bash
git diff --check

pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S05 | 赤フェーズ | red-required / characterization allowed after S03 | dev-coder reported the reduced scenario was already fixed by S03 and `.agent/index-all.json` currently contains `deps.raw_direct_edges` for `init-local-00001 -> epic-local-00001`; `.agent/index.json` lacks `raw_direct_edges`. | delegated worker record | pass | No fabricated Red; S05 records public CLI sync characterization after earlier fix. |
| S05 | 緑フェーズ | public CLI sync artifact reproduction passes | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` -> 30 passed in 0.99s | command | pass | Parent-run verification after reviewer finding fixes. |
| S05 | リファクタリング | guardrail satisfied | Diff stayed within `tests/cli_runtime/test_runtime_deps_s04.py`; no runtime/source implementation files changed. | diff inspection | pass | `git diff --check` passed. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S05 | `deps-raw.puml` already contains existing debug `raw_direct` labels, so absence assertion would over-constrain a non-primary artifact. | dev-coder ledger note | kept S05 focused on `.agent/index-all.json` and JSON non-goal guards for `.agent/index.json` / `.agent/deps-issues.json`; did not add `deps-raw.puml` absence assertion | N/A | no | worker ledger note; design non-goal is no contract expansion, not absence of existing debug labels |
| S05 | `.agent/deps-issues.json` nested `deps.raw_direct_edges` expansion was not guarded. | code-reviewer | added assertion that `raw_direct_edges` is absent from both top-level deps-issues payload and nested `deps` object | N/A | no | first S05 code-reviewer P1 finding |
| S05 | S05 CLI evidence did not cover closed/satisfied target raw audit before claiming EC-003. | code-reviewer | added second `sync --no-github --no-update-active` run with cached closed high-level target and asserted raw direct edge remains in `.agent/index-all.json` | cl-ec003-satisfied-raw-audit | no | first S05 code-reviewer P1 finding |
| S05 | Closed-target rerun did not prove the target remained closed, and `.agent/index.json` top-level guard was missing. | code-reviewer | added target epic GitHub linkage, asserted rerun preserves `github.state="CLOSED"`, and added top-level `.agent/index.json` raw edge absence guard | cl-ec003-satisfied-raw-audit | no | second S05 code-reviewer P1/P2 findings |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S05 | cl-ac003-index-all-raw | public CLI sync writes `.agent/index-all.json` raw direct high-level edge audit. | Test asserts `deps.raw_direct_edges` with `from`, `from_kind`, `to`, `to_kind`, and `relation`. | pass | Public artifact surface. |
| S05 | cl-ec003-satisfied-raw-audit | raw audit is maintained as full-history artifact independent of satisfied / closed target status. | Test mutates cached target epic state to `closed`, reruns `sync --no-github`, and asserts `.agent/index-all.json` still contains the same raw direct edge. | pass | Non-goal JSON artifacts also remain without `raw_direct_edges`. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-ac003-index-all-raw | S05 | yes | characterization | delegated characterization: fixed by S03 | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` | pass, 30 passed in 0.99s | Public sync artifact. |
| cl-ec003-satisfied-raw-audit | S05 | yes | characterization | delegated characterization: full-history index carries raw edge | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` | pass, 30 passed in 0.99s | Closed cached target raw edge remains in index-all, with target state asserted as `CLOSED`. |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-ac003-index-all-raw | S05 | CLI runtime sync test | pass | `.agent/index-all.json` has raw direct edge. |
| cl-ec003-satisfied-raw-audit | S05 | CLI runtime sync test and S03 presentation test | pass | S05 checks public artifact with cached closed high-level target; S03 checks presentation-level closed retention. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| boundary note | N/A | deps-raw absence assertion | N/A | Existing `deps-raw.puml` debug output can contain `raw_direct`; S05 primary contract is `.agent/index-all.json` raw audit and JSON non-goal guard. | no | yes, step review required |
| reviewer finding fix | N/A | deps-issues nested guard | N/A | S05 non-goal guard must cover nested `deps` object in `.agent/deps-issues.json`. | no | yes, re-review required |
| reviewer finding fix | cl-ec003-satisfied-raw-audit | closed target CLI artifact evidence | cl-ec003-satisfied-raw-audit | S05 closure claim now has public CLI sync evidence for a cached closed high-level target. | no | yes, re-review required |
| reviewer finding fix | cl-ec003-satisfied-raw-audit | closed target state assertion | cl-ec003-satisfied-raw-audit | S05 closed-target evidence now asserts the rerun artifact preserves `github.state="CLOSED"`. | no | yes, re-review required |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S05 | delegated | CLI runtime sync artifact reproduction test | dev-coder | S05 CLI `sync --no-github` Raw Audit Reproduction | `plan.md` S05 | `tests/cli_runtime/test_runtime_deps_s04.py`; optional `tests/cli_runtime/test_sync.py` was not needed | runtime/source implementation, live GitHub, external repo mutation, `deps-issues.json` / `deps-raw.puml` contract expansion | `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` | implementation file change required or artifact contract expansion needed | changed files, characterization evidence, verification, ledger note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S05 | dev-coder | Added hermetic public CLI sync reduced reproduction for `.agent/index-all.json` `deps.raw_direct_edges`; reviewer findings added nested deps-issues guard, cached closed-target re-sync, closed-state assertion, and top-level index guard. | `tests/cli_runtime/test_runtime_deps_s04.py` | delegated: `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` -> 30 passed; parent after fixes: same command -> 30 passed | fresh re-review passed | S07 integration guard remains pending | accepted for commit gate |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S05 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit gate | First review found nested deps-issues guard gap and missing closed/satisfied CLI evidence; second review found missing closed-state assertion and top-level index guard; after fixes fresh re-review passed, confidence 0.91. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S05 | committed | S05 test/report files | S05 test commit, amended with this final commit-gate evidence | `git status --short --branch` -> clean after S05 commit before final evidence amendment; clean check must be rerun after amend | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/cli_runtime/test_runtime_deps_s04.py` - public CLI sync artifact reduced reproduction.
- `spec-dock/active/issue/report.md` - S05 observed evidence ledger.

#### コミット
- S05 test commit amended with final commit-gate evidence.

#### メモ
- `deps-raw.puml` の既存 debug 表示は S05 の primary artifact contract ではないため、absence assertion は追加しない。

---

### セッションログ（2026-06-27 S06）

#### 対象
- Step: S06 Issue-Source High-Level Target Regression
- AC/EC: AC-004, EC-002
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S06 — Issue-Source High-Level Target Regression`
  - closure ids: `cl-ac004-issue-regression`, `cl-ec002-non-empty-source`

#### 実施内容
- 既存 issue-source -> high-level target の blocker / satisfied semantics に `direct_node_dependencies` が混入しないことを domain/application tests に追加した。
- non-empty high-level source の direct status と descendant issue readiness projection が別 field で観測できることを public CLI runtime test に追加した。
- S06 は test-only regression coverage として完了し、runtime/source implementation は変更していない。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_deps_s04.py

72 passed in 1.33s
```

```bash
git diff --check

pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S06 | 赤フェーズ | covered-existing / regression characterization | dev-coder reported pre-change characterization command passed with 71 tests; S06 adds regression coverage without known failing behavior. | delegated worker record | pass | No fabricated Red; regression hardening step. |
| S06 | 緑フェーズ | regression matrix passes required tests | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_deps_s04.py` -> 72 passed in 1.33s | command | pass | Parent-run verification on current worktree. |
| S06 | リファクタリング | guardrail satisfied | Diff stayed within allowed test files; no implementation files, `effective_depends_on` semantic expansion, or snapshot churn. | diff inspection | pass | `git diff --check` passed. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S06 | CLI non-empty high-level source regression for separate `dependency_contexts` and `direct_node_dependencies`. | implementation | added public CLI runtime test | cl-ec002-non-empty-source | no | `tests/cli_runtime/test_runtime_deps_s04.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S06 | cl-ac004-issue-regression | issue-source high-level target blocker/satisfied semantics remain covered. | Domain/application tests assert issue-source contexts keep `direct_node_dependencies == []` and existing readiness outcomes. | pass | Protects existing issue-source axis. |
| S06 | cl-ec002-non-empty-source | non-empty source direct status remains separate from descendant issue readiness. | CLI test asserts `effective_depends_on` / `dependency_contexts` and `direct_node_dependencies` are separate payload fields. | pass | Direct source edge remains visible without changing `effective_depends_on` meaning. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-ac004-issue-regression | S06 | yes | characterization | delegated pre-change command passed with 71 tests | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 72 passed in 1.33s | Regression hardening. |
| cl-ec002-non-empty-source | S06 | yes | characterization | delegated pre-change command passed with 71 tests | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 72 passed in 1.33s | Public CLI non-empty source regression. |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-ac004-issue-regression | S06 | domain/application tests | pass | Existing issue-source behavior protected. |
| cl-ec002-non-empty-source | S06 | CLI runtime test | pass | Separation of direct node dependency status from issue readiness projection. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S06 | N/A | N/A | Planned closure ids were used as-is. | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S06 | delegated | regression coverage | dev-coder | S06 Issue-Source High-Level Target Regression | `plan.md` S06 | domain/application/CLI runtime test files | broad snapshot churn, `effective_depends_on` semantic expansion, unrelated implementation refactor | `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_deps_s04.py` | semantics conflict or implementation defect requiring broader scope | changed files, regression matrix, verification, no-decision statement | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S06 | dev-coder | Added regression assertions for issue-source high-level target semantics and CLI non-empty source separation. | `tests/unit/domain/test_deps.py`, `tests/unit/application/test_check_deps.py`, `tests/cli_runtime/test_runtime_deps_s04.py` | delegated: required command -> 72 passed; parent: required command -> 72 passed | fresh review passed | S07 non-goal boundary hardening remains pending | accepted for commit gate |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S06 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit gate | Fresh code-reviewer pass, confidence 0.88. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S06 | committed | S06 test/report files | S06 test commit, amended with this final commit-gate evidence | `git status --short --branch` -> clean after S06 commit before final evidence amendment; clean check must be rerun after amend | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/unit/domain/test_deps.py` - issue-source regression assertion.
- `tests/unit/application/test_check_deps.py` - issue-source regression assertions.
- `tests/cli_runtime/test_runtime_deps_s04.py` - non-empty source CLI regression.
- `spec-dock/active/issue/report.md` - S06 observed evidence ledger.

#### コミット
- S06 test commit amended with final commit-gate evidence.

#### メモ
- No material implementation decisions beyond the approved plan.

---

### セッションログ（2026-06-27 S07）

#### 対象
- Step: S07 Non-Goal Boundary Hardening
- Boundary closures: `cl-boundary-artifacts`, `cl-boundary-storage-source`, `cl-boundary-external`
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S07 — Non-Goal Boundary Hardening`

#### 実施内容
- `.agent/index-all.json` は `deps.raw_direct_edges` を保持しつつ、`.agent/index.json` / `.agent/deps-issues.json` には `raw_direct_edges` を出さないことを追加 assertion で補強した。
- closed/satisfied 相当の high-level raw edge が `deps-raw.puml` の active visual surface に出ず、empty note になることを presentation / CLI reduced fixture の両方で固定した。
- `sync --no-github` 後も `.meta.json.depends_on` が source/target ともに保存形式のまま残ることを assert した。
- S07 は test-only boundary hardening として完了し、runtime/source implementation は変更していない。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py

92 passed in 1.56s
```

```bash
git diff --check

pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S07 | 赤フェーズ | inspect-only / covered-existing | dev-coder reported pre-change required command passed with 92 tests; S07 adds boundary assertions without known failing behavior. | delegated worker record | pass | No fabricated Red; boundary characterization step. |
| S07 | 緑フェーズ | non-goal boundary assertions pass | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` -> 92 passed in 1.56s | command | pass | Parent-run verification on current worktree. |
| S07 | リファクタリング | guardrail satisfied | Diff stayed within allowed test files; no implementation files, dogfooding generated runtime, storage migration, or external mutation. | diff inspection | pass | `git diff --check` passed. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S07 | Existing reduced fixtures needed explicit boundary assertions for storage and non-goal artifacts. | implementation | added assertions to S03/S05 reduced coverage surfaces | cl-boundary-artifacts / cl-boundary-storage-source | no | `tests/unit/presentation/test_runtime_sync_s07.py`, `tests/cli_runtime/test_runtime_deps_s04.py` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S07 | cl-boundary-artifacts | Non-goal artifacts do not become complete raw audit surfaces. | Tests assert `raw_direct_edges` is absent from `.agent/index.json`, `.agent/deps-issues.json`, and `deps-raw.puml` active visual output for closed/satisfied raw edge. | pass | `deps-raw.puml` may still show existing debug raw edges in other contexts; not promoted to complete audit. |
| S07 | cl-boundary-storage-source | `.meta.json.depends_on` storage format is not migrated by sync. | CLI reduced fixture asserts source `.meta.json.depends_on == ["epic-local-00001"]` and target remains `[]` after sync. | pass | Storage remains source of truth. |
| S07 | cl-boundary-external | Reduced flows remain hermetic and do not require live GitHub/external repo mutation. | Tests use temp repo and `--no-github`; no implementation or external mutation code added. | pass | Final QA may still inspect full diff. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-boundary-artifacts | S07 | yes | characterization | delegated pre-change command passed with 92 tests | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 92 passed in 1.56s | Non-goal artifact boundary. |
| cl-boundary-storage-source | S07 | yes | characterization | delegated pre-change command passed with 92 tests | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 92 passed in 1.56s | Storage format preserved. |
| cl-boundary-external | S07 | yes | characterization | delegated pre-change command passed with 92 tests | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | pass, 92 passed in 1.56s | Hermetic no-github reduced flows. |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-boundary-artifacts | S07 | presentation/CLI runtime tests | pass | index-all is audit surface; non-goal artifacts are not complete audit surfaces. |
| cl-boundary-storage-source | S07 | CLI runtime test | pass | `.meta.json.depends_on` remains unchanged. |
| cl-boundary-external | S07 | CLI runtime test and diff inspection | pass | No live GitHub/external repo mutation added. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | S07 | N/A | N/A | Planned boundary closure ids were used as-is. | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S07 | delegated | boundary hardening | dev-coder | S07 Non-Goal Boundary Hardening | `plan.md` S07 | presentation/CLI runtime test files | artifact contract expansion, storage migration, dogfooding generated runtime implementation edits, external mutation | `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` | boundary conflict or approved implementation defect | changed files, boundary evidence, verification, no-decision statement | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S07 | dev-coder | Added non-goal artifact, storage, and external-boundary assertions to existing reduced fixtures. | `tests/unit/presentation/test_runtime_sync_s07.py`, `tests/cli_runtime/test_runtime_deps_s04.py` | delegated: required command -> 92 passed; parent: required command -> 92 passed | fresh review passed | S90 docs impact and S99 final QA remain pending | accepted for commit gate |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S07 | step reviewer | code-reviewer | fresh | passed | no | proceed to commit gate | Fresh code-reviewer pass, confidence 0.90. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S07 | committed | S07 test/report files | S07 test commit, amended with this final commit-gate evidence | `git status --short --branch` -> clean after S07 commit before final evidence amendment; clean check must be rerun after amend | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/unit/presentation/test_runtime_sync_s07.py` - non-goal artifact boundary assertions.
- `tests/cli_runtime/test_runtime_deps_s04.py` - storage/external boundary assertions.
- `spec-dock/active/issue/report.md` - S07 observed evidence ledger.

#### コミット
- S07 test commit amended with final commit-gate evidence.

#### メモ
- `deps-raw.puml` は既存 debug raw view を持つため、全面的な absence contract ではなく complete raw audit surface に昇格しない境界として固定した。

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| `src/spec_dock/assets/spec_dock/docs/reference_deps.md` / `reference_sync.md` and dogfooding mirror `spec-dock/docs/reference_deps.md` / `reference_sync.md` | yes | doc-writer | Documented `deps check --json` top-level `direct_node_dependencies`, `.agent/index-all.json` `deps.raw_direct_edges`, non-goal artifact boundaries, and unchanged `.meta.json.depends_on` storage. Provider/dogfooding copies match by `diff -u`; `git diff --check` passed. | pass |

#### S90 セッションログ（2026-06-27）

##### 実施内容
- Provider-side docs source of truth under `src/spec_dock/assets/spec_dock/docs/` に今回の public JSON / sync artifact contract を追記した。
- Dogfooding `spec-dock/docs/` copy は secondary generated/consumer copy として同文に更新した。
- CLI help / generated context guidance は現行の `index-all` full-history guidance と矛盾しないため変更しない判断とした。

##### 実行コマンド / 結果
```bash
diff -u src/spec_dock/assets/spec_dock/docs/reference_deps.md spec-dock/docs/reference_deps.md
diff -u src/spec_dock/assets/spec_dock/docs/reference_sync.md spec-dock/docs/reference_sync.md
git diff --check

pass
```

##### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S90 | doc-writer | Updated dependency/sync references for `direct_node_dependencies`, `deps.raw_direct_edges`, and non-goal artifact boundaries. | `src/spec_dock/assets/spec_dock/docs/reference_deps.md`, `src/spec_dock/assets/spec_dock/docs/reference_sync.md`, `spec-dock/docs/reference_deps.md`, `spec-dock/docs/reference_sync.md` | `diff -u` provider/dogfooding docs matched; `git diff --check` passed; pytest not run for docs-only change | fresh spec-reviewer passed | CLI help text not changed because current guidance is not contradictory | accepted for commit gate |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | required command sufficient after recording final ledger; no broader external/CLI lane required | initial final QA review failed because this final ledger omitted the integrated validation evidence. Fresh QA re-review passed and raised non-blocking P2 to cover epic source reduced behavior. Parent added `test_cli_deps_check_json_blocks_epic_source_direct_node_dependency`; `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` -> 32 passed; final required command `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` -> 135 passed in 1.56s. | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | initial final code review found that direct high-level raw dependencies with lifecycle `unknown` and all descendant issues done could be classified as satisfied before fail-closed unknown handling. Fixed `_high_level_lifecycle_for_direct_dependency` to return indeterminate for `unknown` before descendant aggregate satisfaction and added `test_inspect_target_deps_fails_closed_for_unknown_direct_node_lifecycle_with_done_descendants`. Fresh code re-review passed with no findings. | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | initial final spec review found missing S99 evidence and a stale implementation summary that still said JSON/sync were unimplemented. Updated this final ledger and replaced the stale summary with the S02-S07 completed state. Second final spec review found QA/code/spec rows still pending; updated QA/code pass evidence and latest final command result. Fresh final spec re-review passed with no findings. | 2 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| QA/code/spec final reviewer gates passed; final commit amended with this commit-gate evidence; post-commit clean check `git status --short --branch` -> clean before PR push | final code/test/report fix for unknown direct high-level lifecycle, epic-source CLI regression, and S99 ledger closure | final response / PR #242 | ready |

### PR CI repair（2026-06-27）
| 対象 | 失敗内容 | 修正 | 検証 | 結果 |
|---|---|---|---|---|
| PR #242 `provider-tests` | `make lint` failed on ruff import order and format check for `deps.py`, `json_state.py`, and `tests/cli_runtime/test_runtime_deps_s04.py`. | `uv run ruff check --fix src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`; `uv run ruff format src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py tests/cli_runtime/test_runtime_deps_s04.py` | `make lint` -> pass; `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py` -> 135 passed in 1.64s | ready for PR branch update |
| PR #242 `provider-tests` | After formatting repair, `uv run pytest` failed on an older CLI JSON key expectation and checked-in dogfooding snapshot/mirror parity. | Updated `tests/cli_runtime/test_deps.py` to include additive `direct_node_dependencies` and direct node blocker behavior; synced provider runtime assets to dogfooding mirror; updated checked-in dogfooding `.meta.json` snapshot for iss-00235. | focused failing tests -> pass; `make lint` -> pass; `uv run pytest` -> 1419 passed, 76 skipped in 798.07s | ready for PR branch update |

## 遭遇した問題と解決 (任意)
- 問題: final review で、direct node dependency 側の高水準 target lifecycle が `unknown` の場合に、descendant issues が全て done だと `all_descendant_issues_done` として satisfied になり得る判定順序が見つかった。
  - 解決: `unknown` lifecycle を descendant aggregate satisfaction より先に indeterminate として扱い、focused regression test を追加した。
- 問題: final QA で、initiative source の reduced coverage はあるが epic source 自体の `.meta.json.depends_on` を public CLI で検証する reduced test が不足していると指摘された。
  - 解決: `deps check --id <epic> --json` で epic source direct node dependency が `direct_node_dependencies` に出ることを検証する CLI regression test を追加した。
- 問題: PR #242 の `provider-tests` で static analysis が失敗した。
  - 解決: ruff の import order / format 差分を修正し、`make lint` と final pytest lane を再実行した。
- 問題: PR #242 の `provider-tests` で full pytest が失敗した。
  - 解決: additive JSON contract の既存 CLI test expectation、dogfooding runtime mirror、checked-in dogfooding `.meta.json` snapshot を更新し、`uv run pytest` full suite を再実行した。

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- ...

## 省略/例外メモ (必須)
- 該当なし
