---
種別: interview
ID: "20260615t152809z-interview"
タイトル: "Issue Execution Hardening Scope Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-16"
親: ["iss-00186"]
関連: []
scope: "issue"
scope_id: "iss-00186"
created_at: "2026-06-15T15:28:09Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: []
---

# 20260615t152809z-interview Issue Execution Hardening Scope Boundary

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
    - `iss-00186` の必須スコープ、対象外、非交渉制約、受け入れ条件が変わる。
  - `design.md`:
    - skill / workflow docs / authoring docs / templates / prompt / tests の surface responsibility と変更対象が変わる。
  - `plan.md`:
    - implementation step の数、順序、delegated role、reviewer gate、検証方法が変わる。
  - `ADR`:
    - 現時点では追加 ADR は不要の見込み。ただし既存 ADR 適用範囲を超えて runtime enforcement や template authority を変える場合は ADR triage が必要になる。
- chat 上の軽微な一問では足りない理由:
  - 回答によって `iss-00186` が「最小 skill/workflow hardening」になるか、「templates / prompt / empirical harness まで含む横断 cleanup」になるかが変わり、後続の requirement / design / plan すべてに影響するため。

## 質問の目的 (必須)
- 対象者:
  - iwasawayuuta
- 何を明確にする質問か:
  - `iss-00186` の実装範囲をどこまで含めるか。
- 回答が後続判断へ与える影響:
  - scope / non-scope、受け入れ条件、変更対象ファイル、実装 step 分割、レビュー種別、検証範囲、follow-up issue の有無を固定する。

## 質問 (必須)
- pressure-test question:
  - `iss-00186` は、`spec-dock-issue-execution` の first-read gate spine を強化する最小 issue として閉じるべきか、それとも templates / prompt / empirical harness まで含む横断 hardening issue として扱うべきか。
- 質問:
  - 今回の `iss-00186` のスコープは、どの範囲に固定しますか？
- 回答してほしいこと:
  - 下の Option A/B/C のうち、採用したい方向を選んでください。迷う場合は、Codex 推奨の Option B を前提に requirement / design / plan を作成します。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `.agents/skills/spec-dock-clarification/SKILL.md`
  - `.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `.agents/skills/spec-dock-issue-execution/SKILL.md`
  - `spec-dock/docs/workflow_clarification.md`
  - `spec-dock/docs/workflow_spec_authoring.md`
  - `spec-dock/docs/workflow_issue.md`
  - `spec-dock/docs/phase_plan_issue.md`
  - `spec-dock/docs/authoring/issue-plan.md`
  - `spec-dock/active/issue/{requirement,design,plan}.md`
  - `spec-dock/active/epic/{requirement,design}.md`
  - `spec-dock/active/epic/discussions/20260605t080509z-adr-skill-docs-template-context-surface-ownership.md`
  - `iss-00162` context surface inventory
  - `iss-00165` workflow docs boundary design
  - `iss-00166` template scaffold requirement
  - `iss-00186` research / disc artifacts:
    - `20260613t082454z-research-issue-execution-step-gate-analysis.md`
    - `20260613t082641z-research-skill-workflow-spine-policy-analysis.md`
    - `20260613t083027z-research-deep-consultant-skill-policy-findings.md`
    - `20260613t084318z-disc-issue-execution-skill-update-direction.md`
- local context で解決できたこと:
  - 追加 ADR は基本不要で、既存 accepted ADR「Skills = operational workflow spine / Docs = detail semantics / Templates = scaffold」を適用すれば足りる。
  - `workflow_issue.md` には per-step review / commit / delegation / completion policy が既に存在する。
  - 問題の中心は rule 不在ではなく、`spec-dock-issue-execution` skill の first-read surface に `single current step -> review pass -> commit -> clean -> next step unlock` が十分目立たないこと。
  - `iss-00166` が templates scaffold consistency の主領域を既に持っているため、templates 全面 rewrite を `iss-00186` に吸収すると scope が膨らむ。
  - `tests/unit/infra/test_init_update.py` は provider `spec-dock-issue-execution` skill / `workflow_issue.md` の fragment を assert しており、文言変更時は最小 assertion update が必要になる。
- まだ人間判断が必要な理由:
  - template / prompt / empirical harness まで含めるかは、技術的な正誤ではなく、今回の issue を小さく確実に閉じるか、横断的に一気に整えるかという優先順位判断であるため。

## 回答案 (必須)
- Option A:
  - 最小 scope。
  - 必須変更は `spec-dock-issue-execution` skill の additive per-step cadence reminder と、必要最小限の test assertion update のみ。
  - `workflow_issue.md` / authoring docs / templates / prompt は inspection のみで、変更は follow-up に回す。
- Option B:
  - 推奨 scope。
  - 必須変更は provider `spec-dock-issue-execution` skill、必要最小限の `workflow_issue.md` exact semantics 補強、関連 test assertion update、dogfooding mirror / validate / sync 確認。
  - authoring docs / templates / `/execute-issue` prompt は alignment check を行い、重大な矛盾だけ同 issue 内で小さく修正する。全面 template rewrite や empirical harness は follow-up。
- Option C:
  - 広めの横断 scope。
  - skill、workflow docs、authoring docs、templates、`/execute-issue` prompt、必要なら empirical compliance harness まで同一 issue で扱う。
  - 一気に整う可能性はあるが、`iss-00166` 等の既存分担と重なり、step 数と review コストが大きくなる。

## Codex の分析 (必須)
- 判断軸:
  - agent 追随性を上げる first-read surface の強化。
  - 既存 ADR の責務分担に反しないこと。
  - `iss-00166` など近傍 issue との scope 重複を増やさないこと。
  - per-step review / commit を計画自体で守れる粒度にすること。
- tradeoff:
  - Option A は小さいが、`workflow_issue.md` 側の `Step Result Approval` / final commit 境界などの曖昧さが残る。
  - Option B は、skill の first-read 改善と detail authority の補強を両立しやすい。
  - Option C は包括的だが、templates / prompt / empirical harness が混ざり、1 step = 1 review scope = 1 commit の設計が重くなる。
- リスク:
  - scope を広げすぎると、skill hardening issue が scaffold governance / prompt governance / empirical harness issue に膨張する。
  - scope を狭めすぎると、skill だけ変わって workflow docs の用語曖昧さが残る。
  - templates を compliance authority に近づける変更は既存 ADR と衝突する。
- 具体シナリオ / edge case:
  - S01/S02 が同じファイルを触ると agent がまとめて実装しやすいため、skill 入口に single-step loop を置く必要がある。
  - `degraded mode` や `approved-local-execution` が通常 success に見えると、親 agent direct implementation を誘発するため、workflow docs で例外境界を明確にする必要がある。
  - template の `N/A` delegated role 表現が気になる場合でも、既存 `iss-00166` の領域と重なるため、今回の issue では alignment check と重大矛盾の小修正に留める方が分割しやすい。

## Codex の推奨案 (必須)
- 推奨:
  - Option B。
- 理由:
  - ユーザーが問題視した「複数 step の同時実装」「per-step review / commit 欠落」「メイン agent の直接実装」を、first-read skill と workflow detail の両方で抑えられる。
  - 既存 ADR の `compact workflow spine in skills + details in docs/templates` に最も合う。
  - templates / prompt / empirical harness を全て必須にしないため、`iss-00186` を小さく reviewable に保てる。
- 未回答時の影響:
  - スコープが固定できず、requirement / design / plan の AC、対象外、変更対象、implementation step、reviewer gate が確定しない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User selected Option B.
- 回答:
  - 「オプションBを採用します。」
- 回答日時:
  - 2026-06-16

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
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Option B は、`spec-dock-issue-execution` skill の first-read gate spine と `workflow_issue.md` の detail semantics を同時に補強しつつ、templates / prompt / empirical harness の全面横断作業を必須範囲から外せるため、既存 ADR と近傍 issue 分担に最も整合する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - 必須 scope は provider `spec-dock-issue-execution` skill、必要最小限の `workflow_issue.md` exact semantics 補強、関連 test assertion update、dogfooding mirror / validate / sync 確認とする。
  - authoring docs / templates / `/execute-issue` prompt は alignment check 対象とし、重大な矛盾だけ同 issue 内の小修正を許容する。
  - empirical harness、全面 template rewrite、runtime enforcement は対象外または follow-up とする。
- `design.md`:
  - Surface responsibility table と変更対象 / alignment check / follow-up 境界を Option B 前提で記述する。
- `plan.md`:
  - research adoption、skill update、workflow docs update、test assertion update、alignment check、mirror/sync/validate、review gates を分離した実行 step とする。
- `ADR`:
  - 追加しない。既存 accepted ADR の適用として扱う。
- reflected_to 更新方針:
  - canonical docs と `report.md` Evidence Adoption Ledger へ反映後、必要に応じて `reflected_to` を更新する。
- adoption reflection:
  - `report.md` の Evidence Adoption Ledger と Spec Authoring Gate に、Option B 採用と blocking question 解消を記録する。

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
