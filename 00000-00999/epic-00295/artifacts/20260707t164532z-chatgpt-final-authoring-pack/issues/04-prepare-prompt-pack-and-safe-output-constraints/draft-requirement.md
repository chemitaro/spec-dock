---
種別: "Issue draft requirement"
ID: "epic-00295-04"
Issue候補: "C04"
タイトル: "prompt pack prepare と safe output constraints を実装する"
親Epic: "epic-00295"
状態: "draft-adoption-candidate"
作成者: "ChatGPT"
最終更新: "2026-07-07"
依存: ["03-implement-github-sync-preflight"]
authority: "evidence_only"
adoption_status: "unreviewed"
bundle_generation_not_promotion: true
---

# C04 prompt pack prepare と safe output constraints を実装する — draft requirement

## Purpose

preflight evidence から ChatGPT に渡す prompt pack を deterministic に生成し、禁止 claim と ZIP output contract を明示する。

## Parent Epic trace

- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Repository: `chemitaro/spec-dock`
- Branch: `codex/authoring-pack-installed-runtime`
- Epic path: `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00295-chatgpt-authoring-pack-installed-runtime/`
- Trace requirement groups: skill taxonomy、runtime command surface、GitHub sync/evidence mode、ZIP safety、candidate validation、approval boundary、relay delivery。
- Authority: this draft is evidence-only and is not canonical Issue docs until adopted through `spec-dock-issue-planning` `draft-adoption` mode.

## Scope

- `authoring pack prepare` use case を実装する。
- source-manifest、stale-if、safe-output-constraints、mode-specific prompt config を生成する。
- forbidden authority claims を prompt と validator contract に埋め込む。
- Initiative/Epic/Issue/selected-skeleton の mode selection を扱う。
- `local-context` prompt pack では provided context と unsynced reason を明記する。

## Non-scope

- backend process 実行。
- ZIP central directory review / extraction。
- candidate adoption や canonical rewrite。
- secret/raw transcript の durable 保存。

## Requirements

- prompt pack は同じ input から同じ output tree を生成する。
- authority fields は `evidence_only` / `unreviewed` / `bundle_generation_not_promotion: true` を要求する。
- ZIP root は `specdock-authoring-pack/` を要求する。
- canonical adoption、`.assurance.json` mutation、authorized profile、reviewer pass、execution-ready、PR-ready の claim を禁止する。
- secret-looking data、raw transcript、host-local absolute path を保存契約に入れない。

## Acceptance criteria

- prompt pack tree sample が生成される。
- `manifest.json` / `source-manifest.json` / `stale-if.json` / `safe-output-constraints.md` の例が tests で検証される。
- `local-context` sample に unsynced reason、provided context paths、adoption limitation が含まれる。
- broad `--force` bypass を示唆しない。

## Evidence expectations

- Implementation or doc changes must produce a machine-readable or reviewer-readable finish evidence bundle.
- Evidence must keep `authority: evidence_only` for ChatGPT-derived draft/stage outputs.
- Forbidden authority claims must be absent: canonical adoption、`.assurance.json` mutation、authorized profile、fresh reviewer pass、execution-ready、PR-ready。
- Verification output must distinguish validation pass from adoption/reviewer pass.
- この Issue は中間 Issue であり、PR delivery を行わず Issue 12 へ defer する。

## Suggested grade

- Suggested grade: implementation-slice（中間 Issue、PR delivery defer）
