---
種別: draft-design
ID: "20260702t081000z-draft-design"
タイトル: "Redesign Initiative Requirement Design Plan Templates draft-design pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00271", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00271"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical design.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00271-DESIGN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["design.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00271 Redesign Initiative Requirement Design Plan Templates — draft-design pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `design.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `design.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 設計書ドラフト（Issue）
ID: "iss-00271"
タイトル: "Redesign Initiative Requirement Design Plan Templates"
関連GitHub: ["#271"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00271 Initiative テンプレート再設計 — 設計ドラフト

## ドラフト扱い
- この設計書は、Epic 全体の Issue 境界をそろえるための先行ドラフトである。
- `issue start` 後に、Issue Planning workflow と必要な assurance / reviewer gate に従い、正規設計へ更新する。
- このドラフトは実装開始許可ではない。

## 設計方針
- Initiative templates は、実装詳細ではなく戦略レイヤーの意思決定と Epic handoff を支える入力欄を持つ。
- 詳細な責務表はテンプレートへ重複させず、`iss-00273` が作成する `docs/authoring/scope-layering.md` へ薄くリンクできる構造にする。
- DDD / EDA は補助語彙に留め、対象 repo の既存 architecture が明確な場合だけ使えるようにする。
- 日本語運用では、見出しと説明文を日本語ファーストにし、識別子・コマンド・固定語だけ原文保持を許容する。

## 変更対象候補
| 対象 | 変更意図 |
|---|---|
| `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md` | Initiative の目的、capability landscape、stakeholder、source-grounded clarification、Epic handoff を記述できるようにする。 |
| `src/spec_dock/assets/spec_dock/templates/initiative/design.md` | system context、scope ownership、source-of-truth、artifact adoption、ADR / reviewer gate、Epic boundary を表現できるようにする。 |
| `src/spec_dock/assets/spec_dock/templates/initiative/plan.md` | Epic decomposition、handoff readiness、controlled re-slicing、report evidence、final reviewer gate を表現できるようにする。 |
| `tests/` | テンプレート構造や禁止語彙を確認する既存テストがあれば更新し、必要なら focused assertion を追加する。 |

## 要件から設計への対応
| 要件 | 設計対応 |
|---|---|
| `I271-AC-001` | requirement template に strategic purpose / capability / source-of-truth / Epic handoff の欄を置く。 |
| `I271-AC-002` | design template に context / boundary / adoption / reviewer gate の欄を置く。 |
| `I271-AC-003` | plan template に Epic decomposition / handoff readiness / re-slicing / report evidence の欄を置く。 |
| `I271-AC-004` | Issue-level TDD や private implementation detail をテンプレート必須欄にしない。 |
| `I271-AC-005` | DDD / EDA mandatory wording を避け、architecture-aware な補助説明にする。 |
| `I271-AC-006` | 日本語ファースト guidance を template authoring guidance として入れる。 |
| `I271-AC-007` | scope-layering reference のリンク導線を準備するが、dangling link は避ける。 |

## 依存関係
- `iss-00272` は、ここで整えた Initiative / Epic 共通の scope 語彙を受け取る。
- `iss-00273` は、ここで準備した reference link 導線を確定させる。
- この Issue は `iss-00276` の final quality gate まで PR delivery を行わない。

## 検証戦略
- テンプレート差分のレビューで、上流責務と下流責務が混ざっていないことを確認する。
- 既存 scaffold / snapshot tests があれば、Initiative templates の新しい構造に合わせて更新する。
- `rg` による構造確認で、必須 guidance と禁止 wording を検査する。
- 日本語ファーストの確認では、説明本文が日本語で、識別子だけ英語のままになっていることを点検する。

## 実行時に正規化する論点
- 既存テストの正確な配置。
- scope-layering reference への link insertion をこの Issue に含めるか、予定どおり `iss-00273` へ渡すかの最終判断。
- assurance profile / Issue grade に応じた正規 `design.md` の詳細節。
