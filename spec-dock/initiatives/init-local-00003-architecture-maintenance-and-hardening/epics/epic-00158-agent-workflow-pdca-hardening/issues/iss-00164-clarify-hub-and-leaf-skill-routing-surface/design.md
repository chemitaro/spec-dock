---
種別: 設計書（Issue）
ID: "iss-00164"
タイトル: "Clarify Hub And Leaf Skill Routing Surface"
関連GitHub: ["#164"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00164 Clarify Hub And Leaf Skill Routing Surface — 設計

## 目的・制約

- 目的:
  - `spec-driven-tdd-workflow` hub skill を、SpecDock work の entrypoint / route selector / cross-cutting invariant surface として読める状態にする。
  - Leaf skills が task-specific first-read workflow spine を所有し、hub は leaf detail を複製しない境界を固定する。
- 必須:
  - Requirement AC-001 の route matrix が hub skill の first-read surface で検証できる。
  - Global invariants は fresh reviewer pass、non-pass state、canonical ownership、evidence adoption、provider/mirror境界に絞る。
  - `spec-dock-clarification` への route は skill-owned clarification workflow として明示する。
- 禁止:
  - Leaf skill の詳細 workflow を hub にコピーしない。
  - Leaf skill rewrite をこの issue へ吸収しない。
  - Runtime gate / validation logic / workflow docs / templates を変更しない。

## 既存実装 / 規約の理解

- 参照した実装 / docs:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `.agents/skills/spec-driven-tdd-workflow/SKILL.md`
  - `spec-dock/active/issue/requirement.md`
  - `spec-dock/active/epic/requirement.md`
  - `spec-dock/active/epic/design.md`
  - `iss-00163` completed report evidence
- 現状理解:
  - Hub はすでに route table と global reminders を持つ。
  - 先行 issue の結果として、`spec-dock-clarification` と `workflow_clarification.md` の境界は skill-owned workflow + bridge/reference doc に寄っている。
  - Hub はこの境界を routing layer として反映し、leaf-owned detail を増やさない。
- 採用するパターン:
  - Provider source を編集し、dogfooding mirror を byte-equivalent に保つ。
  - Docs-only / skill-text-only inspection と targeted `rg` / `cmp` で閉じる。
- 採用しないもの:
  - Leaf skill internal rewrite。
  - Runtime enforcement。
  - Workflow docs / templates の同時整理。

## 採用方針 / トレードオフ

- 論点:
  - Hub にどれだけの workflow を残すか。
- 決定:
  - Hub には route selection、surface ownership、cross-cutting invariant、direct references だけを置く。
  - Leaf skill の具体手順は leaf skill 側の first-read spine に置き、hub では route 先と handoff condition だけを説明する。
- 理由:
  - Hub が薄すぎると route が不安定になるが、厚すぎると leaf workflow spine と重複して drift する。
  - Requirement の route matrix と global invariant を hub に残すと、entrypoint としての有用性を保ちつつ scope creep を避けられる。

## データ境界 / ファイル変更計画

```text
src/spec_dock/assets/install_root/.agents/skills/
`-- spec-driven-tdd-workflow/
    `-- SKILL.md  # 変更: provider hub skill source of truth

.agents/skills/
`-- spec-driven-tdd-workflow/
    `-- SKILL.md  # 変更: dogfooding mirror parity
```

- 変更しない:
  - Leaf skill files。
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - runtime / tests except existing parity smoke if needed。

## Route Matrix Contract

| Task type / cue | Route target | Hub responsibility | Leaf responsibility |
|---|---|---|---|
| Initiative requirement/design/plan planning | `spec-dock-initiative-planning` | route selection and phase gate invariant | initiative planning workflow spine |
| Epic requirement/design/plan planning | `spec-dock-epic-planning` | route selection and phase gate invariant | epic planning workflow spine |
| Issue requirement/design/plan planning | `spec-dock-issue-planning` | route selection and handoff gate invariant | issue planning workflow spine |
| Issue execution after approved executable plan | `spec-dock-issue-execution` | route only after planning artifacts and handoff readiness | TDD execution / report update workflow |
| Ambiguity, domain-language sharpening, one-question clarification, analysis-only or draft-only work | `spec-dock-clarification` | route to skill-owned clarification workflow | source-grounded grill loop and artifact capture |
| Delegated architecture draft evidence | `spec-dock-system-architect` | route as evidence producer only | scope-local design analysis draft |
| Delegated implementation plan draft evidence | `spec-dock-implementation-planner` | route as evidence producer only | scope-local plan analysis draft |
| ADR drafting / decision facilitation | `spec-dock-adr-facilitation` | route decision-facilitation work | ADR-specific facilitation workflow |

## Hub Wording Design

- Opening bullets:
  - Retain `entry/routing skill` identity.
  - State that skills own first-read workflow spine, docs own detailed semantics, templates own scaffolds/examples.
  - Avoid saying docs are the source of mandatory workflow authority.
- Global invariants:
  - Fresh `spec-reviewer` pass is required for phase promotion.
  - Missing / stale / failed / unavailable / denied / waived / provisional reviewer results are not pass.
  - Canonical docs are main orchestrator-owned.
  - Sub-agent / delegated outputs remain evidence until adopted in canonical docs and report.
- Route table:
  - Use the route matrix above.
  - Keep leaf descriptions short and outcome-focused.
  - `spec-dock-clarification` route must mention skill-owned source-grounded clarification, not docs-owned runbook authority.
- Quick reminders:
  - Keep reminders to hub-level invariants and command/path references.
  - If a reminder starts explaining leaf-specific procedure, remove it or convert it into a reference to the leaf skill / docs.

## 要件 → 設計マッピング

- AC-001 -> Route Matrix Contract
- AC-002 -> Hub Wording Design / File Change Plan
- AC-003 -> Route Matrix Contract row for `spec-dock-clarification`
- AC-004 -> Scope boundary / changed-files plan / report follow-up handling
- AC-005 -> Provider/mirror verification in plan
- AC-006 -> Global invariants section
- EC-001 -> Keep hub global invariant list minimal and inspect for duplicated leaf detail
- EC-002 -> Verify `iss-00163` completion and route targets exist before implementation

## 検証戦略

- Docs-only / skill-text-only change:
  - Use targeted `rg` positive checks for route targets and ownership wording.
  - Use targeted negative checks for stale docs-owned workflow wording and compliance-authority wording.
  - Use `cmp -s` for provider/mirror parity.
  - Use existing agent-tooling parity unittest as smoke coverage for install_root / dogfooding mirror.
- Final validation:
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`

## リスク / ロールバック

- リスク:
  - Hub becomes too broad and duplicates leaf workflow details.
  - Hub becomes too thin and route selection is no longer externally verifiable.
  - Provider/mirror drift.
- ロールバック:
  - Revert the two hub skill files and report evidence commit if reviewer finds route wording regression.

## 未確定事項

- Blocking question:
  - なし。
- Follow-up:
  - If implementation finds leaf-owned wording that should move into leaf skills, record it as follow-up instead of editing leaf skills in this issue.
