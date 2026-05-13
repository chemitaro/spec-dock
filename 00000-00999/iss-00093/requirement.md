---
種別: 要件定義書（Issue）
ID: "iss-00093"
タイトル: "Automatic Sync After State Mutations"
関連GitHub: ["#93"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-05-13"
親: ["epic-00090", "init-local-00003"]
---

# iss-00093 Automatic Sync After State Mutations — 要件定義（WHAT / WHY）

## 目的
- spec-dock の構造、依存関係、GitHub 状態、active 状態に影響する mutation コマンドの成功後に、派生 state を自動更新する。
- `spec-dock/.agent/index*.json`、`spec-dock/.agent/deps-issues.json`、`spec-dock/dashboard.md`、PUML が古いまま残り、エージェントや人間が誤判断するリスクを下げる。

## 背景・現状
- 現状の挙動:
  - `import` 系はローカル作成後に `sync_after_import` を実行して派生 artifact を更新する。
  - `new initiative/epic/issue`、`deps add/remove`、`delete`、`close`、`issue finish` は成功後に sync artifact 更新を保証していない。
  - `active set` は active pointer と既存 agent state の active fields を patch するが、構造・依存・GitHub 状態の再投影ではない。
- 現状の課題:
  - ユーザーが `sync` を手動実行し忘れると、dashboard や集中管理 JSON が古いままになる。
  - 依存関係や close 状態を元に次の作業を判断するエージェントが、古い state を正として扱う可能性がある。
- 再現手順:
  1. `./spec-dock/scripts/spec-dock new issue ...` または `deps add/remove` を実行する。
  2. `spec-dock/.agent/index-all.json`、`spec-dock/.agent/deps-issues.json`、`spec-dock/dashboard.md` を確認する。
  3. 変更内容が反映されるには別途 `./spec-dock/scripts/spec-dock sync` が必要になる。
- 情報源:
  - `application/create_node.py`
  - `application/import_node.py`
  - `application/mutate_deps.py`
  - `application/delete_node.py`
  - `application/close_node.py`
  - `application/issue_lifecycle.py`
  - `application/sync_state.py`

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - spec-dock を使って issue / epic / initiative と実装作業を管理する開発者。
  - `.agent` state と dashboard を読みながら作業する AI エージェント。
- 代表シナリオ:
  - 新しい issue を作成した直後、dashboard と index に新 issue が反映されている。
  - 依存関係を追加・削除した直後、deps projection と PUML に反映されている。
  - GitHub issue を close した直後、GitHub 状態を取得できる場合は派生 state が更新される。

## スコープ
- 必須:
  - mutation 成功後に共通の post-mutation sync を実行する設計を追加する。
  - `new initiative/epic/issue`、`deps add/remove`、`delete`、`close`、`issue finish` の必要性を評価し、対象コマンドを明示する。
  - sync artifact 書き込み失敗時の exit code、stdout/stderr、部分更新リスクを既存 sync failure contract と整合させる。
  - 自動 sync の有無がテストで観測できること。
- 禁止:
  - sync の失敗を黙殺して、成功した mutation と区別不能にしない。
  - `sync` 実装を各 command handler に重複実装しない。
  - provider source を飛ばして dogfooding workspace だけを修正しない。
- 対象外:
  - 手動編集された `.meta.json` の監視やファイルシステム常駐 watcher。
  - GitHub API の新規永続 cache 設計。
  - 既存 command 名や CLI 引数の破壊的変更。

## 境界
- 常に行う:
  - ローカル mutation が成功した後に、派生 artifact 更新の成功・失敗を結果として観測可能にする。
- 判断が必要:
  - GitHub 状態を伴う `close` / `issue finish` では GitHub enabled sync を使うか、既存 `sync_after_import` と同様に local projection 更新に留めるか。
  - 失敗時に mutation 自体の成功を exit code 0 と扱うか、artifact stale リスクとして non-zero にするか。
- 行わない:
  - mutation 前の preflight sync をこの Issue の主目的にしない。

## 非交渉制約
- 既存の layered architecture を維持し、application 層の共通処理として扱う。
- `src/spec_dock/assets/spec_dock/...` を provider-side source of truth として変更する。
- sync artifact の failure semantics は `SyncCommandResult.artifact_failure` と整合させる。
- テストは hermetic にし、live GitHub へ依存しない。

## 前提
- `sync_state._sync_impl` は index/tree/deps/dashboard artifact の書き込み結果と失敗状態を返せる。
- `import_node` には post-import sync の前例がある。
- mutation command の結果型は必要に応じて post-sync result を保持できるよう拡張できる。

## 受け入れ条件
- AC-001:
  - アクター: ユーザー
  - 前提: 既存 epic があり、`new issue` が成功する
  - 操作: `./spec-dock/scripts/spec-dock new issue ...`
  - 期待結果: 新 issue 作成後に `.agent/index-all.json`、`.agent/index.json`、`dashboard.md` が更新される
  - 観測点: CLI 出力、artifact の mtime / 内容、runtime test
- AC-002:
  - アクター: ユーザー
  - 前提: 2 つの issue が存在する
  - 操作: `deps add` または `deps remove`
  - 期待結果: `.meta.json` 更新後に `.agent/deps-issues.json` と `deps-issues.puml` が更新される
  - 観測点: CLI 出力、artifact 内容、runtime test
- AC-003:
  - アクター: ユーザー
  - 前提: linked GitHub issue を close できる gh stub がある
  - 操作: `close` または `issue finish`
  - 期待結果: close 後に派生 state が stale のまま残らない。GitHub 状態反映方式は design で明示される
  - 観測点: CLI 出力、artifact 内容、runtime test
- AC-004:
  - アクター: エージェント
  - 前提: post-mutation sync の artifact write が失敗する
  - 操作: mutation command を実行する
  - 期待結果: mutation 成功と artifact stale / partial failure が区別でき、再実行 guidance が出る
  - 観測点: exit code、stderr/stdout、result object、runtime test

## 例外・エッジケース
- EC-001:
  - 条件: mutation が失敗する
  - 期待: post-mutation sync は実行されない
  - 観測点: sync runner / artifact writer の呼び出しなし
- EC-002:
  - 条件: `deps add` が既存 edge により `unchanged` を返す
  - 期待: artifact stale を生まないため sync 実行は不要、または unchanged として明示的に skip される
  - 観測点: result / CLI 出力
- EC-003:
  - 条件: artifact writer が途中失敗する
  - 期待: `failed_partial_or_stale` 相当の情報を保持し、手動 `sync` guidance を出す
  - 観測点: runtime test

## 用語（ドメイン語彙）
- mutation command:
  - spec-dock の source-of-truth となる node tree、`.meta.json`、active、または linked GitHub state を変更する command。
- derived artifact:
  - `spec-dock/.agent/*.json`、`spec-dock/dashboard.md`、`spec-dock/*.puml` など、sync で再生成される読み取り用 state。
- post-mutation sync:
  - mutation 成功後に内部的に実行される artifact refresh。

## 未確定事項
- Q-001:
  - 質問: `close` / `issue finish` の自動 sync は GitHub enabled をデフォルトにするか。
  - 推奨案: close 直後の状態反映が目的なので GitHub enabled を検討する。ただし hermetic test と gh failure handling を design で固定する。
  - 影響範囲: GitHub CLI 呼び出し回数、offline UX、failure semantics。
