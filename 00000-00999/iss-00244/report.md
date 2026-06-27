---
種別: 実装報告書（Issue）
ID: "iss-00244"
タイトル: "Simplify Issue Execution Guidance Into Plan Centric Preflight Validation"
関連GitHub: ["#244"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00244 Simplify Issue Execution Guidance Into Plan Centric Preflight Validation — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | user / orchestrator | `guidance issue-execution` を step-by-step dynamic selector として維持するか、plan-centric preflight validator へ縮退するか。 | dynamic selector 維持; plan-centric preflight; hybrid fallback | plan-centric preflight を採用し、実行順序・レビュー・品質ゲートは `plan.md` に集約する。 | ユーザーは複雑な動的状態管理より、実装計画書一本に作業契約を集約する方向を支持した。 | applied | `discussions/20260627t131746z-research-plan-centric-guidance-requirement-preparation.md`; `discussions/20260627t132248z-disc-plan-centric-guidance-requirement-scope-synthesis.md`; `requirement.md`; `design.md`; `plan.md` | なし |
| D-002 | resolved | compatibility | user | 既存の `workflow next` / dynamic guidance field 互換を残すか。 | compatibility shim; hard cutover | hard cutover を採用し、不要な interface / field は削除対象にする。 | ユーザーが「hard cutoverを採用します。不要なインターフェースやフィールドは削除」と明示した。 | applied | `discussions/20260627t132404z-interview-default-guidance-dynamic-fields-cutover.md`; `requirement.md` AC-001/AC-002; `design.md` S01/S03 | なし |
| D-003 | resolved | test-strategy | orchestrator | Issue Planning の実運用テストで、substantive draft requirement が `reason_code=requirement-scaffold` と表示され、`assurance classify` の `standard` と guidance の `strict` も不一致だった。 | この issue の外へ延期; この issue の planning/validation 要件へ織り込む | 本 issue の AC-009/AC-010 と S05 に取り込み、guidance semantics、authorized profile source consistency、provider/dogfood parity を検証対象にする。 | `assurance classify` は requirement を valid/standard と判定する一方、guidance は scaffold/strict を表示したため、agent-facing guidance の状態表現と profile source を検証する必要がある。 | applied | `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md`; `plan.md` S05/tc-009/tc-010 | なし |
| D-004 | resolved | test-strategy | ChatGPT Pro advisory review / orchestrator | GPT-5.5 Pro review が、`may_execute_approved_plan`、旧 structured step selector 不要テスト、invalid assurance fail-closed、projection refresh negative test の明示を推奨した。 | 既存 plan のまま; すべて採用; source-grounded な不足分だけ採用 | source-grounded な不足分だけ採用し、`tc-011` - `tc-014` と output / preflight contract へ反映した。 | 外部 review には active issue 本体が確認できないという誤認があったため、助言をそのまま権威化せず、ローカル文書と照合できた指摘だけ採用する。 | applied | `discussions/20260627t150729z-research-chatgpt-pro-plan-review-adoption.md`; `requirement.md`; `design.md`; `plan.md` | なし |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | requirement / design / plan | Plan-centric guidance への縮退、report-control-plane の廃止、Step Obligation Pattern の plan authoring 移管を本 issue の主対象として採用した。 | `discussions/20260627t131746z-research-plan-centric-guidance-requirement-preparation.md` | なし |
| EAL-002 | adopted | discussion | requirement / design / plan | dynamic selector を削り、preflight validator と plan lint に責務を分ける構成を採用した。 | `discussions/20260627t132248z-disc-plan-centric-guidance-requirement-scope-synthesis.md` | なし |
| EAL-003 | adopted | user decision | requirement / design / plan | hard cutover と不要 field 削除を互換性方針として採用した。 | `discussions/20260627t132404z-interview-default-guidance-dynamic-fields-cutover.md` | なし |
| EAL-004 | adopted | command / research | design / plan / report | Issue Planning guidance の manual test 結果を採用し、guidance semantics drift と profile source inconsistency を検証対象へ加えた。 | `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md`; `./spec-dock/scripts/spec-dock guidance issue-planning`; `./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json` | 実装時に S05 で再検証 |
| EAL-005 | partially_adopted | external advisory review | requirement / design / plan / report | GPT-5.5 Pro review のうち、ローカル文書と照合できた不足分を採用した。active issue 本体未確認という指摘は Oracle 側の可視性制約として参考止まりにした。 | `discussions/20260627t150729z-research-chatgpt-pro-plan-review-adoption.md`; Oracle session `iss-00244-plan-centric-guidance` | なし |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `guidance issue-execution` を plan-centric preflight validator に単純化する要件・設計・計画が作成済み。 | Issue Planning guidance の manual test 結果を `discussions/` と plan の検証対象へ反映済み。 | low | provisional: fresh spec-reviewer pending |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active epic/issue docs, runtime code, discussions, user hard-cutover decision | Q-001 resolved; Q-002/Q-003 design-routed | adopted | provisional: reviewer pending | no | promote to design, then request final spec-review |
| design | `application/workflow.py`, `context_packets.py`, `context_routing.py`, `runbook.py`, `presentation/workflow.py`, shipped skills, templates, tests | no blocking open question; deletion depth captured as S03 | adopted | provisional: reviewer pending | no | promote to plan, then request final spec-review |
| plan | requirement/design AC and module dependency analysis | no blocking open question | adopted | provisional: reviewer pending | no | ready for spec-review; implementation starts only after passed review |

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
- 実装は未開始。本フェーズでは `iss-00244` の要件定義書、設計書、実装計画書を具体化し、Issue Planning guidance の manual test findings を discussion artifact として記録した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-27 14:05 - 14:45）

#### 対象
- Step: planning authoring
- AC/EC: AC-001..AC-010, EC-001..EC-006
- 計画上の出典（Planned source）:
  - `plan.md` sections: Issue Execution Plan / Step Contract
  - closure ids: tc-001..tc-010

#### 実施内容
- `guidance issue-planning` を実行し、初期状態が requirement capture であることを確認した。
- `requirement.md` を具体化した後、`assurance classify` と `assurance compose` を実行した。
- `design.md` と `plan.md` を具体化し、plan-centric preflight validation への hard cutover 方針を反映した。
- Issue Planning guidance の manual test として、substantive draft requirement が `reason_code=requirement-scaffold` に残る挙動を確認し、discussion artifact に記録した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock guidance issue-planning
# result: state=requirement-capture, reason_code=requirement-scaffold

./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json
# result: ok=true, status=valid, authorized_profile=standard

./spec-dock/scripts/spec-dock assurance classify --stage requirement --format json
# result: ok=true, status=valid, authorized_profile=standard, assurance.json written

./spec-dock/scripts/spec-dock assurance compose --artifact all --format json
# result: ok=true; design.md, plan.md, report.md changed

./spec-dock/scripts/spec-dock assurance verify --format json
# result: ok=true, status=valid, authorized_profile=standard

./spec-dock/scripts/spec-dock validate
# result: spec-dock: ok (validate) nodes=153

./spec-dock/scripts/spec-dock guidance issue-planning
# result: state=requirement-capture, reason_code=requirement-scaffold, authority=authorized_profile=strict

npx -y @steipete/oracle --engine browser --model gpt-5.5-pro --browser-thinking-time extended ...
# result: GPT-5.5 Pro advisory review completed; accepted additions recorded in discussions/20260627t150729z-research-chatgpt-pro-plan-review-adoption.md
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| planning | 代替証跡（authoring） | manual-required | guidance / assurance command behavior observed | command / docs inspection | pass-with-finding | finding recorded in `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md` |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| planning | Draft frontmatter が残る substantive requirement を guidance が `requirement-scaffold` と表現し、`assurance verify` の `standard` と guidance の `strict` が不一致になる。 | manual test | recorded and added to plan verification | tc-009 / tc-010 | yes | `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| planning | tc-001..tc-010 | requirement/design/plan authoring complete before implementation | documents updated; assurance compose run | provisional | final spec-review pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-009 | S05 | yes | manual-required | Issue Planning guidance manual test | `./spec-dock/scripts/spec-dock guidance issue-planning`; `./spec-dock/scripts/spec-dock assurance classify --stage requirement --dry-run --format json` | pass-with-finding | finding incorporated into plan |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001..tc-010 | planning | requirement/design/plan inspection | provisional | implementation and final gates pending |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | tc-009 / tc-010 | guidance-semantics-manual-test | tc-009 / tc-010 | Issue Planning guidance manual test exposed provider/dogfood semantics drift. | yes | yes |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/dbca/spec-dock` | iss-00244 | current session | spec-reviewer if needed | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue planning complete / session end / scope change / host policy conflict / user revocation | none | proceed to final spec-review |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planning | approved-local-execution | docs-only authoring with current orchestrator context | N/A | requirement/design/plan/report/discussions | active issue docs | docs update only | implementation code changes | guidance and assurance commands | reviewer failure / unresolved blocking gap | updated artifacts / verification / risks | pass-with-finding |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| planning | N/A | no delegated draft used in this phase | requirement/design/plan/report/discussions | guidance and assurance commands | provisional | final spec-review pending | accepted for review |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| planning | direct issue-planning authoring requested by user | user request; risk accepted: no unresolved blocking risk | active issue docs and discussions | docs authoring | git diff can revert docs-only edits | guidance / assurance commands -> pass-with-finding | spec-reviewer pending | proceed to review |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | final spec authoring review | spec-reviewer | fresh pending | provisional | no | proceed to request review | requirement/design/plan/report authored |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| planning | not committed | docs-only planning artifacts | pending | pending | implementation not started | N/A | N/A | N/A |

#### 変更したファイル
- `requirement.md` - plan-centric preflight validator の要件を具体化。
- `design.md` - dynamic context routing removal と plan lint / skill / template 更新方針を具体化。
- `plan.md` - Step-level Obligation Pattern を含む実装計画を具体化。
- `report.md` - 計画作成中の採用判断と manual test findings を記録。
- `discussions/20260627t143104z-research-issue-planning-guidance-manual-test-findings.md` - Issue Planning guidance manual test findings を記録。

#### コミット
- 未実施。

#### メモ
- 実装開始前に fresh spec-reviewer の pass が必要。

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | doc-writer | `plan.md` S90 に docs impact resolution を明記 | pending |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added | `plan.md` tc-001..tc-010; S05 / S99 | pending |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | implementation not started | 0 | pending |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report alignment | pending fresh review | 0 | pending |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| report.md planning ledger | requirement/design/plan/report/discussions | final response | pending |

## 遭遇した問題と解決 (任意)
- 問題: Issue Planning guidance が、substantive draft requirement を `reason_code=requirement-scaffold` と表示した。
  - 解決: `assurance classify` と provider/runtime inspection で原因を切り分け、manual test finding として discussion artifact に記録し、S05/tc-009/tc-010 に検証対象として組み込んだ。

## 学んだこと (任意)
- guidance のユーザー向け reason code は safety gate としては機能していても、agent が次の作業を判断する signal としては draft/scaffold/review-needed を分ける必要がある。

## 今後の推奨事項 (任意)
- 実装時は provider source と dogfooding runtime の両方で guidance output を比較し、`assurance classify` と矛盾しない状態表現に揃える。

## 省略/例外メモ (必須)
- 実装・コードレビュー・QA は未実施。本フェーズは issue planning authoring と manual test findings の記録に限定する。

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
