---
種別: interview
ID: "20260702t015343z-interview"
タイトル: "Phase 3 Delivery And Pull Request Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t014409z-02-interview"
  - "20260702t015012z-interview"
  - "20260702t014409z-research"
scope: "epic"
scope_id: "epic-00270"
created_at: "2026-07-02T01:53:43Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260702t014409z-02-interview-phase3-first-scope-interview.md"
  - "artifacts/20260702t015012z-interview-phase3-issue-slicing-flexibility-criteria.md"
  - "artifacts/20260702t014409z-research-phase3-repo-context-implementation-survey.md"
reflected_to: []
---

# 20260702t015343z-interview Phase 3 Delivery And Pull Request Boundary

## 正式質問として扱う理由

- 影響する artifact:
  - `requirement.md`:
    - Epic acceptance criteria と final delivery expectation に影響する。
  - `design.md`:
    - Provider-side assets と dogfooding mirror impact をどの統合単位で扱うかに影響する。
  - `plan.md`:
    - 最終品質ゲート Issue、PR readiness、Issue完了順、review repair loop の設計に影響する。
  - `ADR`:
    - 現時点では不要。
- chat 上の軽微な一問では足りない理由:
  - V3 は「可能なら1PR」「最終IssueでEpic品質ゲート/手動テスト/PR delivery」を想定しているが、前回回答で Issue slicing は柔軟にすることになったため、delivery boundary を明文化する必要がある。

## 質問の目的

- 対象者:
  - product maintainer / Epic owner
- 何を明確にする質問か:
  - この Epic を原則1本のPRとしてdeliveryするか、IssueごとのPR分割を通常選択肢に入れるか。
- 回答が後続判断へ与える影響:
  - Final quality Issue の責務、manual test evidence、PR creation timing、review repair loop、Epic completion gate が変わる。

## 質問

- pressure-test question:
  - この Epic は templates / skills / docs / tests をまたぐため、1PRにまとめると整合性確認はしやすい一方、PRが大きくなる可能性があります。どちらを優先しますか。
- 質問:
  - `epic-00270` のdeliveryは、原則として「Epic全体を1PRでまとめ、最後のIssueが品質ゲート・手動テスト・PR deliveryを担当する」形に寄せますか。それとも「IssueごとのPR分割」を通常の選択肢として plan に入れますか。
- 回答してほしいこと:
  - A / B / C のどれに近いかを教えてください。

## source-grounded context

- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - V3 `issue-06-epic-quality-gate-manual-tests-and-pr-delivery.md` は、Epic全体の final validation / manual tests / review repair / PR readiness を担当する critical Issue として定義されている。
  - V3 `quality-gate-plan.md` と `manual-test-and-delivery-checklist.md` は final quality gate をPR readinessと結びつけている。
  - `workflow_epic.md` は epic-wide pre-PR gate を持ち、base endpointからfinal endpointまでの全差分を対象に quality gate を置く方針を既に含む。
  - 前回回答では、6 Issue は暫定 baseline、追加 Issue / 再分割は中程度の gate で柔軟に許すと決まった。
- local context で解決できたこと:
  - Final quality / manual test / PR readiness は必要。
  - PR merge 自体は明示許可なしでは行わない。
  - raw manual-test workspaces は commit せず、report/artifact に evidence summary を残す。
- まだ人間判断が必要な理由:
  - PR単位は開発運用方針であり、repo facts だけでは1PR固定か分割許容かを決められない。

## 回答案

- Option A:
  - 原則1PR。V3の想定どおり、最後のcritical IssueがEpic全体の品質ゲート・手動テスト・review repair・PR deliveryを担当する。IssueごとのPR分割は例外。
- Option B:
  - 原則は1PRだが、PRが大きすぎる、reviewabilityが落ちる、または独立した価値/リスク境界が明確な場合は、IssueごとのPR分割を許す。分割した場合も最後にEpic統合品質ゲートを置く。
- Option C:
  - IssueごとのPR分割を通常方針にする。最後のIssueは全体PR deliveryではなく、Epic closeout / final report / integration verificationを担当する。

## Codex の分析

- 判断軸:
  - Provider-side templates / skills / docs / tests の整合性を一括で検証できるか。
  - PR reviewability と修正サイクルの重さ。
  - Final quality Issue の意味が明確か。
  - Issue slicing flexibility と矛盾しないか。
- tradeoff:
  - Option A はV3に最も忠実で、整合性確認が単純。一方、差分が大きい場合にPR reviewが重くなる。
  - Option B はV3のdelivery modelを保ちつつ、PR size / reviewability リスクへ対応できる。
  - Option C は小さなPRにしやすいが、Phase 3全体の整合確認が分散し、final quality Issue の責務が弱くなる。
- リスク:
  - 1PR固定にしすぎると、大きすぎるPRでreview repairが遅くなる。
  - PR分割を広く許すと、templates / skills / docs / tests の整合性がPR間で一時的に崩れる。
- 具体シナリオ / edge case:
  - Initiative templates と Epic templates は別Issueでも、片方だけmergeすると docs/skills との整合性が一時的に悪くなる可能性がある。
  - Smoke tests は前段テンプレート/skill更新と同じPRにある方が、テストが要求する新契約を同時に証明しやすい。
  - ただし diff が巨大化した場合は、provider template redesign と skill/docs/test updates を分ける方がreviewしやすい可能性がある。

## Codex の推奨案

- 推奨:
  - Option B。
- 理由:
  - V3の「可能なら1PR」「最後にEpic品質ゲート」を保ちながら、実際のdiff sizeやreviewabilityに応じた分割を許せる。
  - 前回決まった中程度 gate の Issue slicing flexibility と整合する。
  - 分割しても最後にEpic統合品質ゲートを残すため、全体整合性を失いにくい。
- 未回答時の影響:
  - `plan.md` の final delivery gate と PR readiness 条件を固定できない。

## ユーザー回答

- answer capture:
  - Option A を採用する。
  - 今回の Epic はそこまで大きく膨らまない想定なので、原則1つの Pull Request で delivery する。
  - Issue ごとの Pull Request 分割は現状行わない。
  - ただし、計画具体化の中で1PR方針に破綻が見えた場合は、その時点で分割を再検討する。
- 回答:
  - `epic-00270` は原則1PRで delivery する。最後の Issue が Epic 全体の品質ゲート、手動テスト、PR delivery を担当する。IssueごとのPR分割は現時点では plan に通常方針として入れず、必要になった場合に再検討する。
- 回答日時:
  - 2026-07-02

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Canonical Epic docs へどの粒度で V3 reference を取り込むか。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - `requirement.md` / `plan.md` / `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Epic規模の想定とV3のfinal quality Issue方針に基づき、原則1PR delivery が明示されたため採用する。PR分割は通常方針ではなく、1PR方針が破綻する場合の再検討事項として扱う。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Final delivery acceptance criteria に、原則1PR delivery と最終品質ゲートを反映する。
- `design.md`:
  - Provider/dogfooding mirror consistency review は Epic 全体の統合単位で扱う。
- `plan.md`:
  - Final quality Issue、PR delivery checklist、1PR方針、破綻時の再検討条件に反映する。
- `ADR`:
  - 今回は不要見込み。
- reflected_to 更新方針:
  - 回答後、canonical docs と report ledger に反映した時点で更新する。
- adoption reflection:
  - canonical docs へ反映するまでは、この interview artifact が user-approved evidence。`report.md` Evidence Adoption Ledger へ採用記録を残す必要がある。
