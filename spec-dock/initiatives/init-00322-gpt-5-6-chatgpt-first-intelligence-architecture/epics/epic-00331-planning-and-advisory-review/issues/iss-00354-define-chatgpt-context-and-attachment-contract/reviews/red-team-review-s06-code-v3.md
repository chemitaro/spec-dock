# S06 Fresh Red Team Review

* Candidate/Issue: iss-00354 / S06
* repository: chemitaro/spec-dock
* source branch: codex/iss-00354-chatgpt-context-contract
* source HEAD: 377013c75c06ec6c8326e7eadadea5dc48525c8c
* reviewer thread: fresh Red Team v3

## Verdict

FAIL

## Findings

### P0

なし

### P1

#### RT-354-S06-v3-001 — 閉じた Blue resolution と lineage 検証を scalar subclass で迂回できる

* **ID:** `RT-354-S06-v3-001`
* **該当箇所:** `application/ports.py::BlueThreadBinding.__post_init__`、`BlueBindingResolution.__post_init__`、`application/issue_planning.py::_validate_blue_resolution`、`run_issue_planning_revise`、`tests/unit/application/test_issue_planning.py::test_s06_forged_resolution_is_blocked_before_transport_or_new_blue`
* **観測事実:** exact HEAD は resolution と binding 本体を `type(...) is ...` で確認するよう修正されているが、`status` は `in` / `==`、`lineage_sha256` は `isinstance(..., str)`、正規表現、`!=` で検証しており、各比較は field object のオーバーライド可能な等価演算に依存している。read-only probe では、内部文字列が `forged` でも `exact` と等価に振る舞う `str` subclass が closed status を通過した。また、内部文字列が要求 lineage と異なる64桁16進文字列でも、`__ne__` が偽を返す `str` subclass は SHA 形式検証と lineage 不一致検証を通過した。現行テストは通常の `str` である `forged`、別 digest、非16進 digest だけを使用している。
* **受入条件への影響:** 実際には未知 status または別 Candidate/source lineage の binding が `exact` として扱われ、誤った provider handle を `invoke_continuation()` に渡せる。verified matching lineage だけを継続し、不正・曖昧な lineage は submission 前に停止する `ISS354-REQ-011` / `ISS354-REQ-013` と、v1/v2 P1 の forged/subclass bypass 修正条件を満たさない。
* **最小限の修正方向:** ports の通常構築時検証と application 境界の双方で、status と digest を exact built-in `str` に閉じ、オーバーライドされた等価演算を通さない正規値同士で比較する。`str` subclass および exact dataclass の field mutation を用いた unknown-status、cross-lineage negative testを追加する。

#### RT-354-S06-v3-002 — submission state の等価演算を偽装すると unknown fallback と未送信 publication gate を迂回できる

* **ID:** `RT-354-S06-v3-002`
* **該当箇所:** `application/ports.py::ThreadInvocationReceipt.__post_init__`、`application/issue_planning.py::_validate_thread_receipt`、`_require_publishable_thread_receipt`、`run_issue_planning_revise::revision_backend_invoker`
* **観測事実:** `receipt` と `result` の実型確認、Blue/Red binding の排他、mode別 binding 必須条件は追加されている。一方、`mode`、`submission_state`、`result.status`、publication 時の `result.reason` は exact scalar type を確認せず、`in`、`==`、`!=` だけで判定している。read-only probe では、内部文字列が `unknown` でも `not_submitted` と等価に振る舞う `str` subclass が valid continuation receipt として受理され、continuation-unavailable fallback 条件を真にした。別の probe では、内部文字列が `not_submitted` でも `successful` と等価に振る舞う state が constructor、application validator、`pass / transport_received` publication gate のすべてを通過した。
* **受入条件への影響:** submission state が実質 unknown の continuation から新規 Blue を開始でき、また実質未送信の receipt で Candidate または Review の公開処理へ到達できる。これは「unknown は fallback 0」「明示された `not_submitted + continuation unavailable` の場合だけ新規 Blue」「publication は実際の successful submission と `transport_received` に限定」という S06 契約に対する fail-open である。
* **最小限の修正方向:** receipt の mode/state と public result の status/reason を ports と application の両境界で exact built-in `str` として検査し、その後に closed value を比較する。underlying `unknown` を `not_submitted` に、underlying `not_submitted` を `successful` に見せる subclass／mutated-field testを追加し、fallback、publisher、commit がすべて0であることを固定する。

#### RT-354-S06-v3-003 — 必須 privacy／forged-boundary test matrix が実公開面を検査していない

* **ID:** `RT-354-S06-v3-003`
* **該当箇所:** `tests/unit/application/test_issue_planning.py::test_s06_private_thread_sentinel_stays_out_of_public_and_artifact_surfaces`、`test_s06_forged_resolution_is_blocked_before_transport_or_new_blue`、`test_s06_forged_receipt_blocks_before_publisher_and_commit`、`tests/unit/domain/test_issue_planning_contracts.py::test_s06_public_contract_shapes_remain_content_free`
* **観測事実:** repair v2 は、一つの private sentinel を provider handle と fake transcript に埋め、実際に公開された Candidate ZIP の全 entry、Review JSON、Review summary、captured prompt、attachment tuple／各 Path を走査するよう要求している。 現行 privacy test は application の create/review transaction を実行せず、手作業で作った binding、receipt、public result、合成した prompt/path と、provider から受け取った authoring ZIP を連結して検索している。published Candidate ZIP、published Review JSON／summary、および fake transcript sentinel は検査対象に入っていない。 また forged tests は plain invalid values だけで、P1-001／002を再現する scalar subclass・等価演算偽装・field mutationを含まない。
* **受入条件への影響:** 現行 suite は P1-001／002の application-boundary bypass が存在しても Green のままであり、実際の Candidate／Review 公開経路へ private handle、transcript、private URL/path が混入する退行も検出できない。v2 P1 が要求した failure/privacy matrix と `cl-s06-blue-red` / `tc-s06-001` の executable evidence が未完了である。
* **最小限の修正方向:** 既存 application/domain test範囲内で、sentinel付きの同一 thread portを通して create と review を実行し、生成された Candidate ZIP全entry、Review result／summary、実captured prompt／attachmentsを検査する。併せて P1-001／002の subclass／mutated-field casesを既存 forged matrixへ追加する。

### P2

なし

## Scope checked

* canonical `requirement.md` の Blue continuity、fresh Red、unique-lineage fallback、thread evidence privacy、successful-submission transactionに関する `ISS354-REQ-011`〜`014`、`031`、`032`。
* canonical `design.md` の Blue/Red thread transaction、private receipt/public result分離、privacy boundary、S06 test architecture。
* canonical `plan.md` の S06、`cl-s06-blue-red`、`tc-s06-001`、source drift、unavailable fallback、fresh Red、privacy test契約。
* `artifacts/implementation-briefs/s06-blue-continuity-fresh-red-20260805.md`、Blue repair brief v1/v2、Fresh Red review v1/v2、implementation/test matrix。
* GitHub connectorで exact HEAD `377013c75c06ec6c8326e7eadadea5dc48525c8c` の commit、branch比較、実装差分を確認した。connector観測時、named branch tipは指定HEADと identical、ahead `0`、behind `0`であり、default branch fallbackは使用していない。
* GitHub exact HEAD の次の実装・テストを確認した。

  * `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py`
  * `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  * `tests/unit/application/test_issue_planning.py`
  * `tests/unit/domain/test_issue_planning_contracts.py`
* v2で指摘された `result: Any`、virtual `__post_init__` 再呼出し、Blue/Red binding同時保持、missing binding publication、stateful publication failure/collision/source-drift、fallback object identity、E306について、現在の修正箇所と対応テストを確認した。E306のblank line、actual `PlanningInvocationResult` annotation、top-level exact dataclass type checks、publisher前 receipt gateは現HEADに存在する。

## Evidence and limitations

* GitHub connectorによるrepository、named branch、exact commit、四つのimplementation/test blobのread-only inspectionに成功した。添付bundleから復元した四ファイルのGit blob SHAはGitHub exact HEADのblob identityと一致した。
* exact sourceから抽出した validator を用いるread-only supplemental probeで、以下を再現した。

  * 内部値が未知 status／別 lineage digestである `str` subclassが `_validate_blue_resolution()` に受理される。
  * 内部値が `unknown` である stateが `not_submitted` としてcontinuation fallback条件を成立させる。
  * 内部値が `not_submitted` である stateが `successful` として publication gateを通過する。
* 添付された四つのPython blobに対する `python -m compileall` は成功した。
* exact HEADについてGitHub workflow runとcombined statusは確認できなかった。実行環境ではrepository checkoutを取得できなかったため、brief記載のfocused pytest、application/domain full suite、Ruff、mypy、`spec-dock validate`、`git diff --check`は本reviewでは実行していない。
* live Oracle/browser、concrete provider handle receipt、same-provider-thread continuation、実providerでのfresh Red作成は未確認である。application-private fake portによるunit evidenceをlive provider evidenceとして扱っていない。
* exact HEADの`report.md`がS06 closureをまだ記録していないことは、fresh review後の別evidence commit境界と整合するためfindingにしていない。
* repository、仕様、Candidate、テスト、commit、PRへの変更は行っていない。
