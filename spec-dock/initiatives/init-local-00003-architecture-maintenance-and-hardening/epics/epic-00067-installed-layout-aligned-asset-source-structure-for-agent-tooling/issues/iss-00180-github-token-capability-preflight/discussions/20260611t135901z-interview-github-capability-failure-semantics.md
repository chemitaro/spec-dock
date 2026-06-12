---
種別: interview
ID: "20260611t135901z-interview"
タイトル: "Github Capability Failure Semantics"
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

# 20260611t135901z-interview Github Capability Failure Semantics

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
    - capability probe failure を fatal にするか warning / limitation にするかで受け入れ条件が変わる。
  - `design.md`:
    - `doctor` の exit code、PR observation final JSON の normalized status / recommended action / limitation の扱いが変わる。
  - `plan.md`:
    - CLI tests と script tests の expected return code / JSON status が変わる。
  - `ADR`:
    - 現時点では不要。
- chat 上の軽微な一問では足りない理由:
  - failure semantics は automation の制御フローと人間への報告に直接影響するため。

## 質問の目的 (必須)
- 対象者:
  - `spec-dock` maintainer。
- 何を明確にする質問か:
  - GitHub token capability failure をコマンド失敗として扱うか、diagnostic / limitation として扱うか。
- 回答が後続判断へ与える影響:
  - `doctor` / PR observation の終了コード、JSON status、human gate への遷移、テスト期待値が決まる。

## 質問 (必須)
- pressure-test question:
  - 権限不足が見つかったときに、`doctor` や PR observation は即 non-zero / failed にするべきか、それとも「環境診断は成功したが finding / limitation がある」として返すべきか。
- 質問:
  - Capability probe failure の扱いはどれにしますか？
- 回答してほしいこと:
  - Option A / B / C のどれを採用するか。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / discussions / primary source:
  - GitHub issue `#180` は、現在の `unknown` が原因切り分けを難しくしていることを問題にしている。
  - `iss-00170` / `iss-00176` は `unknown`、`limitation`、`human_gate`、non-success を final JSON で表現する文脈を持つ。
  - 既存 `doctor` は findings がある場合に診断結果として stderr へ出す command surface を持つ。
- local context で解決できたこと:
  - 権限不足そのものはコードや spec tree の破損ではなく、GitHub workflow を正しく観測できない環境状態である。
  - PR observation においては required capability が欠けると merge-prepared evidence としては成功扱いできない。
- まだ人間判断が必要な理由:
  - `doctor` は診断 command なので finding があるだけで non-zero にすべきか曖昧であり、PR observation は automation gate なので permission limitation を success 扱いしない必要がある。

## 回答案 (必須)
- Option A:
  - Fatal everywhere。core capability が欠けたら `doctor` も PR observation も non-zero / failed とする。
- Option B:
  - Diagnostic non-fatal。`doctor` は finding を返して exit 0、PR observation も limitation を返すが command 自体は exit 0 とし、final JSON の status / recommended action で human gate にする。
- Option C:
  - Surface-specific semantics。`doctor` は diagnosis command として exit 0 + findings を返す。PR observation は stdout final JSON を返すため process は原則 exit 0 を維持するが、normalized status は `unknown` / `human_gate` / `permission_denied` 相当にし、merge-prepared evidence には使えない non-success とする。Malformed input / script misuse / JSON construction failure は non-zero。

## Codex の分析 (必須)
- 判断軸:
  - コマンド実行そのものの成功と、観測対象 workflow の成功を分離できるか。
  - automation が permission limitation を merge-prepared と誤認しないか。
  - 人間が原因を直すための情報を確実に受け取れるか。
- tradeoff:
  - Option A は単純だが、diagnostic command と observation command の出力を受け取れずに失敗扱いで止まる可能性がある。
  - Option B は扱いやすいが、PR observation で limitation を成功扱いする誤用リスクが残る。
  - Option C は exit code と semantic status を分離でき、既存の final JSON authority 境界と合う。
- リスク:
  - process exit 0 を維持する場合、caller が final JSON を読まないと成功誤認する。skill guidance / tests で normalized status を必ず見る契約を強める必要がある。
  - `permission_denied` のような新 status を導入するか、既存 `unknown` + limitation に留めるかは design で決める必要がある。
- 具体シナリオ / edge case:
  - `doctor` で check-runs read が失敗しても、diagnostic report 自体は生成できている。
  - PR observation で check-runs read が失敗した場合、CI status を passed として返してはいけない。
  - `gh` が存在しない / repo slug が解決できない / JSON が壊れる場合は capability limitation ではなく command/runtime error として扱う可能性がある。

## Codex の推奨案 (必須)
- 推奨:
  - Option C。
- 理由:
  - `doctor` は診断結果を返すこと自体が価値なので exit 0 + findings が自然。一方で PR observation は merge-prepared evidence には使えない non-success を JSON で明示する必要がある。process failure と semantic failure を分けると、エージェントが原因を読んで次の行動を選びやすい。
- 未回答時の影響:
  - command return code、final JSON status、human gate / recommended action の要件が曖昧になり、実装とテストがぶれる。

## ユーザー回答 (回答後に必須)
- answer capture:
  - チャットで `オプションCを採用します。` と回答。
- 回答:
  - Option C を採用する。
  - `doctor` は diagnosis command として exit 0 + findings を返す。
  - PR observation は stdout final JSON を返すため process は原則 exit 0 を維持するが、normalized status は `unknown` / `human_gate` / `permission_denied` 相当の non-success とし、merge-prepared evidence には使えない。
  - Malformed input / script misuse / JSON construction failure は non-zero とする。
- 回答日時:
  - 2026-06-11T14:00:00Z

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし。現時点の blocking scope questions は解消済み。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`
  - `design.md`
  - `plan.md`
  - `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - `doctor` は診断結果を返すこと自体が価値であり、capability finding があるだけで command failure にしない。
  - PR observation は final JSON を authority とする既存境界を保ちつつ、permission limitation を merge-prepared evidence に使えない semantic non-success として明示する必要がある。
  - process failure と semantic failure を分けることで、caller が JSON の limitation / recommended action を読んで修正または human gate へ進める。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - MUST に `doctor` は capability findings を診断結果として返すことを入れる。
  - MUST に PR observation は permission limitation を final JSON の semantic non-success として返し、merge-prepared evidence に使えないことを入れる。
  - MUST に malformed input / script misuse / JSON construction failure は command/runtime error として扱うことを入れる。
- `design.md`:
  - process exit code と semantic status を分離する。
  - `doctor` は findings list / warning message に capability result を追加する。
  - PR observation は normalized status、limitations、recommended next action に permission limitation を反映する。
  - `permission_denied` を新 status として導入するか、既存 `unknown` / `human_gate` + limitation に留めるかは design phase で具体化する。
- `plan.md`:
  - `doctor` tests は exit 0 + findings を期待する。
  - PR observation tests は process exit 0 + final JSON semantic non-success を期待する。
  - malformed input / script misuse / invalid JSON などは non-zero case として別に検証する。
- `ADR`:
  - 現時点では不要。failure semantics は issue-level decision として `report.md` に記録する。
- reflected_to 更新方針:
  - requirement / design / plan 作成時にこの interview を採用 evidence として参照し、`report.md` Evidence Adoption Ledger に採用済みとして記録する。
- adoption reflection:
  - `iss-00180` は capability failure を一律 fatal にせず、surface ごとに process success と semantic non-success を分ける。

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
