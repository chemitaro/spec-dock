---
種別: interview
ID: "20260619t152719z-interview"
タイトル: "No Findings Issue Comment Promotion Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00218"]
関連: []
scope: "issue"
scope_id: "iss-00218"
created_at: "2026-06-20T00:27:19+09:00"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260619t131514z-research"
  - "20260619t151927z-disc"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
---

# 20260619t152719z-interview No Findings Issue Comment Promotion Boundary

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - `codex_no_findings_issue_comment` を merge-prepared に昇格する acceptance condition と scope。
  - `design.md`:
    - completion signal taxonomy、confidence、retryability、merge-prepared effect の設計。
  - `plan.md`:
    - fake `gh` fixture と wait/observation propagation tests の必須ケース。
  - `ADR`:
    - 現時点では不要。ただし product-wide policy に広げるなら ADR 候補。
- chat 上の軽微な一問では足りない理由:
  - 回答によって、strict no-findings issue comment を `merge_prepared` に昇格するか、manual/non-retryable gate に留めるかが変わり、要件・設計・テスト義務が大きく変わるため。

## 質問の目的 (必須)
- 対象者:
  - Product owner / maintainer
- 何を明確にする質問か:
  - submitted PR review object が存在せず、Codex no-issues が issue comment transport だけで観測された場合の promotion boundary。
- 回答が後続判断へ与える影響:
  - `codex_no_findings_issue_comment` を `passed` / `merge_prepared` / `observation_complete=true` へ昇格する要件にするか、または `manual_review_required_non_retryable` のような human confirmation state に留めるかを決める。

## 質問 (必須)
- pressure-test question:
  - strict no-findings issue comment は、十分な安全条件を満たすなら formal PR review object と同等の merge-prepared evidence として扱ってよいか。
- 質問:
  - Codex-authored、current trigger/current head、strict no-findings allow-list、CI passed、merge blocker なし、unresolved thread / changes-requested なし、blocking collection failure なし、という条件をすべて満たす issue comment を、新 signal `codex_no_findings_issue_comment` として `passed` / `merge_prepared` / `observation_complete=true` に昇格してよいですか？
- 回答してほしいこと:
  - Option A / B / C のいずれを採用するか。別案がある場合は、pre-merge と post-merge closeout で扱いを分けるかも含めて回答してほしい。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - `20260619t131514z-research-pr-observation-fallback-signal-root-cause-analysis.md`
  - `20260619t151927z-disc-fallback-signal-improvement-options.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `spec-dock/initiatives/.../iss-00187-actions-pr-observation-ci-state/discussions/20260616t000000z-03-disc-architect-pr-review-completion-signal-contract.md`
- local context で解決できたこと:
  - `fallback_issue_comment` は現行 contract では low-confidence / non-promoting であり、直接昇格すべきではない。
  - deep consultants と既存 discussion は、generic fallback を残して strict no-findings issue comment に distinct signal を追加する案を推奨している。
  - repeated resume では issue comment が submitted PR review object に変わらないため、retryable pending と non-retryable classification mismatch を分ける必要がある。
- まだ人間判断が必要な理由:
  - source-grounded な推奨は Option A だが、issue comment を formal PR review object と同等の merge-prepared evidence に昇格するかは product/workflow owner の risk tolerance を決める判断である。

## 回答案 (必須)
- Option A:
  - 推奨。条件をすべて満たす strict no-findings issue comment は `codex_no_findings_issue_comment` として `passed` / `merge_prepared` / `observation_complete=true` に昇格する。
  - `fallback_issue_comment` は引き続き low-confidence / non-promoting にする。
- Option B:
  - strict no-findings issue comment でも pre-merge では自動 `merge_prepared` にせず、`manual_review_required_non_retryable` として返す。post-merge closeout では evidence note として issue finish を許可する。
- Option C:
  - 現行維持。issue comment transport はすべて non-promoting fallback のままにし、operator が都度 human gate / waiver で処理する。

## Codex の分析 (必須)
- 判断軸:
  - false pass risk、false block risk、operator action の明確さ、既存 contract との互換性、future maintenance。
- tradeoff:
  - Option A は body allow-list / boundary checks / blocker precedence の設計負荷を引き受ける代わりに、PR #216 型の false block を根本解決できる。
  - Option B は安全側だが、pre-merge の merge-prepared false block は残る。
  - Option C は実装不要だが、今回と同じ詰まりが再発する。
- リスク:
  - Option A で allow-list が広すぎると false pass risk がある。
  - Option B/C では no-issues signal が来ていても workflow が human gate に残り、agentic closeout が止まりやすい。
- 具体シナリオ / edge case:
  - no-findings comment が current head ではなく古い head を指す場合は昇格してはならない。
  - no-findings comment と unresolved thread / changes requested が同居する場合は blockers が勝つ。
  - CI pending / failed 中は no-findings comment だけで pass してはならない。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - `fallback_issue_comment` の安全契約を壊さず、strict no-findings completion だけを独立 signal として扱えるため。
  - PR #216 型の false block を解消し、generic issue comment false pass を避けられるため。
  - 既存 iss-00187 discussion / deep consultant 2 名の推奨と一致するため。
- 未回答時の影響:
  - requirement / design / plan で acceptance criteria と tests を確定できず、特に pre-merge merge-prepared 昇格の有無が曖昧になる。

## ユーザー回答 (回答後に必須)
- answer capture:
  - ユーザーは Option A を採用すると回答した。
- 回答:
  - Option A を採用する。条件をすべて満たす strict no-findings issue comment は、新 signal `codex_no_findings_issue_comment` として `passed` / `merge_prepared` / `observation_complete=true` に昇格する。
- 回答日時:
  - 2026-06-20

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Option A は、`fallback_issue_comment` の安全側 contract を維持しつつ、strict no-findings issue comment だけを distinct completion signal として扱うため、PR #216 型の false block を解消しながら generic issue comment false pass を避けられる。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - AC と scope に、`codex_no_findings_issue_comment` の昇格条件を明記する。
  - `fallback_issue_comment` は引き続き low-confidence / non-promoting とすることを非交渉制約に入れる。
- `design.md`:
  - completion signal taxonomy に `codex_no_findings_issue_comment` を追加する。
  - current trigger / current head / strict allow-list / blockers absent / CI passed / no collection limitation を昇格条件として設計する。
  - `wait_or_resume` は retryable pending に限定し、generic fallback は non-retryable human action として分離する。
- `plan.md`:
  - fake `gh` fixture で strict no-findings issue comment promotion、generic fallback non-promotion、old head / pre-trigger rejection、blocker precedence、CI non-pass rejection、wait propagation をテスト義務にする。
- `ADR`:
  - 現時点では不要。issue-local additive signal として扱う。
- reflected_to 更新方針:
  - requirement / design / plan 作成時に本回答を採用し、front matter `reflected_to` は必要に応じて更新する。
- adoption reflection:
  - この回答により、iss-00218 は Option A を前提に要件定義へ進める。

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
