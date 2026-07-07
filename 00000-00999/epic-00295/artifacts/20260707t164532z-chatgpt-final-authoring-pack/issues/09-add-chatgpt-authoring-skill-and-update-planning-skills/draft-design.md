---
種別: "Issue draft design"
ID: "epic-00295-09"
Issue候補: "C09"
タイトル: "`spec-dock-chatgpt-authoring` skill を追加し既存 planning skills を更新する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["draft-requirement.md"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C09 `spec-dock-chatgpt-authoring` skill を追加し既存 planning skills を更新する — draft design

## Scope boundary

This Issue owns only the slice described below. It must not expand into deferred commands or final PR delivery unless this is Issue 12.

- `spec-dock-chatgpt-authoring/SKILL.md` を追加する。
- `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` の wording を更新する。
- `spec-dock-issue-planning` は `zero-base` / `requirement-first` / `draft-adoption` modes を持つ。
- human-facing order を Initiative -> Epic -> Issue -> ChatGPT evidence lane として明示する。
- installer managed skill list と host-adapter metadata を必要に応じて更新する。

## Target provider-side paths

- src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md
- src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md
- src/spec_dock/cli.py or managed skill list equivalent

## Runtime / docs / skill impact

- Runtime: managed skill install verification を追加する可能性がある。
- Docs: skill taxonomy と stop gates の source になる。
- Skill: new shared evidence lane skill を追加し、planning skills の役割を整理する。

## Design notes

- Keep provider-side source of truth under `src/spec_dock/assets/...` where applicable.
- Runtime commands must return deterministic status and diagnostics.
- Evidence-only artifacts must preserve `authority: evidence_only`, `adoption_status: unreviewed`, and `bundle_generation_not_promotion: true`.
- Validators and staging commands must not write canonical docs or `.assurance.json`.
- `github-synced` and `local-context` evidence must be distinguishable in provenance when this Issue touches authoring flow.
- User-facing skill names must retain the `spec-dock-` prefix when this Issue touches skills or docs.

## Failure modes

- 新 skill が planning skill の代替として canonical adoption を主張する。
- Issue planning を早すぎる段階で skill 分割する。
- managed skill list に追加されず installed repo に現れない。
- old skill names を変更してユーザー導線を壊す。

## Tests / validation impact

- managed skill inventory test
- skill file presence test
- update/init install simulation
- stop gate wording snapshot
- user-facing name table check

## Adoption boundary

This draft design is suitable as input to `spec-dock-issue-planning` `draft-adoption`, but it is not canonical design until Codex rewrites/adopts the selected claims and obtains the required reviewer evidence.
