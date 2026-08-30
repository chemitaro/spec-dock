---
種別: 実装計画書（Issue）
ID: "iss-00382"
タイトル: "Full Regression Baseline Lifecycle And Successor Evidence"
関連GitHub: ["#382"]
状態: "planned"
最終更新: "2026-08-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00382 Full Regression Baseline Lifecycle And Successor Evidence — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

Level 3。quality gate合否、schema migration、pytest lifecycle、sharded observationを扱うためred/greenのvertical sliceに分ける。ただしproduction distributionへは波及させず、一つのpure evaluatorをdeep seamとする。

## 目標

一つのrepository-level evaluatorがactive historical failureと明示的resolved successorをfail closedに判定し、pytest guardとstandalone Full Regressionが同じresultを返す。Issue 372 retained-skill successorをcoverage lossなしでgreenにし、既存active failure contractを変えない。

## 順序・依存

pure evaluator → observation adapter → ledger migration → canonical runner/workflowの順で一人のproduction writerが実装する。各stepはfocused testがgreenになってから次へ進む。Issue 372は本Issueのhuman merge後にのみ再開する。

## 実装step

### Step 1 — schema 1 active compatibilityをRED/GREENにする

`tests/unit/test_full_regression_baseline.py`にsame node/signature failureのみgreen、pass/missing/skip/signature mismatchはredとなるtestsを先に追加する。最小のparse/model/evaluateでgreenにし、既存normalization/signature semanticsをcharacterizeする。

### Step 2 — resolved successor sliceをRED/GREENにする

retained-skill old nodeを`resolved/superseded`、successorを完全なnode ID `tests/cli_runtime/test_distribution_cutover.py::test_s40b_retained_skill_identity_matches_current_provider_and_dogfood`とする。byte-for-byte一致、normal pass、exactly-onceだけをgreenにし、関数名だけ/suffix match、missing ID、uncollected、deselected、skip、xfail、xpass、failed、error、duplicate、old failure再発を個別にredで固定する。

### Step 3 — fixed/retired/schema negative contractをRED/GREENにする

fixed-in-placeはold nodeのnormal passだけgreenにする。retired baselineはnon-empty unique evidence IDとaccepted authorityを要求し、synthetic observationの同一IDが`checked=true`かつ`outcome=absent`の場合だけgreenにする。missing/unknown/present/uncheckedをredにし、unknown lifecycle/mode、duplicate row/node/evidence ID、historical signature消失をparse errorにする。current ledgerにはretired row/providerを追加せず、両adapterは空evidence mappingを供給してfail closedする。汎用retirement inferenceは実装しない。

### Step 4 — pytest observation adapterを接続する

`tests/conftest.py`のevent観測を維持し、ledger parse・normalization・signature・set comparisonの重複をshared evaluatorへ置換する。`report.wasxfail`でxfail/xpassを区別し、setup/call/teardown errorをtyped observationにする。

### Step 5 — standalone observation/runnerを接続する

shard pytest hookからmachine-readable observation JSONを出力し、JUnitで証明不能なoutcomeを推定しない。runnerはprocess/shard/artifact/render/exitだけを所有する。同一observationを両adapterへ与えるcontract testをred-firstで追加する。

### Step 6 — ledgerをschema 2へ移行する

migration前後のrow/node/signature/rationale対応をtestで固定する。retained-skill rowだけをresolved/supersededへ移し、他のrowはactiveのまま保持する。row削除やfailure count調整でgreen化しない。

### Step 7 — canonical workflow pathへcutoverする

workflow commandを`uv run python -m scripts.quality.verify_full_regression --shards 4`へ変更する。Issue 368 artifactはhistorical evidenceとして残し、canonical fallbackにしない。provider lane testsでworkflow、manual command、pytest guardのauthorityを固定する。

### Step 8 — focused/ordinary quality verification

```bash
uv run pytest tests/unit/test_full_regression_baseline.py
uv run pytest tests/unit/test_provider_test_lanes.py -k full_regression
uv run pytest tests/unit/test_provider_test_lanes.py
uv run ruff check scripts/quality tests/conftest.py tests/unit/test_full_regression_baseline.py tests/unit/test_provider_test_lanes.py
uv run mypy scripts/quality tests/conftest.py
make lint
uv run pytest
./spec-dock/scripts/spec-dock validate
```

### Step 9 — exact candidate Full Regression

clean candidate SHAから`uv run python -m scripts.quality.verify_full_regression --shards 4`を実行し、active、resolved、unexpected結果をmachine-readable receiptへ記録する。candidate変更後はstale receiptを再利用しない。

### Step 10 — report / Strict / human merge handoff

tracked reportをfreeze前に完成させる。exact pushed SHAへStrict reviewを行い、findingがあればTDDで修正してnew SHAを再reviewする。merge-ready PRまでagentが整え、人間merge前にIssue 382/372をfinishしない。

## 検証

AC01〜AC09をStep 1〜10へtraceする。AC02/03はStep 2、AC04はStep 4/5、AC05はStep 6、AC06はStep 7、AC07/08はStep 8/9、AC09はStep 10で判定する。

## rollback

historical baselineを削除してrollbackしない。adapter/canonical runnerの不具合はshared evaluator contractを保ったforward-fixとする。Issue 368 artifactへのsilent fallback、schema 1へのauthority rollback、distribution production変更は禁止する。

## exit / handoff

- pure evaluatorと二adapterにpolicy重複がない。
- retained-skill successorと既存active rowsの全contractがgreen。
- focused、ordinary、lint、validate、exact Full Regressionが同一candidateでgreen。
- Strict passしたexact SHAのPRがmerge-ready。
- human merge後にIssue 372 dependencyがsatisfiedになり、Issue 372追加Step 10Bへ引き渡せる。

stop condition発生時はcoderがscopeを広げず、RED evidenceと必要なowner decisionをprimaryへ返す。
