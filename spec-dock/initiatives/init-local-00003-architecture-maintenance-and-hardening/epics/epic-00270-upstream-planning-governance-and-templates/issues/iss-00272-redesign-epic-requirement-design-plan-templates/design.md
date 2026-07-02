---
種別: 設計書（Issue）
ID: "iss-00272"
タイトル: "Redesign Epic Requirement Design Plan Templates"
関連GitHub: ["#272"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00272 Epic テンプレート再設計 — 設計

## 位置づけ
- この Issue は、provider-side Epic templates を Initiative から Issue へ渡す handoff surface として強化する。
- 実装の source of truth は `src/spec_dock/assets/spec_dock/templates/epic/` である。
- checked-in dogfooding mirror `spec-dock/templates/epic/` は provider asset parity の検証対象であり、必要に応じて同じ内容へ同期する。
- この Issue では PR を作成しない。完了後は `issue finish` により `iss-00273` へバトンを渡す。

## 証跡採用
| 証跡 | 採用判断 | 理由 |
|---|---|---|
| `artifacts/20260702t081002z-draft-design-epic-template-redesign-pre-start-seed.md` | partially_adopted | target files、AC対応、禁止事項、実装時論点を採用した。正本設計としては詳細不足のため再構成した。 |
| `artifacts/20260702t093309z-draft-design-epic-template-redesign-system-architect-design-draft.md` | adopted | AC対応、設計判断、boundary / contract model、template contract、互換性を正本設計へ採用する。 |

## 設計判断
- D272-001: Epic requirement template は、capability / model envelope、主要ユースケース、Epic-level acceptance、scope / non-scope、downstream Issue seed を記述できる構造にする。
- D272-002: Epic design template は、cross-Issue boundary、design slice catalog、contract portfolio、artifact adoption、failure / migration / rollback、test strategy を表現できる構造にする。
- D272-003: Epic plan template は、Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を扱える構造にする。
- D272-004: Epic templates には Issue-level TDD step、test function detail、private helper / class design を必須欄として入れない。
- D272-005: `artifacts/` は raw evidence surface として扱い、採用済み判断は canonical docs、accepted ADR、または `report.md` Evidence Adoption Ledger へ置く。
- D272-006: DDD / EDA は標準前提にしない。既存 architecture が明確な場合だけ補助語彙として使える余地を残す。
- D272-007: 日本語運用では、見出しと説明本文を日本語ファーストにする。ファイルパス、コマンド、コード識別子、SpecDock 固定語、外部固有名詞は原文保持を許容する。
- D272-008: shipped template に dogfooding 固有 Issue ID を入れない。

## 要件から設計への対応
| 要件 | 設計対応 |
|---|---|
| `I272-AC-001` | `requirement.md` template に capability / model envelope、主要ユースケース、Epic-level acceptance、scope / non-scope、downstream Issue seed を追加する。 |
| `I272-AC-002` | `design.md` template に cross-Issue boundary、design slice catalog、contract portfolio、failure / migration / test strategy を追加する。 |
| `I272-AC-003` | `plan.md` template に Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を追加する。 |
| `I272-AC-004` | 3 templates すべてで Issue-level TDD step、private implementation design を必須化しない。 |
| `I272-AC-005` | `artifacts/` の raw evidence 境界と canonical adoption / report EAL への採否導線を追加する。 |
| `I272-AC-006` | 日本語ファースト guidance を各 template の作成方針として含める。 |
| `I272-AC-007` | Epic plan の Issue handoff package に parent trace、allowed local delta、forbidden parent boundary changes、expected evidence を含める。 |

## 変更対象
| 対象 | 変更方針 |
|---|---|
| `src/spec_dock/assets/spec_dock/templates/epic/requirement.md` | 作成方針、capability / model envelope、downstream Issue seed、artifact authority boundary を追加する。 |
| `src/spec_dock/assets/spec_dock/templates/epic/design.md` | cross-Issue boundary、design slice catalog、contract portfolio、artifact adoption、failure / migration / rollback、test strategy を追加する。 |
| `src/spec_dock/assets/spec_dock/templates/epic/plan.md` | Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を追加する。 |
| `spec-dock/templates/epic/{requirement,design,plan}.md` | provider asset と同じ内容へ同期する。 |
| `tests/unit/infra/test_init_update.py` | Epic template の主要契約を focused assertion として追加する。 |

## 変更しないもの
- Initiative templates の追加変更。ただし `iss-00271` の語彙は参照する。
- Issue grade templates、Issue profile templates、runtime command、dependency algorithm。
- workflow docs / skills / scope-layering reference の本格更新。これは `iss-00273` 以降が扱う。
- PR 作成、GitHub Issue close、merge 操作。

## 互換性
- 既存 authored Epic docs は移行しない。新規作成または update 後の scaffold が改善された template を受け取る。
- provider template と dogfooding mirror の parity は維持する。
- templates は starting scaffold であり、workflow docs や ADR の全文複製にはしない。

## 検証方針
- `tests/unit/infra/test_init_update.py` の focused assertion で Epic templates の新しい契約を確認する。
- provider / dogfooding mirror parity test で同期漏れを確認する。
- targeted `rg` で mandatory DDD / EDA、Issue-level TDD、private design、dogfooding 固有 Issue ID、dangling scope-layering link の混入を確認する。
- `./spec-dock/scripts/spec-dock validate` で SpecDock tree の構造を確認する。

## バトン
- `iss-00273` へ、scope-layering reference と workflow docs / skills に接続すべき Epic handoff 語彙を渡す。
- `iss-00274` へ、Epic execution readiness が消費する Issue handoff package 語彙を渡す。
