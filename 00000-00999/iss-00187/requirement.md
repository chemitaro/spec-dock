---
種別: 要件定義書（Issue）
ID: "iss-00187"
タイトル: "Use Actions Endpoint For PR Observation CI State"
関連GitHub: ["#187"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-17"
親: ["epic-00158", "init-local-00003"]
---

# iss-00187 Use Actions Endpoint For PR Observation CI State — 要件定義（何を、なぜ行うか）

## 目的
- `github-pr-observation` の CI 状態観測を、Fine-grained PAT で付与可能な `Actions` read 権限を中心に動作する contract へ変更する。
- PR 作成後 / push 後の観測で、CI の成功・失敗・実行中・pending・判断不能を後続 agent が判断できる状態を維持する。
- `Checks` read を通常解決策として要求することで workflow が止まる運用問題を解消しつつ、観測できない範囲を成功扱いしない false-pass-safe な出力にする。

## 背景・現状
- 現状の挙動:
  - `github-pr-observation` は PR の head SHA に対して CI と Codex review の状態を収集し、`ci.status`、`normalized_status`、`recommended_next_action`、`limitations` を含む final JSON を返す。
  - 現行の CI collector は主に `GET /repos/{repo}/commits/{sha}/check-runs`、`GET /repos/{repo}/commits/{sha}/status`、`gh pr view --json mergeStateStatus,statusCheckRollup` を使い、失敗 check run の詳細取得に `GET /repos/{repo}/actions/runs/{run_id}/jobs` を使う。
  - Permission denied は `github_token_permission_denied` limitation と `recommended_next_action="fix_github_token_permissions"` として表現される。
- 現状の課題:
  - Fine-grained PAT では `Checks` read 相当の権限を利用者が付与できない運用があり、GitHub Actions 上では CI 状態を確認できるにもかかわらず PR observation が permission blocker で止まる。
  - この blocker は利用者の token 設定ミスではなく、現在の collector が実運用で付与可能な permission surface と噛み合っていないことに起因する。
  - `fix_github_token_permissions` を通常解決策として返しても、利用者が dashboard 上で解決できない場合がある。
- 再現手順:
  1. Fine-grained PAT を使い、GitHub Actions workflow は読めるが check runs / status rollup は読めない権限状態にする。
  2. PR に対して `github-pr-observation` の snapshot / wait script を実行する。
  3. CI が GitHub Actions 上で観測可能であっても、check runs 取得の permission denied により final JSON が `unknown` / `fix_github_token_permissions` へ倒れる。
- 観測点:
  - UI: GitHub Actions の workflow run / job 状態。
  - HTTP: GitHub REST API の workflow runs / workflow jobs / check runs / commit statuses / PR metadata read。
  - DB: 該当なし。
  - ログ: PR observation final JSON、`limitations`、stderr progress、fake `gh` test log。
- 情報源:
  - GitHub issue #187。
  - `discussions/20260615t154753z-01-research-actions-ci-observation-scope.md`。
  - `discussions/20260615t154753z-02-interview-actions-only-pass-contract.md`。
  - `.agents/skills/github-pr-observation/scripts/lib/fetch_pr_checks_snapshot.sh`。
  - `.agents/skills/github-pr-observation/scripts/fetch_pr_observation_snapshot.sh`。
  - `.agents/skills/github-pr-observation/scripts/wait_pr_observation.sh`。
  - `tests/unit/infra/test_init_update.py` の fake `gh` script regression tests。
  - GitHub REST docs: workflow runs/jobs は `Actions` read、check runs は `Checks` read、combined commit status は `Commit statuses` read を要求する。

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - Fine-grained PAT 環境で SpecDock / Codex PR workflow を運用するユーザー。
  - PR 作成後または push 後に、merge preparation / repair workflow の判断材料として PR observation final JSON を読む agent。
- 代表シナリオ:
  - GitHub Actions の CI が成功しており Codex review も完了している PR で、後続 workflow が `merge_prepared` へ進めるか判断する。
  - GitHub Actions の CI が失敗している PR で、後続 workflow が `fix_ci` を推奨できる。
  - GitHub Actions の CI が queued / pending / running の PR で、後続 workflow が待機または resume を推奨できる。
  - Actions では観測できない外部 check provider があり得る PR で、成功扱いする範囲と limitation を final JSON 上で区別する。

## スコープ
- 必須:
  - Provider-side PR observation assets under `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` を正本として変更する。
  - Dogfooding mirror under `.agents/skills/github-pr-observation/` は provider source と整合する検証対象として扱う。
  - CI collector は GitHub Actions workflow runs / jobs を primary observation surface とする。
  - Fine-grained PAT の通常運用では、付与不能な `Checks` read を通常解決策として要求しない。
  - Actions-only green evidence を `ci.status="passed"` として許可する。ただし full check/status rollup または external check provider coverage を証明できない場合は final JSON に明示的な limitation を残す。
  - 失敗、実行中、pending、queued、requested、waiting、cancelled、timed_out、action_required、unsupported、ambiguous は `passed` に昇格しない。
  - Workflow run / job 自体の `stale` conclusion は CI failure 系として扱うが、PR head SHA mismatch / snapshot 中の head change は CI failure ではなく stale head freshness failure として再実行へ誘導する。
  - Post-observation 追加修正として、CI passed / head matched かつ current trigger boundary に unresolved feedback や pending review signal がない一方で Codex review completion signal が観測できない状態を、generic `wait_timeout` ではなく `review_completion_unknown` 系の non-pass terminal-like state として表現する。
  - `review_completion_unknown` は merge-ready / pass ではなく、人間または orchestration layer の確認を要求する状態として扱う。
  - Post-review-inventory 追加修正として、current trigger boundary に selected されていなくても、GitHub review thread payload 上で `isResolved=false` かつ `isOutdated=false` と観測できる unresolved thread は latest head に残る actionable review work として扱い、`review_completion_unknown` / merge-prepared / issue finish の前に可視化する。
  - `selected_unresolved_count == 0` は current trigger boundary 上の selected blocker がないことだけを示し、actionable review work がないことの証明として扱わない。
  - Downstream contract として `ci.status`、`normalized_status`、`overall_status`、`recommended_next_action`、`limitations`、`ci.failures`、`decision` の実用上の意味を維持する。
  - Fake `gh` による script-level regression tests を追加 / 更新する。
- 禁止:
  - GitHub token permission model 自体を変更する。
  - Fine-grained PAT dashboard の UI を変更する。
  - PR merge の自動実行を追加する。
  - GitHub Actions workflow 定義そのものを再設計する。
  - Codex review lifecycle 観測を、current-boundary completion unknown の分類、その安全な wait termination、および latest head に残る non-outdated unresolved review thread の actionable inventory 化以外へ広げる。
  - Caller-provided endpoint、method、GraphQL query、headers、request body、`jq`、raw `gh` arguments を受け取る拡張を追加する。
  - 観測不能な CI surface を暗黙に成功扱いする。
- 対象外:
  - GitHub Actions 以外の全 check provider を完全同等に観測できるようにすること。
  - Branch protection / required checks policy の全面再現。
  - CI log download / log parsing の追加。
  - Codex review comment / review thread collector の全面再設計。
  - Generic issue comment、review request disappearance、selected comments zero、selected unresolved zero を completion / pass とみなすこと。
  - `github-pr-merge-preparer` の triage / repair grouping 仕様変更。

## 境界
- 常に行う:
  - `Actions` read で読める workflow runs / jobs から head SHA の CI 状態を判断する。
  - Workflow run / job の失敗系 conclusion は `ci.status="failed"` とし、可能な範囲で workflow / job / failed step を `ci.failures` に残す。
  - Workflow run / job の in-progress / queued / pending 系は `running` または `pending` とし、wait / resume 可能な状態にする。
  - Actions-only green を `passed` にする場合でも、full rollup / external provider coverage が未証明なら limitation を明示する。
  - Permission / auth / rate limit / schema / transient failure は token や stderr 本文を漏らさず、既存と同様に machine-readable limitation として返す。
  - `review_completion_unknown` は、CI/head が完了し、current-boundary review evidence が安定して変化しておらず、かつ actionable unresolved review inventory が空であることを wait wrapper が確認した後にだけ terminal-like に扱う。
- 判断が必要:
  - Commit statuses / PR status rollup を supplemental signal として残す場合、permission denied を blocking とするか、Actions primary の limitation とするか。
  - External provider の存在をどこまで検出できるか。検出できない場合は「未証明の範囲」として limitation に留める。
  - 既存 `ci.check_runs` / `ci.commit_statuses` shape を互換目的で残す場合の値の埋め方。
  - `review_completion_unknown` の top-level `normalized_status` を `human_gate` とするか `unknown` とするか。現時点の推奨は inspect-before-merge を明示する `human_gate`。
  - Strict allowlisted no-findings issue comment を distinct secondary signal として追加できるか。観測可能な actor/time/trigger evidence が不足する場合は deferred とする。
- 行わない:
  - `Checks` read permission denial を、Actions で判断可能な GitHub Actions-centered CI の通常 blocker として扱わない。
  - Actions-only green の limitation を下流 agent から見えない場所に隠さない。
  - `unknown` を `passed` と同義に扱わない。
  - `review_completion_unknown` を `passed`、`merge_prepared`、または selected feedback zero の別名にしない。

## 非交渉制約
- Final JSON の stdout machine-readable contract を壊さない。
- Progress / diagnostics は stderr に留め、stdout は JSON authority とする。
- Secrets、token values、raw auth stderr を出力しない。
- Fixed script surface を維持し、任意 GitHub API proxy にしない。
- Provider source を先に更新し、dogfooding mirror は検証対象として扱う。
- False pass を避けるため、unsupported / ambiguous / unobserved failure-risk state は explicit limitation または `unknown` にする。
- Review completion を証明できない状態は pass にせず、`review_completion_unknown` または pending / timeout として明示する。

## 前提
- この issue の対象 repo は GitHub Actions-centered CI を主対象にする。
- GitHub official REST docs 上、workflow runs / workflow jobs は fine-grained token の `Actions` repository permission read で利用可能である。
- Check runs / combined commit status / PR status rollup は supplemental or compatibility signal として扱えるが、Fine-grained PAT の通常 path で必須にしない。
- Downstream agent は final JSON の `ci.status` と `recommended_next_action` を主要判断材料として使う。

## 受け入れ条件
- AC-001:
  - アクター: PR observation を実行する agent。
  - 前提: Fine-grained PAT が `Actions` read を持ち、GitHub Actions workflow runs / jobs は読めるが check runs / full status rollup は読めない。
  - 操作: `fetch_pr_observation_snapshot.sh` または `wait_pr_observation.sh` を PR head SHA に対して実行する。
  - 期待結果: GitHub Actions workflow runs / jobs から CI 状態を判断し、`Checks` read を通常解決策として要求しない。
  - 観測点: final JSON の `ci.status`、`limitations`、`recommended_next_action`、fake `gh` test log。
- AC-002:
  - アクター: 後続の merge preparation / repair workflow。
  - 前提: PR head SHA の全 GitHub Actions workflow runs / jobs が terminal success / skipped / neutral 相当であり、失敗・実行中・pending はない。
  - 操作: PR observation final JSON を読む。
  - 期待結果: `ci.status="passed"` を返せる。Full check/status rollup または external provider coverage が未証明の場合は、成功判定とは別に limitation が明示される。
  - 観測点: `ci.status="passed"`、`limitations[].code`、`limitations[].severity`、`decision.recommended_next_action`。
- AC-003:
  - アクター: 後続の repair workflow。
  - 前提: PR head SHA の GitHub Actions workflow run / job / step に failure / error / cancelled / timed_out / action_required / startup_failure / stale conclusion 相当がある。
  - 操作: PR observation final JSON を読む。
  - 期待結果: `ci.status="failed"` になり、`recommended_next_action` は CI 修正へ進める値になる。可能な範囲で failed workflow / job / step の情報が `ci.failures` に入る。
  - 観測点: `ci.status`、`ci.failures`、`normalized_status`、`recommended_next_action`。
- AC-004:
  - アクター: 後続の wait / resume workflow。
  - 前提: PR head SHA の GitHub Actions workflow run / job が queued / requested / waiting / pending / in_progress 相当である。
  - 操作: PR observation final JSON を読む。
  - 期待結果: `ci.status` は `pending` または `running` になり、成功扱いせず、待機または resume が必要だと分かる。
  - 観測点: `ci.status`、`normalized_status`、`recommended_next_action`、wait result。
- AC-005:
  - アクター: PR observation を保守する開発者。
  - 前提: Permission denied / auth missing / rate limit / schema unavailable / transient failure が発生する。
  - 操作: fake `gh` regression tests または実 script を実行する。
  - 期待結果: final JSON に machine-readable limitation が入り、secret / token / raw stderr は漏れない。Actions で判断可能な通常 green path では `fix_github_token_permissions` を不要に要求しない。
  - 観測点: `limitations`、`stderr_sha256`、stdout/stderr secret absence assertions。
- AC-006:
  - アクター: PR observation を実行する agent。
  - 前提: PR head SHA は期待 head と一致し、CI は `passed`。current trigger boundary では Codex-authored submitted PR review、allowlisted no-findings signal、current unresolved thread、changes-requested evidence、pending review request / pending review signal、blocking collection failure のいずれも観測されない。さらに all-fetched review thread inventory 上でも `isResolved=false` かつ `isOutdated=false` の actionable carryover unresolved thread が観測されない。
  - 操作: `wait_pr_observation.sh` が同じ current-boundary no-completion evidence を quiet / same-fingerprint stability 条件まで観測する。
  - 期待結果: final JSON は generic `wait_timeout` ではなく `review_completion_unknown` 系の `decision.status_reason` と `recommended_next_action="human_gate"` を返す。`passed` / `merge_prepared` にはならない。
  - 観測点: `normalized_status`、`decision.status_reason`、`decision.completion_signal`、`wait.quiet_seconds_observed`、`wait.same_fingerprint_observed`、fake `gh` wait test。
- AC-007:
  - アクター: PR observation を実行する agent。
  - 前提: current-boundary に pending review request または current pending PR review signal がある。
  - 操作: `fetch_pr_observation_snapshot.sh` または `wait_pr_observation.sh` を実行する。
  - 期待結果: pending state は `review_completion_unknown` に昇格せず、待機 / resume の対象として扱われる。
  - 観測点: `codex_review.lifecycle.status`、`decision.status_reason`、`recommended_next_action`。
- AC-008:
  - アクター: 後続の repair / merge preparation workflow。
  - 前提: current trigger boundary の selected unresolved count は `0` だが、GitHub review thread payload 上で `isResolved=false` かつ `isOutdated=false` の carryover unresolved thread が観測される。
  - 操作: PR observation final JSON を読む。
  - 期待結果: carryover thread は actionable review inventory として可視化され、`summary.review="unresolved"` または同等の unresolved review state になり、`review_completion_unknown` / `merge_prepared` にはならない。
  - 観測点: `decision.actionable_unresolved_count`、`decision.carryover_unresolved_count`、`decision.carryover_unresolved_thread_ids`、`summary.review`、`recommended_next_action`。

## 例外・エッジケース
- EC-001:
  - 条件: Actions API は読めるが workflow runs が 0 件で、CI が存在しないのか未作成 / 遅延なのか判断できない。
  - 期待: `none` または `unknown` として扱い、既存の zero-check grace / deadline semantics と整合させる。成功扱いしない。
  - 観測点: `ci.status`、zero-check limitation、wait behavior。
- EC-002:
  - 条件: Actions workflow runs は成功だが external check provider の存在または required status rollup を証明できない。
  - 期待: ユーザー回答に基づき `ci.status="passed"` を許可する。ただし full rollup / external provider coverage が未証明である limitation を明示する。
  - 観測点: `ci.status="passed"`、coverage limitation。
- EC-003:
  - 条件: Actions workflow runs / jobs の head SHA が expected head SHA と一致しない、または snapshot collection 中に PR head が変わる。
  - 期待: stale head freshness failure として扱い、CI 修正ではなく current head で再実行するよう促す。成功扱いしない。
  - 観測点: `stale_head` limitation、`recommended_next_action="rerun_for_current_head"`。
- EC-004:
  - 条件: Actions API 自体が permission denied / auth missing / rate limited / schema unavailable / transient failure で読めない。
  - 期待: `unknown` と machine-readable limitation を返す。Actions で判断できない状態を成功扱いしない。
  - 観測点: `ci.status="unknown"`、`limitations[].capability="actions_read"`、secret absence。

## 入力→出力例（必要時）
- EX-001:
  - 入力: head SHA に紐づく GitHub Actions workflow runs がすべて `completed/success`。
  - 出力: `ci.status="passed"`。Full rollup が未証明なら coverage limitation を併記。
- EX-002:
  - 入力: head SHA に紐づく workflow job の step が `completed/failure`。
  - 出力: `ci.status="failed"`、`ci.failures[].kind="github_actions_job"`、failed step 情報。
- EX-003:
  - 入力: head SHA に紐づく workflow run が `in_progress`。
  - 出力: `ci.status="running"`、`recommended_next_action` は wait / wait_or_resume 系。

## 用語（ドメイン語彙）
- TERM-001:
  - `Actions read`: GitHub REST Actions workflow runs / jobs を読む fine-grained repository permission。
- TERM-002:
  - `Actions-only green`: GitHub Actions workflow runs / jobs からは全て成功系 terminal state と判断できるが、check runs / commit statuses / full status rollup / external provider coverage は完全証明されていない状態。
- TERM-003:
  - `Full rollup`: GitHub の check runs、commit statuses、PR status check rollup など、Actions 以外の provider を含み得る総合的な check/status 観測面。
- TERM-004:
  - `Coverage limitation`: CI status 自体とは別に、観測できた surface と観測できなかった surface を final JSON 上で machine-readable に示す limitation。

## 未確定事項
- Blocking question:
  - なし。
- Resolved question:
  - `discussions/20260615t154753z-02-interview-actions-only-pass-contract.md`
  - 質問: Actions-only green evidence で `ci.status="passed"` を許可するか。
  - 回答: 許可する。
  - 採用: Option A。Full rollup / external provider coverage が未証明の場合は limitation を明示し、曖昧・失敗・実行中・pending は成功扱いしない。
- Non-blocking design questions:
  - Existing `ci.check_runs` / `ci.commit_statuses` fields を互換目的でどの粒度まで残すか。
  - Commit statuses / PR rollup の permission denied を supplemental limitation とする場合の exact limitation code。
  - Actions workflow run と job のどちらを canonical failure detail とし、同一 run attempt の重複をどう deduplicate するか。
