---
種別: 実装計画書（Issue）
ID: "iss-00369"
タイトル: "Fresh Distribution Provisioning"
関連GitHub: ["#369"]
状態: "planned"
最終更新: "2026-08-18"
依存: ["requirement.md", "design.md"]
親: ["epic-00365", "init-local-00003"]
---

# iss-00369 Fresh Distribution Provisioning — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

**selected level: `strict`**

fresh repositoryへのmanaged tree作成、prompt/backup boundary、package byte parity、partial creation recoveryを変更するため`strict`とする。

Risk factors:

- repository root内の既存unrelated content
- create/no-replace semanticsとdirectory TOCTOU
- package asset inventory/mode/symlink parity
- prompt後のstale plan
- fresh retryのintent isolation

`critical`再評価条件:

- fresh planがmanaged boundary外を変更し得る
- cleanupがunknown/user-owned contentを不可逆削除し得る
- platform capability不足を検出せずmutationを開始するpathがある
- recoveryにincident responseが必要なdata loss caseが見つかる

## 目標

fresh `init`をD1 engineへ切り替え、collision-free provisioning、write-zero blocker、fresh journal resume、current package bytes/behaviorを検証する。Issue終了時にfresh flowの別scaffold mutation engineを残さない。

## 順序・依存

dependency: `iss-00368`

1. D1 contract/journal/kernelのstability確認
2. current fresh behavior characterization
3. fresh contract/assessment/plan
4. fresh apply/journal/postcondition
5. CLI prompt/backup/cutover
6. legacy route removal
7. docs/parity/handoff

Package inventory fixtureとnegative filesystem fixtureは2〜4に並行して作成できる。

Migration:

- D1のjournal protocolとcommon action grammarを前提に、fresh `init`を一回のhard cutoverでnew serviceへ移す。dual writerやruntime toggleは残さない。
- new fresh journal作成前のconsumerはcurrent fresh admissionから通常再実行できる。new journal作成後はsame/compatible protocolによるforward recoveryだけを正規経路とする。
- current fresh targetにlegacy retry evidenceが存在する場合は、root/intent/plan/checkpointをexactに証明できるときだけ限定変換し、情報不足ならwrite前にblockする。

## 実装step

### Step 1 — D1 handoff gate

- recognized flowがsingle service/kernel/journalを使用し、protocol/versioning testsがgreenであることを確認する。
- D1のpublic/internal extension pointsを記録し、fresh専用second grammarを作らないconstraintをtest planへ入れる。

Exit: fresh overlayを追加してもD1 resume digest/authority contractを壊さないinterfaceがある。

### Step 2 — Current fresh contractをcharacterizeする

- physical install root、scaffold resources、fresh-only seed、mode、symlink、managed skill inventoryを列挙する。
- `test_init_update.py`のbyte-exact install、second init、unmanaged root content、workbench behaviorをfocused fixturesにする。
- prompt/backupが現行で発生するconditionとno-write conditionをsource/testから固定する。未確認behaviorを推測で追加しない。

Verification:

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py -k 'fresh'
uv run pytest tests/unit/infra/test_init_update.py -k 'init or install_current_target_catalog or workbench'
```

### Step 3 — Fresh ContractとAssessmentを実装する

- current physical sourceからfresh desired/seed/directory policyを導出する。
- expected-absent、safe parent、collision、unrelated-preserve dispositionを実装する。
- blocker有りassessmentからplanを発行しない。
- `mutation_required`をprompt adapter用にresultへ明示する。

Negative tests:

- non-directory parent
- parent/final symlink
- non-writable path
- managed target collision
- root rebind
- unrelated root contentをblock/removeしない

### Step 4 — Fresh Plan/Apply/Journalを接続する

- deterministic ensure-directory/create/mode/symlink/version actionを作る。
- expected-absent preconditionとno-replace publishをkernelで実行する。
- created directory/actionをjournal checkpointに含める。
- full postcondition assessmentがadopt-onlyであることを確認してfinalizeする。

Failure tests:

- journal create failure
- directory create後failure
- staging write/publish failure
- destination appearance
- checkpoint/postcondition failure
- same-plan retry convergence
- retry intent mismatch

### Step 5 — CLI cutoverとprompt/backup boundary

- `main()` fresh branchをservice dispatch/result mappingへ置換する。
- mutation-required result後だけcurrent prompt/backupを実行し、承認後にroot/plan digestを再検証する。
- second init without forceのcurrent guidanceを維持する。
- success/error exit/outputをgolden testで固定する。

### Step 6 — Fresh legacy seamを削除する

- fresh flowから`scaffold_applier`、alternate recursive copy、private publish shortcut、plan outside mutationを削除する。
- import/call graph testでfresh and recognizedがsame service/kernelを使用することを確認する。
- D1 compatibility adapterがfresh writerとして残っていないことを検査する。

### Step 7 — Docs、package parity、handoff

- README init/retry/second-init guidanceを更新する。
- source/dogfood/package fresh inventory comparisonを実行する。
- D3がremove actionを追加できるよう、create-focused assumptionをcommon grammarに残さない。

## 検証

```bash
uv run pytest tests/unit/infra/test_managed_distribution.py
uv run pytest tests/unit/infra/test_init_update.py -k 'init or fresh or install_current_target_catalog or workbench'
make lint
```

Required evidence:

- fresh target before/after inventory and SHA/mode/link comparison
- collision casesのwrite-zero tree snapshot
- unrelated sentinel unchanged
- prompt/backup call count
- journal/checkpoint/staging inventory on injected failures
- same-plan retry convergence
- fresh flowのlegacy seam absence

Linux/macOS focused runはcandidate SHAを記録する。最終required parityはD5が確定する。

## rollback

- cutover前またはnew journal作成前はcode revert可能。
- new fresh journal作成後はsame/compatible packageでforward recoveryする。
- created directoryをrollback目的でunknown childrenごとrecursive removeしない。
- exact pre/post identity不一致はblockし、manual guidanceを返す。
- package rollbackでfresh desired inventoryが変わる場合、plan digest/protocol compatibilityを証明できなければresumeしない。

## exit / handoff

- I369-R01〜R10とacceptance 1〜10がevidenceに結び付く。
- fresh/recognized両flowがsingle service/kernel/journalを使用。
- fresh-only seed semanticsとno-backfill semanticsがtestsで固定。
- current command/flag/output/second-init behaviorが維持。
- fresh legacy mutation seamが削除。
- D3へ、remove/preserve postconditionを追加可能なunified action/result contractを引き渡す。
- residual riskはuninstall JSON compatibility、recursive removal、purge authority、final package/platform parityとしてD3〜D5へ渡す。
