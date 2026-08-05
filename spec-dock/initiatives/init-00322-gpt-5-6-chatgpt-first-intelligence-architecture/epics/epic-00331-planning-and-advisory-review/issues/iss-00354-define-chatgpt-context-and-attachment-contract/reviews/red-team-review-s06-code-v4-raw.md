# S06 Fresh Red Team Review v4

* Candidate/Issue: iss-00354 / S06
* repository: chemitaro/spec-dock
* source branch: codex/iss-00354-chatgpt-context-contract
* source HEAD: 01868d47b190cdf9e3d82336994c6d201e9ab1e2
* reviewer thread: fresh Red Team v4

## Verdict

FAIL

## Findings

### P0

なし

### P1

#### RT-354-S06-v4-001 — 許可された continuation-unavailable → new Blue fallback が publisher 前 receipt gate で必ず拒否される

* **ID:** `RT-354-S06-v4-001`
* **ファイル/関数/テスト名:** `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py::run_issue_planning_revise` 内 `revision_backend_invoker` および publisher 前の `_require_publishable_thread_receipt` 呼出し、`tests/unit/application/test_issue_planning.py::test_s06_semantic_revision_fallback_reuses_exact_synthesized_input`
* **観測事実:** `revision_backend_invoker` は、検証済み continuation receipt が exact `not_submitted` かつ exact `True` の場合に `invoke_new_blue()` を一度呼び、その返却 receipt を `mode="new_blue"` として検証し、最終 receipt として保存する。一方、transport 成功後の publication gate では、最終 validated mode を保持せず、`use_continuation` だけから `receipt_mode` を二度とも `"continuation"` に設定している。`use_continuation` は fallback 後も `True` のため、保存済みの `"new_blue"` receipt は `_validate_thread_receipt(..., mode="continuation")` で mode mismatch となり、`blocked / planning_context_rejected / ("thread_receipt_invalid",)` に閉じる。
* **観測事実:** exact HEAD の positive test は、この経路について `candidate_revised`、continuation 1回、new Blue 1回、Blue commit 1回を要求しているため、実装とテスト期待値が直接矛盾する。
* **観測事実:** v3対象HEADでは、fallback後の receipt が `"new_blue"` の場合に publication gate の mode を切り替える処理が存在した。今回の修正で未検証fieldの再読を除去した際、代替となる「validatorが返した最終 validated mode」の引継ぎが実装されていない。
* **受入条件への影響:** exact verified Blue continuation が送信前に利用不能だった場合、同一 synthesized input で新規 Blue を一度だけ開始する `ISS354-REQ-013`、S06 positive control、および v3 Blue repair brief の必須fallback契約を完了できない。Candidate publicationとBlue lineage commitへ到達できず、修正なしにマージできない。
* **最小限の修正方向:** fallback後に `_validate_thread_receipt` が返した最終 validated modeをローカル値として保持し、publisher前gateへ渡す。validated `"new_blue"` の場合は continuation binding/provider/lineage要求を適用しない。未検証の `receipt.mode` を再読して分岐しない。

### P2

なし

## Scope checked

* GitHub connectorで `chemitaro/spec-dock`、named branch `codex/iss-00354-chatgpt-context-contract`、exact HEAD `01868d47b190cdf9e3d82336994c6d201e9ab1e2` を確認した。branch tipと指定HEADは `identical`、ahead `0`、behind `0`であり、default branch fallbackは使用していない。
* exact HEADのcommit metadataと、v3対象HEAD `377013c75c06ec6c8326e7eadadea5dc48525c8c` からの差分を確認した。exact HEAD自体はv3 brief／reviewを保存するevidence-only commitであり、対象snapshotにはその直前のS06 runtime/test修正が含まれる。
* 添付bundle内の canonical `requirement.md`、`design.md`、`plan.md`、S06 v3 Blue repair brief、Fresh Red v3 reviewを確認した。
* GitHub exact HEADで次の四ファイルを確認した。

  * `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  * `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  * `tests/unit/application/test_issue_planning.py`
  * `tests/unit/domain/test_issue_planning_contracts.py`
* `RT-354-S06-v3-001`について、`BlueThreadBinding`、`BlueBindingResolution`、application境界がstatus／digestをexact built-in `str`へ閉じ、unknown status、invalid SHA、cross-lineage、`str` subclass mutationをsubmission前に拒否する実装とnegative matrixを確認した。
* `RT-354-S06-v3-002`について、receipt mode、submission state、`PlanningInvocationResult.status`／`reason`、continuation flagをapplication境界で直接検証し、scalar subclassおよびfrozen field mutationをpublisher／commit前に拒否する実装とテストを確認した。
* `RT-354-S06-v3-003`について、同一stateful thread portで実際のcreate／review publication経路を通し、Candidate ZIP全entry名・全entry bytes、Review JSON、Review summary、create／review result、captured prompt、実attachment tuple、各Path reprを同一private sentinelで走査するテストを確認した。
* source drift、publication failure、collision、stateful planning→revision→fresh Red、fresh Red別binding、public-shape非公開契約の既存テストを確認した。domain public shapeにはprovider handle、Blue／Red binding、transcriptが含まれない。 

## Evidence and limitations

* GitHub connectorによるrepository、named branch、exact commit、exact-ref file blobのread-only inspectionに成功した。添付内容をrepository sourceの代替には使用していない。
* v3の三件について、scalar type hardening、application-boundary再検証、実公開経路privacy scanはexact HEADに存在する。今回のFAILは、それらの修正に伴って新たに生じたfallback後のpublication-mode引継ぎ欠落による。
* exact HEADに関連するGitHub Actions workflow runおよびcombined statusは存在しなかった。repository checkoutを取得できる実行環境ではなかったため、focused pytest、application/domain full suite、Ruff、mypy、`spec-dock validate`、`git diff --check`は本レビューでは実行していない。
* P1はテスト実行結果の推測ではなく、exact HEADの制御フローと、同じexact HEADにあるpositive testの期待値との静的な矛盾に基づく。
* live Oracle/browser、concrete provider handle、same-provider-thread continuation、実providerによるfresh Red生成は未確認である。application-private fake portの証跡をlive provider evidenceへ昇格していない。
* repository、Candidate ZIP、レビュー成果物、コード、テスト、commit、PRへの変更は行っていない。
