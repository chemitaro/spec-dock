---
種別: 要件定義書（Issue）
ID: "iss-00303"
タイトル: "Issue Draft Adoption Validation"
関連GitHub: ["#303"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295", "init-local-00003"]
---

# C08 Issue draft adoption と selected skeleton validation contracts を実装する — draft requirement

## Purpose

Issue node 作成後に、ChatGPT draft pack を canonical Issue docs へ採否判断するための input integrity を検証する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `authoring validate issue-draft-adoption` を実装する。
- `authoring validate selected-skeleton-fill` を実装または runtime 化する。
- Issue node exists、parent trace、draft pack digest、draft-to-canonical target mapping を検査する。
- selected profile、template hash、section inventory、missing/extra section diagnostics を検査する。
- `.assurance.json` は observation-only とし、mutation を拒否する。
- fresh reviewer pass 前に execution-ready を主張しない。

## Non-scope

- canonical docs の再記述そのもの。
- fresh reviewer pass の発行。
- `.assurance.json` mutation。
- Issue execution implementation。

## Requirements

- draft adoption input は Issue node 作成後にだけ使う。
- draft pack は canonical Issue docs ではなく adoption candidate として扱う。
- selected skeleton mismatch、profile mismatch、stale template hash は block/stale/rejected diagnostics になる。
- execution-ready claim は forbidden claim として拒否する。
- EAL disposition が canonical adoption の前提になる。

## Acceptance criteria

- issue draft adoption positive fixture が pass し、canonical target mapping を出力する。
- selected skeleton fill positive fixture が section inventory を検証する。
- missing/extra section、stale template hash、profile mismatch negative fixtures が検出される。
- `.assurance.json` mutation claim fixture が rejected になる。
- execution-ready self-claim が rejected になる。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）
