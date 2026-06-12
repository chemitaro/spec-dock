---
種別: interview
ID: "20260611t135608z-interview"
タイトル: "Github Capability Probe Profile"
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

# 20260611t135608z-interview Github Capability Probe Profile

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
    - capability check が固定最小 API セットなのか、workflow 別 profile なのかで MUST / OUT OF SCOPE が変わる。
  - `design.md`:
    - 共通 probe contract の入力、出力、判定語彙、`doctor` と PR observation の使い方が変わる。
  - `plan.md`:
    - test fixture、stubbed `gh` call、script integration の数と順序が変わる。
  - `ADR`:
    - 現時点では不要。probe profile policy を長期 architecture contract にする場合のみ候補。
- chat 上の軽微な一問では足りない理由:
  - probe 対象の粒度は実装範囲と安全境界に直結し、後続 docs へ採用証跡が必要になるため。

## 質問の目的 (必須)
- 対象者:
  - `spec-dock` maintainer。
- 何を明確にする質問か:
  - `doctor` と PR observation で同じ fixed probe を使うのか、必要 capability が異なる profile を持つのか。
- 回答が後続判断へ与える影響:
  - API call set、output schema、permission guidance、テスト matrix が決まる。

## 質問 (必須)
- pressure-test question:
  - `doctor` は広い GitHub workflow 前提を診断し、PR observation は PR checks に必要な capability だけを診断する、という profile 分離を許すか。
- 質問:
  - GitHub token capability probe は、固定の最小必須 API セット 1 種にしますか。それとも `doctor` 用と PR observation 用の profile を分けますか？
- 回答してほしいこと:
  - Option A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue `#180` は、`check-runs`、`statusCheckRollup`、`gh pr checks` の permission failure を具体例として挙げている。
  - 同 issue は capability 候補として Repository metadata read、Issues read/write、Pull requests read、Actions read、Checks read、Commit statuses read を挙げている。
  - `iss-00176` は `wait_pr_observation.sh` が fixed trigger write と read-only observation を行う contract を持つため、PR observation 側には issue comment write capability も関係する。
  - `iss-00170` は CI/check/status collection と review/comment/thread collection を扱うが、arbitrary endpoint / method / raw gh args は受け付けない境界を持つ。
- local context で解決できたこと:
  - `#180` の直接原因は PR checks / statuses 系 API の read 権限不足。
  - PR observation workflow は fixed set の GitHub calls を持つため、profile 化しても arbitrary API checker にする必要はない。
  - `doctor` は環境診断なので、PR observation に限らない Issues write などを確認したい要求があり得る。
- まだ人間判断が必要な理由:
  - fixed minimal set は実装が小さいが将来不足しやすく、profile 分離は正確だが scope と出力が複雑になる。

## 回答案 (必須)
- Option A:
  - Fixed minimal profile。`doctor` と PR observation の両方で、まず repo metadata、PR read、check-runs read、commit statuses read、statusCheckRollup read だけを確認する。Issue comment write などは docs guidance に留める。
- Option B:
  - Two profiles。`doctor` は broader workflow profile として repo metadata、issues read/write、pull requests read、actions/checks/statuses read を確認し、PR observation は PR observation profile として check-runs/statusCheckRollup/statuses と trigger comment write availability を確認する。
- Option C:
  - Fixed core + optional profile extensions。共通 core は metadata / PR read / check-runs / statuses / statusCheckRollup に固定し、`doctor` だけ optional extended checks として Issues write / trigger comment write / Actions read を明示的に表示する。PR observation は core + 必要時の trigger write failure を limitation 化する。

## Codex の分析 (必須)
- 判断軸:
  - `#180` の直接症状を過不足なく検出できるか。
  - `doctor` の発見性と PR observation の実害低減を両立できるか。
  - broad permission checker になりすぎないか。
- tradeoff:
  - Option A は小さいが、`@codex review` trigger 投稿権限不足や Issue close/comment 権限不足の診断が弱い。
  - Option B は正確だが、profile 定義と output matrix が大きくなる。
  - Option C は direct cause を core で固定しつつ、`doctor` の発見性を optional extension に逃がせる。
- リスク:
  - Issues write probe が実際に書き込む形になると危険なので、write capability は原則として read-only に近い検査か dry capability inference に留める必要がある。
  - GitHub API permission model は fine-grained PAT / classic PAT / GitHub App token で見え方が異なるため、permission 名を断定しすぎない。
- 具体シナリオ / edge case:
  - `statusCheckRollup` は読めないが check-runs は読める。
  - check-runs は読めないが PR metadata は読める。
  - PR observation の trigger comment POST だけ失敗する。
  - rate limit / transient failure は permission denied と分ける。

## Codex の推奨案 (必須)
- 推奨:
  - Option C。
- 理由:
  - `#180` の直接問題に効く core probe を固定しつつ、`doctor` の broader diagnosis も表現できる。PR observation 側は core failure と trigger write failure を limitation として返せば、arbitrary checker 化を避けられる。
- 未回答時の影響:
  - capability probe の API call set と output schema を要件に落とせず、設計が過剰または不足する。

## ユーザー回答 (回答後に必須)
- answer capture:
  - チャットで `オプションCを採用します。` と回答。
- 回答:
  - Option C を採用する。
  - 共通 core probe は metadata / PR read / check-runs / statuses / statusCheckRollup に固定する。
  - `doctor` だけ optional extended checks を表示し、PR observation は core failure と trigger write failure を limitation 化する。
- 回答日時:
  - 2026-06-11T13:58:00Z

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Capability probe failure を command failure にするか、warning / limitation として non-zero にしないか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - `#180` の直接症状は PR checks / statuses 系 API の read 権限不足であり、core probe に固定できる。
  - 一方で `doctor` は環境診断として broader capability を示したいので、optional extended checks を持てる形にする。
  - PR observation は observation workflow の安全境界を維持し、core probe failure と trigger write failure を limitation として返す。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - MUST に fixed core probe を定義する。
  - MUST に `doctor` の optional extended checks を、core とは分けて表示することを入れる。
  - MUST に PR observation が core failure / trigger write failure を machine-readable limitation として返すことを入れる。
  - MUST NOT に arbitrary GitHub API checker 化、raw token 出力、probe のための不要な write operation を入れる。
- `design.md`:
  - capability probe result は `core` と `extended` を分けた model にする。
  - core は metadata / PR read / check-runs / statuses / statusCheckRollup の固定 endpoint 群にする。
  - extended は `doctor` 表示用で、Issue comment write / Actions read などを optional capability として扱う。
  - PR observation は core failure を permission limitation として final JSON に入れ、trigger comment POST failure は trigger write limitation として別扱いする。
- `plan.md`:
  - core probe の unit / stub tests を先に作る。
  - `doctor` integration は core + extended 表示を検証する。
  - PR observation integration は core failure と trigger write failure の limitation 表示を検証する。
- `ADR`:
  - 現時点では不要。profile policy は issue-level decision として `report.md` に記録する。
- reflected_to 更新方針:
  - requirement / design / plan 作成時にこの interview を採用 evidence として参照し、`report.md` Evidence Adoption Ledger に採用済みとして記録する。
- adoption reflection:
  - `iss-00180` の capability check は broad checker ではなく、fixed core + doctor-only optional extended checks として扱う。

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
