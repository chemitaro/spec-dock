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
- 実装とローカル検証は完了済み。
- Fresh reviewer gate は初回レビューで P1/P2 を検出し、修正後の再検証を実施済み。再レビュー待ち。
- Issue完了、PR作成は未実施。

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
| final-initial | Nietzsche (`019f2279-4543-7f02-9b0a-f1912064e210`) | spec-reviewer | fresh | fail | no | repair | P1: `spec-dock-initiative-planning` skill に `scope-layering.md` / source-grounded / 日本語ファースト入口が不足。 |
| final-initial | Aristotle (`019f2279-78c0-7843-bf3b-a045ea39586e`) | code-reviewer | fresh | pass | no | repair P2 | P2: `spec-dock-initiative-planning` skill の薄い参照不足。P3: progress summary stale。 |
| final-initial | Bohr (`019f2279-b579-72a1-99d1-74e57d7a0545`) | qa-reviewer | fresh | fail | no | repair | P1: Initiative planning skill verification gap。P2: `scope-layering.md` mirror parity map 不足。 |
| final-recheck | Russell (`019f227d-d8e8-7463-8fde-306b7e91c7af`) | spec-reviewer | fresh | pass | no | finish after P2 report trace fix | P1 は解消。P2: S05 closure ID 表記を plan と合わせる。 |
| final-recheck | Averroes (`019f227e-050c-79f3-ba25-f9b1ca497dd1`) | qa-reviewer | fresh | pass | no | finish | 前回 P1/P2 は解消。追加 QA verification gate なし。 |

## 実装記録
- S00 planning normalization: completed。
- S01 Red / characterization: completed。
  - delegated role: `dev-coder` Helmholtz (`019f2264-7455-77f2-a899-e518bea02d71`)
  - changed files: `tests/unit/infra/test_init_update.py`
  - closure delta: `C273-001`, `C273-006`, `C273-008` の characterization assertions を追加した。
  - worker note: `No material implementation decisions beyond the approved plan.`
  - verification: `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> expected Red。`docs/authoring/scope-layering.md` が provider docs asset に存在しないため `is_file()` assertion failed。
- S02 scope-layering reference: completed。
  - delegated role: `doc-writer` Harvey (`019f2266-9790-7f11-aec5-89dbf37a22b4`)
  - changed files: `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`; `spec-dock/docs/authoring/scope-layering.md`
  - closure delta: `C273-001`, `C273-004`, `C273-005`, `C273-010` の reference authority、evidence/canonical 境界、日本語ファースト、DDD/EDA 非必須方針を追加した。
  - worker note: `No material implementation decisions beyond the approved plan.`
  - verification: provider / mirror の `test -f` passed。`diff -q src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md spec-dock/docs/authoring/scope-layering.md` -> no diff。本文で evidence-only、日本語ファースト、identifier/command 保持、DDD/EDA 非必須を確認した。
- S03 workflow docs thin links / draft handoff boundary: completed。
  - delegated role: `doc-writer` Hume (`019f226a-91e3-7a20-948e-bee144497e44`)
  - changed files: `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md`; `src/spec_dock/assets/spec_dock/docs/workflow_epic.md`; `src/spec_dock/assets/spec_dock/docs/workflow_issue.md`; `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md`; `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md`; mirror 5 files under `spec-dock/docs/`
  - closure delta: `C273-001`, `C273-002`, `C273-003`, `C273-004`, `C273-005`, `C273-008`, `C273-010` の thin link、Issue-local draft handoff package、canonical Issue docs 非先取り、parent envelope 非再定義を追加した。
  - worker note: `No material implementation decisions beyond the approved plan.`
  - verification: provider / mirror 5 ペアの `diff -q` -> no diff。`rg -n "authoring/scope-layering\\.md|draft-design|draft-plan|Issue-local|path index"` で必要語を確認。対象 docs の `git diff --check` passed。
- S04 phase / authoring docs thin links: completed。
  - delegated role: `doc-writer` Herschel (`019f226e-9725-7cf1-aad4-19c708e211ae`)
  - changed files: `src/spec_dock/assets/spec_dock/docs/phase_requirement.md`; `src/spec_dock/assets/spec_dock/docs/phase_design.md`; `src/spec_dock/assets/spec_dock/docs/phase_plan.md`; `src/spec_dock/assets/spec_dock/docs/phase_plan_initiative.md`; `src/spec_dock/assets/spec_dock/docs/phase_plan_epic.md`; `src/spec_dock/assets/spec_dock/docs/phase_plan_issue.md`; `src/spec_dock/assets/spec_dock/docs/authoring/decision-routing.md`; mirror 7 files under `spec-dock/docs/`
  - closure delta: `C273-001`, `C273-002`, `C273-004`, `C273-005`, `C273-010` の phase-level thin link、scope ownership 迷子防止、Epic plan handoff readiness を追加した。
  - worker note: `No material implementation decisions beyond the approved plan.`
  - verification: provider / mirror 対応ペアの `diff -q` -> no diff。`rg -n "authoring/scope-layering\\.md|Issue-local|draft-design|draft-plan|pre-start"` で必要語を確認。対象 docs の `git diff --check` passed。
- S05 planning / clarification skills thin links: completed。
  - delegated role: `doc-writer` Galileo (`019f226d-7fed-70a1-b149-27536bfce250`)
  - changed files: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`; `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`; mirror 4 files under `.agents/skills/`
  - closure delta: `C273-003`, `C273-004`, `C273-005`, `C273-008`, `C273-009` の source-grounded / 日本語ファースト guidance、evidence-only reminder、pre-start draft handoff、canonical Issue docs 非先取り reminder を追加した。
  - worker note: `No material implementation decisions beyond the approved plan.`
  - verification: provider / mirror 4 ペアの `diff -q` -> no diff。`rg -n "authoring/scope-layering\\.md|draft-design|draft-plan|Issue-local|path index|evidence-only"` と initiative-planning 向け `rg -n "scope-layering\\.md|Source-grounded read|日本語ファースト"` で必要語を確認。
- S06 final template links and mirror sync: completed。
  - delegated role: `doc-writer` Ampere (`019f2272-111b-7e40-8df8-cb777d766178`)
  - changed files: `src/spec_dock/assets/spec_dock/templates/README.md`; `src/spec_dock/assets/spec_dock/templates/epic/plan.md`; `src/spec_dock/assets/spec_dock/templates/epic/design.md`; `src/spec_dock/assets/spec_dock/templates/initiative/design.md`; `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`; mirror 5 files under `spec-dock/templates/`
  - closure delta: `C273-001`, `C273-002`, `C273-003`, `C273-005`, `C273-006`, `C273-010` の template-level thin link、Issue-local draft path index、skip / fallback evidence、pre-start canonical Issue boundary を追加した。
  - worker note: template-only boundary を維持し、tests / docs / skills / report は触らなかった。
  - verification: provider / mirror 5 ペアの `diff -q` -> no diff。`rg -n "docs/authoring/scope-layering\\.md|draft-design|draft-plan|Issue-local|path index|pre-start|fallback"` で必要語を確認。対象 templates の `git diff --check` passed。
- S07 drift / wording cleanup: completed。
  - delegated roles: `doc-writer` Hypatia (`019f2274-a6b9-79c3-be47-9a397760cb4c`); `dev-coder` Faraday (`019f2277-3818-72b3-a450-4b793fd2761a`)
  - changed files: `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`; `spec-dock/docs/authoring/scope-layering.md`; `tests/unit/infra/test_init_update.py`
  - closure delta: `C273-005`, `C273-006`, `C273-007`, `C273-010` の日本語主文ガード、古い placeholder 期待値、`scope-layering.md` provider/mirror parity coverage を現行仕様へ合わせた。
  - worker note: `No material implementation decisions beyond the approved plan.`
  - verification: `diff -q src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md spec-dock/docs/authoring/scope-layering.md` -> no diff。`uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> passed。`git diff --check -- tests/unit/infra/test_init_update.py` -> passed。
- S91 reviewer repair: completed。
  - changed files: `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`; `.agents/skills/spec-dock-initiative-planning/SKILL.md`; `tests/unit/infra/test_init_update.py`; this `report.md`
  - closure delta: final reviewer P1/P2 を解消し、planning skill 4 種すべてと `scope-layering.md` mirror parity を durable verification 対象にした。
  - verification: initiative-planning provider / mirror `diff -q` -> no diff。focused pytest 2 件 passed。`git diff --check` passed。
- S90 verification / report evidence: completed。
  - verification: focused pytest 2 件、`./spec-dock/scripts/spec-dock validate`、`./spec-dock/scripts/spec-dock assurance verify`、`git diff --check` passed。
  - remaining before finish: final fresh reviewer gates and `issue finish`。

## 検証
- 実施済み:
  - `./spec-dock/scripts/spec-dock deps check iss-00273` -> ready。
  - `./spec-dock/scripts/spec-dock assurance classify --stage requirement` -> `authorized_profile: standard`。
  - `./spec-dock/scripts/spec-dock assurance compose --artifact all` -> design / plan / report changed。
  - `./spec-dock/scripts/spec-dock assurance verify` -> passed。
  - `./spec-dock/scripts/spec-dock validate` -> passed（`nodes=178`）。
  - `git diff --check` -> passed。
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> failed as expected（S01 Red）。
  - `diff -q src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md spec-dock/docs/authoring/scope-layering.md` -> passed（no diff）。
  - workflow docs provider / mirror 5 ペアの `diff -q` -> passed（no diff）。
  - phase / authoring docs provider / mirror 対応ペアの `diff -q` -> passed（no diff）。
  - planning / clarification skills provider / mirror 4 ペアの `diff -q` -> passed（no diff）。
  - template provider / mirror 5 ペアの `diff -q` -> passed（no diff）。
  - `rg -n "authoring/scope-layering\\.md|docs/authoring/scope-layering\\.md|draft-design|draft-plan|Issue-local|path index|pre-start|evidence-only" ...` -> 期待語の存在を確認。
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> passed。
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets` -> passed。
  - `./spec-dock/scripts/spec-dock validate` -> passed（`nodes=178`）。
  - `./spec-dock/scripts/spec-dock assurance verify` -> passed（`authorized_profile: standard`）。
  - `git diff --check` -> passed。
  - reviewer repair 後: `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> passed。
  - reviewer repair 後: `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets` -> passed。
  - reviewer repair 後: `git diff --check` -> passed。
- 未実施:
  - final reviewer re-check。

## 完了 / PR
- Issue完了: 未実施。
- PR作成: 未実施。この Epic は `iss-00276` でまとめて PR delivery を扱う。
