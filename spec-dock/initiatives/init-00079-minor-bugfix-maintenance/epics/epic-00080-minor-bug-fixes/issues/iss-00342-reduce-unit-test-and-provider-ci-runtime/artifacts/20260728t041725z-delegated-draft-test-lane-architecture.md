---
種別: delegated architecture evidence
ID: "20260728t041725z"
タイトル: "Delegated Draft Test Lane Architecture"
状態: "draft"
作成者: "system-architect"
最終更新: "2026-07-28"
親: ["iss-00342"]
template: "blank"
authority: "raw"
created_by_role: system-architect
scope_id: iss-00342
source_paths:
  - "requirement.md"
  - "design.md"
  - "plan.md"
  - "report.md"
  - "artifacts/20260728t025412z-adr-separate-fast-merge-gate-and-full-regression-execution.md"
  - "artifacts/20260728t015759z-research-unit-test-and-provider-ci-runtime-investigation.md"
  - ".github/workflows/provider-ci.yml"
  - "pyproject.toml"
  - "Makefile"
  - "README.md"
  - "AGENTS.md"
  - "tests/cli_runtime/harness.py"
  - "tests/unit/cli/test_cli_smoke.py"
  - "tests/unit/infra/test_init_update.py"
intended_targets:
  - "design.md"
  - "plan.md"
adoption_status: unreviewed
reflected_to: []
diff_guard_result: passed
specialist_status: usable
---

# 20260728t041725z Delegated Draft Test Lane Architecture

この文書は、`iss-00342` のtest-lane設計をmain orchestratorがcanonical `design.md` / `plan.md`へ統合するためのdelegated evidenceである。accepted authority、canonical adoption、phase promotion、reviewer pass、implementation readinessは主張しない。

## 1. Requirement Coverage

| Design ID | 設計差分 | 主な要件 |
|---|---|---|
| `DES-TL-001` | 全itemを`fast` / `full_regression`へexactly-one分類する | BH-001/002、AC-001/002/007 |
| `DES-TL-002` | 7 required-fast nodeでCLI/parity obligationを固定する | AC-006 |
| `DES-TL-003` | bare fast、明示fast、明示fullのstable commandを定める | AC-001/002、外部コマンド契約 |
| `DES-TL-004` | PR fast workflowと`provider-tests` identityを維持する | BH-003、AC-003 |
| `DES-TL-005` | `main` / manual full workflowとconcurrencyを定める | BH-004〜006、AC-004/005/009 |
| `DES-TL-006` | collection、coverage、routing、性能の検証を定める | AC-007〜009 |
| `DES-TL-007` | post-merge failure、rerun、rollbackを定める | BH-007、AC-010/011 |

## 2. Existing Context Findings

- current full collectionは`C=2696`。
- path別item数は`tests/cli_runtime/ = 1269`、`tests/unit/infra/test_init_update.py = 553`、`tests/manual_tests/ = 215`、`tests/integration/ = 3`、その他`656`。
- `tests/unit/infra/test_init_update.py`を除くunit実行は既存調査で5.45秒、`tests/cli_runtime`は1,228.31秒。
- 現行`pyproject.toml`は`testpaths = ["tests"]`だけで、root / `tests/`に`conftest.py`はない。
- 現行`.github/workflows/provider-ci.yml`は`push`と`pull_request`の双方から`provider-tests`を起動し、bare `uv run pytest`を実行する。
- accepted ADRはPR/default fast、manual / `main` post-merge full、no schedule、full failureのpost-merge visibilityをauthorityとして固定している。
- prior `iss-00160` ADRにより、local subprocess、filesystem、tempdir、local git、stub `gh`を遅さだけでintegrationへ再分類してはならない。

### Current source hashes

| Source | SHA-256 |
|---|---|
| `requirement.md` | `995fc453b3dac18f7b56106eadc3b25bebc0b514e5a78353cf5c9b0669436117` |
| `design.md` | `46da36e23503bb34aab558fadda78bce7e70ca77fcad0cd250024eeb23948e82` |
| `plan.md` | `50aecab18b17a67f25867c7ff398ce8b69136b1ca225949b4efa110ca52bd8db` |
| `report.md` | `e7846bdeb3dbbb7f6298909ba73fa23851ced03db44422c57fb057f25e727824` |
| accepted ADR | `30d171a12c4ea3b915c8545cce5e3c13c22cf5f264ce62ad16079a44c40dd484` |
| research | `10cb4396962b4a396ff5aa1ef71015e466c5aa612c9eeb55105a50ffb2914f0d` |
| `.github/workflows/provider-ci.yml` | `1c5ae8807d9911ce1949d54e1ade906d685c230e4eca9670296bb8d7e73db36d` |
| `pyproject.toml` | `d6347e896a753079da2fcaf4b43e273baebe33fe5cba23b1d2599d2438bf523e` |
| `Makefile` | `dbdb4868a682f1730f0f15523008e76bfbccf3541a0b8d2d22f3b310a37e206c` |
| `tests/unit/cli/test_cli_smoke.py` | `211fdcf46485477dc075eaa9f1cbbbc17524c53fcf7c5b52ce1159a8d9df56b7` |
| `tests/unit/infra/test_init_update.py` | `2a581172839417dcac9040aed31e662661c8fc9bc412795018353cc7a26e8384` |
| `tests/cli_runtime/harness.py` | `74cdf88585eedc7949d1fc826baa4b9fe95957d6baf252f59195103e328762cd` |

## 3. Design Decisions

### 3.1 Lane algebra

`C`をformal full collection、`F`をfast items、`H`をfull-regression items、`U`を未分類itemsとする。

```text
F ∩ H = ∅
F ∪ H = C
U = C - (F ∪ H) = ∅
```

初期snapshotは`C=2696 / F=661 / H=2035 / U=0`。完了時は最終統合状態のnode ID集合をauthorityとする。

### 3.2 Heavy prefixes

```text
tests/cli_runtime/
tests/integration/
tests/manual_tests/
tests/unit/infra/test_init_update.py::
```

heavy prefix外の新規testは既定で`fast`、prefix内または明示`full_regression`付きは`full_regression`とする。

### 3.3 Corrected hook invariant

`tests/conftest.py`の`pytest_collection_modifyitems`は、**今回収集されたitemsだけ**をexactly-one laneへ分類する。

- collected itemが`fast`と`full_regression`の両方を持つ場合はcollection error。
- required-fast nodeが今回のcollectionに含まれる場合は`fast`へ分類し、明示`full_regression`との衝突はerror。
- heavy prefix配下のcollected itemは、required-fast例外でない限り`full_regression`。
- その他のcollected itemは`fast`。
- hook完了時、各collected itemはちょうど一方のmarkerだけを持つ。

focused / partial collectionでは、7 required-fast node全件の存在や`|H| > 0`を要求してはならない。例えば`pytest tests/unit/cli/test_cli_smoke.py`は2 required-fast nodeだけを収集し、heavy itemが0件でも正しい。

次のglobal invariantは、repo-root full collectionを行う専用contract test / validationでだけ検査する。

- required-fast 7 nodeがすべて存在する。
- `H`が空でない。
- `F ∩ H = ∅`、`F ∪ H = C`、`U = 0`。
- default / formal fast collectionに`H`が含まれない。
- formal full collectionが`F ∪ H`と一致する。

## 4. Alternatives Considered

| Option | 判断 | 理由 |
|---|---|---|
| pytest marker + default `addopts` | 採用候補 | pytest標準selectorでbare fastとformal fullを表現できる |
| custom `--full-regression` filtering hook | 非採用 | 独自flag、独自deselection、markerとの優先順位を保守するsurfaceが増える |
| 全node/path manifest | 非採用 | 新規testのsilent omissionと巨大inventory driftを生みやすい |
| 1 workflow + event conditionals | 非採用 | routing inspectionとcheck identityが複雑になる |
| PR workflow +独立full workflow | 採用候補 | trigger、責任、failure semanticsが明確になる |

## 5. Boundary / Contract Model

```text
pytest collection
  -> tests/conftest.py: collected itemsをexactly-one分類
      -> F: bare/default/local fast/PR
      -> H: explicit fullのみ
  -> Makefile: selector expressionのstable facade
      -> Provider CI / provider-tests: pull_request -> lint + F
      -> Provider Full Regression: main push / workflow_dispatch -> F ∪ H
```

test-lane policyはprovider repositoryのtest / workflow operationに閉じ、product runtime behavior、consumer scaffold、external repository pipelineを変更しない。

## 6. Dependency Analysis

- `tests/conftest.py`: item classificationのowner。workflow routingやperformance policyは持たない。
- `pyproject.toml`: marker登録、`--strict-markers`、bare default `-m fast`。
- `Makefile`:利用者とworkflowが呼ぶfast/full commandのsingle facade。
- workflow: raw marker式を複製せずMake targetを呼ぶ。
- `README.md` / `AGENTS.md`: bare fast、formal full、post-merge failure operationを利用者へ説明する。
- global collection contract test: hookのlocal invariantを、repo-wide completenessへ昇格して検証する。

Deletion tests:

- classifier削除でfull-regression inventory / global invariant testが失敗する。
- required-fast node削除・renameでglobal contract testが失敗する。
- full workflow削除でevent truth-table testが失敗する。
- `provider-tests` renameでidentity contract testが失敗する。

## 7. Source of Record

- durable policy: accepted ADR。
- item classification: `tests/conftest.py`。
- pytest default: `pyproject.toml`。
- stable local commands: `Makefile`。
- PR merge gate: `.github/workflows/provider-ci.yml`。
- post-merge/manual full: `.github/workflows/provider-full-regression.yml`。
- contributor operation: `README.md` / `AGENTS.md`。
- actual counts、durations、SHA、skip delta、run results: `report.md`。

Provider-only workflowsは`src/spec_dock/assets/install_root/`へshipしない。

## 8. Data Flow / Domain Model / Interface Contract

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["--strict-markers", "-m", "fast"]
markers = [
  "fast: default provider test lane used during development and pull requests",
  "full_regression: long-running provider regression excluded from the default lane",
]
```

```make
.PHONY: lint test-provider-fast test-provider-full

test-provider-fast:
	uv run pytest -m fast

test-provider-full:
	uv run pytest -m "fast or full_regression"
```

Interface semantics:

- bare `uv run pytest`: fast。
- `uv run pytest tests/unit`: collected unit itemsのうちfastだけ。partial collectionでもglobal inventory errorを起こさない。
- `make test-provider-fast`: PRと同じfast contract。
- `make test-provider-full`: `F ∪ H`のformal full contract。
- `uv run pytest -m full_regression`: diagnostic heavy-only selectorでありformal fullではない。

## 9. File / Module Change Plan

| Path | 目的 |
|---|---|
| `tests/conftest.py` | collected-item classifier |
| `pyproject.toml` | markers / default fast |
| `Makefile` | stable fast/full commands |
| `.github/workflows/provider-ci.yml` | PR-only lint + fast、identity維持 |
| `.github/workflows/provider-full-regression.yml` | main/manual full |
| `tests/unit/test_provider_test_lanes.py`または同等 | global collection contract |
| `tests/unit/infra/test_init_update.py` | workflow routing、non-shipping、required-fast contract |
| `README.md` / `AGENTS.md` | commands、failure operation、rollback |

`src/spec_dock/assets/**`、product runtime code、canonical docsは本delegated artifactの変更対象外。

## 10. Migration / Compatibility / Rollback

- `Provider CI` workflow nameと`provider-tests` job key/nameを維持する。
- PR workflowは`pull_request`だけをtriggerにし、`make lint`と`make test-provider-fast`を実行する。
- 独立full workflowは`main` pushと`workflow_dispatch`だけをtriggerにし、scheduleを持たない。
- selector omission、required check欠落、許容不能なescapeが見つかった場合、PR commandを`make test-provider-full`へ戻す。
- bare defaultが危険なら`pyproject.toml`のdefault `-m fast`を一時撤回する。
- rollback後もmarkers、manual full command、post-merge full workflow、計測証跡を保持する。

## 11. Observability

- full failureに`continue-on-error`を付けず、red Actions runとして残す。
- workflow名、event、SHA、duration、counts、failed node、logを確認可能にする。
- failure ownerはmaintainer。
- local reproductionは`make test-provider-full`。
- 通常対応はforward fixまたはActions rerun。自動rollback、自動Issue作成、既存mergeの遡及blockは行わない。
- initial cutoverで新しいhard timeoutを設けず、120秒 / 10分の非blocking targetをhard SLAへ変更しない。

## 12. Test Strategy

### Required-fast node IDs

1. `tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_legacy_flag_reports_parser_error`
2. `tests/unit/cli/test_cli_smoke.py::TestCliSmoke::test_active_set_by_id_succeeds_through_runtime_subprocess`
3. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_docs_match_provider_assets`
4. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_checked_in_dogfooding_mirror_templates_match_provider_assets`
5. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_workflow_seed_matches_repo_root_ci_workflow`
6. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_68_provider_only_workflow_is_not_shipped_via_install_root`
7. `tests/unit/infra/test_init_update.py::TestInitUpdate::test_issue_71_checked_in_dogfooding_agent_tooling_parity_matches_install_root_assets`

### Collection and routing validation

- focused collection: subsetだけで成功し、global required-fast / `H > 0` guardを発火しない。
- full collection: `C=F∪H`、disjoint、`U=0`、required-fast全件、`H>0`。
- default / explicit fast: heavy実行0。
- formal full: current full node IDsと一致。
- workflow truth table: PR=yes/no、non-main push=no/no、main push=no/yes、dispatch=no/yes、schedule=no/no。
- before / after full node ID、skip / xfail、test deletion、assertion deletionのdeltaを記録する。

### Corrected AC-008 execution

AC-008のauthorityは、最終統合状態・同一checkout・Python・cache条件で行う**3 paired local runs**である。

```text
pair 1: fast run -> full run
pair 2: fast run -> full run
pair 3: fast run -> full run
```

各pairで`fast elapsed < full elapsed`を確認する。この3回のfull runをfinal full execution evidenceとして兼用し、別の「final full 1回」を追加して4回目にしてはならない。実装途中ではfocused testsとcollection-only validationを使い、30〜40分full実行は最終統合状態へまとめる。

PR `provider-tests`は別途3 runのstarted-to-completed elapsedを記録する。

## 13. ADR Candidates

追加ADR候補なし。marker、Make target、2-workflow topology、corrected hook scopeは、accepted fast/full policyをIssue-localに具体化する可逆設計である。

## 14. Risks

- global completenessをhookへ埋め込むとfocused testが常に失敗する。
- hookがpartial collectionで`H > 0`を要求すると、fast-only focused testが実行不能になる。
- heavy prefix外の遅い新規testはfastへ入るため、duration regressionと明示`full_regression` reviewが必要。
- required-fast nodeのrenameはglobal contract failureになるため、inventory更新と代替contract reviewを同時に行う。
- direct `pytest -m ...`はdefaultをoverrideできる。正式利用者contractはMake targetに限定する。
- branch protection現物は403で未観測のため、workflow / job identityを保守的に維持する。
- full実行回数を「3 paired」と「final 1回」で二重計上すると、時間とAC interpretationが矛盾する。

## 15. Requirement Clarification Requests

owner判断が必要な新規requirement gapはない。

設計統合時に修正すべき既存記述:

- global required-fast存在と`H > 0`はhook invariantではなく、full collection contract validationへ移す。
- AC-008は3 paired local fast/full runs。別のfinal full 1回を追加せず、3 full runsをfinal evidenceとして兼用する。

これらはaccepted policyを変更せず、focused-test usabilityとAC-008整合を修正する。

## 16. Integration Notes for Main Orchestrator

- 本artifactのcorrected hook invariantを`design.md`の`DES-TL-001`、failure model、test strategyへ統合する。
- 3 paired runsの扱いを`design.md`の`DES-TL-006`と`plan.md`の最終verification順序へ統合する。
- canonical採用はmain orchestratorがEvidence Adoption Ledgerへ記録し、fresh `spec-reviewer`へ提示する。
- 本artifactは`adoption_status: unreviewed`であり、自己採用claimを持たない。
- lightweight provenance: current local sources、live collection、focused smoke実測を使用。leaf sub-agent evidenceは使用していない。

### Recommended next action

1. main orchestratorが本artifactを採否判定する。
2. 採用する場合、canonical design / planの上記2点だけをsurgicalに修正する。
3. fresh `spec-reviewer`でrequirement traceability、focused collection、AC-008を再確認する。
4. 実装はreviewer pass後に開始する。

### Validation performed

- `uv run pytest --collect-only -q -p no:cacheprovider`: `2696 tests collected`。
- CLI required-fast 2 node: `2 passed in 2.00s`。
- workflow/parity required-fast 5 node: `5 passed in 0.07s`。
- artifact作成前にcanonical `requirement.md` / `design.md` / `plan.md` / `report.md`のSHA-256を記録した。
- post-write canonical hash再照合で4 canonical hashesがbaselineと一致した。
- `git diff --check`: exit 0、diagnosticなし。

### Diff Guard

- baseline canonical hashes: 「Current source hashes」表の4 canonical rows。
- allowed delta: 本artifact 1ファイルの追加・更新のみ。
- post-write canonical hashes:
  - `requirement.md`: `995fc453b3dac18f7b56106eadc3b25bebc0b514e5a78353cf5c9b0669436117`
  - `design.md`: `46da36e23503bb34aab558fadda78bce7e70ca77fcad0cd250024eeb23948e82`
  - `plan.md`: `50aecab18b17a67f25867c7ff398ce8b69136b1ca225949b4efa110ca52bd8db`
  - `report.md`: `e7846bdeb3dbbb7f6298909ba73fa23851ced03db44422c57fb057f25e727824`
- canonical target delta: none。4 hashesはbaselineと一致。
- result: `passed`。

`specialist_status: usable`

No canonical edit, final authority, promotion, reviewer-pass, or user-dialogue ownership is claimed.
