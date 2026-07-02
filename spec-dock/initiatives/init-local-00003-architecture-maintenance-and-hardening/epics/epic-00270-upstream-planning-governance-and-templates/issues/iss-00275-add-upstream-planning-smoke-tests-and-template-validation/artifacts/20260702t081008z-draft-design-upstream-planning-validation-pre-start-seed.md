---
種別: draft-design
ID: "20260702t081008z-draft-design"
タイトル: "Add Upstream Planning Smoke Tests And Template Validation draft-design pre-start seed"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
親: ["iss-00275", "epic-00270"]
authority: "evidence"
not_canonical: true
scope_type: "issue"
scope_id: "iss-00275"
draft_lifecycle_state: "migrated_from_misplaced_canonical"
draft_origin: "pre_start_canonical_body_migration"
source_paths: ["old canonical design.md body before placeholder restore", "../requirement.md", "../report.md#EAL-00275-DESIGN", "../../../requirement.md", "../../../design.md", "../../../plan.md"]
intended_targets: ["design.md"]
adoption_status: "unreviewed"
reflected_to: []
---

# iss-00275 Add Upstream Planning Smoke Tests And Template Validation — draft-design pre-start seed

## 移行メモ

この artifact は、accepted ADR `20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` に従い、Issue Start 前に canonical `design.md` に置かれていたドラフト本文を Issue-local evidence として退避したものです。

- authority: evidence only（証跡のみ）
- canonical adoption: Issue Start 後に Issue Planning の EAL で adopted / partially_adopted / rejected / stale / blocked を判断する（このartifact単体では正本化しない）
- original source: placeholder復元前に canonical `design.md` に置かれていた旧本文
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要

## 移行前本文

---
種別: 設計書ドラフト（Issue）
ID: "iss-00275"
タイトル: "Add Upstream Planning Smoke Tests And Template Validation"
関連GitHub: ["#275"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
artifact_state: "draft-before-issue-start"
---

# iss-00275 Upstream planning smoke tests と template validation 追加 — 設計ドラフト

## ドラフト扱い
- この設計書は先行ドラフトであり、実装開始前に正規設計へ更新する。
- 前段 Issue の実際の差分を確認してから、テスト配置と検証粒度を決める。

## 設計方針
- Machine checks は構造的欠落と禁止導線を扱う。
- 自然言語の意味的十分性、日本語の質、説明の分かりやすさは reviewer finding として扱う。
- Tests は既存 suite の配置に合わせ、過剰に fragile な全文一致を避ける。
- Manual smoke evidence は `report.md` に要約し、raw workspace / logs は commit しない。

## 変更対象候補
| 対象 | 変更意図 |
|---|---|
| `tests/` | templates / docs / skills の構造、reference link、authority language、日本語ファースト guidance を検証する。 |
| `src/spec_dock/assets/spec_dock/templates/{initiative,epic}/` | テストにより不足が見つかった場合の最小修正。 |
| `src/spec_dock/assets/spec_dock/docs/` | reference / link / workflow guidance の不足が見つかった場合の最小修正。 |
| `src/spec_dock/assets/install_root/.agents/skills/` | skill wording の不足が見つかった場合の最小修正。 |
| `spec-dock/` | dogfooding validation の確認対象。必要な refresh は正規 workflow に従う。 |

## 要件から設計への対応
| 要件 | 設計対応 |
|---|---|
| `I275-AC-001` | reference existence / link reachability checks。 |
| `I275-AC-002` | authority leak / duplicate table / decision-only ready wording checks。 |
| `I275-AC-003` | DDD / EDA mandatory wording checks。 |
| `I275-AC-004` | handoff package / Option B guidance checks。 |
| `I275-AC-005` | Japanese-first guidance checks。 |
| `I275-AC-006` | machine check と reviewer judgment の境界を test comments / docs に残す。 |
| `I275-AC-007` | command results を report に記録する。 |

## 依存関係
- `iss-00271` から `iss-00274` の成果に依存する。
- `iss-00276` はこの Issue の validation evidence を final gate に使う。

## 検証戦略
- 既存 test suite を先に確認し、最小の focused tests を追加する。
- `validate` は必ず実行候補に含める。
- docs-only / skill-only 変更は inspection evidence を許容する。
- テストで発見した不足が前段 Issue の範囲に戻る場合は、report に記録してこの Issue 内で gate repair するか、必要なら plan amendment を行う。

## 実行時に正規化する論点
- 具体的な test file / fixture。
- `sync` を実行する必要があるか。
- dogfooding workspace refresh を行うか、read-through に留めるか。
