---
種別: 実装報告書（Issue）
ID: "iss-00138"
タイトル: "Split Issue Planning and Execution Skills"
関連GitHub: ["#138"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00138 Split Issue Planning and Execution Skills — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する。

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
| D-001 | resolved | scope | orchestrator + user interview | `spec-dock-issue-planning` を lightweight planning reminder とするか delegated/canonical authoring role とするかが requirement scope を左右した | Option A: existing workflow を保った Issue planning entrypoint; Option B: discussion draft author 寄り; Option C: canonical direct authoring 寄り | Existing workflow を保ち、Issue planning と Issue execution を分割する。Design draft は `system-architect`、plan draft は `implementation-planner` が作れるが、main orchestrator が正式 docs を作成する。 | ユーザー回答で「既存ルールを保ったまま分割」と明示されたため。Epic delegated authoring model とも整合する。 | applied | `discussions/20260529t012153z-interview-issue-planning-skill-authority-boundary.md`; `requirement.md` | design phase で docs routing と dogfooding parity の詳細を具体化する |
| D-002 | resolved | operation | orchestrator | `system-architect` draft の post-run diff guard が pre-existing dirty discussion により blocked になった | Option A: delegated draft を採用証跡として使う; Option B: diff guard failed draft を採用拒否し、main orchestrator manual authoring path で canonical design を作る | Diff guard failed の draft は adoption-ready delegated evidence として扱わず、採用拒否済みの参考証跡として記録する。Canonical design は main orchestrator が requirement と source docs に基づいて作成する。 | `workflow_spec_authoring.md` / `phase_design.md` は post-run diff guard pass まで delegated output を adoption-ineligible とする。今回の block は委任前から未追跡だった research/interview discussion が原因。採用拒否済みのため unresolved `blocked` adoption entry は残さない。 | applied | `delegated-authoring diff-guard` blocked; `discussions/20260529t015038z-disc-issue-planning-execution-split-design-analysis.md`; `design.md` | Plan phase では baseline hygiene を確認し、dirty baseline が残る場合は同じく採用拒否 + manual authoring path に戻す |
| D-003 | resolved | operation | orchestrator | `implementation-planner` draft の post-run diff guard が pre-existing dirty discussion により blocked になった | Option A: delegated draft を採用証跡として使う; Option B: diff guard failed draft を採用拒否し、main orchestrator manual authoring path で canonical plan を作る | Diff guard failed の draft は adoption-ready delegated evidence として扱わず、採用拒否済みの参考証跡として記録する。Canonical plan は main orchestrator が reviewer-pass requirement/design と source docs に基づいて作成する。 | Delegated plan output は post-run diff guard pass、report ledger adoption evidence、fresh plan review が揃うまで adoption-ineligible。今回の block は既存 discussion が dirty baseline と判定されたためで、draft 内容の plan blocker ではない。 | applied | `delegated-authoring diff-guard` blocked; `discussions/20260529t020902z-disc-issue-planning-execution-split-plan-draft.md`; `plan.md` | Plan `spec-reviewer` を実行し、pass まで修正する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-001 | adopted | discussion memo | user | Add Issue planning skill, keep Issue execution for implementation, clarify hub routing, preserve clarification combination. | `requirement.md` | purpose / scope / AC | User-provided scope memo defined the desired split and initial success conditions. | direct user intent | `discussions/20260529t000926z-disc-issue-planning-execution-skill-split-scope-memo.md`; `requirement.md` | main orchestrator | `spec-reviewer` pass for requirement phase | no | design phase |
| EAL-002 | adopted | research | orchestrator | Current assets/docs/tests have Initiative/Epic planning skills but no Issue planning skill; Issue execution is the only Issue leaf skill. | `requirement.md` | background / scope / AC | Source-grounded read confirmed the existing asymmetry and affected shipped asset/test surfaces. | source-grounded local repo evidence | `discussions/20260529t012153z-01-research-issue-planning-execution-split-source-grounding.md`; `requirement.md` | main orchestrator | `spec-reviewer` pass for requirement phase | no | design phase |
| EAL-003 | adopted | interview | user | Preserve existing workflow, split planning/execution, keep delegated draft flow, and keep main orchestrator canonical ownership. | `requirement.md` | scope / constraints / AC / EC | User answer resolved the authority boundary and ruled out new direct canonical authoring authority. | direct user answer | `discussions/20260529t012153z-interview-issue-planning-skill-authority-boundary.md`; `requirement.md` | main orchestrator | `spec-reviewer` pass for requirement phase | no | design phase |
| EAL-004 | rejected | delegated design draft | `system-architect` | Proposed design analysis for skill split implementation. | N/A: not adopted into canonical artifact | N/A: not adopted | Post-run diff guard was blocked by pre-existing dirty discussion files, so this draft is adoption-ineligible and was explicitly rejected as delegated evidence. Canonical design was written through main orchestrator manual authoring path from approved requirement and source docs. | rejected delegated evidence; not used for phase promotion | `discussions/20260529t015038z-disc-issue-planning-execution-split-design-analysis.md`; `delegated-authoring diff-guard` blocked output; `design.md` | main orchestrator | `spec-reviewer` pass for design phase | no: rejected evidence is resolved and cannot promote or block design | design review passed; proceed with plan review |
| EAL-005 | rejected | delegated plan draft | `implementation-planner` | Proposed implementation plan slices, test strategy, review gates, docs impact, and final quality gate. | N/A: not adopted into canonical artifact | N/A: not adopted | Post-run diff guard was blocked by pre-existing dirty discussion files, so this draft is adoption-ineligible and was explicitly rejected as delegated evidence. Canonical plan is written through main orchestrator manual authoring path from reviewer-pass requirement/design and source docs. | rejected delegated evidence; not used for phase promotion | `discussions/20260529t020902z-disc-issue-planning-execution-split-plan-draft.md`; `delegated-authoring diff-guard` blocked output; `plan.md` | main orchestrator | pending `spec-reviewer` for plan phase | no: rejected evidence is resolved and cannot promote or block plan | run plan review on manual canonical plan |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` states the primary objective as splitting Issue planning and Issue execution while keeping existing workflow semantics. | Scope includes provider/dogfooding parity, hub routing, docs, and tests as secondary support for the split. | low: requirement explicitly forbids new direct canonical authoring authority and full automation. | `spec-reviewer` pass for requirement phase; non-blocking hygiene findings corrected in report |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Active issue/epic docs; `workflow_clarification.md`; `workflow_spec_authoring.md`; `workflow_issue.md`; `phase_plan_issue.md`; provider skill assets; README; `tests/test_init_update.py`; `tests/cli_runtime/test_wrappers.py`; discussion memo; research artifact | Answered in `discussions/20260529t012153z-interview-issue-planning-skill-authority-boundary.md`: preserve existing workflow, split planning/execution, keep `system-architect` and `implementation-planner` draft roles, main orchestrator owns canonical docs | adopted into `requirement.md`; reviewer hygiene findings applied to report evidence | `spec-reviewer` pass: no P0/P1 blocker; P2/P3 report hygiene findings corrected | no current requirement-blocking question | promote to design authoring; request `system-architect` discussion draft |
| design | `requirement.md`; `design.md`; `report.md`; `workflow_spec_authoring.md`; `phase_design.md`; `workflow_issue.md`; `phase_plan_issue.md`; `authoring/issue-plan.md`; provider skill assets; provider docs; tests; research/interview discussions | `system-architect` draft failed diff guard and was rejected as delegated evidence; canonical design was authored manually from approved requirement and source docs. Re-review added `authoring/issue-plan.md` as field-level plan contract and clarified dogfooding paths as parity outputs. | adopted into `design.md`; rejected diff-guard-failed delegated draft as non-authoritative evidence in EAL-004 | `spec-reviewer` pass: no findings; prior P1/P2 findings corrected | no current design-blocking question | promote to plan authoring; request `implementation-planner` discussion draft |
| plan | `requirement.md`; `design.md`; `plan.md`; `report.md`; `workflow_spec_authoring.md`; `phase_plan.md`; `phase_plan_issue.md`; `authoring/issue-plan.md`; `workflow_issue.md`; `implementation-planner` draft; tests/docs source surfaces | `implementation-planner` draft failed diff guard and was rejected as delegated evidence; canonical plan was authored manually from reviewer-pass requirement/design and source docs. Re-review corrections added required parity evidence, external final commit evidence, PR Delivery / Merge Preparation gates, Implementation Delegation Gate destinations, exact ledger note output, and per-step commit/no-op gates. | adopted into `plan.md`; rejected diff-guard-failed delegated draft as non-authoritative evidence in EAL-005 | `spec-reviewer` pass: no P0/P1 blocker; one non-blocking P2 wording suggestion about final commit scope remains | no current plan-blocking question | implementation preparation ready; wait for user confirmation before execution |

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
| `spec-dock-system-architect` | iss-00138 | `discussions/20260529t015038z-disc-issue-planning-execution-split-design-analysis.md` | active context; active issue requirement/design/plan/report; issue discussions; workflow docs; provider skills; docs README; tests | `design.md`; `report.md`; `plan.md` | rejected | [] | failed: `dirty_baseline_discussion` | not integrated as delegated evidence; main orchestrator manual authoring path used for `design.md` | entire draft is adoption-ineligible as delegated evidence due diff guard block | resolved by rejection in EAL-004; pre-existing dirty discussion files in baseline: `20260529t012153z-01-research...md`, `20260529t012153z-interview...md` | design `spec-reviewer` passed | no delegated draft promotion; canonical design passed fresh `spec-reviewer` |
| `spec-dock-implementation-planner` | iss-00138 | `discussions/20260529t020902z-disc-issue-planning-execution-split-plan-draft.md` | active context; active issue requirement/design/plan/report; workflow docs; provider skills; provider docs; tests | `plan.md`; `report.md` | rejected | [] | failed: `dirty_baseline_discussion` | not integrated as delegated evidence; main orchestrator manual authoring path used for `plan.md` | entire draft is adoption-ineligible as delegated evidence due diff guard block | resolved by rejection in EAL-005; pre-existing dirty discussion files in baseline include research/interview/design draft discussion files | pending plan `spec-reviewer` | no delegated draft promotion; canonical plan still requires fresh `spec-reviewer` |

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

### セッションログ（2026-05-29 HH:MM - HH:MM）

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
| user instruction | `/Users/iwasawayuuta/workspace/worktrees/spec-dock/spec-dock-issue-planning-execution-split` | iss-00138 | current session, 2026-05-29 | `spec-reviewer`, `system-architect`, `implementation-planner` | Create requirement/design/plan through existing spec-dock authoring workflow; use `spec-reviewer` until pass; use `system-architect` for design draft evidence and `implementation-planner` for plan draft evidence; canonical docs remain main-orchestrator-owned. No implementation edits, destructive action, GitHub mutation, publishing, credentialed access, scope expansion, or direct canonical write by delegated authors. | implementation readiness report to user / session end / scope change / host policy conflict / user revocation | none | proceed with requirement review, then delegated design draft, design integration/review, delegated plan draft, plan integration/review |

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

### セッションログ（2026-05-29 HH:MM - HH:MM）

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
