---
種別: 設計書（Issue）
ID: "iss-00382"
タイトル: "Full Regression Baseline Lifecycle And Successor Evidence"
関連GitHub: ["#382"]
状態: "planned"
最終更新: "2026-08-30"
依存: ["requirement.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00382 Full Regression Baseline Lifecycle And Successor Evidence — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

historical baselineを消さず、current candidateの観測を一つのpure evaluatorで判定する。repository quality policyをdistribution packageへ混入させず、pytest guardとstandalone Full Regression runnerを薄いadapterにする。

## Current / Target

現状は`tests/conftest.py`とIssue 368 artifact `verify-full-regression.py`がledger path、schema validation、failure normalization、signature照合を重複実装する。schema 1は同じfailureの継続だけを成功とするためsuccessor evidenceを表現できず、workflowもhistorical Issue artifactをcanonical executableとして直接参照する。

Targetは次である。

```text
pytest reports ─┐
                ├─ CandidateObservation ──> pure evaluator ──> BaselineEvaluation
shard hook JSON ┘                                      │
                                                       ├─ pytest guard adapter
baseline schema 1/2 ──> pure parser ───────────────────└─ standalone runner
```

canonical authorityは`scripts/quality/`とrepository-root ledgerである。Issue 368 artifactはhistorical evidenceとして固定し、workflow/runtime fallbackにしない。

## 責務・Interface

- `scripts/quality/full_regression_baseline.py`: filesystem、Git、subprocess、pytest、JUnitをimportしない。schema 1/2 parse、failure normalization/signature、baseline evaluationを一意に所有する。
- `scripts/quality/verify_full_regression.py`: shard process、observation JSON、artifact、CLI exit/renderingだけを所有する。
- `tests/conftest.py`: collection/report eventを観測しshared evaluatorへ渡す。lifecycle分岐を持たない。

```python
class BaselineContractError(ValueError): ...

@dataclass(frozen=True)
class CandidateObservation:
    collected: tuple[str, ...]
    executed: tuple[str, ...]
    outcomes: Mapping[str, Literal[
        "passed", "failed", "skipped", "xfailed", "xpassed", "error"
    ]]
    failure_signatures: Mapping[str, str]
    retirement_evidence: Mapping[str, RetirementEvidenceObservation]

@dataclass(frozen=True)
class RetirementEvidenceObservation:
    checked: bool
    outcome: Literal["absent", "present", "unknown"]

@dataclass(frozen=True)
class BaselineEvaluation:
    verified: bool
    active_verified: tuple[str, ...]
    resolved_verified: tuple[str, ...]
    retired_verified: tuple[str, ...]
    violations: tuple[BaselineViolation, ...]

def parse_baseline(payload: Mapping[str, object]) -> FullRegressionBaseline: ...
def normalize_failure_message(message: str, repository: Path) -> str: ...
def failure_signature(message: str, repository: Path) -> str: ...
def evaluate_baseline(
    baseline: FullRegressionBaseline,
    observation: CandidateObservation,
) -> BaselineEvaluation: ...
```

adapterは`verified`とtyped violationsをrenderするだけで判定を再実装しない。

## data / failure

全rowはhistorical `nodeid`、`fixed_point_signature_sha256`、`rationale`を保持する。schema 1は全rowを`active`として互換読取する。schema 2 lifecycleは以下に限定する。

- `active`: old nodeがexact signatureでfailする。
- `resolved/fixed-in-place`: old nodeがexactly once collected/executedされnormal passする。
- `resolved/superseded`: 明示successorがexactly once collected/executedされnormal passし、old failureが再発しない。
- `retired`: baseline rowにnon-emptyで一意な`retirement_evidence_id`とaccepted authority referenceを要求する。observationの同一IDが`checked=true`かつ`outcome="absent"`の場合だけgreenとする。

unknown lifecycle/mode、duplicate row/current/successor node/evidence ID、missing historical signature、invalid successor reference、retired rowのmissing evidence ID/authorityはevaluation前に`BaselineContractError`とする。skip、xfail、xpass、setup/teardown/collection error、missing、duplicate、deselectionをpassへ丸めない。JUnitで証明不能なoutcomeはpytest hookがshardごとにmachine-readable observation JSONを出力する。

`CandidateObservation.retirement_evidence`はadapter inputであり、pure evaluatorはfilesystemをprobeしない。Issue 382のcurrent ledgerにretired rowはなく、pytest/standalone adapterは空mappingを供給する。将来retired rowを追加するownerはaccepted authorityに対応するrow-specific probeと、その結果からこのtyped observationを作るadapter testを同じ変更で追加しなければならない。provider未登録またはevidence未取得なら必ずviolationとなる。synthetic pure unit testだけがcurrent Issueでpositive retired observationを直接構築する。

## 変更対象

変更対象は`scripts/__init__.py`、`scripts/quality/{__init__.py,full_regression_baseline.py,verify_full_regression.py}`、`tests/conftest.py`、`tests/unit/{test_full_regression_baseline.py,test_provider_test_lanes.py}`、`.github/workflows/provider-full-regression.yml`、`full-regression-ledger.json`、必要最小限のdocumentation/reportである。

`src/spec_dock/`以下のdistribution production/runtime/assets、Issue 372のM1〜M5、public CLI/JSON、managed distribution recovery、ordinary fast-lane skip policy、workflow trigger/merge-blocking位置づけは変更しない。

## 移行・互換性・rollback

schema 1互換をtestsで固定してからschema 2へ移行する。retained-skill rowだけを`resolved/superseded`とし、successorを完全なnode ID `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood`へ固定する。他のactive rowのnode/signature/rationaleは同一でなければならない。current migrationでretired rowは作らない。

workflowは`uv run python -m scripts.quality.verify_full_regression --shards 4`へ切り替える。rollbackはhistorical row削除、schema 1 authority復活、Issue 368 artifactへのsilent fallbackでは行わずforward-fixする。

## testability

- pure table testsでactive、fixed、superseded、synthetic retired evidenceと全negative outcomeをI/Oなしで検証する。
- migration testで既存active集合不変とretained-skill rowだけのresolved移行を検証する。
- 同一observationに対するpytest/standalone adapterのtyped result同値を検証する。
- contract testでadapter側にlifecycle policyが戻らないことを固定する。
- canonical runnerのmachine-readable receiptでactive/resolved/unexpected分類を観測する。

## risk

- JUnitだけでXPASSをpassと誤認するリスク: pytest hook observation JSONをauthorityにする。
- policy二重実装: evaluator以外のlifecycle分岐を禁止する。
- historical evidence消失: migration invariantでrow/signature対応を固定する。
- repository policyの配布物混入: `scripts/quality/`以外へproduction sourceを追加しない。
- retiredのunchecked ignore化: absence evidence未実装時はfail closedする。

## stop conditions

- distribution production/runtime/assetsの変更が必要になる。
- historical row/signatureの削除または上書きが必要になる。
- 証明不能なoutcomeをnormal passと推定する。
- evaluatorがI/O、pytest、JUnit、subprocess、Gitを所有する。
- adapterにlifecycle policyが残る。
- unexpected failure/errorをbaseline更新だけで吸収しようとする。
