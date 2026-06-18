---
種別: interview
ID: "20260617t154625z-interview"
タイトル: "Decision Boundary Primary Intent"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-18"
親: ["iss-00196"]
関連: []
scope: "issue"
scope_id: "iss-00196"
created_at: "2026-06-17T15:46:25Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "GitHub issue #196"
  - "spec-dock/active/epic/requirement.md"
  - "spec-dock/active/epic/design.md"
  - "spec-dock/active/epic/plan.md"
  - "spec-dock/docs/workflow_issue.md"
  - "spec-dock/docs/workflow_epic.md"
  - "spec-dock/docs/workflow_initiative.md"
  - "spec-dock/docs/workflow_spec_authoring.md"
  - "spec-dock/docs/workflow_clarification.md"
  - ".agents/skills/spec-dock-issue-planning/SKILL.md"
  - ".agents/skills/spec-dock-hub/SKILL.md"
  - "deep-consultant:019ed80a-0631-7543-bdfe-f5896e16e451"
  - "spec-dock/active/issue/discussions/20260618t000451z-disc-deep-consultant-decision-scope-synthesis.md"
reflected_to: []
---

# 20260617t154625z-interview Decision Boundary Primary Intent

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
    - issue scope / non-scope / acceptance criteria が変わる。
  - `design.md`:
    - docs / skills / templates のどこに gate を置くかが変わる。
  - `plan.md`:
    - implementation step 分割と review scope が変わる。
  - `ADR`:
    - durable policy として残すかどうかの判断に影響し得る。
- chat 上の軽微な一問では足りない理由:
  - 回答により、workflow docs / skills だけで閉じるか、templates まで更新するかが変わり、複数 artifact への反映と adoption evidence が必要になるため。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / user
- 何を明確にする質問か:
  - `iss-00196` の requirement phase で固定すべき scope boundary。
- 回答が後続判断へ与える影響:
  - 必須成果物、非スコープ、step 分割、review gate、docs / skills / templates の更新対象が決まる。

## 質問 (必須)
- pressure-test question:
  - この issue は「workflow docs / skills に decision routing gate を明文化する」だけで閉じるべきか、それとも「templates に Issue readiness / Epic planning checklist を追加する」まで含めるべきか。
- 質問:
  - `iss-00196` の今回の完了条件として、template 更新まで必須にしますか？
- 回答してほしいこと:
  - A / B / C / D のどれを採用するか。必要なら理由や境界条件も教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue `#196` は workflow docs / skills に Issue readiness gate, Epic planning gate, clarification routing を追加したいと述べている。
  - Parent epic `epic-00158` は provider-side skills / docs / templates の context surface cleanup を対象にしている。
  - Parent epic は runtime gate / automated harness を first wave blocker にしない。
  - `workflow_issue.md` は Issue を実装最小単位とするが、decision-only issue の検出 gate は薄い。
  - `workflow_epic.md` は Epic を設計の背骨とするが、Issue へ渡す decision set / carry-over uncertainty は薄い。
  - `spec-dock-issue-planning` skill は unresolved gaps を clarification / prior authoring phase へ戻すが、上位 scope へ戻す条件は first-read gate として薄い。
- local context で解決できたこと:
  - Runtime enforcement は今回の主対象外。
  - Provider-side source を authority とし、dogfooding mirror は検証対象。
  - Canonical `requirement.md` はまだ template なので、GitHub issue body と parent epic evidence から requirement を具体化する必要がある。
- まだ人間判断が必要な理由:
  - Template 更新を必須にするかは、実効性と scope creep の tradeoff であり、local source だけでは maintainer intent を確定できない。

## 回答案 (必須)
- Option A:
  - Docs / skills のみを必須にする。Templates は対象外または follow-up。
- Option B:
  - Docs / skills に加え、Issue / Epic の templates に短い readiness checklist を追加する。
- Option C:
  - Requirement phase では B を前提にするが、design で template 影響が大きいと判明した場合は follow-up に切り出す。
- Option D:
  - B-lite / contract-first。Workflow docs + skills + 最小限の Issue/Epic template readiness checklist を必須にする。ただし template は policy authority ではなく、短い readiness prompt / context surface に限定する。広範な template/example migration は follow-up 可。

## Codex の分析 (必須)
- 判断軸:
  - 実効性、scope の小ささ、parent epic との整合、future agent が最初に読む面への効き方。
- tradeoff:
  - A は小さく安全だが、agent が新規 issue を作るときの scaffold には効きにくい。
  - B は実効性が高いが、docs / skills / templates の三面更新になり review scope が広がる。
  - C は実効性と小ささのバランスを取りやすいが、design phase で split 判断を明確にする必要がある。
  - D は最小 checklist を必須化して A への後退を防ぎつつ、B の scope creep と template authority drift を抑える。
- リスク:
  - Template に gate を入れすぎると scaffold が compliance authority に見える。
  - Template を全く触らないと、Issue readiness gate が日常運用で見落とされる可能性が残る。
- 具体シナリオ / edge case:
  - `management_core` や shared kernel boundary のような複数 Issue に影響する判断は Epic に戻すべき。
  - small naming や局所 fallback のような軽微判断は Issue 内で許容しないと運用が重くなる。

## Codex の推奨案 (必須)
- 推奨:
  - Option D。
- 理由:
  - Deep consultant の独立分析では、docs/skills だけでは first-read reliability と future harness/eval surface として弱く、Issue/Epic artifact 側にも最小限の readiness prompt が必要とされた。一方で、template は canonical policy authority にせず、短い prompt と正本参照に限定するのが正しい。
- 未回答時の影響:
  - `requirement.md` の必須スコープと非スコープを確定できず、design / plan に進めない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User supports the deep-consultant recommendation and adopts Option D as the premise for `iss-00196`.
- 回答:
  - Option D: B-lite / contract-first を採用する。Workflow docs + skills + minimal Issue/Epic template readiness checklist を必須範囲に含める。ただし templates は canonical policy authority ではなく、短い readiness prompt / context surface に限定する。
- 回答日時:
  - 2026-06-18

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Should persistent workflow docs/templates include a project-specific dogfooding example such as `management_core` / shared kernel boundary, or keep examples generic and record the project-specific case only as issue evidence?

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - User explicitly supports the deep-consultant proposal. This decision fixes the issue scope boundary and prevents both docs-only weakness and broad template scope creep.
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Required scope includes workflow docs, planning skills, and minimal Issue/Epic template readiness prompts.
  - Templates must remain prompts/scaffolds and not become policy authority.
- `design.md`:
  - Design must keep canonical rules in workflow docs / skills and add only short template cues with references.
- `plan.md`:
  - Plan should split docs/skills and minimal template checklist work into reviewable steps if needed.
- `ADR`:
  - Not required by this answer alone; revisit only if design reveals a durable, surprising policy decision requiring ADR.
- reflected_to 更新方針:
  - Update after canonical `requirement.md` and `report.md` adoption.
- adoption reflection:
  - Reflect Option D as the adopted issue scope decision.

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
