---
種別: interview
ID: "20260713t002530z-interview"
タイトル: "Experimental Workbench Rollout Boundary"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312"]
関連: []
scope: "epic"
scope_id: "epic-00312"
created_at: "2026-07-13T00:25:30Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "artifacts/20260712t235647z-research-workbench-clarification-baseline-and-decision-inventory.md"
  - "artifacts/20260713t001708z-interview-scope-workbench-copy-collision-policy.md"
reflected_to:
  - "epic-00312 requirement/design/plan authoring input"
  - "epic-00312 report.md Evidence Adoption Ledger"
---

# 20260713t002530z-interview Experimental Workbench Rollout Boundary

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
    - Experimental capabilityの対象利用者とavailability。
  - `design.md`:
    - Provider asset / installed runtime / dogfooding-only boundary。
  - `plan.md`:
    - Rollout Issue、provider-consumer parity、final dogfood gate。
  - `ADR`:
    - 現時点では不要。
- chat 上の軽微な一問では足りない理由:
  - 回答により実装場所、tests、docs、`init/update`影響、受け入れ条件が変わる。

## 質問の目的 (必須)
- 対象者:
  - Product owner / maintainer。
- 何を明確にする質問か:
  - Experimental Workbenchをdogfooding repoだけで開始するか、installed product surfaceとして全consumerへ配布するか。
- 回答が後続判断へ与える影響:
  - Provider-side source of truth、compatibility wrapper、consumer parity、help/docs exposureを決める。

## 質問 (必須)
- pressure-test question:
  - Experimentalであっても`.workbench/` scanner pruneは全consumerのruntime safety contractになりうる一方、copy commandまで全consumerへ見せると未成熟なpublic surfaceになる。
- 質問:
  - 初期リリースでは、Workbench safetyと`workbench copy` commandを`spec-dock init/update`で全consumerへ配布しexperimental表記で提供しますか、それともまずこのprovider dogfooding repoだけで試しますか。
- 回答してほしいこと:
  - Option A / B / Cの選択、またはrollout境界の修正。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Parent Initiativeのprovider / dogfooding parity原則、Epic 295 installed runtime先例、provider assetとroot compatibility surface、init/update tests。
- local context で解決できたこと:
  - Provider-side assetsがconsumerへ配布されるsource of truthであり、dogfooding `spec-dock/`単独編集は正式実装にならない。
- まだ人間判断が必要な理由:
  - Experimental commandをどの利用者へ公開するかはProduct ownerのrollout判断である。

## 回答案 (必須)
- Option A:
  - **全consumerへexperimental提供（推奨）**。Provider runtime / ignore / docs / testsへ実装し、`init/update`で配布する。CLI helpとdocsでexperimental、互換保証を限定すると明記する。
- Option B:
  - **Dogfooding-only**。Root compatibility / manual helperにだけ実装し、provider installed runtimeへはまだ入れない。実測後に別Issueで昇格する。
- Option C:
  - **Safetyだけ全consumer、copy commandはdogfooding-only**。Ignore / scanner pruneは正式配布し、copy CLIはlocal helperとして試す。

## Codex の分析 (必須)
- 判断軸:
  - 実際のdogfood価値、provider-consumer parity、未成熟CLIの互換負担、二重実装回避。
- tradeoff:
  - Aは実物に近いdogfoodができるがpublic surfaceになる。Bは安全だがcompatibility helperからruntimeへの二段移行が必要。Cは安全基盤を先行できるがcopy実装の配置が一時的に二重化しやすい。
- リスク:
  - AのCLI contract固定化、B/Cのdogfooding-only implementation drift。
- 具体シナリオ / edge case:
  - Consumer repoで`update`後に`.workbench/`が保持されるケース、experimental commandをautomationがstableと誤認するケース。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - Command自体が単純化されており、正式なprovider runtimeへ一度だけ実装した方がdogfooding parityを保てる。Experimental表記と限定的compatibility promiseで未成熟性を管理できる。
- 未回答時の影響:
  - Requirementの主要挙動は進められるが、Issue分割とrollout受け入れ条件を確定できない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 2026-07-13のチャット回答。
- 回答:
  - Option Aを採用する。
  - `.workbench/` ignore、runtime-wide scanner除外、experimental `workbench copy` commandをprovider runtimeへ実装する。
  - `spec-dock init/update`でconsumer repositoryへ配布する。
  - CLI helpとdocsでexperimentalと明示し、dogfooding-onlyの別実装は持たない。
- 回答日時:
  - 2026-07-13 Asia/Tokyo

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - no
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - なし。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`, `design.md`, `plan.md`, `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Product ownerが明示的にrollout boundaryを選択し、provider / consumer implementation、docs、tests、acceptanceを決めるため採用する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - Workbenchは全consumerへ配布するexperimental capabilityとし、dogfooding-onlyではない。
- `design.md`:
  - Provider-side runtime / assetsを唯一のimplementation authorityとし、dogfooding treeはparity確認面とする。
- `plan.md`:
  - Safety foundation、copy command、installed docs / dogfood / final gateの3 Issue構成を採用候補とする。
- `ADR`:
  - 現時点では不要。Experimental contractとしてEpic canonical docsで所有する。
- reflected_to 更新方針:
  - Canonical authoring時にrequirement / design / planへ反映し、report EALへ本artifactを採用証跡として記録する。
- adoption reflection:
  - Option Aを採用。Option B / Cのdogfooding-only laneは二重実装とdriftを生むため棄却する。

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
