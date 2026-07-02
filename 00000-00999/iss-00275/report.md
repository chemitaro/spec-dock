---
種別: 実装報告書（Issue）
ID: "iss-00275"
タイトル: "Add Upstream Planning Smoke Tests And Template Validation"
関連GitHub: ["#275"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00275 Upstream planning smoke tests と template validation 追加 — レポート

## 進捗サマリー
- Issue scaffold と正規 `requirement.md` は作成済みである。
- Pre-start の design / plan seed は Issue-local `draft-design` / `draft-plan` artifact として保持している。
- `issue start` 後に `assurance classify` / `assurance compose` を実行し、生成テンプレートの placeholder を専門家ドラフトに基づく正規 `design.md` / `plan.md` へ置き換えた。
- system-architect と implementation-planner のドラフトを取得し、main orchestrator が採用判断を行った。
- 実装、focused tests、Issue完了、PR作成は未実施である。

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|
| D-275-001 | resolved | scope | この Issue は validation slice であり、前段4 Issueの成果を構造検証する。 | Epic plan Slice 05 | adopted | 実装時に focused tests / smoke checks へ落とす。 |
| D-275-002 | resolved | delivery | この Issue では PR を作成しない。 | Epic one-PR delivery policy | adopted | `iss-00276` へ handoff する。 |
| D-275-003 | resolved | test-strategy | machine tests は構造欠落に限定し、自然言語の意味品質は reviewer finding に残す。 | `D-006`, `I275-EC-001` | adopted | fresh `spec-reviewer` に false-positive risk を確認させる。 |
| D-275-004 | resolved | grade | Requirement の `strict` を運用等級として採用し、system-architect / implementation-planner evidence と fresh review を必要にする。 | Issue requirement, Grade Specialist Evidence Gate | adopted | runtime assurance profile が `standard` でも strict 相当の証跡を維持する。 |
| D-275-005 | resolved | command-surface | `new artifact draft-design` / `draft-plan` を統一 primitive とし、actor別 command は追加しない。 | ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` | adopted | tests は command surface の増殖ではなく non-mutation / fail-closed を確認する。 |

## 証跡採用台帳（Evidence Adoption Ledger / 必須）
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-275-001 | adopted | `epic-00270` canonical docs | `requirement.md` / `design.md` / `plan.md` | Slice 05 の目的、許可変更、禁止変更、検証期待を採用した。 | `epic-00270/requirement.md`, `epic-00270/design.md`, `epic-00270/plan.md` | focused tests / smoke checks へ落とす。 |
| EAL-275-002 | adopted | accepted ADRs / interviews | `requirement.md` / `design.md` | artifact authority、architecture-neutral、Option B、日本語ファースト、unified draft artifact primitive を採用した。 | `artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md`, `artifacts/20260702t024118z-adr-architecture-neutral-template-authoring-policy.md`, `artifacts/20260702t030615z-interview-phase3-handoff-package-inspection-strength.md`, `artifacts/20260702t040113z-adr-japanese-first-spec-authoring-policy.md`, `artifacts/20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` | 実装時に closure mapping を確認する。 |
| EAL-275-003 | adopted | pre-start draft-design | `design.md` | pre-start seed は authority ではないが、AC/EC の初期分解と検証期待が Issue 要件と整合するため、正規設計の参考として採用した。 | `artifacts/20260702t081008z-draft-design-upstream-planning-validation-pre-start-seed.md` | 実装時には正規 `design.md` を優先する。 |
| EAL-275-004 | adopted | pre-start draft-plan | `plan.md` | pre-start seed は executable plan ではないが、Slice 05 の検証項目を保持していたため、実装計画の参考として採用した。 | `artifacts/20260702t081009z-draft-plan-upstream-planning-validation-pre-start-seed.md` | 実装時には正規 `plan.md` を優先する。 |
| EAL-275-005 | partially_adopted | system-architect draft | `design.md` | `DES-001..012`、machine / smoke / reviewer 分担、既存テスト面、false-positive 境界を採用した。一方、canonical authority や reviewer pass の自己主張は採用していない。 | `artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md` | fresh `spec-reviewer` で正本への統合結果を確認する。 |
| EAL-275-006 | partially_adopted | implementation-planner draft | `plan.md` | milestone、closure mapping、focused command ladder、stop condition、no-PR handoff を採用した。一方、placeholder 状態の観測や未検証 command 結果は実行証跡として採用していない。 | `artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` | 実装時に command 実行結果を別途記録する。 |
| EAL-275-007 | adopted | local assurance commands | `.assurance.json`, `design.md`, `plan.md`, `report.md` | `assurance classify` / `assurance compose` により正本テンプレートを配置した後、main orchestrator が具体化した。 | `.assurance.json`, `design.md`, `plan.md`, `report.md` | 編集後に `assurance classify` / `assurance verify` を再実行する。 |
| EAL-275-008 | adopted | fresh `spec-reviewer` gate | `requirement.md`, `design.md`, `plan.md`, `report.md` | Dewey は AC/EC trace、machine / smoke / reviewer 境界、DDD / EDA と日本語ファーストの false-positive 境界、draft authority isolation、unified draft artifact ADR、no-PR handoff を確認し、P0/P1/P2 なしで `review_status: pass` とした。 | Dewey: `019f22ae-51a7-7ea2-a13c-8a2ed1806d72`; `review_status: pass`; `overall_confidence_score: 0.88` | 実装へ進む。 |

## 仕様 authoring ゲート（Spec Authoring Gate / 必須）
| フェーズ | 調査証跡 | 未確定事項 / 回答 | 採用判断 | レビュアー判定 | ブロック有無 | 昇格 / 次アクション |
|---|---|---|---|---|---|---|
| requirement | Epic docs、accepted ADRs、pre-start draft artifacts、Issue requirement | blocking open question はない。 | requirement.md を正本として採用 | pass | no | execute approved plan |
| design | system-architect draft、既存 tests / docs / skills の targeted inventory、Epic design decisions | machine / smoke / reviewer の分担は解決済み。 | `design.md` に採用 | pass | no | execute approved plan |
| plan | implementation-planner draft、Issue requirement / design、Epic plan Slice 05 | PR は作らず `iss-00276` へ handoff する。 | `plan.md` に採用 | pass | no | execute approved plan |

## 委任ドラフト証跡（Delegated Draft Evidence / 必須）
| ロール | 範囲 | ドラフトパス | 参照元 | 予定反映先 | 採用状態 | 反映先 | 差分ガード結果 | 統合結果 | 採用しなかった部分 | ブロッカー | レビュー結果 | 昇格判断 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00275 | `artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md` | active issue docs、pre-start draft artifacts、active epic docs、relevant tests / docs / skills / templates | `design.md` | partially_integrated | `design.md` | pass: artifact-only edit; `validate` pass; canonical docs not edited by delegate | machine / smoke / reviewer 分担、設計 ID、既存 test surface、false-positive 境界を統合 | final authority、reviewer pass、implementation readiness claim | none | pass | execute approved plan |
| implementation-planner | iss-00275 | `artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` | active issue docs、pre-start draft artifacts、active epic docs、relevant tests / docs / skills | `plan.md` | partially_integrated | `plan.md` | pass: artifact-only edit; `validate` pass; canonical docs not edited by delegate | milestone、closure、focused command ladder、stop condition、handoff を統合 | 未実行 command を実施済み証跡として扱うこと | none | pass | execute approved plan |

#### グレード別専門家証跡ゲート（Grade Specialist Evidence Gate）
| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | system-architect / implementation-planner or explicit skip reason | used | `artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md`; `artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` | pass | ready |
| strict | system-architect / implementation-planner | used | `artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md`; `artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` | pass | ready |

#### レビューゲート状態（Reviewer Gate Status）
| gate | reviewer scope | reviewer role | freshness | state | risk acceptance | promotion |
|---|---|---|---|---|---|---|
| planning | planning spec-review | spec-reviewer | fresh | pass | no | execute approved plan |

## Issue-local draft artifact path index
| 種別 | パス | 状態 | authority |
|---|---|---|---|
| pre-start draft-design | `artifacts/20260702t081008z-draft-design-upstream-planning-validation-pre-start-seed.md` | adopted as evidence | evidence-only |
| pre-start draft-plan | `artifacts/20260702t081009z-draft-plan-upstream-planning-validation-pre-start-seed.md` | adopted as evidence | evidence-only |
| specialist draft-design | `artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md` | partially_integrated | evidence-only |
| specialist draft-plan | `artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` | partially_integrated | evidence-only |

## 実装記録
- 未実施。

## 検証
- 実施済み:
  - `./spec-dock/scripts/spec-dock assurance classify --stage requirement` -> pass。`.assurance.json` を作成。
  - `./spec-dock/scripts/spec-dock assurance compose --artifact all` -> pass。`design.md` / `plan.md` / `report.md` を配置。
  - system-architect draft 作成時の `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`)。
  - implementation-planner draft 作成時の `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`)。
- 未実施:
  - focused pytest commands は未実施。実装ステップで実行する。
  - 実装後の focused test / smoke check は未実施。正本更新後の planning verification は完了済み。

## 完了 / PR
- Issue完了: 未実施。
- PR作成: 未実施。この Epic は `iss-00276` でまとめて PR delivery を扱う。

<!-- spec-dock:managed-section begin id="report.step-evidence" -->
## Step Evidence
| Step | Closure | Verification | Result | Evidence | Next action |
|---|---|---|---|---|---|
| planning-compose | `CLOS-275-006`, `CLOS-275-009`, `CLOS-275-011` | `assurance classify`, `assurance compose`, delegated drafts | pass | `.assurance.json`, `artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md`, `artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` | run assurance verify / validate / spec-review |
| planning-review | `CLOS-275-006`, `CLOS-275-011`, `CLOS-275-012` | fresh `spec-reviewer` | pass | Dewey `019f22ae-51a7-7ea2-a13c-8a2ed1806d72`; `review_status: pass` | execute approved plan |
<!-- spec-dock:managed-section end id="report.step-evidence" -->
