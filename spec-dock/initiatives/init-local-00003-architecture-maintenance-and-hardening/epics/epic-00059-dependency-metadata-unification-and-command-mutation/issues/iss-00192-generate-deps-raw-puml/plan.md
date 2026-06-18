---
種別: 実装計画書（Issue）
ID: "iss-00192"
タイトル: "Generate Raw Dependency View"
関連GitHub: ["#192"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
依存: ["requirement.md", "design.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00192 Generate Raw Dependency View — 実装計画（実行契約 / Execution Contract）

## この計画で満たす要件ID
- AC:
  - AC-001: `sync` が `spec-dock/deps-raw.puml` を生成し、dashboard / sync output から発見できる。
  - AC-002: issue->issue raw direct dependency を ancestor package と `blocks` direction で表示する。
  - AC-003: epic->epic / initiative->initiative parent-level dependency を package endpoint と nesting で読み分けられる。
  - AC-004: epic->issue / issue->epic など mixed dependency を package endpoint / rectangle endpoint と nesting で読み分けられる。
  - AC-005: 既存 `deps-issues.puml` / `.agent/deps-issues.json` の semantics を変えない。
  - AC-006: deps preflight failure を許容する `sync --force` では stale graph を残さず disabled `deps-raw.puml` を上書きする。
  - AC-007: `deps-raw.puml` を generated artifact として ignore する。
- EC:
  - EC-001: descendant issue がない parent participant も表示する。
  - EC-002: nonparticipant sibling を除外し、ancestor package は保持する。
  - EC-003: done / closed issue participant も raw view に含める。
  - EC-004: raw dependency が 0 件でも valid PlantUML note を生成する。
- 制約:
  - `.meta.json.depends_on` 以外の dependency storage を追加しない。
  - raw dependency JSON artifact を追加しない。
  - `deps check` / `deps add/remove` / existing effective dependency view を変更しない。
  - provider-side runtime source を正本として変更する。

## 依存関係から導く実装順序
- 依存関係の参照元:
  - `design.md` の `依存関係分析`、`Module Dependency Diagram`、`ディレクトリ / ファイル変更計画`。
- 順序ルール:
  - application contract を先に固定する。
  - renderer は contract の後に実装する。
  - writer / dashboard / CLI / `.gitignore` は renderer artifact ができてから統合する。
  - disabled behavior と compatibility regression は normal path 統合後に閉じる。
- step 依存サマリー:
  - S01: raw direct dependency contract propagation。S02/S03/S04 を unblock。
  - S02: valid renderer and dependency-focused subset。S03/S04 を unblock。
  - S03: normal sync artifact write, discovery, ignore。S04/S05 を unblock。
  - S04: forced deps failure disabled artifact。S05 を unblock。
  - S05: existing dependency artifact regression preservation。S90/S99 を unblock。
  - S90: docs impact resolution。S99 を unblock。
  - S99: final quality gate。

## ステップ一覧
- S01:
  - 観測可能な振る舞い: `SyncStateResult` が raw direct dependency map を保持する。
  - 依存: requirement/design reviewer pass。
  - unblock: S02/S03/S04。
  - 対象ファイル: `application/contracts.py`, `application/sync_state.py`, `presentation/contracts.py`, affected tests。
  - 閉じる要件: cl-001 support, cl-006 guard。
  - レビューゲート: code-reviewer。
- S02:
  - 観測可能な振る舞い: valid `deps-raw.puml` renderer が dependency-focused subset を出力する。
  - 依存: S01。
  - unblock: S03/S04。
  - 対象ファイル: `presentation/json_state.py`, `presentation/puml.py`, focused presentation tests。
  - 閉じる要件: cl-002, cl-003, cl-004, cl-005, cl-009, cl-010, cl-011, cl-012 renderer side。
  - レビューゲート: code-reviewer。
- S03:
  - 観測可能な振る舞い: normal `sync` が `deps-raw.puml` を書き、dashboard / sync output / `.gitignore` に反映する。
  - 依存: S01/S02。
  - unblock: S04/S05。
  - 対象ファイル: `infra/artifact_writer.py`, `application/sync_state.py`, `presentation/markdown.py`, `presentation/cli_text.py`, `src/spec_dock/assets/spec_dock/.gitignore`, runtime tests。
  - 閉じる要件: cl-001, cl-008, cl-012 sync side。
  - レビューゲート: code-reviewer。
- S04:
  - 観測可能な振る舞い: `sync --force` の deps failure 時に disabled `deps-raw.puml` を上書きする。
  - 依存: S03。
  - unblock: S05。
  - 対象ファイル: `presentation/puml.py`, `presentation/json_state.py`, `application/sync_state.py`, focused runtime tests。
  - 閉じる要件: cl-007。
  - レビューゲート: code-reviewer。
- S05:
  - 観測可能な振る舞い: 既存 effective dependency artifacts / readiness / mutation semantics が変わっていない。
  - 依存: S01-S04。
  - unblock: S90/S99。
  - 対象ファイル: focused regression tests and fixture updates only。
  - 閉じる要件: cl-006。
  - レビューゲート: code-reviewer or approved-no-op evidence。
- S90:
  - 観測可能な振る舞い: docs impact が updated または justified no-op として解消される。
  - 依存: S01-S05。
  - unblock: S99。
  - 対象ファイル: likely `src/spec_dock/assets/spec_dock/docs/reference_sync.md`, possibly `reference_deps.md`。
  - 閉じる要件: docs impact closure。
  - レビューゲート: spec-reviewer。
- S99:
  - 観測可能な振る舞い: final QA / code / spec gates が通り、closure coverage と report evidence が閉じる。
  - 依存: S01-S90。
  - unblock: PR / merge preparation / issue finish。
  - 対象ファイル: report evidence and bounded review fixes only。
  - 閉じる要件: all closure ids。
  - レビューゲート: qa-reviewer, issue-wide code-reviewer, spec-reviewer。

## 要件 ↔ ステップ対応
- AC-001 -> S03
- AC-002 -> S02
- AC-003 -> S02
- AC-004 -> S02
- AC-005 -> S05
- AC-006 -> S04
- AC-007 -> S03
- EC-001 -> S02
- EC-002 -> S02
- EC-003 -> S02
- EC-004 -> S02/S03
- design reviewer P2 -> S02 (`cl-005`)

## 仕様固定クロージャ索引（Spec-Locked Closure Index）

| 識別子（ID） | ステップ（step） | スライス（slice） | 種別（type） | 仕様リンク | 固定する期待値 | 観測可能な入力 / 状態 | 防ぐ bug class | 必須 | 証跡レベル（evidence level） | クロージャ証跡（closure evidence） |
|---|---|---|---|---|---|---|---|---|---|---|
| cl-001 | S03 | normal sync artifact | acceptance | AC-001 | `sync` が `spec-dock/deps-raw.puml` を生成し dashboard / sync output に表示する | valid raw dependency tree and sync | artifact omitted / undiscoverable | yes | red-required | report Step/Test Closure |
| cl-002 | S02 | issue raw edge | acceptance | AC-002 | issue->issue edge が ancestor package と `blocks` direction を持つ | issue depends_on issue | hierarchy lost / edge reversed | yes | red-required | report Step/Test Closure |
| cl-003 | S02 | parent raw edge | acceptance | AC-003 | epic/initiative parent-level edge が package endpoint と nesting で読める | epic/initiative depends_on parent | parent intent compiled away | yes | red-required | report Step/Test Closure |
| cl-004 | S02 | mixed parent/issue edge | acceptance | AC-004 | epic->issue / issue->epic edge が package endpoint / rectangle endpoint で読める | mixed node-kind dependency | mixed intent indistinguishable | yes | red-required | report Step/Test Closure |
| cl-005 | S02 | initiative mixed edge | reviewer coverage | design reviewer P2 | initiative->issue または issue->initiative edge が coverage される | initiative and issue mixed dependency | initiative mixed edge gap | yes | red-required | report Step/Test Closure |
| cl-006 | S05 | compatibility | regression | AC-005 | `deps-issues` / readiness / mutation semantics が変わらない | existing deps fixtures and commands | raw graph leaks into effective graph | yes | covered-existing + focused regression | report Closure Coverage |
| cl-007 | S04 | disabled artifact | negative | AC-006 | `sync --force` failure が disabled `deps-raw.puml` を上書きする | invalid deps tree after valid artifact | stale graph remains | yes | red-required | report Step/Test Closure |
| cl-008 | S03 | generated ignore | acceptance | AC-007 | shipped `.gitignore` が `deps-raw.puml` を ignore する | initialized repo `.gitignore` / check-ignore | generated file tracked | yes | red-required / inspect assertion | report Step/Test Closure |
| cl-009 | S02 | empty parent participant | edge case | EC-001 | descendant issue なし parent participant が package endpoint として残る | parent dependency with no issue expansion | empty parent dropped | yes | red-required | report Step/Test Closure |
| cl-010 | S02 | dependency-focused subset | edge case | EC-002 | nonparticipant sibling は出ず、ancestor package は出る | tree with unrelated sibling | full tree leakage | yes | red-required | report Step/Test Closure |
| cl-011 | S02 | done participant | edge case | EC-003 | done / closed issue participant も raw view に含まれる | done issue with direct dependency | todo filter reused | yes | red-required | report Step/Test Closure |
| cl-012 | S02/S03 | zero dependency | edge case | EC-004 | dependency 0 件でも valid PlantUML note と file が生成される | valid tree with no edges | skipped/empty/stale artifact | yes | red-required | report Step/Test Closure |

## レビュー / QA ゲート方針
- RG1 step review:
  - 実施タイミング: 各 implementation step の commit 前。
  - reviewer: code/runtime/tests/scaffold は `code-reviewer`、docs-only は `spec-reviewer`。
  - pass 条件: `review_status: pass`。
- QG1 final QA:
  - reviewer: `qa-reviewer`。
  - 範囲: cl-001..cl-012 の obligation coverage、missing high-value tests、integration test 要否。
- CG1 final code review:
  - reviewer: issue-wide `code-reviewer`。
  - 範囲: integrated diff、architecture boundary、compatibility、test quality。
- SG1 final spec review:
  - reviewer: `spec-reviewer`。
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。

## 実行ルール（全ステップ共通）
- 1 implementation step = 1 behavior slice = 1 review scope = 1 commit boundary を標準とする。
- 実行結果、Red / Green / Refactor evidence、discovered tests、closure delta、reviewer verdict、commit/no-op evidence は `report.md` に記録する。
- delegated worker output は reviewer pass の代替にしない。
- 新しい仕様差分、bug class、外部 contract risk、未計画 closure が見つかった場合は report に記録し、必要なら plan amendment と fresh spec review を先に行う。

## 実装ステップ

### 実装ステップ S01 — Raw Direct Dependency Contract Propagation
- 振る舞いの目標（behavior goal）:
  - resolved raw direct dependencies を application sync state から presentation / writer へ渡せる contract にする。
- design 参照:
  - `SyncStateResult.raw_node_depends_on_map`, `DepsRawArtifact`, `ArtifactBundle.deps_raw`。
- 依存:
  - approved requirement/design/plan。
- unblock:
  - S02, S03, S04。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/contracts.py`
  - minimal affected tests / fixtures。
- 計画済み契約（planned contract）:
  - scope:
    - `SyncStateResult.raw_node_depends_on_map` を追加し、`load_node_dependency_resolutions()` 由来の direct dependency を保持する。
    - `DepsRawArtifact` と `ArtifactBundle.deps_raw` を追加する。
  - テスト義務:
    - closure id: cl-001 support, cl-006 guard。
    - coverage rationale: renderer / writer の入力 contract であり、raw map が readiness に漏れないことが重要。
  - Red / 代替証跡の要件:
    - red-required: raw map population。
    - covered-existing: readiness behavior は S05 で focused regression。
  - 実装範囲:
    - allowed paths: 対象ファイルと focused tests。
    - forbidden changes: `deps check`, `deps add/remove`, raw JSON artifact, `.meta.json` storage, unrelated fixture refactor。
  - Green 検証:
    - focused application/sync test。
    - affected constructor fixture tests。
  - Refactor / cleanup ガードレール:
    - dependency validation ownership を移動しない。
  - closure 証跡要件:
    - Step Contract Closure, Test Contract Closure, Closure Coverage。
  - report 証跡の記録先:
    - `report.md` Implementation Delegation Gate, TDD evidence, Step Contract Closure, Test Contract Closure, Step Commit Gate。
  - amendment trigger:
    - presentation 層で `.meta.json` read が必要になる、または `.agent/deps-raw.json` が必要になる。

#### 委任契約（delegation contract）
- 委任ロール（delegated role）:
  - dev-coder。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `workflow_issue.md`, target files。
- 許可 paths:
  - S01 対象ファイルと focused tests。
- 禁止 changes:
  - readiness semantics / mutation contract / dependency storage / unrelated refactor。
- 受け入れ条件:
  - `raw_node_depends_on_map` が dependent node id -> sorted prerequisite node ids を保持する。
  - existing `issue_depends_on_map` と `deps_eval_by_id` が readiness path のまま。
- 必須 tests または docs-only verification:
  - focused red/green test and affected fixture tests。
- reviewer focus:
  - code-reviewer: contract boundary, no readiness semantic change, narrow fixture updates。
- 必須出力（output required）:
  - changed files, test command/result, unresolved risks, ledger note。
- 停止条件（stop conditions）:
  - raw map population に `deps_reader` semantics 変更が必要、または presentation filesystem read が必要。

#### 具体テストケース一覧
- `tc-s01-001` acceptance: sync state carries raw direct dependencies
  - 前提: valid graph に issue->issue `.meta.json.depends_on` がある。
  - 操作: existing application sync path / focused test harness で sync state を collect する。
  - 期待結果: `SyncStateResult.raw_node_depends_on_map` が dependent issue id -> prerequisite issue id を含む。
  - 失敗検出: 現状のように raw dependency が validation 後に破棄される回帰を検出する。
  - 検証方法: focused sync/application test。
  - 関連 closure id: cl-001
- `tc-s01-002` regression: raw map does not replace effective dependency map
  - 前提: raw parent-level dependency と issue-level effective dependency の違いが観測できる fixture がある。
  - 操作: `raw_node_depends_on_map` と `issue_depends_on_map` を inspect する。
  - 期待結果: raw map は node-level ids を保持し、`issue_depends_on_map` は existing effective issue dependency のまま。
  - 失敗検出: raw map が readiness input に漏れる回帰を検出する。
  - 検証方法: focused assertion or S05 regression。
  - 関連 closure id: cl-006

#### ステップ完了契約（step closure contract）
- closure id:
  - cl-001 support, cl-006 guard。
- close 条件:
  - raw map contract が通り、existing readiness path へ影響しない証跡がある。
- 検証 evidence:
  - focused test command / affected fixture tests。
- report evidence:
  - Step Contract Closure, Test Contract Closure, Closure Coverage。
- 残リスク:
  - constructor fixture churn。mechanical update として reviewer が確認する。

#### ステップゲート（step gate）
- step reviewer gate:
  - reviewer: code-reviewer。
  - review 範囲: S01 diff and focused tests。
  - pass 条件: review_status: pass。
  - re-review rule: 指摘修正後に pass まで再実行。
- commit / no-op gate:
  - closure 状態: committed。
  - commit 範囲: S01 only。
  - no-op: invalid unless current code already carries raw map。

### 実装ステップ S02 — Valid `deps-raw.puml` Renderer and Dependency-Focused Subset
- 振る舞いの目標:
  - raw direct dependency から dependency-focused nested package PlantUML を生成する。
- design 参照:
  - `deps-raw.puml` payload / rendering contract。
- 依存:
  - S01。
- unblock:
  - S03, S04。
- 対象ファイル:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py`
  - focused presentation tests。
- 計画済み契約:
  - scope:
    - `render_deps_raw_artifact()` と `render_deps_raw_puml()` を追加する。
    - issue / epic / initiative participant と ancestor package を deterministic に subset 化する。
  - テスト義務:
    - closure id: cl-002, cl-003, cl-004, cl-005, cl-009, cl-010, cl-011, cl-012 renderer side。
    - coverage rationale: artifact の observable contract 本体であり、AC/EC と visual decision を直接守る。
  - Red / 代替証跡の要件:
    - red-required for all renderer cases。
  - 実装範囲:
    - allowed paths: 対象ファイルと focused tests。
    - forbidden changes: full-tree rendering, hidden anchor nodes without amendment, raw JSON output, `deps-issues` semantic change。
  - Green 検証:
    - text-level PlantUML tests。
  - Refactor / cleanup ガードレール:
    - helper extraction は小さく、existing `deps-issues` rewrite を避ける。
  - closure 証跡要件:
    - Step Contract Closure, Test Contract Closure, Closure Coverage。
  - report 証跡の記録先:
    - `report.md` TDD evidence and closure ledgers。
  - amendment trigger:
    - accepted endpoint design を PlantUML syntax で表せず hidden anchors 等が必要になる。

#### 委任契約（delegation contract）
- 委任ロール: dev-coder。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, visual simulation `.puml`, `presentation/json_state.py`, `presentation/puml.py`。
- 許可 paths:
  - S02 対象ファイルと focused tests。
- 禁止 changes:
  - full tree view, raw JSON artifact, `deps-issues` semantics change。
- 受け入れ条件:
  - PlantUML text が `left to right direction`, `skinparam linetype ortho`, `skinparam packageStyle rectangle`, nested packages, issue state rectangles, uniform `: blocks` edges を持つ。
- 必須 tests:
  - 下記 concrete cases。
- reviewer focus:
  - code-reviewer: renderer correctness, deterministic sorting, escaping, separation from `deps-issues`。
- 必須出力:
  - changed files, test command/result, sample snippets if useful, unresolved risks。
- 停止条件:
  - PlantUML package endpoint が accepted design どおり表現できない。

#### 具体テストケース一覧
- `tc-s02-001` acceptance: issue->issue edge with ancestors
  - 前提: `iss-b` depends_on `iss-a` があり、ancestor initiative / epic が存在する。
  - 操作: `deps-raw.puml` を render する。
  - 期待結果: ancestor packages、両 issue rectangles、`iss-a alias --> iss-b alias : blocks` が出る。
  - 失敗検出: hierarchy 欠落または edge direction 反転を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-002
- `tc-s02-002` acceptance: parent-level package endpoint edge
  - 前提: `epic-b depends_on epic-a` または `init-b depends_on init-a` がある。
  - 操作: `deps-raw.puml` を render する。
  - 期待結果: package aliases と package endpoint `blocks` edge が出る。issue-only edge に compile されない。
  - 失敗検出: parent-level intent が失われる回帰を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-003
- `tc-s02-003` acceptance: epic->issue or issue->epic mixed edge
  - 前提: `iss-x depends_on epic-y` または `epic-y depends_on iss-x` がある。
  - 操作: render する。
  - 期待結果: package endpoint と issue rectangle endpoint が nested context 内に出る。
  - 失敗検出: mixed edge が issue-only edge として失われる回帰を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-004
- `tc-s02-004` reviewer P2: initiative-involved mixed edge
  - 前提: `iss-x depends_on init-y` または `init-y depends_on iss-x` がある。
  - 操作: render する。
  - 期待結果: initiative package endpoint と issue rectangle endpoint が出て、`blocks` direction が保たれる。
  - 失敗検出: initiative-involved mixed edge coverage gap を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-005
- `tc-s02-005` edge case: nonparticipants omitted and ancestors retained
  - 前提: participant issue、unrelated sibling issue、ancestor packages がある。
  - 操作: render する。
  - 期待結果: participant と ancestors は出るが、unrelated sibling issue / epic は出ない。
  - 失敗検出: full-tree leakage を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-010
- `tc-s02-006` edge case: parent participant without descendant issue expansion
  - 前提: direct participant が epic または initiative で、descendant issue を direct participant として含まない。
  - 操作: render する。
  - 期待結果: package endpoint が edge endpoint として残る。
  - 失敗検出: empty package removal により raw intent が消える回帰を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-009
- `tc-s02-007` edge case: done / closed participant included
  - 前提: done / closed issue が raw direct dependency に参加している。
  - 操作: render する。
  - 期待結果: todo projection で除外されず raw view に出る。
  - 失敗検出: todo-only filtering の誤用を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-011
- `tc-s02-008` edge case: zero raw direct dependencies
  - 前提: valid tree に direct dependency が 0 件。
  - 操作: render する。
  - 期待結果: valid PlantUML と no-dependencies note が出る。
  - 失敗検出: empty file / skipped file / stale graph risk を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-012

#### ステップ完了契約
- closure id:
  - cl-002, cl-003, cl-004, cl-005, cl-009, cl-010, cl-011, cl-012 renderer side。
- close 条件:
  - renderer tests が通り、visual decision と矛盾しない。
- 検証 evidence:
  - focused presentation tests。
- report evidence:
  - Step/Test Closure and Closure Coverage。
- 残リスク:
  - rendered bitmap layout variance。source text contract を primary evidence とする。

#### ステップゲート
- step reviewer gate:
  - reviewer: code-reviewer。
  - review 範囲: S02 renderer and tests。
  - pass 条件: review_status: pass。
- commit / no-op gate:
  - closure 状態: committed。
  - commit 範囲: S02 only。
  - no-op: invalid。

### 実装ステップ S03 — Normal Sync Artifact Write, Discovery, and Ignore Integration
- 振る舞いの目標:
  - normal `sync` が `spec-dock/deps-raw.puml` を書き、dashboard / sync output / `.gitignore` に反映する。
- design 参照:
  - artifact pipeline, dashboard/sync discovery, generated artifact ignore。
- 依存:
  - S01, S02。
- unblock:
  - S04, S05。
- 対象ファイル:
  - `application/contracts.py`, `application/sync_state.py`, `infra/artifact_writer.py`, `presentation/markdown.py`, `presentation/cli_text.py`, `src/spec_dock/assets/spec_dock/.gitignore`, runtime / infra tests。
- 計画済み契約:
  - scope:
    - writer が root `deps-raw.puml` を書く。
    - `ArtifactWriteResult.deps_raw_puml_path` を返す。
    - dashboard と sync output に path を出す。
    - `.gitignore` に `deps-raw.puml` を追加する。
  - テスト義務:
    - closure id: cl-001, cl-008, cl-012 sync side。
  - Red / 代替証跡:
    - red-required for file write/discovery。
    - inspect assertion acceptable for `.gitignore` if matching existing test style。
  - 実装範囲:
    - allowed paths: 対象ファイルと focused tests。
    - forbidden changes: dogfooding generated artifact direct edit, unrelated dashboard redesign。
  - Green 検証:
    - CLI runtime sync test, presentation/infra unit tests, gitignore test。
  - Refactor / cleanup ガードレール:
    - existing artifact paths を消さず、新 path を deterministic に追加する。
  - amendment trigger:
    - writer atomicity redesign が必要、または root `spec-dock/` 以外へ出す必要が出る。

#### 委任契約（delegation contract）
- 委任ロール: dev-coder。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, `artifact_writer.py`, `markdown.py`, `cli_text.py`, `.gitignore`, existing sync tests。
- 許可 paths:
  - S03 対象ファイルと focused tests。
- 禁止 changes:
  - generated dogfooding artifact edits, global gitignore policy changes, unrelated UI/docs redesign。
- 受け入れ条件:
  - normal sync writes and reports `spec-dock/deps-raw.puml`; dashboard exposes raw deps view; `.gitignore` marks it generated。
- 必須 tests:
  - 下記 concrete cases。
- reviewer focus:
  - code-reviewer: artifact pipeline integration and scaffold source-of-truth discipline。
- 必須出力:
  - changed files, test command/result, generated path evidence。
- 停止条件:
  - integration requires direct edit of dogfooding generated artifacts。

#### 具体テストケース一覧
- `tc-s03-001` acceptance: sync writes deps-raw artifact
  - 前提: valid direct raw dependency を持つ temp repo。
  - 操作: existing hermetic sync command/test harness を実行する。
  - 期待結果: `spec-dock/deps-raw.puml` が存在し、valid renderer output を含む。
  - 失敗検出: renderer はあるが writer integration がない回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_sync.py` or existing runtime sync fixture。
  - 関連 closure id: cl-001
- `tc-s03-002` discovery: dashboard and sync output include raw path
  - 前提: normal sync succeeds。
  - 操作: `spec-dock/dashboard.md` と sync stdout / `render_sync_text()` を inspect する。
  - 期待結果: both include `spec-dock/deps-raw.puml`。
  - 失敗検出: artifact created but undiscoverable を検出する。
  - 検証方法: presentation unit test plus runtime sync assertion。
  - 関連 closure id: cl-001
- `tc-s03-003` generated artifact ignore
  - 前提: initialized temp repo に shipped `spec-dock/.gitignore` がある。
  - 操作: `.gitignore` を inspect し、可能なら `git check-ignore spec-dock/deps-raw.puml` を実行する。
  - 期待結果: `deps-raw.puml` が ignore される。
  - 失敗検出: generated file が source change として出る回帰を検出する。
  - 検証方法: `tests/cli_runtime/test_sync.py` gitignore tests or `tests/unit/infra/test_init_update.py`。
  - 関連 closure id: cl-008
- `tc-s03-004` edge case: zero dependency sync still writes file
  - 前提: valid temp repo has no direct raw dependencies。
  - 操作: sync を実行する。
  - 期待結果: `spec-dock/deps-raw.puml` が存在し、no-dependencies note を含む。
  - 失敗検出: edge list empty で file が skip される回帰を検出する。
  - 検証方法: CLI runtime sync test。
  - 関連 closure id: cl-012

#### ステップ完了契約
- closure id:
  - cl-001, cl-008, cl-012 sync side。
- close 条件:
  - file write, discovery, ignore の証跡がある。
- 検証 evidence:
  - runtime / presentation / gitignore tests。
- report evidence:
  - Step/Test Closure, Closure Coverage。
- 残リスク:
  - artifact write order change。reviewer が existing outputs preserved を確認する。

#### ステップゲート
- reviewer: code-reviewer。
- pass 条件: review_status: pass。
- commit 範囲: S03 only。
- no-op: invalid。

### 実装ステップ S04 — Forced Deps Failure Disabled Artifact Behavior
- 振る舞いの目標:
  - `sync --force` の deps preflight failure 時に stale valid graph ではなく disabled `deps-raw.puml` を書く。
- design 参照:
  - disabled output contract。
- 依存:
  - S03。
- unblock:
  - S05。
- 対象ファイル:
  - `presentation/puml.py`, `presentation/json_state.py`, `application/sync_state.py`, focused CLI runtime tests。
- 計画済み契約:
  - scope:
    - disabled renderer と forced sync bundle behavior。
  - テスト義務:
    - closure id: cl-007。
  - Red / 代替証跡:
    - red-required。
  - 実装範囲:
    - allowed paths: 対象ファイルと focused tests。
    - forbidden changes: preflight validation rule change, forced sync warning semantics change。
  - Green 検証:
    - disabled renderer test and forced sync runtime test。
  - Refactor / cleanup ガードレール:
    - existing disabled tree/deps-issues style に合わせ、新 failure framework は作らない。
  - amendment trigger:
    - existing force path で bundle build ができず broader error handling が必要になる。

#### 委任契約（delegation contract）
- 委任ロール: dev-coder。
- 入力 docs:
  - AC-006, design disabled output contract, existing disabled renderers, `workflow_issue.md`。
- 許可 paths:
  - S04 対象ファイルと focused tests。
- 禁止 changes:
  - validation rules, `deps check` semantics, error swallowing。
- 受け入れ条件:
  - forced failure output is disabled PlantUML, not skipped/stale。
- 必須 tests:
  - 下記 concrete cases。
- reviewer focus:
  - code-reviewer: stale prevention, error sanitization, no validation semantics change。
- 必須出力:
  - changed files, test command/result, stale prevention evidence。
- 停止条件:
  - hermetic forced failure fixture が作れない、または validation contract change が必要。

#### 具体テストケース一覧
- `tc-s04-001` acceptance: disabled renderer includes failure note
  - 前提: renderer receives `deps_preflight_error`。
  - 操作: disabled `deps-raw.puml` を render する。
  - 期待結果: `title deps-raw - DEPS_DISABLED`, `deps_preflight_failed`, `deps.valid=false`, `mode=sync --force`, sanitized error, `@enduml` が出る。
  - 失敗検出: disabled diagnostic content 欠落を検出する。
  - 検証方法: presentation renderer unit test。
  - 関連 closure id: cl-007
- `tc-s04-002` acceptance: forced sync overwrites stale valid graph
  - 前提: existing valid `spec-dock/deps-raw.puml` がある。その後 metadata を invalid deps に変更する。
  - 操作: `sync --force` を実行する。
  - 期待結果: `deps-raw.puml` が disabled content で上書きされ、previous edge text が残らない。
  - 失敗検出: forced failure 後の stale artifact を検出する。
  - 検証方法: CLI runtime sync failure fixture。
  - 関連 closure id: cl-007

#### ステップ完了契約
- closure id:
  - cl-007。
- close 条件:
  - renderer and runtime levels で disabled output が確認される。
- 検証 evidence:
  - focused renderer test and forced sync runtime test。
- report evidence:
  - pre-existing valid content setup, forced failure command/result, disabled replacement evidence。
- 残リスク:
  - error text sanitize variance。source contract に合わせる。

#### ステップゲート
- reviewer: code-reviewer。
- pass 条件: review_status: pass。
- commit 範囲: S04 only。
- no-op: invalid。

### 実装ステップ S05 — Existing Dependency Artifact and Readiness Regression Preservation
- 振る舞いの目標:
  - new raw view が existing effective dependency artifacts / readiness / mutation semantics を変えていないことを証明する。
- design 参照:
  - compatibility / rollback / no raw JSON artifact。
- 依存:
  - S01-S04。
- unblock:
  - S90, S99。
- 対象ファイル:
  - tests and mechanical fixture updates only unless real regression points to S01-S04 code。
- 計画済み契約:
  - scope:
    - existing deps tests / sync tests / focused characterization。
  - テスト義務:
    - closure id: cl-006。
  - Red / 代替証跡:
    - covered-existing plus focused regression assertion。
  - 実装範囲:
    - allowed paths: focused tests / fixture updates or bounded fix of S01-S04 regression。
    - forbidden changes: dependency semantics rewrite, broad snapshot churn。
  - Green 検証:
    - targeted existing tests and broader runtime/presentation lane。
  - Refactor / cleanup ガードレール:
    - S05 は compatibility gate であり feature追加に使わない。
  - amendment trigger:
    - existing semantics change が見つかった場合。

#### 委任契約（delegation contract）
- 委任ロール:
  - dev-coder for bounded test repair/fix, otherwise approved-no-op evidence。
- 入力 docs:
  - AC-005, design compatibility/rollback, existing tests。
- 許可 paths:
  - focused tests / fixture updates, or bounded regression fix。
- 禁止 changes:
  - `deps check`, `deps add/remove`, `deps-issues` expected behavior rewrite。
- 受け入れ条件:
  - cl-006 closed。
- 必須 tests:
  - 下記 concrete cases。
- reviewer focus:
  - code-reviewer: compatibility evidence and mechanical fixture updates。
- 必須出力:
  - commands/results, changed files if any, no-op or fix evidence。
- 停止条件:
  - broad fixture churn or semantic drift。

#### 具体テストケース一覧
- `tc-s05-001` regression: existing deps-issues JSON and PUML remain issue-only
  - 前提: existing representative deps fixture がある。
  - 操作: sync/render し `.agent/deps-issues.json` と `deps-issues.puml` を inspect する。
  - 期待結果: todo issue-only effective graph のまま。raw parent packages は入らない。
  - 失敗検出: raw map が existing deps-issues artifacts に漏れる回帰を検出する。
  - 検証方法: existing `test_deps` / `test_sync` assertions plus focused characterization。
  - 関連 closure id: cl-006
- `tc-s05-002` regression: dependency mutation and readiness commands still pass
  - 前提: existing tests cover `deps add/remove`, `deps check`, sync readiness。
  - 操作: targeted existing regression lane を実行する。
  - 期待結果: new artifact の expected additions 以外に behavior change がない。
  - 失敗検出: readiness / mutation contract drift を検出する。
  - 検証方法: `uv run pytest tests/cli_runtime/test_deps.py` and relevant sync tests。
  - 関連 closure id: cl-006

#### ステップ完了契約
- closure id:
  - cl-006。
- close 条件:
  - compatibility tests pass or exact blocker recorded。
- 検証 evidence:
  - targeted existing tests / broader lane as needed。
- report evidence:
  - Test Contract Closure, Closure Coverage, no-op/fix evidence。
- 残リスク:
  - none if tests/review pass。

#### ステップゲート
- reviewer:
  - code-reviewer if changes; approved-no-op evidence if no changes。
- pass 条件:
  - review_status: pass or valid approved-no-op。
- commit 範囲:
  - S05 only if changes。

### ドキュメント影響の解消ステップ S90（docs impact resolution / docs refresh）
- 対象:
  - likely `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - possibly `src/spec_dock/assets/spec_dock/docs/reference_deps.md`
  - generated artifact lists in shipped docs/templates if present。
- 対応:
  - `deps-raw.puml` を sync generated artifact として記載する。
  - raw direct dependency view と issue-level effective readiness view の違いを必要最小限で明記する。
  - docs 更新不要の場合は report に justified no-op を記録する。
- doc update owner:
  - doc-writer when updates are required。
- spec/doc review:
  - reviewer: spec-reviewer。
  - pass 条件: docs が requirement / design / plan と整合し、未解決の必須 docs 影響がない。

#### 委任契約（delegation contract）
- 委任ロール: doc-writer。
- 入力 docs:
  - `requirement.md`, `design.md`, `plan.md`, S01-S05 observed behavior, `reference_sync.md`, `reference_deps.md`。
- 許可 paths:
  - identified shipped docs and focused docs tests。
- 禁止 changes:
  - workflow policy rewrites, unrelated wording cleanup, canonical issue docs except orchestrator report evidence。
- 必須 verification:
  - docs diff inspection, relevant pytest if docs tests exist, spec-reviewer docs/spec alignment。
- 停止条件:
  - docs update would change product contract beyond approved requirement/design。

#### 具体テストケース一覧
- `tc-s90-001` docs impact: sync artifact inventory is not stale
  - 前提: sync outputs を列挙する shipped docs を inspect する。
  - 操作: docs と actual sync wrote list / dashboard Observability を比較する。
  - 期待結果: `spec-dock/deps-raw.puml` を記載する、または report に non-blocking no-op rationale がある。
  - 失敗検出: new artifact を docs が漏らす回帰を検出する。
  - 検証方法: docs diff inspection and relevant docs tests if present。
  - 関連 closure id: docs impact closure
- `tc-s90-002` docs impact: raw view is not described as readiness source
  - 前提: dependency docs を inspect する。
  - 操作: `deps-raw` / `deps-issues` language を確認する。
  - 期待結果: raw direct visualization と issue-level effective readiness view が区別されている。
  - 失敗検出: `deps-raw.puml` を readiness authority と誤読させる docs を検出する。
  - 検証方法: docs inspection and spec-reviewer。
  - 関連 closure id: cl-006

#### ステップ完了契約
- S90 docs impact が updated または approved-no-op として解消される。
- `report.md` Docs Impact Resolution に owner、evidence、spec-reviewer result を記録する。

#### ステップゲート
- step reviewer: spec-reviewer docs/spec alignment pass。
- commit gate: docs changed なら S90 commit、no change なら approved-no-op evidence。

### 最終品質ゲートステップ S99（final quality gate）
- branch diff 範囲:
  - S01-S05/S90 integrated diff and report evidence。
- 必須 validation:
  - `./spec-dock/scripts/spec-dock validate`
  - targeted pytest lanes from step evidence。
  - broader `uv run pytest tests/unit` and `uv run pytest tests/cli_runtime` unless reviewers accept narrower evidence。
- final QA gate:
  - reviewer: qa-reviewer。
  - 範囲: cl-001..cl-012 obligation coverage and integration test sufficiency。
  - pass 条件: reviewer pass。
- final code review ゲート:
  - reviewer: issue-wide code-reviewer。
  - 範囲: application / presentation / infra / tests / docs / scaffold integrated diff。
  - pass 条件: review_status: pass。
- final spec review ゲート:
  - reviewer: spec-reviewer。
  - 範囲: requirement / design / plan / report / implementation / tests / docs alignment。
  - pass 条件: reviewer pass。
- final commit gate:
  - commit 範囲: final report ledger / delivery evidence boundary only。
  - final report ledger: no open decision/adoption/reviewer gaps。
  - post-commit external evidence destination: final response / PR / issue comment as appropriate。

#### 具体テストケース一覧
- `tc-s99-001` final QA coverage
  - 前提: S01-S90 report evidence が complete。
  - 操作: qa-reviewer が closure ids, tests, integration need を review する。
  - 期待結果: QA pass、または bounded missing tests が追加され re-reviewed。
  - 失敗検出: insufficient behavior coverage のまま completion する回帰を検出する。
  - 検証方法: qa-reviewer verdict in report。
- `tc-s99-002` final integrated diff review
  - 前提: all step commits are present or approved-no-op。
  - 操作: issue-wide code-reviewer が integrated diff を review する。
  - 期待結果: code review pass after bounded fixes。
  - 失敗検出: cross-step architecture / compatibility regression を検出する。
  - 検証方法: code-reviewer verdict in report。
- `tc-s99-003` final spec alignment
  - 前提: implementation, tests, docs, report are complete。
  - 操作: spec-reviewer が requirement/design/plan/report alignment を確認する。
  - 期待結果: spec review pass after bounded fixes。
  - 失敗検出: unsatisfied AC/EC, docs impact gaps, stale evidence を検出する。
  - 検証方法: spec-reviewer verdict in report。

## 推奨検証コマンド
- Narrow first:
  - `uv run pytest tests/unit/presentation/test_runtime_sync_s07.py`
  - `uv run pytest tests/cli_runtime/test_sync.py`
  - `uv run pytest tests/cli_runtime/test_deps.py`
  - `uv run pytest tests/unit/infra/test_init_update.py`
- Broader lanes before S99 completion:
  - `uv run pytest tests/unit`
  - `uv run pytest tests/cli_runtime`
  - `./spec-dock/scripts/spec-dock validate`

## 未確定事項
- なし。

## 最終完了条件
- AC/EC 達成:
  - cl-001..cl-012 が Step Contract Closure / Test Contract Closure / Closure Coverage で閉じている。
- docs 影響解決:
  - S90 が updated または approved-no-op として reviewer pass している。
- 全 implementation step 完了:
  - S01-S05/S90 が committed または valid approved-no-op。
- final quality gate pass:
  - qa-reviewer: pass。
  - issue-wide code-reviewer: pass。
  - spec-reviewer: pass。
- delivery:
  - required PR Delivery Gate / Merge Preparation Gate evidence を `workflow_issue.md` に従って記録し、issue finish 前に未解決 ledger を残さない。
