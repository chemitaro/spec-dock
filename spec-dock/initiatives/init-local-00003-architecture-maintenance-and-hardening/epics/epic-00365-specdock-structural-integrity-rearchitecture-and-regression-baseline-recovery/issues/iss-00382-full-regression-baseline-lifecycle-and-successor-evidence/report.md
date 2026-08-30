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
| M6 ledger authority cutover | root authority files absent、canonical sources still referenced Issue 368 artifact | root authority 2 files、historical SHA-256 freeze、provider lane 32 passed、ordinary pytest 1570 passed |

### M6 authority cutover追記（pre-freeze不整合の訂正）

pre-freeze Full Regression candidate SHA `8b66840688da20b686399d7bc6f05d6bb77ac5e5`について、既存のverification結果自体は確認済みだった。しかしその後、canonical `tests/conftest.py` と `scripts/quality/verify_full_regression.py` がIssue 368配下のledger/timing weightsを直接参照していることを確認した。これはcanonical authorityをrepository rootへ置く設計との不整合であり、M6として追加修正した。

- 現行schema 2 ledger（26 active、1 resolved/superseded、0 retired）と現用timing weightsを`full-regression-ledger.json` / `full-regression-timing-weights.json`としてrepository rootへ移した。
- pytest guard、canonical runner、test helperの既定pathをroot authorityへ変更し、Issue 368配下へのcanonical runtime dependencyを除いた。workflowは既にcanonical runnerを参照していたため変更していない。
- Issue 368配下のledgerは親固定点 `48b34e23283f9270d671d1e1eb3c3a3365fe1856`のhistorical schema 1内容へ復元した。timing weightsは親固定点から変更されていないことを確認した。provider lane testは両artifactのSHA-256を固定して、将来の書換えをfail closedにする。

従前のOutcomeにある「historical artifact自体は変更していない」は、M6 cutover前の状態を記録した履歴上の記述であり、M6では一時的にschema 2へ移行されていたIssue 368 ledgerを親固定点へ復元した、というのが確定した事実である。過去のverification結果や実施済みmilestoneは改変せず、この追記で時系列と現在のauthorityを明示する。

M6 cutover後の確認結果:

- RED: `test_full_regression_authority_is_root_and_issue368_history_is_frozen` はroot ledger不在で失敗した。
- GREEN: provider laneのledger/migration/full-regression選択20 passed、provider lane全体32 passed、pure evaluator 36 passed。
- `make lint`: ruff check、ruff format check、mypy（175 source files）がすべてpass。
- ordinary `uv run pytest`: 1570 passed、1134 skipped（56.28秒）。
- `./spec-dock/scripts/spec-dock validate`: `spec-dock: ok (validate) nodes=228`。
- M6ではFull Regression本体を実行していない。authority cutover後のcandidateでのheavy実行はprimaryがStep 9で行う。

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
