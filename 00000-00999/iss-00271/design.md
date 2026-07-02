---
種別: 設計書（Issue）
ID: "iss-00271"
タイトル: "Redesign Initiative Requirement Design Plan Templates"
関連GitHub: ["#271"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00271 Initiative テンプレート再設計 — 設計

## 位置づけ
- この Issue は、provider-side Initiative templates を上流 planning の入口として強化する。
- 実装の source of truth は `src/spec_dock/assets/spec_dock/templates/initiative/` である。
- checked-in dogfooding mirror `spec-dock/templates/initiative/` は provider asset parity の検証対象であり、必要に応じて同じ内容へ同期する。
- この Issue では PR を作成しない。完了後は `issue finish` により `iss-00272` へバトンを渡す。

## 証跡採用
| 証跡 | 採用判断 | 理由 |
|---|---|---|
| `artifacts/20260702t081000z-draft-design-initiative-template-redesign-pre-start-seed.md` | partially_adopted | target files、AC対応、禁止事項は有用だが、正本設計としては詳細不足のため再構成した。 |
| `artifacts/20260702t090407z-draft-design-initiative-template-redesign-system-architect-design-draft.md` | adopted | AC対応、設計判断、境界、検証観点、リスクを正本設計へ採用する。 |

## 設計判断
- D271-001: Initiative requirement template は、戦略目的、capability landscape、source-of-truth、stakeholder / trigger、Epic handoff seed を入力できる構造にする。
- D271-002: Initiative design template は、system context、scope boundary、decision authority、artifact adoption、reviewer gate、Epic boundary を表現できる構造にする。
- D271-003: Initiative plan template は、Epic decomposition、handoff readiness、fresh reviewer gate、report evidence、controlled re-slicing を扱える構造にする。
- D271-004: Initiative templates には Issue-level implementation detail、TDD cycle、private class / file design、詳細な実装順序を必須欄として入れない。
- D271-005: DDD / EDA は標準前提にしない。既存 architecture が明確な場合だけ補助語彙として使える余地を残す。
- D271-006: 日本語運用では、見出しと説明本文を日本語ファーストにする。ファイルパス、コマンド、コード識別子、SpecDock 固定語、外部固有名詞は原文保持を許容する。
- D271-007: `docs/authoring/scope-layering.md` の作成と最終リンク追加は `iss-00273` が担当する。この Issue では壊れた相対リンクを作らず、後続で薄くリンクできる接続点だけを用意する。

## 要件から設計への対応
| 要件 | 設計対応 |
|---|---|
| `I271-AC-001` | `requirement.md` template に戦略目的、capability landscape、source-of-truth、stakeholder / trigger、Epic handoff seed を追加する。 |
| `I271-AC-002` | `design.md` template に system context、scope boundary、decision authority、artifact adoption、reviewer gate、Epic boundary を追加する。 |
| `I271-AC-003` | `plan.md` template に Epic decomposition、handoff readiness、fresh reviewer gate、report evidence、controlled re-slicing を追加する。 |
| `I271-AC-004` | 3 templates すべてで Issue-level implementation detail、TDD cycle、private code design を必須化しない。 |
| `I271-AC-005` | DDD / EDA を必須見出しや標準前提にしない。 |
| `I271-AC-006` | 日本語ファースト guidance を各 template の作成方針として含める。 |
| `I271-AC-007` | scope-layering reference の後続リンク接続点を用意し、未作成ファイルへの dangling link は作らない。 |

## 変更対象
| 対象 | 変更方針 |
|---|---|
| `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md` | strategic purpose、capability landscape、source-of-truth、stakeholder / trigger、Epic handoff seed を追加する。 |
| `src/spec_dock/assets/spec_dock/templates/initiative/design.md` | scope boundary、decision authority、artifact adoption、reviewer gate、Epic boundary を追加する。 |
| `src/spec_dock/assets/spec_dock/templates/initiative/plan.md` | Epic portfolio、handoff readiness、report evidence、fresh reviewer gate、controlled re-slicing を追加する。 |
| `spec-dock/templates/initiative/{requirement,design,plan}.md` | provider asset と同じ内容へ同期する。 |
| `tests/unit/infra/test_init_update.py` | Initiative template の主要契約を focused assertion として追加する。 |

## 変更しないもの
- `src/spec_dock/assets/spec_dock/templates/issue*` と Issue grade profile templates。
- runtime command、dependency algorithm、GitHub mutation、PR作成、Issue close。
- `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` の作成。
- workflow docs / skills の本格更新。これは `iss-00273` 以降が扱う。

## 互換性
- 既存 authored Initiative docs は移行しない。新規作成または update 後の scaffold が改善された template を受け取る。
- provider template と dogfooding mirror の parity は維持する。
- templates は starting scaffold であり、workflow docs や ADR の全文複製にはしない。

## 検証方針
- `tests/unit/infra/test_init_update.py` の focused assertion で Initiative templates の新しい契約を確認する。
- provider / dogfooding mirror parity test で同期漏れを確認する。
- `rg` で mandatory DDD / EDA、Issue-level TDD、private class / file design の混入を確認する。
- `./spec-dock/scripts/spec-dock validate` で SpecDock tree の構造を確認する。

## バトン
- `iss-00272` へ、strategic purpose、capability landscape、source-of-truth、artifact adoption、reviewer gate、handoff readiness、日本語ファースト guidance の語彙を渡す。
- `iss-00273` へ、scope-layering reference の final thin link insertion が未完了であることを渡す。
