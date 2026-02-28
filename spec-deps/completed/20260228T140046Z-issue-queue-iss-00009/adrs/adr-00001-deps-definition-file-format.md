---
種別: ADR（Architecture Decision Record）
ID: "adr-00001"
タイトル: "依存定義ファイル（名前・形式・スキーマ）"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-02-24"
親: ["iss-00009"]
---

# adr-00001 依存定義ファイル（名前・形式・スキーマ）

## 結論（Decision） (必須)
- 採用: Option A（`deps.json` / JSON）
- 置き場所: 各ノード直下（initiative/epic/issue のディレクトリ）
- スキーマ（`schema_version: 1`）:
  - `depends_on`: 依存先の配列
    - 要素: spec-dock node id（`init-*` / `epic-*` / `iss-*`）または GitHub issue number（整数、または数字文字列）
- ファイルが無い場合: `depends_on=[]` として扱う（依存なし）

## 背景（Context） (必須)
- `meta.json` は SSOT として安定運用されており、依存関係を追加するためのスキーマ拡張/書き換えは避けたい。
- 依存は「人間が編集する」前提なので、シンプルで衝突しづらい形式が望ましい。
- runtime script は stdlib のみで動く必要がある（JSON 以外は追加依存を避けたい）。

## 選択肢（Options considered） (必須)
- Option A: `deps.json`（JSON）
  - 概要:
    - 各ノード配下（initiative/epic/issue）に `deps.json` を置き、`depends_on` 配列で依存先を列挙する。
  - 例（案）:
    - `{ "schema_version": 1, "depends_on": ["iss-00123", "epic-00010", "123"] }`
  - Pros:
    - stdlib で扱いやすい（`json`）。
    - スキーマ拡張がしやすい（将来 `note` 等を追加できる）。
  - Cons:
    - コメントが書けない（運用で困る可能性）。
    - JSON の末尾カンマ等で壊れやすい。
- Option B: `depends_on.txt`（プレーンテキスト）
  - 概要:
    - 1行1依存（空行/コメント許可）で列挙する。
  - Pros:
    - 人間が書きやすく、diff/merge も素直。
    - コメントを入れられる。
  - Cons:
    - 将来の拡張が難しい（付加情報を持ちにくい）。
    - 構文曖昧さ（空白/コメント/記法）を設計する必要がある。

## 判断理由（Rationale） (必須)
- 理由: runtime script（stdlib）のまま実装が単純で、後方互換を保ったままスキーマ拡張しやすい。
- 注意: JSON にコメントが書けないため、コメント需要が高い場合は将来 `deps.md` 等の補助を追加検討する。

## 影響（Consequences） (必須)
- Positive（良い点）:
  - 依存関係が `meta.json` から分離され、SSOT の安定性を維持できる。
- Negative / Debt（悪い点 / 将来負債）:
  - 選択した形式により、編集体験や将来拡張のしやすさが固定される。
- 影響範囲（コード/テスト/運用/データ）:
  - runtime script: 依存定義ファイルの探索・パース・バリデーション
  - templates: 空の依存ファイルを生成するか（任意）
  - docs: 依存定義の書き方のガイド追加
- 移行/ロールバック:
  - 初期導入は「ファイルが無ければ依存なし」として扱えるため、段階導入が可能。
- Follow-ups（追加の Epic/Issue/ADR）:
  - 依存定義のサンプル/ベストプラクティスの整備

## 参考（References） (任意)
- `spec-deps/completed/20260228T140046Z-issue-queue-iss-00009/requirement.md`（Q-001）
