---
種別: disc
ID: "20260714t175806z-disc"
タイトル: "PR Repair Unit U2"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-14"
親: ["iss-00319"]
関連: []
authority: "proposed"
derived_from: []
reflected_to: []
---

# 20260714t175806z-disc PR Repair Unit U2

## Repair Unit Identity

- source_batch: `20260714t154712z-pr-repair-batch`
- unit_id: `U2`
- root_cause_family: `artifact_collision.wall_clock_flake`
- covered_ids: `R4`, `R7`
- source_links: PR #323 / Codex current-boundary review / Provider CI run 29352522159 / duplicate same-head run 29352527033
- failure_class: `check_failure:provider-tests` + `external_or_flaky:test_timing`
- decided_priority: `required-ci`
- merge_blocking: `yes`
- disposition: `fix-now`
- status: `implemented-locally`

## Delegation Gate

- このArtifactはU2 worker delegation前に作成した（historical gate evidence）。
- Worker scope、allowed file、validation、stop conditionは本Artifactとrepair batch S100-R2へbindした。
- allowed mutation file: `tests/cli_runtime/test_artifact_import_chatgpt_output.py` only。
- focused node: `tests/cli_runtime/test_artifact_import_chatgpt_output.py::TestArtifactImportChatGptOutput::test_existing_blank_chatgpt_output_slug_coexists_with_import`。
- forbidden mutation: 上記以外の全tracked file。Production clock、provider/dogfood runtime、shared test harness、global clockを含む。
- Implementationは完了。commit、push、latest-head CI、re-observationはpending。

## Validity Analysis

- Head `a7a7c072`にbindしたCodex current-boundary reviewはnew findings 0 / thread 0だった。
- Provider CI run 29352522159はF4の1 testだけ失敗し、2597 passed / 75 skipped / 2 warningsだった。
- 同じheadのduplicate run 29352527033は成功し、failureがnondeterministic wall-clock flakeであることを実証した。
- Duplicate successはfailed required runを置換しないため、F4はrequired-CI blockerとしてvalidである。
- F1 Linux descriptor publicationはUbuntuでoperationally passedし、追加変更は不要。

## Need-To-Fix Decision

- need_to_fix: `yes`
- reason: Required Provider CI run 29352522159がfailureのままであり、PR #323をmerge-preparedにできない。
- repair boundary: `tests/cli_runtime/test_artifact_import_chatgpt_output.py` only。Production clock、harness、global clockを含む他の全tracked fileへ変更を広げない。

## Root Cause

- Artifact blank作成とimport collisionの期待名がwall clockの秒境界に依存し、temporary consumer subprocess側のclockを固定していない。
- 同じheadのsuccess/failure分岐はproduct behaviorの恒常的失敗ではなく、test timing nondeterminismと一致する。

## Options Considered

1. Failed runをduplicate successで無視する
   - Required run failureが残るため不採用。
2. Productionまたはglobal clockへinjection pointを追加する
   - Product scopeを不要に拡大するため不採用。
3. Test内のtemporary consumer copied clockだけを固定する
   - Fresh consultation `pr323-f4-required-ci-consultati`が推奨。One-file test-onlyの最小修復として採用。

## Recommended Design

- Init後、temporary consumerの`spec-dock/scripts/spec_dock_runtime/infra/clock.py`だけを上書きし、`now_iso` / `today`を固定する。
- Real `new artifact blank` subprocessを1回、real `artifact import` subprocessを1回実行する。
- Exact unsuffixed filename、`-01` collision filename、import JSON、source survivalをassertする。
- Production clock、test harness共通部、global clock、runtime APIは変更しない。

## Implementation Plan

1. `tests/cli_runtime/test_artifact_import_chatgpt_output.py`だけを編集する。
2. Temporary consumer init後にcopied `clock.py`をdeterministic implementationへ置換する。
3. Real blank creation/import subprocessを各1回実行する。
4. Exact filename/JSON/source survivalを固定assertする。
5. `tests/cli_runtime/test_artifact_import_chatgpt_output.py::TestArtifactImportChatGptOutput::test_existing_blank_chatgpt_output_slug_coexists_with_import`を20回repeatし、file + S04 + `test_new`、lint/fullを実行する。
6. Fresh review後にcommit/pushし、新headのUbuntu Provider CIとCodex reviewを観測する。

## Validation Plan

- `tests/cli_runtime/test_artifact_import_chatgpt_output.py::TestArtifactImportChatGptOutput::test_existing_blank_chatgpt_output_slug_coexists_with_import`を20回repeatし、全回pass。
- `tests/cli_runtime/test_artifact_import_chatgpt_output.py` + S04 regression + `test_new`。
- `make lint`。
- Full pytest。
- `git diff --check`。
- Fresh code/QA/spec review。
- Commit/push後のfresh Ubuntu Provider CIとlatest-head Codex review。

## Out of Scope

- Production runtime、provider publisher、dogfood publisher。
- Shared test harness、global clock、public clock API。
- Production clockを含む`tests/cli_runtime/test_artifact_import_chatgpt_output.py`以外の全tracked file。
- F1追加修正。F1はUbuntuでoperationally passed。
- F2 active symlink reconciliation、F3 staged replacement race。両方P2 deferを維持。
- PR merge。

## Implementation Result

- status: `implemented-locally`
- allowed change: `tests/cli_runtime/test_artifact_import_chatgpt_output.py` only。
- exact focused node: `tests/cli_runtime/test_artifact_import_chatgpt_output.py::TestArtifactImportChatGptOutput::test_existing_blank_chatgpt_output_slug_coexists_with_import`。
- forbidden change: 上記以外の全tracked file。Production clock、harness、global clockを含む。
- U2 worker implemented the deterministic copied-clock test-only repair in that exact one-file boundary.
- Focused node repeated 20/20 pass; related regression 68 passed / 5 skipped.
- `make lint` PASS; `git diff --check` PASS.
- Fresh code review PASS (P0-P3=0); fresh QA conditional PASS (P0-P3=0).
- Full `uv run pytest` PASS: 2598 passed / 75 skipped / 2 warnings in 1629.67s.
- F1 is covered/completed by U1; F2/F3 remain deferred and nonblocking. F4 is implemented locally and remains pending terminal commit/push/latest-head CI/re-observation gates.

## Commit Evidence

- status: `pending-commit-push`
- expected scope: U2 test change + repair evidence Artifacts。
- local evidence: exact one-file test change only; commit and push are still pending。

## Re-observation Result

- status: `pending-new-head`
- required evidence: New-head Provider CI、Codex current-boundary review、required checks、review threads、mergeability、base drift。
- No new-head evidence exists yet; it must be collected after commit/push.

## Residual Risk / Follow-up

- F2 / F3はP2 deferを維持し、U2へ含めない。
- Required CIがfresh new headでpassするまでF4/U2はmerge-blocking。
- Duplicate same-head successはflake classification evidenceであり、required failureのpass evidenceではない。
