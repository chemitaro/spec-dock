---
種別: artifact
ID: "20260730t120701z-01"
タイトル: "PR 351 Required CI Repair ChatGPT Consultation"
状態: "archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
template: "blank"
authority: "advisory"
derived_from:
  - "PR #351 Provider CI run 30540472689, job 90863805552"
  - "ChatGPT session iss00334-pr351-ci-repair-consult"
reflected_to:
  - "20260730t115808z-pr-repair-batch-pr-351-repair-batch.md"
  - "20260730t120701z-disc-pr-repair-unit-active-pointer-fixture.md"
---

# 20260730t120701z-01 PR 351 Required CI Repair ChatGPT Consultation

## 位置づけ
- 用途: 型を先に決めず、scope-local `artifacts/` に作業用 evidence を置く。
- `blank` は template identity であり、filename token ではありません。filename は `<ts>-<slug>.md` / same-second collision は `<ts>-<nn>-<slug>.md` を使い、`blank` を含める必要はありません。
- canonical `requirement.md` / `design.md` / `plan.md` / `report.md` の代替ではありません。採用する内容は canonical docs、accepted ADR、または `report.md` Evidence Adoption Ledger へ反映します。

## メモ (必須)
- bound repository: `chemitaro/spec-dock`
- bound branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- bound HEAD: `555dafd6f9e1252ddf8b50cb23c275e20c263266`
- model selection evidence: `requested=Pro`, `resolved=Pro`, `verified=yes`
- ChatGPTはdefault branchを検査せず、指定branch／HEAD／PR #351を確認した。
- 対象はRequired CIの単一failureだけに限定し、Oracle local configuration boundaryを再検討しないよう明示した。

## 整理メモ（任意）
- facts:
  - `test_s10_current_v4_guide_satisfies_completeness_contract`はGit管理外の`spec-dock/active/issue` symlink経由でZIPを開く。
  - GitHub Actionsのfresh checkoutはそのpathを持たず、`FileNotFoundError`となった。
  - 同一ZIPは対象Issueのcanonical artifact pathでtracked Git blobとして存在する。
  - Required pytest laneの結果は`1 failed, 1140 passed, 2119 skipped`だった。
- questions:
  - root causeは十分に支持されるか。
  - one-test fixture path修正が最小の正しい修復か。
  - 必要な検証と具体的な回帰リスクは何か。
- decisions:
  - ChatGPTはroot causeをhigh confidenceで支持した。
  - 対象テストのfixture pathだけをtracked canonical Issue artifactへ変更することを推奨した。
  - product runtime、Oracle invocation/configuration、CI setup、ZIP bytes、canonical planning docs、新規abstractionの変更は不要とした。
- actions:
  - exact test、test module、ordinary `uv run pytest`の順で検証する。
  - repository quality gateとして`make lint`、SpecDock validate、fresh PR observationも実行する。
- links:
  - `tests/unit/domain/test_issue_planning_candidate.py`
  - `20260730t115808z-pr-repair-batch-pr-351-repair-batch.md`
- discard condition:
  - source HEAD、failed check、fixture identityのいずれかが変わった場合、この相談結果を新しい修復判断へ流用しない。
