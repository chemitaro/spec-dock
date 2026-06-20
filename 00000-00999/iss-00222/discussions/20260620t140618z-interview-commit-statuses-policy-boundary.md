---
種別: interview
ID: "20260620t140618z-interview"
タイトル: "Commit Statuses Policy Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-20"
親: ["iss-00222"]
関連: []
scope: "issue"
scope_id: "iss-00222"
created_at: "2026-06-20T14:06:18Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00158-agent-workflow-pdca-hardening/issues/iss-00222-forbid-checks-api-pr-observation/discussions/20260620t140307z-research-checks-api-forbidden-surface-research.md"
reflected_to: []
---

# 20260620t140618z-interview Commit Statuses Policy Boundary

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / discussions / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `scratch` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - PR observation CI source of truth の scope / non-scope / acceptance criteria。
  - `design.md`:
    - `pr_observation_checks.py` から commit statuses collection / pass fallback を残すか削るか。
  - `plan.md`:
    - red test の expected forbidden calls、zero Actions runs の closure、doctor probe update の範囲。
  - `ADR`:
    - 現時点では不要。Issue-local policy clarification として足りる見込み。
- chat 上の軽微な一問では足りない理由:
  - 回答により、CI 判定の許可 API surface、zero Actions runs の pass/fail semantics、既存テストの変更範囲が変わるため。

## 質問の目的 (必須)
- 対象者:
  - Product maintainer / Issue owner.
- 何を明確にする質問か:
  - GitHub PR observation が legacy commit statuses endpoint `GET /repos/{repo}/commits/{sha}/status` を引き続き読むことを許すか、Actions workflow runs/jobs だけに限定するか。
- 回答が後続判断へ与える影響:
  - 許す場合は commit statuses の permission / pass / failure tests を残す。禁止する場合は commit statuses fallback と capability probe を削除し、Actions-only non-success behavior に統一する。

## 質問 (必須)
- pressure-test question:
  - 「Checks API / status rollup を禁止する」だけでなく、「CI 状態は Actions workflow runs / jobs を正とする」という要件を、legacy commit statuses にも適用しますか？
- 質問:
  - PR observation の CI 判定で `GET /repos/{repo}/commits/{sha}/status` による legacy commit statuses read も廃止し、Actions workflow runs/jobs だけを許可する、という理解でよいですか？
- 回答してほしいこと:
  - Option A / B のどちらを採用するか。必要なら `mergeStateStatus` だけを別扱いにするかも補足してください。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue `#222` は `/check-runs`, `statusCheckRollup`, `gh pr checks` equivalent を明示的に禁止している。
  - GitHub issue `#222` は「CI 状態の取得は GitHub Actions の workflow runs / jobs を正とする」と書いている。
  - Current `pr_observation_checks.py` は `/check-runs`, `/status`, `statusCheckRollup`, Actions runs/jobs を全て読む。
  - Current tests include zero Actions runs passing via green check-runs or green commit statuses.
  - Current doctor capability core includes `check_runs_read`, `commit_statuses_read`, and `status_check_rollup_read`; `actions_read` is extended.
- local context で解決できたこと:
  - `/check-runs` と `statusCheckRollup` は禁止。
  - `ci_coverage_limited_to_github_actions` は正常系として不要。
  - Actions unavailable/inconclusive は forbidden fallback ではなく Actions observation limitation として表す必要がある。
- まだ人間判断が必要な理由:
  - GitHub issue body は commit statuses endpoint を名指しで禁止していないが、目的文は Actions-only と読める。ここを agent が勝手に決めると、既存 repo の legacy status behavior に影響する。

## 回答案 (必須)
- Option A:
  - Commit statuses も PR observation CI 判定から廃止する。Allowed CI source は Actions workflow runs/jobs のみ。Zero Actions runs は non-pass / unknown / none として扱う。
- Option B:
  - Commit statuses は Checks API ではないため、限定的な fallback として残す。ただし `/check-runs`, `statusCheckRollup`, `gh pr checks` は廃止する。
- Option C:
  - Commit statuses は今回の実装では判断保留にし、まず `/check-runs` と `statusCheckRollup` だけ削除する。後続 issue で Actions-only 完全化を扱う。

## Codex の分析 (必須)
- 判断軸:
  - Issue `#222` の目的への忠実度、GitHub token permission への依存削減、CI false-positive / false-negative risk、既存テスト変更量。
- tradeoff:
  - Option A は一番明快で permission surface が小さいが、Actions を使わない legacy status-only repo では PR observation が pass できなくなる。
  - Option B は後方互換性を残すが、「Actions workflow runs/jobs を正とする」という Issue 222 の意図が弱くなる。
  - Option C は差分を小さくするが、仕様変更 issue として未完了感が残る。
- リスク:
  - Commit statuses を残すと、future agent が「Checks 禁止だが external status fallback はある」と解釈し続け、今回の設計制約がぼやける。
  - Commit statuses を削ると、required check state や non-Actions CI の観測力が下がる。
- 具体シナリオ / edge case:
  - A repo has zero Actions workflow runs but a successful legacy commit status. Option A keeps non-pass; Option B can pass.
  - Actions read is unavailable but commit statuses are readable. Option A returns Actions observation unavailable; Option B may still infer CI.

## Codex の推奨案 (必須)
- 推奨:
  - Option A.
- 理由:
  - GitHub issue `#222` is framed as a specification change, not a narrower permission workaround. "Actions workflow runs / jobs を正とする" を強い設計制約として扱う方が、doctor / skill / tests / future operation の表現が単純で一貫する。
- 未回答時の影響:
  - `requirement.md` と `design.md` で CI source boundary を確定できず、commit statuses に関する acceptance criteria と red tests が分岐する。

## ユーザー回答 (回答後に必須)
- answer capture:
  - User answered "はい" to Option A: legacy commit statuses read is also removed from PR observation CI decisions, leaving Actions workflow runs/jobs as the only allowed CI source.
- 回答:
  - はい。PR observation の CI 判定では `GET /repos/{repo}/commits/{sha}/status` による legacy commit statuses read も廃止し、Actions workflow runs/jobs だけを許可する。
- 回答日時:
  - 2026-06-20

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - N/A

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - GitHub issue `#222` の Actions workflow runs/jobs を正とする方針を、legacy commit statuses にも適用するユーザー判断として採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Allowed CI source は GitHub Actions workflow runs/jobs のみ。Checks API、status rollup、`gh pr checks`、commit statuses は forbidden / non-source。
- `design.md`:
  - `pr_observation_checks.py` から `/check-runs`, `/status`, `statusCheckRollup` collection と external green fallback logic を削除する。
- `plan.md`:
  - Forbidden API call absence, Actions-only pass/pending/failed/unknown, zero Actions runs non-pass, doctor probe update, docs/skill update を closure に含める。
- `ADR`:
  - 現時点では不要。Issue-local accepted answer として扱う。
- reflected_to 更新方針:
  - Canonical `requirement.md` / `design.md` / `plan.md` 作成時に reflected_to を更新する。
- adoption reflection:
  - `report.md` Evidence Adoption Ledger の blocked entry を answered/adopted に更新する。

## 条件付き補足 (必要な場合だけ)
- PlantUML 図:
  ```plantuml
  @startuml
  ' TODO: 質問依存、意思決定フロー、before/after、責務境界が必要なら追加する
  @enduml
  ```
- 詳細 tradeoff:
  - ...
- 後続 reflection proposal:
  - ...
- 追加で作る discussion docs:
    - ...
