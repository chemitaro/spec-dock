---
種別: 論点整理（Epic）
ID: "20260623t034212z-disc"
タイトル: "Issue Draft Integration Review"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
親: ["epic-00224", "init-local-00003"]
---

# Issue Draft Integration Review

この文書は `epic-00224` の Issue 作成後に、各 Issue の draft requirement / draft design が統合された状態で抜け漏れ・重複を起こしていないかを確認するための discussion evidence である。Canonical Issue docs ではない。

## Issue Map

`iss-00226 / #226` は decision-only Issue として作成されたが、ADR authority は Epic-scope accepted ADR へ移動したため closed / superseded historical evidence とする。Downstream implementation handoff の対象 Issue は `iss-00227`〜`iss-00233` である。

| Slice | Issue | GitHub | Draft requirement | Draft design |
|---|---|---:|---|---|
| I01 | `iss-00227` | `#227` | `issues/iss-00227-.../discussions/20260623t033541z-draft-requirement-draft-requirement.md` | `issues/iss-00227-.../discussions/20260623t033545z-draft-design-draft-design.md` |
| I02 | `iss-00228` | `#228` | `issues/iss-00228-.../discussions/20260623t033549z-draft-requirement-draft-requirement.md` | `issues/iss-00228-.../discussions/20260623t033557z-draft-design-draft-design.md` |
| I03 | `iss-00229` | `#229` | `issues/iss-00229-.../discussions/20260623t033601z-draft-requirement-draft-requirement.md` | `issues/iss-00229-.../discussions/20260623t033605z-draft-design-draft-design.md` |
| I04 | `iss-00230` | `#230` | `issues/iss-00230-.../discussions/20260623t033609z-draft-requirement-draft-requirement.md` | `issues/iss-00230-.../discussions/20260623t033613z-draft-design-draft-design.md` |
| I05 | `iss-00231` | `#231` | `issues/iss-00231-.../discussions/20260623t033617z-draft-requirement-draft-requirement.md` | `issues/iss-00231-.../discussions/20260623t033623z-draft-design-draft-design.md` |
| I06 | `iss-00232` | `#232` | `issues/iss-00232-.../discussions/20260623t033628z-draft-requirement-draft-requirement.md` | `issues/iss-00232-.../discussions/20260623t033633z-draft-design-draft-design.md` |
| I07 | `iss-00233` | `#233` | `issues/iss-00233-.../discussions/20260623t033638z-draft-requirement-draft-requirement.md` | `issues/iss-00233-.../discussions/20260623t033644z-draft-design-draft-design.md` |

## Ownership Check

| Contract | Owner | Duplication guard |
|---|---|---|
| Required ADRs | Epic-scope accepted ADRs | Do not defer ADR-level decisions to a leaf Issue. |
| Assurance Contract / classification | I01 / `iss-00227` | I07 only closes rollout, not classification core. |
| Workflow Runbook / fixed Skill kernel | I02 / `iss-00228` | I03/I04 consume Runbook; they do not rewrite Skill kernel. |
| Artifact composition / stale source binding | I03 / `iss-00229` | I04 consumes step facts; it does not own planning section composition. |
| Step routing / context policy | I04 / `iss-00230` | I06 consumes reviewer evidence; it does not own context packet generation. |
| Trusted review trigger | I05 / `iss-00231` | I06 consumes review generation evidence; it does not trigger arbitrary body reviews. |
| PR blocker closure | I06 / `iss-00232` | I07 consumes metrics; it does not redefine blocker policy. |
| Rollout / telemetry / Auto-Lite readiness | I07 / `iss-00233` | Automatic Lite default remains out of initial rollout. |

## Gap Check

- E-RQ-001〜021 are covered by I01〜I07 in `plan.md`; Epic-scope accepted ADRs provide G0 decision baseline.
- E-AC-001〜021 are covered by I01〜I07 in `plan.md`.
- `E-AC-008` is assigned to I03, the stale source binding owner.
- `E-AC-005`, `E-AC-006`, `E-AC-007` are assigned to I02/I03/I04 respectively.
- `E-RQ-012` formal close is assigned to I07; I01 only contributes strict-legacy detection prerequisite.
- MyPy / Ruff external preparation is reflected as a static-analysis expectation in all implementation draft requirements/designs without changing feature scope.

## Dependency Check

Registered dependencies:

```text
iss-00228 -> iss-00227
iss-00229 -> iss-00227, iss-00228
iss-00230 -> iss-00229
iss-00231 -> iss-00227
iss-00232 -> iss-00230, iss-00231
iss-00233 -> iss-00228, iss-00229, iss-00230, iss-00231, iss-00232
```

`iss-00233` is intentionally blocked by all implementation slices required for rollout.
`iss-00227 -> iss-00226` was removed after `iss-00226 / #226` was closed / superseded.

## Reviewer Focus

- Confirm each Issue draft has a clear parent E-RQ/E-AC trace.
- Confirm no draft claims canonical Issue readiness; these are discussion drafts only.
- Confirm no Issue contains automatic Lite default enablement.
- Confirm context routing is isolated to I04 and consumed by I06/I07 without redefinition.
- Confirm PR review trigger is isolated to I05 and blocker policy to I06.
