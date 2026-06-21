---
種別: disc
ID: "20260620t141320z-disc"
タイトル: "Actions Only Collector Design"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
関連: []
authority: "proposed"
derived_from:
  - "20260620t141316z-research-actions-only-pr-observation-viability-research.md"
  - "Deep Consultant collector design analysis 2026-06-20"
reflected_to:
  - "report.md Evidence Adoption Ledger"
---

# 20260620t141320z-disc Actions Only Collector Design

## 位置づけ
- 用途: 集まった質問回答や調査をもとに、意思決定前の synthesis、選択肢、tradeoff、reflection proposal、ADR candidate triage、推奨反映先を整理する。
- authority default: `proposed`。通常は doc type から推定し、例外時だけ front matter の `authority` で override する。
- この artifact は synthesis / reflection proposal / adoption target / ADR triage の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 人間から回答を引き出し、回答欄や未回答事項を管理する場合は `interview` を使う。
- 生ログや未整理の思考は `scratch`、事実確認や外部根拠は `research`、長期判断の固定は `adr` に分ける。
- この doc は proposal / synthesis であり、issue `report.md` の observed evidence ledger ではない。採否の最終証跡は canonical docs / ADR / `report.md` Evidence Adoption Ledger に昇格する。
- doc が大きくなりすぎたら、質問回答は `interview`、事実調査は `research`、raw capture は `scratch`、長期決定は `adr` へ分割する。

## 対象論点 (必須)
- 今回整理する論点:
  - PR observation の CI collector を Actions workflow runs/jobs のみで構成する具体方式。
- この synthesis が必要な理由:
  - 既存 `pr_observation_checks.py` は Actions、check-runs、commit statuses、status rollup を混在させているため、禁止 API を削除するだけでは判定意味論と JSON contract が曖昧になる。

## derived question sheets / research (必須)
- `interview`:
  - `20260620t140618z-interview-commit-statuses-policy-boundary.md`
- `research`:
  - `20260620t141316z-research-actions-only-pr-observation-viability-research.md`
- その他の根拠:
  - Deep Consultant collector design analysis。
  - provider-side current files:
    - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_observation_checks.py`
    - `pr_observation_snapshot.py`
    - `pr_observation_wait.py`
    - `fetch_pr_checks_snapshot.sh`
    - `wait_pr_observation.sh`

## synthesis (必須)
- 合意済みのこと:
  - CI source は Actions workflow runs/jobs だけにする。
  - run-level status/conclusion を primary CI status とし、jobs は診断 detail として扱う。
  - check-runs / commit statuses / status rollup / `gh pr checks` fallback は削除する。
  - `ci_coverage_limited_to_github_actions` は出さない。
- 未合意 / 未確定のこと:
  - 旧 JSON fields を削除するか、compatibility marker として残すか。
  - `fetch_pr_checks_snapshot.sh` を rename するか、historical entrypoint として残すか。
- source-grounded に解決できたこと:
  - Actions workflow runs can be filtered by PR head sha (`head_sha`) and jobs can be listed by run id with `Actions` read permission.
  - Jobs API が失敗しても、run-level conclusion が failed なら CI failed の観測は維持できる。

## 選択肢 / tradeoff (必須)
- Option A: 既存 collector を Actions-only に縮小し、public entrypoint は維持する（推奨）
  - Pros:
    - 既存 `fetch_pr_observation_snapshot.sh` / `wait_pr_observation.sh` 利用者への破壊を最小化できる。
    - forbidden API を collector 内で一箇所から削除できる。
    - wait/resume / review evidence の上位構造を大きく変えずに済む。
  - Cons:
    - `fetch_pr_checks_snapshot.sh` など historical naming が残ると混乱を招く。
    - 旧 JSON fields を残す場合、使ってよい signal と使ってはいけない signal の説明が必要。
- Option B: collector / script を全面 rename する
  - Pros:
    - `checks` という語の混乱を減らせる。
  - Cons:
    - 呼び出し元、tests、skill docs、外部運用手順への破壊が広がる。
    - Issue #222 の主目的は forbidden API 排除であり、rename は副作用が大きい。
- Option C: GitHub GraphQL / PR mergeability を supplemental CI signal として残す
  - Pros:
    - GitHub UI に近い判断材料が得られる可能性がある。
  - Cons:
    - `statusCheckRollup` 相当の forbidden surface を再導入しやすい。
    - Actions-only 方針を崩す。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `pr_observation_checks.py` は Actions-only CI collector として再定義する。
  - JSON payload に `ci.source_policy = "github_actions_only"` のような明示 marker を置く。
  - 旧 fields を残す場合は `collection_policy: "forbidden"` / empty / deprecated とし、判定に使わない。
  - wait progress / fingerprint は Actions runs/jobs と limitations のみに基づける。
  - `--zero-check-grace-polls` は backward-compatible alias とし、可能なら `--zero-actions-grace-polls` を追加する。
- まだ proposal に留める理由:
  - JSON compatibility の最終決定は implementation design と tests の読取結果に依存する。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Allowed / forbidden API surfaces、compatibility expectation。
- `design.md`:
  - Collector structure、payload contract、wait behavior、entrypoint compatibility。
- `plan.md`:
  - S01 collector red/green tests、S02 wait/snapshot compatibility tests。
- `ADR`:
  - 不要。
- `report.md` Evidence Adoption Ledger:
  - Deep Consultant design evidence の採用記録。

## ADR triage / ADR candidate triage (必須)
- ADR candidate か:
  - no
- hard to reverse:
  - no
- surprising without context:
  - yes
- real tradeoff:
  - yes
- ADR 化しない場合の反映先:
  - `design.md` / `plan.md`

## 推奨案 (必須)
- Option A を採用する。public entrypoint は維持し、内部 collector と docs/usage を Actions-only CI collector として再定義する。run-level conclusion を CI 判定の primary source、jobs を failure detail とし、forbidden surface fallback は全て削除する。

## 推奨反映先 (必須)
- `requirement.md`:
  - CI source は Actions runs/jobs のみ。
- `design.md`:
  - `pr_observation_checks.py` の責務縮小、旧 fields の扱い、wait/fingerprint 更新。
- `plan.md`:
  - fake-gh forbidden-call tests、Actions green/failure/zero-runs/jobs-unavailable tests。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - EAL-DEEP-002。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Option B: rename の blast radius が主目的に比べて大きい。
  - Option C: forbidden surface 再導入リスクが高い。
- deferred:
  - 旧 JSON fields の完全削除可否は downstream usage 調査後に design で固定する。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - Actions-only collector architecture。
  - forbidden call guard。
  - public entrypoint compatibility。
  - `ci_coverage_limited_to_github_actions` retirement。
- 追加で作る discussion docs:
  - なし。
