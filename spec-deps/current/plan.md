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

# issue-25 巨大な app.py を複数 module に分割し tests/test_cli.py を領域別に再編する — 実装計画（TDD: Red → Green → Refactor）

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
- 制約:
  - CLI 契約、artifact 契約、exit code 契約を維持する
  - `commands -> application -> domain/ports -> infra/presentation` の依存方向を崩さない
  - `1 step = 1 review scope = 1 git commit scope` を原則とする
  - 最終ゲートは `git diff origin/main...HEAD` を対象に branch 全体を spec review する

## マイルストーン一覧
- M1 CLI foundation:
  - 対象:
    - `cli/parser.py`
    - `cli/registry.py`
    - `cli/bootstrap.py`
    - `cli/dispatch.py`
    - `commands/contracts.py`
    - `application/contracts.py`
    - `application/ports.py`
    - `presentation/contracts.py`
    - `commands/*` thin wrapper
    - `tests/cli_runtime/harness.py`
    - `tests/cli_runtime/test_wrappers.py`
  - exit:
    - `app.py` から parser/bootstrap/dispatch へ委譲できる
    - 旧 helper を thin delegation で呼べる
    - help/exit ownership が維持される
- M2 read-side shared core:
  - 対象:
    - `domain/models.py`
    - `domain/tree.py`
    - `domain/status.py`
    - `domain/deps.py`
    - `domain/validation.py`
    - `application/status_context.py`
    - `application/check_deps.py`
    - `application/validate_tree.py`
    - `application/contracts.py`
    - `application/ports.py`
    - `infra/derived_state_reader.py`
    - `infra/json_store.py`
    - `presentation/cli_text.py`
    - `presentation/json_state.py`
    - `presentation/contracts.py`
    - 対応 renderer/test
  - exit:
    - `validate` と `deps check` が新 layered path で green
    - readiness / validation の shared rule が pure 化される
- M3 active/sync core:
  - 対象:
    - `application/set_active.py`
    - `application/sync_state.py`
    - `application/contracts.py`
    - `application/ports.py`
    - `infra/active_store.py`
    - `infra/artifact_writer.py`
    - `infra/fs_repo.py`
    - `infra/git_cli.py`
    - `infra/clock.py`
    - `presentation/json_state.py`
    - `presentation/markdown.py`
    - `presentation/cli_text.py`
    - `presentation/contracts.py`
    - 対応 command/test
  - exit:
    - `active show`、`active set/clear`、`sync` がそれぞれ独立 slice として green
    - rollback / active-update / artifact write 契約が維持される
- M4 create/import core:
  - 対象:
    - `application/create_node.py`
    - `application/import_node.py`
    - `application/contracts.py`
    - `application/ports.py`
    - `infra/template_scaffolder.py`
    - `infra/github_cli.py`
    - `presentation/contracts.py`
    - `presentation/cli_text.py`
    - 対応 command/test
  - exit:
    - `new node`、`new doc`、`import` が独立 slice として green
    - `import -> sync` 契約が維持される
- M5 cleanup/finalization:
  - 対象:
    - `tests/test_cli.py` 分割
    - `tests/test_init_update.py`
    - `tests/cli_runtime/*`
    - `tests/domain_runtime/*`
    - `tests/presentation_runtime/*`
    - 旧 helper 直依存の段階解消
    - docs impact 判定
    - final diff review
  - exit:
    - test tree 分割と旧 helper detachment が別 review scope で完了する
    - full suite green
    - branch 全体の spec review が pass

## ステップ一覧
- 注記:
  - ここでの `requirement trace` は step が当該 AC/EC の観測点へ寄与することを示す
  - AC/EC の達成完了判定は `S99 final diff review quality gate` と `## final exit contract` を正本とする
- S01:
  - 観測可能な振る舞い:
    - parser/registry/bootstrap/dispatch と command wrapper が導入されても、CLI help と exit ownership が維持される
  - requirement trace:
    - AC-001
    - EC-001
  - review gate:
    - CLI foundation diff review
- S02:
  - 観測可能な振る舞い:
    - `validate` が新 layered path で動作し、構造/deps validation を維持する
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
  - review gate:
    - validate slice review
- S03:
  - 観測可能な振る舞い:
    - `deps check` が新 layered path で動作し、text/json/exit code/readiness 契約を維持する
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-003
  - review gate:
    - deps slice review
- S04:
  - 観測可能な振る舞い:
    - `active show` が新 layered path で動作し、current CLI 表示契約を維持する
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
  - closure observation points:
    - `active show` read-side layering
    - `active show` CLI contract
  - review gate:
    - active show slice review
- S05:
  - 観測可能な振る舞い:
    - `active set/clear` が新 layered path で動作し、guard/order/rollback 契約を維持する
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-003
  - closure observation points:
    - `active set/clear` write-side layering
    - `active set/clear` CLI + rollback contract
  - review gate:
    - active write slice review
- S06:
  - 観測可能な振る舞い:
    - `sync` が新 layered path で動作し、`sync --force` と artifact 契約を維持する
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-004
  - review gate:
    - sync slice review
- S07:
  - 観測可能な振る舞い:
    - `new initiative|epic|issue` が新 layered path で動作し、scaffold collision fail-fast no-write を維持する
  - requirement trace:
    - AC-001
    - AC-004
  - closure observation points:
    - `new node` live layered path
    - `new node` CLI + generated artifact contract
  - review gate:
    - new node slice review
- S08:
  - 観測可能な振る舞い:
    - `new doc` が新 layered path で動作し、discussion sequence/path/template write 契約を維持する
  - requirement trace:
    - AC-001
    - AC-004
  - closure observation points:
    - `new doc` live layered path
    - `new doc` CLI + generated file contract
  - review gate:
    - new doc slice review
- S09:
  - 観測可能な振る舞い:
    - `import initiative|epic|issue` が新 layered path で動作し、`import -> sync` 契約を維持する
  - requirement trace:
    - AC-001
    - AC-002
    - AC-004
    - EC-002
  - review gate:
    - import slice review
- S10:
  - 観測可能な振る舞い:
    - test tree が `tests/test_init_update.py`, `tests/cli_runtime`, `tests/domain_runtime`, `tests/presentation_runtime` へ分割される
  - requirement trace:
    - AC-003
    - AC-005
  - closure observation points:
    - test tree physical split
    - critical contract tests remain discoverable
  - review gate:
    - test tree split review
- S11:
  - 観測可能な振る舞い:
    - 旧 helper 直依存が解消され、layered entrypoint 経由へ統一される
  - requirement trace:
    - AC-005
  - review gate:
    - old helper detachment review

## 要件 ↔ ステップ対応
- AC-001 -> S01, S02, S03, S04, S05, S06, S07, S08, S09, S11, S99
- AC-002 -> S02, S03, S04, S05, S06, S09
- AC-003 -> S10
- AC-004 -> S02, S03, S04, S05, S06, S07, S08, S09
- AC-005 -> S10, S11, S99
- EC-001 -> S01
- EC-002 -> S09
- EC-003 -> S03, S05
- EC-004 -> S06

## レビュー / QA ゲート方針
- RG1 step review:
  - timing:
    - 各 S01-S11 の Green/Refactor 完了後
  - scope:
    - 当該 step の staged diff のみ
  - policy:
    - `1 step = 1 review scope = 1 commit scope`
    - 指摘修正も同じ step scope に閉じる
- QG1 slice QA:
  - timing:
    - 各 S01-S11 の review 前
  - scope:
    - その step が触る unit/integration test と既存互換 test の最小集合
  - policy:
    - failing test を先に 1 本以上追加し、Green は最小実装に留める
- SG1 final diff gate:
  - timing:
    - S99
  - scope:
    - `git diff origin/main...HEAD` の branch 全差分
  - policy:
    - `spec_reviewer` による branch 全体レビューを pass させる
    - reviewer の blocking finding が 1 件でもあれば修正→再レビューを繰り返す

## 実行ルール（全ステップ共通）
- plan 全体は実装着手前に承認する。
- cadence / approval policy は `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` を正本とする。
- 互換参照: `Red → Green → Refactor → review → fix → re-review → report → commit/no-op`
- 各 step は 1 つの観測可能な振る舞いを単位とする。
- `block` は optional concern group。単純な step では最小 wrapper 1 個でよい。
- `iteration` は 1 回の TDD cycle とし、各 iteration は `Red → Green → Refactor` で閉じる。
- failing test は iteration ごとに 1 本ずつ進める。
- `Green` は最小実装、`Refactor` は green 維持を前提とする。
- `S90` は必ず実行する。docs impact が `none` の場合も no-op resolution step として review/report まで閉じる。
- 最後に `git diff origin/main...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- step review の対象と git commit の対象は一致させる。
- shared helper は単独コミットにせず、最初の消費者 slice と同じ commit に入れる。
- read-only flow を先に、write-path を後に、旧 helper の削除は最後に行う。
- `S90` は docs-only no-op を許容するが、独立 review scope を維持するため docs change の有無にかかわらず 1 commit で閉じる。
- shared contract / stored-shape は final-state interface 一覧を `design.md` で固定しつつ、実装導入は最初の消費者 step で additive に行う。
- 導入順の正本:
  - `S01`: facade/wiring に必要な最小 contract shell
  - `S02`: `SpecNodeSeed` / `SpecNode` / `SpecGraph` / `ValidationReport` / `StoredMetaRecord`
  - `S03`: `domain/ids.py` の canonical helper と `IssueSnapshot` / `IssueStatusSnapshot` / `Deps*` / `StoredIssueSnapshot`
  - `S04-S05`: `ActiveSelection` / `ActiveManifest*` / `ActiveStateSnapshot`
  - `S06`: `SyncRequest` / `SyncStateResult` / `ActiveUpdateOutcome` / `ArtifactWriteFailure` / `SyncCommandResult` / `ArtifactWriteResult` / `ArtifactBundle` とその下位 artifact contract
  - `S07-S08`: `CreateNodeRequest` / `CreatePlan` / `CreateNodeResult` / `CreateDiscussionDocRequest` / `CreateDiscussionDocResult`
  - `S09`: `ImportNodeRequest` / `ImportNodeResult`
- 後続 step の shared contract を先行 step で final 形のまま固定しない。

## legacy shim matrix
| 旧 module | 中間段階の扱い | 正式移設先 | 削除/最終整理 step | rollback unit |
| --- | --- | --- | --- | --- |
| `ids.py` | wrapper 維持可 | `domain/ids.py` | `S11` | `S03/S05/S07` |
| `io_json.py` | wrapper 維持可 | `infra/json_store.py` | `S11` | `S03/S06` |
| `github.py` | wrapper 維持可 | `infra/github_cli.py` | `S11` | `S03/S07/S09` |
| `render_md.py` | wrapper 維持可 | `presentation/markdown.py` | `S11` | `S06` |
| `render_puml.py` | wrapper 維持可 | `presentation/puml.py` | `S11` | `S06` |
| `active.py` | thin delegation のみ許容 | `application/set_active.py`, `domain/active.py`, `infra/active_store.py` | `S11` | `S04-S06` |
| `nodes.py` | thin delegation のみ許容 | `application/create_node.py`, `application/import_node.py`, `domain/*` | `S11` | `S07-S09` |

## 実装ステップ

### S01 — CLI foundation を導入し、旧 helper への thin delegation を残したまま新入口を固定する
- target:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/*`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/*`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/contracts.py`
- design refs:
  - [design.md](/srv/mount/spec-dock/spec-deps/current/design.md)
- step boundary:
  - parser/registry/bootstrap/dispatch/wrapper 導入まで
  - `application/domain/infra/presentation` の本実装はまだ temporary shim 経由の旧 helper delegation を許容
  - `commands/*` は stage-1 として bootstrap 済み `UseCases` facade のみを受け取り、旧 `app.py` helper を直接呼ばない
  - wrapper は top-level command 入口の到達性 smoke までをこの step に含める
  - `application/contracts.py` / `application/ports.py` / `presentation/contracts.py` は facade/wiring に必要な最小 shell だけを導入し、後続 step の final DTO 一覧をこの step では固定しない

#### update_plan（着手時に登録）
- [ ] 調査/Red/Green/Refactor/レビュー/報告/コミットの作業単位を登録する

#### B1 — parser/bootstrap/dispatch
- purpose:
  - CLI wiring を rollback 可能な 1 単位で固定する
- files:
  - `app.py`
  - `cli/parser.py`
  - `cli/registry.py`
  - `cli/bootstrap.py`
  - `cli/dispatch.py`
  - `commands/contracts.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `presentation/contracts.py`

##### I1 — parser/help contract
- slice goal:
  - help/argparse/exit ownership が維持されたまま新 parser へ通る

###### Red
- failing test:
  - parser/help tree regression test
- expected failure:
  - 新 parser 未導入で help tree と exit code が一致しない

###### Green
- minimum implementation:
  - `cli/parser.py` を導入する
  - `app.py` から parser 作成を委譲する
- pass condition:
  - help text と argparse failure=2 が維持される

###### Refactor
- cleanup target:
  - `app.py` の argparse 定義の縮小
- invariants to keep green:
  - help text
  - argparse failure=2

##### I2 — bootstrap/dispatch contract
- slice goal:
  - command dispatch と business exit ownership が新 dispatch へ通る

###### Red
- failing test:
  - representative dispatch smoke test
- expected failure:
  - bootstrap/dispatch 未導入で command run が新入口を通らない

###### Green
- minimum implementation:
  - `cli/registry.py`, `cli/bootstrap.py`, `cli/dispatch.py` を導入する
  - `commands/*` は bootstrap 済み `UseCases` facade を呼ぶ thin wrapper に留める
- pass condition:
  - dispatch と business exit code の既存契約が維持される
  - `commands/*` は bootstrap 済み `UseCases` facade だけを見る

###### Refactor
- cleanup target:
  - `app.py` の dispatch 分岐の縮小
- invariants to keep green:
  - business exit code
  - wrapper は thin delegation のまま
  - temporary shim のみが旧 helper を内部利用できる

##### I3 — wrapper harness
- slice goal:
  - top-level command wrapper の到達性を暫定 smoke で観測できる

###### Red
- failing test:
  - wrapper smoke regression in existing test surface
- expected failure:
  - wrapper smoke が既存 test surface で観測できない

###### Green
- minimum implementation:
  - `tests/test_cli.py` 内の暫定 smoke を使って `new/import/active/sync/deps/validate` wrapper 到達性を固定する
- pass condition:
  - 各 wrapper が bootstrap 済み `UseCases` facade を呼べる

###### Refactor
- cleanup target:
  - wrapper smoke の暫定 helper
- invariants to keep green:
  - `app.py` に command 実装本体を戻さない
  - `commands/*` に direct fs/git/gh/render 実装を持ち込まない

#### step gate
- review:
  - CLI foundation diff review
- expected tests:
  - parser/help regression
  - argparse failure=2 regression
  - business exit ownership regression
  - staged delegation path tests:
    - `commands/* -> UseCases facade`
    - legacy helper access is shim-in-facade only
    - representative shim-delegation smoke
  - stdout/stderr/warnings order smoke:
    - success stdout owner
    - warnings final emission owner
    - uncaught runtime failure owner
  - entrypoint-level failure -> exit `1` smoke
  - top-level wrapper smoke:
    - `new`
    - `import`
    - `active`
    - `sync`
    - `deps`
    - `validate`
- structural checks:
  - `app.py` は新規 workflow を増やさず、stage-1 では legacy helper body が rollback 用に残っていてよいことを diff review で確認
  - `commands/*` は S01 では bootstrap 済み `UseCases` facade への thin delegation のみを許容し、独自 orchestration を持たないことを diff review で確認
  - old helper への委譲は `UseCases` facade 内 temporary shim に閉じ、`cli/bootstrap.py` は wiring のみ、`commands/*` からの direct call を持ち込まないことを diff review で確認
  - rollback unit は `app.py / cli/parser.py / cli/registry.py / cli/bootstrap.py / cli/dispatch.py / commands/* / commands/contracts.py / application/contracts.py / application/ports.py / presentation/contracts.py` 一式であることを report と diff review で確認
  - `--help => 0`, `argparse failure => 2`, `business outcome => commands`, `uncaught runtime => dispatch`, `warnings final emission => dispatch` の owner を diff review と report で確認
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit
  - 例: `refactor(cli): parser/bootstrap/dispatch を導入`

### S02 — `validate` vertical slice を新 layered path へ移す
- target:
  - `commands/validate.py`
  - `application/validate_tree.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `domain/models.py`
  - `domain/tree.py`
  - `domain/validation.py`
  - `infra/contracts.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `validate_tree`
  - `validate_graph_and_deps`
- step boundary:
  - `validate` のみ
  - `deps check` や `sync` の共通 helper はまだ巻き込まない
  - shared contract file は `validate` に必要な最小 additive edit のみ許容する
  - shared DTO / stored-shape の初回導入責務は `validate` が最初に消費するものに限定し、`SpecNodeSeed`, `SpecNode`, `SpecGraph`, `ValidationReport`, `StoredMetaRecord` の正本 module をここで固定する
  - `ActiveManifest*` / `ActiveStateSnapshot` / `StoredIssueSnapshot` はこの step では final 固定しない
  - 許容する additive edit は `ValidateTreeRequest`, `ValidationResult`, `CliText` 接続と validate 専用 shared DTO / stored-shape 導入に必要な範囲へ限定する

#### B1 — validate path
- purpose:
  - 最小の read-only vertical slice で layered path を実証する

##### I1 — domain validation core
- slice goal:
  - structural/deps validation rule を pure domain/application へ切り出す

###### Red
- failing test:
  - structural validation unit test
- expected failure:
  - rule がまだ `app.py` / 旧 helper に残っている

###### Green
- minimum implementation:
  - `domain/tree.py`
  - `domain/validation.py`
  - `application/validate_tree.py`
- pass condition:
  - validation rule が pure path で評価できる

###### Refactor
- cleanup target:
  - validation helper の pure 化
- invariants to keep green:
  - checked node count
  - `domain` は `subprocess` `git` `gh` `Path.write_text` `print` に依存しない

##### I2 — validate command + renderer
- slice goal:
  - `validate` が `commands -> application -> domain -> presentation` で通る

###### Red
- failing test:
  - `validate` CLI regression
- expected failure:
  - command と renderer が新 path に接続されていない

###### Green
- minimum implementation:
  - `commands/validate.py`
  - `render_validate_text(result)`
  - command request/result 接続
- pass condition:
  - 構造/deps validation の既存挙動が CLI から維持される
  - `commands/validate.py` は request normalization のみ、workflow 本体は `application/validate_tree.py`、text ownership は `presentation/cli_text.py` に留まる

###### Refactor
- cleanup target:
  - validate request normalization
- invariants to keep green:
  - error message semantics
  - stdout/stderr ownership

#### step gate
- review:
  - validate slice review
- expected tests:
  - validate regression
  - domain validation unit tests
  - domain no-I/O / import dependency assertions
  - validate exit code `0/1`
  - validate stdout/stderr split regression
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S03 — `deps check` vertical slice を新 layered path へ移す
- target:
  - `application/status_context.py`
  - `commands/deps.py`
  - `application/check_deps.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `domain/models.py`
  - `domain/ids.py`
  - `domain/status.py`
  - `domain/deps.py`
  - `infra/contracts.py`
  - `infra/github_cli.py`
  - `infra/derived_state_reader.py`
  - `infra/active_store.py`
  - `presentation/json_state.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `resolve_issue_status_context`
  - `resolve_issue_statuses`
  - `build_progress_map`
  - `inspect_target_deps`
  - `DepsCheckResult`
- step boundary:
  - `deps check` text/json/exit code/readiness
  - `active set` guard での再利用は次 step で消費する
  - `EC-004` のうち artifact path/name を伴う Markdown/PUML/JSON rendering ownership は `S06` で閉じる

#### B1 — deps readiness
- purpose:
  - shared readiness path を先に固定する

##### I1 — shared readiness inputs
- slice goal:
  - status context と active context の入力を use case へ集約する

###### Red
- failing test:
  - deps readiness input unit test
- expected failure:
  - issue status source selection と active manifest 読取が旧 helper 依存のまま

###### Green
- minimum implementation:
  - `application/status_context.py`
  - `domain/status.py`
  - `infra/github_cli.py`
  - `infra/derived_state_reader.py`
  - `infra/active_store.py`
  - `check_deps(req)` の入力 wiring
- pass condition:
  - readiness 入力が ports 経由で self-contained に解決できる
  - `status_context` / `check_deps` / `domain.deps` の seam 契約が `S05` 再利用可能な形で固定される

###### Refactor
- cleanup target:
  - status snapshot mapper
- invariants to keep green:
  - github/cached の source selection
  - active issue context の受け渡し
  - `domain/status.py` は no-I/O を維持する
  - `domain/deps.py` は no-I/O を維持する

##### I2 — deps text path
- slice goal:
  - `deps check` text 出力と exit code を維持する

###### Red
- failing test:
  - `deps check` text regression
- expected failure:
  - text renderer と command wiring が新 path に繋がっていない

###### Green
- minimum implementation:
  - `commands/deps.py`
  - `presentation/cli_text.py`
  - text command outcome 接続
- pass condition:
  - readiness / blockers / exit code が CLI text で維持される

###### Refactor
- cleanup target:
  - deps target inspection DTO
- invariants to keep green:
  - `0/3/1` exit code
  - stderr/warnings order

##### I3 — deps json path
- slice goal:
  - `deps check --json` の payload ownership を固定する

###### Red
- failing test:
  - `deps check --json` payload regression
- expected failure:
  - json renderer ownership が未固定

###### Green
- minimum implementation:
  - `presentation/json_state.py`
  - json output wiring
- pass condition:
  - json payload shape が既存契約どおり

###### Refactor
- cleanup target:
  - JSON boundary だけに raw dict を閉じ込める
- invariants to keep green:
  - json payload shape
  - dataclass -> json boundary のみ raw dict 許容

#### step gate
- review:
  - deps slice review
- expected tests:
  - deps text/json regression
  - domain status unit tests
  - domain deps unit tests
  - domain no-I/O / import dependency assertions
  - target normalization regression
  - business exit code `0/3/1`
  - `--json` stdout-only regression
  - stderr/warnings order regression
  - source selection regression
  - shared readiness seam contract regression
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S04 — `active show` vertical slice を新 layered path へ移す
- target:
  - `commands/active.py`
  - `application/set_active.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `domain/models.py`
  - `infra/contracts.py`
  - `infra/active_store.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `show_active`
  - `ActiveViewEntry`
- step boundary:
  - `active show` のみ
  - `clear_active` / `set_active` の transaction/rollback は次 step
  - loader は migration-capable な `load_active_manifest()` を使い、`load_active_manifest_no_migrate()` は S09 専用とする
  - S04 が受け入れる legacy manifest input は `.work/active.json` と `.work/current.json` の 2 系統に限定する
  - 競合時優先順位は `spec-dock/.agent/active.json` > `.work/active.json` > `.work/current.json` に固定する
  - S04 で shared module を編集する場合も write/rollback path の意味変更は行わない

#### B1 — active read
- purpose:
  - read-side を write transaction から切り離して review 可能にする

##### I1 — active manifest read model
- slice goal:
  - manifest entry を `ActiveViewEntry` へ正規化する read model を固める

###### Red
- failing test:
  - active read-model unit test
- expected failure:
  - manifest/path 正規化が旧 helper 依存のまま

###### Green
- minimum implementation:
  - `show_active(req)` の read-model 部分
  - `infra/active_store.py::load_active_manifest()` から manifest を読む
- pass condition:
  - `initiative/epic/issue/source/warnings` を含む `ActiveViewResult` が安定して返る
  - legacy manifest を読む場合も `load_active_manifest()` 側の migration-capable semantics で current state へ正規化される
  - migration は read-time/in-memory 正規化に留まり、write-back は行わず、`id/path/source/warnings` の current CLI 観測点が維持される
  - `source` は `agent.active | legacy.work.active | legacy.work.current | none` のいずれかで固定される
  - 競合時の `source` 優先順位は `agent.active` > `legacy.work.active` > `legacy.work.current` に固定される

###### Refactor
- cleanup target:
  - active manifest normalization
- invariants to keep green:
  - active show は current CLI 表示契約を壊さない

##### I2 — active show command
- slice goal:
  - current CLI の表示契約を新 path で維持する

###### Red
- failing test:
  - `active show`
- expected failure:
  - command と text renderer が新 path に接続されていない

###### Green
- minimum implementation:
  - `commands/active.py::run_show`
  - `render_active_show_text`
- pass condition:
  - `active show` が current CLI 表示契約で通る
  - `ShowActiveRequest()` zero-input normalization、help/argparse、exit code `0`、stdout/stderr/warnings order が既存契約で通る
  - manifest absent では `not set` 単独行、manifest present では `initiative|epic|issue` 3 行、partial 欠損は `(none)` 表示で固定される

###### Refactor
- cleanup target:
  - show request normalization
- invariants to keep green:
  - `id/path` 表示契約
  - stdout ownership

#### step gate
- review:
  - active show slice review
- expected tests:
  - active show regression
  - application stubbed-port test
  - active set/clear non-regression smoke for shared-module edits
  - zero-input normalization regression
  - help/argparse regression
  - exit code `0`
  - stdout/stderr/warnings order regression
  - migration-capable loader regression:
    - supported legacy inputs は `.work/active.json` と `.work/current.json`
    - legacy manifest を read-time/in-memory で current state へ正規化する
    - write-back しない
    - `id/path/source/warnings` の観測結果が current CLI 契約に一致する
    - fixture matrix:
      - current manifest
      - legacy `.work/active.json`
      - legacy `.work/current.json`
      - manifest absent
      - conflict priority:
        - current + legacy coexist
        - legacy active + legacy current coexist
- structural checks:
  - `commands/active.py::run_show` は request normalization / renderer selection / `CommandOutcome` 生成に限定し、direct fs/json side effect を持たないことを diff review で確認
  - read orchestration は `application/set_active.py::show_active()` に集約され、manifest read は `infra/active_store.py`、text ownership は `presentation/cli_text.py` が正本であることを diff review で確認
  - `show_active()` は migration-capable `load_active_manifest()` のみを利用し、`load_active_manifest_no_migrate()` を S04 から呼ばないことを diff review か port-level test で確認
  - shared module 編集は `show_active` read path に限定し、`set_active` / `clear_active` の write/rollback 契約へ意味変更を持ち込まないことを diff review で確認
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S05 — `active set/clear` vertical slice を新 layered path へ移す
- target:
  - `commands/active.py`
  - `application/set_active.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `domain/models.py`
  - `infra/active_store.py`
  - `infra/fs_repo.py`
  - `infra/json_store.py`
  - `infra/git_cli.py`
  - `infra/clock.py`
  - `infra/contracts.py`
  - `domain/active.py`
  - `domain/ids.py`
  - `presentation/cli_text.py`
  - `presentation/json_state.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `set_active`
  - `clear_active`
  - `commit_active_state`
- step boundary:
  - `active set` と `active clear` の guard/order/rollback
  - `sync` の active auto-update は次 step

#### B1 — active transaction
- purpose:
  - rollback を含む最重要 write-path を isolated review 可能にする

##### I1 — deps guard + branch decision
- slice goal:
  - `set_active` の guard と branch decision を command から分離する

###### Red
- failing test:
  - active deps-guard regression
- expected failure:
  - readiness / checkout policy が旧 helper 依存のまま

###### Green
- minimum implementation:
  - `set_active(req)` の guard 部分
  - `application/status_context.py` の shared readiness path を再利用する
  - `domain/active.py` と `domain/deps.py` の利用
  - `infra/git_cli.py` 接続
- pass condition:
  - guard blocked/unknown と branch decision が既存契約どおり
  - readiness source selection は `application/status_context.py` shared seam 経由に固定される

###### Refactor
- cleanup target:
  - branch policy helper
- invariants to keep green:
  - force semantics
  - no manifest write before guard success
  - `active_issue_id` の取得は shared readiness seam と別責務のまま維持する

##### I2 — shared commit_active_state
- slice goal:
  - `commit_active_state()` に manifest/pointer/context-pack の正本順序を固定する

###### Red
- failing test:
  - active manifest/pointer write-order regression
- expected failure:
  - shared transaction helper が未実装

###### Green
- minimum implementation:
  - `commit_active_state(...)`
  - manifest/pointer/context-pack update
- pass condition:
  - `set_active` write path の manifest/pointer/context-pack 順序が shared helper で固定される
  - `render_context_pack` ownership が `presentation/json_state.py` 側に閉じる

###### Refactor
- cleanup target:
  - active transaction helper の shared 化
- invariants to keep green:
  - write order
  - infra は `context_pack_text` を受け取るだけで render しない

##### I3 — set command wiring
- slice goal:
  - `active set` を shared transaction helper へ接続する

###### Red
- failing test:
  - active set command regression
- expected failure:
  - `run_set` と `render_active_set_text` が新 path に未接続

###### Green
- minimum implementation:
  - `commands/active.py::run_set`
  - `set_active(req)` の commit path 接続
  - `render_active_set_text`
- pass condition:
  - `active set` が shared write order と CLI text 契約で通る

###### Refactor
- cleanup target:
  - set command outcome normalization
- invariants to keep green:
  - blocked/unknown/force semantics
  - stdout/stderr ownership

##### I4 — clear command wiring
- slice goal:
  - `active clear` の placeholder 永続化と CLI 契約を独立に固定する

###### Red
- failing test:
  - active clear placeholder regression
- expected failure:
  - `run_clear` と placeholder manifest path が未接続

###### Green
- minimum implementation:
  - `clear_active(req)`
  - `commands/active.py::run_clear`
  - `render_active_clear_text`
  - `patch_manifest=None` による active-field clear
- pass condition:
  - `active clear` は placeholder manifest persistence と `patch_manifest=None` による active-field clear 契約で通る
  - success exit `0` と zero-input normalization が既存契約で通る

###### Refactor
- cleanup target:
  - clear command outcome normalization
- invariants to keep green:
  - placeholder manifest 契約
  - pointer/context-pack placeholder update

##### I5 — rollback injection
- slice goal:
  - best-effort rollback 契約を failure injection で固定する

###### Red
- failing test:
  - rollback failure injection
- expected failure:
  - write/apply/patch failure 時の restore path が未実装

###### Green
- minimum implementation:
  - snapshot/restore wiring
  - rollback error reporting
- pass condition:
  - failure injection で `manifest/pointer/context-pack/agent state` restore と dual-error reporting が観測できる

###### Refactor
- cleanup target:
  - rollback reporting
- invariants to keep green:
  - git rollback は行わない
  - manifest/pointer/context-pack/agent state rollback は維持

#### step gate
- review:
  - active write slice review
- expected tests:
  - active set regression
  - active clear regression:
    - placeholder manifest persistence
    - pointer/context-pack placeholder update
    - agent state active-field clear
    - `git rollback` 非対象
    - zero-input normalization
    - success exit `0`
    - `render_active_clear_text` stdout/stderr contract
  - rollback injection tests
  - shared readiness seam regression
  - blocked/unknown/force-path exit code regression
  - blocked/unknown warning-error text regression
  - context-pack rendering ownership regression
- structural checks:
  - `commands/active.py` は request normalization / renderer selection / `CommandOutcome` 生成に限定し、direct fs/git/json/render side effect を持たないことを diff review で確認
  - workflow orchestration は `application/set_active.py` に集約され、`presentation` / `infra` / `domain` の責務境界を崩していないことを diff review で確認
  - `infra/active_store.py` は `context_pack_text` を受け取るだけで render を呼ばず、shared readiness source selection は `application/status_context.py` 側に残ることを diff review で確認
  - `domain/active.py` は I/O primitive や adapter import を持たず、`presentation/cli_text.py` / `presentation/json_state.py` が rendering ownership を維持することを diff review または import assertion で確認
  - `commit_active_state()` / `run_set` / `run_clear` / rollback injection が iteration ごとに別 failing test で閉じていることを diff review と report で確認
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S06 — `sync` vertical slice を新 layered path へ移す
- target:
  - `commands/sync.py`
  - `application/sync_state.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/artifact_writer.py`
  - `infra/fs_repo.py`
  - `infra/json_store.py`
  - `infra/clock.py`
  - `presentation/json_state.py`
  - `presentation/markdown.py`
  - `presentation/puml.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `collect_sync_state`
  - `maybe_auto_update_from_branch`
  - `write_sync_artifacts`
  - `SyncCommandResult`
- step boundary:
  - `sync` と artifact write のみ
  - `S05` の active transaction helper を消費する
  - `new/import` からの再利用は次 step 以降で消費
  - active 更新後に artifact write が失敗した場合は非原子的境界を許容し、その事実を観測可能にする

#### B1 — sync pipeline
- purpose:
  - artifact 契約と active auto-update 順序を 1 review scope で検証する

##### I1 — collect_sync_state
- slice goal:
  - sync の state collection を write から分離する

###### Red
- failing test:
  - sync state collection regression
- expected failure:
  - collect path が旧 helper 依存のまま

###### Green
- minimum implementation:
  - `collect_sync_state()`
  - structural/deps preflight
  - active manifest mode switch
- pass condition:
  - sync state が write 前に確定できる

###### Refactor
- cleanup target:
  - state result mapper
- invariants to keep green:
  - no artifact write yet

##### I2 — active auto-update before artifacts
- slice goal:
  - final active を artifact より先に確定する

###### Red
- failing test:
  - sync active auto-update ordering regression
- expected failure:
  - active auto-update が artifact write より後になる

###### Green
- minimum implementation:
  - `maybe_auto_update_from_branch()`
  - `S05` の active transaction helper 利用
- pass condition:
  - final active が artifact write より前に確定する

###### Refactor
- cleanup target:
  - ActiveUpdateOutcome composition
- invariants to keep green:
  - final active を含む artifact 前提
  - `sync_after_import` とは policy 分離
  - artifact write 失敗時に active 更新済み / artifact stale-or-partial となりうる
  - failure reason が CLI/test から識別可能である

##### I3 — json artifact bundle
- slice goal:
  - JSON artifact 契約を独立に固定する

###### Red
- failing test:
  - sync json artifact regression
- expected failure:
  - JSON renderer ownership と writer 接続が未完

###### Green
- minimum implementation:
  - `write_sync_artifacts()`
  - `presentation/json_state.py`
  - `infra/artifact_writer.py`
- pass condition:
  - `index*.json / tree*.json / deps-issues.json` が既存 path/name/content 契約で書かれる
  - placeholder / `deps.valid=false` / `deps.error` 契約が維持される

###### Refactor
- cleanup target:
  - JSON artifact bundle 組み立て
- invariants to keep green:
  - JSON artifact の output path/name/content shape

##### I4 — markdown / tree puml artifacts
- slice goal:
  - markdown / tree puml artifact 契約を JSON と分離して固定する

###### Red
- failing test:
  - sync markdown/tree-puml artifact regression
- expected failure:
  - markdown / tree puml renderer ownership が未接続

###### Green
- minimum implementation:
  - `presentation/markdown.py`
  - `presentation/puml.py` の tree 出力
  - `write_sync_artifacts()` への markdown / tree puml 組み込み
- pass condition:
  - `dashboard.md / tree*.puml` が既存 path/name/content 契約で書かれる

###### Refactor
- cleanup target:
  - markdown / tree puml bundle 組み立て
- invariants to keep green:
  - dashboard/tree artifact 契約

##### I5 — deps-issues puml + writer completion
- slice goal:
  - deps-issues puml と writer completion を独立に固定する

###### Red
- failing test:
  - sync deps-issues-puml regression
- expected failure:
  - `deps-issues.puml` と writer completion が未固定

###### Green
- minimum implementation:
  - `presentation/puml.py` の deps-issues 出力
  - `write_sync_artifacts()` completion
- pass condition:
  - `sync --force` は `deps-issues.puml` を含む全 artifact を生成し、既存 path/name/content 契約を維持する

###### Refactor
- cleanup target:
  - writer completion path
- invariants to keep green:
  - deps-issues artifact 契約

##### I6 — sync command text/outcome
- slice goal:
  - `sync` の stdout/stderr/exit 契約を user-facing で固定する

###### Red
- failing test:
  - `sync` CLI text regression
- expected failure:
  - `render_sync_text()` と `SyncCommandResult -> CommandOutcome` が未接続

###### Green
- minimum implementation:
  - `commands/sync.py`
  - `render_sync_text()`
  - `SyncCommandResult -> CommandOutcome` 接続
- pass condition:
  - `sync` の stdout success line / stderr lines / exit code / active updated-unchanged text が既存契約で通る
  - stderr/warnings order が既存契約で通る
  - post-active artifact-write failure injection で `exit=1`, `active updated`, `artifact stale-or-partial allowed`, `failure reason observable` が固定される

###### Refactor
- cleanup target:
  - sync command outcome normalization
- invariants to keep green:
  - stdout/stderr ownership
  - business exit code

#### step gate
- review:
  - sync slice review
- expected tests:
  - sync regression
  - artifact renderer tests
  - `json/markdown/puml` artifact regression:
    - path/name snapshot
    - content snapshot
    - `sync --force` placeholder snapshot
    - `deps-issues.puml` disabled-path snapshot
  - `sync` stderr/exit code regression
  - `sync --force` regression
  - `sync` help/args regression:
    - subparser help snapshot
    - global help tree からの到達
  - post-active artifact-write failure contract regression:
    - `exit=1`
    - active update 済み
    - artifact stale-or-partial 許容
    - failure reason が CLI/test から観測可能
- structural checks:
  - `commands/sync.py` は request normalization / `CommandOutcome` 生成に限定し、workflow は `application/sync_state.py` に集約されることを diff review で確認
  - `presentation` が content shape を所有し、`infra/artifact_writer.py` が path/name を所有することを diff review で確認
  - active auto-update は artifact write より前であることを diff review と failure injection で確認
  - artifact write failure は `SyncCommandResult.artifact_failure` へ理由を残し、CLI で user-visible になることを diff review と regression で確認
  - JSON / markdown-tree / deps-issues-puml / command outcome が iteration ごとに別 failing test で閉じていることを diff review と report で確認
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S07 — `new initiative|epic|issue` vertical slice を新 layered path へ移す
- target:
  - `commands/new.py`
  - `application/create_node.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/template_scaffolder.py`
  - `infra/fs_repo.py`
  - `infra/clock.py`
  - `infra/github_cli.py`
  - `domain/ids.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `create_node_core`
  - `plan_node_creation`
- step boundary:
  - `new node` のみ
  - `new doc` と `import` はまだ含めない

#### B1 — node create
- purpose:
  - no-write preflight と template/meta write を新 path へ移す

##### I1 — create preflight + planning
- slice goal:
  - ID/title/slug/github mode と candidate path planning を planner に閉じ込める

###### Red
- failing test:
  - create planning regression
- expected failure:
  - create planning が旧 helper 依存のまま

###### Green
- minimum implementation:
  - `create_node_core`
  - `plan_node_creation`
  - github mode normalization
- pass condition:
  - `CreatePlan.planned_paths` 相当の candidate output set が typed request から安定して導出できる
  - no-write preflight に必要な path 集合と planning が typed request で閉じる

###### Refactor
- cleanup target:
  - create request normalization
- invariants to keep green:
  - no-write preflight の full collision 判定は I2 で閉じる
  - path allocation

##### I2 — execute/order + representative kind
- slice goal:
  - full no-write preflight と execute/order 契約を representative kind で固定する

###### Red
- failing test:
  - new node execute/order regression
- expected failure:
  - full collision preflight と execute path が新 use case に接続されていない

###### Green
- minimum implementation:
  - `create_initiative`
  - `execute_create_plan`
  - `infra/template_scaffolder.py`
  - full no-write preflight over planned paths
- pass condition:
  - representative kind で template copy -> meta write 順序が固定される
  - `execute_create_plan(plan: CreatePlan, ports: Ports) -> list[Path]` の seam 契約と planning/write ownership split が固定される
  - collision 時は full no-write preflight が generated paths / `.meta.json` / nested scaffold path を含む candidate set 全体で fail-fast する

###### Refactor
- cleanup target:
  - create executor helper
- invariants to keep green:
  - metadata write order
  - no-write preflight は write 前に完了する

##### I3 — kind parity
- slice goal:
  - remaining kinds の generated scaffold/path parity を固定する

###### Red
- failing test:
  - new node kind parity regression
- expected failure:
  - epic/issue 差分や nested wrapper/placeholder parity が未固定

###### Green
- minimum implementation:
  - `create_epic/issue`
- pass condition:
  - `new initiative|epic|issue` が template/meta write 順序と generated path/name/content shape を維持する
  - per-kind generated scaffold 互換として `initiative -> epics/new-epic`, `epic -> issues/new-issue`, `issue -> placeholder set` を落とさない

###### Refactor
- cleanup target:
  - kind-specific create helper
- invariants to keep green:
  - metadata write order

##### I4 — GitHub/no-side-effect matrix
- slice goal:
  - GitHub mode 非対称 default と no-side-effect 契約を固定する

###### Red
- failing test:
  - new node GitHub flag matrix regression
- expected failure:
  - GitHub mode 非対称や no-gh side effect 契約が未固定

###### Green
- minimum implementation:
  - GitHub mode handling across `create_initiative/epic/issue`
- pass condition:
  - GitHub mode matrix は `kind x flag combo x default x gh side effect x exit source` で固定される
  - `--no-github` と invalid title/slug では gh side effect が発生しない

###### Refactor
- cleanup target:
  - github mode normalization
- invariants to keep green:
  - github create/link/local mode 契約

##### I5 — success text + S09 seam
- slice goal:
  - success text と import 再利用 seam を固定する

###### Red
- failing test:
  - new node success/seam regression
- expected failure:
  - success text と `execute_create_plan()` seam が未固定

###### Green
- minimum implementation:
  - `presentation/cli_text.py`
- pass condition:
  - `execute_create_plan()` を `S09` から再利用可能な seam として固定し、import 側が graph load / collision planning を二重実行しない前提が残る
  - success text が kind ごとの既存契約で通る

###### Refactor
- cleanup target:
  - create success text rendering
- invariants to keep green:
  - reuse seam ownership split

#### step gate
- review:
  - new node slice review
- expected tests:
  - new initiative/epic/issue regression:
    - initiative local/create/link
    - epic local/create/link
    - issue local/create/link
    - initiative nested wrapper path
    - epic nested wrapper path
    - issue placeholder set
    - args/help
    - stdout/stderr
    - exit code
    - generated path/name/content shape
  - template collision tests
  - collision fail-fast no-write regression
  - github mode flag matrix regression
  - `execute_create_plan()` reuse seam regression
- structural checks:
  - `commands/new.py` は args/help normalization / request translation / renderer selection に限定し、workflow orchestration や direct fs/gh side effect を持たないことを diff review で確認
  - planning は `application/create_node.py`、template/meta write は `infra/template_scaffolder.py` / repository port、text ownership は `presentation/cli_text.py` が正本であることを diff review で確認
  - `new node` slice について args/help、stdout/stderr、exit code、generated path/name/content shape の AC-004 観測点が gate の test 群で閉じていることを review で確認
  - `new node` live path が `commands -> application -> infra/presentation` の layered path へ移り、`app.py` は source of truth ではなくなることを diff review で確認
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S08 — `new doc` vertical slice を新 layered path へ移す
- target:
  - `commands/new.py`
  - `application/create_node.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `infra/template_scaffolder.py`
  - `infra/fs_repo.py`
  - `infra/clock.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `create_discussion_doc`
  - `load_template_text`
  - `write_text`
- step boundary:
  - `new doc` のみ
  - node create / import は巻き込まない
  - `S07` 完了かつ green を前提とする
  - shared file を編集しても `new node` 側の意味変更は持ち込まない

#### B1 — discussion doc create
- purpose:
  - doc sequence/path/template write を isolated review 可能にする

##### I1 — discussion doc planning
- slice goal:
  - doc numbering と path allocation を node create から分離する

###### Red
- failing test:
  - doc sequence/path regression
- expected failure:
  - discussion planner が未分離

###### Green
- minimum implementation:
  - `create_discussion_doc`
  - discussion sequence helper
  - plan path allocation
- pass condition:
  - new doc の numbering/path planning が安定する

###### Refactor
- cleanup target:
  - doc planner helper
- invariants to keep green:
  - doc numbering
  - no unintended overwrite

##### I2 — template load/write + CLI text
- slice goal:
  - template selectionと write ownership を `TemplateScaffolder` に集約する

###### Red
- failing test:
  - `new doc`
- expected failure:
  - template load / render / write が新 use case に接続されていない

###### Green
- minimum implementation:
  - `load_template_text`
  - `render_text`
  - `write_text`
  - `presentation/cli_text.py` の success text
- pass condition:
  - `new doc` が template selection と write ownership を維持する
  - `render_new_doc_text` の stdout/stderr/warnings/exit code 契約が維持される
  - generated file の path/name/content shape と duplicate 時 fail-fast no-write 契約が維持される

###### Refactor
- cleanup target:
  - new doc success text rendering
- invariants to keep green:
  - template selection
  - write ownership は `TemplateScaffolder`

#### step gate
- review:
  - new doc slice review
- expected tests:
  - new doc regression
  - new node non-regression for shared-file edits
  - doc template/path tests
  - new doc help / invalid slug / duplicate sequence regression
  - new doc stdout/stderr/warnings/exit regression
  - generated file path/name/content shape regression
  - duplicate/no-write regression
- structural checks:
  - `new doc` live path が `commands -> application -> infra/presentation` の layered path へ移り、`app.py` は source of truth ではなくなることを diff review で確認
  - `application/create_node.py` の shared-file edits は `create_discussion_doc` branch に限定し、`create_node_core` 系に意味変更を持ち込まないことを diff review で確認
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S09 — `import initiative|epic|issue` vertical slice を新 layered path へ移す
- target:
  - `commands/import_cmd.py`
  - `application/import_node.py`
  - `application/contracts.py`
  - `application/ports.py`
  - `application/sync_state.py::sync_after_import`
  - `infra/github_cli.py`
  - `infra/fs_repo.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `import_node_core`
  - `build_linked_create_request`
  - `sync_after_import`
  - `load_active_manifest_no_migrate`
- step boundary:
  - import 系のみ
  - `create_node` / `sync` の既存 step を再利用
  - `S06` と `S07` に依存し、`S08` には依存しない
  - `S07` 完了かつ green を前提とし、`execute_create_plan()` seam 契約を受け継ぐ
  - parent fallback は `ActiveStateStore.load_active_manifest_no_migrate()` を前提にする

#### B1 — import + post sync
- purpose:
  - `import -> sync` を単独 review/commit scope にする

##### I1 — import lookup + preflight
- slice goal:
  - GitHub lookup、duplicate guard、parent fallback、no-write preflight を固める

###### Red
- failing test:
  - import preflight integration
- expected failure:
  - import lookup と preflight が旧 helper 依存のまま

###### Green
- minimum implementation:
  - `import_node_core`
  - `build_linked_create_request`
  - `load_active_manifest_no_migrate` を使った parent fallback
- pass condition:
  - lookup/duplicate/parent fallback/no-write preflight が command 成功経路抜きで閉じる

###### Refactor
- cleanup target:
  - import request mapper
- invariants to keep green:
  - no-write preflight
  - title/slug explicit contract
  - parent fallback は `load_active_manifest_no_migrate() -> ActiveSelection -> resolve_parent_from_active()` 鎖を使う

##### I2 — import issue + post-import sync
- slice goal:
  - import 完了後だけ `sync_after_import()` が走る契約を維持する

###### Red
- failing test:
  - `import -> sync` regression
- expected failure:
  - post-import sync policy が未接続

###### Green
- minimum implementation:
  - `import_initiative/epic/issue`
  - `sync_after_import()`
  - `presentation/cli_text.py` の import success text
- pass condition:
  - import 成功後だけ post-import sync が走り、failure/duplicate/invalid-parent/create-failure では起動しない

###### Refactor
- cleanup target:
  - import lower-level reuse
- invariants to keep green:
  - `no_migrate`
  - `update_active_from_branch=False`
  - import 成功後のみ post-sync 起動

#### step gate
- review:
  - import slice review
- expected tests:
  - import regression
  - import->sync regeneration regression
  - import->sync closure artifact assertion
  - post-import sync negative-path regression
  - import stdout/stderr/warnings regression
  - `execute_create_plan()` reuse seam regression:
    - import で graph load / collision planning を二重実行しない
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S10 — test tree を設計どおりに分割する
- target:
  - `tests/test_cli.py`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/*`
  - `tests/domain_runtime/*`
  - `tests/presentation_runtime/*`
- design refs:
  - test layout tree
  - command-wise runtime test split
- step boundary:
  - test file の物理分割のみ
  - runtime helper call site の最終 detachment は次 step
  - guard-first refactor step として、discovery/import entrypoint の safety net を先に固定する
  - `unittest discover` 成立条件は `tests/`, `tests/cli_runtime/`, `tests/domain_runtime/`, `tests/presentation_runtime/` を regular package 化する `__init__.py` 方式に固定し、`load_tests` は採用しない
  - `tests/test_cli.py` は S10 完了時点で no-op shim ではなく移設済みの残骸整理対象として縮小する
  - S10 全体は semantic-no-change refactor とし、pure move / helper extraction / import path 修正以外の意味変更を持ち込まない
  - src bootstrap owner は package-local helper に固定し、moved test から `Path(__file__).resolve().parents[1] / "src"` 前提を持ち込まない

#### B1 — file split
- purpose:
  - reviewer が command ごとの失敗面を追いやすい test tree を先に作る

##### I1 — installer/wrapper split
- slice goal:
  - installer/update と runtime wrapper tests の正本を先に分ける

###### Red
- failing test:
  - installer/wrapper discovery regression
- expected failure:
  - file split 後に discover 対象や helper import が崩れる

###### Green
- minimum implementation:
  - `tests/test_init_update.py`
  - `tests/cli_runtime/harness.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `tests/`, `tests/cli_runtime/`, `tests/domain_runtime/`, `tests/presentation_runtime/` の `__init__.py`
- pass condition:
  - installer/update と wrapper tests が新配置で discover される
  - `test_init_update.py` が installer assertions を所有し、`cli_runtime/harness.py` が subprocess/git/gh/runtime setup を所有する

###### Refactor
- cleanup target:
  - shared runtime harness import
- invariants to keep green:
  - `python -m unittest discover -v`
  - `cli_runtime/harness.py` は `cli_runtime/*` だけが参照し、`domain_runtime/*` / `presentation_runtime/*` は独自 helper へ閉じる
  - `cli_runtime/harness.py` を domain/presentation test から参照しない
  - semantic-no-change: pure move / helper extraction / import path 修正に留める
  - moved tests の src bootstrap は package-local helper で一貫させる

##### I2 — command runtime split
- slice goal:
  - runtime command contract を file 単位で分割する

###### Red
- failing test:
  - command runtime discovery regression
- expected failure:
  - command別ファイルへ移すと test entrypoint が崩れる

###### Green
- minimum implementation:
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_active.py`
  - `tests/cli_runtime/test_sync.py`
  - `tests/cli_runtime/test_deps.py`
  - `tests/cli_runtime/test_import.py`
  - `tests/cli_runtime/test_validate.py`
- pass condition:
  - runtime command contract が file 単位で分割されても discover が維持される

###### Refactor
- cleanup target:
  - duplicated command fixtures
- invariants to keep green:
  - command-wise runtime test coverage
  - semantic-no-change: assertion の意味と観測点を変えない

##### I3 — domain/presentation split
- slice goal:
  - pure domain/presentation test を runtime integration から分離する

###### Red
- failing test:
  - pure test discovery regression
- expected failure:
  - pure test の新配置で import path が崩れる

###### Green
- minimum implementation:
  - `tests/domain_runtime/test_ids.py`
  - `tests/domain_runtime/test_tree.py`
  - `tests/domain_runtime/test_deps.py`
  - `tests/domain_runtime/test_active.py`
  - `tests/presentation_runtime/test_markdown.py`
  - `tests/presentation_runtime/test_puml.py`
  - `tests/presentation_runtime/test_json_state.py`
- pass condition:
  - pure domain/presentation test が runtime integration と分離されて通る
  - domain/presentation subtree は各 subtree 内 helper のみを使う

###### Refactor
- cleanup target:
  - duplicated fixture/helper import
- invariants to keep green:
  - I1/I2 green 後の file split/refactor に留め、意味変更を持ち込まない
  - 既存 assertion coverage
  - pure unit と integration の分離

#### step gate
- review:
  - test tree split review
- expected tests:
  - `python -m unittest discover -v`
  - touched test modules
  - critical inventory still covered:
    - staged delegation path (pre-S11 seam)
    - active rollback failure-injection
    - import->sync regeneration
    - sync artifact path/name/content snapshots
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit

### S11 — 旧 helper 直依存を解消し layered entrypoint 経由へ統一する
- target:
  - `app.py`
  - `commands/*`
  - `application/*`
  - `tests/cli_runtime/*`
  - `tests/domain_runtime/*`
  - `tests/presentation_runtime/*`
  - 旧 helper call site 一式
- design refs:
  - final module tree
  - dependency UML
- step boundary:
  - 旧 helper 直依存の解消のみ
  - user-facing behavior change は含めない
  - guard-first refactor step として、legacy import 禁止と layer 方向の safety net を先に固定する
  - stage-5 cleanup では rollback 基準を wrapper seam ではなく `git revert / commit rollback` へ切り替える

#### B1 — helper detachment
- purpose:
  - 段階移行で残した delegation を最後に除去する

##### I1 — command/application call-site detachment
- slice goal:
  - runtime code が final public API だけを見る状態へ揃える

###### Red
- failing test:
  - final API call-site regression
- expected failure:
  - thin delegation 前提の runtime call site が残っている

###### Green
- minimum implementation:
  - old helper direct call を final layered API へ切り替える
- pass condition:
  - runtime code が final public API 経由だけで通る
  - `commands/*` は `UseCases` facade 以外の `application/domain/infra` implementation へ直接依存しない

###### Refactor
- cleanup target:
  - compatibility shim の縮小
- invariants to keep green:
  - import graph の layer 方向
  - command behavior unchanged

##### I2 — legacy infra/domain shim cleanup
- slice goal:
  - `ids.py`, `io_json.py`, `github.py` の flat shim を matrix どおり整理する

###### Red
- failing test:
  - legacy infra/domain import assertion regression
- expected failure:
  - `ids/io_json/github` 依存がまだ残っている

###### Green
- minimum implementation:
  - `ids.py`, `io_json.py`, `github.py` の dead path を削除または wrapper 限定にする
- pass condition:
  - infra/domain 系 flat shim の import が残らない

###### Refactor
- cleanup target:
  - infra/domain compatibility shim の削除
- invariants to keep green:
  - stage-5 cleanup では rollback は `git revert / commit rollback` で担保する

##### I3 — legacy presentation/runtime shim cleanup
- slice goal:
  - `render_md.py`, `render_puml.py`, `active.py`, `nodes.py` の flat shim を matrix どおり整理する

###### Red
- failing test:
  - legacy presentation/runtime import assertion regression
- expected failure:
  - `render_md/render_puml/active/nodes` 依存がまだ残っている

###### Green
- minimum implementation:
  - `render_md.py`, `render_puml.py`, `active.py`, `nodes.py` の dead path を削除または wrapper 限定にする
- pass condition:
  - presentation/runtime 系 flat shim の import が残らない
  - `active.py` と `nodes.py` に残る場合の許容形は legacy shim matrix どおり thin delegation のみである

###### Refactor
- cleanup target:
  - presentation/runtime compatibility shim の削除
- invariants to keep green:
  - branch diff に import 逆流が残らない
  - command behavior unchanged
  - wrapper 許容範囲は legacy shim matrix と一致する

#### step gate
- review:
  - old helper detachment review
- expected tests:
  - `python -m unittest discover -v`
  - focused regressions:
    - `import -> sync`
    - `active set` guard/order
    - `deps check`
    - markdown/puml/json artifact contracts
  - critical test inventory confirmation:
    - final API call-site regression
    - active rollback failure-injection
    - import->sync regeneration
    - sync artifact path/name/content snapshots
  - legacy import prohibition / layer direction assertions
    - `commands/* -> UseCases facade only`
    - `domain/*` no I/O import
    - `infra/*` only through ports
  - stage-5 rollback evidence:
    - wrapper seam 廃止後は `git revert / commit rollback` が唯一の rollback 基準であることを report に記録
    - legacy seam 除去後に rollback basis が切り替わったことを diff review で確認
    - partial import rollback は対象外であり rollback unit は commit 単位であることを report に記録
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - 1 commit
  - rollback target は commit hash ではなく「この S11 commit 自体が revert target」であることを report と commit message で自己記述的に残す

### S90 — docs impact resolution / docs refresh
- target:
  - docs / assets / workflow / skill / none
- step boundary:
  - docs impact の確認と必要な refresh のみ
  - implementation scope の追加は行わない
  - docs-only step だが review/report/commit scope は独立して閉じる
  - docs impact が `none` でも no-op resolution step として必ず実行する

#### B1 — docs impact gate
- purpose:
  - docs impact を no-op か更新かで明示的に閉じる

##### I1 — docs impact detect
- slice goal:
  - docs impact の有無を観測可能に判定する

###### Red
- failing test:
  - docs impact checklist regression
- expected failure:
  - docs 影響の判定根拠が plan/report に残らない

###### Green
- minimum implementation:
  - changed assets/workflow/docs を棚卸しする
  - `docs / assets / workflow / skill / none` を判定する
- pass condition:
  - docs impact の有無と理由が記録される

###### Refactor
- cleanup target:
  - docs impact checklist
- invariants to keep green:
  - no implementation scope expansion

##### I2 — docs refresh or no-op record
- slice goal:
  - 必要更新か no-op かを report まで閉じる

###### Red
- failing test:
  - docs resolution record regression
- expected failure:
  - 反映または no-op 理由が記録されない

###### Green
- minimum implementation:
  - 必要な docs refresh を行う、または no-op 理由を `report.md` へ記録する
- pass condition:
  - docs impact resolved が追跡可能になる

###### Refactor
- cleanup target:
  - docs refresh note
- invariants to keep green:
  - shipped runtime asset 説明との整合

#### step gate
- review:
  - docs impact review
- expected checks:
  - docs impact checklist:
    - `docs / assets / workflow / skill / none` の判定根拠が残る
    - docs refresh が必要な場合は対象パスと理由が列挙される
    - no-op の場合は no-op 理由が列挙される
  - plan/design/requirement との整合:
    - docs refresh が issue-25 の requirement/design/plan に矛盾しない
- report update:
  - `spec-deps/current/report.md`
- commit policy:
  - docs change がある場合は 1 commit
  - no-op の場合も `report.md` の no-op 判定記録を含む 1 commit

### S99 — final diff review quality gate
- branch diff scope:
  - `git diff origin/main...HEAD`
  - 対象はこの branch の実装差分全体であり、step ごとの staged diff ではなく最終統合状態を見る

#### B1 — final validation
- purpose:
  - branch 全体の品質と requirement/design/plan trace を閉じる

##### I1 — full validation sweep
- slice goal:
  - branch 全体差分に対する validation を揃える

###### Red
- failing test:
  - final validation checklist regression
- expected failure:
  - full suite / packaging / lowercase / smoke のどれかが未確認

###### Green
- minimum implementation:
  - `python -m unittest discover -v`
  - requirement/design/plan との trace check
  - runtime packaging / shipped asset check
  - lowercase path 増分なし確認: `rg --files | rg '[A-Z]'`
  - shipped asset smoke check:
    - runtime asset をコピーした fresh repo 相当の test fixture で CLI entrypoint が起動する
    - `validate`, `deps check --json`, `active show`, `sync --force`, `new issue`, `import issue` の代表経路が少なくとも 1 回ずつ通る
- pass condition:
  - branch 全体差分の validation 証跡が揃う

###### Refactor
- cleanup target:
  - final validation checklist
- invariants to keep green:
  - AC/EC trace が欠けない

##### I2 — architecture/spec gate
- slice goal:
  - architecture drift と spec drift を reviewer pass で閉じる

###### Red
- failing test:
  - architecture/spec gate regression
- expected failure:
  - thinness / layer / DTO / trace のどれかが reviewer で blocking になる

###### Green
- minimum implementation:
  - `app.py` thinness check:
    - `app.py` が entrypoint/dispatch/error handling 以外の command body を持たない
  - command thinness check:
    - `commands/*` が direct fs/git/gh/render 実装を持たず、typed request DTO 正規化と `UseCases` 呼び出しに留まる
  - layer violation 確認:
    - `commands -> application -> domain/ports -> infra/presentation` の逆流 import が diff にない
    - `domain` が `subprocess`, `print`, `Path.write_text`, `gh`, `git` を持ち込んでいない
  - DTO / contract check:
    - public request/result/contract が dataclass として `application/contracts.py` / `presentation/contracts.py` / `commands/contracts.py` に集約される
    - `dict[str, Any]` は `JsonStore` / JSON read-write 境界に限定される
    - `commands/*` は raw CLI value を `TargetRef` 等の typed request に正規化してから use case を呼ぶ
  - touched file / AC-EC trace:
    - `AC-001`: runtime package tree / `app.py` 薄化差分
    - `AC-002`: `application/domain/infra/presentation` への責務分離差分
    - `AC-003`: `tests/test_init_update.py`, `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_new.py`, `tests/cli_runtime/test_active.py`, `tests/cli_runtime/test_sync.py`, `tests/cli_runtime/test_deps.py`, `tests/cli_runtime/test_import.py`, `tests/cli_runtime/test_validate.py`, `tests/cli_runtime/test_wrappers.py`, `tests/domain_runtime/test_ids.py`, `tests/domain_runtime/test_tree.py`, `tests/domain_runtime/test_deps.py`, `tests/domain_runtime/test_active.py`, `tests/presentation_runtime/test_markdown.py`, `tests/presentation_runtime/test_puml.py`, `tests/presentation_runtime/test_json_state.py` の分割差分
    - `AC-004`: 重要 command regression test と artifact regression
    - `AC-005`: full suite green
    - `EC-001`-`EC-004`: 該当 regression test と reviewer finding 0 件
  - `spec_reviewer` pass
- pass condition:
  - branch 全体差分が reviewer pass になる

###### Refactor
- cleanup target:
  - final gate report
- invariants to keep green:
  - final diff gate は branch 全体差分が `pass` になるまで修正→再レビューを繰り返す

## 未確定事項
- なし

## final exit contract
- AC/EC 達成:
  - S01-S11, S90, S99 完了後に requirement の AC/EC をすべて満たす
- docs impact resolved:
  - `none` または必要更新反映済み
- final diff approved:
  - `spec_reviewer` pass
  - branch diff review の blocking finding 0 件
