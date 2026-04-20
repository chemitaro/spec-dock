---
種別: research
ID: "20260417t023838z-research"
タイトル: "pr review and staging failure analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-04-17"
親: ["iss-00082"]
関連: ["#1778", "#1821", "#82"]
---

# 20260417t023838z-research pr review and staging failure analysis

## 調査目的 (必須)
- PR `#1821` の Codex review P1 が `spec-dock` runtime 側の bug かを切り分ける。
- staging workflow failure が今回の repo-local bugfix issue の修正対象かどうかを整理する。

## 調査方法 (必須)
- PR review comment の対象 file / 指摘内容を確認した。
- workflow run `24541771497` と `management_api_test` failure summary を確認した。
- branch diff の変更範囲と、`spec-dock` runtime path の責務を照合した。

## 調査結果 (必須)
- Codex の P1 指摘対象は `spec-dock/scripts/spec_dock_runtime/infra/fs_repo.py` で、`.meta.json` の `type` または `id` が欠けている malformed node を loader が silent skip している点だった。
- 指摘の論点は migration docs ではなく runtime の metadata integrity contract であり、本 repo の `spec-dock` 本体に属する。
- staging failure は既存 workflow `Test and Deploy for Staging` の `management_api_test` failure で、failing assertion は async outbox delivery の観測タイミング依存だった。
- failing assertion は `pending` / `in_progress` のみを期待していたが、実際には `delivered` まで進行していた。
- branch diff 上、management API 本体や staging workflow そのものは今回の spec-dock migration 差分で変更していなかった。

## 結論 (必須)
- repo-local actionable bug として追うべきなのは、`spec-dock` runtime 側の malformed metadata silent skip である。
- staging failure は external consumer app 側の flaky / overspecified integration assertion とみるのが自然であり、本 issue `iss-00082` の修正対象には含めない。
- したがって `iss-00082` は malformed metadata fail-fast に閉じ、staging failure は background evidence としてのみ参照する。

## リスク/制約 (任意)
- staging failure 自体の根本原因修正は別 issue / 別 repo トラックが必要になる可能性が高い。
- 本 research は issue scoping の材料であり、implementation proof ではない。

## 参考（References） (任意)
- GitHub PR comments on `#1821`
- GitHub workflow run `24541771497`
- job `management_api_test`
- `gh run view 24541771497 --job 71748942532 --log`
