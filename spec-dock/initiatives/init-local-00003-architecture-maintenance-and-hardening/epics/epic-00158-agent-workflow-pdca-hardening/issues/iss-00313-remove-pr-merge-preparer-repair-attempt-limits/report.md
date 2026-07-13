---
種別: 実装報告書（Issue）
ID: "iss-00313"
タイトル: "Remove PR Merge Preparer Repair Attempt Limits"
関連GitHub: ["#313"]
状態: "execution-complete"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00313 Remove PR Merge Preparer Repair Attempt Limits — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）である。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit evidenceを記録する。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置く。

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
| D-001 | `resolved` | operation / scope / compatibility | product owner + ChatGPT-Use consultation + orchestrator | 固定回数撤廃後の無限反復防止、mandatory consultation範囲、repair-batch authority、fallback、legacy template compatibilityを確定する必要がある | fixed count only; unlimited repair; evidence-gated semantic continuation | 固定回数を停止権限から外し、fresh evidence・material strategy delta・validation・再観測で継続を判定する。ChatGPTはadvisory evidenceに限定し、staleはrefresh-first、hard-unrecoverable時だけ明示承認のone-invocation local-only fallbackを許可する | 回数は進捗のproxyにすぎず、早すぎる停止と盲目的反復の両方を防げないため、fresh evidenceとmaterial strategy deltaをauthorityにする | `promoted_to_adr` | `artifacts/20260713t040923z-adr-evidence-gated-pr-repair-continuation.md`; fresh ADR review `passed` | cross-skill展開は別ADR/Epicで扱う。Issue実行ブロッカーなし |
| D-002 | `resolved` | deviation | final spec-reviewer | canonical docs変更後のissue-local assurance source binding更新が、AC-013とplan禁止pathの文言上はmetadata変更禁止に含まれていた | refreshを戻してstale assuranceにする; 手動例外とする; standard classifyによるsource_binding hash refreshだけを明示許可する | profile/authority/schema/classificationの手動変更は禁止し、canonical docs変更後のSpecDock classifyによるsource_binding SHA refreshだけを許可する | assurance authorityを有効に保ちながら、実装がassurance obligationを弱める変更を禁止できる | `applied` | requirement AC-013/CON-002、design 13.4、plan 3.3、`assurance classify --stage requirement`、`assurance verify` | issue-local source-binding例外であり、共通policy変更や追加follow-upは不要 |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | 調査（`research`） / product-owner interview | requirement/design/plan | Current fixed limits、same-family stop、existing gatesをsource-groundedに確認し、progress-based継続を採用した | `artifacts/20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md`; `artifacts/20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md` | canonical authoring |
| EAL-002 | `adopted` | product-owner raw proposal | requirement/design/plan | ChatGPT-Use consultationとintegrated repair-batchをprimary workflowにするowner intentを原文で保持した | `artifacts/20260713t005848z-user-proposal-chatgpt-assisted-integrated-pr-repair-batch.md` | canonical authoring |
| EAL-003 | `adopted` | ChatGPT-Use raw consultation / 調査（`research`） | requirement/design/plan/ADR candidate | Raw transcript全体と検証済みsynthesisを採用。ChatGPT outputはadvisory evidenceであり、runtime identityとcanonical adoptionはlocal orchestratorが所有する | `artifacts/20260713t012618z-chatgpt-raw-integrated-pr-repair-workflow-consultation.md`; `artifacts/20260713t011949z-research-chatgpt-consultation-integrated-pr-repair-workflow.md` | canonical authoring; ADR facilitation |
| EAL-004 | `adopted` | product-owner interview / 議論（`discussion`） | requirement/design/plan/ADR candidate | Raw分析レポート案の全面採用によりmandatory scope、fallback、legacy compatibilityを解決し、採用contractを一つのsynthesisへ統合した | `artifacts/20260713t012046z-interview-mandatory-chatgpt-consultation-scope.md`; `artifacts/20260713t013418z-disc-adopted-integrated-pr-repair-workflow-synthesis.md` | requirement phase authoring; ADR facilitation |
| EAL-005 | `partially_adopted` | ChatGPT 5.6 Pro Issue planning pack / local-context | requirement/design/plan | single-Issue境界、strict推奨、semantic continuation gate、integrated batch、consultation authority、provider-first変更面、test/rollback方針を採用した。candidate固有のauthority文言、未検証主張、採用前チェック状態は正本へ持ち込まずlocal evidenceに合わせて修正した | `artifacts/20260713t025134z-draft-requirement-chatgpt56-issue-requirement-candidate.md`; `artifacts/20260713t034500z-chatgpt-raw-chatgpt56-issue-planning-transcript.md` SHA-256 `ca44fdb2e6ef35f7fc49cb87455fbd153fb9ced8a03988c154c5f9af70525327`; source manifest SHA-256 `5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d` | canonical requirement/design/plan integration; fresh spec review |
| EAL-006 | `adopted` | ChatGPT 5.6 Pro authoring transport / local mechanical reconstruction | planning evidence provenance | 初回ZIPはprovenance表現とscanner抵触語によりreject。同一ChatGPT conversationへ修正を依頼したが修正版attachment取得がtransport failureとなったため、指示された限定的metadata/語句修正とmanifest再計算のみを初回packへ機械適用した。再構築ZIPはpack review pass。ChatGPTが生成した取得不能ZIPとのbyte identityは主張しない | `artifacts/20260713t034501z-chatgpt-raw-chatgpt56-pack-repair-transcript.md` SHA-256 `1f06fdaff2e8c8d08698f69d82063cbdeacc92fc1843887815f8b7e400042295`; reconstructed ZIP SHA-256 `d9809657e544185d28ae84c73a0a913db1bc48e3515c1f6763d4605290fedab6`; tree digest `ca9f01ba6c70a284df3c925b8b97af4ce30f004d34735018389fcd0a6478df73` | transformed evidence provenance accepted; raw and canonical authority remain separate |
| EAL-007 | `partially_adopted` | ChatGPT 5.6 Pro design candidate + fresh spec-reviewer | design | responsibility architecture、continuation algorithm、consultation contract、template/file surface、compatibility/test strategyを採用。採用済みmanual fallback欠落、strict/candidate authority表現、stale policy矛盾はlocal integrationと反復reviewで修正した | `artifacts/20260713t030000z-draft-design-chatgpt56-issue-design-candidate.md`; canonical design SHA-256 `9beb093a291f104a194857b1ed7566b8e13060604d1708aa308e5fd213f2f7e6` | assurance binding refresh; plan authoring |
| EAL-008 | `partially_adopted` | ChatGPT 5.6 Pro plan candidate + fresh spec-reviewer | plan | S01→S05→S90→S95→S99、allowed/forbidden paths、Red/Green tests、CLOS-001..016、parity/rollback/security gatesを採用。candidate/strict authority表現、current state、DES-011 fallback/stale-refresh closureをcanonical stateへ修正した | `artifacts/20260713t033000z-draft-plan-chatgpt56-issue-plan-candidate.md`; fresh plan review `passed` | assurance binding refresh complete; planning complete |
| EAL-009 | `adopted` | product-owner language correction + fresh spec-reviewer | requirement/design/plan | ChatGPT由来の英語説明文を日本語へ統合し、パス、コマンド、コード、ID、schema field、列挙契約値、完全一致markerだけを原文維持した。翻訳中に生じた`partial-use`とstale相談fallbackの曖昧さも要件・DES-011へ整合させた | fresh Japanese-doc review `passed`; final SHA-256は更新済みassurance source bindingを参照 | 日本語正本としてplanning gate維持; 今後の再発防止はmemory update noteへ記録 |
| EAL-010 | `adopted` | ADR facilitation + fresh spec-reviewer | requirement/design/plan/accepted ADR | 回数ではなく証拠へ継続authorityを移す長期運用判断をIssue-local ADRへ昇格し、stale相談のrefresh-first契約を全正本で統一した | `artifacts/20260713t040923z-adr-evidence-gated-pr-repair-continuation.md`; fresh ADR review `passed` | accepted ADRを実装契約としてS01へ進む |
| EAL-011 | `adopted` | S90 impact audit + fresh spec-reviewer | design/plan/tests | 現行providerを検証するIssue 105回帰テストの旧固定上限肯定assertを追随対象とし、当該1ファイルだけを許可パス・S90/S99検証へ追加した | fresh S90 amendment review `passed`; target Red `1 failed`; updated target Green `1 passed` | S95 independent reviewsへ進む |
| EAL-012 | `adopted` | S95 spec/code/QA findings | provider skill/templates/tests/report | fallback invocation監査field、絶対停止・再利用禁止、semantic stop、test感度、report観測台帳の不足を共通P1 root causeとして採用し、Red強化後に修正した | initial reviews `failed`; strengthened Red `3 failed`; provider Green `3 passed`; projected integration `4 passed` | fresh S95 re-review |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | 固定回数による停止を廃止し、fresh evidence・material strategy delta・validationで継続を判定する | integrated repair batch、mandatory ChatGPT consultation、one-invocation manual fallback、template同期 | 中: consultation導入が主目的化しsemantic continuationが埋没する恐れ。AC-001/002/006をprimary gateとして固定 | 合格（passed） |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | provider skill/templates、回答済みinterviews、adopted synthesis、ChatGPT 5.6 Pro local-context pack、親Epic docs | manual fallback契約は回答済み。追加質問なし | EAL-001..006に従い採用/部分採用。authority claimとstale candidate stateは棄却 | `passed` | no | `promote` |
| design | canonical requirement、ChatGPT 5.6 design candidate、current provider/templates、assurance standard contract | manual fallback/stale refresh predicateはreviewで解決 | EAL-007として部分採用し、candidate authorityと不整合を修正 | `passed` | no | `promote` |
| plan | canonical requirement/design、ChatGPT 5.6 plan candidate、provider/test topology、accepted ADR、assurance standard contract | none | EAL-008..010として部分採用/採用し、candidate表現とADRブロッカーを解決 | `passed` | no | `execute approved plan` |

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
| ChatGPT 5.6 Pro | iss-00313 | `artifacts/20260713t025134z-draft-requirement-chatgpt56-issue-requirement-candidate.md`; `artifacts/20260713t030000z-draft-design-chatgpt56-issue-design-candidate.md`; `artifacts/20260713t033000z-draft-plan-chatgpt56-issue-plan-candidate.md` | source manifest `5a10d9f35e84419daf6e8bd37b2886a2bea7d4ee723693e7de1b59abe7af530d` | `requirement.md`, `design.md`, `plan.md` | `partially_integrated` | `requirement.md`, `design.md`, `plan.md` | pack review pass; local source reconciliation; fresh requirement/design/plan reviews | single-Issue境界、semantic continuation、integrated batch、authority/security/test/design/execution sequenceを統合 | candidate authority/self-status、未検証主張、manual fallback/鮮度predicate不整合、strict profile claim | none | `passed` | `promote` |

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

## S01 ローカルソース結び付けと特性記録

- ブランチ: `iss-00313-remove-pr-merge-preparer-repair-attempt-limits`
- 基準HEAD: `cdb35c037708a97f8d423b16c9d275d4ee2e456f`
- worktree ownership: 対象ブランチは本worktreeだけで使用され、他worktreeとの重複なし。
- 作業ツリー差分: Issue正本、assurance binding、accepted ADRだけ。S01開始時点でprovider/tests/mirror差分なし。
- 基準テスト: 計画指定の3件を実行し、`3 passed in 3.30s`。

### S01 ソース結び付け表

| 対象 | SHA-256 | 分類 |
|---|---|---|
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md` | `7a630fcc1e44ba78220abc12c17cf0acbf797fd1f5e863c945fa41337c9d1f0a` | provider authority / 旧固定上限あり |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/agents/openai.yaml` | `098d65f17c2db28da883c2ef24da592ff7bdb386696d270488cdd0cf06fa4c67` | provider metadata authority |
| `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/templates/pr-repair-batch.md` | `d324ad20b7dc22f0ac0c271d16f48e346706ed3b11d97b88c13adefcf7f98020` | skill-local body template / 旧loop limitあり |
| `src/spec_dock/assets/spec_dock/templates/artifacts/pr-repair-batch.md` | `26563debf685efc3f68eeca8e5ab24dae3ef626ce0ede80fe1144ea69f42b255` | generated artifact provider template / 旧停止条件あり |
| `src/spec_dock/assets/spec_dock/templates/discussions/pr-repair-batch.md` | `26563debf685efc3f68eeca8e5ab24dae3ef626ce0ede80fe1144ea69f42b255` | generated discussion provider template / artifactと同一 |
| `tests/cli_runtime/test_new.py` | `dc3fa88c73f47a01852ed3c277a14b8fa482f132db6dd3a7ba8067770f489a0d` | S02/S05 test authority |
| `tests/cli_runtime/test_runtime_new_doc_s09.py` | `bf5db094911212ce71e822de2cf60e2f6785626a8e2185d82da448f01b5dc519` | S02/S05 parity test authority |
| `tests/cli_runtime/test_wrappers.py` | `6d3788d7dd9c326ebbc451b44b64a81b8d6cfd0117ea0073d8954000f3eebf17` | installed skill contract test authority |

### S01 旧ポリシー一覧

- provider skill `SKILL.md:305-315`: P0 1回、同一P1 family 2回、合計4回、同一family再発時の自動human gate。
- skill-local template `templates/pr-repair-batch.md:114`: same failure class / total attempts の上限到達を停止条件とする。
- artifact/discussion provider templates `:220-230`: 同一family再発とloop limit到達を停止条件とする。
- 既存のpermission/auth、external/flaky、base conflict、unknown、scope expansion、migration、secret/deployment、ambiguous intent、platform-only操作等のhard gateは置換対象外。

### S01 完了判定

`TC-S01-001`、`TC-S01-002`、`TC-S01-003`はすべて`pass`。ローカル本文、対象パス、旧marker、baselineを確認し、Issue境界との不一致なし。S02へ進行可。

## S02 Red契約テスト

- delegated role: `dev-coder`
- changed files: `tests/cli_runtime/test_new.py`、`tests/cli_runtime/test_runtime_new_doc_s09.py`、`tests/cli_runtime/test_wrappers.py`
- 許可外変更: なし。
- 新規node IDs:
  - `TestCliNew::test_new_artifact_pr_repair_batch_uses_evidence_gated_continuation_contract`
  - `TestRuntimeNewDocS09::test_pr_repair_batch_continuation_fields_remain_markdown_only_and_runtime_opaque`
  - `TestCliRulesContract::test_scaffolded_pr_merge_preparer_uses_evidence_gated_repair_continuation_policy`
- 観測Red: `2 failed, 1 passed`。generated / installed surfaceで `ChatGPT Consultation Gate`、`Integrated Repair Strategy`、`Iteration Ledger`、`strategy_delta`、`orchestrator_disposition`、`telemetry only` が欠落し、旧固定上限・同一family自動停止markerが残存したため失敗。
- 特性Green: runtime opaque testは、既存`CreateDiscussionDocRequest`経路だけで新Markdownフィールドを保持し`pass`。
- 基準回帰: S01指定3件は`3 passed in 2.84s`。Ruffと`git diff --check`もpass。
- 完了判定: `TC-S02-001..006`の肯定・否定・維持・runtime非依存・installed projection・hard gate preservation感度を備え、provider差分なしで意図したRedを確認。S03/S04へ進行可。

## S03 プロバイダースキルとエージェントプロンプト

- delegated role: `doc-writer`
- changed files: provider `SKILL.md` と `agents/openai.yaml` の2件だけ。
- 実装: 固定P0/P1/total capと同一family再発だけの自動停止を削除。observe→integrated batch→fresh consultation→orchestrator disposition/`strategy_delta`→bounded worker→push→re-observe、相談状態、stale refresh-first、hard-unrecoverable時の明示承認one-invocation local-only fallback、telemetry-only iterationを明記。
- authority: ChatGPTはadvisory evidenceのみ。orchestratorが採否を所有し、既存P2/P3 no-mutation、hard gate、禁止GitHub操作、人間merge境界を維持。
- 検証: YAML parse、`git diff --check`、wrapper焦点テスト`1 passed`。`requirement expansion`と`scope expansion`の完全一致markerも確認。
- 完了判定: `TC-S03-001..005` pass。S03許可外変更なし。

## S04 修復バッチテンプレート

- delegated role: `doc-writer`
- changed files: skill-local、artifact provider、discussion providerの3テンプレートだけ。
- 実装: `ChatGPT Consultation Gate`、`Integrated Repair Strategy`、`Orchestrator Disposition`、`Iteration Ledger`と、`consultation_status`、`strategy_delta`、`orchestrator_disposition`、telemetry-only、sanitized repository-relative evidenceを追加。raw model conversation、secret、host absolute pathの格納を禁止。
- 互換性: 新runtime field/schemaなし。artifact/discussion provider templatesは`cmp -s`でbyte-identical。旧batchはappend-compatibleで移行不要。
- 検証: 新規焦点3件`3 passed in 1.75s`、旧markerの否定`rg`結果なし、`git diff --check` pass。
- 完了判定: `TC-S04-001..005` pass。S04許可外変更なし。

## S05 プロバイダーからdogfoodingへの統合

- delegated role: `dev-coder`
- 標準更新: `uvx --from . spec-dock update .` 成功。current checkoutをbuild/installし、既存repo-root shortcut警告だけを観測。
- Issue保全: update前後でIssue配下19ファイルの一覧とSHA-256が完全一致し、正本・既存artifact・ADR・assuranceの追加削除または書き換えなし。
- provider↔mirror: `SKILL.md`、`openai.yaml`、skill-local template、artifact template、discussion templateの5組すべて`cmp -s` exit 0。
- 検証:
  - 新規焦点: `3 passed`
  - 既存基準: `3 passed`
  - 対象3モジュール全体: `82 passed, 5 skipped`
  - `ruff format --check`: pass（`test_wrappers.py`を機械整形後）
  - `ruff check`: pass
  - `mypy`: `Success`（3 files）
  - `git diff --check`: pass
- 安全性: `/Users`、`/Volumes`、`/home`、credential assignment、旧limit/loop authority markerはいずれも0。推奨regexの`/`検出は文中区切り文字の偽陽性と確認。
- スコープ: provider 5件、生成mirror 5件、tests 3件、親所有のIssue正本・ADR・assuranceだけ。runtime、observation、GitHub関連の変更なし。
- 完了判定: `TC-S05-001..006` pass。S90へ進行可。

## S90 影響監査と計画修正

- `validate`: `spec-dock: ok (validate) nodes=204`。
- `sync`: active unchanged、index/tree/deps/dashboard投影を正常更新。
- 現在のprovider/mirrorに旧固定回数authorityなし。テスト内の禁止marker一覧とIssue正本・履歴artifactは否定検査または履歴証拠として正当に残る。
- 発見事項: `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_105_pr_merge_preparer_content_regression_contract` が現在のproviderへ旧P0/P1/合計上限を肯定アサートしており、変更後に失敗する現行回帰契約だった。
- 判断: スコープをruntime等へ広げず、当該テストだけをS90追随テストとしてdesign/planの許可パスと検証へ追加。fresh spec review後に`dev-coder`へ委任する。
- Closure Delta: `CLOS-001`、`CLOS-002`、`CLOS-008`、`CLOS-013`の既存検証を強化。新しい要件・設計意味は追加しない。
- fresh plan amendment review: `passed`。assurance `standard / normal`、verify `ok`。
- delegated follow-up: `tests/unit/infra/test_init_update.py` の当該testだけを更新。旧固定上限・再発だけの停止を否定し、新相談/戦略/telemetry/re-analysis契約を肯定。既存hard gate assertは維持。
- follow-up verification: 対象node `1 passed`、Ruff format/check、mypy、diff-checkがpass。
- 最終S90検索の判断:
  - tests内の旧文言は否定marker一覧として正当。
  - active Issue正本は現状説明・禁止marker・検査commandとして正当。
  - 過去の`iss-00105` designは履歴証拠として正当。
  - provider/mirrorの再発文言は自動停止ではなくmandatory re-analysisを要求する新契約。
- 最終dogfooding: `validate` ok（nodes=204）、`sync` ok（active unchanged）。有効な旧固定上限authority、一般文書の競合、cross-skill要件なし。S90完了、S95へ進行可。

## 実装サマリー

固定回数と同一family再発だけを停止authorityとするPR修復契約を、fresh consultation evidence、orchestrator disposition、material strategy delta、検証・再観測に基づくsemantic continuationへ置換した。providerを正本としてskill、agent prompt、3テンプレート、生成mirror、4つの回帰テストを更新し、runtime/schema/GitHub操作は変更していない。

## 実装記録

### ステップ別観測証跡

| ステップ | 主対象 | 委任 / 所有者 | 観測結果 | 完了状態 |
|---|---|---|---|---|
| S01 | source binding / baseline | main orchestrator | HEAD・worktree・8hash・旧markerを記録、基準3 tests pass | complete |
| S02 | Red contract tests | dev-coder | 新契約欠落と旧marker残存で2 fail、runtime opaque 1 pass | complete |
| S03 | provider skill / prompt | doc-writer | fixed caps削除、consultation・semantic continuation・telemetry契約を追加 | complete |
| S04 | provider templates | doc-writer | integrated strategy、consultation、disposition、iteration ledgerを追加 | complete |
| S05 | update / parity / regression | dev-coder | 標準update、5 cmp、82 passed / 5 skipped、Ruff・mypy pass | complete |
| S90 | impact audit | main + dev-coder | 旧Issue105回帰testを発見・計画修正・Red/Green、validate/sync pass | complete |
| S95 first pass | independent reviews | spec / code / QA reviewers | fallback監査field、曖昧なrepeated-fails停止、test感度、report scaffoldをP1判定 | failed and repair started |
| S95 repair | tests / policy / projection / report | dev-coder + doc-writer + main | 強化Red 3件、provider Green、projection 5面一致、4 node・静的検査・validate/sync pass | complete; re-reviews passed |
| S99 | final verification ladder | main orchestrator | focused 4、target modules、cli_runtime 1194、static、dogfooding、parity、scopeを最終実行 | complete |

### TDD / Red・Green・Refactor証跡

| ステップ | フェーズ | 観測証跡 | 結果 |
|---|---|---|---|
| S01 | baseline | 既存焦点3件 | 3 passed |
| S02 | Red | 新marker欠落・旧stop marker残存 | 2 failed, 1 passed |
| S03/S04 | Green | provider統合後の新規焦点3件 | 3 passed |
| S05 | integration | 対象3 modules | 82 passed, 5 skipped |
| S90 | discovered Red | Issue105回帰testが旧P0 capを要求 | 1 failed |
| S90 | discovered Green | Issue105回帰testを新契約へ更新 | 1 passed |
| S95 repair | Red | 6 fallback fields、絶対停止、再利用禁止、曖昧stopを検出 | 3 failed |
| S95 repair | Green候補 | provider 4面修正後のprovider焦点 | 3 passed |
| 全体 | Refactor | test_wrappersのみRuff機械整形。一般化・runtime変更なし | pass |

### 発見されたテスト / リスク

| ID | 発見 | 対応 | 計画修正 | 状態 |
|---|---|---|---|---|
| DT-001 | Issue105 regressionが旧fixed capsを肯定 | 当該testを新semantic contractへ更新 | design/planへ許可path・S90/S99 gateを追加 | resolved |
| DT-002 | fallback audit fieldsが欠落しても焦点testsがpass | 6 fields、全状態、refresh-first、denial/expiry/reuseをassert | 既存CLOS-007/009/010の感度強化 | resolved |
| DT-003 | `repeatedly fails` がcount stopと解釈可能 | semantic strategy delta条件へ置換しforbidden assert追加 | 新要件なし | resolved |
| DT-004 | legacy append compatibilityの実動test不足 | Markdown-only/runtime opaqueと移行不要contractを既存証拠として維持 | non-blocking P2としてS95再判定対象 | open non-blocking |
| DT-005 | 旧数値上限の否定testが主に既知文字列へ依存 | 現provider/mirrorのsemantic scanとreviewで現在違反なしを確認 | future mutation-sensitivity debt。現在の契約違反なし | open non-blocking |

### Closure Coverage

| Closure | 観測証跡 | 状態 |
|---|---|---|
| CLOS-001 | provider/mirror旧fixed cap否定test・rg | pass |
| CLOS-002 | recurrence re-analysis・strategy delta assert | pass |
| CLOS-003 | consultation-before-worker順序をskill/template/testで確認 | pass |
| CLOS-004 | consultation freshness/state/binding fields | pass |
| CLOS-005 | ChatGPT advisory evidence / orchestrator disposition | pass |
| CLOS-006 | semantic continuation全gate | pass |
| CLOS-007 | refresh-first、hard-unrecoverable fallback、one-invocation audit fields | pass |
| CLOS-008 | permission/auth等hard gateとP2/P3 no-mutation assert | pass |
| CLOS-009 | generated batch consultation/disposition/iteration fields | pass |
| CLOS-010 | skill/prompt/templates意味一致と5面parity | pass |
| CLOS-011 | identity/frontmatter/update/parity/validate/sync | pass |
| CLOS-012 | runtime opaque、Markdown-only、migrationなし | pass |
| CLOS-013 | diff scopeにruntime/observation/GitHub変更なし | pass |
| CLOS-014 | approved plan、ADR、step evidence、fresh reviews | pass |
| CLOS-015 | raw conversation/secret/host path禁止scan | pass |
| CLOS-016 | single workflow slice、cross-skill expansionなし | pass |

### Workflow-Scoped Authorization

| 許可元 | repo/worktree | issue | named roles | 境界 | 期限 | 状態 |
|---|---|---|---|---|---|---|
| ユーザーのSpecDock Issue Execution依頼 | current worktree | iss-00313 | dev-coder、doc-writer、spec-reviewer、code-reviewer、qa-reviewer | active scope内のdocumented role responsibility。破壊的操作・scope expansion・外部公開・private systemは含まない | issue完了、session終了、scope変更、user revocation | active |

### Delegated Worker Evidence

| ステップ | role | 許可変更 | 検証 | 親統合判断 |
|---|---|---|---|---|
| S02 | dev-coder | tests 3 files | intended Red、baseline、Ruff、diff-check | accepted |
| S03 | doc-writer | provider skill / openai.yaml | wrapper surface、YAML、rg、diff-check | accepted |
| S04 | doc-writer | provider templates 3 files | generated tests、cmp、rg、diff-check | accepted |
| S05 | dev-coder | standard update mirrors / tests | 82 pass、5 skip、Ruff、mypy、5 cmp | accepted |
| S90 | dev-coder | Issue105 test only | Red then 1 pass、Ruff、mypy | accepted |
| S95 repair tests | dev-coder | related tests 3 files | intended 3 Red、Ruff、diff-check | accepted |
| S95 repair policy | doc-writer | provider skill + 3 templates | provider focus 3 pass、cmp、rg | accepted |
| S95 repair projection | dev-coder | standard generated mirrors | active Issue 19hash不変、5 cmp、4 node、Ruff・mypy、validate/sync | accepted |

### Parent Implementation Exception

親によるsource/test/template実装は行っていない。親の直接変更はIssue単位のrequirement、design、plan、report、ADRと観測証跡統合に限定した。

### Grade Specialist Evidence Gate

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | manual authoring fallback | used | manual-authored canonical docs、ChatGPT planning candidateのlocal integration、accepted ADR | passed | ready |

### Review History

| Gate | reviewer | state | findings / disposition |
|---|---|---|---|
| planning / Japanese docs / ADR | spec-reviewer | passed | blocking findings resolved before execution |
| S90 plan amendment | spec-reviewer | passed | discovered regression testを限定scopeへ追加 |
| S95-A first | spec-reviewer | failed | fallback fields、ambiguous stop、report scaffoldを修正 |
| S95-B first | code-reviewer | failed | fallback contractとtest sensitivityを修正 |
| S95-C first | qa-reviewer | failed | fallback scenario coverageを修正 |
| S95-A re-review | spec-reviewer | passed | P0/P1なし。P2 residual riskを記録 |
| S95-B re-review | code-reviewer | passed | P0-P3なし |
| S95-C re-review | qa-reviewer | passed | P0/P1なし。P2 residual riskを記録 |

### Reviewer Gate Status

| step | gate name | reviewer role | freshness | state | risk acceptance | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| S99 | final report review | spec-reviewer | fresh | passed | no | `execute approved plan` | P0/P1なし、CLOS-001..016閉鎖、commit ready |

### Milestone / Commit Candidate Gate

| Milestone | closure | commit state | evidence |
|---|---|---|---|
| M0-M4 | implementation integrated | uncommitted candidate | S01-S05 evidence |
| M90 | impact resolved | uncommitted candidate | S90 evidence |
| M95 | complete | eligible | fresh spec/code/QA re-reviews passed; P0/P1なし |
| M99 | local execution complete | commit eligible | final verification ladder passed; delivery evidence pending |

## 最終品質ゲート

| Gate | 現在結果 | 次アクション |
|---|---|---|
| Docs impact S90 | passed | none |
| QA S95-C | passed | P2 residual risksをS99/final reportへ保持 |
| Code review S95-B | passed | S99 final ladder |
| Spec review S95-A | passed | S99 final ladder |
| Final commit / PR | commit candidate ready | git commit、push、PR delivery、remote checks/reviews観測 |

## S99 最終品質・完了監査

| 検証段階 | コマンド / 対象 | 観測結果 |
|---|---|---|
| Focused | 新規3 node + Issue105 regression | `4 passed in 1.98s` |
| Target modules | `test_new.py`、`test_runtime_new_doc_s09.py`、`test_wrappers.py` | `82 passed, 5 skipped in 72.78s` |
| Runtime regression | `uv run pytest tests/cli_runtime` | `1119 passed, 75 skipped, 2 warnings in 1080.80s` |
| Static | Ruff format/check + mypy on 4 changed test files | all pass |
| Dogfooding | `spec-dock validate` / `spec-dock sync` | nodes=204 / active unchanged |
| Assurance | `assurance verify --issue iss-00313` | standard / normal / ok |
| Parity | provider↔mirror 5組 + artifact↔discussion | all byte-identical |
| Negative audit | old fixed caps、loop limit、曖昧repeated-fails stop | no authority-surface matches |
| Positive audit | consultation、strategy delta、fallback audit fields、telemetry、human gate | required markers present |
| Diff hygiene | `git diff --check`、status/stat/name-only | pass、tracked diff 19件 + accepted ADR 1件の計20 worktree entries。すべて許可scope内 |

`tests/cli_runtime`のwarning 2件は、duplicate ZIP entryを拒否する既存テストが意図的に発生させる`UserWarning: Duplicate name`であり、失敗ではない。skip 75件も既存の条件付きlaneで、新規テストのskipはない。

### 最終クロージャ判断

- CLOS-001..016: すべてpass。
- P0/P1: 0。
- unresolved needs-human: なし。
- 残余P2: DT-004（legacy batch appendの専用実動test不足）、DT-005（否定testのsemantic mutation感度）。現在の契約違反ではなくPR mergeabilityを妨げない。
- `.assurance.json`: source-binding SHA refreshのみ。profile、authority、complexity、schema変更なし。
- rollback: provider 5面と生成mirror 5面を同一commitで戻せる。runtime migration・既存batch変換・永続state追加なし。
- delivery readiness: commit、push、PR作成、remote checks/review観測へ進行可。

## 遭遇した問題と解決

- S90で旧fixed-cap肯定testを発見し、限定的なplan amendmentとfresh review後に更新した。
- S95でfallback監査fieldとtest感度不足をP1として検出し、Red強化後にprovider契約を修正した。
- 初回report scaffoldが観測証跡として不十分だったため、S01-S95、CLOS-001..016、委任、review statusへ置換した。
- `.assurance.json`の差分はrequirement/design/planのsource-binding SHA refreshだけであり、authorized profile、complexity tier、authority、schemaは変更していない。planの禁止対象である手動・権限変更ではなく、SpecDock assurance classifyによる必須binding更新として扱う。

## 学んだこと

- count telemetryを残す場合でも、停止authorityと明確に分離するテストが必要。
- fallbackはproseだけでなく、invocation binding・approval・consumptionを個別fieldで監査可能にする必要がある。

## 省略/例外メモ

- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Red、Green、Refactorの観測結果は「TDD / Red・Green・Refactor証跡」に記録済み。
- CLOS-001..016は「Closure Coverage」に対応付け、S95 repairとS99の結果を反映済み。
<!-- spec-dock:managed-section end id="report.step-evidence" -->
