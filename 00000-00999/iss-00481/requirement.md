---
種別: 要件定義書（Issue）
ID: "iss-00481"
関連GitHub: ["#481"]
状態: "draft"
最終更新: "2026-10-31"
---

# iss-00481 Fix Template Link Tests In Linked Worktrees — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

## 目的
リンク付きの worktree でも `tests/unit/infra/test_authoring_kit_assets.py` が、CI や clean な checkout と同じ結果になる。

## 背景
作業用 worktree では `spec-dock/initiatives` が catalog（main チェックアウトの `spec-dock/.canonical`）への絶対パスのリンクである（epic-00424 R-B2）。雛形リンクのテストは、旧入れ子の置き場の上で `Path.resolve()` を使うため、リンクをたどって main 側へ移り、12件が落ちる。epic-00425 の #472、#475 の担当も同じ失敗を報告した。

## 観測可能な要件
- 雛形の相対リンクが、雛形を置く場所から見て配布ガイドを指すことを、リンクの有無に関わらず確かめる。
- この worktree でも、clean な checkout でも、同じ結果になる。

## スコープ
- 対象: `tests/` 内の、旧入れ子の置き場の上で `resolve()` する検証。
- 対象外: 製品コード、雛形、ガイド。テストの意図（リンクの行き先の一致）は弱めない。

## 失敗・境界条件
- リンクの行き先のファイルが無い、またはガイドと別を指すときは、これまでどおり失敗する。

## 受け入れ条件
- 修正前、この worktree で12件が落ちる。修正後に通る。
- `make lint` と `uv run pytest`（全体）が、この worktree で通る。

## 制約・前提
- 編集は `tests/` とこの Issue の Scope のディレクトリだけ。
