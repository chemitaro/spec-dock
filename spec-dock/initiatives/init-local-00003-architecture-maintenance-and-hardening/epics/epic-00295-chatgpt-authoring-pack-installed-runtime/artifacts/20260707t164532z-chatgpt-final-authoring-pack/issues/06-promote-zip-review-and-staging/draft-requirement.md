---
種別: "Issue draft requirement"
ID: "epic-00295-06"
Issue候補: "C06"
タイトル: "ZIP/tree review と staging を runtime command へ昇格する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["04-prepare-prompt-pack-and-safe-output-constraints"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C06 ZIP/tree review と staging を runtime command へ昇格する — draft requirement

## Purpose

ChatGPT output ZIP/tree を canonical docs に触れずに安全検査し、staged evidence と EAL candidate を生成する runtime command として提供する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `authoring pack review` と `authoring pack stage` を実装する。
- ZIP central directory を safe extraction 前に検査する。
- required metadata、root、source hashes、stale-if、forbidden authority claims を検査する。
- unsafe entry、secret-looking content、raw transcript、nested archive、binary、symlink 等を reject する。
- stage report、dry-run diff、EAL candidates、ownership marker を生成する。

## Non-scope

- canonical docs への採用。
- Issue/Epic node creation。
- `authoring adopt` command。
- ZIP durable repository storage contract の最終化。

## Requirements

- ZIP は review pass 前に展開しない。
- valid pack でも adoption_status は `unreviewed` のまま staged evidence として扱う。
- tree fallback は ZIP central directory evidence を欠くため fallback evidence として分類する。
- canonical docs を直接上書きしない。
- forbidden authority claim は `rejected` とする。

## Acceptance criteria

- valid ZIP fixture が review pass / stage evidence を生成する。
- path traversal、absolute path、hidden path、secret、raw transcript、nested archive、binary、symlink、unsupported suffix、encrypted entry、wrong root、metadata missing、source hash mismatch、forbidden claim fixtures が拒否される。
- stage output に EAL candidate と dry-run diff が含まれる。
- canonical docs unchanged evidence が残る。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）
