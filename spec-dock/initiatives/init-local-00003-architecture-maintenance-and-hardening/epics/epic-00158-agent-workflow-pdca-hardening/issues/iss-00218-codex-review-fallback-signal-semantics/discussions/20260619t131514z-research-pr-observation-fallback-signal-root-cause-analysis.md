---
種別: research
ID: "20260619t131514z-research"
タイトル: "PR Observation Fallback Signal Root Cause Analysis"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-06-19"
親: ["iss-00218"]
関連: []
authority: "synthesized"
derived_from:
  - "PR #216 observation after iss-00214"
  - "iss-00187 discussions on PR review completion signal contract"
  - "deep-consultant findings 2026-06-19"
reflected_to: []
---

# 20260619t131514z-research PR Observation Fallback Signal Root Cause Analysis

## 調査目的 (必須)
- PR #216 / iss-00214 の merge preparation で発生した `fallback_issue_comment_low_confidence` human gate が、単発の運用事故なのか、PR observation の証拠モデル上の未解決問題なのかを明らかにする。
- どのような問題が起き、なぜ repeated resume では解決しなかったのかを整理し、iss-00218 の requirement / design / plan に渡せる原因分析を作る。

## sources / 調査方法 (必須)
- 参照先:
  - GitHub PR #216: https://github.com/chemitaro/spec-dock/pull/216
  - `gh pr view 216 --repo chemitaro/spec-dock --json state,mergedAt,mergeCommit,headRefOid,baseRefName,url`
  - `gh pr view 216 --repo chemitaro/spec-dock --json state,isDraft,mergeStateStatus,headRefOid,url,statusCheckRollup,comments,reviews`
  - `gh pr checks 216 --repo chemitaro/spec-dock`
  - `spec-dock/active/issue/report.md` before finishing iss-00214
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t000000z-03-disc-architect-pr-review-completion-signal-contract.md`
  - deep-consultant Banach / Carver findings, 2026-06-19
- 検証手順:
  - PR #216 が merged であること、merge commit、latest head、check status、review comment / review object の形を `gh` で確認した。
  - provider-side PR observation skill docs と Python modules で、`fallback_issue_comment` の分類と decision への反映を確認した。
  - iss-00187 の過去 discussion で、no-findings issue comment を terminal signal として扱う案が既に検討されていたことを確認した。
  - deep-consultant 2 名に、PR observation semantics と SpecDock lifecycle/gate mismatch の観点から read-only 分析を依頼した。
- 実験条件:
  - PR #216 は `MERGED`、merge commit は `42af291f209014828fc8d0fd4640fb2f20c213b1`。
  - PR #216 の latest observed head は `9fab10fa14d1feb7c141b2d1a2e6885e9bedc847`。
  - `validate` x2 と `provider-tests` x2 は all pass。
  - `mergeStateStatus` は `CLEAN`。
  - Codex bot の no-issues comment は存在するが、`reviews` は空。

## facts / 観測できた事実 (必須)
- PR #216 は `2026-06-19T13:10:19Z` に merged され、GitHub issue #214 / SpecDock issue `iss-00214` は `issue finish` で close / active clear 済み。
- PR #216 の最新 head `9fab10fa14d1feb7c141b2d1a2e6885e9bedc847` では、`validate` と `provider-tests` がすべて success だった。
- PR #216 には Codex bot の issue comment があり、latest head について `Codex Review: Didn't find any major issues. Breezy!` と表示していた。
- しかし `gh pr view ... --json reviews` の `reviews` は空であり、Codex の no-issues signal は submitted PR review object としては観測されなかった。
- `pr_review_snapshot.py` は Codex-authored submitted PR review を見つけた場合だけ `completion_signal="submitted_pull_request_review"` / `confidence="high"` とする。
- 同じ module は current-boundary の Codex-authored issue comment を見つけると `completion_signal="fallback_issue_comment"` / `confidence="low"` とする。
- 同じ module は `completion_signal == "fallback_issue_comment"` の場合、`decision_status_reason="fallback_issue_comment_low_confidence"`、`decision_status="human_gate"`、`decision_action="wait_or_resume"` を返す。
- `pr_observation_wait.py` も `completion_signal == "fallback_issue_comment"` または `decision_reason == "fallback_issue_comment_low_confidence"` を `human_gate` / `wait_or_resume` として扱う。
- `github-pr-observation/SKILL.md` は、issue comments / reactions / quiet windows は fallback/supporting evidence であり、`fallback_issue_comment` は pass / complete / merge-ready に昇格しないと明記している。
- iss-00187 の過去 discussion は、generic issue comment を成功扱いしない設計を維持しつつ、strict no-findings issue comment だけを `codex_no_findings_issue_comment` のような新 signal として扱う案を既に提示していた。

## inference / 推測 (必須)
- 事実から推測したこと:
  - 今回の問題は PR #216 個別の CI / implementation failure ではなく、PR observation の review completion evidence model が現行 Codex bot の no-issues transport とずれていることに起因する。
  - 現行設計は「generic issue comment をレビュー完了証拠にしない」という安全側の意図を持つが、「strict no-issues issue comment」を generic fallback と同じ bucket に入れているため、merge safety evidence が揃った PR でも human gate に落ちる。
  - repeated resume で解決しなかった理由は、欠けていたのが時間待ちの非同期結果ではなく evidence transport の分類だったため。既に issue comment として保存された artifact は、再観測しても submitted PR review object には変わらない。
  - `wait_or_resume` が retryable pending と non-retryable evidence classification mismatch の両方に使われており、operator には「待てば解決する状態」に見えやすい。
  - merge readiness gate と observation confidence gate が混ざっており、実装リスク / review feedback の不足ではなく、観測器側の信頼度不足が issue execution closeout を止めた。
- 推測の根拠:
  - PR #216 は merged / checks pass / unresolved thread 0 / CLEAN だった一方、observation は `fallback_issue_comment_low_confidence` だけで `human_gate` を返し続けた。
  - code path は `fallback_issue_comment` を明示的に low-confidence / non-promoting としている。
  - iss-00187 discussion はこの問題を予見し、`codex_no_findings_issue_comment` を distinct terminal signal として追加する案を残している。
  - deep-consultant 2 名とも、問題の本質を「レビュー gate を弱めること」ではなく「PR lifecycle completion / observation confidence / retryability の分離」と分析した。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - Codex bot がどの条件で submitted PR review object ではなく issue comment transport を使うのか。
  - no-issues comment body の許容表現をどこまで allow-list すべきか。
  - GitHub API から issue comment と exact head SHA の対応をどの程度強く証明できるか。
  - merged PR だけ特別扱いするべきか、未 merge PR でも strict no-findings fallback を terminal と見なすべきか。
  - `fallback_pass_candidate` の既存判定は `No major issues found.` 系だけを許容しているが、今回実際に観測された `Codex Review: Didn't find any major issues. Breezy!` をどの signal として扱うべきか。
- 確認できない理由:
  - Codex bot / GitHub connector 側の transport selection はこの repository 内の実装では制御できない。
  - body allow-list は安全性と実用性の tradeoff があり、requirement / design authoring で明示判断が必要。
  - 今回の依頼範囲は issue 作成・start・research 作成であり、実装調査や fixture 設計は次の planning / execution で行う。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - strict no-findings issue comment を、未 merge PR でも merge-prepared 判定に昇格してよいか。それとも merged PR / post-merge closeout 専用の terminal-low-confidence state に留めるか。
  - `fallback_issue_comment_low_confidence` を成功に昇格するのではなく、`manual_review_required_non_retryable` / `terminal_low_confidence` のような別 status を追加する方針でよいか。
  - no-issues comment の body matching を英語固定 allow-list にするか、Codex Review prefix と reviewed commit line も条件に含めるか。
- pressure-test question として切り出すべき候補:
  - `checks passed + CLEAN + unresolved thread 0 + no-issues issue comment` でも、古い head の comment なら絶対に pass しないことをどう証明するか。
  - fallback no-issues comment と同時に changes requested / unresolved thread がある場合、どの evidence を優先するか。
  - missing completion signal と fallback completion signal の retryability を output schema でどう分けるか。
- 質問せずに解決できた候補:
  - PR #216 で起きた human gate は CI failure ではなく、CI repair 後も review completion evidence classification により残った。
  - `fallback_issue_comment` が現行実装で low-confidence / non-promoting なのは意図された安全側設計である。
  - `wait_or_resume` が今回の状態に適さない理由は、時間待ちでは evidence transport が変わらないためである。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `human_gate`
  - `wait_or_resume`
  - `fallback_issue_comment`
  - `merge_prepared`
  - `observation_complete`
- 既存 docs / code / tests / discussions での使われ方:
  - `human_gate` は actionable feedback、blocking limitation、fallback low confidence、missing completion など複数の意味で使われる。
  - `wait_or_resume` は本来 retryable pending に向くが、現行では fallback low-confidence terminal-like state にも返る。
  - `fallback_issue_comment` は low-confidence supporting evidence として扱われ、`fallback_pass_candidate` があっても top-level status を昇格しない。
  - `merge_prepared` は checks / review / merge blocker absence を総合した downstream gate だが、review completion confidence gap で止まる。
  - `observation_complete=false` は「まだ結果が来ていない」と「結果は来たが transport が低信頼」を区別しない。
- 判断が必要な理由:
  - operator が次に取るべき行動が異なる。pending なら待つべきだが、non-retryable confidence gap なら人間が evidence を採用するか、証拠モデルを拡張する必要がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - EC-001: strict no-findings issue comment が current trigger / expected head に対応し、checks pass、unresolved thread 0、changes requested 0。
  - EC-002: generic Codex issue comment、曖昧な賞賛、途中経過 comment が current trigger にある。
  - EC-003: strict no-findings issue comment はあるが、unresolved review thread または changes requested evidence がある。
  - EC-004: strict no-findings issue comment はあるが、comment が古い head / trigger boundary 外。
  - EC-005: checks pending / running 中に no-findings issue comment だけが先に来る。
  - EC-006: PR が already merged で、checks pass、fallback no-findings comment だけが review completion evidence として残っている。
- その edge case が requirement / design / plan に与える影響:
  - EC-001 / EC-006 は pass / terminal-low-confidence / manual-confirmed のどれに落とすかを仕様化する必要がある。
  - EC-002 は現行どおり non-promoting fallback に留めるべき。
  - EC-003 は fallback no-findings より actionable blockers を優先する必要がある。
  - EC-004 は head / trigger boundary の相関を受け入れ条件に含める必要がある。
  - EC-005 は `wait_or_resume` を維持する pending case として扱う必要がある。

## implications / 判断への含意 (必須)
- iss-00218 の requirement は「fallback issue comment を成功扱いに緩める」ではなく、「PR observation の evidence transport / confidence / retryability / merge-prepared gate への影響を分離する」と定義すべき。
- design では少なくとも次の軸を分ける必要がある:
  - review completion signal
  - evidence transport
  - confidence
  - review verdict
  - retryability
  - merge-prepared effect
- `codex_no_findings_issue_comment` のような distinct signal を追加する案が有力。ただし generic `fallback_issue_comment` の意味を変えると既存安全契約とテストを壊すため、後方互換の観点では新 signal 追加が望ましい。
- output schema には、`wait_or_resume` と human-only/non-retryable state を区別できる field が必要になる可能性が高い。
- SpecDock closeout guidance では、PR merged 後の observation confidence gap を issue finish の blocker とするか、evidence note として扱うかを明文化する必要がある。
- ADR は現時点では必須ではないが、「machine-authored issue comment を formal review completion として扱う」方針を product-wide に固定するなら ADR 候補になる。

## リスク/制約 (任意)
- 無条件に Codex issue comment を success 扱いすると、途中経過や曖昧な comment を no-review-work と誤認する false pass risk がある。
- 一方で現行のままでは、実質的に merge-ready / already-merged な PR が repeated resume でも解消しない human gate に残る false block risk がある。
- body allow-list を厳しくしすぎると、実際の Codex no-issues wording の揺れを取り逃がす。緩くしすぎると false pass risk が増える。
- GitHub API / Codex connector の transport は外部挙動であり、repo 側では観測と分類の設計で吸収する必要がある。

## 反映先 (任意)
- reflected_to:
  - `iss-00218/requirement.md`
  - `iss-00218/design.md`
  - `iss-00218/plan.md`
  - 必要なら `github-pr-observation/SKILL.md`
  - 必要なら `workflow_issue.md`

## 参考（References） (任意)
- PR #216: https://github.com/chemitaro/spec-dock/pull/216
- GitHub issue #218: https://github.com/chemitaro/spec-dock/issues/218
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00187-actions-pr-observation-ci-state/discussions/20260616t000000z-03-disc-architect-pr-review-completion-signal-contract.md`
