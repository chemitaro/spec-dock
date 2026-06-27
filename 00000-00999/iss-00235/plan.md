---
種別: 実装計画書（Issue）
ID: "iss-00235"
タイトル: "Repair high level dependency source projection"
関連GitHub: ["#235"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00235 Repair high level dependency source projection — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: `deps check` exposes high-level source direct dependencies.
  - AC-002: unresolved high-level source direct dependencies make `deps check` non-ready.
  - AC-003: `.agent/index-all.json` exposes raw high-level source edges.
  - AC-004: existing issue readiness behavior remains intact.
- EC:
  - EC-001: empty high-level source.
  - EC-002: non-empty high-level source.
  - EC-003: satisfied / done / closed target remains in raw audit.
  - EC-004: existing issue-source high-level target.
- 制約:
  - No synthetic issues.
  - No `.meta.json.depends_on` storage format change.
  - No `deps-issues.json` complete raw graph dump.
  - No `effective_depends_on` semantic expansion.
  - No `deps-raw.puml` complete audit contract expansion.
  - No live GitHub mutation or external product repo mutation.
  - Provider source of truth under `src/spec_dock/assets/spec_dock/...` is changed first; dogfooding `spec-dock/` generated runtime is not treated as implementation source.
  - New regression tests are hermetic and do not require live GitHub.

## 依存関係から導く実装順序
- 参照元:
  - `design.md` の module dependency diagram と file change plan。
- 順序:
  - S01: domain/application result contract を先に固定する。
  - S02: S01 の result を `deps check --json` に出す。
  - S03: sync full-history artifact に raw audit を出す。
  - S04: public CLI `deps check --json` reduced reproduction を固定する。
  - S05: public CLI `sync --no-github` artifact reduced reproduction を固定する。
  - S06: 既存 issue-source high-level target readiness regression を固める。
  - S07: non-goal artifact/source boundary regression を固める。
  - S90: docs impact を解消する。
  - S99: final QA/code/spec gates を閉じる。
- 実行 invariant:
  - 1 implementation step = 1 observable behavior = 1 review scope = 1 commit。
  - 各 step は delegated implementation、targeted verification、fresh reviewer pass、report evidence、step commit、post-commit clean check を閉じてから次へ進む。

## ステップ一覧
- S01 Direct Node Dependency Status Contract:
  - `check_deps` が checked target 自体の direct node dependency を application result として返し、未解決なら non-ready にできる。
- S02 `deps check --json` Additive JSON Contract:
  - `direct_node_dependencies` を JSON 出力し、`ready=false` / `blockers` からも non-ready 理由を観測できる。
- S03 `.agent/index-all.json` Raw Direct Edge Audit:
  - `.agent/index-all.json` の `deps.raw_direct_edges` に complete raw direct edge audit を追加する。
- S04 CLI `deps check --json` Reduced Reproduction:
  - `--no-github` の reduced repo で #235 相当の `deps check` false-ready 修正を public CLI surface から固定する。
- S05 CLI `sync --no-github` Raw Audit Reproduction:
  - `--no-github` の reduced repo で `.agent/index-all.json` raw audit を public CLI artifact surface から固定する。
- S06 Issue-Source High-Level Target Regression:
  - 既存 issue-source high-level target semantics を regression で固定する。
- S07 Non-Goal Boundary Hardening:
  - `deps-issues.json` / `deps-raw.puml` / storage / source-of-truth / external mutation の non-goal boundary を検証する。
- S90 Docs Impact Resolution:
  - JSON contract / sync artifact contract の docs 影響を確認し、必要なら docs を更新する。
- S99 Final Quality Gate:
  - QA / code / spec の issue-wide reviewer gates と final verification を閉じる。

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02, S04
- AC-002 -> S01, S02, S04
- AC-003 -> S03, S05
- AC-004 -> S06
- EC-001 -> S01, S02, S04
- EC-002 -> S01, S06
- EC-003 -> S03, S05
- EC-004 -> S06
- design boundary constraints -> S07, S99

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ | スライス | 種別 | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル | クロージャ証跡 |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-ac001-direct-check | S01/S02/S04 | deps-check-direct-source | acceptance | AC-001 | `direct_node_dependencies` が source/target ids/kinds を返す | Empty high-level source が `.meta.json.depends_on=["epic-..."]` を持つ | raw edge が issue projection で消える | yes | red-required | report Step/Test Closure |
| cl-ac002-non-ready | S01/S02/S04 | deps-check-readiness | acceptance | AC-002 | unresolved direct node dependency で `ready=false`、`blockers` に target node id | target epic が unresolved open/unknown | false-ready | yes | red-required | report Step/Test Closure |
| cl-ac003-index-all-raw | S03/S05 | index-all-raw-audit | acceptance | AC-003 | `.agent/index-all.json` が `deps.raw_direct_edges` を source/target kind 付きで返す | sync state に raw high-level edge がある | full-history audit 欠落 | yes | red-required | report Step/Test Closure |
| cl-ac004-issue-regression | S06 | issue-source-regression | regression | AC-004/EC-004 | issue-source high-level target blockers / satisfied deps / `effective_depends_on` が維持される | 既存 issue-source high-level target scenarios | iss-00207 regression | yes | covered-existing | report Closure Coverage |
| cl-ec001-empty-source | S04 | empty-source-runtime | acceptance | EC-001 | empty source でも dependency-free ready output にならない | source initiative/epic に descendant issue がない | empty source compile loss | yes | red-required | report Step/Test Closure |
| cl-ec002-non-empty-source | S01/S06 | non-empty-source-separation | characterization | EC-002 | direct node status と descendant issue readiness projection が混同されない | source に descendant issues と parent direct dependency がある | double-count / semantic mixing | yes | red-required | report Step/Test Closure |
| cl-ec003-satisfied-raw-audit | S03/S05 | satisfied-raw-audit | acceptance | EC-003 | satisfied/done/closed dependency も `raw_direct_edges` に残る | target が closed/done/satisfied | raw audit が readiness filter で消える | yes | red-required | report Step/Test Closure |
| cl-boundary-artifacts | S07/S99 | non-goal-artifacts | regression | design constraints | `deps-issues.json` と `deps-raw.puml` を complete raw audit に昇格しない | sync/presentation artifacts | artifact scope creep | yes | inspect-only + covered-existing | report Closure Coverage |
| cl-boundary-storage-source | S07/S99 | non-goal-source-storage | regression | requirement constraints | fake issue、storage format change、dogfooding generated runtime source edit を行わない | issue-wide diff | storage/source-of-truth regression | yes | inspect-only | report Closure Coverage |
| cl-boundary-external | S07/S99 | non-goal-external | regression | requirement constraints | live GitHub mutation / external product repo mutation なし、tests are hermetic | command/test evidence and diff | external-state dependency | yes | inspect-only | report Closure Coverage |

## レビュー / QA ゲート方針
- Step reviewer:
  - runtime/source/test 変更は `code-reviewer`。
  - docs-only 変更は `spec-reviewer`。
  - reviewer fail は bounded delegated follow-up で修正し、fresh pass まで再実行する。
- Final gates:
  - `qa-reviewer`: AC/EC と closure coverage、追加 test 要否。
  - `code-reviewer`: issue-wide integrated diff、layering、compatibility、forbidden changes。
  - `spec-reviewer`: requirement / design / plan / report / implementation / tests / docs alignment。

## 実行ルール（全ステップ共通）
- 実装は `dev-coder` へ委任する。
- Main orchestrator は canonical issue docs / report の更新、reviewer coordination、commit / PR coordination を担当する。
- 計画外の仕様判断、対象外 artifact 変更、storage contract 変更、GitHub live dependency が必要になったら停止し、report ledger と plan/design amendment を検討する。
- 実装結果・コマンド・reviewer verdict・commit evidence は `report.md` に記録する。

## 実装ステップ S01 — Direct Node Dependency Status Contract
- 振る舞いの目標:
  - `check_deps` が high-level target node 自体の direct raw dependency status を application result として持つ。
- design 参照:
  - `direct_node_dependencies` contract / domain model delta。
- 依存:
  - requirement/design/plan reviewer pass。
- unblock:
  - S02, S03, S04。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py`
  - `tests/unit/domain/test_deps.py`
  - `tests/unit/application/test_check_deps.py`
- 禁止変更:
  - `.meta.json.depends_on` storage format 変更。
  - synthetic issue 作成。
  - `effective_depends_on` の high-level source direct dependency 混入。
  - presentation JSON / sync artifact の本格変更。
- 計画済み契約:
  - closure ids: `cl-ac001-direct-check`, `cl-ac002-non-ready`, `cl-ec002-non-empty-source`
  - Red: empty high-level source direct dependency が現状 false-ready になることを public application/domain test で固定する。
  - Green: result に direct node dependency status があり、unresolved は `ready=false` / blockers に反映される。
  - Verification: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py`
- 委任契約:
  - delegated role: `dev-coder`
  - source of truth / input docs: `requirement.md`, `design.md`, `plan.md`, root-cause research discussion
  - allowed changes: 対象ファイルに限定し、domain/application result contract と focused tests だけを変更する。
  - stop conditions: storage migration、synthetic issue、`effective_depends_on` semantic change、allowed paths 外の変更、planned tests が実行不能な場合。
  - output required: changed files、Red/Green evidence、verification result、material decision の Ledger Note または `No material implementation decisions beyond the approved plan.`
  - report evidence destination: `report.md` S01 session log、TDD evidence、Step/Test Closure、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
- 具体テストケース:
  - `tc-s01-001`: empty initiative source `init -> epic` direct dependency blocks `check_deps` result.
  - `tc-s01-002`: non-empty high-level source keeps direct node status separate from issue readiness fields.
- reviewer focus:
  - status rule の domain 集約、additive contract、既存 issue readiness path の非回帰。
- amendment trigger:
  - additive result model で表現できない、または `effective_depends_on` の意味変更が必要になった場合。

## 実装ステップ S02 — `deps check --json` Additive JSON Contract
- 振る舞いの目標:
  - `render_deps_check_json()` が `direct_node_dependencies` を出力する。
- 依存:
  - S01 committed。
- unblock:
  - S04。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `tests/unit/presentation/test_runtime_sync_s07.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`（必要時のみ）
- 禁止変更:
  - 既存 JSON field の削除 / rename。
  - presentation layer で readiness を再計算すること。
  - `dependency_contexts` への source-node-only dependency 混入。
- 計画済み契約:
  - closure ids: `cl-ac001-direct-check`, `cl-ac002-non-ready`
  - Red: renderer が direct node dependency payload を出せないことを固定する。
  - Green: JSON に source/target ids/kinds、expansion、lifecycle、disposition、basis が出る。
  - Verification: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`
- 委任契約:
  - delegated role: `dev-coder`
  - source of truth / input docs: `requirement.md`, `design.md`, `plan.md`, S01 worker evidence
  - allowed changes: 対象ファイルに限定し、`deps check --json` presentation contract と focused tests だけを変更する。
  - stop conditions: result model にない状態を presentation が再計算する必要がある、existing JSON field rename/delete が必要、allowed paths 外の変更が必要。
  - output required: changed files、JSON sample、verification result、material decision の Ledger Note または `No material implementation decisions beyond the approved plan.`
  - report evidence destination: `report.md` S02 session log、TDD evidence、Step/Test Closure、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
- 具体テストケース:
  - `tc-s02-001`: renderer emits `direct_node_dependencies`.
  - `tc-s02-002`: existing top-level keys and node blocker/dependency context keys remain additive-compatible.
- reviewer focus:
  - JSON compatibility、field naming、empty-list stability、presentation recomputation の有無。
- amendment trigger:
  - `blockers` に high-level ids を含めることが documented contract と衝突する場合。

## 実装ステップ S03 — `.agent/index-all.json` Raw Direct Edge Audit
- 振る舞いの目標:
  - Full-history sync artifact が `deps.raw_direct_edges` を complete に返す。
- 依存:
  - S01 committed。
- unblock:
  - S05, S07。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`（既存 `raw_node_depends_on_map` が不足する場合のみ）
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`（typed edge list が必要な場合のみ）
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `tests/unit/presentation/test_runtime_sync_s07.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
- 禁止変更:
  - `deps-issues.json` を complete raw graph dump にすること。
  - `deps-raw.puml` を complete audit artifact にすること。
  - readiness/satisfied state で `raw_direct_edges` を filter すること。
  - `.agent/index.json` へ raw audit を追加すること。
- 計画済み契約:
  - closure ids: `cl-ac003-index-all-raw`, `cl-ec003-satisfied-raw-audit`
  - Red: `.agent/index-all.json` に high-level raw direct edge が出ないことを固定する。
  - Green: deterministic `deps.raw_direct_edges` が source/target kind と `relation: raw_direct` を持つ。
  - Verification: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`
- 委任契約:
  - delegated role: `dev-coder`
  - source of truth / input docs: `requirement.md`, `design.md`, `plan.md`, S01 worker evidence
  - allowed changes: 対象ファイルに限定し、`.agent/index-all.json` full-history raw audit と focused tests だけを変更する。
  - stop conditions: `deps-issues.json` / `deps-raw.puml` contract expansion が必要、`.agent/index.json` 変更が必要、raw edge kind が graph から解決不能、allowed paths 外の変更が必要。
  - output required: changed files、`index-all` payload sample、verification result、material decision の Ledger Note または `No material implementation decisions beyond the approved plan.`
  - report evidence destination: `report.md` S03 session log、TDD evidence、Step/Test Closure、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
- 具体テストケース:
  - `tc-s03-001`: `index-all` includes `init -> epic` raw direct edge.
  - `tc-s03-002`: satisfied/done/closed raw dependency remains in audit.
- reviewer focus:
  - complete raw audit semantics、deterministic sorting、node kind correctness、non-goal artifacts 非変更。
- amendment trigger:
  - `.agent/index-all.json` additive field が compatibility 上許容できない場合。

## 実装ステップ S04 — CLI `deps check --json` Reduced Reproduction
- 振る舞いの目標:
  - `--no-github` で #235 の false-ready を public CLI `deps check --json` surface から再現・修正確認できる。
- 依存:
  - S02 committed。
- unblock:
  - S06。
- 対象ファイル:
  - `tests/cli_runtime/test_runtime_deps_s04.py`
  - `tests/cli_runtime/test_deps.py`（必要時のみ）
- 禁止変更:
  - live GitHub dependency。
  - external product repo mutation。
  - private helper behavior を primary evidence にすること。
- 計画済み契約:
  - closure ids: `cl-ac001-direct-check`, `cl-ac002-non-ready`, `cl-ec001-empty-source`
  - Red: current behavior が dependency-free `ready=true` になることを CLI runtime test で固定する。
  - Green: `deps check --id init --no-github --json` は `ready=false`、`blockers` と `direct_node_dependencies` を返す。
  - Verification: `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` plus `uv run pytest tests/cli_runtime/test_deps.py` if touched。
- 委任契約:
  - delegated role: `dev-coder`
  - source of truth / input docs: `requirement.md`, `design.md`, `plan.md`, S01/S02 worker evidence
  - allowed changes: 対象 test files に限定し、public CLI `deps check --json` reduced reproduction を追加する。実装修正が必要なら S01/S02 scope に戻す。
  - stop conditions: live GitHub が必要、external repo mutation が必要、fixture rewrite が broad になる、implementation file 変更が必要。
  - output required: changed files、failing-before or characterization evidence、verification result、material decision の Ledger Note または `No material implementation decisions beyond the approved plan.`
  - report evidence destination: `report.md` S04 session log、TDD evidence、Step/Test Closure、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
- 具体テストケース:
  - `tc-s04-001`: CLI `deps check --json` non-ready for empty high-level source raw dependency.
- reviewer focus:
  - hermetic temp repo、public command observation、fixture scope。
- amendment trigger:
  - broad fixture rewrite や unrelated scaffold support が必要になった場合。

## 実装ステップ S05 — CLI `sync --no-github` Raw Audit Reproduction
- 振る舞いの目標:
  - `--no-github` で #235 の full-history raw audit 欠落を public CLI `sync` artifact surface から再現・修正確認できる。
- 依存:
  - S03 committed。
- unblock:
  - S07。
- 対象ファイル:
  - `tests/cli_runtime/test_runtime_deps_s04.py`
  - `tests/cli_runtime/test_sync.py`（必要時のみ）
- 禁止変更:
  - live GitHub dependency。
  - external product repo mutation。
  - `deps-issues.json` / `deps-raw.puml` contract expansion。
- 計画済み契約:
  - closure ids: `cl-ac003-index-all-raw`, `cl-ec003-satisfied-raw-audit`
  - Red: current `sync --no-github` output lacks `deps.raw_direct_edges` in `.agent/index-all.json`。
  - Green: `sync --no-github` writes `deps.raw_direct_edges` with source/target kinds.
  - Verification: `uv run pytest tests/cli_runtime/test_runtime_deps_s04.py` plus `uv run pytest tests/cli_runtime/test_sync.py` if touched。
- 委任契約:
  - delegated role: `dev-coder`
  - source of truth / input docs: `requirement.md`, `design.md`, `plan.md`, S03 worker evidence
  - allowed changes: 対象 test files に限定し、public CLI `sync --no-github` artifact reproduction を追加する。実装修正が必要なら S03 scope に戻す。
  - stop conditions: live GitHub が必要、external repo mutation が必要、`deps-issues.json` / `deps-raw.puml` expansion が必要、implementation file 変更が必要。
  - output required: changed files、artifact payload sample、verification result、material decision の Ledger Note または `No material implementation decisions beyond the approved plan.`
  - report evidence destination: `report.md` S05 session log、TDD evidence、Step/Test Closure、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
- 具体テストケース:
  - `tc-s05-001`: CLI/runtime `sync --no-github` writes `deps.raw_direct_edges` to `.agent/index-all.json`.
- reviewer focus:
  - public artifact observation、deterministic payload、hermetic temp repo。
- amendment trigger:
  - sync CLI fixture が broad unrelated scaffold rewrite を必要とする場合。

## 実装ステップ S06 — Issue-Source High-Level Target Regression
- 振る舞いの目標:
  - 既存 issue-source high-level target readiness semantics を守る。
- 依存:
  - S01-S04 committed。
- unblock:
  - S99。
- 対象ファイル:
  - `tests/unit/domain/test_deps.py`
  - `tests/unit/application/test_check_deps.py`
  - `tests/cli_runtime/test_runtime_deps_s04.py`
  - 実装 file は S06 で見つけた承認済み scope の defect 修正に限る。
- 禁止変更:
  - broad snapshot churn。
  - `effective_depends_on` semantic expansion。
- 計画済み契約:
  - closure ids: `cl-ac004-issue-regression`, `cl-ec002-non-empty-source`
  - Verification: `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/cli_runtime/test_runtime_deps_s04.py`
- 委任契約:
  - delegated role: `dev-coder`
  - source of truth / input docs: `requirement.md`, `design.md`, `plan.md`, S01-S04 worker evidence
  - allowed changes: 対象 files に限定し、issue-source high-level target と non-empty source separation の regression coverage だけを変更する。
  - stop conditions: existing issue-source semantics と approved design が衝突する、broad snapshot churn が必要、`effective_depends_on` semantic expansion が必要。
  - output required: changed files、regression matrix、verification result、material decision の Ledger Note または `No material implementation decisions beyond the approved plan.`
  - report evidence destination: `report.md` S06 session log、Discovered Tests、Closure Coverage、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
- 具体テストケース:
  - `tc-s06-001`: issue-source high-level target blockers/satisfied dependencies remain covered.
  - `tc-s06-002`: non-empty source direct status remains separate from descendant issue readiness.
- reviewer focus:
  - regression coverage、private-method-only tests 回避、issue readiness path 非回帰。
- amendment trigger:
  - existing issue-source semantics と direct source readiness の間に real conflict が出た場合。

## 実装ステップ S07 — Non-Goal Boundary Hardening
- 振る舞いの目標:
  - non-goal artifacts / source-of-truth / external mutation boundaries を issue-wide diff と focused regressions で守る。
- 依存:
  - S03, S05, S06 committed。
- 対象ファイル:
  - `tests/unit/presentation/test_runtime_sync_s07.py`
  - `tests/unit/presentation/test_deps_raw_puml.py`（必要時のみ）
  - `tests/cli_runtime/test_runtime_deps_s04.py`
  - 実装 file は S07 で見つけた承認済み scope の defect 修正に限る。
- 禁止変更:
  - `deps-raw.puml` / `deps-issues.json` contract expansion。
  - `.meta.json.depends_on` storage migration。
  - dogfooding `spec-dock/` generated runtime implementation edits。
  - live GitHub mutation / external product repo mutation。
- 計画済み契約:
  - closure ids: `cl-boundary-artifacts`, `cl-boundary-storage-source`, `cl-boundary-external`
  - Verification: `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`; if touched, `uv run pytest tests/unit/presentation/test_deps_raw_puml.py`
- 委任契約:
  - delegated role: `dev-coder`
  - source of truth / input docs: `requirement.md`, `design.md`, `plan.md`, S03/S05/S06 worker evidence
  - allowed changes: 対象 files に限定し、non-goal artifact/source/external boundary assertions と必要最小の approved-scope defect fix だけを変更する。
  - stop conditions: storage migration、dogfooding generated runtime implementation edit、external mutation、non-goal artifact contract expansion、allowed paths 外の変更が必要。
  - output required: changed files、boundary evidence summary、verification result、material decision の Ledger Note または `No material implementation decisions beyond the approved plan.`
  - report evidence destination: `report.md` S07 session log、Closure Coverage、Closure Delta、Delegated Worker Evidence、Reviewer Gate Status、Step Commit Gate。
- 具体テストケース:
  - `tc-s07-001`: `deps-issues.json` / `deps-raw.puml` do not become complete raw audit.
  - `tc-s07-002`: issue-wide diff contains provider source/test changes only for implementation, no storage migration or external repo mutation evidence.
- reviewer focus:
  - non-goal contract expansion 回避、source-of-truth discipline、external-state independence。
- amendment trigger:
  - AC-003 complete audit と existing visual projection の間に real conflict が出た場合。

## ドキュメント影響の解消ステップ S90
- 対象:
  - `spec-dock/docs/reference_deps.md`
  - `spec-dock/docs/reference_sync.md`
  - CLI help docs / generated context guidance that mention `deps check --json`, `index-all`, `deps-issues.json`, or `deps-raw.puml`
- 対応:
  - docs impact があれば `doc-writer` に provider source of truth の focused update を委任する。
  - docs impact がなければ、理由を `report.md` に記録する。
- reviewer:
  - `spec-reviewer`
- verification:
  - docs change が shipped scaffold / snapshots に影響する場合は targeted tests を追加し、必要に応じて `uv run pytest tests/unit/infra/test_init_update.py`。

## 最終品質ゲートステップ S99
- branch diff 範囲:
  - iss-00235 の requirement/design/plan/report/discussions/source/tests/docs。
- 必須 validation:
  - `uv run pytest tests/unit/domain/test_deps.py tests/unit/application/test_check_deps.py tests/unit/presentation/test_runtime_sync_s07.py tests/cli_runtime/test_runtime_deps_s04.py`
  - QA が必要と判断した場合: `uv run pytest tests/cli_runtime/test_deps.py tests/cli_runtime/test_sync.py`
- final QA gate:
  - reviewer: `qa-reviewer`
  - 範囲: AC-001..AC-004 / EC-001..EC-004 coverage、missing high-value tests、manual/integration test 要否。
- final code review gate:
  - reviewer: `code-reviewer`
  - 範囲: integrated diff、layering、additive compatibility、deterministic sorting、forbidden changes。
- final spec review gate:
  - reviewer: `spec-reviewer`
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。
- final commit / PR gate:
  - final report ledger を更新し、clean status を確認し、PR 作成後に mergeable state を確認する。

## 未確定事項
- なし。

## 最終完了条件
- AC-001..AC-004 と EC-001..EC-004 の closure evidence が `report.md` に記録済み。
- S01-S07 が committed または approved-no-op。
- S90 docs impact が resolved。
- S99 QA / code / spec reviewer pass。
- Targeted validation が pass。
- Git branch が PR として main に merge 可能な状態。
