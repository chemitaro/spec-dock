---
種別: ADR（Architecture Decision Record）
ID: "20260721t231721z-19-adr"
タイトル: "Signed Human Gate Evidence and Complete M-001 through M-019 Closure Package"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "accepted"
accepted_authority: "user-approved in this ChatGPT thread"
accepted_at: "2026-07-22"
accepted_by: "Human"
mirror_eligible: true
artifact_type: "adr"
derived_from:
  - "Candidate v10 independent Red-Team Formal Review"
  - "Human approval and M-019 traceability discussion"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "HUMAN-APPROVAL-EVIDENCE-CONTRACT.md"
  - "FINAL-METRIC-PACKAGE-CONTRACT.md"
---

# Signed Human Gate Evidence and Complete M-001 through M-019 Closure Package

## 位置づけ

Human approvalをgenericなCandidate承認文として扱うだけでは、HumanがE1-I1〜E1-I3のmandatory four-item matrixを確認したというM-019一次事実を監査可能に保持できない。また、E3-I3がM-001〜M-016だけをlocal final packageとすると、M-017〜M-019のmaterialization、publication、Human-Gate Evidenceがrelease／Epic finish／Initiative closureから脱落する。

## ADR 化基準

- hard to reverse: yes。Human Gate、materialization、report、E3-I3 release、Initiative closureのauthority chainへ影響する。
- surprising without context: yes。Human approvalはexact SHAだけでなくIssue-local matrixの署名済みEvidenceを必要とし、E3-I3は自ら生成しないEvidenceをimmutable referenceとしてpackageへ含める。
- real tradeoff: yes。approval recordとfinal package contractが増える代わりに、暗黙推論と遡及的Evidence生成を排除する。

## 結論（Decision）

1. Human Portfolio Approvalは、exact Candidate SHAに加え、E1-I1、E1-I2、E1-I3それぞれの4禁止事項を12／12 PASS、violation 0として明示記録する。
2. signed approval source recordをCandidate-SHA-bound Workbenchへ保存し、そのSHAを記録する。
3. Human承認後、`HUMAN-APPROVAL-EVIDENCE-CONTRACT.md`のclosed renderでcanonical Human approval evidence Discussionを生成する。
4. `report.md`のM-019 referenceはcanonical approval evidence pathとsource approval record SHAへ解決しなければならない。
5. E3-I3はM-001〜M-016をoperationalに評価し、M-017／M-018／M-019をimmutable referenceとして検証する。
6. E3-I3 final Issue Delivery Review、Human merge、Epic Delivery Review、Epic finish、Initiative closureはM-001〜M-019 complete packageを必須とする。
7. E3-I3はM-017〜M-019の過去事実を再生成、再署名、推測しない。

## 背景（Context）

Candidate v10は上位Initiative PlanでM-001〜M-019を要求していたが、Human approval署名文はM-019 matrixを直接記録せず、Epic 3 local handoffはM-001〜M-016で終端していた。この分断により、Human Gate一次事実と最終closure packageが曖昧になった。

## 選択肢（Options considered）

### Generic exact-SHA approvalだけを保持

却下。Questionを表示したことと、Humanが各matrixをPASSと署名したことは同値ではない。

### E3-I3がM-019を再評価する

却下。Human approvalという過去のauthority eventを後続Issueが再生成できない。

### Signed approval Evidence＋complete final package

採用。一次事実のownerと最終packageのconsumerを分離し、immutable referenceで接続できる。

## 判断理由（Rationale）

- Human Gateの事実をexact signed recordとcanonical locatorで固定できる。
- M-017〜M-019のownerを維持しつつ、E3-I3のrelease packageを完全化できる。
- upper-level proseとIssue-local handoffのterminal rangeが一致する。
- report、Epic Review、Initiative closureが同じEvidence packageを参照できる。

## 影響（Consequences）

### Positive

- M-019を遡及生成せず監査できる。
- final decision packageのrangeが一意になる。
- Human Approval、materialization、publication、implementation、closureのtraceが閉じる。

### Negative

- Human approval recordとcanonical Evidence Artifactのrender／hash管理が追加される。
- E3-I3 final packageはM-017〜M-019 reference integrityも検証する必要がある。

### Follow-up

- Human Review UI／Skillへexact approval blockを組み込む。
- E3-I3 report／Artifact templateへM-001〜M-019 manifestを組み込む。
- Reviewerはsigned record、canonical locator、complete final packageを必須確認する。
