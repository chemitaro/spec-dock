---
種別: disc
ID: "20260726t164657z-disc-v15-red-team-pass-admission"
タイトル: "iss-00334 Candidate v15 Fresh Red Team PASS Admission"
状態: "resolved"
作成者: "Codex Main"
最終更新: "2026-07-27"
親: ["iss-00334", "epic-00331", "init-00322"]
authority: "main-review-admission"
adoption_status: "decided"
candidate_id: "iss-00334-v15-20260726t154840z"
candidate_sha256: "07a2c240c9d2edee5faa58f0ad4ab09b05b542dba2e1a8d61234d479c0355fbd"
candidate_source_head: "2e86ec64289ec8102470df75329025d46bbfa51a"
review_thread_id: "6a6633e1-dff4-83ee-8c82-40270b06f29e"
review_artifact: "20260726t164628z-chatgpt-output-v15-fresh-red-team-review.md"
review_artifact_sha256: "def84b590618a405fc2be2ce30999ccdd9f610a2a28f0b116fd3164c06c9f51a"
---

# iss-00334 Candidate v15 Fresh Red Team PASS Admission

## 1. 対象identity

Main Review Admission Gateは、次のimmutable Candidateとfresh read-only Red Team reviewだけを対象にした。

- logical filename: `20260726t154840z-iss-00334-issue-planning-candidate-v15.zip`
- Candidate ID: `iss-00334-v15-20260726t154840z`
- version: `15`
- internal root: `20260726t154840z-iss-00334-issue-planning-candidate-v15/`
- external SHA-256: `07a2c240c9d2edee5faa58f0ad4ab09b05b542dba2e1a8d61234d479c0355fbd`
- source HEAD: `2e86ec64289ec8102470df75329025d46bbfa51a`
- Blue Team thread: `6a65399a-4940-83e8-a955-8c3a731b68a8`
- fresh Red Team thread: `6a6633e1-dff4-83ee-8c82-40270b06f29e`
- preserved review: `20260726t164628z-chatgpt-output-v15-fresh-red-team-review.md`
- preserved review SHA-256: `def84b590618a405fc2be2ce30999ccdd9f610a2a28f0b116fd3164c06c9f51a`

Red TeamはCandidate v15だけを対象とするfresh threadで実行し、Candidate、repository、canonical documents、patch、replacement documents、revised ZIPを変更・生成していない。ChatGPT Useのfresh-run model selection evidenceは`requested=Pro`、`resolved=Pro`、`verified=yes`だった。

## 2. 検証結果

Mainのdeterministic preflightは`127/127 PASS`だった。次を独立に確認した。

- ZIPのexternal SHA-256、single internal root、entry type、path safety、size limits。
- `MANIFEST.json`、`CHECKSUMS.sha256`、`SOURCE-BASELINE.json`、`PLACEHOLDER-ORACLE-MAP.json`のidentityとinventory。
- source baselineの49 Git blob entriesと20 planned-absent paths。
- v14からv15へのformal document diffが、Main Admissionで採用したRT-001とRT-003だけを修正していること。
- RT-002のsame-thread locator、session registry、new persistent stateが恒久product requirementとして再導入されていないこと。

fresh Red Teamの判定は次のとおり。

| 項目 | 結果 |
|---|---|
| RP-01〜RP-07 | all `PASS` |
| P0 | `0` |
| P1 | `0` |
| nonblocking | `0` |
| Verdict | `PASS` |

## 3. Main Admission

fresh Red Team Reviewを、Candidate v15の仕様適合を示すread-only evidenceとして採用する。

| 対象 | Main disposition | 判断 |
|---|---|---|
| RT-001 | `resolved` | Plannerの三文書response、Runtimeのmandatory controls付きimmutable ZIP、S05のsole packaging／identity ownership、create→archive Review direct handoffがv15で閉じ、fresh ReviewがPASSした。 |
| RT-002 | `resolved/rejected`を維持 | init-00322限定の同一Blue thread運用を恒久product contractへ昇格しない。v15にも再導入されていない。 |
| RT-003 | `resolved` | data-only named `ArchiveReviewContract`、generic default後方互換、Issue-specific positive／negative tests、exact allowed pathsがv15で閉じ、fresh ReviewがPASSした。 |
| 新規finding | `none` | Candidate内かつIssue-localなmaterial P0／P1、nonblocking findingは報告されなかった。 |

これにより、暫定Charterに基づく「Blue Team修正 → fresh Red Team Review」のCandidate review/fix cycleはv15で完了する。

## 4. 成立しない状態

このAdmissionは次を成立させない。

- canonical `requirement.md`、`design.md`、`plan.md`への採用または置換。
- Human Gateの承認。
- canonical `spec-reviewer` pass。
- implementation start、execution readiness、PR readiness、merge readiness、Issue finish。

Candidate v15の正式採用とcanonical placementは、別のHuman authorizationとidentity-bound adoption decisionを必要とする。

## 5. 運用・tooling observation

今回のdogfoodingでは、次を将来の実装・改善候補として観測した。ただし、Candidate v15のReview verdictを変更するblockerではない。

1. 現行のgeneric `authoring pack review`はgeneric prompt-pack schemaを前提とし、Issue Planning Candidate schemaの受入validatorとしては利用できない。Candidate-specific contractはiss-00334の実装対象である。
2. ChatGPT Useのsame-thread follow-upではmodel selection evidenceが`skipped`／`verified=no`になる一方、fresh runでは`requested=Pro`、`resolved=Pro`、`verified=yes`を取得できた。continuation時のmodel evidenceは観測上の制約として扱い、fresh Red Teamではfail-closedに確認した。

## 6. 次アクション

1. 本Admission、保存済みReview、`report.md`更新をcommit/pushする。
2. Candidate v15とReview evidenceをimmutableに保持する。
3. Humanが明示的に採用を承認するまでcanonical三文書を置換せず、実装を開始しない。
