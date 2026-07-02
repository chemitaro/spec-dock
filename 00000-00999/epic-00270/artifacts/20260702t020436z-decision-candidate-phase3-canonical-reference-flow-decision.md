---
種別: decision-candidate
ID: "20260702t020436z-decision-candidate"
タイトル: "Phase 3 Canonical And Reference Flow Decision"
状態: "proposed"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["epic-00270"]
関連:
  - "20260702t015700z-interview"
  - "20260702t020436z-01-disc"
authority: "proposed"
derived_from:
  - "artifacts/20260702t015700z-interview-phase3-canonical-detail-level.md"
  - "artifacts/20260702t020436z-01-disc-phase3-reference-adoption-map.md"
reflected_to: []
---

# 20260702t020436z-decision-candidate Phase 3 Canonical And Reference Flow Decision

## 判断候補

- proposed decision:
  - `epic-00270` の canonical docs は中程度の詳細にする。
  - V3 reference の採用判断、境界、Issue slicing policy、handoff package、acceptance/gate は canonical docs に反映する。
  - 詳細分析、長い例、playbook、補助判断は split artifacts または ADR 候補へ分離し、canonical docs から参照する。
- trigger:
  - V3 ZIP は有用だが、raw full-intake artifact だけでは後続エージェントが参照しにくい。
- affected scope:
  - `epic-00270` requirement/design/plan/report and downstream Issue planning.

## observed facts

- V3 ZIP 24 Markdown files are preserved in raw intake artifact.
- User approved Option B for canonical detail level.
- User explicitly said V3 references should be used, not ignored or copied wholesale into canonical docs.
- Current repo already treats `artifacts/` as working evidence, not canonical authority.

## ambiguity / constraint

- Canonical docs must be sufficient for reviewer and downstream Issue handoff.
- Canonical docs must not become a large raw reference dump.
- ADR should be used for durable decisions only, not every note.

## options considered

- Option A:
  - Copy most V3 reference content into canonical docs.
  - Rejected as too heavy for maintainable Epic docs.
- Option B:
  - Keep canonical docs focused on adopted decisions and handoff; use split artifacts/ADR candidates for detailed references.
  - User-approved.
- Option C:
  - Keep canonical docs thin and rely mostly on artifact references.
  - Rejected as too weak for reviewer gate and downstream Issue handoff.

## rationale

- This keeps V3 assets alive while preserving SpecDock's canonical authority model.
- It gives coding agents shorter, topic-specific references.
- It avoids forcing every downstream Issue to read a 2,000+ line raw intake file.

## adoption target

- `requirement.md`:
  - State that V3 assets are source evidence and that canonical docs adopt only selected requirements/boundaries/gates.
- `design.md`:
  - Define the reference flow: raw intake -> split artifacts/decision candidates/ADR candidates -> canonical docs/report ledger.
- `plan.md`:
  - Require Issue handoffs to reference canonical docs plus the relevant split artifact, not the whole ZIP.
- `ADR`:
  - Create only when a decision is durable, surprising, or likely to be reused outside this Epic.
- `report.md` Evidence Adoption Ledger:
  - Record this decision candidate if adopted.

## risk if wrong

- Too much canonical detail makes docs hard to review and maintain.
- Too little canonical detail makes downstream Issue planning depend on raw artifact interpretation.
- Too many ADRs would create governance overhead without added clarity.

## rollback or revisit

- Revisit if `spec-reviewer` finds canonical docs insufficient for phase promotion.
- Revisit if downstream Issue planning repeatedly needs raw V3 references not captured in split artifacts.

## status / disposition

- status:
  - proposed
- disposition evidence:
  - Awaiting adoption into canonical docs and report ledger.
