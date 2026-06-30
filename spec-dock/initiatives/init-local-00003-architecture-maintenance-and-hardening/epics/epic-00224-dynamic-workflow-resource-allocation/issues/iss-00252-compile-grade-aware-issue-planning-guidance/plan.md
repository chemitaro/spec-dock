---
種別: 実装計画書（Issue）
ID: "iss-00252"
タイトル: "Compile Grade Aware Issue Planning Guidance"
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00252 Compile Grade Aware Issue Planning Guidance — Issue 実装計画書（Strict）

## 1. 実装戦略

ADR と Epic design の grade matrix を、agent-facing guidance と docs に落とす。runtime wording と docs wording が分岐しないよう、source-of-truth surface を先に確認する。

## 2. マイルストーン

| Milestone | 成果 | 検証 |
|---|---|---|
| M0 | current guidance / docs / skill wording の baseline | inspection |
| M1 | grade selection と authority split を guidance に追加 | focused tests / docs inspection |
| M2 | requirement / design / plan authoring rules を追加 | docs / skill inspection |
| M3 | specialist 推奨 / 必須 / fallback wording を追加 | guidance regression |
| M90 | provider / dogfooding mirror parity | parity inspection |
| M95 | strict spec review | spec-reviewer pass |
| M99 | issue-local handoff gate | focused tests, `./spec-dock/scripts/spec-dock validate` |

## 3. Behavior Backlog

| Behavior | 内容 | Closure |
|---|---|---|
| B-001 | guidance が grade matrix を返す | AC-001 |
| B-002 | Lite non-default と unknown -> Standard 以上を示す | AC-002 / AC-003 |
| B-003 | `authorized_profile` と manual escalation の分離を示す | AC-004 |
| B-004 | Standard の specialist 推奨 / skip reason を示す | AC-005 |
| B-005 | Strict / Critical の specialist fallback evidence を示す | AC-006 |
| B-006 | G2 / G3 が参照できる wording を固定する | AC-007 |

## 4. 変更対象

- issue-planning guidance source
- issue planning skill handoff docs
- `workflow_spec_authoring.md` and phase docs
- provider / dogfooding mirror
- relevant guidance tests

## 5. 禁止変更

- `new doc` draft routing を変更しない。
- readiness classifier を変更しない。
- Fresh `spec-reviewer` gate を弱めない。

## 6. Review / commit gate

- M1〜M3 は docs / guidance wording の coherent diff として review する。
- M99 で実行した command、未実施理由、provider / dogfooding parity を `report.md` に記録する。

## 7. Epic branch baton / PR policy

- この Issue では個別 PR を作成しない。
- M99 は `iss-00253` に渡せる local closure checkpoint とする。
- M99 通過後、grade-aware guidance、docs / tests、report evidence を commit し、その HEAD から `iss-00253` の branch を開始する。
- G2 / G3 が並列可能に見える場合でも、この Epic PR では抜け漏れ・重複を避けるため default baton order を `iss-00253 -> iss-00254` とする。
