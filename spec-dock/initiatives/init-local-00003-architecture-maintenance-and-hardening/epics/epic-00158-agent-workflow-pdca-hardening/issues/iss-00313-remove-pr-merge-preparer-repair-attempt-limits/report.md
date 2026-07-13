---
種別: 実装報告書（Issue）
ID: "iss-00313"
タイトル: "Remove PR Merge Preparer Repair Attempt Limits"
関連GitHub: ["#313"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00313 Remove PR Merge Preparer Repair Attempt Limits — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | 未解決（open） | 運用 / 範囲 / 互換性 | product owner + ChatGPT-Use consultation + orchestrator | 固定回数撤廃後の無限反復防止、mandatory consultation範囲、repair-batch authority、fallback、legacy template compatibilityを確定する必要がある | fixed count only; unlimited repair; progress-based integrated batch with ChatGPT body candidate | progress-based継続、stagnation human gate、blocking/uncertain時mandatory consultation、runtime identityを保持するbody-only adoption、batch内analysis/design/plan/result統合、明示waiver以外fail-closed、legacy template同期 | blocker-centric ADRを維持しつつ、mandatory external consultationとintegrated batch authorityをADR candidateとしてrouteする | 設計昇格準備中（design/ADR facilitation pending） | `requirement.md`; `artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md`; raw transcript SHA-256 `3ac6307f23c073eddb7608ac8878234596a27b0590b4b8003817e12dc96fe7ab` | design/plan authoringと並行してADR facilitationし、Issue Execution前にresolvedへ更新 |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 採用（`adopted`） | 調査（`research`） / product-owner interview | requirement/design/plan | Current fixed limits、same-family stop、existing gatesをsource-groundedに確認し、progress-based継続を採用した | `artifacts/20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md`; `artifacts/20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md` | canonical authoring |
| EAL-002 | 採用（`adopted`） | product-owner raw proposal | requirement/design/plan | ChatGPT-Use consultationとintegrated repair-batchをprimary workflowにするowner intentを原文で保持した | `artifacts/20260713t005848z-user-proposal-chatgpt-assisted-integrated-pr-repair-batch.md` | canonical authoring |
| EAL-003 | 採用（`adopted`） | ChatGPT-Use raw consultation / 調査（`research`） | requirement/design/plan/ADR candidate | Raw transcript全体と検証済みsynthesisを採用。ChatGPT outputはadvisory evidenceであり、runtime identityとcanonical adoptionはlocal orchestratorが所有する | `artifacts/20260713t012618z-chatgpt-raw-integrated-pr-repair-workflow-consultation.md`; `artifacts/20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md` | canonical authoring; ADR facilitation |
| EAL-004 | 採用（`adopted`） | product-owner interview / 議論（`discussion`） | requirement/design/plan/ADR candidate | Raw分析レポート案の全面採用によりmandatory scope、fallback、legacy compatibilityを解決し、採用contractを一つのsynthesisへ統合した | `artifacts/20260713t012046z-interview-mandatory-chatgpt-consultation-scope.md`; `artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md` | requirement phase authoring; ADR facilitation |
| EAL-005 | 一部採用（`partially_adopted`） | ChatGPT 5.6 Pro Issue planning pack / local-context | requirement/design/plan | single-Issue境界、strict推奨、semantic continuation gate、integrated batch、consultation authority、provider-first変更面、test/rollback方針を採用した。candidate固有のauthority文言、未検証主張、採用前チェック状態は正本へ持ち込まずlocal evidenceに合わせて修正した | `artifacts/20260713t025134z-draft-requirement-chatgpt56-issue-requirement-candidate.md`; `artifacts/20260713t034500z-chatgpt-raw-chatgpt56-issue-planning-transcript.md` SHA-256 `ca44fdb2e6ef35f7fc49cb87455fbd153fb9ced8a03988c154c5f9af70525327`; source manifest SHA-256 `5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d` | canonical requirement/design/plan integration; fresh spec review |
| EAL-006 | 採用（`adopted`） | ChatGPT 5.6 Pro authoring transport / local mechanical reconstruction | planning evidence provenance | 初回ZIPはprovenance表現とscanner抵触語によりreject。同一ChatGPT conversationへ修正を依頼したが修正版attachment取得がtransport failureとなったため、指示された限定的metadata/語句修正とmanifest再計算のみを初回packへ機械適用した。再構築ZIPはpack review pass。ChatGPTが生成した取得不能ZIPとのbyte identityは主張しない | `artifacts/20260713t034501z-chatgpt-raw-chatgpt56-pack-repair-transcript.md` SHA-256 `1f06fdaff2e8c8d08698f69d82063cbdeacc92fc1843887815f8b7e400042295`; reconstructed ZIP SHA-256 `d9809657e544185d28ae84c73a0a913db1bc48e3515c1f6763d4605290fedab6`; tree digest `ca9f01ba6c70a284df3c925b8b97af4ce30f004d34735018389fcd0a6478df73` | transformed evidence provenance accepted; raw and canonical authority remain separate |
| EAL-007 | 一部採用（`partially_adopted`） | ChatGPT 5.6 Pro design candidate + fresh spec-reviewer | design | responsibility architecture、continuation algorithm、consultation contract、template/file surface、compatibility/test strategyを採用。採用済みmanual fallback欠落、strict/candidate authority表現、stale policy矛盾はlocal integrationと反復reviewで修正した | `artifacts/20260713t030000z-draft-design-chatgpt56-issue-design-candidate.md`; canonical design SHA-256 `9beb093a291f104a194857b1ed7566b8e13060604d1708aa308e5fd213f2f7e6` | assurance binding refresh; plan authoring |
| EAL-008 | 一部採用（`partially_adopted`） | ChatGPT 5.6 Pro plan candidate + fresh spec-reviewer | plan | S01→S05→S90→S95→S99、allowed/forbidden paths、Red/Green tests、CLOS-001..016、parity/rollback/security gatesを採用。candidate/strict authority表現、current state、DES-011 fallback/stale-refresh closureをcanonical stateへ修正した | `artifacts/20260713t033000z-draft-plan-chatgpt56-issue-plan-candidate.md`; fresh plan review `passed` | assurance binding refresh complete; planning complete |
| EAL-009 | 採用（`adopted`） | product-owner language correction + fresh spec-reviewer | requirement/design/plan | ChatGPT由来の英語説明文を日本語へ統合し、パス、コマンド、コード、ID、schema field、列挙契約値、完全一致markerだけを原文維持した。翻訳中に生じた`partial-use`とstale相談fallbackの曖昧さも要件・DES-011へ整合させた | fresh Japanese-doc review `passed`; final SHA-256は更新済みassurance source bindingを参照 | 日本語正本としてplanning gate維持; 今後の再発防止はmemory update noteへ記録 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | 固定回数による停止を廃止し、fresh evidence・material strategy delta・validationで継続を判定する | integrated repair batch、mandatory ChatGPT consultation、one-invocation manual fallback、template同期 | 中: consultation導入が主目的化しsemantic continuationが埋没する恐れ。AC-001/002/006をprimary gateとして固定 | 合格（passed） |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | provider skill/templates、回答済みinterviews、adopted synthesis、ChatGPT 5.6 Pro local-context pack、親Epic docs | manual fallback契約は回答済み。追加質問なし | EAL-001..006に従い採用/部分採用。authority claimとstale candidate stateは棄却 | passed（初回failed後、conditional findingを機械修正） | no | assurance classify後にdesignへ昇格 |
| design | canonical requirement、ChatGPT 5.6 design candidate、current provider/templates、assurance standard contract | manual fallback/stale refresh predicateはreviewで解決 | EAL-007として部分採用し、candidate authorityと不整合を修正 | passed（fresh spec-reviewer、SHA `9beb093a...`） | no | assurance binding refresh後にplan authoring |
| plan | canonical requirement/design、ChatGPT 5.6 plan candidate、provider/test topology、assurance standard contract | none unresolved; ADRはexecution前gate | EAL-008として部分採用し、stale candidate/profile表現を修正 | passed（fresh spec-reviewer conditional findingはbookkeepingのみ、本行/EAL/委任証跡修正で充足） | no for planning; ADR remains execution blocker | planning complete; execution handoffはADR/source-binding/ownership確認後 |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used（ChatGPT 5.6 Pro local-context authoring pack）
- 未使用の場合:
  - not applicable
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
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
  - legacy `discussions/` と既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT 5.6 Pro | iss-00313 | `artifacts/20260713t025134z-draft-requirement-chatgpt56-issue-requirement-candidate.md`; `artifacts/20260713t030000z-draft-design-chatgpt56-issue-design-candidate.md`; `artifacts/20260713t033000z-draft-plan-chatgpt56-issue-plan-candidate.md` | source manifest `5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d` | `requirement.md`, `design.md`, `plan.md` | `partially_integrated` | `requirement.md`, `design.md`, `plan.md` | pack review pass; local source reconciliation; fresh requirement/design/plan reviews | single-Issue境界、semantic continuation、integrated batch、authority/security/test/design/execution sequenceを統合 | candidate authority/self-status、未検証主張、manual fallback/stale predicate不整合、strict profile claim | none for planning | requirement/design/plan passed | planning promotion complete; ADR remains execution gate |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| ワークフロー単位の許可証跡不足（missing workflow-scoped authorization evidence） | blocked / incomplete | ワークフロー利用依頼の authorization source と boundary を記録する、または手動 authoring に戻す | ワークフロー単位の named role 許可（Workflow-Scoped Authorization） / この section | ineligible |
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

### セッションログ（2026-07-13 HH:MM - HH:MM）

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

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| ワークフロー利用依頼 / 明示承認 / なし（user request to use SpecDock workflow / explicit approval / none） | ... | iss-00313 | 現在セッション（current session） / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | 範囲: active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility。破壊的操作 / 外部公開 / credentialed external mutation / scope expansion / private external system use / out-of-workflow role は含めない | 完了 / セッション終了 / scope 変更 / host policy conflict / user revocation（issue complete / session end / scope change / host policy conflict / user revocation） | none / denied / unavailable / host conflict | 続行 / separate-confirmation exception は user に確認 / block gate / record waiver request |

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

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `lite` | `not applicable` | `not applicable` | ライト該当なし理由（lite not applicable reason） | `pass / fail / blocked` | `ready / blocked` |
| `standard` | `system-architect / implementation-planner / manual fallback` | `used / skipped / unavailable / denied` | `artifacts/...` / manual evidence / skip reason: ... | `pass / fail / blocked` | `ready / blocked` |
| `strict` | `system-architect / implementation-planner / manual fallback` | `used / unavailable / denied` | `artifacts/...` / manual fallback evidence | `pass / fail / blocked` | `ready / blocked` |
| `critical` | `system-architect / implementation-planner / manual fallback` | `used / unavailable / denied` | `artifacts/...` / explicit approval and risk acceptance | `pass / fail / blocked` | `ready / blocked` |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer / final reviewer | code-reviewer / spec-reviewer / qa-reviewer | fresh / stale | passed / failed / unavailable / denied / waived / provisional | yes / no / N/A | proceed / blocked / incomplete / follow-up required | ... |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
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

### セッションログ（2026-07-13 HH:MM - HH:MM）

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

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
