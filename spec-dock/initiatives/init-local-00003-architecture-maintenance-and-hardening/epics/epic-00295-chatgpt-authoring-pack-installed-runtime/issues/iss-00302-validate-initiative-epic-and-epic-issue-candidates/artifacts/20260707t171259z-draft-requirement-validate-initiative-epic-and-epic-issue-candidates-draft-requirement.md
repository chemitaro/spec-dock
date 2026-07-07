---
種別: 要件定義書（Issue）
ID: "iss-00302"
タイトル: "Initiative Epic Validation"
関連GitHub: ["#302"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295", "init-local-00003"]
---

# C07 Initiative/Epic と Epic/Issue 候補 validators を実装する — draft requirement

## Purpose

ChatGPT batch planning output を node creation 前の candidate-only evidence として検証し、重複・境界・権限 claim の誤りを検出する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `authoring validate initiative-epic-candidates` を実装する。
- `authoring validate epic-issue-candidates` を実装する。
- parent trace、scope/non-scope、dependencies、duplicate/overlap diagnostics を検査する。
- per-candidate draft requirement/design/plan の存在と target mapping を検査する。
- profile recommendation は advisory-only とし、`authorized_profile` claim を拒否する。

## Non-scope

- Epic/Issue node creation。
- human approval check の final decision。
- Issue draft adoption after node creation。
- PR delivery。

## Requirements

- candidate validator は node creation readiness を直接主張しない。
- Issue Decomposition Approval Gate は human explicit approval 前で停止する。
- candidate pack は `authority: evidence_only` / `adoption_status: unreviewed` を維持する。
- duplicate / overlap / parent mismatch は diagnostics として出す。
- profile authority claim は forbidden claim として reject する。

## Acceptance criteria

- Initiative -> Epic candidate fixture が parent trace と candidate docs を検証できる。
- Epic -> Issue candidate fixture が issue list、dependencies、draft packs を検証できる。
- duplicate/overlap negative fixture が fail/rejected diagnostics を出す。
- `authorized_profile` claim fixture が rejected になる。
- human approval before node creation が validator output で明示される。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）
