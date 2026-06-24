---
種別: 実装報告書（Issue）
ID: "iss-00237"
タイトル: "Analyze Manual Test Routing Failures"
関連GitHub: ["#237"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-24"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00237 Analyze Manual Test Routing Failures — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | test-strategy | orchestrator | MT-009 / MT-024 の runtime routing failure が policy matrix ではなく `_classify_task_kind` の substring heuristic に起因する | Option A: 否定文除外のみ; Option B: evidence-based classifier; Option C: explicit `task_kind` / `risk_tags` schema | Option B をこの issue で採用し、Option C は follow-up 候補にする | Option B は2つの FAIL を同時に解消でき、変更範囲を `context_packets.py` と CLI routing regression tests に閉じられる | promoted_to_design / promoted_to_plan | `discussions/20260624t062220z-disc-routing-repair-design-options.md`, `requirement.md`, `design.md`, `plan.md` | explicit field 化は follow-up 候補 |
| D-002 | resolved | test-strategy | code-reviewer | S02 classifier fix に reviewer-directed regression を追加する必要があり、当初の S02 allowed paths が production file のみに狭すぎた | A: tests 追加を戻す; B: S02 allowed paths を reviewer-directed regression に限って拡張 | B を採用し、`tests/cli_runtime/test_workflow_context_routing.py` への S02 reviewer-directed regression 追加だけを許可する | reviewer finding の false-negative 経路を再発防止するには public CLI regression が必要。変更範囲は既存 S01 test file に限定される | promoted_to_plan / applied | `plan.md`, code-reviewer finding, targeted pytest 22 passed | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | source_role | claim | 対象（target_artifact） | target_section | 判断理由（rationale） | evidence_strength | 証跡（evidence_path） | adopter | reviewer | blocking | 次アクション（next_action） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | discussion / research | orchestrator / deep-consultant synthesis | MT-009 / MT-024 の root cause は `_classify_task_kind` の substring heuristic であり、Option B evidence-based classifier が最小十分な修正方針である | `requirement.md`, `design.md`, `plan.md` | purpose / scope / precedence / execution steps / closure index | failure analysis、Deep Consultant 由来の Option B 推奨、runtime matrix 非原因の判断を canonical artifacts に採用した | high: manual test evidence + source inspection + design options discussion | `discussions/20260624t062221z-research-runtime-routing-failure-analysis.md`, `discussions/20260624t062338z-research-mt009-runtime-task-routing-failure.md`, `discussions/20260624t062339z-research-mt024-bug-exploration-routing-failure.md`, `discussions/20260624t062220z-disc-routing-repair-design-options.md` | main orchestrator | spec-reviewer pass, subagent `019ef862-abd2-7863-9dbb-ac5775c8f284` | no | 実装で S01/S02 を実行し、結果を本 report に追記 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | runtime task を docs-only に過小分類せず、否定文だけで security-sensitive に過剰分類しないことを AC-001 / AC-002 に固定 | security-sensitive / docs-only / migration true positive 維持を AC-003 / AC-004 / AC-005 に固定 | 低: regression tests を primary objective と safety objective の両方に置く | pass: spec-reviewer planning review |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | manual test summary、routing failure research、design options discussion、`context_packets.py` / `context_routing.py` inspection | なし | adopted | pass: spec-reviewer subagent `019ef862-abd2-7863-9dbb-ac5775c8f284` | no | `requirement.md` を approved に更新 |
| design | Option B evidence-based classifier、既存 `_classify_task_kind` / routing matrix / CLI tests inspection | なし | adopted | pass: spec-reviewer subagent `019ef862-abd2-7863-9dbb-ac5775c8f284` | no | `design.md` を approved に更新 |
| plan | AC/EC、regression test obligations、implementation boundary、follow-up candidates | なし | adopted | pass: spec-reviewer subagent `019ef862-abd2-7863-9dbb-ac5775c8f284` | no | `plan.md` を approved に更新 |

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
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

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
- S01 では runtime routing failure を再現する CLI runtime regression tests を追加した。
- S02 では `_classify_task_kind` を evidence-based classifier に変更し、S01 の Red を Green にした。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-24 16:16 JST - S01）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, EC-001, EC-002, EC-003
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S01 — routing classifier regression を赤で固定する`
  - closure ids: tc-237-001, tc-237-002, tc-237-003, tc-237-004, tc-237-005

#### 実施内容
- `tests/cli_runtime/test_workflow_context_routing.py` に CLI public output を使う regression / characterization tests を追加した。
- tc-237-001 / tc-237-002 は現行 production code に対して expected Red として観測した。
- tc-237-003 / tc-237-004 / tc-237-005 は existing true positive guard として同じ targeted run 内で pass した。
- Material implementation decisions: No material implementation decisions beyond the approved plan.

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_workflow_context_routing.py

expected Red: 2 failed, 16 passed
- tc-237-001: expected `runtime`, actual `docs-only`
- tc-237-002: expected not `security-sensitive`, actual `security-sensitive`
- tc-237-003〜tc-237-005: covered-existing guards pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | Red / alternative | tc-237-001〜tc-237-002 red-required; tc-237-003〜tc-237-005 covered-existing | targeted pytest: 2 failed, 16 passed | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | S01 は expected Red。Green 化は S02 の対象 |
| S01 | Refactor | guardrail satisfied | production code 変更なし、test-only diff | diff inspection / code-reviewer | pass | allowed path のみ変更 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | none | dev-coder / orchestrator | recorded | N/A | no | S01 approved test list のみ |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-237-001〜tc-237-005 | tests added; Red evidence recorded; closure coverage linked | tests added in `tests/cli_runtime/test_workflow_context_routing.py`; targeted pytest expected Red; code-reviewer pass | pass | S02 が Green 化を担当 |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-237-001 / `test_workflow_next_runtime_paths_override_docs_only_verification_phrase` | S01 | yes | red-required | expected Red | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | fail as expected | actual `docs-only` |
| tc-237-002 / `test_workflow_next_negated_security_phrase_does_not_escalate` | S01 | yes | red-required | expected Red | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | fail as expected | actual `security-sensitive` |
| tc-237-003 / `test_workflow_next_affirmative_authz_terms_still_escalate` | S01 | yes | covered-existing | true positive guard | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | security true positive preserved |
| tc-237-004 / `test_workflow_next_explicit_docs_only_still_routes_to_doc_writer` | S01 | yes | covered-existing | true positive guard | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | docs-only true positive preserved |
| tc-237-005 / `test_workflow_next_affirmative_migration_terms_still_route_to_rollback_plan` | S01 | yes | covered-existing | true positive guard | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | migration true positive preserved |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-237-001 | S01 | targeted pytest | pass | expected Red captured |
| tc-237-002 | S01 | targeted pytest | pass | expected Red captured |
| tc-237-003 | S01 | targeted pytest | pass | covered-existing guard |
| tc-237-004 | S01 | targeted pytest | pass | covered-existing guard |
| tc-237-005 | S01 | targeted pytest | pass | covered-existing guard |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | tc-237-001〜tc-237-005 | N/A | tc-237-001〜tc-237-005 | approved plan 通り | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / issue-execution workflow | `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock` | iss-00237 | current session | dev-coder, code-reviewer | S01 allowed path only; no production code; no push / PR | issue complete / scope change / user revocation | none | proceed to S02 after S01 commit gate |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | test-only runtime regression slice | dev-coder | tc-237-001〜tc-237-005 tests | `plan.md` S01 | `tests/cli_runtime/test_workflow_context_routing.py` | production code / `src_spec_dock/**` / canonical docs/report | targeted pytest expected Red | fixture cannot reproduce | changed files, tests, verification, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | tc-237-001〜tc-237-005 の CLI regression / guard tests を追加 | `tests/cli_runtime/test_workflow_context_routing.py` | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` -> expected Red: 2 failed, 16 passed | code-reviewer pass | S01 単独では Red。S02 で Green 化 | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | passed | N/A | proceed | subagent `019ef87b-1299-7f90-a9a9-004279d81564`, no findings |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | pending commit | `tests/cli_runtime/test_workflow_context_routing.py`, `report.md` S01 evidence | this S01 ledger entry | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `tests/cli_runtime/test_workflow_context_routing.py` - routing classifier regression / guard tests
- `spec-dock/active/issue/report.md` - S01 execution evidence

#### メモ
- S01 の Red は approved plan 通り。S02 で production code を変更し Green 化する。

### セッションログ（2026-06-24 16:22 JST - S02）

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, EC-001, EC-002, EC-003
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S02 — evidence-based classifier を実装する`
  - closure ids: tc-237-001, tc-237-002, tc-237-003, tc-237-004, tc-237-005, tc-237-006

#### 実施内容
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py` の `_classify_task_kind` を evidence-based precedence に変更した。
- affirmative security、affirmative migration、runtime evidence、explicit docs-only、runtime fallback の順に分類する。
- 否定・禁止・停止条件行にだけ出る high-risk / migration word は affirmative evidence から除外する。
- `docs-only verification` / `tests または docs-only verification` は docs-only 判定から除外する。
- Material implementation decisions: No material implementation decisions beyond the approved plan.

#### 実行コマンド / 結果
```bash
uv run pytest tests/cli_runtime/test_workflow_context_routing.py

22 passed in 34.28s

git diff --check

pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S02 | Green | tc-237-001〜tc-237-006 Green | targeted pytest: 22 passed | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | S01 Red と reviewer-directed regressions が Green |
| S02 | Refactor | classifier helper は allowed file 内に限定 | `git diff --check` pass; allowed file only | command / diff inspection | pass | no policy matrix change |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02 | classifier は heuristic のまま | dev-coder / design risk | follow-up candidate として既存 D-001 / design に維持 | N/A | no | explicit `task_kind` / `risk_tags` field 化は scope 外 |
| S02 | same-line guard phrase による high-risk false negative | code-reviewer | reviewer-directed regression を追加し classifier を explicit negated evidence span 判定へ修正 | reviewer-directed | no | code-reviewer finding; targeted pytest 22 passed |
| S02 | weak phrase と同じ行の explicit docs-only marker false negative | code-reviewer | reviewer-directed regression を追加し explicit marker を優先 | reviewer-directed | no | code-reviewer finding; targeted pytest 22 passed |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S02 | tc-237-001〜tc-237-006 | classifier changed and tests Green; AC/EC 全対応 | `context_packets.py` changed; targeted pytest 22 passed; `git diff --check` pass | pass | reviewer-directed regressions included |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-237-001 / `test_workflow_next_runtime_paths_override_docs_only_verification_phrase` | S02 | yes | red-required -> Green | S01 expected Red | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | runtime evidence overrides weak docs-only phrase |
| tc-237-002 / `test_workflow_next_negated_security_phrase_does_not_escalate` | S02 | yes | red-required -> Green | S01 expected Red | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | negated high-risk phrase no longer escalates |
| tc-237-003 / `test_workflow_next_affirmative_authz_terms_still_escalate` | S02 | yes | covered-existing | S01 pass | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | security true positive preserved |
| tc-237-004 / `test_workflow_next_explicit_docs_only_still_routes_to_doc_writer` | S02 | yes | covered-existing | S01 pass | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | docs-only true positive preserved |
| tc-237-005 / `test_workflow_next_affirmative_migration_terms_still_route_to_rollback_plan` | S02 | yes | covered-existing | S01 pass | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | migration true positive preserved |
| tc-237-006 / targeted routing suite | S02 | yes | covered-existing | S01 expected Red | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` | pass | full targeted suite Green: 22 passed |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-237-001 | S02 | targeted pytest | pass | AC-001 / EC-001 |
| tc-237-002 | S02 | targeted pytest | pass | AC-002 / EC-002 |
| tc-237-003 | S02 | targeted pytest | pass | AC-003 / EC-003 |
| tc-237-004 | S02 | targeted pytest | pass | AC-004 |
| tc-237-005 | S02 | targeted pytest | pass | AC-005 |
| tc-237-006 | S02 | targeted pytest | pass | AC-006 |
| reviewer-directed same-line security guard | S02 | targeted pytest | pass | prevents high-risk false negative |
| reviewer-directed same-line docs-only weak phrase | S02 | targeted pytest | pass | preserves explicit docs-only true positive |
| reviewer-directed same-line migration guard | S02 | targeted pytest | pass | preserves migration true positive |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | reviewer-directed same-line regressions | `test_workflow_next_affirmative_authz_terms_with_unrelated_guard_still_escalate`; `test_workflow_next_explicit_docs_only_marker_with_weak_phrase_still_routes_to_doc_writer`; `test_workflow_next_affirmative_migration_terms_with_unrelated_guard_still_route_to_rollback_plan`; `test_workflow_next_affirmative_migration_terms_after_unrelated_guard_still_route_to_rollback_plan` | tc-237-003 / tc-237-004 / tc-237-005 | code-reviewer finding への bounded fix | yes: S02 allowed paths を reviewer-directed regression に限って拡張 | yes, S02 re-review |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02 | delegated | production classifier change plus reviewer-directed regressions | dev-coder | evidence-based `_classify_task_kind`; reviewer-directed same-line regression tests | `plan.md` S02 amended allowed paths | `context_packets.py`; `tests/cli_runtime/test_workflow_context_routing.py` reviewer-directed regressions only | domain routing matrix / workflow_state / docs templates | targeted pytest Green | policy matrix change required | changed files, verification, risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S02 | dev-coder | `_classify_task_kind` を evidence-based precedence に変更し、reviewer-directed same-line regressions を追加 | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py`, `tests/cli_runtime/test_workflow_context_routing.py` | `uv run pytest tests/cli_runtime/test_workflow_context_routing.py` -> 22 passed; `git diff --check` -> pass | code-reviewer pass | heuristic risk remains | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | code-reviewer | fresh | passed | N/A | proceed | subagent `019ef882-387c-7a30-97aa-44f45e538369`, no findings after re-review |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S02 | pending review / commit | `context_packets.py`, `tests/cli_runtime/test_workflow_context_routing.py`, `plan.md` S02 amendment, `report.md` S02 evidence | this S02 ledger entry | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/context_packets.py` - evidence-based task kind classifier
- `tests/cli_runtime/test_workflow_context_routing.py` - reviewer-directed same-line regression tests
- `spec-dock/active/issue/plan.md` - S02 allowed paths amendment for reviewer-directed regressions
- `spec-dock/active/issue/report.md` - S02 execution evidence

#### メモ
- operator-visible docs update は不要。explicit field 化は follow-up candidate のまま。

### セッションログ（2026-06-24 HH:MM - HH:MM）

#### 対象
- Step: S01, S02, ...
- AC/EC: AC-___, EC-___
- 計画上の出典（Planned source）:
  - `plan.md` section:
  - closure ids:

#### 実施内容
- ...

#### 実行コマンド / 結果
```bash
<command>

<result>
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required / covered-existing / inspect-only / manual-required | ... | `command` / 文書点検（docs inspection） / 手動記録（manual record） | pass / approved-no-op / fail / blocked | ... |
| S01 | 緑フェーズ（Green） | ... | ... | `command` / 点検（inspection） / 手動記録（manual record） | pass / fail / blocked | ... |
| S01 | リファクタリング（Refactor） | guardrail satisfied / no refactor needed | ... | 差分点検（diff inspection） / command | pass / approved-no-op / fail / blocked | ... |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | none / ... | implementation / review / QA / user report | recorded / added test / deferred / amended plan | tc-001 / new | yes / no | ... |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-001 | ... | ... | pass / approved-no-op / fail / blocked | ... |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | red-required / covered-existing / inspect-only / manual-required | ... | ... | pass / approved-no-op / fail / blocked | ... |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001 | S01 | ... | pass / approved-no-op / fail / blocked | ... |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none / added / removed / changed / alias-mapped | tc-001 | tc-001 / test-name | tc-001 | ... | yes / no | yes / no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / explicit approval / none | ... | iss-00237 | current session / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none / denied / unavailable / host conflict | proceed / ask user / block gate / record waiver request |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated / approved-local-execution / degraded mode | multi-layer / shipped scaffold / pattern analysis / integration / large worker scope / none | repo-analyst / dev-coder / doc-writer / N/A | ... | ... | ... | ... | ... | ... | worker summary / changed files / verification / risks / integration decision | pass / fail / blocked |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder / doc-writer / repo-analyst | ... | `path/to/file` | `command` -> pass / docs-only inspection -> pass | pass / fail / unavailable / denied / waived / provisional | none / ... | accepted / rejected / needs follow-up |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer / final reviewer | code-reviewer / spec-reviewer / qa-reviewer | fresh / stale | passed / failed / unavailable / denied / waived / provisional | yes / no / N/A | proceed / blocked / incomplete / follow-up required | ... |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed / approved-no-op | ... | <hash or final ledger reference> | `git status --short` -> clean | ... | ... | ... | ... |

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- <hash> <message>

#### メモ
- ...

---

### セッションログ（2026-06-24 HH:MM - HH:MM）

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes / no | doc-writer / N/A | ... | pass / fail / blocked |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added / already sufficient / not applicable | ... | pass / fail / blocked |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | ... | 0 | pass / fail / blocked |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | ... | 0 | pass / fail / blocked |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| ... | ... | final response / PR / issue comment / other external delivery evidence | ready / blocked |

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...

## 今後の推奨事項 (任意)
- ...

## 省略/例外メモ (必須)
- 該当なし
