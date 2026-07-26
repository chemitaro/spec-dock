---
種別: disc
ID: "20260726t154840z-disc-human-approved-decision-snapshot"
タイトル: "iss-00334 Human-approved D-001 through D-024 Decision Snapshot"
状態: "package-evidence"
作成者: "Blue Team"
最終更新: "2026-07-27"
親: ["iss-00334", "epic-00331", "init-00322"]
authority: "closed-baseline-evidence"
adoption_status: "unreviewed"
canonical_status: "non-authoritative"
source_logical_filename: "20260723t091726z-iss-00334-issue-planning-candidate-v1.zip"
source_external_zip_sha256: "a7d4074a0b90cb97eed12023a3da60ed7e4a17b2f05b046b7e1af76b6e3a1b6a"
source_artifact: "artifacts/20260723t091726z-disc-current-effective-decisions.md"
reflected_to: []
---

# iss-00334 Human-approved Decision Snapshot

## Authority precedence

```text
accepted Initiative ADR / canonical Initiative docs
→ canonical Parent Epic docs / accepted Epic ADR
→ explicit Human answer in clarification
→ source-grounded Issue-local technical decision
→ research inference
```

## Current decisions

### D-001 Outcome

Issue Planning Workflowを製品能力として実装し、Planning runだけで完了しない。

### D-002 Official interface

Humanは`spec-dock-issue-planning` Skillを起動する。

### D-003 Independent CLI

repo-local `spec-dock-chatgpt`をCore CLIから分離する。

### D-004 ChatGPT command family

```text
planning create
planning revise
review planning
```

### D-005 Responsibility

- Skill: mode、lane、Human Gate、semantic decision
- ChatGPT CLI: target、Git、Prompt、Oracle、result retrieval
- Core Runtime: safety、identity、adoption、parity、validation、publication、readiness
- Main: mutation、commit、push
- Human: adoption、start、merge

### D-006 Prompt resources

provider-managed closed Markdown resources。raw overrideとpublic custom templateなし。

### D-007 Complete Bundle

ChatGPTは一つのfresh sessionで三文書を生成し、Codexはsemantic rewriteしない。

### D-008 Dual Review transport

archive-candidateとgit-boundを正式支援する。silent fallbackなし。

### D-009 Revision

SemanticはChatGPT complete replacement。Mechanicalはclosed change set。両方new identity／fresh Review。

### D-010 Human Gate

Review PASSだけでは開始不可。Plan adoptionとimplementation-start authorizationをexact identityへbindする。

### D-011 Authorization evidence

Workbench source JSON SHAとcanonical Issue Artifactを使う。raw transcriptは保存しない。

### D-012 Archive adoption

Human Gate後にfixed-order atomic replaceしbyte／placeholder parityを証明する。

### D-013 Git-bound parity

reviewed HEADとpublication HEADを分離し、target blob不変とapproval-only diffを証明する。

### D-014 Planning publication

dedicated Planning commit、push、remote HEAD、commit tree parityを必須とする。

### D-015 Readiness

Review、authorization、parity、validation、publicationの論理積からderived stateを返す。state DBなし。

### D-016 `.assurance.json`

Planning Candidate、adoption、readinessの副作用として変更しない。

### D-017 `report.md`

Planning receipt、Review authority、Human authorization authority、state storeにしない。

### D-018 Existing primitive

Git preflight、direct argv、redaction、safe ZIP、digest、atomic publicationを再利用する。

### D-019 Legacy boundary

replacement capabilityをE1-I1で追加し、physical removalはE1-I3へ残す。

### D-020 Security

sensitive-data exclusion、direct argv、fail-closed。shell exceptionはHuman Gateが必要。

### D-021 Projection

provider-first、wheel／sdist、fresh init、update、dogfood parity。

### D-022 Dogfood

eligibilityを仕様化し、exact Issueはfeature-complete直前にHumanが選ぶ。

### D-023 Negative fixtures

PA-NF-01〜PA-NF-10をIssue-localで10／10 PASS、violations 0。

### D-024 Delivery

one Issue／one branch／one Delivery PR／required Review／Human merge。

## No new ADR

本決定集合はaccepted Initiative ADR 02、03、08、20、21、22とaccepted Epic walking-skeleton ADRのIssue-local具体化であり、新規ADRを必要としない。
