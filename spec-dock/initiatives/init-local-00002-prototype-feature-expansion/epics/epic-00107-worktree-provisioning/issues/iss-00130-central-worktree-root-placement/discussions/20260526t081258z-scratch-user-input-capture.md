---
種別: scratch
ID: "20260526t081258z-scratch"
タイトル: "User Input Capture"
状態: "draft | archived"
作成者: "iwasawayuuta"
最終更新: "2026-05-26"
親: ["iss-00130"]
関連: []
authority: "raw"
derived_from: []
reflected_to: []
---

# 20260526t081258z-scratch User Input Capture

## 位置づけ
- 用途: 未整理の発話、観察、思考、会話ログ、作業中の下書きを低摩擦に置く。
- authority default: `raw`。raw capture は非 authoritative であり、この文書だけで決定済み、調査済み、要件確定として扱わない。
- 長期保存する価値が出たら、文脈をもとに `interview` / `research` / `disc` / `adr` を新規作成するか、`requirement.md` / `design.md` / `plan.md` を修正する。
- 既存 `note` artifact は grandfathered だが、新規 raw capture には `scratch` を使う。

## メモ (必須)
- 2026-05-26 user input:
  - 現行の `spec-dock worktree create` は、product root と同じ親 path に worktree container を自動生成する。
  - Codex sandbox を有効にしている場合、その sibling container は current project writable root の外になり、作業権限がない問題がある。
  - Codex の editable root を project ごとに追加することはできるが、手動設定が project ごとに必要になり human error につながる。
  - 通常の product checkout と linked worktree は lifecycle が異なる。worktree は役割を終えたら削除する短命・一時的な開発 surface である。
  - この PC で開発する全 product の spec-dock managed worktree を 1 つの directory に集約し、その directory だけを Codex writable root として許可したい。
  - 集約 directory は `/Users/iwasawayuuta/workspace/worktrees` が候補。
  - shell environment variable に worktree root path をあらかじめ設定し、tool はその env var があることを前提にしたい。
  - env var がない状態で worktree を作成しようとした場合、worktree は作成せず、警告または明確な message を表示する。
  - この開発環境では `/Users/iwasawayuuta/workspace/worktrees` を作成し、zsh profile で CLI environment variable として export する想定。
  - worktree root 配下の namespace は各 product 名をそのまま使いたい。この repo では `spec-dock` が namespace に該当する。
  - namespace 内の個別 worktree 名は現行の命名 logic を基本的に維持する想定。ただし、より良い修正案があれば提案してほしい。
  - 要件定義を作る前に、既存コードベースを十分に理解し、必要なヒアリングを行う。
  - 調査、分析、ヒアリングは `discussions/` に document を積み重ねながら進める。

## 整理メモ（任意）
- facts:
  - user intent is not simply changing one path; it changes the placement contract from implicit sibling path to explicit environment-provided central root.
  - user wants missing env var to be blocking for `worktree create`, not fallback to old sibling behavior.
- questions:
  - exact env var name must be fixed.
  - whether spec-dock should create the root directory when env var is set but the directory does not exist needs confirmation.
  - namespace collision behavior across products with identical basename needs confirmation.
- decisions:
  - none yet; interview required before canonical requirement promotion.
- actions:
  - inspect current `worktree create` implementation, docs, tests, and local shell/workspace layout.
  - create research and discussion docs before editing `requirement.md`.
- links:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/worktree.py`
  - `tests/cli_runtime/test_worktree.py`
  - `src/spec_dock/assets/spec_dock/docs/reference_worktree.md`
- discard condition:
  - Once the canonical `requirement.md`, `design.md`, and `plan.md` reflect the accepted scope and this raw capture has been linked from report evidence, this scratch document can remain as raw provenance only.
