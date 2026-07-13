---
種別: 実装報告書（Issue）
ID: "iss-00316"
タイトル: "Experimental Scoped Workbench Copy And Source Wins Merge"
関連GitHub: ["#316"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00312", "init-local-00003"]
---

# iss-00316 Experimental Scoped Workbench Copy And Source Wins Merge — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-316-001 | resolved | scope | user / Epic planning / GPT-5.6 Pro | Root Workbenchをcopy commandへ含めるか | 一括copy; manual selective copy; root selector追加 | Root Workbenchはgarbage-proneなscope外scratchであり、一括copy commandへ含めず、必要fileだけagentが手動選択する | 親Epicのroot exclusionと明示された運用判断を保ち、scope内handoffを単純化する | applied | Epic E-RQ-007/E-RQ-014; requirement RQ-316-001 | Issue-local command contractへ適用。追加follow-upなし |
| D-316-002 | resolved | implementation | GPT-5.6 Pro / repo inventory | Source-winsとdestination-only保持におけるdirectory/leaf型衝突 | destructive replacement; skip; fail | Same-type directory mergeとordinary leaf replacementだけを許し、directory/non-directory衝突はdestination subtreeを削除せずfailする | Destination-only data lossを避け、content classifierなしの単純なfilesystem error境界を保つ | promoted_to_design | `design.md` DES-316-005 entry matrix、fresh design reviewer r2 pass | Design promotion確定。Implementationでfresh code review |
| D-316-003 | resolved | implementation | S05 security reviewer r1/r2 | NodeRepositoryがguard前にbelow-specdock symlink metadataを読める | Schema-shaped guard; general repo change; Workbench-specific full discovery guard | Workbench operation専用で`initiatives`以下のactual metadata discovery surfaceをtop-down `lstat`し、exact `.workbench` prune、全dir symlinkと`.meta.json` symlink/nonregularをreader前に拒否 | General NodeRepository semanticsを変えずexplicit copyだけをfail-closedにし、Issue315のresolve-before-guard回帰を防ぐ | applied | Security review r1/r2 fail→r3 pass、external metadata observer/node_repo未呼出しtests、focused63 pass | `fs_repo` discovery変更時にguard/test同期 |
| D-316-004 | resolved | implementation | S05 security reviewer r1 | `mutation_started`をatomic primitive前に立てfalse positive | 常にpre-mark; post-success; unknown tri-state | `mkdir`/`unlink`/symlink creationは成功後、partial mutationし得る`copy2`だけ呼出前にmark | Public booleanを維持しつつ観測可能な部分変更を最も正直に表す | applied | Injected mkdir/unlink/symlink failure=false、unlink成功後/copy2 fault=true、r3 pass | TOCTOU/transactionはnon-goal |
| D-316-005 | resolved | implementation | final code-reviewer / remediation r1-r3 reviewers | Preflight後のsource/destination directory・leaf差し替えで検査済みidentity/missing premiseとcopy時pathnameが乖離し得る | 完全なdirfd実装; boundaryごとのidentity/missing再検証; 対応なし | EC-316-005の範囲で、各directory boundaryとmutation直前にidentityを再検証し、missing destination作成・leaf write時は親identityとleaf missing premiseも検証する。前提変化はcontent-free failureとする | 完全なtransaction/TOCTOU排除へscope拡張せず、RQ-316-007/008の境界外read/write防止を満たす | applied | r3でinitially-missing/post-unlink leafを`copy2`/`symlink_to`直前に再検証。Source/destination root、missing parent、nested leaf、symlink read後parentのdeterministic swap testsを含むfocused32 pass、Workbench関連109 pass、lint pass、provider/dogfood parity pass。Fresh `gpt-5.6-sol` medium code-reviewer pass、P0-P3なし | 最後の`lstat`からprimitiveまでの極小TOCTOU、full dirfd transaction/rollbackはEC-316-005の明示的scope外 |
| D-316-006 | resolved | execution infrastructure | user during Issue execution | DevCoderとcode/QA/spec reviewerの固定model/reasoning設定がtask-specificな実行時選択を妨げる | 固定値維持; 全role unpin; 指定4roleだけunpin | `dev-coder`、`code-reviewer`、`qa-reviewer`、`spec-reviewer`だけprovider authorityとdogfood mirrorから`model`/`model_reasoning_effort`を削除し、今回の残作業は起動時に`gpt-5.6-sol` / `medium`を明示する | Userの明示指示を最小差分で適用し、他13 roleのfixed profileを維持する。Workbench product semanticsは変更しない | applied | 対象8 TOMLは各2行削除のみ、4/4 byte parity、taxonomy test 1 pass、other-role audit pass、fresh `gpt-5.6-sol` medium code-reviewer pass、P0-P3なし | Invocation-time model指定の一般smokeはIssue scope外。以後の本Issue DevCoder/reviewer起動バナーで個別確認 |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-316-001 | partially_adopted | `artifacts/20260713t072536z-research-chatgpt-5-6-pro-issue-planning-evidence.md` | GPT-5.6 Pro research/evidence producer | Parent trace、target parity、independent scope resolution、source-wins merge、symlink/containment、step/test proposal | `requirement.md`、`design.md`、`plan.md` | requirement全体、design contracts、closure/step/test候補 | 親Epicとcurrent repoで検証可能なcontractだけを採用し、候補module/error field名、未実行test/pass claim、runtime authorityと異なるstrict候補はauthority化しない | high for proposal, unverified for execution | SHA-256 `c65aa09c49271beb0bbef87aa4c210c6a6a227a46cc05509acf8c52e5c238765` | main orchestrator | requirement r3 pass、design r2 pass、plan r2 pass | no | Planning integration complete; implementation evidenceは各stepで別記録 |
| EAL-316-002 | partially_adopted | current repo inventory | repo-analyst | Existing selector再利用、source/target別`NodeRepository`解決、provider layers/test surfaces | `design.md`、`plan.md` | responsibility/change surface/dependency order/verification | Current symbolsとtestsに基づくshared resolver、copy eligibility分離、independent scope、layer/test surfaceを採用。Exact helper/file allocationはcode reviewで最小化する | high, current checkout inspection | parser/registry/worktree/application/ports/bootstrap/fs/presentation/tests inventory | main orchestrator | fresh plan r2 passed | no | Implementationでcurrent diffを再確認し各fresh code review |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-316-001 | 明示one-shot scoped Workbench handoff、destination-only保持、source wins | Selector parity、containment、output secrecy、focused regressionとIssue 319へのdistribution relay | 完全transactionへ拡張せず、changed-premiseをfail-closedにする境界を維持する | D-316-005 remediation、final QA、issue-wide code review、fresh final spec review、commit、push/clean確認済み。Issue Finishへ進む |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Parent Epic W2、Issue 315 result、current runtime/tests、GPT-5.6 planning evidence | Product open questionなし。Exact internal namesはdesign local delta | partially_adopted/re-written | passed | no | promote |
| design | Reviewed requirement、current layered runtime/tests、GPT-5.6 evidence、repo inventory、fresh design reviewer r2 | Product open questionなし。Exact symbol/error名はimplementation freedom | partially_adopted/re-written | passed | no | promote |
| plan | Reviewed design、standard authority、GPT-5.6 planning evidence、repo inventory、issue-plan schema、fresh plan reviewer r2 | Product open questionなし。S01/S03責任境界とstep-local report destinationを修正済み | partially_adopted/re-written | passed | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used
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
| ChatGPT 5.6 Pro evidence producer | iss-00316 | `artifacts/20260713t072536z-research-chatgpt-5-6-pro-issue-planning-evidence.md` | GitHub current branch、parent Epic、Issue 315、runtime/docs/tests | requirement/design/plan candidates | integrated | `requirement.md`、`design.md`、`plan.md` | passed | 全canonical planning artifactへ検証・再記述 | exact module/error/result field名、未実行test/pass claim、strict候補 | none | passed | execute approved plan |

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
- S01–S06のruntime/CLI/test実装とS90 docs impact判定を完了し、各step commitをpush済み。
- Final reviewで発見したcopy-time identity/missing-premise P1はD-316-005 r3で解決し、fresh bounded code-reviewがpassした。
- User指示により4 execution roleのmodel/reasoning固定を解除し、provider/dogfood parityとtaxonomy回帰を追加した。Fresh final QA、issue-wide code review、fresh final spec review、implementation commit `5fbd0af0`のpush/clean確認まで完了し、残るactionはreport-only closure commitとIssue Finishである。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-13 S00 planning/baseline）

#### 対象
- Step: S00 Baseline、assurance、planning closure。
- Closure: C316-02 baseline、implementation readiness。

#### 実施内容
- GitHub-synced GPT-5.6 Pro evidenceとcurrent repo inventoryをcanonical requirement/design/planへ段階統合した。
- Fresh spec-review: requirement r3 pass、design r2 pass、plan r2 pass。
- Runtime authorityは`authorized_profile=standard`。GPT候補のstrict self-claimは採用していないが、symlink/containment、copy-time partial failure、manual linked-worktree obligationsをplanに保持した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock assurance verify --issue iss-00316 --format json
# ok=true, status=valid, authorized_profile=standard

uv run pytest tests/cli_runtime/test_worktree.py -q
# 51 passed in 53.00s

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=209

git diff --check
# pass

./spec-dock/scripts/spec-dock guidance issue-execution
# state=ready, may_execute_approved_plan=true
```

#### S00 closure
- Planning evidenceはEAL/Delegated Draft/Spec Authoring/Grade Specialist/Reviewer Gateへ記録済み。
- Product open question、unresolved stale/blocked EAL、assurance staleなし。
- Planning commit `aed3b3f429d713b347a4fe1ed401571608a7242a`をpushし、upstream差`0 0`、cleanを確認した。

### セッションログ（2026-07-13 S01 shared target resolver）

#### 対象
- Step: S01 Existing target selectorの最小共有化。
- Closure: C316-02。

#### 委任と実施内容
- Fresh dev-coderへtarget-record selector boundaryの抽出とcharacterizationだけを委任した。
- `_resolve_target`をnew `application/worktree_target.py::resolve_worktree_target`へ意味論不変で移動し、existing show/remove/re-resolveが共有boundaryを利用する。
- Copy command、copy eligibility、ports/filesystem/presentation、dogfood projectionは未変更。

#### テスト駆動開発証跡
| フェーズ | 観測証跡 | 結果 |
|---|---|---|
| Baseline/Alternative | Existing CLI selector 3 cases | 3 passed |
| Red | Shared `resolve_worktree_target`未提供 | expected `AttributeError` |
| Green | New boundary focused 4、full worktree suite | 4 passed / 52 passed |
| Refactor | Ruff、mypy 3 source files、diff check | pass |

#### 具体的な検証
```bash
uv run pytest -q tests/cli_runtime/test_worktree.py
# 52 passed（worker）、fresh reviewer独立再実行pass

uv run ruff check <affected files>
# All checks passed

uv run mypy <3 source files>
# Success: no issues found

git diff --check
# pass
```

#### Closure / review
- `tc-s01-001`: ID/absolute path/unique basename/external linked target parity pass。
- `tc-s01-002`: Ambiguous basename/branch-only stable failure pass。
- Same-current/bare/path-missingはdesignどおりS03 copy eligibilityへ残した。
- Fresh code-reviewer: pass、P0/P1/blocking/nonblockingなし。
- Ledger Note: Material implementation decision/plan deviationなし。

### セッションログ（2026-07-13 S02 thin vertical happy path）

#### 対象
- Step: S02 Parser-to-filesystem minimal copy path。
- Closure: C316-01、C316-03/C316-05/C316-09の最小経路。

#### 委任と実施内容
- Fresh dev-coderへparser/command/application/ports/infra/presentationを通るsingle ordinary fileのvertical sliceを委任した。
- `workbench copy --scope <full-id> --to <selector> [--json]`を追加し、source=current固定、S01 resolver共有、source/target別node inventory、target側renamed scope pathを用いた。
- Text/JSONはexperimental/noncanonical/disposable/one-shot/no-syncを示し、body/entry listを出力しない。
- S03の全preflight、S04 recursive merge、S05 full symlink safety、S06 final failure presentationは未着手。

#### テスト駆動開発証跡
| フェーズ | 観測証跡 | 結果 |
|---|---|---|
| Red | `workbench` parser未認識 | 2 expected failures |
| Green | New Workbench focused tests | 2 passed |
| Regression | Workbench + existing Worktree | 54 passed、fresh reviewer独立再実行54 passed |
| Refactor | Ruff、mypy 131 source files、format、diff check | pass |

#### Closure / review
- Different target slugへsingle file bytesをcopyし、同command再実行成功、authority isolation markers/body非露出を確認した。
- Fresh code-reviewer: pass、P0/P1/blockingなし。
- Nonblocking relay:
  - Source変更後のexplicit source-wins感度はS04 C316-05で必須。
  - Ancestor symlink/TOCTOU/recursive/empty/no_source/stable failureはS03–S06で閉じる。
  - Destination root作成後のcopy failureはS05/S06で`mutation_started`相当を正直に表現する。
- Ledger Note: Approved planどおりのdeferred obligationsでありplan amendmentなし。

### セッションログ（2026-07-13 S03 independent scope/preflight）

#### 対象
- Step: S03 Independent scope、copy eligibility、pre-mutation failure。
- Closure: C316-02、C316-03、C316-04。

#### 委任と実施内容
- Fresh dev-coderへcopy application eligibility、source/target side別scope解決、`no_source`、empty/malformed rootを委任した。
- `WorkbenchCopyError(code, side, mutation_started)`とcontent-free rendererを追加し、same-current/bare/path-missing、missing/duplicate/invalid/unsupported scope、direct file/symlink Workbench rootをcopy前に拒否する。
- `FilesystemGateway.path_kind`は`lstat`を使いbroken symlinkをdereferenceしない。Empty sourceだけはminimal adapterでtarget directory作成successとした。

#### テスト駆動開発証跡
| フェーズ | 観測証跡 | 結果 |
|---|---|---|
| Red | Error/preflight contract欠如 | 15 failed / 2 passed（fixture 1件修正） |
| Green | Focused application + CLI | 28 passed、fresh reviewer再実行28 passed |
| Regression | Related selector cases | 3 passed |
| Refactor | Ruff/format/mypy/diff check | pass |

#### Closure / review
- Same ID/different slug、source/target side別missing/duplicate/invalid、invalid ID normalizationを確認。
- Same-current/bare/path-missingはscope load/copy未呼出し、`no_source` absent/existing target sentinel不変、empty success、malformed roots external影響なし。
- Fresh code-reviewer: pass、P0/P1/blockingなし。
- Nonblocking: trim/lowercase positive regressionとbroken-symlink固有caseはS05/S06で必要性を再評価。Current `lstat` pathはreview確認済み。
- Ledger Note: Observable contract変更、scope creep、plan amendmentなし。

### セッションログ（2026-07-13 S04 recursive source-wins merge）

#### 対象
- Step: S04 Dedicated guarded recursive merge。
- Closure: C316-05、C316-06。

#### 委任と実施内容
- Fresh dev-coderへfilesystem adapterとfocused infra testsだけを委任した。
- Destination-only保持、same leaf source-wins、nested merge、repeat idempotency、opaque mixed bytes、leaf symlink non-deref replacement、directory/non-directory collision保全、empty source、unsupported special failureを実装した。
- Classifier/manifest/counter/transaction/rollback/generic frameworkは追加していない。

#### テスト駆動開発証跡
| フェーズ | 観測証跡 | 結果 |
|---|---|---|
| Red | Recursive mixed treeをsingle-file adapterが拒否 | 1 expected failure |
| Green | Infra + application + CLI focused | 36 passed |
| Fresh review rerun | Application + infra | 28 passed |
| Refactor | Ruff/format/mypy/diff check | pass |

#### Closure / review
- Source変更後のexplicit overwriteと3回目snapshot equalityでsource-wins/idempotencyへ感度を持たせた。
- Binary/archive/`.env`/Python/config/nested `.git`のbytes一致、destination-only/外部symlink target/type-collision subtree保全、FIFO failureを確認。
- Fresh code-reviewer: pass、P0/P1/blocking/nonblockingなし。
- S05へsource descendant symlink object、injected I/O、TOCTOU/ancestor containment、`mutation_started`をrelay。
- Ledger Note: No material implementation decisions beyond approved DES-316-005 entry matrix。

### セッションログ（2026-07-13 S05 symlink/containment/failure）

#### 対象
- Step: S05 Security/path and partial-failure boundary。
- Closure: C316-07、C316-08、C316-09。

#### 委任と実施内容
- Fresh dev-coderへcomponent-wise ancestry guard、source descendant symlink object、destination traversal guard、fault mappingを委任した。
- Fresh security review r1で2 P1、r2で1 P1を検出し、各remediationを別fresh dev-coderへ委任した。
- Final r3でP0/P1/blockingなしを確認した。

#### テスト駆動・修正証跡
| Phase | Evidence | Result |
|---|---|---|
| Initial Red | Symlink/containment/fault contract | 9 failed / 29 passed |
| Initial Green | S03–S05 focused | 52 passed |
| Review r1 | Guard-before-reader gap、mutation false-positive | fail: P1 x2 |
| Remediation 1 | Schema ancestry pre-read guard、atomic primitive mark timing | focused87 pass |
| Review r2 | Unexpected directory/root `.meta.json` surface gap | fail: P1 x1、reviewer57 pass |
| Remediation 2 | Full initiatives discovery mirror、exact Workbench prune | focused63 pass |
| Review r3 | Security/path final | pass、63 passed、P0/P1=0 |
| Static | Ruff/format/mypy/diff check | pass |

#### Closure / review
- Repo/specdock/scope/Workbench ancestorをresolve-before-guardせずcomponent-wise検査し、NodeRepositoryの全metadata discovery surfaceをread前にguardする。
- Source descendant broken/external symlinkはlink text object、destination ancestryはexternal sentinel不変、leaf link自身だけ置換。
- Pre-mutation mkdir/unlink/symlink failureは`mutation_started=false`、successful removal後/partial copy2はtrue。Raw OSError/body/canonical claimなし。
- Fresh security reviewer r3: pass。Nonblockingはfuture `fs_repo` discovery変更時のguard/test同期のみ。
- Ledger Note: D-316-003/004へresolved/appliedとして統合。Plan amendment不要。

### セッションログ（2026-07-13 S06 output/regression/manual relay）

#### 対象
- Step: S06 Public contract、focused compatibility、manual linked-worktree handoff。
- Closure: C316-01、C316-02、C316-09、C316-10。

#### 委任と実施内容
- Fresh dev-coderへhelp/text/JSON contract、copy-only selector error sanitization、opacity regression、normal dogfood projection、manual two-worktree scenarioを委任した。
- Copy helpにexperimental/noncanonical/disposable/one-shot/no-sync/copy-back boundaryを追加し、forbidden optionsをtestsで固定した。
- Copy-only selector failureをcontent-free `WorkbenchCopyError`へ写像し、existing worktree outputは変更していない。
- Normal `uvx --from . spec-dock update .`でdogfood runtimeへ投影し、provider primary authorityを維持した。

#### Automated evidence
| Lane | Result |
|---|---|
| Workbench CLI/application/infra/presentation | worker71 passed、reviewer71 passed |
| Worktree/validate/sync/deps/Issue315 opacity | worker34 passed、reviewer30 passed/51 deselected |
| Provider/dogfood runtime compare | source code差分なし、cacheのみ除外 |
| Ruff/format/mypy/diff check | pass |
| Dogfood help smoke | pass |

#### Manual linked-worktree evidence
- Managed temp: `/private/tmp/codex-agent-work/501/session-20260713t094151z-issue316-manual-linked-worktrees-52798b66`。
- Same `iss-00316`、target slug `iss-00316-manual-target-renamed`。Sourceに`.env`、binary、nested `.git/config`、source/same leaf、broken symlink、targetにsame/target-onlyを配置。
- Basename `--to target`とscope `' ISS-00316 '`でsuccess。Target renamed slug使用、target-only保持、same source-wins、binary/.env/.git hashes一致、link text `../missing-target`。
- Absolute path rerun後、6 ordinary file hash不変。Same-current=`target_ineligible`、no-source=`no_source`、双方`mutation_started=false`、target-only hash不変。

#### Closure / review
- Success/failure text/JSONはmarkersとstable code/side/mutationだけを持ち、raw selector/path/candidate/message/body/entry list/rollback claimを含まない。
- Copied fake metadata/ADR/dependencyはvalidate/sync/depsに発見されずbytes保持。
- Fresh code-reviewer: pass、P0/P1/blocking/nonblockingなし。
- Issue319 relay: package/fresh init/update、public reference docs、full suite/static、final inventory parity、Epic PRは未実施。
- Ledger Note: S06 C316-01/02/09/10 closed。No new product semantics。

### セッションログ（2026-07-13 S90 docs impact）

#### 対象
- Step: S90 Docs impact resolution。
- Closure: C316-10 docs ownership。

#### 委任と点検
- Fresh doc-writerがprovider/dogfood `guide.md`、`README.md`、`reference_worktree.md`、implemented help/text/JSON、Epic W5 ownershipを点検した。
- `workbench copy --help`がexperimental/noncanonical/disposable/one-shot/scoped/no sync/copy-back、引数を自己完結説明する。
- README command listは非網羅、`reference_worktree.md`はworktree family限定であり、新command不存在を示す誤情報はない。

#### 判断 / review
- Approved no-op。Permanent docs変更なし。
- Provider/dogfood `guide.md`/`reference_worktree.md` cmp一致、live help 3 surfaces、`git diff --check` pass。
- Fresh spec-reviewer: pass、blockingなし。
- Issue319 relay: Consolidated Workbench/Artifact import/reference docs、root manual-selection、source-wins/no-sync、placement/date/authority、migration/preservation。
- Ledger Note: Partial docs updateはW5統合guideとの二重管理になるため、本Issueはcommand-local contractで閉じる。

### セッションログ（2026-07-13 S99 remediation r3 / execution-role unpin）

#### 対象
- D-316-005: copy-time directory/leaf identity差し替えのfail-closed remediation。
- D-316-006: user指示によるDevCoderとcode/QA/spec reviewerのmodel/reasoning固定解除。

#### 実施内容
- DevCoderを`gpt-5.6-sol` / reasoning `medium`で起動し、source/destination directory identity、destination parent identity、existing/missing leaf premiseを各read/mutation boundaryで再検証した。
- Initially-missing leaf出現とpost-unlink leaf再出現をordinary file/symlinkの双方でdeterministicに注入し、外部sentinel不変、link object保持、`mutation_started`の前後整合を検証した。
- Provider authorityとdogfood mirrorの4 role TOMLから固定2 keyだけを削除し、他roleのfixed profileとpermission/prompt属性を維持するtaxonomy regressionを追加した。

#### 検証 / review
- Workbench: focused infra 32 pass、Workbench関連109 pass、`make lint` pass（mypy 231 filesを含む）、`git diff --check` pass、provider/dogfood `fs_cli.py` parity pass。
- Config: taxonomy focused 1 pass、対象4 roleの4/4 byte parity、他13 role fixed-key audit、対象diff check pass。
- Fresh `gpt-5.6-sol` / medium code-reviewer: Workbench remediation pass（P0-P3なし）。Full dirfd transaction、atomicity、rollback、最後の検査からprimitiveまでの極小TOCTOUはEC-316-005のscope外。
- Fresh `gpt-5.6-sol` / medium code-reviewer: role unpin pass（P0-P3なし）。Invocation-time一般smokeはscope外だが、各reviewer起動バナーでmodel/effortを確認した。
- Ledger Note: D-316-005/D-316-006 resolved/applied。Fresh final QA、issue-wide code review、fresh final spec reviewはpass済み。Implementation commit `5fbd0af0`をpushし、clean/upstream `0 0`を確認した。

### 実装横断ゲート

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user request to use `spec-dock-epic-execution` / `spec-dock-issue-planning` / `spec-dock-issue-execution` | `/Volumes/990p2t/offloaded/home/iwasawayuuta/.codex/worktrees/bcea/spec-dock` | iss-00316 | current Work3 session | spec-manager / repo-analyst / ChatGPT evidence producer / spec-reviewer / dev-coder / code-reviewer / qa-reviewer / doc-writer | active repo/worktree、active scope、current session、SpecDock-defined role responsibility。破壊的操作、scope expansion、external publish/mergeは含めない | issue complete / session end / scope change / user revocation | none | workflowを継続し各fresh gateを記録 |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | Shared selector boundary抽出とcharacterization | dev-coder | application worktree target resolver + focused tests | requirement/design/plan S01/C316-02 | `application/worktree.py`、new `application/worktree_target.py`、`test_worktree.py` | Copy command/eligibility/fs/presentation/dogfood/canonical docs | focused/full worktree pytest、Ruff、mypy、diff check | Public semantics変更、scope外refactor、baseline failure | worker summary/changed files/Red-Green/tests/risks/Ledger Note | pass |
| S02 | delegated | Multi-layer minimal vertical behavior | dev-coder | parser→command→application→ports/infra→presentation + focused tests | requirement/design/plan S02/C316-01/03/05/09 | Provider runtime candidate filesとnew `test_workbench.py` | S03–S06 obligations、root/--from/sync/classifier、dogfood/canonical docs | focused/combined pytest、Ruff、mypy、format、diff check | Resolver複製、source path転写、body漏洩、scope外変更 | worker summary/changed files/Red-Green/tests/risks/Ledger Note | pass |
| S03 | delegated | Independent scope/pre-mutation error matrix | dev-coder | copy application/contracts/path-kind/error rendering + focused tests | requirement/design/plan S03/C316-02/03/04 | Workbench application/contracts/ports/bootstrap/command/fs/presentation/tests | S04 recursive matrix、S05 ancestor/mid-copy、root/sync/classifier/canonical docs | focused app/CLI、selector regression、Ruff/format/mypy/diff | Mutation前target change、source path転写、raw error漏洩 | worker summary/changed files/Red-Green/tests/risks/Ledger Note | pass |
| S04 | delegated | Recursive merge/content opacity | dev-coder | filesystem adapter + focused infra/application/CLI tests | requirement/design/plan S04/C316-05/06 | `infra/fs_cli.py`、new infra tests、必要最小限のadapter test fixtures | S05 ancestor/mid-copy、classifier/manifest/counter/rollback、canonical docs | focused pytest、Ruff/format/mypy/diff | Whole replacement、data loss、symlink deref、silent skip | worker summary/changed files/Red-Green/tests/risks/Ledger Note | pass |
| S05 | delegated | Security/path/failure boundary + two remediation batches | dev-coder | Workbench application/contracts/ports/fs/presentation + focused tests | requirement/design/plan S05/C316-07/08/09 | Current Workbench runtime/test files | Transaction/rollback/TOCTOU complete prevention、S06 docs/manual/dogfood | focused S03–S05、external observer/fault tests、Ruff/format/mypy/diff | External read/write、false mutation signal、raw error leak | worker summaries/findings/fixes/tests/risks/Ledger Notes | pass after r3 |
| S06 | delegated | Public output/regression/manual relay | dev-coder | Provider output/tests + normal dogfood projection + managed temp manual | requirement/design/plan S06/C316-01/02/09/10 | Missing provider runtime/tests、generated dogfood runtime | Public reference docs、package/fresh update/full gate/PR、new semantics | focused suites、parity、manual scenario、Ruff/format/mypy/diff | Content leak、dogfood-only patch、W5 scope invasion | changed files/tests/manual/relay/Ledger Note | pass |
| S90 | delegated | Docs impact inspection | doc-writer | Provider/dogfood public docs + live help + W5 boundary | requirement/design/plan S90/C316-10 | Docs only if misinformation; otherwise no-op | Issue317/318 semantics、final rollout/migration、code/tests | docs inspection/cmp/live help/spec review | Partial docs duplication、future semantics | changed files or no-op rationale/inspected paths/Ledger Note | approved-no-op |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Existing selectorをshared application boundaryへ意味論不変で抽出 | `application/worktree.py`; new `application/worktree_target.py`; `test_worktree.py` | focused4/full52 pass、Ruff/mypy/diff pass | fresh code-reviewer pass | none | accepted |
| S02 | dev-coder | Minimal `workbench copy` vertical slice、independent scope resolution、authority markers | contracts/ports/new workbench command+app/parser/registry/bootstrap/fs/presentation/new tests | Red2→Green2、combined54、Ruff/mypy/format/diff pass | fresh code-reviewer pass | S03–S06 planned obligations | accepted |
| S03 | dev-coder | Eligibility、side-specific scope errors、no_source/empty/malformed root、mutation probes | Workbench application/contracts/ports/bootstrap/command/fs/presentation、CLI+unit tests | Red15/2→Green28、selector3、Ruff/format/mypy/diff pass | fresh code-reviewer pass | Trim/lower positive and broken-link case nonblocking | accepted |
| S04 | dev-coder | Dedicated recursive source-wins mergeとopaque bytes/type collision tests | `infra/fs_cli.py`; new infra test | Red1→focused36、reviewer28、Ruff/format/mypy/diff pass | fresh code-reviewer pass | S05 planned safety/failure closures | accepted |
| S05 | dev-coder + two fresh remediation workers | Ancestry/inventory guard、symlink object、mutation tracking、content-free failures | Workbench application/contracts/ports/bootstrap/fs/presentation + unit/infra/CLI/presentation tests | Red9→52、fix1 87、fix2/r3 63、Ruff/format/mypy/diff pass | r1 fail P1x2、r2 fail P1x1、r3 pass | Future fs_repo discovery sync | accepted after remediation |
| S06 | dev-coder | Help/output matrix、copy error sanitization、opacity regression、dogfood projection、manual handoff | provider parser/command/presentation/tests + generated dogfood runtime | automated71+34、reviewer71+30、parity/manual/static pass | fresh code-reviewer pass | Issue319 final distribution/docs/full gate | accepted |
| S90 | doc-writer | Command-local help sufficient、public docsはnon-misleading、W5 ownership | none | inspected paths/live help/provider-dogfood cmp/diff pass | fresh spec-reviewer pass | Issue319 docs scaffold must be concretized later | approved-no-op |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| N/A | Parentによるsource/test直接実装なし。全stepをnamed workerへ委任 | N/A | N/A | reportのorchestrator統合のみ | N/A | fresh reviewer gates | code/spec/QA reviewer | unavailable/waiverなし |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `lite` | not applicable | not applicable | `lite_candidate=false` | not applicable | not applicable |
| `standard` | manual fallback | used | Dedicated specialistを追加利用せず、既に取得済みのGPT-5.6 Pro architecture/implementation-plan候補とcurrent repo inventoryを重複なく統合。Source: parent/Issue315/current parser-registry/application/ports/infra/presentation/tests、issue-plan schema。Symlink/containment、copy-time partial failure、manual linked-worktreeを追加obligationとしてplanへ維持。 | passed | ready |
| `strict` | not applicable | not authorized | Runtime authorityはstandard。GPT候補のstrict self-claimは採用しない | not applicable | not applicable |
| `critical` | not applicable | not authorized | Critical triggerなし | not applicable | not applicable |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| PLANNING | requirement/design/plan authoring | spec-reviewer | fresh | passed | no | execute approved plan | requirement r3、design r2、plan r2 pass |
| S01 | step reviewer | code-reviewer | fresh | passed | no | proceed | P0/P1/blocking/nonblockingなし |
| S02 | step reviewer | code-reviewer | fresh | passed | no | proceed | P0/P1/blockingなし、planned relay 3件 |
| S03 | step reviewer | code-reviewer | fresh | passed | no | proceed | P0/P1/blockingなし、nonblocking tests 2件 |
| S04 | step reviewer | code-reviewer | fresh | passed | no | proceed | P0/P1/blocking/nonblockingなし |
| S05 | security/path reviewer | code-reviewer | fresh | passed | no | proceed | r1/r2 P1 remediation後r3 P0/P1=0 |
| S06 | step reviewer | code-reviewer | fresh | passed | no | proceed | P0/P1/blocking/nonblockingなし |
| S90 | docs impact reviewer | spec-reviewer-history | fresh | passed | no | proceed | approved-no-op、blockingなし |
| S99-pre-remediation | final integrated code review | code-reviewer | fresh | failed | no | block Issue Finish | P1: copy-time source/destination directory identity差し替えで境界外read/writeの可能性。D-316-005 |
| S99-report-audit | final integrated spec review | spec-reviewer-history | fresh | conditional_pass | no | report修正後に再review | 実装整合はpass-quality。report placeholder、closure/QA/relay evidence不足を修正する |
| S99-report-recovery | report-only recovery review r2 | spec-reviewer | fresh | passed | no | execute approved plan: D-316-005 bounded remediationのみ | Managed Step Evidenceを実証跡参照へ置換。P1/closure/final gatesは未解決のまま正確。Issue Finish不可 |
| S99-remediation-r1 | D-316-005 remediation review | code-reviewer | fresh | failed | no | remediation r2 | Missing destination parent identity未検証、nested/actual mutation tests不足、symlink write直前gap。P1 x1 root-cause family |
| S99-remediation-r2 | D-316-005 remediation review | code-reviewer | fresh | failed | no | bounded remediation r3 | Destination leaf missing premiseをcopy2/symlink_to直前に未検証。反証でexternal sentinel上書き。P1 x1同一family。要求が明確な局所修正のためscope拡張なしで継続 |
| S99-remediation-r3 | D-316-005 remediation review | code-reviewer | fresh | passed | no | proceed to final gates | Directory/parent/leaf identity・missing premiseをboundaryで再検証。Deterministic race tests、external sentinel不変、focused32 pass。P0-P3なし |
| S99-role-unpin | user-injected execution infrastructure review | code-reviewer | fresh | passed | no | include in final gates | 4 roleだけ固定key削除、他13 role維持、provider/dogfood parity、taxonomy test pass。P0-P3なし |
| S99-final-qa | final issue obligation coverage | qa-reviewer | fresh | passed | no | proceed to issue-wide code review | Focused36、unit1066、CLI1135 pass/75 skip、lint/assurance/validate/parity/diff pass。Integration不要。P0-P3なし |
| S99-final-code | final issue-wide integrated code review | code-reviewer | fresh | passed | no | proceed to final spec review | Planning後全implementation commits + current remediation/config/report。Workbench80、role taxonomy含む33、assurance/validate/parity/diff pass。P0-P3なし、confidence 0.97 |
| S99-final-spec-r1 | final specification alignment | spec-reviewer | superseded | failed | no | report-only correction then fresh re-review | r2に置換済み。実装/spec/parent/relayは整合。Final QA/codeをpendingとするstale report claim 3箇所がP2だった |
| S99-final-spec-r2 | final specification alignment | spec-reviewer | fresh | passed | no | execute approved plan: commit and push/clean verification then Issue Finish | r1 stale claim解消、requirement/design/plan/report/implementation/tests/parent/Issue319 relay整合。P0-P3なし、confidence 0.99 |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| PLANNING/S00 | committed | Issue316 requirement/design/plan/report/assurance/GPT raw artifact | `aed3b3f429d713b347a4fe1ed401571608a7242a` | clean/upstream `0 0` | not applicable | planning artifacts | `git diff --check` pass | selector baseline 51 pass、validate/assurance/guidance ready |
| S01 | committed | shared target resolver + characterization + report | `bf54c810ad9fe71196e231814b95286e6faf6001` | clean/upstream `0 0` | not applicable | S01 contract | `git diff --check` pass | Fresh code-reviewer pass、full worktree 52 pass |
| S02 | committed | Minimal workbench copy vertical slice + tests + report | `fc0c77916dc4d9e4a094e5d403cd256cf1585f43` | clean/upstream `0 0` | not applicable | S02 contract | `git diff --check` pass | Fresh code-reviewer pass、combined54 pass |
| S03 | committed | Copy preflight/error contract + tests + report | `cd7e8759a92612eb61467bc24bc704ab07507da4` | clean/upstream `0 0` | not applicable | S03 contract | `git diff --check` pass | Fresh code-reviewer pass、focused28 pass |
| S04 | committed | Recursive merge adapter + focused tests + report | `84659dc3a840ba026ff7b80b6478a81be46c5bb3` | clean/upstream `0 0` | not applicable | S04 contract | `git diff --check` pass | Fresh code-reviewer pass、focused36/28 pass |
| S05 | committed | Symlink/containment/failure + remediation + report | `ffb54ebe24f6745ee5d503b1142234be76e87fc5` | clean/upstream `0 0` | not applicable | S05 contract | `git diff --check` pass | Security reviewer r3 pass、focused63 pass |
| S06 | committed | Output/regression/tests/dogfood projection/report | `2ff1cc946d3afb7a04c2354aaf6fb03ae516f2dc` | clean/upstream `0 0` | not applicable | S06 contract | `git diff --check` pass | Fresh code-reviewer pass、automated/manual/parity pass |
| S90 | committed approved-no-op evidence | No permanent docs; S90 evidence in report | `8ac45d18638d1d2e8ae5398d711a262e770b86f9` | clean/upstream `0 0` | Help self-contained、docs non-misleading、Issue319 consolidated owner | provider/dogfood guide/README/reference_worktree/help | `git diff --check` pass | Fresh spec-reviewer pass |
| S99 | committed | D-316-005 remediation + role profile unpin + tests + final ledger | `5fbd0af0b8c23bf779212543e6ab3a64dd660a65` | pushed、clean/upstream `0 0` | not applicable | Workbench race guards、4 role TOML、focused regressions | `git diff --cached --check` pass、commit hook pass | Final QA/code/spec pass、P0-P3なし |

### 要件・受け入れ条件・例外条件の最終closure状態

| 契約ID | 状態 | 観測証跡 / blocker |
|---|---|---|
| RQ-316-001 / AC-316-001 | pass | CLI/help/invalid args、no `--from`、root対象外。S02/S06 tests |
| RQ-316-002 / AC-316-002 | pass | Existing selector parity、same-current/bare/path-missing preflight。S01/S03/S06 tests |
| RQ-316-003 / AC-316-003 | pass | Source/target独立scope解決、same ID/different slug manual。S03/S06 |
| RQ-316-004 / AC-316-004 | pass | `no_source`、empty success、non-directory root failure、pre-mutation sentinel。S03/S06 |
| RQ-316-005 / AC-316-005 | pass | Recursive destination-only保持、source-wins、idempotency、type conflict保全。S04/S06 |
| RQ-316-006 / AC-316-006 | pass | Binary/archive/`.env`/Python/config/nested `.git` opaque byte copy。S04/S06 |
| RQ-316-007 / AC-316-007 | pass | Existing symlink/containmentに加え、source/destination root、missing parent、nested leaf、symlink read後parentのidentity swapをfail-closed化。External sentinel不変、D-316-005 r3 |
| RQ-316-008 / AC-316-008 | pass | Changed-premiseをcontent-free failureにし、mutation前=false、unlink後=trueをdeterministic testsで確認。D-316-005 r3 |
| RQ-316-009 / AC-316-009 | pass | Text/JSON authority markers、body/path/selector非露出。S02/S03/S05/S06 |
| RQ-316-010 / AC-316-010 | pass-with-final-relay-pending | Provider/dogfood parity、manual linked worktree、regression、S90 no-op。Issue319 final distributionは未実施 |
| EC-316-001–004 | pass | Empty source、broken/external symlink object、leaf replacement、directory/leaf conflict tests |
| EC-316-005 | pass | 検査前提崩壊をdeterministic swap testsでfailure化。最後の検査からprimitiveまでの極小TOCTOU、full dirfd transaction/rollbackは明示的非保証 |
| EC-316-006–009 | pass | Detached/locked classification parity、portable guard、malformed Workbench root tests |

### Spec-Locked Closure Index 状態

| Closure | 状態 | 証跡 / blocker |
|---|---|---|
| C316-01 | pass | S02/S06 CLI help・invalid argument contract |
| C316-02 | pass | S01 shared selector + S03 eligibility + S06 manual selector |
| C316-03 | pass | S03 independent resolution + S06 renamed target slug |
| C316-04 | pass | S03 missing/empty/malformed Workbench tests |
| C316-05 | pass | S04 recursive source-wins/destination-only/idempotency tests |
| C316-06 | pass | S04 opaque mixed bytes tests |
| C316-07 | pass | Existing symlink tests + directory/parent/leaf identity swap tests。Boundary外sentinel不変、fresh remediation review pass |
| C316-08 | pass | Injected I/O + initially-missing/post-unlink leaf appearance tests。Stable failure/mutation signal、fresh remediation review pass |
| C316-09 | pass | S02/S03/S05/S06 text/JSON and mutation signal tests |
| C316-10 | pass-with-Issue319-relay | S06 parity/manual/regression、S90 no-op。Epic W5はIssue319 owner |

### Issue319へのdeferred delivery relay

- Dependency evidence: `deps check iss-00319`は`iss-00316`、`iss-00317`、`iss-00318`をblockerとして列挙する。Issue319はIssue316完了後も全先行Issueを待つfinal quality ownerである。
- Current pushed implementation head: `5fbd0af0b8c23bf779212543e6ab3a64dd660a65`、clean/upstream `0 0`。Issue316 milestone commit一覧は直前のMilestone / Commit Candidate Gateを正本とする。
- Per-Issue PRを作らない理由: 親Epic planはIssue319にpackage/fresh init/update、consolidated docs、full suite/static、inventory parity、単一Epic PR deliveryを集約しており、中間Issue PRは同一feature branch chainを重複deliveryするため。
- Remaining W5 gates: Issue317 Artifact import、Issue318 placement/ignore rules、Issue319 package/fresh init/update、public docs/migration、full suite/static、final provider/dogfood/inventory parity、Epic PR observation。
- Issue316ではPR作成・PR監視・`merge-prepared`を実施または主張しない。Issue319のfinal gateまでdeferredである。

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | no（approved-no-op） | doc-writer | Command-local helpが自己完結し、既存docsは非網羅かつ非誤認。commit `8ac45d18` | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | pre-remediation whole issue obligation coverage | focused/manualで十分、integration suite不要 | unit 1056 pass + unrelated timing 1 fail/single rerun pass、CLI 1135 pass/75 skipped、focused73 pass、`make lint` pass、assurance/validate/parity pass | passed before P1 discovery; remediation後fresh gate required |
| qa-reviewer final | D-316-005 remediation + role unpinを含むwhole issue obligation coverage | `tests/integration`不要。Deterministic infra raceと静的agent設定はunit/CLI/full regressionで十分。Package/fresh init/updateはIssue319 owner | Focused36、taxonomy単独1、unit1066、CLI1135 pass/75 skip、`make lint`、assurance、validate、provider/dogfood parity、current diff pass | passed; P0-P3なし |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | P1: post-preflight directory swapでsource read / destination mutationがWorkbench境界外へ逃げ得る。deterministic source/target swap testsとidentity revalidationが必要 | 0 | fail / blocked |
| code-reviewer remediation | D-316-005 r3 + role-unpinを別々にbounded review | Workbench/configともP0-P3なし。極小TOCTOUはEC-316-005 scope外 | 3 remediation passes + 1 config pass | passed for bounded scope; issue-wide reviewは後続final rowでpass |
| code-reviewer final | planning後の全implementation commits + current remediation/config/report | P0-P3なし。D-316-005、mutation semantics、output secrecy、4 role限定unpin、mirror parity、Issue319 deferred boundary整合 | pre-remediation fail後のfresh issue-wide re-review 1 | passed; confidence 0.97 |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | 実装/spec整合はpass-quality。report placeholder、closure表、QA/code/spec/final commit、Issue319 relayの不足を指摘 | 0 | conditional_pass; report再review required |
| spec-reviewer r2 | report-only recovery | 全placeholderを除去し、D-316-005と関連closure/final gateを未解決として保持。実装再開可、Issue Finish不可 | 1 | passed |
| spec-reviewer final r1 | requirement / design / plan / report / final diff alignment | 実装/spec/parent/Issue319 relayは整合。Final QA/codeをpendingとするstale report claimをP2 1 root-causeとして指摘 | 2 | fail; report-only correction後fresh re-review |
| spec-reviewer final r2 | corrected report + requirement/design/plan/implementation/tests/parent/Issue319 relay alignment | r1 stale claim解消。P0-P3なし、confidence 0.99 | 3 | passed |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| D-316-005とrole-unpinの実装、final QA、issue-wide code review、fresh final spec review証跡を統合済み | D-316-005 remediation + role-unpin + final ledger | Issue319 final delivery / Epic PR | implementation commit `5fbd0af0` pushed、clean/upstream `0 0`。Report-only closure commit後にIssue Finish |

## 遭遇した問題と解決 (任意)
- 問題: Step-local security reviewを通過後、issue-wide final code reviewでpost-preflight directory identity swapのP1を発見した。
  - 解決: D-316-005 r3でdirectory/parent/leaf premiseをmutation/read boundaryで再検証し、deterministic regressionとfresh bounded code-reviewをpassした。
- 問題: DevCoderとreviewerのrepo設定がmodel/reasoningを固定し、今回の`gpt-5.6-sol` / `medium`指定をroleごとに自由に適用できなかった。
  - 解決: User指示により4 roleだけ固定keyをprovider/dogfood双方から削除し、taxonomy regressionとfresh code-reviewをpassした。今回の残作業では起動時にmodel/effortを明示する。
- 問題: `git diff --check 198fb155..HEAD`がraw GPT evidence artifact line 5のtrailing whitespaceを検出する。
  - 解決状況: SHA-256固定済みraw evidenceの内容不変契約を優先する明示exemptionとし、artifactを整形しない。実装・canonical docsのcurrent diff checkはcleanを要求する。

## 学んだこと (任意)
- Preflightのpathname検査だけではcopy-time changed-premiseを閉じられない。EC-316-005のfail-closed契約にはdirectory identity境界のdeterministic regressionが必要である。

## 今後の推奨事項 (任意)
- Issue319はIssue316へのdependency edge、Issue316 pushed head/commit列、per-Issue PRを作らない理由、残存Epic W5 gateを引き継ぐ。Issue316単独では`merge-prepared`を主張しない。

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- S00–S90のRed / Green / Refactor、manual、review、commit証跡は「実装記録（セッションログ）」に記録した。
- C316-01–10とRQ/AC/ECの観測結果は「要件・受け入れ条件・例外条件の最終closure状態」と「Spec-Locked Closure Index 状態」に集約した。D-316-005 r3によりC316-07/08はpassし、final QA/code/spec、implementation commitのpush/clean確認も完了した。
<!-- spec-dock:managed-section end id="report.step-evidence" -->
