---
種別: interview
ID: "20260530t081150z-interview"
タイトル: "Matt Pocock adoption issue primary scope"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-05-30"
親: ["iss-00142"]
関連: []
scope: "issue"
scope_id: "iss-00142"
created_at: "2026-05-30T08:11:50Z"
created_by: "Codex"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/active/issue/discussions/20260529t154740z-research-initial-skill-adoption-research.md"
  - "spec-dock/docs/workflow_clarification.md"
  - "spec-dock/docs/workflow_spec_authoring.md"
  - "spec-dock/docs/workflow_issue.md"
  - "spec-dock/docs/phase_plan_issue.md"
  - "spec-dock/docs/authoring/issue-plan.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md"
  - "src/spec_dock/assets/install_root/.agents/skills/spec-dock-system-architect/SKILL.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/requirement.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/design.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/discussions/mattpocock-skills-source/skills/engineering/diagnose/SKILL.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/discussions/mattpocock-skills-source/skills/engineering/tdd/SKILL.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/discussions/mattpocock-skills-source/skills/engineering/to-issues/SKILL.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/discussions/mattpocock-skills-source/skills/engineering/improve-codebase-architecture/SKILL.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/discussions/mattpocock-skills-source/skills/engineering/triage/SKILL.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/discussions/mattpocock-skills-source/skills/engineering/prototype/SKILL.md"
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00067-installed-layout-aligned-asset-source-structure-for-agent-tooling/issues/iss-00134-matt-pocock-grill-skill-review-patterns/discussions/mattpocock-skills-source/skills/productivity/handoff/SKILL.md"
reflected_to: []
---

# 20260530t081150z-interview Matt Pocock adoption issue primary scope

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - この issue の目的、必須スコープ、禁止スコープ、受け入れ条件、対象外を決める。
  - `design.md`:
    - どの Matt Pocock skill essence を、既存 workflow / docs / skill guidance / template / follow-up issue のどこへ接続するかを決める。
  - `plan.md`:
    - 実装 step を含めるか、調査・設計・follow-up 作成までに留めるかで、step 分解、review gate、検証方法が変わる。
  - `ADR`:
    - `triage` / `prototype` / `diagnose` のように workflow authority や artifact lifecycle を変える判断が durable decision になる場合だけ候補になる。
- chat 上の軽微な一問では足りない理由:
  - 回答が issue の完了条件と downstream handoff を変え、後続の要件定義書へ直接反映されるため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `iss-00142` を「Matt Pocock skills の採用方針を確定する analysis / authoring issue」として閉じるのか、それとも「選定した P0/P1 の概念を実際に workflow docs / skills / templates へ反映する implementation issue」として閉じるのかを確定する。
- 回答が後続判断へ与える影響:
  - 要件定義書で、必須成果物を research / requirement / design / plan / follow-up issue までにするか、provider-side shipped assets の変更と tests / dogfooding validation まで含めるかが変わる。

## 質問 (必須)
- 質問:
  - この issue の主成果は、Matt Pocock skills の採用判断と要件・設計・計画の確定までに留めますか。それとも、選定した概念の実装反映までこの issue に含めますか。
- 回答してほしいこと:
  - 下の Option A / B / C のうち、今回の `iss-00142` の primary scope に一番近いものを選んでください。必要なら組み合わせや条件付きでも構いません。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `iss-00142` の canonical `requirement.md` / `design.md` / `plan.md` はまだ template 状態であり、実質的な作業内容は `20260529t154740z-research-initial-skill-adoption-research.md` にある。
  - `workflow_clarification.md` は、source-grounded read、一問一答、unanswered `interview` artifact、回答後の採用判断、canonical docs 反映を要求している。
  - `workflow_spec_authoring.md` は、requirement -> fresh `spec-reviewer` pass -> design -> fresh `spec-reviewer` pass -> plan -> fresh `spec-reviewer` pass の phase promotion を要求している。
  - `workflow_issue.md` と `spec-dock-issue-execution` は、template-only / unresolved な requirement / design / plan のまま execution に入らず、planning / clarification に戻ることを要求している。
  - `iss-00134` は `grill-me` / `grill-with-docs` を無加工移植せず、spec-dock-native な `docs-aware clarification workflow` として翻訳した。
  - Matt Pocock `diagnose` は feedback loop first、reproduce、ranked hypotheses、instrument、regression test、cleanup / post-mortem を要求している。
  - Matt Pocock `tdd` は public interface / observable behavior、one test at a time、vertical tracer bullet、horizontal batching 禁止を要求している。
  - Matt Pocock `to-issues` は plan / spec / PRD を tracer bullet vertical slices と HITL / AFK に分け、依存順で issue 化する。
  - Matt Pocock `improve-codebase-architecture` は deep module、interface、seam、adapter、deletion test、locality / leverage という vocabulary を持つが、`CONTEXT.md` 直接運用は spec-dock の正本モデルと衝突しうる。
  - Matt Pocock `triage` / `prototype` は魅力的だが、spec-dock の readiness / GitHub sync / artifact lifecycle と衝突しやすい。
  - Upstream `mattpocock/skills` は local capture commit `0288510dd61ff6ef7c2003834082ab8f2387e80e` の後に `e3b90b5238f38cdea5996e16861dcae28ef52eda` があり、差分は `grill-with-docs/CONTEXT-FORMAT.md` の小変更だった。今回対象の `diagnose` / `tdd` / `to-issues` などには直接影響しない。
- local context で解決できたこと:
  - 直接移植ではなく spec-dock-native translation が必要であること。
  - 新規 skill を大量追加すると entrypoint が分散し、authority model と衝突しやすいこと。
  - P0 候補は `diagnose` / `tdd` / `to-issues`、P1 候補は `improve-codebase-architecture` / `zoom-out`、P2 候補は `handoff` / `write-a-skill`、follow-up 候補は `triage` / `prototype` であること。
- まだ人間判断が必要な理由:
  - この issue をどこまでの成果で閉じるべきかは、プロダクト運用上の優先順位と変更リスクの判断であり、ローカル文書だけでは確定できない。

## 回答案 (必須)
- Option A:
  - Analysis / authoring issue として閉じる。
  - この issue では採用分類、非採用理由、follow-up 分割、`requirement.md` / `design.md` / `plan.md` の作成までを成果にし、workflow docs / skills / templates の実装変更は別 issue に切る。
- Option B:
  - P0 concept adoption まで実装する。
  - `diagnose` / `tdd` / `to-issues` のうち合意した P0 概念を、既存 docs / skills / templates へ最小反映し、tests / dogfooding validation までこの issue に含める。
- Option C:
  - Hybrid にする。
  - この issue では `diagnose` / `tdd` / `to-issues` の採用設計と、低リスクな docs / skill guidance の最小反映だけ行う。新規 first-class skill、`triage`、`prototype`、大きな workflow 変更は follow-up issue に分ける。

## Codex の分析 (必須)
- 判断軸:
  - scope の明確さ、review 可能性、spec-dock authority model との整合、implementation readiness までの距離、skill proliferation のリスク。
- tradeoff:
  - Option A は最も安全で、要件定義書を早く正確に固められる一方、実装価値は後続 issue に先送りされる。
  - Option B は価値が出るのが早い一方、P0 の選定、反映先、tests、dogfooding validation、review gate が増え、issue が膨らみやすい。
  - Option C は現実的な最小実装を含められるが、どこまでを「低リスクな最小反映」とみなすかを requirement / design で厳密に書く必要がある。
- リスク:
  - Option B / C で scope を広げすぎると、`iss-00134` が避けた「外部 skill の直接移植」や「entrypoint 分散」に戻る可能性がある。
  - Option A だけだと、調査 issue としては閉じるが、Matt Pocock essence が実際の workflow へ反映されるまでにもう一段 issue が必要になる。
- 具体シナリオ / edge case:
  - `diagnose` を first-class `spec-dock-diagnosis` として追加する場合、bug issue が approved `plan.md` を飛ばして実装に入らないよう、`workflow_issue.md` との境界設計が必要になる。
  - `tdd` の horizontal batching 禁止を `plan.md` へ入れる場合、既存の `Spec-Locked Closure Index` と `具体テストケース一覧` のどちらへ置くかを明確にする必要がある。
  - `to-issues` の HITL / AFK を取り込む場合、GitHub label ではなく spec-dock の issue readiness / dependency / reviewer gate と対応づける必要がある。

## Codex の推奨案 (必須)
- 推奨:
  - Option C。
- 理由:
  - 既存 research は、P0 概念の価値が高い一方で大量 skill 追加を避けるべきだと示している。したがって、この issue ではまず P0/P1/P2/P3 の採用判断を requirement に固定し、低リスクな docs / skill guidance への最小反映まで許容するのが、価値と安全性のバランスがよい。
  - 新規 first-class skill、GitHub triage adapter、throwaway prototype lifecycle など、authority / workflow lifecycle へ強く触れるものは follow-up issue に分けた方が reviewer が判断しやすい。
- 未回答時の影響:
  - `requirement.md` の目的、スコープ、受け入れ条件、対象外を確定できず、design / plan へ進めない。

## ユーザー回答 (回答後に必須)
- 回答:
  - Option C を採用する。
  - この issue では、Matt Pocock skills の採用設計と、spec-dock と自然に統合できる低リスクな docs / skill guidance の最小反映を扱う。
  - 大きな workflow 変更、新規 first-class skill、`triage` / `prototype` のような authority / lifecycle へ強く触れる内容は follow-up issue に分ける。
  - 目的は、Matt Pocock skills の直接移植ではなく、spec-dock とうまく統合することである。
- 回答日時:
  - 2026-05-30

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - 現時点ではなし。要件定義中に、具体的な反映先や follow-up 分割で高影響な曖昧さが出た場合は、別の unanswered `interview` を作成する。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- 採用 / 棄却 / deferred の理由:
  - ユーザー回答により Option C が primary scope として採用された。
  - 既存 research の「大量 skill 追加を避け、spec-dock-native translation として取り込む」方針と整合する。
  - この判断により、requirement では `diagnose` / `tdd` / `to-issues` などの採用候補を評価しつつ、実装反映は低リスクな docs / skill guidance の最小範囲に限定する。

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - 目的は「Matt Pocock skills のうち `grill-me` / `grill-with-docs` 以外の有用な essence を、spec-dock-native に採用分類し、低リスクな最小反映まで行う」こととして書く。
  - 必須スコープには、P0/P1/P2/P3 の採用分類、見送り理由、follow-up 分割、低リスクな docs / skill guidance 反映を含める。
  - 禁止スコープには、直接移植、大量の新規 skill 追加、spec-dock authority model を壊す外部 workflow の導入、`CONTEXT.md` / PRD / GitHub label state の別正本化を含める。
- `design.md`:
  - 既存 `workflow_clarification.md`、`workflow_issue.md`、`phase_plan_issue.md`、`authoring/issue-plan.md`、既存 shipped skills への最小接続点を設計する。
  - 新規 first-class skill や大きな lifecycle 変更が必要な候補は follow-up として分離する設計にする。
- `plan.md`:
  - step は、採用分類の固定、低リスク反映、docs impact / validation、follow-up issue 化のような小さな behavior slice に分ける。
  - 反映対象が docs-only / skill-text-only の場合は、code test ではなく inspection / structural assertion / spec-review evidence を検証手段にする。
- `ADR`:
  - 現時点では ADR までは不要。新規 first-class `spec-dock-diagnosis` や GitHub triage adapter など、後から戻しにくい durable decision が必要になった場合だけ ADR candidate とする。
- reflected_to 更新方針:
  - requirement 作成時にこの回答を `requirement.md` と `report.md` の Evidence Adoption Ledger / Spec Authoring Gate へ反映し、反映後に `reflected_to` を更新する。

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
