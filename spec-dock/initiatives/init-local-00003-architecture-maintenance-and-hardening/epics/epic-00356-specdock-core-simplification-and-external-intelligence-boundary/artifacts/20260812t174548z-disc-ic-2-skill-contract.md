---
種別: disc
ID: "20260812t174548z-disc"
タイトル: "IC-2 Skill Contract"
状態: "complete"
作成者: "Codex main orchestrator"
最終更新: "2026-08-13"
親: ["epic-00356"]
template: "disc"
authority: "evidence"
derived_from:
  - "../plan.md"
  - "../issues/iss-00359-replace-managed-workflow-skills-with-specdock-skills/report.md"
reflected_to: ["../report.md"]
---

# 20260812t174548z-disc IC-2 Skill Contract

Epic Plan §6.1のIC-2実行契約に従い、Issue 359が提供する二つのrepo-local skill、Current guide link、external capability欠如時のzero-write、legacy removal handoffを統合確認した証拠である。これはRuntime gateや新しい正本ではなく、Issue 359 ownerの入力をEpic main orchestratorが文書上で判定したものである。

## Inputs

- Epic Plan §6 / §6.1のIC-2 entry、verification、evidence destination、pass / fail transition。
- Issue 359 `requirement.md` / `design.md` / `plan.md` / `report.md`とPR #363。
  - head `948d0cf0dedb84ca34e51a4adc0995820aa011f6`
  - merge `a6ded0d9a838b40cdcd741fa473cd264b801f245`
  - GitHub state `MERGED`、`validate` 2件と`provider-tests` 1件が`SUCCESS`
- Current main `a6ded0d9a838b40cdcd741fa473cd264b801f245`上で2026-08-13に再実行した検証。
  - `uv run pytest --run-full-regression tests/unit/infra/test_init_update.py -q -k issue_359`: `11 passed, 575 deselected`
  - `uv run pytest tests/unit/infra/test_issue_359_skill_helpers.py -q`: `9 passed`
  - `uv run pytest --run-full-regression tests/cli_runtime/test_new.py -q -k issue_359`: `7 passed, 43 deselected`
- Issue 359 report §7〜§9のprovider / dogfood byte parity、exact skill inventory、Current docs pointer、legacy handoff inventory。

## Synthesis

- Current managed skillは`.agents/skills/spec-dock/**`と`.agents/skills/spec-dock-grill-with-docs/**`の二treeで、provider / dogfood bytesが一致する。
- `spec-dock` skillはread-only / present-only / forbidden operationを区別し、canonical R/D/P/ReportやGit / GitHubを自動変更しない。
- `spec-dock-grill-with-docs`はimplicit invocationを禁止し、explicit selector、四route、title、`grilling` / `domain-modeling`の両capabilityを必須入力とする。
- External capabilityが欠ける、入力が曖昧、preflightが失敗する場合はArtifact CLIを呼ばずzero-writeとなる。
- 成功時はCLIが作成した一つのArtifactだけをidentity-pinned finalizerで確定し、canonical scope、metadata、active / deps stateを変更しない。
- Current docsは二skill、Authoring overview、Artifact guide、CLI helpへ到達する。
- Issue 360へ渡すobsolete inventoryは旧managed 18 skill + legacy 3 skillであり、Issue 359ではpruneしていない。
- この確認で未確定のIC-2項目はない。

## Options and trade-offs

- **採用: pass。** 二skill contract、guide link、missing-capability zero-write、exactly-one Artifact、legacy removal inventoryがIssue 359 reportとfresh testで一致する。
- Issue 359の`I359-AC-017`にある「IC-2 passは未宣言」をIssue 359自身のself-approvalへ書き換える案は採用しない。本ArtifactとEpic reportでEpic main orchestratorが判定する。
- 旧skillを新skillへのcompatibility wrapperとして残す案は、Issue 360のhard cutover contractに反するため採用しない。
- Pass transitionとしてIC-2をclosedにし、Issue 360の文書上のimplementation handoffを許可する。Formal `issue start`とreviewは別gateである。

## Reflection

- Verdict: `pass`。
- Epic `report.md`へ本Artifact、exact source identity、fresh test結果、pass transitionを反映する。
- Issue 360は旧18 + legacy 3 skill、adapter / shim / config / agent-driven workflowをownership evidenceに従い移行し、二skillのsemantic contractを再設計しない。
- 本Artifactはevidenceであり、Issue 360のRequirement / Design / Planと親Epic Planがdurable authorityである。
