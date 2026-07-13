---
種別: 実装報告書（Issue）
ID: "iss-00316"
タイトル: "Experimental Scoped Workbench Copy And Source Wins Merge"
関連GitHub: ["#316"]
状態: "draft | approved"
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
| OAL-316-001 | 明示one-shot scoped Workbench handoff、destination-only保持、source wins | Selector parity、containment、output secrecy、focused regressionとIssue 319へのdistribution relay | 低。安全対策をcontent classifierやtransactionへ拡張せず、final distributionをIssue 319へ戻した | pass: fresh requirement reviewer r3 |

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
- Planning中。実装は未開始。

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

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Existing selectorをshared application boundaryへ意味論不変で抽出 | `application/worktree.py`; new `application/worktree_target.py`; `test_worktree.py` | focused4/full52 pass、Ruff/mypy/diff pass | fresh code-reviewer pass | none | accepted |
| S02 | dev-coder | Minimal `workbench copy` vertical slice、independent scope resolution、authority markers | contracts/ports/new workbench command+app/parser/registry/bootstrap/fs/presentation/new tests | Red2→Green2、combined54、Ruff/mypy/format/diff pass | fresh code-reviewer pass | S03–S06 planned obligations | accepted |
| S03 | dev-coder | Eligibility、side-specific scope errors、no_source/empty/malformed root、mutation probes | Workbench application/contracts/ports/bootstrap/command/fs/presentation、CLI+unit tests | Red15/2→Green28、selector3、Ruff/format/mypy/diff pass | fresh code-reviewer pass | Trim/lower positive and broken-link case nonblocking | accepted |
| S04 | dev-coder | Dedicated recursive source-wins mergeとopaque bytes/type collision tests | `infra/fs_cli.py`; new infra test | Red1→focused36、reviewer28、Ruff/format/mypy/diff pass | fresh code-reviewer pass | S05 planned safety/failure closures | accepted |
| S05 | dev-coder + two fresh remediation workers | Ancestry/inventory guard、symlink object、mutation tracking、content-free failures | Workbench application/contracts/ports/bootstrap/fs/presentation + unit/infra/CLI/presentation tests | Red9→52、fix1 87、fix2/r3 63、Ruff/format/mypy/diff pass | r1 fail P1x2、r2 fail P1x1、r3 pass | Future fs_repo discovery sync | accepted after remediation |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

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
| S06 | step reviewer | code-reviewer | pending | pending | N/A | blocked until pass | Public/regression/manual relay |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| PLANNING/S00 | committed | Issue316 requirement/design/plan/report/assurance/GPT raw artifact | `aed3b3f429d713b347a4fe1ed401571608a7242a` | clean/upstream `0 0` | not applicable | planning artifacts | `git diff --check` pass | selector baseline 51 pass、validate/assurance/guidance ready |
| S01 | committed | shared target resolver + characterization + report | `bf54c810ad9fe71196e231814b95286e6faf6001` | clean/upstream `0 0` | not applicable | S01 contract | `git diff --check` pass | Fresh code-reviewer pass、full worktree 52 pass |
| S02 | committed | Minimal workbench copy vertical slice + tests + report | `fc0c77916dc4d9e4a094e5d403cd256cf1585f43` | clean/upstream `0 0` | not applicable | S02 contract | `git diff --check` pass | Fresh code-reviewer pass、combined54 pass |
| S03 | committed | Copy preflight/error contract + tests + report | `cd7e8759a92612eb61467bc24bc704ab07507da4` | clean/upstream `0 0` | not applicable | S03 contract | `git diff --check` pass | Fresh code-reviewer pass、focused28 pass |
| S04 | committed | Recursive merge adapter + focused tests + report | `84659dc3a840ba026ff7b80b6478a81be46c5bb3` | clean/upstream `0 0` | not applicable | S04 contract | `git diff --check` pass | Fresh code-reviewer pass、focused36/28 pass |
| S05 | ready for commit | Symlink/containment/failure + remediation + report | pending | pending | not applicable | S05 contract | `git diff --check` pass | Security reviewer r3 pass、focused63 pass |

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
