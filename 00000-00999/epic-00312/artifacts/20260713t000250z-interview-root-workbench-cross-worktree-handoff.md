---
種別: interview
ID: "20260713t000250z-interview"
タイトル: "Root Workbench Cross Worktree Handoff"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312"]
関連: []
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-13T00:02:50Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260712t235647z-research-workbench-clarification-baseline-and-decision-inventory.md"
  - "artifacts/20260712t235757z-interview-initial-workbench-copy-file-policy.md"
reflected_to:
  - "epic-00312 requirement/design/plan authoring input"
  - "epic-00312 report.md Evidence Adoption Ledger"
---

# 20260713t000250z-interview Root Workbench Cross Worktree Handoff

## 位置づけ
- 用途: 重要判断に関わる一つの質問を、回答前の source-grounded 正式質問シートとして作成し、回答後に同じ artifact を完成 record にする。
- authority default: `proposed`。ユーザー回答と採用判断を反映した後は、必要に応じて `user-approved` または `synthesized` に更新する。
- この artifact は answer capture / adoption target / reflection の evidence surface であり、main orchestrator が canonical docs / accepted ADR / `report.md` Evidence Adoption Ledger へ採用するまでは canonical authority ではない。
- 技術的に調べられることは先に docs / code / tests / ADR / artifacts / primary source を確認する。
- 一つの `interview` artifact には one essential question / 一つの本質的な質問だけを書く。回答によって新しい高影響な曖昧さが見つかった場合は、追加質問をこの file に増やさず、次の unanswered `interview` を作成する。
- trivial な yes/no は、重要な判断、後続反映、回答証跡が必要なら `interview` を使い、そうでなければ issue comment や `blank` で足りる。
- 回答から複数質問の synthesis が必要になったら `disc`、追加調査が必要になったら `research`、長期判断が固まったら `adr` を新規作成する。

## 正式質問として扱う理由 (必須)
- 影響する artifact:
  - `requirement.md`:
    - Root Workbenchのcross-worktree handoff対象とnon-scope境界。
  - `design.md`:
    - Scope copy commandとroot topic handoffの責務分離。
  - `plan.md`:
    - Experimental v1にroot copy commandを含めるか、manual workflowへ延期するか。
  - `ADR`:
    - 現時点では不要。
- chat 上の軽微な一問では足りない理由:
  - 回答によりpublic CLI surface、Issue slicing、root Workbenchの腐敗・二重scope管理リスクが変わる。

## 質問の目的 (必須)
- 対象者:
  - Product owner / maintainer。
- 何を明確にする質問か:
  - Scopeに閉じないroot Workbenchから新worktreeへ何を、どの単位で持ち込むか。
- 回答が後続判断へ与える影響:
  - Scope copy commandだけでv1を閉じるか、root topic handoff機能も同時に作るかを決める。

## 質問 (必須)
- pressure-test question:
  - Root Workbench全体は日付をまたぐ横断・未整理作業を含むため丸ごとcopyできないが、個別file選択を導入すると先ほど採用した「選別しない単純copy」と緊張する。
- 質問:
  - Root Workbenchの情報を新worktreeへ持ち込む標準は、関連topicを先にScope-local `.workbench/`へ移してからScope copyする方式と、rootの日付/topic directoryを単位に別copy commandで直接持ち込む方式のどちらにしますか。
- 回答してほしいこと:
  - Option A / B / Cの選択、または境界の修正。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Epic 00312 baseline、回答済みfile policy interview、root date bucket / scope-local Workbench合意、current worktree runtime surface。
- local context で解決できたこと:
  - Root Workbenchは`spec-dock/.workbench/YYYY-MM-DD/`、Scope-local Workbenchは`<scope>/.workbench/`。RootにScope ID bucketを作らず、root全体の自動copyもしない。
- まだ人間判断が必要な理由:
  - Root topicをScope ownershipへattachしてから運ぶか、non-scopeのままworktree間transferする価値を持たせるかはproduct運用判断である。

## 回答案 (必須)
- Option A:
  - **Scopeへattachしてからcopy（推奨）**。Root topicのうち新worktreeで必要なdirectoryを、source側の対象Scope `.workbench/`へ手動で移動またはコピーし、その後`workbench copy <scope-id>`でScope Workbench全体を持ち込む。Root専用commandは作らない。
- Option B:
  - **Root topic copy command**。`workbench copy-root <YYYY-MM-DD>/<topic> --to <worktree>`のようにtopic directoryを単位として直接copyする。Root全体やfile単位selectionは提供しない。
- Option C:
  - **初期はroot transfer対象外**。必要な場合は通常のfilesystem copyを人間／Codexが手動実行し、dogfoodで頻度を測ってからA/Bを決める。

## Codex の分析 (必須)
- 判断軸:
  - CLI最小性、scope ownershipの明確さ、root腐敗、二重tree回避、実際のpre-scope / cross-scope利用頻度。
- tradeoff:
  - AはScope ownershipを明確にし、既存Scope copy commandを再利用できるが、source側で一段整理が必要。Bは横断topicをそのまま運べるが、追加CLIとpath contractが必要。Cは最小だが手動操作がばらつく。
- リスク:
  - Aでは複数Scopeに関係するtopicの所属を早く固定しすぎる。Bではroot topic copyがsession/path管理へ拡張しやすい。Cではworktree分岐時の欠落が再発する。
- 具体シナリオ / edge case:
  - 一つのroot topicから複数Epicが生まれる場合、同じtopicを複数worktreeへ持ち込む場合、日付bucket全体に無関係なtopicが混在する場合。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - Experimental v1のpublic commandをScope copy一つに保てる。新worktreeで実装する対象が決まった段階では、必要topicをそのScopeの作業文脈へattachすることが自然であり、root全体やpath-selection commandを作らずに済む。
- 未回答時の影響:
  - Scope-local safety foundationとcopy commandは設計できるが、root Workbenchのhandoffをv1 scope / non-scopeのどちらに置くか確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 2026-07-13のチャット回答。Root Workbenchはゴミを多く含む未整理領域であり、一括handoff対象にしないと明示した。
- 回答:
  - Root Workbench用のcopy commandは作らない。
  - Root Workbenchを自動・一括copyしない。
  - 新worktreeやScopeで必要なfileだけをモデルが内容に基づいて判断し、通常のfilesystem操作で手動copyする。
  - Root Workbenchは基本的に雑多で不要物を含む前提であり、全体を引き継がない。
- 回答日時:
  - 2026-07-13 Asia/Tokyo

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Scope-local Workbench copy時にsource / destinationで同名pathが衝突した場合、sourceで上書きするか、衝突時に停止するか、既存を保持するか。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`, `design.md`, `plan.md`, `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Root Workbenchの実態と低摩擦運用に関するProduct ownerの明示判断であり、v1 CLI non-scopeとmodel運用を決めるため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Root Workbenchはcross-worktree一括copyの対象外。必要fileのmodel判断によるmanual copyだけを許容する。
- `design.md`:
  - `workbench copy`はScope IDを持つScope-local Workbenchだけを扱う。Root date bucket / topic / path selectionをcommand contractへ含めない。
- `plan.md`:
  - Root handoff helper、copy-root、attach command、automatic root transferを全Issueのnon-scopeにする。Docs / skillへmanual selection ruleだけを記載する。
- `ADR`:
  - 現時点では不要。
- reflected_to 更新方針:
  - Canonical authoring時にrequirement / design / planへ反映し、report EALへ本artifactを採用証跡として記録する。
- adoption reflection:
  - Option Aのうち「必要topicをScopeへattachしてからScope copy」は許容するが、attach専用commandは作らず、モデルが必要fileを手動copyする運用へ簡素化する。

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
- 追加で作る artifacts:
  - ...
