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
| M7 Strict前静的監査P1修復 | root ledger metadataの旧runner command assertion failure | canonical command 1行修正、adapter equivalence contract test追加 |
| M8 Provider parity hermetic build dependency preparation repair | macOS parity jobで16件が`Missing dependencies: setuptools>=69`、native venvのpip `--target`経路がstale setuptoolsを置換できない | native build-backend pip経路修正、fallback characterization、artifact-build unit 5 passed、heavy parityは15 passed/dirty-status 1 failure |

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

### M7 Strict前静的監査追記（M6 receiptの扱い）

M6 commit `22309ce0932c3233385d5cdefe317e867cfd3c52`に対するFull Regression verified結果を確認した後、Strict review前の静的監査で2件のP1を検出した。

- root `full-regression-ledger.json`の`commands.current_full`が旧Issue 368 verifierを指していたため、exact canonical command `uv run python -m scripts.quality.verify_full_regression --shards 4`をassertするRED testを追加し、metadataの該当1行を修正した。これはAC06のcanonical command metadata違反であり、Full Regressionの結果そのものを変更する修正ではない。
- pytest adapterの`build_candidate_observation`とstandalone adapterの公開JSON境界について、同一typed observationをround-tripし、同一baselineへの`BaselineEvaluation.to_dict()`を直接比較するcontract testを追加した。既存のshared evaluator/JSON実装が同値を満たしていたため、production behaviorは変更していない。
- M7の変更により`22309ce...`時点のFull Regression receiptはstaleである。M7後のcandidate SHAに対するFull RegressionはprimaryがStep 9で再取得する。

M7ではP2として扱ったhistorical verifier testのdirect loadとoutcome set境界の重複は変更していない。前者はhistorical compatibility evidence、後者はJSON input validationとpolicy domain validationの別責務であり、今回のP1修復範囲外である。

### M8 Provider parity hermetic build dependency preparation repair追記

PR #383 Provider CI run `33315553126`のmacOS parity job `99268220215`で、candidate wheel fixture setupの16件すべてが`Missing dependencies: setuptools>=69`でERRORとなり、Ubuntu parityはfail-fastでcancelledになった。根因は、native build venvのpip-present経路がbuild backend requirementsをvenv自身のsite-packagesへ`pip install --target`しており、seeded setuptools 68.2.2のdist-infoを置換できなかったことである。local wheelhouseには`setuptools==75.8.0`が存在する。

- RED: `uv run pytest --run-full-regression --full-regression-shard tests/unit/infra/test_init_update.py -k 'native_build_venv_installs_backend_requirements_in_place or pip_unavailable_fallback_keeps_target_install_semantics'`でnative command assertionが失敗した。観測された旧commandは`--target <venv>/lib/python3.12/site-packages`を含み、fallback testはpassした。
- GREEN: build-backend専用helperを追加し、native pip probe成功時のcommandを`python -m pip install --no-cache-dir --upgrade --no-index --find-links <local wheelhouse> <exact pins>`（`--target`なし）へ変更した。pip unavailable経路は既存generic target installerのまま維持した。focused 2 passed、Issue 69 artifact-build unit group 5 passed、`make lint` pass。
- 指定heavy command `uv run pytest --run-full-regression --full-regression-shard tests/integration/test_epic_00343_distribution.py`は、15 passed、1 failed（`test_tc_346_s01_001_candidate_wheel_receipt`）だった。唯一のfailureはcandidate fixtureが未commitの`tests/unit/infra/test_init_update.py`変更をpre/post dirty statusとして検出したもので、残り15件のbuild/install/distribution semantic assertionsはpassした。testやworkflowを変更して隠していない。
- workflow、pyproject、wheelhouse、distribution production/runtime/assets、integration testは変更していない。manual Full Regression run `33315602048`は旧SHAの結果であり、M8後はstaleとしてprimaryが再取得する。

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

### M9 external certification evidence materialization（追加）

M8時点の「exact candidate Full Regression、Strict pass、merge-ready PR、人間mergeは未完了」という記録は、その時点の履歴として変更しない。以下は、その後に取得されたcode candidate `46d16fd0a0cfa286db0bc4c292b5d5b73190a10f`に対するM9の外部認証であり、M8の暫定未完了状態をsupersedeする現在の証跡である。

- Provider CI run `33322223928`は、provider-tests pass（2m33s）、macOS parity pass（1h6m4s）、Ubuntu parity pass（1h13m44s）だった。
- Provider Full Regression run `33323717175`はpass（1h7m36s）となり、artifact id `9736472371`、name `provider-full-regression-evidence`を生成した。`result.json`はcandidate SHAが`46d16fd0a0cfa286db0bc4c292b5d5b73190a10f`とexact matchし、`status=verified`、`evaluation.verified=true`、active 26／resolved 1／retired 0／violations 0だった。result JSONのSHA-256は`e1b77c0294ff383d8ac71af6f78540508bae28b6c71a7f2d9d1952a16d229782`である。
- Strict session `required-strict-github-connector-verificati-503`は`review_status=pass`、findings 0、confidence 0.95だった。Strict JSONのSHA-256は`0d3ae1fd8b86d4b5e0c49f00379e987eb538128fd7101ce8979a10303e26d4da`である。
- PR #383は、このreviewed candidateにおいてOPEN、non-draft、MERGEABLE/CLEANである。人間によるmergeはまだ実施していない。

このM9追記はtrackedなplan/reportを変更するため、新しいdoc-only candidate SHAを生成する。したがって、上記のCI、Full Regression、Strictは`46d16fd...`に対する証跡であり、追記後の新HEADに対する証跡ではない。primaryはこの追記をcommit/pushした後、新しいexact SHAでCI、Full Regression、Strictを再実行してからmerge判断を行う。これにより、認証対象と文書追記後candidateの自己参照を避ける。Issue #372の再開およびIssue 382/372のfinishは、人間mergeを含む残存ライフサイクル条件の成立後に行う。
