---
種別: note
ID: "20260330t040314z-note"
タイトル: "implementation-handoff-summary"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-30"
親: ["iss-00038"]
関連: []
---

# 20260330t040314z-note implementation-handoff-summary

## 背景と目的 (必須)
- `iss-00038` は `epic-00033` の最後の open issue であり、実装担当者が着手時に迷わないよう、引き継ぎたい事実と注意点を短くまとめる。
- この note は requirement/design/plan の補助であり、「今回どこまでが担当範囲か」を素早く把握するためのメモである。

## 事実（観測結果） (必須)
- `epic-00033` の open issue は `iss-00038` のみである。
- `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` は完了済みである。
- `iss-00040` が担当していた `wrappers` / `domain` / `dogfooding parity` / `final regression` は current snapshot でも pass 済みで、`iss-00038` が再実行 ownership を持たない。
- `iss-00038` の残責務は `docs parity + final spec review record` のみである。
- targeted docs list は次の 6 ファイルである。
  - `src/spec_dock/assets/spec_dock/docs/reference_github.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_naming.md`
  - `src/spec_dock/assets/spec_dock/docs/reference_sync.md`
  - `spec-dock/docs/reference_github.md`
  - `spec-dock/docs/reference_naming.md`
  - `spec-dock/docs/reference_sync.md`
- 現時点では targeted docs list に provider-side / dogfooding 側の差分はない。
- close status の優先正本は `spec-dock/.agent/index-all.json` と `spec-dock/active/epic/report.md` である。
- `iss-00038` の完了条件は、docs の差分有無にかかわらず、`validate` / `sync` の成功結果と final spec review record を残すことである。

## 検討メモ (任意)
- 今回は「何か大きな実装を足す issue」ではなく、「最後の close-out packet を作る issue」と考えるとぶれにくい。
- docs parity は no-op で終わる可能性が高い。その場合でも no-op だったこと自体を evidence として扱う。
- upstream issue report には古い reviewer コメントや status ノイズが残っている箇所があるが、close 判定は generated state と epic report を優先する。
- `iss-00040` を再実行すると ownership が重複してしまうので、必要なのは参照であって再取得ではない。

## 次アクション (必須)
- [requirement.md](../requirement.md) / [design.md](../design.md) / [plan.md](../plan.md) を正本として読む。
- `S02` で targeted docs list を確認し、差分がなければ no-op parity evidence として記録する。
- `S03` で `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` の結果を取る。
- `S04` で `iss-00034` / `iss-00035` / `iss-00036` / `iss-00037` / `iss-00040` / `iss-00038` の evidence を束ねた final spec review record を `report.md` に書く。
- 実行中に scope が揺れたら、`iss-00040` の再実行ではなく blocker として切り分ける。

## 参考（References） (任意)
- [requirement.md](../requirement.md)
- [design.md](../design.md)
- [plan.md](../plan.md)
- [epic report](/srv/mount/spec-dock/spec-dock/active/epic/report.md)
- [iss-00040 report](/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/report.md)
