---
種別: 実装報告書（Issue）
ID: "iss-00196"
タイトル: "Document Decision Implementation Layer Responsibilities"
関連GitHub: ["#196"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00196 Document Decision Implementation Layer Responsibilities — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合はこの section を残したうえで `No material interpretation changes.` / `No decision entries.` を明示する。この Issue では material decisions があるため、下表の D-001 以降を canonical decision entries として扱う。

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
| D-001 | resolved | scope | user + deep consultant | `iss-00196` の scope が docs/skills だけか、templates も含むかが未確定だった | A: docs/skills only; B: docs+skills+template checklist; D: B-lite contract-first | Option D / B-lite contract-first を採用し、workflow docs、planning skills、minimal template readiness prompts を対象にする | Harness / prompt / context engineering 上、docs/skills だけでは authoring failure を防ぎにくい。一方、templates は policy authority ではなく thin scaffold に留める必要がある | applied | `discussions/20260617t154625z-interview-decision-boundary-primary-intent.md`; `discussions/20260618t000451z-disc-deep-consultant-decision-scope-synthesis.md`; `requirement.md` | design/plan で具体的な変更対象へ分解する |
| D-002 | resolved | interpretation | user + deep consultant | templates に具体例を置くべきか、docs に置くべきかが未確定だった | C+: generic examples in docs/templates; clean-template revision: examples only in docs | Clean-template policy を採用する。Templates は薄く、skills も薄く、詳細説明と具体例は docs に置く | Templates は完成 artifact の初期形であり、例や authoring-only instruction が残ると downstream implementation agent のノイズになる | applied | `discussions/20260618t000833z-interview-decision-boundary-example-policy.md`; `discussions/20260618t003437z-disc-deep-consultant-clean-template-revision.md`; `requirement.md` | design/plan で docs examples と template absence checks を定義する |
| D-003 | resolved | compatibility | spec-reviewer | Parent Epic が `templates = examples` を所有する古い文言を保持し、Issue requirement の clean-template policy と衝突していた | A: Issue requirement だけで supersede; B: parent Epic wording を最小修正 | Parent Epic の context surface ownership wording を clean-template policy に合わせ、templates は thin scaffold / evidence slots、docs は examples / detailed semantics と明示する | Design / plan は parent Epic に trace するため、親の矛盾を残すと reviewer が相反する実装対象を読む | applied | `spec-reviewer` finding `019ed82f-1e31-7b32-b7b0-b75e9a40f63f`; `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md` | requirement gate の fresh re-review を実施する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | research | `requirement.md` 背景・現状 / スコープ | GitHub #196、parent epic、workflow docs、planning skills の source-grounding として採用した | `discussions/20260617t154620z-research-decision-implementation-layer-source-grounding.md` | design phase で具体的な docs/skills/templates 差分へ展開する |
| EAL-002 | `adopted` | discussion + deep consultant | `requirement.md` スコープ / 受け入れ条件 | User-approved Option D と deep consultant の B-lite contract-first 推奨が一致したため採用した | `discussions/20260617t154625z-interview-decision-boundary-primary-intent.md`; `discussions/20260618t000451z-disc-deep-consultant-decision-scope-synthesis.md` | design phase で template readiness prompt の最小形を定義する |
| EAL-003 | `adopted` | discussion + deep consultant | `requirement.md` 非交渉制約 / 受け入れ条件 / エッジケース | ユーザー回答と再分析により、examples out of templates、thin skills、docs detailed guidance が採用方針として確定した | `discussions/20260618t000833z-interview-decision-boundary-example-policy.md`; `discussions/20260618t003437z-disc-deep-consultant-clean-template-revision.md` | design phase で docs examples と template noise checks を定義する |
| EAL-004 | `adopted` | reviewer | Parent Epic requirement/design/plan alignment | Requirement review の P1 finding を採用し、親 Epic の古い `templates = examples` 表現を clean-template 方針へ揃えた | `spec-reviewer` finding `019ed82f-1e31-7b32-b7b0-b75e9a40f63f`; `spec-dock/active/epic/requirement.md`; `spec-dock/active/epic/design.md`; `spec-dock/active/epic/plan.md` | fresh requirement re-review |
| EAL-005 | `adopted` | reviewer | `design.md` / `report.md` design gate fixes | Design review の P1/P2 finding を採用し、example ownership を `decision-routing.md` に一本化し、no-decision placeholder を material decision entries と矛盾しない説明へ修正した | `spec-reviewer` finding `019ed835-b27c-7531-8711-3fbd34da811c`; `design.md`; `report.md` | fresh design re-review completed: `019ed838-6ee0-7663-8fa6-24a409b84cf2` |
| EAL-006 | `adopted` | reviewer | `plan.md` constraint closure coverage | Plan review の P2 finding を採用し、non-scope constraints を closure index の `tc-009` と S99 closure に追加した | `spec-reviewer` finding `019ed83c-a029-7dd2-9cb1-bee6a676ac08`; `plan.md` | fresh plan re-review completed: `019ed83f-4cda-7901-bb8c-208f2e2f965e` |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` は decision responsibility と implementation responsibility の境界明文化を主目的にしている | Templates / skills の thinness、docs examples、dogfooding evidence は主目的を支える context-surface 要件として扱う | low | passed through requirement/design/plan fresh spec-reviewer gates |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | GitHub #196; parent epic requirement/design/plan; workflow docs; planning skills; issue discussions | Option D / B-lite contract-first adopted; clean-template policy adopted; no remaining blocking interview question | adopted into `requirement.md` and this `report.md` ledger; reviewer P1 parent-Epic contradiction fixed | passed: fresh `spec-reviewer` re-review `019ed831-fee1-7ed2-8cc2-bfd6c9f0fdbb` | no | promote to design authoring |
| design | passed requirement; parent epic requirement/design/plan; workflow docs; phase design playbook; provider docs/skills/templates inventory | system-architect direct-write skipped because target discussions subtree was already dirty; manual design fallback recorded; no blocking design question | adopted into `design.md`; reviewer P1/P2 findings fixed | passed: fresh `spec-reviewer` re-review `019ed838-6ee0-7663-8fa6-24a409b84cf2` | no | promote to plan authoring |
| plan | passed requirement and design; phase plan issue playbook; authoring issue-plan schema; workflow issue completion policy | implementation-planner direct-write skipped because target discussions subtree was already dirty; manual plan fallback recorded; P2 constraint coverage finding fixed | adopted into `plan.md`; `tc-009` added for non-scope constraints | passed: fresh `spec-reviewer` re-review `019ed83f-4cda-7901-bb8c-208f2e2f965e` | no | ready for issue execution handoff, subject to normal execution workflow gates |

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
| system-architect | iss-00196 | 該当なし | `requirement.md`; parent epic docs; workflow docs; issue discussions | `design.md`; `report.md` | blocked（direct-write draft skipped） | なし（[]） | not_run: target `discussions/` subtree already has untracked current-authoring artifacts, making static direct-write adoption-ineligible | manual design authoring fallback | delegated design draft itself | なし（manual path available） | fresh requirement reviewer pass: `019ed831-fee1-7ed2-8cc2-bfd6c9f0fdbb` | manual fallback; fresh `spec-reviewer` required for canonical `design.md` |
| implementation-planner | iss-00196 | 該当なし | `requirement.md`; `design.md`; parent epic docs; workflow docs | `plan.md`; `report.md` | blocked（direct-write draft skipped） | なし（[]） | not_run: target `discussions/` subtree already has untracked current-authoring artifacts, making static direct-write adoption-ineligible | manual plan authoring fallback | delegated plan draft itself | なし（manual path available） | fresh design reviewer pass: `019ed838-6ee0-7663-8fa6-24a409b84cf2` | manual fallback; fresh `spec-reviewer` required for canonical `plan.md` |

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
- S01 では provider-side workflow docs に decision routing の入口を追加し、具体例と good / bad pattern の置き場として `docs/authoring/decision-routing.md` を新設した。
- Skills / templates / runtime / tests / GitHub state は S01 の許可範囲外として変更していない。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-18 S01）

#### 対象
- Step: S01
- AC/EC: AC-001, AC-003, EC-001, EC-002, EC-003, EC-004
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S01 — Provider docs decision-routing guidance`
  - closure ids: tc-001, tc-002

#### 実施内容
- `doc-writer` に S01 provider docs 変更を委任し、許可パス外変更がないことを親 orchestrator が確認した。
- Provider workflow docs に `authoring/decision-routing.md` への参照と decision responsibility の入口 rule を追加した。
- `src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md` を追加し、routing matrix、generic examples、good / bad patterns、handoff checklist を置いた。

#### 実行コマンド / 結果
```bash
rg -n "decision-routing|Decision-only|Issue-local|Epic|Initiative" src/spec_dock/assets/spec_dock/docs

pass: provider docs and new authoring guide contain the expected routing terms.

rg -n "good|bad|example|例" src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md

pass: new authoring guide contains generic examples and good / bad pattern sections.

git diff --check

pass: no whitespace errors.
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01 | 代替証跡（Red / alternative） | inspect-only | Existing docs did not have a single `decision-routing.md` target or explicit Decision-only routing matrix before S01 | docs inspection / pre-step plan evidence | pass | Failing-first code test is not applicable for docs-only step |
| S01 | 緑フェーズ（Green） | inspect-only | Workflow docs now link decision routing; `decision-routing.md` owns examples and patterns | `rg` / docs inspection | pass | Skills/templates/runtime/tests unchanged |
| S01 | リファクタリング（Refactor） | guardrail satisfied | Workflow docs stay concise; examples are centralized in `decision-routing.md` | diff inspection / `git diff --check` | pass | no extra cleanup needed |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S01 | none | implementation | recorded | tc-001, tc-002 | no | worker returned `No material implementation decisions beyond the approved plan.` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01 | tc-001, tc-002 | docs contain routing rule and `decision-routing.md` owns examples | Provider workflow docs link `authoring/decision-routing.md`; new authoring guide contains routing matrix, examples, good/bad patterns | pass | reviewer gate pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-001 | S01 | yes | inspect-only | Existing docs lacked a single decision-routing authoring guide and explicit routing matrix | `rg -n "decision-routing|Decision-only|Issue-local|Epic|Initiative" src/spec_dock/assets/spec_dock/docs` | pass | workflow docs and guide expose routing terms |
| tc-002 | S01 | yes | inspect-only | Examples were not centralized in a dedicated decision-routing authoring doc | `rg -n "good|bad|example|例" src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md` | pass | examples/good/bad patterns live in docs authoring guide |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-001 | S01 | provider docs routing inspection | pass | step reviewer gate pending |
| tc-002 | S01 | `decision-routing.md` examples/patterns inspection | pass | step reviewer gate pending |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | tc-001, tc-002 | N/A | tc-001, tc-002 | S01 で追加 closure / 削除 closure / alias 変更は発生していない | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | `/Users/iwasawayuuta/.codex/worktrees/7e5f/spec-dock` | iss-00196 | current session | doc-writer, spec-reviewer, code-reviewer, qa-reviewer | same repo, active issue, current session, named roles; no destructive action / publishing / credentialed access / scope expansion / private external system use | issue complete / session end / scope change / user revocation | none | proceed with plan-scoped delegated steps |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01 | delegated | shipped docs / workflow text | doc-writer | provider docs decision-routing guidance | `plan.md` S01 and provider docs | `workflow_issue.md`, `workflow_epic.md`, `workflow_initiative.md`, `workflow_spec_authoring.md`, `docs/authoring/decision-routing.md` | skills, templates, runtime code, tests, package/config, `.github`, GitHub state, dogfooding mirror, canonical issue docs/report | targeted `rg`; `git diff --check`; parent diff guard | need runtime enforcement; unclear routing responsibility; examples cannot be generic | changed files; verification results; unresolved risks; Ledger Note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01 | doc-writer | Added decision-routing references to workflow docs and created `docs/authoring/decision-routing.md`; no material implementation decisions beyond approved plan | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`; `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`; `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`; `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`; `src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md` | targeted `rg` -> pass; `git diff --check` -> pass | pending spec-reviewer | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01 | unavailable / denied / host conflict / impossible because ... | approval source / risk accepted: yes / no | `path/to/file` | ... | ... | `command` -> pass / docs-only inspection -> pass | reviewer role + passed / failed / unavailable / denied / waived / provisional | blocked / incomplete / waived with explicit risk acceptance / next action |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer | spec-reviewer | fresh | passed | no | proceed to commit | pass by `spec-reviewer` `019ed84a-c36a-7e83-a59a-fdf0c6ed9508`; P2 Closure Delta cleanup applied before commit |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01 | committed | provider docs S01 diff and report evidence | `57e61118` | `git status --short` -> clean after S01 commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` - decision-only Issue routing入口を追加
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` - Epic-owned durable decision routing を追加
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` - Initiative-owned operating decision routing を追加
- `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` - authoring 中の decision-only finding routing を追加
- `src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md` - 具体例と good / bad pattern の docs surface を追加

#### コミット
- `57e61118` (`docs(workflow): decision routing guidanceを追加`)

#### メモ
- S01 は docs-only step。Skills / templates / runtime / tests / GitHub state は変更していない。

---

### セッションログ（2026-06-18 HH:MM - HH:MM）

#### 対象
- Step: S02
- AC/EC: AC-002, AC-006
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S02 — Thin skill decision-only gates`
  - closure ids: tc-003, tc-004

#### 実施内容
- `doc-writer` に S02 provider skill 変更を委任し、許可パス外変更がないことを親 orchestrator が確認した。
- Issue planning / Epic planning / Initiative planning / Clarification の各 skill に、decision-only / cross-scope finding の thin stop/routing gate と `decision-routing.md` 参照を追加した。
- 具体例や routing matrix は skill に複製せず、docs への参照に留めた。

#### 実行コマンド / 結果
```bash
rg -n "decision-only|decision routing|decision-routing|Epic|Initiative|stop" src/spec_dock/assets/install_root/.agents/skills/spec-dock-*

pass: target provider skills expose decision-only routing terms and docs links.

git diff --check

pass: no whitespace errors.
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S02 | 代替証跡（Red / alternative） | inspect-only | Existing provider skills did not all expose the new decision-only routing gate and docs link | docs inspection / pre-step plan evidence | pass | docs-only skill text step |
| S02 | 緑フェーズ（Green） | inspect-only | Target provider skills now contain thin routing gate / reminder and link to `decision-routing.md` | `rg` / skill inspection | pass | examples are not copied into skill bodies |
| S02 | リファクタリング（Refactor） | guardrail satisfied | Skill additions remain short routing guidance | diff inspection / `git diff --check` | pass | no extra cleanup needed |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02 | none | implementation | recorded | tc-003, tc-004 | no | worker returned `No material implementation decisions beyond the approved plan.` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S02 | tc-003, tc-004 | Skill files contain thin decision routing and no long examples | Provider planning/clarification skills link `decision-routing.md` and contain short stop/routing text | pass | reviewer gate pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-003 | S02 | yes | inspect-only | Target skills lacked a complete first-read decision-only gate aligned to S01 docs | `rg -n "decision-only|decision routing|decision-routing|Epic|Initiative|stop" src/spec_dock/assets/install_root/.agents/skills/spec-dock-*` | pass | routing terms and docs links present |
| tc-004 | S02 | yes | inspect-only | Examples are owned by docs and should not be duplicated in skills | manual skill inspection / `git diff --check` | pass | skill additions are short routing guidance |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-003 | S02 | provider skill routing inspection | pass | step reviewer gate pending |
| tc-004 | S02 | skill thinness inspection | pass | step reviewer gate pending |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | tc-003, tc-004 | N/A | tc-003, tc-004 | S02 で追加 closure / 削除 closure / alias 変更は発生していない | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S02 | delegated | shipped skill text | doc-writer | provider planning / clarification skill routing gates | `plan.md` S02, S01 docs, provider skills | four listed provider skill files | provider docs, templates, runtime code, tests, package/config, `.github`, GitHub state, dogfooding mirror, canonical issue docs/report | targeted `rg`; `git diff --check`; parent diff guard | broad rewrite needed; docs route target missing; examples required in skill | changed files; verification results; unresolved risks; Ledger Note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S02 | doc-writer | Added thin decision-only stop/routing gates and `decision-routing.md` links to planning/clarification skills; no examples copied into skills | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` | targeted `rg` -> pass; `git diff --check` -> pass | pending spec-reviewer | none | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S02 | step reviewer | spec-reviewer | fresh | passed | no | proceed to commit | pass by `spec-reviewer` `019ed850-a084-7c10-83d1-9dd43557b62d`; P2 S01 commit evidence cleanup applied before S02 commit |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S02 | committed | provider skill S02 diff and report evidence | `50584a63` | `git status --short` -> clean after S02 commit | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md` - Issue planning の decision-only gate を追加
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` - Epic planning の cross-scope routing reminder を追加
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` - Initiative planning の routing reminder を追加
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` - clarification の decision-only routing gap 分類を追加

#### コミット
- `50584a63` (`docs(skills): decision-only routing gateを追加`)

#### メモ
- S02 は skill-text-only step。Provider docs / templates / runtime / tests / GitHub state は変更していない。

---

### セッションログ（2026-06-18 HH:MM - HH:MM）

#### 対象
- Step: S03
- AC/EC: AC-004, AC-006, EC-004
- 計画上の出典（Planned source）:
  - `plan.md` section: `実装ステップ S03 — Thin templates / no embedded examples`
  - closure ids: tc-005, tc-006

#### 実施内容
- `doc-writer` に S03 provider template 変更を委任し、許可パス外変更がないことを親 orchestrator が確認した。
- Template README から具体例 ownership / example surface 表現と不要な例示を削り、thin scaffold / evidence slot の責務に寄せた。
- Epic design template から `good example surface` 表現を削り、`evidence slot` としての位置づけに変更した。

#### 実行コマンド / 結果
```bash
rg -n "例:|サンプル|good example|bad example|management_core|shared kernel" src/spec_dock/assets/spec_dock/templates

pass: no matches. The command returned exit 1 because no forbidden concrete example markers were found.

rg -n "good example surface|scaffold / examples|scaffolds/examples|example surface|scaffold/example" src/spec_dock/assets/spec_dock/templates

pass: no matches. The command returned exit 1 because stale template/example ownership phrases were absent.

git diff --check

pass: no whitespace errors.
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S03 | 代替証跡（Red / alternative） | inspect-only | Provider templates still contained `good example surface` / concrete example phrasing | diff inspection / pre-step plan evidence | pass | docs-only template text step |
| S03 | 緑フェーズ（Green） | inspect-only | Target provider templates now describe thin scaffold / evidence slot only | targeted `rg` / template inspection | pass | no concrete examples added to templates |
| S03 | リファクタリング（Refactor） | guardrail satisfied | Template changes remain narrow wording cleanup | diff inspection / `git diff --check` | pass | no extra cleanup needed |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S03 | none | implementation | recorded | tc-005, tc-006 | no | worker returned `No material implementation decisions beyond the approved plan.` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S03 | tc-005, tc-006 | Templates remain thin and do not embed concrete examples | Provider template README and epic design template no longer contain example-surface ownership terms or concrete example markers | pass | reviewer gate pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| tc-005 | S03 | yes | inspect-only | Template README and epic design template contained stale example-surface phrasing | `rg -n "good example surface|scaffold / examples|scaffolds/examples|example surface|scaffold/example" src/spec_dock/assets/spec_dock/templates` | pass | no stale ownership phrases found |
| tc-006 | S03 | yes | inspect-only | Templates risked carrying concrete examples that should live in docs | `rg -n "例:|サンプル|good example|bad example|management_core|shared kernel" src/spec_dock/assets/spec_dock/templates` | pass | no concrete example markers found |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| tc-005 | S03 | provider template ownership phrase inspection | pass | step reviewer gate pending |
| tc-006 | S03 | provider template concrete example marker inspection | pass | step reviewer gate pending |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | tc-005, tc-006 | N/A | tc-005, tc-006 | S03 で追加 closure / 削除 closure / alias 変更は発生していない | no | no |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S03 | delegated | shipped template text | doc-writer | provider template thinness cleanup | `plan.md` S03, S01 docs, provider templates | `src/spec_dock/assets/spec_dock/templates/README.md`; `src/spec_dock/assets/spec_dock/templates/epic/design.md` | provider docs, skills, runtime code, tests, package/config, `.github`, GitHub state, dogfooding mirror, canonical issue docs/report | targeted `rg`; `git diff --check`; parent diff guard | template schema rewrite needed; examples required in templates; runtime behavior needed | changed files; verification results; unresolved risks; Ledger Note | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S03 | doc-writer | Removed example ownership phrasing from provider template README and epic design template; kept templates as thin scaffold / evidence slots | `src/spec_dock/assets/spec_dock/templates/README.md`; `src/spec_dock/assets/spec_dock/templates/epic/design.md` | targeted `rg` -> pass; `git diff --check` -> pass | pending spec-reviewer | none | accepted |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S03 | step reviewer | spec-reviewer | fresh | passed | no | proceed to commit | pass by `spec-reviewer` `019ed858-d3ba-7843-af05-1852f95aadcb`; P2 AC/EC traceability cleanup applied before commit |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S03 | pending review | provider template S03 diff and report evidence | pending | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/templates/README.md` - template責務をthin scaffold / evidence slotへ整合
- `src/spec_dock/assets/spec_dock/templates/epic/design.md` - `good example surface`表現を削除

#### コミット
- pending

#### メモ
- S03 は template-text-only step。Provider docs / skills / runtime / tests / GitHub state は変更していない。

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
