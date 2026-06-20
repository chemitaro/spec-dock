---
種別: disc
ID: "20260620t141319z-disc"
タイトル: "Feasibility Without Checks API"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
関連: []
authority: "proposed"
derived_from:
  - "20260620t141316z-research-actions-only-pr-observation-viability-research.md"
  - "Deep Consultant feasibility analysis 2026-06-20"
reflected_to:
  - "report.md Evidence Adoption Ledger"
---

# 20260620t141319z-disc Feasibility Without Checks API

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
  - Checks API / `statusCheckRollup` / `gh pr checks` / commit statuses を完全に使わずに、PR observation の価値を維持できるか。
- この synthesis が必要な理由:
  - Issue #222 は単なる権限エラー回避ではなく、PR observation の CI source contract を反転させる要求である。実装前に「維持する機能」と「意図的に捨てる機能」を分ける必要がある。

## derived question sheets / research (必須)
- `interview`:
  - `20260620t140618z-interview-commit-statuses-policy-boundary.md`: legacy commit statuses も廃止する回答を採用済み。
- `research`:
  - `20260620t140307z-research-checks-api-forbidden-surface-research.md`
  - `20260620t141316z-research-actions-only-pr-observation-viability-research.md`
- その他の根拠:
  - Deep Consultant feasibility analysis。
  - GitHub REST API docs: Actions workflow runs/jobs は `Actions` read、check-runs は `Checks` read、commit statuses は `Commit statuses` read。

## synthesis (必須)
- 合意済みのこと:
  - CI 判定は GitHub Actions workflow runs/jobs のみに限定する。
  - Checks API、`statusCheckRollup`、`gh pr checks` 相当、legacy commit statuses は PR observation CI 判定で使わない。
  - Checks/statuses/rollup を読まないことを limitation として扱わない。
- 未合意 / 未確定のこと:
  - 旧 JSON fields を削除するか、compatibility metadata として空で残すかは design で決める。
  - `fetch_pr_checks_snapshot.sh` のファイル名を変更するか、historical name として残して usage を更新するかは design で決める。
- source-grounded に解決できたこと:
  - PR observation は維持可能。ただし GitHub UI の branch protection required checks / external provider checks を再現する機能ではなくなる。
  - 監視できる対象は、PR metadata、Actions runs/jobs、review/comment/thread evidence、wait/resume stability に限定される。

## 選択肢 / tradeoff (必須)
- Option A: Actions-only PR observation として維持する（推奨）
  - Pros:
    - Issue #222 とユーザー回答に一致する。
    - `Checks` / `Commit statuses` permissions を不要にできる。
    - forbidden API surface の静的・動的テストを明確に書ける。
    - Actions run/job failure detail は維持できる。
  - Cons:
    - external/non-Actions checks は観測できない。
    - GitHub UI の mergeability / required checks と一致しない場合がある。
    - status-only repo は pass しなくなる。
- Option B: Checks API だけ排除し、commit statuses は fallback に残す
  - Pros:
    - status-only CI の一部観測を残せる。
  - Cons:
    - ユーザー回答に反する。
    - `Commit statuses` permission surface を残すため、「Actions-only」契約が弱くなる。
    - zero Actions + green status の pass fallback が復活し、Issue #222 の意図と衝突する。
- Option C: GitHub branch protection / mergeability API を CI 判定に使う
  - Pros:
    - GitHub UI の mergeability に近づけられる可能性がある。
  - Cons:
    - `statusCheckRollup` 相当の再導入リスクが高い。
    - どの API が CI rollup に当たるかの境界が曖昧になり、forbidden surface を守りにくい。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - PR observation は Actions-centered であり、GitHub UI の全 checks 再現ではないと明記する。
  - forbidden surface を列挙する。
  - external/non-Actions checks の観測喪失を intentional loss として書く。
  - zero Actions runs は pass 不可とする。
- まだ proposal に留める理由:
  - requirement/design/plan へ反映する前に、観点別 discussion と report EAL で採用根拠を固定するため。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Scope / Non-scope / Acceptance Criteria / Edge Cases。
- `design.md`:
  - Source-of-truth contract、forbidden call policy、loss model。
- `plan.md`:
  - Forbidden-call red tests、zero-Actions behavior tests、doctor tests。
- `ADR`:
  - 現時点では不要。Issue-local で完結可能だが、将来も繰り返し効く場合は ADR 化候補。
- `report.md` Evidence Adoption Ledger:
  - Deep Consultant feasibility evidence の採用記録。

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
  - `requirement.md` / `design.md` / `plan.md` / `report.md`

## 推奨案 (必須)
- Option A を採用する。PR observation の価値は Actions CI、PR metadata、review evidence、wait/resume stability として維持できる。一方で GitHub UI の all checks / branch protection 再現は意図的に捨てる。この tradeoff を requirement に明示し、pass 判定を external/non-Actions signal に依存させない。

## 推奨反映先 (必須)
- `requirement.md`:
  - 「PR observation is Actions-only for CI」「external/non-Actions checks are out of scope」「zero Actions runs cannot pass」。
- `design.md`:
  - CI collector source contract、forbidden API guard、observability/loss model。
- `plan.md`:
  - fake `gh` に forbidden call を検出させる tests。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - EAL-DEEP-001。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Option B: ユーザー回答と Actions-only 方針に反する。
  - Option C: forbidden surface 再導入リスクが高い。
- deferred:
  - JSON compatibility field の最終形は design へ defer。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - Actions-only CI observation の採用。
  - forbidden surface の明文化。
  - lost capability と edge cases の明文化。
- 追加で作る discussion docs:
  - `disc-actions-only-collector-design`
  - `disc-observation-semantics-and-losses`
  - `disc-doctor-tests-docs-migration`
