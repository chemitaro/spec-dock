---
種別: ADR（Architecture Decision Record）
ID: "20260721t111256z-15-adr"
タイトル: "Source baselineへbindしたcanonical Bundle replacementを採用する"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-21"
親: ["init-00322"]
関連:
  - "20260720t141001z-13-adr-immutable-candidate-zip-as-planning-review-and-approval-boundary"
  - "20260721t090958z-14-adr-outcome-aware-idempotent-portfolio-materialization"
authority: "accepted"
accepted_authority: "human"
accepted_at: "2026-07-21"
accepted_by: "Human review-resolution direction"
mirror_eligible: true
derived_from:
  - "Candidate v6 independent Formal Review F-001"
  - "Observed source blobs at HEAD 2667b4342f803606859a71740b29f0b51b1b3f37"
reflected_to:
  - "CANONICAL-BUNDLE-REPLACEMENT.md"
  - "CANONICAL-REPLACEMENT-MAP.json"
  - "REPORT-MATERIALIZATION-DISPOSITION-TEMPLATE.md"
  - "NEW-PORTFOLIO-MATERIALIZATION-RECOVERY.md"
  - "MATERIALIZATION-MAP.md"
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
artifact_type: "adr"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260721t111256z-15-adr-source-baseline-bound-canonical-bundle-replacement.md"
---

# Source baselineへbindしたcanonical Bundle replacementを採用する

## 位置づけ

Human承認済みCandidateは、既存Initiativeのcanonical三文書を意図的に置換する。既存fileとCandidate bytesが異なることをgeneric `mismatch`として扱うと、正しいsource baselineからの置換そのものが不可能になる。一方、無条件overwriteは未承認変更やbranch driftを破壊する。

## ADR 化基準

- hard to reverse: yes。Initiative authority、旧Portfolio退役、新Portfolio materialization、commit boundaryへ影響する。
- surprising without context: yes。`mismatch`の一部は阻害要因ではなく、Human-approved source migrationの正しい開始状態である。
- real tradeoff: yes。単純copyよりpreflight／backup／ledgerが増える代わりに、source drift、partial replacement、silent overwriteを防ぐ。

## 結論（Decision）

1. destructive mutation前にC0 preflightを行い、source HEAD、canonical三文書／report Git blob、destination ownership、source backup、replacement staging、future destination ownershipを検証する。
2. Existing Initiative canonical三文書を`absent | source-baseline-exact | replacement-exact | unexpected-mismatch`で分類する。
3. Existing canonical三文書では`absent`をinvalidとし、`source-baseline-exact → replacement-exact`だけを許可する。
4. replacementは`requirement → design → plan`の固定順、same-filesystem temp file＋fsync＋atomic replaceで行い、post-write SHA／Git blobを検証する。
5. 各fileのpre-state／post-stateをWorkbench ledgerへ記録し、partial prefixからactual bytesに基づきresumeする。`replacement-exact`は再書込みしない。
6. `unexpected-mismatch`では停止し、無条件overwrite、manual reconstruction、ad hoc Git checkout／resetを行わない。
7. Human-approved rollbackはverified source backupだけを使い、`plan → design → requirement`の逆順でbaselineへatomic restoreする。
8. rollbackがold Portfolioを自動復元しないことを明示し、破壊的mutation後はresume、separate unwind、またはHuman-approved blocked stateへrouteする。
9. `report.md`は置換せず、全parity後にCandidate SHA marker付きdisposition blockを一度だけidempotent appendする。
10. final parityはInitiative三文書、全Epic Bundle／ADR、binding substitution、report disposition、Node／dependencyを被覆し、remote verification成功までsource backupを保持する。

## 背景（Context）

Candidate v6は`absent／exact／mismatch`だけを定義し、既存Initiative三文書を必ず`mismatch`へ分類した。旧7 Epic退役と新Node作成の後にcanonical placementで停止するため、reviewed sourceからapproved replacementへのmigration transitionが欠落していた。

## 選択肢（Options considered）

### A. Existing fileをすべてgeneric mismatchとして停止

正しいreplacementを永久に実行できないため不採用。

### B. Human承認を理由に無条件overwrite

source drift、別process変更、部分成功を検出できないため不採用。

### C. Git checkout／resetで都度復旧

path boundaryと証跡が曖昧で、unrelated changeを巻き込むため不採用。

### D. Source-baseline-bound state transition＋verified backup＋atomic resume

approved sourceとreplacementを厳密に区別し、partial failureから再開／rollbackできるため採用。

## 判断理由（Rationale）

- `SOURCE-BASELINE.json`の既存blob identityを実行contractとして活用できる。
- Candidate replacement bytesとsource bytesの双方をcontent-addressedに保持できる。
- destructive retirement前に後段の確定的blockerを発見できる。
- Git commitをpublication boundaryとして維持しつつ、commit前のlocal partial stateを復旧できる。

## 影響（Consequences）

### Positive

- intentional replacementとunexpected mismatchを区別できる。
- 3-file replacementの任意prefixから安全にresumeできる。
- Human-approved rollbackとblocked stateを明確にできる。
- report appendとfinal parityまで一つのauthorityへ統合できる。

### Negative

- Workbench source backup、replacement staging、canonical replacement ledgerが必要になる。
- old Portfolio退役後のfull original-state rollbackは自動化せず、Human判断が残る。
- atomic file APIとdirectory fsyncのplatform差をimplementation時に検証する必要がある。


## Follow-up authority

Candidate v8ではADR 16（`20260721t124850z-16-adr-runtime-valid-portfolio-materialization-and-publication.md`）が、Runtime-valid Node input、Epic scaffold replacement、Artifact disposition、Epic identity binding、pre-commit report／publication evidenceの追加契約を定義する。
