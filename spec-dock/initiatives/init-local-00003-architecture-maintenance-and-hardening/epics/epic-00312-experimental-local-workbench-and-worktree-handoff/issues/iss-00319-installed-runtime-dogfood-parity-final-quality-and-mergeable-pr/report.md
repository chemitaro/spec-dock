---
種別: 実装報告書（Issue）
ID: "iss-00319"
タイトル: "Installed Runtime Dogfood Parity Final Quality And Mergeable PR"
関連GitHub: ["#319"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00312", "init-local-00003"]
---

# iss-00319 Installed Runtime Dogfood Parity Final Quality And Mergeable PR — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-319-001 | resolved | operation | main orchestrator | Root `.workbench/`はcurrent dogfood root `.gitignore`投影前で、Artifact import sourceとして不適格 | Rootから直接import; scope-localへ手動選択copy; preservation例外 | 完全回答一件だけをIssue319 scope-local `.workbench/`へbytes不変で手動copyし、そこからimportする | Root Workbenchを一括継承しない運用とruntime source eligibilityを同時に守る | applied | Root direct importは`source_ineligible` / `committed=false`。Scoped source importはEPE-319-001で`committed=true` | Root一時copyは削除済み。Scoped sourceはignoredのまま保持 |
| D-319-002 | resolved | scope | ChatGPT 5.6 Pro / main orchestrator | Bundled候補にversion bump、migration file、Linux/PR exact gateなど未検証候補を含む | 全採用; 全棄却; canonical authorityで段階採否 | Parent/Issue relayとlocal現物に一致するdistribution/final-quality候補だけをRequirementへ部分採用し、未検証候補はdefer/rejectする | ChatGPT self-claimをauthority/pass evidenceにせず、Issue319で実測するため | applied | EAL-319-001〜004、Requirement §8 | Requirement fresh review後、Design/Planへ順次promotion |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| ID | adoption_status | source | source_role | claim | target_artifact | target_section | rationale | evidence_strength | evidence_path | adopter | reviewer | blocking | next_action |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| EAL-319-001 | partially_adopted | `artifacts/20260714t110631z-chatgpt-output-issue-319-chatgpt-5-6-pro-bundled-planning-report.md` | external ChatGPT 5.6 Pro bundled draft | Requirement/Design/Plan、distribution topology、main integration、full/manual/review/PR順序候補 | requirement.md; design.md; plan.md | Requirement §§1–9 | Parent W5、Issue315–318 relay、local現物と一致する候補だけを採用。Current pass claimや未検証exact gateは不採用 | advisory + byte-preserved complete answer | EPE-319-001 | main orchestrator | Requirement r3 / Design r1 / Plan r2 passed | no | Execute approved plan |
| EAL-319-002 | adopted | Parent Epic W5/DS-005 and Issue315–318 relay | canonical parent/prior Issue evidence | Final distribution/docs/full quality/manual/Epic closure/PR ownership | requirement.md | §§2–7 | Reviewed canonical authorityでIssue319の責務とdependencyを固定する | canonical source-grounded | Parent Epic requirement/design/plan/report; Issue315–318 reports | main orchestrator | PLANNING-REQ-r3 passed | no | Execute approved plan |
| EAL-319-003 | deferred | ChatGPT bundled planning | external analysis | Version bump、`uv.lock`変更、dedicated migration file、exact Linux runner/required PR checks | future design.md/plan.md if proven | Requirement §§8–9 | Repository policy/runner/PR live stateを未検証で、Issue scope内の必要性がまだ確定しない | advisory unverified | EAL-319-001 Artifact | main orchestrator | PLANNING-REQ-r3 passed | no; revisit条件あり | S00/S01で現物確認し必要時だけ採用 |
| EAL-319-004 | rejected | ChatGPT alternative expansion | external analysis | Root bulk copy、automatic sync、classifier、typed `chatgpt-output`、blank reservation、ChatGPT pass self-claim | none | none | Parent/accepted ADR/Issue315–318 contractに反する | canonical conflict | EAL-319-001 Artifact; accepted ADR | main orchestrator | PLANNING-REQ-r3 passed | no | no_action; downstreamへ持ち込まない |
| EAL-319-005 | adopted | fresh system architecture review | system-architect `gpt-5.6-sol` / medium | Workbench root/ignore authority修正、final-head PR observation、exact parity exception、Ubuntu/static relay | design.md | §§4–11 | Parent/current filesと一致し、head-changing report commitによるstale evidenceを防ぐ | fresh specialist source-grounded review | Current parent/Issue315–318/provider CI/design diff | main orchestrator | PLANNING-DES-r1 passed | no after remediation | Execute approved plan |
| EAL-319-006 | adopted | fresh implementation planning review | implementation-planner `gpt-5.6-sol` / medium | Uncommitted main integration、managed wheel-only consumers、hermetic GitHub-linked fixture、issue-finish fail-safe、exact inventory | plan.md | S00–S100 | Approved designを実在command/fixture/review/commit順序へ落とし、4 blocking findingsを修復後pass | fresh specialist source-grounded review | Current runtime/help/tests/Issue315–318 relay/plan diff | main orchestrator | PLANNING-PLAN-r2 passed | no after remediation | Execute approved plan |

### External preservation handoff（content-free）

| evidence id | preservation_status | import_kind | storage_identity | source | destination | sha256 | byte_count | committed | warning_codes | adoption boundary |
|---|---|---|---|---|---|---|---|---|---|---|
| EPE-319-001 | imported_byte_exact | chatgpt-output | blank | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr/.workbench/issue319-chatgpt-5-6-pro-planning-report.md` | `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00312-experimental-local-workbench-and-worktree-handoff/issues/iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr/artifacts/20260714t110631z-chatgpt-output-issue-319-chatgpt-5-6-pro-bundled-planning-report.md` | `9352f5120661d61e65bc8591e466a4a69e0a55c6f871bf8d123199964b445641` | 85219 | true | none | Preservationはcanonical adoption/reviewer pass/readinessを意味しない。採否はEAL-319-001〜004で管理 |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-319-001 | Issue315〜318のaccepted capabilityをproviderからpackage/fresh/existing/dogfoodへ配布し、全E-RQ/E-ACと単一PR deliveryを閉じる | Latest main integration、public docs、static repair、manual evidence、PR checks/review observation | medium。副次repair/release作業がnew semantics/general refactor/version-release拡張へ逸脱し得るため、Requirement RQ-319-016とowning-contract routingで禁止 | PLANNING-REQ-r3 passed |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | Parent Epic、Issue315–318、accepted ADR、local git/package/docs/tests、EPE-319-001 | ChatGPT exact gates/version/migration/Linux/PR policyは実行時確認 | partial adoption; reject expansion; defer unverified | passed | no | promote |
| design | Approved requirement、assurance standard、ChatGPT Artifact、fresh system-architect、parent/current CI/static relay | Exact plan/test/commit stepはPlanで定義 | Partial ChatGPT adoption + system-architect findings adopted | passed | no | promote |
| plan | Approved requirement/design、ChatGPT Artifact、fresh implementation-planner、current command/test/runtime | PR terminal external evidenceは実行時観測 | Partial ChatGPT adoption + implementation-planner findings adopted | passed | no | promote |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
- 委任 authoring の使用:
  - used（ChatGPT 5.6 Pro bundled Requirement/Design/Plan candidate）
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
| ChatGPT 5.6 Pro | iss-00319 | `artifacts/20260714t110631z-chatgpt-output-issue-319-chatgpt-5-6-pro-bundled-planning-report.md` | Parent Epic、Issue315–318、accepted ADR、provider docs、package/tests | requirement.md、design.md、plan.md | partially_integrated | [requirement.md, design.md, plan.md] | passed: scoped import byte exact and canonical source cross-check passed | Bundled candidates integrated after parent/current-source correction | Unverified pass counts、exact gate invention、scope expansions | none | passed | promote |

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
| User request to use Epic/Issue planning/execution and ChatGPT | current Work3 checkout | iss-00319 | current session | spec-manager、repo-analyst、system-architect、implementation-planner、doc-writer、dev-coder、spec/code/qa-reviewer | Active repo/worktree/scope/current session/documented responsibility。Scope expansion/destructive/private external/out-of-workflow roleを含まない | Issue complete/session end/scope change/user revocation/host conflict | none | Continue workflow without per-role reapproval |

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
| standard | system-architect and implementation-planner | used | Fresh system-architect and implementation-planner `gpt-5.6-sol` / medium。Architecture findings二件、planning findings四件+fixture follow-up一件を修復後に各specialist passed | passed | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| PLANNING-REQ-r3 | requirement alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。Preservation/EAL/OAL、親trace、testable AC、authority/secrecy、PR ownershipを承認 |
| PLANNING-DES-r1 | design alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。System-architect remediation、distribution/update/parity/Linux/manual/PR final-head設計を承認 |
| PLANNING-PLAN-r2 | plan executability/alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。C319-01〜16、S00〜S100、main/wheel/fixture/static/final-head/lifecycle contractを承認 |
| PLANNING-FINAL-r1 | planning closeout alignment | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。ChatGPT原文保存、EAL/EPE/OAL、terminal review/specialist gate、assurance/readiness、Requirement/Design/Plan整合を承認 |
| S00-BASELINE-r2 | live baseline and exact inventory | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。GitHub/branch/pre-feature ref、37 exact pairs、14 generated rows、wheel/test/platform inventory、C319-01とS01 preconditionを承認 |
| S01-CODE-r1 | latest main integration | code-reviewer | fresh | passed | no | promote | findingsなし。Issue314 preflight/receiptとIssue315〜318 Workbench contract、provider/dogfood parity、test inventoryを承認 |
| S01-SPEC-r1 | latest main integration | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。Non-destructive merge、C319-02、accepted contracts、known raw Artifact exceptionを承認 |
| S02-CODE-r1 | package/fresh/update | code-reviewer | fresh | passed | no | promote | findingsなし。Cache exclusion/wheel/sdist/test sensitivity/cross-platform path、sdist→wheel再buildを承認 |
| S02-SPEC-r1 | package/fresh/update | spec-reviewer | fresh | passed | no | promote | P0〜P2なし、confidence 0.99。C319-03〜05、4 scope path/type/bytes/SHA保持、nonblocking metadata観察を承認 |
| S03-SPEC-r1 | public docs and dogfood parity | spec-reviewer | fresh | passed | no | promote | findingsなし、confidence 0.99。C319-06〜07、provider-first projection、7 docs pairs、semantic completeness、code-reviewer N/Aを承認 |
| S04-CODE-r1 | focused/full/static quality and repair | code-reviewer | fresh | passed | no | promote | Blocking findingなし。6 filesのstatic/test repair、runtime semantics不変、affected/full/static evidence、C319-08 closureを承認 |
| S04-QA-r3 | regression and platform quality | qa-reviewer | fresh | passed | no | promote | Blocking findingなし。Focused W1〜W4、affected/relay、unit/CLI/integration/full、static gateを確認。C319-09はlocal/config pass、PR Ubuntu実runをS100へ保持 |
| S05-SPEC-PREADOPT-r1 | pre-adoption checkpoint | spec-reviewer | fresh | passed | no | promote | findingsなし。Import bytes/source survivalを確認し、adoption pendingのままpreservationとadoptionを分離してEAL/rewriteへ進む境界を承認 |
| S05-SPEC-FINAL-r1 | installed integrated scenario | spec-reviewer | fresh | passed | no | promote | findings 0、confidence 0.99。Copy/import/EAL/rewrite順序、authority、opacity、secrecy、C319-10/15を承認 |
| S05-QA-r1 | installed integrated scenario | qa-reviewer | fresh | passed | no | promote | findings 0。Synthetic fixture、fake gh fail-closed、copy/import invariants、sync opacity、content-free evidenceを承認 |

#### レビュー修復履歴（Review Remediation History）
| ステップ（step） | 対象 | 検出事項 | 修復結果 |
|---|---|---|---|
| PLANNING-REQ-r1 | requirement alignment | EPE receipt/EAL未記録をblocking findingとして検出。Canonical本文findingなし | Preservation receiptとEALを記録し、r2で確認 |
| PLANNING-REQ-r2 | requirement alignment | r1修復後、Mandatory OAL placeholderをblocking findingとして検出 | OAL-319-001を具体化し、r3でpassed |
| PLANNING-PLAN-r1 | plan executability/alignment | Configured static authorityが`make lint`ではなく個別mypy/RuffになっていたためC319-08をblock | S04へauthority/repair順序を修復し、r2でpassed |
| S00-BASELINE-r1 | live baseline and exact inventory | Generated exceptionがdirectory/category levelでrefresh commandも曖昧 | Consumer canonical namespaceを分離し、14 exact generated entriesと実在refresh commandへ修復してr2でpassed |
| S04-STATIC-r1 | repository-wide static gate | Initial `make lint`でRuff/format/mypy violationsを検出 | 6 filesへformatとtest typingの最小修復を限定し、affected/full/staticを再実行 |
| S04-QA-r1 | static repair QA | Test double 2箇所のtype ignoreがplanのno skip/disable/exclude gateに抵触 | Source guard delegationへ置換し、type ignoreを削除して再検証 |
| S04-QA-r2 | runtime safety QA | Annotation/import修復がruntime `get_type_hints`利用時にP2 regressionを生む可能性を検出 | Runtime-resolvable collection imports/annotationsへ修復し、affected 652、relay 10+46、fresh r3 reviewでpassed |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S00 planning | committed | Issue319 Requirement/Design/Plan/Artifact/assurance/report | `7a3793de` | clean / upstream `0 0` | N/A | C319-01 planning/preservation/assurance | `git diff --check` passed | PLANNING-FINAL-r1 passed |
| S00 baseline | committed | Issue319 report live baseline only | `eb154791` | clean / upstream `0 0` | N/A | Exact GitHub/git/pair/exception/wheel/test/platform inventory | `git diff --check` passed | S00-BASELINE-r2 passed |
| S01 | committed | `origin/main` merge + five conflict resolutions + report evidence | `1230c456` | clean / upstream `0 0`、origin/main left 0 | N/A | Issue314/315〜318 accepted contracts、provider/dogfood conflict pairs | Conflict paths clean。Whole mergeはbyte-preserved raw Artifactの既知13行だけ例外 | S01-CODE-r1 / S01-SPEC-r1 passed |
| S02 | committed | Python cache packaging repair + wheel/fresh/update evidence + report | `09e84df2` | clean / upstream `0 0` | N/A | C319-03〜05、tc319-s02-01〜03 | `git diff --check` passed | S02-CODE-r1 / S02-SPEC-r1 passed |
| S03 | committed | Root/provider docs + candidate-wheel dogfood projection + report | `da59f73c` | clean / upstream `0 0` | N/A | C319-06〜07、tc319-s03-01〜03 | `git diff --check` passed | S03-SPEC-r1 passed / code-reviewer N/A (docs-only) |
| S04 | committed | Static/test repair 6 files + report evidence | `149771db` | clean / upstream `0 0` | N/A | C319-08、C319-09 local/config、tc319-s04-01〜04 | `git diff --check` / focused/full/static passed | S04-CODE-r1 / S04-QA-r3 passed |
| S05 | commit candidate | Installed integrated manual scenario report evidence only | 2026-07-14 S05 session ledger | verify after commit | N/A | C319-10、C319-15、tc319-s05-01〜03 | `git diff --check` passed | S05-SPEC-PREADOPT-r1 / S05-SPEC-FINAL-r1 / S05-QA-r1 passed |

#### 変更したファイル
- S00 planning: `requirement.md`, `design.md`, `plan.md`, `report.md`, `.assurance.json`, imported ChatGPT Artifact。
- S01 integration: `origin/main` merge、conflict resolution 5 files、`report.md`。
- S02 candidate: `pyproject.toml`, `setup.py`, `tests/unit/infra/test_init_update.py`, `report.md`。
- S03: `README.md`, provider/dogfood docs 7 exact pairs、`report.md`。
- S04: `scripts/authoring-pack/authoring_pack_review.py`, `scripts/authoring-pack/invoke_chatgpt_backend.py`, `tests/cli_runtime/test_artifact_import_chatgpt_output.py`, `tests/cli_runtime/test_artifact_import_s04.py`, `tests/cli_runtime/test_wrappers.py`, `tests/unit/infra/test_init_update.py`, `report.md`。
- S05 candidate: `report.md` only。

#### コミット
- `7a3793de` `docs(issue-319): ChatGPT原文保存と最終品質計画を確定`
- `eb154791` `docs(issue-319): S00ベースラインと配布在庫を記録`
- `1230c456` `chore(integration): origin/mainの先行Issue変更を最終品質ブランチへ統合`
- `09e84df2` `fix(packaging): wheelとsdistへのPythonキャッシュ混入を防止`
- `da59f73c` `docs(workbench): WorkbenchとArtifact importの公開運用契約を整備`
- `149771db` `chore(quality): 静的解析ゲート違反を最小差分で解消`
- S05 candidate: `docs(issue-319): installed手動統合証跡を記録`

#### メモ
- S00 live baselineの追加記録はplanning authorityを変更せず、report evidenceだけを更新する。

---

### セッションログ（2026-07-14 20:29 - 20:45 JST）

#### 対象
- Step: S00 Planning and live baseline
- AC/EC: C319-01、C319-02 precondition、C319-03〜10 target inventory

#### 実施内容
- Active contextはInitiative `init-local-00003` / Epic `epic-00312` / Issue `iss-00319`。
- GitHub #315〜#318はclosed、#312/#319はopen。Issue319 branchをheadに持つ既存PRは0件。
- `git fetch origin`後の`origin/main...HEAD`はleft 31 / right 54、merge-baseは`3acdd76ccec00367c420fe967a7ee74da3342ed9`。S01はmerge必須。
- Pre-feature existing-consumer baselineは`7def2c10e29078e82c6a30441e79fe7cee3b1883`。Workbench ignore導入`914abdf7`の直親で、当該assetに`.workbench/`がなく、既存init/update/package contractは存在するためfixture候補として採用。
- Planning Artifact/sourceはSHA-256 `9352f5120661d61e65bc8591e466a4a69e0a55c6f871bf8d123199964b445641`、85219 bytes、`cmp`一致、source ignoredを再確認。

#### Exact provider / dogfood inventory

Issue315〜318導入差分から抽出したexact pairはS00時点ですべてbyte-equal。Projection directionはprovider → dogfood、rebuild commandは`spec-dock update .`。Templates/systemの変更pairは0件。

| Provider authority | Dogfood projection | S00 |
|---|---|---|
| `src/spec_dock/assets/spec_dock/.gitignore` | `spec-dock/.gitignore` | equal |
| `src/spec_dock/assets/spec_dock/docs/authoring/chatgpt-pack.md` | `spec-dock/docs/authoring/chatgpt-pack.md` | equal |
| `src/spec_dock/assets/spec_dock/docs/README.md` | `spec-dock/docs/README.md` | equal |
| `src/spec_dock/assets/spec_dock/docs/guide.md` | `spec-dock/docs/guide.md` | equal |
| `src/spec_dock/assets/spec_dock/docs/reference_naming.md` | `spec-dock/docs/reference_naming.md` | equal |
| `src/spec_dock/assets/spec_dock/docs/reference_worktree.md` | `spec-dock/docs/reference_worktree.md` | equal |
| `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md` | `spec-dock/docs/workflow_chatgpt_authoring_pack.md` | equal |
| `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | `spec-dock/docs/workflow_spec_authoring.md` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py` | `spec-dock/scripts/spec_dock_runtime/application/authoring_pack/github_sync_preflight.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` | `spec-dock/scripts/spec_dock_runtime/application/contracts.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_artifact_doc.py` | `spec-dock/scripts/spec_dock_runtime/application/create_artifact_doc.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delegated_authoring.py` | `spec-dock/scripts/spec_dock_runtime/application/delegated_authoring.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` | `spec-dock/scripts/spec_dock_runtime/application/delete_node.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_artifact.py` | `spec-dock/scripts/spec_dock_runtime/application/import_artifact.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` | `spec-dock/scripts/spec_dock_runtime/application/ports.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workbench.py` | `spec-dock/scripts/spec_dock_runtime/application/workbench.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py` | `spec-dock/scripts/spec_dock_runtime/application/worktree.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree_target.py` | `spec-dock/scripts/spec_dock_runtime/application/worktree_target.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` | `spec-dock/scripts/spec_dock_runtime/cli/bootstrap.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` | `spec-dock/scripts/spec_dock_runtime/cli/parser.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py` | `spec-dock/scripts/spec_dock_runtime/cli/registry.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/artifact_import.py` | `spec-dock/scripts/spec_dock_runtime/commands/artifact_import.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/workbench.py` | `spec-dock/scripts/spec_dock_runtime/commands/workbench.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py` | `spec-dock/scripts/spec_dock_runtime/domain/authoring_pack/source_manifest.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py` | `spec-dock/scripts/spec_dock_runtime/infra/assurance_store.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py` | `spec-dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py` | `spec-dock/scripts/spec_dock_runtime/infra/fs_cli.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` | `spec-dock/scripts/spec_dock_runtime/infra/fs_repo.py` | equal |
| `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` | `spec-dock/scripts/spec_dock_runtime/presentation/cli_text.py` | equal |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | `.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` | equal |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | `.agents/skills/spec-dock-epic-planning/SKILL.md` | equal |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | `.agents/skills/spec-dock-initiative-planning/SKILL.md` | equal |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` | `.agents/skills/spec-dock-issue-planning/SKILL.md` | equal |
| `src/spec_dock/assets/install_root/.codex/agents/code-reviewer.toml` | `.codex/agents/code-reviewer.toml` | equal |
| `src/spec_dock/assets/install_root/.codex/agents/dev-coder.toml` | `.codex/agents/dev-coder.toml` | equal |
| `src/spec_dock/assets/install_root/.codex/agents/qa-reviewer.toml` | `.codex/agents/qa-reviewer.toml` | equal |
| `src/spec_dock/assets/install_root/.codex/agents/spec-reviewer.toml` | `.codex/agents/spec-reviewer.toml` | equal |

#### Root-only / generated exceptions

| Exact path | Owner | Reason / direction / rebuild |
|---|---|---|
| `README.md` | provider root docs | Package scaffold外のpublic landing。S03で意味整合をreviewし、byte parity対象外 |
| `src/spec_dock/cli.py` | provider installer | Installed targetを生成する実装authorityでdogfood copyを持たない |
| `pyproject.toml` | provider package | Wheel package-data authorityでdogfood copyを持たない |
| `setup.py` | provider package | Build-time stale-asset pruning authorityでdogfood copyを持たない |
| `Makefile` | static gate | `make lint` entrypoint。自動rebuildなし |
| `scripts/static_analysis/run.sh` | static gate | Ruff/format/mypy orchestration。自動rebuildなし |
| `.github/workflows/provider-ci.yml` | provider CI | Ubuntu publication gate。install-root assetではなくrepository CI authority |
| `.github/workflows/ci.yml` | dogfood validation CI | sync/validate authority。push/PRで実行 |
| `spec-dock/.agent/active.json` | active store | Consumer state projection。`./spec-dock/scripts/spec-dock active set --id iss-00319 --no-checkout --no-github`で再生成 |
| `spec-dock/active/initiative` | active store | Initiative symlink projection。同じ`active set` commandで再生成 |
| `spec-dock/active/epic` | active store | Epic symlink projection。同じ`active set` commandで再生成 |
| `spec-dock/active/issue` | active store | Issue symlink projection。同じ`active set` commandで再生成 |
| `spec-dock/active/context-pack.md` | active store | Active context projection。同じ`active set` commandで再生成 |
| `spec-dock/.agent/deps-issues.json` | sync projection | Consumer dependency projection。`./spec-dock/scripts/spec-dock sync --no-github`で再生成 |
| `spec-dock/.agent/index-all.json` | sync projection | Full node index。同じ`sync --no-github` commandで再生成 |
| `spec-dock/.agent/index.json` | sync projection | Current node index。同じ`sync --no-github` commandで再生成 |
| `spec-dock/.agent/tree-all.json` | sync projection | Full tree。同じ`sync --no-github` commandで再生成 |
| `spec-dock/.agent/tree.json` | sync projection | Current tree。同じ`sync --no-github` commandで再生成 |
| `spec-dock/.agent/runbooks/current-runbook.json` | guidance projection | Machine runbook。`./spec-dock/scripts/spec-dock guidance issue-execution`で再生成 |
| `spec-dock/.agent/runbooks/current-runbook.md` | guidance projection | Human runbook。同じ`guidance issue-execution` commandで再生成 |
| `spec-dock/active/current-runbook.json` | guidance projection | Active machine runbook copy。同じ`guidance issue-execution` commandで再生成 |
| `spec-dock/active/current-runbook.md` | guidance projection | Active human runbook copy。同じ`guidance issue-execution` commandで再生成 |

`spec-dock/initiatives/`以下のcanonical Node/Evidenceとimported Artifactはconsumer-owned dogfood dataであり、provider parity候補でもgenerated exceptionでもない。Providerへ逆投影しない。

#### Package / test / platform inventory

- `pyproject.toml`のpackage-data authorityは`assets/**/*`、`assets/**/.gitignore`、`assets/install_root/.agents/**`、`.codex/**`、`.github/**`。Expected feature membersは上表のprovider pathsを`spec_dock/assets/`以下へ写したexact entriesである。
- Forbidden seeded entriesは`spec_dock/assets/spec_dock/scripts/spec-dock-close-smoke.sh`、`spec_dock/assets/github/workflows/spec-dock-close.yml`、`spec_dock/assets/spec_dock/templates/initiative/current/stale.md`、`spec_dock/assets/spec_dock/templates/initiative/completed/stale.md`、`spec_dock/assets/spec_dock/templates/adr.md`、`spec_dock/assets/spec_dock/templates/issue/discussions/rules.md`、`spec_dock/assets/spec_dock/templates/issue/discussions/_template.md`、`spec_dock/assets/spec_dock/templates/initiative/epics/new-epic`、`spec_dock/assets/spec_dock/templates/epic/issues/new-issue`、`spec_dock/assets/spec_dock/templates/issue/legacy/README.md`、`spec_dock/assets/spec_dock/templates/design.md`、`spec_dock/assets/spec_dock/templates/plan.md`、`spec_dock/assets/spec_dock/templates/report.md`、`spec_dock/assets/spec_dock/templates/requirement.md`。Workbench、dogfood canonical data、root mirror、tests、generated `.agent`もwheel memberに含めない。
- W1 focused: `tests/cli_runtime/test_delete.py`, `tests/cli_runtime/test_worktree.py`, `tests/unit/domain/test_authoring_source_manifest_workbench.py`, `tests/unit/infra/test_installer_workbench_resolver_opacity.py`, `tests/unit/infra/test_runtime_fs_repo_workbench_opacity.py`, `tests/unit/infra/test_runtime_resolver_workbench_opacity.py`, `tests/unit/infra/test_init_update.py`。
- W2 focused: `tests/cli_runtime/test_workbench.py`, `tests/unit/application/test_workbench.py`, `tests/unit/infra/test_runtime_fs_cli_workbench.py`, `tests/unit/presentation/test_workbench.py`。
- W3 focused: `tests/cli_runtime/test_artifact_import_chatgpt_output.py`, `tests/cli_runtime/test_artifact_import_s04.py`, `tests/unit/application/test_binary_artifact_import_ports.py`, `tests/unit/commands/test_artifact_import_chatgpt_output.py`, `tests/unit/infra/test_binary_artifact_publisher.py`, `tests/unit/presentation/test_artifact_import_chatgpt_output.py`, `tests/cli_runtime/test_runtime_new_doc_s09.py`。
- W4 focused: `tests/cli_runtime/test_wrappers.py`, `tests/unit/infra/test_init_update.py`。
- Full authorityは`uv run pytest`、static authorityは`make lint`。Ubuntu authorityは`.github/workflows/provider-ci.yml`の`provider-tests` / `ubuntu-latest`で、`uv run pytest`によりW3 testsを通常collectionする。

---

### セッションログ（2026-07-14 S01 latest main integration）

#### 対象
- Step: S01
- AC/EC: C319-02 / AC-319-003

#### 実施内容
- S00 clean/upstream `0 0`後に`git fetch origin`し、left 31 / right 55を確認。`git merge --no-commit --no-ff origin/main`で`MERGE_HEAD=0481b394`を未コミット統合した。
- 最初のsandbox内mergeは`.agents/`置換権限で停止し、tracked rollbackと`MERGE_HEAD`不在を確認。mergeが生成した未追跡物だけを`/private/tmp/issue319-failed-merge-20260714`へ非破壊退避してから同一commandを権限付きで再実行した。
- Content conflict 5件をowner分類: provider/dogfood `github_sync_preflight.py` 2件、provider/dogfood `source_manifest.py` 2件、`tests/unit/infra/test_init_update.py` 1件。
- DevCoder `gpt-5.6-sol` / mediumが、Workbench source fail-fast + Issue314 receipt publication、`.workbench` traversal prune + `file_observer`、Issue314/315〜319 test inventory、Codex/GitHub両surfaceのunpinned profile contractを併合。Unresolved conflict/markerは0、conflict投影2組はbyte-equal。
- Focused verificationはDevCoder 92 passed（unit 79 + CLI 13）。Code reviewer追加確認はisolated wheel 1 passed、concurrent snapshot 3 passed。Spec reviewer確認はfocused 28 passed、assurance valid、validate `nodes=212`。
- Whole staged `git diff --check`の13件はすべて`origin/main`由来Issue313 byte-preserved raw ChatGPT Artifact 1件の既存trailing whitespace。原文不変契約のため修正せず、競合解消差分の`diff --check` passと分離して既知例外化した。
- Fresh code reviewer passed後、fresh spec reviewerが`passed / promote`、confidence 0.99。Blocking findingsなし。

---

### セッションログ（2026-07-14 S02 candidate wheel / fresh init / existing update）

#### 対象
- Step: S02
- AC/EC: C319-03〜05 / AC-319-004〜006

#### 実施内容
- `codex-tmp` managed sessionで`uv build`した初回wheelにgenerated Python cache 133件を検出。Workbench memberは0件。既存Issue69 build testがsource copy時にcacheを除外していたため、実source buildへの感度がなかった。
- DevCoder `gpt-5.6-sol` / mediumが、`pyproject.toml` package-data exclusion、`setup.py` wheel staging prune + sdist release-tree filter、cacheを含むsource contextからのwheel/sdist全inventory回帰を最小追加。Version/`uv.lock`は変更なし。
- 修復後のcandidate wheelは`spec_dock-0.2.3-py3-none-any.whl`、SHA-256 `cb3049daddd35bbf162e5c9d1d1ebdc1a703530508bd3506b4e48bb76513d628`。Wheel/sdistの`__pycache__`/`.pyc`/`.pyo`は0、Workbench memberは0、S00 expected feature entriesは存在しforbidden seeded entriesは不在。
- Absolute candidate wheelを`uvx --no-cache --from`へ渡したfresh initが成功。Installed `workbench copy` / `artifact import chatgpt-output` help、ChatGPT/Issue planning skills、unpinned DevCoder/reviewer configs、4 placement ignore、installed cache 0件を確認。
- Pre-feature ref `7def2c10e29078e82c6a30441e79fe7cee3b1883`を`git archive`し、そのabsolute wheelからexisting consumerをinit。Root/Initiative/Epic/Issue Workbenchへtext/Python/TOML/Markdown/binary/nested sentinelを配置後、candidate wheelでupdateした。
- Update前後の4 placementは`diff -qr`すべてexit 0。File countsはroot 1 / initiative 1 / epic 1 / issue 2、bytesは24 / 29 / 26 / 899758で一致。Scope prefixへ正規化した全5 regular fileのbefore/after SHA-256 manifestも`diff=0`、symlink countは双方0で、relative path / entry type / bytes / SHA-256を確認した。Installed managed copy/import/skill assetsは更新され、本文はreportへ記録していない。
- Verification: focused packaging 4 passed、Ruff pass、mypy pass、`tests/unit/infra` 680 passed、copy/import CLI 20 passed、`git diff --check` pass。Setuptools license TOML deprecation warningは既存でscope外。
- Non-blocking observation: sdist内`src/spec_dock.egg-info/SOURCES.txt`にはrelease-tree filter前のcache path文字列が残るが、cache file memberは0。当該sdistからwheel再buildも成功し、再build wheelのcache memberは0であるため配布実体/consumer behaviorへ影響しない。

---

### セッションログ（2026-07-14 S03 public docs / dogfood projection）

#### 対象
- Step: S03
- AC/EC: C319-06〜07 / AC-319-007〜008

#### 実施内容
- Doc-writer `gpt-5.6-sol` / mediumがroot `README.md`とprovider docs 7 filesへ、experimental/non-canonical/disposable、root date-bucket/manual selection/no bulk copy、scoped one-shot source-wins/no sync/no copy-back/no classifier、single Markdown blank import、byte/source保持、typed token非予約、EAL/canonical rewrite、update preservationを既存説明へ最小統合した。
- Provider authorityだけを先に編集した状態のtestは106件中3 failed / 103 passedで停止。3件はすべてexpected provider/dogfood parity failureで、dogfood-only修正は行わなかった。
- S02 packaging fixを含むcurrent sourceからcandidate wheelをbuild。SHA-256は`88804856d7d0d2524c065e58e2bffd1b72f59158447661f3c5ceb615a7e8e290`、Python cache member 0。Absolute wheelを`uvx --no-cache --from`へ渡し`spec-dock update`でdogfoodへ正規投影した。
- Provider/dogfood docs 7 exact pairs、Issue315〜318関連runtime/skills/agent config exact pairsはbyte-equal。Root-only `README.md`はpublic landing authority、canonical Node/Evidenceとgenerated projectionsはS00 exception ledgerどおりで逆投影しない。Template/system/migration/version/lock変更は必要性がなくno-op。
- Projection後verificationは`tests/cli_runtime/test_wrappers.py tests/unit/infra/test_init_update.py` 561 passed、docs contract search pass、`git diff --check` pass。

---

### セッションログ（2026-07-14 S04 focused / full / static / Linux quality）

#### 対象
- Step: S04
- AC/EC: C319-08〜09 / AC-319-009〜010

#### 実施内容
- Issue315〜318のfocused contractをfinal S03 headから実行し、W1 99 passed、W2 132 passed、W3 112 passed、W4 10 passedを確認した。
- Baseline laneはunit 1186 passed、CLI runtime 1194 passed / 75 skipped / 2 warnings、integration 3 passed。Initial `make lint`はRuff/format/mypy violationを検出し、DevCoder `gpt-5.6-sol` / mediumがproduction runtime semanticsを変えず、composition/import/future除去を含むstatic/test repairだけを6 filesへ限定した。Optional regex matchはinitial mypy repairでexplicit assertion/narrowingへ修復した。
- Fresh QA r1はtest double 2箇所のtype ignoreがplanのno skip/disable/exclude gateに抵触するとfinding化し、r2はruntime `get_type_hints`互換性のP2を検出した。両方を修復後、affected 652 passed、QA affected 585 passed、relay 10 + 46 passed。Fresh code-reviewer r1とQA reviewer r3はいずれもblocking findingなしでpassedした。
- Final full regressionは2598 passed / 75 skipped / 2 warnings、1672.23秒。Final `make lint`はRuff check/format check 375 files、mypy 246 source filesがall passし、追加global Ruff check/formatもpassした。
- C319-08はfocused/full/static evidenceによりpass。C319-09はArtifact import publication testのlocal passと`.github/workflows/provider-ci.yml` Ubuntu collection/config確認までpassした。PR head上のUbuntu実runはS100 pendingであり、完了を自己主張しない。

#### 変更したファイル
- `scripts/authoring-pack/authoring_pack_review.py`
- `scripts/authoring-pack/invoke_chatgpt_backend.py`
- `tests/cli_runtime/test_artifact_import_chatgpt_output.py`
- `tests/cli_runtime/test_artifact_import_s04.py`
- `tests/cli_runtime/test_wrappers.py`
- `tests/unit/infra/test_init_update.py`

#### クロージャ
- `tc319-s04-01`: pass — W1〜W4 focused regression。
- `tc319-s04-02`: pass — unit / CLI runtime / integration / full regression。
- `tc319-s04-03`: pass — authoritative `make lint`とglobal Ruff。
- `tc319-s04-04`: local/config pass、S100 pending — Ubuntu workflowはPR head実run後にterminal closeする。

---

### セッションログ（2026-07-14 S05 fresh installed integrated manual scenario）

#### 対象
- Step: S05
- AC/EC: C319-10、C319-15 / AC-319-011

#### 実施内容
- Candidateは`spec_dock-0.2.3-py3-none-any.whl`、version `0.2.3`、SHA-256 `876cc9c4ecb00c702cc46b4882106ece630f3931849c168dc898a6626c85b486`。Installed feature members 5件はcandidate wheel memberとbyte-equalだった。
- Safe synthetic Git repositoryへGitHub-linked Initiative / Epic / Issue nodeを3件導入し、同一commitのlinked worktree 2件を用意した。Fixture-local fake `gh`のallowed callは3件、unknown / mutation / network callは0件だった。
- Root Workbenchから必要file 1件だけをmanual selectionし、root bulk copyを行わなかった。Scoped sourceはregular 5 / symlink 1、targetはregular 7 / symlink 1。Shared regular 5件はbyte-equal、target-only 2件は保持された。Hidden `.git`、binary、config、symlink objectは内容を分類・解釈せずopaqueに扱った。
- `workbench copy --json`はpassし、experimental / non-canonical / disposable / one-shot / no-sync contractをcontent-free outputで確認した。Absolute target pathとWorkbench本文は記録していない。
- `artifact import chatgpt-output`を2回実行した。各Artifactは193 bytes、SHA-256 `7627940c724b1be0a0918acdd85fb270365b9b7102c6d48d6527305de7350d6b`、`committed=true`、`storage_identity=blank`、warning none。Sourceは両回とも残り、`cmp`一致、既存Artifactのno-overwriteを確認した。
- Pre-adoption checkpointではpreservation成功後もadoptionをpendingのまま保持した。Fixture EALへpreservation statusとadoption statusを別fieldで記録し、採用判断後にcanonical rewriteを実施した。Rewrite後もsourceとimport済みArtifactはbyte-unchangedだった。
- Sync output 9件でWorkbench filename hitは0件。Sensitive marker、full-body、absolute pathのsecrecy scan hitもすべて0件だった。

#### クロージャ
- `tc319-s05-01`: pass — Candidate-wheel-onlyのsynthetic copy → import → EAL → rewrite順序とauthority境界。
- `tc319-s05-02`: pass — Source survival、shared bytes、destination-only保持、Artifact no-overwrite、post-rewrite不変。
- `tc319-s05-03`: pass — Fake gh fail-closed、semantic discovery opacity、body/secret/absolute path非露出。
- C319-10 / C319-15: pass。Fresh final spec reviewはfinding 0 / confidence 0.99、fresh QA reviewはfinding 0。

#### 変更したファイル
- `report.md` only。Fixture、Workbench、manual Artifactはrepository外またはGit-ignoredで、versioned product fileの変更なし。

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
