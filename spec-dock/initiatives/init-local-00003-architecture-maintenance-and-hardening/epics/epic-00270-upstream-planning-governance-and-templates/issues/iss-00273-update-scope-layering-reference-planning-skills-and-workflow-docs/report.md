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
- Issue scaffold と正規 `requirement.md` は作成済み。
- `assurance classify --stage requirement` は `authorized_profile: standard` を返した。
- `assurance compose --artifact all` を実行し、その後 `design.md` / `plan.md` を Issue 固有の正規文書へ更新した。
- Issue requirement / Epic plan は `strict` 相当の specialist evidence を要求するため、system-architect draft と implementation-planner draft を取得した。
- 実装、最終検証、Issue完了、PR作成は未実施。

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|
| D-273-001 | resolved | scope | `scope-layering.md` は狭い operational reference とし、workflow docs / phase docs / skills / templates は thin link に留める。 | Issue requirement, Epic D-001, system-architect draft | promoted_to_design | `design.md` の authority model と変更対象へ反映した。 |
| D-273-002 | resolved | operation | この Issue では PR を作成せず、完了後に `issue finish` で `iss-00274` へバトンを渡す。 | Epic plan の 1PR delivery 方針 | promoted_to_plan | `plan.md` の S99 に反映した。 |
| D-273-003 | resolved | grade | runtime authorized profile は `standard` だが、Issue requirement と Epic plan の `strict` obligation に合わせて specialist evidence と final reviewer gates を維持する。 | `assurance classify`, Issue requirement | applied | Grade Specialist Evidence Gate に記録した。 |

## Evidence Adoption Ledger（証跡採用台帳）
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-273-001 | adopted | `epic-00270` canonical docs | `requirement.md` / `design.md` / `plan.md` | Slice 03 handoff と accepted ADR を Issue 要件・設計・計画へ落とす。 | `epic-00270/requirement.md`, `epic-00270/design.md`, `epic-00270/plan.md` | 実装で reference / link / skills を更新する。 |
| EAL-273-002 | adopted | accepted ADR | `design.md` | scope-layering reference は single provider-side reference と thin links で扱う。 | `artifacts/20260702t022907z-adr-scope-layering-reference-publication-surface.md` | S02-S06 で実装する。 |
| EAL-273-003 | adopted | `iss-00271` / `iss-00272` completion evidence | `design.md` / `plan.md` | Initiative / Epic templates の接続点と日本語ファースト / authority 語彙を前提にする。 | commit `10e17424`, commit `0a959794`, `deps check iss-00273` -> ready | S06 で final thin links を接続する。 |
| EAL-273-DESIGN-SEED | partially_adopted | migrated pre-start canonical body | `design.md` | target surfaces、scope-layering 方針、検証観点を採用した。正本設計は現物調査と system-architect draft で再構成した。 | `artifacts/20260702t081004z-draft-design-scope-layering-planning-guidance-pre-start-seed.md` | Fresh `spec-reviewer` で正本設計を確認する。 |
| EAL-273-PLAN-SEED | partially_adopted | migrated pre-start canonical body | `plan.md` | 実行順、バトン、検証候補を採用した。正本計画は implementation-planner draft で具体化した。 | `artifacts/20260702t081005z-draft-plan-scope-layering-planning-guidance-pre-start-seed.md` | Fresh `spec-reviewer` で正本計画を確認する。 |
| EAL-273-DESIGN-DRAFT | adopted | system-architect draft | `design.md` | authority model、AC/EC mapping、target surfaces、risk/test strategy を採用した。draft 自体は evidence-only とする。 | `artifacts/20260702t101615z-draft-design-draft-design-scope-layering-guidance-system-architect.md` | Fresh `spec-reviewer` で正本設計を確認する。 |
| EAL-273-PLAN-DRAFT | adopted | implementation-planner draft | `plan.md` | step order、closure index、verification ladder、review gates を採用した。draft 自体は evidence-only とする。 | `artifacts/20260702t101719z-draft-plan-scope-layering-guidance-implementation-planner.md` | Fresh `spec-reviewer` で正本計画を確認する。 |
| EAL-273-ASSURANCE | adopted | assurance commands | `design.md` / `plan.md` / `report.md` | runtime assurance は `authorized_profile: standard` と判定し、compose を実行した。Issue requirement 上の strict obligation は追加 gate として維持する。 | `assurance classify --stage requirement`, `assurance compose --artifact all` | `assurance verify` と reviewer gate を通す。 |

## Spec Authoring Gate
| phase | investigated_facts | open_questions | adoption_decision | reviewer_verdict | blocking | promotion_decision |
|---|---|---|---|---|---|---|
| requirement | Epic handoff、accepted ADR、pre-start seed を確認した。 | none | adopted | pass | no | execute approved plan |
| design | system-architect draft、pre-start seed、現物 docs / skills / templates を確認した。 | none | adopted | pass | no | execute approved plan |
| plan | implementation-planner draft、pre-start seed、実行順と検証梯子を確認した。 | none | adopted | pass | no | execute approved plan |

## Grade Specialist Evidence Gate
| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | system-architect / implementation-planner | used | `artifacts/20260702t101615z-draft-design-draft-design-scope-layering-guidance-system-architect.md`; `artifacts/20260702t101719z-draft-plan-scope-layering-guidance-implementation-planner.md`; canonical `design.md` / `plan.md` に採用判断を反映 | pass | ready |
| strict | system-architect / implementation-planner | used | `artifacts/20260702t101615z-draft-design-draft-design-scope-layering-guidance-system-architect.md`; `artifacts/20260702t101719z-draft-plan-scope-layering-guidance-implementation-planner.md`; canonical `design.md` / `plan.md` に採用判断を反映 | pass | ready |

## Delegated Draft Evidence（委任ドラフト証跡）
| created_by_role | scope_id | artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | fallback_decision | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00273 | `artifacts/20260702t101615z-draft-design-draft-design-scope-layering-guidance-system-architect.md` | active issue docs; parent epic docs; predecessor issues; provider docs / skills / templates | `design.md` | source input evidence only（adopted） | `design.md` | passed | source input integrated into canonical `design.md`; draft itself is evidence-only | none | none | canonical artifact fresh reviewer gate（pass）; canonical docs hold authority | execute approved plan via canonical artifact; draft remains evidence-only |
| implementation-planner | iss-00273 | `artifacts/20260702t101719z-draft-plan-scope-layering-guidance-implementation-planner.md` | active issue docs; parent epic docs; predecessor issues; provider docs / skills / templates; tests | `plan.md` | source input evidence only（adopted） | `plan.md` | passed | source input integrated into canonical `plan.md`; draft itself is evidence-only | none | none | canonical artifact fresh reviewer gate（pass）; canonical docs hold authority | execute approved plan via canonical artifact; draft remains evidence-only |
| migrated pre-start seed | iss-00273 | `artifacts/20260702t081004z-draft-design-scope-layering-planning-guidance-pre-start-seed.md` | pre-start canonical body | `design.md` | historical input only（partially_adopted） | `design.md` | passed by manual reconciliation | seed input integrated where still current; seed itself is evidence-only | none | none | canonical artifact fresh reviewer gate（pass）; canonical docs hold authority | execute approved plan via canonical artifact; seed remains evidence-only |
| migrated pre-start seed | iss-00273 | `artifacts/20260702t081005z-draft-plan-scope-layering-planning-guidance-pre-start-seed.md` | pre-start canonical body | `plan.md` | historical input only（partially_adopted） | `plan.md` | passed by manual reconciliation | seed input integrated where still current; seed itself is evidence-only | none | none | canonical artifact fresh reviewer gate（pass）; canonical docs hold authority | execute approved plan via canonical artifact; seed remains evidence-only |

## Reviewer Gate Status（レビュアーゲート状態）
| gate | reviewer | reviewer_role | freshness | state | risk_acceptance | promotion_decision | note |
|---|---|---|---|---|---|---|---|
| planning | Beauvoir (`019f225f-01d5-7963-be80-0e3648cf8aa2`) | spec-reviewer | fresh | pass | no | execute approved plan | 正規 `requirement.md` / `design.md` / `plan.md` / `report.md`、Issue-local artifacts、親 Epic、前段 Issue を確認し、findings なし。 |

## 実装記録
- S00 planning normalization: completed。
- S01 以降の実装は未実施。

## 検証
- 実施済み:
  - `./spec-dock/scripts/spec-dock deps check iss-00273` -> ready。
  - `./spec-dock/scripts/spec-dock assurance classify --stage requirement` -> `authorized_profile: standard`。
  - `./spec-dock/scripts/spec-dock assurance compose --artifact all` -> design / plan / report changed。
- 未実施:
  - `assurance verify`。
  - focused pytest。
  - targeted grep。
  - `./spec-dock/scripts/spec-dock validate`。
  - `git diff --check`。
  - final reviewer gates。

## 完了 / PR
- Issue完了: 未実施。
- PR作成: 未実施。この Epic は `iss-00276` でまとめて PR delivery を扱う。
