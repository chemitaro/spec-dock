---
種別: disc
ID: "20260620t141317z-disc"
タイトル: "Observation Semantics And Losses"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
関連: []
authority: "proposed"
derived_from:
  - "20260620t141316z-research-actions-only-pr-observation-viability-research.md"
  - "Deep Consultant feasibility/risk analyses 2026-06-20"
reflected_to:
  - "report.md Evidence Adoption Ledger"
---

# 20260620t141317z-disc Observation Semantics And Losses

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
  - Checks/statuses/status rollup を排除した後の PR observation の意味論と、意図的に失う観測能力。
- この synthesis が必要な理由:
  - 「監視機能を維持できる」という表現が、GitHub UI の all checks 再現まで含むと誤解されると、受け入れ条件と実装が衝突する。

## derived question sheets / research (必須)
- `interview`:
  - `20260620t140618z-interview-commit-statuses-policy-boundary.md`
- `research`:
  - `20260620t141316z-research-actions-only-pr-observation-viability-research.md`
- その他の根拠:
  - Deep Consultant feasibility and risks analyses。

## synthesis (必須)
- 合意済みのこと:
  - Maintained: PR metadata、head freshness、draft/open state、Actions workflow runs/jobs、run/job failure details、review/comment/thread evidence、wait/resume stability。
  - Lost: check-runs、commit statuses、statusCheckRollup required-check state、`gh pr checks` 相当、external provider checks、zero Actions + green fallback。
  - CI pass は Actions の観測結果だけで決める。
- 未合意 / 未確定のこと:
  - external/non-Actions checks の存在をユーザー向けにどの wording で表示するか。
- source-grounded に解決できたこと:
  - Actions API unavailable は fallback せず unknown / human gate とする。
  - zero Actions runs は pass しない。
  - non-Actions required checks の状態を SpecDock が検出できないことは intentional limitation であり、permission error ではない。

## 選択肢 / tradeoff (必須)
- Option A: loss を明示した Actions-only semantics（推奨）
  - Pros:
    - ユーザー・実装者・reviewer の期待値が一致する。
    - forbidden surface 回帰を防ぎやすい。
    - status-only / external CI の扱いが明確になる。
  - Cons:
    - PR observation の「完全性」は下がる。
    - GitHub UI と観測結果が異なる理由を docs で説明する必要がある。
- Option B: loss を表示せず、Actions-only を通常 CI observation として扱う
  - Pros:
    - UI/JSON wording は簡潔になる。
  - Cons:
    - external/non-Actions checks が見えないことを利用者が誤解する。
    - merge-preparer や reviewer が「すべての check が green」と誤って主張するリスクがある。
- Option C: zero Actions runs を neutral/pass に近く扱う
  - Pros:
    - CI を持たない repo では進行しやすい。
  - Cons:
    - Actions 以外の CI や遅延実行を誤って pass する。
    - Issue #222 の「Actions が判断できない場合は unavailable」を求める趣旨に反する。

## reflection proposal (必須)
- canonical docs / workflow / template / skill guidance へ反映すべき候補:
  - `merge-prepared` / PR ready の wording は「observed Actions CI failure がない」程度に限定し、「all required checks passed」と言わない。
  - external/non-Actions checks は out of scope として、観測不能でも fallback しない。
  - `ci_coverage_limited_to_github_actions` は削除し、必要なら `ci.source_policy=github_actions_only` のような neutral marker を置く。
  - zero Actions runs は `none` / `unknown` / human gate へ倒す。
- まだ proposal に留める理由:
  - 表示文言と JSON field は design/implementation で具体化する。

## adoption target / 採用先候補 (必須)
- `requirement.md`:
  - Scope / Non-scope / Edge cases。
- `design.md`:
  - Observation semantics / loss table / downstream wording。
- `plan.md`:
  - tests for zero Actions, external green ignored, wording assertions。
- `ADR`:
  - 不要。
- `report.md` Evidence Adoption Ledger:
  - EAL-DEEP-003。

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
  - `requirement.md` / `design.md` / `plan.md`

## 推奨案 (必須)
- Option A を採用する。PR observation は Actions-centered monitoring として維持し、external/non-Actions checks を観測しないことを明記する。zero Actions runs と Actions API unavailable は pass ではなく unknown/human gate に倒す。

## 推奨反映先 (必須)
- `requirement.md`:
  - Accepted behavior と out-of-scope。
- `design.md`:
  - Loss model、status mapping、wording policy。
- `plan.md`:
  - zero-runs / status-only repo / merge-preparer wording regression tests。
- `ADR`:
  - なし。
- `report.md` Evidence Adoption Ledger:
  - EAL-DEEP-003。

## 未採用 / deferred 理由 (必須)
- 未採用:
  - Option B: 監視結果の過大表現につながる。
  - Option C: Actions-only の判断不能時に pass してしまう。
- deferred:
  - 表示文言の最終 wording は docs/skill update 時に固定する。

## 次アクション (必須)
- `requirement.md` / `design.md` / `plan.md` / `adr` へ反映する内容:
  - Observability retained/lost table。
  - zero Actions / Actions unavailable edge cases。
  - downstream wording constraints。
- 追加で作る discussion docs:
  - なし。
