---
種別: ADR（Architecture Decision Record）
ID: "20260728t100038z-adr"
タイトル: "Generic Imported File Identity And Privacy Boundary"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-28"
親: ["epic-00343"]
authority: "accepted"
accepted_authority: "accepted ADR"
accepted_at: "2026-07-28"
accepted_by: "user (product contract); main orchestrator (architecture contract)"
mirror_eligible: true
derived_from:
  - "epic-00312/artifacts/20260728t060417z-interview-generic-file-import-filename-contract.md"
  - "epic-00312/artifacts/20260728t060706z-interview-external-file-import-policy.md"
  - "epic-00343/artifacts/20260728t083918z-disc-epic-00343-workbench-file-import-architecture-draft.md"
reflected_to:
  - "epic-00343/requirement.md"
  - "epic-00343/design.md"
  - "epic-00343/plan.md"
  - "epic-00343/report.md"
---

# 20260728t100038z-adr Generic Imported File Identity And Privacy Boundary

## ADR 化基準

- hard to reverse: yes。filenameとCLI resultはtracked repositoryおよび利用者scriptに残るpublic contractである。
- surprising without context: yes。original basenameが`adr-*.md`でもtyped ADRではなく、external sourceのhash / byte countも通常outputへ出さない。
- real tradeoff: yes。既存typed grammarとの統合や豊富なprovenanceより、semantic isolation、original basename保持、privacyを優先する。

## 結論（Decision）

次の契約を一体のpublic boundaryとして採用する。項目1〜7のproduct contractは、ユーザーがfilename Option Aおよびexternal-file policyのinterviewで明示した判断と、その判断を正本化したfresh-reviewed requirementに基づく。項目8のarchitecture contractは、同requirementのno-overwrite / observable stateを満たすためmain orchestratorが設計し、fresh spec-reviewで検証する判断であり、ユーザーがfilesystem primitiveを直接選択したという意味ではない。

1. generic imported-file filenameは標準`<timestamp>--<safe-original-basename>`、collision時`<timestamp>-<nn>--<safe-original-basename>`とする。
2. `--`はgeneric imported-file familyとtyped / blank Markdown Artifact grammarを分離するdelimiterであり、typed `file` tokenではない。
3. stable public identityはfull destination basenameとし、timestamp / optional suffix slotはtyped / blank / genericの全familyで共有する。
4. normalizerはpath safetyとcomponent lengthに必要な最小変更だけを行い、title / slug / MIME / contentからfilenameを生成しない。
5. explicit source pathは指定file一件を読むauthorizationである。repository外sourceに追加allow flagを要求しない。
6. external sourceのuser-visible outputとtracked provenanceはbasenameだけを許し、absolute path、parent component、body、hash、byte countその他content-derived valueを出さない。
7. generic importはcanonical docs、report、ADR、assuranceを変更せず、generic `.md`をtyped Artifact / ADRとしてsemantic parseしない。
8. Architecture decision: FD-bound no-replace publicationの成功を唯一のcommit pointとする。commit前failureは`not_committed`、commit後のdurability / owned-temp cleanup warningは`committed_with_warning`かつretry不要とする。

## 背景（Context）

現行`artifact import chatgpt-output`はWorkbench内のlowercase `.md`をblank Artifactへ取り込む専用経路であり、任意fileのimport契約ではない。generic importへそのtitle / slug / Markdown semanticsを拡張すると、original filenameの喪失、typed ADR誤認、binary decode、external path漏洩、warning後の重複retryが起き得る。

このため、user-approved filename Option Aとexternal-file policyを、実装Issueごとに再解釈されない長期contractとして分離する。

## 選択肢（Options considered）

### Option A: 独立generic familyとprivacy-safe resultを採用

- Pros:
  - original basename / extensionを最大限保持できる。
  - typed Artifact / ADR discoveryから決定的に分離できる。
  - external sourceをrepository provenanceへ漏らさない。
  - callerがcommit済みwarningを機械判定し、重複importを避けられる。
- Cons:
  - 新しいfilename parserと全family共通slot ledgerが必要。
  - hash / byte countを通常outputで利用できない。
  - `--` delimiterとfull-basename identityがpublic contractとして固定される。

### Option B: existing typed / blank grammarと`chatgpt-output` resultを再利用

- Pros:
  - 新しいgrammarとresult objectが少なく見える。
  - 既存Markdown flowの部品を直接流用できる。
- Cons:
  - title / slugまたはtyped `file` tokenが必要になり、ユーザーが選んだoriginal basename中心の契約に反する。
  - `adr-*.md`等をsemantic documentとして誤認し得る。
  - external pathやcontent-derived metadataを既存resultから安全に除く責務が曖昧になる。
- Decision: rejected。

### Option C: persistent import catalogでsource-kindとidentityを管理

- Pros:
  - import provenanceとidentityを別metadataへ豊富に保持できる。
- Cons:
  - user-requested single-file copyを越えるstate / migration / privacy surfaceを増やす。
  - source locationをtracked metadataへ残す誘因が強い。
- Decision: rejected。

## 判断理由（Rationale）

primary objectiveは、Workbench専用Markdown flowではなく、利用者が明示した任意の一fileをroot / Initiative / Epic / Issue Artifactへ安全に保存できることである。独立delimiter、full-basename identity、opaque lifecycle、external basename-only visibilityを一体で採用すると、この価値を既存typed authorityと混同せずに実現できる。

commit stateはfilename / identityと同様にcaller-visible contractである。commit後warningをfailureへ落とすと同じsourceの再実行が別identityを生成するため、単一commit pointとretry dispositionも本ADRに含める。

## 影響（Consequences）

- Positive:
  - text / binary / invalid UTF-8を同じopaque byte contractで扱える。
  - typed ADR mirror、default discovery、dependency/context生成がgeneric bodyを読まない。
  - external sourceのlocationとcontent-derived metadataを標準outputから隔離できる。
- Negative / Debt:
  - generic parser、minimal normalizer、cross-family slot ledger、privacy-safe resultの維持が必要。
  - future format変更は既存tracked filenameとcaller contractを考慮するmigrationが必要。
  - observabilityのためのhash / byte countはinternal verification / test evidenceに限定される。
- Migration:
  - existing typed / blank Artifactと`chatgpt-output` contractは変更しない。
  - existing fileをrenameせず、new generic importから新familyを使用する。
- Rollback:
  - implementation rollout前はこのADRとEpic docsを再reviewして変更できる。
  - rollout後に機能を無効化しても既存generic Artifact filenameをgrandfathered evidenceとして保持し、自動rename / deleteしない。

## 参考（References）

- `epic-00343/requirement.md`: E-RQ-010〜020、E-AC-009〜018
- `epic-00343/design.md`: D-004〜D-009
- `epic-00343/report.md`: EAL-002、EAL-003、EAL-016
- 旧Epicのuser interviews:
  - `20260728t060417z-interview-generic-file-import-filename-contract.md`
  - `20260728t060706z-interview-external-file-import-policy.md`
