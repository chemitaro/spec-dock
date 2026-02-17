---
種別: 要件定義書（Issue）
ID: "iss-local-00002"
タイトル: "active set の処理分離と checkout 制御の明確化"
関連GitHub: ["#2"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-02-17"
親: ["epic:TBD", "init-00002"]
---

# iss-local-00002 active set の処理分離と checkout 制御の明確化 — 要件定義（WHAT / WHY）

## 目的（ユーザーに見える成果 / To-Be） (必須)
- `active set` 実行時に「アクティブ化」と「ブランチ操作」を分離し、active 設定を常にローカルSSOT基準で安定実行できるようにする。
- 明示フラグでのみ checkout を実行し、要件定義フェーズ（initiative/epic）を `main` 上で安全に進められるようにする。

## 背景・現状（As-Is / 調査メモ） (必須)
- 現状の挙動（事実）:
  - `active set` は target 種別に応じて checkout と active 設定を密結合で処理している。
  - `node_id` 指定でも `github.issue_number` があるノードは checkout 分岐へ入る。
  - checkout 後に `github.issue_number` で再解決しており、ブランチ差分で「ノード未発見」になり得る。
- 現状の課題（困っていること）:
  - active 設定が失敗してもブランチだけ変わる（副作用が先に発生）。
  - 要件整理（initiative/epic）でも不用意に checkout が走る。
  - ロジックが複雑化し、意図しない再解決による不安定性がある。
- 再現手順（最小で）:
  1) `main` で `./spec active set init-00002` を実行（`init-00002` は `github.issue_number=2` を持つ）。
  2) ブランチが `2-codex-team-mcp` に切り替わった後、`No node found for github.issue_number=2` で失敗。
- 観測点（どこを見て確認するか）:
  - Git: `git rev-parse --abbrev-ref HEAD`
  - active: `spec-dock/.agent/active.json`
  - stderr: `active set` エラーメッセージ
- 実際の観測結果（貼れる範囲で）:
  - Input/Operation: `./spec active set init-00002`
  - Output/State: ブランチ変更後に active 設定失敗
- 情報源（ヒアリング/調査の根拠）:
  - Issue/チケット: ユーザー報告（2026-02-17）
  - ドキュメント: `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - コード:
    - `src/spec_dock/assets/spec_dock/scripts/spec-dock`（`_active_set`, `_find_node_by_github_issue_number`, `_parse_active_set_target`）
  - テスト:
    - `tests/test_cli.py`（`test_active_set_github_issue_number_requires_linked_node` など）

## 対象ユーザー / 利用シナリオ (任意)
- 主な利用者（ロール）:
  - spec-dock 利用者（要件整理・実装の両方を行う開発者）
- 代表的なシナリオ:
  - シナリオA: `main` のまま initiative/epic を active にして仕様文書を更新する。
  - シナリオB: issue を active にし、必要時のみ明示フラグで作業ブランチへ移動する。

### UML（任意） (任意)
```plantuml
@startuml
actor User
participant "spec active set" as Cmd
database "Local nodes (meta.json)" as SSOT
participant "Git checkout(optional)" as Git
database "active.json + active/**" as Active

User -> Cmd: active set <target> [--checkout|--no-checkout]
Cmd -> SSOT: resolve target (local-first)
Cmd -> Active: set active (always first)
alt --checkout
  Cmd -> Git: create/switch desired branch
end
@enduml
```

## スコープ（暴走防止のガードレール） (必須)
- MUST（必ずやる）:
  - `active set` は **ローカルノード解決→active設定** を先に完了する。
  - checkout は active 設定と分離し、明示フラグ時のみ実行する。
  - デフォルト挙動は checkout しない。
  - `--no-checkout` 指定時は checkout 処理を完全スキップする。
  - 数値指定でローカルノード未解決時は、checkout/active変更なしで失敗する。
  - initiative / epic / issue の active 設定を統一フローで扱う（不足レイヤーは placeholder）。
  - ノード解決はローカル優先（GitHub API 依存にしない）。
- MUST NOT（絶対にやらない／追加しない）:
  - active 決定を checkout 後の branch 推論に依存させない。
  - 未解決ターゲットでブランチ変更しない。
  - 自動 import や GitHub 側メタデータ更新を追加しない。
- OUT OF SCOPE:
  - `import` コマンドの仕様変更
  - `sync` の branch 推論アルゴリズム全体刷新
  - cross-repo URL 解決（owner/repo 対応）

## 境界（Always / Ask / Never） (必須)
- Always（常に守る）:
  - local SSOT（`spec-dock/initiatives/**/meta.json`）を唯一の解決基準にする。
  - エラー時は副作用最小（少なくとも未解決ターゲットでは副作用ゼロ）にする。
  - destructive でない Git 操作のみを使う。
- Ask（迷ったら相談）:
  - checkout 失敗時の終了コード方針（active成功/checkout失敗の扱い）
  - `--checkout` の適用範囲（issue 限定か、initiative/epic 含むか）
- Never（絶対にしない）:
  - `git reset --hard` / 強制 push / 履歴改変の自動実行
  - ローカル未解決を GitHub 自動参照で補完する仕様

## 非交渉制約（守るべき制約） (必須)
- 既存の active manifest 形式（`schema_version=2`, `initiative/epic/issue`）を維持する。
- 既存の placeholder 運用（active 未設定レイヤーは `system/active-none`）を維持する。
- 既存の `validate` 制約（`github.issue_number` 一意性）と整合する。
- Git 操作は不可逆操作を導入しない。

## 前提（Assumptions） (必須)
- ユーザーはローカル spec ツリーを先に作成/import 済みである。
- `active set` はローカル repo で実行される。
- `git` は利用可能である（checkout 指定時）。

## 判断材料/トレードオフ（Decision / Trade-offs） (任意)
- 論点: active 設定と checkout を結合するか分離するか
  - 選択肢A: 結合（現行）
    - Pros: 1コマンドで完結
    - Cons: 失敗時の副作用、分岐複雑化、要件整理フェーズと相性悪い
  - 選択肢B: 分離（採用）
    - Pros: ロジック単純化、失敗時挙動の予測可能性向上、運用意図に一致
    - Cons: checkout が必要な場合は明示が必要
  - 決定: B（分離）
  - 理由: 安全性・可読性・運用整合性を最優先するため

## リスク/懸念（Risks） (任意)
- R-001: 既存ユーザーが「自動checkout前提」で運用している
  - 影響: 期待挙動の変化
  - 対応: ヘルプ/README/リリースノートで明示
- R-002: checkout 失敗時に active だけ更新される設計への認識差
  - 影響: オペレーション混乱
  - 対応: stderr に「activeは更新済み」を明示

## 受け入れ条件（観測可能な振る舞い） (必須)
- AC-001:
  - Actor/Role: 開発者
  - Given: `init-00002` がローカルに存在し、`github.issue_number=2` を持つ
  - When: `./spec active set init-00002` を実行する（デフォルト）
  - Then: active は initiative に設定され、ブランチは変化しない
  - 観測点（UI/HTTP/DB/Log など）: `spec-dock/.agent/active.json`, `git rev-parse --abbrev-ref HEAD`
  - 権限/認可条件（ある場合）: なし
- AC-002:
  - Actor/Role: 開発者
  - Given: `github.issue_number=2` を持つローカルノードが一意に存在する
  - When: `./spec active set 2` を実行する（デフォルト）
  - Then: checkout せずに対象ノードを active 化できる
  - 観測点（UI/HTTP/DB/Log など）: `active.json`, `active/context-pack.md`, current branch
  - 権限/認可条件（ある場合）: なし
- AC-003:
  - Actor/Role: 開発者
  - Given: node 解決可能かつ `--checkout` 指定
  - When: `./spec active set <target> --checkout` を実行する
  - Then: active 設定後に branch 名 `<id>-<slug>`（不適合時 `<id>`）へ checkout/create する
  - 観測点（UI/HTTP/DB/Log など）: current branch, stderr/info log
  - 権限/認可条件（ある場合）: `git` 実行権限
- AC-004:
  - Actor/Role: 開発者
  - Given: `--no-checkout` 指定
  - When: `./spec active set <target> --no-checkout` を実行する
  - Then: checkout 関連処理を一切実行しない
  - 観測点（UI/HTTP/DB/Log など）: `git` 呼び出し回数0, current branch不変
  - 権限/認可条件（ある場合）: なし
- AC-005:
  - Actor/Role: 開発者
  - Given: `github.issue_number=<n>` のローカルノードが存在しない
  - When: `./spec active set <n>` を実行する
  - Then: エラー終了し、active/branch ともに変更されない
  - 観測点（UI/HTTP/DB/Log など）: stderr, `active.json` 差分なし, current branch不変
  - 権限/認可条件（ある場合）: なし

### 入力→出力例 (任意)
- EX-001:
  - Input: `./spec active set epic-local-00001`
  - Output: `initiative=init-local-00001, epic=epic-local-00001, issue=(none)` / branch不変
- EX-002:
  - Input: `./spec active set iss-00123 --checkout`
  - Output: active更新 + branch=`iss-00123-<slug>`

## 例外・エッジケース（仕様として固定） (必須)
- EC-001:
  - 条件: `github.issue_number=<n>` が複数ノードに重複
  - 期待: `Ambiguous github.issue_number=<n>` で失敗（副作用なし）
  - 観測点（UI/HTTP/DB/Log など）: stderr, active/branch不変
- EC-002:
  - 条件: `--checkout` 指定時に working tree が dirty
  - 期待: checkout は失敗（active 設定は維持）し、dirty理由を表示
  - 観測点: stderr, `active.json`, current branch
- EC-003:
  - 条件: slug が非ASCIIまたは無効ref
  - 期待: branch 名は `<id>` へフォールバック
  - 観測点: stderr warn, current branch

## 用語（ドメイン語彙） (必須)
- TERM-001: active 設定 = `active.json` と `spec-dock/active/*` を更新する処理
- TERM-002: checkout 処理 = branch を作成/切替する Git 操作
- TERM-003: local-first 解決 = target 解決に GitHub API を使わずローカル `meta.json` を優先すること

## 未確定事項（TBD / 要確認） (必須)
- Q-001:
  - 質問: フラグ名は `--checkout/--no-checkout` で確定するか
  - 選択肢:
    - A: `--checkout`（デフォルト no-checkout）+ `--no-checkout`
    - B: `--with-checkout` のみ
  - 推奨案（暫定）: A
  - 影響範囲: AC-003, AC-004, CLI互換性
- Q-002:
  - 質問: checkout 失敗時の終了コードとメッセージ方針をどうするか
  - 選択肢:
    - A: 非0終了（active更新済みを明示）
    - B: 0終了（warningのみ）
  - 推奨案（暫定）: A
  - 影響範囲: EC-002, CI/自動化スクリプト

## Definition of Ready（着手可能条件） (必須)
- [x] 目的が 1〜3行で明確になっている
- [x] MUST/MUST NOT/OUT OF SCOPE が書けている
- [x] Always/Ask/Never が書けている
- [x] AC/EC が観測可能（テスト可能）な形になっている
- [x] 観測点（UI/HTTP/DB/Log など）または確認方法が明記されている
- [x] 未確定事項が「質問/選択肢/推奨案/影響範囲」で整理されている

## 完了条件（Definition of Done） (必須)
- すべてのAC/ECが満たされる
- 未確定事項が解消される（残す場合は「残す理由」と「合意」を明記）
- MUST NOT / OUT OF SCOPE を破っていない

## 省略/例外メモ (必須)
- 該当なし
