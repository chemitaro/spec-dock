---
種別: disc
ID: "20260629t123000z-disc"
タイトル: "issue execution guidance false positive manual fallback"
状態: "draft | proposed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["iss-00247"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# issue execution guidance false positive manual fallback

## 対象論点

`./spec-dock/scripts/spec-dock guidance issue-execution` が active issue `iss-00247` について `state=blocked` / `reason_code=design-not-substantive` / `may_execute_approved_plan=false` を返した。

この issue の `design.md` / `plan.md` / `requirement.md` は既に issue-local docs として具体化され、fresh `spec-reviewer` pass も `report.md` に記録済みである。したがって、この guidance 出力は execution skill の stop condition と衝突する一方、canonical docs と human-approved plan の現状とは一致しない。

## 観測した事実

- 実行日時: 2026-06-29
- 実行コマンド: `./spec-dock/scripts/spec-dock guidance issue-execution`
- 出力:
  - `state: blocked`
  - `next_action: issue-planning-required`
  - `reason_code: design-not-substantive`
  - `active_issue: iss-00247`
  - `may_execute_approved_plan: false`
  - `authority: authorized_profile=standard, lite_candidate=false, obligation_source=authorized_profile`
- 既存記録:
  - `report.md` D-004 は、現行 workflow preflight が frontmatter の `template` 語に反応して `design-not-substantive` を返す false positive を記録している。
  - `report.md` は fresh `spec-reviewer` `019f133b-ee00-73f0-8303-e2791a5d7638` の `review_status=pass` を記録している。
  - `plan.md` section 9 は execution readiness checklist を満たしている。

## 判断

この guidance 出力は実行前の重要な観測結果として記録するが、今回の execution authority には使わない。以後の実装は次を source of truth とする。

- `spec-dock/docs/workflow_issue.md`
- `spec-dock/active/issue/requirement.md`
- `spec-dock/active/issue/design.md`
- `spec-dock/active/issue/plan.md`
- `spec-dock/active/issue/report.md`

## 採用先

- `report.md`:
  - runtime guidance false positive と manual fallback を Decision Ledger / session log / discovered issue として記録する。
- future implementation:
  - `guidance issue-execution` の `design-not-substantive` 判定が frontmatter title 中の `template` に過剰反応しないよう、workflow classifier の改善候補として扱う。

## ADR triage

- ADR candidate: no
- hard to reverse: no
- surprising without context: yes
- real tradeoff: yes
- ADR 化しない理由: issue-local execution tooling の false positive と fallback 記録であり、長期 architecture decision ではない。

## 次アクション

- S00 を manual fallback として開始する。
- 実行中に追加の guidance / command 不整合が見つかった場合は、この issue の discussion artifact または `report.md` に記録する。
