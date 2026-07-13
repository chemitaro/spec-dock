---
種別: 要件定義書（Issue）
ID: "iss-00315"
タイトル: "Experimental Workbench Ignore And Opaque Traversal Foundation"
関連GitHub: ["#315"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312", "init-local-00003"]
---

# iss-00315 Experimental Workbench Ignore And Opaque Traversal Foundation — Issue 要件定義

## 目的
- Git-ignored、non-canonical、disposableな`.workbench/`を、SpecDock default semantic discoveryが内部まで読まないreserved boundaryとして成立させる。
- 後続Issue 316/317がcopy/importを追加する前に、scratch contentがnode、ADR、dependency、context、authoring sourceとして誤解釈されないfoundationを提供する。

## 親trace
- Epic requirements: E-RQ-001–005、E-RQ-013、E-RQ-015、E-RQ-017–018。
- Epic acceptance: E-AC-001–002、E-AC-010、E-AC-011のupdate-preservation foundation。
- Epic design: DS-001 Ignore and opaque traversal foundation。
- 継承する不変条件:
  - Provider authorityは`src/spec_dock/assets/spec_dock/**`。Dogfood `spec-dock/**`はinstalled verification surface。
  - `.workbench/`はnode、canonical state、durable evidence、review/readiness authorityではない。
  - RuntimeはWorkbench lifecycle、TTL、catalog、promotion、secret/content classificationを管理しない。

## 観測可能な成果
- Root、Initiative、Epic、Issue direct-child `.workbench/`内fileがrepository managed `.gitignore`でignoredになる。
- Default semantic discoveryはpath componentがexactly `.workbench`のdirectory内部を列挙、stat、read、parse、hashしない。
- `.workbench-notes`、`my.workbench`等の非exact nameは通常pathとして扱われる。
- Workbench内の偽/壊れた`.meta.json`、legacy `meta.json`、ADR/dependency/source-like content、unreadable/large descendantはvalidate/sync/deps/context/source manifest結果へ影響しない。
- Workbench外のmalformed metadataは従来どおりfailし、general validationを緩和しない。
- Authoring semantic sourceとしてexact `.workbench` file/directoryまたはそのdescendantを指定した場合、内容を読む前に安定errorで拒否する。
- Scope delete/worktree removeはnonempty Workbenchの存在をblockerにせず、scope/worktreeとともに削除できる。
- `spec-dock update`は既存root/scoped Workbench bytesとnested contentを保持する。

## Issue要件
- RQ-315-001 Ignore placement:
  - Provider `.gitignore` assetとinstaller fallbackは、`spec-dock/`以下のexact `.workbench/` directoryを全supported placementでignoreする。
- RQ-315-002 Opaque exact-component boundary:
  - Default semantic discoveryはexact path component `.workbench`でsubtreeをpruneし、内部entryをsemantic inputへ含めない。
  - Substring/extension-like nameには適用しない。
- RQ-315-003 Discovery inventory:
  - Recursive callsiteを`default-semantic-discovery`、`explicit-user-operation`、`generated-known-tree`へ分類し、前者だけを変更対象とする。
  - 全`rglob`/directory walkを一律置換しない。
- RQ-315-004 Node/graph isolation:
  - Current/legacy node metadata discoveryとそれに依存するvalidate/sync/deps/active/context graphはWorkbench contentを読まない。
- RQ-315-005 Independent resolver isolation:
  - Common node readerを迂回するinstaller recovery、delete fallback、delegated-authoring scope resolution等のdefault semantic resolverも同じopaque contractを守る。
- RQ-315-006 Authoring source isolation:
  - Authoring source preflightとmanifest builderの双方で、exact Workbench file/dir/descendantをreject/pruneし、blocker収集後のmanifest readへ進ませない。
- RQ-315-007 Explicit operation preservation:
  - Node subtree delete、worktree remove、template scaffold、ZIP/pack explicit tree、通常filesystem operation等の明示操作を、default semantic discovery helperへ機械的に置換しない。
- RQ-315-008 Delete/remove no blocker:
  - Workbench存在をscope delete/worktree removeの新blockerにせず、backup/promotionを要求しない。
- RQ-315-009 Update preservation/parity:
  - Installer updateはexisting Workbench contentを変更せず、provider runtime/assets更新をdogfood/consumerへ配布する。
- RQ-315-010 Scope discipline:
  - Workbench copy command、Artifact import、workflow/skill preservation、TTL/catalog/secret scanは変更しない。

## 受け入れ条件
- AC-315-001 Git ignore matrix:
  - Root/Initiative/Epic/Issue `.workbench/probe`が`git check-ignore`でignored、near-nameは意図せずreserved扱いされない。
- AC-315-002 Node metadata opacity:
  - Workbench内fake current/legacy metadata、duplicate-looking IDs、malformed JSONがnode records/validate/sync/depsへ入らず、外部malformed metadataは従来どおりfailする。
- AC-315-003 No descendant access:
  - Large/unreadable/broken descendantsを持つWorkbenchでもdefault discoveryがdescendantをstat/readせず、result/error/processing対象が増えない。
- AC-315-004 Independent resolver parity:
  - Installer recovery、delete fallback、delegated scope resolutionがWorkbench metadataを候補にしない。
- AC-315-005 Authoring source rejection:
  - Exact Workbench file/dir/descendant inputはstable blockerでpublish/manifest generation前にfailし、parent directory selectionではWorkbench subtreeをhashしない。
- AC-315-006 Explicit operations unchanged:
  - Existing delete/remove/template/ZIP/pack explicit operationsのcontract regressionがない。
- AC-315-007 Disposable deletion:
  - Nonempty Workbenchを持つscope/worktreeを既存明示delete/remove contractで処理でき、Workbench専用blocker/promotionがない。
- AC-315-008 Update preservation:
  - Fresh init/update後にignore/opaque foundationが配布され、existing root/scoped sentinel bytes/nested filesが保持される。
- AC-315-009 Provider/dogfood authority:
  - Implementationはprovider側を正本とし、dogfood projectionはdocumented generated差分以外でparityを満たす。

## 非機能・安全性
- Default discoveryの処理量はWorkbench descendant数/sizeに比例しない。
- Workbench body/secret-like contentをlog/errorへ出さない。
- New third-party dependency、persistent catalog、schema migrationを追加しない。
- Existing public CLI/node/artifact contractsを変更しない。

## スコープ
- 必須:
  - Provider `.gitignore`/fallback、default discovery runtime/installer callsites、authoring source manifest、focused tests、update preservation/parity evidence。
- 対象外:
  - Issue 316 scoped copy、Issue 317 Artifact import、Issue 318 workflow/skills、Issue 319 final PR delivery。

## Evidence / authority
- Raw planning evidence:
  - `artifacts/20260713t044108z-research-chatgpt-5-6-pro-issue-planning-evidence.md`（SHA-256 `6080fe2c3e75060eb3a31f9b5014bf5fdd96d9bdd8a68352e5cf2f6b71ddbac7`）。
- Canonical authority:
  - 本requirement、reviewed design/plan、parent Epic/accepted ADR。
- ChatGPT evidenceの採否とreviewer verdictは`report.md` EAL/Spec Authoring Gateへ記録する。

## 未確定事項
- Product/parent boundaryを変更する未確定事項はない。
- Exact helper/module/error token/test function nameはdesign/plan local deltaとする。
