---
種別: 要件定義書（Issue）
ID: "iss-00304"
タイトル: "ChatGPT Authoring Skill"
関連GitHub: ["#304"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-08"
親: ["epic-00295", "init-local-00003"]
---

# iss-00304 ChatGPT Authoring Skill — Issue 要件定義

## 1. 目的

この Issue は、ChatGPT / Oracle を用いた高深度 authoring を SpecDock の installed skill surface に組み込み、既存の Initiative / Epic / Issue planning skills から安全に参照できる shared evidence lane を提供する。

新設する skill 名は `spec-dock-chatgpt-authoring` とする。これは human-facing に理解しやすく、既存 skill 名の `spec-dock-` prefix / scope-first naming と揃える。

この skill は canonical docs を直接採用しない。ChatGPT output、ZIP、draft、candidate、review / stage report はすべて evidence-only として扱い、scope planning skill と main orchestrator の採用判断、fresh `spec-reviewer` pass、Issue execution gate を置き換えない。

## 2. 背景

`epic-00295` では、ChatGPT 5.5 Pro Extended / Oracle を利用して、Requirement / Design / Plan / Issue draft を ZIP / tree artifact として生成し、SpecDock workflow に取り込む authoring pack runtime を整備している。

`iss-00296` から `iss-00303` までで、installed runtime の配置、`authoring` command skeleton、GitHub sync preflight、prompt pack、backend invocation adapter、ZIP review/staging、candidate validation、Issue draft adoption validation が実装された。

一方、ユーザーが実際に触れる entrypoint は skill である。既存の `spec-dock-initiative-planning` / `spec-dock-epic-planning` / `spec-dock-issue-planning` は、ChatGPT authoring evidence lane を前提にした naming、mode、stop gate、authority boundary をまだ明示していない。この Issue はその skill layer を整備する。

## 3. 親スコープから継承する境界

- Parent Initiative: `init-local-00003`
- Parent Epic: `epic-00295` `ChatGPT Authoring Pack Installed Runtime`
- Provider-side source of truth:
  - `src/spec_dock/assets/install_root/.agents/skills/`
- Dogfood workspace:
  - `spec-dock/` は validation / active docs surface であり、provider-side installed skill source ではない。
- ChatGPT-derived output は canonical authority ではない。
- Runtime validation pass は canonical adoption / reviewer pass / execution-ready / PR-ready を意味しない。
- 中間 Issue のため、この Issue では PR を作成しない。PR delivery は `iss-00307` に defer する。

## 4. Scope

### 4.1 In scope

- `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` を追加する。
- `spec-dock-chatgpt-authoring` の責務、使用条件、input / output evidence、forbidden claims、失敗時の扱いを定義する。
- 既存 planning skills の human-facing wording を更新し、ChatGPT authoring lane との関係を明示する。
  - `spec-dock-initiative-planning`
  - `spec-dock-epic-planning`
  - `spec-dock-issue-planning`
- `spec-dock-issue-planning` に次の 3 mode を明示する。
  - `zero-base`: Issue requirement / design / plan を対話・調査から作る。
  - `requirement-first`: 人間または Codex が作成した requirement を基に design / plan を作る。
  - `draft-adoption`: Epic planning / ChatGPT authoring pack から得た draft requirement / design / plan を正式版へ採用・再構成する。
- human-facing skill order を次の順に整理する。
  - Initiative planning
  - Epic planning
  - Issue planning
  - ChatGPT authoring evidence lane
- installed managed skill inventory / installer simulation / docs index の必要箇所を更新する。
- stop gate matrix を reviewer-readable evidence として残す。

### 4.2 Out of scope

- 既存 planning skill 名の破壊的 rename。
- `spec-dock-issue-planning` を複数 skill へ分割すること。
- ChatGPT output を canonical docs へ自動採用する `authoring adopt`。
- `.assurance.json` の自動 mutation。
- `authorized_profile` の自動決定。
- fresh `spec-reviewer` / `code-reviewer` / `qa-reviewer` pass の代替。
- execution-ready / PR-ready / merge-ready の自動 claim。
- backend invocation adapter / ZIP review / candidate validation runtime の再設計。
- この Issue での PR 作成。

### 4.3 Unchanged

- Existing planning skill names remain the primary user-facing entrypoints.
- `spec-dock-hub` remains the routing / invariant surface.
- `spec-dock-issue-execution` remains responsible for execution after reviewer-gated planning artifacts exist.
- `spec-dock-chatgpt-authoring` is supplemental evidence production and packaging guidance, not scope ownership.

## 5. Actors / Triggers

| Actor / trigger | Expected behavior |
|---|---|
| Human user asks to use ChatGPT / Oracle for SpecDock authoring | Route to `spec-dock-chatgpt-authoring` as evidence lane, then return to the relevant planning skill for canonical adoption. |
| Initiative planning needs Epic candidates | Initiative planning may use ChatGPT authoring pack evidence, but human approval before Epic node creation remains a stop gate. |
| Epic planning needs Issue drafts | Epic planning may use ChatGPT authoring pack ZIP/tree output for Issue draft artifacts, but Issue creation approval remains explicit. |
| Issue planning starts from existing drafts | `spec-dock-issue-planning` uses `draft-adoption` mode and records adoption / rejection in `report.md`. |
| GitHub branch cannot be synced | ChatGPT authoring lane may allow explicit `local-context` evidence mode, but outputs must be labeled lower-confidence and cannot claim GitHub-synced evidence. |

## 6. Required Behavior

### BH-001: new skill is installed and discoverable

`spec-dock init` / `spec-dock update` must install `spec-dock-chatgpt-authoring/SKILL.md` into consumer repositories as a managed skill under `.agents/skills/`.

### BH-002: naming remains stable and human-friendly

All user-facing SpecDock skills touched by this Issue must keep the `spec-dock-` prefix. Existing planning skill names must remain unchanged unless a later dedicated migration Issue explicitly changes them.

### BH-003: ChatGPT authoring is evidence lane only

`spec-dock-chatgpt-authoring` must clearly state that it produces or coordinates evidence such as prompt packs, invocation summaries, ZIP outputs, staged trees, candidate reports, and draft artifacts. It must not claim canonical adoption, reviewer pass, execution readiness, PR readiness, Issue finish, Epic completion, or mergeability.

### BH-004: planning skills retain canonical authority

`spec-dock-initiative-planning`, `spec-dock-epic-planning`, and `spec-dock-issue-planning` must state that canonical Requirement / Design / Plan documents are adopted by the planning workflow and reviewer-gated there. ChatGPT output is source evidence until adopted.

### BH-005: Issue planning modes are explicit

`spec-dock-issue-planning` must describe `zero-base`, `requirement-first`, and `draft-adoption` as distinct modes with different starting evidence and stop gates. `draft-adoption` must require `report.md` Evidence Adoption Ledger entries and fresh reviewer pass before execution.

### BH-006: stop gates are visible

The touched skill docs must preserve or add stop conditions for:

- missing active scope
- stale / missing GitHub sync evidence when synced evidence is required
- unreviewed or unsafe ChatGPT output
- missing human approval before node creation
- draft-only Issue docs
- missing fresh reviewer pass
- forbidden authority claims

### BH-007: local wrapper path is not product dependency

The skill docs may mention configurable backend invocation conceptually, but must not hardcode the user-specific local wrapper path as a formal SpecDock workflow dependency. Local `oracle-chatgpt` remains an operator-configurable backend example outside shipped workflow authority.

## 7. Acceptance Criteria

- AC-001: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-chatgpt-authoring/SKILL.md` exists and has a valid skill header.
- AC-002: `spec-dock-chatgpt-authoring` is installed by `spec-dock init/update` into a target repository through the existing install_root mechanism.
- AC-003: Existing planning skill names remain unchanged.
- AC-004: `spec-dock-issue-planning/SKILL.md` explicitly describes `zero-base`, `requirement-first`, and `draft-adoption` modes.
- AC-005: Planning skill docs describe ChatGPT output as evidence-only and route canonical adoption back to planning + `report.md` + fresh `spec-reviewer`.
- AC-006: The new ChatGPT authoring skill lists forbidden authority claims: canonical adoption, `.assurance.json` mutation, authorized profile decision, reviewer pass, execution-ready, PR-ready, merge-ready, Issue finish, Epic completion, PR delivery.
- AC-007: A reviewer-readable stop gate / responsibility matrix exists in the skill docs or Issue report evidence.
- AC-008: Installer / managed skill inventory tests or install simulation prove the new skill is shipped.
- AC-009: Local wrapper scan finds no hardcoded personal ChatGPT wrapper path in shipped installed assets / tests touched by this Issue.
- AC-010: `spec-dock validate`, `assurance verify`, and `git diff --check` pass before issue finish.
- AC-011: This intermediate Issue records no-per-Issue-PR rationale and defers PR delivery to `iss-00307`.

## 8. Non-Functional Requirements

- Skill docs must be short operational kernels, not long generated runbooks.
- Wording must be stable, human-friendly, and suitable for installed consumer repos.
- The new skill must avoid private machine assumptions, secrets, account state, browser profile details, and local absolute paths.
- Changes should be limited to installed skill assets, docs index / install inventory if required, tests, dogfood mirror inspection if needed, and Issue evidence.
- The implementation should preserve layered provider/dogfood boundaries.

## 9. Grade

Authorized profile: `standard`

Rationale: this Issue changes shipped installed workflow guidance and skill discovery surface. It is mostly documentation / installed asset work, but it affects public workflow contracts and therefore requires Standard reviewer gates.

## 10. Dependencies

- `iss-00297` authoring command skeleton is already implemented.
- `iss-00298` / `iss-00299` / `iss-00300` define sync, pack, and backend invocation concepts.
- `iss-00301` / `iss-00302` / `iss-00303` define ZIP review, candidate validation, and draft adoption evidence boundaries.
- Final PR delivery remains delegated to `iss-00307`.

## 11. Open Questions / Uncertainty

- Whether `spec-dock/docs/README.md` or workflow docs need a small index update is implementation-time inspection. Broad workflow guidance is planned for `iss-00306`; this Issue should only update index text needed for discoverability.
- ChatGPT Use planning was attempted for this Issue but browser automation ended before a result could be captured. The canonical docs therefore adopt Issue-local drafts and repo inspection evidence, not ChatGPT result claims.
