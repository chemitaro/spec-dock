---
種別: interview
ID: "20260808t083300z-interview"
タイトル: "Issue Profile and Draft Routing Decision Interview"
状態: "answered"
作成者: "iwasawayuuta"
最終更新: "2026-08-08"
親: ["iss-00358"]
関連:
  - "iss-00357"
  - "20260808t082616z-research"
  - "20260808t085519z-01-disc"
  - "20260808t085519z-interview"
scope: "issue"
scope_id: "iss-00358"
created_at: "2026-08-08T08:33:00Z"
created_by: "iwasawayuuta"
status: "answered"
authority: "user-approved"
adoption_status: "partially_adopted"
derived_from:
  - "original ChatGPT thread: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115/c/6a7509b4-8640-83ee-a26d-60c5d59d8479"
  - "ChatGPT clarification session: required-repository-connector-context-repository-57"
reflected_to:
  - "20260808t085519z-01-disc"
---

# 20260808t083300z-interview Issue Profile and Draft Routing Decision Interview

## 位置づけ

- 元のChatGPTスレッドが、Issue 357 / 358のClarificationを行った結果、最初に確認すべき一問として選定した。
- 意味論の主所有者はIssue 358だが、回答はIssue 357のRuntime削除境界にも直接影響する。
- 回答後はこの同じArtifactへ記録し、同じChatGPTスレッドへ回答を返す。Canonical docsへの採用は別工程で行う。

## 正式質問として扱う理由

- `requirement.md`:
  - Issue 357のAssurance / Profile removalと、Issue 358のsingle-template要件を決める。
- `design.md`:
  - Runtime mechanismとAuthoring policyの境界、historical read compatibilityを決める。
- `plan.md`:
  - profile routing削除、Template再構成、I4のobsolete asset prune順を決める。
- chat上の軽微な一問では足りない理由:
  - 両Issueの並行可否と同時編集面を左右し、未回答のままではRuntimeとTemplateのTarget contractを固定できない。

## 質問の目的

- 対象者:
  - SpecDockのProduct Ownerであるユーザー。
- 何を明確にする質問か:
  - 新規作成SurfaceからIssue Grade / Profile selection / Assurance stateを完全に除去するか。
- 回答が後続判断へ与える影響:
  - Issue 357のAssurance store / profile loader削除と、Issue 358の単一Template化を同時に確定する。

## 質問

- pressure-test question:
  - Profileを残す場合、その選択authorityをどこに置けば、除去対象のPolicy stateをStorage Coreへ再導入せずに済むか。
- 質問:
  - 新しいAuthoring Kitでは、Issueの`design.md`と`plan.md`を`lite / standard / strict / critical`のprofile別Templateから各一種類のmodel-neutral Templateへ統一し、それに伴って`.assurance.json`、`authorized_profile`、`draft-design` / `draft-plan`のprofile routingを新規作成Surfaceから完全に外しますか？
- 回答してほしいこと:
  - 「完全に外す」か「残す」か。残す場合は、Profileを選ぶ新しいauthorityも指定してほしい。

## source-grounded context

- 現行Runtimeでは、`draft-design` / `draft-plan`がvalidな`.assurance.json`、`authorized_profile`、`templates/issue-profiles/<profile>/`を要求する。
- 現行Issue TemplateとDocsはGrade / Reviewer / EAL / Promotionを前提としている。
- 親EpicはStorage CoreからAssuranceと認知的Workflowを外し、Authoring Kitをprovider-neutralにする方向を示している。
- Existing `.assurance.json`、profile別文書、`draft-*` ArtifactはHistorical Evidenceとして保持できるため、新規Surfaceからの除去と既存データ削除は別判断である。
- 技術調査だけではProductとしてProfileを残す価値判断を確定できないため、人間判断が必要である。

## 回答案

- Option A — 新規Surfaceから完全に外す:
  - Scopeごとに単一Templateを提供する。
  - Existing `.assurance.json`、profile別文書、`draft-*` Artifactは自動削除・書換えせずHistorical Evidenceとして保持する。
  - Obsolete managed templateの実PruneはIssue 360で行う。
- Option B — Profileを残す:
  - CLI flag、node metadata、user config、classification command、Agent判断など、新しい選択authorityが必要になる。
  - Issue 357 / 358の責務境界を再設計する必要がある。
- Option C — 判断を延期する:
  - RuntimeとTemplateの共有契約を固定できないため、両Issueの具体化・並行実装を止める。

## Codex の分析

- 判断軸:
  - Storage Coreのprovider neutrality、state最小化、historical data preservation、並行作業の非衝突性。
- tradeoff:
  - Option Aは新規Surfaceを単純化する一方、旧profileによる作成補助は提供しない。Option Bはprofile機能を維持できるが、新authorityとstateをCoreまたは周辺へ再導入する。
- リスク:
  - Option AでHistorical fileまで削除するとdata compatibilityを壊すため、新規作成Surfaceの除去と既存Evidenceの保持を明確に分離する必要がある。
- 具体シナリオ / edge case:
  - Existing consumerに`.assurance.json`と`draft-design`が残っていても、update後のvalidateが失敗せず、Fresh Issueだけが単一Templateを使う。

## Codex の推奨案

- 推奨:
  - Option A。新規Surfaceから完全に外し、Existing dataはHistorical Evidenceとして保持する。
- 理由:
  - 元のChatGPTスレッドのClarificationとローカル実装調査が一致しており、Profileを残すと削除対象のPolicy authorityを別形式で再導入する必要がある。
- 未回答時の影響:
  - Issue 357はAssurance Runtimeの削除範囲を確定できず、Issue 358はTemplate Catalogを確定できない。

## ユーザー回答

- answer capture:
  - Runtime上のProfile / Assurance / routingは完全に外す。
  - Workflow的な複雑な仕組みは取り入れない。
  - 一方、Issueのlevelごとに「作業完了時のあるべき状態・達成するゴール」は異なるため、Plan作成を支援する文書は`light`、`standard`、`strict`、`critical`別に複数用意したい。
  - これらはRuntimeが分類・選択・強制するTemplate routingではなく、各levelに応じた作業の進め方とPlanの完成基準を示すAuthoring documentとして扱いたい。
  - 具体的な対応方法とbest practiceは、元のChatGPTスレッドのChatGPT Proへ提案を依頼する。
- 回答:
  - Profile / Assurance / `draft-*` routingを新規作成Surfaceから完全に外す。
  - 単一のPlan guideへ統合する部分は採用せず、非実行型・非強制型のlevel別Plan authoring documentsを検討する。
- 回答日時:
  - 2026-08-08

## 追加確認の要否

- 追加確認が必要か:
  - yes
- 必要な場合に次の unanswered `interview` として切り出す質問:
  - ChatGPTの提案を受け、level別文書を「別Template」「一つのGuide内のVariant」「共通Base + level別Completion Profile」のどれにするか判断する。

## 採用判断

- adoption_status:
  - partially_adopted
- adoption target:
  - Issue 357 / 358のRequirement / Design / Plan候補。
- 採用 / 棄却 / deferred の理由:
  - RuntimeからProfile / Assurance / routingを除去し、Historical Evidenceだけを保持する提案は採用する。
  - `design.md`と`plan.md`を各一種類のTemplateへ統一する提案のうち、Plan authoring guidanceまで単一化する部分は採用しない。
  - level別文書の最適な構成はChatGPTの提案をEvidenceとして受けてから確定する。
- `report.md` Evidence Adoption Ledger への反映要否:
  - 旧EALを必須化せず、Canonical docsへ採用した時点で通常のreflection evidenceを残す。

## requirement / design / plan / ADR への含意

- `requirement.md`:
  - Runtime Profile / Assurance / `draft-*` routingの廃止とHistorical Evidence保持を明記する。
  - level別Plan authoring documentsはWorkflow stateやRuntime gateではないことを明記する。
- `design.md`:
  - Runtime routingとAuthoring guidanceを分離し、levelは文書上の選択可能なcompletion profileとして設計する候補を検討する。
  - Historical read compatibilityを維持する。
- `plan.md`:
  - I1はRuntime mechanismを除去し、I2はlevel別Plan authoring guidanceを定義し、I4はobsolete managed assetsをPruneする順序を固定する。
- `ADR`:
  - level別文書構造が長期契約になる場合、ChatGPT提案後にADR要否を判定する。
- reflected_to 更新方針:
  - ChatGPT提案とユーザーの後続判断をCanonical docsへ採用した時点で更新する。
- adoption reflection:
  - 現時点ではInterview Artifactへの回答記録のみ。Canonical docsには未反映。
