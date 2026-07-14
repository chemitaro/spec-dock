---
種別: レポート（Epic）
ID: "epic-00312"
タイトル: "Experimental Local Workbench And Worktree Handoff"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00312 Experimental Local Workbench And Worktree Handoff — レポート（進捗 / 決定 / 結果）

> このテンプレートは observed evidence slot scaffold です。Epic の進捗、採用判断、reviewer state、blocking / next action、closure / follow-up を記録する starting shape を提供しますが、workflow / compliance authority ではありません。判断の詳細と lifecycle policy は skills / docs / accepted ADRs / reviewer gates を参照し、観測した証跡だけをこの report ledger に残します。

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - Human承認済み5-Issue分割を実行し、GitHub #315〜#318はclosed、#319/#312はopen。Issue319 S00〜S05はcommit/push済みで、local distribution/docs/full/static/manual gatesはpassした。
  - Workbench ignore/opacity、explicit scoped copy、byte-preserving Artifact import、ChatGPT-first preservation、installed consumer/manual integrationまで実装済み。S90 closureはfresh spec reviewでpassed/promote、confidence 0.99、findings 0となった。
- 次のマイルストーン:
  - Issue319 S99は`5eee0da4`でcommit/push済み、clean/upstream `0 0`。S100 Phase AでPR [#323](https://github.com/chemitaro/spec-dock/pull/323)をready/open/unmergedとして作成した。次のreport commitをfinal observation HEADとしてからUbuntu/check/review/mergeability/base driftを観測する。
- ブロッカー:
  - C319-12はfull pass。C319-09/13/14とterminal C319-15/16はS100までpendingであり、PR merge-prepared claimとIssue/Epic finishはactual observationまで不可。

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact やEpic判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | 採用（`adopted`） | 6件のuser-answer interview、baseline research、clarification synthesis | `requirement.md` の配置、非正本境界、root運用、scoped copy、merge、rollout要件 | 8件のclarification evidenceを検証し、6件の明示回答をproduct decisionとして採用。session/manifest/TTL、root bulk copy、content filtering、sync、dogfood-only実装を禁止した | `artifacts/20260712t235647z-research-workbench-clarification-baseline-and-decision-inventory.md` から `artifacts/20260713t015912z-interview-unfiltered-filesystem-copy-without-content-classification.md` | fresh requirement review |
| EAL-002 | 部分採用（`partially_adopted`） | ChatGPT 5.6 Pro GitHub-synced research | `requirement.md` の候補要件、AC、3-Issue分割seed | GitHub `main@081ba648` を参照したarchitecture分析を採用。exact CLI spelling、error名、port分割、symlink/collision/preflight/partial fieldはdesign候補へ分離し、親制約とcopy policyはhuman dispositionを優先した | `artifacts/20260713t012038z-research-chatgpt-5-6-pro-github-synced-epic-planning-analysis.md` | fresh requirement review |
| EAL-003 | 採用（`adopted`） | product-owner interview | 親 Initiative と `requirement.md` のlocal-only境界 | local-only廃止対象はInitiative/Epic/Issue等のnodeであり、Workbenchは非永続の一時fileであるとの回答で親trace blockerを解消した | `artifacts/20260713t013008z-interview-local-only-node-prohibition-and-disposable-workbench-boundary.md` | fresh `spec-reviewer` で親整合を再確認 |
| EAL-004 | 採用（`adopted`） | product-owner interview | `requirement.md` のunfiltered copy boundary | extension、language、purpose、content、filename、special-entry分類を含む独自copy対象判定を作らず、通常のfilesystem copyへ委ねる回答を採用した | `artifacts/20260713t015912z-interview-unfiltered-filesystem-copy-without-content-classification.md` | fresh `spec-reviewer` で採用済みcopy policyとの整合を再確認 |
| EAL-005 | 採用（`adopted`） | fresh `spec-reviewer` findings | requirement phase correction/promotion | 5回のfail findingを全て反映し、親node境界、unfiltered copy、WHAT/HOW分離、AC trace、report observed stateを閉じた | 6回目 fresh reviewer `sixth_review_epic_00312_requirement`、2026-07-13、`review_status: pass` | requirementをpromoteしdesign phaseへ進む |
| EAL-006 | 採用（`adopted`） | fresh design `spec-reviewer` findings | `design.md` / design promotion | Exact `.workbench` authoring source拒否、source symlink非dereference、destination ancestry containment、source Workbench missing=`no_source`/no mutationを採用。内容classifierではなくsemantic/path/CLI境界として限定し、2回目fresh reviewerで閉じた | reviewer `rereview_epic_00312_design`、2026-07-13、`review_status: pass` | designをpromoteしplan phaseへ進む |
| EAL-007 | 採用（`adopted`） | fresh plan `spec-reviewer` findings | `plan.md` | W1/W2/W3のclosure ownershipを実scopeへ合わせ、E-AC-003をW2、E-RQ-016/E-AC-009をW2 CLI surfaceとW3 docs surfaceへ分担した | reviewer `review_epic_00312_plan`、2026-07-13、`review_status: fail` | fresh plan reviewerを再実行 |
| EAL-008 | 採用（`adopted`） | fresh plan re-review finding | `requirement.md` handoff seed / `design.md` DS and AC trace | Planで発見したownership gapを上流へ戻し、E-AC-003をW2へ、E-AC-009をW2 CLI/no-syncとW3 docsへ分担した。Product requirement/design mechanismは変更していない | requirement reviewer `ownership_rereview_epic_00312_requirement`: pass、design reviewer `ownership_rereview_epic_00312_design`: pass、2026-07-13 | stale解除。Fresh plan reviewerを再実行 |
| EAL-009 | 採用（`adopted`） | fresh plan `spec-reviewer` finding | `report.md` observed state | Plan本体のownership/dependency/final quality/deferred PR/human approval/draft lifecycleは整合。Reportに上流re-passを記録してからfresh plan verdictを取得する | reviewer `third_review_epic_00312_plan`、2026-07-13、`review_status: fail` | report修正後にfresh plan reviewer |
| EAL-010 | 採用（`adopted`） | fresh plan `spec-reviewer` | `plan.md` / plan promotion | W1/W2/W3 ownership、W1→W2、W3 depends on W1+W2、W3 final quality/PR、deferred PR、human approval、draft lifecycleがreviewed requirement/designと整合した | reviewer `fourth_review_epic_00312_plan`、2026-07-13、`review_status: pass` | planをpromoteしhuman Issue decomposition approval gateへ進む |
| EAL-011 | 部分採用（`partially_adopted`） | user-proposed decision + GPT-5.6 Pro GitHub-synced research | Epic 00312 requirement/design/plan revision | Byte-preserving importを同一Epicへ統合しW3 runtime/W4 workflow/W5 final qualityへ再分割する提案を採用。Typed token/prefix reservation案はuser decisionにより棄却し、import kind + existing blank grammarへrefineした | `artifacts/20260713t023439z-decision-candidate-chatgpt-output-artifact-import-contract.md`; `artifacts/20260713t031057z-research-chatgpt-5-6-pro-artifact-import-integration-analysis.md`; transcript SHA-256 `3729ae71031219be3eb2507cd2c7da84dc3306821ebb646b39c7144dd3a1e7d5` | canonical phase refresh/fresh reviewer |
| EAL-012 | 採用（`adopted`） | product-owner interview + ADR candidate | Artifact import identity/compatibility | `chatgpt-output-*` blank prefixを予約せず、template-created blankとimport resultの両方を許容する。`chatgpt-output`はimport kind、stored fileはexisting blank grammar、provenance/authorityはEALで管理する | `artifacts/20260713t031557z-interview-chatgpt-output-prefix-coexistence-without-reservation.md`; `artifacts/20260713t031808z-adr-template-free-artifact-import-and-blank-filename-coexistence.md` | requirement reviewerでADR/requirement整合を確認し、pass後ADR acceptedへ昇格 |
| EAL-013 | 採用（`adopted`） | fresh requirement `spec-reviewer` finding | ADR/requirement byte-opacity alignment | ADR候補のUTF-8限定を削除し、single regular `.md`のopaque bytesをencoding/Markdown validationなしでcopyするrequirementへ統一した | reviewer `review_import_requirement_epic_00312`、2026-07-13、`review_status: fail` | fresh requirement reviewerを再実行 |
| EAL-014 | 採用（`adopted`） | fresh requirement `spec-reviewer` | refreshed requirement + Artifact import ADR | E-RQ-019–024/E-AC-013–016、opaque bytes、blank coexistence、5-Issue seedが整合したためrequirementをpromoteしADRをacceptedへ昇格した | reviewer `rereview_import_requirement_epic_00312`、2026-07-13、`review_status: pass` | design refresh + fresh reviewer |
| EAL-015 | 採用（`adopted`） | fresh design `spec-reviewer` | refreshed design | Import kind/blank grammar、independent use case、opaque binary publication、temp/hash/source stability/no-overwrite、workflow branch、W3/W4/W5 responsibilityがaccepted requirement/ADRと整合した | reviewer `review_import_design_epic_00312`、2026-07-13、`review_status: pass` | plan refresh + fresh reviewer |
| EAL-016 | 採用（`adopted`） | fresh plan `spec-reviewer` | refreshed 5-Issue plan | W1 foundation、W2 scoped copy、W3 import runtime、W4 preservation workflow、W5 final quality/PRのownership、dependency、deferred PR、human approval/draft lifecycleが整合した | reviewer `review_import_plan_epic_00312`、2026-07-13、`review_status: pass`; validate nodes=204 | human 5-Issue approval gate |
| EAL-017 | 採用（`adopted`） | Issue315 final report / GitHub #315 | E-RQ-001〜005、013、015、017〜018 foundation | Ignore、semantic opacity、authority isolation、delete/update preservation、provider/dogfood parityを実装・review・commit/pushしIssue closed | Issue315 C315-01〜08、final QA/code/spec gates | Issue319 final distribution evidenceへ採用済み |
| EAL-018 | 採用（`adopted`） | Issue316 final report / GitHub #316 | E-RQ-006〜012、014、016 scoped copy | Explicit same-repo linked-worktree copy、independent scope resolution、source-wins/destination-only、symlink/containment/failure transparencyを実装・review・commit/pushしIssue closed | Issue316 C316-01〜10、final QA/code/spec gates | Issue319 installed scenarioへ採用済み |
| EAL-019 | 採用（`adopted`） | Issue317 final report / GitHub #317 | E-RQ-019〜023、E-AC-013〜015 Artifact import | Single Markdown、opaque bytes、blank coexistence、collision/no-overwrite、source survival/publication safetyを実装・review・commit/pushしIssue closed | Issue317 C317-01〜11、final QA/code/spec gates | Issue319 package/manual/full evidenceへ採用済み |
| EAL-020 | 採用（`adopted`） | Issue318 final report / GitHub #318 | E-RQ-024、E-AC-016 preservation workflow | Preservation-before-adoption、EAL/canonical rewrite/fresh review、external/delegated/ZIP lane分離を実装・review・commit/pushしIssue closed | Issue318 C318-01〜11、final QA/code/spec gates | Issue319 planning/manual flowへ採用済み |
| EAL-021 | 採用（`adopted`） | Issue319 S00〜S99 reports / current repo audit | Distribution/docs/full/static/manual/Epic closure | Latest main、candidate wheel、fresh/existing consumer、dogfood parity、public docs、full/static、installed copy→import→EAL→rewrite、40-ID closureをcurrent headで実証 | Commits `7a3793de`〜`672cb23e`; S90 committed/clean; S99-QA-r1 / S99-CODE-r1 / S99-SPEC-r2 passed on `HEAD 672cb23e`; findings 0、spec confidence 0.99 | C319-12 full pass。S99 ledger commit/push/clean後S100へ進む |
| EAL-022 | 延期（`deferred`） | Issue319 S100 live GitHub gate | PR URL、Ubuntu actual run、Codex fixed review、required checks、review threads、mergeability/base drift、Issue/Epic finish | PR #323はready/open/unmergedで作成済み。External observationは未実施のため推測しない | [PR #323](https://github.com/chemitaro/spec-dock/pull/323)、pre-observation HEAD `5eee0da4` | 次のreport commitをfinal observation HEADとしてpush後、actual stateを観測しterminal evidenceへ更新する |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | Git-ignored、non-canonical、disposableな低摩擦scratchを、分類/管理systemなしで提供する | scoped copyの境界安全、failure transparency、provider/dogfood parity | 低。独自classifier/preflightをrequirementから除外し、標準copy boundaryを維持した | pass。6回目fresh requirement reviewer |
| OAL-002 | Root manual selectionとscope-local one-shot handoff、ChatGPT原文のbyte-preserving evidence保存を実consumerで成立させる | Package/update/docs/full/static/PR quality gate | 低。Version/release/migrationやroot bulk/sync/classifier/typed tokenへ拡張しない | S00〜S99 ordered full pass。S100 terminal gate pending |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Artifact import decision/research + prefix coexistence answer + ADR | product open questionなし。Import kind + blank grammar + opaque bytesをadopted | evidence/reviewer findingsをadopted/refined | passed（`rereview_import_requirement_epic_00312`） | no | promote。ADR accepted、design入力へ固定 |
| design | Refreshed requirement、accepted Artifact import ADR、GPT-5.6 research、actual Artifact runtime contracts | product open questionなし。Import kind + blank grammar + opaque bytes + binary publisher/workflow slicesを反映 | evidence/refinementsをadopted | passed（`review_import_design_epic_00312`） | no | promote。Plan入力へ固定 |
| plan | Passed refreshed requirement/design、accepted ADR、GPT-5.6 five-slice proposal | W1–W5 scope/dependency/final qualityを反映 | evidence/refinementsをadopted | passed（`review_import_plan_epic_00312`） | no | promoted。Human承認後に5 Issueを作成し、W1〜W4 closed、W5実行中 |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used。ChatGPT 5.6 ProをGitHub-synced evidence producerとして使用した。
- canonical adoption:
  - ChatGPT outputはraw research evidenceのまま保存し、main orchestratorが採否をEALへ記録してrequirementを再記述した。delegated output自体をcanonicalへ昇格していない。
- lifecycle state（契約値）:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`
- 昇格不可 state:
  - `stale`, `rejected`, `superseded`, `blocked`
- 標準出力先:
  - 対象 scope の `artifacts/` direct child にある flat Markdown
  - filename: typed artifacts use `<ts>-<type>-<slug>.md` or `<ts>-<nn>-<type>-<slug>.md`; blank artifacts use `<ts>-<slug>.md` or `<ts>-<nn>-<slug>.md`
- 軽量 provenance:
  - `created_by_role`, `scope_id`, `source_paths`, `intended_targets`, `adoption_status: unreviewed`, `reflected_to: []`, `diff_guard_result`, fallback decision, report evidence destination, adoption ledger note
  - 互換 label: role, phase, scope, authorization source, source artifacts, draft artifact path, status, integration result, rejected portions, blockers, reviewer result, promotion decision
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
| ChatGPT 5.6 Pro evidence producer | epic-00312 | `artifacts/20260713t012038z-research-chatgpt-5-6-pro-github-synced-epic-planning-analysis.md` | GitHub `chemitaro/spec-dock` `main@081ba648`、Epic clarification artifacts | Epic requirement/design/plan candidates、Issue slicing evidence | 部分採用（partially_adopted） | `requirement.md`、EAL | GitHub-sync preflight pass | orchestratorが候補を検証・再記述 | 親制約の未承認解釈、special-entry独自preflight、exact CLI/mechanismのauthority claim | なし | 5回fail findingsを反映し6回目pass | requirement promoted。design/plan候補は各phaseで別途採否・fresh review |

### 委任ドラフトの失敗モード（Delegated Draft Failure Modes）
| 失敗モード | 期待される判定 | 許可される次アクション | レポート証跡の記録先（report evidence destination） | 昇格可否 |
|---|---|---|---|---|
| ワークフロー単位の許可証跡不足（missing workflow-scoped authorization evidence） | blocked / incomplete | ワークフロー利用依頼の authorization source と boundary を記録する、または手動 authoring に戻す | ワークフロー単位の named role 許可（Workflow-Scoped Authorization） / この section | ineligible |
| 前段 reviewer pass 不足 / stale（missing/stale previous reviewer pass） | blocked / incomplete | レビューゲートを再実行する（rerun reviewer gate） | Spec Authoring Gate / reviewer evidence | ineligible |
| 設計中の要件 gap（requirement gap during design） | blocked / incomplete | requirement phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| 計画中の設計 gap（design gap during plan） | blocked / incomplete | design phase へ戻す | 判断台帳 / ゲート証跡（decision ledger / gate evidence） | ineligible |
| ロール利用不可（role unavailable） | blocked / manual path | 利用不可を記録し、妥当なら手動で続行する | この section | ineligible |
| 禁止行為の試行（forbidden action attempt） | rejected | ドラフトを破棄し incident を記録する | この section / decision ledger | ineligible |
| 古いドラフト（stale draft） | stale | 再生成または差分調整する | この section | ineligible |
| 置換済みドラフト（superseded draft） | superseded | 置換先ドラフトを参照する | この section | ineligible |
| 委任使用主張に対する証跡不足（missing draft evidence when delegated use is claimed） | incomplete | 証跡を追加する、または委任使用 claim を外す | この section | ineligible |
| reviewer 利用不可 / 拒否 / waiver / provisional（reviewer unavailable/denied/waived/provisional） | blocked / incomplete | fresh な passed reviewer を取得する、または昇格なしの risk acceptance を記録する | レビューゲート証跡（reviewer gate evidence） | ineligible |

## 決定事項（ADRリンク） (必須)
- `adr-20260713t031808z-template-free-artifact-import-and-blank-filename-coexistence`: `chatgpt-output`をimport kindとして扱い、template/frontmatterなしのblank naming/collision grammarと共存させるaccepted decision。

## 完了した Issue / PR / Release (必須)
- `iss-00315` / GitHub #315: closed。Workbench ignore/opacity/delete/update foundation。
- `iss-00316` / GitHub #316: closed。Explicit scoped Workbench copy/source-wins handoff。
- `iss-00317` / GitHub #317: closed。Byte-preserving `chatgpt-output` Artifact import。
- `iss-00318` / GitHub #318: closed。ChatGPT-first preservation/EAL/canonical rewrite workflow。
- `iss-00319` / GitHub #319: open。S00〜S99 committed/pushed。S100 Phase A complete、external observation pending。
- Epic GitHub #312: open。Issue319 terminal delivery後にclose判断する。
- PR: [#323](https://github.com/chemitaro/spec-dock/pull/323) ready/open/unmerged。Ubuntu provider-tests、Codex fixed review、required checks、review threads、mergeability、base driftは未観測であり、推測しない。

## Requirement / Acceptance content-free closure mapping（必須）

| Explicit IDs | Current status | Content-free evidence / remaining gate |
|---|---|---|
| E-RQ-001, E-RQ-002, E-RQ-003, E-RQ-004, E-RQ-005 | implemented / locally verified | Issue315 final closure、Issue319 fresh/update/dogfood inventory。Git-ignored、root/scoped placement、semantic opacity、authority isolation |
| E-RQ-006, E-RQ-007, E-RQ-008, E-RQ-009, E-RQ-010, E-RQ-011, E-RQ-012 | implemented / locally verified | Issue316 final closure、Issue319 S05。Explicit scoped copy、root exclusion、independent resolution、opaque complete content、source-wins、safety/content-free failure |
| E-RQ-013, E-RQ-014, E-RQ-015, E-RQ-016, E-RQ-017, E-RQ-018 | implemented / locally verified | Issue315/316 closure、S02/S03 update/parity/docs。Minimal surface、no sync、disposable、experimental、provider-first、update preservation |
| E-RQ-019, E-RQ-020, E-RQ-021, E-RQ-022, E-RQ-023, E-RQ-024 | implemented / locally verified | Issue317/318 closure、S05 two imports/EAL/rewrite。Explicit import、approved source、byte identity、blank collision/no-overwrite、publication safety、authority checkpoint |
| E-AC-001, E-AC-002, E-AC-003, E-AC-004 | local pass | Issue315/316 focused closure、S02/S05 installed evidence。Ignore matrix、opaque traversal、root separation、explicit handoff |
| E-AC-005, E-AC-006, E-AC-007, E-AC-008 | local pass | Issue316 final testsとS05。Target/scope resolution、merge contract、content opacity、failure transparency |
| E-AC-009, E-AC-010, E-AC-011, E-AC-012 | local final gate passed; S100 terminal delivery pending for E-AC-012 | No lifecycle/sync、delete、update/parityはIssue315/316/S02/S03でpass。Final local full/static/manualはS04/S05 pass。S99 QA/code/spec r2 ordered full pass |
| E-AC-013, E-AC-014, E-AC-015, E-AC-016 | local pass; S100 delivery observation pending | Issue317/318 final closure、S05 source/hash/no-overwrite/EAL/rewrite。PR Ubuntu actual runとterminal authority claimだけS100 pending |

## ドキュメント影響（Docs Impact）

| Surface | Disposition | Evidence |
|---|---|---|
| Root README / public provider and dogfood docs | updated | S03 `da59f73c`、provider-first candidate-wheel projection、7 exact pairs、fresh spec pass |
| Runtime help / installed skills / agent config | updated and distributed | Issue315〜318 provider authority、S02 wheel-only fresh/update、provider/dogfood parity |
| Rules/templates/migration/version/`uv.lock` | verified-no-op | Current contractで追加変更の必要性なし。S00/S02/S03/S90 audit |

## リスク台帳（Risk Ledger）

| Risk | State | Blocking boundary | Next action |
|---|---|---|---|
| PR Ubuntu actual run / Codex fixed review / required checks / review threads / mergeability / base drift未観測 | pending | PR作成は完了。Merge-prepared/Issue/Epic finish blocking | 次のreport commitをfinal observation HEADとしてpush後に観測・repairする |
| Byte-preserved raw Artifactの既存trailing whitespace | accepted nonblocking | 原文不変契約により修正しない。Product/runtime差分ではない | Terminal reviewで既知例外として維持 |
| sdist `SOURCES.txt`にcache path文字列が残るがarchive memberは0 | accepted nonblocking | Candidate/sdist再build wheelにcache member 0。Consumer behavior影響なし | Packaging contract変更時に再評価 |
| Scope expansion | closed by contract | Version/lock/migration/new deps/root bulk/sync/classifier/typed tokenはnon-goal | Material necessity発見時だけ新規decision/reviewへ戻す |

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - Candidate wheelによるfresh init、pre-feature existing update、dogfood projection、installed manual scenarioまでlocal pass。
- 監視値（エラー率/レイテンシなど）:
  - Runtime service rolloutは対象外。Test/pass countsとcontent-free hashesはIssue319 reportが保持する。
- 障害/アラート:
  - なし。PR/CI external observationは未実施。

## フォローアップ（別Issue化） (必須)
- 新規follow-up Issueなし。残作業は既存`iss-00319`のS100 report commit/push、PR #323のUbuntu/CI/Codex review/thread/mergeability/base drift観測、finishである。
- PR mergeはuser明示指示なしに行わない。

## 省略/例外メモ (必須)
- S90はfresh spec-reviewer passed/promote後、`672cb23e`でcommit/push/clean済み。S99 QA/code/spec r2もpassed/promoteし、C319-12はfull pass。S100前のterminal項目とEpic completionはself-passしない。
- EAL-022だけがdeferred。S100 Phase Aは完了したがexternal observationとterminal closureは未完了であり、no-merge契約を維持する。
