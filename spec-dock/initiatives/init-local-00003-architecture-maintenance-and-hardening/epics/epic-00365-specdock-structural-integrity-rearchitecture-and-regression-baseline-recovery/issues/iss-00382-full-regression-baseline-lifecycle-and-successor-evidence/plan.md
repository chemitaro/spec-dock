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

### Step 8A — M6 ledger authority cutover（追加）

Step 8の検証で、pre-freeze candidate SHA `8b66840688da20b686399d7bc6f05d6bb77ac5e5`の実装がIssue 368配下のledger/timing weightsをcanonical runtimeから参照している不整合を確認した。この追加stepでは、既存Step 1〜8の実施済み記録を書き換えず、authorityの切替とhistorical evidenceの固定だけを行う。

1. REDとしてprovider lane testに、repository rootの`full-regression-ledger.json` / `full-regression-timing-weights.json`の存在、`tests/conftest.py`・canonical runner・provider workflowからIssue 368 artifact pathが消えていること、Issue 368配下の2 artifactが親固定点 `48b34e23283f9270d671d1e1eb3c3a3365fe1856`のSHA-256内容と一致することを追加する。
2. 現行schema 2 ledger（26 active、1 resolved/superseded、0 retired）とtiming weightsをrepository rootへ移し、pytest guard / canonical runnerの既定pathおよびtest helperをroot authorityへ変更する。Issue 368配下のledger/timing weightsは親固定点のhistorical schema 1/contentへ戻し、fallbackは実装しない。
3. focused provider tests、`make lint`、ordinary pytest、`spec-dock validate`を実行する。Full Regressionはこのauthority cutoverを含むcommit後のprimaryがcandidate SHAで実行し、Step 9のreceiptへ記録する。

M6の完了条件は、canonical runtimeがroot authorityだけを読み、Issue 368 artifactがhistorical evidenceとして固定され、既存のschema migration invariantとlane policyが変わらないことである。

### Step 8B — M7 Strict前静的監査P1修復（追加）

M6 commit `22309ce0932c3233385d5cdefe317e867cfd3c52`でFull Regressionがverifiedになった後、Strict review前の静的監査で次のP1を検出した。この追加stepは、実施済みStep 1〜8Aを改変せず、metadataとadapter contractの証拠を補強する。

1. root `full-regression-ledger.json`の`commands.current_full`が旧Issue 368 verifierを指していたため、REDとしてexact canonical command `uv run python -m scripts.quality.verify_full_regression --shards 4`をassertし、metadataの1行だけを修正する。
2. `build_candidate_observation`でpytest phase reportsから作ったtyped observationを、standaloneの公開JSON境界`observation_to_json` / `observation_from_json`でround-tripするcontract testを追加する。同じbaselineへ`evaluate_baseline`を適用した両方の`BaselineEvaluation.to_dict()`（classification、violations、verified）が完全一致することを直接検証する。既存実装がこのcharacterizationを満たす場合はproduction codeを変更しない。
3. focused provider/evaluator、`make lint`、ordinary pytest、`spec-dock validate`、`git diff --check`を再実行する。M7後はroot ledgerとtest追加でcandidate SHAが変わるため、`22309ce...`時点のFull Regression receiptはstaleとして再利用せず、primaryがStep 9で再実行する。

M7ではproduction evaluator/runner/conftest、ledger rows/signatures/lifecycle、distribution sourceを変更しない。historical verifierのdirect-load testとoutcome set境界の重複は、canonical runtime dependencyではないため対象外とする。

### Step 8C — M8 Provider parity hermetic build dependency preparation repair（追加）

PR #383のProvider CI run `33315553126`でmacOS parity job `99268220215`がcandidate wheel fixture setupの16件すべてで`Missing dependencies: setuptools>=69`となり、Ubuntu parityはfail-fastでcancelledになった。manual Full Regression run `33315602048`は旧SHAでpassしているが、M8後のcandidateではstale receiptとして扱う。

1. REDとしてnative build venvのpip-present経路が、staleなseeded setuptoolsを置換できるbuild-backend installation command（`--target`なし、`--upgrade`、`--no-index`、`--find-links`、exact pinned requirements）を満たすことをテストする。pip unavailable経路は既存のgeneric target installerでhermetic fallbackを維持するcharacterization testも追加する。
2. native venvでpip probeが成功した場合だけ、build-backend専用の小helperをそのvenvの通常pip environmentへ適用する。pip unavailableまたはvenv生成失敗時は既存`_issue_69_install_target_packages`のtarget semanticsを使い、`python -m build --no-isolation`、local wheelhouse、network禁止、OS分岐なしを維持する。
3. Issue 69 artifact-build unit group、指定distribution parity、`make lint`、ordinary pytest、`spec-dock validate`、`git diff --check`を実行する。未commit作業ツリーではcandidate fixtureのclean-status assertionが失敗し得るため、heavy結果はsemantic passと環境由来のdirty-status failureを分離して記録し、primaryがM8 commit後に再実行する。

M8の変更範囲はIssue 69 test harnessとこのIssueのplan/reportだけであり、workflow、pyproject、wheelhouse、distribution production/runtime/assets、integration test、public CLIを変更しない。

### Step 9 — exact candidate Full Regression

clean candidate SHAから`uv run python -m scripts.quality.verify_full_regression --shards 4`を実行し、active、resolved、unexpected結果をmachine-readable receiptへ記録する。candidate変更後はstale receiptを再利用しない。

### Step 10 — report / Strict / human merge handoff

tracked reportをfreeze前に完成させる。exact pushed SHAへStrict reviewを行い、findingがあればTDDで修正してnew SHAを再reviewする。merge-ready PRまでagentが整え、人間merge前にIssue 382/372をfinishしない。

### Step 8D — M9 external certification evidence materialization（追加）

M8後のexact candidate `46d16fd0a0cfa286db0bc4c292b5d5b73190a10f`について取得済みの外部認証を、既存のStep 1〜10およびM1〜M8の実施済み履歴を書き換えず、append-onlyでcanonical reportへ記録する。M9は新しいproduction変更やpolicy変更ではなく、Issue 382のmerge-ready判定に必要なcandidate SHA／CI／Full Regression／Strict／PR状態の証跡を固定する作業である。

1. code candidate SHA `46d16fd0a0cfa286db0bc4c292b5d5b73190a10f`に対するProvider CI run `33322223928`（provider-tests pass 2m33s、macOS parity pass 1h6m4s、Ubuntu parity pass 1h13m44s）を記録する。
2. Provider Full Regression run `33323717175`（pass 1h7m36s、artifact id `9736472371`、name `provider-full-regression-evidence`）を記録し、`result.json`のcandidate SHA exact match、`status=verified`、`evaluation.verified=true`、active 26／resolved 1／retired 0／violations 0、およびSHA-256 `e1b77c0294ff383d8ac71af6f78540508bae28b6c71a7f2d9d1952a16d229782`を照合する。
3. Strict session `required-strict-github-connector-verificati-503`の`review_status=pass`、findings 0、confidence 0.95、およびJSON SHA-256 `0d3ae1fd8b86d4b5e0c49f00379e987eb538128fd7101ce8979a10303e26d4da`を記録する。
4. PR #383がこのreviewed candidateでOPEN、non-draft、MERGEABLE/CLEANであることを記録する。人間によるmergeおよびIssue 382/372のfinishはagentの権限外として未実施のまま保持する。
5. このM9追記自体が新しいdoc-only candidate SHAを生成するため、上記のCI／Full Regression／Strict証跡を追記後のHEADの証跡として扱わない。primaryはplan/report追記をcommit/pushした後の新しいexact SHAについて、CI、Full Regression、Strictを再取得し、自己参照を避ける。

M9の完了条件は、上記の外部認証が`46d16fd...`に正確に紐づき、追記前の未完了／stale記録を歴史として保持しつつ、追記後の新candidate再認証が必要であることが明示されていることである。

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
