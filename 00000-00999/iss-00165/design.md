---
種別: 設計書（Issue）
ID: "iss-00165"
タイトル: "Align Workflow Docs With Skill Spine Boundary"
関連GitHub: ["#165"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-06"
依存: ["requirement.md"]
親: ["epic-00158", "init-local-00003"]
---

# iss-00165 Align Workflow Docs With Skill Spine Boundary — 設計

## 目的・制約

- 目的:
  - Workflow / phase / authoring / entry docs を、skill-owned first-read workflow spine の detail / reference layer として読める状態にする。
  - Docs に残すべき lifecycle policy、field semantics、hard cases、report evidence semantics を保ちながら、mandatory first action が docs-only に隠れるような authority wording を避ける。
- 必須:
  - `iss-00163` / `iss-00164` の completed direction と矛盾しない。
  - Provider-side docs source を変更し、dogfooding mirror で検証する。
  - `workflow_clarification.md` は `spec-dock-clarification` skill-owned workflow の bridge/reference として扱う。
  - `workflow_spec_authoring.md` / `workflow_issue.md` は detail authority を維持しつつ、対応 skill との entry relationship を明示する。
- 禁止:
  - Runtime behavior、CLI validation、templates、skills をこの issue に吸収しない。
  - Docs を空洞化し、policy detail / hard cases を消さない。
  - Full link retirement や broad docs rewrite を行わない。

## 既存実装 / 規約の理解

- 参照した実装 / docs:
  - `src/spec_dock/assets/spec_dock/docs/README.md`
  - `src/spec_dock/assets/spec_dock/docs/guide.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`
  - `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`
  - `src/spec_dock/assets/spec_dock/docs/authoring/issue-plan.md`
  - `spec-dock/active/epic/issues/iss-00162-align-skill-docs-template-context-surfaces/discussions/20260606t040013z-disc-context-surface-inventory.md`
- 現状理解:
  - `workflow_clarification.md` はすでに bridge/reference 色が強いが、entry docs の高頻度ルールではまだ「正本」と読める表現が残る。
  - `workflow_spec_authoring.md` は phase promotion detail authority として妥当だが、skill-first entry relationship を opening で明確にした方がよい。
  - `workflow_issue.md` は lifecycle/completion policy detail authority として維持し、`spec-dock-issue-execution` / `spec-dock-issue-planning` の first-read spine との関係を明示する。
  - `phase_plan_issue.md` と `authoring/issue-plan.md` は issue plan field semantics / executable step schema の detail authority であり、skill-first routing を補足する対象である。
- 採用するパターン:
  - Opening / 高頻度ルール / 関連欄で authority relationship を短く補正する。
  - 詳細 policy 本文は大きく移動しない。
  - Provider docs と mirror docs の byte or semantic parity を検証する。
- 採用しないもの:
  - Skill rewrite。
  - Template rewrite。
  - Runtime gate / validation changes。
  - Docs 全体の章構成刷新。

## 採用方針 / トレードオフ

- 論点:
  - Docs をどこまで薄くするか。
- 決定:
  - Docs は thin にはしない。Docs は detailed semantics / policy / hard cases を持つ。
  - ただし docs の opening / entry wording は、skill が first-read workflow spine を所有し、docs は detail / reference を所有するという関係を明示する。
- 理由:
  - Docs から詳細を削ると、agent が field semantics や lifecycle policy を確認できなくなる。
  - 一方で、docs が mandatory first action authority と読めると、skill を読んだだけでは実行順序が分からないという元の問題を再導入する。

## 対象ファイルと責務

```text
src/spec_dock/assets/spec_dock/docs/
|-- README.md                    # 変更: docs entrypoint を skill-first routing / detail reference として整える
|-- guide.md                     # 変更候補: high-level guide に古い authority wording がある場合のみ補正
|-- workflow_clarification.md    # 変更候補: bridge/reference wording の補強
|-- workflow_spec_authoring.md   # 変更: phase promotion detail authority と skill entry relationship を明示
|-- workflow_issue.md            # 変更: issue planning/execution skills と lifecycle detail authority の境界を明示
|-- phase_plan_issue.md          # 変更候補: issue plan field semantics detail authority として明示
`-- authoring/
    `-- issue-plan.md            # 変更候補: executable step schema / field semantics detail authority として明示

spec-dock/docs/
|-- README.md                    # dogfooding mirror validation target
|-- guide.md                     # dogfooding mirror validation target
|-- workflow_clarification.md    # dogfooding mirror validation target
|-- workflow_spec_authoring.md   # dogfooding mirror validation target
|-- workflow_issue.md            # dogfooding mirror validation target
|-- phase_plan_issue.md          # dogfooding mirror validation target
`-- authoring/issue-plan.md      # dogfooding mirror validation target
```

- 変更しない:
  - `src/spec_dock/assets/install_root/.agents/skills/`
  - `src/spec_dock/assets/spec_dock/templates/`
  - Runtime scripts / Python code / tests except existing docs/mirror verification commands。

## Boundary Wording Contract

| Surface | Target wording | Must avoid |
|---|---|---|
| `README.md` / `guide.md` | Skills are operational entrypoints; docs are detail/reference navigation | Saying clarification/spec authoring/issue execution is docs-only source of first action |
| `workflow_clarification.md` | Bridge/reference for `spec-dock-clarification` skill-owned grill loop | Reclaiming mandatory clarification runbook authority from the skill |
| `workflow_spec_authoring.md` | Detail authority for phase promotion semantics, evidence schema, hard cases | Hiding phase-order first action without skill entry reference |
| `workflow_issue.md` | Detail authority for lifecycle, execution policy, completion gates | Making issue execution appear valid without approved plan / skill entry / report gates |
| `phase_plan_issue.md` / `authoring/issue-plan.md` | Field semantics and executable plan schema detail authority | Presenting template/schema details as the operational entrypoint |

## 要件 → 設計マッピング

- AC-001 -> Boundary Wording Contract and targeted `rg` negative checks.
- AC-002 -> Detail retention read-through for workflow / phase / authoring docs.
- AC-003 -> `workflow_clarification.md` and README / guide clarification wording.
- AC-004 -> Provider / mirror validation strategy.
- AC-005 -> File change plan and forbidden changes.
- EC-001 -> Detail retention policy.
- EC-002 -> Link / bridge wording inspection.
- EC-003 -> Decision ledger / follow-up handling if skill rewrite is discovered.

## 検証戦略

- Pre-change / red alternative:
  - Targeted inspection for old docs-as-source-of-first-action wording in provider docs.
  - Inventory rows from `iss-00162` prove target docs are the owner lane for this issue.
- Green verification:
  - Targeted `rg` for positive boundary wording:
    - skill / first-read / operational entrypoint
    - docs / detail / reference / semantics / hard cases
    - `spec-dock-clarification` + bridge/reference
  - Targeted negative `rg` for stale wording:
    - `workflow_clarification.md` as source of truth for clarification workflow
    - docs as only source of mandatory workflow / compliance authority
  - Manual read-through of changed sections to confirm detail semantics are not removed.
  - `./spec-dock/scripts/spec-dock sync`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - `git diff --name-only` to prove no skills/templates/runtime scope absorption.
- Reviewer gates:
  - Step-level `spec-reviewer` for docs-only diff.
  - Final `qa-reviewer`, `code-reviewer`, and `spec-reviewer` before finish.

## リスク / ロールバック

- リスク:
  - Docs become too thin and lose useful policy detail.
  - Docs still imply mandatory first actions live only in docs.
  - Link wording changes break existing readers.
  - Scope expands into templates / skills / runtime.
- ロールバック:
  - Revert provider docs and mirror docs changes in the affected commit.
  - If wording is too thin, restore detail paragraphs while preserving skill-first entry wording.
  - If a skill rewrite is discovered as necessary, stop and record follow-up instead of absorbing it.

## 未確定事項

- Blocking question:
  - なし。
- Follow-up:
  - Leaf-specific skill expansion is outside this issue unless a docs contradiction cannot be resolved without it.
