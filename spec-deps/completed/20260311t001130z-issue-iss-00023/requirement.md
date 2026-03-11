---
種別: 要件定義書（Issue）
ID: "iss-00023"
タイトル: "runtime CLI の責務分割と sync 状態導出をリファクタリングする"
関連GitHub: ["#23", "https://github.com/chemitaro/spec-dock/issues/23"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-03-11"
親: []
---

# iss-00023 runtime CLI の責務分割と sync 状態導出をリファクタリングする — 要件定義（WHAT / WHY）

## 目的（ユーザーに見える成果 / To-Be） (必須)
- spec-dock 開発者が runtime CLI の構造を追いやすくなり、`sync` / `deps check` / `active set` の状態判断を安全に変更できるようにする。
- 利用者が README の例に従って操作したとき、実装済み CLI と食い違わずに使える状態へ戻す。

## 背景・現状（As-Is / 調査メモ） (必須)
- 現状の挙動（事実）:
  - runtime CLI の主要処理が `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` に集中している。
  - `_sync()` が preflight validate、GitHub fetch、cached snapshot 読み込み、progress/deps 導出、artifact 出力まで一括で担っている。
  - `--github` なしの `sync` は `.agent/index*.json` の cached status / github 情報を再利用する。
  - README に `new adr` という、実装済み CLI と一致しないコマンド例が残っている。
- 現状の課題（困っていること）:
  - 変更時の影響範囲が広く、責務境界が読み取りにくい。
  - cache 由来なのか GitHub 由来なのかがコード上で追いにくく、状態の意味が曖昧になりやすい。
  - ドキュメントが実装とズレていて、利用者を誤誘導する。
- 再現手順（最小で）:
  1) `README.md` の ADR 作成例を読む。
  2) 実際の runtime CLI help と突き合わせる。
  3) `app.py` の `_sync()` を読み、status 導出と cache 再利用箇所を追う。
- 観測点（どこを見て確認するか）:
  - UI: 該当なし
  - HTTP: 該当なし
  - DB: 該当なし
  - Log: CLI stderr/stdout、README 記述、テスト結果
- 実際の観測結果（貼れる範囲で）:
  - Input/Operation: `./spec-dock/scripts/spec-dock new adr --issue iss-00123 --title "Token rotation strategy"`
  - Output/State: `new` の subcommand に `adr` は存在せず失敗する
- 情報源（ヒアリング/調査の根拠）:
  - Issue/チケット: GitHub issue `#23`
  - ドキュメント: `README.md`
  - コード:
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py`（`_sync`, `_parse_args`, `main` / runtime CLI 契約と状態導出の中心）
    - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/github.py`（GitHub adapter の境界）
  - 画面/ログ/DB: CLI help / unittest 実行結果

## 対象ユーザー / 利用シナリオ (任意)
- 主な利用者（ロール）:
  - spec-dock 自体を保守する開発者
  - spec-dock を導入して日常利用する CLI 利用者
- 代表的なシナリオ:
  - 開発者が `sync` 周辺ロジックを修正し、既存挙動を壊さずに新しい helper/module に分離する
  - 利用者が README を読んで discussion/ADR 作成コマンドを実行する

## スコープ（暴走防止のガードレール） (必須)
- MUST（必ずやる）:
  - runtime CLI の `sync` 周辺の責務を分割し、少なくとも status/source 導出を独立した読みやすい単位にする。
  - cache 利用の意味をコード上で明示化し、GitHub 未接続時の状態の扱いを追いやすくする。
  - README の runtime CLI 利用例を実装と一致させ、とくに discussion/ADR 作成まわりの誤記を解消する。
  - `deps check` / `active set` は今回の主たる refactor 対象ではなく、`sync` 周辺で抽出した helper と整合すること、および既存互換を保つことを確認対象とする。
  - 既存機能の互換を可能な限り維持し、回帰テストを通す。
- MUST NOT（絶対にやらない／追加しない）:
  - installer CLI の外部仕様を大きく変えない。
  - Issue/Epic/Initiative モデル自体を再設計しない。
  - 無関係な大規模 rename/move を行わない。
- OUT OF SCOPE:
  - GitHub 連携方式の全面刷新
  - 新規大機能追加
  - Initiative/Epic ワークフローの導入

## 境界（Always / Ask / Never） (必須)
- Always（常に守る）:
  - shipped assets の変更は API 変更として扱い、tests / README を合わせる。
  - lowercase path 制約を守る。
  - 既存 CLI 契約は可能な限り保つ。
- Ask（迷ったら相談）:
  - 互換を壊す CLI 変更が必要になった場合。
  - 大規模 module move/rename が必要になった場合。
- Never（絶対にしない）:
  - ユーザー未承認で破壊的な git 操作をしない。
  - 関係ないファイルの変更を混ぜない。

## 非交渉制約（守るべき制約） (必須)
- `python -m unittest discover -v` を通す。
- path 名に新たな大文字を導入しない。
- shipped assets 配下の実装変更に対応する docs/tests を必ず更新する。

## 前提（Assumptions） (必須)
- このリポジトリは spec-dock 自身の開発元であり、runtime 実装は `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/` にある。
- この開発環境には Initiative/Epic はなく、issue 単位で workflow を再現する。
- GitHub issue `#23` とブランチ `iss-00023-runtime-cli-refactor` を本作業のトレーサビリティ基点として使う。

## 判断材料/トレードオフ（Decision / Trade-offs） (任意)
- 論点: 全面分割するか、`sync` 周辺から段階的に分割するか
  - 選択肢A: command 全体を同時に再編する
  - 選択肢B: `sync` / status 導出 / README 整合を優先して段階的に整理する
  - 決定: 選択肢B
  - 理由: 影響範囲を制御しつつ、今回の主要課題に直接効くため

## リスク/懸念（Risks） (任意)
- R-001: helper/module 抽出時に import 循環が発生する
  - 影響: runtime 起動失敗
  - 対応: pure helper から先に切り出し、command routing は最後に整理する
- R-002: status 表現変更が既存 JSON 期待値を壊す
  - 影響: 多数の回帰テスト失敗
  - 対応: shape 互換を優先し、追加情報は補助フィールドで持つ

## 受け入れ条件（観測可能な振る舞い） (必須)
- AC-001:
  - Actor/Role: spec-dock 開発者
  - Given: runtime CLI の `sync` 周辺コードを読む
  - When: issue status/source 導出の流れを追う
  - Then: `app.py` から issue status 導出と progress 集計の責務が分離され、少なくとも dedicated helper/module を経由して追跡できる
  - 観測点（UI/HTTP/DB/Log など）:
    - runtime module 構成
    - `app.py` が dedicated helper/module を呼び出していること
    - 関連テスト
  - 権限/認可条件（ある場合）: 該当なし
- AC-002:
  - Actor/Role: spec-dock 開発者
  - Given: GitHub を使わない `sync` の実装と、それに依存する `deps check` / `active set` の互換挙動を確認する
  - When: 実装とテストを見る
  - Then: cached status の由来は internal helper/module の戻り値または内部表現で明示され、外部 JSON artifact の既存 shape は維持したまま GitHub 由来と混同しない。また `deps check` / `active set` は必要最小限の追従変更または互換確認に留まる
  - 観測点（UI/HTTP/DB/Log など）:
    - helper/module の戻り値・命名
    - 回帰テスト
    - 既存 artifact 互換
  - 権限/認可条件（ある場合）: 該当なし
- AC-003:
  - Actor/Role: spec-dock 利用者
  - Given: README の利用例を読む
  - When: `Usage (local scripts)` 節の runtime CLI 例、とくに discussion/ADR 作成コマンドを参照する
  - Then: 実装済み CLI と一致するコマンド例だけが記載されており、`new adr` のような未実装 command 例は残っていない
  - 観測点（UI/HTTP/DB/Log など）:
    - `README.md`
    - `--help` 出力
  - 権限/認可条件（ある場合）: 該当なし
- AC-004:
  - Actor/Role: CI / spec-dock 開発者
  - Given: 変更後のブランチ
  - When: テストを実行する
  - Then: `python -m unittest discover -v` が成功する
  - 観測点（UI/HTTP/DB/Log など）: unittest 実行結果
  - 権限/認可条件（ある場合）: 該当なし

### 入力→出力例 (任意)
- EX-001:
  - Input: `./spec-dock/scripts/spec-dock new doc adr --issue iss-00123 --title "Token rotation strategy"`
  - Output: ADR 文書が作成される
- EX-002:
  - Input: `sync` 実行時に GitHub 未接続かつ cached snapshot が存在する
  - Output: cached status 利用が内部的に区別可能な形で導出される

## 例外・エッジケース（仕様として固定） (必須)
- EC-001:
  - 条件: GitHub 情報が取得できない、または `--github` を付けない
  - 期待: cache 由来または unknown 由来の状態が、GitHub 最新状態と混同しにくい形で扱われる
  - 観測点（UI/HTTP/DB/Log など）: sync/deps 関連実装、対応テスト
- EC-002:
  - 条件: README の例と CLI 実装がズレる
  - 期待: 実装に合わせて README が更新され、少なくとも誤った `new adr` 記述は残らない
  - 観測点: `README.md`, runtime `--help`

## 用語（ドメイン語彙） (必須)
- TERM-001: runtime CLI = 導入先 repo に配置される `spec-dock/scripts/spec-dock` とその `spec_dock_runtime` 実装
- TERM-002: cached status = GitHub fetch を行わず `.agent/index*.json` 由来で再利用される issue 状態
- TERM-003: source = status がどこから導出されたかを示す由来情報

## 未確定事項（TBD / 要確認） (必須)
- 該当なし

## Definition of Ready（着手可能条件） (必須)
- [x] 目的が 1〜3行で明確になっている
- [x] MUST/MUST NOT/OUT OF SCOPE が書けている
- [x] Always/Ask/Never が書けている
- [x] AC/EC が観測可能（テスト可能）な形になっている
- [x] 観測点または確認方法が明記されている
- [x] 未確定事項が「質問/選択肢/推奨案/影響範囲」で整理されている

## 完了条件（Definition of Done） (必須)
- すべての AC / EC が満たされる
- 未確定事項が実装方針として収束し、残す場合は理由が明記される
- MUST NOT / OUT OF SCOPE を破っていない

## 省略/例外メモ (必須)
- Initiative/Epic が存在しないため、親は空配列で運用する
