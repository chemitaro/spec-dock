---
種別: disc
ID: "20260726t225541z-disc"
タイトル: "Candidate v15 Human Adoption Decision"
状態: "resolved"
作成者: "iwasawayuuta"
最終更新: "2026-07-27"
親: ["iss-00334", "epic-00331", "init-00322"]
関連:
  - "20260726t154840z-iss-00334-issue-planning-candidate-v15.zip"
  - "20260726t164628z-chatgpt-output-v15-fresh-red-team-review.md"
  - "20260726t164657z-disc-v15-red-team-pass-admission.md"
authority: "human-adoption-evidence"
candidate_id: "iss-00334-v15-20260726t154840z"
candidate_sha256: "07a2c240c9d2edee5faa58f0ad4ab09b05b542dba2e1a8d61234d479c0355fbd"
candidate_source_head: "2e86ec64289ec8102470df75329025d46bbfa51a"
adoption_base_head: "bc2449c5b75598fac1f414deb28604d129253009"
derived_from:
  - "artifacts/20260726t154840z-iss-00334-issue-planning-candidate-v15.zip"
  - "artifacts/20260726t164628z-chatgpt-output-v15-fresh-red-team-review.md"
  - "artifacts/20260726t164657z-disc-v15-red-team-pass-admission.md"
reflected_to:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
---

# iss-00334 Candidate v15 Human Adoption Decision

## 1. 対象identity

- logical filename: `20260726t154840z-iss-00334-issue-planning-candidate-v15.zip`
- Candidate ID: `iss-00334-v15-20260726t154840z`
- external SHA-256: `07a2c240c9d2edee5faa58f0ad4ab09b05b542dba2e1a8d61234d479c0355fbd`
- Candidate source HEAD: `2e86ec64289ec8102470df75329025d46bbfa51a`
- canonical adoption base HEAD: `bc2449c5b75598fac1f414deb28604d129253009`
- fresh Red Team thread: `6a6633e1-dff4-83ee-8c82-40270b06f29e`
- fresh Red Team verdict: `PASS`、P0 `0`、P1 `0`、nonblocking `0`
- deterministic preflight: `127/127 PASS`

## 2. Human decision

Humanは現在のCodex taskで、Candidate v15を確認後に「OKです。このZIPファイルをこのissueに展開してください」「適切なパスに、正規の、正式なパスに配置をしてください」と指示した。

Mainはこの指示を、exact Candidate v15をIssueのcanonical planning pathsへ採用する明示承認として扱う。次は承認範囲に含めない。

- implementation start
- `.assurance.json` mutation
- execution readiness
- PR readiness / merge readiness
- Issue finish

## 3. 正式配置

| Candidate source | 正式な配置先 | 操作 |
|---|---|---|
| `requirement.md` | Issue直下`requirement.md` | whole-file byte-for-byte replacement |
| `design.md` | Issue直下`design.md` | whole-file byte-for-byte replacement |
| `plan.md` | Issue直下`plan.md` | whole-file byte-for-byte replacement |
| `artifacts/20260726t154840z-disc-human-approved-decision-snapshot.md` | Issue `artifacts/` direct child | byte-for-byte copy |
| `artifacts/20260726t154840z-research-implementation-and-test-impact-map.md` | `artifacts/20260726t154840z-01-research-implementation-and-test-impact-map.md` | byte-for-byte copy後、same-second collision規則に従うfilename-only配置 |
| `artifacts/20260726t154840z-research-scope-reset-authority-trace.md` | `artifacts/20260726t154840z-02-research-scope-reset-authority-trace.md` | byte-for-byte copy後、same-second collision規則に従うfilename-only配置 |
| original Candidate ZIP | `artifacts/20260726t154840z-iss-00334-issue-planning-candidate-v15.zip` | exact immutable ZIPを保存 |

`MANIFEST.json`、`CHECKSUMS.sha256`、`SOURCE-BASELINE.json`、`PLACEHOLDER-ORACLE-MAP.json`はpackage controlsであり、canonical Issue rootへloose fileとして配置しない。exact Candidate ZIP内で保持する。

## 4. 配置時の不変条件

- 三文書および3つの補助Markdownの本文bytesはCandidateと一致させる。
- control filesとinternal inventoryを含むCandidate ZIPのSHA-256を変更しない。
- `.meta.json`を変更しない。
- `.assurance.json`を変更しない。
- `report.md`をCandidateで置換せず、既存履歴を保持してadoption dispositionだけを追記する。
- Candidate内の`report.md`禁止契約を維持する。

## 5. 採用結果と残存gate

Candidate v15のplanning contentをIssueのcanonical pathsへ配置する。Candidate package内のcandidate-era status wordingはreviewed bytesの一部として保持し、canonical adoptionの事実とdownstream authorityは`report.md`のEvidence Adoption Ledgerで管理する。

この配置後もfresh canonical `spec-reviewer` passは未取得である。配置後の`guidance issue-planning`は`.assurance.json`未作成の状態で`state=blocked`、`reason_code=design-not-substantive`を返している。これはCandidateの配置失敗ではなく、Candidate外で行う既存assurance workflowとcanonical review gateが未完了であることを示す。

Implementation startとexecution handoffは、既存assurance workflowをCandidate外で完了し、canonical三文書と`report.md`を対象にfresh `spec-reviewer`がPASSし、Humanがimplementation startを明示的に承認するまで停止する。
