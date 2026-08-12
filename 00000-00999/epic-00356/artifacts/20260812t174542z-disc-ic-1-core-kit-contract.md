---
種別: disc
ID: "20260812t174542z-disc"
タイトル: "IC-1 Core Kit Contract"
状態: "complete"
作成者: "Codex main orchestrator"
最終更新: "2026-08-13"
親: ["epic-00356"]
template: "disc"
authority: "evidence"
derived_from:
  - "../plan.md"
  - "../issues/iss-00357-reduce-runtime-to-storage-core/report.md"
  - "../issues/iss-00358-simplify-authoring-kit-and-document-contracts/report.md"
reflected_to: ["../report.md"]
---

# 20260812t174542z-disc IC-1 Core Kit Contract

Epic Plan §6.1のIC-1実行契約に従い、Issue 357のStorage CoreとIssue 358のAuthoring Kitが共有するCurrent contractを統合確認した証拠である。これはRuntime gateや新しい正本ではなく、Epic main orchestratorによる文書上のhandoff判定である。

## Inputs

- Epic Plan §6 / §6.1のIC-1 entry、verification、evidence destination、pass / fail transition。
- Issue 357 `requirement.md` / `design.md` / `plan.md` / `report.md`とPR #362。
  - head `55a7e41df93297832f5db2b0c3abb96161355cc9`
  - merge `8e10f255b3377bf879b459380f563729522e22b2`
  - GitHub state `MERGED`、`validate` 2件と`provider-tests` 1件が`SUCCESS`
- Issue 358 `requirement.md` / `design.md` / `plan.md` / `report.md`とPR #361。
  - head `5d1e3a4ccd09b4f6a1f5272107e6100b6f289bef`
  - merge `3e166d4c81e9780ec346e3194c34fc09a2692bf7`
  - GitHub state `MERGED`、`validate` 2件と`provider-tests` 1件が`SUCCESS`
- Issue 359を含むcurrent main `a6ded0d9a838b40cdcd741fa473cd264b801f245`上で2026-08-13に再実行した検証。
  - `uv run pytest --run-full-regression tests/cli_runtime/test_storage_core_cli.py -q`: `4 passed`
  - `uv run pytest tests/unit/infra/test_authoring_kit_assets.py -q -k s09`: `23 passed, 281 deselected`
  - `uv run pytest --run-full-regression tests/cli_runtime/test_new.py::TestCliNew::test_new_issue_creates_thin_design_and_plan_templates_without_assurance_contract tests/cli_runtime/test_new.py::TestCliNew::test_new_artifact_blank_issue_omits_blank_token_and_uses_artifacts_dir tests/cli_runtime/test_new.py::TestCliNew::test_new_artifact_full_direct_catalog_success -q`: `3 passed`

## Synthesis

- Fresh Initiative / Epic / Issueはそれぞれ一つの`requirement.md`、`design.md`、`plan.md`、thin `report.md`を生成し、`.assurance.json`を新規作成しない。
- Reportはrequired headingだけを持つ空でも有効な記録であり、実行可否の機械gateではない。
- Current Artifact catalogは`blank`、`research`、`interview`、`disc`、`decision-candidate`、`adr`の六種である。type省略は`blank`として扱われ、Issue Planは一つだけである。
- Base Guideと四Completion Guideが存在し、Planning Levelはdocs-onlyでRuntime metadata / parser / Assuranceへ結合しない。
- Providerとdogfoodのowned Authoring Kit assetはbyte parityを満たす。
- Content / Guide / heading mismatchはIssue 358、copy / parser / filename / Runtime mismatchはdownstream Runtime ownerへ返す契約が固定されている。
- 共有workflow state machineを再導入する必要はない。
- この確認で未確定のIC-1項目はない。

## Options and trade-offs

- **採用: pass。** PRのmerge/check結果、Issue report、Current main上のFresh node・Report・Artifact catalog・optional type・guide path・provider/dogfood fixture testがすべて一致する。
- Artifactを作らずIssue 357 / 358 reportだけを暗黙handoffに使う案は、Epic Planのevidence destinationを満たさないため採用しない。
- Issue 359の実装済み事実をIC-1の事前承認だったと遡及表現しない。本Artifactは2026-08-13時点のformal checkpoint記録である。
- Pass transitionとしてIC-1をclosedにし、Issue 360の親gate入力として利用できる。Runtime dependency readinessの意味は変更しない。

## Reflection

- Verdict: `pass`。
- Epic `report.md`へ本Artifact、exact source identity、fresh test結果、pass transitionを反映する。
- Issue 360はIC-1単独では開始せず、IC-2、direct dependency、formal `issue start`、R/D/P reviewを別gateとして確認する。
- 本Artifactはevidenceであり、Issue 360のRequirement / Design / Planと親Epic Planがdurable authorityである。
