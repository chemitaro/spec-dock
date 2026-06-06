---
種別: disc
ID: "20260605t050100z-disc"
タイトル: "Issue Decomposition Synthesis For Skill Docs Workflow Spine"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-05"
親: ["epic-00158"]
関連:
  - "iss-00159"
authority: "proposed"
derived_from:
  - "spec-dock/active/epic/discussions/20260605t050037z-research-chatgpt-issue-decomposition-report.md"
  - "spec-dock/active/epic/discussions/20260605t043350z-disc-agent-workflow-pdca-analysis-summary.md"
  - "user correction 2026-06-05: regression checks are not the immediate independent issue"
  - "spec-dock/active/epic/discussions/20260605t053300z-research-chatgpt-clarification-grill-alignment-report.md"
reflected_to: []
---

# 20260605t050100z-disc Issue Decomposition Synthesis For Skill Docs Workflow Spine

## 位置づけ

この doc は、ChatGPT `じっくり思考 Pro` による issue decomposition report と、その後のユーザー補正を、後続 issue 作成のために短く整理した synthesis である。

この doc 自体は canonical backlog ではない。後続で作る issue / requirement / design / plan へ採用する場合は、各 issue の `report.md` Evidence Adoption Ledger に採用証跡を残す。

## 最新補正

- `Add Skill Spine Regression Checks` は、今すぐ独立 issue として前面に出さない。
- 今回の主因は「ルールが足りない」ことよりも、モデルが最初に読む context surface が薄い、分散している、お手本として弱いこと。
- したがって first wave の主戦場は、全ての skill / docs / templates を一度整理し、「どこを読んでも skill と docs と templates の正しい住み分けが見える」状態にすること。
- regression checks / harness は、この整理後に効果維持や drift 検出のために追加する後段 guard として扱う。
- `spec-dock-clarification` は、単なる return-to-authoring wording 追加では不足する。これは SpecDock 版 `Grill with me` / `Grill with dog` integration surface として、source-grounded grill loop の workflow spine を skill に出し、`interview` / `research` / `disc` templates も同じ振る舞いを示すように整える対象である。

## 情報充足度

- 結論:
  - 具体 issue へ分割するための情報は概ね十分に揃っている。
- 追加 broad research は不要:
  - 各 issue の冒頭で local inventory / provider-vs-mirror confirmation を行えば足りる。
- まだ不確実だが issue 作成をブロックしないこと:
  - current branch が GitHub から見えないため、branch-specific file state は local worktree で確認する必要がある。
  - provider asset と dogfooding mirror の完全な差分は各 issue 内で確認する。
  - reviewer status vocabulary / harness layout / runtime schema は対象 issue 内で inventory する。
- runtime issue だけは後段:
  - runtime gate / validation / `gate status` は、skill/docs/harness で期待 contract を固定してから扱う方がよい。

## Revised PDCA sequence

ChatGPT report の issue 分解案は参考にするが、最新補正により sequence は次のように置き直す。

1. `Make Issue Planning Skill Expose Mandatory Authoring Gates`
   - 既存 `iss-00159`。
   - issue planning skill を first concrete specimen として扱う。
   - ただし isolated fix で完結させず、後続の全体整理へ学びを渡す。
2. `Align Skill Docs Template Context Surfaces`
   - first wave の中核。
   - 対象は provider-side の skills / docs / templates 全体。
   - skill は「モデルが必ず守る operational workflow spine」を持つ。
   - docs は「概念、項目の意味、詳細な判断材料、source of truth」を担う。
   - templates は「scaffold と良い記入例の入口」を担い、compliance authority にはしない。
   - どの surface を読んでも、この住み分けと同じお手本が見える状態にする。
3. `Revise spec-dock-clarification as source-grounded grill workflow`
   - `spec-dock-clarification` を SpecDock 版の source-grounded grill loop として再設計する。
   - skill は read sources -> provisional understanding -> one pressure-test question -> artifact capture -> iterate/handoff を first-read surface に出す。
   - docs は formal triggers / artifact semantics / ledger semantics を担う。
   - `interview.md` / `research.md` / `disc.md` は同じ behavior を scaffold/example として示す。
   - `Align Skill Docs Template Context Surfaces` の中核 sub-issue として切ってよい。
4. `Clarify Hub And Leaf Skill Routing Surface`
   - hub skill は router + global invariant として整理する。
   - leaf skills は first-read runbook と docs 参照を担う。
   - これは `Align Skill Docs Template Context Surfaces` の一部に含めてもよい。
5. `Align Workflow Docs With Skill Spine Boundary`
   - docs 側から agent operational workflow を掘り出し、skill 側に置くべき spine と docs 側に残すべき meaning / detail を分ける。
   - docs は thin skill の代替ではなく、skill から呼ばれる detailed reference として整理する。
6. `Align Templates As Scaffolds And Examples`
   - templates が compliance authority に見えないようにしつつ、良い evidence slots と記入例を揃える。
7. `Add Skill Spine Regression Checks`
   - 後段。
   - cleaned-up surfaces の drift 検出や最低限の phrase / heading guard として追加する。
   - first wave の独立 issue ではない。

## 推奨 issue backlog

### Skill-only / docs-surface issues

- `Make Issue Planning Skill Expose Mandatory Authoring Gates`
  - 既存 `iss-00159`。
  - first concrete specimen として維持する。
  - ただし後続の全体整理で wording / structure を再確認する。
- `Align Skill Docs Template Context Surfaces`
  - 現時点の最重要候補。
  - provider-side skills / docs / templates を横断して、住み分け、参照導線、お手本の一貫性を整理する。
  - Non-scope: runtime gate、automated harness、workflow policy の大幅変更。
- `Revise spec-dock-clarification as source-grounded grill workflow`
  - `spec-dock-clarification` を `Grill with me` / `Grill with dog` 的な SpecDock integration skill として再設計する。
  - skill に operational spine を置く:
    - source を読む。
    - provisional understanding を作る。
    - ambiguity / assumption / impact を切る。
    - one essential pressure-test question を選ぶ。
    - 重要判断は unanswered `interview` を作ってから聞く。
    - 回答後、同じ artifact を complete する。
    - 次の一問か handoff を判断する。
  - docs は artifact semantics、formal trigger、mode、ledger、orchestrator / specialist protocol の詳細を担う。
  - templates は `interview` / `research` / `disc` を中心に good scaffolds として整える。
  - Non-scope: original skill の exact copy、generic coaching skill 化、runtime gate、automated harness first。
- `Clarify Hub And Leaf Skill Routing Surface`
  - `spec-driven-tdd-workflow` を router + global invariant layer として整理する。
  - leaf skills には task-specific first-read runbook を置く。
  - `Align Skill Docs Template Context Surfaces` に吸収可能。
- `Align Workflow Docs With Skill Spine Boundary`
  - docs に埋もれた operational steps を skill へ寄せる。
  - docs には meaning / field semantics / detailed reference / policy rationale を残す。
  - `Align Skill Docs Template Context Surfaces` に吸収可能。
- `Align Templates As Scaffolds And Examples`
  - templates を scaffold / evidence slot / example surface として整える。
  - templates が completion や compliance の authority に見えないようにする。
  - `Align Skill Docs Template Context Surfaces` に吸収可能。
- `Align Clarification Skill Return Handoffs`
  - clarification が issue planning / prior phase へ戻る handoff wording を補強する。
  - この軽量案は最新の grill alignment analysis により不十分と判断する。
  - 採用する場合は `Revise spec-dock-clarification as source-grounded grill workflow` に吸収する。

### Guard / harness issues

- `Add Skill Spine Regression Checks`
  - Required headings / invariant phrases / docs references / provider mirror consistency の lightweight guard。
  - cleanup 後の drift detection。
  - 今すぐ独立 issue としては優先しない。
- `Add Manual Workflow Scenario Harness`
  - stale reviewer、missing evidence、template-only docs、waived reviewer などの scenario を manual / semi-manual に評価する。
  - context surface cleanup と必要な guard の後。

### Docs-only issues

- `Audit Spec Authoring Docs For Gate Semantics`
  - `workflow_spec_authoring.md` などの gate semantics を skill spine と矛盾しないよう整理する。
- `Audit Issue Lifecycle Docs For Execution Handoff`
  - `workflow_issue.md` の planning -> execution -> completion handoff を skill と整合させる。
- `Define Reviewer Gate Evidence Contract`
  - fresh / stale / unavailable / waived / provisional の evidence wording を docs 側で明確にする。

### Template issues

- `Keep Templates As Scaffolds With Evidence Slots`
  - templates が compliance authority に見えないようにしつつ、必要な evidence slots を保つ。
  - context surface cleanup に含める候補。

### Runtime-later issues

- `Design Gate Status Read Model`
  - runtime / CLI gate work の設計 issue。
  - skill/docs/harness contract が固まった後。
- `Add Runtime Issue Start Readiness Check`
  - issue start / execution readiness guard。
  - Later only。
- `Add Runtime Issue Finish Completion Guardrails`
  - issue finish / completion laundering guard。
  - Later only。

## `iss-00159` に混ぜないもの

- hub skill rewrite。
- issue execution skill rewrite。
- epic / initiative parity。
- clarification return handoff。
- automated / manual compliance harness。
- docs audit。
- template audit。
- runtime gate / validation / `gate status --json`。

`iss-00159` は、`spec-dock-issue-planning` skill の first-read workflow spine だけに集中する。

## 採用しない方がよい案

- Runtime gate first:
  - 今回の主因である first-read instruction visibility に直接効きにくい。
- Copy docs into skills:
  - skill bloat と source-of-truth drift を招く。
- Rewrite all skills mechanically:
  - 形式だけ揃えても、docs / templates との住み分けが見えなければ今回の問題を解けない。
  - 横断 cleanup は行うが、目的は量産 rewrite ではなく context surface の一貫性を作ること。
- Make templates compliance authorities:
  - templates は scaffolds であり、completion / compliance の authority ではない。
- Treat delegated drafts as canonical by placement:
  - main orchestrator adoption と `report.md` evidence なしには canonical にしない。
- Treat `issue finish` as workflow completion:
  - `issue finish` は lifecycle closure であり、delivery / validation / review / PR evidence の代替ではない。

## Issue 作成メモ

- SpecDock title は ASCII alphanumerics + spaces が安全。
- 各 shipped asset 変更 issue は軽量でも requirement / design / plan を持つべき。
- discussion-only bootstrap で足りるのは、asset をまだ変更しない inventory / comparison のみ。
- 各 issue の最初に local inventory を置く:
  - provider-side source path。
  - dogfooding mirror path。
  - related docs。
  - expected verification。
- `Align Skill Docs Template Context Surfaces` を作る場合の inventory 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - dogfooding mirror under `.agents/` and `spec-dock/` for verification only。
