# iss-00354 S06 Blue Team repair brief v2

> **対象:** S06 Blue continuity / fresh Red のみ
> **修正入力:** Fresh Red v2、reviewed HEAD `be33362289b1f3e1af9eb395d5be31f932f42329`
> **Red v2 review SHA-256:** `6b2e4d72cf9679426b78d7cac0d56df901f0f11aad99b18bf6e2c66489f05c56`
> **採用対象:** `RT-354-S06-v2-001`〜`004`のP1、および`RT-354-S06-v2-005`のevidence-only補正方針
> **非対象:** S07以降、CLI、infra、Oracle adapter、canonical三文書、PR、merge、Issue close、アーキテクチャ再設計

## 1. Identity / repair baseline

| 項目                      | 確認値                                        |
| ----------------------- | ------------------------------------------ |
| Repository              | `chemitaro/spec-dock`                      |
| Branch                  | `codex/iss-00354-chatgpt-context-contract` |
| Reviewed HEAD           | `be33362289b1f3e1af9eb395d5be31f932f42329` |
| Branch comparison       | `identical` / ahead `0` / behind `0`       |
| Default-branch fallback | 未使用                                        |
| Current commit          | `fix(s06): continuationハンドルでlineageを厳格化`   |

GitHub named branch tipと指定HEADは一致している。 Red v2の正式なfinding、検証範囲、未実行gateは添付レビューを正本とする。

現行application validatorは`resolution.__post_init__()`、`binding.__post_init__()`、`receipt.__post_init__()`を呼び直しており、overrideされたmethodをapplication-boundary検証として信頼している。 また、`ThreadInvocationReceipt.result`は`Any`であり、ports側の通常構築時検証だけでは破損portからのforged objectを閉じられない。

## 2. Repair allowlist

### Implementation workerの変更許可

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/domain/test_issue_planning_contracts.py
```

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
artifacts/**
reviews/**
provider / installed / dogfood projection
```

S06はverified matching lineageだけをBlue継続へ使用し、lineageが一意でbinding unavailableの場合だけcomplete inputでnew Blue、曖昧または不正ならsubmission前にHuman blockとする。private handle/transcriptはpublic artifactへ出さない。

## 3. Required implementation changes

### 3.1 `application/ports.py`

通常構築時のdefense-in-depthとして各`__post_init__()`は残してよい。ただしapplicationはこれらを再呼出しせず、独立に全fieldを検証する。

#### `ThreadInvocationReceipt.result`

型注釈を次へ閉じる。

```python
result: PlanningInvocationResult
```

`TYPE_CHECKING` importへ`PlanningInvocationResult`を追加する。serializerは追加しない。

#### Private contractの保持

以下は維持する。

* `BlueThreadBinding.provider_handle`: `repr=False`, `compare=False`
* `BlueBindingResolution.binding`: `repr=False`, `compare=False`
* `ThreadInvocationReceipt.result`、Blue/Red binding: `repr=False`, `compare=False`
* private contractに`to_dict()`、`from_dict()`、JSON serializerを追加しない

### 3.2 `application/issue_planning.py`

#### `_validate_blue_resolution()`

次を削除する。

```text
resolution.__post_init__()
binding.__post_init__()
```

application内でfieldを直接検査する。

```text
resolution is BlueBindingResolution
status ∈ {"exact", "unavailable", "ambiguous"}

exact:
  binding is BlueThreadBinding
  lineage_sha256 is str
  regex fullmatch [0-9a-f]{64}
  provider_handle is not None
  lineage_sha256 == prior_lineage.binding_sha256

unavailable / ambiguous:
  binding is None
```

unknown status、不正SHA、missing/wrong binding、cross-lineage digestはすべて次へ閉じる。

```text
status = blocked
reason = planning_context_rejected
details = ("blue_lineage_ambiguous",)
resolve後のtransport calls = 0
backend calls = 0
new Blue calls = 0
publisher calls = 0
commit calls = 0
```

callerは三値をexhaustiveに分岐し、`exact以外ならnew Blue`というfall-throughを持たせない。

```text
exact       -> continuation
unavailable -> new Blue最大1
ambiguous   -> Human block
otherwise   -> Human block
```

#### `_validate_thread_receipt()`

次を削除する。

```text
receipt.__post_init__()
receipt.blue_binding.__post_init__()
```

application側で以下を直接検証する。

1. `receipt`が`ThreadInvocationReceipt`。
2. `receipt.result`が実際の`PlanningInvocationResult`。
3. expected modeとreceipt modeが一致し、modeが三値のいずれか。
4. submission stateが`successful|not_submitted|unknown`。
5. continuation flagが`bool`。
6. Blue bindingは`None`または`BlueThreadBinding`。存在時はlowercase SHA-256、non-`None` provider handle。
7. Blue/Red bindingの同時保持は禁止。
8. `result.status == "pass"`ならstateは`successful`。
9. `not_submitted` / `unknown`ではBlue/Red bindingを両方禁止。
10. successful `new_blue` / `continuation`ではBlue binding必須、Red binding禁止。
11. successful `fresh_red`ではRed binding必須、Blue binding禁止。
12. `continuation_unavailable_before_submission=True`は次の組合せだけ許可。

```text
mode == continuation
submission_state == not_submitted
result.status != pass
blue_binding is None
red_binding is None
```

13. successful continuationでは次をすべて一致させる。

```text
receipt.blue_binding is required_binding
receipt.blue_binding.lineage_sha256 == required_lineage_sha256
receipt.blue_binding.provider_handle is required_provider_handle
```

検証中の`AttributeError`、`TypeError`、`ValueError`は既存のcontent-free resultへ閉じる。

```text
blocked / planning_context_rejected / ("thread_receipt_invalid",)
```

#### `_thread_backend_invoker()`

port receiptを受け取った直後に直接検証し、成功するまで`capture()`や`receipt.result`返却を行わない。

```text
port invocation
-> direct receipt validation
-> capture
-> return PlanningInvocationResult
```

invalid receiptではpublisher、Candidate/Review parsing、commitへ到達させない。

#### `_require_publishable_thread_receipt()`

publication直前に同じ直接validatorを再実行し、次を必須とする。

```text
receipt count == 1
result is PlanningInvocationResult
result.status == pass
result.reason == transport_received
submission_state == successful
operationごとのrequired bindingが存在
```

`getattr()`でstatusだけを読む方式を使わない。

Create、Review、Semantic Revisionのすべてで、このgateをarchive/JSON処理およびpublisher呼出しより前に維持する。

#### Semantic Revision fallback

continuationからnew Blueへのfallbackは次の全条件を満たす場合だけ許可する。

```text
valid continuation receipt
submission_state == not_submitted
continuation_unavailable_before_submission is True
```

`unknown`、invalid receipt、flagなし`not_submitted`、successful submissionからのfallbackは0。

fallback時は同じtransport invocation内の同じ値を再利用する。

```text
same synthesized object
same prompt str object
same attachment_paths tuple object
same individual Path objects
```

再synthesis、attachment drop、copy、ZIP、wrapper/API fallbackは追加しない。

#### Publication / commit順序

正常系の順序は変更しない。

```text
valid successful receipt
-> output/source validation
-> Candidate publication
-> commit_blue(receipt, published lineage)
-> command success
```

publication failure、collision、source driftでは`commit_blue()`を呼ばない。pending bindingをreusable storeへ入れるのは`commit_blue()`だけとし、`invoke_new_blue()`または`invoke_continuation()`時点では保存しない。

## 4. Required tests

既存のstateful `tc-s06-001`は保持する。次を追加または強化する。

### 4.1 Forged boundary tests

dataclass constructorを通さず、または`__post_init__()`をno-op overrideしたobjectを使用する。

* forged unknown `BlueBindingResolution.status`
* forged exact cross-lineage binding
* forged invalid SHA binding
* forged receipt with `SimpleNamespace` result
* forged fresh Red receipt carryingBlue/Red両binding
* forged successful Blue receipt withoutBlue binding
* forged unknown/not-submitted receipt carryingbinding

全caseでapplication direct validatorが拒否し、backend/new Blue/publisher/commitが0であること。

### 4.2 Unknown / not-submitted matrix

```text
unknown:
  fallback 0
  publication 0
  commit 0

not_submitted without continuation flag:
  fallback 0
  publication 0
  commit 0

not_submitted with valid continuation-unavailable flag:
  continuation 1
  new Blue 1
  successful submission最大1
```

continuation-unavailable fixtureの`result`は`SimpleNamespace`ではなく、実際のnon-pass `PlanningInvocationResult`を使用する。

### 4.3 Stateful failure transaction

同一`_StatefulThreadPort`を使い、次を検証する。

* thread-backed Candidate publication failure:

  * new Blue call 1
  * publisher call 1
  * commit 0
  * committed store unchanged
* thread-backed collision:
  -既存Candidate bytes不変

  * second pending bindingはstoreへ入らない
  * commit count増分0
    -既存committed binding不変
* successful-but-unpublished pending binding:

  * subsequent `resolve_blue()`でexactとして返さない
  * reusable storeに存在しない

### 4.4 Source drift call counts

Semantic Revisionのsource HEAD driftで次をすべて明示assertする。

```text
resolve_blue calls = 0
transport calls = 0
backend calls = 0
publisher calls = 0
commit calls = 0
```

generic source-drift testではなく、thread-backed dependenciesを使用する。

### 4.5 Privacy sentinel

一つのprivate sentinelをprovider handleおよびfake transcript markerへ埋め、次をすべて走査する。

```text
repr(BlueThreadBinding)
repr(ThreadInvocationReceipt)
PlanningInvocationResult.to_dict()
PlanningCommandResult.to_dict()
published Candidate ZIP全entry bytes
published Review JSON bytes
published Review summary bytes
captured synthesized.prompt
repr(captured synthesized.attachment_paths)
各attachment Pathのrepr
```

sentinel、`provider_handle`、session handle、raw transcript、private URL/pathがzero-matchであること。

### 4.6 Fallback identity

continuation-unavailable fallbackで以下を`is`比較する。

```text
first_synthesized is fallback_synthesized
first_synthesized.prompt is fallback_synthesized.prompt
first_synthesized.attachment_paths is fallback_synthesized.attachment_paths
all(first is second for each Path pair)
```

### 4.7 Domain public-shape test

`tests/unit/domain/test_issue_planning_contracts.py::test_s06_public_contract_shapes_remain_content_free`を維持・強化し、public serializationに次がないことを確認する。

```text
provider_handle
blue_binding
red_binding
thread receipt
transcript
private sentinel
```

production domain contractは変更しない。

### 4.8 Ruff E306

`_semantic_revision_setup()`内で`source_hash`代入とnested `create_transport`定義の間にblank lineを追加する。現行sourceはblank lineがなく、Red v2が`E306`対象として指摘している。

## 5. P2 evidence identity correction

Red v2は、repository上のRed v1 review blobと記録済みSHA-256が対応していないと報告している。現行GitHub fileのblob OIDは`41eab41345922f2acbb00edbf3a486d8dc155de3`である。

implementation workerはこの修正を行わない。親orchestratorがevidence-only commitで次を行う。

1. Red v1 reviewのGitHub blobからexact raw bytesを取得する。
2. raw SHA-256を再計算する。
3. Red v2で観測された次の値と一致することを確認する。

```text
73a44751e7bcd6975cbdbfcbff92f0690a64e83faf5bdd8b8e066e7d1aa7ada6
```

4. 既存記録の`adeadc27...`を`superseded / incorrect digest`として訂正する。
5. 次を別fieldとして記録する。

```text
git_blob_oid: 41eab41345922f2acbb00edbf3a486d8dc155de3
raw_sha256:   73a44751e7bcd6975cbdbfcbff92f0690a64e83faf5bdd8b8e066e7d1aa7ada6
```

Git blob OIDとraw SHA-256は異なるalgorithmのため数値を同一にするのではなく、**同一byte列への二つの識別子として再現可能に対応付ける**。Red v1 review本文をsilent overwriteしない。`adeadc27...`に対応する別byte列を保持する必要がある場合は別filenameのimmutable evidenceとして保存する。

親orchestratorだけが次を扱う。

```text
artifacts/**
reviews/**
report.md
```

implementation repair commitのdiffへこれらを混在させない。

## 6. Verification commands

```bash
BRANCH=codex/iss-00354-chatgpt-context-contract
REVIEWED_HEAD=be33362289b1f3e1af9eb395d5be31f932f42329
REPAIR_BASE=<parent-orchestratorが確定したevidence-only baseline>

git fetch origin "$BRANCH"
test "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")"

uv run pytest \
  tests/unit/application/test_issue_planning.py \
  -k 's06 or thread or lineage or receipt or privacy' -q

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

Allowlist:

```bash
ALLOWED='^(src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/(ports|issue_planning)\.py|tests/unit/application/test_issue_planning\.py|tests/unit/domain/test_issue_planning_contracts\.py)$'

test -z "$(
  git diff --name-only "$REPAIR_BASE" HEAD |
  grep -Ev "$ALLOWED" || true
)"
```

## 7. Stop conditions

次のいずれかで停止し、allowlistを拡張しない。

* branch tipが確定`REPAIR_BASE`と異なる。
* direct validationにinfra/session metadata変更が必要。
* private handleをdomain/public resultへ保存する必要がある。
* unknown resolutionまたはinvalid receiptがnew Blue/publisherへ到達する。
* continuation fallbackでprompt/path object identityを維持できない。
* publication failure後のpending bindingをstoreから除外できない。
* source driftでresolveまたはtransportが呼ばれる。
* Ruff E306を含むfocused/static gateが一件でもfailする。
* CLI、infra、canonical docs、S07以降の変更が必要。
* implementation diffに`artifacts/**`、`reviews/**`、`report.md`が入る。

## 8. Commit / push / Fresh Red v3 handoff

Implementation commit:

```bash
git add \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py

git commit -m "fix(iss-00354): close S06 forged thread boundaries"
git push origin codex/iss-00354-chatgpt-context-contract
```

Fresh Red v3は別のfresh threadで、pushed exact HEADをread-only reviewする。handoffには次を含める。

```text
repository / branch
REPAIR_BASE
resulting exact HEAD
branch tip ahead 0 / behind 0
exact four-file diff
Red v2 raw SHA-256
forged resolution/receipt backend call counts
unknown/not-submitted fallback・publication・commit counts
publication failure/collision store state
source drift five-boundary call counts
privacy sentinel zero-match対象一覧
fallback prompt/tuple/Path identity assertions
Ruff E306を含む全command exit code
P2 evidence correction commitは別担当・別diffであること
live Oracle/provider continuationは未検証であること
```

## 9. Model evidence boundary

このbriefで観測したのはGitHub repository/branch/HEAD/sourceと、添付Red v2 reviewのbyte hashだけである。wrapper、browser、model picker、reasoning-effortの実測証跡はない。

```text
GPT-5.6 Luna: 未検証
Reasoning Effort Max: 未検証
Luna / Maxの組合せ: 未検証
live provider continuation: 未検証
```
