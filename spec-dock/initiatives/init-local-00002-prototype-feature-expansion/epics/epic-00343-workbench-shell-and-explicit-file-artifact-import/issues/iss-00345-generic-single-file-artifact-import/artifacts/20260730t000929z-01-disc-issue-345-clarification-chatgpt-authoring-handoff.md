---
種別: disc
ID: "20260730t000929z-01-disc"
タイトル: "Issue 345 明確化とChatGPT authoring引き継ぎ"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00345"]
関連: ["epic-00343", "20260730t000929z-research"]
authority: "proposed"
mode: "draft-only"
next: "spec-dock-issue-planning + spec-dock-chatgpt-authoring; orchestrator adoption + fresh spec review"
derived_from:
  - "20260730t000929z-research-issue-345-generic-file-import-source-grounding.md"
  - "epic-00343/artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md"
reflected_to: []
---

# 20260730t000929z-01-disc Issue 345 明確化とChatGPT authoring引き継ぎ

## objective / authoring objective

`iss-00345` のplaceholder requirementをsource-groundedなcritical Issue draftへ具体化し、assurance compose後のdesignとplanを作るためのChatGPT authoring handoffである。返答はevidence-onlyであり、canonical docsの書換え、EAL/OAL記入、assurance mutation、review pass、readiness、Issue finish、PR/mergeを主張してはならない。

## fixed decisions — reopenしないこと

- `artifact import file --file <path>`、exactly one root/initiative/epic/issue target、rootはfake graph nodeではない。
- repository-root-relative source resolution、repository内外のreadable regular single file、leaf symlink reject / ancestor symlink allow、explicit pathによるread authorization。
- opaque byte preservation、source non-mutation、cross-FS success、FD-bound no-replace commit、unsupported capability fail closed、`committed_with_warning`はretry不要。
- `<timestamp>--<safe-original-basename>`、collision時`<timestamp>-<nn>--...`、`--` generic family、full destination basename identity、typed/blank/generic shared slot、extension/case/space/Unicodeを残すminimal normalization。
- external sourceのbasename-only visibilityと全経路content-free output。absolute/parent path、body、hash/byte count/MIME/encoding等content-derived metadataを出さない。
- generic bodyはvalidate/sync/deps/context/ADR mirror/default discoveryでopaque。generic `.md`をtyped Artifact/ADRにしない。
- existing `artifact import chatgpt-output` のWorkbench-only lowercase `.md` guard、title/slug、blank naming/result contractは不変。
- Issue 344 merged premiseを前提とし、Issue 346がwheel consumer E2E、integrated dogfood、opt-in full regression、Epic final review/PRを所有する。

## Issue-local decisions ChatGPT may concretize

- critical assurance profileに必要なIssue R/D/Pの構造、requirement ID / design ID / test closure IDの追跡可能な粒度。
- `commands/artifact_import.py` → `application/import_artifact.py` → `contracts.py` → `infra/binary_artifact_publisher.py` → `presentation/cli_text.py` の最小責務分割と既存call-site整合。
- generic parser、shared allocation slot、minimal basename normalizer、privacy-safe result DTO、FD/identity checks、staging/cleanup warningの具体的なlocal contract。ただしfixed decisionを変える提案は不可。
- focused/default laneのhermetic test seam、fault injection、CLI text/JSON assertion、docs対象、およびIssue 346へ残すdelivery boundary。

## R / D / P expectations

| Artifact | 必須の出力 |
|---|---|
| Requirement | actor/trigger、target/source/eligibility/naming/privacy/authority/opaque lifecycle/compatibility、失敗時non-mutation、critical acceptanceとnon-goalを観測可能に定義 |
| Design | D-003〜009とaccepted ADRを参照し、CLI/application/domain/infra/presentation/docs/testsの境界、root resolver、content-free result、publication stateを固定。具体的primitiveの変更を必要とする場合はamendmentへ戻す |
| Plan | provider-firstのsmall vertical batches、Red/Green、focused/default checks、fault/compatibility matrix、docs、Issue 346 handoff、EAL/OAL/Spec Authoring Gate/fresh reviewer gateを順序化 |

## acceptance and test envelope

- 4 target、zero/multiple selector reject、repo-root-relative nested invocation、external absolute/relative、cross-FS source。
- regular / empty / binary / NUL / invalid UTF-8 / PDF/image/ZIP / no-extension / multi-suffix、missing/directory/leaf symlink/special/unreadable、ancestor symlink。
- byte equality、source survival、identity mutation/hash mismatch、no-overwrite/collision/suffix exhaustion、generic/typed/blank/`chatgpt-output` concurrent slot collision。
- external privacy across success、preflight failure、allocation failure、publication failure、warning、unexpected failure。bodyのdecode/parse不在と`validate`/`sync`/deps/context/ADR mirror compatibility。
- docsはgeneric importのevidence-only boundaryと既存ChatGPT-output互換を説明する。wheel consumer、integrated dogfood、opt-in full regression、Epic-wide final qualityは345のacceptanceに含めない。

## scope / non-scope

| In scope | Out of scope |
|---|---|
| generic single-file importのfeatureとfocused/default lane | directory/glob/bulk/recursive import、source classification/MIME/catalog、archive extraction |
| source保全、publication、privacy、opaque lifecycle、operator docs | canonical docs/ADR/report/assuranceの自動変更、watch/sync/copy-back |
| provider sourceと必要なtests/docs | `chatgpt-output`契約変更、Workbench shell再実装、rootをnode graphへ追加 |
| Issue-local reviewable milestone | Issue 346のwheel/dogfood/full regression/Epic final PR、merge/finish |

## source index / prompt attachments

1. `issues/iss-00345.../requirement.md`、`design.md`、`plan.md`、`report.md`（scaffold/current stateを明示）。
2. `epic-00343/requirement.md`（E-RQ-008〜025、E-AC-008〜018）。
3. `epic-00343/design.md`（D-003〜009）。
4. `epic-00343/plan.md`（Candidate 2、critical grade、Candidate 3 boundary）。
5. accepted ADR `artifacts/20260728t100038z-adr-generic-imported-file-identity-and-privacy-boundary.md`。
6. `iss-00344` approved R/D/P（merged premiseのみ）。
7. 現行sourceとnearest tests: `application/import_artifact.py`、`contracts.py`、`commands/artifact_import.py`、`infra/binary_artifact_publisher.py`、`presentation/cli_text.py`、Epic planが指すtest surfaces。

## prompt framing / expected Markdown output

Promptは「sourceにない機能を足さず、fixed decisionsを再検討せず、current source/testを読んで矛盾を列挙し、Issue-local R/D/P draftとtraceability matrixを日本語で返す」とする。出力は次を含むMarkdownに限定する。

1. source-grounded assumptionsとsource conflict/gap。
2. draft Requirement / Design / Plan（placeholderを直接canonical化しない）。
3. requirements/design/tests/layer/ownershipのmatrix、focused test command候補、failure/privacy assertion。
4. accepted ADRから逸脱する場合のstop-and-escalate条件、Issue 346 handoff。
5. forbidden authority claimsがないことのself-check。

ChatGPT outputはcomplete standalone Markdownならpreservation checkpointを通し、main orchestratorが必要に応じて`artifact import chatgpt-output`でbyte-preserving evidenceとして保存する。import receiptはadoption、review、readinessを意味しない。

## adoption targets and gates

- main orchestratorがclaim単位でEvidence Adoption Ledger（EAL）へ`adopted` / `partially_adopted` / `rejected` / `deferred`を記録するまで、generated draftはproposalのままとする。
- Objective Alignment Ledger（OAL）はprimary objective evidence、secondary requirement evidence、inversion risk、reviewer verdictを記録する。Spec Authoring Gateはsource grounding、preservation状態、canonical rewrite対象、未採用理由を確認する。ChatGPTはこれらを埋めず、状態をpassとしない。
- canonical R/D/P反映後にfresh `spec-reviewer`が必要であり、reviewer gateはChatGPT authoring outputやruntime validationで代替しない。

## unresolved questions: none

高影響な利用者意図はEpic R/D/Pとaccepted ADRで固定済みである。implementation seamの確認はplanningで現行source/testsに対して行うべきであり、人間に再質問する理由にはならない。したがってinterview artifactは作成しない。

## proposed next action

`mode=draft-only`で `spec-dock-issue-planning` と `spec-dock-chatgpt-authoring` を順に用いる。main orchestratorがevidenceを採否しcanonical R/D/Pへ反映し、その後fresh spec reviewへ戻す。これはapproval、pass、readinessの宣言ではない。
