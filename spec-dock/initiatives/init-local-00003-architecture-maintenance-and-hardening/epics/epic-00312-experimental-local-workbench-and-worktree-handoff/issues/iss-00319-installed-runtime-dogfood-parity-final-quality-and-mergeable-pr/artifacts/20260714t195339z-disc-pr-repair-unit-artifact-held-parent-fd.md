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
- status: `unit-created-pre-delegation-blocked-by-U3`
- execution_order: Delegate only after U3 is implemented, reviewed, committed, and pushed; both units are required before re-observation

## Delegation Gate

- 本Artifactはworker delegation前に作成する。U3 completionまでU4 workerへhandoffしない。
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
- need_to_fix: `yes`。U4完了までArtifact importはmerge-prepared security contractを満たさない。

## Adopted Descriptor Lifecycle

1. Destination parentをrepository rootからcomponent-by-componentに`O_DIRECTORY | O_NOFOLLOW`でopenし、directory identityをverifyする。
2. Verified destination-parent fdをtemp create前からcleanup完了まで一度保持する。
3. Temp fileはcryptographically adequate/random candidate basenameを生成し、same parent fd + basenameで`O_RDWR | O_CREAT | O_EXCL | O_NOFOLLOW`（availableなら`O_CLOEXEC`）、mode `0o600`として作る。`mkstemp(dir=pathname)`は使わない。
4. Source copy、fsync、staged hashはexisting temp fd contractを維持する。
5. Linux publicationはheld parent fdを`dst_dir_fd`としてverified temp descriptorをno-replace hard-linkする。Publication時にparent pathnameをopenし直さない。
6. macOS publicationはheld parent fdとdestination basenameを`fclonefileat`へ渡し、helper内でparent pathnameをopenし直さない。
7. Directory fsyncはheld parent fdへ実行する。
8. Post-confirmationはdestination basename + held parent fd + no-follow openでhashする。
9. Temp cleanup/identity inspection/unlinkはtemp basename + held parent fdで実施し、visible pathnameが差し替えられてもoriginal verified directory objectだけへ作用する。
10. Parent fdは全cleanup path完了後に一度closeする。Error mapping、no-overwrite、source preservation、committed/cleanup semanticsは維持する。

## Post-Publication Visible Parent Change

- Visible destination parent pathnameがpublication後に差し替わっても、actual publication/confirmation/cleanupはheld original parent fdへboundする。
- Public resultは既存committed warning taxonomyを使う。必要ならexisting `destination_read_failed` contractへmapし、新しい`destination_parent_changed` warning enumやJSON fieldを追加しない。
- Diagnostic specificityよりpublic compatibilityを優先する。Existing taxonomyで安全な表現が不可能ならhuman gateへ戻す。

## Deterministic Test Contract

- A-RACE-1: `temp_create` hookでdestination parent pathnameをexternal directory symlinkへswapする。External sentinel/inventory不変、outside temp/destinationなし、safe `destination_ineligible`またはdefined pre-publication failureをassertする。
- A-RACE-2: Staging後/publication前にparent pathnameをswapする。Publicationはheld original parentへだけ作用し、external sentinel不変、cleanupもoriginal parent内tempへ作用する。
- A-RACE-3: Linux/macOS publication syscall直前にparent pathnameをswapする。Callはheld fd + basenameを使い、outside writeなしをassertする。
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
- U4差分に対してfresh code reviewer、QA reviewer、spec reviewerを順に実行し、P0/P1=0を要求する。
- Focused gates、actual macOS gate、lint、full、parity、fresh reviews、commit/pushはpending。
- U3/U4両方のpushed latest headでfresh fixed-endpoint PR observationを実行し、CI 4/4 passとP0/P1=0を要求する。

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

- U3 prerequisite: `pending`
- implementation: `pending`
- focused/current-macOS/full gates: `pending`
- fresh reviews: `pending`
- commit/push: `pending`
- latest-head CI/re-observation: `pending-after-U3-and-U4`
