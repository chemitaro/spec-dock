---
種別: disc
ID: "20260714t195339z-disc"
タイトル: "PR Repair Unit U4 Artifact Held Parent FD"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-15"
親: ["iss-00319"]
関連: []
authority: "proposed"
derived_from: ["20260714t195256z-chatgpt-output-pr-323-symlink-race-repair-design"]
reflected_to: []
---

# 20260714t195339z-disc PR Repair Unit U4 Artifact Held Parent FD

## Repair Unit Identity

- source_batch: `20260714t154712z-pr-repair-batch`
- unit_id: `U4`
- root_cause_family: `artifact_import.destination_parent_symlink_race`
- covered_ids: `R9`
- source_links: PR #323 / latest Codex P1 / consultation `pr323-symlink-race-repair-design`
- evidence_ref: `artifacts/20260714t195256z-chatgpt-output-pr-323-symlink-race-repair-design.md`
- evidence_integrity: SHA-256 `92726c3966e78dfa3bdd5236093493966271f3a552fbc08b44de938c213799a1` / 40156 bytes / evidence-only
- bound_head_sha: `90a7adf3`
- failure_class: `review_feedback:artifact_destination_parent_symlink_race`
- decided_priority: `P1`
- merge_blocking: `yes`
- disposition: `fix-now`
- status: `completed-and-pushed-latest-head-combined-observation-pending`
- execution_order: U3 prerequisite completed at head `3dd94928d6d4b8a3810b9170b9fcb027572c64f2`; U4 pre-delegation、code、QA、final spec gatesとcommit/push `82874bf35d2f4b4a3b360bb08d7c26ffe0935210`は完了。Separate U5後のlatest-head combined external gatesだけを残す

## Delegation Gate

- 本Artifactはworker delegation前に作成済み。U3 prerequisiteはhead `3dd94928d6d4b8a3810b9170b9fcb027572c64f2`で完了し、U4固有のfresh pre-delegation gateがpassした後にworkerへhandoffした。
- Workerは`gpt-5.6-sol` / reasoning `medium`を使う。
- allowed mutation files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`
  - `spec-dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`（providerのexact dogfood mirror）
  - `tests/unit/infra/test_binary_artifact_publisher.py`
- forbidden mutation: 上記以外の全tracked file。Contracts/public warning enum、application/commands/CLI tests、common filesystem abstraction、general refactorを含む。
- stop condition: Existing warning/error/cleanup contractで安全に表現できない、macOS/Linux supported primitiveが不足する、public JSON変更が必要、またはU3とのshared abstractionが必要になった場合は実装せずorchestratorへ戻す。

## Validity / Need-To-Fix

- Current publisherはpathname ancestry guard後、`mkstemp(dir=destination.parent)`、late parent open、absolute destination confirmation、pathname temp cleanupでparent pathを繰り返し再解決する。
- Destination parentをguard後にexternal directoryへのsymlinkへ差し替えると、stagingまたは後続mutationがrepository外へredirectされ得る。
- Existing staged-path replacement testはverified temp descriptor bindingを覆うが、destination parent object bindingを覆わない。
- Latest CI 4/4 passは当該raceを感知しないためP1 findingの反証にならない。
- need_to_fix: `completed locally and pushed`。Latest-head Ubuntu actual `linkat` gateとCI/re-observation完了までmerge-prepared security contract全体のclosureは確定しない。

## Adopted Descriptor Lifecycle

1. Existing lexical containment/source guardを完了し、source fdとinitial identityを取得する。
2. `inject("temp_create")`をdestination parentのsecure component walk/openより前に一度実行する。このhookでvisible parentがexternal symlinkへswapされた場合、続くsecure walkがrejectし、exact `BinaryArtifactPublishError(code="destination_ineligible", cleanup_state="not_created", committed=False)`で終了する。Tempまたはformal destinationをoriginal/external parentのどちらにも作らない。
3. Destination parentをrepository rootからcomponent-by-componentに`O_DIRECTORY | O_NOFOLLOW`でopen・identity verifyし、verified parent fdを取得する。このfdをtemp createからcleanup完了まで一度保持する。
4. Temp fileはcryptographically adequate/random candidate basenameを生成し、same parent fd + basenameで`O_RDWR | O_CREAT | O_EXCL | O_NOFOLLOW`（availableなら`O_CLOEXEC`）、mode `0o600`として作る。`mkstemp(dir=pathname)`は使わない。
5. Source copy、temp fsync、staged hash、stage barrier、source stability verificationをexisting descriptor contractで完了する。
6. Source verification後かつformal publication前に`inject("before_publication")`を一度実行する。直後にvisible destination parentをrepository rootからsecure re-walkし、得たidentityをheld parent fdのidentityと比較する。Missing、symlink、identity mismatchはpublication helperを呼ばず、exact `BinaryArtifactPublishError(code="destination_ineligible", cleanup_state="removed", committed=False)`へmapする。Temp cleanupはheld original parent fdだけへ作用する。
7. Pre-publication revalidationがpassした場合だけformal publicationへ進む。Linuxはheld parent fdを`dst_dir_fd`としてverified temp descriptorをno-replace hard-linkし、macOSは`fclonefileat(temp_fd, held_parent_fd, destination_basename, 0)`を使う。Helper内でparent pathnameをopenし直さない。Actual publication syscall windowでvisible parentがswapされてもsyscallはheld fd + basenameへboundする。
8. Publication成功時点でcommittedとなる。Directory fsyncはheld parent fdへ実行する。
9. Publication後、visible destination parentを再度secure re-walkし、held parent fd identityと比較する。Missing、symlink、identity mismatchならformal destinationのdescriptor confirmationを試みず、existing committed-warning contractへexactにmapする。Resultは`committed=True`、`warning_codes=("destination_read_failed",)`、`destination_sha256=staged_sha256`、`destination_byte_count=staged_byte_count`とし、新warning enumを追加しない。
10. Post-publication parent identityが一致する場合だけ、destination basename + held parent fd + no-follow openでhash confirmationする。既存のdestination mismatch/read failure contractを維持する。
11. Temp cleanup/identity inspection/unlinkはtemp basename + held parent fdで実施し、visible pathnameが差し替えられてもoriginal verified directory objectだけへ作用する。Parent fdは全cleanup path完了後に一度closeする。

## Post-Publication Visible Parent Change

- Visible destination parent pathnameがpre-publication revalidation後からactual syscallまでのwindowで差し替わっても、actual publicationとcleanupはheld original parent fdへboundする。
- Publication後のsecure visible-parent re-walk/identity comparisonがmismatchを検出した場合、public resultはexact existing `destination_read_failed` committed-warning contractを使う。Staged hash/countをdestination hash/countとして返し、新しい`destination_parent_changed` warning enumやJSON fieldを追加しない。
- Diagnostic specificityよりpublic compatibilityを優先する。Existing taxonomyで安全な表現が不可能ならhuman gateへ戻す。

## Deterministic Test Contract

- A-ORDER-1: Call logで`inject("temp_create")`がdestination-parent secure component walk/openより前であること、secure walk/held-fd取得後にfd-relative temp createが続くことをassertする。
- A-RACE-1: `inject("temp_create")`でdestination parent pathnameをexternal directory symlinkへswapする。Secure walkがswapをrejectし、exact `code="destination_ineligible"`、`cleanup_state="not_created"`、`committed=False`をassertする。External sentinel/inventory不変、original/externalの双方にtemp/formal destinationなしをassertする。
- A-ORDER-2: Call logでsource copy → temp fsync → staged hash → source stability verification → `inject("before_publication")` → secure visible-parent re-walk/identity compare → publication helperの順序をassertする。
- A-RACE-2: `inject("before_publication")`でparent pathnameをswapする。Re-walk mismatchがformal publicationを抑止し、exact `code="destination_ineligible"`、`cleanup_state="removed"`、`committed=False`をassertする。External sentinel/inventory不変、formal destinationなし、temp cleanupはheld original parent内だけに作用する。Publicationが進むという旧期待は採用しない。
- A-RACE-3: Pre-publication revalidation後、Linux/macOS actual publication syscallのinside-window hook/monkeypatchでparent pathnameをswapする。Publication callがheld fd + basenameだけを使ってoriginal parentへcommitすること、external sentinel/inventory不変、outside temp/destinationなしをassertする。Publication後re-walk mismatchによりresultがexact `committed=True`、`warning_codes=("destination_read_failed",)`、destination hash/countがstaged hash/countと一致、cleanupがheld original parentだけへ作用することをassertする。
- A-ORDER-3: Call logでpublication syscall → held-parent directory fsync → secure visible-parent re-walk/identity compare → identity一致時のみfd-relative destination confirmation → held-fd temp cleanup → held parent fd closeの順序をassertする。Mismatch時はconfirmationをskipしてexisting committed warningへmapする。
- A-LINUX-1: Linux call-shape unit testはlate `os.open(destination.parent)`を許さず、captured held `dst_dir_fd`をassertする。
- A-MACOS-1: `fclonefileat(temp_fd, held_parent_fd, destination_basename, 0)` shapeをassertする。Mockだけではactual macOS gateをcloseしない。
- A-CLEANUP-1: Visible parentをdisplaceしてもtemp identity check/unlinkがheld original parentだけへ作用し、external same-name sentinelを保持する。
- Existing destination collision、publication unsupported、staged pathname replacement、committed warning、temp retained testsを維持する。Absolute destination `os.open` monkeypatchはfd-relative boundaryに合わせて最小更新する。
- Safe synthetic bytesだけを使い、body、absolute host path、secret-like valueをevidenceへ出力しない。

## Validation Plan

```bash
uv run pytest tests/unit/infra/test_binary_artifact_publisher.py
uv run pytest tests/unit/application/test_binary_artifact_import_ports.py
uv run pytest tests/unit/commands/test_artifact_import_chatgpt_output.py
uv run pytest tests/cli_runtime/test_artifact_import_chatgpt_output.py tests/cli_runtime/test_artifact_import_s04.py
cmp src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py spec-dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py
make lint
uv run pytest
git diff --check
```

- Current macOS hostで`tests/unit/infra/test_binary_artifact_publisher.py`をactual focused executionし、real `fclonefileat` publication pathを含むことをevidenceで確認する。Mock call-shapeだけではcloseしない。
- Actual Python 3.10 interpreterで`python3.10 -m pytest tests/unit/infra/test_binary_artifact_publisher.py`をpre-push実行し、exact publisher infra fileのpassを要求する。Python 3.10 interpreter unavailableはpassではなく、explicit gate/human conditionとして停止・報告する。
- U4 pre-delegation fresh rereviewはPASSし、worker handoffを許可した。実装後のfresh code reviewerはPASS（P0-P3=0）、QA reviewerはconditional PASS（code P0-P3=0）。
- REDはisolated old HEADへnew adversarial/order nodesだけを適用し、6 failed / 1 Linux-only skippedを確認した。
- GREEN current macOS focused publisherは47 passed / 1 Linux-only skipped。Actual uv CPython 3.10.15でも47 passed / 1 Linux-only skipped。Current macOSでreal `fclonefileat` syscall-window race nodeが実行済み。
- Related Artifact import regressionは33 passed。Four adversarial/order nodesは10回ずつ、合計40/40 pass。
- `make lint`、provider/dogfood exact `cmp`、`git diff --check`はPASS。
- Required full `uv run --python 3.12 pytest`は2606 passed / 76 skipped / 2 warnings in 1757.50sでPASS。
- Final fresh spec/precommit reviewはPASS。Commit/push `82874bf35d2f4b4a3b360bb08d7c26ffe0935210`完了。Actual Linux `linkat` syscall-window raceはlocal macOSでは実行不能のため、U5後latest-head Ubuntu CIの必須combined gateとして残す。
- U3/U4/U5を含むpushed latest headでfresh fixed-endpoint PR observationを実行し、全required CI successとP0/P1=0を要求する。

## Out of Scope

- New public warning enum/JSON field、public API/CLI behavior変更。
- Workbench/Artifact共通filesystem abstraction。
- Linux `O_TMPFILE` / `AT_EMPTY_PATH`全面再設計。
- Pathname `mkstemp`、late parent re-open、absolute destination confirmation/cleanup fallback。
- U3 Workbench behavior、recursive directory hardening、unrelated refactor。
- PR merge。

## Consultation Disposition

- use: Held destination-parent fd lifecycle、fd-relative temp/publication/fsync/confirmation/cleanup、deterministic external-sentinel tests、actual macOS gate。
- partial-use: Post-publication visible parent changeはexisting warning taxonomyへmapし、新warning enumは導入しない。これはuser simplicity-first constraintsとcanonical requirementsに整合するorchestrator bounded decisionであり、explicit human selectionとは主張しない。
- use: Current macOS actual focused gateとactual Python 3.10 exact infra-file gate。いずれもorchestrator bounded decisionであり、interpreter unavailableをpass扱いしない。
- reject: Common abstraction、staging-only or publication-only fd binding、late parent reopen、pathname cleanup、`O_TMPFILE`全面変更。
- Evidence Artifactはcanonical authorityではなく、本unitが採用境界を明示する。

## Commit / Re-observation Evidence

- U3 prerequisite: `complete`。Focused/local/full/fresh reviews/commit/pushがhead `3dd94928d6d4b8a3810b9170b9fcb027572c64f2`で完了。
- U4 pre-delegation fresh gate: `complete`
- implementation: `complete-locally`
- exact changed code/test files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`
  - `spec-dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py`
  - `tests/unit/infra/test_binary_artifact_publisher.py`
- scope boundary: Exactly the three authorized files。Public warning enum/JSON、application/commands/CLI、common abstractionは変更なし。
- RED isolated old HEAD/new nodes: 6 failed / 1 Linux-only skipped。
- GREEN current macOS: Focused publisher 47 passed / 1 Linux-only skipped。Real `fclonefileat` syscall-window node executed。
- GREEN actual Python 3.10: uv CPython 3.10.15、focused publisher 47 passed / 1 Linux-only skipped。
- related/repeat gates: Artifact import related regression 33 passed。Four adversarial/order nodes 40/40。
- static/parity/diff gates: `make lint` PASS、provider/dogfood exact `cmp` PASS、`git diff --check` PASS。
- full pytest: `uv run --python 3.12 pytest` PASS。2606 passed / 76 skipped / 2 warnings in 1757.50s。
- fresh reviews: Code review PASS P0-P3=0。QA conditional PASS、code P0-P3=0。Final fresh spec/precommit PASS。
- Linux actual gate: latest-head Ubuntu CIでactual `linkat` syscall-window race nodeの実行成功を要求する。Local macOSのskipはpass代替ではない。
- commit/push: `complete` at `82874bf35d2f4b4a3b360bb08d7c26ffe0935210`
- local closure: R9/F7 implementation、focused/related/repeat/current-macOS/Python 3.10/static/parity/full、fresh code/QA/spec reviews、commit/push complete。Head `82874bf3` current reviewでF7再発なし。
- latest-head CI/re-observation: `pending-after-U5-commit-push`; Ubuntu actual `linkat`をcombined headで確認する
