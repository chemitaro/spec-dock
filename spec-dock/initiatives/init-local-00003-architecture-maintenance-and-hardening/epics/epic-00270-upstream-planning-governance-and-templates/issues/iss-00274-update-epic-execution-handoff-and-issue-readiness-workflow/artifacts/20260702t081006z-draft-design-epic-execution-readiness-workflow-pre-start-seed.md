---
種別: draft-design
ID: "20260702t081006z-draft-design"
タイトル: "Update Epic Execution Handoff And Issue Readiness Workflow draft-design pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00274", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00274"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical design.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00274-DESIGN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["design.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00274 Update Epic Execution Handoff And Issue Readiness Workflow — draft-design pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `design.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `design.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 設計書ドラフト（Issue）
ID: "iss-00274"
タイトル: "Update Epic Execution Handoff And Issue Readiness Workflow"
関連GitHub: ["#274"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00274 Epic execution handoff と Issue readiness workflow 更新 — 設計ドラフト

## ドラフト扱い
- この設計書は先行ドラフトであり、実装開始前に正規設計へ更新する。
- `iss-00272` と `iss-00273` の成果により、対象ファイルと文言を最終化する。

## 設計方針
- Epic execution は coordinator / structural gate として振る舞う。
- Structural blockers と reviewer findings を分離し、機械的に確認できる欠落だけを blocking とする。
- Semantic sufficiency は `spec-reviewer` の責務として残し、skill は reviewer gate を置き換えない。
- Issueリレーは `issue finish` -> 次の `issue start` を基本とし、PR は final quality Issue に集約する。

## 変更対象候補
| 対象 | 変更意図 |
|---|---|
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-execution/SKILL.md` | Epic execution の first-read / readiness / handoff inspection guidance を更新する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | Epic planning から execution への handoff readiness を明示する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Issue start 前後の parent handoff / no per-Issue PR 方針を補助する。 |
| 必要な `phase_*` docs | readiness gate の参照を最小限追加する。 |
| `tests/` | runtime behavior を変更する場合のみ focused tests を追加する。 |

## 要件から設計への対応
| 要件 | 設計対応 |
|---|---|
| `I274-AC-001` | Epic execution skill が Epic docs と Issue handoff package を読むようにする。 |
| `I274-AC-002` | structural blocker list を skill / docs に明示する。 |
| `I274-AC-003` | reviewer finding の扱いと semantic reviewer 非代替を明示する。 |
| `I274-AC-004` | raw artifact authority / decision-only ready を禁止する。 |
| `I274-AC-005` | no per-Issue PR と final PR delivery Issue を明示する。 |
| `I274-AC-006` | 日本語ファースト authoring guidance を execution / readiness 文脈へ反映する。 |

## 依存関係
- `iss-00272` の Epic handoff fields に依存する。
- `iss-00273` の scope-layering reference と artifact authority wording に依存する。
- `iss-00275` はこの Issue の structural / semantic 分離を検証する。

## 検証戦略
- skill / workflow docs の read-through で、Issue execution へ進む前の必要入力が明確か確認する。
- structural blockers と reviewer findings が混同されていないことを確認する。
- runtime behavior を変更した場合のみ、CLI runtime tests を追加または更新する。
- 日本語ファースト guidance の文面を確認する。

## 実行時に正規化する論点
- skill guidance だけで十分か、runtime guidance / tests も必要か。
- Issue finish / next issue start の具体的な記述箇所。
- reviewer finding を report のどの ledger に残すかの実行時表現。
