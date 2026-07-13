---
種別: disc
ID: "20260713t082242z-disc"
タイトル: "PR Repair Unit U003 Default Manifest Infra Coverage"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-13"
親: ["iss-00314"]
関連: ["20260713t064556z-pr-repair-batch", "PR #321", "comments 3568618494, 3568746654, 3568987959"]
authority: "proposed"
derived_from: ["R004", "R007", "R011"]
reflected_to: ["report.md"]
---

# PR Repair Unit U003 Default Manifest Infra Coverage

- source_batch: `20260713t064556z-pr-repair-batch-pr-repair-batch.md`
- unit_id: U003
- root_cause_family: `source-manifest-coverage`
- covered_ids: R004, R007, R011
- source_links: PR review comments 3568618494, 3568746654, 3568987959
- failure_class: `review_feedback:source-manifest-coverage`
- decided_priority: `P1`
- merge_blocking: yes
- disposition: `fix-now`

## Validity Analysis

Valid. The default preflight executes `infra/authoring_pack/git_fetch.py` and `preflight_receipt_writer.py`, but empty `source_paths` uses `DEFAULT_SOURCE_PATHS` that omits these modules. Their changes are invisible to default `source_manifest_hash`, stale-if, and pack binding.

## Need-To-Fix Decision

Fix now. The default workflow's durable provenance must cover code that performs the fetch and publication.

## Root Cause

`DEFAULT_SOURCE_PATHS` predates the new infra modules and was not expanded when the runtime dependency graph changed.

## Options Considered

- Add the two exact infra module paths: selected; minimal and deterministic.
- Add the whole infra directory: rejected because it may over-broaden provenance to unrelated modules.
- Require explicit source paths: rejected because default workflow is a required contract.

## Recommended Design

Add the provider-runtime-relative paths for `git_fetch.py` and `preflight_receipt_writer.py` to the default source path tuple in stable order. Mirror the provider asset to dogfood. Test that default manifests include both paths and change hash when either file changes, while explicit paths retain existing semantics.

## Implementation Plan

1. Add red-first default manifest coverage/hash sensitivity tests.
2. Add the two exact paths to `DEFAULT_SOURCE_PATHS`.
3. Sync provider/dogfood source manifest modules if needed.
4. Verify preflight/pack, install parity, format/lint/mypy, provider/dogfood parity.

## Validation Plan

- default manifest contains both infra paths
- changing either infra file changes default manifest hash
- explicit source path tests remain green
- preflight/pack and isolated install tests pass
- Ruff format/lint, mypy, diff-check pass

## Out of Scope

P2 platform/Windows findings, generic directory discovery, classifier changes, and other default manifest expansion.

## Implementation Result

Default source tupleへ2 exact infra pathsを追加し、4 provider/dogfood targetsのinclusion/hash sensitivityとexplicit-path非展開を固定した。isolated init/update parityを拡張し、fresh code-reviewer PASS。

## Commit Evidence

`ca341959a1cbac04ebc1f33247ba2431bbde4d93`。focused 7、authoring unit 62、CLI 5、make lint、parity、diff pass。

## Re-observation Result

new head push後に実行する。

## Residual Risk / Follow-up

Low after hash-sensitivity and installed parity evidence.
