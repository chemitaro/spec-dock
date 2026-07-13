---
種別: ADR
ID: "adr-20260713t031808z-template-free-artifact-import-and-blank-filename-coexistence"
タイトル: "Template Free Artifact Import And Blank Filename Coexistence"
状態: "accepted"
authority: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["epic-00312", "init-local-00003"]
extends:
  - "adr-20260701t072851z-artifact-domain-filename-template-contract"
---

# ADR: Template-free Artifact import and blank filename coexistence

## Status
Accepted. Refreshed canonical requirementと本ADRはfresh `spec-reviewer` passで整合確認済み。

## Context
Epic 00259のaccepted ADRはArtifact catalog、typed/blank filename grammar、`new artifact` template routingを固定した。ChatGPT Firstでは、完成済みMarkdown reportをCodexが要約・再構成する前に、原文bytesを変更せずArtifactへ保存する経路が必要になった。

`chatgpt-output` を新typed filename tokenにすると、従来validなblank slug `chatgpt-output-*` とgrammarが重なる。Product ownerはblank prefixを予約・禁止せず、template-based blank creationとChatGPT output importの両方を許容すると決定した。

## Options
### A. `chatgpt-output`を新typed Artifact tokenにし、blank prefixを予約する
- Pros: filenameだけでtyped recognitionできる。
- Cons: 既存blank input compatibilityを狭め、user decisionに反する。

### B. `chatgpt-output`をimport operation kindとし、保存fileは既存blank filename grammarを使う
- Pros: blank grammar/catalog/template routingを変更せず、予約prefixが不要。Filenameとbytesだけの単純な保存になる。
- Cons: filenameだけではcreation route/provenanceを一意に判定できない。

### C. Frontmatterまたはsidecar receiptでimport provenanceを埋め込む
- Pros: originをmachine-readableにできる。
- Cons: 本文不変契約またはsingle-file MVPに反し、新しいpersistent metadata modelを作る。

## Decision
- Option Bを採用する。
- `chatgpt-output` は `artifact import` commandが受け付けるMVP import kindであり、Artifact filename parserの新typed tokenにはしない。
- Destination basenameは既存blank grammarを使う。
  - standard: `<ts>-chatgpt-output-<slug>.md`
  - collision: `<ts>-<nn>-chatgpt-output-<slug>.md`
  - parser上のartifact identityはblank contractの`<ts>`または`<ts>-<nn>`。
- Existing `new artifact blank --slug chatgpt-output-...`を禁止しない。Import resultとtemplate-created blankはfilenameだけでは区別しない。
- Creation route、source Workbench path、capture boundary、SHA-256、byte count、adoption statusはcommand resultと`report.md` EALへ記録する。本文frontmatter、sidecar、catalog/indexは作らない。
- `new artifact` catalog/template semanticsは変更しない。`new artifact chatgpt-output`は追加しない。
- Importはsingle regular `.md` file、current worktreeのroot/scoped `.workbench/` source、copy-not-move、byte-preserving、no-overwrite、hash verificationに限定する。
- Source bytesはopaqueとして扱い、encoding detection/validation/conversion、Markdown parse/normalizationを行わない。
- Imported fileはevidence-onlyで、filename/contentからauthorityを得ない。

## Consequences
- Epic 00259 ADRのtyped/blank filename grammarとfuture `new artifact` catalogを変更しない。
- `artifact import`というtemplate-free第二作成経路をArtifact contractへ追加する。
- Generic validatorは既存blank filenameとして認識し、frontmatterを要求しない。
- Import provenanceを後から知るにはEALまたはoperation logを参照する。Persistent provenance lookupはMVP non-goal。
- `chatgpt-output`という語はstorage type identityではなくimport intentを表す。User-facing docsはこの区別を明記する。
- 将来machine-readable originやPDF/bundle/capture catalogが必要になった場合は別ADR/Epicで再検討する。

## Rejected Alternatives
- Blank prefix reservation: user decisionとcompatibility維持に反するため棄却。
- New typed token with ambiguous parser precedence: template-created blankをimported typeと誤推定するため棄却。
- Frontmatter injection: byte-preserving contractに反するため棄却。
- Sidecar/receipt Artifact: single-file MVPとno-second-catalog boundaryに反するため棄却。

## Review / adoption gate
- Requirementへoperation/authority/compatibility contractを反映し、fresh `spec-reviewer`で本ADRと整合確認した。
- Designでbinary publication/hash/no-overwriteを固定する。
- Issue nodeはrevised planのfresh reviewとhuman approval後にのみ作成する。
