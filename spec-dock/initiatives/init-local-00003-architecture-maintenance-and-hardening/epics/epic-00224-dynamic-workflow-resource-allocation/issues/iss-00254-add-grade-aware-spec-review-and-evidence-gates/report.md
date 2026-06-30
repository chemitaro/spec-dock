---
種別: 実装報告書（Issue）
ID: "iss-00254"
タイトル: "Add Grade Aware Spec Review And Evidence Gates"
関連GitHub: ["#254"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00254 Add Grade Aware Spec Review And Evidence Gates — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合は `No material interpretation changes` / `No decision entries` を明示する。本 Issue では D-001 / D-002 に material decision を記録している。

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
| D-001 | resolved | scope | orchestrator | G3 が docs/template wording だけで閉じるか、runtime readiness hook まで含むかの境界 | docs-only; runtime readiness hook; PR/code-review policy まで拡張 | runtime readiness hook まで含め、PR/code-review policy は対象外にする | AC-005 が missing evidence readiness block を要求しており、docs-only では観測可能性が弱い。一方 PR/code-review policy は明示的に非対象。 | applied | `design.md` section 4〜9; `plan.md` S02; delegated design draft | none |
| D-002 | resolved | implementation | orchestrator | report evidence parser を完全 schema 化するか、stable headings / tokens に限定するか | full schema; stable headings / tokens; manual-only | stable headings / tokens に限定する | G3 は schema migration issue ではなく、false positive を避ける最小 fail-closed hook が必要。 | promoted_to_design | `design.md` section 5; delegated design draft alternatives | none |
| D-003 | resolved | operation | spec-reviewer | delegated draft adoption に前段 reviewer evidence が必要 | delegated draft を promotion evidence とする; manual authoring fallback として source evidence のみ採用 | delegated drafts は source-grounded input として部分採用し、canonical promotion evidence は main-orchestrator manual authoring + fresh planning spec-review で成立させる | Requirement/design/plan 初期状態が draft であり、前段 phase reviewer pass は存在しない。draft を authority/adoption/pass 代替にしないため。 | applied | planning spec-review P1; `report.md` EAL / Delegated Draft Evidence | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | partially_adopted | sub-agent / system-architect | design.md / plan.md / report.md | G3 の Report Evidence Gate、runtime readiness hook、docs/template scope、non-goals、test strategyを source-grounded input として採用。ただし前段 reviewer pass がないため、delegated draft 自体を promotion evidence には使わない。 | `discussions/20260630t180146z-draft-design-g3-evidence-gate-design-proposal.md`; `design.md` sections 2〜12; D-003 | planning spec-review pass |
| EAL-002 | partially_adopted | sub-agent / implementation-planner | plan.md / report.md | closure IDs、step sequence、test commands、reviewer gates、Epic branch baton/no per-issue PR policyを source-grounded input として採用。ただし前段 reviewer pass がないため、delegated draft 自体を promotion evidence には使わない。 | `discussions/20260630t180152z-disc-g3-implementation-plan-draft.md`; `plan.md` sections 2〜10; D-003 | planning spec-review pass |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | G3 は fresh review / EAL / delegated adoption / grade evidence を phase promotion と issue readiness に接続する slice。 | docs/template 更新、runtime readiness hook、focused tests、no per-issue PR baton を計画に固定した。 | low | planning spec-review pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active issue draft、Epic G3 plan、delegated design/plan drafts、runtime workflow state / authority surfaces | none | manual authoring candidate; delegated drafts are source input only | planning spec-review pass | no | execute approved plan |
| design | delegated system-architect draft、`workflow_state.py`、`workflow.py`、`authority.py`、docs/templates/tests | no prior requirement reviewer pass; manual fallback recorded in D-003 | manual authoring candidate; delegated draft not used as promotion evidence | planning spec-review pass | no | execute approved plan |
| plan | delegated implementation-planner draft、existing tests、Epic branch baton policy | no prior requirement/design reviewer pass; manual fallback recorded in D-003 | manual authoring candidate; delegated draft not used as promotion evidence | planning spec-review pass | no | execute approved plan |

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
| system-architect | iss-00254 | `discussions/20260630t180146z-draft-design-g3-evidence-gate-design-proposal.md` | active issue docs; Epic docs; workflow/docs/templates/runtime/tests | `design.md`; `plan.md`; `report.md` | partially_adopted | `design.md`; `plan.md`; `report.md` | orchestrator inspection pass | source input integrated; not promotion evidence | none | prior reviewer evidence missing; resolved by manual authoring fallback D-003 | planning spec-review pass | execute manual-authored canonical docs |
| implementation-planner | iss-00254 | `discussions/20260630t180152z-disc-g3-implementation-plan-draft.md` | active issue docs; Epic docs; workflow/docs/templates/runtime/tests | `plan.md`; `report.md` | partially_adopted | `plan.md`; `report.md` | orchestrator inspection pass | source input integrated; not promotion evidence | none | prior reviewer evidence missing; resolved by manual authoring fallback D-003 | planning spec-review pass | execute manual-authored canonical docs |

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

## 実装サマリー

Planning phase では、G3 の要件・設計・実装計画を Strict issue として具体化し、delegated `system-architect` / `implementation-planner` draft を source input として canonical docs へ再記述した。実装は未開始であり、S01 以降の実装・テスト証跡は execution phase で追記する。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 planning）

#### 対象
- Step: S00 Baseline / 採用証跡
- AC/EC: planning readiness candidate for AC-001〜AC-008
- 計画上の出典（Planned source）:
  - `plan.md` sections 2〜10
  - planning closure ids: G3-C-001 / G3-C-099 candidate only

#### 実施内容
- `issue start iss-00254` を実行した。
- `guidance issue-planning` で `design-not-substantive` block を確認した。
- `system-architect` と `implementation-planner` に discussion draft を委任した。
- 2 つの delegated draft を source inspection し、採用部分を `requirement.md`、`design.md`、`plan.md`、`report.md` へ再記述した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock guidance issue-planning

red / baseline: state=blocked, reason_code=design-not-substantive
note: initial issue docs were template-like and required substantive planning before execution.
```

```bash
./spec-dock/scripts/spec-dock guidance issue-planning

green: state=ready, next_action=planning-ready
```

```bash
./spec-dock/scripts/spec-dock guidance issue-execution

green: state=ready, next_action=execute-approved-plan, may_execute_approved_plan=true
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S00 | Red / baseline | template-like planning docs must block execution | initial `guidance issue-planning` returned `design-not-substantive` | observed command output | pass | baseline recorded before canonical planning rewrite |
| S00 | Green / inspect-only | delegated draft source input / planning readiness | draft 2 件を source input として canonical docs へ再記述し、EAL / Delegated Draft Evidence / Spec Authoring Gate に記録 | source inspection; guidance command | pass | implementation not started |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S00 | runtime report evidence gate は既存 readiness には未実装のため、G3 implementation scope に含める必要がある | planning investigation | requirement/design/plan に runtime hook と tests を固定 | G3-C-001〜G3-C-005 | no | `design.md`; `plan.md` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | planning candidate for G3-C-001 / G3-C-099 | Strict issue planning docs are substantive and executable before implementation starts | `guidance issue-planning` ready; `guidance issue-execution` ready; planning spec-review pass | partial | implementation closure remains pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning-readiness | S00 | yes | inspect-only / planning-readiness | initial docs were draft; guidance blocked on design-not-substantive | `./spec-dock/scripts/spec-dock guidance issue-planning`; `./spec-dock/scripts/spec-dock guidance issue-execution` | pass | execution tests not run yet |
| G3-C-001〜G3-C-005 | S01〜S02 | yes | implementation / runtime tests | N/A | planned focused docs/runtime tests | pending | not closed by S00 |
| G3-C-006〜G3-C-008 | S03 / S90 | yes | regression / parity | N/A | planned regression and parity checks | pending | not closed by S00 |
| G3-C-095 | S95 | yes | reviewer gates | N/A | qa-reviewer / code-reviewer / spec-reviewer | pending | not closed by S00 |
| G3-C-099 | S99 | yes | final local checkpoint | N/A | final commands / commit / issue finish | pending | not closed by S00 |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| planning-readiness candidate | S00 | planning docs / guidance | pass | implementation evidence pending execution |
| G3-C-001〜G3-C-005 | S01〜S02 | docs/runtime implementation and tests | pending | implementation not started |
| G3-C-006〜G3-C-008 | S03 / S90 | regression and parity evidence | pending | implementation not started |
| G3-C-095 | S95 | fresh QA / code / spec review | pending | implementation not started |
| G3-C-099 | S99 | final commands, commit, issue finish | pending | implementation not started |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | G3-C-001〜G3-C-099 | G3 closure IDs | G3-C-001〜G3-C-099 | planned closure set retained; S00 only establishes planning-readiness candidate, not implementation closure | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / workflow issue planning | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/cdfe/spec-dock` | iss-00254 | current session | system-architect / implementation-planner / spec-reviewer / code-reviewer / qa-reviewer | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| planning | delegated | strict issue requires specialist draft evidence | system-architect / implementation-planner | discussion draft evidence only | active issue docs / Epic docs / runtime docs/code/tests | active issue `discussions/` direct child | canonical docs / source / tests | source-grounded draft; no self-claim | forbidden path / self-claim / unresolved design gap | draft artifact path / summary | pass |
| S01〜S99 | pending | implementation not started | N/A | parent orchestration with possible bounded workers | approved plan | planned paths only | out-of-scope PR policy / G2 routing redesign | focused tests / lint / validate / reviews | reviewer blocker / test failure | report evidence | pending execution |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| planning | system-architect | G3 evidence gate design proposal produced | discussion draft only | source inspection | planning spec-review pass | none | source input recorded in EAL-001 |
| planning | implementation-planner | G3 executable implementation plan draft produced | discussion draft only | source inspection | planning spec-review pass | none | source input recorded in EAL-002 |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| planning canonical adoption | canonical requirement/design/plan/report are main-orchestrator-owned and cannot be written by delegated specialists | user requested workflow-driven issue planning; risk accepted: no special waiver | active issue requirement/design/plan/report | local edit / source adoption | revert planning commit or patch rollback | guidance issue-planning / issue-execution ready | planning spec-review pass | N/A |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan | no P0/P1/P2 findings after re-review |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| planning | candidate | requirement/design/plan/report/discussion drafts | pending planning commit | pending | N/A | changed files | N/A | guidance ready; planning spec-review pass |

#### 変更したファイル
- `requirement.md` - G3 requirements approved candidate
- `design.md` - Report Evidence Gate / runtime readiness hook design
- `plan.md` - Strict executable implementation plan
- `report.md` - delegated draft adoption and planning evidence
- `discussions/20260630t180146z-draft-design-g3-evidence-gate-design-proposal.md` - delegated design draft
- `discussions/20260630t180152z-disc-g3-implementation-plan-draft.md` - delegated implementation plan draft

#### コミット
- pending: planning commit after fresh spec-review

#### メモ
- No per-issue PR. G3 will hand off to G4 after execution checkpoint.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | pending execution | planned in S01 / S90 | pending |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | pending execution | planned in S95 | pending |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | pending execution | 0 | pending |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report planning alignment | no P0/P1/P2 findings after re-review | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| planning candidate; implementation not started | no commit yet | final response after checkpoint; no per-issue PR | pending |

## 遭遇した問題と解決 (任意)
- 問題: 初期状態では `design.md` が draft で `guidance issue-planning` が `design-not-substantive` を返した。
  - 解決: delegated specialist drafts を作成し、採用部分を canonical requirement/design/plan/report に再記述した。

## 学んだこと (任意)
- G3 は docs/template wording だけでは AC-005 を満たしにくく、runtime readiness hook と focused negative tests を計画に含める必要がある。

## 今後の推奨事項 (任意)
- Execution phase では report evidence parser を狭く実装し、schema migration へ広げない。

## 省略/例外メモ (必須)
- 該当なし
