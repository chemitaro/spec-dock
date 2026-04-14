---
種別: disc
ID: "20260414t083309z-disc"
タイトル: "New epic rationale"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-14"
親: ["epic-00074"]
関連: ["#74", "epic-00048"]
---

# 20260414t083309z-disc New epic rationale

## 議題
- `epic-00048` ではなく、新しい epic として `epic-00074` を切り出すべきかを確認する。
- 今回の対象を、Codex CLI と GitHub Copilot の両方にまたがる sub-agent / config asset expansion として扱うかを固定する。

## 背景
- `epic-00048` は、host-neutral protocol、thin adapter skill、host adapter metadata までを完了済みの範囲として閉じている。
- 今回の依頼は、その延長である host-native custom agent だけに留まらず、Codex CLI 設定、GitHub Copilot 設定、そしてそれらに付随する sub-agent / agent 配備までを含む。
- これは単一の managed asset 追加ではなく、installer の managed asset inventory と host 別 source layout の契約を広げる話になる。
- 既存 epic に押し込むと、完了済みの thin adapter closure と新しい host-native asset expansion の boundary が曖昧になる。

## 選択肢
- Option A: `epic-00048` を拡張する
  - Pros:
    - 既存の host-adapter 文脈をそのまま使える。
    - follow-up としては見通しが良い。
  - Cons:
    - 完了済み scope と拡張 scope が混ざり、done boundary がぼやける。
    - host-native config asset の追加が、thin adapter scaffolding の review 対象を不必要に広げる。
    - これから追加される host や asset family を、既存 epic の契約に押し込めにくい。
- Option B: 新 epic `epic-00074` を作る
  - Pros:
    - 既存 epic の完了済み scope を壊さずに、拡張対象だけを別 portfolio に切り出せる。
    - Codex CLI 設定、GitHub Copilot 設定、sub-agent 配備を同じ value unit として整理できる。
    - 今後の host 追加や asset family 追加を、同じ epic family で扱いやすい。
  - Cons:
    - epic が 1 つ増える。
    - dependency と documentation の追跡が少し増える。

## 推奨案
- Option B を採用する。
- 理由は、今回の変化が「既存の host adapter を少し直す」ではなく、「複数 host にまたがる agent/config asset の配備契約を広げる」ためである。
- 既存 epic の closure を維持したまま、新しい capability を value-based に分離したほうが、後続の requirement / design / plan を読みやすく保てる。

## 未決事項
- 追加対象の host と asset family の詳細な一覧。
- Codex CLI 設定と GitHub Copilot 設定の source-of-truth 配置先。
- sub-agent / custom agent の命名と managed ownership のルール。

## 次アクション
- この epic を正本として、次に requirement / design / plan を埋める。
- 詳細が来たら、host ごとの asset class と installer contract を分解して issue 計画へ落とす。
