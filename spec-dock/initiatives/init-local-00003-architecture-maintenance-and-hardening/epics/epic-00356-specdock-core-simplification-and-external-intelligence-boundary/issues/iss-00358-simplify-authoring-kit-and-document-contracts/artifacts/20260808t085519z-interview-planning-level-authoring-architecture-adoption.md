---
種別: interview
ID: "20260808t085519z-interview"
タイトル: "Planning Level Authoring Architecture Adoption Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-08-08"
親: ["iss-00358"]
関連:
  - "20260808t083300z-interview"
  - "20260808t085519z-01-disc"
  - "iss-00357"
scope: "issue"
scope_id: "iss-00358"
created_at: "2026-08-08T08:55:19Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "adopted"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT proposal session: required-repository-connector-context-repository-58"
reflected_to: []
---

# 20260808t085519z-interview Planning Level Authoring Architecture Adoption Interview

## 位置づけ

- Product Ownerの回答を受けて同じChatGPTスレッドが提示したbest practiceを、Canonical docsへ反映する前に採否確認する一問である。
- 詳細な比較、file tree、level別完成基準、責務分担、テスト候補は`20260808t085519z-01-disc`にまとめた。

## 正式質問として扱う理由

- `requirement.md`:
  - Canonical Planを一つにすること、Planning Levelがdocumentation-onlyであることを決める。
- `design.md`:
  - Base Guideと4 Completion Guideの構造、Runtime非関与、Git履歴を決める。
- `plan.md`:
  - Issue 358の配布ファイル、段階的開示、parity / linkテストを決める。
- `ADR`:
  - 長期のAuthoring contractとして固定する必要性を判断する。
- chat上の軽微な一問では足りない理由:
  - Provider assetのPath、Skill参照先、Runtime / Authoring境界、既存consumer移行へ波及する。

## 質問の目的

- 対象者:
  - SpecDockのProduct Ownerであるユーザー。
- 何を明確にする質問か:
  - ChatGPTが推奨したPlanning Level文書構造を正式なAuthoring Kit方針として採用するか。
- 回答が後続判断へ与える影響:
  - Issue 358のRequirement / Design / Plan authoring briefと、Issue 357 / 359 / 360へのhandoff contractを固定する。

## 質問

- pressure-test question:
  - level別にCanonical Plan fileを分けた場合に生じる「どれが現在の正本か」というauthorityとroutingを、Workflow機構なしで本当に解決できるか。
- 質問:
  - 各IssueのCanonicalな`plan.md`は一つだけ維持し、共通`docs/authoring/plan.md`と、`light.md`・`standard.md`・`strict.md`・`critical.md`の4つのPlanning Level Completion Guideを参照する構成を採用しますか？
- 回答してほしいこと:
  - 採用するか。採用しない場合は、level別Canonical Plan fileまたは単一巨大Guideのどちらを希望するか。

## source-grounded context

- 現行profile別Templateは`.assurance.json.authorized_profile`とRuntime routingへ結合している。
- Product OwnerはこのRuntime機構を完全撤去しつつ、作業完了時のあるべき状態をlevel別文書で残すと回答した。
- ChatGPTは、別Plan file方式はroutingと複数正本を再導入し、単一巨大Guideは肥大化と規則混在を招くため、Base + Completion Guide方式を推奨した。
- 推奨方式ではRuntimeがlevelをparse / persist / validate / enforceせず、選択level・理由・再評価条件を通常の`plan.md`本文へ記録する。

## 回答案

- Option A — 推奨案を採用:
  - Canonical `plan.md`は一つ。
  - 共通Base Guideと4 Completion Guideを配布する。
  - Runtimeはlevelを認識しない。
- Option B — level別Canonical Plan file:
  - `plan-light.md`等を作る。正本選択、routing、level変更時の扱いを別途設計する必要がある。
- Option C — 単一巨大Guide:
  - ファイル数は減るが、全levelの文脈を毎回読み、重複・混在・競合が増える。

## Codex の分析

- 判断軸:
  - Canonical authorityの単一性、Runtime軽量化、progressive disclosure、Git管理、Agentの読み間違い、provider neutrality。
- tradeoff:
  - Option Aは文書数が増えるが、共通部とlevel差分を分離できる。Option Bはlevel固有形を直接示せるが旧routing問題を再生する。Option Cは単純に見えるがGuideを肥大化させる。
- リスク:
  - Option AでもLevel Guideが共通規則を複製するとdriftするため、Baseへの独立差分として書き、link / parityテストが必要である。
- 具体シナリオ / edge case:
  - `standard`から`strict`へ変更しても、`plan.md`のPathは変えず、Level欄、理由、必要項目だけをGit diffで更新できる。

## Codex の推奨案

- 推奨:
  - Option Aを採用する。
- 理由:
  - ユーザーの「複雑なWorkflowは不要」「level別のあるべき状態は文書として必要」を同時に満たし、正本とRuntime stateを増やさない。
- 未回答時の影響:
  - Issue 358のTemplate / Guide file treeと、Issue 357のsingle-template Runtime contractを固定できない。

## ユーザー回答

- answer capture:
  - 「オプションAを採用します」と明示された。
- 回答:
  - Option Aを採用する。
  - 各IssueのCanonical `plan.md`は一つだけ維持する。
  - 共通`docs/authoring/plan.md`と、`light.md`、`standard.md`、`strict.md`、`critical.md`の4つのPlanning Level Completion GuideをAuthoring Kitとして提供する。
  - RuntimeはPlanning Levelをparse / persist / validate / route / enforceしない。
- 回答日時:
  - 2026-08-08

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - Issue 357のTarget `issue finish` semantics。

## 採用判断

- adoption_status:
  - adopted
- adoption target:
  - Issue 358のRequirement / Design / Plan、およびIssue 357 / 359 / 360へのhandoff contract。
- 採用 / 棄却 / deferred の理由:
  - Product OwnerがOption Aを明示採用したため。
  - Canonical Planの単一性、Runtime軽量化、progressive disclosure、Git可視性を同時に満たす。
- `report.md` Evidence Adoption Ledger への反映要否:
  - 旧EALを必須化せず、Canonical reflection時に通常の採用証跡を残す。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Planning Levelのdocumentation-only契約とCanonical `plan.md`一つの要件を採用候補として反映する。
- `design.md`:
  - Base + 4 Completion Guide、Runtime非関与、Git diffによる履歴を採用候補として反映する。
- `plan.md`:
  - Provider / dogfood更新、link / parity / forbidden vocabulary / preservationテストを実装計画候補へ反映する。
- `ADR`:
  - Issue Designで十分に固定できるかをauthoring時に判断し、必要ならADR候補とする。
- reflected_to 更新方針:
  - Canonicalへ実際に採用した時点で更新する。
- adoption reflection:
  - Interview Artifact上で採用済み。Canonical docsにはまだ未反映。
