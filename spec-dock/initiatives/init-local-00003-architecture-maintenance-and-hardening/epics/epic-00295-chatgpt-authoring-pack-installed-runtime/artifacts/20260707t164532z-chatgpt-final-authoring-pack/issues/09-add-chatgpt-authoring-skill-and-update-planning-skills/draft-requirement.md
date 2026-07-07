---
種別: "Issue draft requirement"
ID: "epic-00295-09"
Issue候補: "C09"
タイトル: "`spec-dock-chatgpt-authoring` skill を追加し既存 planning skills を更新する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["02-add-authoring-command-skeleton"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C09 `spec-dock-chatgpt-authoring` skill を追加し既存 planning skills を更新する — draft requirement

## Purpose

human-facing skill taxonomy、names、ordering、modes、stop gates を installed skill docs と managed skill list に反映する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `spec-dock-chatgpt-authoring/SKILL.md` を追加する。
- `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` の wording を更新する。
- `spec-dock-issue-planning` は `zero-base` / `requirement-first` / `draft-adoption` modes を持つ。
- human-facing order を Initiative -> Epic -> Issue -> ChatGPT evidence lane として明示する。
- installer managed skill list と host-adapter metadata を必要に応じて更新する。

## Non-scope

- planning skill 名の破壊的 rename。
- Issue planning を複数 skill へ分割すること。
- runtime command の詳細実装。
- canonical adoption や reviewer pass を ChatGPT skill が行うこと。

## Requirements

- user-visible skill names は `spec-dock-` prefix を持つ。
- 既存 planning skill names は可能な限り維持する。
- `spec-dock-chatgpt-authoring` は shared evidence lane であり、scope planning skill の代替ではない。
- stop gate と forbidden authority claims を各 skill に明示する。
- installed managed skill として `spec-dock update/init` 後に存在する。

## Acceptance criteria

- `spec-dock-chatgpt-authoring` が installed managed skill として存在する。
- 既存 planning skill names が維持されている。
- Issue planning modes が docs に明示されている。
- stop gate matrix が Initiative/Epic/Issue/ChatGPT lane の責務差分を示す。
- skill install simulation または inventory test が通る。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）
