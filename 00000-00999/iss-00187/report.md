---
種別: 実装報告書（Issue）
ID: "iss-00187"
タイトル: "Use Actions Endpoint For PR Observation CI State"
関連GitHub: ["#187"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-16"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00187 Use Actions Endpoint For PR Observation CI State — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | orchestrator + user interview | Actions-only green evidence を `passed` と扱えるかが requirement / design / plan を左右する | Option A: Actions-only green を pass 許可し limitation を残す; Option B: full rollup なしでは unknown | Option A を採用する | #187 の目的は Fine-grained PAT で付与可能な Actions read surface へ通常観測を寄せること。未証明 surface は limitation として残せば false-pass risk を可視化できる | applied | `discussions/20260615t154753z-01-research-actions-ci-observation-scope.md`; `discussions/20260615t154753z-02-interview-actions-only-pass-contract.md`; `requirement.md` | design / plan で collector contract と test obligation に展開する |
| D-002 | resolved | deviation | orchestrator | `system-architect` / `implementation-planner` delegated authoring は diff-guard 付き discussion draft を標準とするが、既存の requirement evidence discussions が未コミットで target `discussions/` baseline を dirty にしている | Option A: 現在の dirty discussions を前提に手動 authoring fallback; Option B: 途中 commit/stage して delegated draft precondition を作る | Option A を採用する | ユーザーは仕様書作成を要求しており、途中 commit は要求されていない。dirty baseline 上で delegated draft を昇格証跡にすると diff-guard 契約が弱くなるため、canonical design/plan は orchestrator が直接作成し、fresh spec-reviewer gate で品質保証する | applied | `git status --short`; `design.md`; `plan.md`; Delegated Draft Evidence | 実装開始前に design / plan spec-reviewer gate を通す |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md` | Current implementation, existing tests, and GitHub permission surfaces define the concrete requirement boundary for #187 | `discussions/20260615t154753z-01-research-actions-ci-observation-scope.md` | Continue to design authoring |
| EAL-002 | adopted | discussion / user answer | `requirement.md` | User explicitly allowed Actions-only green evidence to produce `ci.status="passed"` when limitation semantics remain visible | `discussions/20260615t154753z-02-interview-actions-only-pass-contract.md` | Continue to design authoring |
| EAL-003 | adopted | reviewer | `requirement.md` | Requirement reviewer identified non-blocking ambiguity between workflow-run stale conclusion and stale head freshness failure; requirement now separates CI failure from rerun-needed freshness failure | Initial `spec-reviewer` pass with P2 cleanup; `requirement.md` | Fresh requirement re-review completed |
| EAL-004 | adopted | reviewer | `requirement.md` | Fresh requirement re-review found no findings and confirmed requirement is ready for design promotion | Fresh `spec-reviewer` pass result; `requirement.md`; `report.md` | Promote to design authoring |
| EAL-005 | adopted | orchestrator analysis | `design.md` | Existing provider scripts and tests define the lowest-risk implementation boundary: keep public collector CLI, move CI primary source to Actions, retain supplemental signals as compatibility evidence | `rg` / source inspection of PR observation scripts and tests; `design.md` | Run design spec review |
| EAL-006 | adopted | orchestrator analysis | `plan.md` | Implementation order follows dependency graph: collector contract first, taxonomy second, wrappers third, docs/mirror fourth, final gates last | `design.md`; `plan.md` closure index | Run plan spec review |
| EAL-007 | adopted | reviewer | `design.md`, `plan.md` | Design reviewer passed the gate with P2 improvements: wrapper permission handling must be mandatory, and Actions-derived `ci.failures[]` shape must be explicit | `spec-reviewer` design review result; `design.md`; `plan.md` | Run fresh design re-review |
| EAL-008 | adopted | reviewer | `design.md` | Fresh design re-review found no findings and confirmed P2 cleanup was reflected into design and plan obligations | Fresh `spec-reviewer` design re-review result; `design.md`; `plan.md`; `report.md` | Promote to plan review |
| EAL-009 | adopted | reviewer | `plan.md`, `report.md` | Plan reviewer failed the first plan gate on missing delegation-contract fields, S90 delegation contract, concrete report evidence destinations, and stale design gate state; plan/report were updated accordingly | `spec-reviewer` plan review result; `plan.md`; `report.md` | Run fresh plan re-review |
| EAL-010 | adopted | reviewer | `plan.md` | Fresh plan re-review failed on incomplete concrete test cards and S90 role mismatch; plan now adds full card fields for S01/S02/S03/S90 and assigns doc-writer to skill-text wording with dev-coder/utility for mechanical sync | Fresh `spec-reviewer` plan re-review result; `plan.md` | Run second fresh plan re-review |
| EAL-011 | adopted | reviewer | `plan.md`, `report.md` | Second fresh plan re-review found no findings and confirmed implementation handoff readiness | Fresh `spec-reviewer` plan re-review result; `plan.md`; `report.md` | Ready for implementation handoff |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | #187 と `requirement.md` は Fine-grained PAT で付与可能な Actions read surface を通常 CI 観測に使うことを主要目的にしている | False-pass safety は limitation と unknown/pending/failed classification で保持する | low | requirement/design/plan spec-reviewer pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | GitHub issue #187; active issue scaffold; parent epic requirement/design; current PR observation scripts; fake `gh` tests; GitHub REST docs; research discussion | Answered: Actions-only green pass is allowed with explicit limitation; reviewer P2 clarified stale conclusion vs stale head freshness failure | adopted into `requirement.md` | initial pass with P2 cleanup; fresh re-review pass with no findings | no | promoted to design |
| design | `requirement.md`; provider PR observation scripts; wrapper classification; fake `gh` tests; parent dogfooding/provider rules | None blocking; delegated architecture draft not used due dirty discussion baseline and no mid-authoring commit; P2 reviewer findings applied | adopted into `design.md` | fresh re-review pass with no findings | no | promoted to plan review |
| plan | `design.md`; `docs/authoring/issue-plan.md`; closure requirements; affected test harness | None blocking; delegated implementation-planner draft not used due same diff-guard precondition; updated to reflect mandatory wrapper change, failure detail closure, required delegation fields, S90 contract, report evidence destinations, complete concrete test cards, and skill-text doc-writer ownership | adopted into `plan.md` | second fresh re-review pass with no findings | no | ready for implementation handoff |

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
| system-architect | iss-00187 | 該当なし | `requirement.md`; research/interview discussions; PR observation scripts/tests | `design.md` | not used | [] | not_run; target `discussions/` baseline dirty from uncommitted requirement evidence | 手動 authoring fallback | 該当なし | diff-guard precondition unavailable without mid-authoring commit/stage | pending spec-reviewer | delegated draft 昇格なし。canonical design は fresh spec-reviewer gate で昇格判断 |
| implementation-planner | iss-00187 | 該当なし | `requirement.md`; `design.md`; authoring docs | `plan.md` | not used | [] | not_run; same target `discussions/` baseline dirty | 手動 authoring fallback | 該当なし | diff-guard precondition unavailable without mid-authoring commit/stage | pending spec-reviewer | delegated draft 昇格なし。canonical plan は fresh spec-reviewer gate で昇格判断 |

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

### セッションログ（2026-06-16 HH:MM - HH:MM）

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
| user instruction invoking `$spec-dock-issue-planning` workflow | `/Users/iwasawayuuta/.codex/worktrees/1fe5/spec-dock` | iss-00187 | current session | spec-reviewer; system-architect; implementation-planner; future dev-coder/code-reviewer/qa-reviewer as named in `plan.md` | same repo/worktree, active issue, issue-local docs and bounded implementation steps; no destructive action, publishing, credential expansion, or scope expansion without separate instruction | issue complete / session end / scope change / host policy conflict / user revocation | system-architect and implementation-planner discussion-draft authoring not used because target discussions baseline is dirty; reviewer roles available | proceed with canonical docs plus fresh spec-reviewer gates |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| authoring-requirement | delegated-review | workflow gate | spec-reviewer | requirement review | `requirement.md`; `report.md`; discussions | read-only review | file edits | reviewer findings and `review_status` | P0/P1 blocker | findings, status, rationale | fresh pass |
| authoring-design | approved-local-authoring | dirty delegated-draft baseline | N/A for draft; spec-reviewer for gate | canonical design authoring and review | `design.md`; `report.md` | issue-local docs | source code/test edits | fresh spec-reviewer | design blocker | findings, status, rationale | pass; promoted to plan review |
| authoring-plan | approved-local-authoring | dirty delegated-draft baseline | N/A for draft; spec-reviewer for gate | canonical plan authoring and review | `plan.md`; `report.md` | issue-local docs | source code/test edits | fresh spec-reviewer | plan blocker | findings, status, rationale | initial fail; cleanup applied; re-review pending |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| requirement-review-1 | spec-reviewer | Initial requirement review returned pass with P2 cleanup findings for stale taxonomy and research metadata alignment | none | read-only spec review | pass | P2 cleanup applied before promotion | accepted |
| requirement-review-2 | spec-reviewer | Fresh requirement re-review returned no findings and confirmed design promotion readiness | none | read-only spec review | pass | none | accepted |
| design-review-1 | spec-reviewer | Initial design review returned pass with P2 cleanup findings for wrapper permission handling and Actions failure detail shape | none | read-only spec review | pass | P2 cleanup applied before re-review | accepted |
| design-review-2 | spec-reviewer | Fresh design re-review returned no findings and confirmed design promotion readiness | none | read-only spec review | pass | none | accepted |
| plan-review-1 | spec-reviewer | Initial plan review failed on missing delegation contract fields, missing S90 delegation contract, vague report evidence destinations, and stale design gate state | none | read-only spec review | fail | P1/P2 cleanup applied; re-review pending | accepted for remediation |
| plan-review-2 | spec-reviewer | Fresh plan re-review failed on incomplete concrete test cards and S90 skill-text role ownership | none | read-only spec review | fail | P1/P2 cleanup applied; second re-review pending | accepted for remediation |
| plan-review-3 | spec-reviewer | Second fresh plan re-review returned no findings and confirmed implementation handoff readiness | none | read-only spec review | pass | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| requirement | spec authoring gate | spec-reviewer | fresh | passed | N/A | proceed to design | Fresh re-review had no findings |
| design | spec authoring gate | spec-reviewer | fresh | passed | N/A | proceed to plan review | Fresh re-review had no findings |
| plan | spec authoring gate | spec-reviewer | fresh | passed | N/A | ready for implementation handoff | Second fresh re-review had no findings |

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

### セッションログ（2026-06-16 HH:MM - HH:MM）

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
