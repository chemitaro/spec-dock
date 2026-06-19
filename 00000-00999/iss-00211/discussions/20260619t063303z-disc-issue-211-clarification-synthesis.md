---
種別: disc
ID: "20260619t063303z-disc"
タイトル: "Issue 211 Clarification Synthesis"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00211"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260619t063303z-disc Issue 211 Clarification Synthesis

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - Issue 211 で追加する `spec-dock-epic-execution` を、どの責務範囲の coordinator skill として定義するか。
  - 新 skill だけを追加するか、Epic workflow reference docs にも Epic execution lifecycle を定義するか。
- この synthesis が必要な理由:
  - GitHub #211 は新 skill 追加を主眼にしつつ、必要なら複数 workflow docs の更新も許容している。
  - 変更範囲を決めないまま requirement / design / plan を書くと、skill-only 実装と workflow docs 追加のどちらにも読める曖昧な契約になる。

## derived question sheets / research (必須)
- `interview`:
  - `20260619t063309z-interview-issue-211-scope-pressure-test.md`
- `research`:
  - `20260619t063017z-research-issue-211-clarification-source-review.md`
- その他の根拠:
  - GitHub issue #211
  - `spec-dock/docs/workflow_epic.md`
  - `spec-dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-merge-preparer/SKILL.md`

## synthesis (必須)
- 合意済みのこと:
  - Issue 211 は Issue 210 と独立した Issue として扱う。ただし Issue 210 の Epic planning handoff 情報は参照してよい。
  - `spec-dock-epic-execution` は Issue planning / Issue execution / PR merge preparation を置き換えない。
  - PR merge 自体は扱わず、merge-ready preparation / observation / repair loop は `github-pr-merge-preparer` に委譲する。
  - Option B を採用する。新 skill に加えて、`workflow_epic.md` に Epic execution lifecycle / completion gate / PR merge-preparer handoff の短い reference section を追加する。
- 未合意 / 未確定のこと:
  - `workflow_issue.md` / `workflow_spec_authoring.md` / `decision-routing.md` / `reference_github.md` まで更新する必要があるかは、実装設計中に明確な欠落が見つかった場合だけ最小更新として扱う。
- source-grounded に解決できたこと:
  - Provider-side installed skill の source of truth は `src/spec_dock/assets/install_root/.agents/skills/`。
  - Existing provider-side skills に `spec-dock-epic-execution` は存在しない。
  - Runtime CLI command の追加は、GitHub #211 の必須要件ではない。既存 `deps check`, `issue start`, `issue finish`, `sync`, `validate` と既存 skills の orchestration で足りる可能性が高い。
  - Active Issue docs はまだ template scaffold で、Issue 211 固有の requirement / design / plan にはなっていない。

## 選択肢 / tradeoff (必須)
- Option A:
  - Scope:
    - 新しい `spec-dock-epic-execution` skill、dogfooding mirror、必要な provider tests / snapshots のみを主成果にする。
  - Pros:
    - 差分が小さい。
    - First-read operational surface の追加という GitHub #211 の中心要件に集中できる。
  - Cons:
    - Issue 210 で追加した `workflow_epic.md` handoff section と Issue 211 の execution counterpart が docs 上で接続されにくい。
    - skill と workflow reference の間に drift しやすい。
- Option B:
  - Scope:
    - Option A に加えて、`workflow_epic.md` に Epic execution lifecycle / completion gate / PR merge-preparer handoff の短い reference section を追加する。
    - 他 docs は、明確な cross-reference 欠落が見つかった場合だけ最小更新する。
  - Pros:
    - Issue 210 の Planning Completion / Handoff と Issue 211 の Execution Coordinator が repo docs 上でつながる。
    - Skill は first-read coordinator に集中し、長めの lifecycle semantics は workflow reference に逃がせる。
    - Docs 横断 cleanup へ膨らみすぎるリスクを抑えられる。
  - Cons:
    - skill-only より変更対象と test obligation が増える。
    - `workflow_epic.md` の provider-side source と dogfooding reflection の扱いを慎重に検証する必要がある。
- Option C:
  - Scope:
    - GitHub #211 に列挙された docs すべてを横断的に更新する。
  - Pros:
    - 関連 workflow surface を広く整えられる。
  - Cons:
    - Issue 211 が workflow docs cleanup に膨らみ、主目的である coordinator skill 追加から焦点がずれる。
    - 既存 docs との重複と drift risk が高い。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `requirement.md`: coordinator skill の責務、非責務、acceptance criteria、docs update scope を固定する。
  - `design.md`: provider-side skill path、dogfooding mirror、existing skill handoff、workflow docs update boundary、test strategy を定義する。
  - `plan.md`: skill追加、docs更新、test/snapshot更新、review/verification を段階化する。
  - `workflow_epic.md`: Option B 採用時のみ、Epic planning handoff 後の execution lifecycle と completion gate を短く定義する。
- まだ proposal に留める理由:
  - Skill-only にするか、Epic workflow reference まで更新するかは owner-intent / scope tradeoff であり、local source だけでは一意に決めない方がよい。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Scope / non-scope / constraints / acceptance criteria。
- `design.md`:
  - Structure / flow / interfaces / trade-offs / risks。
- `plan.md`:
  - Step split / delegated work / validation plan / completion gates。
- `ADR`:
  - 現時点では不要。既存 workflow family への leaf skill 追加であり、不可逆な architecture decision ではない。
- `report.md` Evidence Adoption Ledger:
  - Research / discussion / interview の採用記録、検証結果、未解決事項。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - no
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `interview`, `requirement.md`, `design.md`, `plan.md`, `report.md`

## 推奨案 (必須)
- Option B を推奨し、ユーザー回答により採用済み。
- 理由:
  - Issue 210 の成果は Epic planning handoff を定義したが、execution coordinator behavior は later Issue に残している。Issue 211 ではこの counterpart を skill と workflow reference の両方で最小限つなぐのが自然。
  - `spec-dock-epic-execution` skill は first-read operational instructions として短く保ち、詳細な lifecycle semantics は `workflow_epic.md` に置く方が drift しにくい。
  - Option C ほど docs 更新範囲を広げないため、主目的である coordinator skill 追加に集中できる。

## 推奨反映先 (必須)
- `requirement.md`:
  - Option B を前提に scope / non-scope / AC を記載する。
- `design.md`:
  - Skill body, workflow_epic reference section, existing skill handoffs, tests を設計する。
- `plan.md`:
  - S01 skill authoring、S02 workflow_epic minimal reference、S03 mirror/test/snapshot、S90 review、S99 finish readiness。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - Research artifact、discussion artifact、interview answer を採用証跡として記録する。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Option C は scope が広く、Issue 211 の focus を逸らすため現時点では採用しない。
- deferred:
  - `workflow_issue.md` / `workflow_spec_authoring.md` / `decision-routing.md` / `reference_github.md` の更新は、実装設計中に明確な欠落が見つかった場合の最小更新に留める。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - interview の回答に基づいて Issue 211 の scope と docs update boundary を canonical docs に反映する。
- 追加で作る discussion docs:
  - 現時点では追加不要。回答後に新しい高影響論点が出た場合のみ、次の `interview` または `disc` を作る。
