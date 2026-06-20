---
種別: disc
ID: "20260619t151927z-disc"
タイトル: "Fallback Signal Improvement Options"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00218"]
関連: []
authority: "proposed"
derived_from:
  - "20260619t131514z-research"
  - "deep-consultant Faraday findings 2026-06-20"
  - "deep-consultant Hegel findings 2026-06-20"
reflected_to: []
---

# 20260619t151927z-disc Fallback Signal Improvement Options

## 対象論点 (必須)
- 今回整理する論点:
  - `fallback_issue_comment_low_confidence` によって PR observation / merge-prepared gate が human gate に残り続ける問題への具体的な対処案。
  - Codex no-issues が submitted PR review object ではなく issue comment として出る場合、その signal をどこまで merge-prepared evidence に昇格してよいか。
  - `wait_or_resume` が retryable pending と non-retryable confidence gap の両方に使われる問題をどう分離するか。
- この synthesis が必要な理由:
  - root cause research では問題の原因を整理したが、requirement / design / plan に進むには、複数の改善策の tradeoff と採用方針を明確にする必要がある。
  - 単に `fallback_issue_comment` を成功扱いにすると false pass risk が高く、逆に現状維持では PR #216 型の false block が残る。

## derived question sheets / research (必須)
- `interview`:
  - なし。
- `research`:
  - `20260619t131514z-research-pr-observation-fallback-signal-root-cause-analysis.md`
- その他の根拠:
  - deep-consultant Faraday: strict no-findings issue comment を新 signal に昇格し、generic fallback は非昇格のままにする案を推奨。
  - deep-consultant Hegel: 後方互換性と安全性の観点から、`fallback_issue_comment` の意味は変えず `codex_no_findings_issue_comment` を追加する案を推奨。
  - iss-00187 prior discussion: `codex_no_findings_issue_comment` 相当の additive signal 案、wrapper / docs / tests の変更候補を既に提示。

## synthesis (必須)
- 合意済みのこと:
  - `fallback_issue_comment` は現行 docs / code / tests 上、low-confidence / non-promoting の安全側 contract であり、この意味を直接変更するべきではない。
  - PR #216 型の問題は「レビュー gate を弱めたい」ではなく、「strict no-findings issue comment と generic fallback issue comment を同じ bucket に入れている」ことから起きている。
  - `wait_or_resume` は retryable pending に使うべきで、再観測しても transport が変わらない evidence classification mismatch には不適切。
  - no-findings issue comment を扱う場合でも、current trigger / current head / Codex-authored / strict allow-list / blockers absent / CI passed などの条件が必要。
- 未合意 / 未確定のこと:
  - `confidence` に `medium-high` のような新値を増やすか、既存 enum 互換を優先して `medium` にするか。
  - 実観測文言 `Codex Review: Didn't find any major issues. Breezy!` を allow-list に含める場合、どの正規化ルールを採用するか。
  - 未 merge PR でも strict no-findings issue comment を `merge_prepared` に昇格するか、まずは terminal-low-confidence として human confirmation を求めるか。
  - closeout workflow で PR merged 後の confidence gap を issue finish の blocker にするか、evidence note にするか。
- source-grounded に解決できたこと:
  - 現行実装は `fallback_issue_comment` を意図的に `human_gate` / `wait_or_resume` に固定している。
  - 過去 discussion は generic fallback を残しつつ strict no-findings を新 signal にする案をすでに有力案として残している。
  - downstream waiver だけでは根本解決にならず、collector の evidence taxonomy を改善する必要がある。

## 選択肢 / tradeoff (必須)
- Option A: 新 signal `codex_no_findings_issue_comment` を追加する。
  - Pros:
    - `fallback_issue_comment` の後方互換 contract を壊さない。
    - strict no-findings issue comment だけを terminal completion として扱える。
    - collector / observation snapshot / wait loop の三層に一貫した signal を流せる。
    - PR #216 型の false block を解消できる。
  - Cons:
    - body allow-list / trigger boundary / head correlation / blocker precedence の設計と fixture が必要。
    - output schema に新しい completion signal を増やすため、docs と tests の更新が必要。
- Option B: 既存 `fallback_issue_comment` を条件付きで昇格する。
  - Pros:
    - 実装量は小さく見える。
    - 既存 field を再利用できる。
  - Cons:
    - `fallback_issue_comment` が low-confidence / non-promoting である既存 contract と名前の意味を壊す。
    - generic Codex issue comment を false pass しやすくなる。
    - 既存 tests / docs の意図と衝突し、将来の読者が安全境界を誤解しやすい。
- Option C: downstream merge-preparer / closeout で waiver する。
  - Pros:
    - 観測器本体の変更なしに運用回避できる。
    - 緊急時の人間採用フローとしては使える。
  - Cons:
    - observation consumer ごとに判断が分岐し、source of truth が弱くなる。
    - open PR の merge-prepared false block を根本解決しない。
    - issue execution が同じ human gate に再び詰まりやすい。
- Option D: `retryability` / `resolution_class` だけを追加する。
  - Pros:
    - `wait_or_resume` の誤誘導を減らせる。
    - operator UX と closeout report の正確性は改善する。
  - Cons:
    - no-findings issue comment を pass として扱う根拠分類は別途必要。
    - 単独では green/open PR が human gate に残る。
- Option E: merged PR だけ特別扱いする。
  - Pros:
    - post-merge closeout の詰まりを安全側に解消しやすい。
    - 既に merged なら merge-prepared 判断のリスクは低い。
  - Cons:
    - pre-merge の正しい green/no-findings PR を止め続ける。
    - PR observation の一般 contract ではなく closeout workaround になる。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `github-pr-observation/SKILL.md` に completion signal taxonomy を追加し、submitted PR review / strict no-findings issue comment / generic fallback issue comment / missing signal を明確に分ける。
  - `workflow_issue.md` または github-pr-merge-preparer guidance に、retryable pending と non-retryable observation limitation の違いを記録する。
  - `wait_or_resume` は pending / latency guard / timeout-resumable に限定し、non-retryable fallback は別 action / reason を返す。
- まだ proposal に留める理由:
  - body allow-list と confidence enum の最終判断は requirement / design authoring で明示する必要がある。
  - 実装前に fake `gh` fixture の再現範囲を確定する必要がある。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - `fallback_issue_comment` を直接昇格しないこと。
  - strict no-findings issue comment を新 completion signal として扱う条件。
  - `wait_or_resume` を non-retryable confidence gap に返さないこと。
- `design.md`:
  - `completion_signal`, `evidence_transport`, `review_verdict`, `confidence`, `retryability`, `merge_prepared_effect` の分離。
  - `codex_no_findings_issue_comment` / `no_findings_completion_candidate` の schema。
  - blocker precedence と trigger/head boundary rules。
- `plan.md`:
  - review collector, observation snapshot, wait loop, docs/mirror, tests の段階実装。
  - fake `gh` fixture による PR #216 相当の再現。
- `ADR`:
  - 現時点では不要。machine-authored issue comment を product-wide の formal review completion とみなす方針に拡張する場合のみ ADR 候補。
- `report.md` Evidence Adoption Ledger:
  - 本 discussion を requirement/design/plan 作成時の採用 evidence として記録する。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no for issue-local implementation; conditional yes if product-wide policy is introduced.
- hard to reverse:
  - no if implemented as additive signal with tests; yes if `fallback_issue_comment` semantics are rewritten globally.
- surprising without context:
  - yes. Issue comments normally feel less authoritative than PR reviews, so promotion conditions must be documented.
- real tradeoff:
  - yes. False pass risk and false block risk must be balanced.
- ADR 化しない場合の反映先:
  - `requirement.md`, `design.md`, `plan.md`, `github-pr-observation/SKILL.md`

## 推奨案 (必須)
- Best practice proposal:
  - `fallback_issue_comment` は今後も low-confidence / non-promoting として保持する。
  - strict no-findings issue comment 用に新 signal `codex_no_findings_issue_comment` を追加する。
  - 新 signal は、少なくとも次の条件をすべて満たす場合だけ `passed` / `merge_prepared` / `observation_complete=true` に昇格できる:
    - Codex-authored issue comment。
    - current trigger boundary 内。
    - expected latest head と観測 head が一致し、comment が対象 head と矛盾しない。
    - body が strict allow-list に一致する。
    - CI checks が passed。
    - PR が draft / non-open / stale head / visible merge blocker 状態ではない。
    - current selected unresolved thread がない。
    - selected changes-requested evidence がない。
    - review/thread collection に blocking limitation がない。
  - `fallback_pass_candidate` は既存の non-promoting signal として残し、必要なら `no_findings_completion_candidate` を新設する。
  - `wait_or_resume` は retryable pending 専用にし、generic fallback / non-retryable low-confidence は `manual_review_required_non_retryable` 相当の action/reason に分ける。
  - `confidence` は後方互換を優先してまず `medium` を推奨する。`medium-high` を増やす場合は schema / docs / tests で明示する。

この案は、generic issue comment false pass を避けつつ、PR #216 型の no-issues transport mismatch を解消できる。既存の安全側 contract を壊さず、collector から wait loop まで同じ evidence model を伝搬できるため、最も保守しやすい。

## 推奨反映先 (必須)
- `requirement.md`:
  - AC: strict no-findings issue comment が条件を満たすと terminal no-findings completion として扱われる。
  - AC: generic fallback / ambiguous comment は pass しない。
  - AC: `wait_or_resume` は non-retryable fallback に返らない。
- `design.md`:
  - signal taxonomy と schema field。
  - current-boundary / expected-head / blocker precedence rules。
  - propagation rule: observation snapshot / wait loop は collector の decision を再解釈しない。
- `plan.md`:
  - S01 collector taxonomy。
  - S02 observation snapshot / wait propagation。
  - S03 retryability / action semantics。
  - S90 docs and mirror update。
  - S99 validation and fake `gh` fixture suite。
- `ADR`:
  - なし。ただし product-wide review evidence policy にするなら別途 ADR。
- `report.md` Evidence Adoption Ledger:
  - 本 discussion と deep-consultant findings の採用判断。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - `fallback_issue_comment` 自体の昇格: 既存 contract と名前の意味を壊し、false pass risk が高い。
  - merge-preparer-only waiver: downstream workaround であり、observation consumers 間の判断が分岐する。
  - merged PR 専用特別扱い: closeout には効くが、pre-merge merge-prepared false block を解決しない。
- deferred:
  - `retryability` / `resolution_class` の詳細 schema: 新 completion signal と合わせて設計するが、pass 判定の根拠とは分離する。
  - ADR 化: issue-local additive change の範囲なら不要。方針を product-wide に広げる場合に再検討する。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - requirement に、新 signal の条件、non-promoting fallback の維持、non-retryable fallback の action 分離を記載する。
  - design に、signal taxonomy、schema、body allow-list、head/trigger boundary、blocker precedence、propagation rules を記載する。
  - plan に、fake `gh` fixture の具体ケースと provider/mirror/docs update steps を記載する。
  - ADR は現時点では作らない。
- 追加で作る discussion docs:
  - body allow-list と confidence enum に未決が残る場合だけ、短い interview または disc を追加する。
