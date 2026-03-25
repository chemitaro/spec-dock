---
種別: note
ID: "008-note"
タイトル: "Spec Deps Curation Log"
状態: "accepted"
作成者: "Codex CLI"
最終更新: "2026-03-25"
親: ["init-local-00001"]
関連: [
  "004-adr-runtime-cli-layered-architecture.md",
  "005-disc-review-loop-and-outcome-matrix-lessons.md",
  "006-disc-repo-scope-and-create-state-lessons.md",
  "007-disc-manual-rerun-current-state.md"
]
---

# 008-note Spec Deps Curation Log

## 目的
- `spec-deps` 削除前に、何を新しい initiative discussion へ残し、何を残さないと判断したかを記録する。

## keep 方針
- 現在の architecture / product policy / dogfooding 再開判断に効く durable knowledge だけを残す。
- issue-28 の corrective patch を逐次追うための一時的な execution trace は残さない。
- 重複 ADR は複製せず、initiative 側に既にある文書を正本とする。

## 新たに移したもの
- `004-adr-runtime-cli-layered-architecture.md`
  - 旧 `spec-deps/current/adrs/adr-001-runtime-cli-layered-architecture.md` の durable な設計判断
- `005-disc-review-loop-and-outcome-matrix-lessons.md`
  - 旧 `047` / `048` の engineering lesson
- `006-disc-repo-scope-and-create-state-lessons.md`
  - 旧 `053` / `060` の durable な判断
- `007-disc-manual-rerun-current-state.md`
  - 旧 `062` の current-state 要約

## 移さなかったもの

### 1. 既存 initiative discussion と重複するもの
- `spec-deps/current/adrs/adr-002-spec-dock-dogfooding.md`
- `spec-deps/current/adrs/adr-003-spec-dock-agentic-cli-roadmap.md`

- 理由:
  - それぞれ既存の `001-adr-adopt-dogfooding.md`、`002-adr-agentic-cli-roadmap.md` に実質吸収済みである。

### 2. 実行時点依存の plan / issue trace
- `017`, `055`, `061` などの manual test plan
- `001` から `046`、`049` から `059` の issue-28 corrective analysis 群

- 理由:
  - 特定の review comment、scope 名、temporary workspace、repo provisioning、当時の exit gate に依存しやすい。
  - durable knowledge としては、統合後の `005` / `006` / `007` の方が再利用しやすい。

### 3. 中間結論で、後続判断により supersede されたもの
- `056` の exploratory-round root-cause

- 理由:
  - 後続の contract cleanup と manual rerun current-state により、現在参照すべき判断は `006` / `007` に再整理された。

## 削除前の確認メモ
- 実行証跡は `manual-tests/` 配下に残っている。
- 旧 `spec-deps` を削除する前提でも、initiative 側には最低限必要な ADR / discussion を移せた。
