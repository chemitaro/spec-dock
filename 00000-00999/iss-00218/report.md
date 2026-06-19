---
種別: 実装報告書（Issue）
ID: "iss-00218"
タイトル: "Codex Review Fallback Signal Semantics"
関連GitHub: ["#218"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00218 Codex Review Fallback Signal Semantics — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | orchestrator / user interview | strict no-findings issue comment を merge-prepared evidence に昇格するか | Option A: strict condition で昇格; Option B: manual/non-retryable; Option C: 現状維持 | Option A を採用し、`codex_no_findings_issue_comment` を issue-local additive signal とする | ユーザー回答が Option A。generic fallback の安全契約を維持しつつ PR #216 型 false block を解消できる | promoted_to_design | `discussions/20260619t152719z-interview-no-findings-issue-comment-promotion-boundary.md` | `requirement.md`, `design.md`, `plan.md` に反映済み |
| D-002 | resolved | implementation | spec-reviewer | design review で collector と snapshot / wait の authority 境界が曖昧 | collector が merge-prepared まで返す; collector は review completion のみ返す | collector は `review_completion_observed` まで、top-level `merge_prepared` は snapshot / wait のみ返す | collector は CI / PR metadata を持たないため、merge-prepared authority を持たせない | promoted_to_design | design reviewer fail/pass sequence | `design.md` に反映済み |
| D-003 | resolved | operation | dev-coder / orchestrator | `requirement.md`, `design.md`, `plan.md` frontmatter が reviewer pass 後も `draft` のままだった | そのまま実装を続ける; planning へ戻す; reviewer-pass 証跡に合わせて frontmatter を `approved` に修正する | reviewer-pass と Spec Authoring Gate の execution-ready 証跡に合わせ、3 artifact と `report.md` の状態を `approved` に修正した | execution skill は draft artifact を実装開始ブロッカーにするため、reviewer-pass 証跡と metadata を一致させる必要がある | applied | requirement/design/plan reviewer pass; Spec Authoring Gate; frontmatter diff | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md`, `design.md`, `plan.md` | PR #216 の root cause と existing code contract を source-grounded facts として採用 | `discussions/20260619t131514z-research-pr-observation-fallback-signal-root-cause-analysis.md` | none |
| EAL-002 | adopted | discussion | `requirement.md`, `design.md`, `plan.md` | Option A を best practice proposal として採用し、B/C/D/E は non-blocking rejected/deferred とした | `discussions/20260619t151927z-disc-fallback-signal-improvement-options.md` | none |
| EAL-003 | adopted | interview | `requirement.md`, `design.md`, `plan.md` | ユーザーが Option A を明示採用したため、promotion boundary を canonical docs に反映 | `discussions/20260619t152719z-interview-no-findings-issue-comment-promotion-boundary.md` | none |
| EAL-004 | adopted | reviewer | `requirement.md` | fresh spec-reviewer が requirement を pass したため requirement gate を通過 | spec-reviewer Bohr: `review_status=pass` | none |
| EAL-005 | adopted | reviewer | `design.md` | design reviewer の P1/P2 指摘を修正し、fresh re-review が pass した | spec-reviewer Helmholtz/McClintock/Wegener/Huygens sequence | none |
| EAL-006 | adopted | reviewer | `plan.md` | plan reviewer の P1/P2 指摘を修正し、fresh re-review が pass した | spec-reviewer Tesla/Dalton sequence | none |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `codex_no_findings_issue_comment` を追加し、PR #216 型 false block を解消する要件・設計・計画を作成 | `fallback_issue_comment` non-promotion、retryable/non-retryable action 分離、docs clarity | low | requirement/design/plan reviewer pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | research / discussion / interview / parent epic requirement / provider code | Option A adopted in `discussions/20260619t152719z-interview-no-findings-issue-comment-promotion-boundary.md` | adopted | passed: spec-reviewer Bohr | no | promoted to design |
| design | reviewed requirement / discussions / provider scripts / tests | reviewer found head-sha, collector authority, evidence-field gaps; all fixed | adopted after fixes | failed then passed: Helmholtz fail, McClintock fail, Wegener fail, Huygens pass | no | promoted to plan |
| plan | reviewed requirement / reviewed design / phase_plan_issue / authoring/issue-plan | reviewer found blocker coverage, boundary coverage, report gates, docs-only case gaps; all fixed | adopted after fixes | failed then passed: Tesla fail, Dalton pass | no | execution-ready after final validation |

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
| system-architect | iss-00218 | 該当なし | requirement / discussions / provider code | design.md | not used | [] | not_run | 手動 authoring fallback | 該当なし | scope-local direct-write consent が未確認 | final design reviewer pass | 委任ドラフト昇格なし |
| implementation-planner | iss-00218 | 該当なし | reviewed requirement / reviewed design / plan docs | plan.md | not used | [] | not_run | 手動 authoring fallback | 該当なし | scope-local direct-write consent が未確認 | final plan reviewer pass | 委任ドラフト昇格なし |

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
- S01 では、PR review collector に `codex_no_findings_issue_comment` の review-level completion signal を追加した。
- Generic `fallback_issue_comment` は low-confidence / non-promoting のまま維持し、non-retryable fallback action として `manual_review_required_non_retryable` を返す。
- Step review の指摘により、no-findings issue comment の昇格条件を current PR head と expected head の一致、full-body exact allow-list、actionable unresolved thread 不在に限定した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-20 S01）

#### 対象
- Step: S01 Collector no-findings signal taxonomy
- AC/EC: AC-001, AC-002, AC-004, EC-001, EC-002, EC-003
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S01 — Collector no-findings signal taxonomy`
  - closure ids: `tc-001`, `tc-002`, `tc-003`

#### 実施内容
- `dev-coder` に S01 のみを委任し、許可 path を `pr_review_snapshot.py` と `tests/unit/infra/test_init_update.py` に限定した。
- Collector に review-level signal `codex_no_findings_issue_comment`、必須 evidence `no_findings_completion_candidate`、strict no-findings allow-list、missing expected head / old trigger / stale head context rejection を追加した。
- Generic `fallback_issue_comment` は success に昇格せず、`manual_review_required_non_retryable` を返すようにした。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py -k "issue_218_s01 or issue_182_s01_review_collector_marks_no_major_issues_fallback_candidate or issue_176_s03_review_collector_does_not_mark_fallback_as_primary or issue_187_s100_fallback_issue_comment_is_not_no_completion_evidence"

11 passed, 436 deselected
```

```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_review_collector_excludes_resolved_thread_inline_comments_from_status -vv

1 passed
```

```bash
git diff --check

pass: no output
```

```bash
uv run pytest tests/unit/infra/test_init_update.py -k "review_collector or no_findings or fallback_issue_comment"

interrupted after 27 passed, 397 deselected in 201.17s while running existing issue_170 collector test.
The same issue_170 test passed when rerun directly.
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 赤フェーズ（Red） | red-required for `tc-001`, `tc-002`, `tc-003` | delegated worker reported 6 expected failures after adding S01 expectations before implementation | delegated worker evidence | pass | worker did not stage/commit/report |
| S01 | 緑フェーズ（Green） | S01 collector tests pass | parent rerun of S01-focused selector: 11 passed | `uv run pytest ... -k "issue_218_s01 or issue_182_s01_review_collector_marks_no_major_issues_fallback_candidate or issue_176_s03_review_collector_does_not_mark_fallback_as_primary or issue_187_s100_fallback_issue_comment_is_not_no_completion_evidence"` | pass | validates tc-s01-001 through tc-s01-008 and adjacent fallback behavior |
| S01 | 緑フェーズ（Green） | existing collector regression remains healthy | issue_170 resolved-thread collector test passed directly | `uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_170_pr_review_collector_excludes_resolved_thread_inline_comments_from_status -vv` | pass | broad selector was interrupted while this existing test was active; direct rerun passed |
| S01 | リファクタリング（Refactor） | guardrail satisfied / no broad refactor | no formatting whitespace issues | `git diff --check` | pass | no broad collector refactor |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | broad selector was slow/interrupted while an existing issue_170 test was active | parent verification | reran the active existing test directly and confirmed pass; used narrower S01 selector for S01 closure | tc-001, tc-002, tc-003 | no | direct issue_170 test pass; S01-focused 8-test pass |
| S01 | future Codex wording changes may need allow-list expansion | delegated worker | recorded as non-blocking future risk; current issue keeps strict allow-list | tc-001 | no | worker Ledger Note |
| S01 | no-findings body with additional caveat lines could otherwise false-promote | code-reviewer | delegated follow-up added full-body exact allow-list regression | tc-001 | no | S01-focused pytest 10 passed |
| S01 | expected head alone was insufficient without current PR head confirmation | code-reviewer | delegated follow-up added current PR head mismatch regression | tc-003 | no | S01-focused pytest 10 passed |
| S01 | current/actionable unresolved threads not tied to selected Codex review could otherwise be bypassed | code-reviewer | delegated follow-up gated no-findings promotion on `actionable_unresolved_thread_ids` and added regression | tc-001, tc-003 | no | S01-focused pytest 11 passed |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002, tc-003 | Collector decision が design の signal taxonomy に一致する | S01-focused pytest 11 passed; `git diff --check` pass | pass | second step re-review passed |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 / tc-s01-001 | S01 | yes | red-required | delegated worker reported expected Red failure before implementation | S01-focused pytest selector | pass | observed Codex Review wording promotes at collector review level |
| tc-002 / tc-s01-002 | S01 | yes | red-required | delegated worker reported expected Red failure before implementation | S01-focused pytest selector | pass | generic comment remains non-promoting fallback |
| tc-003 / tc-s01-003 | S01 | yes | red-required | delegated worker reported expected Red failure before implementation | S01-focused pytest selector | pass | missing expected head does not promote |
| tc-003 / tc-s01-004 | S01 | yes | red-required | delegated worker reported expected Red failure before implementation | S01-focused pytest selector | pass | no-findings comment outside trigger boundary does not promote |
| tc-003 / tc-s01-005 | S01 | yes | red-required | delegated worker reported expected Red failure before implementation | S01-focused pytest selector | pass | stale head context does not promote |
| tc-001 / tc-s01-006 | S01 | yes | red-required | delegated follow-up worker reported expected Red failure before implementation | S01-focused pytest selector | pass | no-findings body with caveat line does not promote |
| tc-003 / tc-s01-007 | S01 | yes | red-required | delegated follow-up worker reported expected Red failure before implementation | S01-focused pytest selector | pass | current PR head mismatch does not promote |
| tc-001, tc-003 / tc-s01-008 | S01 | yes | red-required | delegated follow-up worker reported expected Red failure before implementation | S01-focused pytest selector | pass | actionable unresolved thread prevents no-findings promotion |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001 | S01 | S01-focused pytest selector | pass | no-findings issue comment new signal; full-body exact allow-list; no actionable unresolved threads |
| tc-002 | S01 | S01-focused pytest selector | pass | generic fallback non-promotion |
| tc-003 | S01 | S01-focused pytest selector | pass | missing expected head / old trigger / stale head context / current PR head mismatch / actionable unresolved thread rejection |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| alias-mapped | tc-001 | `test_issue_182_s01_review_collector_marks_no_major_issues_fallback_candidate` | tc-001 | existing no-major wording now maps to new signal instead of non-promoting fallback candidate | no | step code review required |
| added | tc-001 | `test_issue_218_s01_no_findings_comment_with_caveat_line_remains_fallback` | tc-001 | step reviewer found loose line-level body matching could false-promote caveated comments | no | yes, step re-review required |
| added | tc-003 | `test_issue_218_s01_no_findings_comment_current_pr_head_mismatch_does_not_promote` | tc-003 | step reviewer found expected-head presence alone did not prove current PR head match | no | yes, step re-review required |
| added | tc-001, tc-003 | `test_issue_218_s01_review_collector_no_findings_with_actionable_unresolved_thread_does_not_promote` | tc-001, tc-003 | step reviewer found current unresolved threads outside selected Codex review evidence could otherwise be bypassed | no | yes, step re-review required |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction to execute issue workflow | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/26b6/spec-dock` | iss-00218 | current session | dev-coder, code-reviewer, spec-reviewer, qa-reviewer | same repo, active issue, current session, named roles; no destructive action / publishing / credentialed access / scope expansion | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | runtime / tests behavior in shipped installed skill asset | dev-coder | collector taxonomy only | requirement/design/plan S01 | `pr_review_snapshot.py`, `tests/unit/infra/test_init_update.py` | snapshot/wait/docs/canonical docs/GitHub state/secrets | S01 targeted pytest and `git diff --check` | expected head missing promotion, broad matcher, allowed paths outside scope | changed files, tests, risks, Ledger Note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Added `codex_no_findings_issue_comment`, strict allow-list, mandatory `no_findings_completion_candidate`, boundary rejection, and non-retryable generic fallback action | `pr_review_snapshot.py`; `tests/unit/infra/test_init_update.py` | worker reported Red: 6 expected failures; Green: targeted pytest 47 passed; tidy: `git diff --check` pass | failed: code-reviewer found head-match and full-body-match gaps | future Codex wording changes out of scope | accepted with bounded follow-up |
| S01 | dev-coder | Tightened promotion to require current PR head / expected head match and full-body exact no-findings body match; added regressions for caveat-line body and current head mismatch | `pr_review_snapshot.py`; `tests/unit/infra/test_init_update.py` | worker reported Red: 2 expected failures; Green: targeted pytest 49 passed; tidy: `git diff --check` pass | failed: first re-review found actionable unresolved thread gap | frontmatter readiness metadata discrepancy resolved in D-003 | accepted with bounded follow-up |
| S01 | dev-coder | Tightened promotion to reject current/actionable unresolved review threads; added regression for strict no-findings plus actionable unresolved thread | `pr_review_snapshot.py`; `tests/unit/infra/test_init_update.py` | worker reported Red: 1 failed / 10 passed; Green: targeted pytest 11 passed; tidy: `git diff --check` pass | passed: second code-reviewer re-review | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | N/A delegated path used | N/A | N/A | N/A | revert S01 commit if needed after review | S01-focused pytest; `git diff --check` | code-reviewer pending | none |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | code-reviewer | stale initial review | failed | N/A | bounded follow-up delegated | initial review found missing current PR head comparison and loose line-level no-findings match |
| S01 | step reviewer | code-reviewer | stale first re-review | failed | N/A | bounded follow-up delegated | first re-review found no-findings could bypass actionable unresolved threads |
| S01 | step reviewer | code-reviewer | fresh second re-review | passed | N/A | proceed to Step Commit Gate | no findings; reviewer confirmed S01 scope is correct |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | `pr_review_snapshot.py`, `tests/unit/infra/test_init_update.py`, `requirement.md`, `design.md`, `plan.md`, `report.md` | S01 commit at `HEAD` after commit gate | `git status --short --branch` -> clean working tree, branch ahead 1 | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` - S01 collector taxonomy。
- `tests/unit/infra/test_init_update.py` - S01 collector tests。
- `spec-dock/active/issue/report.md` - S01 observed evidence ledger。
- `spec-dock/active/issue/requirement.md` - reviewer-pass と一致する frontmatter status 修正。
- `spec-dock/active/issue/design.md` - reviewer-pass と一致する frontmatter status 修正。
- `spec-dock/active/issue/plan.md` - reviewer-pass と一致する frontmatter status 修正。

#### コミット
- S01 commit at `HEAD`: `fix(pr-observation): no-findings issue commentのcollector分類を追加`

#### メモ
- Material implementation decisions are recorded in D-003 and reviewer follow-up rows above.

---

### セッションログ（2026-06-19 HH:MM - HH:MM）

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
| user instruction / explicit approval / none | ... | iss-00218 | current session / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none / denied / unavailable / host conflict | proceed / ask user / block gate / record waiver request |

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

### セッションログ（2026-06-19 HH:MM - HH:MM）

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
