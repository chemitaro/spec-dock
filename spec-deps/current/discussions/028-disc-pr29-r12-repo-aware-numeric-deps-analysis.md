---
種別: ディスカッション
ID: "disc-028"
タイトル: "PR29 R12 repo-aware numeric deps resolution analysis"
状態: "open"
作成者: "Codex CLI"
最終更新: "2026-03-19"
関連: ["issue-28-runtime-regression-bugs", "PR #29"]
---

# PR29 R12 分析

## 対象レビュー
- review comment id: `2959331231`
- path: `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- 指摘要旨:
  - current repo `#123` と foreign repo `other/repo#123` の共存を許した結果、既存の numeric deps ref `depends_on: [123]` が bare issue number 解決のままで曖昧化する

## 結論
- 妥当性: `valid`
- 修正要否: `必要`
- 優先度評価: `high`

## 根拠
- 現行 provider では cross-repo overlap を local-id fallback で許容している
- 一方 `infra/deps_reader.py` の numeric ref 解決は bare `issue_number` ベースで、repo 文脈を使っていない
- したがって既存 repo が `depends_on: [123]` で current repo issue を参照している状態で foreign `other/repo#123` を導入すると、numeric ref が `Ambiguous github.issue_number=123` に退行しうる

## 修正案
1. numeric deps ref を廃止する
2. overlap 時だけ numeric deps ref を fail にする
3. bare numeric deps ref を current repo 文脈で解決する

## 推奨案
- 最善案は `3`
- `current_repo_slug` が解決できる場合、bare numeric ref `123` は current repo issue `current/repo#123` を優先解決する
- `current_repo_slug` が解決できず、scoped/unscoped が混在する場合のみ fail-closed にする
- legacy app path が同じ bare issue number 解決を持つなら parity させる

## 推奨テスト
- 既存 `depends_on: [123]` が current repo issue を指している状態で foreign `other/repo#123` を追加しても、validate/sync が current repo issue を解決し続ける

## 構造
```plantuml
@startuml
title R12 numeric deps resolution

rectangle "existing deps.json" {
  [depends_on: [123]]
}

rectangle "graph after foreign import" {
  [current/repo#123]
  [other/repo#123]
}

[depends_on: [123]] --> [current repo context]
[current repo context] --> [current/repo#123]
[current repo context] -x [other/repo#123]
@enduml
```
