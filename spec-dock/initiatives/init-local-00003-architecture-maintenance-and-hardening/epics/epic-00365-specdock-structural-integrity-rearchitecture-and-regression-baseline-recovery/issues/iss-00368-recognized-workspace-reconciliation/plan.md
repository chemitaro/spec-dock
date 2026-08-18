---
種別: 実装計画書（Issue）
ID: "iss-00368"
タイトル: "Recognized Workspace Reconciliation"
関連GitHub: ["#368"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00368 Recognized Workspace Reconciliation — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `strict`**

public installer behavior、managed files、historical ownership、recovery state、cross-version migration を変更し、失敗時は consumer workspace が部分更新状態になり得るため `strict` とする。

Risk factors:

- public `update` / `init --force` compatibility
- filesystem identity と user-owned data preservation
- legacy marker migration
- partial failure 後の forward recovery
- Linux/macOS syscall behavior

`critical` 再評価条件:

- unknown/user-owned path を不可逆に変更し得る path が見つかる
- journal mismatch が自動 mutation へ進み data loss を起こし得る
- recovery に security incident response または repository 外 path の調査が必要になる
- exact pre/post identity で crash state を一意判定できないまま mutation 継続が必要になる

## 目標

recognized target の `update` と `init --force` を新 unified reconciliation engine へ hard cutover し、blocker write-zero、exact-SHA journal resume、current public behavior を focused tests で証明する。fresh target の同名 entrypoint は D2 の owner として現行挙動を保持する。Issue 終了時に recognized flow の旧 scaffold callback/marker orchestration/plan外 mutation routeを残さない。

## 順序・依存

外部 Issue dependency はない。作業内 dependency は次の順に固定する。

1. current contract characterization
2. pure assessment/plan boundary
3. journal/kernel execution
4. update cutover
5. init-force cutover
6. legacy recovery migration
7. legacy route removal
8. docs、completion sweep

Test fixture、JSON/text golden data、platform capability inventory は 1〜3 と並行作成できるが、cutover 前に review する。

## 実装step

### Step 1 — Current behavior と public contract を固定する

- exact commit の `DistributionOperation`、`DistributionAction`、`DistributionPlan`、admission、retry marker、scaffold callback、CLI orchestration を call graph にする。
- `tests/unit/infra/test_managed_distribution.py` と `test_init_update.py` から recognized-target update/init-force の ownership/safety/output matrix と、fresh target に対する `init` / `init --force` / `update` の現行 compatibility matrix を抽出する。
- missing/current/historical/obsolete/unknown/modified/wrong-mode/symlink/hardlink/parent/root/provider/stage case を parameterized characterization tests にする。
- no-write assertion は target tree bytes、marker、staging、backup、version、outside sentinel を含める。

Targeted verification:

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py -k 's25 or s30 or s35 or s55'
uv run pytest tests/unit/infra/test_init_update.py -k 'update or force'
```

Exit: current safety/output contract が test 名と expected result で追跡可能である。

### Step 2 — Assessment と executable plan を型で分離する

- immutable Distribution Contract input を current catalog/historical manifest から構築する。
- read-only observation と disposition を `WorkspaceAssessment` 相当へ集約する。
- blocker 有り assessment から executable plan を作れない constructor/factory contract にする。
- deterministic action ordering、canonical plan serialization、`plan_digest` を実装する。
- current `DistributionAction` diagnostic semantics を compatibility mapping する。

Negative tests:

- blocker 有り plan construction
- unsafe relative path
- duplicate/conflicting action
- incomplete precondition
- action order permutation で digest drift
- absolute path/content bytes が diagnostic に漏れる case

Exit: assessment test は filesystem write を観測せず、plan digest fixture が stable である。

### Step 3 — Journal と kernel の recognized subset を実装する

- operation journal の schema/protocol version、root/intent/authority/contract/plan binding を実装する。
- regular/symlink/directory/staging identity を用途別 type に分ける。
- exact pre-action SHA と expected post-action identity を action record に入れる。
- descriptor-bound create/replace/remove/mode/staging/journal operation を kernel に集約する。
- checkpoint は atomic publish 後の re-observation を通して単調更新する。

Negative tests:

- journal create failure で target write 0
- provider/source mutation
- target appearance/replacement
- root/parent rebind
- hardlink/symlink swap
- staging write/publish/cleanup failure
- checkpoint write failure後の pre/post ambiguous state

Exit: same-process failure と simulated crash state の双方で journal が安全に残る。

### Step 4 — recognized target の `update` を新 service へ切り替える

- CLI parse/resource location を保ち、service call と result rendering に置換する。
- current/historical upgrade、missing create、obsolete prune、mode repair、user content preservation を新 engine で通す。
- postcondition assessment と version update を service transaction sequence に含める。
- update 対象で `scaffold_applier` と `allow_blocked_scaffold_paths` に依存しない。

Verification:

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest tests/unit/infra/test_init_update.py -k 'update'
```

Exit: update の successful/blocked/partial-recovery paths が new ProcessResult から出力される。

### Step 5 — recognized target の `init --force` を同じ flow へ切り替える

- force を unknown overwrite authority として扱わない。
- update と共通 assessment/action/kernel/journal を使用し、intent policy の必要差分だけを contract に置く。
- no-op/no-write case で prompt、backup、journalを作らない。
- existing public success/error semantics を維持する。

Negative tests:

- modified/unknown target を `--force` で上書きしない
- recognized admission mismatch
- root/parent rebind
- update journal を init-force で resume しない

Exit: update と init-force が second grammar を持たず、intent mismatch が write 0 で block される。

### Step 6 — Legacy `.distribution-retry.json` migration を閉じる

- exact current marker fixturesを用意する。
- root、operation、package/protocol、stage lease、same-plan reconstruction を全て満たす caseだけ one-way conversion/compatibility resumeする。
- malformed、dual、cross-root、different-operation、newer target、unknown stage、plan mismatchは markerを変更せず blockする。
- conversion後は new journalだけをwriterとし、legacy markerを再生成しない。

Forward-recovery test:

- interrupted current update fixture → safe conversion → same desired postcondition
- exact pre-action SHA mismatch → block
- compatible newer package → same plan only resume
- incompatible/downgrade → block

Exit: legacy recovery behaviorが explicit reason codeとoperator guidanceを持つ。

### Step 7 — Recognized legacy pathを削除する

- update/init-forceから scaffold callback、CLI-owned marker phase writer、private rename shortcut、plan外 mutationへのcall edgeを除去する。
- fresh-only compatibility codeをD2まで残す場合は recognized intentから到達不能にする。
- dependency/import/AST testでsingle service/kernel routeを固定する。

Exit:同一 recognized operationを旧/新二経路で実行できない。

### Step 8 — Docsとcompletion sweep

- READMEのupdate/init-force/retry guidanceを実装と一致させる。
- journal protocol compatibilityとmanual recovery diagnosticを記載する。
- Requirement/Design/Plan/ADRとの矛盾を確認する。
- affected tests、lint、type check、package testsを実行する。

## 検証

Required commands:

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest tests/unit/infra/test_init_update.py -k 'update or force or distribution'
make lint
```

追加確認:

- target tree byte snapshotのbefore/after
- outside sentinel unchanged
- marker/journal/staging inventory
- exact one service/kernel call route
- diagnosticにabsolute path、file content、secretなし
- LinuxとmacOSでfocused safety subset。D5前の結果はprovisional evidenceとして同じcandidate SHAを記録する。

Full RegressionはこのIssueで既存failureを修復しない。candidate SHAで実行した場合はpre-Epic baselineとの差分だけを分類し、新規attributable failureをblockerとする。

## rollback

### Migration前

new journal作成前のfailureまたはcutover前test failureはcode revertで戻す。target mutationは0件でなければならない。

### Migration後

new journalが存在するconsumerではold codeへ単純rollbackしない。same/compatible newer packageでforward recoveryし、root/intent/authority/plan/protocol/pre-action SHA不一致はmanual reviewのため停止する。

### Legacy marker

conversion前のlegacy markerは失敗時に書き換えない。conversion成功後はnew journalをauthorityとし、legacy writerを復活させない。

## exit / handoff

- I368-R01〜R10とacceptance 1〜10がtest/evidenceに結び付く。
- update/init-forceのlegacy execution routeが削除済み。
- current safety testsを弱めず、新negative/resume testsが成功。
- current public command/flag/text/exit behaviorが維持。
- new journal protocol、exact-SHA rule、legacy conversion conditionがdocsと一致。
- D2へ、fresh intentを追加できるstable Contract/Assessment/Kernel/Journal/Result seamを引き渡す。
- residual riskはfresh-only scaffold semantics、deprovision/purge action、final Linux/macOS/package parityであり、D2〜D5へ明示的に渡す。
