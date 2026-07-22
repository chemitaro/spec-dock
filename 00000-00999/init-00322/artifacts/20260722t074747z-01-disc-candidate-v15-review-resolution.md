---
種別: disc
ID: "20260722t074747z-01-disc"
タイトル: "Candidate v15 Review Resolution"
状態: "user-approved"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "current-effective discussion evidence"
artifact_type: "disc"
derived_from:
  - "Candidate v15 Independent Red-Team Formal Review"
  - "INIT-00322-V15-RT-001"
reflected_to:
  - "Candidate v16"
  - "PLANNING-ADOPTION-GATE.md"
  - "HUMAN-REVIEW.md"
  - "MATERIALIZATION-MAP.md"
  - "Initiative Requirement／Design／Plan"
  - "Epic 1 Requirement／Design／Plan／Issue Boundary Map"
  - "Epic 2 Requirement／Design／Plan／Issue Boundary Map"
  - "All-Issue Boundary Map"
  - "ADR 21"
  - "Current Effective Decision Snapshot"
---

# Candidate v15 Review Resolution

## Review result

Candidate v15はexact Candidate identity、ZIP safety、GitHub source binding、3 Epic／7 Issue／9 edge topology、positive Planning Adoption chain、Candidate identity／Placeholder Oracle等をPASSした。一方、中央contractが正しくても、Human Review、Materialization acceptance、All-Issue Map、Initiative／Epic local Requirement／Design／Plan／handoff、ADR 21、Current Effective Decisionにおいてmandatory negative fixture setが短縮されており、P1 `INIT-00322-V15-RT-001`となった。

## Adopted resolutions

1. Portfolio topology、Issue title／slug、9 direct dependenciesは変更しない。
2. Planning Adoptionのnegative fixtureを`PA-NF-01`〜`PA-NF-10`のclosed setとして固定する。
3. closed setは次の10分類とする: `PA-NF-01` archive Review PASS only、`PA-NF-02` git-bound Review PASS only、`PA-NF-03` Human Gate only、`PA-NF-04` parity only、`PA-NF-05` wrong logical Candidate filename／Candidate SHA、`PA-NF-06` wrong reviewed HEAD／exact target paths、`PA-NF-07` source drift、`PA-NF-08` semantic mutation during adoption、`PA-NF-09` parity failure、`PA-NF-10` validation／planning-publication failure。
4. central contractへの参照だけではlocal acceptanceを満たさない。Reviewが指定した全producer／consumer surfaceへ、10 IDと説明を省略せずlocal normative contractとして投影する。
5. E1-I1 producerとE2-I1 consumerの双方で、10／10 fixture PASS、合計20／20、violations 0をacceptance evidenceとHuman Reviewへ要求する。
6. Candidate v15 bytesとReview結果を変更せず、完全なCandidate v16とfresh independent Reviewを作成する。

## Not adopted

- `negative fixtures`という総称だけで10分類を暗黙継承させること。
- `Review-only／wrong-identity／validation-failure`等の短縮3分類でpackage-wide contractを代用すること。
- positive chainからnegative behaviorを推論できるため明示fixtureは不要とすること。
- P1をCandidate v15内のin-place patchとして扱うこと。
