---
種別: 実装報告書（Issue）
ID: "iss-00176"
タイトル: "GitHub PR observation should trigger and wait for Codex review completion"
関連GitHub: ["#176"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-08"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00176 GitHub PR observation should trigger and wait for Codex review completion — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | user / orchestrator | `iss-00176` を分析準備 issue として閉じるか、この issue で実装まで進めるかが未確定だった | A: 既存 `iss-00176` を実装 issue として育てる; B: 新規 issue を作成する | A を採用。`iss-00176` 内で要件・設計・計画・実装まで進める | ユーザーが明示的に「このissueで実装まで進めます」と回答したため。既存 GitHub issue `#176` と discussion evidence も今回 scope と一致する | applied | `discussions/20260609t030339z-interview-issue-scope-for-deterministic-codex-review-trigger.md` | `requirement.md` に反映済み。design / plan でも同一 scope を前提にする |
| D-002 | resolved | operation | user / orchestrator | 初回 `wait_pr_observation.sh` が timeout / limit に到達した後、継続観測のために再実行すると default trigger 投稿により不要な2回目の Codex review が起動し得る | A: 常に新規 `@codex review` を投稿する; B: 既存 trigger を自動 reuse する; C: default は `post-once` のまま、明示 `resume` mode で既存 trigger boundary を継続観測する | C を採用。trigger mode 未指定時は default `post-once`、timeout / limit 後は明示 `resume` mode を使う | 初回観測の決定性を維持しつつ、長時間 CI / review の継続観測で二重 trigger を避けられる。自動 reuse は古い trigger 混入リスクがあるため採用しない | applied | ユーザー指摘と合意; `requirement.md` AC-008 / EC-007 / EX-004 | design / plan でも mode contract と resume metadata を前提にする |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | discussion / research | `requirement.md` | ChatGPT / Deep Consultant 分析は、通常 path の決定的 `@codex review` 投稿、固定 write boundary、既存 trigger 自動 reuse 禁止、submitted PR review primary、stdout / stderr 境界を一貫して支持しており、現行実装の gaps と整合する | `discussions/20260608t092803z-research-chatgpt55-pro-codex-review-trigger-completion-analysis.md`; `discussions/20260608t111111z-research-deterministic-codex-review-trigger-design.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh` | requirement spec-reviewer gate |
| EAL-002 | adopted | interview | `requirement.md` | ユーザー回答により、`iss-00176` は計画準備だけでなくこの issue 内で実装まで進める scope と確定した | `discussions/20260609t030339z-interview-issue-scope-for-deterministic-codex-review-trigger.md` | requirement spec-reviewer gate |
| EAL-003 | adopted | discussion | `requirement.md` | timeout / limit 後の継続観測では、default `post-once` を再実行すると二重 trigger になるため、明示 `resume` mode と resume metadata を要件化する必要がある | ユーザー指摘; `requirement.md` AC-008 / EC-007 / EX-004 | requirement spec-reviewer gate |
| EAL-004 | adopted | reviewer | `requirement.md` | spec-reviewer が、resume 時の review thread collection の取得・選択・件数・ID が検証可能でないと thread collection 漏れを acceptance で見逃すリスクを指摘したため、AC-008 / EC-007 に review thread ids / counts と boundary 以前の除外証跡を追加した | `/private/tmp/iss-00176-requirement-resume-spec-review.json`; `requirement.md` AC-008 / EC-007 | rerun requirement spec-reviewer gate |
| EAL-005 | adopted | reviewer | `requirement.md` | spec-reviewer が、thread だけでなく PR reviews / review comments についても collection 全体の counts / IDs / boundary 除外証跡がないと抜け漏れを acceptance で検出できないと指摘したため、AC-008 / EC-007 に reviews / review comments / review threads の collection summary を同一粒度で要求した | `/private/tmp/iss-00176-requirement-resume-spec-review-r2.json`; `requirement.md` AC-008 / EC-007 | rerun requirement spec-reviewer gate |
| EAL-006 | adopted | reviewer | `requirement.md` | spec-reviewer が、AC-008 は同一粒度になった一方で EC-007 側の selected IDs / boundary-before exclusion reasons / unresolved thread IDs が不足していると指摘したため、EC-007 に AC-008 と同じ collection summary 粒度を明記した | `/private/tmp/iss-00176-requirement-resume-spec-review-r3.json`; `requirement.md` EC-007 | rerun requirement spec-reviewer gate |
| EAL-007 | adopted | interview | `requirement.md` | ユーザー回答により、エージェントが危険な追加 `gh api` 利用やノイズの多い全件コメント取得をせずに review 本文を読めるよう、selected review body full text を final stdout JSON に含める方針を採用した | `discussions/20260609t130000z-interview-review-body-output-contract.md`; `requirement.md` AC-003 / AC-004 / EC-006 | rerun requirement spec-reviewer gate |
| EAL-008 | adopted | delegated draft / system-architect | `design.md` | system-architect draft は、fixed write helper、default `post-once`、explicit `resume`、read-only collector 境界、stdout JSON authority、selected body full text、collection summary、test strategy を requirement と既存実装に沿って具体化していたため、正式設計へ採用した | `discussions/20260609t133000z-disc-design-draft-system-architect-pr-observation-codex-review.md`; `design.md` | design spec-reviewer gate |
| EAL-009 | adopted | reviewer | `design.md` | spec-reviewer が、selected review body full text と既存 `body-mode` の関係が未定義だと AC-003 / AC-004 / EC-006 を実装で取りこぼすリスクがあると指摘したため、selected body は `body-mode` 非依存で final stdout JSON に全文収録する設計へ明確化した | `/private/tmp/iss-00176-design-spec-review.json`; `design.md` `body-mode` 適用範囲 / テスト戦略 | rerun design spec-reviewer gate |
| EAL-010 | adopted | delegated draft / implementation-planner | `plan.md` | implementation-planner draft は、fixed trigger write helper、wait mode orchestration、read-only collector contract、final wait JSON integration、skill docs、package/install regression、docs impact、final quality gate を requirement/design と一致する実装順序に具体化していたため、正式計画へ採用した。主 orchestrator は review scope を明確にするため、draft の docs/package step を S05a（skill docs）と S05b（package/install regression）に分割して反映した | `discussions/20260609t143000z-disc-implementation-plan-draft-pr-observation-codex-review.md`; `plan.md` | plan spec-reviewer gate |
| EAL-011 | adopted | reviewer | `report.md` | plan spec-reviewer の P2 finding は、計画自体を fail させるものではないが、delegated implementation-planner evidence の provenance auditability を補強する必要を指摘したため、EAL-010 の supplemental provenance と discussion draft frontmatter 欠落の扱いを report 側に明記した | `/private/tmp/iss-00176-plan-spec-review.json`; `report.md` EAL-010 supplemental provenance; Delegated Draft Evidence | rerun plan spec-reviewer gate after report provenance update |
| EAL-012 | adopted | reviewer | `plan.md` | plan spec-reviewer rerun の P2 finding は、S90 / S99 の delegation contract に `必須出力` が明示されていないため handoff が少し曖昧になると指摘した。計画は pass だったが、実装引き渡しの曖昧さを減らすため S90 / S99 に必須出力を追加した | `/private/tmp/iss-00176-plan-spec-review-r2.json`; `plan.md` S90 / S99 delegation contract | rerun plan spec-reviewer gate after S90/S99 output update |
| EAL-013 | adopted | reviewer | `plan.md` / `report.md` | final plan spec-reviewer rerun は findings 0 で、S90 / S99 の `必須出力` 補強、delegated draft provenance 補強、計画の executable schema 充足を確認したため、plan authoring gate の final pass として採用した | `/private/tmp/iss-00176-plan-spec-review-r3.json`; `plan.md`; `report.md` | plan phase ready for execution handoff |

### EAL-010 supplemental provenance

| 項目 | 値 |
|---|---|
| source_role | `implementation-planner` |
| claim | `plan.md` can execute iss-00176 by implementing fixed trigger helper, wait trigger mode, read-only review collector contract, final wait JSON integration, skill docs, package/install regression, S90 docs impact, and S99 final quality gates in that dependency order |
| target_artifact | `plan.md` |
| target_section | `この計画で満たす要件ID`; `依存関係から導く実装順序`; `ステップ一覧`; `仕様固定クロージャ索引`; `実装ステップ S01-S05b`; `S90`; `S99`; `最終完了条件` |
| evidence_strength | strong for executable planning because it is grounded in reviewed `requirement.md`, reviewed `design.md`, current scripts/tests, authoring docs, and was integrated by the orchestrator into canonical `plan.md`; not implementation evidence |
| evidence_path | `discussions/20260609t143000z-disc-implementation-plan-draft-pr-observation-codex-review.md`; `plan.md` |
| adopter | main orchestrator |
| reviewer | plan `spec-reviewer`; initial pass with P2 provenance findings recorded at `/private/tmp/iss-00176-plan-spec-review.json`; final pass findings 0 / confidence 0.93 recorded at `/private/tmp/iss-00176-plan-spec-review-r3.json` |
| blocking | no; final plan reviewer pass confirms provenance cleanup and executable plan readiness |
| adoption_note | The discussion draft frontmatter remains evidence-only and is not rewritten as if produced with richer metadata. Missing frontmatter fields are covered by this report-side supplemental provenance and the Delegated Draft Evidence row, preserving raw delegated evidence while making orchestrator adoption auditable. |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | ... | ... | なし / 低 / 中 / 高（none / low / medium / high） | 合格 / 不合格 / blocked（pass / fail / blocked） |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `SKILL.md`; `wait_pr_observation.sh`; `fetch_pr_observation_snapshot.sh`; `fetch_pr_review_snapshot.sh`; `discussions/20260608t092803z-research-chatgpt55-pro-codex-review-trigger-completion-analysis.md`; `discussions/20260608t111111z-research-deterministic-codex-review-trigger-design.md`; `discussions/20260609t030339z-interview-issue-scope-for-deterministic-codex-review-trigger.md`; `discussions/20260609t130000z-interview-review-body-output-contract.md`; parent epic requirement/design | `iss-00176` をこの issue 内で実装まで進めること、default `post-once` と明示 `resume` mode、selected review body full text の stdout 収録を採用することを確定 | adopted | pass: findings 0 / confidence 0.93 (`/private/tmp/iss-00176-requirement-review-body-spec-review.json`) | no | promote to design authoring |
| design | `requirement.md`; `report.md`; `discussions/20260609t133000z-disc-design-draft-system-architect-pr-observation-codex-review.md`; `SKILL.md`; `wait_pr_observation.sh`; `fetch_pr_observation_snapshot.sh`; `fetch_pr_review_snapshot.sh`; `tests/unit/infra/test_init_update.py`; parent epic design | 未確定事項なし。Codex author login の揺れや GitHub response fields は `confidence` / `limitations` で表現し、実装時検証に回す | system-architect draft と design reviewer finding を採用し、fixed write helper + wait orchestration + read-only collectors + stdout JSON contract + selected body `body-mode` 非依存 + fake `gh` test strategy として `design.md` に統合 | pass: findings 0 / confidence 0.92 (`/private/tmp/iss-00176-design-spec-review-r2.json`); first review failed with one major finding and was fixed (`/private/tmp/iss-00176-design-spec-review.json`) | no | submit design for user confirmation before plan authoring |
| plan | `requirement.md`; `design.md`; `report.md`; `discussions/20260609t143000z-disc-implementation-plan-draft-pr-observation-codex-review.md`; `workflow_spec_authoring.md`; `phase_plan_issue.md`; `authoring/issue-plan.md`; current scripts/tests | 未確定事項なし。implementation-planner draft を採用し、S05 を docs contract と package/install regression に分割して step-local review scope を明確化した | adopted | pass: findings 0 / confidence 0.93 (`/private/tmp/iss-00176-plan-spec-review-r3.json`); earlier P2 provenance and S90/S99 output findings were fixed and re-reviewed (`/private/tmp/iss-00176-plan-spec-review.json`, `/private/tmp/iss-00176-plan-spec-review-r2.json`) | no | plan phase ready for execution handoff |

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
| system-architect | iss-00176 | `discussions/20260609t133000z-disc-design-draft-system-architect-pr-observation-codex-review.md` | `spec-dock/active/issue/requirement.md`; `spec-dock/active/issue/report.md`; `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`; `wait_pr_observation.sh`; `fetch_pr_observation_snapshot.sh`; `fetch_pr_review_snapshot.sh`; `spec-dock/active/epic/design.md`; related discussions | `design.md`; later `plan.md` | adopted by orchestrator in `EAL-008` | `design.md` | pass: only the requested flat discussion draft was newly produced by the delegated role; baseline worktree already contained prior requirement/report/discussion changes | fixed write helper、default/resume mode contract、collector boundary、JSON contract、test strategy を正式設計へ統合 | implementation-planner 向け detail は plan authoring で再検討するため、design には実装 step 粒度で採用しない | なし（none） | pass: findings 0 / confidence 0.92 (`/private/tmp/iss-00176-design-spec-review-r2.json`) | design phase ready for user confirmation |
| implementation-planner | iss-00176 | `discussions/20260609t143000z-disc-implementation-plan-draft-pr-observation-codex-review.md` | `spec-dock/active/issue/requirement.md`; `spec-dock/active/issue/design.md`; `spec-dock/active/issue/report.md`; `spec-dock/docs/workflow_spec_authoring.md`; `spec-dock/docs/phase_plan_issue.md`; `spec-dock/docs/authoring/issue-plan.md`; target scripts/tests | `plan.md` | adopted by orchestrator in `EAL-010` | `plan.md` | pass: only the requested flat discussion draft was newly produced by the delegated role; baseline worktree already contained prior requirement/design/report/discussion changes | implementation sequence、closure index、step-local tests、delegation contracts、S90/S99 gates を正式計画へ統合。draft frontmatter にない diff_guard_result / fallback decision / report evidence destination / adoption ledger note は、この row と `EAL-010 supplemental provenance` で report-side adoption evidence として補完する | draft の combined docs/package step は reviewer scope を分離するため S05a / S05b に分割して採用した。raw delegated draft は evidence-only として保持し、frontmatter を accepted authority 風に後編集しない | なし（none） | pass: findings 0 / confidence 0.93 (`/private/tmp/iss-00176-plan-spec-review-r3.json`) | plan phase ready for execution handoff |

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
- [実装した内容の概要を2-3文で記載]

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-09 S01 fixed trigger write helper）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-002, AC-006, AC-007, EC-001, EC-005
- 計画上の出典（Planned source）:
  - `plan.md` `実装ステップ S01 — fixed trigger write helper`
  - closure ids: cl-001, cl-002, cl-003

#### 実施内容
- `trigger_codex_review.sh` を追加し、`--repo` / `--pr` / `--head-sha` だけを受け付ける固定 write helper とした。
- PR head が一致する場合だけ `POST repos/{owner}/{repo}/issues/{pr}/comments` に固定本文 `@codex review` を投稿し、comment metadata JSON を返す。
- pre-trigger stale、post-trigger stale、POST failure、before snapshot untrusted、multiple exact candidates、exact-one recovery を fake `gh` で固定した。
- code-reviewer r1 で `gh api --field` の `@` file magic と recovery trust gap を検出し、`--raw-field` と trusted before/after snapshot 条件へ修正した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py -k issue_176_s01
# 8 passed, 297 deselected

git diff --check -- src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh tests/unit/infra/test_init_update.py
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ / 代替証跡（Red / alternative） | red-required | helper script 不在から S01 fake `gh` tests を追加する計画。dev-coder 実装では red 実行ログは未分離だが、code-reviewer r1 が実 gh `--field` 問題と recovery trust gap を検出し、追加 failing scenario を確定した。 | reviewer finding / review-driven characterization | pass | r1 findings を red 相当の追加 characterization として扱った。 |
| S01 | 緑フェーズ（Green） | focused fake `gh` pytest | `issue_176_s01` 8 tests passed | `uv run pytest tests/unit/infra/test_init_update.py -k issue_176_s01` | pass | fixed POST, invalid input no-gh, pre/post stale, fail-closed, untrusted before snapshot, multiple candidates, exact-one recovery. |
| S01 | リファクタリング（Refactor） | no non-fixed write surface | helper は `--raw-field body=@codex review` の固定 POST と read-only `gh pr view` / issue comments snapshot に限定。 | `git diff --check` / code-reviewer r2 | pass | 汎用 GitHub write helper 化はしていない。 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | `gh api --field body=@codex review` は `@` を file magic として扱うリスク | code-reviewer r1 | `--raw-field` に変更し fake `gh` expectation も更新 | cl-001 | no | `test_issue_176_s01_trigger_helper_posts_fixed_review_comment_once` |
| S01 | before snapshot が信頼不能でも exact-one recovery してしまうリスク | code-reviewer r1 | before/after snapshot trust check を追加し、before untrusted では recovery unavailable にした | cl-003 | no | `test_issue_176_s01_trigger_helper_does_not_recover_without_trusted_before_snapshot` |
| S01 | multiple exact candidates と post-trigger head drift の検出不足 | code-reviewer r1 | negative tests を追加 | cl-003 / cl-002 | no | `test_issue_176_s01_trigger_helper_rejects_multiple_new_exact_comments`, `test_issue_176_s01_trigger_helper_fails_when_head_changes_after_post` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | cl-001, cl-002, cl-003 | S01 tests pass; helper has executable permission; no non-fixed write surface is exposed | focused pytest 8 passed; `ls -l` で executable permission 確認; code-reviewer r2 passed | pass | install/package inclusion は S05b 範囲。 |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-001 / tc-s01-001 | S01 | yes | red-required | helper 不在 / r1 finding | `uv run pytest tests/unit/infra/test_init_update.py -k issue_176_s01` | pass | one fixed POST with `--raw-field body=@codex review`. |
| cl-002 / tc-s01-002 | S01 | yes | red-required | helper 不在 | same | pass | pre-trigger stale no POST; post-trigger stale non-success. |
| cl-003 / tc-s01-003 | S01 | yes | red-required | helper 不在 / r1 finding | same | pass | POST failure no blind retry; zero/multiple/untrusted fail closed. |
| cl-003 / tc-s01-004 | S01 | yes | red-required | helper 不在 | same | pass | before/after trusted exact-one recovery only. |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-001 | S01 | fake `gh` call log asserts one POST to `repos/owner/repo/issues/13/comments` with fixed body via `--raw-field` | pass | caller-provided body/endpoint/raw args are rejected before `gh`. |
| cl-002 | S01 | pre-trigger stale no POST; post-trigger stale non-success | pass | trigger metadata is retained on post-trigger stale. |
| cl-003 | S01 | POST failure no blind retry; exact-one recovery only; untrusted/multiple fail closed | pass | recovery depends on trusted before/after snapshots. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | cl-003 | before snapshot untrusted / multiple exact comments | cl-003 | code-reviewer r1 により fail-closed の技術的穴を検出 | no | yes, r2 passed |
| added | cl-002 | post-trigger head drift | cl-002 | S01 helper の post-head check を固定するため | no | yes, r2 passed |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/3b01/spec-dock` | iss-00176 | current session | dev-coder, code-reviewer | same repo, active issue, named role; S01 allowed files only | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated, then approved-local-execution for review fixes | fixed write boundary and tests | dev-coder / parent local fix after capacity failure | S01 helper and tests | `requirement.md`, `design.md`, `plan.md` | `trigger_codex_review.sh`, S01 tests | wait orchestration, collectors, skill docs, GitHub state | focused pytest and diff check | non-fixed write surface required | worker JSON / reviewer JSON / verification | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | fixed trigger write helper と 5 tests を追加 | `trigger_codex_review.sh`, `tests/unit/infra/test_init_update.py` | `uv run pytest tests/unit/infra/test_init_update.py -k issue_176_s01` -> 5 passed; `git diff --check` -> pass | r1 failed | live GitHub behavior not exercised; S05b package inclusion outside S01 | accepted with required fixes |
| S01 | parent local fix | reviewer findings に基づき `--raw-field`、trusted snapshot recovery、追加 negative tests を実装 | same | `uv run pytest tests/unit/infra/test_init_update.py -k issue_176_s01` -> 8 passed; `git diff --check` -> pass | r2 passed | live GitHub pagination/API shape outside fake fixture | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | dev-coder fix delegation failed because selected model was at capacity | workflow-scoped local fix within same S01 boundary | `trigger_codex_review.sh`, `tests/unit/infra/test_init_update.py` | code-reviewer findings only | inspect diff and restore S01 files if reviewer failed | focused pytest 8 passed; diff check pass | code-reviewer r2 passed | unavailable handled by local bounded fix and fresh reviewer gate |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer r1 | code-reviewer | fresh | failed | no | blocked until fixes | `/private/tmp/iss-00176-s01-code-review.json`; high findings on `--field` and recovery trust. |
| S01 | step reviewer r2 | code-reviewer | fresh | passed | no | proceed | `/private/tmp/iss-00176-s01-code-review-r2.json`; findings 0, confidence high. |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | S01 target files + report S01 ledger | current S01 commit in git history | `git status --short` -> clean for S01 scope after amend | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh` - fixed `@codex review` trigger write helper.
- `tests/unit/infra/test_init_update.py` - S01 fake `gh` tests.
- `spec-dock/.../iss-00176.../report.md` - S01 execution evidence.

#### コミット
- current S01 commit in git history: `feat(github-pr-observation): Codexレビュー起動ヘルパーを追加`

### セッションログ（2026-06-08 HH:MM - HH:MM）

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
| user instruction / explicit approval / none | ... | iss-00176 | current session / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none / denied / unavailable / host conflict | proceed / ask user / block gate / record waiver request |

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

### セッションログ（2026-06-08 HH:MM - HH:MM）

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
