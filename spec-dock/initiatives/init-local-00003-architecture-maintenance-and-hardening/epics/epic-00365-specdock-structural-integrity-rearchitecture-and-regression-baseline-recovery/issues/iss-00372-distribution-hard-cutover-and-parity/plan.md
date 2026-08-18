---
種別: 実装計画書（Issue）
ID: "iss-00372"
タイトル: "Distribution Hard Cutover And Parity"
関連GitHub: ["#372"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00372 Distribution Hard Cutover And Parity — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `strict`**

all public distribution flows、package artifacts、Linux/macOS、release evidence、legacy removalを確定するため`strict`とする。

Risk factors:

- structural cleanupによるhidden caller breakage
- package surface drift
- platform-specific filesystem behavior
- public JSON/CLI compatibility
- Full Regression attribution誤り

`critical`再評価条件:

- cleanup/cutoverでauthority外data lossまたはsecurity boundary breachが見つかる
- platform差がrepository外mutationやirrecoverable journal stateを起こし得る
- release recoveryにincident responseが必要

## 目標

D1〜D4のunified architectureを唯一のproduction pathとして固定し、legacy seam absence、all-surface package parity、Linux/macOS focused evidence、public semantic parity、Full Regression no-new-attributable-failureを同じcandidate SHAで完成させる。

## 順序・依存

dependencies: `iss-00368`, `iss-00369`, `iss-00370`, `iss-00371`

1. integrated contract/route inventory
2. legacy seam absence gate
3. structural absence tests
4. public semantic completion matrix
5. package surface parity
6. Linux/macOS evidence
7. Full Regression attribution
8. docs/final completion sweep

Package fixture preparationとCI configuration draftは前倒し可能だが、final evidenceはD1〜D4 merged candidate SHAで取り直す。

## 実装step

### Step 1 — Integrated route/contract inventory

- all public command/flagからservice/kernel/journal/resultへのcall graphを作る。
- D1〜D4のacceptance testsとcross-Issue invariantsをone matrixに統合する。
- remaining legacy symbols/imports/writers/readers/callbacks/assetsを分類する。
- reader-only migration seamはowner、authority、removal conditionを明示する。

Exit:remove対象とallowed migration readerがcomplete allowlistになっている。

### Step 2 — Legacy seam absenceをowner exit gateとして検証する

少なくとも次をdenylist候補としてsource確認する。production executable pathまたはwriterがD1〜D4で未削除なら、該当owner Issueのexit未達としてD5をblockし、D5のchange setでは除去しない。migration-only readerはStep 1のexplicit allowlistとwrite-zero evidenceを満たす場合だけ残存を許可する。

- `_UninstallTargetIdentity`
- `_UninstallAction`
- `_build_uninstall_plan()`
- `_apply_uninstall_plan()`
- `_verify_uninstall_postcondition()`
- CLI-owned recursive uninstall helpers
- legacy retry marker writers
- private `_rename_distribution_no_replace` import
- `scaffold_applier`
- `allow_blocked_scaffold_paths`
- operation-specific fallback mutation route

Namesがimplementation中に変わった場合はsemantic roleで追跡し、単なるrenameをremoval evidenceにしない。

Exit: denylist候補はsourceからabsent、またはmigration-only reader allowlistに限定される。owner Issueへ戻すresidual seamが一件でもあればD5の次stepへ進まない。

### Step 3 — Structural absence testsを追加する

- AST/import testでCLI boundaryを固定する。
- runtime spyでall commandsがsingle service entrypointを呼ぶことを確認する。
- production source内のlegacy symbol/writer/callback patternをdenylistする。
- migration readerはexplicit allowlistとwrite-zero testsを持つ。
- dependency cycleとkernel bypassを検出する。

Negative fixture:legacy helper/callback/writerを再導入するとtestが確実にfailする。

### Step 4 — Public semantic completion matrix

- init、init-force、update、deprovision、purgeのsuccess/block/partial/retryをone tableにする。
- parser/flag/mutual exclusion、text/exit、JSON schema version 1/one-object/action fields/sanitizationをgolden compareする。
- ownership/preservationとfailure/resume matrixをall intentsで実行する。
- no new command/flag/schemaを確認する。

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest tests/unit/infra/test_init_update.py
```

### Step 5 — Package surface parity

- source canonical inventoryとdogfood projectionを比較する。
- wheel/sdistをclean/seeded-stale build contextから作る。
- wheel、sdist、installed resources、fresh consumerをpath/bytes/mode/symlink/manifestで比較する。
- legacy writer/assetsがartifactに残らないことを確認する。
- fresh consumerでinit/update/deprovision/purge focused flowを実行する。

### Step 6 — Linux/macOS focused evidence

- provider CIのfocused distribution jobを`ubuntu-latest`/`macos-latest` matrixにするか、同等にrequired checksとして構成する。
- same candidate SHA、Python/package versions、commandsをrecordする。
- no-follow、flock、atomic/no-replace publish、symlink/hardlink、root rebind、journal resumeを両OSで実行する。
- capability不足simulationがwrite-zero diagnosticになることを確認する。

macOSをbest-effort/allow-failureにしない。

### Step 7 — Full Regression attribution

- pre-Epic exact baseline SHAで`uv run pytest --run-full-regression`を再計測する。
- candidate exact SHAで同commandを実行する。
- stable failure identity/root causeでdiffし、new/resolved/unchanged/unclassifiedに分類する。
- Epic attributable new failureは修正して0にする。
- unrelated existing failureはsibling Epic handoff evidenceに残すが、このIssueで修復/node作成しない。
-旧Issue 360の26件をcurrent expected countにしない。

### Step 8 — Docsとfinal completion sweep

- README、migration/recovery docs、canonical docs、ADR、HTMLのcommands/names/semanticsをsource/testsと照合する。
- `.meta.json`とnode path/titleを手編集していないことをdiffで確認する。
- no placeholder、stale legacy guidance、duplicate scopeを確認する。
- release candidate SHAへ全evidenceを束縛する。

## 検証

Required command set:

```bash
make lint
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest
uv run pytest --run-full-regression
```

Build/parity commandsはrepositoryのcurrent `pyproject.toml`/Makefileに従い、wheel/sdist/installed/fresh consumerのSHA/inventory resultを保存する。

Required gates:

- structural absence: pass
- all-intent behavior matrix: pass
- public CLI/JSON parity: pass
- package surfaces: pass
- Linux: pass
- macOS: pass
- affected fast suite: pass
- Epic attributable Full Regression new failures: 0
- docs/source consistency: pass

## rollback

- structural absence gate前にbehavior testsをgreenにする。
- hidden repository callerまたはproduction legacy seamが見つかった場合はD5をblockし、owner Issueでsingle serviceへ移行する。legacy private APIをpublic guaranteeとして復活させない。
- release rollbackはactive new journal protocolとのcompatibilityを確認してから行う。互換性がなければforward recovery packageを先に提供する。
- package parity failure時はreleaseを停止し、個別artifactを手修正しない。
- platform failure時はbest-effortへ格下げせずkernel/capability gateを修正する。

## exit / handoff

- I372-R01〜R10とacceptance 1〜10がsame candidate SHA evidenceに結び付く。
- legacy execution seam/writer/private import/fallbackがabsence testで不在。
- all public intentsがsingle service/kernel/journal/resultを使用。
- source/dogfood/wheel/sdist/installed/fresh parityがpass。
- Linux/macOS required checksがpass。
- current public CLI/JSON semanticsがpass。
- Full Regression attribution完了、Epic attributable new failure 0。
- canonical docs/ADR/HTML/READMEがimplementationと一致。
- remaining unrelated Full Regression failuresはsibling Epic candidateへのevidenceとしてhandoffし、node追加は行わない。
- Epic 365を一般refactor、Windows、AI orchestration、generic transaction、whole rollbackへ延長しない。
