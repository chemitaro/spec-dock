---
種別: research
ID: "20260601t091408z-research"
タイトル: "Issue finish synthetic approval source analysis"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-01"
親: ["iss-00149"]
関連: ["#149"]
authority: "synthesized"
derived_from:
  - "https://github.com/chemitaro/spec-dock/issues/149"
  - "spec-dock/docs/workflow_issue.md"
  - "spec-dock/docs/workflow_spec_authoring.md"
  - "spec-dock/docs/workflow_clarification.md"
  - "spec-dock/active/context-pack.md"
  - "spec-dock/.agent/active.json"
  - "spec-dock/scripts/spec_dock_runtime/domain/authority.py"
  - "spec-dock/scripts/spec_dock_runtime/application/set_active.py"
  - "spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py"
  - "tests/domain_runtime/test_authority.py"
  - "tests/cli_runtime/test_issue_lifecycle.py"
reflected_to:
  - "spec-dock/active/issue/requirement.md"
  - "spec-dock/active/issue/report.md"
---

# 20260601t091408z-research Issue finish synthetic approval source analysis

## 調査目的
- GitHub #149 の bug report が repo-local actionable bug かを確認する。
- `issue start` が作る active state と `issue finish` が要求する lifecycle authority gate の不整合を、docs / code / tests / generated active state から確認する。
- requirement phase で固定すべき success condition、non-scope、未確定判断を整理する。

## sources / 調査方法
- 参照先:
  - GitHub issue #149: observed failure、reproduction shape、expected behavior。
  - `spec-dock/docs/workflow_issue.md`: primary lifecycle、`issue start` / `issue finish` 契約、finish authority gate。
  - `spec-dock/docs/workflow_spec_authoring.md`: requirement gate、promotion record / active manifest authority boundary。
  - `spec-dock/docs/workflow_clarification.md`: formal question trigger と interview artifact 条件。
  - `spec-dock/active/context-pack.md`: current active issue の generated authority guidance。
  - `spec-dock/.agent/active.json`: `issue start` 後の active manifest。
  - `spec-dock/scripts/spec_dock_runtime/domain/authority.py`: authority gate と synthetic approval rejection。
  - `spec-dock/scripts/spec_dock_runtime/application/set_active.py`: active manifest entry construction。
  - `spec-dock/scripts/spec_dock_runtime/application/issue_lifecycle.py`: `issue_start()` / `issue_finish()` flow。
  - `tests/domain_runtime/test_authority.py`: synthetic approval の許可 / 拒否対象。
  - `tests/cli_runtime/test_issue_lifecycle.py`: current expected behavior and manual lifecycle promotion test helper。
- 検証手順:
  - `./spec-dock/scripts/spec-dock issue start iss-00149` を実行して active issue を設定した。
  - `spec-dock/.agent/active.json` と `spec-dock/active/context-pack.md` を確認した。
  - `rg` と `sed` で runtime code / tests を確認した。
- 実験条件:
  - worktree: `/Users/iwasawayuuta/.codex/worktrees/e8ee/spec-dock`
  - branch: `iss-00149-issue-finish-synthetic-approval-closeout-bug`
  - active issue: `iss-00149`

## facts / 観測できた事実
- GitHub #149 は `issue start <issue>` 後、PR merge 後の `issue finish` が `active_synthetic_approval_not_lifecycle_approval` で fail-closed する bug report である。
- `workflow_issue.md` は通常の issue execution start を `issue start <target>`、通常の completion を `issue finish` としている。
- 同じ `workflow_issue.md` は、`issue finish` が active manifest issue entry の `authority=approved`、fresh `promotion_record`、exact grant `issue_finish` を要求すると定義している。
- `approved_runtime_promotion_record(node_id=...)` は `promotion_decision: "runtime_active_selection"` を生成する。
- `build_active_manifest()` は active entry 作成時に `approved_runtime_grants()` と `approved_runtime_promotion_record()` を使う。
- `evaluate_authority_gate()` は `implementation_start`、`issue_ready`、`issue_finish`、`phase_completion` に対して `promotion_decision == "runtime_active_selection"` を `active_synthetic_approval_not_lifecycle_approval` として拒否する。
- `issue_finish()` は GitHub close / active clear の前に `_require_issue_finish_authority(active_load.manifest.issue)` を必ず通す。
- `tests/domain_runtime/test_authority.py` は synthetic active approval が lifecycle grants を満たせないことを明示的にテストしている。
- `tests/cli_runtime/test_issue_lifecycle.py` には `_promote_active_issue_lifecycle()` という test helper があり、active issue の `promotion_record.promotion_decision` を `main_orchestrator_promotion` へ直接差し替えると `issue finish` success path が成立する。
- `tests/cli_runtime/test_issue_lifecycle.py` には `test_issue_finish_blocks_normal_active_set_synthetic_approval_before_close` があり、現状の blocking behavior を expected behavior として固定している。
- 現在の `iss-00149` active context-pack は initiative / epic / issue すべてに `downstream_block=active_synthetic_approval_not_lifecycle_approval` を表示している。
- 現在の active manifest の issue entry は `grants` に `issue_finish` を含む一方、`promotion_record.promotion_decision` は `runtime_active_selection` である。

## inference / 推測
- GitHub #149 の root cause は、`issue start` / `active set` が作る runtime active selection と、`issue finish` が要求する lifecycle approval の間に supported transition path がないことである。
- `grants` に `issue_finish` が含まれていても synthetic approval として拒否されるため、operator から見ると grant 表示と実際の gate result が矛盾して見えやすい。
- 現在の fail-closed rule 自体は delegated authoring / artifact authority hardening の安全設計に由来しており、単純に synthetic approval を lifecycle approval と同一視すると authority boundary regression になり得る。

## unverified / 未検証事項
- `issue finish` 自体が lifecycle-grade promotion を内部生成してよいか、または明示 command を挟むべきかは、product workflow の好みと security posture に依存するため未確定。
- `implementation_start` / `issue_ready` / `phase_completion` にも同じ transition gap を解くべきか、この issue では `issue_finish` に閉じるべきかは未確定。
- active manifest に lifecycle grants を表示し続けるべきか、synthetic approval では downstream lifecycle grants を持たせないようにするべきかは design phase の判断が必要。

## terminology conflicts / 用語衝突
- `approved`:
  - active entry は `authority=approved` と表示されるが、lifecycle approval としては synthetic で拒否される。
- `grants`:
  - active entry grants は `issue_finish` を含むが、`promotion_decision=runtime_active_selection` のため `issue_finish` gate を通らない。
- `promotion_record`:
  - runtime active selection も promotion record shape を持つが、workflow / tests 上は lifecycle-grade promotion record とは別物である。
- 判断が必要な理由:
  - 要件上「公式 CLI だけで closeout できる」を満たすには、どの用語 / state transition を official path として認めるかを固定する必要がある。

## edge cases / 具体シナリオ
- GitHub issue がすでに CLOSED:
  - `issue_finish` は already-closed を success として扱う契約だが、現状は authority gate が先に落ちるため active clear まで進めない。
- GitHub close / PR merge は成功済み:
  - 問題は GitHub state ではなく local active authority state なので、GitHub 側の再操作では解決しない。
- active manifest を直接編集する workaround:
  - `promotion_decision` を `main_orchestrator_promotion` へ手動変更すると test helper 相当の success path になるが、generated/runtime state 直接編集であり standard workflow にできない。
- active entry が initiative / epic / issue すべて synthetic:
  - context-pack は全階層に downstream block を表示する。issue finish の最小修正範囲を issue entry だけにするか、階層全体の authority 表示も直すかは design 判断が必要。

## implications / 判断への含意
- Requirement は「`issue start` から始めた通常 issue を、手動 active.json 編集なしで official CLI path だけで `issue finish` できる」を success condition として固定できる。
- Requirement は「synthetic active selection と lifecycle approval の区別を壊さない」を非交渉制約にするべきである。
- Requirement は GitHub close / PR readiness / final delivery をこの issue の修正対象に含めず、authority transition / recovery path に閉じるべきである。
- Design 前に、preferred official path が internal auto-promotion か explicit command かをユーザーに確認する必要がある。

## リスク/制約
- `active_synthetic_approval_not_lifecycle_approval` の fail-closed rule は既存 tests で固定されているため、単に削除すると delegated authoring authority gate の退行になる。
- `workflow_issue.md` の finish contract と `workflow_spec_authoring.md` の Promotion Record boundary の両方に影響するため、docs/tests/runtime の parity を保つ必要がある。

## 反映先
- `spec-dock/active/issue/requirement.md`:
  - background、scope、acceptance criteria、edge cases、unresolved question。
- `spec-dock/active/issue/report.md`:
  - Evidence Adoption Ledger、Spec Authoring Gate。

## 参考（References）
- GitHub issue #149: `issue finish が issue start 由来の active state を synthetic approval として拒否し通常 closeout できない`
- Memory-derived prior observation:
  - `issue finish` は merge/close 後でも `active_synthetic_approval_not_lifecycle_approval` で失敗し得る。
  - 手動 workaround は active issue entry の `promotion_decision` を lifecycle-grade 値へ修正して再実行することだった。
