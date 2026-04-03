---
種別: disc
ID: "20260402t045118z-disc"
タイトル: "Agent interface and invalid artifact prevention"
状態: "archived"
作成者: "Codex CLI"
最終更新: "2026-04-02"
親: ["epic-00048"]
関連: ["#48", "20260402t062520z-disc", "20260402t062520z-disc"]
---

# 20260402t045118z-disc Agent interface and invalid artifact prevention

## 議題
- この discussion の元内容をどこへ再配置したかを明示する。

## 背景
- 当初この discussion には、epic 本題である agent-facing interface / host adapter 戦略と、architecture-level governance で扱うべき invalid artifact prevention が混在していた。
- ユーザー判断により、前者は epic 本題へ戻し、後者は architecture initiative 側へ移管する方針となった。

## 選択肢
- Option A:
  - Pros:
    - このファイルに混在内容を残し続ける。
  - Cons:
    - epic の本題がぶれる。
- Option B:
  - Pros:
    - epic 本題の議論を別 discussion に復元し、invalid artifact prevention は architecture initiative 側へ移す。
  - Cons:
    - discussion が分かれる。

## 推奨案
- Option B を採用済み。
- epic 本題の議論は `20260402t062520z-disc-agent-facing-interface-and-host-adapter-strategy.md` に復元した。
- invalid artifact prevention / governance の議論は `init-local-00003` 配下の `20260402t062520z-disc-invalid-artifact-creation-prevention-and-governance.md` へ移管した。

## 未決事項
- なし。

## 次アクション
- epic-00048 では restored discussion を前提に requirement/design を詰める。
- invalid artifact prevention は architecture initiative 側で継続検討する。
