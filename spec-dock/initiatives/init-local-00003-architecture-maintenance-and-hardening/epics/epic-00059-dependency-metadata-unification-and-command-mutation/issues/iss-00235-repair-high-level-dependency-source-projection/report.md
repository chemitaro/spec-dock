---
種別: 実装報告書（Issue）
ID: "iss-00235"
タイトル: "Repair high level dependency source projection"
関連GitHub: ["#235"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00235 Repair high level dependency source projection — 実装報告（観測証跡台帳 / Observed Evidence Ledger）

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
| D-001 | resolved | interpretation | orchestrator + deep-consultant | GitHub issue #235 は `iss-00207` と重複するか、別 edge case か。 | 重複として閉じる; `iss-00207` に吸収する; high-level source direct dependency の別 issue として扱う。 | #235 は high-level source 自体の direct dependency が issue-keyed projection で落ちる問題であり、issue source -> high-level target を扱う `iss-00207` とは別 scope。 | 手動再現で `.meta.json.depends_on` は保存されたが、`deps check --id init-00001` / `index-all` / `deps-issues` から消えた。既存 tests は source issue axis が中心。 | applied | `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md` | future requirement/design/plan に source-axis test matrix を反映する。 |
| D-002 | resolved | test-strategy | spec-reviewer | Initial plan S04/S05 bundled multiple observable surfaces in one step. | Keep bundled steps; split by observable surface and commit/review scope. | S04/S05 を `deps check` CLI、`sync` artifact、issue-source regression、non-goal boundary の separate step に分割する。 | `spec-dock-issue-execution` と `phase_plan_issue.md` は 1 implementation step = 1 observable behavior = 1 review scope = 1 commit を要求する。 | applied | `plan.md` S04-S07; plan reviewer finding 2026-06-27 | none |
| D-003 | resolved | implementation | orchestrator + deep-consultant | 前回実装は `.agent/index-all.json` に `deps.raw_direct_edges` を追加したが、GitHub #235 の期待は source node payload の `depends_on` が消えないことだった。 | `deps.raw_direct_edges` を維持する; `nodes[source].depends_on` に raw dependency を出す; 両方を出す。 | `.agent/index-all.json` は `nodes[source].depends_on` を raw direct dependency audit とし、`deps.raw_direct_edges` は追加しない。`deps check` は既存 readiness surface に合流し、`direct_node_dependencies` は補助 field に留める。 | deep-consultant が node-level `depends_on` を推奨し、二重管理による drift と top-level `deps` contract 拡大をリスクとして指摘した。Issue #235 も `init-01926.depends_on` が generated index view にないことを実害として挙げている。 | promoted_to_design | `design.md` 採用方針 / `.agent/index-all.json`; current implementation diff; deep-consultant result 2026-06-27 | none |
| D-004 | resolved | compatibility | code-reviewer | raw node-level `depends_on` を `nodes_all` で持つと `.agent/index.json` / tree projections に漏れ、todo projection で omitted target への dangling ref を作る。 | all projections に出す; full-history `index-all` に限定する; tree だけにも出す。 | raw audit `depends_on` は `.agent/index-all.json` の node payload に限定し、default `.agent/index.json` と tree artifacts には出さない。 | code-reviewer P1 finding。default index consumers は current/future projection を読むため、full-history audit field を混ぜると projection 境界を壊す。 | applied | `src/.../presentation/json_state.py`; `tests/cli_runtime/test_deps.py::test_sync_index_all_preserves_high_level_node_depends_on_without_github` | none |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）

Delegated draft、worker note、research、reviewer finding、discussion、command output を canonical artifact や実装判断へ取り込む場合、この台帳に採用判断を記録する。raw transcript ではなく、orchestrator が検証した採否・理由・証跡・次アクションだけを記録する。

- `adoption_status`: `adopted` / `partially_adopted` / `rejected` / `deferred` / `stale` / `blocked`
- `blocked` または `stale` の unresolved entry は promotion / implementation start / issue ready / issue finish / phase completion を止める。
- `deferred` は blocking でない根拠と revisit 条件を持つ場合だけ完了時に残せる。
- Evidence Adoption Ledger なしで delegated evidence の採用を主張してはならない。
- Evidence Adoption Ledger fields: ID, adoption_status, source, source_role, claim, target_artifact, target_section, rationale, evidence_strength, evidence_path, adopter, reviewer, blocking, next_action.

| 識別子（ID） | 採用状態（adoption_status） | 出所（source） | 対象（target） | 判断理由（rationale） | 証跡（evidence） | 次アクション（next_action） |
|---|---|---|---|---|---|---|
| EAL-001 | `adopted` | research + manual command | issue analysis | GitHub #235 の保存済み raw dependency が readiness/index projection から失われることを reduced reproduction で確認したため。 | `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md`; `/private/tmp/iss-00235-repro`; `deps check --id init-00001 --no-github --json` -> `ready: true`, empty dependency fields | future requirement/design/plan に受け入れ条件と test matrix を反映する。 |
| EAL-002 | `adopted` | sub-agent | issue analysis | runtime/domain、artifact/contract、issue-scope comparison の3観点が、raw storage ではなく issue-keyed projection loss を根本原因とする点で一致したため。 | `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md` deep-consultant synthesis | design で raw node dependency result と issue readiness result を分離する。 |
| EAL-003 | `partially_adopted` | `system-architect` discussion draft | `design.md` | Draft の raw audit / issue readiness separation は採用したが、`deps.raw_direct_edges` 方針は D-003 で superseded し、node-level `depends_on` contract に置き換えた。 | `discussions/20260626t054055z-disc-design-high-level-source-direct-deps.md`; diff guard pass: delegated write は discussion draft のみ; D-003 | integrated into `design.md`; superseded portion rejected; fresh spec-reviewer re-run required after this revision |
| EAL-004 | `adopted` | `implementation-planner` discussion draft | `plan.md` | Draft の closure index と S01-S05/S90/S99 は有用だったが、reviewer 指摘により S04/S05 を S04-S07 へ分割し non-goal closure と step-local delegation contracts を追加した。 | `discussions/20260626t055323z-disc-plan-high-level-source-direct-deps.md`; diff guard pass: delegated write は discussion draft のみ | integrated into `plan.md`; fresh spec-reviewer pass recorded in Spec Authoring Gate |

## 目的整合台帳（Objective Alignment Ledger / 必須）

主要目的と副次要件の主従が逆転していないことを記録する。特に clarification / authoring / handoff の変更では、primary objective evidence、secondary requirement evidence、inversion risk、reviewer verdict を残す。

| 対象 | 主要目的の証跡（primary objective evidence） | 副次要件の証跡（secondary requirement evidence） | 逆転リスク（inversion risk） | レビュアー判定（reviewer verdict） |
|---|---|---|---|---|
| OAL-001 | GitHub #235 の再現確認と根本原因を research に記録した。 | issue scaffold 作成、issue start、deep-consultant 3系統の統合。 | low | provisional |
| OAL-002 | Approved requirement/design/plan は #235 の high-level source direct dependency false-ready と raw audit 欠落を primary objective として扱う。 | workflow 上の delegated draft / reviewer gates / per-step commit gate を plan に反映した。 | low | requirement/design/plan passed |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）

Requirement / design / plan の phase promotion ごとに、調査、未確定事項、回答、採用判断、reviewer verdict、blocking / non-blocking、次アクションを記録する。

| フェーズ（phase） | 調査証跡（investigated facts） | 未確定事項 / 回答（open questions / answers） | 採用判断（adoption decision） | レビュアー判定（reviewer verdict） | ブロック有無（blocking） | 昇格 / 次アクション（promotion / next_action） |
|---|---|---|---|---|---|---|
| research | `discussions/20260623t162536z-research-high-level-source-dependency-projection-root-cause.md`; manual reproduction; code inspection; deep-consultant synthesis | `deps-raw.puml` の complete audit contract は design decision が必要。 | adopted | provisional | no | requirement/design/plan authoring |
| requirement | `requirement.md`; research discussion; GitHub #235 reproduction | AC-002 が `ready=false` を要求すること、AC-003 が `.agent/index-all.json` を required audit surface とすることを fixed。 | adopted | first review failed; second fresh `spec-reviewer` pass, confidence 0.91 | no | promoted to design |
| design | `design.md`; `discussions/20260626t054055z-disc-design-high-level-source-direct-deps.md`; runtime source inspection | `direct_node_dependencies` value schema は existing domain vocabulary に合わせる。 | adopted | first review pass with P2; schema vocabulary updated; second fresh `spec-reviewer` pass, confidence 0.90 | no | promoted to plan |
| plan | `plan.md`; `discussions/20260626t055323z-disc-plan-high-level-source-direct-deps.md`; phase_plan_issue / authoring docs | Delegated draft adoption evidence, single-surface step split, proposal-only draft metadata, and step-local delegation contracts were required. | adopted with revision | first two fresh `spec-reviewer` reviews failed; third fresh `spec-reviewer` pass, confidence 0.91 | no | execution handoff ready |
| execution-handoff | `requirement.md`; `design.md`; `plan.md`; `report.md`; active issue context | No unresolved requirement/design/plan gaps after reviewer pass. | approved | planning artifacts fresh-pass complete | no | start S01 under `spec-dock-issue-execution` |

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
| system-architect | iss-00235 | `discussions/20260626t054055z-disc-design-high-level-source-direct-deps.md` | `requirement.md`; root-cause research; runtime source/tests | `design.md`, `plan.md`, `report.md` | partially adopted | `design.md` | pass | raw audit / issue readiness separation と non-goal artifact boundary を canonical design に統合 | `deps.raw_direct_edges` 方針は D-003 で superseded し node-level `depends_on` へ置換。implementation step ordering details は plan phase へ送った | none | design spec-reviewer re-run required after D-003 revision | promoted to design after re-review |
| implementation-planner | iss-00235 | `discussions/20260626t055323z-disc-plan-high-level-source-direct-deps.md` | `requirement.md`; `design.md`; design discussion; phase_plan_issue; authoring docs | `plan.md`, `report.md` | adopted with revision | `plan.md` | pass | closure index と step sequence を canonical plan に統合し、reviewer finding に基づき S04/S05 を S04-S07 へ分割し step-local delegation contracts を追加 | original bundled S04/S05 step shape | none | first/second plan spec-reviewer failed; third pass | promoted to plan / execution handoff ready |

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
- 前回の `deps.raw_direct_edges` 実装方針を取り消し、`.agent/index-all.json` では node-level `depends_on` を raw direct dependency audit surface として出す方針へ修正した。
- `deps check --json` は high-level source node 自体の direct dependency を既存 readiness surface (`dependency_contexts`, `node_blockers`, `satisfied_dependencies`, `blockers`) に合流し、補助 field として `direct_node_dependencies` を返す。
- Provider runtime、dogfooding mirror、docs、focused regression tests を更新し、`make lint` と broader regression が成功した。

## 実装記録（セッションログ） (必須)

### セッションログ（2026-06-27 再実装）

#### 対象
- Step: S01-S07, S90
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003, EC-004
- 計画上の出典（Planned source）:
  - `plan.md` S01-S07 / S90
  - closure ids: `cl-ac001-direct-check`, `cl-ac002-non-ready`, `cl-ac003-index-all-raw`, `cl-ac004-issue-regression`, `cl-ec001-empty-source`, `cl-ec002-non-empty-source`, `cl-ec003-satisfied-raw-audit`, `cl-boundary-artifacts`, `cl-boundary-storage-source`, `cl-boundary-external`

#### 実施内容
- 問題のあった前回実装を `revert(deps): 前回の高水準依存投影実装を取り消す` として独立 commit に分離した。
- deep-consultant の再分析に基づき、`.agent/index-all.json` の raw audit surface を `deps.raw_direct_edges` ではなく `nodes[source].depends_on` に修正した。
- `deps check` は high-level source direct dependency を既存 readiness contexts に合流し、`direct_node_dependencies` は補助 field とした。
- Provider runtime と dogfooding runtime mirror を同期し、docs / issue artifacts を新方針へ更新した。

#### 実行コマンド / 結果
```bash
uv run pytest tests/unit/application/test_check_deps.py::TestCheckDepsApplication::test_deps_check_blocks_empty_initiative_direct_node_dependency tests/unit/application/test_check_deps.py::TestCheckDepsApplication::test_deps_check_keeps_direct_node_status_separate_from_issue_readiness -q
# 2 passed in 0.05s

uv run pytest tests/cli_runtime/test_deps.py::TestCliDeps::test_deps_check_returns_ready_and_blockers_and_closure_json tests/cli_runtime/test_deps.py::TestCliDeps::test_deps_check_json_blocks_empty_high_level_source_direct_dependency_without_github tests/cli_runtime/test_deps.py::TestCliDeps::test_sync_index_all_preserves_high_level_node_depends_on_without_github -q
# 3 passed in 5.28s

uv run pytest tests/unit/presentation/test_runtime_sync_s07.py::TestRuntimeSyncS07::test_sync_use_case_writes_artifacts_and_paths -q
# 1 passed in 0.08s

uv run pytest tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json -q
# 2 passed in 1.40s

make lint
# ruff check: pass; ruff format check: pass; mypy: pass

uv run pytest tests/unit/application/test_check_deps.py tests/unit/domain/test_deps.py tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_deps.py tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_runtime_mirror_match_provider_assets tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_initiatives_do_not_ship_legacy_deps_json -q
# 201 passed, 10 skipped in 199.13s

uv run pytest
# 1413 passed, 76 skipped in 800.84s
```

#### テスト駆動開発証跡（TDD / Red / Green / Refactor Evidence）
| ステップ（step） | フェーズ（phase） | 計画した証跡要件 | 観測した証跡 | 証跡手段（command / inspection / manual record） | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|---|
| S01/S02 | Green | high-level source direct dependency が readiness contexts と補助 JSON field に出る | application tests 2件 pass; CLI JSON test pass | `uv run pytest ...test_check_deps...`; `uv run pytest ...test_deps...` | pass | issue source は direct mirror で二重計上しないよう境界修正 |
| S03/S05 | Green | `.agent/index-all.json` の `nodes[source].depends_on` に raw direct dependency が残る | CLI sync test pass | `uv run pytest tests/cli_runtime/test_deps.py::TestCliDeps::test_sync_index_all_preserves_high_level_node_depends_on_without_github -q` | pass | `deps.raw_direct_edges` は出さない |
| S06/S07 | Green | existing issue-source behavior と non-goal artifact boundary を維持 | existing CLI JSON test / broader regression pass | `uv run pytest ... test_deps.py ...`; broader regression | pass | `effective_depends_on` の意味は維持 |
| S90 | Green | docs / mirror / snapshot を新 contract に合わせる | lint / mirror snapshot tests pass | `make lint`; `test_init_update.py` focused tests | pass | docs に `nodes[*].depends_on` contract を追記 |

#### 発見されたテスト / リスク（Discovered Tests）
| ステップ（step） | 発見されたテスト / リスク（test / risk） | 起票元（source） | 実施した対応 | クロージャID / 新規ID（closure id / new id） | 計画修正要否（plan amendment required） | 証跡（evidence） |
|---|---|---|---|---|---|---|
| S02 | `direct_node_dependencies` だけで説明すると既存 consumer が `dependency_contexts` から理由を取れない | deep-consultant | existing readiness contexts に合流し、補助 field に留めた | `cl-ac001-direct-check`, `cl-ac002-non-ready` | yes | D-003; updated design/plan; tests |
| S03 | `deps.raw_direct_edges` は `index-all` の既存 node contract と二重管理になる | deep-consultant | `nodes[source].depends_on` contract に置換 | `cl-ac003-index-all-raw`, `cl-ec003-satisfied-raw-audit` | yes | D-003; sync CLI test |

#### ステップ契約の完了証跡（Step Contract Closure）
| ステップ（step） | クロージャID（closure ids） | 計画上の close 条件（close condition from plan） | 観測した証跡 | 結果（result） | メモ（notes） |
|---|---|---|---|---|---|
| S01/S02/S04 | `cl-ac001-direct-check`, `cl-ac002-non-ready`, `cl-ec001-empty-source` | high-level source direct dependency を `deps check --json` で観測し、unresolved なら non-ready | application tests / CLI JSON test pass | pass | `dependency_contexts`, `node_blockers`, `direct_node_dependencies` を確認 |
| S03/S05 | `cl-ac003-index-all-raw`, `cl-ec003-satisfied-raw-audit` | full-history artifact に raw dependency audit が残る | CLI sync test pass | pass | `nodes[source].depends_on` を確認 |
| S06/S07 | `cl-ac004-issue-regression`, `cl-ec002-non-empty-source`, boundary closures | issue-source behavior と non-goal artifact boundary を維持 | broader regression / existing JSON test / diff inspection | pass | `deps.raw_direct_edges` は追加しない |
| S90 | docs impact | docs / mirror / snapshot を更新し検証する | docs diff; mirror tests; `make lint` | pass | provider docs と dogfooding docs を同期 |

#### テスト契約の完了証跡（Test Contract Closure）
| クロージャID / テストID（closure id / test id） | ステップ（step） | 必須 | 証跡レベル（evidence level） | 実装前証跡 | 検証コマンドまたは代替 path | 観測結果 | メモ（notes） |
|---|---|---|---|---|---|---|---|
| `cl-ac001-direct-check` | S01/S02/S04 | yes | red-required | #235 / research reproduction | focused application + CLI JSON tests | pass | source/target ids/kinds を確認 |
| `cl-ac002-non-ready` | S01/S02/S04 | yes | red-required | #235 false-ready | focused application + CLI JSON tests | pass | `ready=false`, blocker populated |
| `cl-ac003-index-all-raw` | S03/S05 | yes | red-required | #235 index-all omission | CLI sync test | pass | `nodes[source].depends_on` populated |
| `cl-ac004-issue-regression` | S06 | yes | covered-existing | existing issue-source behavior | broader regression | pass | issue-source test remains unchanged except additive empty `direct_node_dependencies` |
| `cl-boundary-artifacts` | S07 | yes | inspect-only + covered-existing | design constraints | CLI sync test and diff inspection | pass | no `deps.raw_direct_edges` implementation |

#### クロージャ網羅（Closure Coverage）
| クロージャID（closure id） | ステップ（step） | 検証証跡 | 観測結果 | メモ（notes） |
|---|---|---|---|---|
| `cl-ac001-direct-check` | S01/S02/S04 | `test_deps_check_blocks_empty_initiative_direct_node_dependency`, CLI JSON test | pass | direct dependency surfaced |
| `cl-ac002-non-ready` | S01/S02/S04 | same tests | pass | false-ready prevented |
| `cl-ac003-index-all-raw` | S03/S05 | `test_sync_index_all_preserves_high_level_node_depends_on_without_github`; `test_sync_index_all_preserves_satisfied_high_level_node_depends_on_without_github` | pass | node-level raw audit limited to index-all |
| `cl-ac004-issue-regression` | S06 | `test_deps_check_returns_ready_and_blockers_and_closure_json`; broader regression | pass | issue-source path not double counted |
| `cl-boundary-storage-source` | S07/S99 | diff inspection; `.meta.json.depends_on` storage unchanged | pass | no synthetic issue |
| `cl-boundary-external` | S07/S99 | tests use temp repos and `--no-github` for new regressions | pass | no external product repo mutation |

#### クロージャ差分（Closure Delta）
| 変更種別（change） | クロージャID（closure id） | テストID alias（test id alias） | 解決先クロージャID（resolved closure id） | 理由 | 計画修正要否（plan amendment required） | 再レビュー要否（re-review required） |
|---|---|---|---|---|---|---|
| changed | `cl-ac003-index-all-raw` | raw edge list -> node-level depends_on | `cl-ac003-index-all-raw` | 前回 `deps.raw_direct_edges` 方針が不適切だったため | yes | yes |
| changed | `cl-ac001-direct-check` | direct-only field -> existing readiness contexts + mirror | `cl-ac001-direct-check` | existing consumers が `dependency_contexts` / `node_blockers` を読むため | yes | yes |

#### ワークフロー委任同意の証跡（Workflow Delegation Consent）
| 同意元（consent source） | リポジトリ / worktree（repo/worktree） | 対象課題（active issue） | セッション（session） | 指名ロール（named roles） | 境界（boundary） | 期限 / 無効化条件（expires / invalidation condition） | 拒否 / 利用不可理由（denied / unavailable reason） | 次アクション（next action） |
|---|---|---|---|---|---|---|---|---|
| user instruction + skill invocation | `/Users/iwasawayuuta/.codex/worktrees/c2a6/spec-dock` | iss-00235 | current session | deep-consultant, system-architect, implementation-planner, spec-reviewer, code-reviewer, qa-reviewer | same repo, active issue, session, named role; no destructive action / publishing / credentialed access / scope expansion / private external system use | issue complete / session end / scope change / host policy conflict / user revocation | `system-architect` additional draft unavailable due thread limit; existing design revised manually from source-grounded analysis | proceed with manual canonical update and fresh reviewer gates |

#### 実装委任ゲート（Implementation Delegation Gate）
| ステップ（step） | 判断（decision） | 必須理由（required reason） | 委任ロール（delegated role） | 委任範囲（delegated scope） | 正本（source of truth） | 許可変更（allowed changes） | 禁止変更（forbidden changes） | 必須検証（required verification） | 停止条件（stop conditions） | 必須出力（output required） | 観測結果（observed result） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S01-S07/S90 | approved-local-execution | thread limit prevented additional write-capable design delegation; parent retained single-writer canonical/report responsibility and made bounded implementation in active issue scope | N/A | provider runtime, mirror, tests, docs, issue artifacts | requirement/design/plan; D-003; #235 | listed changed files only | storage migration, synthetic issue, `deps.raw_direct_edges`, external repo mutation | focused tests, broader regression, `make lint` | design conflict, failing tests, reviewer fail | report evidence, changed files, verification | pass |

#### 親実装例外（Parent Implementation Exception）
| ステップ（step） | 委任不可 / 不可能理由（delegation unavailable/impossible reason） | ユーザー承認 / risk acceptance（user approval / risk acceptance） | 許可ファイル（allowed files） | 許可操作（allowed operation） | ロールバック計画（rollback plan） | 変更後検証（post-change verification） | レビューゲート（reviewer gate） | 利用不可 / 拒否 / host conflict / waiver 対応（unavailable / denied / host conflict / waiver handling） |
|---|---|---|---|---|---|---|---|---|
| S01-S07/S90 | sub-agent thread limit blocked additional `system-architect`; current task required continued progress and canonical docs are parent-owned | user asked to continue to PR-ready state; no reviewer waiver accepted | runtime provider/mirror files, focused tests, docs, issue artifacts | bounded implementation and canonical artifact update | backup branch `backup/iss-00235-previous-impl-8377788c`; revert commit `99cc094d`; current diff review | `make lint`; focused and broader pytest | fresh code/spec/QA review still required | treated as approved-local-execution evidence only, not reviewer pass |

#### レビューゲート状態（Reviewer Gate Status）
| ステップ（step） | ゲート名（gate name） | レビュアーロール（reviewer role） | 鮮度（freshness） | 状態（state） | リスク受容（risk acceptance） | 昇格 / 完了判断（promotion / completion decision） | メモ（notes） |
|---|---|---|---|---|---|---|---|
| S01-S07/S90 | step / docs reviewer | code-reviewer / spec-reviewer | fresh | passed | no | proceed | final spec-reviewer P2 docs ambiguity was fixed in `reference_sync.md` provider and dogfooding mirror |

#### ステップ commit ゲート（Step Commit Gate）
| ステップ（step） | クロージャ状態（closure state） | コミット範囲（commit scope） | コミットハッシュ / 最終台帳（commit hash / final ledger） | コミット後 clean 確認（post-commit clean check） | 差分なし根拠（no-op rationale） | 差分なし確認済み契約 / ファイル（no-op checked contracts / files） | 差分なし diff-clean コマンド（no-op diff-clean command） | 差分なし read-only 確認（no-op read-only confirmation） |
|---|---|---|---|---|---|---|---|---|
| S01-S07/S90 | pending commit | current implementation diff | pending | pending | N/A | N/A | N/A | N/A |

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/{models.py,deps.py}` - high-level source direct dependency status model / evaluation
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py` - raw node dependency map handoff to inspection
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` - `deps check` JSON helper field and `index-all` node-level `depends_on`
- `spec-dock/scripts/spec_dock_runtime/...` - dogfooding runtime mirror
- `tests/unit/application/test_check_deps.py`, `tests/cli_runtime/test_deps.py`, `tests/unit/infra/test_init_update.py` - regression and snapshot coverage
- `src/spec_dock/assets/spec_dock/docs/reference_{deps,sync}.md`, `spec-dock/docs/reference_{deps,sync}.md` - user-facing contract docs
- `requirement.md`, `design.md`, `plan.md`, `report.md` - D-003 implementation strategy correction

#### コミット
- pending

#### メモ
- `deps.raw_direct_edges` は intentionally not implemented。
- `direct_node_dependencies` は authoritative-only field ではなく、existing readiness surface の補助 mirror。

## 最終品質ゲート（Final Quality Gate / 必須）

### ドキュメント影響の解消ステップ S90（Docs Impact Resolution）
| 対象 | 更新要否 | 担当（owner） | 証跡（evidence） | 仕様レビュアー結果（spec-reviewer result） |
|---|---|---|---|---|
| docs / templates / README / workflow / skill / migration notes | yes | approved-local-execution | `src/spec_dock/assets/spec_dock/docs/reference_deps.md`, `src/spec_dock/assets/spec_dock/docs/reference_sync.md`, dogfooding mirrors updated; final spec-reviewer P2 ambiguity fixed | pass |

### 最終 QA ゲート（Final QA Gate）
| レビュアー（reviewer） | 範囲 | 統合テスト判断（integration test decision） | 証跡（evidence） | 結果（result） |
|---|---|---|---|---|
| qa-reviewer | whole issue obligation coverage | added epic-source direct dependency coverage and satisfied raw audit coverage after P2 findings | qa-reviewer pass; `test_deps_check_json_blocks_epic_source_direct_dependency_without_github`; `test_sync_index_all_preserves_satisfied_high_level_node_depends_on_without_github`; broader regression `201 passed, 10 skipped`; full `uv run pytest` `1413 passed, 76 skipped` | pass |

### 最終コードレビューゲート（Final Code Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| code-reviewer | issue-wide integrated diff | initial P1: raw node-level `depends_on` leaked into `.agent/index.json` / tree projections; fixed by limiting raw audit to `.agent/index-all.json` and adding tests for `index.json` omission | 1 | pass |

### 最終 spec review ゲート（Final Spec Review Gate）
| レビュアー（reviewer） | 範囲 | 指摘 / 修正（findings / fixes） | 再 review 回数（re-review count） | 結果（result） |
|---|---|---|---|---|
| spec-reviewer | requirement / design / plan / report / implementation / tests / docs alignment | initial P2: final gate placeholders remained; replaced placeholders with observed QA/code/docs/verification evidence; final P2: scoped `reference_sync.md` raw `depends_on` contract to `.agent/index-all.json` only | 2 | pass |

### 最終 commit（Final Commit）
| 最終 report 台帳（final report ledger） | 最終 commit 範囲（final commit scope） | コミット後の外部証跡送付先（post-commit external evidence destination） | 結果（result） |
|---|---|---|---|
| D-003/D-004, closure tables, QA/code/spec gates, final verification evidence | provider runtime, dogfooding mirror, tests, docs, issue artifacts | final response and PR #242 update | pending final commit |

## 遭遇した問題と解決 (任意)
- 問題: 前回実装は `.agent/index-all.json` に `deps.raw_direct_edges` を追加する方式だった。
  - 解決: D-003 で superseded とし、`.agent/index-all.json` の `nodes[source].depends_on` を raw audit surface に変更した。
- 問題: code-reviewer が `.agent/index.json` への raw `depends_on` leak を P1 指摘した。
  - 解決: raw node-level `depends_on` を full-history `index-all` payload のみで付与し、default `index.json` には出さない regression を追加した。
- 問題: final spec-reviewer が `reference_sync.md` の raw `depends_on` 説明を `index-*.json` / `tree-*.json` 全体へ広く読める P2 として指摘した。
  - 解決: provider docs と dogfooding mirror の説明を `.agent/index-all.json` `nodes[*].depends_on` 限定へ修正した。

## 学んだこと (任意)
- `index-all` と `index.json` は projection boundary が異なるため、full-history audit field は `nodes_all` 共有元ではなく final `payload_all` で付与する必要がある。

## 今後の推奨事項 (任意)
- 依存 projection の新規 field を追加する場合は、full-history audit、current/future projection、readiness authority、visual/debug artifact の4面を分けて reviewer checklist に入れる。

## 省略/例外メモ (必須)
- 該当なし
