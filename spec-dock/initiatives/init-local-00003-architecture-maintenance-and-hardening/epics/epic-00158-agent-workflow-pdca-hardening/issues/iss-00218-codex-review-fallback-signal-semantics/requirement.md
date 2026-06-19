---
種別: 要件定義書（Issue）
ID: "iss-00218"
タイトル: "Codex Review Fallback Signal Semantics"
関連GitHub: ["#218"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["epic-00158", "init-local-00003"]
---

# iss-00218 Codex Review Fallback Signal Semantics — 要件定義（何を、なぜ行うか）

## 目的
- GitHub PR observation が、Codex の no-findings signal を submitted PR review object と issue comment transport の違いだけで誤って human gate に残し続けないようにする。
- `fallback_issue_comment` の既存安全契約は維持し、厳密条件を満たす no-findings issue comment だけを新 signal `codex_no_findings_issue_comment` として merge-prepared evidence に昇格できるようにする。
- retryable な待機状態と、待っても解消しない low-confidence fallback / non-retryable 状態を operator action 上も分離する。

## 背景・現状
- PR #216 では、latest head の CI は pass、`mergeStateStatus=CLEAN`、unresolved thread / changes requested は観測されなかった。
- しかし Codex の no-findings は submitted PR review object ではなく issue comment として `Codex Review: Didn't find any major issues. Breezy!` の形で観測された。
- 現行 `github-pr-observation` は current-boundary Codex issue comment を一律 `completion_signal="fallback_issue_comment"` / `confidence="low"` とし、`human_gate` / `wait_or_resume` に落とす。
- そのため repeated resume をしても、issue comment transport が submitted PR review object に変化せず、同じ human gate が再発した。
- 既存 docs は `fallback_issue_comment` を low-confidence / non-promoting と明記しており、この契約自体は generic issue comment false pass を防ぐために維持する。

## 情報源
- `discussions/20260619t131514z-research-pr-observation-fallback-signal-root-cause-analysis.md`
- `discussions/20260619t151927z-disc-fallback-signal-improvement-options.md`
- `discussions/20260619t152719z-interview-no-findings-issue-comment-promotion-boundary.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_snapshot.py`
- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
- `tests/unit/infra/test_init_update.py`
- `iss-00187` の PR review completion signal contract discussion

## 対象ユーザー / 利用シナリオ
- 主な利用者:
  - `github-pr-observation` / `github-pr-merge-preparer` を使って PR の review / CI / merge readiness を観測する agent と maintainer。
- 代表シナリオ:
  - Codex review request 後、Codex が PR review object ではなく no-findings issue comment を返す。
  - CI、head、review blocker が安全条件を満たす場合は、agent が merge-prepared と判断して closeout へ進める。
  - generic issue comment、古い head の comment、CI pending / failed、unresolved thread、changes requested、collection limitation がある場合は pass しない。

## スコープ
- 必須:
  - Provider-side `github-pr-observation` installed skill / scripts の completion signal taxonomy を拡張する。
  - `codex_no_findings_issue_comment` を追加し、厳密条件を満たす場合だけ `passed` / `merge_prepared` / `observation_complete=true` にする。
  - 既存 `fallback_issue_comment` は low-confidence / non-promoting のまま維持する。
  - `wait_or_resume` を non-retryable generic fallback に返さないようにし、retryable pending と分ける。
  - fake `gh` fixture による regression tests を追加・更新する。
  - `github-pr-observation/SKILL.md` と必要な shipped / dogfooding docs を更新する。
- 禁止:
  - `fallback_issue_comment` 自体を条件付き success に意味変更する。
  - Codex-authored でない issue comment、曖昧な進捗 comment、任意の肯定的 comment を no-findings として扱う。
  - CI non-pass、stale head、draft / non-open PR、unresolved thread、changes requested、blocking collection failure を no-findings comment で上書きする。
  - GitHub API の任意 endpoint / query / raw `gh` args を追加する。
- 対象外:
  - Codex bot がどの transport を選ぶかの外部仕様変更。
  - product-wide ADR として machine-authored issue comment 全般を formal review completion にする判断。
  - PR merge-preparer 側だけの waiver / workaround。

## 非交渉制約
- `fallback_issue_comment` は引き続き `confidence="low"` / non-promoting supporting evidence とする。
- 新 signal は additive contract とし、既存 submitted PR review object の high-confidence pass path を壊さない。
- Current trigger boundary と expected head の対応が確認できない no-findings issue comment は昇格しない。
- Blocker precedence は常に no-findings promotion より優先する。
- 実観測の PR #216 文言 `Codex Review: Didn't find any major issues. Breezy!` は、今回解消する事故の再現条件として strict allow-list の対象に含める。
- `confidence` はまず既存互換を優先し、新 signal には `medium` を使う。新 enum 値を増やす場合は別途 schema / docs / tests で明示する。

## 前提
- `@codex review` trigger / resume boundary は既存 script contract に従う。
- `head-sha` が指定されている場合、観測対象 head と expected head の一致を safety condition にできる。
- Existing fake `gh` tests は PR metadata、comments、reviews、review comments、threads、checks を hermetic に再現できる。

## 受け入れ条件
- AC-001 strict no-findings issue comment promotion:
  - アクター: PR observation collector / wait script。
  - 前提: Codex-authored issue comment が current trigger boundary 内にあり、expected head が current PR head と一致し、body が strict no-findings allow-list に一致する。CI は passed、PR は open / non-draft、merge blocker はなく、current unresolved thread / changes requested / blocking collection failure はない。
  - 操作: PR observation snapshot または wait を実行する。
  - 期待結果: `completion_signal="codex_no_findings_issue_comment"`、`confidence="medium"`、`decision.status="passed"`、`decision.recommended_next_action="merge_prepared"`、`observation_complete=true` になる。
  - 観測点: stdout JSON の `codex_review.lifecycle`、`decision`、top-level normalized / overall status。
- AC-002 generic fallback non-promotion:
  - アクター: PR observation collector / wait script。
  - 前提: Current-boundary Codex issue comment はあるが、body が strict no-findings allow-list に一致しない。
  - 操作: PR observation snapshot または wait を実行する。
  - 期待結果: `fallback_issue_comment` は low-confidence / non-promoting のままで、`merge_prepared` へ昇格しない。non-retryable fallback は `wait_or_resume` ではない human action を返す。
  - 観測点: stdout JSON の `completion_signal`、`confidence`、`fallback_pass_candidate` または後継 candidate、`recommended_next_action`。
- AC-003 blocker precedence:
  - アクター: PR observation collector / wait script。
  - 前提: Strict no-findings issue comment は存在するが、current unresolved thread、changes requested、CI failed / pending、draft / non-open PR、stale head、blocking collection failure のいずれかがある。
  - 操作: PR observation snapshot または wait を実行する。
  - 期待結果: no-findings signal は blocker を上書きせず、既存の blocker action が優先される。
  - 観測点: `status_reason`、`recommended_next_action`、`observation_complete`。
- AC-004 boundary rejection:
  - アクター: PR observation collector。
  - 前提: No-findings issue comment が trigger boundary 外、または expected head と矛盾する古い観測に属する。
  - 操作: PR observation snapshot を実行する。
  - 期待結果: `codex_no_findings_issue_comment` に昇格しない。
  - 観測点: selected/current signal と decision payload。
- AC-005 documentation clarity:
  - アクター: maintainer / agent。
  - 前提: `github-pr-observation/SKILL.md` を読む。
  - 操作: completion signal taxonomy と recommended action を確認する。
  - 期待結果: submitted PR review、strict no-findings issue comment、generic fallback issue comment、missing completion signal、retryable pending、non-retryable fallback の違いが読める。
  - 観測点: provider-side skill doc と dogfooding mirror inspection。

## 例外・エッジケース
- EC-001: `Codex Review: Didn't find any major issues. Breezy!`
  - 条件: 実観測と同じ Codex no-findings wording が current-boundary issue comment として存在する。
  - 期待: strict no-findings allow-list に一致し、他 safety condition が満たされれば新 signal に昇格する。
- EC-002: `No major issues found.`
  - 条件: 既存 matcher が認識している no-major-issues line が存在する。
  - 期待: 他 safety condition が満たされれば新 signal に昇格する。
- EC-003: generic progress comment
  - 条件: `I am still reviewing this PR.` など no-findings ではない Codex issue comment がある。
  - 期待: `fallback_issue_comment` のまま pass しない。
- EC-004: blockers coexist
  - 条件: no-findings issue comment と changes requested / unresolved thread が同居する。
  - 期待: blocker action が勝つ。
- EC-005: CI non-pass
  - 条件: no-findings issue comment はあるが CI が pending / running / failed / none。
  - 期待: CI action が勝ち、merge-prepared にはならない。
- EC-006: collection limitation
  - 条件: review/thread collection に blocking limitation がある。
  - 期待: no-findings issue comment だけでは pass しない。

## 用語（ドメイン語彙）
- `fallback_issue_comment`: Codex-authored current-boundary issue comment を見つけたが、formal completion として扱えない low-confidence fallback signal。
- `codex_no_findings_issue_comment`: Strict safety condition を満たす Codex no-findings issue comment を formal completion として扱う新 signal。
- `strict no-findings allow-list`: false pass を避けるために限定された no-findings body matcher。今回の実観測文言と既存 `No major issues found.` 系を含む。
- `retryable pending`: 待機または resume により結果が変わり得る状態。
- `non-retryable fallback`: 待機しても transport / evidence classification が変わらないため、人間確認または証拠モデル改善が必要な状態。

## 未確定事項
- Blocking question:
  - なし。Option A は user-approved で、残る詳細は issue-local design / tests で固定できる。
- Non-blocking implementation note:
  - `retryability` / `resolution_class` を独立 field として追加するか、既存 `recommended_next_action` / `status_reason` の改善に留めるかは design で決める。
