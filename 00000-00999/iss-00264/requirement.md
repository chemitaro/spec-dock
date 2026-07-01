---
種別: 要件定義書（Issue）
ID: "iss-00264"
タイトル: "Future node scaffold artifacts default"
関連GitHub: ["#264"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00264 Future node scaffold artifacts default — Issue 要件定義

## 目的
New initiative / epic / issue scaffold の future default を `artifacts/` に切り替え、`discussions/` の default creation を止める。既存 node は移行せず、old-only / mixed layout を valid に残す。

## 上位 trace
- Epic requirements: E-RQ-001, E-RQ-002, E-RQ-007.
- Epic acceptance criteria: E-AC-007, E-AC-008.
- Epic design decisions: D-005.
- Depends on: `iss-00262`, `iss-00263`.

## スコープ
- 必須:
  - Provider-side node templates/scaffolder を更新し、新規 initiative/epic/issue に `artifacts/` と `artifacts/rules.md` を用意する。
  - `discussions/` は new node default では作らない。
  - installer/init/update expectations と scaffold tests を更新する。
  - legacy nodes without `artifacts/` remain valid であることを守る。
- 対象外:
  - 既存 node の一括 migration。
  - existing `discussions/` の削除/移動。
  - `new artifact` command の詳細実装。

## 受け入れ条件
- AC-264-001 new scaffold:
  - new initiative/epic/issue scaffold は default で `artifacts/` を持つ。
- AC-264-002 no default discussions:
  - new scaffold は default で `discussions/` を作成しない。
- AC-264-003 rules:
  - `artifacts/rules.md` が provider-side source から配置される。
- AC-264-004 update compatibility:
  - `spec-dock update` は既存 `discussions/` を移動/削除せず、必要な future assets を追加できる。
- AC-264-005 old-only valid:
  - old-only fixture は validate で invalid 扱いされない。

## 検証期待
- Installer/scaffold tests in `tests/unit/infra/`.
- CLI runtime scaffold tests.
- `uv run pytest tests/unit/infra` focused lane。

## 依存
- `iss-00262`, `iss-00263`。
