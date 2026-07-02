---
種別: 実装報告書（Issue）
ID: "iss-00276"
タイトル: "Epic Quality Gate Manual Tests And PR Delivery"
関連GitHub: ["#276"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00276 Epic品質gate、手動テスト、PR delivery — レポート

## 進捗サマリー
- Issue scaffold を作成した。
- 正規 `requirement.md` を作成した。
- 旧 canonical `design.md` / `plan.md` に置かれていた pre-start draft body は、Issue-local `draft-design` / `draft-plan` artifact へ移した。
- Canonical `design.md` / `plan.md` は `awaiting-assurance-compose` placeholder に戻した。
- 実装、テスト、Issue完了、PR作成は未実施。

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|
| D-276-001 | resolved | scope | この Issue の正本は `requirement.md` であり、`design.md` / `plan.md` は実行時に正規化する先行ドラフトである。 | ユーザー指示、Issue Planning workflow | applied | `issue start` 後に前段5 Issue の結果を取り込み、正規設計・正規計画へ更新する。 |
| D-276-002 | resolved | operation | この Issue だけが PR readiness / PR creation を扱う。前段IssueではPRを作成しない。 | Epic plan の1PR delivery方針、delivery boundary interview | applied | 実行時に1PR維持可否を確認し、破綻する場合は Epic plan amendment を行う。 |
| D-276-003 | resolved | quality-gate | Final gate は automated checks、manual dogfooding、reviewer gates、raw manual files not staged の確認を統合する。 | `epic-00270` requirement / plan | applied | 実行時に検証結果と未実施理由を report に記録する。 |

## 証跡採用台帳
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-276-001 | adopted | `epic-00270` canonical docs | `requirement.md` / `design.md` / `plan.md` | Epic の Slice 06 handoff を final quality / PR delivery Issue の要件とドラフト計画へ落とした。 | `epic-00270/requirement.md`, `epic-00270/design.md`, `epic-00270/plan.md` | 前段5 Issue 完了後に final gate と PR creation を実施する。 |
| EAL-276-002 | adopted | user decision / interview | `requirement.md` | IssueごとのPRではなく、最後の品質gate Issueで1PR delivery を扱う方針を採用した。 | `artifacts/20260702t015343z-interview-phase3-delivery-pr-boundary.md` | 実行時に1PRが維持できるか確認する。 |
| EAL-276-003 | adopted | Epic EAL-023 / local validation commands | `report.md` | Batch planning artifact の検証は Epic-level evidence として記録済みであり、この Issue では実装検証とは分けて参照する。 | `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`); `deps check epic-00270` / `deps check iss-00276` -> expected blocked | Issue固有の final quality validation は `issue start` 後に行う。 |
| EAL-00276-DESIGN | deferred | migrated pre-start canonical body | `artifacts/20260702t081010z-draft-design-epic-quality-pr-delivery-pre-start-seed.md` | 旧 canonical `design.md` body は pre-start handoff seed として有用だが canonical authority ではないため、Issue-local draft artifact へ移した。採用可否は Issue Start 後の EAL で判断する。 | old `design.md` before placeholder restore | Issue Start 後に採用 / 部分採用 / 棄却を判断する。 |
| EAL-00276-PLAN | deferred | migrated pre-start canonical body | `artifacts/20260702t081011z-draft-plan-epic-quality-pr-delivery-pre-start-seed.md` | 旧 canonical `plan.md` body は pre-start handoff seed として有用だが executable canonical plan ではないため、Issue-local draft artifact へ移した。採用可否は Issue Start 後の EAL で判断する。 | old `plan.md` before placeholder restore | Issue Start 後に採用 / 部分採用 / 棄却を判断する。 |

## 仕様 authoring ゲート
| フェーズ | 状態 | 採用判断 | レビュアー判定 | ブロック有無 | 次アクション |
|---|---|---|---|---|---|
| requirement | 作成済み | Epic handoff から採用 | Pascal の batch pass は historical evidence。current post-ADR requirement は fresh spec-review 対象。 | no | current planning set の fresh spec-review 後、Issue開始時に再確認する。 |
| design | placeholder restored | Issue-local draft artifact を evidence として保持し、正規設計は未合成 | Pascal の batch pass は historical evidence。current placeholder / draft artifact boundary は fresh spec-review 対象。 | no | `issue start` 後に artifact 採否を判断し、assurance compose と fresh reviewer gate を通す。 |
| plan | placeholder restored | Issue-local draft artifact を evidence として保持し、正規計画は未合成 | Pascal の batch pass は historical evidence。current placeholder / draft artifact boundary は fresh spec-review 対象。 | no | `issue start` 後に artifact 採否を判断し、assurance compose と fresh reviewer gate を通す。 |

## Grade Specialist Evidence Gate
- issue grade: `critical`
- draft-design artifact: `artifacts/20260702t081010z-draft-design-epic-quality-pr-delivery-pre-start-seed.md`
- draft-plan artifact: `artifacts/20260702t081011z-draft-plan-epic-quality-pr-delivery-pre-start-seed.md`
- specialist obligation: specialist output がない場合は原則 blocked。manual fallback は risk acceptance / extra reviewer / rollback-safety evidence がある場合だけ例外
- 現在状態: migration artifact は存在するが、specialist enrichment / manual fallback evidence は Issue Start まで未実施である。
- readiness への影響: draft artifact が存在するだけでは、この Issue は execution-ready にならない。

## 実装記録
- 未実施。

## 検証
- 実施済み:
  - Batch planning artifact validation: Epic EAL-023 に従い `./spec-dock/scripts/spec-dock validate` が成功した（`nodes=178`）。
  - Dependency-chain confirmation: Epic EAL-023 に従い `deps check epic-00270` / `deps check iss-00276` は前段Issue未完了で blocked となり、リレー依存どおりであることを確認した。
- 未実施:
  - このIssue固有の final quality validation / PR readiness は未実施。前段5 Issue 完了後、`issue start` して正規 plan に従って実施する。

## 完了 / PR
- Issue完了: 未実施。
- PR作成: 未実施。この Issue が最終的な PR delivery を扱う。
