---
種別: 実装報告書（Issue）
ID: "iss-00267"
タイトル: "Workflow docs skills and README alignment"
関連GitHub: ["#267"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00267 Workflow docs skills and README alignment — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-267-001 | resolved | scope | orchestrator | `new doc` / `discussions` references span future guidance, legacy preservation, runtime removal evidence, and source identifiers | blanket replacement; leave all references; classify by context | Classify before editing. Future guidance moves to `new artifact` / `artifacts`; legacy preservation and removed-command evidence may remain only with explicit context. | Requirement AC-267-003 and design DES-267-003 require classification, and repo-analyst found high-risk mixed guidance in workflow docs and skills. | promoted_to_design | `design.md` classification policy; repo-analyst classification evidence | none |
| D-267-002 | resolved | scope | orchestrator | `.codex/AGENTS.md` and `.codex/agents/*.toml` contain old delegated authoring guidance but are outside approved Issue file boundary | include in this Issue; defer to follow-up; no action | Keep this Issue scoped to README, provider docs/templates, install_root skills, repo-local skills, and dogfooding mirrors. Do not edit `.codex/` agent config in Issue 267. | Requirement scope names provider docs / install_root skills / README / guides / workflow / template guidance; direct `.codex/agents` maintenance may require separate host-agent policy review. | deferred | repo-analyst classification: `.codex/AGENTS.md`, `.codex/agents/*.toml` old guidance | Non-blocking; revisit only if final spec-reviewer requires `.codex` alignment for Epic closeout. |
| D-267-003 | resolved | implementation | spec-reviewer | Clarification skill/workflow still routed future capture through legacy vocabulary and suggested `scratch`. | leave as-is; update clarification skill only; update skill and referenced workflow together | Update clarification guidance so future capture uses `new artifact` under scope-local `artifacts/`, raw/freeform uses `blank`, and `scratch` / `discussions` are historical input only. | Final spec-reviewer P1 finding showed AC-267-001/002 and Epic D-004 conflict until both skill and workflow doc were aligned. | applied | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`; `.agents/skills/spec-dock-clarification/SKILL.md`; `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`; `spec-dock/docs/workflow_clarification.md` | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-267-001 | adopted | repo-analyst sub-agent classification | `design.md`, `plan.md`, implementation handoff | Read-only classification identified concrete high-risk guidance clusters and provider/mirror parity facts; adopted as planning baseline and doc-writer handoff constraints. | subagent `019f1e09-8b08-7321-9d9a-89edd06080c8`; durable summary below: `CE-267-001` through `CE-267-010` | Use as S01-S04 doc-writer input. |

### S00 分類証跡サマリー（Classification Evidence）
| ID | 分類 | 対象 | 判断 | grep-friendly evidence |
|---|---|---|---|---|
| CE-267-001 | future guidance update | `README.md` | `new doc adr` and `templates/discussions` examples are future-facing and must move to `new artifact` / `artifacts`. | `README.md:new doc adr`, `README.md:templates/discussions` |
| CE-267-002 | future guidance update | provider delegated authoring docs | `phase_design.md`, `phase_plan.md`, and `workflow_spec_authoring.md` still describe new delegated output via `discussions` / `new doc`. | `src/spec_dock/assets/spec_dock/docs/phase_design.md:new doc <type>`, `phase_plan.md:discussions`, `workflow_spec_authoring.md:discussions` |
| CE-267-003 | future guidance update | provider `workflow_issue.md` | Mixed `new artifact` and old scope-local discussions wording is high-risk and must be reconciled. | `src/spec_dock/assets/spec_dock/docs/workflow_issue.md:new artifact`, `workflow_issue.md:scope-local discussions` |
| CE-267-004 | future guidance update | shipped/repo-local skills | `spec-dock-hub` and `github-pr-merge-preparer` route delegated output / PR repair docs through `new doc` or discussion paths. | `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md:new doc`, `github-pr-merge-preparer/SKILL.md:new doc pr-repair-batch`, `.agents/skills` mirror |
| CE-267-005 | legacy preservation keep | `docs/rules/*/artifacts.md` | Already states future `artifacts/` and legacy `discussions/` preservation; keep unless small wording alignment is needed. | `src/spec_dock/assets/spec_dock/docs/rules/*/artifacts.md:Legacy`, `Future` |
| CE-267-006 | legacy label strengthen | `docs/rules/*/discussions.md` | `new doc` catalog may remain only as legacy/preservation catalog and should not read as future creation guidance. | `src/spec_dock/assets/spec_dock/docs/rules/*/discussions.md:new doc` |
| CE-267-007 | legacy preservation keep | `templates/README.md` | Current/future contrast is mostly intentional; verify wording only. | `src/spec_dock/assets/spec_dock/templates/README.md:new doc`, `Future new artifact`, `preservation` |
| CE-267-008 | docs-only out of scope | runtime/code/tests | Runtime and tests contain many `new doc` / `new artifact` / `discussions` identifiers; do not edit in docs-only pass except conditional parity assertion path. | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/`, `tests/` |
| CE-267-009 | deferred out of scope | `.codex/AGENTS.md`, `.codex/agents/*.toml` | Old delegated authoring guidance exists but is outside approved Issue boundary; defer unless final reviewer blocks. | `.codex/AGENTS.md:new doc`, `.codex/agents/*.toml:new doc` |
| CE-267-010 | provider/mirror parity | docs/templates/skills mirrors | Provider docs and `spec-dock/docs` were equal before edits; templates report files differ; skills differ only by cache artifacts. | `diff -qr src/spec_dock/assets/spec_dock/docs spec-dock/docs`, `diff -qr src/spec_dock/assets/spec_dock/templates spec-dock/templates`, `diff -qr src/spec_dock/assets/install_root/.agents/skills .agents/skills` |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-267-001 | Future guidance will point to `new artifact` / `artifacts` via DES-267-001 and S01-S04. | Legacy `discussions/` preservation remains explicit via DES-267-002; runtime/source identifiers are not changed by docs-only work. | low | passed by S00 spec-reviewer |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `requirement.md` approved; Epic ADR/design/plan reviewed; initial `rg` classification showed target references across README/docs/skills/mirrors. | none | adopted | passed | no | promote |
| design | Repo-analyst classification and prior Issue 266 boundary reviewed; design expanded with current structure, classification policy, contracts, file boundaries, non-scope, and review strategy. | `.codex/agents` old guidance is out-of-scope unless final reviewer blocks; recorded as D-267-002. | adopted | passed | no | promote |
| plan | Plan expanded with S00-S99 sequence, closures, allowed/forbidden files, delegation boundaries, and final checks. | P2 clarified conditional parity-test update path; P3 preserved durable classification evidence. | adopted | passed | no | execute approved plan |

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
  - 既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | passed | manual-authored canonical docs |

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
- S00 planning readiness を実施し、Issue 267 の design / plan を approved execution authority へ具体化した。
- 実装本体（S01-S04 docs/skills alignment）は fresh spec-reviewer による planning gate 通過後に doc-writer へ委任する。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-01 S00 planning）

#### 対象
- Step: S00 Plan Readiness and Classification Baseline
- AC/EC: AC-267-003, AC-267-005; CLOS-267-003, CLOS-267-007, CLOS-267-008
- 計画上の出典（Planned source）:
  - `plan.md` section: S00 Plan Readiness and Classification Baseline
  - closure ids: CLOS-267-003, CLOS-267-007, CLOS-267-008

#### 実施内容
- Active Issue と guidance state を確認した。
- Epic design / plan、Issue requirement、前段 Issue 266 の delegated authoring boundary を参照した。
- repo-analyst に read-only classification を委任し、残存 `new doc` / `discussions` guidance の分類と provider/mirror parity evidence を取得した。
- `design.md` を、分類方針、対象/非対象境界、provider/mirror 方針、docs-only safety、レビュー戦略を含む approved design に更新した。
- `plan.md` を、S00-S99、closure index、allowed/forbidden files、delegation boundary、final quality gate を含む approved plan に更新した。
- `.assurance.json` を `assurance classify --stage requirement` / `assurance verify` で更新・検証した。

#### 実行コマンド / 結果
```bash
git fetch origin main
# From https://github.com/chemitaro/spec-dock
#  * branch              main       -> FETCH_HEAD

git merge origin/main
# Already up to date.

./spec-dock/scripts/spec-dock guidance issue-planning
# initial: blocked reason_code=design-not-substantive

./spec-dock/scripts/spec-dock assurance classify --stage requirement
# assurance classify: ok; authorized_profile: standard

./spec-dock/scripts/spec-dock assurance verify
# assurance verify: ok; authorized_profile: standard
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S00 | 代替証跡（planning characterization） | inspect-only | initial `guidance issue-planning` reported `design-not-substantive`; repo-analyst found high-risk stale guidance clusters | command + read-only classification | pass | Established planning gap before implementation. |
| S00 | 緑フェーズ（planning update） | manual-required | design / plan promoted to substantive approved artifacts; assurance classify/verify passed | document update + command | pass | Fresh spec-reviewer still required before execution. |
| S01-S04 | 実装 / 修正 | docs-only implementation | docs/skills/README/mirror alignment completed; P1 clarification fix applied | command + docs inspection + fresh spec-reviewer | pass | Complete. |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S00 | `workflow_issue.md` mixes `new artifact` and old scope-local discussions wording | repo-analyst | recorded and promoted to doc-writer constraints | CLOS-267-001 through CLOS-267-004 | no | EAL-267-001 |
| S00 | `.codex/agents` old guidance is outside current approved scope | repo-analyst / orchestrator | deferred as non-blocking unless final reviewer requires it | D-267-002 | no | D-267-002 |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | CLOS-267-003, CLOS-267-007 | classification baseline and docs-only boundary established | design / plan / report updated; assurance verify passed; fresh spec-reviewer passed | pass | Complete. |
| S01-S04 | CLOS-267-001 through CLOS-267-006 | docs/skills implementation and mirror parity | docs/skills/README/mirrors updated; classification and parity checks passed | pass | Complete after P1 clarification guidance fix and fresh spec-reviewer pass. |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| CLOS-267-003 | S00 | yes | inspect-only | repo-analyst classification | `rg` classification summary in EAL-267-001 | pass | Full post-implementation `rg` evidence due in S04/S99. |
| CLOS-267-008 | S00 | yes | reviewer-required | planning docs updated | fresh spec-reviewer review | pass | Final re-review also passed after implementation fix. |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-267-001 | S01-S04 | README/docs/skills now use `new artifact` / `artifacts/` for future guidance | pass | Verified by `rg` classification and final spec-review. |
| CLOS-267-002 | S01-S04 | retained `discussions/` wording is legacy / historical / preservation | pass | Verified by `rg` classification and final spec-review. |
| CLOS-267-003 | S00/S04/S99 | remaining `new doc` is legacy/preservation context only | pass | Final `rg -n "new doc"` classification recorded. |
| CLOS-267-004 | S03/S04 | provider and repo-local skills route future output to `artifacts/` | pass | Final P1 fix covered clarification skill; provider/mirror skills match except cache. |
| CLOS-267-005 | S02/S04 | template README and report mirrors align with artifact catalog and legacy preservation | pass | Provider/mirror template diff has no output. |
| CLOS-267-006 | S04 | provider docs/templates and dogfooding mirrors align; skills differ only by generated cache | pass | `diff -qr` evidence recorded. |
| CLOS-267-007 | S00/S99 | runtime/source/test semantics unchanged | pass | `git diff --name-only` stayed within allowed docs/skills/README/mirror and issue docs. |
| CLOS-267-008 | S00/S99 | final fresh spec-review pass | pass | Re-review after P1 fix passed with no findings. |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | all | none | all | No closure alias or semantic change after plan approval. | no | no |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / workflow role policy | `/Users/iwasawayuuta/.codex/worktrees/b4d4/spec-dock` | iss-00267 | current session | repo-analyst, spec-reviewer, doc-writer after gate | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none | proceed with reviewer, then doc-writer if pass |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S00 | delegated | pattern analysis / provider-mirror classification | repo-analyst | read-only classification of docs/skills/README/mirrors | Issue requirement/design/plan | no writes | no source/test/runtime changes | compact classification table | none | evidence / risks / recommended file groups | pass |
| S01-S04 | delegated after S00 pass | persistent docs/skills maintenance | doc-writer | provider docs/templates/skills plus mirrors per plan | approved design/plan | docs/skills/README/mirror wording only | runtime/source/test behavior changes, discussion migration, new doc restoration | classification evidence, changed files, docs-only verification, risks | spec-reviewer fail or scope expansion | worker summary / changed files / verification / risks | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S00 | repo-analyst | Classified stale future guidance, legacy/preservation references, docs-only out-of-scope references, provider/mirror parity, and recommended doc-writer file groups. | none | read-only classification | not applicable | `.codex/agents` old guidance deferred outside current scope | accepted |
| S01-S04 | doc-writer | Aligned future artifact creation and delegated output guidance to `new artifact` / target scope `artifacts/`; relabelled retained `discussions/` / `new doc` content as legacy / historical / preservation; mirrored provider docs/templates/skills into dogfooding surfaces. | README; provider docs/templates/skills; `spec-dock/docs`; `spec-dock/templates`; `.agents/skills`; report evidence only | `rg -n "new doc"` classification; provider/mirror `diff -qr`; `git diff --check`; `./spec-dock/scripts/spec-dock validate` | failed initial final spec-review due clarification P1 | Remaining `new doc` references are legacy discussion preservation examples only; `.codex/agents` old guidance remains deferred outside approved scope. | accepted after fix |
| S01-S04-fix | doc-writer | Fixed final spec-review P1: clarification future capture now uses `new artifact` / `artifacts/`; `blank` is raw/freeform capture; `scratch` is legacy-only. | `spec-dock-clarification/SKILL.md`; `workflow_clarification.md` provider and mirror copies | `rg -n "scratch|discussion artifact|discussions/rules|new artifact|artifacts/rules"`; provider/mirror `diff -q`; `git diff --check` | passed fresh re-review | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S00 | parent is allowed to edit issue-level planning artifacts | workflow role boundary | issue `design.md`, `plan.md`, `report.md` | planning artifact edits | git diff can revert issue docs if needed | assurance classify/verify passed | spec-reviewer passed | complete |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| `standard` | `system-architect / implementation-planner / manual fallback` | manual fallback | manual-authored canonical docs using accepted Epic specs plus repo-analyst classification evidence CE-267-001 through CE-267-010. | passed | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S00 | planning spec review | spec-reviewer | fresh | passed | no | execute approved plan | `review_status: pass`; P2 conditional parity-test path and P3 durable classification evidence were addressed before implementation. |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S99 | ready-for-commit | Issue 267 docs/skills/README/mirror alignment and issue evidence | pending Issue commit | to be checked after commit | no-op not applicable | not applicable | not applicable | not applicable |

#### 変更したファイル
- `design.md` - promoted to substantive approved Issue design.
- `plan.md` - promoted to substantive approved implementation plan.
- `report.md` - recorded S00 classification / planning evidence.
- `.assurance.json` - refreshed standard profile assurance after design/plan promotion.

#### コミット
- not yet committed; ready for Issue finish and commit.

#### メモ
- Main branch merge was attempted after user request and returned `Already up to date`.

---

### セッションログ（2026-07-01 S01-S04 implementation）

#### 対象
- Step: S01-S04, S90, S99
- AC/EC: AC-267-001 through AC-267-005

#### 実施内容
- S01-S04 doc-writer implementation ran after S00 fresh spec-reviewer pass.
- Updated README future artifact examples from `new doc` / `discussions` to `new artifact` / `artifacts/`.
- Updated provider workflow / phase / authoring docs so delegated authoring future output targets scope-local `artifacts/` direct child and uses `new artifact`.
- Relabelled provider `docs/rules/*/discussions.md` as legacy / historical / preservation surface while preserving legacy `new doc` examples explicitly as historical context.
- Updated provider template README and mirrored provider report templates into `spec-dock/templates/{initiative,epic,issue}/report.md`.
- Updated provider install_root skills and repo-local mirrors, including `github-pr-merge-preparer` `new artifact pr-repair-batch` and repair unit artifact guidance.
- Mirrored provider docs to `spec-dock/docs` and provider skill changes to `.agents/skills`.
- No runtime source, command implementation, validation, scaffold logic, or tests were edited.

#### 分類結果
- Future guidance: moved to `new artifact` / `artifacts/` in README, workflow docs, phase docs, authoring docs, template README, `spec-dock-hub`, and `github-pr-merge-preparer`.
- Legacy preservation: retained `new doc` examples only in `docs/rules/{initiative,epic,issue}/discussions.md` and template README with explicit legacy / historical / preservation wording.
- Removed-command / source / test evidence: not edited in this doc-writer pass; runtime/source/tests were outside scope.
- Provider / mirror parity: provider docs and `spec-dock/docs` match after mirror sync; provider skills and `.agents/skills` match except generated `__pycache__`.

#### 実行コマンド / 結果
```bash
rg -n 'new doc|new artifact|discussions|artifacts' README.md src/spec_dock/assets/spec_dock/docs src/spec_dock/assets/spec_dock/templates src/spec_dock/assets/install_root/.agents/skills spec-dock/docs spec-dock/templates .agents/skills
# pass for classification; remaining `new doc` occurrences are in legacy/preservation discussion docs and template README only.

diff -qr src/spec_dock/assets/spec_dock/docs spec-dock/docs
# no output; provider docs and dogfooding docs match.

diff -qr src/spec_dock/assets/install_root/.agents/skills .agents/skills
# only generated cache difference:
# Only in src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib: __pycache__

rg -n "scratch|discussion artifact|discussions/rules|new artifact|artifacts/rules" src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md
# pass for P1 fix: `discussion artifact` / `discussions/rules` absent; `scratch` appears only in legacy / historical input wording.

diff -q src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md .agents/skills/spec-dock-clarification/SKILL.md
# no output; provider and repo-local clarification skill match.

diff -q src/spec_dock/assets/spec_dock/docs/workflow_clarification.md spec-dock/docs/workflow_clarification.md
# no output; provider and dogfooding clarification workflow match.

git diff --check
# pass; no output.

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=171
```

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | doc-writer after S00 pass | README, provider docs/templates/skills, dogfooding docs/templates/skills mirror updated; `rg`, provider/mirror diff, `git diff --check`, and `validate` evidence recorded above | passed |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | not applicable: docs/skills/README-only diff, no source/tests/runtime behavior changes | `git diff --name-only`; `git diff --check`; `./spec-dock/scripts/spec-dock validate` | not applicable |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | not applicable: runtime source/tests/command implementation were not changed | 0 | not applicable |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | Initial final review failed on clarification future capture guidance; D-267-003 fix applied. Fresh re-review found no findings. | 1 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| report records S00-S99 evidence, final spec-review pass, docs-only code/QA not-applicable decision | Issue 267 docs/skills/README/mirror alignment plus issue planning/report evidence | final response now; Epic PR after iss-00268 | ready |

## 遭遇した問題と解決 (任意)
- 問題: `guidance issue-planning` reported stale assurance after design/plan edits。
  - 解決: `assurance classify --stage requirement` and `assurance verify` refreshed the standard profile contract。

## 学んだこと (任意)
- `workflow_issue.md` has mixed future and stale delegated-output wording, so implementation must avoid broad string replacement and preserve legacy/preservation context.

## 今後の推奨事項 (任意)
- If final reviewers require `.codex/agents` alignment, create or promote a follow-up scope because it is outside the current Issue boundary.

## 省略/例外メモ (必須)
- 該当なし

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
- Record Red, Green, and refactor evidence for each executed step.
- Link each closure id to its observed verification result.
<!-- spec-dock:managed-section end id="report.step-evidence" -->
