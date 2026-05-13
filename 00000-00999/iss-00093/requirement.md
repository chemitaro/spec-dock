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
  - GitHub issue を close した直後、GitHub issue の最新状態を取得した上で派生 state が更新される。

## スコープ
- 必須:
  - mutation 成功後に派生 state を自動更新する。
  - 自動 sync 対象は `new initiative`、`new epic`、`new issue`、`deps add`、`deps remove`、`delete`、`close`、`issue finish` とする。
  - 自動 sync は、対象 mutation 後に存在するリンク済み GitHub issue の最新状態を取得する。リンク済み GitHub issue が存在しない node は GitHub 取得対象外だが、派生 state のローカル投影には反映する。
  - `close` と `issue finish` は close 後の GitHub 状態を取得し、dashboard / index に close 済み状態を反映する。
  - `issue finish` 後の自動 sync は、`issue finish` の lifecycle contract である active state clear を維持する。issue branch 上で finish した場合も、branch-derived active restoration によって active issue が復元されてはならない。
  - mutation 本体が成功し、自動 sync だけが失敗した場合はコマンド全体を失敗扱いにし、mutation 成功済みであることと sync 失敗による stale / partial risk を明示する。
  - sync artifact 書き込み失敗時の exit code、stdout/stderr、部分更新リスクを既存のユーザー向け sync failure 表現と矛盾させない。
  - 自動 sync の有無がテストで観測できること。
- 禁止:
  - sync の失敗を黙殺して、成功した mutation と区別不能にしない。
  - 同じ同期結果を複数の不整合な形式で表示しない。
  - provider source を飛ばして dogfooding workspace だけを修正しない。
  - 今回の実装では `--no-auto-sync` などの opt-out オプションを追加しない。
- 対象外:
  - `active set` / `active clear` の自動 sync 対象化。active pointer と既存 agent state の active fields patch は既存責務として扱う。
  - `new doc` の自動 sync 対象化。node tree / dependency projection への影響が薄いため、この Issue では対象外とする。
  - 手動編集された `.meta.json` の監視やファイルシステム常駐 watcher。
  - GitHub API の新規永続 cache 設計。
  - 既存 command 名や CLI 引数の破壊的変更。

## 境界
- 常に行う:
  - 対象 mutation が成功した後に、リンク済み GitHub issue の最新状態取得を含む派生 artifact 更新を実行する。
  - 自動 sync の成功・失敗を CLI で観測可能にする。
  - 自動 sync 失敗時は non-zero exit とし、mutation 本体の成功済み状態、artifact の stale / partial risk、手動 recovery command を表示する。
- 判断が必要:
  - なし。対象コマンド、GitHub 状態取得、失敗時の non-zero 扱い、opt-out 不要はユーザーヒアリングで確定済み。
- 行わない:
  - mutation 前の preflight sync をこの Issue の主目的にしない。
  - 自動 sync を回避する CLI オプションを追加しない。

## 非交渉制約
- 既存の layered architecture を崩さない。
- `src/spec_dock/assets/spec_dock/...` を provider-side source of truth として変更する。
- 既存のユーザー向け sync failure semantics と矛盾しない。
- テストは hermetic にし、live GitHub へ依存しない。

## 前提
- `import_node` には post-import sync の前例がある。
- `new initiative/epic/issue` は GitHub issue linkage を持つ通常経路を対象とする。
- 既存データに local-only node が含まれる場合でも、リンク済み GitHub issue だけを取得対象にし、local-only node のローカル投影は維持する。

## 受け入れ条件
- AC-001:
  - アクター: ユーザー
  - 前提: `new initiative` が成功する
  - 操作: `./spec-dock/scripts/spec-dock new initiative ...`
  - 期待結果: 新 initiative 作成後にリンク済み GitHub issue の最新状態取得を含む自動 sync が実行され、`.agent/index-all.json`、`.agent/index.json`、`dashboard.md` に新 initiative が反映される
  - 観測点: CLI 出力、artifact の mtime / 内容、runtime test
- AC-002:
  - アクター: ユーザー
  - 前提: 既存 initiative があり、`new epic` が成功する
  - 操作: `./spec-dock/scripts/spec-dock new epic ...`
  - 期待結果: 新 epic 作成後にリンク済み GitHub issue の最新状態取得を含む自動 sync が実行され、`.agent/index-all.json`、`.agent/index.json`、`dashboard.md` に新 epic が反映される
  - 観測点: CLI 出力、artifact の mtime / 内容、runtime test
- AC-003:
  - アクター: ユーザー
  - 前提: 既存 epic があり、`new issue` が成功する
  - 操作: `./spec-dock/scripts/spec-dock new issue ...`
  - 期待結果: 新 issue 作成後にリンク済み GitHub issue の最新状態取得を含む自動 sync が実行され、`.agent/index-all.json`、`.agent/index.json`、`dashboard.md` に新 issue が反映される
  - 観測点: CLI 出力、artifact の mtime / 内容、runtime test
- AC-004:
  - アクター: ユーザー
  - 前提: 2 つの issue が存在する
  - 操作: `deps add` または `deps remove`
  - 期待結果: `.meta.json` 更新後にリンク済み GitHub issue の最新状態取得を含む自動 sync が実行され、`.agent/deps-issues.json` と `deps-issues.puml` が更新される
  - 観測点: CLI 出力、artifact 内容、runtime test
- AC-005:
  - アクター: ユーザー
  - 前提: 削除対象 node が存在し、`delete` が成功する
  - 操作: `./spec-dock/scripts/spec-dock delete ...`
  - 期待結果: local tree の削除後に、残存するリンク済み GitHub issue の最新状態取得を含む自動 sync が実行され、削除対象は `.agent/index-all.json`、`.agent/index.json`、`dashboard.md`、依存 projection から消える
  - 観測点: CLI 出力、artifact 内容、runtime test
- AC-006:
  - アクター: ユーザー
  - 前提: linked GitHub issue を close できる gh stub がある
  - 操作: `close` または `issue finish`
  - 期待結果: close 後にリンク済み GitHub issue の最新状態を取得する自動 sync が実行され、派生 state が stale のまま残らない。`issue finish` の場合は active state clear が維持され、`.agent/active.json` と active symlink が対象 issue を復元しない
  - 観測点: CLI 出力、artifact 内容、active state、runtime test
- AC-007:
  - アクター: エージェント
  - 前提: post-mutation sync の artifact write が失敗する
  - 操作: mutation command を実行する
  - 期待結果: コマンド全体は non-zero exit になり、mutation 成功と artifact stale / partial failure が区別でき、再実行 guidance が出る
  - 観測点: exit code、stderr/stdout、runtime test
- AC-008:
  - アクター: ユーザー
  - 前提: 対象 mutation command を実行する
  - 操作: help / parser / command behavior を確認する
  - 期待結果: `--no-auto-sync` などの opt-out option は存在しない
  - 観測点: CLI help、parser test

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
- EC-004:
  - 条件: GitHub 状態取得を伴う自動 sync が失敗する
  - 期待: mutation 本体が成功済みの場合でもコマンド全体は non-zero exit になり、GitHub sync 失敗と recovery guidance を表示する
  - 観測点: gh stub failure test、CLI 出力、result object
- EC-005:
  - 条件: issue branch 上で `issue finish` が成功し、その直後に自動 sync が実行される
  - 期待: branch-derived active restoration により active issue が復元されず、finish 後の active clear 状態が維持される
  - 観測点: `.agent/active.json`、`spec-dock/active/issue`、CLI 出力、runtime test

## 用語（ドメイン語彙）
- mutation command:
  - spec-dock の source-of-truth となる node tree、`.meta.json`、active、または linked GitHub state を変更する command。
- derived artifact:
  - `spec-dock/.agent/*.json`、`spec-dock/dashboard.md`、`spec-dock/*.puml` など、sync で再生成される読み取り用 state。
- post-mutation sync:
  - mutation 成功後に内部的に実行される artifact refresh。
- GitHub 状態取得:
  - sync 対象内のリンク済み GitHub issue について、GitHub issue の最新 state / title など sync が扱う issue 情報を取得すること。local-only node は取得対象外とする。

## 未確定事項
- なし。

## ヒアリング結果
- 2026-05-13:
  - 自動 sync 対象は `new initiative/epic/issue`、`deps add/remove`、`delete`、`close`、`issue finish` とする。
  - 自動 sync は基本的に GitHub issue 情報を取りに行く。`close` / `issue finish` 後も GitHub 状態を取得する。
  - mutation 本体成功後に自動 sync が失敗した場合、コマンド全体は失敗扱いにする。
  - opt-out option は不要。この Issue では実装しない。
