---
種別: 要件定義書（Issue）
ID: "iss-00222"
タイトル: "Forbid Checks API In PR Observation"
関連GitHub: ["#222"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["epic-00158", "init-local-00003"]
---

# iss-00222 Forbid Checks API In PR Observation — 要件定義

## 目的

`github-pr-observation` の CI 観測から GitHub Checks API / PR status rollup / `gh pr checks` 相当 / legacy commit statuses を完全に排除し、GitHub Actions workflow runs/jobs を唯一の CI source of truth にする。

PR metadata、review、review comments、issue comments、review threads の監視機能は維持する。禁止対象は `checks` という語や互換名ではなく、GitHub Checks API / status rollup surface の利用である。

## 背景・現状

- GitHub issue `#222` は、PR observation が Checks API / `statusCheckRollup` / `gh pr checks` 相当を使わないことを求めている。
- ユーザー回答により、legacy commit statuses (`GET /repos/{owner}/{repo}/commits/{sha}/status`) も Actions-only 制約に含めることが確定した。
- 追加のユーザー回答により、`checks` という名称や既存互換名を消す必要はない。禁止対象は GitHub Checks API / status rollup API 利用である。
- 現行実装は provider-side `github-pr-observation` asset で、Actions runs/jobs に加えて次を supplemental source として使っている。
  - `gh pr view --json mergeStateStatus,statusCheckRollup`
  - `GET /repos/{repo}/commits/{sha}/check-runs`
  - `GET /repos/{repo}/commits/{sha}/status`
  - Actions runs が 0 件でも check-runs / commit statuses が green なら pass 可能な fallback
- GitHub REST API docs 上、workflow runs/jobs は `Actions` read permission、check-runs は `Checks` read permission、commit statuses は `Commit statuses` read permission であり、別 permission surface である。
- Review/comment 監視は Checks API と別経路で、PR reviews / review comments / issue comments / GraphQL `reviewThreads` を使っている。

## 情報源

- GitHub issue `#222`
- `discussions/20260620t140307z-research-checks-api-forbidden-surface-research.md`
- `discussions/20260620t140618z-interview-commit-statuses-policy-boundary.md`
- `discussions/20260620t141316z-research-actions-only-pr-observation-viability-research.md`
- `discussions/20260620t141319z-disc-feasibility-without-checks-api.md`
- `discussions/20260620t141320z-disc-actions-only-collector-design.md`
- `discussions/20260620t141317z-disc-observation-semantics-and-losses.md`
- `discussions/20260620t141318z-disc-doctor-tests-docs-migration.md`
- `discussions/20260620t143349z-adr-forbid-checks-api-in-pr-observation.md`
- `discussions/20260620t144016z-interview-checks-named-compatibility-boundary.md`
- Provider-side implementation under `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/`
- Runtime doctor capability probe under `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`
- Focused regression tests under `tests/unit/infra/test_init_update.py` and `tests/cli_runtime/test_runtime_doctor_s04.py`
- GitHub Docs:
  - REST API endpoints for workflow runs
  - REST API endpoints for workflow jobs
  - REST API endpoints for check runs
  - REST API endpoints for commit statuses
  - REST API endpoints for pull request reviews / review comments / issue comments

## 対象ユーザー / 利用シナリオ

- 主な利用者:
  - PR 作成後に `github-pr-observation` / `github-pr-merge-preparer` で CI と review 状態を監視する Codex workflow。
  - GitHub token に `Checks` / `Commit statuses` permission を与えず、Actions と PR review/comment の read 権限だけで PR observation を運用したい利用者。
- 代表シナリオ:
  - PR の head SHA に紐づく GitHub Actions workflow runs/jobs を観測し、CI passed / failed / pending / running / unknown を判断する。
  - PR review、review comments、issue comments、unresolved review threads を継続して観測し、review blocker / human gate を判断する。
  - Actions が判断不能な場合は Checks/statuses に fallback せず、Actions observation unavailable / unknown / human gate として報告する。

## スコープ

### 必須

- PR observation の CI 判定 source を GitHub Actions workflow runs/jobs のみにする。
- 次の forbidden surface を PR observation CI 判定・fallback・limitation 判定から排除する。
  - `GET /repos/{owner}/{repo}/commits/{ref}/check-runs`
  - `GET /repos/{owner}/{repo}/commits/{sha}/status`
  - `statusCheckRollup`
  - `gh pr checks` 相当
  - `ci_coverage_limited_to_github_actions` のように、Checks/statuses/status rollup を読まないことを limitation として扱う出力
- GitHub Actions runs/jobs が取得可能な場合は、その run/job state だけで CI 状態を判断する。
- Actions runs/jobs が取得不能、0 件、または判断不能な場合は pass にせず、unknown / none / human gate へ倒す。
- Review/comment/thread 監視は維持する。
- Doctor / capability probe は Checks/statuses/status rollup 権限不足を PR observation の修復対象にしない。
- Tests は forbidden API call が発生したら失敗するようにする。
- Docs / skill guidance は Actions-only CI observation と intentional loss を明記する。

### 禁止

- GitHub Checks API を fallback として使うこと。
- Commit statuses を fallback として使うこと。
- `statusCheckRollup` / `gh pr checks` 相当で required checks / merge blocking checks を推論すること。
- Actions が 0 件のときに green check-runs / green commit status を根拠に pass とすること。
- `checks` という単語だけを理由に script 名、JSON field、historical docs、compatibility docs を削除すること。
- Review/comment/thread 監視を Checks API 排除に巻き込んで弱めること。

### 対象外

- GitHub UI の all checks / branch protection / external CI provider checks を完全再現すること。
- Actions 以外の CI provider を PR observation の CI source of truth にすること。
- Historical discussion / report evidence に残る過去の `check-runs` / `statusCheckRollup` 記述を書き換えること。
- GitHub review comment 投稿機能そのものの仕様変更。ただし existing review/comment observation が壊れないことは受け入れ条件に含める。

## 境界

- 常に行う:
  - CI 判定は Actions workflow runs/jobs のみを見る。
  - PR metadata / review / comments / review threads は従来通り別経路で見る。
  - Forbidden endpoint / field / CLI surface は fake `gh` と static inspection で回帰検出する。
- 判断が必要:
  - 既存 JSON compatibility fields を空/deprecated metadata として残すか、最小限に整理するかは design で決める。ただし残す場合も CI 判定に使わない。
  - `fetch_pr_checks_snapshot.sh` など historical compatibility name は残してよいが、docs/usage で Actions-only であることを明記する。
- 行わない:
  - Checks/statuses/status rollup を読めないことを warning や limitation にする。
  - `checks` 語の全面禁止。
  - Review/comment observation を GraphQL `statusCheckRollup` 禁止と混同すること。

## 非交渉制約

- Provider-side source of truth は `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/` と `src/spec_dock/assets/spec_dock/...` に置く。
- Dogfooding mirror under `.agents/` / `spec-dock/` は必要に応じて検証対象にするが、実装 source of truth ではない。
- PR observation は read-only を基本とする。Codex review trigger の既存 allowed write (`POST repos/{owner}/{repo}/issues/{pr}/comments`) はこの issue の主対象外。
- Review/comment read capability は維持する。GitHub token には `Actions: read` と PR review/comment observation に必要な `Pull requests: read` / issue comments read 相当が必要である。

## 受け入れ条件

- AC-001: Forbidden Checks API surface を呼ばない
  - アクター: PR observation scripts
  - 前提: fake `gh` が `/check-runs`, `/status`, `statusCheckRollup`, `gh pr checks` 相当を呼ぶと失敗する。
  - 操作: PR observation snapshot / wait の CI collection を実行する。
  - 期待結果: forbidden surface は一度も呼ばれず、CI 判定は Actions runs/jobs のみから構成される。
  - 観測点: fake `gh` call log、unit tests、static scan。

- AC-002: Actions green は pass として観測できる
  - アクター: PR observation scripts
  - 前提: current head SHA に紐づく Actions workflow runs/jobs が success terminal state である。
  - 操作: PR observation snapshot / wait を実行する。
  - 期待結果: CI は passed / merge-preparation eligible として扱われ、Checks/statuses limitation は出ない。
  - 観測点: JSON payload、wait result、tests。

- AC-003: Actions failure / pending / running は Actions のみで判定される
  - アクター: PR observation scripts
  - 前提: Actions workflow run/job に failure、pending、queued、in_progress、cancelled、timed_out などが含まれる。
  - 操作: PR observation snapshot / wait を実行する。
  - 期待結果: 状態に応じて failed / pending / running / unknown へ分類され、check-runs/statuses fallback は発生しない。
  - 観測点: JSON payload、progress/fingerprint、tests。

- AC-004: zero Actions runs は pass しない
  - アクター: PR observation scripts
  - 前提: current head SHA に Actions workflow runs が 0 件で、legacy check-runs/statuses は green 相当の fixture を持つ。
  - 操作: PR observation snapshot / wait を実行する。
  - 期待結果: CI は passed にならず、none / unknown / human gate として扱われる。
  - 観測点: JSON payload、wait decision、tests。

- AC-005: Review/comment/thread 監視を維持する
  - アクター: PR observation scripts
  - 前提: PR に issue comments、PR reviews、review comments、unresolved review threads がある。
  - 操作: PR observation snapshot / wait を実行する。
  - 期待結果: review/comment/thread evidence は従来通り収集され、Checks API 排除によって欠落しない。
  - 観測点: `review` payload、limitations、tests。

- AC-006: Doctor は不要な Checks/status permissions を要求しない
  - アクター: `spec-dock doctor` / capability diagnostics
  - 前提: token には Actions read と PR/comment read はあるが Checks / Commit statuses permission はない。
  - 操作: PR observation capability diagnostics を実行する。
  - 期待結果: Checks/statuses/status rollup permission failure は repair target にならず、Actions read と review/comment read が診断対象になる。
  - 観測点: doctor output、tests。

- AC-007: Docs / skill guidance は API 禁止と語彙禁止を混同しない
  - アクター: user / future implementer
  - 前提: shipped skill/docs に `checks` という互換名が残る場合がある。
  - 操作: guidance を読む。
  - 期待結果: 禁止対象が GitHub Checks API / status rollup surface であり、`checks` という単語の全面禁止ではないことが分かる。
  - 観測点: docs diff、static scan scope、spec review。

## 例外・エッジケース

- EC-001: Actions API unavailable
  - 条件: Actions workflow runs/jobs endpoint が permission denied / auth missing / rate limited / transient failure / schema unavailable。
  - 期待: Checks/statuses に fallback せず、Actions observation unavailable / unknown / human gate とする。
  - 観測点: limitations、recommended next action、tests。

- EC-002: Jobs API unavailable but run-level conclusion is failed
  - 条件: workflow run は failed conclusion を持つが jobs API が読めない。
  - 期待: CI failed は維持し、job detail unavailable を limitation / diagnostic として出す。check-runs fallback はしない。
  - 観測点: JSON payload、tests。

- EC-003: External required check が failed / pending
  - 条件: GitHub UI では external required check が failed / pending だが Actions は green。
  - 期待: SpecDock は external required check を観測しない。これは intentional loss であり、GitHub UI mergeability の完全再現を主張しない。
  - 観測点: docs wording、merge-preparer wording。

- EC-004: Status-only repository
  - 条件: GitHub Actions を使わず commit statuses だけで CI を表現する repository。
  - 期待: PR observation は CI passed と判定しない。Actions-only scope として unknown / none / human gate へ倒す。
  - 観測点: tests、docs。

- EC-005: Historical compatibility names
  - 条件: `fetch_pr_checks_snapshot.sh` など `checks` named public surface が残る。
  - 期待: その名前は compatibility name として許容される。ただし GitHub Checks API を呼ばず、Actions-only behavior を明記する。
  - 観測点: docs、static scan、tests。

## 用語

- GitHub Checks API:
  - `GET /repos/{owner}/{repo}/commits/{ref}/check-runs` など、GitHub Checks permission surface に属する API。
- status rollup:
  - `statusCheckRollup` や `gh pr checks` 相当の PR checks aggregation surface。
- legacy commit statuses:
  - `GET /repos/{owner}/{repo}/commits/{sha}/status` で得られる commit status API。
- Actions-only CI observation:
  - GitHub Actions workflow runs/jobs を唯一の CI source of truth とする PR observation。
- Review/comment evidence:
  - issue comments、PR reviews、PR review comments、reviewThreads、reviewDecision など、CI rollup とは別の review observation surface。

## 未確定事項

- なし。
