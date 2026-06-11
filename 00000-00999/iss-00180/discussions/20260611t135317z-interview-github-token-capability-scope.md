---
種別: interview
ID: "20260611t135317z-interview"
タイトル: "Github Token Capability Scope"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-06-11"
親: ["iss-00180"]
関連: []
scope: "<initiative | epic | issue | local-topic>"
scope_id: "iss-00180"
created_at: "2026-06-11THH:MM:SSZ"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from: []
reflected_to: ["requirement.md", "design.md", "plan.md", "report.md"]
---

# 20260611t135317z-interview Github Token Capability Scope

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
    - `iss-00180` の必須 scope を `doctor` 中心にするか、PR observation workflow の preflight / limitation 表示まで含めるかが変わる。
  - `design.md`:
    - runtime `doctor` command の診断として設計するか、`.agents/skills/github-pr-observation` scripts の実行前 capability probe として設計するかが変わる。
  - `plan.md`:
    - 実装順序、テスト対象、provider-side source と dogfooding mirror の parity 対象が変わる。
  - `ADR`:
    - 現時点では不要。`doctor` と workflow preflight の責務境界を長期 contract として固定する場合のみ ADR 候補になる。
- chat 上の軽微な一問では足りない理由:
  - 回答によって issue の実装 surface と受け入れ条件が変わり、後続の requirement / design / plan に採用証跡が必要になるため。

## 質問の目的 (必須)
- 対象者:
  - `spec-dock` maintainer。
- 何を明確にする質問か:
  - GitHub token capability check をどの実行面の product contract として定義するか。
- 回答が後続判断へ与える影響:
  - `doctor` の環境診断を先に作るのか、PR observation / merge-preparer の `unknown` 低減を先に作るのか、または両方を 1 issue に含めるのかが決まる。

## 質問 (必須)
- pressure-test question:
  - この issue の成功条件は「手動で `spec-dock doctor` を実行したときに token 権限不足を診断できること」か、「PR observation / merge-preparer の通常 workflow が `unknown` の前に permission 問題を示すこと」か。
- 質問:
  - `iss-00180` では、GitHub token capability check の必須 scope をどこまで含めたいですか？
- 回答してほしいこと:
  - 下の Option A / B / C のどれを採用するか。必要なら「A を先に、この issue では B は docs だけ」などの組み合わせで回答してよい。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue `#180`: `GH_TOKEN` 優先の fine-grained PAT で `check-runs`、`statusCheckRollup`、`gh pr checks` が `Resource not accessible by personal access token` になり、`GH_TOKEN` を外すと取得できた。
  - `spec-dock/active/issue/requirement.md`: 現在は scaffold のままで、要件は未具体化。
  - 親 epic `epic-00067`: `.agents` / `.codex` / `.github` の installed layout と agent-tooling assets の hardening が中心。
  - `iss-00170`: `github-pr-observation` の deterministic PR observation、CI / review collection、`unknown` / limitation / stdout JSON 境界を定義済み。
  - `iss-00176`: `wait_pr_observation.sh` が `@codex review` trigger と PR observation を担い、GitHub auth / permission / rate limit / schema failure を non-success / limitation として JSON 表現する前提を持つ。
  - `iss-00178`: observation result は evidence であり、triage / repair 判断は `github-pr-merge-preparer` 側に置く境界を定義している。
  - runtime `doctor`: 既に構造・metadata・active pointer などの診断 command として存在する。
- local context で解決できたこと:
  - GitHub API の失敗対象と症状は `#180` 本文で十分具体化されている。
  - PR observation 側には既に `unknown` / limitation を final JSON に含める設計文脈がある。
  - `doctor` 側には環境診断の入口があるが、GitHub token capability probe は現時点の主要 contract としてはまだ固定されていない。
- まだ人間判断が必要な理由:
  - `doctor` に入れると手動診断として扱いやすい一方、実際に困った workflow は PR observation / merge-preparer の実行中であり、どちらを issue の「必須成功条件」にするかは product intent の判断になる。

## 回答案 (必須)
- Option A:
  - `doctor` first。`spec-dock doctor` に GitHub token capability check を追加し、`GH_TOKEN` 優先状態、必要 API の read probe、permission 不足の説明、fine-grained PAT permission 目安を出す。
- Option B:
  - PR workflow first。`github-pr-observation` / `github-pr-merge-preparer` の通常 path で、`check-runs` / `statusCheckRollup` / `gh pr checks` などの permission failure を `unknown` ではなく token permission limitation として final JSON / progress / guidance に出す。
- Option C:
  - 両方。ただし 1 issue 内で、共通 capability probe を小さく設計し、`doctor` は手動診断、PR observation は runtime limitation 表示として同じ判定語彙を使う。

## Codex の分析 (必須)
- 判断軸:
  - 利用者がどの時点で原因に気づけるべきか。
  - GitHub write/read 境界を広げずに read-only probe として保てるか。
  - provider-side `.agents` scripts と runtime `doctor` の両方にまたがる場合、diff と test scope が過大にならないか。
- tradeoff:
  - Option A は実装と説明が比較的閉じるが、PR observation 実行中の `unknown` 体験は直接は改善しない。
  - Option B は実害の出た workflow に効くが、手動 diagnosis と permission 目安の発見性は弱い。
  - Option C は product 体験として最も一貫するが、runtime command と installed agent-tooling script の両方に触れるため、issue scope が広がる。
- リスク:
  - capability probe が broad な GitHub API checker になると、固定 endpoint / no arbitrary API の既存安全境界を弱める。
  - `GH_TOKEN` / hosts.yml token の詳細を出しすぎると secret 漏洩リスクがある。表示は token source と capability 結果に留める必要がある。
  - permission 不足と一時的 GitHub failure / rate limit / repo setting を誤分類すると、利用者の判断を誤らせる。
- 具体シナリオ / edge case:
  - `GH_TOKEN` が設定されているが fine-grained PAT に Checks / Actions read が不足している。
  - `GH_TOKEN` を外すと `gh auth` の保存済み token では同じ API が読める。
  - Issue / PR read はできるが commit check-runs / statusCheckRollup だけ読めない。
  - 権限不足時も raw token や hosts.yml の秘密値は出さない。

## Codex の推奨案 (必須)
- 推奨:
  - Option C。ただし実装は共通 probe を小さくし、まず `doctor` と PR observation の permission limitation 表示に限定する。
- 理由:
  - `#180` の問題は「手動で診断したい」と「実行中に unknown へ落ちる前に原因を出したい」の両方を含んでいるため。片方だけだと、発見性または実害低減のどちらかが残る。
- 未回答時の影響:
  - 要件を `doctor` only に狭めるか PR workflow まで含めるかを決められず、requirement / design / plan の scope が曖昧なままになる。

## ユーザー回答 (回答後に必須)
- answer capture:
  - チャットで `option Cを採用します。` と回答。
- 回答:
  - Option C を採用する。`iss-00180` は `doctor` と PR observation workflow の両方を scope に含める。
  - 共通 capability probe を小さく設計し、`doctor` は手動診断、PR observation は runtime limitation 表示として同じ判定語彙を使う。
- 回答日時:
  - 2026-06-11T13:55:00Z

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Capability probe の最小必須 API セットを issue 内で固定するか、`doctor` と PR observation で probe profile を分けるか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - GitHub issue `#180` は手動診断と PR observation 実行中の `unknown` 低減の両方を問題としているため、Option C が issue intent と最も一致する。
  - ただし安全境界を保つため、実装は read-only capability probe と permission limitation 表示に限定する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - MUST に `spec-dock doctor` と PR observation workflow の両方で GitHub token capability 不足を診断 / 表示できることを入れる。
  - MUST に共通判定語彙、`GH_TOKEN` 優先状態の表示、read-only fixed probe、secret 非表示を入れる。
  - MUST NOT に arbitrary GitHub API checker 化、raw token / hosts.yml secret 出力、GitHub write operation を入れる。
- `design.md`:
  - 共通 capability probe を小さな contract として設計し、`doctor` と `github-pr-observation` が同じ結果語彙を参照する。
  - `doctor` は手動診断 surface、PR observation は final JSON / limitation / guidance surface として扱う。
  - probe failure は permission denied / auth missing / rate limited / transient unknown を分け、permission denied を `Resource not accessible by personal access token` と対応づける。
- `plan.md`:
  - 先に capability probe contract と unit tests を作り、次に `doctor` integration、最後に PR observation limitation 表示へ広げる。
  - provider-side source、dogfooding mirror、runtime tests / script stub tests の対象を明記する。
- `ADR`:
  - 現時点では不要。scope 採用は issue-level decision として `report.md` に記録する。
- reflected_to 更新方針:
  - requirement / design / plan 作成時にこの interview を採用 evidence として参照し、`report.md` Evidence Adoption Ledger に採用済みとして記録する。
- adoption reflection:
  - `iss-00180` の headline は `doctor` だけの環境診断ではなく、GitHub token capability を shared diagnostic contract として扱う issue にする。

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
