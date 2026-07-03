---
種別: 実装報告書（Issue）
ID: "iss-00271"
タイトル: "Redesign Initiative Requirement Design Plan Templates"
関連GitHub: ["#271"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00271 Initiative テンプレート再設計 — レポート

## 進捗サマリー
- Issue scaffold を作成した。
- 正規 `requirement.md` を作成した。
- 旧 canonical `design.md` / `plan.md` に置かれていた pre-start draft body は、Issue-local `draft-design` / `draft-plan` artifact へ移した。
- `assurance classify --stage requirement` / `assurance compose --artifact all` / `assurance verify` を実行し、runtime authorized profile は `standard` と判定された。
- Epic / Issue planning 上の suggested grade は `strict` のため、specialist draft evidence と fresh reviewer gate を追加して扱う。
- `system-architect` / `implementation-planner` の draft artifacts を採用し、canonical `design.md` / `plan.md` を Issue 固有の正本へ更新した。
- James (`019f2218-e191-7702-a11d-f7fed6209e84`) による fresh `spec-reviewer` gate で `review_status: pass` となった。
- provider-side Initiative templates と checked-in dogfooding mirror を更新した。
- focused template contract test、mirror parity test、targeted wording inspection、SpecDock validate が成功した。
- 実装後の `spec-reviewer` / `code-reviewer` / `qa-reviewer` はいずれも `review_status: pass` となった。P2/P3 指摘は report と template wording へ反映した。
- Issue完了、PR作成は未実施。

## 仕様解釈・判断台帳
| ID | 状態 | 種別 | 判断 / 解釈 | 根拠 | 処置 | フォローアップ |
|---|---|---|---|---|---|---|
| D-271-001 | resolved | scope | この Issue の正本は `requirement.md` / `design.md` / `plan.md` であり、pre-start seed は Issue-local artifacts として採否を記録する。 | ユーザー指示、accepted ADR、Issue Planning workflow | applied | 実装は正規 `plan.md` に従って進める。 |
| D-271-002 | resolved | operation | この Issue では PR を作成せず、完了後に `issue finish` で `iss-00272` へバトンを渡す。 | Epic plan の1PR delivery方針 | applied | final PR delivery は `iss-00276` が扱う。 |
| D-271-003 | resolved | assurance | runtime assurance は `authorized_profile: standard` だが、Epic plan の suggested grade は `strict` であるため、標準profileに加えて specialist draft evidence と fresh reviewer gate を維持する。 | `assurance classify --stage requirement`, Epic plan | applied | reviewer gate で整合性を確認する。 |

## Evidence Adoption Ledger（証跡採用台帳）
| ID | 採用状態 | 出所 | 対象 | 判断理由 | 証跡 | 次アクション |
|---|---|---|---|---|---|---|
| EAL-271-001 | adopted | `epic-00270` canonical docs | `requirement.md` / `design.md` / `plan.md` | Epic の Slice 01 handoff を Issue 要件、設計、計画へ落とした。 | `epic-00270/requirement.md`, `epic-00270/design.md`, `epic-00270/plan.md` | 実装時に逸脱があれば report に記録する。 |
| EAL-271-002 | adopted | accepted ADRs | `requirement.md` | architecture-neutral、complete-understanding、Japanese-first の制約を Issue 要件へ継承した。 | `artifacts/20260702t024118z-adr-architecture-neutral-template-authoring-policy.md`, `artifacts/20260702t025127z-adr-complete-understanding-before-canonical-authoring.md`, `artifacts/20260702t040113z-adr-japanese-first-spec-authoring-policy.md` | 実行時の reviewer gate で再確認する。 |
| EAL-271-003 | deferred | Epic EAL-023 / local validation commands | historical batch planning set | Batch planning artifact の検証は historical evidence として参照する。現在の検証は Issue 固有の実装後に取り直す。 | `./spec-dock/scripts/spec-dock validate` -> pass (`nodes=178`); `deps check epic-00270` / `deps check iss-00276` -> expected blocked | Issue固有の実装検証をこの report に記録する。 |
| EAL-00271-DESIGN | partially_adopted | migrated pre-start canonical body | `design.md` | 旧 canonical `design.md` body の target files、AC対応、禁止事項を採用した。正本設計は system-architect draft と現物調査を踏まえて再構成した。 | `artifacts/20260702t081000z-draft-design-initiative-template-redesign-pre-start-seed.md` | 実装後 reviewer gate で確認する。 |
| EAL-00271-PLAN | partially_adopted | migrated pre-start canonical body | `plan.md` | 旧 canonical `plan.md` body の実行順とバトン設計を採用した。正本計画は implementation-planner draft と現物調査を踏まえて再構成した。 | `artifacts/20260702t081001z-draft-plan-initiative-template-redesign-pre-start-seed.md` | 実装後 reviewer gate で確認する。 |
| EAL-271-DESIGN-DRAFT | adopted | system-architect draft | `design.md` | AC対応、設計判断、境界、非対象、検証観点、リスクを採用した。source path inventory と final authority claims は採用していない。 | `artifacts/20260702t090407z-draft-design-initiative-template-redesign-system-architect-design-draft.md` | Fresh `spec-reviewer` で正本設計を確認する。 |
| EAL-271-PLAN-DRAFT | partially_adopted | implementation-planner draft | `plan.md` | step order、target files、test ladder、finish gate を採用した。draft artifact の `diff_guard_result: failed` は成功証跡として採用しない。 | `artifacts/20260702t090341z-draft-plan-implementation-plan-initiative-template-redesign.md` | Fresh `spec-reviewer` で正本計画を確認する。 |
| EAL-271-ASSURANCE | adopted | assurance commands | `design.md` / `plan.md` / `report.md` | `assurance classify` は `authorized_profile: standard` を返し、`assurance compose` と `assurance verify` は成功した。Epic suggested grade は `strict` のため追加reviewer gateを維持する。 | `assurance classify --stage requirement`, `assurance compose --artifact all`, `assurance verify` | 実装前に fresh `spec-reviewer` を通す。 |
| EAL-271-IMPLEMENTATION | adopted | approved issue plan | Initiative templates / tests | provider templates、dogfooding mirror、focused regression assertion を approved plan の範囲内で更新した。 | `src/spec_dock/assets/spec_dock/templates/initiative/{requirement,design,plan}.md`, `spec-dock/templates/initiative/{requirement,design,plan}.md`, `tests/unit/infra/test_init_update.py` | Review gates と `issue finish` を実施する。 |
| EAL-271-REVIEW-FIXES | adopted | post-implementation reviewers | `report.md` / Initiative templates | QA の Red evidence 記録不足、code-reviewer の dogfooding Issue ID 混入、spec-reviewer の diff guard / reviewer gate 記録不足を修正した。 | Curie / Tesla / Kierkegaard review results, `report.md`, `src/spec_dock/assets/spec_dock/templates/initiative/design.md` | focused tests と validate を再実行する。 |

## Spec Authoring Gate（仕様 authoring ゲート）
| phase | investigated_facts | open_questions | adoption_decision | reviewer_verdict | blocking | promotion_decision |
|---|---|---|---|---|---|---|
| requirement | Epic handoff、accepted ADR、Issue start 後の再点検を確認した。 | none | adopted | pass | no | execute approved plan |
| design | system-architect draft、pre-start seed、現物テンプレートを確認した。 | none | adopted | pass | no | execute approved plan |
| plan | implementation-planner draft、pre-start seed、実行順と検証梯子を確認した。 | none | adopted | pass | no | execute approved plan |

## Grade Specialist Evidence Gate
| Grade | required specialist / fallback | usage | evidence | fresh spec-reviewer verdict | execution readiness |
|---|---|---|---|---|---|
| strict | system-architect / implementation-planner | used | `artifacts/20260702t090407z-draft-design-initiative-template-redesign-system-architect-design-draft.md`; `artifacts/20260702t090341z-draft-plan-implementation-plan-initiative-template-redesign.md`; canonical `design.md` / `plan.md` に採用判断を反映 | pass | ready |

- issue grade: `strict`
- specialist obligation: system-architect / implementation-planner または manual fallback evidence が必要
- 現在状態: system-architect draft と implementation-planner draft を取得し、report EAL に採用判断を記録した。
- readiness への影響: draft artifact の存在だけでは execution-ready ではない。正規 `design.md` / `plan.md` と fresh reviewer gate により実装可否を判断する。

## Delegated Draft Evidence（委任ドラフト証跡）
| created_by_role | scope_id | artifact_path | source_paths | intended_targets | adoption_status | reflected_to | diff_guard_result | integration_result | fallback_decision | blockers | reviewer_result | promotion_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| system-architect | iss-00271 | `artifacts/20260702t090407z-draft-design-initiative-template-redesign-system-architect-design-draft.md` | active issue docs; initiative templates | `design.md` | adopted | `design.md` | passed | source input integrated | none | none | pass | execute approved plan |
| implementation-planner | iss-00271 | `artifacts/20260702t090341z-draft-plan-implementation-plan-initiative-template-redesign.md` | active issue docs; initiative templates | `plan.md` | not used for delegated readiness | `plan.md` | failed | source input integrated by main orchestrator inspection | manual-authored canonical docs used for readiness | none | pass | execute manual-authored canonical docs |
| migrated pre-start seed | iss-00271 | `artifacts/20260702t081000z-draft-design-initiative-template-redesign-pre-start-seed.md` | pre-start canonical body | `design.md` | not used for delegated readiness | `design.md` | not_run | source input integrated by main orchestrator inspection | manual-authored canonical docs used for readiness | none | pass | execute manual-authored canonical docs |
| migrated pre-start seed | iss-00271 | `artifacts/20260702t081001z-draft-plan-initiative-template-redesign-pre-start-seed.md` | pre-start canonical body | `plan.md` | not used for delegated readiness | `plan.md` | not_run | source input integrated by main orchestrator inspection | manual-authored canonical docs used for readiness | none | pass | execute manual-authored canonical docs |

- Archimedes の draft artifact はローカル未追跡 artifact の混在により機械的 diff guard を成功証跡としては採用していない。採用部分は main orchestrator inspection と James の fresh spec-reviewer pass を通して `plan.md` に再記述した。

## Reviewer Gate Status（レビュアーゲート状態）
| gate | reviewer | reviewer_role | freshness | state | risk_acceptance | promotion_decision | note |
|---|---|---|---|---|---|---|---|
| planning | James (`019f2218-e191-7702-a11d-f7fed6209e84`) | spec-reviewer | fresh | pass | no | execute approved plan | Issue requirement / design / plan / report、pre-start seed artifacts、specialist draft artifacts、親 Epic docs を対象に確認した。 |
| post-implementation-spec | Curie (`019f2224-fc01-74a3-813c-5d4d345ae34c`) | spec-reviewer | fresh | pass | no | execute approved plan | P2 指摘として diff guard 表現と post-review ledger 更新を受け、report に反映した。 |
| post-implementation-code | Tesla (`019f2225-22cc-7131-ab33-3836c9c28923`) | code-reviewer | fresh | pass | no | execute approved plan | P2 指摘として shipped template の dogfooding Issue ID を汎用表現へ置換した。 |
| post-implementation-qa | Kierkegaard (`019f2225-45d9-7c83-b048-fc810eb9de4a`) | qa-reviewer | fresh | pass | no | execute approved plan | P3 指摘として Red evidence の未記録を report に追記した。 |

## 実装記録
### Step Evidence
| step | 状態 | 実施内容 | 証跡 |
|---|---|---|---|
| S01 | done | Initiative template contract assertion を `tests/unit/infra/test_init_update.py` に追加した。最初の focused test は既存 template に `Epic handoff seed` 等が不足し、さらに日本語主見出し guard で失敗したため Red evidence として採用する。 | `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> failed, then passed |
| S02 | done | Initiative requirement template に strategic purpose、source-of-truth、capability landscape、stakeholder trigger、Epic handoff seed、日本語ファースト guidance を追加した。 | `src/spec_dock/assets/spec_dock/templates/initiative/requirement.md`, `spec-dock/templates/initiative/requirement.md` |
| S03 | done | Initiative design template に scope boundary、decision authority、artifact adoption、reviewer gate、Epic boundary、scope-layering 接続点を追加した。 | `src/spec_dock/assets/spec_dock/templates/initiative/design.md`, `spec-dock/templates/initiative/design.md` |
| S04 | done | Initiative plan template に handoff readiness、fresh reviewer gate、controlled re-slicing、draft artifact handoff、final PR / closeout 方針を追加した。 | `src/spec_dock/assets/spec_dock/templates/initiative/plan.md`, `spec-dock/templates/initiative/plan.md` |
| S05 | done | provider templates と dogfooding mirror の parity を維持し、日本語主見出しと dangling scope-layering link なしを確認した。 | mirror parity test、targeted `rg` inspection |

### Parent Implementation Exception
- `doc-writer` / `dev-coder` への分離委任は、この実装差分が approved plan の狭い template / test 範囲に閉じており、主オーケストレータが直接編集しても追加の設計判断を発生させないため、親実装例外として扱った。
- 例外の補償として、focused tests、mirror parity、targeted wording inspection、fresh reviewer gates を必須にする。

## 検証
- 実施済み:
  - Batch planning artifact validation: Epic EAL-023 に従い `./spec-dock/scripts/spec-dock validate` が成功した（`nodes=178`）。
  - Dependency-chain confirmation: Epic EAL-023 に従い `deps check epic-00270` / `deps check iss-00276` は前段Issue未完了で blocked となり、リレー依存どおりであることを確認した。
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> passed。
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets` -> passed。
  - `rg -n "^## [A-Za-z]|docs/authoring/scope-layering\\.md|mandatory DDD|mandatory EDA|TDD cycle|private class / file design" src/spec_dock/assets/spec_dock/templates/initiative spec-dock/templates/initiative tests/unit/infra/test_init_update.py` -> template 本体には該当なし。テスト内の negative assertion のみ検出。
  - `./spec-dock/scripts/spec-dock validate` -> passed（`nodes=178`）。
  - Review fixes 後の再検証:
    - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold` -> passed。
    - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets` -> passed。
    - `rg -n "iss-00273|^## [A-Za-z]|docs/authoring/scope-layering\\.md|mandatory DDD|mandatory EDA|TDD cycle|private class / file design" src/spec_dock/assets/spec_dock/templates/initiative spec-dock/templates/initiative tests/unit/infra/test_init_update.py` -> template 本体には該当なし。テスト内の negative assertion のみ検出。
    - `./spec-dock/scripts/spec-dock assurance verify` -> ok（`authorized_profile: strict`, `reason: missing_assurance_contract`）。
    - `./spec-dock/scripts/spec-dock validate` -> passed（`nodes=178`）。
    - `git diff --check` -> passed。
- 未実施:
  - `tests/unit/infra/test_init_update.py` 全体。focused contract と mirror parity でこの Issue の受け入れ条件を確認した。

## 完了 / PR
- Issue完了: reviewer 指摘反映と再検証まで完了。`issue finish` 実行待ち。
- PR作成: 未実施。この Epic は `iss-00276` でまとめて PR delivery を扱う。
