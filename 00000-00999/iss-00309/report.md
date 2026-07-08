---
種別: 実装報告書（Issue）
ID: "iss-00309"
タイトル: "ChatGPT First Planning Skills And Fallback Route Redesign"
関連GitHub: ["#309"]
状態: "reviewed"
作成者: "iwasawayuuta"
最終更新: "2026-07-09"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00295", "init-local-00003"]
---

# iss-00309 ChatGPT First Planning Skills And Fallback Route Redesign — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

> `report.md` は観測証跡台帳（observed evidence ledger）の scaffold です。planned requirements、evidence destination、closure 条件は `plan.md` が持ち、この文書は実際の Red / Green / Refactor evidence、発見された tests、closure delta、reviewer status、commit/no-op evidence を記録する evidence slot です。workflow / compliance authority は skills、docs、accepted ADRs、reviewer gates に置きます。

## 仕様解釈・判断台帳（Spec Interpretation / Decision Ledger / 必須）

`report.md` は実装中・文書更新中に発生した material な仕様解釈、判断、plan 逸脱、tradeoff、open question、promotion / follow-up を記録する audit trail でもある。worker の raw note や作業 transcript を貼る場所ではなく、orchestrator が source docs、diff、tests、reviewer output と照合して issue-level の canonical entry に統合する。

Material な判断がない場合もこの section は残し、次を明示する。

- D-001〜D-003 に、この Issue で採用した ChatGPT Use 直実行版、final quality relay 修正、final quality skip / template field 修正の判断を記録済み。
- 未解決の decision entry はない。

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
| D-001 | resolved | interpretation | orchestrator | ChatGPT Use 直実行版と SpecDock authoring script 経由版のどちらを採用するか | 直実行版を採用; script 経由版を採用; 両方を併用 | 検査可能な ZIP 実体が残った直実行版を正本候補に採用し、script 経由版は不採用 evidence とする | script 経由版は transcript だけが残り、ZIP の展開検査ができなかった。直実行版は ZIP listing / unsafe token scan / transcript render を確認できた | applied | EAL-006; EAL-007; `artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md` | script backend ZIP materialization は必要なら別 Issue で扱う |
| D-002 | resolved | scope / relay | spec-reviewer | `iss-00309` が parent Epic の final quality relay から漏れていた | `iss-00309` を中間 Issue として relay に追加; この Issue が個別 PR を作る; final quality Issue 側だけで吸収 | `iss-00306 -> iss-00309 -> iss-00307` の依存に更新し、中間 Issue として final quality Issue へ送る | Parent Epic は複数 Issue を順に finish し、最後の final quality Issue で Epic-wide quality gate と mergeable PR を作る方針であるため、`iss-00309` も relay に含める必要がある | applied | `iss-00309/.meta.json`; `iss-00307/.meta.json`; parent Epic `plan.md` | なし |
| D-003 | resolved | policy / template | spec-reviewer / qa-reviewer / code-reviewer | final quality skip policy と Epic plan template fields が薄く、multi-Issue implementation Epic が skip rationale だけで final quality Issue を省略できるように読めた | skip を single-Issue/docs-only/no-op に限定; multi-Issue でも skip rationale があれば許可; template fields は現状維持 | multi-Issue implementation Epic は final quality / PR delivery Issue を必須とし、single-Issue/docs-only/no-op 以外は Issue 作成前の別 accepted decision を必要とする。Epic plan template に final quality issue id、completion evidence、dependency-on-all-implementation-Issues、intermediate deferred PR delivery policy を追加する | REQ-012/REQ-013/AC-014 は final quality Issue と relay evidence を workflow contract として要求しており、template が証跡欄を持たないと将来の Epic planning が同じ漏れを再発させる | applied | M95 reviewer-fix evidence; `src/spec_dock/assets/spec_dock/templates/epic/plan.md`; `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | なし |
| D-002 | resolved | scope | spec-reviewer | `iss-00309` が parent Epic の final quality relay に接続されていない | `iss-00309` を例外扱いにする; `iss-00309` を `iss-00306 -> iss-00309 -> iss-00307` の relay に接続する | `iss-00309` は追加 implementation Issue として final quality Issue の前段に接続する | parent Epic は per-Issue PR delivery を禁じ、final quality Issue で PR delivery を行う方針であるため | applied | `./spec-dock/scripts/spec-dock deps add --from iss-00309 --to iss-00306`; `./spec-dock/scripts/spec-dock deps add --from iss-00307 --to iss-00309`; `epic-00295/plan.md` | なし |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | adopted | ユーザー回答（`interview`） | `requirement.md` / `design.md` / `plan.md` | ChatGPT-first を正規 planning route とし、4 tab 上限・timeout・browser failure は wait / retry / recovery 対象にする。従来 planning route は、人間が修正困難な障害を認識して明示承認した場合だけ使う emergency backup とする。 | `artifacts/20260708t150402z-interview-chatgpt-first-planning-route-fallback-boundary-interview.md` | 要件・設計・計画へ反映する |
| EAL-002 | adopted | ユーザー回答（`interview`） | `requirement.md` / `design.md` / `plan.md` | 既存 planning skill 名を ChatGPT-first primary route として維持し、従来 route は `-manual` suffix の human-approved backup skill として分離する。 | `artifacts/20260708t151122z-interview-primary-and-fallback-skill-naming-interview.md` | 要件・設計・計画へ反映する |
| EAL-003 | adopted | ユーザー回答（`interview`） | `requirement.md` / `design.md` / `plan.md` | 複数 Issue を持つ implementation Epic では final quality gate / PR delivery Issue を必須にする。single-Issue / docs-only / no-op Epic は skip rationale と completion evidence を置けば省略でき、単一 Issue Epic では Issue の品質ゲートが Epic の品質ゲートを兼ねられる。 | `artifacts/20260708t152452z-interview-final-quality-gate-issue-scope-interview.md` | 要件・設計・計画へ反映し、Issue Planning の実施タイミングは追加 research で具体化する |
| EAL-004 | adopted | ChatGPT GPT-5.5 Pro Extended 分析（`research`） | `requirement.md` / `design.md` / `plan.md` | Issue Planning timing は Option 3+ を採用する。Epic Planning では各 Issue の draft requirement / draft design / draft plan まで作成し、canonical Issue docs は Epic Execution 中の各 Issue start 直前または直後に、current repository state と prior Issues を踏まえて Issue Planning で正式化する。Issue-local に吸収できない drift は Epic Planning repair / clarification / ADR へ戻す。 | `artifacts/20260708t154900z-research-chatgpt-first-issue-planning-timing-and-epic-execution-workflow.md` | 要件・設計・計画へ反映する |
| EAL-005 | adopted | ユーザー決定（`ADR`） | `requirement.md` / `design.md` / `plan.md` / provider workflow docs / skills / templates | Option 3+ を accepted ADR として正式採用した。今後の workflow docs には end-to-end workflow と Issue draft lifecycle の PlantUML 図を取り込み、skills / templates はこの ADR を前提に更新する。 | `artifacts/20260708t161533z-adr-chatgpt-first-option-3-plus-issue-planning-workflow.md` | 要件・設計・計画へ反映し、実装段階で provider-side docs / skills / templates へ取り込む |
| EAL-006 | adopted | ChatGPT Use 直実行（`iss-00309-formal-specs-zip-2`） | `requirement.md` / `design.md` / `plan.md` / `artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md` / `artifacts/20260708t162513z-research-workflow-impact-map.md` / `artifacts/20260708t162514z-disc-implementation-scope-and-test-strategy.md` | 直実行版は repository-relative path を保持した ZIP 実体として検査でき、展開前検査で traversal や unsafe path は見つからなかった。要件・設計・計画は EAL-001〜EAL-005 の決定を反映し、ChatGPT output を evidence-only とする境界も明示しているため、今回の正本候補として採用した。配置時に SpecDock artifact slot rule に合わせ、同一 timestamp の補助 artifact は一意 slot へ改名した。 | `artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md`; sha256=`eb126a1ab2108528e5fc46e9b142e2b78eb80f7c2ca16fb2ed53a6ca9e25254f` | fresh `spec-reviewer` pass を取得するまでは execution-ready と扱わない |
| EAL-007 | rejected | SpecDock authoring script 経由（`iss-00309-script-formal-specs`） | `requirement.md` / `design.md` / `plan.md` | スクリプト経由は ChatGPT 応答上では ZIP 生成に成功したが、ローカル artifacts へ ZIP 実体が materialize せず、検査・展開・配置できなかった。今回の採用候補としては、検査可能な直実行版を優先する。スクリプト経由のプロンプト契約・preflight/pack prepare/backend invoke の挙動は今後の authoring runtime 改善の参考 evidence として保持する。 | script output claimed sha256=`7fd8f69dd4d9c72f0356fa2f96405359e061c0e78020a33723cc25b3c7e738e2`; repo-portable adopted evidence は EAL-006 に集約 | 必要なら別 Issue で script backend ZIP download/materialization の検証と改善を扱う |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | ChatGPT-first planning skill redesign を正規 workflow にする目的 | script 経由も試行し、配置可能性を比較した | 低（low） | pass |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| requirement | EAL-001〜EAL-006、ChatGPT Use 直実行 ZIP、既存 issue scaffold、parent Epic docs | なし | adopted | pass | いいえ（no） | promote |
| design | EAL-001〜EAL-006、ChatGPT Use 直実行 ZIP、Option 3+ ADR、workflow impact map | なし | adopted | pass | いいえ（no） | promote |
| plan | EAL-001〜EAL-006、ChatGPT Use 直実行 ZIP、implementation scope and test strategy artifact | なし | adopted | pass | いいえ（no） | promote |

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
  - legacy `discussions/` と既存 `iss-00126` などの manifest/Profile/probe/session artifacts は grandfathered evidence として残し、削除・rename・validation failure 化しない。

| ロール（created_by_role） | 範囲（scope_id） | ドラフトパス（artifact draft path） | 参照元（source_paths） | 予定反映先（intended_targets） | 採用状態（adoption_status） | 反映先（reflected_to） | 差分ガード結果（diff_guard_result） | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果（reviewer result） | 昇格判断（promotion decision） |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ChatGPT GPT-5.5 Pro Extended | iss-00309 | `artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md` | GitHub connector: `chemitaro/spec-dock` branch `iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign`; sanitized prompt summary in manifest | `requirement.md`, `design.md`, `plan.md`, `artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md`, `artifacts/20260708t162513z-research-workflow-impact-map.md`, `artifacts/20260708t162514z-disc-implementation-scope-and-test-strategy.md` | adopted | [`requirement.md`, `design.md`, `plan.md`, `artifacts/20260708t162512z-manifest-chatgpt-formal-spec-pack.md`, `artifacts/20260708t162513z-research-workflow-impact-map.md`, `artifacts/20260708t162514z-disc-implementation-scope-and-test-strategy.md`] | ZIP listing / unsafe token scan / transcript render: pass | 正本候補として統合 | fresh reviewer pass / execution-ready claim は ChatGPT から採用しない | なし | pass | promote |
| SpecDock authoring script + ChatGPT GPT-5.5 Pro Extended | iss-00309 | script-output-summary | `spec-dock authoring preflight`, `pack prepare`, `backend invoke`; GitHub connector: `chemitaro/spec-dock` branch `iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign` | `requirement.md`, `design.md`, `plan.md`, `artifacts/` | rejected | [] | transcript render: pass; local ZIP artifact: unavailable | 不採用 | ローカルに ZIP 実体が残らず、検査・展開できなかった | なし（今回の正本候補は直実行版で充足） | N/A | script backend ZIP materialization は follow-up 候補 |

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
- ChatGPT Use 直実行版と SpecDock authoring script 経由版を比較し、検査可能な ZIP 実体を持つ ChatGPT Use 直実行版を採用した。
- 初回 spec-reviewer は fail となり、final quality relay 接続と host-local evidence 除去を修正した。実装は fresh spec-reviewer pass まで開始しない。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-07-09 02:00 - 02:30）

#### 対象
- Step: S00 planning draft adoption / review-fix
- AC/EC: REQ-001〜REQ-020 / EC-001〜EC-010
- 計画上の出典（Planned source）:
  - `plan.md` section: 9. 実装ステップ / 10. 具体テストケース / 11. Step Closure Contract
  - closure ids: CLOS-001〜CLOS-010

#### 実施内容
- ChatGPT Use 直実行版の ZIP 内容を Issue 正本候補へ配置した。
- SpecDock authoring script 経由版はローカル ZIP 実体が取得できないため不採用 evidence とした。
- `iss-00309` を `iss-00306 -> iss-00309 -> iss-00307` の final quality relay に接続した。
- durable evidence から host-local absolute path を除去し、repo-relative artifact と hash に置き換えた。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock deps add --from iss-00309 --to iss-00306
./spec-dock/scripts/spec-dock deps add --from iss-00307 --to iss-00309
./spec-dock/scripts/spec-dock validate
git diff --check
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S00 | 代替証跡（planning characterization） | inspect-only | ChatGPT Use 直実行版と script 経由版を比較し、直実行版を採用した | transcript render / ZIP listing / docs inspection | pass | script 経由はローカル ZIP 未取得 |
| S00 | 緑フェーズ（Green） | docs placement | 要件・設計・計画・補助 artifacts を canonical Issue docs へ配置した | `rsync` / docs inspection | pass | artifact timestamp slot は一意化済み |
| S00 | リファクタリング（Refactor） | guardrail satisfied | `validate` と `diff --check` が通る状態へ調整した | 差分点検（diff inspection） / command | pass | fresh reviewer は未実施 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S00 | `iss-00309` が final quality relay に未接続 | spec-reviewer | deps add と parent Epic plan 修正 | D-002 / CLOS-010 | yes | `iss-00309/.meta.json`; `iss-00307/.meta.json`; `epic-00295/plan.md` |
| S00 | host-local absolute path が durable evidence に残存 | spec-reviewer | repo-relative artifact / sha256 へ置換 | D-001 / CLOS-010 | no | `report.md` EAL-006 / EAL-007 |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S00 | CLOS-001〜CLOS-010 | ChatGPT draft adoption / report gate cleanup / review-fix | `validate` pass; `diff --check` pass; spec-reviewer re-review pass | pass | implementation may start after commit/push evidence is recorded |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| TC-004 | S00 | yes | inspect-only | ChatGPT draft adoption and review-fix | `./spec-dock/scripts/spec-dock validate`; `git diff --check` | pass | spec-reviewer re-review pass |

- `closure id / test id` は Spec-Locked Closure Index の `id` を指す。別 alias を使う場合は `Closure Delta` で対応を記録する。

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-010 | S00 | `validate`; `diff --check`; spec-reviewer re-review | pass | implementation handoff allowed after commit/push evidence |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| changed | CLOS-010 | TC-004 | CLOS-010 | spec-reviewer P1 findings required relay/evidence fixes | yes | completed |

#### ワークフロー単位の named role 許可（Workflow-Scoped Authorization）
`workflow_issue.md` is the policy source for workflow-scoped authorization. This report records observed authorization source, boundary, expiry, and denied / unavailable / host conflict handling only.

Authorization source は、ユーザーによる SpecDock workflow 利用依頼でよい。範囲は active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility に限る。この section は role ごと・phase ごとの追加承認 gate ではなく、scope 内の named role 利用前に追加許可を求める根拠にしてはならない。

別途確認が必要なのは scope expansion、破壊的操作、外部公開、credential を伴う外部 mutation、private external system、SpecDock workflow 外の role 利用である。unavailable / denied / host conflict は fail-closed とし、fresh `passed` reviewer gate の代替にしてはならない。

| 許可元（authorization source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可 / host conflict 理由（denied / unavailable / host conflict reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user request to use SpecDock workflow | active repo/worktree | iss-00309 | current session | spec-reviewer / code-reviewer / qa-reviewer / read-only specialist | active repo/worktree、active SpecDock scope、current session、SpecDock-defined named roles、documented role responsibility | issue complete / session end / scope change / host policy conflict / user revocation | none | continue to fresh spec-reviewer re-review |

#### 実装委任ゲート（Implementation Delegation Gate）
`workflow_issue.md` is the policy source for delegation, reviewer gates, waiver, unavailable, denied, and host-conflict semantics. This report records observed evidence only.

| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S00 | approved-local-execution | issue planning draft adoption / report gate cleanup | N/A | `requirement.md`, `design.md`, `plan.md`, `report.md`, issue-local artifacts | active Issue docs | docs-only canonical adoption and report evidence updates | source code changes before fresh spec-reviewer pass | `./spec-dock/scripts/spec-dock validate`; `git diff --check`; fresh spec-reviewer | stop before implementation until fresh spec-reviewer pass | adopted docs / verification / risks / integration decision | pass |

#### 委任 worker 証跡（Delegated Worker Evidence）
| ステップ（step） | 委任ロール（delegated role） | 委任 worker 要約（delegated worker summary） | 変更ファイル（changed files） | 実行 tests または docs-only 検証（tests run or docs-only verification） | レビュアー判定（reviewer verdict） | 未解決リスク（unresolved risks） | 親統合判断（parent integration decision） |
|---|---|---|---|---|---|---|---|
| S00 | spec-reviewer | Initial review failed with two P1 findings and one P2 report cleanup finding; re-review returned no findings | read-only | review_status: pass | pass | none | accepted |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S00 | no parent implementation exception required | user workflow request | active Issue docs and parent Epic plan | docs-only review-fix | revert docs/deps changes if re-review fails | `validate` pass; `diff --check` pass | spec-reviewer passed | proceed to implementation |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
Lite は specialist / fallback evidence を必須化しないが、not applicable / skip reason を記録する。Standard は specialist evidence、skip reason、または manual fallback を記録する。Strict / Critical は specialist evidence または明示的な manual fallback を記録し、skip reason だけでは readiness evidence にしない。

| グレード（Grade） | 必要な専門家 / 代替（required specialist / fallback） | 使用状況（usage） | 証跡（evidence） | 鮮度 spec-reviewer 判定（fresh spec-reviewer verdict） | 実行可否（execution readiness） |
|---|---|---|---|---|---|
| strict | system-architect / implementation-planner / manual fallback | used | `artifacts/20260708t162513z-research-workflow-impact-map.md`; `artifacts/20260708t162514z-disc-implementation-scope-and-test-strategy.md`; ChatGPT Use 直実行 ZIP | pass | ready |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S00 | authoring gate | spec-reviewer | fresh | pass | no | promote | re-review confirmed relay dependency, evidence normalization, and report scaffold cleanup |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S00 | committed | ChatGPT draft adoption / review-fix scope | commit pending for review-fix delta | post-commit check pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `epic-00295-chatgpt-authoring-pack-installed-runtime/plan.md` - relay policy を `iss-00309` 追加後の final quality gate に合わせて修正。
- `iss-00307-final-quality-gate-and-mergeable-pr-delivery/.meta.json` - final quality Issue が `iss-00309` に依存するよう command-first で更新。
- `iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/.meta.json` - `iss-00309` が `iss-00306` に依存するよう command-first で更新。
- `iss-00309-chatgpt-first-planning-skills-and-fallback-route-redesign/report.md` - local path evidence と scaffold placeholder を整理。

#### コミット
- pending

#### メモ
- Fresh spec-reviewer re-review passed; implementation may proceed after this planning delta is committed.

---

### セッションログ（2026-07-09 02:30 - 03:20）

#### 対象
- Step: M1〜M7 / M90 partial — ChatGPT-first planning skills, manual backup skills, provider docs/templates, dogfood mirror, and managed skill registry
- AC/EC: REQ-001〜REQ-019 / EC-001〜EC-010
- 計画上の出典（Planned source）:
  - `plan.md` section: 3. Allowed change surface / 5. Milestone overview / 9. 実装ステップ / 10. 具体テストケース
  - closure ids: CLOS-001〜CLOS-009

#### 実施内容
- Provider-side installed skill assets に `spec-dock-initiative-planning-manual`、`spec-dock-epic-planning-manual`、`spec-dock-issue-planning-manual` を追加した。
- 既存 planning skill 名は維持し、`spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` を ChatGPT-first primary route として明文化した。
- `spec-dock-chatgpt-authoring` を、primary planning skills から呼ばれる evidence lane として再定義し、retryable / recoverable / blocked / stale / rejected / hard-unrecoverable の failure classification を追加した。
- `_MANAGED_SKILL_NAMES` と test harness の managed skill expectation に manual backup skill 3件を追加した。
- Workflow docs、authoring docs、Epic plan template、hub skill に、Option 3+、Issue draft lifecycle、final quality Issue policy、manual backup boundary、PlantUML 図を反映した。
- `uv run spec-dock update .` で dogfooding mirror の `.agents/skills`、`spec-dock/docs`、`spec-dock/templates` を provider-side source of truth から更新した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_chatgpt_authoring_managed_skill_contract tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_assets_cover_managed_manifest
uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_chatgpt_authoring_managed_skill_contract tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_assets_cover_managed_manifest tests/unit/infra/test_init_update.py::TestInitUpdate::test_bundled_skill_routing_contract
git diff --check
uv run spec-dock update .
./spec-dock/scripts/spec-dock validate
uv run pytest tests/cli_runtime
```

Observed result:
- focused unit tests: pass
- `git diff --check`: pass
- `uv run spec-dock update .`: pass with existing repo-root shortcut warning
- `./spec-dock/scripts/spec-dock validate`: pass (`nodes=203`)
- `uv run pytest tests/cli_runtime`: pass (`1056 passed, 75 skipped`), re-run after M95 fix also pass (`1056 passed, 75 skipped`)
- `uv run pytest tests/unit`: pass (`968 passed`)

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| M1 | inspect/green | manual backup skills exist and state human-approved emergency backup | 3つの `-manual` skill を provider assets と dogfood mirror に追加 | `find`; `rg human-approved emergency backup` | pass | queued/retryable/recoverable failure では使わない境界を記載 |
| M2 | inspect/green | primary planning skills are ChatGPT-first while names remain stable | 既存 planning skills に ChatGPT-first primary route と manual backup boundary を追加 | `rg ChatGPT-first primary route` | pass | canonical docs / EAL / fresh reviewer は planning skill が所有 |
| M3 | inspect/green | ChatGPT authoring remains evidence-only and classifies failures | `spec-dock-chatgpt-authoring` に failure classification と forbidden claims を維持 | focused unit test / docs inspection | pass | hard-unrecoverable は explicit human approval 前提 |
| M4 | green | managed registry installs manual skills | `_MANAGED_SKILL_NAMES` と test harness を更新 | focused unit test | pass | manual skills are copied by init/update |
| M5 | inspect/green | workflow docs include Option 3+ / diagrams / manual boundary | provider docs と dogfood docs に PlantUML と workflow text を追加 | `rg Option 3+`; `rg Issue Draft To Canonical Planning And Execution` | pass | unsupported authoring commands は supported route として案内しない |
| M6 | inspect/green | Epic plan template includes final quality and draft handoff fields | `templates/epic/plan.md` に classification / final quality / draft lifecycle を追加 | `rg final quality Issue policy` | pass | single-Issue/docs-only/no-op skip rationale を残せる |
| M7 | green | dogfooding mirror reflects provider-first changes | `uv run spec-dock update .` で mirror 更新 | update command / `rg` / `validate` | pass | provider side remains source of truth |
| M90 | green | focused regression and structural checks pass | focused unit tests, `diff --check`, `validate`, `tests/cli_runtime` | commands above | pass | `tests/cli_runtime`: `1056 passed, 75 skipped` |
| M95 | red/review-fix | final reviewer blockers are repaired before pass claim | spec-reviewer P1 and qa-reviewer P1 on final quality template/policy | reviewer output; focused tests; `rg`; `git diff --check`; `tests/unit` | pass | P1 fixed by tightening skip eligibility and adding final quality relay template fields; `tests/unit`: `968 passed` |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| M1 | CLOS-002 | 3つの `-manual` skill が provider assets に存在し human approval boundary を持つ | provider / dogfood skill files; focused tests | pass | manual route is emergency backup only |
| M2 | CLOS-001, CLOS-004 | 既存 planning skills が ChatGPT-first primary route を示す | `rg ChatGPT-first primary route`; focused tests | pass | primary skill names remain unchanged |
| M3 | CLOS-003 | `spec-dock-chatgpt-authoring` が evidence-only boundary を保つ | forbidden claims section; focused tests | pass | failure classification added |
| M4 | CLOS-006 | managed skill registry と init output に manual skills が含まれる | `_MANAGED_SKILL_NAMES`; focused init test | pass | order: primary route / execution / authoring lane / manual backups |
| M5 | CLOS-004, CLOS-005, CLOS-007 | workflow docs に Option 3+ / final quality / diagrams が反映される | provider docs; dogfood docs; `rg` | pass | PlantUML uses quoted participant names and ASCII aliases |
| M6 | CLOS-005, CLOS-007 | Epic plan template が final quality Issue policy と draft handoff index を持つ | provider template; dogfood template | pass | final quality skip rationale included |
| M7 | CLOS-008 | dogfooding workspace が provider update の validation surface として整合する | `uv run spec-dock update .`; `validate` pass | pass | update warning was pre-existing shortcut skip |
| M90 | CLOS-010 | relevant pytest / validate / diff check / grep checks を実行または blocker として記録する | focused tests pass; validate pass; diff check pass; `tests/cli_runtime` pass | pass | `tests/cli_runtime`: `1056 passed, 75 skipped` |
| M95 | CLOS-005, CLOS-007, CLOS-010 | final reviewer P1 fixes applied | final quality skip policy constrained; template fields added; focused tests and `tests/unit` pass | pass | re-review pending |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| TC-001 | M1〜M3 | yes | unit + inspect | skill baseline had no manual backup files | focused `test_chatgpt_authoring_managed_skill_contract`; `rg` | pass | primary/manual/evidence-only boundary covered |
| TC-002 | M5〜M6 | yes | inspect | docs/template lacked complete Option 3+ route | `rg Option 3+`; `rg Issue Draft To Canonical Planning And Execution`; template grep | pass | diagrams and final quality policy included |
| TC-003 | M4 | yes | unit + init simulation | managed manifest lacked manual skills | focused `test_bundled_skill_assets_cover_managed_manifest` | pass | harness updated |
| TC-004 | M7〜M90 | yes | command | provider-first mirror needed validation | `./spec-dock/scripts/spec-dock validate`; `git diff --check` | pass | nodes=203 |
| TC-005 | M5 | yes | inspect | unsupported commands must not be advertised as supported | `rg authoring adopt ...` | pass | only appears in Deferred / unsupported section |
| TC-006 | M95 | yes | reviewer | initial final reviewers found P1/P2 final-quality template gaps | fix applied; reviewer re-run pending | pending | re-run after full unit verification |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| CLOS-001 | M2 | planning skill diffs; focused test | pass | ChatGPT-first primary route |
| CLOS-002 | M1 | manual skill files; focused test | pass | human-approved emergency backup |
| CLOS-003 | M3 | authoring skill forbidden claims; focused test | pass | evidence-only lane |
| CLOS-004 | M2/M5 | docs and skill text | pass | Option 3+ and just-in-time Issue planning |
| CLOS-005 | M5/M6 | docs and template | pass | final quality Issue required/skipped |
| CLOS-006 | M4 | managed skill registry test | pass | manual skills distributed |
| CLOS-007 | M5/M6 | PlantUML grep / docs inspection | pass | workflow diagrams included |
| CLOS-008 | M7 | provider-first update and dogfood validation | pass | `uv run spec-dock update .` |
| CLOS-009 | M5 | unsupported command grep | pass | unsupported commands appear only as unsupported examples |
| CLOS-010 | M90 | focused tests / validate / diff check / `tests/cli_runtime` | pass | final reviewer gates pending |
| CLOS-010 | M95 | reviewer findings repair; focused tests; `tests/unit` | pass | spec/QA re-review pending |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| added | CLOS-002 | TC-001 | CLOS-002 | manual backup skills を provider managed assets として追加 | no | yes |
| changed | CLOS-006 | TC-003 | CLOS-006 | managed skill manifest に manual skill 3件を追加 | no | yes |
| changed | CLOS-007 | TC-002 | CLOS-007 | Option 3+ と lifecycle PlantUML を docs/templates に追加 | no | yes |
| changed | CLOS-005 | TC-002 / TC-006 | CLOS-005 | final quality Issue policy の skip eligibility と relay template fields が不足していた | no | pending re-review |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| M1〜M7 | approved-local-execution | scoped docs/skills/templates/test update after reviewer-passed plan | N/A | provider assets, dogfood mirror, focused tests | active Issue plan / provider source of truth | planned skills/docs/templates/registry/tests only | runtime command behavior beyond managed registry; unsupported authoring commands | focused unit tests; `validate`; `diff --check`; `tests/cli_runtime`; final reviewer gates | stop on failing tests or reviewer blockers | changed files, verification results, residual risks | pass; final reviewers pending |
| M95 | approved-local-execution | reviewer-fail repair for docs/template/skill policy | N/A | final quality policy wording and template fields | reviewer findings / active Issue requirement | provider docs/templates/skills/tests and dogfood mirror | unrelated runtime behavior | focused failing tests; `rg`; `diff --check`; full unit re-run; reviewer re-run | stop if P1/P0 remains | fix evidence and re-review result | fix applied; focused tests and `tests/unit` pass; re-review pending |

#### マイルストーン / commit 候補ゲート（Milestone / Commit Candidate Gate）
| マイルストーン / step | クロージャ状態（closure state） | コミット候補 / コミット範囲（commit candidate / scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| M1〜M7/M90 | reviewed | ChatGPT-first planning route docs/skills/templates/tests | commit pending | pending | N/A | N/A | N/A | N/A |
| M95 reviewer-fix | reviewed | final quality skip policy and template relay fields | commit pending | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- Provider assets:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning-manual/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning-manual/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning-manual/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-{initiative,epic,issue}-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-hub/SKILL.md`
  - `src/spec_dock/assets/spec_dock/docs/**`
  - `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
  - `src/spec_dock/cli.py`
- Tests:
  - `tests/cli_runtime/harness.py`
  - `tests/unit/infra/test_init_update.py`
- Dogfood mirror:
  - `.agents/skills/**`
  - `spec-dock/docs/**`
  - `spec-dock/templates/epic/plan.md`

#### メモ
- This Issue directly implements planned provider-side docs/skills/templates/test changes. Final PR delivery for the parent Epic remains owned by the final quality Issue relay, but this Issue still needs local final reviewer gates before `issue finish`.
- Initial final `spec-reviewer` failed with P1 findings on final-quality skip exceptions and Epic plan template fields. Initial `qa-reviewer` failed with the same template coverage as P1. `code-reviewer` passed with a P2 on the same template field gap. The implementation was tightened so multi-Issue implementation Epics require a final quality / PR delivery Issue, skip is limited to single-Issue/docs-only/no-op unless a separate accepted exception exists, and the Epic plan template now includes final quality issue id, completion evidence, dependency-on-all-implementation-Issues, and intermediate deferred PR delivery policy.

---

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / workflow / skill | yes | main orchestrator | `requirement.md`, `design.md`, `plan.md`, `artifacts/20260708t162513z-research-workflow-impact-map.md` | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | focused tests, full unit, validate, diff check, and cli_runtime re-run are adequate | initial P1 fixed; re-review pass with P2 stale ledger cleanup, which was fixed in D-003 | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | initial P2 final quality template gap fixed; re-review no findings | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report alignment | initial final P1/P2 findings fixed; M95 re-review no findings | 2 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| M1〜M95 implementation ledger | provider assets / dogfood mirror / tests / report | final response / PR / issue comment | ready for commit |

## 遭遇した問題と解決 (任意)
- 問題: `iss-00309` が parent Epic の final quality relay から漏れていた。
  - 解決: `iss-00309` を `iss-00306` に依存させ、`iss-00307` を `iss-00309` に依存させた。
- 問題: `report.md` に host-local absolute path evidence が残っていた。
  - 解決: repo-relative artifact と sha256 に置換した。

## 学んだこと (任意)
- ChatGPT/Oracle の実体 ZIP はローカル検査に有用だが、repo の durable evidence にはローカル絶対パスを残さず、repo-relative artifact と hash へ正規化する必要がある。

## 今後の推奨事項 (任意)
- SpecDock authoring script 経由の ZIP materialization failure は、別 Issue で backend download / artifact persistence の検証対象にする。

## 省略/例外メモ (必須)
- 該当なし
