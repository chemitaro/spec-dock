---
種別: 実装報告書（Issue）
ID: "iss-00272"
タイトル: "Redesign Epic Requirement Design Plan Templates"
関連GitHub: ["#272"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00272 Epic テンプレート再設計 — レポート

## 進捗サマリー
- Issue scaffold を作成した。
- 正規 `requirement.md` を作成した。
- 旧 canonical `design.md` / `plan.md` に置かれていた pre-start draft body は、Issue-local `draft-design` / `draft-plan` artifact へ移した。
- Canonical `design.md` / `plan.md` は `awaiting-assurance-compose` placeholder に戻した。
- `assurance classify --stage requirement` / `assurance compose --artifact all` / `assurance verify` を実行し、runtime authorized profile は `standard` と判定された。
- Epic / Issue planning 上の suggested grade は `strict` のため、specialist draft evidence と fresh reviewer gate を追加して扱う。
- `system-architect` / `implementation-planner` の draft artifacts を採用し、canonical `design.md` / `plan.md` を Issue 固有の正本へ更新した。
- Pasteur (`019f2239-917a-7542-a289-e7996c269cef`) による fresh `spec-reviewer` gate で `review_status: pass` となった。
- provider-side Epic templates と checked-in dogfooding mirror を更新した。
- focused template contract test、mirror parity test、targeted wording inspection、SpecDock validate、`git diff --check` が成功した。
- Issue完了、PR作成は未実施。

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|
| D-272-001 | resolved | scope | この Issue の正本は `requirement.md` であり、`design.md` / `plan.md` は実行時に正規化する先行ドラフトである。 | ユーザー指示、Issue Planning workflow | applied | `issue start` 後に `iss-00271` の結果を取り込み、正規設計・正規計画へ更新する。 |
| D-272-002 | resolved | operation | この Issue では PR を作成せず、完了後に `issue finish` で `iss-00273` へバトンを渡す。 | Epic plan の1PR delivery方針、dependency chain | applied | final PR delivery は `iss-00276` が扱う。 |
| D-272-003 | resolved | assurance | runtime assurance は `authorized_profile: standard` だが、Epic plan の suggested grade は `strict` であるため、標準profileに加えて specialist draft evidence と fresh reviewer gate を維持する。 | `assurance classify --stage requirement`, Epic plan | applied | reviewer gate で整合性を確認する。 |

## Evidence Adoption Ledger（証跡採用台帳）
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-272-001 | adopted | `epic-00270` canonical docs | `requirement.md` / `design.md` / `plan.md` | Epic の Slice 02 handoff を Issue 要件と pre-start seed へ落とした。要件は正本として採用し、design / plan seed は evidence-only artifact として保持する。 | `epic-00270/requirement.md`, `epic-00270/design.md`, `epic-00270/plan.md` | Issue開始時に `iss-00271` の結果を反映する。 |
| EAL-272-002 | adopted | dependency chain | `plan.md` | この Issue は `iss-00271` の後続であり、PRなしで `iss-00273` へ渡すリレー設計を採用した。 | `spec-dock deps add --from iss-00272 --to iss-00271` | 実行時に前段の完了証跡を確認する。 |
| EAL-272-003 | adopted | Epic EAL-023 / local validation commands | `report.md` | Batch planning artifact の検証は Epic-level evidence として記録済みであり、この Issue では実装検証とは分けて参照する。 | `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`); `deps check epic-00270` / `deps check iss-00276` -> expected blocked | Issue固有の実装検証は `issue start` 後に行う。 |
| EAL-272-PREVIOUS-ISSUE | adopted | `iss-00271` completion evidence | `design.md` / `plan.md` | `iss-00271` は `issue finish` 済みで、Initiative template 語彙、reviewer fixes、provider / mirror parity の完了差分が現在 branch に存在する。 | `issue finish` output for `iss-00271`, commit `10e17424`, `deps check iss-00272` -> `ready=true` | 実装前 S00 gate として採用する。 |
| EAL-00272-DESIGN | partially_adopted | migrated pre-start canonical body | `design.md` | 旧 canonical `design.md` body の target files、AC対応、禁止事項、実装時論点を採用した。正本設計は system-architect draft と現物調査を踏まえて再構成した。 | `artifacts/20260702t081002z-draft-design-epic-template-redesign-pre-start-seed.md` | 実装後 reviewer gate で確認する。 |
| EAL-00272-PLAN | partially_adopted | migrated pre-start canonical body | `plan.md` | 旧 canonical `plan.md` body の実行順とバトン設計を採用した。正本計画は implementation-planner draft と現物調査を踏まえて再構成した。 | `artifacts/20260702t081003z-draft-plan-epic-template-redesign-pre-start-seed.md` | 実装後 reviewer gate で確認する。 |
| EAL-272-DESIGN-DRAFT | adopted | system-architect draft | `design.md` | AC対応、設計判断、boundary / contract model、template contract、互換性を採用した。final authority claims は採用していない。 | `artifacts/20260702t093309z-draft-design-epic-template-redesign-system-architect-design-draft.md` | Fresh `spec-reviewer` で正本設計を確認する。 |
| EAL-272-PLAN-DRAFT | partially_adopted | implementation-planner draft | `plan.md` | TDD / verification ladder の考え方は採用したが、汎用 Standard scaffold が中心のため、この Issue 固有の実行計画へ再構成した。 | `artifacts/20260702t093345z-draft-plan-implementation-plan-epic-template-redesign.md` | Fresh `spec-reviewer` で正本計画を確認する。 |
| EAL-272-ASSURANCE | adopted | assurance commands | `design.md` / `plan.md` / `report.md` | `assurance classify` は `authorized_profile: standard` を返し、`assurance compose` と `assurance verify` は成功した。Epic suggested grade は `strict` のため追加reviewer gateを維持する。 | `assurance classify --stage requirement`, `assurance compose --artifact all`, `assurance verify` | 実装前に fresh `spec-reviewer` を通す。 |
| EAL-272-IMPLEMENTATION | adopted | approved issue plan | Epic templates / tests | provider templates、dogfooding mirror、focused regression assertion を approved plan の範囲内で更新した。 | `src/spec_dock/assets/spec_dock/templates/epic/{requirement,design,plan}.md`, `spec-dock/templates/epic/{requirement,design,plan}.md`, `tests/unit/infra/test_init_update.py` | Review gates と `issue finish` を実施する。 |

## Spec Authoring Gate（仕様 authoring ゲート）
| phase | investigated_facts | open_questions | adoption_decision | reviewer_verdict | blocking | promotion_decision |
|---|---|---|---|---|---|---|
| requirement | Epic handoff、accepted ADR、`iss-00271` 完了差分を確認した。 | none | adopted | pass | no | execute approved plan |
| design | system-architect draft、pre-start seed、現物テンプレートを確認した。 | none | adopted | pass | no | execute approved plan |
| plan | implementation-planner draft、pre-start seed、実行順と検証梯子を確認した。 | none | adopted | pass | no | execute approved plan |

## Grade Specialist Evidence Gate
| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| standard | system-architect / implementation-planner | used | `artifacts/20260702t093309z-draft-design-epic-template-redesign-system-architect-design-draft.md`; `artifacts/20260702t093345z-draft-plan-implementation-plan-epic-template-redesign.md`; canonical `design.md` / `plan.md` に採用判断を反映 | pass | ready |

- runtime authorized profile: `standard`
- planning suggested grade: `strict`
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要
- 現在状態: system-architect draft と implementation-planner draft を取得し、report EAL に採用判断を記録した。
- readiness への影響: draft artifact の存在だけでは execution-ready ではない。正規 `design.md` / `plan.md` と fresh reviewer gate により実装可否を判断する。

## Delegated Draft Evidence（委任ドラフト証跡）
| created_by_role | scope_id | artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | fallback_decision | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00272 | `artifacts/20260702t093309z-draft-design-epic-template-redesign-system-architect-design-draft.md` | active issue docs; epic templates; initiative templates | `design.md` | source input evidence only（adopted） | `design.md` | passed | source input integrated into canonical `design.md`; draft itself is evidence-only | none | none | canonical artifact fresh reviewer gate（pass）; canonical docs hold authority | execute approved plan via canonical artifact; draft remains evidence-only |
| implementation-planner | iss-00272 | `artifacts/20260702t093345z-draft-plan-implementation-plan-epic-template-redesign.md` | active issue docs; epic templates; tests | `plan.md` | source input evidence only（partially_adopted） | `plan.md` | passed | source input integrated into canonical `plan.md` after main orchestrator inspection; draft itself is evidence-only | none | none | canonical artifact fresh reviewer gate（pass）; canonical docs hold authority | execute approved plan via canonical artifact; draft remains evidence-only |
| migrated pre-start seed | iss-00272 | `artifacts/20260702t081002z-draft-design-epic-template-redesign-pre-start-seed.md` | pre-start canonical body | `design.md` | historical input only（partially_adopted） | `design.md` | passed by manual reconciliation | manual-authored canonical docs used for readiness after main orchestrator inspection; seed itself is evidence-only | manual-authored canonical docs used for readiness | none | canonical artifact fresh reviewer gate（pass）; canonical docs hold authority | execute approved plan via canonical artifact; seed remains evidence-only |
| migrated pre-start seed | iss-00272 | `artifacts/20260702t081003z-draft-plan-epic-template-redesign-pre-start-seed.md` | pre-start canonical body | `plan.md` | historical input only（partially_adopted） | `plan.md` | passed by manual reconciliation | manual-authored canonical docs used for readiness after main orchestrator inspection; seed itself is evidence-only | manual-authored canonical docs used for readiness | none | canonical artifact fresh reviewer gate（pass）; canonical docs hold authority | execute approved plan via canonical artifact; seed remains evidence-only |

## Reviewer Gate Status（レビュアーゲート状態）
| gate | reviewer | reviewer_role | freshness | state | risk_acceptance | promotion_decision | note |
|---|---|---|---|---|---|---|---|
| planning | Huygens (`019f2232-b236-73f2-b5c7-616f6633b485`) | spec-reviewer | superseded | fail | no | re-review after plan repair | P1: 未実施 gate を pass と記録していた点、plan の step contract が粗い点を修正した。 |
| planning-recheck | Linnaeus (`019f2236-4c61-7690-b29d-e9bdd6188436`) | spec-reviewer | superseded | fail | no | re-review after evidence repair | P1: delegated draft の pass 表記と `iss-00271` 完了前提の S00 固定不足を修正した。 |
| planning-final | Pasteur (`019f2239-917a-7542-a289-e7996c269cef`) | spec-reviewer | fresh | pass | no | execute approved plan | 直前 P1 2件の解消を確認し、`review_status: pass`。 |
| post-implementation | Dalton (`019f2240-aea2-7071-9769-a269ca3fae03`) | spec-reviewer | superseded | fail | no | re-review after report authority repair | P1: delegated draft evidence が raw artifact を reviewer pass として読める点を修正した。 |
| post-implementation-recheck | Kuhn (`019f2243-a163-7013-88e3-bf1a0314ca48`) | spec-reviewer | superseded | pass | no | continue code / QA review | raw artifact authority boundary、template contract、mirror parity、forbidden wording、handoff fields の整合を確認した。 |
| code-review | Kant (`019f2243-e3e5-77f0-8497-23b80d9b7c35`) | code-reviewer | superseded | pass | no | fix P2 then re-review | P2: `契約ポートフォリオ` を `## 契約` 配下の `###` に移した。 |
| qa-review | Mill (`019f2243-e4a1-7253-9f55-7b07b4964ed0`) | qa-reviewer | superseded | fail | no | fix test assertions and record fresh reviewer pass | P1: fresh post-implementation pass 未記録、P2: forbidden wording の negative assertion 強化。 |
| code-review-recheck | Mencius (`019f2246-100b-7d12-8e29-5cfcbe524de5`) | code-reviewer | superseded | pass | no | fix P2 then re-review | P2: 重複した `失敗 / 移行 / rollback` H2 を既存 `失敗設計` / `移行戦略` へ統合した。 |
| spec-review-final | Ramanujan (`019f2246-d967-76f0-a703-a89c611407fe`) | spec-reviewer | fresh | pass | no | execute approved plan; finish after final gates | AC/EC、parent Epic handoff、provider/mirror parity、forbidden wording、report authority repair を確認し findings なし。 |
| qa-review-final | Euler (`019f2246-da2c-72a3-8687-071c736d0a71`) | qa-reviewer | fresh | pass | no | record fresh gate before finish | AC-001..007、Red/Green、mirror parity、negative wording、validate、diff-check evidence を確認。P2: fresh pass の report 記録をこの行で解消。 |
| code-review-final | Halley (`019f224a-b282-7251-9964-7f19ba976b71`) | code-reviewer | fresh | pass | no | finish | P2: Epic plan の Issue-level TDD / private implementation design 文言を必須前提にしない表現へ修正済み。最終 findings なし。 |

## 実装記録
### Step Evidence
| step | 状態 | 実施内容 | 証跡 |
|---|---|---|---|
| S00 | done | `iss-00271` 完了証跡、assurance、delegated draft、fresh spec-reviewer gate を確認した。 | `deps check iss-00272` -> ready, `assurance verify` -> ok, Pasteur `review_status: pass` |
| S01 | done | Epic template contract assertion を `tests/unit/infra/test_init_update.py` に追加した。最初の focused test は既存 template に `capability / model envelope` 等が不足して失敗したため Red evidence として採用する。 | `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> failed, then passed |
| S02 | done | Epic requirement template に capability / model envelope、artifact authority、downstream Issue seed、日本語ファースト guidance を追加した。 | `src/spec_dock/assets/spec_dock/templates/epic/requirement.md`, `spec-dock/templates/epic/requirement.md` |
| S03 | done | Epic design template に cross-Issue boundary、design slice catalog、contract portfolio、artifact adoption、failure design の rollback boundary、test strategy を追加した。 | `src/spec_dock/assets/spec_dock/templates/epic/design.md`, `spec-dock/templates/epic/design.md` |
| S04 | done | Epic plan template に Issue handoff package、suggested grade、dependencies、integration checkpoints、final quality gate を追加した。 | `src/spec_dock/assets/spec_dock/templates/epic/plan.md`, `spec-dock/templates/epic/plan.md` |
| S05 | done | provider templates と dogfooding mirror の parity を維持し、日本語主見出し、dogfooding ID なし、dangling scope-layering link なしを確認した。 | mirror parity test、targeted `rg` inspection |
| S06 | done | post-implementation reviewer findings を反映した。`契約ポートフォリオ` の見出し階層、失敗/移行/rollback の重複、Issue-level TDD / private implementation design の必須前提に見える文言、forbidden wording negative assertions を修正した。 | Kant / Mencius / Meitner / Halley code review、Mill / Euler QA review、Ramanujan spec review |

## 検証
- 実施済み:
  - Batch planning artifact validation: Epic EAL-023 に従い `./spec-dock/scripts/spec-dock validate` が成功した（`nodes=178`）。
  - Dependency-chain confirmation: Epic EAL-023 に従い `deps check epic-00270` / `deps check iss-00276` は前段Issue未完了で blocked となり、リレー依存どおりであることを確認した。
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> failed（Red evidence）後、passed。
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets` -> passed。
  - `rg -n "iss-00272|iss-00273|^## [A-Za-z]|docs/authoring/scope-layering\\.md|mandatory DDD|mandatory EDA|TDD cycle|private class / file design|## 失敗 / 移行 / rollback|private implementation design は各 Issue plan で具体化する" src/spec_dock/assets/spec_dock/templates/epic spec-dock/templates/epic tests/unit/infra/test_init_update.py` -> template 本体には該当なし。テスト内の negative assertion のみ検出。
  - `./spec-dock/scripts/spec-dock validate` -> passed（`nodes=178`）。
  - `git diff --check` -> passed。
- 未実施:
  - `tests/unit/infra/test_init_update.py` 全体。focused contract と mirror parity でこの Issue の受け入れ条件を確認した。

## 完了 / PR
- Issue完了: 実装、focused verification、Spec / Code / QA reviewer gate は完了。`issue finish` 実行待ち。
- PR作成: 未実施。この Epic は `iss-00276` でまとめて PR delivery を扱う。
