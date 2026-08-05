# iss-00354 S09 Red v1 — Blue Team 最小修正ブリーフ

## 0. 修正 identity・境界・期待状態

| 項目                       | 値                                                                            |
| ------------------------ | ---------------------------------------------------------------------------- |
| Repository               | `chemitaro/spec-dock`                                                        |
| Named branch             | `codex/iss-00354-chatgpt-context-contract`                                   |
| Source HEAD              | `ac84de312072028ad864d06ae018b3ccf196051d`                                   |
| Branch確認                 | named branch tip と source HEAD は `identical`、ahead `0`、behind `0`            |
| Default branch fallback  | 禁止・未使用                                                                       |
| Review identity          | S09 Fresh Red Team v1                                                        |
| Review verdict           | **FAIL**                                                                     |
| Findings                 | **P0=0 / P1=2**                                                              |
| 修正対象                     | `RT-354-S09-001`、`RT-354-S09-002`のみ                                          |
| Expected resulting state | P1二件のBlue修正、検証、commit/pushが完了し、`ready_for_fresh_red_v2`。S09は未close、S10以降は未開始 |

Red v1はexact HEAD `ac84de312072028ad864d06ae018b3ccf196051d`を対象に、0.17 readerの未characterize schema受理とinline receipt SHA binding不整合の二件だけをP1とした。その他の0.16.1 argv、exact registry、0.17 ZIP/core reader、completed-only decoder、profile-owned builders、unknown-version fail-closedにはfindingを出していない。

### 許可するproduction/testファイル

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_chatgpt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
tests/unit/infra/test_issue_planning_chatgpt.py
tests/unit/infra/test_issue_planning_oracle_artifact.py
```

### 許可するS09 evidenceファイル

`ISSUE_DIR`:

```text
spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/
epics/epic-00331-planning-and-advisory-review/
issues/iss-00354-define-chatgpt-context-and-attachment-contract
```

書込み可能:

```text
${ISSUE_DIR}/report.md
${ISSUE_DIR}/artifacts/implementation-briefs/s09-red-v1-blue-repair-20260806.md
```

identity検証のみ。内容変更禁止:

```text
${ISSUE_DIR}/artifacts/characterization/s09-oracle-017-native-inline-20260806.md
${ISSUE_DIR}/reviews/red-team-review-s09-v1.md
${ISSUE_DIR}/reviews/red-team-review-s09-v1-raw.md
```

### 禁止範囲

* requirement、design、plan、ADRの変更
* application、domain、commands、CLI、bootstrap、generic backend abstractionの変更
* S10のsubmission taxonomy、failure mapping、retry budget
* inline fallback実行、new execution loop
* artifact-pending検出、capture invocation policy、独立capture option
* generic recoveryの追加変更
* Oracle wrapper、API、alternate backend、default branch fallback
* 0.17 Review transcript／sentinel schemaの推測実装
* 0.16.1のbrowser argv、session argv、Review JSON、repository sentinel挙動の変更
* Red v1 review履歴の上書き
* 未観測モデル、Luna、Maxに関するclaim

---

## 1. RT-354-S09-001 — 原因

### 1.1 現在のfail-open経路

Current `issue_planning_oracle_artifact.py`では、0.17専用entry pointがmetadataのversion/statusだけを分離した後、次の0.16.1由来の共有処理へ渡している。

```text
snapshot_review_json_0170
  -> _read_metadata_0170
  -> _snapshot_review_json_from_metadata
  -> artifact.kind == "transcript"
  -> "\n## Answer\n" marker
  -> strict JSON extraction
```

```text
has_exact_repository_access_failure_0170
  -> _read_metadata_0170
  -> _has_exact_repository_access_failure_from_metadata
  -> artifact.kind == "transcript"
  -> "\n## Answer\n" marker
  -> exact "repository access failed"
```

さらに0.17 reader registryは両entry pointを有効な0.17 reader関数として登録している。

0.17 characterizationが確認しているのは、`status=completed`と`kind="file"`のZIP/core artifact schemaである。0.17 transcript、`## Answer` marker、Review JSON extraction、repository sentinelは確認されていない。それにもかかわらず0.16.1 transcriptを0.17として受理するため、partial schemaをfail-closedにするS09契約に反する。Red v1の再現では、0.17 completed metadataへ0.16.1形式のtranscriptを置くとReview JSONとsentinelの双方が受理された。

### 1.2 テスト欠落

現行0.17 testsは以下を確認している。

* exact reader registry
* ZIP core schema
* `transfer` / `origin`の非authority化
* wrong version binding
* invalid status

一方、0.17 Review JSONとrepository sentinelのnegative fixtureがない。0.16.1 positive fixtureだけが共有parserを通るため、version間のfail-openを検出できない。

---

## 2. RT-354-S09-001 — 最小production修正

## 2.1 ReaderにReview出力のcharacterization状態を明示する

`OracleArtifactReader`へprivate booleanを一つ追加する。

```python
review_output_characterized: bool
```

Binding:

```text
Oracle 0.16.1 reader -> review_output_characterized=True
Oracle 0.17.0 reader -> review_output_characterized=False
```

これは新しいpublic architectureではない。既存のversion-bound readerが、現在安全に実行可能なentry pointを明示するためのprivate fail-closed fieldである。

`issue_planning_chatgpt._profile_is_complete()`では、同fieldが実際の`bool`であることを確認する。`None`、欠落、非boolはprofile incompleteとしてversion probe後に停止する。

## 2.2 0.17 Reviewer operationをprompt前にblockする

`invoke_issue_planning_chatgpt()`でprofile選択・help capability検証後、managed Chrome接続およびbrowser argv構築より前に次を判定する。

```python
if role == "reviewer" and not profile.artifact_reader.review_output_characterized:
    return _result(
        "blocked",
        "oracle_capability_unsupported",
        source_evidence,
        None,
    )
```

条件にversion literalを置かない。selected profileが所有するreader capabilityだけを参照する。

Expected 0.17 Reviewer call counts:

| 呼出し                      | 回数 |
| ------------------------ | -: |
| `oracle --version`       |  1 |
| `oracle --help`          |  1 |
| `oracle session --help`  |  1 |
| managed Chrome preflight |  0 |
| browser argv builder     |  0 |
| prompt subprocess        |  0 |
| harvest builder          |  0 |
| capture builder          |  0 |
| session directory作成      |  0 |

Public result:

```text
status=blocked
reason=oracle_capability_unsupported
```

0.16.1 Reviewerは従来どおりpromptを一度送信し、既存closed Review JSONを返す。

## 2.3 `snapshot_review_json_0170()`を明示的fail-closedにする

0.17関数から `_snapshot_review_json_from_metadata()` への委譲を削除する。

最小形:

```python
def snapshot_review_json_0170(...):
    _read_metadata_0170(
        session_root,
        session_id=session_id,
        oracle_version=oracle_version,
    )
    _ = staging_dir
    raise OracleArtifactError("oracle_artifact_rejected")
```

要件:

* `artifact.kind="transcript"`を検索しない。
* `_ANSWER_MARKER`を参照しない。
* JSON payloadを抽出しない。
* 0.16.1 helperを呼ばない。
* version/session/mode/statusの基本metadata defectは従来どおりrejectする。
* 将来0.17 Review schemaをcharacterizeするまでpositive pathを作らない。

Reviewerの通常runtimeは前項のpre-submit blockによりこの関数へ到達しない。直接readerを誤用してもfail-closedになる二重境界とする。

## 2.4 `has_exact_repository_access_failure_0170()`をnegative-onlyにする

0.17関数から `_has_exact_repository_access_failure_from_metadata()` への委譲を削除する。

許容するのはcharacterize済みのfile artifact inventoryのみである。

```python
def has_exact_repository_access_failure_0170(...):
    metadata = _read_metadata_0170(
        session_root,
        session_id=session_id,
        oracle_version=oracle_version,
    )
    artifacts = _artifact_inventory(metadata)
    if any(item.get("kind") != "file" for item in artifacts):
        raise OracleArtifactError("oracle_artifact_rejected")
    _ = staging_dir
    return False
```

意味:

* 0.17のrepository sentinel positive schemaは未characterizeなので、`True`を返す経路を作らない。
* `transcript`、kind欠落、未知kind、file+transcriptはすべてrejectする。
* file-only inventoryではsentinelなしとして`False`を返し、続く0.17 ZIP/core readerへ処理を渡す。
* 空inventoryは`False`後に既存authoring snapshotが`oracle_artifact_missing`でrejectするため、成功へ昇格しない。
* `repository access failed`という本文を検索しない。
* 0.16.1 sentinel parserは一切変更しない。

これにより0.17 Planning / Semantic Revisionのcharacterize済みZIP pathを維持しつつ、未characterize transcript形式だけを閉じられる。

---

## 3. RT-354-S09-001 — 必須回帰テスト

## 3.1 `test_issue_planning_oracle_artifact.py`

### Negative 1: 0.17が0.16.1 Review transcriptを拒否する

Fixture:

```text
version = 0.17.0
status = completed
mode = browser
artifact.kind = transcript
payload = "\n## Answer\n{\"verdict\":\"pass\"}"
```

Assertion:

```text
reader.snapshot_review_json(...) raises OracleArtifactError
error.code == "oracle_artifact_rejected"
```

JSON payloadを返さないことも確認する。

推奨test名:

```python
test_0170_reader_rejects_uncharacterized_0161_review_transcript
```

### Negative 2: 0.17が0.16.1 repository sentinelを拒否する

Fixture:

```text
version = 0.17.0
status = completed
artifact.kind = transcript
answer = "repository access failed"
```

Assertion:

```text
reader.has_exact_repository_access_failure(...) raises OracleArtifactError
error.code == "oracle_artifact_rejected"
```

`True`を返さないことを明示する。

推奨test名:

```python
test_0170_reader_rejects_uncharacterized_0161_repository_sentinel
```

### Negative 3: 0.17未知artifact kindを拒否する

少なくとも次をparameterizeする。

```text
transcript
repository-failure
missing kind
file + transcript
```

すべて`oracle_artifact_rejected`。

### Positive 1: 0.17 file-only core inventoryを維持する

既存のvalid 0.17 ZIP fixtureについて:

```text
has_exact_repository_access_failure_0170(...) is False
snapshot_authoring_zip_0170(...) succeeds
```

`transfer` / `origin`をpath、size、SHA、validation authorityに使用しない既存assertionも維持する。

### Positive 2: 0.16.1 behaviorを維持する

既存testを削除・書換えしない。

```text
0.16.1 Review transcript -> closed JSON success
0.16.1 exact repository sentinel -> True
0.16.1 near-match sentinel -> False
0.16.1 sentinel + file contradiction -> reject
```

## 3.2 `test_issue_planning_chatgpt.py`

### Negative 4: 0.17 Reviewerをpre-submit blockする

推奨test名:

```python
test_0170_reviewer_blocks_before_managed_chrome_prompt_or_recovery
```

Assertion:

```text
result = blocked / oracle_capability_unsupported
version/root-help/session-help = 1/1/1
managed Chrome preflight = 0
browser builder = 0
prompt = 0
harvest builder = 0
capture builder = 0
session directory absent
```

### Positive 3: 0.17 Planner ZIP pathを維持する

既存の `test_0170_runtime_uses_select_always_profile_and_reader` 相当を保持する。

```text
prompt = 1
harvest = 0
capture = 0
result = pass / transport_received
authoring ZIP present
Review JSON absent
```

### Positive 4: reader capability binding

Registry testへ追加する。

```text
0.16.1 reader.review_output_characterized is True
0.17.0 reader.review_output_characterized is False
```

### Negative 5: malformed capability declaration

0.17 readerの`review_output_characterized`をtest内で`None`へ置換し、profile completenessがfail-closedになることを確認する。

```text
version probe = 1
help = 0
prompt = 0
recovery = 0
supported_by_current_runtime = False
```

---

## 4. RT-354-S09-002 — 原因

Canonical inline receiptの実bytesに対するSHA-256は次である。

```text
60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8
```

一方、`report.md` EAL-068は次を記録している。

```text
3fa59e69ad5b1f2345c62f9b5afabe394851ac4ad0c7be07773f55c5e53da370
```

このため、`inline_mode_characterized=True`のpositive evidenceがcanonical bytesへbindingされていない。Red v1はGitHub receipt blobと添付receiptが同一であることを確認しており、別revisionや変換bytesの比較ではない。

GitHub上のcanonical receipt本文はtext-only inline capability、`current / verified=false`、validated ZIP、`status=completed`の境界を保持している。内容自体を変更すべきfindingではない。

既存S09 inline briefも、receipt path・bytes・SHAとEALの一致を明示closure条件にしている。

---

## 5. RT-354-S09-002 — report-only修正

Canonical inline receiptを正本とする。Receipt bytesは変更しない。

`report.md` EAL-068の次の一fieldだけを訂正する。

```diff
- receipt SHA-256 `3fa59e69ad5b1f2345c62f9b5afabe394851ac4ad0c7be07773f55c5e53da370`
+ receipt SHA-256 `60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8`
```

変更してはならない値:

```text
observed artifact SHA-256
= 9566748c79c49e5369d36fff3c76d2cb65250dc281fdaca563c5c0be3bd827a2
```

この二つは別identityである。

* `60f8...` — Markdown receipt file bytes
* `9566...` — Oracleが生成したZIP artifact bytes

### Report履歴契約

* EAL-068はreceipt digestの事実訂正だけを行う。
* EAL-071のRed v1 FAIL、finding IDs、reviewed HEAD、review SHAを変更しない。
* `reviews/red-team-review-s09-v1.md`とrawのbytesを変更しない。
* Red v1をPASS、superseded、resolvedへ書換えない。
* 修正実施後はnext available EAL row、想定`EAL-072`へBlue repair evidenceをappendする。
* S09 current gateは`repair applied / fresh Red v2 pending`とし、`pass`または`closed`にしない。

EAL-072へ記録する最小情報:

```text
source HEAD = ac84de312072028ad864d06ae018b3ccf196051d
findings repaired = RT-354-S09-001, RT-354-S09-002
changed production/test files
canonical inline receipt SHA = 60f8...
receipt bytes changed = no
Red v1 evidence changed = no
focused/static verification results
resulting pushed HEAD
state = repair_applied_pending_fresh_review
next = fresh Red v2
```

---

## 6. 実装順序

1. Source HEADとnamed branch tipがexact一致することを再確認する。
2. Red v1 canonical/raw、inline receipt、EAL-068の現行bytesをhash付きで記録する。
3. Artifact reader negative testsを先に追加し、現行codeで次がfailすることを確認する。

   * 0.17 legacy Review transcript rejection
   * 0.17 legacy repository sentinel rejection
4. Reviewer pre-submit block testを追加し、現行codeではpromptが送信されることを確認する。
5. `OracleArtifactReader.review_output_characterized`を追加する。
6. 0.16.1=`True`、0.17.0=`False`へbindする。
7. Generic invocationへprofile-owned reviewer capability checkを追加する。
8. `snapshot_review_json_0170()`をunconditional fail-closedにする。
9. `has_exact_repository_access_failure_0170()`をfile-only negative gateへ置換する。
10. Focused testsを実行する。
11. 0.16.1 full regressionとexisting 0.17 ZIP/core testsを実行する。
12. Canonical inline receiptのSHA-256を再計算する。
13. EAL-068のreceipt SHAだけを訂正する。
14. EAL-072とcurrent S09 repair-pending stateを追記する。
15. Scope/static/validateを実行する。
16. Commit/push後のexact HEADを確認し、fresh Red v2へ渡す。

---

## 7. 検証コマンド

### 7.1 Focused tests

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_oracle_artifact.py -q
```

```bash
uv run pytest \
  tests/unit/infra/test_issue_planning_chatgpt.py -q
```

```bash
uv run pytest \
  tests/unit/infra \
  -k 'oracle and (artifact or session or profile)' -q
```

### 7.2 Static checks

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

### 7.3 Version-local parser audit

```bash
rg -n \
  '_ANSWER_MARKER|repository access failed|_snapshot_review_json_from_metadata|_has_exact_repository_access_failure_from_metadata' \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_oracle_artifact.py
```

Expected:

* 0.16.1 pathでは既存共有parser参照が残る。
* `snapshot_review_json_0170`から共有Review parser参照は0。
* `has_exact_repository_access_failure_0170`から共有sentinel parser参照は0。
* 0.17 pathに`repository access failed`本文判定は0。

### 7.4 Receipt SHA verification

```bash
python - <<'PY'
from hashlib import sha256
from pathlib import Path

path = Path(
    "spec-dock/initiatives/"
    "init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/"
    "epics/epic-00331-planning-and-advisory-review/"
    "issues/iss-00354-define-chatgpt-context-and-attachment-contract/"
    "artifacts/characterization/"
    "s09-oracle-017-native-inline-20260806.md"
)
actual = sha256(path.read_bytes()).hexdigest()
expected = "60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8"
assert actual == expected, (actual, expected)
print(actual)
PY
```

### 7.5 Receipt immutability

```bash
git diff --exit-code \
  ac84de312072028ad864d06ae018b3ccf196051d \
  -- \
  "$ISSUE_DIR/artifacts/characterization/s09-oracle-017-native-inline-20260806.md"
```

Expected: diff 0。

### 7.6 Report SHA audit

```bash
rg -n \
  'EAL-068|60f8a83fe78152264a83656c9ad7f84d27f8bec2bafdb27179b304c5094544a8|3fa59e69ad5b1f2345c62f9b5afabe394851ac4ad0c7be07773f55c5e53da370' \
  "$ISSUE_DIR/report.md"
```

Expected:

* EAL-068に`60f8...`が一件。
* `report.md`内の旧`3fa...`は0件。
* Red review artifact内の旧値は履歴証跡なので置換対象外。

### 7.7 Review evidence immutability

```bash
git diff --exit-code \
  ac84de312072028ad864d06ae018b3ccf196051d \
  -- \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1.md" \
  "$ISSUE_DIR/reviews/red-team-review-s09-v1-raw.md"
```

### 7.8 Scope audit

```bash
git diff --name-only \
  ac84de312072028ad864d06ae018b3ccf196051d...HEAD
```

許容される差分は、本ブリーフ冒頭の4 source/test、`report.md`、新しいS09 repair brief artifactだけである。

---

## 8. 停止条件

次のいずれかでは修正を押し切らず停止する。

1. 0.17 Review transcript、closed JSON、repository sentinelの新しいschemaを推測する必要がある。
2. 0.17 Reviewerをprompt前にblockするため、application、domain、CLI、public optionの変更が必要になる。
3. `oracle_capability_unsupported`以外の新しいpublic reasonが必要になる。
4. 0.17 Planning / Semantic Revisionのvalid ZIP pathを無効化しなければfail-closedにできない。
5. 0.16.1 Review JSONまたはrepository sentinel behaviorが変わる。
6. Existing 0.17 ZIP/core、`transfer` / `origin`、completed-only status testsが失敗する。
7. Generic recovery、harvest/capture builder、stage taxonomyを変更する必要がある。
8. Canonical receipt bytesを旧EAL SHAへ合わせるために書換える必要がある。
9. Red v1 canonical/raw evidenceを編集する必要がある。
10. Wrong SHAの一括置換がhistorical review evidenceまで変更する。
11. 許可パス外のproduction/test変更が必要になる。
12. Exact branch/HEADまたはreceipt SHAを再現できない。

Canonical planは、partial schemaまたはrequired profile contractを安全にcharacterizeできない場合にfail-closedとし、S10以降をproduction-enableしないことを要求している。

---

## 9. 修正完了条件

Blue workerの完了条件は次のすべてである。

* `RT-354-S09-001`

  * 0.17 legacy Review transcriptを直接readerが拒否する。
  * 0.17 legacy repository sentinelを直接readerが拒否する。
  * 0.17 Reviewerのprompt call countが0。
  * 0.17 file-only ZIP/core pathは維持される。
  * 0.16.1 Review/sentinel positive behaviorは維持される。
* `RT-354-S09-002`

  * Canonical receipt bytesは変更されていない。
  * Receipt SHAは`60f8a83f...4544a8`。
  * EAL-068のreceipt SHAが同値。
  * ZIP artifact SHA `9566748c...827a2`は変更されていない。
  * Red v1履歴は変更されていない。
* Focused pytest、Ruff、Mypy、validate、diff-checkがpassする。
* Allowlist外diffが0。
* Resulting commitがnamed branchへpushされ、local/remote exact HEADが一致する。
* Report stateは`repair_applied_pending_fresh_review`。
* S09 closure claimは`none`。
* 次アクションは、v1とは別のfresh Red Team v2による新しいexact pushed HEADの再レビューである。
* Fresh Red v2でP0/P1=0になるまで、S09 closure、S10開始、PR、merge、Issue close、Issue finishを保留する。
