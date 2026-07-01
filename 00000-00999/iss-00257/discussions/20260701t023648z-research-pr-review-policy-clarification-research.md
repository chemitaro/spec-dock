---
種別: research
ID: "20260701t023648z-research"
タイトル: "PR Review Policy Clarification Research"
状態: "draft | completed | archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["iss-00257"]
関連: []
authority: "synthesized"
derived_from:
  - "specdock-pr-review-policy-update.zip/README.md"
  - "specdock-pr-review-policy-update.zip/docs/issue-draft.md"
  - "specdock-pr-review-policy-update.zip/docs/implementation-notes.md"
  - "specdock-pr-review-policy-update.zip/docs/codex-initial-prompt.md"
  - "specdock-pr-review-policy-update.zip/docs/self-review.md"
  - "specdock-pr-review-policy-update.zip/docs/bundle-checks.json"
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/design.md"
  - "spec-dock/active/issue/plan.md"
  - "spec-dock/active/issue/discussions/20260701t022257z-interview-parent-epic-p2-promotion-policy.md"
  - "spec-dock/active/epic/requirement.md"
  - "spec-dock/active/epic/design.md"
  - ".agents/skills/github-pr-observation/scripts/codex-review-instructions.md"
  - ".agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py"
  - ".agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py"
  - ".agents/skills/github-pr-merge-preparer/SKILL.md"
  - "spec-dock/templates/discussions/pr-repair-batch.md"
  - "tests/unit/infra/test_init_update.py"
reflected_to: []
---

# 20260701t023648z-research PR Review Policy Clarification Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- `iss-00257` の requirement / design / plan を具体化する前に、添付 bundle の意図、現行 repo の実装・テスト・mirror 状態、親 Epic との衝突、追加でユーザー判断が必要な gap を整理する。
- 特に、P2/P3 の non-blocking 化、protected-domain P2 promotion の廃止、terminal P2/P3-only observation の no-mutation 境界、PR repair batch の persistence policy、`root_cause_family` の扱いを明確にする。

## sources / 調査方法 (必須)
- 参照先:
  - 添付 ZIP:
    - `README.md`
    - `docs/issue-draft.md`
    - `docs/implementation-notes.md`
    - `docs/codex-initial-prompt.md`
    - `docs/self-review.md`
    - `docs/bundle-checks.json`
    - `repo-files/...` の 6 Markdown replacement files
  - Active Issue:
    - `spec-dock/active/issue/requirement.md`
    - `spec-dock/active/issue/design.md`
    - `spec-dock/active/issue/plan.md`
    - `spec-dock/active/issue/discussions/20260701t022257z-interview-parent-epic-p2-promotion-policy.md`
  - Parent Epic:
    - `spec-dock/active/epic/requirement.md`
    - `spec-dock/active/epic/design.md`
  - Current implementation / assets:
    - `.agents/skills/github-pr-observation/scripts/codex-review-instructions.md`
    - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
    - `.agents/skills/github-pr-observation/scripts/lib/pr_observation_wait.py`
    - `.agents/skills/github-pr-merge-preparer/SKILL.md`
    - `spec-dock/templates/discussions/pr-repair-batch.md`
    - provider mirrors under `src/spec_dock/assets/install_root/...` and `src/spec_dock/assets/spec_dock/...`
  - Tests:
    - `tests/unit/infra/test_init_update.py`
- 検証手順:
  - `./spec-dock/scripts/spec-dock active show` で active issue が `iss-00257` であることを確認した。
  - `./spec-dock/scripts/spec-dock guidance issue-planning` で state が `requirement-capture` / `requirement-scaffold` であることを確認した。
  - `rg` で `promoted_blocker`, `protected_domain`, `non_blocking_followup`, `P2/P3`, `review-clean`, `root_cause_family` を検索した。
  - ZIP を managed tmp に展開し、replacement Markdown と現行 repo file の `shasum` を比較した。
  - provider/dogfooding mirror の一致を `cmp` / `shasum` / 既存 tests から確認した。
- 実験条件:
  - 実装変更はまだ行っていない。
  - 親 `epic-00224` docs は別 worktree で作業中のため、この Issue では編集しない制約がある。
  - ZIP は `/private/tmp/codex-agent-work/501/session-20260701t023446z-iss-00257-clarification-research-e58bd62a/` に展開して比較した。

## facts / 観測できた事実 (必須)
- Active state:
  - active initiative は `init-local-00003`。
  - active epic は `epic-00224`。
  - active issue は `iss-00257`。
  - active branch は `iss-00257-severity-aware-pr-review-policy`。
- Planning state:
  - `guidance issue-planning` は `state: requirement-capture`、`reason_code: requirement-scaffold` を返した。
  - `design.md` と `plan.md` は `artifact_state: awaiting-assurance-compose` の placeholder で、まだ本文を書き始める段階ではない。
- User-approved clarification:
  - `20260701t022257z-interview-parent-epic-p2-promotion-policy.md` で、`iss-00257` 内では旧 `P2 + protected_domain + machine_evidence => promoted_blocker` を廃止・上書きする扱いが承認された。
  - ただし親 `epic-00224` docs はこの worktree では修正しないことも明示された。
- Bundle policy:
  - 添付 bundle は `P0/P1 block merge`, `P2/P3 are reportable but non-blocking`, `P2/P3 must not be auto-promoted to P1 solely due protected domain or deterministic evidence` を core policy としている。
  - `implementation-notes.md` は blocker policy を `P0/P1 => blocker`, `P2/P3 => non_blocking_followup`, `protected_domain` / `machine_evidence` は metadata とする、と示している。
  - `codex-initial-prompt.md` は `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` と installed mirror の `P2 + protected_domain + machine_evidence => promoted_blocker` を変更対象として明示している。
  - `self-review.md` は terminal P2/P3-only で no branch mutation / no batch update / no push / no re-review としている。
- Current Markdown state:
  - 現行 `codex-review-instructions.md` は `merge-blocking reviewer` と `Do not report non-blocking P2/P3 findings` を含む旧方針。
  - 現行 `github-pr-merge-preparer/SKILL.md` は `review-clean` と `merge-prepared` の分離を一部持つが、bundle の severity-aware / terminal P2/P3-only / root-cause-family batch triage ほど明示的ではない。
  - 現行 `spec-dock/templates/discussions/pr-repair-batch.md` は root cause / review-clean separation を一部持つが、bundle の persistence policy と terminal non-blocking boundary ほど明示的ではない。
- Bundle vs repo file hashes:
  - 現行 `.agents/.../codex-review-instructions.md` と provider mirror は同じ hash だが、bundle replacement とは異なる。
  - 現行 `.agents/.../github-pr-merge-preparer/SKILL.md` と provider mirror は同じ hash だが、bundle replacement とは異なる。
  - 現行 `spec-dock/templates/discussions/pr-repair-batch.md` と provider mirror は同じ hash だが、bundle replacement とは異なる。
- Current code state:
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py` は `P2` かつ `protected_domain` かつ `machine_evidence` の場合に `disposition = "promoted_blocker"` / `reason = "p2_protected_domain_with_machine_evidence"` としている。
  - blocker fingerprints は `blocker` と `promoted_blocker` の両方から生成される。
  - P2/P3-only かつ head / CI / review decision / unresolved-thread / collection failure gates が clean の場合、`completion_signal = "blocker_policy_no_action"` へ進める既存経路がある。
  - `.agents/.../pr_review_snapshot.py` と provider mirror は byte-identical。
  - `pr_observation_wait.py` は blocker fingerprints を使って automation stalled を判定するが、`root_cause_family` の構造化フィールドは見つからなかった。
- Current test state:
  - `test_issue_232_review_collector_treats_p2_only_comment_as_non_blocking` は P2-only が `blocker_policy_no_action` / `merge_prepared` になることを既に保証している。
  - `test_issue_232_review_collector_treats_p1_comment_as_blocker` と pull review body test は P1 が blocker になることを保証している。
  - `test_issue_232_review_collector_promotes_protected_p2_with_machine_evidence` は旧方針を期待しており、今回の変更で更新対象になる。
  - `test_issue_232_review_collector_keeps_one_sided_p2_non_blocking` は protected-only P2 / machine-evidence-only P2 / P3 が non-blocking であることを既に保証している。
  - `test_issue_232_review_collector_preserves_review_decision_blocker_for_p2_only` は P2-only でも GitHub review decision が `CHANGES_REQUESTED` なら human gate が残ることを保証している。
  - `test_issue_232_review_collector_keeps_priorityless_comment_on_fallback_path` は priorityless comment を low-confidence fallback として扱うことを保証している。
  - `test_issue_176_s05b_codex_review_trigger_helper_is_installed_by_init_and_update` は旧 instruction 文言 `Do not report non-blocking P2/P3 findings` を期待しており、更新対象になる。
  - `test_issue_75_pr_monitor_assets_retired_and_observation_scaffold_present` と `test_issue_75_pr_workflow_guidance_uses_observation_without_pr_monitor_routing` は provider/dogfooding mirror parity を確認している。
  - `test_issue_197_pr_review_snapshot_provider_wrapper_invokes_python_entrypoint` は provider/mirror script parity を確認している。

## inference / 推測 (必須)
- 事実から推測したこと:
  - Requirement では、今回の Issue の primary objective を「severity reporting と repair action の分離」として置くのが自然。
  - Scope は Markdown asset replacement、blocker policy implementation、tests update、provider/dogfooding/install mirror parity verification に分けるとよい。
  - Non-scope には親 `epic-00224` docs の修正、PR merge、issue finish、review thread resolve、review dismiss、branch deletion、GitHub platform conversation resolution の自動処理を入れるべき。
  - `protected_domain` と `machine_evidence` は削除せず、terminal report / follow-up triage 用 metadata として保持する方が bundle と既存 parser の両方に合う。
  - `blocker_policy.blocker_fingerprints` は P0/P1 のみから作るようにすると、P2/P3-only observation が automation stalled / repair loop に入らない。
  - Existing CHANGES_REQUESTED / unresolved-thread / collection limitation は P2/P3 severity policy とは別 gate として残すべき。
  - Provider-side asset と dogfooding mirror は同時更新が必要。片方だけ更新すると既存 mirror parity tests に引っかかる。
- 推測の根拠:
  - Bundle の `implementation-notes.md` と `codex-initial-prompt.md` が code/test follow-up を明示している。
  - 現行 tests は P2-only の merge-prepared path と P1 blocker path を既に持つため、protected+machine-evidence P2 の期待を non-blocking へ反転すれば主要 policy が表現できる。
  - Existing tests と skill docs は GitHub mergeability / platform thread resolution を semantic repair target と分けている。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - `uv run pytest` はまだ実行していない。
  - ZIP replacement files を実際に適用した後の full diff はまだ作っていない。
  - `root_cause_family` を runtime JSON に構造化出力する必要があるか、docs/template/merge-preparer skill の運用語彙として扱えば足りるかは未確定。
  - `github-pr-merge-preparer` の実運用に、terminal P2/P3-only final response の固定フォーマットをどこまで要求するかは未確定。
- 確認できない理由:
  - 現時点は clarification phase であり、requirement / design / plan の具体化前に実装変更やテスト実行へ進まないため。
  - `root_cause_family` の扱いは、Issue scope を code parser まで広げるかどうかに関わるため、人間判断を挟む価値がある。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - `root_cause_family` を、この Issue で `pr_review_snapshot.py` / observation JSON の first-class field として抽出・出力する必要があるか。
- pressure-test question として切り出すべき候補:
  - `root_cause_family` は今回の implementation scope に含め、Codex review body の `root_cause_family:` 行を parser で拾って blocker policy finding / blocker fingerprint / automation stalled に反映するべきですか？
- 質問せずに解決できた候補:
  - 親 Epic docs を編集するかどうか: ユーザー回答により、この Issue では編集しないと確定。
  - P2 protected-domain + machine-evidence promotion を残すかどうか: ユーザー回答により、この Issue では廃止・上書きと確定。
  - Bundle replacement files を根拠として使うかどうか: 添付 README / prompt / notes が drop-in replacement と明記しているため採用可能。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `review-clean` vs `merge-prepared`
  - `semantic merge blocker` vs `platform human gate`
  - `protected_domain` vs `merge-blocking severity`
  - `blocker_fingerprint` vs `root_cause_family`
- 既存 docs / code / tests / discussions での使われ方:
  - `review-clean`: review findings が残っていない状態。bundle では P2/P3 が残る場合 `review-clean: no` でも `merge-prepared: yes` があり得る。
  - `merge-prepared`: human が merge 判断できる状態。GitHub platform mergeability を claim するものではない。
  - `semantic merge blocker`: P0/P1 と required CI / semantic merge blockers。P2/P3 は含めない。
  - `platform human gate`: branch protection が unresolved conversation resolution を要求する場合など、code repair target ではなく human / platform gate として扱う。
  - `protected_domain`: review attention を上げる metadata。今回の Issue では severity 自動昇格の根拠にしない。
  - `blocker_fingerprint`: 現行 automation stalled 判定で使う hash。
  - `root_cause_family`: bundle の review / merge-preparer / repair-batch が求める grouping key。ただし現行 runtime JSON には first-class field がない。
- 判断が必要な理由:
  - `root_cause_family` を code-level contract にするか docs-level triage vocabulary にするかで、design と plan の作業量、tests、risk が変わる。

## edge cases / 具体シナリオ (必須)
- edge case:
  - P2 protected-domain + machine-evidence:
    - Example: `P2: auth permission regression. Test: failing test proves access is widened.`
    - Expected for this Issue: `non_blocking_followup`, `protected_domain: true`, `machine_evidence: true`, `blocker_count: 0`, `completion_signal: blocker_policy_no_action` when other gates are clean.
  - P1 protected-domain + machine-evidence:
    - Expected: `blocker`, `blocker_count: 1`, `recommended_next_action: address_review_feedback`.
  - P2-only with GitHub `CHANGES_REQUESTED` review decision:
    - Expected: semantic blocker policy is non-blocking, but GitHub review decision produces human gate / manual review requirement.
  - P2/P3-only with unresolved review threads:
    - Expected: if unresolved-thread state is actionable or platform branch protection requires resolution, this is human/platform gate, not autonomous code repair.
  - Priorityless Codex comment:
    - Expected: low-confidence fallback / manual review required, not silent merge-prepared.
  - Multiple priorities in one body:
    - Expected: declared finding priorities are parsed from declared lines / badges, not incidental mentions.
  - Terminal P2/P3-only after clean CI:
    - Expected: no repo-persistent batch update, no push, no re-review, final response reports grouped non-blocking findings.
- その edge case が requirement / design / plan に与える影響:
  - Requirement needs explicit observable outcomes for P2/P3-only, P0/P1, protected-domain metadata, platform gate separation, and no branch mutation.
  - Design needs explicit blocker policy table and state transitions for `blocker_policy_no_action`.
  - Plan needs focused tests covering protected+machine-evidence P2 non-blocking, old phrase removal / new phrase installation, provider/dogfooding mirror parity, and no parent Epic docs modification.

## implications / 判断への含意 (必須)
- Requirement:
  - Primary objective: severity-aware review reporting and repair-loop action separation.
  - Must state that P2/P3 are reportable but non-blocking and never auto-promoted solely by protected domain or deterministic evidence.
  - Must state terminal P2/P3-only observation avoids branch mutation, repo batch update, push, and re-review.
  - Must state parent `epic-00224` docs are out of scope in this worktree.
  - Must state GitHub platform conversation resolution is human/platform gate, not semantic code repair target.
- Design:
  - `pr_review_snapshot.py` policy table:
    - P0/P1 -> `blocker`, reason `p0_p1_priority`.
    - P2/P3 -> `non_blocking_followup`, reason should be renamed or documented as policy-level non-blocking.
    - Unknown priority -> `unknown`.
    - `protected_domain` and `machine_evidence` remain metadata.
  - `blocker_policy_blockers` should exclude `promoted_blocker` because that disposition should disappear.
  - `blocker_policy_no_action_promotes` should remain gated by head match, no stale context, no actionable unresolved threads, no CHANGES_REQUESTED / requested review, no current pending review, and no blocking collection failure.
  - Merge-preparer and repair-batch docs should make repo-persistent batch conditional on blocking repair / blocking triage.
- Plan:
  - Apply bundle replacement Markdown to six files while preserving provider/dogfooding mirror parity.
  - Update runtime blocker policy in both `.agents` mirror and provider source, or update provider then mirror to keep parity.
  - Update old tests that assert old review instruction and promoted P2 behavior.
  - Add/adjust tests for protected-domain + machine-evidence P2 as non-blocking, P0/P1 as blockers, multiple priority parsing, mirror parity, and terminal P2/P3-only no persistent batch requirement.
  - Run focused tests first, then broader unit lane if feasible.
- ADR:
  - Not required unless `root_cause_family` is elevated into a durable runtime JSON contract or parent Epic policy is updated outside this Issue. Current user constraint points to Issue-local adoption and report evidence instead.

## リスク/制約 (任意)
- Constraint: Do not edit parent `epic-00224` docs in this worktree.
- Risk: If `root_cause_family` remains docs-only, future automation-stalled behavior will still be based on fingerprints, not semantic families.
- Risk: If `root_cause_family` is added as runtime output now, scope increases and parsing free-form review bodies becomes a new contract surface.
- Risk: If terminal P2/P3 findings are not persisted anywhere, final response must be explicit enough that a human can still make a merge decision with residual risk visible.
- Risk: Copying bundle Markdown blindly may overwrite local improvements made after bundle generation. Current hash comparison shows bundle differs from current files, so implementation should review diffs before applying.

## 反映先 (任意)
- reflected_to:
  - planned: `spec-dock/active/issue/requirement.md`
  - planned: `spec-dock/active/issue/design.md`
  - planned: `spec-dock/active/issue/plan.md`
  - planned: `spec-dock/active/issue/report.md` Evidence Adoption Ledger

## 参考（References） (任意)
- `specdock-pr-review-policy-update.zip`
- `spec-dock/active/issue/discussions/20260701t022257z-interview-parent-epic-p2-promotion-policy.md`
