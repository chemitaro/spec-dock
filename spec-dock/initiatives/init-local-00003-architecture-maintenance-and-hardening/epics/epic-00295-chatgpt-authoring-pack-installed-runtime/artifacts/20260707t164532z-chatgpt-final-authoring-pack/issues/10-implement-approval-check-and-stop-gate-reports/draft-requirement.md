---
種別: "Issue draft requirement"
ID: "epic-00295-10"
Issue候補: "C10"
タイトル: "approval check と stop-gate evidence reports を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["07-validate-initiative-epic-and-epic-issue-candidates"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C10 approval check と stop-gate evidence reports を実装する — draft requirement

## Purpose

Epic/Issue node creation 前の explicit human approval を machine-checkable evidence として扱い、自動 node creation を初期 scope から除外する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `authoring approval check` を実装する。
- approval evidence schema を定義する。
- requested scope、effective scope、candidate pack digest、approver、timestamp、approval statement を検査する。
- missing approval、stale digest、scope mismatch を block する。
- unsupported auto-creation diagnostics を出す。

## Non-scope

- Epic/Issue node creation command の追加。
- `authoring create-issues-from-zip` の追加。
- human approval を ChatGPT output で代替すること。
- execution-ready / PR-ready gate。

## Requirements

- node creation 前の approval は explicit evidence がない限り blocked とする。
- approval は Issue slicing / node creation decision の承認であり、draft pack execution-ready ではない。
- approval check は approval state を読むだけで node を作らない。
- candidate digest が変わった場合は stale/block とする。
- report は human-readable と machine-readable の両方を持つ。

## Acceptance criteria

- approval pass fixture が expected report を返す。
- missing approval fixture が blocked になる。
- stale candidate digest fixture が blocked/stale になる。
- scope mismatch fixture が blocked になる。
- auto-creation command がない、または unsupported/deferred として fail-closed する。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）
