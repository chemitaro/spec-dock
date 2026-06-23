---
種別: 実装計画書（Issue）
ID: "iss-00231"
タイトル: "Inject Trusted Base Branch Codex Review Policy"
関連GitHub: ["#231"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-06-23"
依存: ["requirement.md", "design.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00231 Inject Trusted Base Branch Codex Review Policy — 実装計画

## この計画で満たす要件ID
- AC:
  - AC-001, AC-002, AC-003
- EC:
  - EC-001, EC-002, EC-003
- Epic:
  - E-RQ-009
  - E-AC-009, E-AC-010

## 実装順序
- S01: trusted base review policy asset と trigger compiler を実装する。
- S90: provider / dogfooding mirror と docs impact を解消する。
- S99: final validation / reviewer gates / final commit。

## 仕様固定クロージャ索引
| ID | step | 種別 | 固定する期待値 | 証跡レベル |
|---|---|---|---|---|
| tc-231-001 | S01 | acceptance | base SHA policy を取得し、policy hash / reviewed head SHA を含む multiline body を投稿する | covered-existing + green-regression |
| tc-231-002 | S01 | negative | PR head 側や caller-provided body を trusted policy source として使わない | covered-existing + inspect-only |
| tc-231-003 | S01 | compatibility | base SHA metadata が無い既存 fixture では fixed `@codex review` path が維持される | covered-existing |
| tc-231-004 | S01 | negative | stale head / draft / non-open / permission denied の既存 fail-closed behavior を維持する | covered-existing |
| tc-231-004a | S01 | negative | policy missing / invalid / too-large では fixed `@codex review` fallback と limitation を返す | green-regression |
| tc-231-005 | S90 | parity | provider install_root と dogfooding mirror の trigger / policy が一致する | inspect-only |
| tc-231-006 | S99 | final | focused tests、lint、validate、reviewer gates が通る | manual-required |

## 実装ステップ S01 — Trusted base policy trigger
- 対象ファイル:
  - `src/spec_dock/assets/install_root/.github/codex/review-policy.md`
  - `src/spec_dock/assets/install_root/.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
  - `tests/unit/infra/test_init_update.py`
- Green 検証:
  - `uv run pytest tests/unit/infra/test_init_update.py -k 'trigger_helper'`
- closure:
  - tc-231-001〜tc-231-004a
- reviewer:
  - code-reviewer

## ドキュメント影響の解消ステップ S90
- 対象:
  - `.github/codex/review-policy.md`
  - `.agents/skills/github-pr-observation/scripts/trigger_codex_review.sh`
- Green 検証:
  - provider / dogfooding mirror diff inspection
- reviewer:
  - spec-reviewer

## 最終品質ゲートステップ S99
- 必須 validation:
  - `make lint`
  - `uv run pytest tests/unit/infra/test_init_update.py -k 'trigger_helper'`
  - `./spec-dock/scripts/spec-dock validate`
- final QA gate:
  - qa-reviewer
- final code review:
  - code-reviewer
- final spec review:
  - spec-reviewer

## I05 deferred / superseded items
- Policy schema:
  - superseded by fixed Markdown path plus runtime validation because review policy is instruction text, not structured JSON.
- Max size:
  - implemented in S01 as 32 KiB runtime validation.
- Doctor capability:
  - deferred to Epic rollout / operationalization because this Issue's executable evidence is emitted by the trigger helper payload and the final PR observation workflow owns operator-facing diagnosis.
