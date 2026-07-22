---
種別: ADR（Architecture Decision Record）
ID: "20260721t124850z-16-adr"
artifact_type: "adr"
タイトル: "Runtime-valid Node materialization、scaffold replacement、Artifact disposition、publication evidenceを一つの契約へ統合する"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-21"
親: ["init-00322"]
authority: "accepted"
accepted_authority: "Human direction in the init-00322 planning discussion"
accepted_at: "2026-07-21"
accepted_by: "Human"
mirror_eligible: true
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260721t124850z-16-adr-runtime-valid-portfolio-materialization-and-publication.md"
derived_from:
  - "Candidate v7 independent Red-Team Formal Review"
  - "Exact source Runtime title, create, template, and Artifact identity contracts"
reflected_to:
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "NODE-MATERIALIZATION-MAP.json"
  - "EPIC-SCAFFOLD-REPLACEMENT-MAP.json"
  - "ARTIFACT-MATERIALIZATION-MAP.json"
  - "PUBLICATION-EVIDENCE-CONTRACT.md"
---

# Runtime-valid Portfolio materializationとpublication evidenceを一つの契約へ統合する

## 位置づけ

Candidate v7は、既存Initiative三文書のsource-baseline-bound replacementを定義したが、新Node入力、Runtime-created Epic scaffold、Artifact identity／disposition、Epic canonical identity、report publication evidenceの境界が別々であり、完全なmaterialization terminal stateを形成できなかった。

## ADR 化基準

- hard to reverse: yes。Node identity、canonical文書、Artifact、report、Git publicationの全境界へ影響する。
- surprising without context: yes。GitHub Issue作成とlocal scaffoldが非原子的であり、Candidate exact bytesをそのままcopyできない。
- real tradeoff: yes。厳密なpreflight／render／parityを追加する代わりに、破壊的migration後の停止、重複Node、authority lossを防ぐ。

## 結論（Decision）

1. 新3 Epic／7 Issueの全10 Node title／slug／parentを`NODE-MATERIALIZATION-MAP.json`で固定し、旧Portfolio退役前のC0でexact source Runtimeのpure validatorへ通す。invalid inputはCandidate identityの欠陥であり、materialization中に修正しない。
2. `new epic`が生成する`requirement.md`／`design.md`／`plan.md`／`report.md`をexact source templateとactual bindingから再renderし、`runtime-scaffold-exact`を確認する。
3. Candidate Epic三文書はNode binding placeholderを持つreviewable templateとし、actual Epic ID／GitHub Issue／parent／canonical path／actor／dateだけを決定的にrenderする。semantic本文の再執筆を禁止する。
4. Epic canonical三文書は`runtime-scaffold-exact → replacement-exact`だけを許可し、fixed-order atomic replace、actual-byte resume、verified scaffold rollbackを行う。Runtime-created`report.md`、`.meta.json`、rules linksを上書きしない。
5. 全Artifact filenameをsource Runtimeの`<timestamp>[-NN]-<type>-<slug>.md`契約へ正規化し、filename-derived ID／typeとfront matterを一致させる。
6. 全Initiative／Epic Artifactについてcanonical destinationまたは`package-only-non-authoritative`をfile単位で宣言し、source state、candidate template identity、placement／resume／rollback、final parity、report adoption dispositionを固定する。
7. Initiative `report.md`はpre-commit dispositionだけを一度appendする。observed commit／push／remote verification evidenceはGit commit object、push result、remote ref、Candidate-SHA-bound Workbench ledgerをauthorityとし、未来のpublication成功をreportへ事前記入しない。
8. Formal ReviewとHuman Approvalは完全なCandidate ZIP SHAへbindし、上記map／contractのどれかが検証不能ならmaterializationを開始しない。

## 背景（Context）

source RuntimeはCLI input titleをASCII英数字token＋single spaceへ制限し、GitHub Issue作成前にvalidateする。`new epic`はtemplate treeと`.meta.json`を作成するため、Candidate Epic Bundle placement時のdestinationはabsentではない。Artifact identityはfront matterではなくfilenameから導出される。したがって、抽象的なcopy／mismatch契約では実行できない。

## 選択肢（Options considered）

### Candidate内容を無条件overwriteする

unexpected local changeとapproved baselineを区別できず、rollback／resumeが不可能なため不採用。

### Runtime scaffoldをcanonical authorityとして残しCandidateをArtifact化する

Humanが承認したEpic Requirement／Design／Planがcanonicalにならず、Planning authority modelを壊すため不採用。

### Candidate文書とRuntime scaffoldをsemantic mergeする

materializerが設計内容を再判断するため不採用。許可済みbinding placeholderの決定的renderだけを認める。

### Pre-commit report model

採用。one-commit contractを維持しつつ、publication evidenceをGit／remoteへ置く。

## 判断理由（Rationale）

HumanがReviewした意味内容とRuntimeが生成するNode identityを分離し、bindingだけを決定的に合成することで、Candidate integrity、repository convention、resume／rollback、auditabilityを同時に満たせる。

## 影響（Consequences）

### Positive

- 旧Portfolio退役前にinvalid Node inputを検出できる。
- Runtime scaffoldとCandidate Bundleの衝突を明示的なstate transitionとして扱える。
- Artifact ID／type、Human approval scope、canonical destinationが一致する。
- canonical Epic三文書がself-identifyingになる。
- reportとpublication evidenceの循環がなくなる。

### Negative／Debt

- C0、render map、Artifact disposition map、Workbench ledgerの検証項目が増える。
- final canonical SHAはNode ID取得後にrenderして初めて確定する。
- Runtime templateやfilename parserが変更された場合、新Candidate versionとfresh Reviewが必要になる。
