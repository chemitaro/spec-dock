---
種別: ADR（Architecture Decision Record）
ID: "20260628t154553z-adr"
タイトル: "PR Observation Explicit Review Completion"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-29"
親: ["epic-00224"]
authority: "accepted"
supersedes:
  - "review_completion_unknown terminal wait behavior"
amends:
  - "20260623t074444z-adr"
  - "20260623t074447z-adr"
derived_from:
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260628t143306z-research-pr-observation-review-completion-signals.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260628t150332z-disc-pr-observation-completion-wait-repair-draft.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md"
  - "PR #245 dogfooding wait failure"
  - "PR #245 delayed review observation and reviewer feedback on premature under-budget timeout"
reflected_to:
  - "../design.md"
  - "../plan.md"
  - "../report.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/design.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/plan.md"
  - "../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md"
---

# 20260628t154553z-adr PR Observation Explicit Review Completion

## ADR 化基準

- hard to reverse: yes
- surprising without context: yes
- real tradeoff: yes
- ADR として残す理由:
  - PR observation の終了条件は、merge-prepared 判断、review repair loop、dogfooding の信頼性を左右する。
  - PR #245 で、`review_completion_unknown` による早期終了後に Codex submitted PR review と 5 件の P1 finding が遅れて投稿され、時間・静穏・fingerprint 安定を review completion の代替証拠にする危険が実際に確認された。
  - これは単なる implementation detail ではなく、GitHub/Codex review をどう観測し、いつ待機を終了してよいかという運用 contract である。

## 結論（Decision）

- PR observation wait は、review completion を explicit Codex artifact でのみ判断する。
- Trusted completion artifact は、current trigger boundary 後かつ expected head SHA に bind された次のいずれかに限定する。
  - Codex-authored submitted pull request review。
  - Codex-authored strict no-findings issue comment。`Reviewed commit` または同等の head binding と、CI / PR metadata / blocker / carryover gate の統合確認を必須とする。
- `completion_signal=none`、selected review comments 0、selected review threads 0、CI passed、quiet window、same fingerprint、trigger からの経過時間、CI pass からの経過時間は review completion proof ではない。
- Trusted completion artifact がないまま overall deadline に到達した場合は、`timeout` / `wait_or_resume` / `observation_complete=false` として返す。
- `review_completion_unknown` は新規 active wait result の terminal status / terminal `decision.status_reason` として返さない。
  - 既存 artifact を読むための legacy vocabulary としてのみ扱う。
  - downstream は legacy `review_completion_unknown` を no-review-work proof、merge-prepared proof、または review completion proof として扱ってはならない。
- quiet window / same fingerprint は、trusted completion artifact が見えた後の hydration stability にのみ使う。
- Overall deadline 未到達の wait loop では、zero-check grace、pending review hydration、late review artifact による fingerprint reset、または configured stability confirmation が残っている場合、早期に `timeout` へ昇格しない。
  - `timeout` は semantic completion ではなく、観測 budget の到達を示す operational boundary である。
  - budget 内で必要な追加 poll が残る場合は、`pending` / `wait_or_resume` 相当の非完了状態を維持する。
- ambiguous Codex output、wrong head、old trigger、reaction-only、generic Codex issue comment は current completion として扱わない。必要に応じて wait / timeout / human gate 側へ倒す。

## 背景（Context）

- PR #245 の dogfooding で、`wait_pr_observation.sh` は次の状態で終了した。
  - CI passed。
  - `completion_signal=none`。
  - selected review comments / threads が 0。
  - `status_reason=review_completion_unknown`。
  - `post_unknown_fresh_audit_required=true`。
- その約 14 分後、同じ head SHA に Codex submitted PR review が投稿され、5 件の P1 unresolved review thread が発生した。
- 現行実装は、一定時間の無変化、CI pass 後の経過時間、quiet window、same fingerprint を組み合わせて no-completion 状態を terminal-like human gate に昇格していた。
- しかし、これらは GitHub surface の観測値が静かだったことを示すだけで、非同期 Codex review worker が完了した証拠ではない。
- `20260623t074444z-adr` は review trigger instruction の source を script-local asset に変更する ADR であり、review completion の終了条件そのものはこの ADR で補完・変更する。
- `20260623t074447z-adr` は blocker-centric PR closure を固定する ADR であり、この ADR はその前段である「review completion が観測済みかどうか」の判定を明確にする。
- 後続の PR #245 dogfooding では、completion artifact を待つ方向へ修正した後、under-budget の zero-check grace / hydration stability 待機まで `timeout` にしてしまう回帰が reviewer から指摘された。この ADR は、no-completion を完了扱いしないことと、budget 内の正当な追加待機を潰さないことを同時に固定する。

## 選択肢（Options considered）

- Option A: 既存の `review_completion_unknown` terminal-like behavior を維持する。
  - Pros:
    - 待機時間を短くしやすい。
    - 既存 orchestration の変更が小さい。
  - Cons:
    - PR #245 型の delayed P1 finding を見逃す。
    - quiet / same fingerprint / selected comments 0 を completion proof と誤認する。
    - `post_unknown_fresh_audit_required` に downstream safety を押し出し、wait loop 自体の責任が曖昧になる。
  - 判断: 棄却する。
- Option B: `review_completion_unknown` を維持したまま timeout を長くする。
  - Pros:
    - 実装差分が小さい。
    - 短い遅延には効く。
  - Cons:
    - 時間は completion proof ではないため、根本原因が残る。
    - モデル / GitHub / queue の遅延が変われば再発する。
  - 判断: 棄却する。
- Option C: explicit artifact model に切り替え、artifact がない場合は retryable timeout / resume にする。
  - Pros:
    - 完了判定を Codex 由来の observable artifact に結びつけられる。
    - false merge-prepared より false timeout / resume 側へ安全に倒せる。
    - PR #245 型の delayed review を regression として固定できる。
  - Cons:
    - Codex no-findings comment の wording / metadata 変化には保守的 matcher と follow-up が必要。
    - review worker が完了 artifact を出さない障害では timeout / resume が増える。
  - 判断: 採用する。
- Option D: PR observation wait 全体を別 state machine として全面 rewrite する。
  - Pros:
    - 長期的には整理しやすい。
  - Cons:
    - 現 Issue の修正範囲を超える。
    - PR trigger instruction source / assurance path rename など他の repair と混ざりやすい。
  - 判断: 今回は採用しない。Option C を最小の contract repair として行う。

## 判断理由（Rationale）

- Merge safety は「レビューが完了していないのに完了扱いする」ことに最も弱い。
- selected comments 0 は「まだ投稿されていない」状態と「投稿済みで findings がない」状態を区別できない。
- quiet window と same fingerprint は、観測済み artifact の hydration が安定したかを見る補助には使えるが、artifact 未出現を completion へ変換する根拠にはならない。
- timeout は operational boundary であり、semantic completion ではない。したがって retry / resume の outcome にすべきであり、human gate や no-review-work proof にしてはならない。
- Blocker-centric PR closure は、review completion artifact が観測された後に finding / no-finding / blocker disposition を評価して初めて成立する。
- completion artifact が見えた直後の GitHub response は、review body、review comments、review threads の hydration が遅れる場合がある。そのため、explicit artifact model は「artifact が見えた瞬間に即終了」ではなく、head/trigger binding と hydration stability を確認したうえで blocker-centric closure へ渡す。
- 一方で、completion artifact がない状態の quiet / fingerprint stability は no-finding の証拠ではない。この二つの stability 用途を混同すると、delayed review 見逃し、または reviewer 指摘のような premature timeout のどちらかを再発させる。

## 影響（Consequences）

- Positive:
  - PR #245 型の delayed Codex review を wait loop が早期に捨てにくくなる。
  - merge-prepared evidence が explicit Codex artifact に近づく。
  - `review_completion_unknown` による曖昧な terminal state と downstream fresh audit 依存を減らせる。
  - wait / timeout / resume の意味が明確になり、手動判断が必要な状態と再試行可能な状態を分けられる。
- Negative / Debt:
  - Codex の no-findings comment 形式が変わる場合、strict matcher を更新する必要がある。
  - 完了 artifact が出ない外部障害では timeout / resume が増え、運用上の待ち時間が長くなる可能性がある。
  - completion artifact 後の hydration stability と、completion artifact 前の no-completion wait は別物として実装・テストする必要がある。
  - Legacy artifact の `review_completion_unknown` は読み取り時にだけ互換 vocabulary として扱う必要がある。
- 影響範囲:
  - `.agents/skills/github-pr-observation/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/SKILL.md`
  - `pr_observation_wait.py`
  - `pr_review_snapshot.py` の current trigger/head binding と hydration handling
  - `tests/unit/infra/test_init_update.py`
  - PR merge-preparation / observation の operational contract
- 移行/ロールバック:
  - 新規 active wait result では `review_completion_unknown` を出さない。
  - 既存 result JSON に含まれる `review_completion_unknown` は legacy evidence として読み、current completion proof には使わない。
  - 旧 terminal behavior へ戻す場合は、この ADR を supersede する新 ADR が必要である。
- Follow-ups:
  - Codex no-findings comment wording の将来バリエーションは、必要になった時点で follow-up Issue または ADR で扱う。

## 非目標（Non-goals）

- GitHub Checks API / statusCheckRollup を PR observation の authority に追加しない。
- PR trigger instruction source を再変更しない。
- Codex review worker の外部 SLA をこの ADR で保証しない。
- 全面 state-machine rewrite はこの ADR の直接 scope ではない。

## 旧決定との関係（Supersession / Amendment）

- `20260623t074444z-adr Script-local Codex Review Instruction`:
  - 変更済み: review trigger instruction source は script-local asset のまま維持する。
  - 補完: 同 ADR は trigger comment の instruction source を決めるものであり、review completion の終了条件は本 ADR が authority を持つ。
  - 矛盾回避: base-SHA review policy / missing policy human gate 前提は、script-local instruction ADR により既に変更済みであり、本 ADR では扱わない。
- `20260623t074447z-adr Blocker Centric PR Risk Closure And Re Review`:
  - 補完: blocker-centric closure は review completion artifact が観測済みであることを前提に適用する。
  - 変更済み: `review_completion_unknown` は blocker disposition や merge-prepared evidence の前提にならない。
- Epic `design.md` / `plan.md` の trusted base-SHA review policy 記述:
  - 変更済み: `20260623t074444z-adr` により script-local Codex review instruction へ置換済み。
  - 本 ADR はさらに、review trigger 後の observation completion semantics を explicit artifact model へ置換する。

## 参考（References）

- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260628t143306z-research-pr-observation-review-completion-signals.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/discussions/20260628t150332z-disc-pr-observation-completion-wait-repair-draft.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/requirement.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/design.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/plan.md`
- `../issues/iss-00244-simplify-issue-execution-guidance-into-plan-centric-preflight-validation/report.md`
- `20260623t074444z-adr-trusted-base-sha-github-review-policy.md`
- `20260623t074447z-adr-blocker-centric-pr-risk-closure-rereview.md`
