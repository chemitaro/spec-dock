---
種別: draft-design
ID: "20260702t081002z-draft-design"
タイトル: "Redesign Epic Requirement Design Plan Templates draft-design pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00272", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00272"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical design.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00272-DESIGN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["design.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00272 Redesign Epic Requirement Design Plan Templates — draft-design pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `design.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `design.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 設計書ドラフト（Issue）
ID: "iss-00272"
タイトル: "Redesign Epic Requirement Design Plan Templates"
関連GitHub: ["#272"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00272 Epic テンプレート再設計 — 設計ドラフト

## ドラフト扱い
- この設計書は先行ドラフトであり、実装開始前に正規設計へ更新する。
- `iss-00271` の結果を取り込むまでは、文言やリンクの最終形を固定しない。

## 設計方針
- Epic templates は、複数 Issue にまたがる model envelope と handoff contract を表現する。
- Issue の実装順序や TDD 詳細は Issue plan に残し、Epic plan には Issue 切り出し、依存、integration checkpoint、final gate を置く。
- artifact authority flow を明示し、raw research / interview / delegated draft を canonical authority と誤認させない。
- 日本語ファースト authoring を、説明本文と判断理由の既定動作として誘導する。

## 変更対象候補
| 対象 | 変更意図 |
|---|---|
| `src/spec_dock/assets/spec_dock/templates/epic/requirement.md` | capability / model envelope、Epic acceptance、scope / non-scope、downstream Issue seed を記述できるようにする。 |
| `src/spec_dock/assets/spec_dock/templates/epic/design.md` | cross-Issue boundary、contract portfolio、design slice catalog、artifact adoption、test strategy を記述できるようにする。 |
| `src/spec_dock/assets/spec_dock/templates/epic/plan.md` | Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を記述できるようにする。 |
| `tests/` | Epic templates の構造と禁止範囲を確認する focused checks を追加または更新する。 |

## 要件から設計への対応
| 要件 | 設計対応 |
|---|---|
| `I272-AC-001` | requirement template に capability / acceptance / scope を置く。 |
| `I272-AC-002` | design template に cross-Issue boundary / design slice catalog を置く。 |
| `I272-AC-003` | plan template に handoff package / dependencies / final quality gate を置く。 |
| `I272-AC-004` | Issue-level TDD 詳細を Epic template の必須欄にしない。 |
| `I272-AC-005` | artifact adoption と report ledger の導線を置く。 |
| `I272-AC-006` | 日本語ファースト guidance を明示する。 |
| `I272-AC-007` | downstream Issue に渡す fields をテンプレート上で揃える。 |

## 依存関係
- `iss-00271` から上流テンプレート語彙を受け取る。
- `iss-00273` はこの Issue の出力に薄い scope-layering reference links を接続する。
- `iss-00274` は Epic handoff package を readiness inspection の入力として使う。

## 検証戦略
- Epic templates が Issue handoff fields を持つことを文書点検または focused test で確認する。
- Issue-level execution authority を置き換える文言がないことを確認する。
- DDD / EDA が必須語彙になっていないことを確認する。
- 日本語ファースト guidance の対象と許容英語の境界を確認する。

## 実行時に正規化する論点
- `iss-00271` の実装で確定した用語との整合。
- scope-layering reference への final link を `iss-00273` に残すための境界。
- 既存 tests の正確な配置と追加範囲。
