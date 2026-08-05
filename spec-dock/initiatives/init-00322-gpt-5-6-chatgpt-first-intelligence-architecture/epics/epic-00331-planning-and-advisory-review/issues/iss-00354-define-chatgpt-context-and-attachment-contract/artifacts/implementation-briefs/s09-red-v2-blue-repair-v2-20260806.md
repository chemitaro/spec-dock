# iss-00354 S09 Blue Repair v2 — Codex実装ブリーフ

## 0. 実装identityと完了時状態

| 項目                      | 契約値                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------- |
| Repository              | `chemitaro/spec-dock`                                                                 |
| Named branch            | `codex/iss-00354-chatgpt-context-contract`                                            |
| Source HEAD             | `ec179c301c045f94d54abea308c47e79d16c5979`                                            |
| Branch parity           | named branch tipとsource HEADは`identical`、ahead `0`、behind `0`                         |
| Default branch fallback | 禁止・未使用                                                                                |
| 入力review                | S09 Fresh Red Team v2                                                                 |
| Review verdict          | `FAIL`、P0=`0`、P1=`2`                                                                  |
| 修正finding               | `RT-354-S09-V2-001`、`RT-354-S09-V2-002`のみ                                             |
| Worker実行設定              | GPT-5.6 Luna / Reasoning Effort Maxはユーザー指定の実行先設定であり、観測済みmodel evidenceとしてreportへ記録しない |
| `closure_claim`         | `none`                                                                                |
| Expected handoff        | 新しいpushed exact HEAD、`ready_for_fresh_review`、fresh Red v3待ち                          |

GitHub named branchとsource HEADの一致を確認した。Red v2は、0.17 direct readerのmixed inventory fail-openと、push済みrepair HEADに追随していないreport current stateだけをP1とした。

この修正結果は既存Candidateの追記・上書きではなく、次の新identityを持つ**完全置換Candidate**として扱う。

```text
candidate_version = s09-blue-repair-v2
candidate_id = iss-00354-s09-blue-repair-v2-<UTC timestamp>
candidate_created_at = <ISO-8601 UTC timestamp>
source_head = ec179c301c045f94d54abea308c47e79d16c5979
replaces_candidate_head = ec179c301c045f94d54abea308c47e79d16c5979
resulting_head = <new pushed exact SHA>
review_target_head = <same new pushed exact SHA>
closure_claim = none
handoff_status = ready_for_fresh_review
```

一つのUTC timestampをbrief artifact、report EAL、worker handoffで共有する。既存のS09 brief、characterization receipt、Red v1/v2 reviewは変更しない。

---

## 1. 目的

本修正は次の二点だけを実施する。

1. Oracle `0.17.0`の`snapshot_authoring_zip_0170()`が、artifact inventory全件について`kind == "file"`を確認してから共通ZIP snapshot処理へ進むようにする。
2. `report.md`のS09 current-state表示を、既にcommit/push済みでRed v2のreview対象となったHEAD `ec179c301c045f94d54abea308c47e79d16c5979`へ同期する。

Red v2で確認済みの次の契約は変更しない。

* exact `0.16.1` / `0.17.0` profile registry
* unknown / malformed version fail-closed
* 0.16.1 browser argv、session argv、Review JSON、repository sentinel
* 0.17 file-only ZIP/core reader
* `transfer` / `origin`をauthorityにしない境界
* `completed`だけをterminalとする0.17 decoder
* 0.17 Reviewerのpre-submit block
* profile-owned harvest/capture builders
* generic recoveryの現行実装
* S10以降の未実装境界

Canonical planは、0.17 artifact schemaをcharacterize済み範囲へ限定し、unknownまたはpartial schemaをfail-closedにすることをS09の責務としている。

---

## 2. ファイルallowlist

`ISSUE_DIR`:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract
```

### 2.1 Runtime

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

### 2.2 Unit tests

```text
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
```

### 2.3 Evidence

```text
${ISSUE_DIR}/report.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md
```

### 2.4 Expected actual diff

最小実装で内容変更が必要なのは原則として次の4ファイルだけである。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
${ISSUE_DIR}/report.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v2-blue-repair-v2-20260806.md
```

`issue_planning_chatgpt.py`と`test_issue_planning_chatgpt.py`はallowlist内だが、**expected no-op / regression-only**とする。型整合または既存fixture共有のために編集する場合も、Red v2の二findingに直接必要な最小差分に限定し、browser policy、profile selection、Reviewer block、recovery behaviorを変更しない。

---

## 3. 禁止事項

次は実施しない。

* requirement、design、plan、ADRの変更
* application、domain、commands、CLI、bootstrapの変更
* S10以降のstage taxonomy、submission evidence、failure mapping
* inline fallbackの実行
* new-execution retry loop
* artifact-pending stateまたはcapture-specific capabilityの追加
* 独立capture optionの発明
* generic recoveryまたはbuilder invocation policyの変更
* personal wrapperまたはOracle APIの変更
* alternate backend、alternate model、default branchへのfallback
* semver range、unknown patchの受理
* 0.17 transcript、Review JSON、repository sentinel schemaの推測実装
* 0.16.1 readerに0.17専用guardを適用すること
* 共通ZIP helperの意味変更
* Red v1/v2 canonical/raw review bytesの変更
* 既存characterization receipt、旧implementation briefの変更
* 旧Candidate identityの上書き
* S09 closure、S10開始、PR、merge、Issue close、Issue finishの宣言

---

## 4. 事前確認

実装前に次を確認する。

```bash
test "$(git branch --show-current)" = \
  "codex/iss-00354-chatgpt-context-contract"

test "$(git rev-parse HEAD)" = \
  "ec179c301c045f94d54abea308c47e79d16c5979"

git status --short
```

開始時worktreeに既存差分がある場合、その差分を本Candidateへ混入させない。安全に分離できなければ停止する。

次のcurrent code factsを再確認する。

* `snapshot_authoring_zip_0170()`は `_read_metadata_0170()` の後、inventory全件を検査せず `_snapshot_authoring_zip_from_metadata()`へ委譲している。
* 共通helperは`kind == "file"`かつZIP名に一致するentryだけを抽出するため、valid ZIP以外のentryを無視する。
* `has_exact_repository_access_failure_0170()`は既にinventory全件の`kind == "file"`を検査している。
* `snapshot_review_json_0170()`は既にfail-closedである。
* 0.17 reader registryの`review_output_characterized=False`と0.17 Reviewer pre-submit blockは実装済みである。

現行unit testsは、単独の`transcript`、`repository-failure`、kind欠落をrepository sentinel entry pointへ渡すnegative caseは持つが、valid ZIPとのmixed inventoryを`reader.snapshot_authoring_zip()`へ直接渡すcaseを持たない。

---

## 5. RT-354-S09-V2-001 — 最小runtime修正

### 5.1 原因

現在の処理は次の非対称性を持つ。

```text
has_exact_repository_access_failure_0170
  -> 全artifactのkind=fileを要求
  -> mixed inventoryをreject

snapshot_authoring_zip_0170
  -> 全artifactのkindを検査しない
  -> 共通helperがvalid ZIPだけを抽出
  -> transcript / repository-failure / missing-kindを無視してsuccess
```

通常orchestrationではsentinel判定が先に実行されるためmixed inventoryは拒否されるが、reader自身の安全性がcall orderへ依存している。Red v2は直接reader callでこの非対称性を再現している。

### 5.2 追加する0.17専用guard

`issue_planning_oracle_artifact.py`へprivate helperを追加する。

推奨形:

```python
def _require_oracle_0170_file_only_inventory(
    metadata: dict[str, Any],
) -> list[dict[str, Any]]:
    artifacts = _artifact_inventory(metadata)
    if any(item.get("kind") != "file" for item in artifacts):
        raise OracleArtifactError("oracle_artifact_rejected")
    return artifacts
```

契約:

* inventoryがlistでない、上限超過、entryがdictでない場合は既存 `_artifact_inventory()` がrejectする。
* `kind == "file"`以外のentryが一件でもあれば`oracle_artifact_rejected`。
* kind欠落は`None != "file"`としてreject。
* 空inventoryはこのguardではrejectしない。後続の既存ZIP helperが`oracle_artifact_missing`を返す現行semanticsを維持する。
* `transfer`、`origin`等の追加fieldは無視する。
* core `path`、`sizeBytes`、`sha256`、`validation.ok`の検証は既存処理を維持する。
* helperを0.16.1 pathへ適用しない。

### 5.3 `snapshot_authoring_zip_0170()`の変更

次の順序にする。

```python
def snapshot_authoring_zip_0170(...):
    metadata = _read_metadata_0170(
        session_root,
        session_id=session_id,
        oracle_version=oracle_version,
    )
    _require_oracle_0170_file_only_inventory(metadata)
    return _snapshot_authoring_zip_from_metadata(
        session_root,
        metadata=metadata,
        staging_dir=staging_dir,
    )
```

必須条件:

* guardは共通ZIP helperへの委譲**前**に実行する。
* mixed inventoryではartifact fileをopenしない。
* staging snapshotを作成しない。
* valid ZIPだけを選んで未確認entryを捨てる挙動を禁止する。

### 5.4 `has_exact_repository_access_failure_0170()`の整理

既存のinline guardを同じhelperへ置換してよい。

```python
artifacts = _require_oracle_0170_file_only_inventory(metadata)
```

ただしこれは重複除去だけであり、behaviorを変更しない。

```text
file-only inventory -> False
transcript / repository-failure / missing kind / mixed -> reject
```

新しいgeneric abstraction、reader protocol、public capability fieldは追加しない。

### 5.5 共通helperを変更しない

次は変更禁止である。

```text
_snapshot_authoring_zip_from_metadata
_artifact_inventory
_snapshot_artifact
_zip_internal_root
```

`_snapshot_authoring_zip_from_metadata()`は0.16.1 behaviorを保持する共有primitiveのままとする。0.17固有のfail-closed条件は0.17 entry point直下へ置く。

---

## 6. RT-354-S09-V2-001 — テスト行列

### 6.1 必須negative tests

`tests/unit/infra/test_issue_planning_oracle_artifact.py`へ、`reader.snapshot_authoring_zip()`を直接呼ぶparameterized testを追加する。

推奨test名:

```python
test_0170_authoring_zip_rejects_mixed_uncharacterized_inventory
```

| Case | Inventory                               | Expected                   |
| ---- | --------------------------------------- | -------------------------- |
| A    | valid ZIP `file` + `transcript`         | `oracle_artifact_rejected` |
| B    | valid ZIP `file` + `repository-failure` | `oracle_artifact_rejected` |
| C    | valid ZIP `file` + kind欠落entry          | `oracle_artifact_rejected` |

各caseについて、未characterize entryをvalid fileの前後両方へ配置する。

```python
@pytest.mark.parametrize("unknown_first", [False, True])
```

これにより先頭entryだけを検査する誤実装を防ぐ。

各testで次をassertする。

```text
OracleArtifactError.code == "oracle_artifact_rejected"
snapshot resultなし
staging artifactなし
```

可能なら共通helperをspyし、guard failure時の委譲回数が0であることを固定する。

```python
delegation_calls == []
```

これは「0.17専用guardが共通ZIP helperへの委譲前に実行される」ことを直接検証する。

### 6.2 必須positive test

既存file-only success testを維持し、明示的に次をassertする。

```text
inventory = [valid ZIP file]
snapshot succeeds
observed transport filename matches
size and SHA match actual ZIP
internal root remains valid
```

推奨test名:

```python
test_0170_authoring_zip_accepts_file_only_valid_zip
```

既存の

```python
test_0170_reader_accepts_core_schema_and_ignores_transfer_origin
```

をこのpositive testとして強化してもよい。`transfer` / `origin`は存在してもpath・size・SHA・validation authorityにならないことを維持する。

### 6.3 既存negative regression

次を削除・緩和しない。

* 0.17 wrong version
* invalid status
* Review transcript rejection
* repository sentinel rejection
* unknown single kind rejection
* core path defect
* size mismatch
* SHA mismatch
* `validation.ok=false`
* cross-version reader rejection

### 6.4 0.16.1 regression

次を維持する。

* 0.16.1 authoring ZIP snapshot
* 0.16.1 Review JSON
* exact repository sentinel
* near-match sentinelが`False`
* sentinel + file contradictionがreject
* descriptor-rooted open
* mutation / staging rehash rejection
* path containment
* ZIP limits

0.17 file-only guardのために0.16.1共通parserまたは共有helperのsemanticsを変えない。

### 6.5 `test_issue_planning_chatgpt.py`

新しいproduction behaviorは不要である。次の既存testsをregressionとして実行する。

* exact 0.17 profile builder
* completed-only decoder
* 0.17 normal Planner ZIP success
* 0.17 harvest builder ownership
* 0.17 Reviewer pre-submit block
* incomplete review capability block
* unknown `0.17.1` fail-closed

Current orchestration testsはこれらを既に固定している。

追加する場合も、mixed inventoryがpublic resultで

```text
rejected / oracle_artifact_rejected
```

となる既存orchestration behaviorの確認に限定する。retry、capture、stage mappingを追加しない。

---

## 7. RT-354-S09-V2-002 — report-only同期

### 7.1 修正対象

Red v2が指定した次のcurrent surfacesを同期する。

1. `EAL-073`
2. Delegated Worker EvidenceのS09行
3. Reviewer Gate StatusのS09行
4. Milestone / Commit Candidate GateのS09行

Red v2によると、これらの一部が、既にpushされRed v2のreview対象となったHEAD `ec179c...`を「commit/push予定」「未実施」「pending commit」と記録している。

### 7.2 EAL-073の同期

EAL-073へ次を明示する。

```text
source baseline = ac84de312072028ad864d06ae018b3ccf196051d
implementation/resulting HEAD = ec179c301c045f94d54abea308c47e79d16c5979
named branch parity = identical / ahead 0 / behind 0
commit status = committed and pushed
review status = fresh Red v2 completed, FAIL P0=0/P1=2
superseding review evidence = EAL-074
closure claim = none
```

EAL-073のテスト件数、修正内容、EAL-068 SHA訂正、0.16.1/0.17境界は保持する。

次のfuture wordingを除去する。

```text
許可4ファイルとreport/evidenceをcommit/pushし...
commit/push後にfresh Red v2...
fresh Red v2は未実施
pending commit
current worktree contains ... pending commit
```

EAL-073の次アクションは、既に完了したcommit/pushまたはRed v2ではなく、次へ変更する。

```text
EAL-074のRed v2 findingsをBlue repair v2へ渡す。
新しいreplacement Candidateをcommit/pushし、fresh Red v3へ渡す。
```

### 7.3 Delegated Worker Evidence

S09行を次の時制へ統一する。

```text
Blue repair v1 implementation at ec179c... is committed and pushed.
Fresh Red v2 at ec179c... completed with P0=0/P1=2.
V2-001 and V2-002 are the active repair scope.
```

古い「commit/pushとfresh Red v2は未実施」を残さない。

### 7.4 Reviewer Gate Status

S09行は次を唯一のcurrent stateとする。

```text
fresh Red v1: FAIL at ac84de...
fresh Red v2: FAIL at ec179c...
active findings: RT-354-S09-V2-001 / RT-354-S09-V2-002
next gate: fresh Red v3 at the new pushed replacement HEAD
closure: none
```

Red v1またはRed v2をPASSへ変更しない。

### 7.5 Milestone / Commit Candidate Gate

旧Blue repair v1について次を記録する。

```text
commit = ec179c301c045f94d54abea308c47e79d16c5979
branch parity = identical / ahead 0 / behind 0
reviewed by fresh Red v2
review result = FAIL
```

新Blue repair v2について、実装前は新Candidate IDだけを示し、実装・push後に次へ同期する。

```text
closure state = repair-v2-applied / review-pending
candidate id = iss-00354-s09-blue-repair-v2-<timestamp>
resulting head = <new pushed exact SHA>
branch parity = identical / ahead 0 / behind 0
handoff = ready_for_fresh_review
closure claim = none
next = fresh Red v3
```

### 7.6 Append-only EAL

既存EAL-074はRed v2正式review evidenceとして変更しない。現行reportはEAL-074をRed v2 FAILと次のBlue repair入力へ結び付けている。

次のavailable IDsを使用する。競合がなければ以下を想定する。

```text
EAL-075 = 本Blue repair v2 briefの採用
EAL-076 = Blue repair v2 implementation / test / pushed Candidate evidence
```

EAL-075:

```text
source = new brief artifact
source role = chatgpt-use-blue-repair-brief-v2
claim = V2-001/V2-002だけの最小修正
adoption status = adopted
closure claim = none
```

EAL-076:

```text
candidate id/version/timestamp
source head = ec179c...
resulting pushed head
changed files
mixed inventory tests
focused/static results
branch parity
handoff = ready_for_fresh_review
closure claim = none
next = fresh Red v3
```

### 7.7 Immutable evidence

次のbytesを変更しない。

```text
${ISSUE_DIR}/reviews/red-team-review-s09-v1.md
${ISSUE_DIR}/reviews/red-team-review-s09-v1-raw.md
${ISSUE_DIR}/reviews/red-team-review-s09-v2.md
${ISSUE_DIR}/reviews/red-team-review-s09-v2-raw.md
${ISSUE_DIR}/artifacts/characterization/s09-oracle-017-native-20260806.md
${ISSUE_DIR}/artifacts/characterization/s09-oracle-017-native-rerun-20260806.md
${ISSUE_DIR}/artifacts/characterization/s09-oracle-017-native-inline-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md
```

Reportはobserved evidence ledgerであり、履歴を上書きせず、実際のcommit、review、next gateを同期する。

---

## 8. 実装手順

1. Named branch、source HEAD、clean worktreeを確認する。
2. 新Candidate IDとUTC timestampを確定する。
3. 本brief本文を新しいbrief artifactへbyte-identicalに保存する。
4. Mixed inventory negative testsを先に追加する。
5. 修正前codeで3種類のmixed inventoryが誤ってsuccessすることを確認する。
6. `_require_oracle_0170_file_only_inventory()`を追加する。
7. `snapshot_authoring_zip_0170()`で共通helperへの委譲前にguardを呼ぶ。
8. `has_exact_repository_access_failure_0170()`を同じguardへ統一する。
9. File-only positive testと全existing reader testsを実行する。
10. `test_issue_planning_chatgpt.py`を無変更regressionとして実行する。
11. `report.md`の4 stale surfacesを`ec179c...`のcommit/push済み状態へ同期する。
12. EAL-075/EAL-076相当をappendする。
13. Existing S09 artifacts/reviewsのbyte不変を確認する。
14. Static、validate、diff、scope auditを実行する。
15. 新Candidateをcommit/pushする。
16. Named branch tipとresulting HEADのexact equalityを確認する。
17. Report/handoffにresulting HEAD、Candidate ID、timestamp、test resultsを記録する。
18. `ready_for_fresh_review`としてfresh Red v3へ渡す。

---

## 9. 検証コマンド

### 9.1 Direct reader tests

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_oracle_artifact.py -q
```

Focused mixed-inventory selection:

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_oracle_artifact.py \
  -k '0170 and (mixed or inventory or authoring_zip)' -q
```

### 9.2 Profile/orchestration regression

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_chatgpt.py -q
```

```bash
uv run pytest \
  tests/unit/infra \
  -k 'oracle and (artifact or session or profile)' -q
```

### 9.3 Static gates

```bash
uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py \
  tests/unit/infra/test_issue_planning_chatgpt.py \
  tests/unit/infra/test_issue_planning_oracle_artifact.py
```

```bash
uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

```bash
./spec-dock/scripts/spec-dock validate
git diff --check
```

### 9.4 0.17 guard audit

```bash
rg -n \
  '_require_oracle_0170_file_only_inventory|snapshot_authoring_zip_0170|has_exact_repository_access_failure_0170' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

期待結果:

* `snapshot_authoring_zip_0170()`がguardを呼ぶ。
* `has_exact_repository_access_failure_0170()`も同じguardを呼ぶ。
* 0.16.1 entry pointsはguardを呼ばない。
* 共通ZIP helperにversion-specific条件を追加していない。

### 9.5 Stale report wording audit

```bash
rg -n \
  'commit/pushとfresh Red v2は未実施|commit/push後のfresh Red v2|pending commit for four provider/test files|current worktree.*pending commit|許可4ファイルとreport/evidenceをcommit/pushし' \
  "$ISSUE_DIR/report.md"
```

期待結果:

* Current S09 surfacesに該当表現0件。
* Red review artifactまたは旧brief artifactは検索・変更対象にしない。

```bash
rg -n \
  'ec179c301c045f94d54abea308c47e79d16c5979|RT-354-S09-V2-001|RT-354-S09-V2-002|fresh Red v3|closure claim `none`' \
  "$ISSUE_DIR/report.md"
```

### 9.6 Immutable artifact check

```bash
git diff --exit-code \
  ec179c301c045f94d54abea308c47e79d16c5979 \
  -- \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1-raw.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v2-raw.md" \
  "$ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-20260806.md" \
  "$ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-rerun-20260806.md" \
  "$ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-inline-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-oracle-017-profile-inline-20260806.md" \
  "$ISSUE_DIR/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md"
```

### 9.7 Scope audit

```bash
git diff --name-only \
  ec179c301c045f94d54abea308c47e79d16c5979...HEAD
```

許容されるpathは本briefのallowlistだけである。

### 9.8 Push/parity

```bash
git status --short
git rev-parse HEAD
git rev-parse '@{upstream}'
git rev-list --left-right --count HEAD...'@{upstream}'
```

期待結果:

```text
worktree clean
HEAD == upstream
ahead 0 / behind 0
```

---

## 10. 停止条件

次のいずれかでは実装を押し切らず停止する。

1. 0.17 mixed inventoryを拒否するために共通0.16.1 helperのsemantics変更が必要になる。
2. 0.17 transcript、repository sentinel、Review JSON schemaの推測が必要になる。
3. `issue_planning_chatgpt.py`のbrowser、profile、Reviewer、recovery behavior変更が必要になる。
4. S10のstage taxonomy、retry、capture判断が必要になる。
5. 新しいpublic reasonまたはpublic optionが必要になる。
6. 0.17 file-only valid ZIPが通らなくなる。
7. `transfer` / `origin`をauthorityとして読む必要が生じる。
8. 0.16.1 Review/sentinel/ZIP regressionsが発生する。
9. Existing S09 receipt、brief、Red review bytesの変更が必要になる。
10. Report current stateを同期するためにRed v1/v2 verdictを変更する必要がある。
11. Source HEADまたはnamed branch parityを確認できない。
12. Allowlist外ファイルの変更が必要になる。
13. Default branch、wrapper、API、alternate backendが必要になる。
14. New Candidate ID、timestamp、source/resulting identityを一意に記録できない。

---

## 11. 完了・handoff条件

Workerは次をすべて満たした場合だけ`ready_for_fresh_review`を返す。

### Runtime

* `snapshot_authoring_zip_0170()`が全inventory entryの`kind == "file"`を委譲前に検査する。
* valid file + `transcript`をrejectする。
* valid file + `repository-failure`をrejectする。
* valid file + kind欠落をrejectする。
* 未characterize entryが前後どちらにあってもrejectする。
* mixed rejection時に共通ZIP helper call countが0。
* file-only valid ZIPはsuccessする。
* 0.16.1 behaviorは不変。

### Report

* EAL-073が`ec179c...`をpushed implementation identityとして記録する。
* Branch parity `identical / ahead 0 / behind 0`を記録する。
* Old repairについてpending commit/push表現が残らない。
* Delegated Worker Evidence、Reviewer Gate Status、Milestone Gateが同じ時制を持つ。
* EAL-074 Red v2 FAILは不変。
* New briefとimplementation evidenceをappend-onlyで記録する。
* New Candidate ID、version、timestamp、source HEAD、resulting HEADを記録する。
* `closure_claim=none`。
* 次ゲートはfresh Red v3。

### Verification

* Focused artifact tests pass。
* `test_issue_planning_chatgpt.py` pass。
* Infra Oracle/profile subset pass。
* Ruff、Mypy、SpecDock validate、`git diff --check` pass。
* Immutable S09 artifacts/reviewsのdiff 0。
* Allowlist外diff 0。
* New Candidate commitがnamed branchへpush済み。
* Local/remote exact HEAD一致。
* Worktree clean。

### Required worker output

```text
candidate_id
candidate_version
candidate_created_at
source_head
resulting_head
review_target_head
changed_files
unchanged_allowlisted_files
mixed_inventory_test_matrix
positive_file_only_result
focused_test_results
static_results
immutable_artifact_check
scope_audit
branch_parity
report_eal_ids
closure_claim = none
handoff_status = ready_for_fresh_review
next_action = fresh Red v3
```

Fresh Red v3でP0/P1=`0`が確認されるまで、S09をcloseせず、S10以降、PR、merge、Issue close、Issue finishへ進まない。
