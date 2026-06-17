---
種別: 実装報告書（Issue）
ID: "iss-00193"
タイトル: "Node Level Dependency Mutation"
関連GitHub: ["#193"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00193 Node Level Dependency Mutation — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合はこの section を残して `No decision entries.` を明示する。本 issue では D-001 を記録済み。

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
| D-001 | resolved | interpretation | orchestrator + user answer | `deps add/remove` を initiative / epic / issue に広げる際、raw node-level cycle を保存前に拒否するかが未確定だった | Option A: raw node-level graph も検証; Option B: issue-level compiled graph 主体; Option C: 保存後に sync/check/validate へ委ねる | Option A を採用し、raw node-level cycle は配下 issue の有無に関係なく保存前に拒否する | 空 epic / initiative では現時点の issue-level graph が空でも、後から child issue を追加した瞬間に循環が顕在化するため | applied | `discussions/20260617t000842z-interview-node-dependency-validation-boundary.md`; `requirement.md` | design / plan authoring で validation boundary と tests へ反映する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md` | GitHub Issue #193、親 Epic、現行 deps reader / mutation implementation / tests の調査結果を要件の背景・スコープ・AC に採用した | `discussions/20260617t000620z-research-issue-193-node-dependency-mutation-research.md`; `requirement.md` | requirement spec-review を実施する |
| EAL-002 | adopted | discussion/interview | `requirement.md` | ユーザーが Option A を採用し、raw node-level cycle を保存前にブロックする方針を確定したため、非交渉制約と AC/EC に採用した | `discussions/20260617t000842z-interview-node-dependency-validation-boundary.md`; `requirement.md` | design / plan authoring で validation strategy と test obligation に反映する |
| EAL-003 | adopted | spec-reviewer finding | `requirement.md` | Requirement review failed on missing ancestor/container dependency handling and docs-impact scope. Option A の将来 invalid state 防止に整合させるため、ancestor dependency rejection と `workflow_issue.md` docs impact を要件へ採用した | `spec-reviewer` review for requirement gate; `requirement.md` | rerun fresh requirement spec-review |
| EAL-004 | adopted | system-architect discussion draft | `design.md` | Delegated draft が raw + compiled 二段 validation、direct-vs-inherited mutation boundary、file/module change plan、test/docs impact を要件に沿って提示したため canonical design に採用した | `discussions/20260617t-design-node-level-dependency-mutation.md`; `design.md` | run fresh design spec-review |
| EAL-005 | adopted | spec-reviewer finding | `design.md` | Design review passed with non-blocking P3 finding that module diagram metadata was missing. Phase design UML contract に合わせ、Title / answered question / scope / excluded details / update trigger を追加した | `spec-reviewer` design review; `design.md` | rerun fresh design spec-review after metadata fix |
| EAL-006 | adopted | implementation-planner discussion draft | `plan.md` | Delegated draft が S01/S02/S03/S04/S90/S99、SLCI、step-local delegation contracts、concrete test seeds、docs impact、final quality gate を reviewed design に沿って提示したため canonical plan に採用した | `discussions/20260617t-plan-node-level-dependency-mutation.md`; `plan.md` | run fresh plan spec-review |
| EAL-007 | adopted | spec-reviewer finding | `plan.md` | Initial plan review failed because S01 was tests-only but required Green through runtime changes, S02 helper work lacked a standalone verification path, and S01 overclaimed EC-005. The plan was revised so S01 closes raw validation foundation with unit tests, S02 closes public CLI integration, S03 closes direct-edge semantics, and closure mappings no longer overclaim EC-005. | `spec-reviewer` plan review; `plan.md` | rerun fresh plan spec-review after executable-step fixes |
| EAL-008 | adopted | spec-reviewer finding | `plan.md`; `report.md` | Plan review passed with P2 auditability findings: stale no-decision placeholder in report and missing explicit S03/S04 regression seeds. Placeholder was qualified and S03/S04 concrete seeds were added for issue->issue regression, preflight-first, and post-sync guardrails. | `spec-reviewer` plan review; `plan.md`; `report.md` | rerun fresh plan spec-review after P2 cleanup |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `deps add/remove` を issue-only から initiative / epic / issue node-level mutation へ拡張する要件を `requirement.md` に具体化した | Existing issue->issue behavior、`.meta.json` SoT、preflight-first、no dual-read、raw cycle/ancestor/descendant rejection を維持する制約を明記した | low | pass: fresh requirement spec-review passed after ancestor/docs fixes |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | GitHub Issue #193; parent epic docs; `reference_deps.md`; `workflow_issue.md`; `mutate_deps.py`; `deps_reader.py`; `tests/cli_runtime/test_deps.py`; research/interview discussions; first spec-review findings | Answered: `discussions/20260617t000842z-interview-node-dependency-validation-boundary.md`; reviewer gap fixed: ancestor/container dependency rejection and workflow docs impact | adopted | pass: fresh `spec-reviewer` returned no findings after fixes | no | promote to design authoring and request `system-architect` discussion draft |
| design | Reviewed `system-architect` discussion draft; verified scope-limited draft path; inspected current runtime/docs/tests impact; integrated selected evidence into canonical `design.md`; fixed non-blocking diagram metadata finding | none | adopted: raw + compiled validation, direct edge mutation boundary, module/file plan, test/docs strategy | pass: fresh `spec-reviewer` returned no findings after metadata fix | no | promote to plan authoring and request `implementation-planner` discussion draft |
| plan | Reviewed `implementation-planner` discussion draft; verified scope-limited draft path; integrated S01/S02/S03/S04/S90/S99 execution contract, SLCI, delegation contracts, concrete test seeds, docs/final gates into canonical `plan.md`; fixed initial reviewer findings by making S01/S02 independently closable; fixed P2 auditability findings | none | adopted: implementation order and closure obligations | pass: final fresh `spec-reviewer` returned no findings after P2 cleanup | no | execution handoff ready |

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
| system-architect | iss-00193 | `discussions/20260617t-design-node-level-dependency-mutation.md` | `requirement.md`; parent epic docs; workflow/authoring docs; runtime deps files; `tests/cli_runtime/test_deps.py`; prior discussions | `design.md` | adopted | `design.md` | pass: created exactly one flat discussion draft; no canonical/source/test/doc/config/GitHub edits by delegate observed | integrated into canonical design by main orchestrator | Mermaid diagram form replaced with PlantUML module diagram; helper names treated as suggestions | none | pass: fresh design spec-review returned no findings after metadata fix | design promoted |
| implementation-planner | iss-00193 | `discussions/20260617t-plan-node-level-dependency-mutation.md` | `requirement.md`; `design.md`; parent epic docs; workflow/authoring docs; runtime deps files; `tests/cli_runtime/test_deps.py`; design discussion draft | `plan.md` | adopted | `plan.md` | pass: created exactly one flat discussion draft; `git diff --check -- <draft>` passed; no canonical/source/test/doc/config/GitHub edits by delegate observed | integrated into canonical plan by main orchestrator | Draft narrative compressed into executable contract; helper-level unit tests kept conditional; final plan cleanup applied after reviewer findings | none | pass: final fresh plan spec-review returned no findings | plan promoted / execution handoff ready |

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

## 実行ハンドオフ準備（Execution Handoff Readiness / Authoring）
| 対象 | 状態 | 根拠 | 次アクション |
|---|---|---|---|
| iss-00193 issue planning | ready | `requirement.md`, `design.md`, `plan.md` all have fresh `spec-reviewer` pass; `./spec-dock/scripts/spec-dock validate` passed with `nodes=97`; `git diff --check` passed | Start S01 from `plan.md` with `dev-coder`, then follow per-step review/commit gates |

## 実装サマリー (任意)
- S01 では raw node-level dependency graph の domain validation helper を追加し、self / ancestor-container / descendant / cycle を unit level で拒否できる foundation を実装した。
- Public `deps add/remove` mutation path への統合、direct edge add/remove semantics、docs/help 更新は S02 以降で扱う。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-17 S01）

#### 対象
- Step: S01
- AC/EC: AC-006, AC-007, EC-001, EC-002, EC-003, EC-004
- 計画上の出典（Planned source）:
  - `plan.md` section: S01 raw node validation foundation
  - closure ids: slci-ac-006, slci-ac-007, slci-ec-001, slci-ec-002, slci-ec-003, slci-ec-004

#### 実施内容
- `dev-coder` に S01 のみを委任し、domain helper と unit tests を許可範囲の 2 ファイルだけに実装した。
- 親側で diff scope、focused unit test、diff whitespace を確認した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/domain/test_deps.py

6 passed in 0.01s

git diff --check -- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py tests/unit/domain/test_deps.py

pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required | 新規 helper 未実装状態で新規 tests が `AttributeError` により `4 failed, 2 passed` | `uv run pytest tests/unit/domain/test_deps.py` by `dev-coder` | pass | planned helper absence を Red として観測 |
| S01 | 緑フェーズ（Green） | focused unit Green | `6 passed` | `uv run pytest tests/unit/domain/test_deps.py` by `dev-coder` and parent rerun | pass | parent rerun observed `6 passed in 0.01s` |
| S01 | リファクタリング（Refactor） | guardrail satisfied / no refactor needed | 許可範囲 2 ファイルのみ、追加 refactor なし、whitespace check pass | diff inspection; `git diff --check -- src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py tests/unit/domain/test_deps.py` | pass | existing issue-level functions unchanged |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | Public error code mapping is not fixed in S01 | implementation | recorded for S02 integration | slci-ac-006 / slci-ac-007 | no | domain helpers raise `RuntimeError` in existing domain style; S02 maps application/CLI errors |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | slci-ac-006, slci-ac-007, slci-ec-001, slci-ec-002, slci-ec-003, slci-ec-004 | Raw node-level self / ancestor-container / descendant / cycle are rejected before mutation integration; empty epic cycle is detected | domain helper tests in `tests/unit/domain/test_deps.py`; `uv run pytest tests/unit/domain/test_deps.py` -> `6 passed` | pass | S02 still owns public mutation path integration |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-s01-001 | S01 | yes | red-required | helper missing produced `AttributeError` before implementation | `uv run pytest tests/unit/domain/test_deps.py` | pass | raw cycle between empty epics rejected |
| tc-s01-002 | S01 | yes | red-required | helper missing produced `AttributeError` before implementation | `uv run pytest tests/unit/domain/test_deps.py` | pass | source cannot depend on ancestor/container |
| tc-s01-003 | S01 | yes | red-required | helper missing produced `AttributeError` before implementation | `uv run pytest tests/unit/domain/test_deps.py` | pass | source cannot depend on descendant |
| tc-s01-004 | S01 | yes | red-required | helper missing produced `AttributeError` before implementation | `uv run pytest tests/unit/domain/test_deps.py` | pass | source cannot depend on itself |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| slci-ac-006 | S01 | `tc-s01-001`; `uv run pytest tests/unit/domain/test_deps.py` | pass | empty epic raw cycle rejected |
| slci-ac-007 | S01 | `tc-s01-002`, `tc-s01-003`, `tc-s01-004`; `uv run pytest tests/unit/domain/test_deps.py` | pass | self / ancestor / descendant rejected |
| slci-ec-001 | S01 | `tc-s01-001`; `uv run pytest tests/unit/domain/test_deps.py` | pass | cycle between empty epics rejected |
| slci-ec-002 | S01 | `tc-s01-002`; `uv run pytest tests/unit/domain/test_deps.py` | pass | issue -> parent epic rejected |
| slci-ec-003 | S01 | `tc-s01-003`; `uv run pytest tests/unit/domain/test_deps.py` | pass | epic -> child issue rejected |
| slci-ec-004 | S01 | `tc-s01-002`; `uv run pytest tests/unit/domain/test_deps.py` | pass | epic -> parent initiative rejected |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| alias-mapped | tc-s01-001..tc-s01-004 | new unit test methods in `tests/unit/domain/test_deps.py` | slci-ac-006, slci-ac-007, slci-ec-001, slci-ec-002, slci-ec-003, slci-ec-004 | Plan listed concrete seeds but not function names; test names are implementation aliases | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/e0dd/spec-dock` | iss-00193 | current session | dev-coder, code-reviewer | same repo, active issue, session, named role; S01 bounded write scope; no destructive action / publishing / credentialed access / scope expansion / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | workflow requires implementation delegation for source/test changes | dev-coder | raw node validation foundation only | `plan.md` S01 | `domain/deps.py`; `tests/unit/domain/test_deps.py` | CLI/application/infra writer/docs/help/canonical issue docs/report/GitHub state | `uv run pytest tests/unit/domain/test_deps.py` | scope expansion, source/test outside allowed paths, failed focused tests | worker summary / changed files / verification / risks / integration decision | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Added `validate_raw_node_dependency_graph` and `ensure_node_dependency_add_would_be_valid`; added tests for empty epic cycle and self / ancestor / descendant rejection | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`; `tests/unit/domain/test_deps.py` | `uv run pytest tests/unit/domain/test_deps.py` -> `6 passed`; `git diff --check -- ...` -> pass | pass: fresh code-reviewer rerun returned no findings | Public error code mapping deferred to S02 | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | no parent implementation exception used |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | fresh | failed | no | follow-up required | First review found S01 code/tests in scope but report evidence placeholders blocked gate closure |
| S01 | step reviewer rerun | code-reviewer | fresh | passed | no | proceed to commit gate | Fresh rerun returned no findings; S02 should add compiled candidate map integration tests |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | S01 code/tests/report evidence plus issue planning scaffold imported before execution | final S01 commit containing this report ledger | `git status --short` -> clean; `./spec-dock/scripts/spec-dock validate` -> `spec-dock: ok (validate) nodes=97` | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py` - raw node dependency validation helper を追加。
- `tests/unit/domain/test_deps.py` - S01 raw validation unit tests を追加。
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00193-node-level-deps-add-remove/report.md` - S01 observed evidence ledger を記録。

#### コミット
- final S01 commit: `feat(deps): ノード依存の生グラフ検証を追加`

#### メモ
- S01 の first code-reviewer gate は report evidence 未記録により fail。コード差分自体の blocking finding はなし。

---

### セッションログ（2026-06-17 HH:MM - HH:MM）

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
