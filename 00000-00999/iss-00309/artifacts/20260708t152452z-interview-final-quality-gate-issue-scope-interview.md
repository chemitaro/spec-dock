---
種別: interview
ID: "20260708t152452z-interview"
タイトル: "Final Quality Gate Issue Scope Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-09"
親: ["iss-00309"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00309"
created_at: "2026-07-08THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: []
---

# 20260708t152452z-interview Final Quality Gate Issue Scope Interview

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / artifacts / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `blank` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - final quality gate / PR delivery Issue を必須化する範囲。
  - `design.md`:
    - Epic Planning / Epic Execution / Issue Execution の責務境界。
    - final quality Issue が持つ Epic-wide verification / PR delivery / repair loop の責務。
  - `plan.md`:
    - Epic plan template、Issue slicing policy、final Issue candidate の必須/例外条件。
  - `ADR`:
    - 必要なら Epic delivery policy の ADR 候補。
- chat 上の軽微な一問では足りない理由:
  - 回答により、Epic plan template と Epic Planning skill が final quality Issue を常に生成するか、条件付きで生成するかが変わるため。

## 質問の目的 (必須)
- 対象者:
  - SpecDock を利用する人間ユーザー / product owner。
- 何を明確にする質問か:
  - final quality gate / PR delivery Issue をどの Epic に必須化するか。
- 回答が後続判断へ与える影響:
  - `templates/epic/plan.md`、`phase_plan_epic.md`、`workflow_epic.md`、`spec-dock-epic-planning`、`spec-dock-epic-execution` の契約文言が決まる。

## 質問 (必須)
- pressure-test question:
  - final quality Issue がない multi-Issue implementation Epic では、Epic-wide quality gate と PR delivery が中間 Issue に漏れやすい。一方で全 Epic に mandatory にすると、single-Issue / docs-only / no-op Epic では過剰になる可能性がある。
- 質問:
  - final quality gate / PR delivery Issue は、どの範囲で必須にしますか。
- 回答してほしいこと:
  - A/B/C のどれに近いか、または別案を教えてください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/spec_dock/templates/epic/plan.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_chatgpt_authoring_pack.md`
  - `artifacts/20260708t152310z-research-workflow-simulation-and-final-quality-gate-issue-analysis.md`
- local context で解決できたこと:
  - Epic Execution は final quality Issue への PR delivery defer を扱える。
  - ChatGPT authoring workflow docs は reviewed Epic plan が final delivery Issue を定義している場合に relay delivery を行うと書いている。
  - Epic plan template には final quality gate section はあるが、Issue list 末尾に final quality Issue candidate を必ず含める契約は弱い。
- まだ人間判断が必要な理由:
  - final quality Issue を全 Epic 必須にすると過剰になる可能性があり、条件付き必須にすると例外判断のルールが必要になるため。

## 回答案 (必須)
- Option A:
  - すべての Epic に final quality gate / PR delivery Issue を必須にする。single-Issue / docs-only / no-op でも final Issue か明示的 no-op final gate を作る。
- Option B:
  - 複数 Issue を持つ implementation Epic では必須にする。single-Issue / docs-only / no-op Epic は、Epic plan に skip rationale と completion evidence を置けば final quality Issue を省略できる。
- Option C:
  - final quality Issue は推奨に留め、Epic planner が必要と判断した場合だけ作る。

## Codex の分析 (必須)
- 判断軸:
  - PR delivery の一貫性、過剰プロセス回避、Epic-wide gate の抜け漏れ防止、template の分かりやすさ、Execution skill の判定容易性。
- tradeoff:
  - Option A は最も一貫するが、小さな Epic で作業単位が増える。
  - Option B は実務上のバランスがよいが、skip rationale の条件を明記する必要がある。
  - Option C は柔軟だが、今回の問題である「最後に誰が Epic-wide gate と PR delivery を閉じるか」が再び曖昧になりやすい。
- リスク:
  - final quality Issue が optional だと、中間 Issue が PR delivery を始めたり、Epic-wide review repair loop がチャットだけに残る可能性がある。
  - final quality Issue を常に必須にすると、docs-only Epic のような軽い作業で ceremony が増える。
- 具体シナリオ / edge case:
  - 12個の実装 Issue を持つ Epic では final quality Issue が必須でないと PR delivery が分散する。
  - 1個だけの小さな docs update Epic では final quality Issue を別に作るより、その Issue 内で final gate を閉じた方が自然な場合がある。
  - no-op / analysis-only Epic では final quality Issue より Epic report の no-op completion evidence が自然な場合がある。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - 複数 Issue の implementation Epic では final quality Issue を必須にし、Epic-wide gate / PR delivery / repair loop を一箇所へ集約するのが安全。
  - single-Issue / docs-only / no-op Epic では、明示的 skip rationale と completion evidence を要求することで ceremony を抑えつつ、抜け漏れを防げる。
- 未回答時の影響:
  - Epic plan template と Epic Planning skill が final quality Issue をどの強さで要求するか決められない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - Option B を採用する。
  - 単一 Issue の場合は Epic 専用の final quality gate / PR delivery Issue は不要。
  - 単一 Issue Epic では、Issue の品質ゲートが Epic の品質ゲートを兼ねられる。
- 回答:
  - 複数 Issue を持つ implementation Epic では final quality gate / PR delivery Issue を必須にする。
  - single-Issue / docs-only / no-op Epic は、Epic plan に skip rationale と completion evidence を置けば final quality Issue を省略できる。
  - 特に単一 Issue Epic では、その Issue 内の品質ゲートを Epic-level gate として扱う。
- 回答日時:
  - 2026-07-09

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Issue Planning を Epic Planning 中に全件正式化するか、Epic Planning では各 Issue の draft requirement / draft design / draft plan までに留め、Issue Execution 直前に正式 Issue Planning を行うか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - 複数 Issue implementation Epic では Epic-wide verification、review repair、manual test、mergeable PR delivery が中間 Issue に分散しやすいため、final quality Issue を必須化する。
  - 単一 Issue Epic では同じ Issue の品質ゲートで Epic-level gate を兼ねられるため、別 Issue 化を強制しない。
  - docs-only / no-op Epic では、skip rationale と completion evidence を要求することで過剰プロセスを避ける。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - final quality gate / PR delivery Issue の必須範囲を、複数 Issue implementation Epic に限定して明記する。
  - single-Issue / docs-only / no-op Epic では、skip rationale と completion evidence を要求する。
- `design.md`:
  - Epic Planning / Epic Execution は、複数 Issue implementation Epic で最終 Issue を Epic-wide quality gate / PR delivery owner として扱う。
  - 単一 Issue Epic では Issue-local quality gate が Epic gate を兼ねる設計を許容する。
- `plan.md`:
  - Epic plan template と planning skill に、final quality Issue の必須条件、skip 条件、skip evidence を追加する。
- `ADR`:
  - 現時点では不要。後続で Epic delivery policy を恒久判断として固定する場合は ADR 候補にする。
- reflected_to 更新方針:
  - canonical requirement / design / plan 作成時に反映し、report EAL に採用済みとして記録する。
- adoption reflection:
  - reflected_to は canonical docs へ反映した時点で更新する。

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
- 追加で作る artifacts:
  - ...
