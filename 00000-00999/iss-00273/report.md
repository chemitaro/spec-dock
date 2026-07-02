---
種別: 実装報告書（Issue）
ID: "iss-00273"
タイトル: "Update Scope Layering Reference Planning Skills And Workflow Docs"
関連GitHub: ["#273"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00273 Scope-layering reference と planning guidance 更新 — レポート

## 進捗サマリー
- Issue scaffold を作成した。
- 正規 `requirement.md` を作成した。
- 旧 canonical `design.md` / `plan.md` に置かれていた pre-start draft body は、Issue-local `draft-design` / `draft-plan` artifact へ移した。
- Canonical `design.md` / `plan.md` は `awaiting-assurance-compose` placeholder に戻した。
- 実装、テスト、Issue完了、PR作成は未実施。

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|
| D-273-001 | resolved | scope | この Issue の正本は `requirement.md` であり、`design.md` / `plan.md` は実行時に正規化する先行ドラフトである。 | ユーザー指示、Issue Planning workflow | applied | `issue start` 後に `iss-00271` / `iss-00272` の結果を取り込み、正規設計・正規計画へ更新する。 |
| D-273-002 | resolved | operation | この Issue では PR を作成せず、完了後に `issue finish` で `iss-00274` へバトンを渡す。 | Epic plan の1PR delivery方針、dependency chain | applied | final PR delivery は `iss-00276` が扱う。 |

## 証跡採用台帳
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-273-001 | adopted | `epic-00270` canonical docs | `requirement.md` / `design.md` / `plan.md` | Epic の Slice 03 handoff を Issue 要件と pre-start seed へ落とした。要件は正本として採用し、design / plan seed は evidence-only artifact として保持する。 | `epic-00270/requirement.md`, `epic-00270/design.md`, `epic-00270/plan.md` | Issue開始時に前段テンプレート結果を反映する。 |
| EAL-273-002 | adopted | accepted ADR | `requirement.md` | scope-layering reference は1つの provider-side reference と thin links で扱う方針を採用した。 | `artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md` | 実装時に reference と link 範囲を正規化する。 |
| EAL-273-003 | adopted | Epic EAL-023 / local validation commands | `report.md` | Batch planning artifact の検証は Epic-level evidence として記録済みであり、この Issue では実装検証とは分けて参照する。 | `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`); `deps check epic-00270` / `deps check iss-00276` -> expected blocked | Issue固有の実装検証は `issue start` 後に行う。 |
| EAL-00273-DESIGN | deferred | migrated pre-start canonical body | `artifacts/20260702t081004z-draft-design-scope-layering-planning-guidance-pre-start-seed.md` | 旧 canonical `design.md` body は pre-start handoff seed として有用だが canonical authority ではないため、Issue-local draft artifact へ移した。採用可否は Issue Start 後の EAL で判断する。 | old `design.md` before placeholder restore | Issue Start 後に採用 / 部分採用 / 棄却を判断する。 |
| EAL-00273-PLAN | deferred | migrated pre-start canonical body | `artifacts/20260702t081005z-draft-plan-scope-layering-planning-guidance-pre-start-seed.md` | 旧 canonical `plan.md` body は pre-start handoff seed として有用だが executable canonical plan ではないため、Issue-local draft artifact へ移した。採用可否は Issue Start 後の EAL で判断する。 | old `plan.md` before placeholder restore | Issue Start 後に採用 / 部分採用 / 棄却を判断する。 |

## 仕様 authoring ゲート
| フェーズ | 状態 | 採用判断 | レビュアー判定 | ブロック有無 | 次アクション |
|---|---|---|---|---|---|
| requirement | 作成済み | Epic handoff から採用 | Pascal の batch pass は historical evidence。current post-ADR requirement は fresh spec-review 対象。 | no | current planning set の fresh spec-review 後、Issue開始時に再確認する。 |
| design | placeholder restored | Issue-local draft artifact を evidence として保持し、正規設計は未合成 | Pascal の batch pass は historical evidence。current placeholder / draft artifact boundary は fresh spec-review 対象。 | no | `issue start` 後に artifact 採否を判断し、assurance compose と fresh reviewer gate を通す。 |
| plan | placeholder restored | Issue-local draft artifact を evidence として保持し、正規計画は未合成 | Pascal の batch pass は historical evidence。current placeholder / draft artifact boundary は fresh spec-review 対象。 | no | `issue start` 後に artifact 採否を判断し、assurance compose と fresh reviewer gate を通す。 |

## Grade Specialist Evidence Gate
- issue grade: `strict`
- draft-design artifact: `artifacts/20260702t081004z-draft-design-scope-layering-planning-guidance-pre-start-seed.md`
- draft-plan artifact: `artifacts/20260702t081005z-draft-plan-scope-layering-planning-guidance-pre-start-seed.md`
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要
- 現在状態: migration artifact は存在するが、specialist enrichment / manual fallback evidence は Issue Start まで未実施である。
- readiness への影響: draft artifact が存在するだけでは、この Issue は execution-ready にならない。

## 実装記録
- 未実施。

## 検証
- 実施済み:
  - Batch planning artifact validation: Epic EAL-023 に従い `./spec-dock/scripts/spec-dock validate` が成功した（`nodes=178`）。
  - Dependency-chain confirmation: Epic EAL-023 に従い `deps check epic-00270` / `deps check iss-00276` は前段Issue未完了で blocked となり、リレー依存どおりであることを確認した。
- 未実施:
  - このIssue固有の実装・対象ファイル検証は未実施。`issue start` 後に正規 plan に従って実施する。

## 完了 / PR
- Issue完了: 未実施。
- PR作成: 未実施。この Epic は `iss-00276` でまとめて PR delivery を扱う。
