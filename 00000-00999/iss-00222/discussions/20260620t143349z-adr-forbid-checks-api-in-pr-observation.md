---
種別: ADR（Architecture Decision Record）
ID: "20260620t143349z-adr"
タイトル: "Forbid Checks API In PR Observation"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
authority: "accepted"
derived_from:
  - "GitHub issue #222"
  - "discussions/20260620t140307z-research-checks-api-forbidden-surface-research.md"
  - "discussions/20260620t140618z-interview-commit-statuses-policy-boundary.md"
  - "discussions/20260620t141316z-research-actions-only-pr-observation-viability-research.md"
  - "discussions/20260620t141319z-disc-feasibility-without-checks-api.md"
  - "discussions/20260620t141320z-disc-actions-only-collector-design.md"
  - "discussions/20260620t141317z-disc-observation-semantics-and-losses.md"
  - "discussions/20260620t141318z-disc-doctor-tests-docs-migration.md"
  - "user decision 2026-06-20: remove Checks API/statusCheckRollup/gh pr checks and legacy commit statuses from PR observation CI decisions"
reflected_to:
  - "iss-00222 report.md"
  - "iss-00222 requirement.md"
  - "iss-00222 design.md"
  - "iss-00222 plan.md"
---

# 20260620t143349z-adr Forbid Checks API In PR Observation

## 位置づけ

この ADR は、`github-pr-observation` が PR の CI 状態を観測するときに、GitHub Checks API、PR status rollup、`gh pr checks` 相当、legacy commit statuses を使わないという長期的な architecture / contract decision を固定する。

`iss-00222` の `requirement.md`、`design.md`、`plan.md` は、この ADR を source decision として反映する。

## ADR 化基準

- hard to reverse:
  - yes
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `requirement.md` / `design.md` / `plan.md`
- ADR として残す理由:
  - この判断は単なる API 呼び出しの削除ではなく、PR observation の CI source of truth と観測範囲を変える。
  - GitHub UI の all checks / required checks / external checks の再現を意図的に捨てる tradeoff がある。
  - 後続の実装者が `statusCheckRollup`、`/check-runs`、`/status`、`gh pr checks` を便利な fallback として戻しやすいため、禁止境界を ADR として固定する必要がある。

## 結論（Decision）

Accepted.

PR observation の CI 判定は GitHub Actions workflow runs/jobs のみを source of truth とする。

次の API / CLI / GraphQL surface は、PR observation の CI 判定・fallback・limitation 判定に使わない。

- `GET /repos/{owner}/{repo}/commits/{ref}/check-runs`
- `GET /repos/{owner}/{repo}/commits/{sha}/status`
- GraphQL / `gh pr view --json statusCheckRollup` などの `statusCheckRollup`
- `gh pr checks` 相当の checks rollup surface
- Checks/statuses/status rollup が読めないことを表す `ci_coverage_limited_to_github_actions` のような limitation

代替として、CI 判定には Actions workflow runs/jobs を使う。

- `GET /repos/{owner}/{repo}/actions/runs?head_sha=<head_sha>`
- `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`

PR metadata、head freshness、draft/open state、review/review thread/comment evidence は引き続き PR observation の対象に含めてよい。ただし、review evidence 用の GraphQL と、CI rollup 用の `statusCheckRollup` は別物として扱う。CI rollup 用 GraphQL は forbidden surface とする。

## 背景（Context）

`github-pr-observation` は PR 作成後または push 後に、CI、review、comments、unresolved threads、head SHA 変化を観測して、merge-ready / human gate / repair needed を判断するための read-only workflow surface である。

Issue #222 では、Checks API / `statusCheckRollup` / `gh pr checks` 相当を完全に禁止し、CI source of truth を GitHub Actions workflow runs/jobs に置くことが求められた。

調査時点の既存実装は、Actions runs/jobs に加えて `statusCheckRollup`、check-runs、commit statuses を supplemental source として読んでいた。また、Actions runs が 0 件でも external check-runs や commit statuses が green なら pass 可能な fallback を持っていた。

ユーザー回答により、legacy commit statuses も Actions-only 制約に含める方針が確定した。したがって、Checks API だけでなく Commit statuses permission surface も PR observation CI 判定から外す。

## 選択肢（Options considered）

- 選択肢 A（採用）: Actions-only PR observation
  - 概要:
    - CI 判定を Actions workflow runs/jobs に限定する。
    - forbidden surface は呼ばず、fallback にも使わない。
  - 良い点（Pros）:
    - Issue #222 とユーザー決定に一致する。
    - `Checks` / `Commit statuses` permission を PR observation の前提から外せる。
    - forbidden call を fake `gh` / static scan で検出しやすい。
    - Actions run/job の失敗詳細は維持できる。
  - 悪い点 / 制約（Cons）:
    - external/non-Actions checks は観測できない。
    - GitHub UI の required checks / mergeability と一致しない場合がある。
    - zero Actions runs は、CI なし、Actions 遅延、Actions 以外の CI を区別できない。
  - 採用理由:
    - forbidden surface 排除を最優先しつつ、Actions-centered monitoring として PR observation の価値を維持できるため。

- 選択肢 B（棄却）: Checks API だけ排除し、legacy commit statuses を fallback に残す
  - 概要:
    - `/check-runs` と `statusCheckRollup` は使わないが、`/commits/{sha}/status` は supplemental signal として残す。
  - 良い点（Pros）:
    - status-only CI の一部を観測できる。
    - zero Actions runs + green commit status を pass できる。
  - 悪い点 / 制約（Cons）:
    - ユーザー回答に反する。
    - Actions-only contract が曖昧になる。
    - `Commit statuses` permission surface を残す。
  - 棄却理由:
    - PR observation の CI source of truth を Actions runs/jobs に固定する判断と衝突するため。

- 選択肢 C（棄却）: PR status rollup / branch protection / mergeability を supplemental CI signal として使う
  - 概要:
    - `mergeStateStatus`、status rollup、branch protection 由来の情報を使い、GitHub UI の mergeability に近い判定を目指す。
  - 良い点（Pros）:
    - GitHub UI と近い結果を出せる可能性がある。
  - 悪い点 / 制約（Cons）:
    - `statusCheckRollup` 相当を再導入しやすい。
    - forbidden surface の境界が曖昧になる。
    - Actions-only contract が弱くなる。
  - 棄却理由:
    - Issue #222 の主目的である Checks/status rollup 排除を損なうため。

## 判断理由（Rationale）

GitHub Actions workflow runs/jobs は、Checks API と別の API / permission surface として提供されている。Actions runs は PR head SHA で絞り込め、jobs API により failed job / step detail も得られる。

一方で、check-runs、commit statuses、`statusCheckRollup` は、GitHub UI の all checks / branch protection / external CI を再現するには便利だが、今回の forbidden surface そのものである。これらを fallback として残すと、権限不足時や zero Actions runs 時に旧仕様へ戻る。

そのため、PR observation の意味論を次のように反転する。

- Checks/statuses/status rollup が読めないことは limitation ではなく正常系。
- CI 判定は Actions runs/jobs の観測範囲に限定する。
- Actions が判断できない場合は Checks/statuses に fallback せず、unknown / human gate に倒す。
- external/non-Actions checks の観測喪失は bug ではなく intentional loss として requirement/design に明記する。

この判断により、PR observation は GitHub UI の完全な mergeability simulator ではなく、Actions-centered PR observation になる。

## 影響（Consequences）

Positive:

- PR observation から `Checks` / `Commit statuses` permissions を外せる。
- forbidden API surface が明確になり、テストで回帰検出しやすくなる。
- Actions workflow runs/jobs を中心に、CI 判定の source of truth が単純になる。
- `ci_coverage_limited_to_github_actions` のような旧 limitation を廃止できる。
- PR metadata、head freshness、review evidence、wait/resume stability は維持できる。

Negative / debt:

- external/non-Actions checks の結果は観測できなくなる。
- status-only CI repository は PR observation 上 pass しなくなる。
- GitHub UI では required check が pending/failing でも、SpecDock は Actions-only の範囲でしか判断できない。
- zero Actions runs は pass にできず、unknown / none / human gate として扱う必要がある。
- 既存 tests、doctor capability probe、skill docs、merge-preparer wording の更新範囲が広い。

Impact scope:

- `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/`
  - skill wording
  - `pr_observation_checks.py`
  - snapshot / wait scripts
  - progress / fingerprint semantics
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_capability_cli.py`
  - PR observation required capabilities
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - Checks/statuses/status rollup permission diagnostics removal
- tests:
  - forbidden API call regression tests
  - Actions green / failed / pending / zero-runs tests
  - jobs unavailable without check-runs fallback
  - doctor capability tests
  - docs/skill static scan
- docs / skill guidance:
  - “supplemental Checks/statuses/rollup” wording removal
  - “Actions-only CI observation; external/non-Actions checks intentionally not observed” wording addition

Migration / rollback:

- Migration は one-way contract update として扱う。
- Rollback する場合は、ユーザー決定と Issue #222 の forbidden surface を再検討する新 ADR が必要。
- 実装上の互換性として、旧 JSON fields を空/deprecated metadata として残すかは `design.md` で決める。ただし、残す場合も CI 判定に使ってはならない。

Follow-ups:

- `requirement.md` に forbidden / allowed surface、non-scope、edge cases を反映する。
- `design.md` に Actions-only collector、doctor capability、loss model、JSON compatibility を反映する。
- `plan.md` に forbidden-call red tests と migration verification を反映する。

## 参考（References）

- 関連仕様（requirement/design/plan/report）:
  - `iss-00222 requirement.md`
  - `iss-00222 design.md`
  - `iss-00222 plan.md`
  - `iss-00222 report.md`
- 元になった discussion docs（derived_from）:
  - `discussions/20260620t140307z-research-checks-api-forbidden-surface-research.md`
  - `discussions/20260620t140618z-interview-commit-statuses-policy-boundary.md`
  - `discussions/20260620t141316z-research-actions-only-pr-observation-viability-research.md`
  - `discussions/20260620t141319z-disc-feasibility-without-checks-api.md`
  - `discussions/20260620t141320z-disc-actions-only-collector-design.md`
  - `discussions/20260620t141317z-disc-observation-semantics-and-losses.md`
  - `discussions/20260620t141318z-disc-doctor-tests-docs-migration.md`
- 外部資料:
  - GitHub Docs: REST API endpoints for workflow runs: https://docs.github.com/rest/actions/workflow-runs
  - GitHub Docs: REST API endpoints for workflow jobs: https://docs.github.com/rest/actions/workflow-jobs
  - GitHub Docs: REST API endpoints for check runs: https://docs.github.com/rest/checks/runs
  - GitHub Docs: REST API endpoints for commit statuses: https://docs.github.com/rest/commits/statuses
