---
種別: "Issue draft requirement"
ID: "epic-00295-01"
Issue候補: "C01"
タイトル: "authoring pack assets を provider-side installed layout へ昇格する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: []
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C01 authoring pack assets を provider-side installed layout へ昇格する — draft requirement

## Purpose

dogfood helper として存在してきた authoring-pack assets を provider-side source of truth へ移し、consumer repository へ `spec-dock init/update` で配布できる配置へ整理する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `scripts/authoring-pack/` 相当の helper を provider asset 配下へ移設する。
- `spec_dock_runtime/application/authoring_pack/` と `domain/authoring_pack/` の初期 module boundary を作る。
- fixtures / manual test reference が provider-side assets を参照するように整理する。
- 旧 dogfood helper surface は standalone / compatibility surface として位置づけ、source of truth ではないことを文書化する。

## Non-scope

- `authoring` CLI の完全実装。
- GitHub sync preflight、backend invocation、ZIP review/stage の詳細実装。
- installed skill docs の改訂。
- PR delivery。

## Requirements

- provider-side source of truth は `src/spec_dock/assets/...` 配下に置く。
- dogfood workspace と shipped runtime asset を混同しない。
- 移設により canonical docs や `.assurance.json` を直接変更しない。
- 移設後の file inventory と compatibility note を finish evidence として残す。

## Acceptance criteria

- provider-side asset path に authoring-pack helper の正本候補が存在する。
- 旧 helper との互換 surface または廃止方針が明記されている。
- asset path を対象にした最低限の import / fixture / path resolution test が通る。
- 中間 Issue として PR delivery を行わず、Issue 12 へ defer する evidence が残る。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）
