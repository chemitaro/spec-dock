# iss-00354 S06 Blue Team repair brief v1

> **対象:** `iss-00354` / S06 Blue continuity・fresh Red
> **修正入力:** Fresh Red v1 `FAIL`、P0=0 / P1=3 / P2=1 / P3=0
> **採用範囲:** `RT-354-S06-001`〜`003`のP1修正、および`RT-354-S06-004`の証跡運用補正のみ
> **非対象:** アーキテクチャ再設計、S07以降、CLI、infra、Oracle adapter、canonical requirement/design/plan、PR、merge、Issue close

## 1. Identity / repair baseline

| 項目                       | 確認結果                                                               |
| ------------------------ | ------------------------------------------------------------------ |
| Repository               | `chemitaro/spec-dock`                                              |
| Branch                   | `codex/iss-00354-chatgpt-context-contract`                         |
| Reviewed source HEAD     | `a93d38bc07a11a62a63ebdab19f9d26a0cb39938`                         |
| Branch tip comparison    | `identical` / ahead `0` / behind `0`                               |
| Default branch fallback  | 未使用                                                                |
| Commit                   | `feat(s06): issue planningでports境界をfresh review継続性へ接続`             |
| Fresh Red review SHA-256 | `adeadc27ba779688910e0c2933fadc122d14325bf843e84916ce2be6b03fc59b` |
| Review file hash check   | 添付ファイルの実測SHA-256と一致                                                |

GitHub connectorでnamed branchを直接確認し、指定HEADとbranch tipが一致した。commit identityも同じSHAである。 Fresh Red v1の正式入力とP1三件・P2一件は添付レビューを正本とする。

現行blob:

```text
application/ports.py                          3b8f6aaeac1300495dd359c04fe0f785b970ab08
application/issue_planning.py                 597235d28c0f2e93628aeb237d97c052d7961eff
tests/unit/application/test_issue_planning.py 8e43595363a8fb4709201fa28dea0cf65ec12165
tests/unit/domain/test_issue_planning_contracts.py
                                              077a790d6834b8974cb571bbb8493ec2aca587bc
```

現行`BlueThreadBinding`はdigestを検証せず、`BlueBindingResolution`もruntime上の未知statusを閉じていない。`ThreadInvocationReceipt`にはmode別・cross-field invariantがない。 また、applicationはreceipt検証前に`receipt.result`を返し、CreateではCandidate publication後にmissing bindingを検出し得る。  Semantic Revisionは`exact` bindingのlineage digestをprior Candidate bindingと比較せず、`exact`・`ambiguous`以外を実質`unavailable`として扱う。

## 2. Exact repair scope and allowed files

### Code/test repair allowlist

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/domain/test_issue_planning_contracts.py
```

`domain/issue_planning_contracts.py`のproduction変更は不要。既存の`GitBoundOperationBindingV1.binding_sha256`をlineage authorityとして使う。

### Read-only

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/**
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/**
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/**
tests/unit/infra/**
tests/unit/commands/**
tests/cli_runtime/**
tests/integration/**
requirement.md
design.md
plan.md
report.md
.assurance.json
provider / installed / dogfood projection
```

Canonical S06契約は、verified matching lineageだけをBlue継続に使用し、binding unavailableかつlineage一意の場合だけcomplete current inputでnew Blue、曖昧ならbackend invocation 0とする。provider handle/transcriptはpublic artifactへ出さない。 S06 execution cardもapplication/domainと既存unit testsだけを許可している。

## 3. Required implementation changes

### 3.1 `application/ports.py`

#### `BlueThreadBinding`

`__post_init__()`を追加し、次を強制する。

```text
lineage_sha256:
  - str
  - lowercase hexadecimal
  - exactly 64 characters

provider_handle:
  - None禁止
  - repr=False
  - compare=False
```

`to_dict()`、`from_dict()`、JSON serializerは追加しない。

#### `BlueBindingResolution`

`status`をruntimeで次の三値に閉じる。

```text
exact
unavailable
ambiguous
```

不明statusはconstructorで`ValueError`。既存の組合せ制約も維持する。

```text
exact       -> binding必須
unavailable -> binding禁止
ambiguous   -> binding禁止
```

#### `ThreadInvocationReceipt`

新たにmodeを持たせる。

```python
ThreadInvocationMode = Literal["new_blue", "continuation", "fresh_red"]
```

mode、submission state、binding、public resultを次の閉じた組合せにする。

| mode           | submission state            | 必須binding                | 禁止binding      |
| -------------- | --------------------------- | ------------------------ | -------------- |
| `new_blue`     | `successful`                | valid `blue_binding`     | `red_binding`  |
| `continuation` | `successful`                | valid `blue_binding`     | `red_binding`  |
| `fresh_red`    | `successful`                | non-`None` `red_binding` | `blue_binding` |
| 任意             | `not_submitted` / `unknown` | なし                       | Blue/Red両方     |

追加不変条件:

* `result.status == "pass"`なら`submission_state == "successful"`が必須。
* `not_submitted`または`unknown`とpass-resultの組合せは禁止。
* `successful` Blueで`blue_binding=None`は禁止。
* `successful` fresh Redで`red_binding=None`は禁止。
* Blue/Red両bindingの同時保持は禁止。
* `continuation_unavailable_before_submission=True`は、mode=`continuation`、state=`not_submitted`、non-pass result、bindingなしの場合だけ許可。
* private receiptにserializerを追加しない。

型定義だけに依存せず、application側でも同じ条件を再検査する。test doubleや破損portがdataclass検証を迂回してもfail-closedにするためである。

### 3.2 `application/issue_planning.py`

#### 新規private helper

```text
_validate_blue_resolution(...)
_validate_thread_receipt(...)
_require_publishable_thread_receipt(...)
_thread_contract_failure(...)
```

`_thread_contract_failure()`は既存public pairを使う。

```python
PlanningInvocationResult(
    status="blocked",
    reason="planning_context_rejected",
    details=("thread_receipt_invalid",),
)
```

lineage resolutionの不正は既存detailへ閉じる。

```python
PlanningCommandResult(
    status="blocked",
    reason="planning_context_rejected",
    details=("blue_lineage_ambiguous",),
)
```

#### `_validate_blue_resolution()`

Semantic Revisionが生成した`prior_lineage`に対して次を確認する。

1. `resolution.status`が三値のいずれか。
2. `exact`なら`resolution.binding`が`BlueThreadBinding`。
3. `binding.lineage_sha256`がvalid lowercase SHA-256。
4. `binding.lineage_sha256 == prior_lineage.binding_sha256`。
5. `unavailable` / `ambiguous`ならbindingなし。

未知status、不正SHA、cross-lineage digest、破損bindingはすべてtransport/backend invocation前に停止する。`unavailable`へfall throughさせない。

#### `_validate_thread_receipt()`

`_thread_backend_invoker()`がportからreceiptを受け取った直後、`capture()`や`receipt.result`返却より先に実行する。

* modeとreceipt.modeの一致。
* `ThreadInvocationReceipt`の全cross-field invariant。
* continuation successでは、receiptのBlue bindingが要求したbindingと同一objectであること。
* 少なくとも`provider_handle`のobject identityとlineage digestが継続前後で一致すること。
* invalid receiptではcaptureせず、public blocked resultだけを返す。
* port呼出しまたはreceipt構築時の`TypeError`、`ValueError`、`AttributeError`も同じblocked resultへ閉じる。

`thread_port is None`のlegacy one-shot pathはprivate S06 receiptを捏造しない。現行互換経路として直接backend resultを返せるが、**S06 Blue/fresh Red closure evidenceには使用しない**。

#### Create / Review / Semantic Revision publication gate

`transport.status == "pass"`の直後、archive/JSON処理やpublisher呼出しより前に`_require_publishable_thread_receipt()`を呼ぶ。

`thread_port`を使用したoperationでは次が必須。

```text
receipt count == 1
receipt is valid
submission_state == successful
mode matches operation
Blue operation -> valid blue_binding
Fresh Red      -> valid red_binding
```

不成立時:

```text
Candidate publisher calls = 0
Review publisher calls = 0
commit_blue calls = 0
final artifact files = 0
```

これにより、missing bindingをCandidate公開後に検出する現行orphan経路を閉じる。

#### `_commit_published_blue()`

receiptの検証責務を削除し、**事前検証済みreceiptをpublication成功後にcommitするだけ**にする。

```text
valid successful receipt
-> output validation
-> source/current guards
-> Candidate publication
-> commit_blue(receipt, new_lineage)
-> success result
```

`commit_blue()`前のmissing/invalid binding判定でblocked resultを返してはならない。すべてpublisher前に判定する。

`commit_blue()`がfallibleな外部永続化を必要とする場合は停止する。S06内で新しい二相commitやinfra persistenceを追加しない。

#### Semantic Revision resolution

```text
exact:
  digest exact match
  -> same Blue bindingでinvoke_continuation

unavailable:
  -> complete current synthesized inputでinvoke_new_blue最大1回

ambiguous / unknown / invalid / cross-lineage:
  -> backend invocation 0
  -> Human block相当
```

exact continuation後のfallbackは次の全条件を満たす場合だけ許可する。

```text
submission_state == not_submitted
continuation_unavailable_before_submission is True
receipt is otherwise valid
```

その場合も:

* continuation call 1。
* new Blue call 1。
  -同じ`synthesized` object。
  -同じprompt string。
  -同じattachment tupleと各`Path` object。
  -再synthesis、copy、ZIP、attachment drop、wrapper fallbackは0。

`unknown`、successful submission、invalid receipt、flagなし`not_submitted`からnew Blueを開始しない。

## 4. State / lineage / publication invariants

| 条件                                         | 必須結果                                          |
| ------------------------------------------ | --------------------------------------------- |
| invalid Blue SHA                           | constructor拒否。迂回された場合もbackend 0               |
| unknown resolution status                  | backend 0。`unavailable`扱い禁止                   |
| exact cross-lineage binding                | backend 0                                     |
| valid exact binding                        | 同一binding・同一provider handleでcontinuation      |
| resolution unavailable                     | complete inputでnew Blue最大1                    |
| continuation unavailable before submission | 同一synthesized inputでnew Blue最大1               |
| continuation state unknown                 | fallback 0                                    |
| successful Blue without binding            | publication 0                                 |
| successful fresh Red without Red binding   | Review publication 0                          |
| `not_submitted` / `unknown` + pass result  | invalid receipt、publication 0                 |
| Candidate publication failure/collision    | Blue commit 0                                 |
| valid Candidate publication                | publication成功後だけnew lineageへcommit            |
| source HEAD drift                          | resolve / backend / publisher / commitすべて0    |
| Fresh Red                                  | Blue handle・過去Red handleを再利用しない               |
| private evidence                           | Candidate、Review、prompt、public result、reprへ0件 |

## 5. Required tests

### 5.1 Stateful `tc-s06-001`

現在の別々の`_FakeThreadPort`を主要証拠に使わず、一つの`_StatefulThreadPort`と一つのgateway/storeをPlanning、Revision、Reviewで共有する。現行testは各operationを別portで実行しており、cross-operation transactionを証明していない。

必須シーケンス:

```text
Planning successful submission
-> Candidate v1 publication
-> Blue bindingをv1 binding_sha256へcommit
-> Semantic Revisionでv1 lineageをresolve
-> stored Blue bindingと同一object / 同一provider handleでcontinuation
-> Candidate v2 publication
->同じprovider handleをv2 lineageへre-keyしてcommit
-> Candidate v2のFormal Review
-> distinct fresh Red provider handle
-> Red reusable storeは空
```

最低assertion:

```text
create new_blue calls == 1
v1 commit calls == 1
revision resolve digest == v1 output binding SHA
continuation binding is stored v1 binding
revision new_blue calls == 0
v2 committed provider_handle is v1 provider_handle
fresh_red calls == 1
red provider_handle is not Blue provider_handle
Red resolve/commit/reusable-store calls == 0
```

### 5.2 Negative lineage tests

* lowercaseでない、短い、non-hex SHAを`BlueThreadBinding`が拒否。
* exact resolutionが別Candidate digestを返すとbackend 0。
* forged unknown statusを返すとbackend 0。
* forged invalid binding objectを返すとbackend 0。
* `unavailable`だけがnew Blueへ進む。

### 5.3 Receipt/publication matrix

最低限、次をtable-drivenにする。

```text
new_blue + successful + no blue binding
fresh_red + successful + no red binding
not_submitted + pass result
unknown + pass result
not_submitted/unknown + Blue or Red binding
both Blue and Red binding
continuation_unavailable flag with wrong mode/state
continuation successful with different binding object/handle
```

各caseで、invalid constructorまたはapplication blocked、publisher 0、commit 0をassertする。

### 5.4 Unavailable / failure transaction

* exact continuation → `not_submitted` + unavailable flag → new Blue一回。
* unknown state → new Blue 0。
* Candidate publication failure → commit 0、stored lineage 0。
* collision →既存Candidate bytes不変、追加commit 0。
* successful-but-unpublished pending bindingを次回`exact`として返さない。
* source drift →`resolve_blue`、transport、backend、publisher、commitすべて0。

### 5.5 Privacy assertions

private sentinelをprovider handleとfake raw transcriptに使用し、次を走査する。

```text
repr(BlueThreadBinding)
repr(ThreadInvocationReceipt)
PlanningInvocationResult.to_dict()
PlanningCommandResult.to_dict()
published Candidate ZIP entries
published Review JSON / summary
captured prompt
captured attachment path representation
```

sentinel、`provider_handle`、raw transcript、session handle、private URL/pathがすべてzero-matchであること。

`tests/unit/domain/test_issue_planning_contracts.py`には、`GitBoundOperationBindingV1.to_dict()`、`PlanningInvocationResult.to_dict()`、`PlanningCommandResult.to_dict()`の公開shapeがclosedかつcontent-freeで、thread/provider/transcript fieldを持たないassertionを追加する。production domain変更はしない。

テストは次の意図的退行で失敗しなければならない。

* resolverがrequested lineageを無視する。
* `_thread_backend_invoker()`がreceipt検証なしに`result`を返す。
* publisher後にmissing bindingを判定する。
* RedがBlue provider handleを再利用する。
* publication failure時にcommitする。

## 6. P2 evidence / allowlist correction

Fresh Red v1は、旧source `382e49b...`からreviewed HEADまでの差分にS06 brief artifactが含まれ、brief自身の`artifacts/** read-only`と矛盾することをP2として記録した。 GitHub比較でも、旧sourceからtargetまでは次の四pathである。

```text
artifacts/implementation-briefs/s06-blue-continuity-fresh-red-20260805.md
application/ports.py
application/issue_planning.py
tests/unit/application/test_issue_planning.py
```

修正時は実装allowlistと証跡commitを分離する。

### 必須commit順序

1. **Evidence-only baseline commit**

   * 親orchestratorが本repair briefとFresh Red v1をbyte-identicalに保存。
   * production/test変更なし。
   * canonical three documentsと`report.md`は変更しない。
   * 例:

```text
artifacts/implementation-briefs/s06-blue-repair-v1-20260805.md
reviews/red-team-review-s06-code-v1.md
```

2. **Repair implementation commit**

   * Evidence-only commitを`REPAIR_BASE`とする。
   * 変更は四つのcode/test allowlistだけ。
   * `artifacts/**`、`reviews/**`、`report.md`を含めない。

3. **Fresh Red v2後のclosure evidence commit**

   * Fresh Red v2のexact reviewed HEADと結果を保存。
   * `report.md`更新は親orchestratorが別commitで行う。
   * code-review HEADと証跡追加後HEADを混同しない。

これにより、「step briefをartifactとして保存」と「implementation workerではartifacts read-only」を同時に満たす。元のP2を無視せず、repaired Candidateのallowlist基準を、brief/reviewが既に存在するevidence-only baselineへrebindする。

## 7. Exact verification commands

```bash
BRANCH=codex/iss-00354-chatgpt-context-contract
REVIEWED_HEAD=a93d38bc07a11a62a63ebdab19f9d26a0cb39938
REPAIR_BASE=<evidence-only-baseline-commit>

git fetch origin "$BRANCH"
test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")"

uv run pytest \
  tests/unit/application/test_issue_planning.py \
  -k 's06 or thread or lineage or receipt' -q

uv run pytest \
  tests/unit/domain/test_issue_planning_contracts.py \
  -k 's06 or binding or privacy or public_contract' -q

uv run pytest \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py -q

uv run pytest tests/unit/application tests/unit/domain -q

uv run ruff check \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py

uv run mypy \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py

./spec-dock/scripts/spec-dock validate
git diff --check
```

Allowlist audit:

```bash
ALLOWED='^(src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/(ports|issue_planning)\.py|tests/unit/application/test_issue_planning\.py|tests/unit/domain/test_issue_planning_contracts\.py)$'

UNEXPECTED="$(
  git diff --name-only "$REPAIR_BASE" HEAD |
  grep -Ev "$ALLOWED" || true
)"
test -z "$UNEXPECTED"
```

Read-only boundary:

```bash
ISSUE_DIR=spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract

git diff --exit-code "$REPAIR_BASE" HEAD -- \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli \
  "$ISSUE_DIR/requirement.md" \
  "$ISSUE_DIR/design.md" \
  "$ISSUE_DIR/plan.md" \
  "$ISSUE_DIR/report.md" \
  "$ISSUE_DIR/artifacts" \
  "$ISSUE_DIR/reviews"
```

## 8. Stop conditions / commit and Fresh Red handoff

次のいずれかで停止する。

* 実装開始時のbranch tipがevidence-only `REPAIR_BASE`と異なる。
* exact binding検証にinfra/session metadata変更が必要になる。
* provider handleをpublic/domain contractへ保存する必要が生じる。
* receipt検証をpublisher前に配置できない。
* `commit_blue()`がfallibleな外部transactionを必要とする。
* unavailable fallbackで同一synthesized input identityを維持できない。
* Red handle reuseをapplication-private contract/testで検出できない。
* application/domain以外のproduction変更が必要になる。
* canonical docs、CLI、infra、S07以降への変更が必要になる。
* focused/application/domain/static gateのいずれかがfailする。

Repair commit候補:

```bash
git add \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py

git commit -m "fix(iss-00354): close S06 lineage and receipt gates"
git push origin "$BRANCH"
```

push後のFresh Red v2 handoffには次を含める。

```text
repository / branch
REPAIR_BASE
resulting exact HEAD
branch tip comparison ahead 0 / behind 0
exact four-file changed list
Fresh Red v1 SHA-256
tc-s06-001 transaction call sequence
cross-lineage / unknown-status backend call count 0
not_submitted / unknown publication count 0
continuation-unavailable fallback count
publication failure/collision commit count 0
source-drift call counts
privacy sentinel zero-match
全verification commandとexit code
live Oracle/provider continuationは未検証であること
```

Fresh Red v2は新しいfresh threadで、pushed exact HEADをread-only reviewする。今回のBlue threadまたはFresh Red v1 threadをreviewerとして再利用しない。

## 9. Model evidence boundary

このturnで観測したのはGitHub connectorによるrepository/branch/HEAD/blob inspectionと、添付Fresh Red reviewのSHA-256だけである。wrapper、browser、model picker、reasoning-effortの実行証跡はない。

したがって次は未検証である。

```text
GPT-5.6 Luna
Reasoning Effort Max
Luna / Maxの組合せ
本repair brief生成時のresolved model label
live provider continuation capability
```

モデル名やreasoning effortをS06修正・Fresh Red PASSの証拠として使用しない。
