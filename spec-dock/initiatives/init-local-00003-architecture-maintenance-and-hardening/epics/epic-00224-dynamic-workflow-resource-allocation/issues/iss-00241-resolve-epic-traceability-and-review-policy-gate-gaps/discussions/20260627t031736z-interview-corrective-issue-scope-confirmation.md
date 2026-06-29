---
種別: interview
ID: "20260627t031736z-interview"
タイトル: "Corrective Issue Scope Confirmation"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-27"
親: ["iss-00241"]
関連:
  - "iss-00239"
  - "20260627t025746z-research"
  - "20260627t030737z-disc"
scope: "issue"
scope_id: "iss-00241"
created_at: "2026-06-27T03:17:36Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "../../../discussions/20260627t025746z-research-epic-quality-gate-traceability-audit.md"
  - "../../../discussions/20260627t030737z-disc-spec-reviewer-epic-traceability-gate.md"
  - "20260627t031714z-research-clarification-before-requirement-authoring.md"
reflected_to: []
---

# 20260627t031736z-interview Corrective Issue Scope Confirmation

## 位置づけ
- 用途: `iss-00241` の要件定義に入る前に、corrective Issue のスコープを人間判断で確定する。
- authority default: `proposed`。ユーザー回答後に `user-approved` として採用し、`requirement.md` / `design.md` / `plan.md` へ反映する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、canonical docs へ反映されるまでは canonical authority ではない。

## 正式質問として扱う理由
- 影響する artifact:
  - `requirement.md`:
    - `iss-00241` が `iss-00239` の未解決 corrective scope を吸収するかどうかで、受け入れ条件が変わる。
  - `design.md`:
    - template scaffold / assurance classification の補修を同一設計に含めるか、別 Issue 依存として扱うかが変わる。
  - `plan.md`:
    - `iss-00239` を supersede / close する手順を含めるか、別 Issue を blocking dependency として残すかが変わる。
  - Epic `report.md`:
    - Epic closure gate で `iss-00239` を完了扱いにできる条件が変わる。
- chat 上の軽微な一問では足りない理由:
  - この判断は Epic 00224 の閉鎖可否、Issue 依存関係、後続の実装範囲、GitHub Issue lifecycle に影響する。
  - reviewer が `iss-00239` scaffold のまま残っていることを P1 block として指摘しており、曖昧にすると同じ取りこぼしが再発する。

## 質問の目的
- 対象者:
  - Epic owner / human decision maker。
- 何を明確にする質問か:
  - `iss-00241` を単一の corrective integration Issue として広げるか、`iss-00239` を独立 Issue として残すか。
- 回答が後続判断へ与える影響:
  - 要件定義・設計・計画の scope boundary、quality gate、issue close / supersede 方針が決まる。

## 質問
- pressure-test question:
  - Epic の取りこぼし修正を一つの corrective Issue に統合して閉じ切る方が良いか、それとも template scaffold synthesis の論点は既存 `iss-00239` に残して分離したまま進める方が良いか。
- 質問:
  - `iss-00241` のスコープに `iss-00239`（assurance classification 後に design / plan scaffold を合成する問題）の解決まで吸収し、`iss-00239` は superseded / closed として扱いますか？
- 回答してほしいこと:
  - `iss-00241` に吸収する / `iss-00239` を独立で残す / 別方針、のどれにするか。
  - 独立で残す場合、`iss-00241` の Epic closure gate では `iss-00239` を blocking dependency として扱うか、後続 defer として扱うか。

## source-grounded context
- 確認済みの docs / code / tests / ADR / discussions:
  - Epic audit report は、trusted base policy human gate 未実装、skill stale、guidance reflection 不足、`iss-00239` 未解決、Epic report 矛盾を指摘している。
  - spec-reviewer report は、`iss-00239` が scaffold のままであることを Epic close readiness の P1 block と判定している。
  - `iss-00239` は存在するが、現時点では要件・設計・計画・report が scaffold 状態である。
  - `iss-00241` は GitHub issue `#241` として作成済みで、Epic の取りこぼした要件を達成する corrective Issue として作成された。
- local context で解決できたこと:
  - review artifacts は Epic discussions に残し、`iss-00241` ではそれらを参照すればよい。
  - 要件定義書はまだ作成しない。
  - `issue start iss-00241 --force` は dirty worktree guard で止まっており、dependency readiness failure ではない。
- まだ人間判断が必要な理由:
  - `iss-00239` を吸収するかどうかは Issue lifecycle と作業範囲の判断であり、コードや既存 docs だけでは確定できない。

## 回答案
- Option A: `iss-00241` に吸収し、`iss-00239` は superseded / closed とする。
  - Epic closure gate を一つの corrective Issue に集約できる。
  - 既に scaffold のまま残っている Issue を別途 planning / execution する overhead を避けられる。
  - `iss-00241` の scope はやや大きくなる。
- Option B: `iss-00239` は独立 Issue として残し、`iss-00241` は review policy / skill contract / Epic docs / report reconciliation に限定する。
  - 論点の分離は明確になる。
  - Epic close までに少なくとも二つの corrective Issue を完了させる必要があり、今回の「取りこぼしを閉じ切る」意図からは遠くなる。
- Option C: `iss-00239` は後続 defer とし、`iss-00241` では Epic report に未完了として明記する。
  - 今回の PR merge-ready / Epic close-ready を急ぐ場合の逃げ道にはなる。
  - spec-reviewer が P1 block とした論点を残すため、Epic 完了条件とは矛盾しやすい。

## Codex の分析
- 判断軸:
  - Epic を閉じるために必要な traceability gap をこの Issue で解消できるか。
  - Issue 数を増やすことで、再び Epic-level decision が leaf Issue に落ちて取りこぼされないか。
  - `iss-00239` に既に実装やレビュー済み成果物があるか。
- tradeoff:
  - Option A は corrective work を集約できるが、scope が広くなる。
  - Option B は責務分離しやすいが、Epic close gate の管理が複雑になる。
  - Option C は短期的に楽だが、reviewer 指摘と整合しない。
- リスク:
  - `iss-00239` を空のまま残すと、Epic report の completion evidence が再び矛盾する。
  - `iss-00241` が広がりすぎると実装単位が重くなるが、今回の corrective nature では許容範囲と見ている。
- 具体シナリオ / edge case:
  - `iss-00241` が完了しても `iss-00239` が open scaffold のままだと、spec-reviewer は再び Epic close readiness を fail と判定し得る。
  - `iss-00239` を close する場合は、GitHub / SpecDock artifact に superseded reason と参照先 `iss-00241` を残す必要がある。

## Codex の推奨案
- 推奨:
  - Option A。`iss-00241` に `iss-00239` の未解決 corrective scope を吸収し、`iss-00239` は superseded / closed として扱う。
- 理由:
  - 今回のユーザー依頼は「様々な課題」「取りこぼした要件」を解決する新 Issue の作成であり、単一の corrective closure issue として扱う方が intent に合う。
  - `iss-00239` は現時点で scaffold 状態のため、独立成果物を保護する必要が低い。
  - Epic close readiness の観点では、open scaffold corrective Issue を残すこと自体が再レビュー失敗要因になる。
- 未回答時の影響:
  - `iss-00241` の requirement / design / plan に進むと scope が揺れるため、要件定義の前に確認が必要。

## ユーザー回答
- answer capture:
  - `iss-00241` に `iss-00239` の未解決 scope を吸収し、一つの corrective Issue として扱う。
  - この Issue は Epic の取り残しと品質ゲート上の問題修正を関心事とし、今回発見した複数の問題をまとめて解決する。
- 回答:
  - `iss-00241` に吸収する。
- 回答日時:
  - 2026-06-27

## 追加確認の要否
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし。

## 採用判断
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - Epic `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - ユーザーが `iss-00241` へ吸収し、一つの Issue で複数の取りこぼしを解決する方針を明示したため。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意
- `requirement.md`:
  - Option A の場合、template scaffold synthesis / assurance classification enforcement も `iss-00241` の受け入れ条件に含める。
- `design.md`:
  - Option A の場合、review policy gate / guidance reflection / template scaffold synthesis を一つの corrective integration design として整理する。
- `plan.md`:
  - Option A の場合、`iss-00239` supersede / close と evidence reflection を明示 step にする。
- ADR:
  - 必要に応じて新 ADR ではなく、既存 ADR reflection / Epic docs update として扱う。
- reflected_to 更新方針:
  - `iss-00241` の `requirement.md` / `design.md` / `plan.md` へ反映する。
- adoption reflection:
  - `iss-00241` は Epic 00224 の corrective integration Issue として、`iss-00239` の未解決 scope も含める。
