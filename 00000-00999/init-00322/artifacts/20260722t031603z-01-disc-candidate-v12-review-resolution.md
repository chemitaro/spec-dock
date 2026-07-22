---
種別: disc
ID: "20260722t031603z-01-disc"
タイトル: "Candidate v12 Review Resolution"
状態: "user-approved"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-22"
親: ["init-00322"]
authority: "current-effective discussion evidence"
artifact_type: "disc"
derived_from:
  - "Candidate v12 Independent Red-Team Formal Review"
reflected_to:
  - "Candidate v13"
  - "ADR 21"
  - "ADR 22"
---

# Candidate v12 Review Resolution

## Review result

Candidate v12はtransport filename aliasによりFormal identityが`INSUFFICIENT EVIDENCE`となり、内容上はIssue Planningのpositive Human Gate欠落がP1、Human approval filename bindingとplaceholder oracleがP2として報告された。

## Adopted resolutions

1. 3 Epic／7 Issue／9 edge topologyは維持する。
2. Issue PlanningはReview PASS後にHuman Issue Plan Adoption Gateを必須とし、canonical adoption／parity後だけ`execution-ready`へ進む。
3. archiveとgit-boundの両pathでpositive Human decisionを記録する。
4. Candidate identityをlogical filename＋content identityへ再定義し、closed transport suffix aliasを許可する。
5. Human approval record／canonical Evidenceへlogical filename、observed transport filename、ZIP SHAを記録する。
6. placeholder検査をmachine-readable dynamic-file mapへ限定し、static literal examplesをexact hashで管理する。
7. Candidate v12を変更せず、完全なCandidate v13とfresh Reviewを作成する。

## Not adopted

- external transport filenameを無条件にidentityから削除すること。
- transport renameをfuzzyに許可すること。
- Review PASSだけでIssue executionを開始すること。
- repository-wide semantic placeholder scan。
