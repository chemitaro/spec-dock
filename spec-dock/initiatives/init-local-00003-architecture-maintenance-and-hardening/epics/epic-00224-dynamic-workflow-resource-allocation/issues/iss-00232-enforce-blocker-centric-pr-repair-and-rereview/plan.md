---
種別: 実装計画書（Issue）
ID: "iss-00232"
タイトル: "Enforce Blocker Centric PR Repair And Rereview"
関連GitHub: ["#232"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00232 Enforce Blocker Centric PR Repair And Rereview — 実装計画

## この計画で満たす要件ID
- AC: AC-001, AC-002, AC-003, AC-004
- EC: EC-001, EC-002, EC-003
- Epic: E-RQ-010, E-RQ-011, E-AC-011, E-AC-012
- I07 prerequisite: E-AC-013 blocker fingerprint evidence

## 実装順序
- S01: blocker policy payload と decision integration を実装する。
- S90: provider / dogfooding mirror と docs impact を解消する。
- S99: final validation / reviewer gates / final commit。

## 仕様固定クロージャ索引
| ID | step | 種別 | 固定する期待値 | 証跡レベル |
|---|---|---|---|---|
| tc-232-001 | S01 | acceptance | P2-only Codex comment は `blocker_policy_no_action` で merge-prepared を妨げない | green-regression |
| tc-232-002 | S01 | acceptance | protected domain + machine evidence を持つ P2 は `promoted_blocker` になる | green-regression |
| tc-232-003 | S01 | regression | current changes requested / unresolved thread は既存どおり blocker | covered-existing |
| tc-232-004 | S01 | evidence | blocker finding fingerprint が payload に出る | covered-existing |
| tc-232-004a | S01 | negative | P0 / P1 priority comment は blocker になる | green-regression |
| tc-232-004b | S01 | negative | protected-only / evidence-only P2 は promoted blocker にならない | green-regression |
| tc-232-004c | S01 | negative | priority-less current Codex comment は generic fallback に残る | green-regression |
| tc-232-004d | S01 | regression | GraphQL / review-thread limitation は既存 fail-closed behavior を維持する | covered-existing |
| tc-232-004e | S01 | regression | reviewDecision blocker は P2-only no-action で merge-prepared に上書きされない | green-regression |
| tc-232-004f | S01 | negative | P3 priority comment は default non-blocking follow-up になる | green-regression |
| tc-232-005 | S90 | parity | provider install_root と dogfooding mirror の review snapshot script が一致する | inspect-only |
| tc-232-006 | S99 | final | focused tests、lint、validate、reviewer gates が通る | manual-required |

## S01 — Blocker policy integration
- 対象:
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `.agents/skills/github-pr-observation/scripts/lib/pr_review_snapshot.py`
  - `tests/unit/infra/test_init_update.py`
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k 'issue_232 or issue_182_s01_review_collector_exposes_current_changes_requested_evidence'`
- closure:
  - tc-232-001〜tc-232-004e
- reviewer:
  - code-reviewer

## S90 — Docs / mirror impact
- 対象:
  - provider / mirror diff inspection
  - issue requirement / design / plan / report
- Green 検証:
  - `diff -u src/.../pr_review_snapshot.py .agents/.../pr_review_snapshot.py`
- reviewer:
  - spec-reviewer

## S99 — Final quality gate
- 必須 validation:
  - `make lint`
  - focused tests
  - `./spec-dock/scripts/spec-dock validate`
- final QA gate:
  - qa-reviewer
- final code review:
  - code-reviewer
- final spec review:
  - spec-reviewer
