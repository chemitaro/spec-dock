---
title: PR #29 review R6 doctor current repo slug analysis
date: 2026-03-19
type: discussion
status: accepted
---

# 要約

- Codex review の指摘「`doctor` が `validate_graph_and_deps` に `current_repo_slug` を渡していないため、current repo `#123` と foreign repo `other/repo#123` の正常共存を ambiguity と誤診する」は妥当
- 修正は `doctor` でも `validate` / `sync` と同じ current repo slug 解決を使い、repo-aware uniqueness 契約と診断結果を一致させるのが最善

# 妥当性評価

- `validate_tree.py` と `sync_state.py` は `origin_github_repo_slug` から current repo slug を解決して validator に渡している
- 一方 `doctor.py` は同じ validator を呼ぶが `current_repo_slug` を渡していない
- そのため current repo 側の unscoped linkage と foreign scoped linkage が同じ issue number を持つ正常ケースでも、`doctor` だけが fail-closed ambiguity を返しうる
- これは「doctor は supported repair path を案内するが validate と矛盾しない」という requirement/design に反する

# 修正案

## 案A

- `doctor.py` に current repo slug 解決 helper を追加し、`validate_graph_and_deps(..., current_repo_slug=...)` を渡す

評価:

- 影響範囲が最小
- `validate` / `sync` と同じ文脈で doctor が診断できる
- 最も素直で安全

## 案B

- `doctor.py` から `validate_tree.py` 側 helper を再利用する

評価:

- 重複は減る
- ただし application module 間の依存が増えやすく、今回の bounded fix としてはやや重い

## 案C

- validator 自体を repo_root から current repo slug を内部解決する設計へ寄せる

評価:

- 呼び出し側の漏れは減る
- ただし domain/application 境界が崩れやすく、今回の corrective fix としては過剰

# 推奨案

- 案A を採用する
- `doctor` は use case として current repo slug を解決し、validator へ明示的に渡す
- 回帰テストは doctor 実行で current/foreign 同番号の正常 graph が false positive にならないことを固定する

# 必要なテスト

- current repo origin が設定された repo で、unscoped current issue `#123` と scoped foreign issue `other/repo#123` が併存する正常 graph を作る
- `doctor` 実行時に ambiguity / duplicate 系 finding が出ないことを確認する
- origin 未設定で current repo slug が解決不能な場合は、既存 fail-closed 契約を維持する
