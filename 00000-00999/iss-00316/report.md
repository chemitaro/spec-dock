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

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | dev-coder | Existing selectorをshared application boundaryへ意味論不変で抽出 | `application/worktree.py`; new `application/worktree_target.py`; `test_worktree.py` | focused4/full52 pass、Ruff/mypy/diff pass | fresh code-reviewer pass | none | accepted |

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
| S02–S06 | step reviewer | code-reviewer | pending | pending | N/A | blocked until each pass | 各step後にfresh review |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| PLANNING/S00 | committed | Issue316 requirement/design/plan/report/assurance/GPT raw artifact | `aed3b3f429d713b347a4fe1ed401571608a7242a` | clean/upstream `0 0` | not applicable | planning artifacts | `git diff --check` pass | selector baseline 51 pass、validate/assurance/guidance ready |
| S01 | ready for commit | shared target resolver + characterization + report | pending | pending | not applicable | S01 contract | `git diff --check` pass | Fresh code-reviewer pass、full worktree 52 pass |

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
