---
種別: interview
ID: "20260713t005207z-interview"
タイトル: "Same Family Repair Recurrence Continuation Policy"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
関連: []
scope: "issue"
scope_id: "iss-00313"
created_at: "2026-07-13T00:52:07Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md"
reflected_to:
  - "requirement.md authoring input"
  - "design.md authoring input"
  - "plan.md authoring input"
  - "report.md Evidence Adoption Ledger"
---

# 20260713t005207z-interview Same Family Repair Recurrence Continuation Policy

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
    - 固定回数上限撤廃の範囲と、継続・停止の観測可能な条件を決める。
  - `design.md`:
    - `same root_cause_family reappears`をhuman gateのまま残すか、progress-based判定へ置き換えるかを決める。
  - `plan.md`:
    - skill本体と2種類のrepair-batch scaffoldの変更範囲を決める。
  - `ADR`:
    - Accepted blocker-centric ADRのstagnation human gateを維持できるため、新規ADRは現時点で不要。
- chat 上の軽微な一問では足りない理由:
  - 回答により「数値3行だけの削除」と「実質的な同一family一回停止も含む継続契約変更」で受け入れ条件と変更範囲が変わる。

## 質問の目的 (必須)
- 対象者:
  - SpecDock maintainer / 夜間自動実行の運用者。
- 何を明確にする質問か:
  - 同じroot-cause familyがfresh reviewで再出現した場合の自律継続境界。
- 回答が後続判断へ与える影響:
  - Requirementの停止条件、skillの`Fix loop limits`、templateの`Loop Control`と`Stop Conditions`を確定する。

## 質問 (必須)
- pressure-test question:
  - 回数制限だけ削除してもsame-family recurrenceで一度の修正後に止まるなら、夜間自動実行の問題は本当に解消するか。
- 質問:
  - 同じ`root_cause_family`が修正後のfresh reviewで再出現しても、新しい修正戦略と検証可能な前進がある限り自律的に修復を続け、同じ戦略の反復や新しい根拠がない「stagnation」に達した場合だけhuman gateで止める方針にしますか。
- 回答してほしいこと:
  - Option A / B / Cの選択、または継続・停止境界の修正。

## source-grounded context (必須)
- 確認済みの docs / code / tests / ADR / artifacts / primary source:
  - Provider `github-pr-merge-preparer/SKILL.md`、skill-local `pr-repair-batch.md`、runtime artifact template、blocker-centric ADR、Issue research baseline。
- local context で解決できたこと:
  - P0=1回、同一P1=2回、総計4回の数値上限は撤廃対象。permission/auth、外部障害、scope expansion、breaking change等は回数と無関係なhuman gateとして維持する。
- まだ人間判断が必要な理由:
  - same-family recurrenceを即停止とするかprogress-basedにするかは、自律性とfail-closed運用の優先度を決めるproduct-owner判断だから。

## 回答案 (必須)
- Option A:
  - **Progress-based継続（推奨）**。数値上限とsame-family即停止を撤廃し、新しいstrategy/evidenceとscope内の検証可能な前進がある限り続ける。stagnationまたは既存human-gate条件で止める。
- Option B:
  - **数値上限だけ撤廃**。P0/P1/総計の固定値は削除するが、same-familyが一度再出現したらhuman gateで止める。
- Option C:
  - **完全無制限**。same-family recurrenceやstagnationでも止めず、外部/権限/scope判断が必要になるまで修復を続ける。

## Codex の分析 (必須)
- 判断軸:
  - 夜間完走率、安全性、無意味な同一修正反復の防止、既存ADRとの整合。
- tradeoff:
  - Aは不要な停止を解消しつつstagnation safetyを残す。Bは変更が最小だがユーザーの問題を実質的に残す。Cは完走を最大化するが無限反復とCI/token消費を抑えにくい。
- リスク:
  - Progress判定を曖昧にすると、実質的な回数上限へ戻るか、逆に同一修正を無限反復する。
- 具体シナリオ / edge case:
  - 修正後に同じfamilyの別境界条件が見つかる場合はAなら継続、同じpatch/同じfailureが再現するだけならstagnationで停止する。

## Codex の推奨案 (必須)
- 推奨:
  - Option A。
- 理由:
  - 「止まったら続けてくださいと言うだけ」という運用負担はsame-family即停止でも発生するため、数値削除だけでは目的を満たさない。既存ADRのstagnation human gateは安全弁として残せる。
- 未回答時の影響:
  - Requirementの主要な停止条件を確定できず、canonical authoringと実装へ進めない。

## ユーザー回答 (回答後に必須)
- answer capture:
  - 2026-07-13のチャット回答。
- 回答:
  - Option Aのprogress-based継続を採用する。
  - 固定回数とsame-family即停止を撤廃し、新しい修正戦略と検証可能な前進がある限り自律修復を続ける。
  - 無限修正は避け、ChatGPT-Useによるレビュー分析と統合repair-batch authoringをworkflowへ追加する方向で具体化する。
- 回答日時:
  - 2026-07-13 Asia/Tokyo

## 追加確認の要否 (回答後に必須)
- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - ChatGPT-Useが作成するrepair-batch draftの採用・review・fallback境界は、外部分析後にsource-groundedな候補が残る場合だけ質問する。

## 採用判断 (回答後に必須)
- adoption_status:
  - adopted
- adoption target:
  - `requirement.md`, `design.md`, `plan.md`, `report.md` Evidence Adoption Ledger
- 採用 / 棄却 / deferred の理由:
  - Product ownerの明示回答であり、主要な継続・停止契約を確定するため。
- `report.md` Evidence Adoption Ledger への反映要否:
  - yes

## requirement / design / plan / ADR への含意 (回答後に必須)
- `requirement.md`:
  - 固定回数では止めず、progressまたはstagnationで継続可否を判断する。
- `design.md`:
  - ChatGPT-Use analysisとrepair-batchを用いて、family横断の原因・設計・計画を可視化してから修復する。
- `plan.md`:
  - Skill、repair-batch template、ChatGPT-Use handoff、provider/mirror parityを一体で変更・検証する。
- `ADR`:
  - 既存blocker-centric ADRのstagnation human gateを維持するため、新規ADR要否は追加分析後に判断する。
- reflected_to 更新方針:
  - Canonical authoring時に採用し、report EALへartifact pathと採用判断を記録する。
- adoption reflection:
  - Option Aをそのまま採用。追加提案は別raw artifactとChatGPT-Use分析へ分離する。

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
