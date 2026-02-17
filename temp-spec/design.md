---
種別: 設計書（Issue）
ID: "iss-local-00002"
タイトル: "active set の処理分離と checkout 制御の明確化"
関連GitHub: ["#2"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-02-17"
依存: ["requirement.md"]
親: ["epic:TBD", "init-00002"]
---

# iss-local-00002 active set の処理分離と checkout 制御の明確化 — 設計（HOW）

## 目的・制約（要件から転記・圧縮） (必須)
- 目的: `active set` を「active決定」と「checkout実行」に分離し、ローカルノード基準で安定化する。
- MUST:
  - active 設定を先に完了する。
  - checkout をフラグ制御（デフォルト無効）にする。
  - 数値指定未解決時の副作用ゼロを保証する。
- MUST NOT:
  - checkout 後の再走査で active ノードを再決定しない。
  - 未解決ターゲットで branch を変更しない。
- 非交渉制約:
  - active manifest/placeholder の既存仕様は維持。
  - 不可逆 Git 操作は導入しない。
- 前提:
  - ノード解決は local SSOT で完結する。

---

## 既存実装/規約の調査結果（As-Is / 99.9%理解） (必須)
- 参照した規約/実装（根拠）:
  - `src/spec_dock/assets/spec_dock/scripts/spec-dock`: 実装本体（`_active_set` が対象）
  - `tests/test_cli.py`: 現行挙動（checkout先行）を担保している
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`: 現行仕様説明
- 観測した現状（事実）:
  - `active set` が checkout を含む場合、checkout 後に `_scan_nodes` し直して `github.issue_number` 再解決している。
  - `kind=github_issue` では node 未解決でも checkout が先行し得る。
  - `sync` 呼び出しは `update_active=False` のため、active上書き自体は抑止されている。
- 採用するパターン（命名/責務/例外/DI/テストなど）:
  - 既存の small helper 関数分割（`_parse_*`, `_find_*`, `_ensure_*`）を踏襲する。
  - 例外は `RuntimeError` + actionable message を維持する。
- 採用しない/変更しない（理由）:
  - `sync` 全体設計変更はしない（本Issueの責務外）。
  - `meta.json` スキーマ変更はしない（互換性維持）。
- 影響範囲（呼び出し元/関連コンポーネント）:
  - CLI parser（`active set` オプション）
  - runtime `_active_set` 本体
  - テスト期待値
  - README/docs（利用者向け仕様）

## 主要フロー（テキスト：AC単位で短く） (任意)
- Flow for AC-001/AC-002（デフォルト no-checkout）:
  1) target を parse
  2) local-first で node を一意解決
  3) `active.json` + `active/**` を更新
  4) `sync(update_active=False)` を実行
- Flow for AC-003（`--checkout`）:
  1) 上記 active 更新を完了
  2) 解決済み node から desired branch 名を計算
  3) branch 作成/切替を実行（既存なら checkout、無ければ create）
  4) 成否をログ/終了コードへ反映

### UML（任意） (任意)
```plantuml
@startuml
skinparam monochrome true
actor User
participant "active set" as Cmd
database "nodes(meta.json)" as Nodes
database "active manifest" as Active
participant "git" as Git

User -> Cmd: active set <target> [--checkout]
Cmd -> Nodes: resolve target (local-first)
Cmd -> Active: write manifest + pointers
alt --checkout
  Cmd -> Git: checkout/create desired branch
end
Cmd --> User: result
@enduml
```

## データ・バリデーション（必要最小限） (任意)
- MODEL-001: ActiveSetOptions
  - Fields: `target: str`, `checkout: bool`
  - Constraints/Validation:
    - `target` は既存 parser ルールに準拠
    - `checkout` は `--checkout/--no-checkout` から確定
- MODEL-002: ResolvedTarget
  - Fields: `node: _Node`, `resolved_by: ("node_id" | "github_issue")`
  - Constraints:
    - ローカルノードへ一意解決できない場合は失敗

## 判断材料/トレードオフ（Decision / Trade-offs） (任意)
- 論点: checkout を `gh issue checkout` へ依存させるか
  - 選択肢A: 継続依存
    - Pros: GitHub運用と整合しやすい
    - Cons: 外部依存・副作用増・今回の複雑性の温床
  - 選択肢B: active set ではローカル Git 操作中心（採用）
    - Pros: 処理が単純、予測可能、副作用順序が明確
    - Cons: GitHub固有命名は利用者に委ねる場面がある
  - 決定: B
  - 理由: 本Issueの目的（分離と単純化）に最も整合するため

## インターフェース契約（ここで固定） (任意)
### API（ある場合）
- API-001: CLI
  - Request: `./spec active set <target> [--checkout | --no-checkout]`
  - Response: 成功時 `ok (active set)`、必要時 `checkout=...` を表示
  - Errors:
    - target 未解決
    - ambiguous target
    - checkout 失敗（`--checkout` 指定時）

### 関数・クラス境界（重要なものだけ）
- IF-001: `spec-dock::_active_set(specdock_dir: Path, target: str, checkout: bool) -> None`
  - Input: target, checkout mode
  - Output: active 更新（必要時 checkout）
  - Errors/Exceptions: `RuntimeError`（未解決/曖昧/checkout失敗）
- IF-002: `spec-dock::_resolve_active_target(nodes, target) -> _Node`
  - Input: scanned nodes, raw target
  - Output: resolved node
  - Errors/Exceptions: not found / ambiguous
- IF-003: `spec-dock::_maybe_checkout_after_active(repo_root, node, checkout) -> None`
  - Input: resolved node, checkout flag
  - Output: none
  - Errors/Exceptions: dirty tree / git failure（checkout有効時のみ）

### 例外/エラー契約（重要なものだけ） (任意)
- ERR-001: target未解決
  - 発生条件: 数値指定に対応するローカルノードなし
  - 呼び出し元への返し方: `RuntimeError("No node found ...")`
  - ログ/監視: stderr 出力、exit code 非0
- ERR-002: checkout失敗（dirty含む）
  - 発生条件: `--checkout` 指定かつ Git 操作失敗
  - 呼び出し元への返し方: 非0終了（active設定済みの場合は明示）
  - ログ/監視: stderr に失敗理由を出力

## 変更計画（ファイルパス単位） (必須)
- 追加（Add）:
  - なし（既存ファイル変更で対応）
- 変更（Modify）:
  - `src/spec_dock/assets/spec_dock/scripts/spec-dock`: parser と `_active_set` を分離設計へ変更
  - `tests/test_cli.py`: 既存期待の更新、新規回帰テスト追加
  - `README.md`: active set のデフォルト挙動とフラグ説明を更新
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`: checkoutポリシー記述更新
  - `src/spec_dock/assets/spec_dock/docs/guide.md`: workflow 説明更新
- 削除（Delete）:
  - なし
- 移動/リネーム（Move/Rename）:
  - なし
- 参照（Read only / context）:
  - `temp-spec/requirement.md`: 要件準拠確認

## マッピング（要件 → 設計） (必須)
- AC-001/AC-002 → IF-001 + IF-002（local-first解決→active先行）
- AC-003/AC-004 → IF-003（checkoutを後段かつフラグ制御）
- AC-005 → IF-002（未解決でfail-fast、副作用ゼロ）
- EC-001 → `_find_node_by_github_issue_number` / IF-002 の曖昧系エラー
- 非交渉制約 → 既存 `_write_active_manifest`, `_apply_active_pointers`, `_sync(update_active=False)` を維持利用

## テスト戦略（最低限ここまで具体化） (任意)
- 追加/更新するテスト:
  - Unit/CLI:
    - 既存 `active set` 系テストの期待値更新
    - `--checkout` 指定時のみ checkout されることの検証
    - 数値未解決で checkout されないことの検証
    - initiative/epic active で no-checkout が効くことの検証
- どのAC/ECをどのテストで保証するか:
  - AC-001 → `test_active_set_local_only_node_does_not_rename_branch` 拡張
  - AC-003 → 新規 `test_active_set_with_checkout_switches_branch`
  - AC-005 → `test_active_set_github_issue_number_requires_linked_node` 更新
  - EC-002 → dirty tree + `--checkout` テスト更新

### テストマトリクス（AC/EC → テスト） (任意)
- AC-001:
  - Unit: `tests/test_cli.py::test_active_set_github_linked_node_default_no_checkout`（新規）
- AC-003:
  - Unit: `tests/test_cli.py::test_active_set_with_checkout_uses_desired_branch`（新規）
- AC-005:
  - Unit: `tests/test_cli.py::test_active_set_github_issue_number_requires_linked_node`（更新）
- EC-001:
  - Unit: 既存 ambiguous 系テスト（必要なら追加）
- 実行コマンド（該当するものを記載）:
  - `python -m unittest tests.test_cli -k active_set`
  - `python -m unittest tests.test_cli`

## リスク/懸念（Risks） (任意)
- R-001: CLI破壊的変更（暗黙checkout廃止）
  - 影響: 既存スクリプトが branch 切替を期待している場合に挙動変更
  - 対応: docs/README更新 + release note
- R-002: active成功・checkout失敗の部分成功モデル
  - 影響: 利用者の理解コスト
  - 対応: 明確な stderr メッセージを追加

## 未確定事項（TBD） (必須)
- Q-001:
  - 質問: checkout を issue ノードのみに制限するか
  - 選択肢:
    - A: initiative/epic/issue 全て許可
    - B: issue のみ許可
  - 推奨案（暫定）: A（運用自由度優先）
  - 影響範囲: IF-003, AC-003
- Q-002:
  - 質問: checkout 失敗時の終了コードを非0固定にするか
  - 選択肢:
    - A: 非0固定（推奨）
    - B: warningで0
  - 推奨案（暫定）: A
  - 影響範囲: EC-002, CI連携

---

## ディレクトリ/ファイル構成図（変更点の見取り図） (任意)
```text
<repo-root>/
├── src/spec_dock/assets/spec_dock/scripts/
│   └── spec-dock                         # Modify
├── src/spec_dock/assets/spec_dock/docs/
│   ├── guide.md                          # Modify
│   └── reference_github.md               # Modify
├── tests/
│   └── test_cli.py                       # Modify
└── README.md                             # Modify
```

## 省略/例外メモ (必須)
- 該当なし
