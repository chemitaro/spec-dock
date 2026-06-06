---
種別: 計画書（Epic）
ID: "epic-00158"
タイトル: "Agent Workflow PDCA Hardening"
関連GitHub: ["#158"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00158 Agent Workflow PDCA Hardening — 計画（Issue と実施順序）

## この計画で閉じる E-RQ / E-AC

| Requirement / AC | 計画上の閉じ方 | 完了証跡 |
|---|---|---|
| E-RQ-001 Context surface ownership | `Align Skill Docs Template Context Surfaces` と後続 docs/templates lane で横断整合を取る | Provider-side skills/docs/templates diff、矛盾チェック、dogfooding mirror inspection |
| E-RQ-002 First-read executable skill surface | 既存 `iss-00159` を specimen とし、後続 skill lanes へ展開する | Skill first-read smoke、non-pass wording inspection、doc routing inspection |
| E-RQ-003 Clarification skill-owned workflow | 専用 issue で ADR 01 を実装し、`workflow_clarification.md` は bridge を既定にする | `spec-dock-clarification/SKILL.md`、bridge/reference doc、interview/research/disc templates |
| E-RQ-004 Spec authoring gate visibility | issue planning、hub routing、workflow docs、templates で fresh reviewer / non-pass boundary を揃える | Targeted `rg`、Spec Authoring Gate、manual first-read smoke |
| E-RQ-005 Evidence and canonical authority boundary | issue planning、docs alignment、template alignment で EAL / delegated evidence を見える化する | Epic / Issue `report.md` EAL、Delegated Draft Evidence |
| E-RQ-006 First wave decomposition | ADR 02 の first-wave issue set を順序付きで採用し、guard / harness / runtime は deferred に分離する | この `plan.md` の issue list、dependency graph、report follow-up |
| E-RQ-007 Provider source / dogfooding mirror boundary | 各 issue readiness に provider source と mirror validation を必須化する | Provider source diff、mirror inspection、`validate` / `sync` evidence |
| E-AC-001 | Cross-surface ownership consistency を T2-T4 で閉じる | Surface inventory matrix と contradiction check |
| E-AC-002 | ADR 02 issue set を canonical plan に反映する | Issue list / tranche / dependencies |
| E-AC-003 | Clarification 専用 issue を持つ | Clarification skill first-read smoke |
| E-AC-004 | Reviewer gate wording を横断確認する | Non-pass wording and gate evidence check |
| E-AC-005 | Evidence adoption boundary を report へ残す | EAL entries and delegated draft evidence |
| E-AC-006 | Provider / mirror validation を各 shipped asset issue に要求する | `validate`, `sync`, targeted inspection |
| E-AC-007 | Requirement/design/plan gate record を残す | Epic `report.md` Spec Authoring Gate |

## 課題分割方針（Issue slicing policy）

- 分割原則:
  - Context surface responsibility と review boundary で切る。
  - Issue 内の実装 step / TDD cadence / commit rhythm は Issue `plan.md` に任せる。
  - 各 issue は少なくとも一つの E-RQ / E-AC と design decision に trace する。
  - Shipped asset 変更では provider-side source を authority とし、dogfooding mirror を validation target とする。
  - Templates は scaffold / evidence slot / example surface として扱い、compliance authority にしない。
  - Runtime guard / harness / regression checks は first-wave blocker にしない。
- 例外:
  - `Align Skill Docs Template Context Surfaces` が広すぎる場合は、skill family / docs / templates family へ分割する。
  - 逆に局所 issue が cross-surface contradiction を閉じられない場合は、横断 alignment lane へ吸収する。
  - `workflow_clarification.md` の full retirement は、link inventory と bridge risk が解消されるまで deferred にできる。

## 課題一覧（Issue list / 順序 / tranche 付き）

- `iss-00159 Make Issue Planning Skill Expose Mandatory Authoring Gates`:
  - 目的:
    - `spec-dock-issue-planning` を first-read executable な skill spine specimen にする。
  - 成果物:
    - Provider-side `spec-dock-issue-planning/SKILL.md` と dogfooding mirror の semantic identity。
    - Fresh reviewer / non-pass state / evidence adoption / unresolved gap return / docs routing wording。
  - tranche:
    - T1 specimen
  - closes:
    - E-RQ-002, E-RQ-004, E-RQ-005, E-RQ-007
    - E-AC-004, E-AC-005, E-AC-006, E-AC-007
  - 依存:
    - Requirement / design / plan reviewer gates for this Epic.
  - GitHub:
    - Existing issue: `#159`
- `Align Skill Docs Template Context Surfaces`:
  - 目的:
    - Skills / docs / templates の responsibility boundary を横断 inventory し、ADR と矛盾する surface を整理する。
  - 成果物:
    - Provider-side skill/docs/templates inventory。
    - Ownership contradiction matrix。
    - Priority cleanup diff for surfaces that obscure first-read workflow ownership。
  - tranche:
    - T2 inventory / consistency
  - closes:
    - E-RQ-001, E-RQ-006, E-RQ-007
    - E-AC-001, E-AC-002, E-AC-006
  - 依存:
    - `iss-00159` の specimen wording / dogfooding evidence。
  - GitHub:
    - To be created with ASCII title `Align Skill Docs Template Context Surfaces`.
- `Revise spec-dock-clarification as skill-owned grill workflow`:
  - 目的:
    - ADR 01 を実装し、`spec-dock-clarification` を source-grounded grill loop として skill-owned にする。
  - 成果物:
    - Provider-side `spec-dock-clarification/SKILL.md` rewrite。
    - `workflow_clarification.md` bridge/reference conversion。
    - `interview` / `research` / `disc` templates の scaffold/example alignment。
  - tranche:
    - T2 exception lane
  - closes:
    - E-RQ-003, E-RQ-004, E-RQ-005, E-RQ-007
    - E-AC-003, E-AC-004, E-AC-005, E-AC-006
  - 依存:
    - `Align Skill Docs Template Context Surfaces` の ownership inventory。
  - GitHub:
    - To be created with ASCII title `Revise Spec Dock Clarification As Skill Owned Grill Workflow`.
- `Clarify Hub And Leaf Skill Routing Surface`:
  - 目的:
    - Hub skill を router + global invariant とし、leaf skill が workflow spine を所有する構造へ誘導する。
  - 成果物:
    - Provider-side `spec-driven-tdd-workflow/SKILL.md` routing wording。
    - Clarification / issue planning / issue execution / epic planning leaf routing の整合。
  - tranche:
    - T3 routing
  - closes:
    - E-RQ-001, E-RQ-002, E-RQ-003, E-RQ-004
    - E-AC-001, E-AC-003, E-AC-004
  - 依存:
    - `iss-00159`
    - `Revise spec-dock-clarification as skill-owned grill workflow`
  - GitHub:
    - To be created with ASCII title `Clarify Hub And Leaf Skill Routing Surface`.
- `Align Workflow Docs With Skill Spine Boundary`:
  - 目的:
    - Docs が lifecycle / field semantics / hard cases を所有しつつ、skill が省略している hidden mandatory workflow を持たないように整理する。
  - 成果物:
    - `workflow_spec_authoring.md`, `workflow_clarification.md`, `workflow_issue.md`, phase docs, related references の boundary wording。
    - Docs から skill-owned spine へ戻る routing。
  - tranche:
    - T3 docs boundary
  - closes:
    - E-RQ-001, E-RQ-004, E-RQ-005
    - E-AC-001, E-AC-004, E-AC-005
  - 依存:
    - `iss-00159`
    - `Revise spec-dock-clarification as skill-owned grill workflow`
    - `Clarify Hub And Leaf Skill Routing Surface`
  - GitHub:
    - To be created with ASCII title `Align Workflow Docs With Skill Spine Boundary`.
- `Align Templates As Scaffolds And Examples`:
  - 目的:
    - Templates を scaffold / evidence slot / good example として揃え、compliance authority と誤読されないようにする。
  - 成果物:
    - Epic / Issue report evidence slots。
    - Discussion templates, especially `interview`, `research`, `disc`。
    - Template README / scaffold wording alignment。
  - tranche:
    - T4 templates
  - closes:
    - E-RQ-001, E-RQ-003, E-RQ-005
    - E-AC-001, E-AC-003, E-AC-005
  - 依存:
    - `Align Skill Docs Template Context Surfaces`
    - `Revise spec-dock-clarification as skill-owned grill workflow`
    - `Align Workflow Docs With Skill Spine Boundary`
  - GitHub:
    - To be created with ASCII title `Align Templates As Scaffolds And Examples`.

## 統合チェックポイント

- G1 分解レビュー:
  - `iss-00159` 完了後、skill spine pattern が docs over-copy になっていないか確認する。
  - `Align Skill Docs Template Context Surfaces` の scope が広すぎる場合はここで split する。
- G2 統合準備確認:
  - T2 終了時、clarification exception と general ownership model が矛盾していないか確認する。
  - Hub routing を始める前に、leaf skill の authority wording が stable であることを確認する。
- G3 ロールアウト / docs 影響:
  - T3 終了時、workflow docs と hub / leaf skills の source-of-truth wording が矛盾しないか確認する。
  - Templates alignment 前に、docs 側の artifact semantics が十分に残っているか確認する。
- G9 最終 Epic spec review:
  - 全 first-wave issue 完了後、Epic-wide diff / report ledgers / provider-mirror validation を共有証跡にまとめる。
  - Fresh `spec-reviewer` と必要に応じた deep-consultant review を、同じ shared evidence に対して実行する。

## 品質ゲート

- test / observability / migration / docs:
  - Content inspection:
    - Targeted `rg` で ownership wording、fresh reviewer pass、non-pass states、evidence adoption、provider/mirror boundary、template authority wording を確認する。
  - Provider / mirror verification:
    - Provider-side asset diff と dogfooding mirror inspection を各 issue report に残す。
    - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock sync` を実行する。
  - Manual first-read smoke:
    - Skill-owned workflow change では、skill 本文だけで next action / stop condition / reviewer gate / evidence obligation / next docs が読めるか確認する。
  - Report ledger audit:
    - EAL / Delegated Draft Evidence / Spec Authoring Gate に unresolved `blocked` / `stale` が残っていないこと。
  - Regression / harness:
    - First wave では必須にしない。M5 以降の deferred PDCA work とする。

## ロールアウト / ドキュメント影響

- ロールアウト順序:
  - T1: Issue planning skill specimen。
  - T2: Ownership inventory and clarification exception。
  - T3: Hub routing and workflow docs。
  - T4: Templates。
  - Later: regression checks / manual harness / runtime gate。
- 契約 / docs 更新:
  - Provider-side docs impact:
    - `src/spec_dock/assets/spec_dock/docs/`
  - Provider-side templates impact:
    - `src/spec_dock/assets/spec_dock/templates/`
  - Installed agent-tooling assets impact:
    - `src/spec_dock/assets/install_root/.agents/skills/`
  - Dogfooding verification:
    - `.agents/`, `spec-dock/`, `spec-dock/.agent/*`
- Deferred work / revisit conditions:
  - `Add Skill Spine Regression Checks`:
    - Revisit after T4 when cleaned surfaces define stable expected wording / structure.
  - `Add Manual Workflow Scenario Harness`:
    - Revisit after at least two representative skill workflows have stable first-read smoke criteria.
  - Runtime gate / `gate status` / issue start-finish guards:
    - Revisit after authoring contract has machine-checkable signals and report ledger conventions are stable.
  - Full retirement of `workflow_clarification.md`:
    - Revisit after link inventory shows bridge behavior is no longer needed.

## 課題準備完了条件（Issue readiness criteria）

- Issue に要求する最低条件:
  - Parent Epic requirement / design / plan への trace がある。
  - Scope / non-scope が runtime guard / harness / templates authority などの deferred work と混線していない。
  - Provider-side source path と dogfooding mirror validation path が明記されている。
  - Fresh `spec-reviewer` gates が issue requirement / design / plan に記録されている。
  - Shipped asset 変更では rollback / compatibility / docs impact が記録されている。
  - Delegated / external evidence を使う場合、EAL と Delegated Draft Evidence が report に残る。
  - Execution handoff 前に unresolved requirement / design / plan gap がない。

## 最終完了条件

- E-AC 完了:
  - E-RQ / E-AC closure matrix が Epic `report.md` または final evidence に更新されている。
  - First-wave issue lanes が完了、または non-blocking rationale と revisit condition 付きで deferred されている。
- 統合 / ロールアウト完了:
  - Provider-side source と dogfooding mirror validation が全 shipped asset change について記録されている。
  - `validate` / `sync` evidence が記録されている、または該当しない理由が明記されている。
  - Epic-wide pre-PR gate に従い、base/head endpoint、`git diff --stat`、`git diff --name-status`、shared evidence を残す。
- docs 影響解決:
  - Skills / docs / templates の authority boundary に矛盾が残っていない。
  - `workflow_clarification.md` bridge / retirement 状態が記録されている。
  - Deferred work list が revisit condition を持つ。

## 依存 / ブロッカー

- D-001:
  - `iss-00159` の outcome が横断 cleanup の語彙と smoke criteria の specimen になる。
- D-002:
  - Clarification issue は general ownership inventory と ADR 01 の両方に依存する。
- D-003:
  - Hub routing は leaf skill surface が安定してから更新する。
- D-004:
  - Templates は skill/docs boundary が見えてから scaffold/example を整える。
- D-005:
  - Regression / harness / runtime gate は first-wave cleaned surfaces が stable expected behavior を持つまで開始しない。

## 未確定事項

- Blocking question:
  - なし。
- Non-blocking plan defaults:
  - `Align Skill Docs Template Context Surfaces` はまず一つの inventory / first-cleanup issue とし、review scope が広すぎる場合に split する。
  - `workflow_clarification.md` は first wave では bridge/reference を既定とし、full retirement は link inventory 後に判断する。
  - Manual smoke は skill-owned workflow 変更 issue では必須に近い検証とし、full harness は deferred にする。
