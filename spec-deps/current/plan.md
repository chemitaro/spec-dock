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

##### I1 — help/dispatch/exit ownership
- slice goal:
  - help/argparse/dispatch/exit ownership が維持されたまま、新入口へ通る

###### Red
- failing test:
  - parser/help/arg tree regression test
  - representative command dispatch smoke test
- expected failure:
  - 新入口未導入で help/dispatch が通らない

###### Green
- minimum implementation:
  - parser/registry/bootstrap/dispatch を導入
  - `commands/*` は旧 helper を呼ぶ thin wrapper に留める
  - wrapper smoke 用の runtime harness と `test_wrappers.py` を用意する
- pass condition:
  - help/dispatch/exit code の既存契約が維持される

###### Refactor
- cleanup target:
  - `app.py` の parser/dispatch 分岐の縮小
- invariants to keep green:
  - help text
  - business exit code
  - argparse failure=2
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

##### I1 — validate command
- slice goal:
  - `validate` が `commands -> application -> domain -> presentation` で通る

###### Red
- failing test:
  - `validate` exit code / stderr / success text regression
- expected failure:
  - 新 path 未実装で結果が一致しない

###### Green
- minimum implementation:
  - `validate_tree(req)` と `render_validate_text(result)` を実装
- pass condition:
  - 構造/deps validation の既存挙動が維持される

###### Refactor
- cleanup target:
  - validation helper の pure 化
- invariants to keep green:
  - error message semantics
  - checked node count

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

##### I1 — deps text/json
- slice goal:
  - `deps check` text/json/exit code が維持される

###### Red
- failing test:
  - `deps check` ready/not-ready exit code
  - `deps check --json` payload regression
- expected failure:
  - result DTO / renderer ownership 不整合

###### Green
- minimum implementation:
  - `status_context` 導入
  - `check_deps(req)` 導入
  - `IssueGateway` / `DerivedStateReader` / `ActiveStateStore` adapter を接続
  - text/json renderer 接続
- pass condition:
  - readiness/exit code/json shape が維持される

###### Refactor
- cleanup target:
  - deps target inspection DTO
- invariants to keep green:
  - `0/3/1` exit code
  - json payload shape

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

##### I1 — active show
- slice goal:
  - current CLI の表示契約を新 path で維持する

###### Red
- failing test:
  - `active show`
- expected failure:
  - manifest/path 表示が未実装

###### Green
- minimum implementation:
  - `show_active(req)`
  - `render_active_show_text`

###### Refactor
- cleanup target:
  - active manifest normalization
- invariants to keep green:
  - `id/path` 表示契約

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

##### I1 — active set/clear with guard/rollback
- slice goal:
  - shared `commit_active_state()` を通る guard/order/rollback 契約を維持する

###### Red
- failing test:
  - deps guard blocked/unknown
  - `active clear`
  - side-effect order
  - rollback failure injection
- expected failure:
  - active transaction helper が未実装

###### Green
- minimum implementation:
  - `set_active(req)`
  - `clear_active(req)`
  - `commit_active_state(...)`
  - branch/guard wiring

###### Refactor
- cleanup target:
  - active transaction helper の shared 化
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

##### I1 — sync state + artifacts
- slice goal:
  - `sync` と `sync --force` の主経路を維持する

###### Red
- failing test:
  - `sync --force`
  - artifact path/name/content regression
  - active-update message regression
- expected failure:
  - final active と artifact の順序が不一致

###### Green
- minimum implementation:
  - `sync(req)`
  - `collect_sync_state()`
  - `maybe_auto_update_from_branch()`
  - `write_sync_artifacts()`

###### Refactor
- cleanup target:
  - artifact bundle 組み立て
- invariants to keep green:
  - final active を含む artifact
  - `sync --force` の disabled placeholder 契約

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

##### I1 — new initiative/epic/issue
- slice goal:
  - node create の ID/title/slug/github mode 契約を維持する

###### Red
- failing test:
  - `new initiative`
  - `new epic`
  - `new issue`
  - scaffold collision fail-fast no-write

###### Green
- minimum implementation:
  - `create_initiative/epic/issue`
  - `create_node_core`
  - `execute_create_plan`

###### Refactor
- cleanup target:
  - create plan helper
- invariants to keep green:
  - no-write preflight
  - path allocation
  - metadata write order

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

##### I1 — new doc
- slice goal:
  - discussion doc creation 契約を維持する

###### Red
- failing test:
  - `new doc`
  - doc sequence/path regression
- expected failure:
  - template load / path allocation / write ownership が未実装

###### Green
- minimum implementation:
  - `create_discussion_doc`
  - `load_template_text`
  - `write_text`

###### Refactor
- cleanup target:
  - discussion sequence helper
- invariants to keep green:
  - doc numbering
  - template selection
  - no unintended overwrite

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

##### I1 — import flows
- slice goal:
  - import preflight / parent fallback / post-import sync を維持する

###### Red
- failing test:
  - `import initiative`
  - `import epic`
  - `import issue`
  - `import -> sync` artifact regeneration

###### Green
- minimum implementation:
  - `import_initiative/epic/issue`
  - `import_node_core`
  - `build_linked_create_request`
  - `sync_after_import()`

###### Refactor
- cleanup target:
  - import lower-level reuse
- invariants to keep green:
  - `no_migrate`
  - `update_active_from_branch=False`

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

#### B1 — file split
- purpose:
  - reviewer が command ごとの失敗面を追いやすい test tree を先に作る

##### I1 — canonical test tree split
- slice goal:
  - test layout を分割しても振る舞いと coverage entrypoint を維持する

###### Red
- failing test:
  - import path / discovery regression
- expected failure:
  - file split 後に discover 対象や helper import が崩れる

###### Green
- minimum implementation:
  - `tests/test_init_update.py` を installer/update 側の正本にする
  - runtime tests を次の canonical file へ移行する:
    - `tests/cli_runtime/harness.py`
    - `tests/cli_runtime/test_new.py`
    - `tests/cli_runtime/test_active.py`
    - `tests/cli_runtime/test_sync.py`
    - `tests/cli_runtime/test_deps.py`
    - `tests/cli_runtime/test_import.py`
    - `tests/cli_runtime/test_validate.py`
    - `tests/cli_runtime/test_wrappers.py`
    - `tests/domain_runtime/test_ids.py`
    - `tests/domain_runtime/test_tree.py`
    - `tests/domain_runtime/test_deps.py`
    - `tests/domain_runtime/test_active.py`
    - `tests/presentation_runtime/test_markdown.py`
    - `tests/presentation_runtime/test_puml.py`
    - `tests/presentation_runtime/test_json_state.py`

###### Refactor
- cleanup target:
  - duplicated fixture/helper import
- invariants to keep green:
  - `python -m unittest discover -v`
  - 既存 assertion coverage

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

#### B1 — helper detachment
- purpose:
  - 段階移行で残した delegation を最後に除去する

##### I1 — detach legacy helper paths
- slice goal:
  - command と test が final public interface だけを見る状態へ揃える

###### Red
- failing test:
  - legacy helper removal regression
- expected failure:
  - thin delegation 前提の call site が残っている

###### Green
- minimum implementation:
  - old helper direct call を final layered API へ切り替える
  - dead helper を削除または private 化する

###### Refactor
- cleanup target:
  - compatibility shim の削除
- invariants to keep green:
  - import graph の layer 方向
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
- 対象:
  - docs / assets / workflow / skill / none
- 対応:
  - shipped runtime asset の user-facing docs / template / workflow への波及があれば更新する
  - no-op の場合も `report.md` に理由を記録する

### S99 — final diff review quality gate
- branch diff scope:
  - `git diff origin/main...HEAD`
  - 対象はこの branch の実装差分全体であり、step ごとの staged diff ではなく最終統合状態を見る
- required validation:
  - `python -m unittest discover -v`
  - requirement/design/plan との trace check
  - runtime packaging / shipped asset check
  - lowercase path 増分なし確認: `rg --files | rg '[A-Z]'`
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
  - shipped asset smoke check:
    - runtime asset をコピーした fresh repo 相当の test fixture で CLI entrypoint が起動する
    - `validate`, `deps check --json`, `active show`, `sync --force`, `new issue`, `import issue` の代表経路が少なくとも 1 回ずつ通る
  - touched file / AC-EC trace:
    - `AC-001`: runtime package tree / `app.py` 薄化差分
    - `AC-002`: `application/domain/infra/presentation` への責務分離差分
    - `AC-003`: `tests/test_init_update.py`, `tests/cli_runtime/harness.py`, `tests/cli_runtime/test_new.py`, `tests/cli_runtime/test_active.py`, `tests/cli_runtime/test_sync.py`, `tests/cli_runtime/test_deps.py`, `tests/cli_runtime/test_import.py`, `tests/cli_runtime/test_validate.py`, `tests/cli_runtime/test_wrappers.py`, `tests/domain_runtime/test_ids.py`, `tests/domain_runtime/test_tree.py`, `tests/domain_runtime/test_deps.py`, `tests/domain_runtime/test_active.py`, `tests/presentation_runtime/test_markdown.py`, `tests/presentation_runtime/test_puml.py`, `tests/presentation_runtime/test_json_state.py` の分割差分
    - `AC-004`: 重要 command regression test と artifact regression
    - `AC-005`: full suite green
    - `EC-001`-`EC-004`: 該当 regression test と reviewer finding 0 件
- reviewer approvals:
  - `spec_reviewer`: pass
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
