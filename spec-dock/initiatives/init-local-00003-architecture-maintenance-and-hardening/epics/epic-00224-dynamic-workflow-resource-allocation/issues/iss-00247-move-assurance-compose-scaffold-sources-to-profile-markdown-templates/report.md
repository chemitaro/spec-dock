---
種別: 実装報告書（Issue）
ID: "iss-00247"
タイトル: "Move Assurance Compose Scaffold Sources To Profile Markdown Templates"
関連GitHub: ["#247"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00247 Move Assurance Compose Scaffold Sources To Profile Markdown Templates — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | scope | orchestrator + ChatGPT advisory | `report.md` を `design.md` / `plan.md` と同時に Markdown template 化するかが未確定だった | A: design/plan のみ移行; B: design/plan/report を同時移行; C: JSON section manifest 継続 | この Issue は `design.md` / `plan.md` の profile-specific scaffold prose を Markdown template source へ移し、`report.md` は現行 append-oriented managed-section behavior を維持する | `report.md` は placeholder materialization 対象外で evidence ledger lifecycle が別である。既存 research と ChatGPT advisory は report migration defer で一致した | applied | `discussions/20260629t022552z-research-profile-markdown-template-management.md`; `discussions/20260629t043419z-research-source-grounding-profile-markdown-templates.md`; `discussions/20260629t043420z-disc-template-source-scope-decision-synthesis.md`; `requirement.md` scope / AC-003 | `report.md` Markdown template 化は future follow-up 条件として残すが、この requirement phase の blocker ではない |
| D-002 | resolved | scope | user + GPT-5.5 Pro template pack | 前回 requirement は design/plan の JSON prose migration に焦点があり、実際の planning artifact template が薄すぎて手作業 authoring になっていた | A: 前回 requirement のまま design/plan だけ手動補強; B: ZIP template pack を採用して requirement/design/plan を再構成; C: compose を捨てて手動 copy にする | ZIP template pack を採用し、common requirement template と grade-specific design/plan templates を provider assets とする。Issue 自体は scaffold/template contract 変更なので `strict` として扱う | ZIP は common `issue/requirement.md` と `issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` を含み、README / matrix も existing `report.md` 維持を推奨している。ユーザーも先に template を決める方針を明示した | applied | `discussions/20260629t111542z-research-template-pack-adoption.md`; `requirement.md` AC-001〜AC-013; `design.md` DES-001〜DES-010; `plan.md` CLOS-001〜CLOS-009 | 前回 requirement spec-review pass は substantive change により stale。fresh `spec-reviewer` が必要 |
| D-003 | resolved | operation | orchestrator | 再 classify 後、runtime は `authorized_profile=standard` を返したが、Issue docs は `strict` として計画している | A: runtime standard に合わせて計画も standard に落とす; B: `.assurance.json` を手動編集する; C: runtime selection authority は standard のまま、issue-local gate だけ strict に引き上げる | C を採用する。runtime selection authority は `.assurance.json` の `authorized_profile` に限定し、manual strict grade は reviewer / execution obligation の引き上げとして扱う | 現行 classifier は requirement risk facts を defaults/unknown として扱う。scaffold/template contract 変更は strict 相当だが、selection authority を手動変更すると AC-003 / DES-003 に反する | applied | `assurance classify --stage requirement --format json` -> `authorized_profile=standard`; `assurance verify --format json` -> valid; `requirement.md` Assurance runtime note; `design.md` Assurance authority note | classifier の risk fact 抽出改善はこの Issue の実装対象外。必要なら follow-up |
| D-004 | resolved | operation | orchestrator | `guidance issue-planning` が reviewer pass / approved 後も `design-not-substantive` を返した | A: title を変えて preflight を通す; B: workflow preflight false positive として記録する; C: source docs を再度書き直す | B を採用する。現行 preflight は design frontmatter に `template` という語があると scaffold 扱いするため、Issue title `Move Assurance Compose Scaffold Sources To Profile Markdown Templates` に反応している。artifact 内容は fresh `spec-reviewer` pass 済み | `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/workflow.py` の `_classify_design_text` は frontmatter scaffold markers に `template` を含む。Issue title は GitHub issue title と一致させるべきで、判定器を回避するために改名しない | no_action | `guidance issue-planning` -> `reason_code=design-not-substantive`; `spec-reviewer` `019f1321-8efe-7cb0-9ffd-a9b7549cace6` -> pass | この false positive 自体は iss-00247 実装時に workflow preflight 改善候補として扱える |
| D-005 | resolved | scope | user | template の英語 title / heading が後続本文を英語化させる傾向がある | A: 英語見出しを許容する; B: 見出し・title・本文を日本語優先にする; C: 英語 template と日本語 template を別管理する | B を採用する。template は日本語を主言語にし、日本語だけで正確性が落ちる語だけ括弧で英語名を併記する | user-facing / agent-facing template の言語は、後続 authoring の出力言語を誘導する。日本語ユーザー向けの SpecDock 運用では日本語 title / heading が望ましい | applied | `requirement.md` BH-007 / AC-013 / CON-008; `design.md` DES-010; `plan.md` CLOS-009 / S01 / S90 | 実装時に template pack 採用と同時に日本語優先補正を行う |
| D-006 | resolved | operation | orchestrator | `guidance issue-execution` も `design-not-substantive` / `may_execute_approved_plan=false` を返した | A: guidance に従って停止する; B: canonical docs と fresh reviewer pass を根拠に manual fallback で進める; C: issue title を改名して guidance を通す | B を採用する。guidance 出力は観測事実として discussion に記録し、実行 authority は `workflow_issue.md` と承認済み issue docs に戻す | D-004 と同じ false-positive 系統であり、`requirement.md` / `design.md` / `plan.md` は具体化済み、fresh `spec-reviewer` pass もある。ユーザーは実行スクリプトが不安定な場合は手動実施し、問題を discussion に記録するよう指示している | applied | `guidance issue-execution` -> `state=blocked`, `reason_code=design-not-substantive`; `discussions/20260629t123000z-disc-issue-execution-guidance-false-positive-manual-fallback.md` | workflow classifier 改善候補として扱う。実装中に同種の command inconsistency があれば追加記録する |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | research | `requirement.md` | 既存 research は JSON section body から Markdown-template-first hybrid へ移す理由、scope、minimum acceptance を整理しており、現行コードと矛盾しない | `discussions/20260629t022552z-research-profile-markdown-template-management.md` | requirement に目的、背景、scope、AC として反映済み |
| EAL-002 | adopted | research | `requirement.md` | source-grounding research は親 Epic、現行 runtime、tests から safety contract と edge cases を確認した | `discussions/20260629t043419z-research-source-grounding-profile-markdown-templates.md` | requirement の MUST / MUST NOT / AC / EC に反映済み |
| EAL-003 | adopted | discussion + ChatGPT advisory | `requirement.md` | synthesis は design/plan-only migration、report defer、prose-less manifest/index の扱いを整理し、ChatGPT advisory と local facts を照合した | `discussions/20260629t043420z-disc-template-source-scope-decision-synthesis.md`; Oracle session `iss-247-template-scope` | requirement scope / non-scope / unresolved design questions に反映済み |
| EAL-004 | adopted | user-provided GPT-5.5 Pro template pack | `requirement.md`, `design.md`, `plan.md` | ZIP は common requirement template と grade-specific design/plan templates を提供し、今回の「手動 authoring 化している重大問題」を直接解消する source material である | `discussions/20260629t111542z-research-template-pack-adoption.md`; attachment `spec-dock-issue-grade-templates.zip` | requirement を template-pack adoption scope へ拡張し、design/plan を strict template contract / execution plan として再作成済み。fresh reviewer pending |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | `requirement.md` 目的 / AC-001 / AC-002 は design/plan scaffold prose を Markdown template source へ移すことを主目的として固定した | AC-003 は `report.md` compatibility、AC-004〜AC-011 は safety / verification obligations を固定した | superseded by OAL-002 after template pack adoption | previous pass by `spec-reviewer` `019f11b4-279b-7d41-bda7-5954ddc1fbc9` is stale |
| OAL-002 | `requirement.md` 目的 / AC-001 / AC-002 / AC-004 は template pack adoption、profile Markdown template source、common requirement template refresh を主目的として固定した | AC-005〜AC-013 は report compatibility、fail-closed safety、idempotence、dry-run、source binding、installed parity、日本語優先 template language policy を固定した | low | passed by fresh `spec-reviewer` `019f133b-ee00-73f0-8303-e2791a5d7638`; non-blocking P2 evidence freshness note resolved in report |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | `guidance issue-planning` -> `state=requirement-capture`, `reason_code=requirement-scaffold`; parent Epic docs; active issue placeholder; composer / assurance / artifact store code; unit / CLI tests; issue discussions | Blocking user question: none. Design-phase questions remain in `requirement.md` Q-001〜Q-003 | EAL-001〜EAL-003 adopted into `requirement.md` | passed by fresh `spec-reviewer` `019f11b4-279b-7d41-bda7-5954ddc1fbc9`; findings=[]; confidence=0.89 | no | promote requirement phase; next action: design authoring |
| requirement/design/plan refresh | user-provided ZIP inspected; `README.md`, `docs/template-matrix.md`, `docs/final-review.md`, common `issue/requirement.md`, and profile `issue-profiles/*/{design,plan}.md` confirmed; current generated design/plan were minimal managed sections only | Blocking user question: none. Fact: ZIP contains common requirement template, not four requirement templates; design/plan are grade-specific. Q-001〜Q-004 resolved in `requirement.md` section 11 after P2 reviewer note | EAL-004 adopted into `requirement.md`, `design.md`, `plan.md`; D-002 / D-003 applied | passed by fresh `spec-reviewer` `019f1321-8efe-7cb0-9ffd-a9b7549cace6`; one non-blocking P2 traceability note resolved | no | promote planning artifacts; rerun `assurance classify`, `assurance verify`, and `guidance issue-planning` |
| Japanese-first template policy update | user clarified that English template title / heading tends to induce English prose; issue docs updated with BH-007 / AC-013 / CON-008, DES-010, CLOS-009 / S01 / S90 / S99 | Blocking user question: none. The policy applies to template title, heading, subheading, and explanatory prose; code identifiers / commands / paths may remain English where needed | D-005 applied into `requirement.md`, `design.md`, `plan.md`; OAL-002 updated | passed by fresh `spec-reviewer` `019f133b-ee00-73f0-8303-e2791a5d7638`; review_status=pass; one non-blocking P2 evidence freshness note resolved here | no | proceed to implementation planning handoff; keep CLOS-009 in execution closure coverage |

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

## 実装サマリー (任意)
- 実装はまだ開始していない。
- この時点の更新は、ユーザー提供の GPT-5.5 Pro template pack を採用するための requirement / design / plan refresh と authoring evidence の記録である。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-29 20:11 - 20:45）

#### 対象
- Step: planning refresh before implementation
- AC/EC: AC-001〜AC-013
- 計画上の出典（Planned source）:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `discussions/20260629t111542z-research-template-pack-adoption.md`

#### 実施内容
- ユーザー提供 ZIP `spec-dock-issue-grade-templates.zip` を `/private/tmp/spec-dock-issue-grade-templates/` に展開し、common `requirement.md` と `issue-profiles/{lite,standard,strict,critical}/{design,plan}.md` を確認した。
- ZIP 採用により、前回の requirement-only pass は stale と判断した。
- `requirement.md` を template pack adoption / common requirement refresh / grade-specific design-plan templates 導入の scope に更新した。
- `design.md` を strict grade の設計契約として作成した。
- `plan.md` を strict / Spec-Locked TDD の implementation plan として作成した。
- `assurance classify --stage requirement` を再実行し、`.assurance.json` source binding を現行 artifact hash へ更新した。
- `assurance classify` は `authorized_profile=standard` を返したため、runtime selection authority と issue-local strict execution gate を分離する判断を D-003 として記録した。

#### 実行コマンド / 結果
```bash
unzip -l /Users/iwasawayuuta/.codex/attachments/ed533576-0494-4554-8480-1ea2c23320e0/spec-dock-issue-grade-templates.zip

result: pass; common requirement template and lite/standard/strict/critical design/plan templates were present.
```

```bash
./spec-dock/scripts/spec-dock assurance classify --stage requirement --format json

result: pass; .assurance.json written; authorized_profile=standard, lite_candidate=false.
```

```bash
git diff --check

result: pass.
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| planning refresh | docs inspection | ZIP template pack presence and adoption rationale | common requirement and profile design/plan files present | `unzip -l`; `sed`; `rg`; discussion artifact | pass | implementation not started |
| planning refresh | assurance binding | updated source binding after substantive artifact edits | `.assurance.json` regenerated | `assurance classify --stage requirement --format json` | pass | runtime `authorized_profile=standard`; manual strict gate recorded |
| planning refresh | formatting | Markdown diff has no trailing whitespace errors | no diff-check errors | `git diff --check` | pass | no code tests run because no implementation yet |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| planning refresh | runtime classifier reports standard while issue docs use strict grade | `assurance classify` output | recorded as D-003; separated runtime selection authority from issue-local strict gate | CLOS-002 / CLOS-008 | no | `requirement.md`, `design.md`, `plan.md`, D-003 |
| planning refresh | current report template contains future implementation slots | spark-worker quick check | clarified implementation not started and filled planning refresh evidence | CLOS-008 | no | this session log |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| planning refresh | CLOS-008 / CLOS-009 partial | docs / skill impact resolved or explicitly deferred; template language policy traceable | issue-local docs updated; spec-reviewer `019f133b-ee00-73f0-8303-e2791a5d7638` passed | pass | implementation not started |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| CLOS-001〜CLOS-009 | planning refresh | yes | planning-only | requirement/design/plan now define verification obligations | spec-reviewer `019f133b-ee00-73f0-8303-e2791a5d7638` | pass | actual implementation tests deferred to execution |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-001〜CLOS-009 | planned execution | `plan.md` closure index | planned | implementation not started |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | CLOS-001〜CLOS-009 | none | CLOS-001〜CLOS-009 | template pack adoption and Japanese-first template policy expanded the planning contract | yes | yes |

#### 実装未開始スロット
The remaining execution evidence sections below are intentionally left as future slots until implementation starts. They must be filled by the executor as each approved step runs.

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

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
`workflow_issue.md` is the policy source for workflow-scoped delegation consent. This report records observed consent, boundary, expiry, and denied / unavailable handling only.

| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction / explicit approval / none | ... | iss-00247 | current session / ... | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / write-capable delegation / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | none / denied / unavailable / host conflict | proceed / ask user / block gate / record waiver request |

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

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01 | step reviewer / final reviewer | code-reviewer / spec-reviewer / qa-reviewer | fresh / stale | passed / failed / unavailable / denied / waived / provisional | yes / no / N/A | proceed / blocked / incomplete / follow-up required | ... |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
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

### セッションログ（2026-06-29 HH:MM - HH:MM）

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
