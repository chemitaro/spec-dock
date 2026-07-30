---
種別: review
ID: "20260730t150254z-review"
タイトル: "PR 351 S006 Local Closure Review PASS"
状態: "accepted"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
関連: []
authority: "review"
derived_from:
  - "20260730t115808z-pr-repair-batch-pr-351-repair-batch.md"
  - "20260730t143143z-pr-351-s005-atomic-stage-state-validation-chatgpt-followup.md"
  - "20260730t145257z-pr-351-s006-no-transaction-state-chatgpt-followup.md"
reflected_to:
  - "report.md"
---

# PR 351 S006 Local Closure Review PASS

## Scope

- PR: `https://github.com/chemitaro/spec-dock/pull/351`
- reviewed local source base: `6c9302ab08c7f352e85a199b65bdeb522376171c` plus uncommitted S002〜S006 repair delta
- F002: Candidate external-output TOCTOU
- F003: apply preimage drift and durable recovery-state admissibility
- excluded: F004 P2、architecture redesign、style improvement、Oracle-native local configuration change

## Final Fresh Review Results

| perspective | status | P0 | P1 | confidence | result |
| --- | --- | ---: | ---: | ---: | --- |
| Spec | PASS | 0 | 0 | 0.97 | accepted contracts、public result semantics、Human Oracle boundaryにblocking contradictionなし |
| Code | PASS | 0 | 0 | 0.98 | atomic staged file、route precedence、state classifier、rollback durabilityにblocking defectなし |
| QA | PASS | 0 | 0 | 0.98 | changed defect boundariesを直接検証する回帰保護にblocking gapなし |

## Closed Defects

- Candidateはvalidated output descriptor直下でrandom hidden staged ZIPをatomic `openat(O_CREAT|O_EXCL|O_NOFOLLOW)`し、成功fdをownership起点とする。
- publish／cleanupはopen descriptor identityとcurrent nameが一致する場合だけ行い、observed replacementをfail closedする。
- applyは`after_operation_recorded`直後にbranch／HEAD／canonical／companionを再検証し、drift時にconcurrent bytesをrestoreで上書きしない。
- `BACKED_UP` recoveryはactual driftとno driftをbackup snapshotから区別し、いずれもdiscard-onlyとする。
- transaction recoveryはclosed durable-state vocabularyとvalid state combinationをdestructive helper前に検証する。
- no-transaction routeは`OPERATION_RECORDED`／`ROLLED_BACK`だけを新transaction開始可能とし、その他state／orphan publicationをattempt前に停止する。
- successful rollbackはtransaction absenceとdirectory durabilityを確認して`ROLLED_BACK`をatomic記録してから結果を返す。

## Verification

- `uv run pytest tests/unit/infra/test_issue_planning_candidate.py`: `29 passed`
- `uv run pytest tests/unit/infra/test_issue_planning_apply.py`: `19 passed`
- `uv run pytest --run-full-regression tests/integration/test_issue_planning_apply.py`: `60 passed`
- `uv run pytest`: `1152 passed, 2144 skipped`
- `make lint`: Ruff check／format、mypy 281 source files PASS
- provider／dogfood candidate and apply source byte parity: PASS
- `./spec-dock/scripts/spec-dock validate`: `nodes=227`
- `git diff --check`: PASS
- final reviewers re-executed the scoped regression set: `108 passed`

## Residual Risk

- final identity-check-to-name-operation syscall interval is accepted for the portable Darwin／Linux contract.
- same-credential rewriting of private evidence to another semantically valid state is outside the current ownership／permission threat model.
- F004 `information_insufficient` typed transport remains a non-blocking P2 follow-up and is not repaired in this PR.

## Verdict

`PASS`

Local implementation and review gates are closed. Commit／push後のnew exact HEADに対するGitHub Actions and fixed Codex observation remains required before merge-prepared handoff.
