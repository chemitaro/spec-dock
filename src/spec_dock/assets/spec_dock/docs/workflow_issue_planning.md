# 課題 planning ワークフロー（workflow: issue planning）

Issue の `requirement.md` / `design.md` / `plan.md` を作成・更新する workflow です。
この文書は Issue 固有の authoring entrypoint であり、共通 phase promotion は [workflow_spec_authoring.md](workflow_spec_authoring.md)、Issue plan field semantics は [authoring/issue-plan.md](authoring/issue-plan.md) に従います。

対応 leaf skill:
- `.agents/skills/spec-dock-issue-planning/SKILL.md`

## 責務

- active issue と parent docs を確認し、local context で解ける疑問を人間へ聞かない。
- requirement / design / plan を `workflow_spec_authoring.md` の順に作成・更新する。
- 各 phase で fresh `spec-reviewer` の `review_status: pass` を得るまで次 phase へ進めない。
- Spec Authoring Gate evidence を active issue の `report.md` に残す。
- grill-style clarification が必要な場合は、source-grounding の後に一問一答で進める。

## clarification / grill 作法

- 重要質問は回答前に unanswered `interview` を作成する。
- `interview` には質問の目的、質問、回答候補、source-grounded context、Codex の分析、Codex の推奨案、回答欄、採用判断、requirement / design / plan / ADR への含意を置く。
- orchestrator は人間ユーザーに一度に一つだけ質問する。
- 専門 agent は人間へ直接質問しない。質問候補、理由、影響 artifact、推奨回答を orchestrator へ返す。
- 軽微な確認は chat 上の一問で扱ってよい。ただし重要判断へ発展したら formal `interview` lifecycle に戻す。
- 複数質問や research を束ねる場合は `disc` に synthesis / reflection proposal / ADR candidate triage を置く。採否確定は canonical docs、ADR、または `report.md` の Evidence Adoption Ledger に記録する。

## Phase Gates

1. Requirement:
   - user intent、scope、non-scope、acceptance criteria、edge cases を固定する。
   - 未解決の scope / non-scope / acceptance uncertainty が残る場合は design へ進めない。
   - fresh `spec-reviewer` pass を得て、`report.md` の Spec Authoring Gate に evidence を残す。
2. Design:
   - reviewer-pass 済み requirement を前提に、既存 docs / source / ADR / discussions を確認する。
   - requirement gap が見つかった場合は requirement phase に戻す。
   - fresh `spec-reviewer` pass を得て、`report.md` の Spec Authoring Gate に evidence を残す。
3. Plan:
   - reviewer-pass 済み requirement / design を前提に、実装順、verification、review gate、handoff を固定する。
   - Issue plan は `authoring/issue-plan.md` の executable step schema と `具体テストケース一覧` を使う。
   - fresh `spec-reviewer` pass を得て、execution handoff 可否を `report.md` の Spec Authoring Gate に残す。

## 禁止

- implementation edits、tests edits、runtime changes、PR 作成、merge-prepared、issue finish を planning 完了として claim しない。
- reviewer pass 前に implementation readiness を claim しない。
- discussion artifact や grill evidence を fresh `spec-reviewer` pass の代替にしない。
- runtime CLI command split、lifecycle state machine redesign、既存 artifact auto migration、PR / finish lifecycle redesign を planning の副作用として行わない。

## Handoff To Execution

Execution に渡せるのは、次を満たす場合だけです。

- `requirement.md` / `design.md` / `plan.md` が issue 固有の内容である。
- 各 artifact が fresh `spec-reviewer` pass 済みである。
- `report.md` の Spec Authoring Gate に phase、artifact、reviewer、freshness、state、investigated facts、promotion / completion decision、notes が記録されている。
- stale / blocked / unresolved の Evidence Adoption Ledger entry が implementation start を止めていない。

不足がある場合は execution へ渡さず、該当 phase へ戻す。
