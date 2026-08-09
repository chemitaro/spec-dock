---
種別: interview
ID: "20260809t025001z-interview"
タイトル: "Target Report Contract Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-08-09"
親: ["iss-00358"]
関連:
  - "iss-00357"
  - "iss-00359"
  - "iss-00360"
  - "20260808t082616z-research"
  - "20260809t004834z-interview"
scope: "issue"
scope_id: "iss-00358"
created_at: "2026-08-09T02:50:01Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT Use Strict session: required-strict-github-connector-verificati-5"
  - "verified GitHub repository: chemitaro/spec-dock"
  - "verified branch: main"
  - "verified expected SHA: 1c8a8b25470f5b374e44623349d157499df99768"
reflected_to: []
---

# 20260809t025001z-interview Target Report Contract Interview

## 位置づけ

- Target Artifact Surfaceとtype未指定時の`blank`既定値の採用後、ChatGPT Use StrictがGitHub上の最新commitを再調査し、残存Gapの第1位として選定した。
- `report.md`をRuntime gateにしないことは採用済みだが、新規Nodeでの存在契約とCurrent Authoring Kit上の責務が未確定である。
- 回答後はこのArtifactへ記録し、commit・push後に同じChatGPTスレッドへStrictで返す。Canonical docsへの反映は別工程とする。

## 正式質問として扱う理由

- `requirement.md`:
  - 新規Initiative / Epic / Issueにおける`report.md`の存在契約と、品質gateにしないことを決める。
- `design.md`:
  - Scaffolder、Context Pack、Validator、Authoring Kitの責務と、Existing ReportのHistorical compatibilityを決める。
- `plan.md`:
  - Template置換または削除、Runtime依存除去、fresh / existing consumer、回帰テストの範囲を決める。
- chat上の軽微な一問では足りない理由:
  - Issue 357のNode Scaffold / Runtime契約とIssue 358の文書契約の共有境界であり、Issue 359 / 360のSkill・Migrationにも影響する。

## 質問の目的

- 対象者:
  - SpecDockのProduct Ownerであるユーザー。
- 何を明確にする質問か:
  - Targetで新規Nodeに`report.md`を常に生成するか、ファイル自体を任意生成にするか、Current Authoring Kitから外すか。
- 回答が後続判断へ与える影響:
  - Issue 357 / 358のRequirement / Design / Planと、Issue 359 / 360へのhandoffを固定する。

## 質問

- pressure-test question:
  - `report.md`を残すことが、旧EAL・Reviewer Gate・Promotion・Delegated Authoringを復活させず、実装結果と検証を簡潔に残す価値だけを提供できるか。
- 質問:
  - Targetでは、新規Initiative / Epic / Issueの`report.md`をどの契約にしますか？
- 回答してほしいこと:
  - Option A、B、Cのいずれかを選択してほしい。

## 全選択肢の共通前提

- `report.md`を`issue start`、`issue finish`、dependency readinessのgateにしない。
- EAL、Reviewer Gate、Promotion、Delegated Authoringを復活させない。
- Existing `report.md`は削除・書換えしない。
- Durableな要件・設計・計画判断はRequirement / Design / PlanまたはADRへ反映する。

## source-grounded context

- ChatGPT Use StrictはGitHub connectorで`chemitaro/spec-dock`の`main`先端が期待SHA `1c8a8b25470f5b374e44623349d157499df99768`と完全一致することを確認し、そのcommitだけを参照した。
- 親Epic Designは`report.md`をoptionalな「任意の簡潔な実行・結果記録」とするが、ファイル常設か内容任意かは未確定である。
- Issue 358のResearch Artifactも、ファイル常設とファイル自体任意を未決の二択として記録している。
- 現行Node creationはScope Template directoryのファイルをScaffoldするため、Reportの存在契約はRuntimeとAuthoring Kitの両方に波及する。
- 現行Report TemplateはDecision Ledger、EAL、Spec Authoring Gate、Delegated Draft Evidence、Reviewer Status等を含む大規模なWorkflow台帳であり、Targetの軽量化と一致しない。
- 採用済みの`issue finish`とActive / Start契約により、ReportをRuntimeの品質・完了gateにしないことは確定している。

## 回答案

- Option A — 全Scopeで常に薄い`report.md`をScaffold:
  - 新規Initiative / Epic / Issueに常に最小の`report.md`を生成する。
  - 内容はOutcome、Verification、Residual Risks / Follow-ups等の3〜4節程度とし、記入は任意にする。
  - 空のままでもvalidとし、Runtimeは内容を読んで判定しない。
- Option B — `report.md`ファイル自体を任意にする:
  - 新規Nodeでは生成しない。
  - 必要な場合だけ、人間またはAgentがAuthoring Kitの任意Templateから作成する。
  - `report.md`が存在しないことを常に正常とする。
- Option C — `report.md`をCurrent Authoring Kitから外す:
  - 新規作成用TemplateとCurrent navigationから`report.md`を除去する。
  - 実装結果・検証結果はArtifactに残し、Durableな判断だけをRequirement / Design / Plan / ADRへ反映する。
  - Existing ReportはHistorical Evidenceとしてのみ保持する。

## Codex の分析

- 判断軸:
  - Storage Coreの単純性、安定Path、文書スロップの防止、実装・検証結果の記録先、Scaffolder分岐、Existing consumer互換性。
- tradeoff:
  - Aは安定Pathを残し、Template本文の薄型化だけで実現できる。Bは不要な空ファイルを減らせるが、必要時の作成規則を新設する。Cは最も小さいが、Outcome / Verificationの安定した置き場を失う。
- リスク:
  - AでもTemplateを大きなChecklistへ肥大化させると旧Workflowの複雑さが復活するため、節数と責務を薄く保つ必要がある。
- 具体シナリオ / edge case:
  - 新規Issueの`report.md`が空のままでも`validate`と`issue finish`は成功できる。必要な場合だけ、実行結果・検証・残余リスクを追記する。

## Codex の推奨案

- 推奨:
  - Option A。
- 理由:
  - 現行Scaffolderの単純さと安定Pathを保ちながら、内容を任意の軽量Result Summaryへ縮退できる。ファイル常設と記入必須を分けることで、Workflow gateと台帳スロップを復活させず、実装結果・検証・残余リスクの記録先を残せる。
- 未回答時の影響:
  - Issue 357のScaffold / Context Pack / Validation契約と、Issue 358のReport Template / Guide契約を固定できない。

## 各Issueへの影響

| 選択 | Issue 357 | Issue 358 | Issue 359 / 360 |
|---|---|---|---|
| A | 新規Nodeに最小`report.md`が常に存在するScaffold契約を保持し、Runtimeは内容・存在を品質gateにしない。「生成される」「空でもvalid」「start / finishへ影響しない」を回帰する。 | 任意内容の軽量Result Summaryとして定義し、巨大Ledger Templateを3〜4節へ置換する。Durable decisionはR/D/P/ADRへ反映する。 | Issue 359はReportを必須入力にせず、存在する場合だけ結果要約として利用する。Issue 360はFresh Templateを差し替え、Existing Report本文は維持する。 |
| B | Node ScaffoldからReportを除外し、Context Pack・Validator・Active表示はReport欠落を正常扱いする。 | Optional Report Templateの配置、作成条件、命名、Scope差を定義する。 | Issue 359はReportを自動作成せず、Issue 360はFresh consumerからReportを除きExisting Reportを保持する。 |
| C | Runtime・Context Pack・ValidationからCurrent Report参照を除去し、Existing ReportだけをHistorical-compatibleに扱う。 | Current Report Template / Guideを削除し、Outcome / Verificationの保存先をArtifactとCanonical docsへ再配置する。 | Issue 359はReportを案内せず、Issue 360はmanaged Report Template / DocsをpruneしつつNode-local Existing Reportを保持する。 |

## ユーザー回答

- answer capture:
  - 「オプションAを採用します」と明示された。
- 回答:
  - Option Aとして、新規Initiative / Epic / Issueに常に最小の`report.md`をScaffoldする。
  - `report.md`はOutcome、Verification、Residual Risks / Follow-ups等の3〜4節程度の軽量Result Summaryとする。
  - 内容の記入は任意であり、空のままでもvalidとする。
  - Runtimeは`report.md`の内容または記入状態を読んで、`issue start`、`issue finish`、dependency readiness、品質、完了を判定しない。
  - EAL、Reviewer Gate、Promotion、Delegated AuthoringをReport Templateへ復活させない。
  - Existing `report.md`の本文は削除・移動・一括書換えせず保持する。
  - Durableな要件・設計・計画判断はRequirement / Design / PlanまたはADRへ反映する。
- 回答日時:
  - 2026-08-09

## 追加確認の要否

- 追加確認が必要か:
  - 回答後のStrict再調査で判定する。
- 必要な場合に次のunanswered `interview`として切り出す質問:
  - External intelligence smokeの合格条件、または回答後のStrict再調査でより高影響と判断された一問。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - Issue 357 / 358のRequirement / Design / Plan、Issue 359のSkill契約、Issue 360のFresh / Existing consumer移行。
- 採用 / 棄却 / deferred の理由:
  - Product OwnerがOption Aを明示採用したため。
  - 安定Pathと現行Scaffolderの単純さを保ちながら、内容を任意の軽量Result Summaryへ縮退し、Workflow gateと大規模台帳を除去できる。
- `report.md` Evidence Adoption Ledger への反映要否:
  - 旧EALを必須化せず、Canonical reflection時に通常の採用証跡を残す。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Reportの常設契約、内容の任意性、空でもvalid、Runtime gate非関与の契約を採用候補として反映する。
- `design.md`:
  - Scaffolderの安定Path、Runtime非判定、軽量Report Template、Existing Report保持の責務を採用候補として反映する。
- `plan.md`:
  - Report Templateの薄型置換、旧Workflow依存除去、fresh / existing consumer、生成・空valid・start / finish非干渉の回帰テストを採用候補として反映する。
- `ADR`:
  - Issue Designで十分に固定できるかをauthoring時に判断する。
- reflected_to 更新方針:
  - Canonicalへ実際に採用した時点で更新する。
- adoption reflection:
  - Interview Artifact上で採用済み。Canonical docsにはまだ未反映。
