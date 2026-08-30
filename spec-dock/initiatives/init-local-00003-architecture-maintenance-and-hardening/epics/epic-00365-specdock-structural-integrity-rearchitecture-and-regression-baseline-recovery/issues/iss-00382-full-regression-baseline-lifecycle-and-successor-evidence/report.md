---
種別: レポート（Issue）
ID: "iss-00382"
タイトル: "Full Regression Baseline Lifecycle And Successor Evidence"
関連GitHub: ["#382"]
最終更新: "2026-08-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00365", "init-local-00003"]
---

# Result Summary

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

repository-only Full Regression baseline authorityを`scripts/quality/`へ実装した。distribution production/runtime/assets、public CLI/JSON、managed distribution recoveryには変更していない。

- schema 1を全row activeとして互換読取し、schema 2の`active`、`resolved/fixed-in-place`、`resolved/superseded`、synthetic `retired` evidenceを一つのpure evaluatorで判定する。
- pytest guardとstandalone runnerは同じ`CandidateObservation` / `BaselineEvaluation`を使う。adapter側にlifecycle policyを持たせない。
- pytest hook observation JSONでskip、xfail、xpass、setup/call/teardown errorを明示し、JUnitからnormal passを推定しない。
- Issue 368 schema 1 ledgerのhistorical node/signature/rationale/orderをdigestで固定し、26 active＋retained-skill 1 resolved/supersededへ移行した。retired row/providerは追加していない。
- root provider Full Regression workflowを`uv run python -m scripts.quality.verify_full_regression --shards 4`へcutoverし、Issue 368 verifier artifactへのcanonical runtime dependencyを除いた。historical artifact自体は変更していない。

### TDD milestones

| Milestone | RED | GREEN |
|---|---|---|
| M1 pure evaluator | `ModuleNotFoundError: No module named 'scripts.quality'` | evaluator unit 36 passed、ruff、mypy |
| M2 adapters/runner | `ImportError: cannot import name 'build_candidate_observation'` | lane 29 passed、manual shard compatibility、ruff、mypy |
| M3 ledger migration | schema 1のためmigration invariant failure | schema 2 projection digest、26 active、1 resolved、0 retired |
| M4 workflow cutover | canonical runner / old path absence assertion failure | provider workflow focused 19 passed、provider structural 2 passed |
| M5 quality repair | `make lint` format 3 files / mypy 4 errors | formatter適用とtyped test boundaryによりlint green |

## Verification

candidate freeze前に次を確認した。

- `make lint`: ruff check / ruff format check / mypy 175 source files pass
- `uv run pytest tests/unit/test_full_regression_baseline.py tests/unit/test_provider_test_lanes.py`: 67 passed
- `uv run pytest tests/unit/infra/test_init_update.py -k 'provider_only_workflow or workflow_seed or issue_68'`: 2 passed, 197 deselected
- ordinary `uv run pytest`: 1569 passed, 1134 skipped
- `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=228`

exact candidate SHAに対するcanonical Full Regression、Strict review、GitHub CI/PR receiptはtracked reportを変更しないpost-freeze evidenceとして記録する。finding修正またはtracked report修正でSHAが変わった場合はnew candidateとして再取得する。

## Residual Risks / Follow-ups

- current ledgerにretired rowはない。将来追加するownerはaccepted authorityに対応するrow-specific probeとadapter testを同じ変更で追加し、evidence未取得をfail closedにする必要がある。
- Full Regressionはheavy post-merge laneであり、ordinary PR merge-blocking fast gateへ変更していない。
- Issue 368 verifierはhistorical evidenceとして残るが、workflow/manual canonical routeのfallback authorityではない。
- Issue 382のexact candidate Full Regression、Strict pass、merge-ready PR、人間mergeは未完了。Issue 372はそれらが成立するまでblockedのままとする。
