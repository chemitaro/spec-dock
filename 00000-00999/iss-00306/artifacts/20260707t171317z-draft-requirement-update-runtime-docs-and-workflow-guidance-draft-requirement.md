---
種別: 要件定義書（Issue）
ID: "iss-00306"
タイトル: "Runtime Workflow Guidance"
関連GitHub: ["#306"]
状態: "draft | approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
親: ["epic-00295", "init-local-00003"]
---

# C11 runtime docs / reference docs / workflow guidance を更新する — draft requirement

## Purpose

installed runtime command、skill taxonomy、evidence modes、deferred command boundary、relay PR delivery policy を user-facing docs に反映する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- ChatGPT authoring pack workflow docs を追加・更新する。
- backend reference、safe ZIP handling、candidate validation、approval gate、local-context mode を文書化する。
- Initiative/Epic/Issue workflow docs に skill ordering と stop gate を反映する。
- deferred commands を利用可能と誤読させない wording にする。
- manual fallback と `local-context` の adoption limitation を明示する。

## Non-scope

- 新しい runtime behavior の追加。
- deferred command の実装。
- automatic issue creation / PR readiness automation。
- per-Issue PR delivery for intermediate Issues。

## Requirements

- docs は installed runtime / skill surface と一致する。
- `github-synced` default と `local-context` explicit mode の authority 差分を説明する。
- `authoring adopt` 等の deferred commands は初期 scope 外と明記する。
- 中間 Issue no-PR relay と final Issue PR delivery を workflow guidance に含める。
- docs は secret/raw transcript/host-local path の保存を促さない。

## Acceptance criteria

- docs trace matrix が requirement / design / plan / runtime / skill に対応する。
- command examples が supported command に限定されている。
- deferred command warning が明確である。
- `git diff --check` が通る。
- docs / skills / runtime help の terminology が一致する。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）
