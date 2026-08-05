# S06 Fresh Red Team Review v5

* Candidate/Issue: iss-00354 / S06
* repository: chemitaro/spec-dock
* source branch: codex/iss-00354-chatgpt-context-contract
* source HEAD: b832456e84861d7e60b7f43daa490227e03d25f7
* reviewer thread: fresh Red Team v5

## Verdict

PASS

## Findings

### P0

なし

### P1

なし

### P2

なし

## Scope checked

* GitHub connectorでnamed branch `codex/iss-00354-chatgpt-context-contract`を直接解決し、そのtipが指定されたexact HEAD `b832456e84861d7e60b7f43daa490227e03d25f7`であることを確認した。default branchへのfallbackは使用していない。
* v4対象HEAD `01868d47b190cdf9e3d82336994c6d201e9ab1e2` からexact HEADまでのGitHub差分を確認した。差分は2 commitsで、変更対象は次の四ファイルだった。

  * `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/issue_planning.py`
  * `tests/unit/application/test_issue_planning.py`
  * `spec-dock/.../artifacts/implementation-briefs/s06-blue-repair-v4-20260805.md`
  * `spec-dock/.../reviews/red-team-review-s06-code-v4.md`
* exact HEADのcanonical `requirement.md`、`design.md`、`plan.md`を確認し、`ISS354-REQ-011`のverified Blue continuity、`ISS354-REQ-012`のCandidateごとのfresh Red、`ISS354-REQ-013`の一意lineageに対するnew Blue recovery、`ISS354-REQ-014`のprivate thread evidence境界、およびpublication成功後だけBlue lineageを更新するbinding transactionと照合した。
* exact HEADのS06 v4 Blue repair briefとFresh Red v4 reviewを確認し、正式P1 `RT-354-S06-v4-001`の原因、必要なvalidated mode handoff、fallback／continuationの期待状態遷移、negative matrixと照合した。
* `application/issue_planning.py`のapplication-boundary validatorを確認した。`_validate_thread_receipt()`はreceipt/resultのexact object type、mode、submission state、result status/reason、continuation flag、Blue/Red binding、continuation binding/provider/lineageを再検証し、publisher前の`_require_publishable_thread_receipt()`も同じ境界を再適用している。
* `run_issue_planning_revise()`のpositive fallback制御フローを静的に追跡した。

  * `final_thread_contract`はraw receipt、validated result、validated mode、validated submission state、validated Blue bindingを一つのtupleとして保持する。
  * 通常continuationでは`mode="continuation"`として検証した値を保存する。
  * continuationがvalidated `not_submitted`かつvalidated unavailable flag `True`の場合だけ、同一`kwargs`で`invoke_new_blue()`を呼び、second receiptを`mode="new_blue"`として検証し、`final_thread_contract`をsecond validation結果で上書きする。
  * direct new Blueもvalidated `new_blue` contractを保存する。
* transport成功後のpublication gateは、`final_thread_contract`から展開したvalidated `receipt_mode`をpolicy authorityとして使用している。

  * validated `continuation`の場合だけ、prior continuation binding、lineage SHA、provider handleを要求する。
  * validated `new_blue`の場合は、それら三つをすべて`None`にする。
  * publication modeを`use_continuation`、resolution status、最初のcontinuation receipt、raw `receipt.mode`から再構成する分岐は存在しない。
  * raw receiptはgate内でmode mismatchを検出するために再検証されるが、publication policyのmode選択には使用されない。
* Candidate source/current Candidateの再検証、publication、Blue commitの順序を確認した。source drift、publication source stale、collision、archive/build/publication failureではcommitへ到達せず、publication成功後だけcaptured final receiptを新Candidate lineageへcommitする。
* `application/ports.py`で`BlueThreadBinding`、`BlueBindingResolution`、`ThreadInvocationReceipt`、`ChatGptThreadPort`のprivate contractを確認した。mode/state/status/reason/flagのscalar exactness、binding相互排他、successful Blue／fresh Red binding要件、continuation-unavailable状態制約は維持されている。
* `tests/unit/application/test_issue_planning.py`を確認した。

  * normal exact continuationはcontinuation 1、new Blue 0、final mode `continuation`、commit 1を要求し、commit時にprior Blue binding identityを検証する。
  * positive fallbackはcontinuation 1、new Blue 1、publisher 1、commit 1、final receipt mode `new_blue`、committed receiptがfinal new Blue receiptであることを要求する。
  * continuation/new Blue間で同一synthesized object、同一prompt object、同一attachment tuple、各Pathの同一object identityを検証し、backend invocationは1回だけである。
  * validated後のraw final receipt modeを`continuation`へ改変するnegative testは、publisher 0、commit 0、`thread_receipt_invalid`を要求する。
* unknown、`not_submitted`だがunavailable flagなし、forged resolution、forged receipt、scalar subclass、source drift、publication failure、collision、fresh Red、actual create/review privacy sentinel scanの既存fail-closed matrixを確認した。
* `tests/unit/domain/test_issue_planning_contracts.py`で、public result／binding serializationにprovider handle、Blue／Red binding、transcriptが含まれないこと、およびreceiptのresult／binding fieldsがprivate shapeを維持することを確認した。

## Evidence and limitations

* GitHub connectorによるrepository、named branch、branch tip、exact commit、exact-ref file blob、v4 source HEADとの差分、workflow run、combined statusのread-only inspectionを実施した。本レビュー時点でbranch tipと指定HEADは一致し、GitHub Actionsの関連workflow runおよびcombined status entryは存在しなかった。
* GitHubから取得した九ファイルのblob SHAと、補助として提供されたローカルコピーに対する`git hash-object`結果を照合し、すべて一致した。主要な一致値は次のとおり。

  * `issue_planning.py`: `5451326e63d61decefba44addc1f8ad3b8f1c3b6`
  * `ports.py`: `2a85dc6856c61bb50eedc63d4cb8e287d8dd3741`
  * `test_issue_planning.py`: `b9628beb6f6b4033a7ef93ca754ee2a3c8a920e2`
  * `test_issue_planning_contracts.py`: `dc5ab50edccd9678f55fe7a3bf22e77bd11acfd0`
* exact-byteローカルコピーに対して次を実行した。

  * `python -m py_compile`による上記四Pythonファイルのsyntax validation: 成功。
  * Python AST／text probeによる`run_issue_planning_revise()`の静的検証: 成功。

    * `use_continuation`の参照はinvocation path選択内で終了している。
    * publication gateのvalidated `receipt_mode`展開より後には使用されていない。
    * `receipt`または`final_receipt`のraw `.mode`をpublication mode選択に使う参照は存在しない。
    * gateへの`mode=receipt_mode`、`receipts=(final_receipt,)`、validated continuation時だけのbinding／lineage／provider要求を確認した。
* repository checkout取得のための`git clone`は、実行環境のDNS解決失敗（`Could not resolve host: github.com`）で完了しなかった。このため、focused pytest、application/domain test suite、Ruff、mypy、`spec-dock validate`、`git diff --check`は本レビューでは実行していない。本PASSは、exact HEADの制御フロー、GitHub差分、exact-byte static checks、同一HEADのテスト期待値との整合に基づく。
* live Oracle/browser、concrete provider handle receipt、実providerでのsame-provider-thread continuation、実providerでのfresh Red生成は未確認である。fake/private portの静的・unit-test契約をlive provider evidenceへ昇格していない。
* repository、Candidate、レビュー成果物、コード、テスト、commit、branch、PRへの変更は行っていない。
