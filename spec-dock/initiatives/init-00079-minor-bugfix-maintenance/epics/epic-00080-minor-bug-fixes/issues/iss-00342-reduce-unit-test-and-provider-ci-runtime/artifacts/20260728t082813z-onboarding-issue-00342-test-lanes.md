---
種別: onboarding
ID: 20260728t082813z-onboarding
状態: completed
親: [iss-00342]
authority: explanatory
derived_from:
  - requirement.md
  - design.md
  - plan.md
  - report.md
  - artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md
reflected_to: []
created_by_role: doc-writer
---

# iss-00342 オンボーディング: テストレーンを理解する

## 30秒要約

このIssueは、通常の開発とPR確認が遅すぎる問題を扱います。現在の完全なテストは2,696件あり、PRのProvider CIは中央値38.1分です。

結論は、テストを削らずに二つのレーンへ分けることです。日常作業とPRは高速な`fast`、完全な回帰確認は明示的な手動実行と`main`へのmerge後に`full`で行います。現在はplanning-readyですが、execution admissionは未取得です。コード変更、`issue start`、commit、pushはまだ行っていません。

## なぜ必要か

待ち時間の中心はテストです。実測では次の状態でした。

- full collection: 2,696 tests
- `tests/unit`: 380.19秒。そのうち`tests/unit/infra/test_init_update.py`が約98%を占める
- `tests/cli_runtime`: 1,228.31秒（約20分28秒）
- Provider CI: 直近100件の成功runの中央値38.1分

そのため、小さな変更でも完全回帰をPRのmerge blockerとして待つ構造になっています。一方で、遅いテストを消す、`skip`にする、あるいは単に`tests/integration`へ移すことは、検証範囲を見えにくく弱めるため採用しません。

## 採用方針: fast と full の二レーン

`fast`は通常開発とPRのためのレーンです。短時間のunit testsに加え、provider / dogfooding parityと代表的なCLI contract smokeを残します。高速化のために重要な境界を外すのではなく、必要な代表例を明示して残す考え方です。

`full`は完全回帰レーンです。`fast`を含み、長時間テストも含めた論理的な全テスト集合を実行します。PRのmerge前には待たせず、必要なときの手動実行と`main`へのmerge後の事後検知に使います。fullの失敗は赤いまま可視化し、maintainerがrerunまたはforward fixで対応します。既に済んだmergeを遡ってblockしません。

| 起点 | 実行するレーン | 意味 |
|---|---|---|
| local default / fast | `fast` | 通常開発。bare `uv run pytest`、`uv run pytest tests/unit`、`make test-provider-fast` |
| local manual full | `full` | 意図的な完全回帰。`make test-provider-full` |
| PR (`pull_request`) | `fast` | `Provider CI` / `provider-tests`をmerge gateとして維持 |
| `main` push | `full` | merge後の事後検知 |
| `workflow_dispatch` | `full` | GitHub Actionsからの明示手動実行 |
| `schedule` / cron | 実行しない | 非採用。追加しない |

non-`main` の`push`では、どちらのテストworkflowも起動しない計画です。

## 実装イメージ（まだ未実装）

実装ではpytest markerとcollection classifierを使い、各test itemを`fast`または`full_regression`のちょうど一方に分類します。全件を集めたときに、両者の重複も未分類もないことを機械的に検証します。

次の7 nodeをrequired-fastとして固定します。1〜2はCLI smoke、3〜7はheavyな`test_init_update.py`内の例外です。CLIの成功・失敗の代表例と、provider / dogfooding parity、workflowの非配送をPR前に確認するためです。

1. `tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_legacy_flag_reports_parser_error`
2. `tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_by_id_succeeds_through_runtime_subprocess`
3. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets`
4. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets`
5. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_workflow_seed_matches_repo_root_ci_workflow`
6. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_provider_only_workflow_is_not_shipped_via_install_root`
7. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`

コマンド入口はMake targetに集約します。`make test-provider-fast`はPRと同じfast、`make test-provider-full`は全体を明示的に選ぶformal full commandです。workflowはPR用の`.github/workflows/provider-ci.yml`と、`main` / manual full用の`.github/workflows/provider-full-regression.yml`に分離する計画です。`Provider CI` / `provider-tests`という既存のPR check identityは維持します。

## 主な変更箇所と担当ロール

| 対象 | 役割 |
|---|---|
| `tests/conftest.py`、lane contract tests、既存parity tests | `dev-coder`: 分類と検証をtest-firstで実装 |
| `pyproject.toml`、`Makefile`、2つのprovider workflow | `utility-worker`: marker、コマンド、event routingを限定変更 |
| `README.md`、`AGENTS.md` | `doc-writer`: 利用方法と失敗時の運用を説明 |
| `report.md` | main orchestrator: 実測・レビュー・完了証跡を記録 |

`src/spec_dock/**`、consumerの`spec-dock/**`、branch protection、workflow permissions、secretsは対象外です。provider-only workflowをconsumerへshippingしません。

## 実装の進み方

1. baselineを固定し、全node、skip / xfail、known flakyを記録する。
2. classifierとpytest selectorをtest-firstで追加し、fast/fullの集合契約を確認する。
3. Make targetsを追加し、既定・fast・fullの入口を揃える。
4. PR fastと`main` / manual fullのworkflow routingを分け、check identityとno-scheduleを検証する。
5. lint、fast、collection、ローカル計測を確認する。formal fullは最終の3組のpaired runへ集約する。
6. README / AGENTSを更新し、fresh reviewと最終品質ゲートを通す。
7. PRでfastを確認してmerge-readyまで進める。mergeは人だけが行い、その後に`main` fullの結果とIssue lifecycleを確認する。

## やってはいけないこと

- `skip`、`xfail`、test deletion、assertion weakeningで速く見せること
- `schedule` / cronを追加すること
- provider-only workflowをconsumer scaffoldへshippingすること
- branch protectionを変更すること
- agentが自動mergeすること
- full failureを隠す、またはmerge済みの変更を遡ってblockしたものとして扱うこと

## 完了の見方

完了時には、PRでは`provider-tests`のfast checkが通り、`main`では独立したfullが走ります。fullはfastを含む全テスト集合のままで、分類漏れや重複がありません。workflowに`schedule`はなく、full failureはGitHub Actionsで失敗したSHA・test・log・再実行方法を追える状態で残ります。

もしrequired check identityの欠落やselector漏れが分かれば、PRのコマンドを`make test-provider-full`へ戻せるようにします。これは「速さよりも検証契約を優先する」ためのrollbackです。

## 明日最初に読む・確認するもの

1. [requirement.md](../requirement.md): 目的、対象外、受け入れ条件
2. [design.md](../design.md): fast/fullの集合、7 required-fast nodes、event routing
3. [plan.md](../plan.md): 実装順、担当、検証とhuman merge boundary
4. [ADR](20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md): なぜ二レーンとno-scheduleを選んだか

現在のplanning guidanceは`ready` / `planning-ready` / `assurance-valid`です。ただし`may_execute_approved_plan=false`であり、実装開始のadmissionはまだ別途必要です。`issue start`も実装も未実施です。

## 正本リンク一覧

- [Issue requirement](../requirement.md)
- [Issue design](../design.md)
- [Issue plan](../plan.md)
- [Issue report](../report.md)
- [Accepted ADR](20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md)
