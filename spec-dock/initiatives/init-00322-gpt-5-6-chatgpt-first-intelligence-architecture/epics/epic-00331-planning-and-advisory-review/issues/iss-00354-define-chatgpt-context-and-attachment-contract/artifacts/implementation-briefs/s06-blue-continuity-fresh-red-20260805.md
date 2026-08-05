# iss-00354 S06 実装ブリーフ — Blue continuity / fresh Red

> **実装対象:** `plan.md` S06 / `cl-s06-blue-red` / `tc-s06-001`
> **基準:** successful submission にだけ Blue thread state を結び付け、Semantic Revision は exact lineage の Blue を継続し、Review は毎回 fresh Red とする。
> **重要な実装ゲート:** application/domain 内で lineage policy、private thread port、transaction test は実装できる。一方、exact HEAD の concrete Oracle adapter は thread handle を受け取らず、`--followup` を実行せず、submission receipt も返さない。したがって、**application/domain だけの差分で live same-provider-thread continuation を実証してはならない**。policy contract と unavailable fallback を実装し、production continuation capability が未配線なら report に未検証として残す。logical binding だけを作って S06 完了とみなすことは禁止する。

## 1. Identity / GitHub preflight

| 項目                         | 確認結果                                        |
| -------------------------- | ------------------------------------------- |
| Repository                 | `chemitaro/spec-dock`                       |
| Named branch               | `codex/iss-00354-chatgpt-context-contract`  |
| Required source HEAD       | `382e49b5b3d93ff26c4672e633cb33481ca61991`  |
| GitHub branch tip          | `382e49b5b3d93ff26c4672e633cb33481ca61991`  |
| Comparison                 | `identical` / ahead `0` / behind `0`        |
| Default branch fallback    | `0` / 使用していない                               |
| Connector observation date | `2026-08-05`                                |
| Issue                      | `iss-00354`                                 |
| Current commit             | `docs(s05): S05実装とRed Team v2 PASSを報告台帳へ統合` |

添付と GitHub exact HEAD の主要 blob は一致した。

| Blob                                            | Git blob SHA                                |
| ----------------------------------------------- | ------------------------------------------- |
| `requirement.md`                                | `76ebf016b12abb06f2b5daa544ea7a1421c7471e`  |
| `design.md`                                     | `118e46f905b86883aac9df0f34ebca9e7be2fe91`  |
| `plan.md`                                       | `c553db3d222f5c346c1d15c21f0242cebdee0de4`  |
| `application/issue_planning.py`                 | `00204fdac4a043187eefedd2dca9c0294b4fe4f9`  |
| `domain/issue_planning_contracts.py`            | `98ae151819b417773929396657929b70fef10193`  |
| `tests/unit/application/test_issue_planning.py` | `a2ea4f23931d24c3cdffda774be55513835e5603`  |

S05 Fresh Red v2 の reviewed HEAD `ae58ef254e40ebb2fad4e64d8c22627fa312dae0` から current HEAD までは一 commit だけで、差分は S05 brief/review artifacts と `report.md` に限定される。runtime と tests は変更されていない。current `report.md` では S05 が closed、S06 以降が pending と記録されている。

**実装開始前提:** Codex は作業開始直前にも named branch tip が上記 HEAD と一致することを確認する。異なる場合は identity rebind なしに実装を開始しない。

## 2. Current source facts

### 2.1 既存の lineage / identity モデル

新しい公開 lineage schema は不要である。次の既存型を正本として再利用する。

* `PlanningSourceEvidence`: repository、branch、local/remote HEAD、source manifest、snapshot を exact に束縛する。
* `IssueCandidateIdentity`: Issue、Candidate ID/version、source repository/branch/HEAD、ZIP SHA を束縛する。
* `OnboardingCompanionBindingV1`: companion path/SHA を束縛する。
* `GitBoundOperationBindingV1`: Candidate、companion、repository、branch、source HEAD を一つの content-free digest に閉じる。これを **Blue candidate lineage key** として使う。
* `ReviewedPlanningIdentity`: Review 対象 Candidate または git-bound target の exact identity を閉じる。
* `PlanningRevisionRequestV1`: prior Candidate、exact Review bytes digest、選択した P0/P1 を閉じる。

Semantic Revision は既に、prior Candidate、exact Review result、revision request、canonical/relevant source paths を original path のまま complete current input として渡す。source HEAD drift は `_revision_source_state()` で backend invocation 前に検出され、publication 時にも再検査される。

### 2.2 現在の invocation 境界

* `run_issue_planning_transport()` は `backend_invoker` に `repo_root`、`role`、`source_evidence`、`synthesized`、timeout を渡すだけである。
* `IssuePlanningDependencies` は現在 `clock` と `gateway` だけを持ち、thread port はない。
* `PlanningInvocationResult` は public status/reason、source evidence、exit code、response size/SHA、typed ZIP/JSON を持つが、provider handle、thread binding、`prompt_submitted` receipt は持たない。
* concrete `invoke_issue_planning_chatgpt()` は invocation ごとに新しい Oracle session ID を生成する。cross-operation continuation input は受け取らず、現行 recovery は同一 invocation 内の `_recover_same_session()` に限定される。
* Review は現在も新規 Oracle invocation になるが、それは infra の session generation による結果であり、application/domain の「fresh Red policy」として明示されてはいない。

### 2.3 実装上の blocking discrepancy

canonical plan の migration order は S09/S10 の profile/submission evidence を S06 より先に置く一方、current report は S05 closure 後の次 step を S06 としている。

この不一致は次の fail-closed rule で限定する。

* legacy backend の `pass / transport_received` は successful submission と扱える。
* legacy backend の全 non-pass は `not_submitted` と推測せず `unknown` とする。
* explicit `not_submitted` は新しい private thread port が receipt として返した場合だけ使用する。
* `unknown` 後の new Blue、別 thread、再 submission は禁止する。
* live provider continuation の wiring が必要になった時点で S06 allowlist を越えるため停止する。

## 3. S06 exact scope and allowed files

### 3.1 実装スコープ

実装するのは次だけである。

1. Planning の successful submission を private pending Blue binding として扱う。
2. Candidate publication 後にだけ、その binding を `GitBoundOperationBindingV1` へ commit する。
3. Semantic Revision は prior Candidate から再構成した exact binding を解決し、exact なら同一 Blue binding を使用する。
4. exact lineage だが binding unavailable なら、complete current input で new Blue を一度開始する。
5. lineage ambiguous なら backend invocation `0` で Human block 相当とする。
6. Review は毎回 fresh Red invocation とし、Blue/過去 Red の reusable binding を渡さない。
7. provider handle、session handle、raw transcript を public model/output へ入れない。

### 3.2 最小 changed-file allowlist

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py
tests/unit/application/test_issue_planning.py
tests/unit/domain/test_issue_planning_contracts.py
```

`domain/issue_planning_contracts.py` は既存 `GitBoundOperationBindingV1`、`IssueCandidateIdentity`、`ReviewedPlanningIdentity` をそのまま再利用し、**production 変更なし**を第一選択とする。

### 3.3 Read-only / change prohibited

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py
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
artifacts/**
reviews/**
```

CLI、infra、Oracle follow-up argv、provider projection、canonical three documents、S07〜S13、PR/merge/Issue close は S06 の変更対象外である。S06 の canonical allowlist と目的は plan の execution card に従う。

## 4. Required implementation changes (file/symbol level)

### 4.1 `application/ports.py`

次の application-private contract を追加する。名前はこのブリーフに固定する。

* `ThreadSubmissionState`

  * `successful`
  * `not_submitted`
  * `unknown`
* `BlueBindingResolutionStatus`

  * `exact`
  * `unavailable`
  * `ambiguous`
* `BlueThreadBinding`

  * `lineage_sha256`
  * opaque `provider_handle`
  * `provider_handle` は `repr=False`、`compare=False`
  * `to_dict()`、`from_dict()`、JSON serializer を持たせない
* `BlueBindingResolution`

  * status
  * exact の場合だけ `BlueThreadBinding`
* `ThreadInvocationReceipt`

  * public `PlanningInvocationResult`
  * `submission_state`
  * private Blue/Red binding
  * continuation が submission 前に unavailable だったかを示す content-free enum
  * serializer を持たせない
* `ChatGptThreadPort`

  * `resolve_blue(lineage: GitBoundOperationBindingV1)`
  * `invoke_new_blue(...)`
  * `invoke_continuation(binding, ...)`
  * `invoke_fresh_red(reviewed_identity, ...)`
  * `commit_blue(receipt, new_lineage)`
  * Red successful submission の consumed state を記録してもよいが、reusable Red handle を返す API は持たせない

`IssuePlanningDependencies` に `thread_port: ChatGptThreadPort | None = None` を末尾 default field として追加し、既存 constructor を壊さない。

concrete Oracle port は追加しない。`thread_port=None` は capability unavailable と扱う。

### 4.2 `application/issue_planning.py`

#### 共通 helper

* prior Candidate から `GitBoundOperationBindingV1.create(...)` を呼ぶ `_candidate_blue_lineage()` を追加する。
* backend kwargs を一度だけ構築し、thread policy を適用する `_invoke_with_thread_policy()` を追加する。
* legacy backend result から private receipt を作る `_legacy_thread_receipt()` を追加する。

  * `pass / transport_received` のみ `successful`
  * 全 non-pass は `unknown`
  * public reason から `not_submitted` を推測しない
* `run_issue_planning_transport()` 自体の public signature と prompt/attachment contract は変更しない。create/review/revise が渡す `backend_invoker` を application wrapper に差し替える。

#### `run_issue_planning_create()`

* transport 前は `invoke_new_blue` を選ぶ。
* successful receipt が返っても、Candidate publication 前には lineage store を更新しない。
* publication 成功後、既存処理で生成している `GitBoundOperationBindingV1` を `commit_blue()` へ渡す。
* archive rejection、source stale、collision、build/publication failure の場合は commit `0`。
* successful submission 後に publication できなかった private binding は reusable exact binding にしない。次回 resolve は `ambiguous` または `unavailable` にならなければならない。

#### `run_issue_planning_revise()`

* `_revision_source_state()` を thread lookup より先に維持する。
* prior Candidate identity と companion から exact prior lineage を構築する。
* resolution:

  * `exact`: `invoke_continuation()` へ同一 `BlueThreadBinding` を渡す。
  * `unavailable`:既存 semantic revision の complete synthesized input を一度だけ `invoke_new_blue()` へ渡す。
  * `ambiguous`: `PlanningInvocationResult(status="blocked", reason="planning_context_rejected", details=("blue_lineage_ambiguous",))` を返し、thread port/backend call は `0`。
* unavailable fallback は、同じ `synthesized` object、prompt string、attachment tuple、各 `Path` object を再利用する。再 synthesis、attachment drop、copy、ZIP、wrapper fallback は行わない。
* continuation invocation 後の fallback は、port が `not_submitted + continuation_unavailable_before_submission` を明示した場合だけ一度許可する。
* `unknown` または `successful` の後は new Blue を開始しない。
* revised Candidate publication 後だけ、同じ private Blue binding を new `GitBoundOperationBindingV1` へ commit する。

#### `run_issue_planning_review()`

* prompt synthesizer が作成した exact `ReviewedPlanningIdentity` を `invoke_fresh_red()` へ渡す。
* `resolve_blue()`、`invoke_continuation()`、`commit_blue()` を呼ばない。
* fresh Red binding は Blue binding と object identity が異なること。
* Review 完了後に reusable Red binding を残さない。
* same Candidate version で successful Red submission が既に記録されている場合、別の automatic successful submission を作らない。recovery は既存 same-session infra の責務であり、S06 で new Review invocation に置換しない。

## 5. State/lineage/privacy invariants

| 状態 / 条件                            | 必須動作                                                                                                                    |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| 初回 Planning                        | new Blue を開始する                                                                                                          |
| `submission_state=not_submitted`   | pending/committed Blue lineage を更新しない                                                                                   |
| `submission_state=unknown`         | `not_submitted` と推測しない。new Blue、retry、Review再実行を行わない                                                                    |
| successful submission              | private binding を pending にできるが、public outputへは出さない                                                                     |
| Candidate publication success      | その時点でのみ published Candidate の `GitBoundOperationBindingV1` へ commit                                                     |
| publication failure / source stale | commit `0`。successful pending bindingを silently reusable にしない                                                           |
| exact prior lineage                | 同一 `BlueThreadBinding` と同一 opaque provider handle を continuation へ渡す                                                    |
| binding unavailable、lineage exact  | complete current input で new Blue を最大一回                                                                                 |
| lineage ambiguous                  | Human block 相当、backend invocation `0`                                                                                   |
| source HEAD drift                  | existing `revision_source_stale`、thread resolve/invoke `0`                                                              |
| Review                             | fresh Red。Blue、過去 Red、別 Candidate Red の handle reuse `0`                                                                |
| post-submit failure                | new execution `0`。same-session recovery 境界は変更しない                                                                        |
| privacy                            | handle、raw transcript、private target URL、private absolute pathを Candidate、Review、prompt、`to_dict()`、command outputへ含めない |

REQ-011〜014 は exact Blue lineage、fresh Red、unique-lineage fallback、private evidence boundary を要求する。REQ-031 は binding の更新を successful submission に限定し、pre-submit failure で advance しない。

Design の transaction 順序は、successful submission で private binding を得た後も、Candidate lineage の更新を valid Candidate publication 後に限定している。

## 6. Test cases and exact verification commands

### 必須テスト

1. **`tc-s06-001` — Blue continuation / fresh Red transaction**

   * Planning success → Candidate v1 publication → Blue commit。
   * Semantic Revision は v1 exact lineage を解決し、Planning と同一 `BlueThreadBinding` / provider handle を使用。
   * Review は別 object の fresh Red binding を使用。
   * Red の resolve/commit/reusable-store call は `0`。

2. **送信前失敗**

   * `not_submitted` receipt では Blue commit/advance `0`。
   * Candidate/Review publication `0`。
   * public result に private receipt が出ない。

3. **Unavailable handling**

   * exact lineage + resolution unavailable → new Blue 一回。
   * prompt synthesis 一回。
   * same `synthesized` object、prompt、attachment tuple、Path identity。
   * wrapper/API/alternate backend call `0`。

4. **Unknown submission**

   * legacy non-pass または explicit unknown → continuation fallback/new Blue `0`。
   * binding commit `0`。
   * unknown を false に変換しない。

5. **Source drift / ambiguous lineage**

   * source HEAD drift → `revision_source_stale`、resolve/invoke `0`。
   * ambiguous → blocked、backend `0`、details は `blue_lineage_ambiguous` だけ。

6. **Lineage publication transaction**

   * publisher success時だけ `commit_blue` 一回。
   * collision、archive rejection、postflight stale、publication failureでは commit `0`。
   * successful-but-unpublished receipt を次回 exact continuationに再利用しない。

7. **Privacy assertion**

   * sentinel provider handle、raw transcript、private URL/path が以下に存在しない:

     * `repr(BlueThreadBinding)`
     * `PlanningInvocationResult.to_dict()`
     * `PlanningCommandResult.to_dict()`
     * Candidate success output
     * Review result/summary
     * prompt text
     * attachment path serialization
   * private binding/receipt に `to_dict` / `from_dict` がない。
   * `GitBoundOperationBindingV1` は既存の content-free fields だけを保持する。既存 domain tests の typed/public boundaryを維持する。

### Exact verification commands

```bash
SOURCE_HEAD=382e49b5b3d93ff26c4672e633cb33481ca61991

uv run pytest \
  tests/unit/application/test_issue_planning.py \
  -k 's06 or blue or red or thread or lineage' -q

uv run pytest \
  tests/unit/domain/test_issue_planning_contracts.py \
  -k 's06 or lineage or privacy or binding' -q

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
git status --short
git diff --name-only "$SOURCE_HEAD"
```

Allowlist audit:

```bash
ALLOWED='^(src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/(ports|issue_planning)\.py|tests/unit/application/test_issue_planning\.py|tests/unit/domain/test_issue_planning_contracts\.py)$'

test -z "$(
  git diff --name-only "$SOURCE_HEAD" |
  grep -Ev "$ALLOWED"
)"
```

Read-only boundary audit:

```bash
ISSUE_DIR=spec-dock/initiatives/init-00322-gpt-5-6-chatgpt-first-intelligence-architecture/epics/epic-00331-planning-and-advisory-review/issues/iss-00354-define-chatgpt-context-and-attachment-contract

git diff --exit-code "$SOURCE_HEAD" -- \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning_prompt.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/issue_planning_contracts.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli \
  "$ISSUE_DIR/requirement.md" \
  "$ISSUE_DIR/design.md" \
  "$ISSUE_DIR/plan.md" \
  "$ISSUE_DIR/report.md"
```

## 7. Stop conditions and out-of-scope changes

次のいずれかで実装を停止し、allowlist を拡張せず親 orchestrator へ返す。

* named branch tip が `382e49b5b3d93ff26c4672e633cb33481ca61991` から変わった。
* actual same-thread continuation に infra `--followup`、session metadata、bootstrap wiring、commands/CLI の変更が必要になった。
* concrete provider から successful / not-submitted / unknown の private receiptを取得できず、non-pass reasonから推測する必要が生じた。
* `BlueThreadBinding` を作っても provider invocation が opaque handle を実際には消費しない。これは false-green であり実装完了に数えない。
* unavailable fallback で complete current input の同一性を維持できない。
* ambiguous lineage で backend invocation `0`を保証できない。
* Review が Blue または過去 Red binding を受け取れる。
* private handle/transcriptを public dataclass、Candidate、Review、canonical docs、report raw fieldへ保存する必要が生じた。
* same-session harvest と cross-operation Blue continuation を一つの state/store に統合する必要が生じた。
* CLI、infra、provider projection、canonical docs、S07〜S13、PR、merge、Issue close、architecture redesign が必要になった。
* required testsまたは fresh defect-only reviewで P0/P1 が残る。

application/domain policy testsだけが Green でも、concrete continuation port が未配線なら **live Blue continuity は未検証**である。report に capability gap を残し、production same-thread continuation の closure を主張しない。

## 8. Report evidence and commit/push handoff

S06 implementation worker は `report.md` を変更しない。次を content-free handoff として親 orchestrator に返す。

* source HEAD と resulting commit SHA。
* exact changed-file list。
* branch tip comparison `identical / 0 / 0`。
* `start_blue → commit v1 → continue same binding → commit v2` の call sequence。
* Blue handle object identity が continuation 前後で同一だった assertion。
* fresh Red binding が Blue と異なり、Red store/commit `0`だった assertion。
* submission state別の invoke/fallback/commit call counts。
* source drift / ambiguous lineage の backend invocation `0`。
* unavailable fallback時の prompt/attachment/object identity。
* privacy sentinel zero-match。
  -全 verification command、exit code、test count。
* concrete Oracle continuation port、provider handle receipt、live browser continuationの検証状態。
* unresolved capability gapまたは stop condition。

コード/test commit の候補:

```bash
git add \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py \
  tests/unit/application/test_issue_planning.py \
  tests/unit/domain/test_issue_planning_contracts.py

git commit -m "feat(iss-00354): add S06 Blue and fresh Red lineage policy"
git push origin codex/iss-00354-chatgpt-context-contract
```

push 後は GitHub connector で resulting SHA と named branch tip の一致を再確認する。親 orchestrator がその SHA、command evidence、privacy assertion、live-continuation未検証事項を `report.md` の S06 Step Contract Closure / Test Contract Closure / Evidence Adoption Ledger に別途統合する。

no-op または stop の場合は、logical-only bindingをcommitせず、unchanged diff、停止理由、必要な次 step dependencyだけを返す。PR、merge、Issue close、Issue finish は行わない。

## 9. Model evidence boundary

このブリーフ作成 turn で実際に観測した外部境界は GitHub connector による repository、named branch、exact HEAD、blob content、commit/report の read-only inspectionだけである。wrapper、browser、model picker、reasoning-effort setting は実行していない。

GitHub exact-HEAD の `report.md` には、過去の S01 観測として requested `gpt-5.6`、target/resolved `GPT-5.6 Sol`、`strategy=select`、`verified=yes` が記録されている。一方で、同じ記録は **GPT-5.6 Luna / Reasoning Effort Max の実測成功を主張していない**。これは repository-recorded historical evidence であり、本 turn で再実行・独立検証した証跡ではない。

したがって本ブリーフでは次を未検証とする。

* `GPT-5.6 Luna` が実際に選択・解決されたこと。
* `Reasoning Effort Max` が実際に適用されたこと。
* Luna / Max の組合せで本 S06 brief が生成されたこと。
* current concrete Oracle adapter が provider handle を取得し、same Blue follow-upへ渡せること。

S06 の受入条件は model label ではなく、exact lineage、successful-submission transaction、same-binding continuation、fresh Red isolation、privacy assertion の観測証跡で判定する。
