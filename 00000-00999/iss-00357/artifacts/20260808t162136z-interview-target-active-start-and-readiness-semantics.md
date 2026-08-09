---
種別: interview
ID: "20260808t162136z-interview"
タイトル: "Target Active Start and Readiness Semantics Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-08-09"
親: ["iss-00357"]
関連:
  - "iss-00358"
  - "iss-00359"
  - "iss-00360"
  - "20260808t082616z-research"
  - "20260808t092131z-interview"
scope: "issue"
scope_id: "iss-00357"
created_at: "2026-08-08T16:21:36Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT Use Strict session: required-strict-github-connector-verificati-2"
  - "verified GitHub repository: chemitaro/spec-dock"
  - "verified branch: main"
  - "verified expected SHA: 17ef3fd92a865bf8ebd788ed69ff297476c3db99"
reflected_to: []
---

# 20260808t162136z-interview Target Active Start and Readiness Semantics Interview

## 位置づけ

- Target `issue finish`をThin Lifecycle PrimitiveとするOption A採用後、ChatGPT Use StrictでGitHub上の最新commitを再調査し、残存Gapの第1位として選定された。
- `issue finish`だけを薄くしても、`active set`、`.agent/active.json`、Context Pack、`issue start`の経路にAuthority、grants、promotion record、EAL等が残れば、Storage Coreの境界は完成しない。
- 回答後はこのArtifactへ記録し、commit・push後に同じChatGPTスレッドへStrictで返す。Canonical docsへの反映は別工程とする。

## 正式質問として扱う理由

- `requirement.md`:
  - Active Scopeの選択、実装開始、dependency readinessを別の概念として定義する。
- `design.md`:
  - `active set`、`issue start`、`.agent/active.json`、Context Pack、dependency checkの責務境界を決める。
- `plan.md`:
  - Active ManifestとLifecycle applicationから旧Workflow Authorityを除去する範囲と、blocked / unfinished / forceの回帰テストを決める。
- `ADR`:
  - Storage CoreにおけるSelectionとWork Startの長期境界として必要かを判断する。
- chat上の軽微な一問では足りない理由:
  - Issue 357のRuntime・Manifest・Context Pack・Lifecycleの削除範囲だけでなく、Issue 358のAuthoring guidance、Issue 359のSkill操作契約、Issue 360のconsumer移行へ波及する。

## 質問の目的

- 対象者:
  - SpecDockのProduct Ownerであるユーザー。
- 何を明確にする質問か:
  - Targetの`active set`と`issue start`の責務を分けるか、dependency gateをどこで強制するか、readinessが何を意味するか。
- 回答が後続判断へ与える影響:
  - Issue 357のActive / Lifecycle contractと、Issue 358 / 359 / 360へのhandoffを固定する。

## 質問

- pressure-test question:
  - blocked IssueをClarificationやPlanning目的でActiveにする必要と、登録済み依存関係を無視した実装着手を防ぐ必要を、Workflow Authorityを復活させずに両立できるか。
- 質問:
  - Targetの`active set`、`issue start`、dependency readinessをどの契約にしますか？
- 回答してほしいこと:
  - Option A、B、Cのいずれかを選択してほしい。

## source-grounded context

- ChatGPT Use StrictはGitHub connectorで`chemitaro/spec-dock`の`main`先端が期待SHA `17ef3fd92a865bf8ebd788ed69ff297476c3db99`と完全一致することを確認し、そのcommitだけを参照した。
- 現行Active ManifestはIDとPathだけでなく、authority、grants、promotion recordを保持する。
- 現行`active set`とContext PackはImplementation / Finish Authority、Delegated Artifact、ReportのEAL等を評価する。
- dependency readinessもactive選択または作業開始の経路でgateとして使われている。
- `issue finish`では品質・完了gateを除去することが採用済みであり、Active subsystemに別経路で残すと方針が矛盾する。
- `dependency-ready`をplanning completionやimplementation-readyと混同しない契約が必要である。

## 回答案

- Option A — SelectionとWork Startを分離:
  - `active set`はInitiative / Epic / IssueをActive Scopeへ設定するだけとし、blocked Issueも調査・Clarification・Planning目的で選択できる。
  - `active set`はAuthority、grants、promotion record、EAL、Review、Planning Levelを判定しない。
  - `issue start`はIssue専用の作業開始Convenienceとし、unfinished active Issue guard、dependency readiness確認、branch checkout、active設定を行う。
  - `--force`はunfinished active Issue guardのみを迂回し、dependency blockerは迂回しない。
  - `.agent/active.json`はIDとPathだけを保持する。
  - readinessは常にdependency-readyのみを意味する。
- Option B — Active選択とWork Startの両方でDependency Gateを強制:
  - blocked ScopeはActiveにできない。
  - Authority・Review等は判定しない。
  - blocked Issueの調査・Planningには別経路またはforceが必要になる。
- Option C — Active選択とWork Startの両方をSelection-onlyにする:
  - Dependencyは`deps check`が示すAdvisory情報のみとする。
  - blocked Issueでも`issue start`できる。
  - 依存順序をRuntimeが保護しない。

## Codex の分析

- 判断軸:
  - Runtime軽量化、Clarification / Planningの自由度、実装着手時の依存安全性、Workflow Authorityの再侵入防止、操作契約の分かりやすさ。
- tradeoff:
  - AはSelectionとWork Startを分け、調査の自由度と実装時の依存安全性を両立する。BはActive操作が一貫するがblocked Issueの調査経路を複雑にする。Cは最も軽いが誤着手防止を利用者とSkillのみへ委ねる。
- リスク:
  - Aで`ready`を単に「着手可能」と表示するとplanning / implementation readinessと誤読されるため、dependency-onlyと明示する必要がある。
- 具体シナリオ / edge case:
  - 依存先が未closeのIssueは`active set`で開いてRequirementの確認やClarification Artifact作成はできるが、`issue start`はdependency blockerを返して実装branch開始を防ぐ。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - Active Scopeを調査・Planningのため自由に選べる一方、`issue start`を登録済み依存関係を守る安全な実装開始入口として残せる。Workflow Authorityや品質gateをRuntimeへ戻さず、`ready`もdependency-onlyの意味へ縮退できる。
- 未回答時の影響:
  - Issue 357はActive Manifest、Context Pack、`active set`、`issue start`から旧Workflow Authorityをどこまで除去するか固定できない。

## 各Issueへの影響

| 選択 | Issue 357 | Issue 358 | Issue 359 / 360 |
|---|---|---|---|
| A | Active ManifestからAuthority / grants / promotionを除去し、Context PackをScope・文書・Dependency案内へ縮退する。`active set`と`issue start`を分離する。 | `dependency-ready` はplanning / implementation-readyではないとGuideへ明記し、Plan・Report・Planning Levelをstart条件にしない。 | Issue 359は単純な使い分けをSkillで説明する。Issue 360は旧Active Manifestをgenerated stateとして再生成・移行する。 |
| B | Active選択にもDependency評価を残すためRuntimeがやや重くなる。 | blocked IssueのClarification経路を別途説明する。 | Issue 359の説明と回復経路が増える。 |
| C | `issue start`からDependency Gateも除去できる。 | Guideで依存順守を強く注意喚起する。 | 自律並列作業での誤着手防止が弱くなる。 |

## ユーザー回答

- answer capture:
  - 「オプションAを採用します」と明示された。
- 回答:
  - Option AのSelectionとWork Startを分離する契約を採用する。
  - `active set`は調査・Clarification・Planningのための単純なActive Scope選択とし、blocked Issueも選択できる。
  - `active set`はAuthority、grants、promotion record、EAL、Review、Planning Levelを判定しない。
  - `issue start`はunfinished active Issue guard、dependency readiness確認、branch checkout、active設定を行う作業開始Convenienceとする。
  - `--force`はunfinished active Issue guardのみを迂回し、dependency blockerは迂回しない。
  - `.agent/active.json`はIDとPathだけを保持し、readinessはdependency-readyのみを意味する。
- 回答日時:
  - 2026-08-09

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次のunanswered `interview`として切り出す質問:
  - Target Artifact catalogとprovider固有Surface、または`report.md`のTarget semanticsのうち、回答後のStrict再調査で最優先となった一問。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - Issue 357のRequirement / Design / Plan、Issue 358のAuthoring guidance、Issue 359のSkill契約、Issue 360のconsumer移行。
- 採用 / 棄却 / deferred の理由:
  - Product OwnerがOption Aを明示採用したため。
  - Clarification / Planningのための自由なScope選択と、実装開始時のdependency安全性を両立しつつ、Workflow AuthorityをRuntimeへ戻さない。
- `report.md` Evidence Adoption Ledger への反映要否:
  - 旧EALを必須化せず、Canonical reflection時に通常の採用証跡を残す。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Active Selection、Work Start、dependency-readyの責務を分ける契約を採用候補として反映する。
- `design.md`:
  - Active Manifestの最小スキーマ、Context Packの縮退、`active set`と`issue start`の処理順序を採用候補として反映する。
- `plan.md`:
  - 旧Authority / grant / promotion / EAL依存の除去と、blocked / unfinished / force / dependency-readyの回帰テストを採用候補として反映する。
- `ADR`:
  - Issue Designで十分に固定できるかをauthoring時に判断する。
- reflected_to 更新方針:
  - Canonicalへ実際に採用した時点で更新する。
- adoption reflection:
  - Interview Artifact上で採用済み。Canonical docsにはまだ未反映。
