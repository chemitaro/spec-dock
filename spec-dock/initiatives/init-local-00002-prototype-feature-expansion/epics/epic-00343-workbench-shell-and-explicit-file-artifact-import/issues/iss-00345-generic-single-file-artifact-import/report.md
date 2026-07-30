---
種別: 実装報告書（Issue）
ID: "iss-00345"
タイトル: "Generic Single File Artifact Import"
関連GitHub: ["#345"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00343", "init-local-00002"]
---

# iss-00345 Generic Single File Artifact Import — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | interpretation | orchestrator / ChatGPT authoring evidence | runtime guidance の `authorized_profile=strict` と親 Epic の `critical` 推奨が一致しない | 本文で一方を選択する; 差分を未解決入力として保持する | 本 Issue 文書は authority を変更せず、`strict` を観測値、`critical` を高リスク設計入力として併記する | assurance classification は runtime-owned であり、ChatGPT生成物や本文が変更してはならない。一方、filename identity、外部 path privacy、no-overwrite publication、retry disposition は `critical` 相当の検討密度を必要とする | applied | `artifacts/20260730t000929z-01-disc-issue-345-clarification-chatgpt-authoring-handoff.md`; ChatGPT Pro authoring pack | fresh review後に runtime-owned classification を実行する |
| D-002 | resolved | scope | ChatGPT Pro requirement review | `I345-AC-010` がsource raceをcommit直前まで無条件に検知すると読め、親 Epic D-008のthreat-model除外を越えていた | ACを維持; 観測可能期間と除外窓を明示 | stagingから最終source検証までを保証し、その後の非協調的same-inode writeと最終check後のdestination-parent replacementを除外する。staged-byte integrity/no-overwrite/commit-state保証は維持する | 親設計と現publisherの観測境界に一致させるため | applied | ChatGPT Pro fresh requirement review at `b96b8b8ad9a362d3c8a97cea899e7cadc218a439`; `requirement.md` I345-AC-010 | corrected requirementを再レビュー |
| D-003 | resolved | compatibility | ChatGPT Pro requirement review | rollout後にgeneric parserまでrevertすると、保持したgeneric Markdownがmalformedとなりvalidate/sync互換を失う | 全面revertのみ; pre/post rolloutを分離 | データ生成前は全面revert可。生成後はwrite pathを停止できるが、recognizer、validation/sync、semantic opacity、shared-slot reservationを互換層として残す | accepted ADRのgrandfathered evidence保持とruntime validator事実を同時に満たすため | applied | ChatGPT Pro fresh requirement review at `b96b8b8ad9a362d3c8a97cea899e7cadc218a439`; `requirement.md` §15 | corrected requirementを再レビュー |
| D-004 | resolved | operation | SpecDock assurance runtime | classify前のstrict-legacy観測、親Epicのcritical推奨、adaptive classify結果が異なる | 文書でcriticalへ上書き; runtime結果を採用し推奨を設計入力として保持 | `assurance classify --stage requirement` の `standard / normal` をauthorized profileとして採用し、unknown risk factsと親critical推奨はレビュー重点として残す | profile authorityはruntime contractにあり、ChatGPT案や親推奨はclassificationを直接変更しない | applied | `.assurance.json`; `assurance verify` status `valid`; hard triggers `[]` | design/planはStandard templateを基底にし、high-risk詳細を削らずfresh review |
| D-005 | resolved | implementation | ChatGPT Pro design review | source preflightをsetup前に要求するがapplication portが未宣言 | publisher private method利用; explicit guard port追加 | `ExplicitFileSourceGuard`とopaque guarded-source contractを宣言し、publisherはraw pathでなくguarded handleをconsumeする | layered architectureとpre-setup eligibility boundaryを同時に満たすため | promoted_to_design | `design.md` §§4.3, 4.4, 4.7, 4.9 | corrected designを再レビュー |
| D-006 | resolved | compatibility | ChatGPT Pro design review | command catch-allがcommit後のunknown exceptionも`not_committed`へ誤分類し得た | catch-all維持; phase-aware finalizer | commandはstateを推測せず、application/publisher finalizerがpre/post commitを分ける。commit後handled faultはidentity付きwarning/success/retry-not-needed | duplicate retryとstate invariant破壊を防ぐため | promoted_to_design | `design.md` §§4.2, 5.2, 7 | corrected designを再レビュー |
| D-007 | resolved | compatibility | ChatGPT Pro design review | design rollbackがreview済みrequirementのpre/post rollout分離を反映していなかった | parser/ledger全面revert; compatibility層保持 | pre-rolloutのみ全面revert、post-rolloutはwrite disable + recognizer/lifecycle exclusion/shared-slot reservation保持 | grandfathered evidenceのvalidate/sync互換を守るため | promoted_to_design | `design.md` §15 | corrected designを再レビュー |
| D-008 | resolved | implementation | ChatGPT Pro design review | setup作成後にslot exhaustionを検知するとmutation-free failure違反 | existing helper順序を維持; preflight/apply分離 | read-only setup preflight→ledger scan/allocation→setup apply→再検証→publishの順にする | exhaustion/corrupt ledgerでfresh setupを変更しないため | promoted_to_design | `design.md` §§4.4, 4.5, 5.1, 5.2, 12 | corrected designを再レビュー |
| D-009 | resolved | implementation | ChatGPT Pro design re-review | guarded sourceをpublisherがconsumeするとdestination race retry時のFD ownership/closeが不明 | one-shot consume; application-owned lease | applicationがretry loop全体でleaseを所有し、publisherはrewind/borrow、全exitで一度だけclose | source identity維持とresource leak/double-close防止を両立するため | promoted_to_design | `design.md` §§4.3, 4.4, 4.7, 12 | corrected designを再レビュー |
| D-010 | resolved | scope | ChatGPT Pro design re-review | 任意post-commit faultをwarning化する記述がaccepted warning allowlistを越えた | generic warning追加; three-seam限定 | directory fsync、owned-temp cleanup、lock releaseだけをexact codeへmappingし、他のresult fieldsはpre-commit構築 | public contract発明と誤retryを防ぐため | promoted_to_design | `design.md` §§4.2, 5.2, 7.2, 12 | corrected designを再レビュー |
| D-011 | resolved | implementation | ChatGPT Pro design re-review | fresh targetで未作成artifacts directoryから`PC_NAME_MAX`を取得できない | setup先行; parent FD tentative + child FD verify | opened target parent FDでtentative limitを取得し、作成後artifacts FDでidentity/limitを再確認。取得不能/不一致はfail closed | mutation-free preflight順序とplatform limit検証を両立するため | promoted_to_design | `design.md` LC-345-010, §§4.5, 5.2, 12 | corrected designを再レビュー |
| D-012 | resolved | implementation | ChatGPT Pro design final re-review | symlinkだけをpre-open拒否しblocking `O_RDONLY`するとFIFO direct/raceで停止し得る | fstat後拒否のみ; pre-lstat + nonblocking acquisition | 全non-regularをpre-open拒否し、`O_NONBLOCK`相当のrace-safe acquisition後にfstat/path identityを最終判定する | required special-file rejectionをhangなしで満たすため | promoted_to_design | `design.md` §4.7, T345-3 | corrected designを再レビュー |
| D-013 | resolved | compatibility | ChatGPT Pro design final re-review | commit後のsource/temp/parent FD close例外がcommitted resultを潰し得る | public warning追加; no-throw resource finalization | descriptor ownership/close時点を固定し、不可避なpost-commit closeはno-throw、internal evidenceのみ。public warning/stateは不変 | honest commit stateとwarning allowlistを守りduplicate retryを防ぐため | promoted_to_design | `design.md` §§4.2, 4.7, 7.2, T345-3 | corrected designを再レビュー |
| D-014 | resolved | compatibility | ChatGPT Pro design pass review | destination raceの先行attemptでretained tempが生じた場合の最終cleanup state集約が未定義 | 最終attemptのみ; monotonic merge | 全attemptを`retained > removed > not_created`でmergeし、後続commitはwarning、最終failureはretained stateを保持 | honest cleanup stateと既存provider retry semanticsを守るため | promoted_to_design | `design.md` §4.4, T345-2 | combined final spec review |
| D-015 | resolved | compatibility | ChatGPT Pro design pass review | POSIXでもbackslashを無条件置換しminimal normalizationを越えていた | cross-platform一律置換; platform-aware | 実platform separator/alternate separator/reserved-invalidだけを置換し、Linux/macOSではbackslashを保持 | accepted ADR Decision 4のoriginal basename最大保持を満たすため | promoted_to_design | `design.md` §4.6, T345-1 | combined final spec review |
| D-016 | resolved | test-strategy | ChatGPT Pro combined R/D/P review | root rulesのprovider sourceをS90まで作らない計画ではS01のroot target成功契約を満たせない | S90で初作成; S01で最小source作成 | S01でroot rulesの最小provider sourceを作成し、S90は説明完成・install/update parityへ限定する | root targetのvertical sliceをS01単体でGreenにするため | promoted_to_plan | `plan.md` S01, S90; combined review at `cdbb5fccd36d6864f9e76fbf479765ac31001c99` | combined fresh re-review |
| D-017 | resolved | compatibility | ChatGPT Pro combined R/D/P review | S99の全面revert試験がgeneric data生成後のrecognizer互換を壊す | 単一revert; pre/post rollout分離 | pre-rolloutは全面revert、post-rolloutはwrite-disableしrecognizer/validate/sync/body-open/shared-slot/file不変を検証する | requirement/designのgrandfathered evidence互換とplan closureを一致させるため | promoted_to_plan | `plan.md` `tc-s99-002`; combined review at `cdbb5fccd36d6864f9e76fbf479765ac31001c99` | combined fresh re-review |
| D-018 | resolved | operation | ChatGPT Pro combined R/D/P review | requirement/design metadataが旧strict/pendingのままruntime standardと矛盾した | 旧観測値を維持; runtime値へ同期 | requirement/design/planのmetadataと本文を`standard / runtime_classified`へ同期し、親critical推奨はreview focusとして保持する | `.assurance.json`をauthorityとするため | applied | `.assurance.json`; requirement/design/plan front matter; combined review at `cdbb5fccd36d6864f9e76fbf479765ac31001c99` | assurance rebind後にcombined fresh re-review |
| D-019 | resolved | test-strategy | ChatGPT Pro combined R/D/P review | four-target acceptanceに対して成功・拒否matrixがroot/Issueへ偏っていた | root/Issue代表のみ; 4 kind parameterization | root / Initiative / Epic / Issue全成功と、各kindのmissing/mismatch mutation-free拒否をS01で固定する | acceptance criteriaの対象集合をtest closureへ完全投影するため | promoted_to_plan | `plan.md` S01 `tc-s01-004`; combined review at `cdbb5fccd36d6864f9e76fbf479765ac31001c99` | combined fresh re-review |
| D-020 | resolved | compatibility | ChatGPT Pro combined R/D/P review | 動的text fieldに改行/control/bidi/token injectionの境界がなかった | human-readable raw text; reversible one-line quoting | 動的stringをASCII-safeなJSON string literal相当で一行escapeし、JSONは標準escapingを使う。privacyとround-tripをexact testする | CLI構造とログ一行性を保ちつつ任意basenameを可逆表示するため | promoted_to_design | `requirement.md` I345-RQ-010/I345-AC-013; `design.md` §4.8; `plan.md` `tc-s02-010`; combined review at `cdbb5fccd36d6864f9e76fbf479765ac31001c99` | combined fresh re-review |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | clarification research / discussion | canonical `requirement.md`, `design.md`, `plan.md` | source-grounding と利用者判断を、任意の単一ファイル、明示 target、generic identity、Workbench非依存、Issue 346境界として採用する | `artifacts/20260730t000929z-research-issue-345-generic-file-import-source-grounding.md`; `artifacts/20260730t000929z-01-disc-issue-345-clarification-chatgpt-authoring-handoff.md` | ChatGPT案との照合後に正本へ反映し fresh review |
| EAL-002 | adopted | ChatGPT Pro authoring / repository analysis / combined review | canonical `requirement.md`, `design.md`, `plan.md`; onboarding artifact | 4文書の構造、trace、failure/privacy/test設計を採用し、repository誤記とD-002〜D-020のレビュー指摘を補正した。exact commitへのfresh combined reviewがfindings `[]`で合格した | original ZIP SHA-256 `4c3317e697b7fe68b91bfc04401f36b8407b20631460b8ee4199ebf2c4d20eba`; corrected authoring-pack content digest `4da06f4a19034d6dcf8d0d24550298604a97096c1f2d18d56473297ad76ff573`; final review at `3a2e95b57154108aea260325d5c40829b01ccf4a`; reviewed ZIP SHA-256 `8ac851843f89f04b6403e9594876435ca4b5defa3587557202145afee3566a85` | planning artifactsを実装入力として使用可能 |
| EAL-003 | rejected | transport-safe repaired pack | canonical prose | ZIP transport validator通過のための可逆HTML数値参照表現は意味内容ではなく搬送上の符号化であり、正本本文には不自然である | corrected authoring-pack provenance の round-trip 記録 | 原文候補を正本へ採用し、digest付きZIPは生成証跡として保持 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | 任意の readable regular file 一件を、root / Initiative / Epic / Issue の明示 targetへopaqueかつno-overwriteで保存する契約 | 新メンバー向け説明資料、PlantUML、ZIP形式のChatGPT生成物 | low | ChatGPT Pro fresh combined review `pass` at `3a2e95b57154108aea260325d5c40829b01ccf4a` |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | active Issue / parent Epic R/D/P / accepted ADR / provider source / existing tests / clarification artifacts / ChatGPT Pro draft | 利用者確認事項なし。runtime-owned assuranceはstandard、親critical推奨はreview focus | adopted | fresh combined review passed at `3a2e95b57154108aea260325d5c40829b01ccf4a`（findings `[]`） | no | requirement phase promoted |
| design | passed requirement / Standard assurance template / provider layered architecture / existing publisher・allocator・parser / ChatGPT Pro draft | D-005〜D-015/D-018/D-020を反映し、runtime profileはstandard | adopted | fresh combined review passed at `3a2e95b57154108aea260325d5c40829b01ccf4a`（findings `[]`） | no | design phase promoted |
| plan | passed requirement / corrected canonical design / Standard assurance template / current test surfaces / Issue 346 ownership / ChatGPT Pro draft | repository誤記とD-005〜D-020由来test obligationsを補正済み | adopted | fresh combined review passed at `3a2e95b57154108aea260325d5c40829b01ccf4a`（findings `[]`） | no | plan phase promoted; implementation planning input ready |

### ChatGPT Pro 統合再レビュー証跡

- Session: `iss-00345-final-reviewed-pack`
- 対象commit: `3a2e95b57154108aea260325d5c40829b01ccf4a`
- Model evidence: `requested=Pro`, `resolved=Pro`, `verified=yes`
- 判定: `pass`
- 前回5指摘: `previous_findings_resolved=true`
- Findings: `[]`
- Review Markdown artifact: `artifacts/20260730t054439z-chatgpt-output-combined-final-rereview.md`
- Review Markdown SHA-256: `2219d397d4d8b957d9821777cd53fa5bb32e37e6f245d1fc13f3f54fd03395ca`
- Reviewed ZIP: `iss-00345-generic-single-file-artifact-import-reviewed-spec-pack.zip`
- ZIP SHA-256: `8ac851843f89f04b6403e9594876435ca4b5defa3587557202145afee3566a85`
- ZIP validation: compressed data errorなし、exact 4 Markdown entries、展開後の各fileはcanonical requirement/design/plan/onboardingとbyte-for-byte一致

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used（ChatGPT Use / Pro）
- 未使用の場合:
  - manual authoring path / 委任ドラフトを昇格証跡として使っていない理由。
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
| ChatGPT Pro | iss-00345 | authoring ZIP内 `requirement.md`, `design.md`, `plan.md`, `onboarding.md` | active Issue/Epic、accepted ADR、provider source、tests、clarification artifacts | canonical R/D/P、Issue onboarding artifact | adopted | `requirement.md`, `design.md`, `plan.md`, `artifacts/20260730t014107z-issue-345-generic-single-file-artifact-import-onboarding-guide.md` | source-grounding review + pack review + exact-commit combined re-review pass | repository補正とD-002〜D-020を反映して統合 | transport-only encoded spellings、誤ったtest/CLI/path表現 | none | ChatGPT Pro pass at `3a2e95b57154108aea260325d5c40829b01ccf4a` | requirement/design/plan promoted |

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

### セッションログ（2026-07-29 HH:MM - HH:MM）

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
| ワークフロー利用依頼 / 明示承認 / なし（user request to use SpecDock workflow / explicit approval / none） | ... | iss-00345 | 現在セッション（current session） / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | 範囲: active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility。破壊的操作 / 外部公開 / credentialed external mutation / scope expansion / private external system use / out-of-workflow role は含めない | 完了 / セッション終了 / scope 変更 / host policy conflict / user revocation（issue complete / session end / scope change / host policy conflict / user revocation） | none / denied / unavailable / host conflict | 続行 / separate-confirmation exception は user に確認 / block gate / record waiver request |

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

### セッションログ（2026-07-29 HH:MM - HH:MM）

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
| ChatGPT Pro（spec-reviewer相当） | planning phaseのrequirement / design / plan / onboarding alignment | 前回P1×2/P2×3を修正し、fresh combined re-review findings `[]` | 1 | pass at `3a2e95b57154108aea260325d5c40829b01ccf4a` |

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
