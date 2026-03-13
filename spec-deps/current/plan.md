---
種別: 実装計画書（Issue）
ID: "issue-25"
タイトル: "巨大な app.py を複数 module に分割し tests/test_cli.py を領域別に再編する"
関連GitHub: ["https://github.com/chemitaro/spec-dock/issues/25"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-12"
依存: ["requirement.md", "design.md"]
親: ["#25"]
---

# issue-25 巨大な app.py を複数 module に分割し tests/test_cli.py を領域別に再編する — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001
  - AC-002
  - AC-003
  - AC-004
  - AC-005
- EC:
  - EC-001
  - EC-002
  - EC-003
  - EC-004

## 実装原則
- 正しさを速度より優先する。
- 実装順は `leaf-first / dependency-first` を正本とする。
- 先に「低依存な pure rule / DTO / mapper / read model」を固定し、その後に use case、その後に adapter、その後に command/wiring を作る。
- speculative abstraction を禁止する。
  - 具体的な消費者が 1 つもない `registry` / `bootstrap` / shared contract shell を先に増やさない。
  - shared contract は「最初の消費者 step」で additive に導入する。
- `1 step = 1 review scope = 1 git commit scope` を原則とする。
- `1 iteration = 1 Red -> Green -> Refactor` を守る。
- step の exit は「その step の観測点が閉じたこと」を意味し、AC/EC 全体の達成完了は `S99` と `final exit contract` で判定する。

## 実装順の設計判断
- 旧版計画では `S01` に `cli/parser.py`, `cli/registry.py`, `cli/bootstrap.py`, `commands/*` など command 側の shell が先行していた。
- この issue は最終アーキテクチャとしては layered だが、TDD の実装順としては command 側から入る必要はない。
- 設計書の依存関係に従うと、まず固定すべきなのは次の順序である。
  1. `domain/ids.py`, `domain/models.py`, `domain/tree.py`, `domain/validation.py`
  2. `application/validate_tree.py` と最小 reader seam
  3. `domain/status.py`, `domain/deps.py`
  4. `application/check_deps.py`, `application/status_context.py`, `infra/deps_reader.py`
  5. `application/set_active.py` の read path
  6. `application/set_active.py` の write path
  7. `application/sync_state.py`
  8. `application/create_node.py`
  9. `application/create_node.py` の `new doc` branch
  10. `application/import_node.py`
  11. `commands/*`, `cli/*` の共通 shell
- したがって、本計画では command shell を後段へ送り、vertical slice ごとに bottom-up で積み上げる。

## マイルストーン一覧
- M1 pure core:
  - 対象:
    - `domain/ids.py`
    - `domain/models.py`
    - `domain/tree.py`
    - `domain/validation.py`
    - `domain/status.py`
    - `domain/deps.py`
    - `infra/contracts.py`
  - exit:
    - low-dependency rule / DTO / stored-shape が pure test で固定される
- M2 read-side slices:
  - 対象:
    - `application/validate_tree.py`
    - `application/check_deps.py`
    - `application/status_context.py`
    - `infra/derived_state_reader.py`
    - `presentation/cli_text.py`
    - `presentation/json_state.py`
  - exit:
    - `validate` と `deps check` の core が新 layered path で green
- M3 active/sync slices:
  - 対象:
    - `domain/active.py`
    - `application/set_active.py`
    - `application/sync_state.py`
    - `infra/active_store.py`
    - `infra/git_cli.py`
    - `infra/json_store.py`
    - `infra/artifact_writer.py`
    - `infra/clock.py`
    - `presentation/markdown.py`
    - `presentation/puml.py`
  - exit:
    - `active show`, `active set/clear`, `sync` が新 core で green
- M4 create/import slices:
  - 対象:
    - `application/create_node.py`
    - `application/create_node.py` の `new doc` branch
    - `application/import_node.py`
    - `infra/template_scaffolder.py`
    - `infra/fs_repo.py`
    - `infra/github_cli.py`
  - exit:
    - `new node`, `new doc`, `import` が新 core で green
- M5 shell/cleanup:
  - 対象:
    - `commands/*`
    - `cli/parser.py`
    - `cli/registry.py`
    - `cli/bootstrap.py`
    - `cli/dispatch.py`
    - `tests/*` 再編
    - 旧 helper detachment
  - exit:
    - shell の正本化、test tree 分割、旧 helper 直依存解消、final diff gate が完了する

## ステップ一覧
- 注記:
  - ここでの `requirement trace` は step が当該 AC/EC の観測点へ寄与することを示す。
  - AC/EC の達成完了判定は `S99 final diff review quality gate` と `final exit contract` を正本とする。
- S01:
  - 観測可能な振る舞い:
    - ids / graph / validation の pure core が `app.py` 非依存でテストできる
  - requirement trace:
    - AC-001
    - AC-002
    - EC-001
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - pure core review
- S02:
  - 観測可能な振る舞い:
    - `validate` の use case core が最小 adapter 経由で動く
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-001
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - validate core slice review
- S03:
  - 観測可能な振る舞い:
    - status / deps の pure core が fixed input で評価できる
  - requirement trace:
    - AC-001
    - AC-002
    - EC-003
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - deps pure core review
- S04:
  - 観測可能な振る舞い:
    - `deps check` が新 use case + renderer で動く
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-003
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - deps command slice review
- S05:
  - 観測可能な振る舞い:
    - `active show` の read model が migration-capable loader で動く
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - active read slice review
- S06:
  - 観測可能な振る舞い:
    - `active set/clear` の guard/order/rollback が新 core で動く
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-003
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - active write slice review
- S07:
  - 観測可能な振る舞い:
    - `sync` の collect/auto-update/artifact write が新 core で動く
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-004
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - sync slice review
- S08:
  - 観測可能な振る舞い:
    - `new initiative|epic|issue` が no-write preflight を含む new core で動く
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - new node slice review
- S09:
  - 観測可能な振る舞い:
    - `new doc` が discussion sequence/path/template write 契約で動く
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - new doc slice review
- S10:
  - 観測可能な振る舞い:
    - `import initiative|epic|issue` が `import -> sync` 契約を維持して動く
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-002
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - import slice review
- S11:
  - 観測可能な振る舞い:
    - `commands/*` と `cli/*` の shell が、すでにある use case を束ねるだけの薄い層として成立する
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-001
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - shell integration review
- S12:
  - 観測可能な振る舞い:
    - test tree 分割が physical refactor として独立に完了する
  - requirement trace:
    - AC-003
    - AC-005
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - test tree split review
- S13:
  - 観測可能な振る舞い:
    - 旧 helper 直依存の解消と rollback basis の commit-level への切替が完了する
  - requirement trace:
    - AC-001
    - AC-005
    - EC-001
  - trace status:
    - partial contribution only; final AC/EC closure is validated in `S99`
  - review gate:
    - helper detachment / rollback transition review
- S90:
  - 観測可能な振る舞い:
    - docs impact が refresh または no-op 理由付きで閉じる
  - review gate:
    - docs impact review
- S99:
  - 観測可能な振る舞い:
    - branch diff 全体で AC/EC trace と blocking finding `0` 件が確認される
  - requirement trace:
    - AC-001
    - AC-002
    - AC-003
    - AC-004
    - AC-005
    - EC-001
    - EC-002
    - EC-003
    - EC-004
  - review gate:
    - final diff review quality gate

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S13, S14, S99
- AC-002 -> S01, S02, S03, S04, S05, S06, S07, S08, S09, S10, S11, S14
- AC-003 -> S12
- AC-004 -> S02, S04, S05, S06, S07, S08, S09, S10, S11, S14, S99
- AC-005 -> S12, S13, S14, S99
- EC-001 -> S01, S02, S04, S05, S06, S07, S08, S09, S10, S11, S13
- EC-002 -> S10
- EC-003 -> S03, S04, S06
- EC-004 -> S07, S14

## shared contract / stored-shape 導入順の正本
- S01:
  - `domain/ids.py`
  - `domain/models.py` の `SpecNodeSeed`, `SpecNode`, `SpecGraph`, `ValidationReport`
  - `domain/tree.py`
  - `domain/validation.py`
- S02:
  - `application/contracts.py` の `ValidateTreeRequest`, `ValidationResult`
  - `application/ports.py` の validate slice に必要な最小 reader seam
  - `infra/contracts.py` の `StoredMetaRecord`
  - `presentation/contracts.py` の `CliText` を validate text renderer の最初の消費者として導入する
- S03:
  - `domain/models.py` の `IssueSnapshot`, `IssueStatusSnapshot`, `ProgressMap`, `Deps*`
- S04:
  - `application/contracts.py` の `TargetRef`, `CheckDepsRequest`, `DepsCheckResult`
  - `infra/contracts.py` の `StoredIssueSnapshot`, `ActiveManifestEntry`, `ActiveManifest`, `ActiveManifestLoadResult`
- S05:
  - `application/contracts.py` の `ShowActiveRequest`, `ActiveViewEntry`, `ActiveViewResult`
- S06:
  - `application/contracts.py` の `SetActiveRequest`, `ActiveSetResult`, `ClearActiveRequest`, `ActiveClearResult`
  - `domain/models.py` の `ActiveSelection`, `BranchDecision`
  - `application/ports.py` の active write 用 port seam
  - `infra/contracts.py` の `ActiveStateSnapshot`
- S07:
  - `application/contracts.py` の `SyncRequest`, `SyncStateResult`, `ActiveUpdateOutcome`, `ArtifactWriteFailure`, `SyncCommandResult`, `ArtifactWriteResult`
  - `application/ports.py` の sync slice に必要な write-side seam
  - `presentation/contracts.py` の `ArtifactBundle` と下位 artifact contract
  - `S06` の `commit_active_state()` を再利用する internal seam
- S08:
  - `application/contracts.py` の `CreateNodeRequest`, `CreatePlan`, `CreateNodeResult`
- S09:
  - `application/contracts.py` の `CreateDiscussionDocRequest`, `CreateDiscussionDocResult`
- S10:
  - `application/contracts.py` の `ImportNodeRequest`, `ImportNodeResult`
  - `load_active_manifest_no_migrate()` と `execute_create_plan()` を消費する reuse seam
- S11:
  - `commands/contracts.py`
  - `application/contracts.py` の `UseCases` facade
  - `cli/bootstrap.py` が組み立てる `application/ports.py` の bootstrap seam / Ports assembly
- ルール:
  - final-state interface 一覧は `design.md` を正本とする。
  - ただし実装導入は上記の最初の消費者 step で additive に行う。
  - 未消費の shell / facade / registry のために contract を前倒し導入しない。

## legacy shim matrix
| 旧 module | 中間段階の扱い | 正式移設先 | 削除/最終整理 step | rollback unit |
| --- | --- | --- | --- | --- |
| `ids.py` | wrapper 維持可 | `domain/ids.py` | `S13` | `S01/S03/S08` |
| `io_json.py` | wrapper 維持可 | `infra/json_store.py` | `S13` | `S04/S07` |
| `github.py` | wrapper 維持可 | `infra/github_cli.py` | `S13` | `S04/S08/S10` |
| `render_md.py` | wrapper 維持可 | `presentation/markdown.py` | `S13` | `S07` |
| `render_puml.py` | wrapper 維持可 | `presentation/puml.py` | `S13` | `S07` |
| `active.py` | thin delegation のみ許容 | `application/set_active.py`, `domain/active.py`, `infra/active_store.py` | `S13` | `S05/S06/S07` |
| `nodes.py` | thin delegation のみ許容 | `application/create_node.py`, `application/import_node.py`, `domain/*` | `S13` | `S08/S09/S10` |

## レビュー / QA ゲート方針
- RG1 step review:
  - timing:
    - 各 step の Green/Refactor 完了後
  - scope:
    - 当該 step の staged diff のみ
  - policy:
    - `1 step = 1 review scope = 1 commit scope`
    - 指摘修正も同じ scope に閉じる
    - 各 step で新しい direct cross-layer dependency を増やしていないことを diff review で確認する
- QG1 slice QA:
  - timing:
    - 各 step の review 前
  - scope:
    - 当該 step の focused test + 既存互換 smoke
  - policy:
    - failing test を先に 1 本ずつ追加する
    - Green は最小実装に留める
- SG1 final diff gate:
  - timing:
    - S99
  - scope:
    - `git diff origin/main...HEAD`
  - policy:
    - `spec_reviewer` による branch 全体レビューを pass させる

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` を正本とする。
- 互換参照は `Red -> Green -> Refactor -> review -> fix -> re-review -> report -> commit` とする。
- step は 1 つの観測可能な振る舞いを単位とする。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red -> Green -> Refactor` で閉じる。
- read-only / pure core を先に、write path を後に、shell と cleanup は最後に行う。
- docs impact は `S90` で必ず確認する。
- 最後に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- command shell のためだけの abstraction を先行実装しない。

## 実装ステップ

### S01 — ids / graph / validation の pure core を抽出する
- target:
  - `app.py`
  - `ids.py`
  - `domain/ids.py`
  - `domain/models.py`
  - `domain/tree.py`
  - `domain/validation.py`
  - 対応 pure test
- step boundary:
  - command / presentation / gh/git/json I/O は含めない
  - `app.py` の helper から pure な rule と dataclass を切り出すところまで
  - staged coexistence 中の delegation owner は `app.py` とし、この step の rollback unit も `app.py` を含む staged diff とする

#### B1 — ids and graph
- purpose:
  - 最小依存の pure core を最初に固定する

##### I1a — title / local id helpers
- Red:
  - `resolve_input_title_and_slug` / `normalize_local_id_input` pure test を 1 本追加
- Green:
  - `resolve_input_title_and_slug`, `normalize_local_id_input` を `domain/ids.py` へ移す
- Refactor:
  - `app.py` 側の title/local-id helper delegation を整理する

##### I1b — parse / format helpers
- Red:
  - `parse_id` / `format_id` pure test を 1 本追加
- Green:
  - `parse_id`, `format_id` を `domain/ids.py` へ移す
- Refactor:
  - parse/format helper の責務境界を整理する

##### I1c — deps sort helper
- Red:
  - `deps_node_sort_key` pure test を 1 本追加
- Green:
  - `deps_node_sort_key` を `domain/ids.py` へ移す
- Refactor:
  - deps sort helper の delegation を整理する

##### I2 — graph dataclasses
- Red:
  - `SpecNodeSeed -> SpecGraph` の pure test を 1 本追加
- Green:
  - `SpecNodeSeed`, `SpecNode`, `SpecGraph` を導入し、`build_graph()` を `domain/tree.py` へ切り出す
- Refactor:
  - `app.py` 内の node scan 後処理を mapper に整理する

##### I3 — validation rules
- Red:
  - structural validation pure test を 1 本追加
- Green:
  - `validate_graph()`, `validate_graph_and_deps()` を `domain/validation.py` へ切り出す
- Refactor:
  - validation helper 群の責務を `tree` と `validation` に分割する

#### step gate
- review:
  - pure core review
- expected tests:
  - ids pure tests
  - graph build pure tests
  - validation pure tests
  - legacy `ids.py` / `app.py` delegation smoke
  - `domain/*` no-I/O import assertion
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S02 — validate の use case core を作る
- target:
  - `app.py`
  - `application/validate_tree.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/contracts.py`
  - 最小 reader seam
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- step boundary:
  - 先に pure core を消費する最小 use case だけを導入する
  - command shell の一般化はまだしない
  - parser/help/dispatch ownership は `S11` へ defer し、この step では renderer/output compatibility と legacy delegated validate path だけを閉じる
  - 最小 reader seam の concrete owner は staged delegation 中の `app.py` とし、`infra/fs_repo.py` 正本化までは暫定 adapter を増やさない
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py -> validate_tree` seam を含む staged diff とする

#### B1 — validate core
- purpose:
  - 最初の consumer slice として shared contract を最小導入する

##### I1 — validate request/result
- Red:
  - `ValidateTreeRequest`, `ValidationResult` を使う use case test を 1 本追加
- Green:
  - `validate_tree(req, ports)` を導入し、最小 node reader seam を接続する
- Refactor:
  - mapper と ports boundary を整理する

##### I2 — validate text rendering
- Red:
  - validate CLI text regression を 1 本追加
- Green:
  - `render_validate_text()` を導入し、既存 CLI 文言互換を固定する
- Refactor:
  - stdout/stderr ownership を renderer 側に閉じる

#### step gate
- review:
  - validate core slice review
- expected tests:
  - validate use case tests
  - validate text regression
  - minimal reader seam tests
  - validate exit `0/1`
  - stdout/stderr split regression
  - legacy delegated validate smoke
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S03 — status / deps の pure core を抽出する
- target:
  - `domain/status.py`
  - `domain/deps.py`
  - `domain/models.py`
  - 対応 pure test
- step boundary:
  - status resolution / progress / deps evaluation の pure rule まで
  - command / renderer はまだつなげない
  - dependency topology の canonical source はこの step では導入しない
  - `domain/deps.py` は `SpecGraph` から dependency edge を compile せず、supplied `issue_depends_on_map` / `effective_deps_map` を受ける pure rule に限定する
  - この step は additive pure core のみで live consumer は導入しない。legacy path の切替は `S04` / `S06` で開始し、rollback unit は `S03` 単独 commit/staged diff とする

#### B1 — status and deps rules
- purpose:
  - `deps check`, `active set`, `sync` が共有する rule を先に固定する

##### I1 — issue status resolution
- Red:
  - issue status source selection pure test を 1 本追加
- Green:
  - `resolve_issue_statuses()`, `build_progress_map()` を導入する
- Refactor:
  - cached/github snapshot normalization を mapper に閉じる

##### I2a — readiness evaluation
- Red:
  - `evaluate_readiness()` pure test を 1 本追加
- Green:
  - `DepsEvaluation`, `evaluate_readiness(graph, issue_depends_on_map, ...)` を導入する
- Refactor:
  - closure / blockers / guard_reason を pure path に整理する

##### I2b — deps inspection decoration
- Red:
  - `inspect_target_deps()` pure test を 1 本追加
- Green:
  - `inspect_target_deps(graph, issue_depends_on_map, ...)` を導入する
- Refactor:
  - active issue decoration と view-facing state を整理する

##### I2c — deps state / cycle validation
- Red:
  - `build_deps_state()` pure test と deps cycle validation pure test を 1 本追加
- Green:
  - `build_effective_deps_map(graph, issue_depends_on_map)`, `build_deps_state()`, `validate_deps_cycles(issue_depends_on_map)` を導入する
- Refactor:
  - `effective_depends_on` / node-state assembly を `S04` と `S07` の共有 pure path に整理する

#### step gate
- review:
  - deps pure core review
- expected tests:
  - status pure tests
  - deps pure tests
  - deps state / cycle validation pure tests
  - shared readiness fixture regression
  - explicit `issue_depends_on_map` input regression
  - `active_issue_id` が `inspect_target_deps()` の decoration にのみ影響し、`evaluate_readiness()` の結果を変えない pure regression
  - `domain/status.py`, `domain/deps.py` no-I/O assertion
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S04 — deps check slice を組み立てる
- target:
  - `app.py`
  - `application/status_context.py`
  - `application/check_deps.py`
  - `application/validate_tree.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/contracts.py`
  - `infra/deps_reader.py`
  - `infra/derived_state_reader.py`
  - `infra/github_cli.py`
  - `infra/active_store.py`
  - `presentation/cli_text.py`
  - `presentation/json_state.py`
  - 対応 test
- step boundary:
  - primary user-facing scope は `deps check`
  - `active set` 再利用 seam はこの step で固定する
  - canonical dependency topology provider の first consumer はこの step とする
  - `validate_tree` は同じ topology provider へ internal reconnect するが、この step の primary user-facing review scope には含めない
  - parser/help/dispatch ownership は `S11` へ defer し、この step では `deps check` の use case/result/renderer と legacy delegated path だけを閉じる
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py -> check_deps` seam を含む staged diff とする

#### B1 — deps command core
- purpose:
  - 最初の read-side reusable seam を固定する

##### I1 — status context seam
- Red:
  - `status_context` use case test を 1 本追加
- Green:
  - `resolve_issue_status_context()` を導入し、github/cached 選択を ports に閉じる
- Refactor:
  - active issue context の扱いを state decoration 専用に整理する

##### I1b — deps topology seam
- Red:
  - `deps topology reader -> canonical issue_depends_on_map` test を 1 本追加
- Green:
  - `infra/deps_reader.py` と ports 経由の topology provider を導入する
  - `validate_tree()` を same topology provider に再接続する
- Refactor:
  - `deps.json` / shorthand / ref resolve の ownership を topology provider に閉じる

##### I2 — deps text path
- Red:
  - `deps check` text regression を 1 本追加
- Green:
  - `check_deps()` と text rendering をつなぐ
- Refactor:
  - `TargetRef` / target normalization を command-local boundary に整理する

##### I3 — deps json path
- Red:
  - `deps check --json` regression を 1 本追加
- Green:
  - JSON payload ownership を `presentation/json_state.py` に固定する
- Refactor:
  - raw dict は JSON boundary に限定する

#### step gate
- review:
  - deps command slice review
- expected tests:
  - deps use case/result regression
  - deps text/json renderer regression
  - status context tests
  - deps topology provider tests
  - validate topology reconnect regression
  - shared readiness seam contract regression
  - deps cycle fail-fast regression
  - deps exit code `0/3/1`
  - `--json` stdout-only regression
  - source selection regression
  - warnings/stderr order regression
  - target normalization boundary regression
  - legacy delegated deps smoke
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S05 — active show の read model を作る
- target:
  - `app.py`
  - `application/set_active.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/active_store.py`
  - `presentation/cli_text.py`
  - 対応 test
- step boundary:
  - `show_active()` のみ
  - write/rollback は含めない
  - `load_active_manifest_no_migrate()` はまだ使わず、read path は `load_active_manifest()` のみを consumer とする
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py -> show_active` seam を含む staged diff とする

#### B1 — active read
- purpose:
  - write path から独立した active read side を先に固定する

##### I1 — current manifest read model
- Red:
  - `agent.active -> ActiveViewResult` read model test を 1 本追加
- Green:
  - `load_active_manifest()` と `show_active()` の current-path を導入する
- Refactor:
  - `ActiveViewEntry` への mapping を整理する

##### I2 — legacy migration-capable loader
- Red:
  - `.work/active.json` / `.work/current.json` priority + no write-back regression を 1 本追加
- Green:
  - legacy fallback を `load_active_manifest()` に閉じる
- Refactor:
  - source/warnings ownership と read-time/in-memory normalization を固定する

##### I3 — active show rendering
- Red:
  - `active show` text rendering regression を 1 本追加
- Green:
  - `render_active_show_text()` を導入する
- Refactor:
  - source/warnings ownership を read result に揃える

#### step gate
- review:
  - active read slice review
- expected tests:
  - active show read/result regression
  - `active show` text/stdout/stderr/warnings compatibility regression
  - legacy manifest fixture matrix
  - `active show` zero-input / exit `0` regression
  - legacy source priority regression
  - read-time/in-memory normalization with no write-back
  - `load_active_manifest_no_migrate()` 非使用確認
  - legacy delegated active-show smoke
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S06 — active set/clear の write path を作る
- target:
  - `app.py`
  - `domain/active.py`
  - `domain/models.py`
  - `domain/tree.py`
  - `application/set_active.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `application/status_context.py`
  - `infra/active_store.py`
  - `infra/contracts.py`
  - `infra/git_cli.py`
  - `presentation/cli_text.py`
  - `presentation/json_state.py`
  - 対応 test
- step boundary:
  - `active set` / `active clear` の guard/order/rollback
  - sync auto-update は含めない
  - `pre-step7 failure` は rollback 対象外、`commit_active_state()` 内の step 7-9 failure のみ snapshot/restore 対象とする
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py -> set_active/clear_active` seam を含む staged diff とする

#### B1 — active write
- purpose:
  - 最初の高リスク write path を小さい iteration に分割して固定する

##### I1 — active selection + deps guard
- Red:
  - blocked/unknown/force regression を 1 本追加
- Green:
  - `select_active_chain()` と `S04` の topology provider を再利用した readiness guard を導入する
- Refactor:
  - shared readiness seam reuse を固定する
  - invalid/cyclic topology は readiness 判定より前に fail-fast する順序を固定する

##### I2 — branch decision / checkout pre-write
- Red:
  - branch policy failure regression を 1 本追加
- Green:
  - `resolve_branch_decision()` と manifest write 前 checkout を導入する
- Refactor:
  - pre-step7 failure ownership を明文化する

##### I3 — shared commit_active_state
- Red:
  - write-order regression を 1 本追加
- Green:
  - `commit_active_state()` を導入する
- Refactor:
  - context-pack render ownership を整理する

##### I4 — set command path
- Red:
  - `active set` success regression を 1 本追加
- Green:
  - `set_active()` の success path を閉じる
- Refactor:
  - stdout/stderr ownership を整理する

##### I5 — clear command path
- Red:
  - `active clear` placeholder regression を 1 本追加
- Green:
  - `clear_active()` の placeholder path を閉じる
- Refactor:
  - `patch_manifest=None` 契約を固定する

##### I6 — rollback injection
- Red:
  - rollback failure injection を 1 本追加
- Green:
  - snapshot/restore と dual-error reporting を実装する
- Refactor:
  - rollback reporting を整理する

#### step gate
- review:
  - active write slice review
- expected tests:
  - active set/clear use case regression
  - branch policy failure regression
  - managed agent state invalid JSON pre-step7 failure with no snapshot/rollback regression
  - no manifest write before guard success
  - shared readiness seam reuse regression
  - `commit_active_state` authoritative order regression
  - `active clear` zero-input / exit `0` / clear-text regression
  - `active clear` placeholder manifest/pointer/context-pack/agent-state clear regression
  - git rollback 非対象 regression
  - rollback injection
  - blocked/unknown/force-path regressions
  - renderer stdout/stderr/warnings regression
  - legacy delegated active-write smoke
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S07 — sync core を作る
- target:
  - `app.py`
  - `domain/active.py`
  - `application/sync_state.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/json_store.py`
  - `infra/artifact_writer.py`
  - `infra/clock.py`
  - `presentation/contracts.py`
  - `presentation/json_state.py`
  - `presentation/markdown.py`
  - `presentation/puml.py`
  - `presentation/cli_text.py`
  - 対応 test
- step boundary:
  - `sync` と artifact write のみ
  - create/import 再利用はまだ含めない
  - `S06` の `commit_active_state()` を再利用し、active 更新後 artifact 失敗は non-atomic だが観測可能な failure として扱う
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py -> sync` seam を含む staged diff とする

#### B1 — sync pipeline
- purpose:
  - state collection と artifact write を分離して固定する

##### I1 — collect_sync_state
- Red:
  - sync state collection regression を 1 本追加
- Green:
  - `collect_sync_state()` を導入する
- Refactor:
  - state result mapper を整理する

##### I2 — active auto-update
- Red:
  - active-before-artifact ordering regression を 1 本追加
- Green:
  - `infer_active_node_from_branch()` と `maybe_auto_update_from_branch()` を導入する
- Refactor:
  - `ActiveUpdateOutcome` を整理する

##### I3 — json artifacts
- Red:
  - sync JSON artifact regression を 1 本追加
- Green:
  - `index/tree/deps-issues.json` を固定する
- Refactor:
  - JSON bundle を整理する

##### I4 — markdown / puml artifacts
- Red:
  - markdown / puml artifact regression を 1 本追加
- Green:
  - `dashboard.md`, `tree*.puml`, `deps-issues.puml` を固定する
- Refactor:
  - render/write ownership を整理する

##### I5 — sync text/outcome
- Red:
  - `sync` text/outcome regression を 1 本追加
- Green:
  - `render_sync_text()` と `SyncCommandResult` を閉じる
- Refactor:
  - artifact failure reporting を整理する

#### step gate
- review:
  - sync slice review
- expected tests:
  - sync use case/result regression
  - sync deps cycle fail-fast regression
  - JSON artifact path/name/content snapshots
  - dashboard/tree PUML snapshots
  - deps-issues PUML / disabled placeholder regression
  - `sync --force` placeholder semantics regression
  - deps.valid=false / deps.error regression
  - active update after branch / before artifact regression
  - sync success/failure exit behavior regression
  - sync stderr/warnings ordering regression
  - non-atomic artifact failure with `failed_partial_or_stale` regression
  - artifact failure contract regression
  - renderer text regression
  - legacy delegated sync smoke
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S08 — new node core を作る
- target:
  - `app.py`
  - `application/create_node.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/template_scaffolder.py`
  - `infra/fs_repo.py`
  - `infra/github_cli.py`
  - `presentation/cli_text.py`
  - 対応 test
- step boundary:
  - `initiative|epic|issue` の create のみ
  - `new doc` と `import` はまだ含めない
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py -> create_node` seam を含む staged diff とする

#### B1 — create core
- purpose:
  - no-write preflight と planned write を core 側で固定する

##### I1 — planning
- Red:
  - create planning regression を 1 本追加
- Green:
  - `plan_node_creation()` と `CreatePlan` を導入する
- Refactor:
  - GitHub mode default を整理する

##### I2 — execution
- Red:
  - create execution regression を 1 本追加
- Green:
  - `execute_create_plan()` を導入する
- Refactor:
  - created_paths ordering を整理する

##### I3 — CLI contract
- Red:
  - create result/text regression を 1 本追加
- Green:
  - `CreateNodeResult` と text rendering を固定する
- Refactor:
  - collision fail-fast no-write を整理する

#### step gate
- review:
  - new node slice review
- expected tests:
  - planning regression
  - execution regression
  - full candidate-set no-write preflight regression
  - `copy_scaffolded_tree -> write_meta` order regression
  - `created_paths` ordering regression
  - collision/no-write regression
  - per-kind parity regression
  - GitHub mode default / no-side-effect matrix regression
  - `execute_create_plan()` reuse seam regression
  - renderer text regression
  - legacy delegated new smoke
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S09 — new doc core を作る
- target:
  - `app.py`
  - `application/create_node.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/template_scaffolder.py`
  - `presentation/cli_text.py`
  - 対応 test
- step boundary:
  - `new doc` のみ
  - node create core とは別枝に保つ
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py -> create_discussion_doc` seam を含む staged diff とする

#### B1 — discussion doc
- purpose:
  - shared sequence/path/template write 契約を独立に固定する

##### I1 — sequence / planning
- Red:
  - discussion sequence regression を 1 本追加
- Green:
  - `plan_discussion_doc()` を導入する
- Refactor:
  - nonconforming file ignore ルールを整理する

##### I2 — render / write
- Red:
  - new doc file generation regression を 1 本追加
- Green:
  - template load/render/write を導入する
- Refactor:
  - duplicate fail-fast no-write を整理する

##### I3 — CLI contract
- Red:
  - `new doc` result/text regression を 1 本追加
- Green:
  - `CreateDiscussionDocResult` と `render_new_doc_text()` を固定する
- Refactor:
  - duplicate / invalid-sequence failure message と warnings ownership を整理する

#### step gate
- review:
  - new doc slice review
- expected tests:
  - sequence regression
  - generated path/name/content regression
  - doc_type (`adr|disc|research|note`) parity / template selection regression
  - duplicate/no-write regression
  - new node non-regression for shared-file edits
  - invalid slug / duplicate sequence regression
  - renderer text regression
  - legacy delegated new-doc smoke
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S10 — import core を作る
- target:
  - `app.py`
  - `domain/tree.py`
  - `application/import_node.py`
  - `application/contracts.py`
  - `application/create_node.py`
  - `application/sync_state.py`
  - `infra/github_cli.py`
  - `infra/active_store.py`
  - `presentation/cli_text.py`
  - 対応 test
- step boundary:
  - `import` と `sync_after_import()` のみ
  - shell 一般化はまだしない
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py -> import_node` seam を含む staged diff とする

#### B1 — import flow
- purpose:
  - create core と sync core を再利用しながら `import -> sync` を固定する

##### I1 — parent fallback
- Red:
  - import parent fallback regression を 1 本追加
- Green:
  - `resolve_parent_from_active()` と `resolve_parent_for_import()` を導入する
- Refactor:
  - `load_active_manifest_no_migrate()` 専用利用を固定する

##### I2 — import preflight / duplicate no-write
- Red:
  - import duplicate / no-write regression を 1 本追加
- Green:
  - duplicate guard と no-write preflight を import flow に固定する
- Refactor:
  - preflight ownership と failure source を整理する

##### I3 — linked create reuse
- Red:
  - linked create reuse regression を 1 本追加
- Green:
  - `build_linked_create_request()` と create core 再利用を導入する
- Refactor:
  - graph load / collision planning の二重実行を排除する

##### I4 — post-import sync
- Red:
  - `import -> sync` regression を 1 本追加
- Green:
  - `sync_after_import()` を導入する
- Refactor:
  - `post_import_sync` ownership を固定する

#### step gate
- review:
  - import slice review
- expected tests:
  - parent fallback regression
  - duplicate/no-write regression
  - import then sync regression
  - import -> sync artifact path/name/content assertions
  - post-import sync negative-path regression
  - `load_active_manifest_no_migrate() -> ActiveSelection -> resolve_parent_from_active()` 鎖 regression
  - `execute_create_plan()` reuse seam regression
  - renderer text regression
  - legacy delegated import smoke
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S11 — commands / cli shell を正本化する
- target:
  - `commands/contracts.py`
  - `commands/*`
  - `application/contracts.py`
  - `application/ports.py`
  - `cli/parser.py`
  - `cli/registry.py`
  - `cli/bootstrap.py`
  - `cli/dispatch.py`
  - `app.py`
  - 対応 test
- step boundary:
  - use case 実装は増やさない
  - すでにある core を束ねる shell に限定する
  - staged coexistence 中の delegation owner は `app.py` とし、rollback unit は `app.py / cli/parser.py / cli/registry.py / cli/bootstrap.py / cli/dispatch.py / commands/* / commands/contracts.py / application/contracts.py / application/ports.py / presentation/contracts.py` を含む staged diff とする

#### B1 — shell integration
- purpose:
  - speculative abstraction を避けつつ、最後に shell を整理する

##### I1 — command wrappers
- Red:
  - command wrapper contract regression を 1 本追加
- Green:
  - `commands/*` を薄い request normalization + renderer selection 層として導入する
- Refactor:
  - command-local validation failure と business outcome の ownership を整理する

##### I2 — registry / bootstrap
- Red:
  - registry/bootstrap seam regression を 1 本追加
- Green:
  - 実需のある command だけで `registry` と `bootstrap` を導入する
- Refactor:
  - parser と registry の正本を 1 か所に揃える

##### I3 — dispatch thinness
- Red:
  - CLI dispatch ownership regression を 1 本追加
- Green:
  - `app.py` は parser 起動と dispatch 起動前後の最小責務に縮小する
- Refactor:
  - uncaught runtime / argparse / business exit ownership を整理する

#### step gate
- review:
  - shell integration review
- expected tests:
  - parser/help regression
  - argparse failure `2`
  - business exit ownership
  - representative command wrapper smoke
  - staged delegation path regression
  - rollback-ready wrapper swap smoke
  - `commands/* -> UseCases facade + application DTO + presentation renderer + commands/contracts only` structural checks
  - `commands/*` が `domain/*` / `infra/*` / 旧 `app.py` helper に直接依存しない structural checks
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S12 — test tree 分割を独立 review scope で完了する
- target:
  - `tests/test_cli.py`
  - `tests/test_init_update.py`
  - `tests/__init__.py`
  - `tests/cli_runtime/*`
  - `tests/cli_runtime/__init__.py`
  - `tests/domain_runtime/*`
  - `tests/domain_runtime/__init__.py`
  - `tests/presentation_runtime/*`
  - `tests/presentation_runtime/__init__.py`
- step boundary:
  - test file の physical split のみ
  - shell / core の分離が終わったあとに safety net を整理する
  - `unittest discover` は regular package (`__init__.py`) 方式を正本とし、`load_tests` は採用しない
  - semantic-no-change refactor とし、pure move / helper extraction / import path 修正以外の意味変更を持ち込まない

#### B1 — test tree split
- purpose:
  - reviewer が command ごとの失敗面を追える test tree を独立 scope で先に固定する

##### I1 — installer / wrapper split
- Red:
  - installer/wrapper discovery regression を 1 本追加
- Green:
  - `tests/test_init_update.py`, `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_wrappers.py`, 各 package `__init__.py` を導入する
- Refactor:
  - shared runtime harness import を整理する

##### I2 — command runtime split
- Red:
  - command runtime discovery regression を 1 本追加
- Green:
  - `tests/cli_runtime/test_new.py`, `test_active.py`, `test_sync.py`, `test_deps.py`, `test_import.py`, `test_validate.py` を分割する
- Refactor:
  - duplicated command fixtures を整理する

##### I3 — domain / presentation split
- Red:
  - pure test discovery regression を 1 本追加
- Green:
  - `tests/domain_runtime/*`, `tests/presentation_runtime/*` を分割する
- Refactor:
  - pure subtree 内 helper 境界を整理する

#### step gate
- review:
  - test tree split review
- expected tests:
  - `python -m unittest discover -v`
  - touched test modules
  - test module existence + command grouping assertions
  - regular package (`__init__.py`) discovery assertions
  - critical inventory still covered:
    - staged delegation path
    - active rollback failure-injection
    - import->sync regeneration
    - sync artifact path/name/content snapshots
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S13 — helper detachment と rollback basis 切替を完了する
- target:
  - `app.py`
  - `commands/*`
  - `application/*`
  - `ids.py`
  - `io_json.py`
  - `github.py`
  - `render_md.py`
  - `render_puml.py`
  - `active.py`
  - `nodes.py`
  - `tests/cli_runtime/*`
  - `tests/domain_runtime/*`
  - `tests/presentation_runtime/*`
  - 旧 helper call site 一式
- step boundary:
  - 旧 helper 直依存の解消のみ
  - user-facing behavior change は含めない
  - rollback basis は staged seam から `git revert / commit rollback` へこの step で切り替える

#### B1 — helper detachment and rollback transition
- purpose:
  - 段階移行で残した delegation を最後に除去し、rollback 根拠を commit 単位へ切り替える

##### I1 — final API call-site detachment
- Red:
  - final API call-site regression を 1 本追加
- Green:
  - 旧 helper 直依存を final layered API へ切り替える
- Refactor:
  - compatibility shim の縮小を整理する

##### I2 — legacy shim cleanup
- Red:
  - legacy shim import assertion regression を 1 本追加
- Green:
  - `ids.py`, `io_json.py`, `github.py`, `render_md.py`, `render_puml.py`, `active.py`, `nodes.py` を matrix どおり削除または thin wrapper 限定へ整理する
- Refactor:
  - layer direction assertions を整理する

#### step gate
- review:
  - helper detachment / rollback transition review
- expected tests:
  - `python -m unittest discover -v`
  - focused regressions:
    - `import -> sync`
    - `active set` guard/order
    - `deps check`
    - markdown/puml/json artifact contracts
  - final API call-site regression
  - `app.py` thin-entrypoint / no live wrapper / no bootstrap->app wiring structural check
  - legacy import prohibition / layer direction assertions:
    - `commands/* -> UseCases facade + presentation renderer`
    - `domain/*` no I/O import
    - `infra/*` only through ports
  - rollback basis transition evidence:
    - pre-switch rollback unit は staged seam であったこと
    - この step 完了後は `git revert / commit rollback` が唯一の rollback 基準であること
    - partial import rollback は対象外で rollback unit は commit 単位であること
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S90 — docs impact resolution / docs refresh
- target:
  - docs / assets / workflow / skill / none
- step boundary:
  - docs impact の確認と必要な refresh のみ
  - implementation scope の追加は行わない
  - docs impact が `none` でも no-op resolution step として必ず実行する

#### B1 — docs impact gate
- purpose:
  - docs impact を no-op か更新かで閉じる

##### I1 — docs impact detect
- Red:
  - docs impact checklist regression
- Green:
  - changed assets/workflow/docs を棚卸しし `docs / assets / workflow / skill / none` を判定する
  - actual touched doc paths list を記録する
- Refactor:
  - docs impact checklist を整理する

##### I2 — docs refresh or no-op record
- Red:
  - docs resolution record regression
- Green:
  - 必要更新または no-op 理由を `report.md` へ残す
- Refactor:
  - docs refresh note を整理する

#### step gate
- review:
  - docs impact review
- expected checks:
  - docs impact checklist:
    - `docs / assets / workflow / skill / none` の判定根拠
    - docs refresh が必要な場合は対象パスと理由
    - no-op の場合は no-op 理由
  - plan/design/requirement との整合
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S14 — relative path canonical regression を修正する
- target:
  - `application/set_active.py`
  - `infra/active_store.py`
  - `presentation/json_state.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_sync.py`
  - 追加の focused regression tests
- step boundary:
  - `active.json` と state artifact の path canonical を repo-relative へ戻す
  - absolute path persistence/artifact regression の修正に限定する
  - user-facing command 名や exit code の変更は含めない

#### B1 — repo-relative canonicalization
- purpose:
  - portability / stable diff / repo move durability の回帰を閉じる

##### I1 — active manifest canonical path
- Red:
  - `active.json` path durability regression を 1 本追加
- Green:
  - `build_active_manifest()` が repo-relative path を canonical として書く
  - `active_store` の read/write path が repo-relative 正本と整合する
  - 既存の legacy absolute-path `active.json` は best-effort 互換で読める
- Refactor:
  - active path normalization helper を整理する

##### I2 — state artifact canonical path
- Red:
  - `index*.json` / `tree*.json` path portability regression を 1 本追加
- Green:
  - `presentation/json_state.py` が node `path` を `spec-dock/...` 形式で出力する
  - absolute host path が artifact に漏れないことを固定する
- Refactor:
  - relative path helper / mapper の重複を整理する

#### step gate
- review:
  - relative path regression review
- expected tests:
  - focused regressions:
    - `active.json` path is repo-relative
    - legacy absolute-path `active.json` remains readable
    - `index-all.json` / `index.json` / `tree-all.json` / `tree.json` node paths are repo-relative
    - repo move / workspace rename durability smoke または同等の portability regression
  - `python -m unittest discover -v`
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S99 — final diff review quality gate
- target:
  - branch diff
  - final gate evidence
  - `spec-deps/current/report.md`
- branch diff scope:
  - `git diff origin/main...HEAD`
- step boundary:
  - review-only step とする
  - blocking finding が出た場合は元 step に差し戻す
  - `S99` 自体では新規設計や scope 拡張を入れない

#### B1 — final validation
- purpose:
  - branch 全体の品質と trace を閉じる

##### I1 — full validation sweep
- Red:
  - final validation checklist regression
- Green:
  - `python -m unittest discover -v`
  - requirement/design/plan との trace check
  - runtime packaging / shipped asset check
  - lowercase path 増分なし確認: `rg --files | rg '[A-Z]'`
  - fresh repo smoke check:
    - `validate`
    - `deps check --json`
    - `active show`
    - `active set`
    - `sync --force`
    - `new issue`
    - `import issue`
- Refactor:
  - final validation checklist を整理する

##### I2 — architecture/spec gate
- Red:
  - architecture/spec gate regression
- Green:
  - `spec_reviewer` pass
  - branch diff review の blocking finding 0 件
  - staged delegation history / rollback basis transition evidence 完了
  - `app.py` live thinness check
  - command thinness check
  - layer violation check
  - DTO / contract check
  - touched file / AC-EC trace check:
    - `AC-001`: runtime package tree / `app.py` live thin entrypoint / `commands|application|domain|infra|presentation` の物理導入
    - `AC-002`: shared rule / workflow / side effect / rendering の責務分離
    - `AC-003`: `tests/test_init_update.py`, `tests/cli_runtime/*`, `tests/domain_runtime/*`, `tests/presentation_runtime/*` の分割差分
    - `AC-004`: `sync --force`, `deps check`, `active set`, `import -> sync`, scaffold collision no-write の回帰 test 群
    - `AC-005`: `python -m unittest discover -v` green
    - `EC-001`: staged delegation history / rollback basis transition evidence
    - `EC-002`: import 後のみ `sync_after_import()` 起動
    - `EC-003`: deps readiness / active guard/order
    - `EC-004`: JSON/Markdown/PUML artifact path/name/content 契約
- Refactor:
  - final gate report を整理する
- report update:
  - `spec-deps/current/report.md`

## final exit contract
- AC/EC 達成:
  - S01-S14, S90, S99 完了後に requirement の AC/EC をすべて満たす
- docs impact resolved:
  - `none` または必要更新反映済み
- rollback basis transitioned:
  - staged seam から `git revert / commit rollback` へ切り替わっている
- final diff approved:
  - `spec_reviewer` pass
  - branch diff review の blocking finding 0 件
