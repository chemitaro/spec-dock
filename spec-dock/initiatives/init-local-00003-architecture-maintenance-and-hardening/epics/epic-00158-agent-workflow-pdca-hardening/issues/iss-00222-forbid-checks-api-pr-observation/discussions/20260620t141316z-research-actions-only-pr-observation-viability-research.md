---
種別: research
ID: "20260620t141316z-research"
タイトル: "Actions Only PR Observation Viability Research"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
関連: []
authority: "synthesized"
derived_from:
  - "GitHub issue #222"
  - "user answer 2026-06-20: legacy commit statuses also forbidden"
  - "Deep Consultant parallel analysis 2026-06-20"
  - "GitHub REST API docs: Actions workflow runs/jobs, Checks check-runs, Commit statuses"
reflected_to:
  - "report.md Evidence Adoption Ledger"
---

# 20260620t141316z-research Actions Only PR Observation Viability Research

## 位置づけ
- 用途: 外部仕様、実装事実、先例、制約、用語衝突、edge case など、検証可能な根拠を整理する。
- authority default: `synthesized`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は source-grounded research evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 調査結果が選択肢比較を必要とする場合は `disc`、長期判断を支える場合は `adr`、人間判断を必要とする場合は `interview` へつなぐ。
- 事実、推測、未検証事項、用語衝突、edge case、判断への含意を混ぜない。
- local context で解ける疑問は人間に聞かず、この artifact に source-grounding を残す。

## 調査目的 (必須)
- Checks API / `statusCheckRollup` / `gh pr checks` 相当を PR observation から完全排除しても、PR 監視機能を維持できるかを明らかにする。
- Checks API を使わない場合の代替 CI source、実装変更範囲、観測不能になる情報、テスト・doctor・docs への影響を整理する。
- ユーザー回答により、legacy commit statuses (`GET /repos/{owner}/{repo}/commits/{sha}/status`) も Actions-only 制約に含める前提を採用する。

## sources / 調査方法 (必須)
- 参照先:
  - GitHub issue `#222`: Checks API / `statusCheckRollup` / `gh pr checks` 相当を forbidden surface とし、CI source of truth を GitHub Actions workflow runs/jobs に置く要求。
  - `discussions/20260620t140307z-research-checks-api-forbidden-surface-research.md`: 既存実装とテストの forbidden surface 調査。
  - `discussions/20260620t140618z-interview-commit-statuses-policy-boundary.md`: legacy commit statuses も廃止するユーザー回答。
  - Deep Consultant 3視点:
    - feasibility / retained-lost capability
    - Actions-only collector design
    - risks / tests / doctor / migration
  - GitHub REST API docs:
    - Workflow runs: `GET /repos/{owner}/{repo}/actions/runs`, `head_sha` filter, `Actions` read permission.
    - Workflow jobs: `GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs`, `Actions` read permission.
    - Check runs: `GET /repos/{owner}/{repo}/commits/{ref}/check-runs`, `Checks` read permission.
    - Commit statuses: combined status endpoint, `Commit statuses` read permission.
- 検証手順:
  - provider-side PR observation skill/scripts を検索し、現在の `statusCheckRollup`, `/check-runs`, `/status`, `ci_coverage_limited_to_github_actions` の利用箇所を確認した。
  - doctor capability probe と runtime doctor tests を検索し、`check_runs_read`, `commit_statuses_read`, `status_check_rollup_read`, `actions_read` の扱いを確認した。
  - Deep Consultant を並列に使い、機能維持可否、設計方式、リスク/テスト観点を独立に分析した。
- 実験条件:
  - 実装変更は未着手。ここでは source-grounded clarification と design preparation のみを扱う。

## facts / 観測できた事実 (必須)
- GitHub Actions workflow runs/jobs は `Actions` repository permission read で読める別 API surface であり、Checks API / Commit statuses とは permission surface が分離している。
- GitHub check runs endpoint は `Checks` repository permission read を要求する。Issue #222 の forbidden surface と一致する。
- GitHub combined commit status endpoint は `Commit statuses` repository permission read を要求する。ユーザー回答により、この surface も PR observation の CI 判定から排除する。
- 現行 provider-side PR observation は、Actions runs/jobs に加えて `gh pr view --json mergeStateStatus,statusCheckRollup`、`/check-runs`、`/status` を読んでいる。
- 現行設計は、Actions runs が 0 件でも external check-runs または commit statuses が green なら pass 可能な fallback を持つ。
- 現行設計は、Checks / statuses / status rollup の読取不可を `ci_coverage_limited_to_github_actions` limitation として扱う。
- `fetch_pr_observation_snapshot.sh` / `wait_pr_observation.sh` の public entrypoint は、内部 CI collector を Actions-only にしても維持できる見込みが高い。
- `reviewThreads` 等の review evidence 用 GraphQL は、CI rollup の `statusCheckRollup` とは別論点であり、今回の forbidden CI surface と切り分けて扱える。

## inference / 推測 (必須)
- 事実から推測したこと:
  - PR observation 機能は維持可能。ただし「GitHub UI の required checks / external checks を完全再現する機能」ではなく、「Actions-centered PR observation」として仕様を再定義する必要がある。
  - CI 判定の source of truth は `GET /repos/{owner}/{repo}/actions/runs?head_sha=<sha>` と各 run の jobs API に限定できる。
  - zero Actions runs は「CI なし」「Actions 以外の CI」「Actions 作成遅延」を区別できないため、pass ではなく `none` / `unknown` / human gate に倒す必要がある。
  - check-runs/statuses/status rollup を読まないことは limitation ではなく正常系になるため、`ci_coverage_limited_to_github_actions` は廃止対象になる。
  - `mergeStateStatus` は branch protection や required checks の推論を再導入しやすいため、残すとしても CI 判定に使わない制約が必要。
- 推測の根拠:
  - GitHub docs 上、Actions runs/jobs は forbidden surface と異なる permission/API で提供されている。
  - Issue #222 が Actions workflow runs/jobs を代替 source of truth と指定している。
  - Deep Consultant 3視点が一致して、機能維持は可能だが external/non-Actions checks の観測喪失を requirement に明記すべきと結論した。

## unverified / 未検証事項 (必須)
- まだ確認していないこと:
  - 実装後に fake `gh` / unit tests / runtime tests が、forbidden API 呼び出しを完全に検出できるか。
  - downstream consumers が既存 JSON fields (`ci.check_runs`, `ci.commit_statuses`, `ci.required_check_state` など) をどの程度参照しているか。
  - `fetch_pr_checks_snapshot.sh` という既存ファイル名を残す場合、利用者混乱を docs/usage で十分に抑えられるか。
- 確認できない理由:
  - 本フェーズは clarification / design preparation であり、実装・テスト更新はまだ行っていない。
  - downstream usage は repo 内検索で追加確認可能だが、canonical requirement/design を固定してから実施する方が安全。

## question candidates / 質問候補 (必須)
- source-grounded に解けず、人間判断が必要な候補:
  - なし。legacy commit statuses も廃止するかはユーザー回答で確定済み。
- pressure-test question として切り出すべき候補:
  - なし。現時点では追加 interview なしで requirement/design/plan へ進める。
- 質問せずに解決できた候補:
  - Actions-only で監視機能を維持できるか: 可能。ただし external/non-Actions checks の観測は意図的に失う。
  - 代替 API は何か: Actions workflow runs/jobs。
  - 問題は発生しないか: external required checks / status-only CI / zero Actions runs などの観測不能シナリオが発生するため、pass に倒さない設計と docs 明記が必要。

## terminology conflicts / 用語衝突 (必須)
- 衝突している用語:
  - `checks`: GitHub Checks API の check-runs と、一般的な CI checks の総称が混在している。
  - `status`: commit statuses と workflow run status/conclusion が混在している。
  - `required checks`: branch protection required checks と、SpecDock が観測した Actions CI の pass/fail が混在している。
- 既存 docs / code / tests / discussions での使われ方:
  - `github-pr-observation` skill は、Checks / commit statuses / PR status rollup を supplemental source と呼んでいる。
  - `pr_observation_checks.py` は Actions runs/jobs と check-runs/statuses/status rollup を同じ CI collector 内で扱っている。
  - historical discussions は `gh pr checks` や `statusCheckRollup` を過去の検討証跡として含む。
- 判断が必要な理由:
  - 実装後に `checks` という名前の public script / JSON field が残る場合でも、内部意味論は Actions-only CI collector へ変わる。docs と tests で旧 API surface への回帰を防ぐ必要がある。

## edge cases / 具体シナリオ (必須)
- edge case:
  - Actions workflow runs が green だが external required check が failed / pending。
- その edge case が requirement / design / plan に与える影響:
  - SpecDock は external required check を観測しない。これは bug ではなく intentional loss。merge 可否の完全再現を受け入れ条件に含めてはならない。
- edge case:
  - Actions workflow runs が 0 件だが legacy commit status は green。
- その edge case が requirement / design / plan に与える影響:
  - pass してはならない。ユーザー回答により commit statuses は fallback に使わない。
- edge case:
  - Actions run が failed だが jobs API が読めない。
- その edge case が requirement / design / plan に与える影響:
  - run-level conclusion で failed は維持し、job detail unavailable を診断情報として出す。check-runs fallback は禁止。
- edge case:
  - Actions API 自体が権限不足 / unavailable。
- その edge case が requirement / design / plan に与える影響:
  - `actions_read` limitation / unknown / human gate とする。Checks/statuses fallback は禁止。

## implications / 判断への含意 (必須)
- `requirement.md` は forbidden surface を明示する必要がある: `/check-runs`, `/commits/{sha}/status`, GraphQL/CLI `statusCheckRollup`, `gh pr checks`, Checks/statuses/rollup unavailable limitation。
- `requirement.md` は allowed CI surface を Actions workflow runs/jobs のみに固定する必要がある。
- `design.md` は `pr_observation_checks.py` を Actions-only collector へ縮小し、旧 supplemental sources と required-check inference を削除する方針を持つ必要がある。
- `design.md` は backward compatibility のために旧 JSON field を空または deprecated metadata として残すか、削除するかの判断を明記する必要がある。
- `plan.md` は fake `gh` に forbidden call が来たら失敗する red tests を必須化する必要がある。
- doctor / capability probe は core capability を `actions_read` 中心へ変更し、Checks/statuses/status rollup 権限不足を修復対象にしない必要がある。
- historical evidence は書き換えず、現在の skill/docs/canonical issue docs で新方針を明確化する。

## リスク/制約 (任意)
- External/non-Actions CI の状態は観測できなくなる。
- GitHub UI の mergeability / branch protection required checks と SpecDock の Actions-only observation は一致しない場合がある。
- status-only repo は PR observation 上 pass しなくなる。
- JSON shape を急に削除すると downstream script が壊れる可能性があるため、互換 field を残す設計が必要になる可能性がある。
- `fetch_pr_checks_snapshot.sh` などの historical naming は混乱を生むため、usage/docs の修正または alias 追加を検討する。

## 反映先 (任意)
- reflected_to:
  - `discussions/20260620t141319z-disc-feasibility-without-checks-api.md`
  - `discussions/20260620t141320z-disc-actions-only-collector-design.md`
  - `discussions/20260620t141317z-disc-observation-semantics-and-losses.md`
  - `discussions/20260620t141318z-disc-doctor-tests-docs-migration.md`
  - `report.md` Evidence Adoption Ledger

## 参考（References） (任意)
- GitHub Docs: REST API endpoints for workflow runs: https://docs.github.com/rest/actions/workflow-runs
- GitHub Docs: REST API endpoints for workflow jobs: https://docs.github.com/rest/actions/workflow-jobs
- GitHub Docs: REST API endpoints for check runs: https://docs.github.com/rest/checks/runs
- GitHub Docs: REST API endpoints for commit statuses: https://docs.github.com/rest/commits/statuses
