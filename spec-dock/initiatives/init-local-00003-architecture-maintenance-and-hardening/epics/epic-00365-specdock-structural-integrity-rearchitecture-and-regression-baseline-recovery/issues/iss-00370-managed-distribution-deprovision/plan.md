---
種別: 実装計画書（Issue）
ID: "iss-00370"
タイトル: "Managed Distribution Deprovision"
関連GitHub: ["#370"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00370 Managed Distribution Deprovision — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `strict`**

public uninstall、recursive deletion、spec history preservation、JSON compatibility、legacy recoveryを変更するため`strict`とする。

Risk factors:

- deletion authorityとuser-owned content
- recursive filesystem mutation
- public JSON consumers
- partial deletion recovery
- information-poor legacy marker

`critical`再評価条件:

- authority外contentを不可逆削除し得る
- repository外pathへ到達し得る
- partial deletionの復旧にincident responseが必要
- spec history preservationをexactに検証できないままapplyを許可する必要が生じる

## 目標

`uninstall` dry-runと`--apply --keep-specs`をcommon engineへhard cutoverし、owned distribution removalとspec history/unknown preservationをend-to-end証明する。current JSON semanticsを維持し、deprovision対象legacy grammar/writerを削除する。

## 順序・依存

dependency: `iss-00369`

1. current uninstall/JSON characterization
2. deprovision authorityとassessment
3. common removal kernel/action
4. dry-run adapter
5. journaled apply/postcondition
6. legacy marker handling
7. legacy route removal/docs

D4 purge fixtureはauthority comparison用にread-only準備できるが、purge executionを本Issueへ入れない。

Migration:

- dry-runと`--apply --keep-specs`を同じIssue内でnew serviceへhard cutoverし、deprovision対象のold action/plan/apply/postverify/writerを同時に削除する。
- current `.uninstall-retry.json`はoriginal root、intent、plan digest、checkpoint、specs modeを証明できないため、defaultではnew deprovision journalへ変換しない。exact追加証拠がある限定case以外はmarkerを保持してwrite前にblockする。
- D4まで残るremove-specs compatibility routeはnew deprovision journalから到達不能にし、purge authorityを推測移行しない。

## 実装step

### Step 1 — Current contractを固定する

- `_UninstallAction` category/status/reason、plan/apply/postverify、retry marker、payload fieldsをcall graph/schema fixtureにする。
- dry-run、keep-specs、modified/unknown preservation、bounded cleanup、symlink/hardlink、partial failureのexisting testsをinventory化する。
- JSONはexactly one object、schema version、keys、action fields、status/phase/guidance/error sanitizationをgolden fixtureにする。

```bash
uv run pytest tests/unit/infra/test_init_update.py -k 'uninstall'
```

### Step 2 — Deprovision authorityとAssessmentを実装する

- owned tooling/generated/managed asset、spec history root、unknown/preserved pathをContractに定義する。
- current uninstall classificationをcommon dispositionへmapする。
- all-path preflight blockerがあればExecutable Planを発行しない。
- dry-run用diagnostic assessmentとapply planを型で分離する。

Negative tests:

- unmanaged target
- modified/unknown target
- missing ownership evidence
- preserved descendant
- specs rootがsymlink/unsafe
- no specs mode/both modes

### Step 3 — Common removal kernelを実装する

- exact regular/symlink unlink、bounded tree remove、empty-directory cleanupをkernelへ追加する。
- child列挙、identity、link count、authorityをdescriptor-relativeに再検証する。
- outside sentinel、unknown child、hardlink、symlinkをfollow/removeしない。
- exact pre-action SHA/identityとexpected absentをjournal actionに入れる。

Failure tests:

- child identity swap
- root/parent rebind
- partial recursive failure
- unlink/rmdir failure
- unknown child appearance
- checkpoint failure

### Step 4 — Dry-runをnew ProcessResultへ切り替える

- `uninstall` no `--apply`をnew assessment/resultへdispatchする。
- current text/JSON mapperでplanned resultを出す。
- tree/marker/journal/staging before-after equalityをassertする。
- blocker diagnosticsとapplyabilityを区別する。

### Step 5 — `--apply --keep-specs`をjournaled executionへ切り替える

- prepared journal後にcommon action/kernelでremoveする。
- each checkpointとpostconditionを記録する。
- initiatives/spec historyとunknown contentのpre/post identityをverifyする。
- success後だけjournal/stagingをfinalizeする。
- partial failureではretry guidanceとsanitized resultを返す。

### Step 6 — Legacy `.uninstall-retry.json`をfail closedで扱う

- exact current marker bytesとpartial tree fixturesを作る。
- markerがroot/intent/plan/checkpointを証明しないことをtestにする。
- default automatic conversionを拒否し、markerを変更せずtyped guidanceを返す。
- exact additional evidenceでnarrow conversionを実装する場合は、conversion proofとnegative counterexampleを同じchangeに含める。
- deprovision invocationからpurge authorityを推測しない。

### Step 7 — Legacy route removal、docs、completion sweep

- deprovision flowから`_UninstallAction`、`_build_uninstall_plan()`、`_apply_uninstall_plan()`、`_verify_uninstall_postcondition()`、CLI-owned recursive removal、legacy writerを除去する。
- D4まで必要なpurge compatibility codeはdeprovisionから到達不能にする。
- README JSON/dry-run/recovery/keep-specs guidanceを更新する。
- import/symbol/AST testsを追加する。

## 検証

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest tests/unit/infra/test_init_update.py -k 'uninstall or update or init'
make lint
```

Required evidence:

- dry-run tree byte equality
- successful removal inventory
- spec history/unknown/outside sentinel byte equality
- blocker write-zero
- partial failure journal and retry convergence
- deprovision-to-purge authority mismatch
- current JSON golden parity
- legacy marker fail-closed fixture
- deprovision legacy symbol/call-edge absence

## rollback

- new journal作成前はcode revert可能。
- new deprovision journal作成後はsame/compatible packageでforward recoveryする。
- removed file/treeをwhole-operation rollbackで自動復元しない。pending/completed actionをexact pre/post identityで再評価する。
- ambiguous partial deletion、spec history mismatch、unknown childはjournalを保持しmanual guidanceで停止する。
- legacy markerをconversion failure時に削除しない。

## exit / handoff

- I370-R01〜R10とacceptance 1〜10がevidenceに結び付く。
- dry-run、keep-specs、JSON、partial recoveryがcommon engineを使用。
- spec history/unknown preservationがpostcondition testで証明。
- deprovision対象legacy grammar/recursive mutation/writerが削除。
- D4へ、same engine上でseparate purge authority/action/postconditionを追加できる状態を渡す。
- residual riskはexplicit purge、legacy remove-specs retry、final package/platform parityとしてD4/D5へ渡す。
