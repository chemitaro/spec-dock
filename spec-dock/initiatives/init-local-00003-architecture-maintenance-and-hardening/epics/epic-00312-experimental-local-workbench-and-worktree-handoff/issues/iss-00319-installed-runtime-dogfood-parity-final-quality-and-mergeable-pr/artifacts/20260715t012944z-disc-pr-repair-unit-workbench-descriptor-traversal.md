---
種別: disc
ID: "20260715t012944z-disc"
タイトル: "PR Repair Unit U5 Workbench Descriptor Traversal"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-15"
親: ["iss-00319"]
関連: []
authority: "proposed"
derived_from: ["20260715t012925z-chatgpt-output-pr-323-workbench-parent-descriptor-repair-design"]
reflected_to: []
---

# 20260715t012944z-disc PR Repair Unit U5 Workbench Descriptor Traversal

## Repair Unit Identity

- source_batch: `20260714t154712z-pr-repair-batch`
- unit_id: `U5`
- root_cause_family: `workbench_copy.pathname_toctou`
- covered_ids: `R10`
- source_links: PR #323 / Codex review comment `3583742187` / thread `PRRT_kwDOQ99OK86Q8fC6`
- evidence_ref: `artifacts/20260715t012925z-chatgpt-output-pr-323-workbench-parent-descriptor-repair-design.md`
- evidence_integrity: SHA-256 `0a0bb7f0d1a924c59e48cd583e806ab77667d72ec05cb5adfcd31723dee8740a` / 45909 bytes / evidence-only
- bound_head_sha: `82874bf35d2f4b4a3b360bb08d7c26ffe0935210`
- failure_class: `review_feedback:workbench_pathname_toctou`
- decided_priority: `P1`
- merge_blocking: `yes`
- disposition: `fix-now`
- status: `implemented-quality-gates-complete-awaiting-final-spec-commit`
- execution_order: `U5 after U3/U4`; U5完了後にlatest-head CI/Codex re-observationを新規実行する

## Delegation Gate

- 本Artifactはworker delegation前に作成した。
- Workerおよびreviewerは`gpt-5.6-sol` / reasoning `medium`を使う。
- allowed mutation files:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py`
  - `spec-dock/scripts/spec_dock_runtime/infra/fs_cli.py`（providerのexact dogfood mirror）
  - `tests/unit/infra/test_runtime_fs_cli_workbench.py`
- conditional mutation: 既存test hookのprivate boundary変更だけでは上記3ファイルを維持する。Application/CLI testの既存contractが実際に破綻し、unit testだけでは修復不能な場合は実装せずorchestratorへ戻す。
- forbidden mutation: public CLI/JSON contract、Artifact publisher、共通filesystem abstraction、pathname fallback、rollback/transaction、file classifier、copy filter、canonical requirement/design/plan。
- stop condition: Python 3.10 macOS/Linuxで必要なdescriptor primitiveが利用不能、public collision/no-rollback contract変更が必要、allowed boundary外変更が必要、またはsource/destination外へのmutationを防げない場合。

## Validity / Need-To-Fix

- U3はregular-file leafのopen/writeをheld destination-parent fdへ固定したが、recursive directory/symlink branchは依然として`Path.mkdir()`、`Path.unlink()`、`Path.readlink()`、`Path.symlink_to()`、full-path child reopeningを行う。
- Destination parent pathnameをidentity check後にexternal directoryへのsymlinkへ差し替えると、directory作成またはsymlink replacement/createがexternal treeへ向く競合窓がある。
- Reviewer P1はvalid。Latest local full suiteとCIはdeterministic adversarial windowを覆わず、反証にならない。
- need_to_fix: `yes`。PRはU5完了とlatest-head re-observationまでmerge-preparedではない。

## Adopted Design

1. Workbench private recursive merge coreだけをdescriptor-relativeへ変換し、汎用filesystem abstractionは導入しない。
2. 各recursive frameでverified source-directory fdとverified destination-directory fdを列挙から全child処理完了まで保持する。
3. Root pathはdescriptor取得までだけ使用し、以後のdescendant accessはheld parent fd + single basenameだけを使う。
4. Source enumerationは`os.scandir(source_fd)`からnameだけをsnapshot/sortし、`DirEntry` cached type/statをauthorityにしない。
5. Entry inspectionは`os.stat(name, dir_fd=parent_fd, follow_symlinks=False)`、directory openは`O_DIRECTORY | O_NOFOLLOW`、regular file openは`O_NOFOLLOW`を必須とする。
6. Missing destination directoryはheld parent fdで`os.mkdir(name, dir_fd=parent_fd)`し、成功直後に`mutation_started=True`、no-follow stat/open/fstat identity verificationを行う。Rollbackしない。
7. Existing destination file/symlinkはheld parent fdでidentity再確認後`os.unlink(name, dir_fd=parent_fd)`する。成功後に`mutation_started=True`。
8. Source symlink targetはheld source-parent fdで`os.readlink(name, dir_fd=source_parent_fd)`し、前後identityを検証する。Destination linkは`os.symlink(target, name, dir_fd=destination_parent_fd)`で作成する。
9. Regular-file branchはU3のdescriptor copyを再利用し、source/destination parentをfull pathでreopenせず、held parent fd + basenameを受け取る形へ限定的に変更する。
10. Existing collision matrix、source-wins merge、destination-only retention、opaque copy、source retention、bytes/mode/mtime、partial mutation/no rollback、content-free error contractを変更しない。
11. Required primitiveまたはflagが利用不能なplatformではmutation前にfail closedし、`Path.*`やpathname openへfallbackしない。

## Exact Invariants

- Descriptor authority: verified directory fd取得後、visible pathnameはそのframeのauthorityではない。
- Descriptor lifetime: 親fdはchild inspection/mutation全体、child fdはrecursive call全体でopen。
- Basename-only: descendant filesystem operationへabsolute pathやmulti-component pathを渡さない。
- Source-before-mutation: current entryのsource directory/file/symlinkをopen/read/verifyしてからdestinationを変更する。
- No-follow: symlink targetをdirectory/fileとしてopenせず、unlinkはlink objectだけを対象にする。
- Exclusive creation: regular fileは`O_CREAT | O_EXCL`、directoryは`mkdir`、symlinkは`symlink`のsyscall resultをauthorityとする。
- Mutation flag: successful mkdir/unlink/exclusive file create/symlink createの直後だけtrueへ遷移し、falseへ戻さない。
- No rollback: mkdir後open failure、unlink後create failure、mid-copy failureではpartial stateを保持する。
- Provider authority: providerを先に変更し、dogfood mirrorとexact byte parityを必須とする。

## Deterministic Test Contract

- W-FD-ROOT-1: Root destination-parentをverified fd取得後、relative root `mkdir`直前にexternal directoryへのsymlinkへ差し替える。External inventory/bytes不変、mutationはheld/displaced original parent内だけ。
- W-FD-ROOT-2: Root `mkdir`成功直後にfailureを注入する。`mutation_started=True`、rollbackなし、external tree不変。
- W-FD-NEST-1: Nested destination-parent visible pathをheld fd取得後に差し替え、child mkdir/file/symlink mutationがexternal targetへ到達しない。
- W-FD-DIR-1: `mkdir`後child open前にcreated directoryをsymlinkへ差し替える。`O_NOFOLLOW | O_DIRECTORY`でsafe failure、`mutation_started=True`、external tree不変。
- W-FD-SYM-1: Existing destination symlink/fileのidentity capture後、unlink前にleafを差し替える。Mismatch時はcurrent entry mutation flag unchanged。
- W-FD-SYM-2: Verified unlink成功後、symlink create前にentryを挿入する。Createは`EEXIST`、`mutation_started=True`、external target不変。
- W-FD-SYM-3: Missing symlink destinationへcreate直前にentryを挿入する。Createは`EEXIST`、`mutation_started=False`。
- W-FD-SOURCE-1: Source parent visible pathをfd取得後に差し替える。Enumeration/readlink/openはheld source directoryから行い、replacement sourceを読まない。
- W-FD-SOURCE-2: Source child directory/symlinkをidentity capture後に差し替える。Openまたはpost-read identity mismatchでdestination current entryをmutationしない。
- W-REGRESSION: directory/file/symlink collision、destination-only entries、repeat copy、empty source、unsupported source entry、binary bytes/mode/mtime、mid-copy partial failure、source retention。
- W-CAP: Required primitive/flag unavailable時にfail closedし、pathname fallbackが呼ばれない。
- W-FD-CLEANUP: Successおよびinjected failure各境界でopened fdをexactly once closeする。
- W-PARITY: provider/dogfood file bytes、inventory、SHA-256一致。
- Repetition: 新規adversarial nodesを反復実行しflakiness 0を確認する。

## Portable Residual Limits

- Python 3.10 stdlibの`mkdir -> stat/open`はdirectory creationとdescriptor取得をatomicにできない。Symlink replacementをfollowせずparent redirectionを防ぐが、同権限adversaryによる別real-directory substitutionを完全には排除しない。
- `stat -> unlink`および`stat -> readlink -> stat`にはsame-held-directory内のleaf ABA raceが残る。Outside parentへのredirectやsymlink target dereferenceは防ぐが、serializable concurrent mutationは約束しない。
- これらはdocumented residual riskであり、`openat2`/`renameat2`/`O_PATH`/rollback/transactionを本unitへ追加しない。

## Validation Plan

```bash
uv run --python 3.10 pytest tests/unit/infra/test_runtime_fs_cli_workbench.py
uv run pytest tests/unit/infra/test_runtime_fs_cli_workbench.py
uv run pytest tests/unit/application/test_workbench.py tests/cli_runtime/test_workbench.py
cmp src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py spec-dock/scripts/spec_dock_runtime/infra/fs_cli.py
make lint
git diff --check
uv run --python 3.12 pytest
```

- RED evidenceを現HEADで新規adversarial nodesについて取得する。
- GREEN後、new nodes反復、actual Python 3.10 focused、related regression、lint、parity、diff、full Python 3.12を実行する。
- Fresh code reviewer、QA reviewer、spec/pre-commit reviewerを順に実施し、P0/P1 0を要求する。
- Commit/push後、fixed-endpoint PR observationを新しいlatest headで一度だけtriggerし、GitHub Actions terminal successとCodex current-boundary P0/P1 0を要求する。

## Out of Scope

- Workbench/Artifact共通secure filesystem framework。
- Windows/pathname fallback。
- Linux-only `openat2`、`renameat2`、`O_PATH`、`O_TMPFILE`。
- Tree-wide preflight、atomic transaction、rollback、copy-back、sync。
- Directory metadata、ACL、xattr、ownershipの新規copy contract。
- Public CLI/JSON/error taxonomy変更。
- Root Workbench bulk copyまたはclassifier/filter。
- Artifact publisher U4の追加変更。
- PR merge。

## Consultation Disposition

- use: Recursive frameごとのsource/destination held fd、basename-only `*at` operations、source-before-mutation、relative mkdir/open/unlink/readlink/symlink、capability fail-closed、adversarial matrix。
- partial-use: `mkdir -> open`のreal-directory substitutionとsame-directory leaf ABAはportable residualとして明示し、current P1のoutside-redirection防止へscopeを限定する。
- reject: Obvious `Path.mkdir/unlink/symlink_to`行だけの置換。Path-based enumeration/inspection/reopenが残るため不十分。
- reject: Generic abstraction、pathname recheck fallback、platform-specific stronger primitives、rollback/transaction。
- Evidence Artifactはcanonical authorityではなく、本unitが採用境界を明示する。

## Completion Contract

- implementation: `complete-locally`
- exact allowed files: provider `fs_cli.py`、dogfood mirror、infra Workbench tests。
- scope result: 実装変更は上記3ファイルだけ。Provider first、dogfood exact mirror。Public CLI/JSON、Artifact publisher、canonical requirement/design/plan、pathname fallback、rollbackは未変更。
- RED initial: Head `82874bf35d2f4b4a3b360bb08d7c26ffe0935210`で4 adversarial nodesを先に実行し4 failed。Root mkdir parent swap、nested mkdir parent swap、destination symlink-create parent swap、source readlink parent swap。
- RED QA follow-up: Managed archiveのexact head `82874bf3`へ追加2 testsを重ね、2 failed。Old runtimeにはrecursive descriptor helper `_open_verified_directory_at`が存在せず、nested destination/source child fd取得後の継続契約を満たさない。
- GREEN current: Python 3.10.15 focused 48 passed、Python 3.12.11 focused 48 passed、Workbench application + CLI related 47 passed。
- adversarial repetition: Initial/current 12 nodes x10 = 120/120。QA follow-up 2 nodes x10 = 20/20。
- static/parity: `make lint` PASS、provider/dogfood `cmp` PASS、`git diff --check` PASS。
- fresh code review: Initial review PASS P0-P3=0。QA follow-up delta reviewもPASS P0-P3=0、commit可。
- fresh QA review: Initial P1 coverage gapは追加2 deterministic nested-frame testsで修復。Fresh rereviewはCONDITIONAL PASS、P0/P1=0、P2=2 non-blocking residual、P3=0。QA観点precommit可。
- full Python 3.12 pytest: PASS。`2620 passed / 76 skipped / 2 warnings in 1636.44s (0:27:16)`。
- environment correction: 最初のfull attemptはDevCoderのPython 3.10 focused後に`.venv/bin/python`が3.10.15のままで、authoring-pack `datetime.UTC`とisolated build environmentが93 failureを生じた。`.venv`をPython 3.12.11へ再作成し、元failure代表82 testsを82/82 passで確認後、full suiteを最初から再実行して上記terminal PASSを取得した。これはU5 regressionではない。
- final fresh spec/precommit: `pending`。
- commit/push: `pending`
- latest-head CI/Codex re-observation: `pending`
- merge: `forbidden`
