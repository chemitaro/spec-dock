---
種別: interview
ID: "20260619t023120z-interview"
タイトル: "Issue 210 Essential Scope Question"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00210"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00210"
created_at: "2026-06-19T02:31:20Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: []
---

# 20260619t023120z-interview Issue 210 Essential Scope Question

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Issue 210 の scope / non-scope / acceptance criteria が変わる。
  - `design.md`:
    - `spec-dock-epic-planning` skill と後続 `spec-dock-epic-execution` skill の責務境界、handoff artifact、docs routing が変わる。
  - `plan.md`:
    - 実装 step の対象ファイル、docs impact、Issue 211 への引き渡し条件が変わる。
  - `ADR`:
    - 現時点では ADR 予定なし。長期 default workflow として重い判断に拡張する場合だけ ADR candidate を検討する。
- chat 上の軽微な一問では足りない理由:
  - 回答は Issue 210 の canonical docs と Issue 211 の前提にまたがるため、回答前に source-grounded interview artifact として残す必要がある。

## 質問の目的 (必須)
- 対象者:
  - Product owner / workflow owner
- 何を明確にする質問か:
  - Issue 210 がどこまで Issue 211 の前提になる Epic planning completion / handoff contract を固定するか。
- 回答が後続判断へ与える影響:
  - Issue 210 の requirement/design/plan の scope、更新対象 docs/skills、Issue 211 の開始前提、並行可否が決まる。

## 質問 (必須)
- pressure-test question:
  - Issue 210 は「Epic planning skill の system-architect draft cycle を追加する」だけで閉じるべきか、それとも「Issue 211 がそのまま消費できる Epic planning completion / handoff contract」まで固定するべきか。
- 質問:
  - Issue 210 の要件として、`spec-dock-epic-planning` の first-read workflow に system-architect draft cycle を追加するだけでなく、後続 Issue 211 が使う前提として「Epic planning 完了時に何が揃っているべきか」まで固定しますか？
- 回答してほしいこと:
  - 下の Option A/B/C から近いものを選ぶか、別案を指定してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue #210 body
  - GitHub issue #211 body
  - `epic-00158/requirement.md`
  - `epic-00158/plan.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/authoring/decision-routing.md`
  - Issue 210 local `requirement.md` / `design.md` / `plan.md` / `report.md`
- local context で解決できたこと:
  - Issue 210 は Epic planning の workflow を扱い、Issue 211 は Epic planning 後の execution coordinator を扱う。
  - system-architect は canonical docs を直接編集せず、discussion draft evidence を作る。
  - Issue canonical docs は Issue planning workflow で正式化し、Epic planning 後の draft package は discussion evidence として扱う。
- まだ人間判断が必要な理由:
  - Issue 210 が Issue 211 の前提 contract をどこまで明文化するかは、後続実行の重さ、docs impact、scope 境界を変える owner-intent 判断である。

## 回答案 (必須)
- Option A:
  - Narrow: Issue 210 は `spec-dock-epic-planning/SKILL.md` の first-read workflow 追加を中心に閉じる。Issue 211 用 handoff は最小限の関連づけに留める。
- Option B:
  - Handoff-focused: Issue 210 で Epic planning completion / handoff contract まで固定する。具体的には Epic requirement/design/plan reviewer gate、system-architect draft adoption、Issue list/deps、cross-issue draft package、issue-local draft requirement/design の存在を、Issue 211 の入力条件として読めるようにする。
- Option C:
  - Broad: Issue 210 で planning skill だけでなく workflow docs / delegated authoring docs / templates まで広く整え、Issue 211 はほぼ execution skill 追加だけに集中できる状態まで進める。

## Codex の分析 (必須)
- 判断軸:
  - 後続 Issue 211 が迷わず実行できるか。
  - Issue 210 と 211 の責務が重複しないか。
  - 親 Epic の「skill は workflow spine、docs は詳細、templates は薄い scaffold」という境界を守れるか。
  - first wave の範囲を runtime gate / harness へ広げすぎないか。
- tradeoff:
  - Option A は小さいが、Issue 211 側で planning completion の定義を再発明しやすい。
  - Option B は Issue 210 と 211 の接続が最も明確で、scope も planning boundary に収まりやすい。
  - Option C は後続が楽になる一方、Issue 210 が広くなりすぎ、workflow docs/templates 整備 issue と混線しやすい。
- リスク:
  - Handoff contract を弱くすると、Issue 211 が execution coordinator に planning の未決事項を吸収してしまう。
  - Handoff contract を広げすぎると、Issue 210 が docs/templates 横断 cleanup になってしまう。
- 具体シナリオ / edge case:
  - 大きな Epic では cross-issue draft package がないと Issue 間の vocabulary / dependency / handoff がばらける。
  - 軽微な Epic では system-architect draft cycle を毎回強制すると workflow が重くなるため、skip reason の扱いが必要になる。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - #210 は #211 の前段なので、execution coordinator が消費する planning completion / handoff artifacts を #210 側で定義するのが自然。ただし execution cycle、issue start/finish、PR merge preparation は #211 に残すことで scope を保てる。
- 未回答時の影響:
  - Issue 210 の requirement/design/plan で、更新対象と acceptance criteria を確定できず、Issue 211 との境界が曖昧なままになる。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User selected Option B, with an explicit boundary refinement: Issue 210 and Issue 211 should remain independent Issues. Issue 210 may define and expose information that Issue 211 can reference, but Issue 210 must not make Issue 211 part of its own execution scope.
- 回答:
  - Option B が良い。前提として、Issue 210 と Issue 211 は独立した Issue とする。情報を参照するのは問題ない。
- 回答日時:
  - 2026-06-19

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - none

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger / Spec Authoring Gate
- 採用 / 棄却 / deferred の理由:
  - The answer fixes the scope boundary for Issue 210: define Epic planning completion and handoff artifacts as a planning contract, while keeping Issue 211 independent and responsible for Epic execution coordination.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Scope should require Issue 210 to define Epic planning completion / handoff contract: reviewer-gated Epic requirement/design/plan, system-architect draft adoption, Issue list/dependency registration, cross-issue draft package, and issue-local draft requirement/design as referenceable inputs.
  - Non-scope should explicitly say Issue 210 does not implement Epic execution coordination and does not make Issue 211 a subtask.
- `design.md`:
  - Design should separate producer/consumer boundary: Issue 210 produces planning/handoff guidance; Issue 211 may consume it but remains an independent issue.
  - Design should route execution cycle, issue start/finish, PR merge preparation, and full Epic execution loop to Issue 211.
- `plan.md`:
  - Plan steps should update epic planning skill/docs for planning completion and handoff contract, then verify that Issue 211 can reference the contract without duplicating execution responsibilities.
- `ADR`:
  - No ADR required from this answer alone.
- reflected_to 更新方針:
  - Update after canonical docs adopt this answer.
- adoption reflection:
  - Record adoption in Issue 210 report Evidence Adoption Ledger and Spec Authoring Gate when canonical requirement is updated.

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
