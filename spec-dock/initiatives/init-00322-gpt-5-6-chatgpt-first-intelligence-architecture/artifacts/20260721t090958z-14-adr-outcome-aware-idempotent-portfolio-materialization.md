---
種別: ADR（Architecture Decision Record）
ID: "20260721t090958z-14-adr"
タイトル: "Runtime outcomeへbindしたidempotent Portfolio materializationを採用する"
状態: "accepted"
作成者: "GPT-5.6 Pro"
最終更新: "2026-07-21"
親: ["init-00322"]
関連:
  - "20260720t112401z-12-adr-initiative-planning-orchestrates-epic-planning-through-issue-boundaries"
  - "20260720t141001z-13-adr-immutable-candidate-zip-as-planning-review-and-approval-boundary"
authority: "accepted"
accepted_authority: "human"
accepted_at: "2026-07-21"
accepted_by: "Human review-resolution direction"
mirror_eligible: true
derived_from:
  - "Candidate v5 independent Formal Review F-001 and F-002"
  - "Observed Runtime create outcomes at source HEAD 2667b4342f803606859a71740b29f0b51b1b3f37"
reflected_to:
  - "NEW-PORTFOLIO-MATERIALIZATION-RECOVERY.md"
  - "MATERIALIZATION-MAP.md"
  - "LEGACY-PORTFOLIO-RETIREMENT.md"
  - "initiative/requirement.md"
  - "initiative/design.md"
  - "initiative/plan.md"
  - "Epic 1 Planning Bundle"
  - "CANONICAL-BUNDLE-REPLACEMENT.md"
  - "CANONICAL-REPLACEMENT-MAP.json"
artifact_type: "adr"
canonical_path: "spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/artifacts/20260721t090958z-14-adr-outcome-aware-idempotent-portfolio-materialization.md"
---

# Runtime outcomeへbindしたidempotent Portfolio materializationを採用する

## 位置づけ

Human承認済みCandidateから新しいEpic／Issue Nodeを作る処理は、GitHub Issue作成、local scaffold／metadata作成、create lock cleanup、post-syncが一つのatomic transactionではない。旧Portfolio退役後のcreate失敗でremote-only、partial local、valid local＋sync failure等が発生すると、単純な再実行はGitHub Issue重複やNode binding重複を生む。

## ADR 化基準

- hard to reverse: yes。Node identity、GitHub Issue、dependency、canonical file placement、destructive replacementの安全性へ影響する。
- surprising without context: yes。CLI failureでもremote Issueまたはlocal Nodeが成立している場合がある。
- real tradeoff: yes。単純な直列scriptよりledgerとoutcome分類が増える代わりに、重複生成、曖昧な再開、manual metadata editを防ぐ。

## 結論（Decision）

1. 旧Portfolio retirementと新Portfolio materializationを別authorityへ分離する。
2. 新Portfolio materializationは一時Workbench ledgerを持ち、全3 Epic／7 Issue semantic keyを順番にbindする。
3. `pre_github_fail`、`post_github_remote_only_fail`、`post_github_local_write_fail`、`post_github_body_and_cleanup_fail`、`post_github_local_write_success_cleanup_fail`、post-sync failureを別状態として扱う。
4. remote Issueを一度観測したsemantic keyは、remote closure／binding clearまで`--create-github-issue`を再実行せず、`--github-issue`でlink-existingする。
5. valid local Nodeを観測したsemantic keyはcreateを再実行しない。sync、dependency、Bundle placement、parityから再開する。
6. partial local stateでは`doctor`とpath／metadata／linkage inspectionを先に行い、proven failed destinationだけをHuman-approved bounded cleanupできる。`.meta.json`を手書きして完成させない。
7. 全10 Nodeがvalidにbindされるまでdependencyを作らず、全approved dependencyが成立するまでBundleを配置しない。
8. dependency addとnew Epic Bundle placementもledgerによりidempotentに再開する。Existing Initiative canonical三文書はADR 15の`source-baseline-exact → replacement-exact` state transition、source backup、atomic replace、resume／rollbackに従う。
9. complete parity前にcommit／pushしない。
10. full unwindはHuman承認時だけ行い、新PortfolioのedgeとNodeを逆順に除去する。旧Portfolioを自動復元しない。

## 背景（Context）

Observed RuntimeはGitHub Issueをlocal create lockより先に作成し得る。local createはscaffold、metadata、post-write verification、lock cleanup、post-syncに分かれ、failure outcomeはremote-only、partial local、local success＋cleanup failure等を区別する。MaterializerはこのoutcomeをCandidate-level semantic key、binding、dependency、Bundle placementの順序へ変換しなければならない。

## 選択肢（Options considered）

### A. create commandを成功するまで同じ引数で再実行

remote Issue重複を生むため不採用。

### B. failureごとにoperator判断へ委ねる

破壊的退役後にauthorityと順序を発明させるため不採用。

### C. Runtimeへ新しいtransaction DBを実装してからmaterialize

本Initiativeのminimal-state方針に対して過剰であり不採用。

### D. Candidate-level bounded ledger＋outcome-specific recovery

既存RuntimeとGitHub Issue linkageを利用し、重複なしでresume／cleanup／unwindできるため採用。

## 判断理由（Rationale）

- Runtimeの既存`--github-issue` link-existing経路を再利用できる。
- Candidate semantic keyとobserved IDを一時ledgerで結び付ければ、新しい永続DBは不要。
- Node、dependency、Bundle placementをphase分離することで、create failureが下流mutationへ波及しない。
- Human-approved bounded cleanupとfull unwindを明示し、manual metadata reconstructionを禁止できる。

## 影響（Consequences）

### Positive

- duplicate GitHub Issuesとduplicate Node bindingsを防ぐ。
- CLI failure後も既成立状態を失わず再開できる。
- dependency／Bundle placement／parityまで一つのfail-closed contractになる。
- canonical source replacementをgeneric mismatchへ誤分類せず、別のbaseline-bound authorityへ委譲できる。

### Negative

- Workbench ledgerとoutcome classificationが必要になる。
- partial local cleanupはHuman approvalとproven path boundaryを必要とする。
- full unwind後も旧Portfolioは自動復元されず、Human判断が必要になる。


## Follow-up authority

Candidate v8ではADR 16（`20260721t124850z-16-adr-runtime-valid-portfolio-materialization-and-publication.md`）が、Runtime-valid Node input、Epic scaffold replacement、Artifact disposition、Epic identity binding、pre-commit report／publication evidenceの追加契約を定義する。
