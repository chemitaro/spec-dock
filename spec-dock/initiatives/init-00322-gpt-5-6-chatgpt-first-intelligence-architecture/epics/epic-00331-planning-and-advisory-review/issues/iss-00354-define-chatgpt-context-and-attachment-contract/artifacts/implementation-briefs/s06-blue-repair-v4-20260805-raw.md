# S06 Blue Team repair brief v4 — validated fallback mode handoff

## 1. Identity / repair target

| 項目                      | 確認値                                        |
| ----------------------- | ------------------------------------------ |
| Issue / step            | `iss-00354` / S06                          |
| Repository              | `chemitaro/spec-dock`                      |
| Named branch            | `codex/iss-00354-chatgpt-context-contract` |
| Exact source HEAD       | `01868d47b190cdf9e3d82336994c6d201e9ab1e2` |
| Branch comparison       | `identical` / ahead `0` / behind `0`       |
| Default-branch fallback | 未使用                                        |
| 修正対象                    | `RT-354-S06-v4-001` のP1一件だけ                |

Fresh Red v4が確認した欠陥は、continuationの送信前unavailable後に得たvalid `new_blue` receiptを保存している一方、publication gateのmodeを古い`use_continuation=True`から`continuation`として再構成してしまう点である。 Exact sourceにも、fallback後のreceiptを`new_blue`として検証した後、gate直前で`use_continuation`から`receipt_mode="continuation"`を二重代入する制御フローが存在する。

## 2. Minimal changed-file scope

実装allowlistは次の四ファイルを上限とする。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/domain/test_issue_planning_contracts.py
```

今回の最小差分は原則として次の二ファイルだけとする。

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
tests/unit/application/test_issue_planning.py
```

`ports.py`のreceipt schema、`test_issue_planning_contracts.py`のpublic-shape契約、domain、prompt、infra、CLI、provider projection、canonical specs、`report.md`、`artifacts/**`、`reviews/**`は変更しない。

## 3. Required implementation change

### 3.1 `run_issue_planning_revise()`のlocal validated contract

semantic revision branchに、**最後に成功したapplication-boundary validationのスナップショット**を一つだけ保持する。

```text
final_thread_contract:
  raw receipt
  validated PlanningInvocationResult
  validated ThreadInvocationMode
  validated submission state
  validated Blue binding
```

実装形は、一つのoptional tupleまたは同等のatomic local valueとする。複数の独立listに分散させない。

```python
final_thread_contract: tuple[
    ThreadInvocationReceipt,
    PlanningInvocationResult,
    ThreadInvocationMode,
    str,
    BlueThreadBinding | None,
] | None
```

`_validate_thread_receipt()`は既にvalidated mode、submission state、result、Blue bindingを返すため、その戻り値を使用する。raw fieldを再評価してmodeを再構成しない。

### 3.2 `revision_backend_invoker()`の検証順序

#### 通常continuation

```text
invoke_continuation
-> validate with expected mode "continuation"
-> fallback条件なし
-> final_thread_contractをvalidated continuation値で確定
-> validated resultを返す
```

#### continuation-unavailable fallback

```text
invoke_continuation
-> validate with expected mode "continuation"
-> validated submission_state == "not_submitted"
-> validated continuation_unavailable is True
-> invoke_new_blue with同一kwargs
-> validate second receipt with expected mode "new_blue"
-> final_thread_contractをsecond validation結果で上書き
-> second validated resultを返す
```

pre-submit continuation receiptはpublicationまたはcommit対象にしない。fallback後のauthorityはsecond `new_blue` receiptだけである。

#### Direct new Blue

resolutionが`unavailable`の場合:

```text
invoke_new_blue
-> validate with expected mode "new_blue"
-> final_thread_contractを確定
-> validated resultを返す
```

### 3.3 Publication gate

現行の次の二行を削除する。

```python
receipt_mode = "continuation" if use_continuation else "new_blue"
receipt_mode = "continuation" if use_continuation else "new_blue"
```

transport成功後は`final_thread_contract`を展開し、そこに保存した`validated_mode`だけをgate policyに使用する。

```text
final validated mode == continuation:
  required_binding = prior continuation binding
  required_lineage_sha256 = prior lineage SHA
  required_provider_handle = prior provider handle

final validated mode == new_blue:
  required_binding = None
  required_lineage_sha256 = None
  required_provider_handle = None

その他 / contractなし:
  thread_receipt_invalid
  publisher 0
  commit 0
```

`_require_publishable_thread_receipt()`には次を渡す。

```text
receipts = (final raw receipt,)
mode = final validated mode
continuation requirements = final validated modeがcontinuationの場合だけ
```

同helperはraw receiptをpublisher前に再検証し、validated submission state、status、reason、bindingを使ってpublication可否を決めるため、その既存fail-closed境界は維持する。

### 3.4 禁止する分岐

次からpublication modeを決定してはならない。

```text
use_continuation
resolution_status
receipt.mode の再読
最初のcontinuation receipt
provider portの未検証戻り値
```

validated local mode以外が`continuation` / `new_blue`の選択に影響した場合は実装不合格とする。

## 4. Expected state transitions

| 経路                                             | Final validated mode | Continuation requirements | continuation | new Blue | publisher | commit |
| ---------------------------------------------- | -------------------- | ------------------------- | -----------: | -------: | --------: | -----: |
| exact continuation成功                           | `continuation`       | 必須                        |            1 |        0 |         1 |      1 |
| exact continuationが送信前unavailable → fallback成功 | `new_blue`           | すべて`None`                 |            1 |        1 |         1 |      1 |
| continuation `unknown`                         | なし                   | ―                         |            1 |        0 |         0 |      0 |
| `not_submitted`だがunavailable flagなし            | なし                   | ―                         |            1 |        0 |         0 |      0 |
| invalid / mutated receipt                      | なし                   | ―                         |          最大1 |        0 |         0 |      0 |
| fallback後Candidate publication failure         | `new_blue`           | なし                        |            1 |        1 | 1 attempt |      0 |
| fallback後collision                             | `new_blue`           | なし                        |            1 |        1 | 1 attempt |      0 |

Candidate publication成功後だけfinal `new_blue` receiptを新Candidate lineageへcommitする既存順序を維持する。

## 5. Required test changes

### 5.1 Positive fallback regression

既存の

```text
test_s06_semantic_revision_fallback_reuses_exact_synthesized_input
```

を拡張する。現行testは既に`candidate_revised`、continuation 1回、new Blue 1回、commit 1回、同一synthesized inputを要求している。

追加assertion:

```text
final new Blue receipt.mode == "new_blue"
publisher calls == 1
commit calls == 1
committed receipt is final new Blue receipt
result == ok / candidate_revised
```

publisherは既存gateway methodを呼ぶ薄いspyで包み、実Candidate publicationを維持する。

同一input assertionは維持する。

```text
continuation synthesized is new-Blue synthesized
prompt object identity is same
attachment tuple identity is same
each Path object identity is same
```

### 5.2 Normal continuation control

既存のexact continuation testを維持し、必要なら次だけを明示する。

```text
final mode == continuation
continuation calls == 1
new Blue calls == 0
publisher calls == 1
commit calls == 1
committed provider handle is prior provider handle
```

### 5.3 Unvalidated mode reread防止

小さなnegative testを一件追加する。

1. fallbackの`new_blue` receiptを正常にapplication validationする。
2. transport runnerが戻る直前に、保存されたraw receiptの`mode`を`continuation`へmutationする。
3. publication gateは保存済みvalidated mode=`new_blue`をpolicyとして使用する。
4. raw receiptの再検証ではmode mismatchを検出し、publisher/commit前に停止する。

期待値:

```text
status = blocked
reason = planning_context_rejected
details = ("thread_receipt_invalid",)
publisher = 0
commit = 0
```

このtestは「raw `receipt.mode`を読んでgate modeを選び直す」実装を拒否する。

### 5.4 既存matrixを重複実装しない

次は現行testをそのまま保持する。

```text
unknown / not_submitted without flag -> fallback 0
source drift -> resolve/transport/backend/publisher/commit 0
publication failure -> commit 0
collision -> existing Candidate・committed binding不変
same Blue continuation
fresh Red別binding
privacy sentinel scan
scalar subclass / forged receipt matrix
domain public-shape非公開assertion
```

## 6. Verification commands

```bash
SOURCE_HEAD=01868d47b190cdf9e3d82336994c6d201e9ab1e2
BRANCH=codex/iss-00354-chatgpt-context-contract

git fetch origin "$BRANCH"
test "$(git rev-parse HEAD)" = "$SOURCE_HEAD"
test "$(git rev-parse "origin/$BRANCH")" = "$SOURCE_HEAD"

uv run pytest \
  tests/unit/application/test_issue_planning.py \
  -k 's06 and (fallback or continuation or unknown or publication or collision)' \
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

Allowlist:

```bash
ALLOWED='^(src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/(ports|issue_planning)\.py|tests/unit/application/test_issue_planning\.py|tests/unit/domain/test_issue_planning_contracts\.py)$'

test -z "$(
  git diff --name-only "$SOURCE_HEAD" |
  grep -Ev "$ALLOWED" || true
)"
```

## 7. PASS conditions

```text
fallback result == ok / candidate_revised
continuation calls == 1
new Blue calls == 1
publisher calls == 1
commit calls == 1
final publication mode == validated "new_blue"
continuation requirements are not applied to fallback receipt
normal continuation remains mode "continuation"
unknown/not_submitted without flag remain fallback 0
publication failure/collision remain commit 0
all synthesized prompt/attachment identity assertions pass
all pytest/Ruff/mypy/validate/diff checks exit 0
diff is within four-file allowlist
```

## 8. Stop / handoff boundary

次の場合はallowlistを拡張せず停止する。

* branch tipが`01868d47b190cdf9e3d82336994c6d201e9ab1e2`から変わった。
* final validated modeを保持するためにports/domain/infra contractの再設計が必要になる。
* fallback後もcontinuation binding requirementsを外せない。
* raw `receipt.mode`の再読が必要になる。
* publisher前receipt gateを弱める必要が生じる。
  -既存unknown、failure、collision、fresh Red、privacy testが退行する。
* report、review、artifact、spec、infra、CLI、provider projectionの変更が必要になる。

commit/push後は別のfresh Red threadへ、exact pushed HEAD、changed-file list、positive fallback call counts、normal continuation control、mutation negative test、全verification exit codeを渡す。

live Oracle/browser、concrete provider handle receipt、same-provider-thread continuation、実providerのfresh Redは本application/unit修正では未確認であり、fake portのPASSをlive provider evidenceへ昇格しない。
