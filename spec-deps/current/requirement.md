---
種別: 要件定義書（Issue）
ID: "issue-25"
タイトル: "巨大な app.py を複数 module に分割し tests/test_cli.py を領域別に再編する"
関連GitHub: ["https://github.com/chemitaro/spec-dock/issues/25"]
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-03-11"
親: ["#25"]
---

# issue-25 巨大な app.py を複数 module に分割し tests/test_cli.py を領域別に再編する — 要件定義（WHAT / WHY）

## 目的
- runtime CLI を、採用済み ADR に基づく `cli / commands / application / domain / infra / presentation` の layered architecture へ再編し、`app.py` の責務集中を解消する。
- `tests/test_cli.py` を、installer/runtime の境界と runtime command 契約の境界に沿って再編し、失敗原因の局所化と今後の refactor 耐性を上げる。
- 既存 CLI 契約、shipped asset 契約、テスト green を維持したまま、将来の `sync / deps / active / import` 変更コストを下げる。

## 背景・現状
- 現状の挙動:
  - runtime CLI の主要挙動は [app.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py) に集中している。
  - `new/import/active/sync/deps/validate` の実装、argparse、Git/GitHub 呼び出し、tree/deps 導出、artifact 出力が同ファイルに同居している。
  - テストは [test_cli.py](/srv/mount/spec-dock/tests/test_cli.py) の `TestCli` 1 クラスに集中している。
- 現状の課題:
  - `app.py` は command policy、domain rule、infra、副作用順序が混ざっており、変更時の影響範囲が読みにくい。
  - `_sync` や `_active_set` のような高結合ポイントが、import や deps 判定にも波及する。
  - `tests/test_cli.py` は helper とテスト本体が巨大に同居しており、失敗時の原因局所化が難しい。
  - 既存の部分 module 化 (`ids.py`, `github.py`, `render_md.py`, `render_puml.py`) と本体の境界が不揃いで、責務整理が中途半端な状態にある。
- 再現手順:
  1. [app.py](/srv/mount/spec-dock/src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py) を参照すると、entrypoint 以外の層責務が大半残っている。
  2. [test_cli.py](/srv/mount/spec-dock/tests/test_cli.py) を参照すると、installer/runtime/helper/command tests が単一ファイルへ集約されている。
- 観測点:
  - UI:
    - CLI help、stdout/stderr、exit code
  - HTTP:
    - 該当なし
  - DB:
    - 該当なし
  - Log:
    - CLI error/warn 出力
  - Filesystem:
    - `spec-dock/.agent/index*.json`
    - `spec-dock/tree*.json`
    - `spec-dock/deps-issues.*`
    - `spec-dock/dashboard.md`
    - active manifest / pathfile / generated node files
- 情報源:
  - [adr-001-runtime-cli-layered-architecture.md](/srv/mount/spec-dock/spec-deps/current/adrs/adr-001-runtime-cli-layered-architecture.md)
  - [001-disc-runtime-cli-refactor-analysis.md](/srv/mount/spec-dock/spec-deps/current/discussions/001-disc-runtime-cli-refactor-analysis.md)
  - [002-disc-runtime-cli-architecture-v2.md](/srv/mount/spec-dock/spec-deps/current/discussions/002-disc-runtime-cli-architecture-v2.md)
  - GitHub Issue #25

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - `spec-dock` を導入済み repo で runtime CLI を使う開発者
  - runtime asset を保守する開発者
  - runtime CLI 契約テストを更新・追加する開発者
- 代表シナリオ:
  - `sync/deps/active/import` の仕様変更時に、影響対象 module と対応テストを素早く特定したい。
  - shipped asset としての CLI 契約を維持したまま、内部実装だけを安全に再編したい。
  - test failure 時に「どの command 契約が壊れたか」をすぐに判断したい。

## スコープ
- MUST:
  - runtime CLI に、ADR で確定した layered architecture の骨格を導入する。
  - `app.py` を薄い entrypoint/live-shell delegation 中心へ縮小する。
  - runtime package 配下に、少なくとも `commands` `application` `domain` `infra` `presentation` の物理層を導入する。
  - `new/import/active/sync/deps/validate` の user-facing command 実装を `commands` 層へ移す。
  - command を跨いで共有される workflow を `application` 層へ移す。
  - `spec graph` の共有 rule を `domain` 層へ移す。
  - git/gh/fs/json/time などの外部副作用を `infra` 層へ移す。
  - JSON/Markdown/PUML など artifact 描画責務を `presentation` 層へ移す。
  - `tests/test_cli.py` を、最低でも `installer` と `runtime` の観点で分離し、runtime 側を command 契約単位へ再編する。
  - 既存 CLI 契約、artifact 契約、exit code 契約、green を維持する。
  - 最低合格構成として、以下を満たす:
    - `app.py` は CLI entrypoint/dispatch/error handling と live shell 起動に限定される
    - `commands` は `new` `import` `active` `sync` `deps` `validate` の入口を持つ
    - `application` は command を跨ぐ workflow orchestration を少なくとも 1 つ以上持つ
    - `domain` は `spec graph` の rule を少なくとも 1 つ以上保持する
    - `infra` は git/gh/fs/json/time の副作用責務を少なくとも 1 つ以上保持する
    - `presentation` は JSON/Markdown/PUML のいずれかの描画責務を少なくとも 1 つ以上保持する
- MUST NOT:
  - user-facing command 名、引数体系、標準出力/標準エラー契約、exit code を意図せず変更しない。
  - shipped asset の生成物パス/ファイル名を意図せず変更しない。
  - architecture 導入を名目に、過度な DDD/hexagonal 的抽象を一気に持ち込まない。
- OUT OF SCOPE:
  - 新しい user-facing command の追加
  - CLI 機能拡張そのもの
  - GitHub integration 仕様変更
  - installer 側の大規模再設計
  - `design.md` レベルの詳細 interface 固定

## 境界
- Always:
  - architecture は `hybrid layered` を前提とする。
  - domain は `spec graph` を中心概念に置く。
  - command は user-facing 契約の入口として維持する。
- Ask:
  - layer 名や module tree に非自明な命名分岐が出る場合
  - scope を超えて test strategy を大きく増やす場合
  - shipped asset 契約に見える変更が必要な場合
- Never:
  - `helpers.py` / `utils.py` に雑多ロジックを退避するだけで終わらせない。
  - `domain` から `gh` `git` `subprocess` `Path.write_text` `print` に依存させない。
  - `application` を飛ばして workflow を再び command 側に押し戻さない。

## 非交渉制約
- 既存 CLI 契約を維持すること。
- 既存 artifact 契約を維持すること。
- `sync --force`、`deps check` の readiness/exit code、`active set` の副作用順序、`import -> sync` の再生成契約を壊さないこと。
- shipped asset としての runtime code 変更であることを踏まえ、tests と asset layout を同時に整合させること。
- パス命名は lowercase を維持すること。

## 前提
- architecture 方針は ADR `adr-001` で accepted 済み。
- 現時点の issue 文脈では、`spec-deps/current` はこの issue の正本として扱う。
- 詳細な interface や移行順序は次の design で確定する。

## 受け入れ条件
- AC-001:
  - Actor:
    - runtime asset 保守者
  - Given:
    - 現状の runtime CLI 実装が `app.py` に集中している
  - When:
    - Issue #25 の変更後の構成を参照する
  - Then:
    - `app.py` は entrypoint/dispatch/error handling/live shell 起動中心に縮小され、`commands` `application` `domain` `infra` `presentation` の物理層が runtime package 配下に存在する
  - 観測点:
    - runtime package の directory/module tree
    - `app.py` 内に live shell path から到達する command 実装本体が残っていないこと
    - `cli/bootstrap.py` が `app.py` を composition root / application wiring surface として参照していないこと
    - `app.py` に残る legacy helper は dormant compatibility code に限られ、`main()` / `cli/bootstrap.py` / `commands/*` から到達しないこと
    - layer ごとのファイル配置
    - `commands` `application` `domain` `infra` `presentation` の各層に少なくとも 1 つ以上の実責務 module が存在すること
- AC-002:
  - Actor:
    - runtime asset 保守者
  - Given:
    - `sync` `active` `deps` `import` が shared rule を持つ
  - When:
    - 変更後の構成を参照する
  - Then:
    - shared rule と workflow と外部副作用と描画責務が、`application` `domain` `infra` `presentation` に役割分離されている
  - 観測点:
    - `application` が command を跨ぐ use case orchestration を持つこと
    - `domain` が `spec graph` の rule を持ち、`subprocess` `gh` `git` `Path.write_text` `print` に依存しないこと
    - `infra` が git/gh/fs/json/time を扱うこと
    - `presentation` が JSON/Markdown/PUML 描画を担うこと
    - `commands` が workflow の本体や renderer 実装や direct fs/git/gh 呼び出しの置き場になっていないこと
- AC-003:
  - Actor:
    - テスト保守者
  - Given:
    - 現状の `tests/test_cli.py` が巨大である
  - When:
    - 変更後の test 構成を見る
  - Then:
    - 少なくとも installer/runtime の分離と、runtime の `new` `active` `sync` `deps` `import` `validate` `wrappers` を基準とした物理分割が確認できる
  - 観測点:
    - test file layout
    - helper 抽出の位置
    - runtime 契約テストの command 単位対応
- AC-004:
  - Actor:
    - runtime CLI 利用者
  - Given:
    - 既存の command usage と generated artifact を利用している
  - When:
    - 変更後に既存 command/test を実行する
  - Then:
    - user-facing CLI 契約と generated artifact 契約は維持される
  - 観測点:
    - command names
    - args/help
    - stdout/stderr
    - exit codes
    - generated file paths/names
    - generated JSON/Markdown/PUML の content shape と主要内容
    - scaffold collision 時の fail-fast no-write 挙動
    - 次の重要契約に対する明示的な回帰テストが存在し、通過すること:
      - `sync --force`
      - `deps check` の readiness/exit code
      - `active set` の副作用順序/guard
      - `import -> sync` の再生成契約
- AC-005:
  - Actor:
    - CI/開発者
  - Given:
    - existing regression tests がある
  - When:
    - test suite を実行する
  - Then:
    - green を維持し、architecture refactor による regression を出さない
  - 観測点:
    - `python -m unittest discover -v`
    - 重要契約テストが新しい test layout でも引き続き実行されること
## 例外・エッジケース
- EC-001:
  - 条件:
    - architecture 分割途中で command と新 layer が並存する
  - 期待:
    - 互換ラッパーまたは段階移行で挙動互換を維持する
  - 観測点:
    - `app.py` から新 module への委譲
    - rollback 可能性
- EC-002:
  - 条件:
    - `sync` と `import` の共通処理を移設する
  - 期待:
    - `import` 後の再生成契約が保たれ、`import -> sync` の依存が壊れない
  - 観測点:
    - import command behavior
    - generated artifacts
- EC-003:
  - 条件:
    - `active set` と `deps check` の共通 rule を整理する
  - 期待:
    - `deps` readiness 判定と `active set` の guard/order が変わらない
  - 観測点:
    - exit codes
    - warning/error messages
    - active manifest / pointer side effects
- EC-004:
  - 条件:
    - rendering を presentation 層へ移す
  - 期待:
    - JSON/Markdown/PUML の出力内容と保存先契約は変えない
  - 観測点:
    - rendered file contents
    - output file paths

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - runtime CLI の `sync` 実装再編
  - Output:
    - `sync` command policy は commands/application に、deps/tree/status derivation は内側 layer に、render/write は presentation/infra に整理される
- EX-002:
  - Input:
    - CLI test 再編
  - Output:
    - installer/runtime が分離され、runtime tests は command 契約単位のファイルへ整理される

## 用語（ドメイン語彙）
- TERM-001:
  - `hybrid layered architecture`
  - 外側に command を残しつつ、実責務境界を `commands / application / domain / infra / presentation` に置く構成
- TERM-002:
  - `spec graph`
  - `Node / tree / ids / deps / active / status` を中心とする runtime CLI の共有ルール集合
- TERM-003:
  - `command policy`
  - 引数解釈、exit code、stdout/stderr、副作用順序のような user-facing 契約
- TERM-004:
  - `artifact contract`
  - JSON/Markdown/PUML など generated files の path/name/content shape と主要内容に関する互換契約

## 未確定事項
- Q-001:
  - 質問:
    - 各 layer の物理ファイル粒度をどこまで細かく切るか
  - 選択肢:
    - A:
      - layer ごとに最小限のファイル数で導入する
    - B:
      - 初回から細粒度に分割する
  - 推奨案:
    - A
  - 影響範囲:
    - 実装差分量
    - 初期複雑性
    - import 循環リスク
