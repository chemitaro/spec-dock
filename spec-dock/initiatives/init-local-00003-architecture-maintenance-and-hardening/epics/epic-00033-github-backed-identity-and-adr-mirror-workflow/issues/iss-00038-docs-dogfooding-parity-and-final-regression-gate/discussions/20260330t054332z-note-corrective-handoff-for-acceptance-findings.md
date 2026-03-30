---
種別: note
ID: "20260330t054332z-note"
タイトル: "corrective-handoff-for-acceptance-findings"
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-30"
親: ["iss-00038"]
関連: []
---

# 20260330t054332z-note corrective-handoff-for-acceptance-findings

## 背景と目的 (必須)
- `iss-00038` の実装は close-out 記録まで進んでいるが、acceptance review で report artifact の整合に関する corrective findings が 2 件見つかった。
- この note は、追加実装担当者が corrective work だけを最小差分で進められるようにするための handoff である。

## 事実（観測結果） (必須)
- 今回の corrective 対象は `report.md` のみが中心で、runtime や targeted docs contract の再実装は不要である。
- acceptance review で扱う論点は 2 件だけである。
  - `report.md` の front matter `状態` が `draft | approved` のままで曖昧
  - S04 記録に「未コミット」「final review pass 後に実施予定」が残っていて、実際の git history と矛盾
- コミットメッセージのフォーマット問題は今回の corrective scope 外であり、修正不要と明示されている。
- `iss-00040` の ownership を再度引き取る必要はない。
- 既存の S01-S04 は完了済みとして扱い、今回は追加 corrective step として S05/S06 を実施する。

## 検討メモ (任意)
- 今回の問題は実装欠陥ではなく、final close-out record の監査性・状態整合の問題である。
- そのため、最小差分で `report.md` の最終状態を actual git history / approved state に揃えるのが正解。
- requirement/design には corrective path を追加済みなので、実装担当者は plan の S05/S06 に従えばよい。

## 次アクション (必須)
- まず [requirement.md](../requirement.md)、[design.md](../design.md)、[plan.md](../plan.md) を読む。
- 特に plan の `S05` と `S06` だけを今回の実装対象として見る。
- `report.md` で次を修正する。
  - front matter の `状態` を単一の確定値へ正規化する
  - S04 のコミット記録を actual git history に合わせる
- 修正後に spec review を再度受け、corrective close-out が issue docs と整合していることを確認する。
- 既存の S01-S04 の完了記録は消したり書き換えたりせず、追加 corrective log として追記する。

## 参考（References） (任意)
- [requirement.md](../requirement.md)
- [design.md](../design.md)
- [plan.md](../plan.md)
- [acceptance review analysis](/srv/mount/spec-dock/spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00038-docs-dogfooding-parity-and-final-regression-gate/discussions/20260330t053149z-disc-acceptance-review-findings-analysis.md)
