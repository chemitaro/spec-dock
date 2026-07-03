---
種別: draft-design
ID: "20260702t081004z-draft-design"
タイトル: "Update Scope Layering Reference Planning Skills And Workflow Docs draft-design pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00273", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00273"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical design.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00273-DESIGN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["design.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00273 Update Scope Layering Reference Planning Skills And Workflow Docs — draft-design pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `design.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `design.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 設計書ドラフト（Issue）
ID: "iss-00273"
タイトル: "Update Scope Layering Reference Planning Skills And Workflow Docs"
関連GitHub: ["#273"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00273 Scope-layering reference と planning guidance 更新 — 設計ドラフト

## ドラフト扱い
- この設計書は先行ドラフトであり、実装開始前に正規設計へ更新する。
- `iss-00271` / `iss-00272` の実装結果を確認してから、link target と文言を最終化する。

## 設計方針
- 長い責務モデルは `docs/authoring/scope-layering.md` に集約し、他 surface は薄い導線だけ持つ。
- workflow docs は lifecycle authority、scope-layering reference は responsibility / decision-routing authority、templates は authoring prompt という責務分担を維持する。
- `spec-dock-clarification` は、Grill With Docs 的な source-grounded interview を SpecDock の artifacts / report / ADR flow に合わせて案内する。
- 日本語ファースト guidance は docs / skills / artifacts guidance へ置き、固定語や識別子の原文保持は許容する。

## 変更対象候補
| 対象 | 変更意図 |
|---|---|
| `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` | Initiative / Epic / Issue の責務、authority flow、anti-rules を集約する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` | Initiative planning から reference へ誘導する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | Epic planning / handoff から reference へ誘導する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Issue が parent envelope を再定義しないことを reference へ誘導する。 |
| `src/spec_dock/assets/spec_dock/docs/phase_*` / `authoring/*` | phase gate が scope-layering を必要とする箇所だけ参照を追加する。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md` | source-grounded authoring と日本語ファースト guidance を反映する。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md` | Issue handoff と reference flow を反映する。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` | 一問ずつの interview、調査優先、artifact 外部化を明確にする。 |
| Initiative / Epic templates | 既に準備された thin link を reference に接続する。 |

## 要件から設計への対応
| 要件 | 設計対応 |
|---|---|
| `I273-AC-001` | 新規 reference を作成する。 |
| `I273-AC-002` | docs / skills / templates は薄いリンクに留める。 |
| `I273-AC-003` | planning / clarification skills に source-grounded interview flow を反映する。 |
| `I273-AC-004` | artifact authority flow を docs / skills に明記する。 |
| `I273-AC-005` | 日本語ファースト guidance を関連 surface に置く。 |
| `I273-AC-006` | 前段テンプレートの link 導線を実 reference へ接続する。 |
| `I273-AC-007` | focused checks / validate で構造確認する。 |

## 依存関係
- `iss-00271` / `iss-00272` のテンプレート変更に依存する。
- `iss-00274` の readiness guidance は、この Issue の reference と wording を前提にする。
- `iss-00275` の smoke tests は、この Issue の変更を検証対象にする。

## 検証戦略
- reference が存在し、関連 surface から到達できることを確認する。
- full responsibility table が重複していないことを grep / diff で確認する。
- raw artifact authority leak がないことを確認する。
- 日本語ファースト guidance が docs / skills / artifacts guidance に存在することを確認する。

## 実行時に正規化する論点
- どの phase docs にリンクを追加するかの最小範囲。
- templates への link insertion の正確な場所。
- focused test を unit / CLI runtime / docs grep のどこに置くか。
