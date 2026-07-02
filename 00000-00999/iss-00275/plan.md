---
種別: 実装計画書（Issue）
ID: "iss-00275"
タイトル: "Add Upstream Planning Smoke Tests And Template Validation"
関連GitHub: ["#275"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00275 Upstream planning smoke tests と template validation 追加 — Issue 実装計画

## 実装方針
- この Issue は、`iss-00271` から `iss-00274` の成果を対象に、構造的に検出できる欠落を focused tests / smoke checks で固定する validation slice である。
- 既存テストで閉じられる要件は no-op / characterization evidence として扱い、不足がある場合だけ最小の Red を追加する。
- 自然言語の意味品質は fresh `spec-reviewer` の finding として扱い、machine tests は構造条件に限定する。
- この Issue では PR を作成しない。完了後は `issue finish` で `iss-00276` へ引き渡す。

## Plan Readiness
| 入力 | 状態 | 採用判断 |
|---|---|---|
| `requirement.md` | 具体化済み | `I275-AC-001..011` / `I275-EC-001..004` を実装閉包に採用 |
| `design.md` | 本計画と同時に正規化済み | `DES-001..012` を implementation contract として採用 |
| system-architect draft | produced | `artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md` を部分採用 |
| implementation-planner draft | produced | `artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` を部分採用 |
| Epic plan | `iss-00275` active 時点で有効 | Slice 05 の許可変更面、禁止変更、検証期待を採用 |

## 仕様固定クロージャ
| Closure | 要件 | 設計 | 閉じる内容 | 検証 |
|---|---|---|---|---|
| `CLOS-275-001` | `I275-AC-001` | `DES-001` | scope-layering reference の存在と主要 surface からの到達性 | `test_init_update.py` / smoke |
| `CLOS-275-002` | `I275-AC-002` | `DES-002` | full responsibility table 重複、raw artifact authority、decision-only ready wording の構造検出 | focused tests / grep |
| `CLOS-275-003` | `I275-AC-003` | `DES-003` | DDD / EDA を mandatory にしない template contract | focused tests |
| `CLOS-275-004` | `I275-AC-004` | `DES-004` | Issue handoff package と Option B readiness separation | focused tests / smoke |
| `CLOS-275-005` | `I275-AC-005` | `DES-005` | 日本語ファースト guidance と原文保持境界 | focused tests / reviewer |
| `CLOS-275-006` | `I275-AC-006` | `DES-006` | semantic quality を machine-only にしない境界 | plan / report / reviewer |
| `CLOS-275-007` | `I275-AC-007` | `DES-007` | command 結果、未実施、失敗理由、次アクションの report 記録 | `report.md` |
| `CLOS-275-008` | `I275-AC-008` | `DES-008` | pre-start canonical draft body / marker absence | focused tests / grep |
| `CLOS-275-009` | `I275-AC-009` | `DES-009` | Issue-local draft artifact path index | report / handoff check |
| `CLOS-275-010` | `I275-AC-010` | `DES-010` | `new artifact draft-*` canonical non-mutation と fail-closed | `test_new.py` |
| `CLOS-275-011` | `I275-AC-011` | `DES-011` | Strict / Critical は draft artifact path だけで ready にならない | `test_workflow_state.py` / `test_workflow.py` |
| `CLOS-275-012` | `I275-EC-001..004` | `DES-003`, `DES-005`, `DES-006`, `DES-012` | false-positive 境界と raw manual artifact hygiene | tests / reviewer / git status |

## 実装ステップ
| Step | 種別 | 作業内容 | 許可変更面 | 完了条件 |
|---|---|---|---|---|
| S00 | intake | 前段 `iss-00271..iss-00274` の成果、既存 tests、active Issue docs を確認する | docs / tests の read-only | report に coverage baseline を要約できる |
| S01 | characterization | `test_init_update.py` の既存 assertion が `CLOS-275-001..005` をどこまで閉じるか確認する | `tests/unit/infra/test_init_update.py` | gap / no-op evidence を分類済み |
| S02 | Red / Green | 構造 gap がある場合だけ scope-layering、authority、DDD / EDA、日本語ファースト、handoff package の tests を追加・修正する | `tests/unit/infra/test_init_update.py` と必要最小 provider assets | focused test が意図した gap を検出し、修正後に通る |
| S03 | characterization | `new artifact draft-design` / `draft-plan` の profile template、canonical non-mutation、missing / invalid / stale assurance fail-closed を確認する | `tests/cli_runtime/test_new.py` | 既存 coverage または追加 test で `CLOS-275-010` が閉じる |
| S04 | Red / Green | Strict / Critical readiness が draft artifact path だけで進まないことを確認し、不足があれば tests を追加する | `tests/unit/domain/test_workflow_state.py`, `tests/cli_runtime/test_workflow.py` | `CLOS-275-011` が閉じる |
| S05 | minimal repair | Red が出た provider docs / templates / skills / runtime だけを最小修正する | `src/spec_dock/assets/spec_dock/docs/`, `templates/`, `src/spec_dock/assets/install_root/.agents/skills/`, runtime only if proven | focused tests が Green |
| S90 | validation | focused commands、`validate`、必要な smoke read-through、git status を実行する | no new production edit | 結果を report に記録 |
| S91 | review | fresh `spec-reviewer` で coverage relevance、false-positive risk、日本語ファースト境界を確認する | no code edit | `review_status: pass` または findings 修正済み |
| S99 | handoff | PR なしで `issue finish` し、`iss-00276` へ証跡と未解決リスクを渡す | SpecDock lifecycle / report | active issue が完了し、後続が開始可能 |

## Focused command ladder
以下を狭い順に実行し、結果を `report.md` に記録する。

```sh
uv run pytest tests/unit/infra/test_init_update.py -k 'template or scope or japanese or draft or readiness'
uv run pytest tests/cli_runtime/test_new.py -k 'draft_requirement or profile_drafts or artifact_stdout'
uv run pytest tests/cli_runtime/test_validate.py -k delegated_draft
uv run pytest tests/unit/domain/test_workflow_state.py -k 'specialist or delegated_draft or strict or critical'
uv run pytest tests/cli_runtime/test_workflow.py -k 'grade_evidence or assurance or workflow_status'
./spec-dock/scripts/spec-dock validate
```

変更面が広がった場合だけ、次を追加する。

```sh
uv run pytest tests/unit/infra/test_init_update.py
uv run pytest tests/cli_runtime/test_new.py
uv run pytest tests/cli_runtime/test_workflow.py
uv run pytest tests/unit/domain/test_workflow_state.py
uv run pytest tests/cli_runtime
uv run pytest tests/unit
```

## Red 代替方針
| 対象 | Red 分類 | 代替証拠 |
|---|---|---|
| 既存テストで既に閉じている draft artifact fail-closed | covered-existing | focused test 実行結果と report の no-op rationale |
| docs / skill の導線としての読みやすさ | inspect-only | smoke read-through summary と reviewer finding |
| 日本語ファーストの意味的十分性 | reviewer-only | fresh `spec-reviewer` |
| raw manual artifact hygiene | inspect-only | `git status --short` と report 記録 |

## 停止条件
- `iss-00271..iss-00274` の成果が未完了、または accepted ADR と矛盾する。
- tests が Epic 設計の矛盾を示し、局所修正では閉じられない。
- runtime behavior の変更が新しい public command surface、metadata migration、destructive operation を必要とする。
- 1PR delivery 方針の破綻がこの Issue 中に明確になる。

## 完了条件
- `CLOS-275-001..012` が test、smoke、reviewer、report evidence のいずれかで閉じている。
- 未実施または失敗した command がある場合は、理由と次アクションが `report.md` にある。
- raw manual smoke artifacts が staged / tracked されていない。
- Fresh `spec-reviewer` が `review_status: pass` を返している、または findings が修正済みである。
- `./spec-dock/scripts/spec-dock validate` が成功している。
- PR を作らず `iss-00276` へ handoff できる。
