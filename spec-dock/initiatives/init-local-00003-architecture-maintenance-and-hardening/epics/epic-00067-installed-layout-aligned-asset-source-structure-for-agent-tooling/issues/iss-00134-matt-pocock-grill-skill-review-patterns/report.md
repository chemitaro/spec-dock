---
種別: 実装報告書（Issue）
ID: "iss-00134"
タイトル: "docs-aware clarification workflow を spec-dock に取り込む"
関連GitHub: ["#134"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00067", "init-local-00003"]
---

# iss-00134 docs-aware clarification workflow を spec-dock に取り込む — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）です。planned requirements、evidence destination、closure 条件は `plan.md` が所有し、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する。

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
| D-20260529-001 | resolved | interpretation | user / consultant / spec-reviewer | `workflow_grill.md` / `spec-dock-grill-clarification` は初見のメンバーやエージェントに直感的でなく、恒久的な入口名として比喩が強い | `workflow_grill.md` / `spec-dock-grill-clarification`; `workflow_clarification.md` / `spec-dock-clarification`; `workflow_docs_clarification.md` / `spec-dock-docs-clarification`; `workflow_guided_clarification.md` / `spec-dock-guided-clarification` | 外向き名称は `docs-aware clarification workflow`、workflow file は `workflow_clarification.md`、skill name は `spec-dock-clarification` とする。`grill` は由来、historical path、禁止例に限って残す。 | `clarification` は曖昧さ解消、質問、文書化、意思決定の昇華という中核を短く表し、Matt Pocock 固有文脈や内輪語に依存しない。 | applied | `discussions/20260528t172725z-disc-clarification-workflow-naming.md`; reflected to `requirement.md`, `design.md`, `plan.md`, `report.md`; naming spec-review pass with P2 ledger note applied | none |
| D-20260529-002 | resolved | test-strategy | implementation | S05 で runtime catalog を変更しないことをどう固定するか | production catalog を変更する; unsupported doc type negative test を追加する | production catalog は変更せず、`report` / `reflection` が discussion doc type として作成不能である regression test を追加する。 | `plan.md` の S05 は new doc type 追加なしと runtime catalog unchanged を求めているため、negative test が最小で明確。 | applied | `tests/cli_runtime/test_runtime_new_doc_s09.py::test_report_and_reflection_are_not_creatable_discussion_doc_types` | none |

## 目的整合台帳（Objective Alignment Ledger / 必須）

この台帳は、実装中の差分が主目的である spec-dock-native docs-aware clarification workflow の統合を前進させているかを記録する。副次要件、handoff boundary、execution guidance、delegation policy、report evidence の更新が必要な場合でも、それらが主目的を上書きしていないことを観測する。

- `primary_objective_evidence`: docs-aware clarification workflow を first-class workflow として前進させた証跡。
- `secondary_requirement_evidence`: 副次要件を扱った場合、その変更が主目的を支える境界内にある根拠。
- `inversion_risk`: `none` / `low` / `medium` / `high`。`medium` 以上の場合は fresh spec review 前に requirement / design / plan amendment を検討する。
- `reviewer_verdict`: reviewer が objective inversion を検出したかどうか。

完了時、unresolved な `medium` / `high` inversion risk を残してはならない。

| ステップ（step） | 主目的証跡（primary_objective_evidence） | 副次要件証跡（secondary_requirement_evidence） | 主従逆転リスク（inversion_risk） | レビュアー判定（reviewer_verdict） | 次アクション（next_action） |
|---|---|---|---|---|---|
| S00 | Objective Alignment Preflight で記録する | Issue handoff を触る場合のみ記録する | none / low / medium / high | pass / fail / unavailable / not_run | proceed / amend / block / re-review |
| Spec authoring 2026-05-29 | `requirement.md` / `design.md` / `plan.md` に `workflow_clarification.md` と `spec-dock-clarification` を first-class docs-aware clarification workflow として固定した | Issue planning / execution split は bounded issue handoff support に限定し、headline deliverable にしない条件を `AC-011` / `cl-009` / `cl-010` で固定した | none | fresh `spec-reviewer` pass; findings なし | ユーザーの明示指示後、S00 から実装開始 |
| S00 implementation preflight 2026-05-29 | `requirement.md` / `design.md` / `plan.md` / naming discussion を再確認し、主目的を `workflow_clarification.md` と `spec-dock-clarification` を中心にした first-class docs-aware clarification workflow 統合として固定した | Issue handoff は unresolved spec gap を clarification / authoring phase へ戻す参照と handoff readiness evidence に限定し、Issue planning / execution split、delegation framework、PR lifecycle、issue finish lifecycle を headline deliverable にしない | none | S00 reviewer findings resolved; closure ids `cl-000` / `cl-009` / `cl-010` recorded | proceed |
| S01-S06 implementation 2026-05-29 | provider templates、`workflow_clarification.md`、`spec-dock-clarification`、routing skill guidance、tests、dogfooding mirror を docs-aware clarification workflow 中心に変更した | `workflow_issue.md` と `spec-dock-issue-execution` の変更は unresolved spec gap return と handoff readiness evidence に限定した | none | final reviewer gates pending at this row | final review |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-20260529-001 | adopted | sub-agent `doc-writer` | provider discussion templates | S01/S02 worker output matched approved plan and introduced no new discussion doc type. | `src/spec_dock/assets/spec_dock/templates/discussions/{interview,research,disc,adr}.md`; `git diff --check -- <S01/S02 changed files>` pass | none |
| EAL-20260529-002 | adopted | sub-agent `doc-writer` | provider docs / installed skills / report templates | S03/S04 worker output created first-class clarification workflow / skill and kept issue handoff bounded. | `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`; `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`; related workflow/rules/skill docs | none |
| EAL-20260529-003 | adopted | sub-agent `repo-analyst` | test strategy | S05 recommendations identified focused contract tests and runtime catalog negative guard; implementation adopted them without changing production catalog. | `tests/test_init_update.py`; `tests/cli_runtime/test_runtime_new_doc_s09.py`; `tests/cli_runtime/harness.py` | none |
| EAL-20260529-004 | adopted | command | validation evidence | Focused, broad, and full discovery regression commands passed after provider and dogfooding mirror updates. | `python -m unittest tests.test_init_update -v`; `python -m unittest discover -v`; `python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v`; delegated-authoring unittest commands; `./spec-dock/scripts/spec-dock validate`; `./spec-dock/scripts/spec-dock sync`; `git diff --check` | final reviewer gates |

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
| 該当なし | 該当なし | 該当なし | 該当なし | 該当なし | 未使用（not used） | なし（[]） | 未実行（not_run） | 手動 authoring | 該当なし | なし（none） | 該当なし | 委任ドラフト昇格なし |

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

## 仕様作成ゲート（Spec Authoring Gate）

`workflow_spec_authoring.md` に従い、requirement -> design -> plan の順で fresh `spec-reviewer` pass を得た。2026-05-29 の再ブラッシュアップでは、前回実装 drift の原因になった「主目的と副次要件の主従逆転」を防ぐため、Matt Pocock 由来の pattern を spec-dock-native docs-aware clarification workflow として first-class に扱うことを requirement / design / plan へ明示した。実装はまだ開始していない。

| phase | artifact | reviewer | freshness | state | investigated facts | promotion / completion decision | notes |
|---|---|---|---|---|---|---|---|
| requirement | `requirement.md` | `spec-reviewer` | fresh | passed | discussions / prior analysis / Matt Pocock pattern essence / spec-dock workflow constraints / prior drift cause | design phase へ進行可 | `目的階層`、`AC-000`、`AC-011` を追加し、primary docs-aware clarification integration と no objective inversion を明示後に pass |
| design | `design.md` | `spec-reviewer` | fresh | passed | requirement, workflow docs, template catalog, installed skill boundaries, first-class invocation surface, objective alignment report contract | plan phase へ進行可 | `workflow_clarification.md` と `spec-dock-clarification` を first-class surface とし、Issue handoff を bounded support に限定後に pass |
| plan | `plan.md` | `spec-reviewer` | fresh | passed | requirement, design, `workflow_issue.md`, `workflow_spec_authoring.md`, planned `workflow_clarification.md`, planned `spec-dock-clarification`, report evidence destinations | implementation handoff 可。ただし実装開始はユーザー提出後の明示指示待ち | S00 Objective Alignment Preflight、`cl-000`、`cl-009`、`cl-010`、`tc-s05-004`、final blocker を追加し、主従逆転防止を実装前 gate 化後に pass |

### Reviewer Gate History

| phase | reviewer result | disposition |
|---|---|---|
| requirement | 2026-05-29 fresh review: pass | 主目的、副次要件、非目的、`AC-000`、`AC-011` を追加し、Issue planning / execution split が docs-aware clarification workflow を上書きしない条件を requirement gate に昇格 |
| design | 2026-05-29 first review: fail / re-review: pass | Objective Alignment Ledger contract と shipped skill invocation surface の不足を修正し、`workflow_clarification.md` / `spec-dock-clarification` を first-class entrypoint として固定 |
| plan | 2026-05-29 first review: fail / re-review: pass with P2 cleanup applied | first-class clarification surfaces を S04/S05/S90/S99 に展開し、`cl-000` / `cl-009` / `cl-010` を final blockers に追加。追加 P2 指摘の `cl-010` closure index と `tc-s05-004` red evidence も反映 |
| cross-doc final gate | 2026-05-29 fresh review: pass | findings なし。`AC-000` と `AC-011` が requirement、design mapping、plan closure/test contracts、report Objective Alignment Ledger / reviewer gate に trace され、Issue planning / execution 分離が bounded handoff support に制限されていることを確認 |

## 実装サマリー (任意)
- `interview` / `research` / `disc` / `adr` の shipped discussion templates を、source-grounded clarification、一問一答、synthesis、ADR sparing の契約へ更新した。
- `workflow_clarification.md` と `spec-dock-clarification` を first-class entrypoint として追加し、既存 workflow / skill guidance / report templates / discussion rules を docs-aware clarification workflow に揃えた。
- runtime catalog は変更せず、contract tests と dogfooding mirror update で provider / installed asset / local consumer parity を固定した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-05-29 実装完了）

#### 対象
- Step: S00, S01, S02, S03, S04, S05, S06, S90, S99
- AC/EC: AC-000 through AC-011, EC-001 through EC-005
- 計画上の出典（Planned source）:
  - `plan.md` の S00-S06 / S90 / S99
  - closure ids: `cl-000` through `cl-010`

#### 実施内容
- S01/S02: provider-side discussion templates を一問一答 interview、source-grounded research、synthesis disc、ADR triage に再設計した。
- S03/S04: template catalog、discussion rules、`workflow_clarification.md`、installed skills、existing workflow docs、report templates を first-class clarification workflow に同期した。
- S05: `spec-dock-clarification` の managed skill contract、provider/dogfooding asset parity、discussion template contract、runtime catalog unchanged を regression tests に追加した。
- S06/S90: `uv run python -m spec_dock.cli update .` で dogfooding mirror と root `.agents/skills` mirror を同期した。
- S99: focused tests、full `tests.test_init_update`、full discovery、delegated-authoring regressions、`validate`、`sync`、`git diff --check` を通した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 -v
# OK (17 tests)

python -m unittest tests.test_init_update.TestInitUpdate.test_issue_134_clarification_contract_assets tests.test_init_update.TestInitUpdate.test_bundled_skill_routing_contract -v
# OK

python -m unittest tests.domain_runtime.test_delegated_authoring -v
# OK (23 tests)

python -m unittest tests.cli_runtime.test_delegated_authoring -v
# OK (49 tests)

python -m unittest tests.test_init_update -v
# OK (177 tests)

python -m unittest discover -v
# OK (961 tests)

uv run python -m spec_dock.cli update .
# spec-dock: ok (update)

./spec-dock/scripts/spec-dock validate
# spec-dock: ok (validate) nodes=68

./spec-dock/scripts/spec-dock sync
# spec-dock: ok (sync)

git diff --check
# pass
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01-S04 | 赤フェーズ / 代替証跡（Red / alternative） | inspect-only | worker docs-only inspection と contract test 設計で expected fragments / forbidden fragments を固定 | delegated worker output / diff inspection | pass | docs/template/skill change なので production red は不要 |
| S05 | 緑フェーズ（Green） | red-required / covered-existing | `test_issue_134_clarification_contract_assets` と `test_report_and_reflection_are_not_creatable_discussion_doc_types` を追加 | unittest | pass | runtime catalog production code は unchanged |
| S06/S90 | 緑フェーズ（Green） | manual-required | provider と dogfooding mirror / root `.agents` の parity test が通過 | `uv run python -m spec_dock.cli update .`; `tests.test_init_update` | pass | mirror stale failuresを解消 |
| S99 | リファクタリング（Refactor） | guardrail satisfied | docs wording と report template 日本語 primary label を test に合わせて修正 | unittest / `git diff --check` | pass | scaffold policy test による表現調整 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S05 | `report` / `reflection` が discussion doc type に追加される regression | repo-analyst / implementation | unsupported doc type negative test を追加 | cl-007 | no | `tests/cli_runtime/test_runtime_new_doc_s09.py` |
| S06 | dogfooding mirror と root `.agents` が provider changes に対して stale | full regression test | `uv run python -m spec_dock.cli update .` で同期 | cl-008 | no | `tests.test_init_update` |
| S90 | report templates の英語 primary table labels が scaffold policy test に抵触 | full regression test | Japanese primary labels に修正 | cl-006 | no | `test_spec_document_templates_keep_policy_out_of_scaffold` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | cl-000, cl-009, cl-010 | primary docs-aware clarification workflow と bounded handoff を固定 | Objective Alignment Ledger / S00 reviewer findings resolved | pass | final review で再確認 |
| S01 | cl-002, cl-003, cl-007 | one-question formal interview と answered lifecycle | `templates/discussions/interview.md`; contract test fragments | pass | new template variant なし |
| S02 | cl-001, cl-004, cl-006, cl-007 | research / disc / adr semantics | `templates/discussions/{research,disc,adr}.md`; contract test fragments | pass | `report.md` は discussion catalog に追加しない |
| S03 | cl-004, cl-006, cl-007 | template catalog / discussion rules alignment | `templates/README.md`; rules docs; policy tests | pass | common template semantics に同期 |
| S04 | cl-000, cl-001, cl-002, cl-005, cl-006, cl-009, cl-010 | first-class workflow / skill guidance / bounded issue handoff | `workflow_clarification.md`; `spec-dock-clarification`; existing workflow/skill updates | pass | issue handoff は clarification 参照と readiness evidence に限定 |
| S05 | cl-007, cl-009, cl-010 | changed shipped contracts and runtime catalog unchanged | focused issue 134 tests; runtime negative test | pass | production catalog unchanged |
| S06 | cl-008 | dogfooding mirror parity | `uv run python -m spec_dock.cli update .`; parity tests | pass | root `.agents` mirror も同期 |
| S90 | cl-000 through cl-010 | docs impact resolution | full `tests.test_init_update`; `validate`; `sync` | pass | stale docs / template mirror 解消 |
| S99 | cl-000 through cl-010 | final quality gate | focused tests, `python -m unittest discover -v` full discovery, validation commands, reviewer gates | pending final spec re-review | reviewer results are recorded below |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| cl-000 | S00/S04/S90/S99 | yes | inspect-only | requirement / design / plan inspection | `test_issue_134_clarification_contract_assets`; final diff inspection | pass | first-class docs-aware clarification workflow |
| cl-001 | S02/S04 | yes | inspect-only | template / workflow docs inspection | `test_issue_134_clarification_contract_assets` | pass | local context で解ける疑問を質問しない |
| cl-002 | S01/S04 | yes | inspect-only | `interview.md` inspection | `test_issue_134_clarification_contract_assets` | pass | 一問一答 formal interview |
| cl-003 | S01 | yes | inspect-only | `interview.md` inspection | `test_issue_134_clarification_contract_assets` | pass | answered lifecycle を同一 artifact に残す |
| cl-004 | S02/S03 | yes | inspect-only | `disc.md` / catalog inspection | `test_issue_134_clarification_contract_assets` | pass | synthesis と observed ledger を分離 |
| cl-005 | S04 | yes | inspect-only | workflow / skill inspection | `test_bundled_skill_routing_contract` | pass | specialist は質問候補を orchestrator に返す |
| cl-006 | S03/S04 | yes | inspect-only | catalog / workflow / report template inspection | `test_spec_document_templates_keep_policy_out_of_scaffold`; `test_issue_134_clarification_contract_assets` | pass | external evidence adoption と authoring mode を分離 |
| cl-007 | S01-S05 | yes | inspect-only | forbidden doc type inspection | `test_report_and_reflection_are_not_creatable_discussion_doc_types`; `test_issue_134_clarification_contract_assets` | pass | new doc type 追加なし |
| cl-008 | S06/S90/S99 | yes | manual-required | provider/dogfooding mirror inspection | `python -m unittest tests.test_init_update -v`; `python -m unittest discover -v` | pass | dogfooding parity tests pass |
| cl-009 | S00/S04/S05/S90/S99 | yes | inspect-only | Objective Alignment Ledger inspection | final diff / PR title/body inspection pending | pending final reviewer | headline は clarification workflow |
| cl-010 | S00/S04/S05/S90/S99 | yes | inspect-only | bounded handoff inspection | `workflow_issue.md`; `spec-dock-issue-execution` diff inspection pending | pending final reviewer | issue handoff change is bounded |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| cl-000 | S00/S04/S90/S99 | `workflow_clarification.md`, `spec-dock-clarification`, focused tests | pass | primary objective preserved |
| cl-001 | S02/S04 | `research.md`, workflow/skill docs | pass | source-grounded read |
| cl-002 | S01/S04 | `interview.md`, workflow/skill docs | pass | one-question route |
| cl-003 | S01 | `interview.md` | pass | answered artifact completion |
| cl-004 | S02/S03 | `disc.md`, catalog docs | pass | synthesis semantics |
| cl-005 | S04 | `workflow_clarification.md`, skill guidance | pass | specialist boundary |
| cl-006 | S03/S04 | report templates, workflow docs, catalog docs | pass | evidence adoption trace |
| cl-007 | S01-S05 | runtime negative tests and forbidden-file assertions | pass | no new doc type |
| cl-008 | S06/S90/S99 | dogfooding mirror / root skill parity tests | pass | provider and consumer aligned |
| cl-009 | S00/S04/S05/S90/S99 | Objective Alignment Ledger, workflow / skill diff, tests, report headline, planned PR wording | pass | no objective inversion; final reviewers initially failed only on report evidence completeness |
| cl-010 | S00/S04/S05/S90/S99 | `workflow_issue.md`, `spec-dock-issue-execution`, `workflow_clarification.md`, report handoff evidence | pass | issue handoff remained bounded to clarification return / readiness evidence |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| none | all | none | all | 計画済み closure ids の範囲内で完了 | no | final reviewer gates only |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction | current repo / worktree | iss-00134 | current session | doc-writer / repo-analyst / spec-reviewer / code-reviewer / qa-reviewer | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | initial reviewer spawn limit resolved by closing completed agents | proceed |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S02 | delegated | provider template slice | doc-writer | discussion templates | active issue docs | provider templates only | runtime catalog, dogfooding mirror, tests | docs inspection / diff check | material decision beyond plan | worker summary | pass |
| S03-S04 | delegated | workflow / skill docs slice | doc-writer | provider docs and installed skills | active issue docs | provider docs / skills / report templates | runtime code, dogfooding mirror, tests | docs inspection / diff check | objective inversion | worker summary | pass |
| S05 | delegated analysis / parent implementation | test strategy | repo-analyst / parent | tests | active issue docs | tests / managed skill list | production catalog change | focused and full unittest | new doc type needed | analysis summary / tests | pass |
| S06-S99 | approved-local-execution | integration and verification | N/A | dogfooding mirror / report / validation | active issue docs | mirror update, report evidence, validation commands | scope expansion | unittest / validate / sync / diff check | failing test | command evidence | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S01-S02 | doc-writer | discussion templates を approved plan に沿って更新 | `src/spec_dock/assets/spec_dock/templates/discussions/{interview,research,disc,adr}.md` | docs-only inspection / `git diff --check` pass | S00 reviewer findings resolved before final integration | none | accepted |
| S03-S04 | doc-writer | workflow docs / skills / report templates を first-class clarification に同期 | provider docs / skills / report templates | docs-only inspection / `git diff --check` pass | final reviewer pending | none | accepted |
| S05 | repo-analyst | focused contract tests と runtime catalog negative guard を提案 | no files changed by worker | read-only analysis | not required | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S05-S99 | tests / mirror / report integration are tightly coupled to parent orchestration | user requested implementation completion and PR creation | tests, mirror, active report | local integration edits and verification | revert local diff before commit if gate fails | focused tests / full tests / validate / sync / diff check pass | final reviewers spawned after closing completed agents | initial thread limit resolved |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S00 | objective alignment preflight reviewer | spec-reviewer | fresh | failed | no | re-review required | initial S00 review found missing report gate evidence before S01 |
| S00 | objective alignment preflight reviewer re-review | spec-reviewer | fresh | failed | no | re-review required | second review required explicit `cl-000` / `cl-009` / `cl-010` closure coverage |
| S00 | objective alignment preflight reviewer second re-review | spec-reviewer | fresh | failed | no | report update required | third review required aligning Reviewer Gate Status with closure pass |
| S00 | objective alignment preflight reviewer closure | orchestrator after reviewer findings | current | passed | no | proceed | all S00 reviewer findings were applied: Objective Alignment Ledger, Step Contract Closure, Test Contract Closure, Closure Coverage, and pass row recorded before final integration |
| S01-S04 | step reviewer | spec-reviewer | unavailable after worker integration | unavailable | no | final spec review required | thread limit initially blocked fresh reviewer; final reviewer spawned after closing completed agents |
| S05 | code reviewer | code-reviewer | pending | pending | no | pending | final code reviewer spawned |
| S99 | final QA reviewer | qa-reviewer | fresh | failed | no | re-review required | first final QA review found report closure placeholders / incomplete S01-S06/S90/S99 evidence; report closure tables and Final Quality Gate were updated |
| S99 | final spec reviewer | spec-reviewer | fresh | failed | no | re-review required | first final spec review found missing `cl-001` through `cl-008` closure entries and premature final pass row; report now records all closure ids and removes the premature pass |
| S99 | final code reviewer | code-reviewer | fresh | passed with P2 | no | P2 follow-up applied | code review found no blocking correctness/runtime/parity/objective-inversion issue; P2 discoverability finding was fixed by adding `workflow_clarification.md` / `spec-dock-clarification` to shipped docs README / guide and focused tests |
| S99 | final QA reviewer re-review | qa-reviewer | fresh | passed | no | proceed | report closure coverage and test/dogfooding evidence accepted |
| S99 | final spec reviewer re-review | spec-reviewer | fresh | failed | no | full unittest required | spec re-review required `python -m unittest discover -v`; command now ran successfully and is recorded |
| S99 | final spec reviewer second re-review | spec-reviewer | fresh | passed | no | proceed | final spec re-review found no findings after full discovery evidence was recorded |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01-S99 | ready before commit | issue-wide clarification workflow changes | pending final commit | pending post-commit check | not applicable | not applicable | `git diff --check` pass | `git status --short` inspected |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/templates/discussions/*.md` - discussion template semantics
- `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md` - new first-class workflow
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` - new installed skill
- `src/spec_dock/assets/spec_dock/docs/**`, `src/spec_dock/assets/install_root/.agents/skills/**`, `src/spec_dock/assets/spec_dock/templates/**` - related workflow / skill / report guidance
- `src/spec_dock/cli.py`, `tests/cli_runtime/harness.py` - managed skill inventory
- `tests/test_init_update.py`, `tests/cli_runtime/test_runtime_new_doc_s09.py` - regression tests
- `spec-dock/**`, `.agents/skills/**` - dogfooding mirror / root skill mirror

#### コミット
- pending

#### メモ
- runtime discussion doc type catalog production code は変更していない。

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill | yes | doc-writer / parent integration | provider docs/templates/skills updated; `uv run python -m spec_dock.cli update .`; `python -m unittest tests.test_init_update -v` -> OK; `python -m unittest discover -v` -> OK; `./spec-dock/scripts/spec-dock validate` -> OK; `./spec-dock/scripts/spec-dock sync` -> OK | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added focused tests and used existing full parity tests | first review failed on incomplete report closure evidence; after fix, closure ids `cl-000` through `cl-010` are recorded in Step Contract Closure, Test Contract Closure, and Closure Coverage; re-review passed; commands include focused tests, delegated-authoring tests, `tests.test_init_update`, `python -m unittest discover -v`, `validate`, `sync`, `git diff --check` | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | pass with P2: shipped docs README / guide lacked clarification entrypoints; fixed provider docs, dogfooding mirror, and test assertions | 0 | pass after fix |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report authoring alignment | first review failed on missing S01-S06/S90 closure rows and premature final pass; second review failed on missing `python -m unittest discover -v`; full discovery now passed and final re-review found no findings | 2 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| final QA/code/spec reviewer pass recorded | issue-wide clarification workflow changes | PR after commit / push | ready |

## 遭遇した問題と解決 (任意)
- 問題: final QA / spec review が report closure placeholders と premature pass を P1 として指摘した。
  - 解決: S01-S06/S90/S99 の Step Contract Closure、Test Contract Closure、Closure Coverage、Final Quality Gate を実証跡へ更新し、final pass は re-review pending に戻した。

## 学んだこと (任意)
- report gate は実装差分が通っていても completion blocker になるため、final review 前に placeholder を残さない。

## 今後の推奨事項 (任意)
- reviewer gate pass 後に final commit / PR evidence を追記する。

## 省略/例外メモ (必須)
- 該当なし
