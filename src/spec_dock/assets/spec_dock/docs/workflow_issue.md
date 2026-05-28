# 課題ワークフロー（workflow: issue / umbrella）

Issue は実装の最小単位です。
この文書は互換用 umbrella であり、Issue planning と Issue execution の入口、handoff、scope 外を短く示します。

正本:

- Issue planning: [workflow_issue_planning.md](workflow_issue_planning.md)
- Issue execution: [workflow_issue_execution.md](workflow_issue_execution.md)
- 共通 spec authoring gate: [workflow_spec_authoring.md](workflow_spec_authoring.md)
- Issue plan field semantics: [authoring/issue-plan.md](authoring/issue-plan.md)
- 共通 phase playbook: [phase_requirement.md](phase_requirement.md), [phase_design.md](phase_design.md), [phase_plan.md](phase_plan.md)
- Issue plan playbook: [phase_plan_issue.md](phase_plan_issue.md)
- GitHub 連携: [reference_github.md](reference_github.md)
- ADR: [workflow_adr.md](workflow_adr.md)

対応 leaf skill:

- `.agents/skills/spec-dock-issue-planning/SKILL.md`
- `.agents/skills/spec-dock-issue-execution/SKILL.md`

## route

- Issue の `requirement.md` / `design.md` / `plan.md` 作成・更新、grill-style clarification、一問一答の formal `interview`、Spec Authoring Gate evidence は [workflow_issue_planning.md](workflow_issue_planning.md) を使う。
- fresh `spec-reviewer` pass 済みの `requirement.md` / `design.md` / `plan.md` と `report.md` の Spec Authoring Gate evidence を確認した後の approved plan execution、report evidence、PR delivery、merge preparation、issue finish は [workflow_issue_execution.md](workflow_issue_execution.md) を使う。
- execution 中に requirement / design / plan の不足、stale reviewer pass、未解決の仕様判断が見つかった場合は、実装を継続せず planning phase に戻す。
- runtime CLI command split、lifecycle state machine redesign、既存 artifact auto migration、PR / finish lifecycle redesign はこの route 変更の対象外。

## commands

```bash
# 主要ライフサイクル（primary lifecycle）
./spec-dock/scripts/spec-dock new issue --epic <epic-id> --title "..."
./spec-dock/scripts/spec-dock new issue --create-github-issue --epic <epic-id> --title "..."
./spec-dock/scripts/spec-dock import issue <num|#num|canonical-url> --title "..." [--epic <epic-id>]
./spec-dock/scripts/spec-dock issue start <issue-id|github-issue-number|url>
./spec-dock/scripts/spec-dock issue start <issue-id|github-issue-number|url> -f
./spec-dock/scripts/spec-dock issue finish

# 手動 / 復旧専用（manual / recovery only）
./spec-dock/scripts/spec-dock active set <issue-id|github-issue-number|url>
./spec-dock/scripts/spec-dock active set --id <issue-id>
./spec-dock/scripts/spec-dock active set --github-issue <n>
./spec-dock/scripts/spec-dock active set <issue-id|github-issue-number|url> --checkout
./spec-dock/scripts/spec-dock active show

./spec-dock/scripts/spec-dock deps check <target>
./spec-dock/scripts/spec-dock deps add --from <issue-id> --to <issue-id>
./spec-dock/scripts/spec-dock deps remove --from <issue-id> --to <issue-id>
```

Command semantics are maintained for compatibility. Detailed planning and execution policy lives in the route-specific documents above.

## planning summary

- active issue 配下の `requirement.md` / `design.md` / `plan.md` を埋める。
- Requirement / design / plan の phase promotion は `workflow_spec_authoring.md` を正本にし、各 artifact ごとに fresh `spec-reviewer` の `review_status: pass` まで次 phase へ進めない。
- `discussions/` の current catalog は `scratch` / `interview` / `research` / `disc` / `adr` / `draft-requirement` / `draft-design` / `draft-plan`。`report` / `reflection` / `grill-*` を new doc catalog に追加しない。
- `interview` は一問一答の正式質問シート、`research` は source-grounding、`disc` は synthesis / reflection proposal / ADR triage として使う。採否確定は canonical docs、ADR、または `report.md` の Evidence Adoption Ledger に記録する。

## execution summary

- execution 前に `workflow_spec_authoring.md` の requirement / design / plan gate がすべて pass し、Spec Authoring Gate evidence が `report.md` に残っていることを確認する。
- `plan.md` は planned executable workflow contract / command queue である。実行者は step を上から順に読み、各 step の behavior goal、planned obligation、Red または代替 evidence、Green verification、refactor guardrail、closure requirements、report evidence destination、amendment trigger に従う。
- `report.md` は observed evidence ledger である。実際の Red / Green / Refactor 結果、verification result、discovered tests、closure delta、reviewer verdict、commit/no-op evidence は `report.md` に記録し、`plan.md` を実行結果の正本にしない。
- runtime / tests / scaffold behavior は `dev-coder`、shipped docs / templates / skills / workflow text は `doc-writer` に route する。
- docs-only / template-only / skill-text-only step は `spec-reviewer`、code / runtime / tests / scaffold behavior を含む step は `code-reviewer` の fresh pass を得る。

## handoff

Planning から execution に渡せるのは、次を満たす場合だけです。

- `requirement.md` / `design.md` / `plan.md` が issue 固有の内容である。
- 各 artifact が fresh `spec-reviewer` pass 済みである。
- `report.md` の Spec Authoring Gate に phase、artifact、reviewer、freshness、state、investigated facts、promotion / completion decision、notes が記録されている。
- Evidence Adoption Ledger に unresolved `blocked` / `stale` entry がない。

不足がある場合は execution へ渡さず、該当 planning phase へ戻す。

## completion summary

- Final commit gates 後、`issue finish` の前に PR Delivery Gate と Merge Preparation Gate を通す。
- `issue finish` は lifecycle-only command であり、PR 作成、merge readiness、checks、review、final delivery completion を保証しない。
- `complete` と報告してよいのは、required validation、required reviews、closure ids、PR delivery、merge-preparation evidence、final commit gate が `report.md` と external delivery evidence で確認できる場合だけである。
- 完了条件を満たせない状態は `blocked` または `未完了` として扱い、成功報告をしない。

## hard cutover

標準 Issue workflow は hard cutover を前提にしない。fallback 廃止、checked-in data の手動境界修正、entry judgment、T3/T4 owner split などを伴う issue だけ、[reference_hard_cutover.md](reference_hard_cutover.md) の optional pattern を plan / report contract へ明示的に取り込む。

## 仕上げ

```bash
./spec-dock/scripts/spec-dock validate
./spec-dock/scripts/spec-dock sync
```
