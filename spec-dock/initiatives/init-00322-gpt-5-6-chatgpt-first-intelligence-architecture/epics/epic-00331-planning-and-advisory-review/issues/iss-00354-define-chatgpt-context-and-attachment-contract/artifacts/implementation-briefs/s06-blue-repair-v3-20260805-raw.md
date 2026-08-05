# iss-00354 S06 Blue Team repair brief v3

## 1. Identity / repair baseline

| 項目                      | 確認値                                        |
| ----------------------- | ------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                      |
| Branch                  | `codex/iss-00354-chatgpt-context-contract` |
| Exact source HEAD       | `377013c75c06ec6c8326e7eadadea5dc48525c8c` |
| Branch comparison       | `identical` / ahead `0` / behind `0`       |
| Default-branch fallback | 未使用                                        |
| Repair input            | Fresh Red Team v3のP1三件のみ                   |

GitHub connectorでnamed branchと指定HEADの一致を確認した。current commitはS06のlineage、receipt、stateful testをhardeningした四ファイル差分である。 Fresh Red v3は、残存欠陥をscalar `str` subclassによる比較偽装と、実公開経路を通らないprivacy testに限定している。

## 2. Scope / allowed files

変更許可は次の四ファイルだけとする。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/domain/test_issue_planning_contracts.py
```

変更禁止:

```text
requirement.md
design.md
plan.md
report.md
reviews/**
artifacts/**
infra/**
commands/**
cli/**
provider / installed / dogfood projection
S07以降
```

`tests/unit/domain/test_issue_planning_contracts.py`は既存のpublic-shape testを維持する。追加変更は、public serializationにthread/private fieldがないことのassertion補強が必要な場合だけとする。production domain contractは変更しない。

## 3. Minimal implementation changes

### 3.1 `application/ports.py`

対象:

```text
BlueThreadBinding.__post_init__
BlueBindingResolution.__post_init__
ThreadInvocationReceipt.__post_init__
```

scalarを変換・正規化して受理してはならない。`str(value)`、`.lower()`、比較結果によるcanonicalizationは行わず、`str` subclassを拒否する。

#### `BlueThreadBinding`

```text
type(lineage_sha256) is str
re.fullmatch("[0-9a-f]{64}", lineage_sha256)
provider_handle is not None
```

`isinstance(lineage_sha256, str)`は禁止する。

#### `BlueBindingResolution`

```text
type(status) is str
status ∈ {"exact", "unavailable", "ambiguous"}

status == exact:
  type(binding) is BlueThreadBinding

status != exact:
  binding is None
```

statusの閉包判定より先にexact built-in `str`を確認する。

#### `ThreadInvocationReceipt`

通常構築時にも次を直接確認する。

```text
type(mode) is str
type(submission_state) is str
type(result.status) is str
type(result.reason) is str
type(continuation_unavailable_before_submission) is bool
```

その後に既存のclosed-value、Blue/Red排他、mode別binding、submission-state不変条件を適用する。

```text
mode ∈ {"new_blue", "continuation", "fresh_red"}
submission_state ∈ {"successful", "not_submitted", "unknown"}
result.status ∈ {"pass", "blocked", "rejected"}

result.status == pass:
  result.reason == transport_received
  submission_state == successful

submission_state ∈ {not_submitted, unknown}:
  blue_binding is None
  red_binding is None
```

`BlueThreadBinding`、`BlueBindingResolution`、`ThreadInvocationReceipt`のprivate fieldにserializerを追加しない。provider handle、Red binding、receiptをpublic contractへ投影しない。現行private fieldは`repr=False` / `compare=False`であり、この境界を維持する。

### 3.2 `application/issue_planning.py::_validate_blue_resolution`

現在のexact dataclass type検査は維持し、fieldを次の順で直接検証する。現行コードはstatus、digest、digest比較でscalarのoverridden equalityをまだ使用している。

1. `type(resolution) is BlueBindingResolution`
2. `type(prior_lineage) is GitBoundOperationBindingV1`
3. `type(resolution.status) is str`
4. statusの三値閉包
5. `type(prior_lineage.binding_sha256) is str`とSHA形式
6. exact時は`type(binding) is BlueThreadBinding`
7. `type(binding.lineage_sha256) is str`とSHA形式
8. provider handle非`None`
9. exact built-in `str`同士でdigest一致
10. non-exact時はbindingなし

戻り値は、検証済みのbuilt-in `status`とbindingをcallerへ返す。callerは`resolution.status`や`resolution.binding`を再読しない。

```text
exact       -> verified bindingでcontinuation
unavailable -> complete current inputでnew Blue最大1
ambiguous   -> Human block
unknown     -> Human block
invalid     -> Human block
cross-lineage -> Human block
```

unknown、invalid、cross-lineage時の期待値:

```text
resolve_blue = 1
transport = 0
backend = 0
invoke_continuation = 0
invoke_new_blue = 0
publisher = 0
commit_blue = 0
```

### 3.3 `application/issue_planning.py::_validate_thread_receipt`

`receipt`と`result`のexact class確認に続き、全scalarをlocalへ取り込み、次を直接検証する。

```text
type(receipt.mode) is str
type(receipt.submission_state) is str
type(result.status) is str
type(result.reason) is str
type(flag) is bool
```

その後にだけclosed-value比較を行う。

| 条件                                               | 必須結果   |
| ------------------------------------------------ | ------ |
| Blue/Red binding両方あり                             | reject |
| successful Blue、Blue bindingなし                   | reject |
| successful fresh Red、Red bindingなし               | reject |
| not_submitted / unknown、bindingあり                | reject |
| pass、stateがsuccessful以外                          | reject |
| pass、reasonがtransport_received以外                 | reject |
| continuation flag、exact `not_submitted`以外        | reject |
| continuation success、binding object不一致           | reject |
| continuation success、provider handle identity不一致 | reject |
| continuation success、lineage不一致                  | reject |

`required_lineage_sha256 or required_binding.lineage_sha256`は使用しない。`required_lineage_sha256 is not None`で分岐し、選択した値も`type(...) is str`とSHA形式を確認する。

検証済みlocal値だけで後続分岐を行い、validated後にreceiptのscalar fieldを再読しない。

### 3.4 `_require_publishable_thread_receipt`

publisher前に同じdirect validatorを再実行し、次をexact built-in `str`として確認する。

```text
submission_state == "successful"
result.status == "pass"
result.reason == "transport_received"
```

scalar subclass、mutated field、forged receiptはすべて次へ閉じる。

```text
blocked
planning_context_rejected
("thread_receipt_invalid",)
publisher = 0
commit_blue = 0
```

### 3.5 `run_issue_planning_revise::revision_backend_invoker`

fallback条件はvalidatorが返した検証済みlocal値だけで判定する。

```text
submission_state is exact built-in "not_submitted"
AND continuation_unavailable_before_submission is exact bool True
```

この条件だけがnew Blueを一回許可する。

```text
unknown                       -> fallback 0
str subclass unknown          -> fallback 0
str subclass not_submitted    -> fallback 0
invalid mode/status/reason     -> fallback 0
successful                     -> fallback 0
```

既存のsame synthesized object、prompt object、attachment tuple、各`Path` object identity契約は変更しない。現行testはこのidentityを既に`is`で検証しているため、重複テストを追加しない。

## 4. Fail-closed scalar / mutation matrix

test用に、内部文字列と比較結果を分離できる`str` subclassを一つだけ追加する。valid dataclassを通常構築した後、`object.__setattr__`でfieldを差し替え、constructorだけでなくapplication boundaryを検証する。

| Mutated field          | 実際の内部値 / 偽装                        | 期待結果                   | fallback | publisher | commit |
| ---------------------- | ---------------------------------- | ---------------------- | -------: | --------: | -----: |
| resolution.status      | `forged`だが`exact`と等価               | Human block            |        0 |         0 |      0 |
| binding.lineage_sha256 | 別digestだが要求digestと等価               | Human block            |        0 |         0 |      0 |
| resolution.status      | subclassの`exact`                   | Human block            |        0 |         0 |      0 |
| receipt.mode           | 別modeだがexpected modeと等価            | thread receipt invalid |        0 |         0 |      0 |
| submission_state       | 内部値`unknown`、`not_submitted`と等価    | fallback禁止             |        0 |         0 |      0 |
| submission_state       | 内部値`not_submitted`、`successful`と等価 | publication禁止          |        0 |         0 |      0 |
| submission_state       | subclassの`successful`              | publication禁止          |        0 |         0 |      0 |
| result.status          | subclassの`pass`                    | publication禁止          |        0 |         0 |      0 |
| result.status          | 内部値`blocked`、`pass`と等価             | publication禁止          |        0 |         0 |      0 |
| result.reason          | subclassの`transport_received`      | publication禁止          |        0 |         0 |      0 |
| result.reason          | 別reasonだが`transport_received`と等価   | publication禁止          |        0 |         0 |      0 |

positive controlは既存契約を維持する。

```text
exact built-in not_submitted
+ exact bool True
+ valid non-pass PlanningInvocationResult
+ no bindings
-> continuation 1
-> new Blue 1
```

Fresh Red v3が再現したのは、status/digest/state/status/reasonの比較がscalar subclassの等価演算に依存する経路である。

## 5. Required test changes

### 5.1 既存matrixの拡張

次の既存testを拡張し、新しい独立test群を増やし過ぎない。

```text
test_s06_forged_resolution_is_blocked_before_transport_or_new_blue
test_s06_forged_receipt_blocks_before_publisher_and_commit
test_s06_unknown_or_unsubmitted_continuation_does_not_fallback
```

追加case:

* closed literalを持つ`str` subclass
  -未知値をclosed literalに見せる`__eq__`偽装
  -別digestで`__ne__`を偽装
  -通常構築後のfrozen dataclass field mutation
* `mode` / `submission_state` / `result.status` / `result.reason` mutation

各caseでcall countを明示する。

```text
new Blue fallback = 0
publisher = 0
commit = 0
output files = 0
```

### 5.2 実公開経路privacy test

既存の

```text
test_s06_private_thread_sentinel_stays_out_of_public_and_artifact_surfaces
```

を、手作業でobjectを連結するtestから実application transactionへ置換する。現行testはpublished Candidate / Reviewを通していない。

構成:

1. 一つの`_StatefulThreadPort`派生fakeをCreateとReviewで共有する。
2. Blue provider handleの`repr`にprivate sentinel、private path、fake transcript markerを含める。
3. fake portは`invoke_new_blue`と`invoke_fresh_red`で実際に受け取った`synthesized` objectを保存する。
4. `run_issue_planning_create()`を実行してCandidateを公開する。
   5.同じport/gatewayで`run_issue_planning_review()`を実行してReview JSONとsummaryを公開する。
5. Fresh Red bindingがBlue provider handleと別objectであることだけ確認する。lineage transactionの詳細は既存`tc-s06-001`へ委ねる。
6. 次の全surfaceをbyte/string scanする。

```text
repr(BlueThreadBinding)
repr(ThreadInvocationReceipt)
create result.to_dict()
review result.to_dict()

published Candidate ZIP:
  全entry name
  全entry bytes

published Review:
  Review JSON bytes
  Review summary bytes

captured Create / Review synthesized operations:
  prompt
  repr(attachment_paths tuple)
  tuple内の各Path objectのrepr
```

tupleやPathを新しく再構築して検査してはならない。fake portが実際に受け取ったtupleと各objectをそのまま走査する。

期待値:

```text
private provider sentinel = 0 matches
fake transcript sentinel = 0 matches
private absolute path = 0 matches
"provider_handle" public key = 0
reusable Red state = 0
```

### 5.3 重複させない範囲

次は現行testを保持し、同じシナリオを追加しない。

* stateful Planning → Blue commit → Revision → fresh Red transaction。
* source drift時のresolve/transport/backend/publisher/commitゼロ。
* thread-backed publication failure。
* collision時のcommitted Blue不変。
* explicit continuation-unavailable fallbackのprompt/tuple/Path identity。
* fresh Redの別binding。
* domain public-shape test。

`tests/unit/domain/test_issue_planning_contracts.py`では既存のcontent-free public shape assertionを維持する。

## 6. Verification commands

```bash
SOURCE_HEAD=377013c75c06ec6c8326e7eadadea5dc48525c8c
BRANCH=codex/iss-00354-chatgpt-context-contract

git fetch origin "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "origin/$BRANCH")" = "$SOURCE_HEAD"

uv run pytest \
  tests/unit/application/test_issue_planning.py \
  -k 's06 and (forged or receipt or resolution or scalar or privacy or fallback or stateful)' \
  -q

uv run pytest \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py \
  -q

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

Allowlist gate:

```bash
ALLOWED='^(src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/(ports|issue_planning)\.py|tests/unit/application/test_issue_planning\.py|tests/unit/domain/test_issue_planning_contracts\.py)$'

test -z "$(
  git diff --name-only "$SOURCE_HEAD" |
  grep -Ev "$ALLOWED" || true
)"
```

PASS条件:

```text
scalar subclass / mutated-field matrixが全件fail-closed
unknown fallback 0
invalid receipt publication 0
invalid receipt commit 0
実Candidate ZIP全entryのsentinel zero-match
実Review JSON/summaryのsentinel zero-match
captured prompt/attachmentsのsentinel zero-match
既存stateful tc-s06-001が継続してPASS
全pytest / Ruff / mypy / validate / diff-checkがexit 0
差分が四ファイル内
```

## 7. Stop conditions / handoff

次の場合はallowlistを拡張せず停止する。

* branch tipが`377013c75c06ec6c8326e7eadadea5dc48525c8c`から変わった。
* scalar subclassを拒否するためにdomain、infra、CLI変更が必要になる。
  -値をbuilt-in `str`へcoerceしなければ互換性を維持できない。
* publisher前receipt gateを維持できない。
* private handle/transcriptをpublic contractへ追加する必要が生じる。
  -既存stateful continuity、fresh Red、fallback identity testを弱める必要が生じる。
  -実公開経路のsentinel scanが一件でも検出する。
  -四ファイル外の変更が必要になる。

実装commit/push後は、別のfresh Red threadへexact pushed HEAD、四ファイルdiff、scalar matrixのcall count、privacy scan対象とzero-match結果、全command exit codeを渡す。今回のBlueスレッドやRed v3スレッドをreviewerとして再利用しない。

## 8. Unchanged / unverified boundary

次の承認済み契約は変更しない。

```text
same verified Blue continuation
Candidate versionごとのfresh Red
explicit not_submitted + continuation unavailableだけのnew Blue fallback
publisher前receipt gate
Candidate publication成功後だけBlue lineage commit
provider handle / transcript / private pathの非公開
```

live Oracle、browser、concrete provider handle receipt、same-provider-thread continuationはこのapplication/unit修正では未確認である。unit fakeのPASSをlive provider evidenceへ昇格しない。GPT-5.6 LunaおよびReasoning Effort Maxのwrapper実測証跡も、このturnでは未確認である。
