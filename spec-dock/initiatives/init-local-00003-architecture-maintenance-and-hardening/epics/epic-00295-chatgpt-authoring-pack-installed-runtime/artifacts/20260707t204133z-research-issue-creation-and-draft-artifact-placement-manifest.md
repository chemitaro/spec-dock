---
種別: research
ID: "20260707t204133z-research"
タイトル: "Issue Creation And Draft Artifact Placement Manifest"
状態: "completed"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295"]
関連: ["iss-00296", "iss-00297", "iss-00298", "iss-00299", "iss-00300", "iss-00301", "iss-00302", "iss-00303", "iss-00304", "iss-00305", "iss-00306", "iss-00307"]
authority: "synthesized"
derived_from:
  - "spec-dock active show"
  - "spec-dock validate"
  - "spec-dock/active/epic/plan.md"
  - "spec-dock/active/epic/issues/*/.meta.json"
  - "spec-dock/active/epic/issues/*/artifacts/*draft*.md"
reflected_to:
  - "spec-dock/active/epic/issues/*/artifacts/"
---

# Issue Creation And Draft Artifact Placement Manifest

## 調査目的

`epic-00295` で ChatGPT authoring pack installed runtime を実装するために、SpecDock 上の Issue node が実体化され、各 Issue の draft requirement / draft design / draft plan が Issue-local artifact として配置されていることを確認する。

この artifact は、後続の `spec-dock-epic-execution` と `spec-dock-issue-planning` が、各 Issue の正式な要件定義書・設計書・実装計画書を作成するときのハンドオフ索引として扱う。

## sources / 調査方法

- `./spec-dock/scripts/spec-dock active show` で active Initiative / Epic / Issue を確認した。
- `./spec-dock/scripts/spec-dock validate` で SpecDock tree が valid であることを確認した。
- `spec-dock/active/epic/issues/*/.meta.json` で Issue node の parent、GitHub issue link、依存関係を確認した。
- `spec-dock/active/epic/issues/*/artifacts/*draft*.md` で draft requirement / draft design / draft plan の配置を確認した。

## facts / 観測できた事実

- Active Epic は `epic-00295` である。
- `epic-00295` 配下には `iss-00296` から `iss-00307` までの 12 Issue が SpecDock 管理 node として存在する。
- 各 Issue の `.meta.json` には `parent_id: epic-00295` と GitHub issue number が設定されている。
- 各 Issue の `artifacts/` には、draft requirement / draft design / draft plan の 3 ファイルが配置済みである。
- `./spec-dock/scripts/spec-dock validate` は `spec-dock: ok (validate) nodes=202` を返した。
- `./spec-dock/scripts/spec-dock sync --dry-run` は未対応引数のため実行できなかった。これは Issue node / artifact 配置の妥当性ではなく、`sync` command surface の制約である。

## Issue node / draft artifact placement

| Issue | GitHub | Title | Depends on | Draft requirement | Draft design | Draft plan |
| --- | --- | --- | --- | --- | --- | --- |
| `iss-00296` | `#296` | Authoring Pack Assets | none | `issues/iss-00296-promote-authoring-pack-assets/artifacts/20260707t171106z-draft-requirement-promote-authoring-pack-assets-draft-requirement.md` | `issues/iss-00296-promote-authoring-pack-assets/artifacts/20260707t171234z-draft-design-promote-authoring-pack-assets-draft-design.md` | `issues/iss-00296-promote-authoring-pack-assets/artifacts/20260707t171235z-draft-plan-promote-authoring-pack-assets-draft-plan.md` |
| `iss-00297` | `#297` | Authoring Command Skeleton | `iss-00296` | `issues/iss-00297-add-authoring-command-skeleton/artifacts/20260707t171238z-draft-requirement-add-authoring-command-skeleton-draft-requirement.md` | `issues/iss-00297-add-authoring-command-skeleton/artifacts/20260707t171239z-draft-design-add-authoring-command-skeleton-draft-design.md` | `issues/iss-00297-add-authoring-command-skeleton/artifacts/20260707t171239z-01-draft-plan-add-authoring-command-skeleton-draft-plan.md` |
| `iss-00298` | `#298` | GitHub Sync Preflight | `iss-00297` | `issues/iss-00298-implement-github-sync-preflight/artifacts/20260707t171243z-draft-requirement-implement-github-sync-preflight-draft-requirement.md` | `issues/iss-00298-implement-github-sync-preflight/artifacts/20260707t171243z-01-draft-design-implement-github-sync-preflight-draft-design.md` | `issues/iss-00298-implement-github-sync-preflight/artifacts/20260707t171243z-02-draft-plan-implement-github-sync-preflight-draft-plan.md` |
| `iss-00299` | `#299` | Prompt Pack Constraints | `iss-00298` | `issues/iss-00299-prepare-prompt-pack-and-safe-output-constraints/artifacts/20260707t171246z-draft-requirement-prepare-prompt-pack-and-safe-output-constraints-draft-requirement.md` | `issues/iss-00299-prepare-prompt-pack-and-safe-output-constraints/artifacts/20260707t171247z-draft-design-prepare-prompt-pack-and-safe-output-constraints-draft-design.md` | `issues/iss-00299-prepare-prompt-pack-and-safe-output-constraints/artifacts/20260707t171247z-01-draft-plan-prepare-prompt-pack-and-safe-output-constraints-draft-plan.md` |
| `iss-00300` | `#300` | Backend Invocation Adapter | `iss-00299` | `issues/iss-00300-implement-backend-invocation-adapter/artifacts/20260707t171251z-draft-requirement-implement-backend-invocation-adapter-draft-requirement.md` | `issues/iss-00300-implement-backend-invocation-adapter/artifacts/20260707t171251z-01-draft-design-implement-backend-invocation-adapter-draft-design.md` | `issues/iss-00300-implement-backend-invocation-adapter/artifacts/20260707t171252z-draft-plan-implement-backend-invocation-adapter-draft-plan.md` |
| `iss-00301` | `#301` | Zip Review Staging | `iss-00300` | `issues/iss-00301-promote-zip-review-and-staging/artifacts/20260707t171255z-draft-requirement-promote-zip-review-and-staging-draft-requirement.md` | `issues/iss-00301-promote-zip-review-and-staging/artifacts/20260707t171255z-01-draft-design-promote-zip-review-and-staging-draft-design.md` | `issues/iss-00301-promote-zip-review-and-staging/artifacts/20260707t171256z-draft-plan-promote-zip-review-and-staging-draft-plan.md` |
| `iss-00302` | `#302` | Initiative Epic Validation | `iss-00301` | `issues/iss-00302-validate-initiative-epic-and-epic-issue-candidates/artifacts/20260707t171259z-draft-requirement-validate-initiative-epic-and-epic-issue-candidates-draft-requirement.md` | `issues/iss-00302-validate-initiative-epic-and-epic-issue-candidates/artifacts/20260707t171300z-draft-design-validate-initiative-epic-and-epic-issue-candidates-draft-design.md` | `issues/iss-00302-validate-initiative-epic-and-epic-issue-candidates/artifacts/20260707t171300z-01-draft-plan-validate-initiative-epic-and-epic-issue-candidates-draft-plan.md` |
| `iss-00303` | `#303` | Issue Draft Adoption Validation | `iss-00302` | `issues/iss-00303-validate-issue-draft-adoption-and-selected-skeleton/artifacts/20260707t171303z-draft-requirement-validate-issue-draft-adoption-and-selected-skeleton-draft-requirement.md` | `issues/iss-00303-validate-issue-draft-adoption-and-selected-skeleton/artifacts/20260707t171304z-draft-design-validate-issue-draft-adoption-and-selected-skeleton-draft-design.md` | `issues/iss-00303-validate-issue-draft-adoption-and-selected-skeleton/artifacts/20260707t171304z-01-draft-plan-validate-issue-draft-adoption-and-selected-skeleton-draft-plan.md` |
| `iss-00304` | `#304` | ChatGPT Authoring Skill | `iss-00303` | `issues/iss-00304-add-chatgpt-authoring-skill-and-update-planning-skills/artifacts/20260707t171308z-draft-requirement-add-chatgpt-authoring-skill-and-update-planning-skills-draft-requirement.md` | `issues/iss-00304-add-chatgpt-authoring-skill-and-update-planning-skills/artifacts/20260707t171308z-01-draft-design-add-chatgpt-authoring-skill-and-update-planning-skills-draft-design.md` | `issues/iss-00304-add-chatgpt-authoring-skill-and-update-planning-skills/artifacts/20260707t171309z-draft-plan-add-chatgpt-authoring-skill-and-update-planning-skills-draft-plan.md` |
| `iss-00305` | `#305` | Approval Stop Gate Reports | `iss-00304` | `issues/iss-00305-implement-approval-check-and-stop-gate-reports/artifacts/20260707t171312z-draft-requirement-implement-approval-check-and-stop-gate-reports-draft-requirement.md` | `issues/iss-00305-implement-approval-check-and-stop-gate-reports/artifacts/20260707t171313z-draft-design-implement-approval-check-and-stop-gate-reports-draft-design.md` | `issues/iss-00305-implement-approval-check-and-stop-gate-reports/artifacts/20260707t171313z-01-draft-plan-implement-approval-check-and-stop-gate-reports-draft-plan.md` |
| `iss-00306` | `#306` | Runtime Workflow Guidance | `iss-00305` | `issues/iss-00306-update-runtime-docs-and-workflow-guidance/artifacts/20260707t171317z-draft-requirement-update-runtime-docs-and-workflow-guidance-draft-requirement.md` | `issues/iss-00306-update-runtime-docs-and-workflow-guidance/artifacts/20260707t171317z-01-draft-design-update-runtime-docs-and-workflow-guidance-draft-design.md` | `issues/iss-00306-update-runtime-docs-and-workflow-guidance/artifacts/20260707t171317z-02-draft-plan-update-runtime-docs-and-workflow-guidance-draft-plan.md` |
| `iss-00307` | `#307` | Final Quality Gate PR Delivery | `iss-00306` | `issues/iss-00307-final-quality-gate-and-mergeable-pr-delivery/artifacts/20260707t171321z-draft-requirement-final-quality-gate-and-mergeable-pr-delivery-draft-requirement.md` | `issues/iss-00307-final-quality-gate-and-mergeable-pr-delivery/artifacts/20260707t171321z-01-draft-design-final-quality-gate-and-mergeable-pr-delivery-draft-design.md` | `issues/iss-00307-final-quality-gate-and-mergeable-pr-delivery/artifacts/20260707t171322z-draft-plan-final-quality-gate-and-mergeable-pr-delivery-draft-plan.md` |

## inference / 推測

- これらの draft artifact は、各 Issue を `issue start` した後の `spec-dock-issue-planning` で正式な `requirement.md` / `design.md` / `plan.md` へ採用・修正する入力として扱うのが適切である。
- `iss-00307` は、個別 Issue ごとの PR delivery ではなく、Epic 全体の final quality gate と mergeable PR delivery を担う終端 Issue として扱うのが適切である。

## unverified / 未検証事項

- GitHub 側の各 issue 本文が、このローカル SpecDock node と完全に同じ説明になっているかは、この artifact 作成時点では再同期確認していない。
- 各 draft artifact の内容品質は、この manifest では評価していない。正式採用前に、Issue ごとの planning / spec review で確認する。

## question candidates / 質問候補

- 現時点で追加の人間確認は不要。Issue node と draft artifact の配置は確認済みであり、次の判断ポイントは各 Issue の正式 planning 時である。

## terminology conflicts / 用語衝突

- `draft` は Issue-local artifact の候補仕様を指す。canonical `requirement.md` / `design.md` / `plan.md` の正式採用状態とは区別する。
- `Final Quality Gate PR Delivery` は PR 作成そのものだけではなく、Epic 全体の品質ゲート、手動確認、不具合修正、review / CI repair loop を含む。

## edge cases / 具体シナリオ

- Draft artifact が存在していても、正式 `requirement.md` / `design.md` / `plan.md` に採用されるまでは実装権限を与えない。
- 中間 Issue 完了時には PR を作らず、`issue finish` 後に次 Issue を `issue start` する relay policy を維持する。
- `iss-00307` の前に未検証・未修正事項が残った場合は、`iss-00307` の品質ゲート作業として修正し、mergeable PR delivery まで進める。

## implications / 判断への含意

- 既に SpecDock issue node は作成済みのため、この時点で追加の `spec-dock new issue` は不要である。重複 Issue を作るより、現在の 12 Issue を順番に planning / execution / finish する。
- Draft artifact は canonical docs ではなく evidence surface であるため、後続の Issue planning では Evidence Adoption Ledger に採用根拠を明示する。
- Epic 実行は `iss-00300` 以降を続行し、最終的な PR delivery は `iss-00307` で一括実施する。

## 反映先

- `spec-dock/active/epic/issues/*/artifacts/`
- 後続の各 Issue `report.md` Evidence Adoption Ledger
