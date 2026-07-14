---
種別: 実装報告書（Issue）
ID: "iss-00318"
タイトル: "ChatGPT First Preservation Workflow And Skill Integration"
関連GitHub: ["#318"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00312", "init-local-00003"]
---

# iss-00318 ChatGPT First Preservation Workflow And Skill Integration — 実装報告

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger）

| ID | Status | Type | Raised By | Gap | Options | Decision | Rationale | Disposition | Evidence | Follow-up |
|---|---|---|---|---|---|---|---|---|---|---|
| D-318-001 | resolved | scope | ChatGPT 5.6 Pro / repo-analyst | External raw importとdelegated draft provenanceが衝突し得る | 同一lane; parallel lane; delegated guard緩和 | External imported evidenceとdelegated draftをparallel evidence laneとして分離し、existing delegated guardを維持 | Byte preservationとdelegated provenanceの両方を満たす最小境界 | applied | Parent DS-004、Issue317 S90 relay、ChatGPT complete received answer。Requirement RQ-318-007–008へ反映 | Requirement pass後、Designでauthority/validation flowを固定 |
| D-318-002 | resolved | compatibility | system-architect | `committed=true` warningのcheckpoint扱い | block; pass-with-warning; retry | Final path/hash/bytesが確定する`committed=true`は保存済みwarningとして記録し、自動retryしない | Issue317 post-publish semanticsと重複回避に整合 | applied | Issue317 requirement/design/report、specialist evidence。Requirement RQ-318-006へ反映 | Requirement pass後、Design failure matrixへ反映 |
| D-318-003 | resolved | scope | orchestrator | Parent Standard候補とruntime strict guidance | Standard固定; strict自己宣言; assurance authority | Epic候補gradeをauthorityにせずrequirement後のassurance classifyを正とする。取得済みstrict相当evidenceは維持 | Profile偽装を避け、runtime authorityに従う | applied | Parent W4、guidance issue-planning。Requirement Grade節へ反映 | Requirement passとAssurance後、planへ反映 |
| D-318-004 | resolved | ownership | repo-analyst / orchestrator | Public/package/final quality/PR surfaceをIssue318で先行するかIssue319へrelayするか | Issue318へ拡張; no-op; W5へdefer | Root/public/migration/package/fresh init-update/full-global/final QA-code-spec/PR deliveryはIssue319へdeferし、Issue318はworkflow/skill integrationで閉じる | Parent DS-005/W5とapproved Issue318 non-scopeに一致し、one final Epic PR境界を維持 | applied | S90 24-path inventory、runtime/deferred surface diff確認 | Issue319 bundled planningでcanonical採用しfresh reviewする |

## 証跡採用台帳（Evidence Adoption Ledger）

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-318-001 | partially_adopted | ChatGPT 5.6 Pro GitHub-synced complete received answer | external ChatGPT 5.6 Pro | 四分岐、shared checkpoint、lane分離、failure/EAL/Issue319 relay候補 | requirement.md / design.md / plan.md / report.md | Requirement RQ/AC、Design DS-318-001–009・§4–14、Plan §2–10、EPE-318-001 | 親/ADR/local sourceと一致する候補だけを採用し、unverified pass claim、profile自己宣言、実在しないtest selectorは不採用。Planでは実在test surfaceへ補正 | advisory analysis + byte-verified preserved evidence | `artifacts/20260713t180812z-chatgpt-output-issue-318-chatgpt-5-6-pro-planning-report.md`; EPE-318-001 | main orchestrator | requirement r13 passed; design r3 passed; plan r4 passed | no, planning adoption reviewed | S00からapproved planを順番に実行 |
| EAL-318-002 | adopted | current-state analysis | repo-analyst | Exact 14 provider/dogfood paths、Issue317 drift、test surfaces、Issue319 ownership | requirement.md / report.md | Scope、RQ-318-010–013、Deferred PR Delivery Gate | Current checkoutのlocal sourceで直接確認済み | source-grounded read-only repository analysis | Active Epic/Issue317 docs、current provider assets/tests | main orchestrator | PLANNING-REQ-r13 passed | no, entry resolved | Requirement pass後、design/plan intended targetへ必要事項を段階統合 |
| EAL-318-003 | partially_adopted | fresh architecture analysis | system-architect `gpt-5.6-sol`/medium | Shared kernel、parallel lane、authority/failure/rollback候補 | requirement.md / design.md / report.md | RQ-318-006–012、D-318-001–002、DS-318-001–009 | Parent/ADRに整合する設計前提を採用し、runtime拡張案は不採用 | specialist advisory + local-source grounded | Fresh read-only specialist run | main orchestrator | requirement r13 passed; design r3 passed | no, design evidence integrated | Plan handoffで固定設計contractを維持 |
| EAL-318-004 | adopted | fresh implementation planning analysis | implementation-planner `gpt-5.6-sol`/medium | Step/closure/test/delegation seed | plan.md / report.md | Plan §2–10、Grade Specialist Evidence Gate | Approved designを維持するS00–S99順序、C318 closure、role/test/review/commit gateへ統合し、r1–r2 findingsを具体化 | specialist advisory + local-source grounded | Fresh read-only specialist run | main orchestrator | requirement r13 passed; design r3 passed; plan r4 passed | no, planning adoption reviewed | S00からapproved planを順番に実行 |
| EAL-318-005 | rejected | implementation expansion candidates | external ChatGPT 5.6 Pro | Typed token、frontmatter/sidecar、自動EAL/canonical mutation、ZIP単一import、runtime status追加 | none | none | 親Epic、accepted ADR、Issue318 non-scopeに反する | advisory claim rejected by canonical authority | EAL-318-001 complete received answer、accepted ADR | main orchestrator | PLANNING-REQ-r13 passed | no | no_action; rejected claimを後続へ持ち込まない |
| EAL-318-006 | deferred | S90 relay | Issue317 / Epic W5 | README/reference/migration/package/fresh init/update/full/global gate/final PR | iss-00319 | Issue319 requirement/design/plan | W5所有でありIssue318完了をblockしない。RevisitはIssue319開始時 | accepted parent/previous-Issue relay | Issue317 report S90、Epic plan W5 | main orchestrator | PLANNING-REQ-r13 passed | no, scope-owned deferral | Issue319開始時に再確認 |
| EAL-318-007 | adopted | S05 standalone synthetic Markdown | operational dogfood evidence | Complete standalone sourceがbyte exact importされsourceも残る | report.md | Step Evidence S05 / EPE-318-002 | Synthetic body自体はcanonical採用せず、preservation動作の検証claimだけを採用 | direct receipt + hash/byte/cmp | `artifacts/20260714t094952z-chatgpt-output-issue-318-s05-standalone.md`; EPE-318-002 | main orchestrator | EXEC-S05-SPEC-r1 passed | no, committed receipt verified | Safe Artifactとreportをfocused commit |
| EAL-318-008 | adopted | S05 complete received synthetic inline answer | operational dogfood evidence | Complete received textが無編集capture/importされprovider-original byte claimをしない | report.md | Step Evidence S05 / EPE-318-003 | Synthetic body自体はcanonical採用せず、capture boundaryとpreservation動作の検証claimだけを採用 | direct receipt + hash/byte/cmp | `artifacts/20260714t094952z-01-chatgpt-output-issue-318-s05-inline.md`; EPE-318-003 | main orchestrator | EXEC-S05-SPEC-r1 passed | no, committed receipt verified | Safe Artifactとreportをfocused commit |
| EAL-318-009 | adopted | S05 unavailable / ZIP / eligibility failure scenarios | operational dogfood evidence | Genuine unavailable exception field、existing ZIP lane、failed import blockを観測 | report.md | Step Evidence S05 / EPE-318-004 | 保存不能を成功扱いせず、synthetic validation claimだけを採用 | direct exception/exit/inventory/canonical-hash evidence | EPE-318-004、57 ZIP tests、`source_ineligible` receipt | main orchestrator | EXEC-S05-SPEC-r1 passed | no, failure correctly blocked | Safe Artifactとreportをfocused commit |

## 外部原文保存証跡（External Preserved Evidence）

| field | value |
|---|---|
| Record ID | `EPE-318-001` |
| output_form | complete received ChatGPT Markdown report |
| preservation_status | `captured_received_text` |
| capture_boundary | Oracle validated wrapperの`## Answer`直後からEOFまでの受信回答を文字追加・削除・整形なしで機械的にcaptureし、Issue Workbench sourceからimported Artifactまで同一bytes。Provider内部original bytesは境界外 |
| import_kind | `chatgpt-output` |
| storage_identity | `blank` |
| source | `.workbench/chatgpt-5-6-pro-issue318-complete-report.md`（Issue root相対） |
| destination | `artifacts/20260713t180812z-chatgpt-output-issue-318-chatgpt-5-6-pro-planning-report.md`（Issue root相対） |
| SHA-256 | `62fd3fe23b1c69571e3f04f94326994e42381204d1c8a6d54aa3e6446c1ed85e` |
| byte_count | `67335` |
| committed / warning | `true` / none。Source remains、source/destination SHA-256・byte count一致、`cmp` pass、`cleanup_state=removed`、content-free receipt、validate nodes=209 |
| adoption_status | `partially_adopted` |
| rationale | 四分岐、shared checkpoint、lane分離、failure/EAL/Issue319 relayを採用し、exact test名、unverified pass claim、profile自己宣言はauthority化しない |
| adopter | main orchestrator |
| reviewer_status | PLANNING-REQ-r13 / PLANNING-DES-r3 / PLANNING-PLAN-r4 `passed`、plan findingsなし、confidence 0.99 |
| blocking | no。Requirement/design/planの各fresh reviewを通過 |
| next_action | Assuranceをapproved planへ再bindし、S00から実行する |

このrecordはexternal evidence laneであり、delegated draft lifecycle、frontmatter、diff guardを適用しない。Body、secret-like value、absolute host pathは記録しない。

### EPE-318-002 — S05 standalone synthetic preservation

| field | value |
|---|---|
| output_form | complete standalone Markdown |
| preservation_status | `imported_byte_exact` |
| capture_boundary | Issue Workbench sourceからimported Artifactまで。Synthetic bodyはcanonicalへ採用しない |
| import_kind / storage_identity | `chatgpt-output` / `blank` |
| source / destination | `.workbench/issue318-s05-standalone.md` / `artifacts/20260714t094952z-chatgpt-output-issue-318-s05-standalone.md`（Issue root相対） |
| SHA-256 / byte_count | `cd231b9d3b26b5d55d1a9a9e78ca5fff5bdf78a4585a73d5147ad7569af96194` / `199` |
| committed / warning | `true` / none。Source survives、hash/bytes/`cmp`一致、`cleanup_state=removed` |
| adoption_status | `adopted` for operational validation claim only; synthetic body is evidence-only |
| adopter / reviewer_status | main orchestrator / EXEC-S05-SPEC-r1 passed |
| blocking / next_action | no / Fresh S05 review後にsafe Artifactとreportをcommit |

### EPE-318-003 — S05 complete received inline preservation

| field | value |
|---|---|
| output_form | complete received inline answer |
| preservation_status | `captured_received_text` |
| capture_boundary | Complete synthetic answer bodyを追加・削除・整形せずWorkbenchへcaptureし、imported Artifactまで同一bytes。Provider-original bytesは主張しない |
| import_kind / storage_identity | `chatgpt-output` / `blank` |
| source / destination | `.workbench/issue318-s05-inline.md` / `artifacts/20260714t094952z-01-chatgpt-output-issue-318-s05-inline.md`（Issue root相対） |
| SHA-256 / byte_count | `91e54f4f45545cc39a9fef8c6a288548f7484e09df86b48198774ac71d65af5a` / `238` |
| committed / warning | `true` / none。Source survives、hash/bytes/`cmp`一致、`cleanup_state=removed` |
| adoption_status | `adopted` for operational validation claim only; synthetic body is evidence-only |
| adopter / reviewer_status | main orchestrator / EXEC-S05-SPEC-r1 passed |
| blocking / next_action | no / Fresh S05 review後にsafe Artifactとreportをcommit |

### EPE-318-004 — S05 genuinely unavailable exception

| field | value |
|---|---|
| output_form | genuinely incomplete or unavailable inline output |
| preservation_status | `skipped_inline_unavailable` |
| reason | Synthetic scenario intentionally has no complete source; import cannot be attempted honestly |
| decision_owner | main orchestrator |
| nonblocking_rationale | Complete sourceの保存失敗ではなく、製品contentを含まないmanual branch observation。Canonical docsは変更せず後続verificationを継続できる |
| next_action / revisit_condition | Future real unavailable outputでも同じfield completenessを要求し、complete sourceが得られた場合はunavailableへ分類しない |
| adoption_status | `adopted` for exception-contract validation only |
| reviewer_status | EXEC-S05-SPEC-r1 passed |

EPE-318-004にはsource/destination path、hash、byte count、byte-exact claimを記録しない。

## 目的整合台帳（Objective Alignment Ledger）

| 対象 | 主要目的の証跡 | 副次要件の証跡 | 逆転リスク | レビュアー判定 |
|---|---|---|---|---|
| Issue318 planning | 完成ChatGPT outputをcanonical rewrite前に保存するE-RQ-024/E-AC-016 | Delegated guard維持、ZIP compatibility、Issue319 relay | Runtime/import拡張やpublic rolloutが主目的を奪うriskをnon-scopeで遮断 | requirement r13 passed、findingsなし |

## 仕様 authoring ゲート（Spec Authoring Gate）

| phase | investigated facts | open questions / answers | adoption decision | reviewer verdict | blocking | promotion / next_action |
|---|---|---|---|---|---|---|
| requirement | Parent E-RQ-024/E-AC-016/DS-004/W4、accepted ADR、Issue317 runtime/report、GitHub-synced ChatGPT complete received answer、repo/specialist analysis。Workflow authorizationはcurrent Work3/iss-00318/sessionのnamed-role boundary | Product open questionなし。Grade authorityはassurance classifyへ委ね、prior user decisionsはparent Epic/ADRとsource-grounded analysisで解消 | ChatGPT evidenceをpartially_adopted/re-written。r1–r12 findingsを修正しPLANNING-REQ-r13 findingsなし、confidence 0.99 | passed | no | promote |
| design | Approved requirement、parent DS-004、accepted ADR、Issue317、ChatGPT一括候補、system-architect、provider/dogfood/test inventory | Product/design open questionなし。Exact assertion placementはplan/implementationでexisting patternへ限定 | ChatGPT/system-architect evidenceをpartially_adopted/re-written。r1 completeness/dependency/tree/UML、r2保存実行主体を修正しPLANNING-DES-r3 findingsなし、confidence 0.99 | passed | no | promote |
| plan | Approved requirement/design、Standard assurance、ChatGPT一括候補、implementation-planner、実在provider/dogfood/test surface | Product open questionなし。Test変更先はexisting 4 filesへ限定し、Issue319 relayを維持 | ChatGPT/implementation-planner evidenceをpartially_adopted/re-written。r1 step schema/path/static、r2 report ledger/commit boundaryを修正しPLANNING-PLAN-r3 findingsなし、confidence 0.99 | passed | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence）

- Not used in requirement phase。ChatGPT complete received answerはdelegated authoring roleが生成したdraftではなく、`EPE-318-001`のexternal preserved evidenceとしてのみ扱う。
- Delegated draft lifecycle、frontmatter、diff guardの適用対象はない。

| created_by_role | scope_id | artifact draft path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | rejected portions | blockers | reviewer result | promotion decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | iss-00318 | 該当なし | EPE-318-001 external preserved evidence | requirement.md / design.md / plan.md | not used | [] | not_run | manual authoring | 該当なし。External evidenceの除外claimはEAL-318-005に記録 | none | passed | promote |

## ワークフロー単位のnamed role許可（Workflow-Scoped Authorization）

| authorization source | repo/worktree | active issue | session | named roles | boundary | expires | conflict | next action |
|---|---|---|---|---|---|---|---|---|
| User request to use SpecDock Epic/Issue planning/execution workflows | current Work3 checkout | iss-00318 | current session | spec-manager、repo-analyst、system-architect、implementation-planner、doc-writer、dev-coder、spec/code/qa-reviewer | Active repo/worktree/scope/current session/documented responsibility。Scope expansion/destructive/private external/out-of-workflow roleを含まない | Issue complete/session end/scope change/user revocation/host conflict | none | Continue workflow without per-role reapproval |

## グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）

| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | system-architect and implementation-planner | used | Both fresh read-only `gpt-5.6-sol` / reasoning `medium`; repo-grounded evidenceをdesign/planへ統合し、requirement r13、design r3、plan r4で確認 | passed | ready |

## レビューゲート状態（Reviewer Gate Status）

| step | gate | reviewer | freshness | state | risk acceptance | promotion decision | notes |
|---|---|---|---|---|---|---|---|
| PLANNING-REQ-r13 | requirement alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。Requirementからdesignへのpromotionを承認 |
| PLANNING-DES-r3 | design alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。Designからplanへのpromotionを承認 |
| PLANNING-PLAN-r3 | plan executability/alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。PlanからIssue executionへのpromotionを承認 |
| PLANNING-PLAN-r4 | final plan/report runtime alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。Runtime-recognized report schemaとready guidanceを含む最終planning setを承認 |
| EXEC-S00-r1 | S00 baseline evidence | spec-reviewer | fresh | passed | no | promote | findingsなし。Gap/7 pair/61 tests/runtime non-diffをbaseline evidenceとして承認 |
| EXEC-S01-r2 | S01 provider docs contract | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。Main authorityを含む三lane/四分岐/lifecycle docs contractを承認 |
| EXEC-S02-r1 | S02 shared preservation kernel | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。四分岐、status/result matrix、Main/shared責任境界、既存ZIP safety維持を承認 |
| EXEC-S03-r1 | S03 thin planning hooks | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。三callerの呼出し位置、block伝播、matrix非複製、scope authority維持を承認 |
| EXEC-S01-REM-r1 | S01 provider docs Japanese-primary remediation | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。二provider docsの見出し・表ラベルだけを日本語主表記へ修復し、四分岐/status/EAL/ZIP/authority semantics不変を承認 |
| EXEC-S04-CODE-r3 | S04 projection / contract tests | code-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。Exact four branches、result matrix、thin caller、ZIP安定検査、7/7 parity、provider/runtime非変更を承認 |
| EXEC-S04-SPEC-r1 | S04 specification alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。7/7 byte exact projection、single owner、lane/authority semantics不変を承認。独立4-suite実行619 passed |
| EXEC-S05-SPEC-r1 | S05 manual branch evidence | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。二receipt、unavailable field、ZIP safe lane、failure block、canonical non-mutation、ignored Workbench境界を承認 |
| EXEC-S90-SPEC-r2 | S90 exact impact and Issue319 relay | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。Actual 24/24 path集合差0、台帳90実在path重複なし、runtime/public/package先行差分0、tc318-s90-02 relayを承認 |

## Review Remediation History

| review range | phase | observed findings | resolution | terminal gate |
|---|---|---|---|---|
| PLANNING-REQ-r1–r4 | requirement | External/delegated lane、exact preservation/adoption/exception/EAL field | Lane分離、exact values、exceptionとsuccess recordを具体化 | r13 passed |
| PLANNING-REQ-r5–r8 | requirement | 未完了phase promotion、raw transcript scope、terminology | 段階採用とcomplete received answer-only契約へ修正 | r13 passed |
| PLANNING-REQ-r9–r12 | requirement | Decision/EAL schema、incomplete source、authoring/reviewer gate vocabulary | 標準field/valueへ修正し未実行rowを除去 | r13 passed |
| PLANNING-DES-r1–r2 | design | Completeness/dependency/tree/UML、保存実行主体 | 構造図・guard・Main orchestrator実行へ修正 | r3 passed |
| PLANNING-PLAN-r1 | plan | Step schema/test/pathとglobal mypy boundary | 全step contract/case/pathを具体化しglobal gateをIssue319へrelay | r3 passed |
| PLANNING-PLAN-r2 | plan | 標準report ledger接続、S90/S99 commit境界 | 全台帳へ接続しS90/S99を独立commit化 | r3 passed |
| EXEC-S01-r1 | S01 | Planning skillとMain orchestratorの責任が基本原則/図で矛盾 | Planningはcheckpoint呼出し/scope handoff、Mainは保存/EAL/rewriteへ統一 | r2 passed |
| EXEC-S04-code-r1–r2 | S04 | r1でbranch/result assertion感度不足、r2でprovider修復混在、thin-caller禁止token、exact four-branch、ZIP行表現依存を指摘 | Branch section exact set、result別token、matrix複製禁止token、表現非依存ZIP row検査へ強化。S01 provider日本語主表記修復はcommit `be841c2a`へ分離し意味不変を確認 | EXEC-S04-CODE-r3 / EXEC-S04-SPEC-r1 passed |
| EXEC-S90-SPEC-r1 | S90 | Grouped surfaceだけで24 actual/considered pathを閉じ、planの実path単位契約を満たさない。`tc318-s90-02` relay test closureも欠落 | Actual 24/24 paths、no-op/defer実在pathsを個別rowへ展開し、Issue319 gate inventoryと`tc318-s90-02`を追加 | EXEC-S90-SPEC-r2 passed |

## Planning evidence log

- GitHub sync preflight: pass。Branch local/remote HEAD `7ed1985d02703f996ff8a902eca323246a4801ca`、sync_state `synced`。
- ChatGPT model evidence: requested Pro GPT-5.6 Sol、resolved GPT-5.6 Sol + Pro、verified。
- Imported complete received answer is evidence-only; preservation status and adoption status are separate。
- Bundled ChatGPT plan candidateはapproved requirement/designと実在test surfaceへ補正してcanonical planへ統合した。Provider profile自己宣言とunverified pass claimは採用していない。
- No implementation source/tests/shipped docs have been changed in planning phases。
- Runtime report gateを標準table schemaへ修正し、`guidance issue-execution`は`ready` / `execute-approved-plan` / `may_execute_approved_plan=true`を返した。

## Deferred PR Delivery Gate

- Target: `iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr`。
- Dependency: `iss-00317 -> iss-00318 -> iss-00319`。
- Reason: One final Epic PRへpackage、fresh init/update、public docs、full/global quality、final deliveryを集約する。
- Claim boundary: Issue319のPR Delivery / Merge Preparation完了までPR-ready/merge-ready/merge-preparedを主張しない。
- Remaining: Issue319 bundled planning、README/reference/migration、package/fresh init-update、full/global quality、final Epic QA/code/spec、PR creation/observation/repair。
- Issue319 current state: Requirementは未具体化template、design/planは`awaiting-assurance-compose` placeholder。Parent DS-005/W5がowner/dependency authorityを保持し、Issue319 planningで本relayをcanonical化する。
- Revisit: Issue319 planningでdeferred path/gateを採用できない場合、またはfresh consumer検証でIssue318 asset contractの欠落が実証された場合。

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence

### S00 Baseline and contract inventory

- Gap inventory: Provider三docs/四skillsへ`imported_byte_exact|captured_received_text|skipped_inline_unavailable|preservation checkpoint`を検索し、match 0、`rg` exit 1。S01–S03で追加するbaseline gapを確認。
- Projection baseline: 7 provider/dogfood pairを`cmp -s`で確認し、7/7 `MATCH`。
- Runtime/ZIP baseline: `uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py tests/manual_tests/test_review_chatgpt_authoring_pack.py`は61 passed in 11.27s。
- Runtime/source guard: S00開始時と観測後のworktreeはclean。Runtime sourceと上記2 test filesに未コミットdiffなし。
- Red alternative: Docs/skillは`inspect-only`、runtimeは`covered-existing`。Unexpected regressionなし。

### S01 Provider workflow / reference preservation contract

- Delegation: `doc-writer`がapproved S01 contractをprovider三docsだけへ実装。Skills、dogfood、tests、runtime、public/package docsは未変更。
- `workflow_spec_authoring.md`: 三lane分離、preservation-before-adoption/rewrite、complete-source failure block、external/delegated guard境界、共通lifecycleを追加。
- `workflow_chatgpt_authoring_pack.md`: Pre-classification/四branchの利用者向けroute、planning/Main authority、Mainを含むsequenceを追加。
- `authoring/chatgpt-pack.md`: 四branch/status/capture boundary、import result、content-free EALのreference contractを集約。
- Inspect-only verification: Exact status/lifecycle/authority/forbidden termsを`rg`、`git diff --check` pass。Docs-onlyのためpytest未実施。
- Reviewer: EXEC-S01-r1は責任図の矛盾を指摘し修正。Fresh EXEC-S01-r2はfindingsなし、confidence 0.99、`promote`。
- Ledger Note: Approved planを具体化しただけでmaterial implementation decisionなし。S02–S04のskill/projection/test責務は未変更。
- Post-S01 remediation: S04 full installer testで既存の日本語主表記ガードが二provider docsの英語主heading/table labelを検出したため、意味を変えず日本語主＋英語anchorへ修復した。Fresh EXEC-S01-REM-r1はfindingsなし、confidence 0.99、`promote`。S04のprovider変更禁止境界から独立commitへ分離する。

### S02 Shared ChatGPT preservation kernel

- Delegation: `doc-writer`がapproved S02 contractをprovider shared skill一件だけへ実装。Planning skills、dogfood、tests、runtimeは未変更。
- Shared checkpoint: Semantic completenessをfile属性から推測せず、complete standalone、complete received inline、genuinely unavailable、ZIP/treeのexact one branchへ分類する契約を追加。
- Preservation/result semantics: `imported_byte_exact`、`captured_received_text`、`skipped_inline_unavailable`、`pass`、`pass-with-warning`、`block`を明示し、complete source failureからunavailableへの迂回を禁止。
- Authority/secrecy: Shared skillはclassification contractとevidence evaluationだけを所有し、Main orchestratorがcapture/import/exception/EAL/adoption/rewriteを所有。Content-free handoffとrepo-relative receipt metadataだけを許可。
- Compatibility: Existing GitHub-synced/local-context modesとZIP/tree review/quarantine/stage/validation laneを維持。Planning matrix、dogfood、tests、runtimeの変更なし。
- Verification: `git diff --check` pass。Fresh EXEC-S02-r1はfindingsなし、confidence 0.99、`promote`。
- Ledger Note: Approved shared-kernel contractの具体化だけでmaterial implementation decisionなし。S03 thin hookとS04 projection/testsは未変更。

### S03 Thin planning-skill integration

- Delegation: `doc-writer`がprovider Initiative / Epic / Issue planning skill三件だけへ同一のthin hookを追加。Shared/manual skills、dogfood、tests、runtimeは未変更。
- Invocation placement: 各callerでChatGPT output受領直後、claim review / EAL disposition / canonical rewrite前にshared `spec-dock-chatgpt-authoring` preservation checkpointを呼ぶ。
- Stop propagation: Blocking handoffは停止・伝播し、`skipped_inline_unavailable`はreason、decision owner、nonblocking rationale、next actionまたはrevisit conditionが揃う場合だけ継続可能。
- Single ownership: Four-branch/status/import-result matrixはshared skill参照とし、三planning skillへ複製しない。
- Scope authority: InitiativeのEpic creation human approval、EpicのIssue slice/node explicit approval、Issueのfresh reviewer/execution handoffを維持。
- Verification: Three-caller structural comparison、duplicate scan、scope checklist、`git diff --check` pass。Fresh EXEC-S03-r1はfindingsなし、confidence 0.99、`promote`。
- Ledger Note: Approved S03 caller integrationの最小実装だけでmaterial implementation decisionなし。S04 projection/testsは未変更。

### S04 Dogfood projection and automated contract verification

- Delegation: `dev-coder`を`gpt-5.6-sol` / reasoning `medium`で使用し、matching dogfood七filesとexisting `tests/cli_runtime/test_wrappers.py` / `tests/unit/infra/test_init_update.py`を更新。Provider/runtime sourceはS04で変更していない。
- Red evidence: Projection前のprovider/dogfood parity assertionは期待理由でRed。Initial code review r1/r2もbranch/result sensitivity、thin caller single-owner、ZIP表現依存、scope混在を検出した。
- Projection: Provider三docs・四skillsをmatching dogfood七filesへ機械的に投影し、`cmp -s`とSHA-256で7/7 byte exactを確認。
- Contract sensitivity: Shared checkpoint sectionをexact four branchへ限定し、各branch固有操作/status/禁止事項、`pass` / `pass-with-warning` / `block`、failed import再分類禁止を検査。三planning callerは正当なunavailable handoffを許しつつmatrix固有tokenの複製を拒否する。
- ZIP stability: Reference tableを`ZIP / tree`を含む一意rowと4 cellsへ分解し、action/evidence/forbiddenの安定tokenを検査。日本語セル全文には依存しない。
- Verification: Focused wrapper + preservation testは8 passed。Artifact importは4 passed、authoring-pack manual regressionは57 passed。Current final diffに対するfresh spec-reviewer独立4-suite実行は619 passed in 354.82s。
- Concurrency observation: Main側の同時全件実行は変更対象外のwait timing test一件だけ`polls=1`で550 passed / 1 failed、競合中の単独再実行も同じ。Reviewer側の独立619-test runでは同testを含め全件passしたため、S04起因の回帰ではなく並列負荷下の非再現timing observationとして記録し、test修正は行わない。
- Review: EXEC-S04-CODE-r3 / EXEC-S04-SPEC-r1はfindingsなし、confidence 0.99、`promote`。Runtime import source、ZIP/delegated runtime、Issue317 surfaceにdiffなし。
- Ledger Note: Approved S04 projection/test契約の実装のみ。日本語主表記修復はS01 remediation commitへ分離済みで、material design decisionやplan amendmentなし。

### S05 Manual four-branch dogfood evidence

- Standalone: Safe synthetic Workbench Markdownを明示import。Receiptは`committed=true`、warningなし、199 bytes、source survives、source/destination SHA-256と`cmp`一致。`imported_byte_exact`の境界をWorkbench sourceからArtifactまでに限定。
- Inline: Safe complete synthetic answer bodyを無編集capture/import。Receiptは`committed=true`、warningなし、238 bytes、source survives、hash/bytes/`cmp`一致。`captured_received_text`を記録しprovider-original byte identityは非主張。
- Unavailable: Complete sourceが存在しないsynthetic caseをEPE-318-004へ記録。Reason、decision owner、nonblocking rationale、next actionを持ち、path/hash/bytes/byte-exact claimを持たない。
- ZIP/tree: Existing safe review/quarantine/stage laneのmanual regression 57 testsがpass。S05 Artifact inventoryはstandalone/inlineの二件だけで、ZIP用single-file import destinationは作成されていない。
- Failure gate: Approved Workbench外のsafe canonical Markdownをsourceに指定しexit 1、`code=source_ineligible`、`committed=false`、`cleanup_state=not_created`を観測。Unavailableへ再分類せずadoption/rewriteをblockした。
- Canonical non-mutation: Failure前後のrequirement/design/plan SHA-256はそれぞれ`08268a05...99de`、`bff9d2e4...3e5b`、`58cc90ba...ec18`で一致。Artifact inventoryも成功二件だけ。
- Git boundary: Workbench二sourceはignoredかつuntrackedのまま保持し、commit対象はsafe Artifact二件とreportだけ。
- Ledger Note: Approved S05 synthetic observationのみ。Runtime/skill/provider/dogfood/tests/canonical docsを変更せず、material implementation decisionやplan amendmentなし。

### S90 Docs impact and Issue319 ownership closure

- Baseline: Issue317 final commit `7ed1985d`からIssue318 HEAD `6b6bd10d`までをIssue固有差分基準とした。`origin/main...HEAD`はIssue315–318累積のためinventory authorityに使用しない。
- Coverage: Issue318 actual diffは24/24 pathsを分類済み。Provider authority七、dogfood projection七、focused tests二、Issue-local requirement/design/plan/report/assurance/artifacts八で未分類なし。
- Update complete: Provider三docs・四skills、matching dogfood七files、`tests/cli_runtime/test_wrappers.py`、`tests/unit/infra/test_init_update.py`のIssue318 contract、Issue-local canonical docs/assurance/report/artifacts。
- Approved no-op: Artifact rules三scopeとtemplates、Issue317 artifact import runtime、authoring-pack ZIP review/stage runtime、delegated-authoring runtime、root authoring helper。`git diff --quiet 7ed1985d..HEAD -- src/spec_dock/assets/spec_dock/scripts spec-dock/scripts`はexit 0。
- Defer to Issue319: `README.md`、provider/dogfood `docs/README.md`・`guide.md`・`reference_naming.md`・`reference_worktree.md`、migration/release placement、`pyproject.toml`、`src/spec_dock/cli.py`、`src/spec_dock/__init__.py`、`uv.lock`、package/fresh init-update/smoke、full pytest/global static、final manual/Epic QA/code/spec、PR creation/observation/repair。
- Diff evidence: Root/public/package候補にIssue318差分なし。Runtime/provider/dogfoodのimport・ZIP・delegated-authoring実在surfaceを列挙確認し、Issue318 semanticsの先行実装なし。
- Risk: Issue318をblockするmaterial unresolved riskなし。Issue319 nodeがplaceholderであることはnon-blocking handoff conditionで、Parent DS-005/W5がowner/dependencyを固定済み。
- Claim boundary: Issue318ではPRを作成せず、PR-ready / merge-ready / merge-preparedを主張しない。
- Ledger Note: Approved ownership relayを実パス/gateへ具体化したread-only inventoryのみ。New product semantics、runtime変更、material implementation decision、plan amendmentなし。
<!-- spec-dock:managed-section end id="report.step-evidence" -->

## ドキュメント影響の解消（Docs Impact Resolution）

| exact path | disposition | owner | reason | dependency | blocking | reviewer |
|---|---|---|---|---|---|---|
| `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | update-complete | Issue318 | Preservation lifecycle provider authority | Issue317 runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md` | update-complete | Issue318 | Output-form routing provider authority | workflow spec authoring | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md` | update-complete | Issue318 | Four-branch/result/EAL reference | accepted ADR / Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | update-complete | Issue318 | Shared matrix single owner | provider docs | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | update-complete | Issue318 | Initiative thin checkpoint hook | shared skill | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | update-complete | Issue318 | Epic thin checkpoint hook | shared skill | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | update-complete | Issue318 | Issue thin checkpoint hook | shared skill | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/workflow_spec_authoring.md` | update-complete | Issue318 | Exact dogfood projection | matching provider | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/workflow_chatgpt_authoring_pack.md` | update-complete | Issue318 | Exact dogfood projection | matching provider | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/authoring/chatgpt-pack.md` | update-complete | Issue318 | Exact dogfood projection | matching provider | no | EXEC-S90-SPEC-r2 passed |
| `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | update-complete | Issue318 | Exact dogfood projection | matching provider | no | EXEC-S90-SPEC-r2 passed |
| `.agents/skills/spec-dock-initiative-planning/SKILL.md` | update-complete | Issue318 | Exact dogfood projection | matching provider | no | EXEC-S90-SPEC-r2 passed |
| `.agents/skills/spec-dock-epic-planning/SKILL.md` | update-complete | Issue318 | Exact dogfood projection | matching provider | no | EXEC-S90-SPEC-r2 passed |
| `.agents/skills/spec-dock-issue-planning/SKILL.md` | update-complete | Issue318 | Exact dogfood projection | matching provider | no | EXEC-S90-SPEC-r2 passed |
| `tests/cli_runtime/test_wrappers.py` | update-complete | Issue318 | Installed shared/thin-caller contract | seven provider assets | no | EXEC-S90-SPEC-r2 passed |
| `tests/unit/infra/test_init_update.py` | update-complete | Issue318 | Managed seven-asset projection contract | provider/dogfood parity | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00318-chatgpt-first-preservation-workflow-and-skill-integration/.assurance.json` | update-complete | Issue318 | Standard assurance authority | approved planning | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00318-chatgpt-first-preservation-workflow-and-skill-integration/artifacts/20260713t180812z-chatgpt-output-issue-318-chatgpt-5-6-pro-planning-report.md` | update-complete | Issue318 | Preserved bundled planning evidence | import runtime | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00318-chatgpt-first-preservation-workflow-and-skill-integration/artifacts/20260714t094952z-01-chatgpt-output-issue-318-s05-inline.md` | update-complete | Issue318 | Inline preservation dogfood evidence | S05 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00318-chatgpt-first-preservation-workflow-and-skill-integration/artifacts/20260714t094952z-chatgpt-output-issue-318-s05-standalone.md` | update-complete | Issue318 | Standalone preservation dogfood evidence | S05 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00318-chatgpt-first-preservation-workflow-and-skill-integration/requirement.md` | update-complete | Issue318 | Canonical accepted scope/AC | parent E-RQ-024 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00318-chatgpt-first-preservation-workflow-and-skill-integration/design.md` | update-complete | Issue318 | Canonical responsibility/runtime boundary | requirement | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00318-chatgpt-first-preservation-workflow-and-skill-integration/plan.md` | update-complete | Issue318 | Approved S00–S99 execution contract | design | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00318-chatgpt-first-preservation-workflow-and-skill-integration/report.md` | update-complete | Issue318 | Planning/execution/reviewer/relay evidence | S00–S90 | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/rules/initiative/artifacts.md` | approved-no-op | Issue318 no-op check | Blank coexistence unchanged | accepted ADR | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/rules/initiative/artifacts.md` | approved-no-op | Issue318 no-op check | Matching dogfood rule unchanged | provider rule | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/rules/epic/artifacts.md` | approved-no-op | Issue318 no-op check | Blank coexistence unchanged | accepted ADR | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/rules/epic/artifacts.md` | approved-no-op | Issue318 no-op check | Matching dogfood rule unchanged | provider rule | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/rules/issue/artifacts.md` | approved-no-op | Issue318 no-op check | External evidenceへfrontmatterを強制しない | RQ-318-008 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/rules/issue/artifacts.md` | approved-no-op | Issue318 no-op check | Matching dogfood rule unchanged | provider rule | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/templates/README.md` | approved-no-op | Issue318 no-op check | Import is template-free | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/templates/README.md` | approved-no-op | Issue318 no-op check | Matching dogfood template index unchanged | provider template | no | EXEC-S90-SPEC-r2 passed |
| `tests/cli_runtime/test_artifact_import_chatgpt_output.py` | approved-no-op | Issue317 | Import regression authority only | Issue317 runtime | no | EXEC-S90-SPEC-r2 passed |
| `tests/manual_tests/test_review_chatgpt_authoring_pack.py` | approved-no-op | existing authoring lane | ZIP regression authority only | ZIP lane | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` | approved-no-op | Issue317 | Import application contract complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/application/contracts.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py` | approved-no-op | Issue317 | Artifact creation coexistence complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/application/create_artifact_doc.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_artifact.py` | approved-no-op | Issue317 | Import application semantics complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/application/import_artifact.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` | approved-no-op | Issue317 | Import publisher port complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/application/ports.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` | approved-no-op | Issue317 | Runtime dependency wiring complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` | approved-no-op | Issue317 | Import parser contract complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/cli/parser.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py` | approved-no-op | Issue317 | Import command registration complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/cli/registry.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py` | approved-no-op | Issue317 | Import command complete | Issue317 application | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/commands/artifact_import.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py` | approved-no-op | Issue317 | Byte publisher complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` | approved-no-op | Issue317 | Content-free receipt presentation complete | Issue317 | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/presentation/cli_text.py` | approved-no-op | Issue317 projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_review.py` | approved-no-op | existing authoring lane | ZIP review safety unchanged | ZIP contract | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/application/authoring_pack/pack_review.py` | approved-no-op | existing projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/pack_stage.py` | approved-no-op | existing authoring lane | ZIP stage safety unchanged | ZIP review | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/application/authoring_pack/pack_stage.py` | approved-no-op | existing projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py` | approved-no-op | existing authoring lane | Workbench/ZIP source contract unchanged | authoring pack | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py` | approved-no-op | existing projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py` | approved-no-op | existing authoring lane | ZIP safety contract unchanged | authoring pack | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/zip_contract.py` | approved-no-op | existing projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py` | approved-no-op | existing delegated lane | Delegated provenance/diff guard unchanged | delegated contract | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/application/delegated_authoring.py` | approved-no-op | existing projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/delegated_authoring.py` | approved-no-op | existing delegated lane | Delegated domain contract unchanged | delegated contract | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/domain/delegated_authoring.py` | approved-no-op | existing projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delegated_authoring.py` | approved-no-op | existing delegated lane | Delegated command contract unchanged | delegated domain | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/commands/delegated_authoring.py` | approved-no-op | existing projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py` | approved-no-op | existing authoring lane | GitHub-synced preflight unchanged | authoring pack | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py` | approved-no-op | existing projection | Matching dogfood runtime unchanged | provider runtime | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/authoring-pack/authoring_pack_review.py` | approved-no-op | existing authoring lane | Shipped ZIP review wrapper unchanged | ZIP runtime | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/authoring-pack/authoring_pack_review.py` | approved-no-op | existing projection | Matching dogfood wrapper unchanged | provider wrapper | no | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/scripts/authoring-pack/invoke_chatgpt_backend.py` | approved-no-op | existing authoring lane | Shipped backend wrapper unchanged | authoring pack | no | EXEC-S90-SPEC-r2 passed |
| `spec-dock/scripts/authoring-pack/invoke_chatgpt_backend.py` | approved-no-op | existing projection | Matching dogfood wrapper unchanged | provider wrapper | no | EXEC-S90-SPEC-r2 passed |
| `scripts/authoring-pack/authoring_pack_review.py` | approved-no-op | existing root tooling | Root ZIP review helper unchanged | authoring pack | no | EXEC-S90-SPEC-r2 passed |
| `scripts/authoring-pack/invoke_chatgpt_backend.py` | approved-no-op | existing root tooling | Backend wrapper unchanged | authoring pack | no | EXEC-S90-SPEC-r2 passed |
| `README.md` | defer-to-iss-00319 | Issue319 | Root usage/experimental/evidence-only rollout | Issue315–318 complete | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/README.md` | defer-to-iss-00319 | Issue319 | Public docs index | W5 docs rollout | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/README.md` | defer-to-iss-00319 | Issue319 | Matching dogfood public docs index | provider doc | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/guide.md` | defer-to-iss-00319 | Issue319 | Workbench-to-Artifact public guide | Issue318 terminology | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/guide.md` | defer-to-iss-00319 | Issue319 | Matching dogfood public guide | provider doc | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/reference_naming.md` | defer-to-iss-00319 | Issue319 | Blank/chatgpt-output naming examples | Issue317 grammar | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/reference_naming.md` | defer-to-iss-00319 | Issue319 | Matching dogfood naming reference | provider doc | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/assets/spec_dock/docs/reference_worktree.md` | defer-to-iss-00319 | Issue319 | Workbench handoff/no-sync public guidance | Issue316/318 | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `spec-dock/docs/reference_worktree.md` | defer-to-iss-00319 | Issue319 | Matching dogfood worktree reference | provider doc | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `pyproject.toml` | defer-to-iss-00319 | Issue319 | Package-data/build verification | all assets complete | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/cli.py` | defer-to-iss-00319 | Issue319 | Fresh init/update distribution verification | built package | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `src/spec_dock/__init__.py` | defer-to-iss-00319 | Issue319 | Version/release decision | release policy | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `uv.lock` | defer-to-iss-00319 | Issue319 | Final build/lock consistency | package verification | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |
| `tests/unit/cli/test_cli_smoke.py` | defer-to-iss-00319 | Issue319 | Installed package smoke | built package | Issue318 no; Epic yes | EXEC-S90-SPEC-r2 passed |

上表の先頭24行は`git diff --name-only 7ed1985d..6b6bd10d`の24/24実pathと一対一対応する。No-op/deferもwildcardを使用せず、確認した実在pathだけを列挙した。

### Issue319 relay gate inventory

| exact gate | disposition | owner | reason | dependency | blocking | revisit |
|---|---|---|---|---|---|---|
| Migration / release note placement | defer-to-iss-00319 | Issue319 | Dedicated pathは未存在。README/guideまたはW5が承認する新規pathへ配置 | Public docs review | Issue318 no; Epic yes | Issue319 planningでexact pathを決定 |
| Package build and fresh init/update matrix | defer-to-iss-00319 | Issue319 | Wheel/installed consumer parityを最終確認 | Issue315–318 complete | Issue318 no; Epic yes | Distribution failure時にowning Issueへ戻す |
| Full `uv run pytest` | defer-to-iss-00319 | Issue319 | Epic-wide regression gate | Full diff assembled | Issue318 no; Epic yes | Failureをowning stepへroute |
| Repository-wide `uv run mypy src` and global Ruff/static repair | defer-to-iss-00319 | Issue319 | Issue-localでないglobal quality | Full diff assembled | Issue318 no; Epic yes | Existing/new failureを分類 |
| Installed/fresh consumer manual scenario | defer-to-iss-00319 | Issue319 | Workbench handoff→import→EAL→canonical rewriteの統合確認 | Package/docs/runtime parity | Issue318 no; Epic yes | Missing contractをowning Issueへroute |
| Final Epic `qa-reviewer` → `code-reviewer` → `spec-reviewer` | defer-to-iss-00319 | Issue319 | Epic AC/distribution/full qualityを順序付き判定 | All verification complete | Issue318 no; Epic yes | Finding修復後fresh rerun |
| PR create / checks / Codex review / observation / repair | defer-to-iss-00319 | Issue319 | One final Epic PR ownership | Final reviewers pass | Issue318 no; Epic yes | Merge-preparedまでobserve/repair |

## Step Contract Closure

| step | closure ids | close condition | evidence | result |
|---|---|---|---|---|
| S00 | C318-01–10 baseline | Gap、7 pair、import/ZIP tests、runtime non-diffを変更前に固定 | Step Evidence S00、Test Contract Closure、EXEC-S00-r1 | passed |
| S01 | C318-01–07 docs semantics | 三lane、四branch、lifecycle、authority/secrecy、existing guard維持をprovider docsへ固定 | Step Evidence S01、EXEC-S01-r2 | passed |
| S02 | C318-01–05、C318-07–08 shared kernel | 四分岐、status/result matrix、content-free handoff、Main/shared責任境界をshared skill一箇所へ固定 | Step Evidence S02、tc318-s02-01–02、EXEC-S02-r1 | passed |
| S03 | C318-03、C318-05、C318-07–08 caller integration | 三callerの正しい呼出し位置、block伝播、unavailable field、matrix非複製、scope authorityを固定 | Step Evidence S03、tc318-s03-01–02、EXEC-S03-r1 | passed |
| S04 | C318-04、C318-06、C318-08–10 projection/tests | 7/7 exact projection、contract-sensitive installed tests、ZIP/import非回帰、runtime/provider非変更 | Step Evidence S04、tc318-s04-01–03、EXEC-S04-CODE-r3、EXEC-S04-SPEC-r1 | passed |
| S05 | C318-01–05、C318-07、C318-11 manual observation | Success二件のbyte/capture boundary、unavailable field、ZIP lane、failure block、canonical non-mutation | Step Evidence S05、EPE-318-002–004、tc318-s05-01–03、EXEC-S05-SPEC-r1 | passed |
| S90 | C318-10–11 impact/relay | 24/24 path disposition、runtime/no-op boundary、Issue319 owner/dependency/blocking、no merge-ready self-claim | Step Evidence S90、Docs Impact Resolution、tc318-s90-01–02、D-318-004、EXEC-S90-SPEC-r2 | passed |

## Test Contract Closure

| test id | closure ids | evidence level | pre-implementation evidence | verification | result |
|---|---|---|---|---|---|
| tc318-s00-01 | C318-01–08 | inspect-only | 四分岐/status/checkpointの対象7 provider files match 0 | `rg` exact-term inventory | passed baseline gap |
| tc318-s00-02 | C318-04、C318-09–10 | covered-existing | 7/7 provider/dogfood MATCH、focused import/ZIP 61 passed | `cmp -s` pair list、focused pytest、runtime diff inspection | passed baseline |
| tc318-s01-01 | C318-01–05 | inspect-only | S00 exact terms match 0 | Three-doc lifecycle/branch inspection、EXEC-S01-r2 | passed |
| tc318-s01-02 | C318-06–07 | inspect-only | Existing delegated/ZIP contracts present | Lane/authority/secrecy forbidden-term inspection、EXEC-S01-r2 | passed |
| tc318-s02-01 | C318-01–02、C318-07–08 | inspect-only | S01 reference contract fixed | Complete standalone/inline branch、exact status、receipt/content-free authority inspection、EXEC-S02-r1 | passed |
| tc318-s02-02 | C318-03–05、C318-08 | inspect-only | S01 unavailable/ZIP/failure semantics fixed | Unavailable exception、ZIP existing lane、warning/block/no-reclassification inspection、EXEC-S02-r1 | passed |
| tc318-s03-01 | C318-03、C318-05、C318-08 | inspect-only | S02 shared checkpoint passed | Three-file invocation placement、blocking propagation、unavailable field completeness、EXEC-S03-r1 | passed |
| tc318-s03-02 | C318-07–08 | inspect-only | S02 matrix authority passed | Duplicate scan、Initiative/Epic/Issue scope authority checklist、`git diff --check`、EXEC-S03-r1 | passed |
| tc318-s04-01 | C318-01–09 | red-required | Projection前parity Red、review r1/r2でassertion感度不足を検出 | Exact four branch/result/thin caller/ZIP assertions、focused 8 pass、fresh code/spec review | passed |
| tc318-s04-02 | C318-09 | structural regression | S00 baseline 7/7 match | Seven `cmp -s` + SHA-256 pair evidence、provider/dogfood byte exact | passed |
| tc318-s04-03 | C318-04、C318-06、C318-10 | covered-existing | S00 import/ZIP 61 pass | Current final diffでartifact import 4 + ZIP 57、reviewer independent aggregate 619 pass、runtime source diff none | passed |
| tc318-s05-01 | C318-01–02、C318-07、C318-11 | direct manual | Safe complete Workbench sources二件 | Two committed receipts、source survives、hash/bytes/`cmp`一致、最大二Artifact、EXEC-S05-SPEC-r1 | passed |
| tc318-s05-02 | C318-03、C318-05、C318-07 | direct manual | Genuine unavailable synthetic case + approved-Workbench外source | Exception field inspection、exit 1 `source_ineligible`/`committed=false`、canonical hashes不変、EXEC-S05-SPEC-r1 | passed |
| tc318-s05-03 | C318-04 | covered-existing + inventory | Existing safe ZIP fixtures | 57 passed、S05 Artifact inventoryにZIP single-file destinationなし、EXEC-S05-SPEC-r1 | passed |
| tc318-s90-01 | C318-10–11 | inspect-only | Issue317 final commit、Issue318 actual diff、parent W5/DS-005、Issue319 placeholder | 24/24 classification、runtime/deferred diff checks、exact path existence、upstream 0/0、EXEC-S90-SPEC-r2 | passed |
| tc318-s90-02 | C318-11 | inspect-only | Parent DS-005/W5、Issue317 relay、Issue319 placeholder | Deferred path/gate、remaining work、owner/dependency/blocking/revisit、no per-Issue PR/readiness claimをcross-document照合、EXEC-S90-SPEC-r2 | passed |

## Closure Coverage

| closure ids | current evidence | state | next owner |
|---|---|---|---|
| C318-01–05、C318-07 | S01–S04 contract/tests、S05 direct branch/failure evidence、EXEC-S05-SPEC-r1 | passed | S99 final alignment |
| C318-06 | S01 external/delegated/ZIP lane separation、S04 regression | projection/test evidence passed | S99 |
| C318-08 | S02 matrix single-owner、S03 three thin callers、S04 structural tests | projection/test evidence passed | S99 |
| C318-09 | S04 7/7 byte exact projection | passed | S99 inventory |
| C318-04、C318-10 | S04 import/ZIP 61 pass、independent aggregate 619 pass、runtime diff none | passed | S05/S99 |
| C318-11 | S90 exact Issue319 relay、Deferred PR Delivery Gate、EXEC-S90-SPEC-r2 | passed | S99 final alignment |

## Closure Delta

| step | added | removed | changed | unimplemented | re-review |
|---|---|---|---|---|---|
| S00 | none | none | none | S01–S99 obligations remain | EXEC-S00-r1 passed; amendment不要 |
| S01 | none | none | Main/Planning責任図をr1 findingで明確化 | S02–S99 obligations remain | EXEC-S01-r2 passed; plan amendment不要 |
| S02 | none | none | none | S03–S99 obligations remain | EXEC-S02-r1 passed; plan amendment不要 |
| S03 | none | none | none | S04–S99 obligations remain | EXEC-S03-r1 passed; plan amendment不要 |
| S01 remediation | none | none | 二provider docsの見出し・表ラベルを日本語主表記へ修復。Preservation/authority semantics不変 | S04–S99 obligations remain | EXEC-S01-REM-r1 passed; material design changeなし |
| S04 | none | none | Test sensitivityをreview findingsに従い強化。Provider semantics/runtime変更なし | S05–S99 obligations remain | EXEC-S04-CODE-r3 / EXEC-S04-SPEC-r1 passed; plan amendment不要 |
| S05 | none | none | none | S90–S99 obligations remain | EXEC-S05-SPEC-r1 passed; plan amendment不要 |
| S90 | none | none | Deferred owner/path/gateを実在inventoryへ具体化 | S99 obligations remain | EXEC-S90-SPEC-r2 passed; plan amendment不要 |

## Implementation Delegation Gate

| step | decision | role | scope/source | allowed | forbidden | verification/stop/output | result |
|---|---|---|---|---|---|---|---|
| S00 | approved-local-execution | main orchestrator | Approved plan S00 read-only baseline | report.md update、target inventory/test read | provider/dogfood/test/runtime/assurance edits | Stop on regression/drift; output exact command/result/ledger note | completed; EXEC-S00-r1 passed |
| S01 | delegated | doc-writer | Approved plan S01、provider三docs | provider三docsだけ | skills/dogfood/tests/runtime/public/package/report | Docs inspection、diff-check、stop on scope expansion、worker summary/Ledger Note | completed; EXEC-S01-r2 passed |
| S02 | delegated | doc-writer | Approved plan S02、provider shared skill | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`だけ | planning skills/dogfood/tests/runtime/report | Exact four branches/status/result/authority inspection、diff-check、stop on scope expansion、worker summary | completed; EXEC-S02-r1 passed |
| S03 | delegated | doc-writer | Approved plan S03、provider planning skills三件 | Initiative/Epic/Issue planning `SKILL.md`三件だけ | shared/manual skills/dogfood/tests/runtime/report/matrix copy | Three-caller comparison、duplicate scan、scope checklist、diff-check、worker summary | completed; EXEC-S03-r1 passed |
| S04 | delegated | dev-coder `gpt-5.6-sol` / medium | Approved plan S04、reviewed provider assets、matching dogfood七files、existing tests | Dogfood七files、`test_wrappers.py`、`test_init_update.py` | Provider/runtime/public/package/new test file | Exact branch/result/thin caller/ZIP assertions、7/7 compare、focused/full regression、fresh code/spec review | completed; EXEC-S04-CODE-r3 / EXEC-S04-SPEC-r1 passed |
| S05 | approved-local-execution | main orchestrator | Approved plan S05 safe synthetic manual dogfood | Exact Workbench二files、最大二Artifact、report.md | Runtime/skills/provider/dogfood/tests/canonical docs、real/private content | Receipt/hash/byte/cmp/source survival、exception fields、ZIP tests/inventory、failure/canonical hash、fresh spec review | completed; EXEC-S05-SPEC-r1 passed |
| S90 | delegated-read-only | repo-analyst `gpt-5.6-sol` / medium | Approved plan S90、Issue317/318/319、parent Epic、actual diff | Read-only inventory、report handoff | Source/docs/tests/Issue319 edits、PR/readiness claim | 24/24 path classification、runtime/deferred diff、fresh spec review | completed; EXEC-S90-SPEC-r2 passed |

## Milestone / Commit Candidate Gate

| step | reviewer verdict | commit candidate/scope | closure state | commit evidence | post-commit clean |
|---|---|---|---|---|---|
| S00 | EXEC-S00-r1 passed | `docs(issue-318): Preservation契約のベースラインを記録`; report.md only | passed | Focused commit hashはpost-commit external evidenceで記録 | Post-commit external clean/upstream check必須 |
| S01 | EXEC-S01-r2 passed | `docs(chatgpt-first): 原文保存ワークフロー契約を追加`; provider三docs + report.md | passed | Focused commit hashはpost-commit external evidenceで記録 | Post-commit external clean/upstream check必須 |
| S02 | EXEC-S02-r1 passed | `docs(chatgpt-first): 共有preservation checkpointを追加`; provider shared skill + report.md | passed | Focused commit hashはpost-commit external evidenceで記録 | Post-commit external clean/upstream check必須 |
| S03 | EXEC-S03-r1 passed | `docs(chatgpt-first): planning skillへ保存checkpointを接続`; provider planning skills三件 + report.md | passed | Focused commit hashはpost-commit external evidenceで記録 | Post-commit external clean/upstream check必須 |
| S01 remediation | EXEC-S01-REM-r1 passed | `docs(chatgpt-first): 保存契約文書を日本語主表記へ修復`; provider二docs + report.md | passed | Focused remediation commit hashはpost-commit external evidenceで記録 | S04 working diffを残したままcommitし、provider変更がS04 staged scopeへ混在しないことを確認 |
| S04 | EXEC-S04-CODE-r3 / EXEC-S04-SPEC-r1 passed | `test(chatgpt-first): preservation契約と投影を検証`; dogfood七files + existing tests二files + report.md | passed | Focused commit hashはpost-commit external evidenceで記録 | Post-commit clean/upstream check必須 |
| S05 | EXEC-S05-SPEC-r1 passed | `docs(issue-318): preservation分岐のdogfood証跡を記録`; safe Artifact二件 + report.md | passed | Focused commit hashはpost-commit external evidenceで記録 | Workbench sourceをstageしない。Post-commit clean/upstream check必須 |
| S90 | EXEC-S90-SPEC-r2 passed | `docs(issue-318): Issue319への引継ぎ境界を確定`; report.md only | passed | Focused commit hashはpost-commit external evidenceで記録 | Post-commit clean/upstream check必須 |

## Final QA Gate

- S99でqa-reviewer verdict、test sufficiency、integration test要否を記録する。

## Final Code Review Gate

- S99でissue-wide code-reviewer verdict、integrated diff、修正/re-reviewを記録する。

## Final Spec Review Gate

- S99でspec-reviewer verdictとrequirement/design/plan/report/docs alignmentを記録する。

## Final Commit

- Final report ledger、final commit scope、post-commit external evidence destinationを記録する。
