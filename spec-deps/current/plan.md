---
種別: 実装計画書（Issue）
ID: "issue-25"
タイトル: "巨大な app.py を複数 module に分割し tests/test_cli.py を領域別に再編する"
関連GitHub: ["https://github.com/chemitaro/spec-dock/issues/25"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-11"
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
- S01:
  - 観測可能な振る舞い:
    - parser/registry/bootstrap/dispatch と command wrapper が導入されても、CLI help と exit ownership が維持される
  - closes:
    - AC-001
    - EC-001
  - review gate:
    - CLI foundation diff review
- S02:
  - 観測可能な振る舞い:
    - `validate` が新 layered path で動作し、構造/deps validation を維持する
  - closes:
    - AC-002
    - AC-004
  - review gate:
    - validate slice review
- S03:
  - 観測可能な振る舞い:
    - `deps check` が新 layered path で動作し、text/json/exit code/readiness 契約を維持する
  - closes:
    - AC-002
    - AC-004
    - EC-003
    - EC-004
  - review gate:
    - deps slice review
- S04:
  - 観測可能な振る舞い:
    - `active show` が新 layered path で動作し、current CLI 表示契約を維持する
  - closes:
    - AC-002
    - AC-004
  - review gate:
    - active show slice review
- S05:
  - 観測可能な振る舞い:
    - `active set/clear` が新 layered path で動作し、guard/order/rollback 契約を維持する
  - closes:
    - AC-002
    - AC-004
    - EC-003
  - review gate:
    - active write slice review
- S06:
  - 観測可能な振る舞い:
    - `sync` が新 layered path で動作し、`sync --force` と artifact 契約を維持する
  - closes:
    - AC-002
    - AC-004
    - EC-004
  - review gate:
    - sync slice review
- S07:
  - 観測可能な振る舞い:
    - `new initiative|epic|issue` が新 layered path で動作し、scaffold collision fail-fast no-write を維持する
  - closes:
    - AC-001
    - AC-004
  - review gate:
    - new node slice review
- S08:
  - 観測可能な振る舞い:
    - `new doc` が新 layered path で動作し、discussion sequence/path/template write 契約を維持する
  - closes:
    - AC-001
    - AC-004
  - review gate:
    - new doc slice review
- S09:
  - 観測可能な振る舞い:
    - `import initiative|epic|issue` が新 layered path で動作し、`import -> sync` 契約を維持する
  - closes:
    - AC-002
    - AC-004
    - EC-002
  - review gate:
    - import slice review
- S10:
  - 観測可能な振る舞い:
    - test tree が `tests/test_init_update.py`, `tests/cli_runtime`, `tests/domain_runtime`, `tests/presentation_runtime` へ分割される
  - closes:
    - AC-003
    - AC-005
  - review gate:
    - test tree split review
- S11:
  - 観測可能な振る舞い:
    - 旧 helper 直依存が解消され、layered entrypoint 経由へ統一される
  - closes:
    - AC-005
  - review gate:
    - old helper detachment review

## 要件 ↔ ステップ対応
- AC-001 -> S01, S07, S08
- AC-002 -> S02, S03, S04, S05, S06, S09
- AC-003 -> S10
- AC-004 -> S02, S03, S04, S05, S06, S07, S08, S09
- AC-005 -> S10, S11, S99
- EC-001 -> S01
- EC-002 -> S09
- EC-003 -> S03, S05
- EC-004 -> S03, S06

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
- docs impact が `none` でなければ `S90` を実行する。
- 最後に `git diff origin/main...HEAD` を対象に `S99 final diff review quality gate` を実施する。
- reviewer verdict は `report.md` に残す。
- step review の対象と git commit の対象は一致させる。
- shared helper は単独コミットにせず、最初の消費者 slice と同じ commit に入れる。
- read-only flow を先に、write-path を後に、旧 helper の削除は最後に行う。

## legacy shim matrix
| 旧 module | 中間段階の扱い | 正式移設先 | 削除/最終整理 step | rollback unit |
| --- | --- | --- | --- | --- |
| `ids.py` | wrapper 維持可 | `domain/ids.py` | `S11` | `S02-S03` |
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
  - `tests/cli_runtime/harness.py`
  - `tests/cli_runtime/test_wrappers.py`
- design refs:
  - [design.md](/srv/mount/spec-dock/spec-deps/current/design.md)
- step boundary:
  - parser/registry/bootstrap/dispatch/wrapper 導入まで
  - `application/domain/infra/presentation` の本実装はまだ旧 helper delegation を許容
  - `commands/*` wrapper は top-level command 入口の到達性 smoke までをこの step に含める

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
  - `commands/*` は旧 helper を呼ぶ thin wrapper に留める
- pass condition:
  - dispatch と business exit code の既存契約が維持される

###### Refactor
- cleanup target:
  - `app.py` の dispatch 分岐の縮小
- invariants to keep green:
  - business exit code
  - wrapper は thin delegation のまま

##### I3 — wrapper harness
- slice goal:
  - top-level command wrapper の到達性を専用 runtime harness で観測できる

###### Red
- failing test:
  - `tests/cli_runtime/test_wrappers.py`
- expected failure:
  - wrapper smoke 用 harness が未整備で到達性を観測できない

###### Green
- minimum implementation:
  - `tests/cli_runtime/harness.py`
  - `tests/cli_runtime/test_wrappers.py`
  - `new/import/active/sync/deps/validate` の top-level wrapper smoke
- pass condition:
  - 各 wrapper が bootstrap 済み `UseCases` を呼べる

###### Refactor
- cleanup target:
  - wrapper smoke 共通 helper
- invariants to keep green:
  - `app.py` に command 実装本体を戻さない
  - `commands/*` に direct fs/git/gh/render 実装を持ち込まない

#### step gate
- review:
  - staged diff を対象に implementation review
- expected tests:
  - parser/help regression
  - top-level wrapper smoke:
    - `new`
    - `import`
    - `active`
    - `sync`
    - `deps`
    - `validate`
- structural checks:
  - `app.py` は entrypoint/dispatch/error handling に限定されることを diff review で確認
  - `commands/*` が `UseCases` facade 経由のみで orchestration することを diff review で確認
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
  - `domain/tree.py`
  - `domain/validation.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `validate_tree`
  - `validate_graph_and_deps`
- step boundary:
  - `validate` のみ
  - `deps check` や `sync` の共通 helper はまだ巻き込まない

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
  - `domain/deps.py`
  - `infra/github_cli.py`
  - `infra/derived_state_reader.py`
  - `infra/active_store.py`
  - `presentation/json_state.py`
  - `presentation/cli_text.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `resolve_issue_status_context`
  - `inspect_target_deps`
  - `DepsCheckResult`
- step boundary:
  - `deps check` text/json/exit code/readiness
  - `active set` guard での再利用は次 step で消費する

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
  - `infra/github_cli.py`
  - `infra/derived_state_reader.py`
  - `infra/active_store.py`
  - `check_deps(req)` の入力 wiring
- pass condition:
  - readiness 入力が ports 経由で self-contained に解決できる

###### Refactor
- cleanup target:
  - status snapshot mapper
- invariants to keep green:
  - github/cached の source selection
  - active issue context の受け渡し

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
  - domain deps unit tests
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
  - `infra/active_store.py`
  - `infra/fs_repo.py`
  - `infra/json_store.py`
  - `domain/active.py`
  - `presentation/cli_text.py`
  - `presentation/json_state.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `show_active`
  - `ActiveViewEntry`
- step boundary:
  - `active show` のみ
  - `clear_active` / `set_active` の transaction/rollback は次 step

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
  - `infra/active_store.py` から manifest を読む
- pass condition:
  - `id/path` 表示用 DTO が安定して返る

###### Refactor
- cleanup target:
  - active manifest normalization
- invariants to keep green:
  - no write side effect

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
  - `infra/active_store.py`
  - `infra/fs_repo.py`
  - `infra/json_store.py`
  - `infra/git_cli.py`
  - `infra/clock.py`
  - `domain/active.py`
  - `presentation/cli_text.py`
  - `presentation/json_state.py`
  - `presentation/contracts.py`
  - 対応 test
- design refs:
  - `set_active`
  - `clear_active`
  - `commit_active_state`
  - `ActiveUpdateOutcome`
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
  - `domain/active.py` と `domain/deps.py` の利用
  - `infra/git_cli.py` 接続
- pass condition:
  - guard blocked/unknown と branch decision が既存契約どおり

###### Refactor
- cleanup target:
  - branch policy helper
- invariants to keep green:
  - force semantics
  - no manifest write before guard success

##### I2 — shared commit_active_state
- slice goal:
  - `set_active` と `clear_active` が同じ永続化順序を共有する

###### Red
- failing test:
  - active shared write-order regression
- expected failure:
  - shared transaction helper が未実装

###### Green
- minimum implementation:
  - `commit_active_state(...)`
  - `clear_active(req)`
  - manifest/pointer/context-pack/agent-state update
- pass condition:
  - `set_active/clear_active` が shared write order を通る

###### Refactor
- cleanup target:
  - active transaction helper の shared 化
- invariants to keep green:
  - write order
  - placeholder manifest 契約

##### I3 — rollback injection
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
  - failure injection で best-effort rollback が観測できる

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
  - active clear regression
  - rollback injection tests
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
  - `sync --force` の disabled placeholder 契約
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

##### I3 — artifact bundle + write
- slice goal:
  - JSON/Markdown/PUML artifact 契約を維持して書き出す

###### Red
- failing test:
  - sync artifact regression
- expected failure:
  - renderer ownership と writer 接続が未完

###### Green
- minimum implementation:
  - `write_sync_artifacts()`
  - `presentation/json_state.py`
  - `presentation/markdown.py`
  - `presentation/puml.py`
  - `infra/artifact_writer.py`
- pass condition:
  - JSON/Markdown/PUML artifact が既存 path/name/content 契約で書かれる

###### Refactor
- cleanup target:
  - artifact bundle 組み立て
- invariants to keep green:
  - output path/name/content shape
  - dashboard/deps/tree/index artifact 契約

#### step gate
- review:
  - sync slice review
- expected tests:
  - sync regression
  - artifact renderer tests
  - `json/markdown/puml` artifact regression
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
  - ID/title/slug/github mode と no-write preflight を planner に閉じ込める

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
  - no-write preflight と planning が typed request で閉じる

###### Refactor
- cleanup target:
  - create request normalization
- invariants to keep green:
  - no-write preflight
  - path allocation

##### I2 — scaffold/meta write
- slice goal:
  - template copy と meta write の順序契約を維持する

###### Red
- failing test:
  - `new issue`
- expected failure:
  - template/meta write path が新 use case に接続されていない

###### Green
- minimum implementation:
  - `create_initiative/epic/issue`
  - `execute_create_plan`
  - `infra/template_scaffolder.py`
  - `presentation/cli_text.py`
- pass condition:
  - `new initiative|epic|issue` が template/meta write 順序を維持する

###### Refactor
- cleanup target:
  - create success text rendering
- invariants to keep green:
  - metadata write order
  - github create/link/local mode 契約

#### step gate
- review:
  - new node slice review
- expected tests:
  - new initiative/epic/issue regression
  - template collision tests
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
  - `write_text`
  - `presentation/cli_text.py` の success text
- pass condition:
  - `new doc` が template selection と write ownership を維持する

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
  - doc template/path tests
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
  - import 成功後だけ post-import sync が走る

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
  - guard-first refactor step として、discovery/import/coverage entrypoint の safety net を先に固定する

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
- pass condition:
  - installer/update と wrapper tests が新配置で discover される

###### Refactor
- cleanup target:
  - shared runtime harness import
- invariants to keep green:
  - `python -m unittest discover -v`

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
  - runtime command contract が file 単位で分割されても discover/coverage が維持される

###### Refactor
- cleanup target:
  - duplicated command fixtures
- invariants to keep green:
  - command-wise runtime test coverage

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

###### Refactor
- cleanup target:
  - duplicated fixture/helper import
- invariants to keep green:
  - 既存 assertion coverage
  - pure unit と integration の分離

#### step gate
- review:
  - test tree split review
- expected tests:
  - `python -m unittest discover -v`
  - touched test modules
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

#### B1 — helper detachment
- purpose:
  - 段階移行で残した delegation を最後に除去する

##### I1 — command/application call-site detachment
- slice goal:
  - runtime code が final public API だけを見る状態へ揃える

###### Red
- failing test:
  - legacy helper removal regression
- expected failure:
  - thin delegation 前提の runtime call site が残っている

###### Green
- minimum implementation:
  - old helper direct call を final layered API へ切り替える
- pass condition:
  - runtime code が final public API 経由だけで通る

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
  - legacy infra/domain shim regression
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
  - rollback seam が壊れない

##### I3 — legacy presentation/runtime shim cleanup
- slice goal:
  - `render_md.py`, `render_puml.py`, `active.py`, `nodes.py` の flat shim を matrix どおり整理する

###### Red
- failing test:
  - legacy presentation/runtime shim regression
- expected failure:
  - `render_md/render_puml/active/nodes` 依存がまだ残っている

###### Green
- minimum implementation:
  - `render_md.py`, `render_puml.py`, `active.py`, `nodes.py` の dead path を削除または wrapper 限定にする
- pass condition:
  - presentation/runtime 系 flat shim の import が残らない

###### Refactor
- cleanup target:
  - presentation/runtime compatibility shim の削除
- invariants to keep green:
  - branch diff に import 逆流が残らない
  - command behavior unchanged

#### step gate
- review:
  - old helper detachment review
- expected tests:
  - `python -m unittest discover -v`
  - focused regressions on touched commands
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
