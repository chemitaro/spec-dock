---
種別: artifact
ID: "20260713t005848z"
タイトル: "User Proposal For ChatGPT Assisted Integrated PR Repair Batch"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00313"]
template: "blank"
authority: "raw"
derived_from: []
reflected_to:
  - "ChatGPT-Use workflow consultation input"
  - "requirement.md authoring input"
  - "design.md authoring input"
  - "plan.md authoring input"
---

# 20260713t005848z User Proposal For ChatGPT Assisted Integrated PR Repair Batch

## 位置づけ
- 用途: 型を先に決めず、scope-local `artifacts/` に作業用 evidence を置く。
- `blank` は template identity であり、filename token ではありません。filename は `<ts>-<slug>.md` / same-second collision は `<ts>-<nn>-<slug>.md` を使い、`blank` を含める必要はありません。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の代替ではありません。採用する内容は canonical docs、accepted ADR、または `report.md` Evidence Adoption Ledger へ反映します。

## メモ (必須)
- 固定修正回数は撤廃するが、無限に修正を繰り返すworkflowにはしない。
- PR reviewが完了したら、観測されたreview情報とcurrent pushed code stateをChatGPT-Useへ共有し、関連findingをまとめた分析を必須workflowとして実行する。
- ChatGPT-Useの分析結果を根拠として、GitHub PR repair batchを作成する。
- 現行のrepair batchはfinding inventoryと外部`disc` repair unitへのroutingが中心だが、これを変更する。
- Review処理のprimary authority surfaceは一つのrepair batchに閉じる。Batch内で問題を記録し、関連findingをroot-cause family等で統合し、分析、設計、実装計画、検証計画、実装結果、commit/push、re-observationまで追跡する。
- Finding一件ごとの個別対応ではなく、関連する複数findingをまとめて原因と契約を分析し、一つ以上のcoherent repair scopeとして設計・計画する。
- `research`や`disc`は補助的な深掘りに必要な場合は利用可能だが、review repair workflowの中心や必須repair unitとしてrepair batch外へ分散させない。
- ChatGPT-Useにはcurrent branchのGitHub codeとreview情報を参照させ、repair batch全体のdraft作成を依頼する案を検討する。
- ChatGPTがMarkdown fileを作成またはダウンロード可能な形で返し、runtime-generated repair-batch pathへ配置・採用するworkflowも検討する。
- ChatGPT出力をcanonical authorityとして無検証採用せず、main orchestratorがruntime生成path、source coverage、local repository facts、scope、安全な変更境界を確認して採用する必要がある。
- この提案全体をChatGPT-Useで一括分析し、推奨workflow、failure mode、変更対象、template構成、fallback、検証方法を相談する。
- ChatGPT分析後もproduct-owner判断が必要な高影響の論点だけ、一問ずつ追加interviewする。

## 整理メモ（任意）
- facts:
  - Current skillは各blocking familyごとに外部`disc` repair unitを作成してからworkerへ委任する。
  - Current repair-batch templateはRaw Intake、family grouping、repair queue、quality gate、re-observation、loop controlを持つが、各repair unitの詳細な分析・設計・計画は外部`disc`へ委譲する。
- questions:
  - ChatGPT-Useはrepair batchのdraft file全体を生成するownerとするか、analysis evidenceを返してorchestratorがbatchへ採用する形にするか。
  - ChatGPT/browser/GitHub connector failure時にrepair workflowを停止するか、local fallback authoringを許可するか。
  - Progress/stagnationをrepair batch内のどの証跡で判定するか。
- decisions:
  - 固定回数上限とsame-family即停止を廃止し、progress-based継続とstagnation human gateを採用する。
  - Repair analysis/design/planのprimary surfaceをrepair batchへ統合する方向で検討する。
- actions:
  - ChatGPT-Useへ現行skill、templates、ADR、research、interview、本artifactを渡して分析する。
  - 分析結果をローカルsourceと照合し、canonical Issue authoringまたは追加interviewへrouteする。
- links:
  - GitHub Issue `#313`
  - `20260713t005118z-research-pr-merge-preparer-repair-limit-clarification-baseline.md`
  - `20260713t005207z-interview-same-family-repair-recurrence-continuation-policy.md`
- discard condition:
  - Canonical requirement/design/planとreport EALへ採用済みになった後、raw sourceとして保持する。
