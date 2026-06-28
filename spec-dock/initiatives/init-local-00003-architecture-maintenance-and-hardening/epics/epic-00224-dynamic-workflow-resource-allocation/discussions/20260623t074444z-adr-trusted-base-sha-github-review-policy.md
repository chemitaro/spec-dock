---
種別: ADR（Architecture Decision Record）
ID: "20260623t074444z-adr"
タイトル: "Script-local Codex Review Instruction"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["epic-00224"]
authority: "accepted"
supersedes:
  - "Trusted Base SHA GitHub Review Policy"
amended_by:
  - "20260628t154553z-adr"
derived_from:
  - "20260623t074452z-disc-adr-decision-synthesis-after-issue-226-closure.md"
  - "iss-00244 PR #245 dogfooding review trigger failure"
  - "20260628t043053z-research-script-local-codex-review-instruction-source.md"
reflected_to:
  - "../design.md"
  - "../plan.md"
  - "../report.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/design.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/plan.md"
  - "20260628t154553z-adr-pr-observation-explicit-review-completion.md"
---

# 20260623t074444z-adr Script-local Codex Review Instruction

## 変更履歴（Supersession / Amendment）

- 2026-06-28: 旧 trusted base-SHA review policy 方針は、この ADR により script-local Codex review instruction 方針へ変更済み。
- 2026-06-29: `20260628t154553z-adr PR Observation Explicit Review Completion` により、review trigger 後の observation completion semantics は explicit Codex artifact model へ補完・変更済み。
- この ADR は「`@codex review` comment に添える instruction source」を決める。Review completion の終了条件、`review_completion_unknown` の扱い、timeout/resume semantics は `20260628t154553z-adr` を authority とする。
- この ADR は、Codex review が完了したか、findings がないか、または merge-prepared かを判断する authority ではない。completion artifact がない状態を no-review-work proof として扱う旧運用は変更済みである。

## ADR 化基準

- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - Codex PR review trigger がどの instruction を使うかは、PR review の品質、dogfooding 速度、外部 automation の再現性に影響する。
  - 旧決定である trusted base-SHA policy は、個人開発 / dogfooding repo では運用の即時性を阻害し、PR #245 で review trigger 自体が起動できない問題を起こした。

## 結論（Decision）

- 旧方針「PR base SHA の `.github/codex/review-policy.md` からのみ policy を読む」は廃止する。
- Codex review trigger は、GitHub 上の base branch / PR head の `.github/codex/review-policy.md` を読みに行かない。
- Review instruction は `github-pr-observation` skill の comment posting script 近傍に置く script-local Markdown を使用する。
  - 採用予定 path:
    - provider authority: `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`
    - dogfooding installed copy: `.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`
- Trigger runtime は local filesystem の script-local Markdown を読み、valid な場合だけ `@codex review` comment に instruction と metadata を含める。
- Script-local Markdown が missing の場合、review trigger は止めない。Instruction なしの deterministic `@codex review` comment を投稿し、metadata に `instruction_status: missing_plain_fallback` を記録する。
- Script-local Markdown が present だが invalid / oversized / unreadable の場合は、設定不備として human gate とし、comment を投稿しない。
- Runtime は caller-provided body、任意 endpoint、任意 path、raw `gh` args を受け付けない。Write surface は引き続き fixed `POST repos/{owner}/{repo}/issues/{pr}/comments` に限定する。
- Trigger evidence には head SHA、instruction path、instruction hash、instruction status、generated body hash、review target を記録する。

## 背景（Context）

- この repository は個人開発 / dogfooding repo であり、PR author と policy author を adversarial に分離する必要がない。
- Review instruction は、モデル変更や review 運用の調整に合わせてしばらく頻繁に変わる可能性が高い。
- 旧方針では、review instruction の変更を main に merge しないと当該 PR の review trigger で検証できない。
- PR #245 では head 側に `.github/codex/review-policy.md` がある一方、base SHA に同 file がないため、`wait_pr_observation.sh --trigger-mode post-once` が `human_gate` になり、Codex review trigger comment が投稿されなかった。
- `.github/codex/review-policy.md` という置き場所は GitHub/Codex の repository policy に見えるが、実際の用途は「comment posting script が `@codex review` に添える instruction」である。したがって script-local asset として管理する方が責務に合う。

## 選択肢（Options considered）

- Option A: PR base SHA の `.github/codex/review-policy.md` を読む。
  - Pros: team / adversarial repo では PR head から policy を弱めにくい。
  - Cons: policy の同一 PR dogfooding ができない。main merge 前に運用変更を検証できない。個人 repo では安全性の利益が小さい。
  - 判断: 廃止する。
- Option B: PR head SHA の `.github/codex/review-policy.md` を読む。
  - Pros: branch 上の変更を同一 PR で検証できる。
  - Cons: GitHub repository policy に見える file を review 対象差分に置くため、責務が曖昧になる。GitHub API fetch が増え、local dogfooding の現在情報より remote state に寄る。
  - 判断: 今回は採用しない。
- Option C: local checkout の `.github/codex/review-policy.md` を読む。
  - Pros: 現在の作業状態を直接使える。
  - Cons: `.github/codex` を汚染し、GitHub 側の policy と comment trigger 用 instruction の境界が曖昧になる。
  - 判断: 採用しない。
- Option D: `github-pr-observation` script-local Markdown を読む。
  - Pros: comment posting runtime の責務に近く、local checkout の最新 instruction を即時に使える。GitHub base branch に依存しない。`.github/codex` を汚染しない。
  - Cons: installed skill asset と provider asset の同期を tests で守る必要がある。
  - 判断: 採用する。

## 判断理由（Rationale）

- この repo の現在の最適化対象は、adversarial policy governance ではなく、個人開発における review instruction の迅速な調整と dogfooding の再現性である。
- GitHub base branch から policy を読む設計は、過去に必要だと考えた security boundary を優先しすぎており、現在の運用目的と合っていない。
- Local script-local instruction は、「今この branch / checkout で review trigger がどう投稿されるか」を最も直接的に表す。
- Missing instruction で review 自体を止めるのは過剰である。Instruction がない場合でも Codex review を実行し、review の有無を確保する方が価値が高い。
- Present だが invalid な instruction は、意図した運用が壊れている状態なので human gate とする。
- Arbitrary body / path / endpoint を許さない fixed write boundary は、今回の方針変更後も必要である。

## 影響（Consequences）

- Positive:
  - PR #245 のように base branch に policy がない状態でも、script-local instruction または plain fallback で Codex review trigger を投稿できる。
  - Review instruction の変更を main merge 前に当該 branch 上で検証できる。
  - `.github/codex/review-policy.md` を bootstrap asset / project policy として管理する必要がなくなる。
  - Review trigger script の責務と instruction の置き場所が一致する。
- Negative / Debt:
  - Team / adversarial repo 向けの base-strict governance はこの ADR の default では扱わない。
  - Installed skill asset と provider asset の parity を regression tests で確認する必要がある。
  - Existing tests / docs / skill text の trusted base-SHA terminology を置換する必要がある。
- 影響範囲:
  - GitHub PR observation skill
  - `trigger_codex_review.sh`
  - `wait_pr_observation.sh` の trigger behavior
  - provider-side installed assets
  - unit tests for installer / shipped skill scripts
  - Epic / Issue docs that mention trusted base-SHA review policy
- 移行/ロールバック:
  - `.github/codex/review-policy.md` は廃止対象とする。
  - Script-local Markdown が存在しない checkout では plain fallback trigger により review を継続できる。
  - 旧 base-SHA fail-closed behavior へ戻す場合は、新 ADR が必要である。

## 非目標（Non-goals）

- `openai/codex-action` 本番移行をこの ADR で決めない。
- 任意の review body / arbitrary prompt injection を許可しない。
- GitHub Checks API / status rollup を CI evidence として採用しない。
- Team / adversarial repository 向けの strict governance mode をこの Issue の default として実装しない。

## 未確定事項（Open Questions）

- Script-local Markdown の max size は旧実装の 32768 bytes を暫定維持するか、より小さい上限にするかを実装時に確定する。
- Plain fallback comment に含める metadata の最小項目は実装時に確定する。ただし `instruction_status: missing_plain_fallback`、`reviewed_head_sha`、`instruction_path` は必須とする。

## 参考（References）

- `20260628t043053z-research-script-local-codex-review-instruction-source.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md`
