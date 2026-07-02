---
種別: 設計書（Issue）
ID: "iss-00275"
タイトル: "Add Upstream Planning Smoke Tests And Template Validation"
関連GitHub: ["#275"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00275 Upstream planning smoke tests と template validation 追加 — Issue 設計書

## 文書の位置づけ
- この文書は `iss-00275` の正規 Issue 設計書である。
- Issue 要件の `issue grade: strict` を採用し、runtime の assurance profile が `standard` と判定する場合でも、専門家ドラフトと fresh `spec-reviewer` gate を必要とする。
- Pre-start の `draft-design` / `draft-plan` は evidence-only artifact であり、canonical `design.md` / `plan.md` の代替ではない。
- この Issue では PR を作成しない。検証結果は `iss-00276` の final quality / PR delivery に渡す。

## 正本・根拠
| 種別 | パス・識別子 | この Issue への意味 |
|---|---|---|
| Issue 要件 | `requirement.md` | `I275-AC-001..011` と `I275-EC-001..004` の正本 |
| Epic 要件 | `epic-00270/requirement.md` | `E-RQ-003`, `E-RQ-004`, `E-RQ-005`, `E-RQ-007`, `E-RQ-009`, `E-RQ-010` を継承 |
| Epic 設計 | `epic-00270/design.md` | `D-001`, `D-002`, `D-003`, `D-006`, `D-008`, `D-009` を継承 |
| Epic 計画 | `epic-00270/plan.md` | Slice 05 の許可変更面、禁止変更、検証期待、後続 `iss-00276` へのバトン |
| ADR | `artifacts/20260702t074332z-adr-unified-draft-artifact-command-grade-role-policy.md` | `new artifact draft-*` を統一 primitive とし、actor obligation は workflow / EAL / reviewer gate で管理する |
| 設計ドラフト | `artifacts/20260702t114631z-draft-design-system-architect-upstream-planning-validation-design.md` | machine / smoke / reviewer 境界、検証対象、false-positive 境界を採用 |
| 計画ドラフト | `artifacts/20260702t114630z-draft-plan-implementation-planner-canonical-plan-draft.md` | milestone、closure、focused command、stop condition を採用 |

## 設計方針
- `[N] DES-001` Scope-layering は `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` を provider-side reference とし、workflow docs、phase docs、templates、skills は薄い参照に留める。
- `[N] DES-002` Authority / duplication guard は、raw artifact が canonical authority と読める文面、decision-only Issue が execution-ready と読める文面、full responsibility table の過剰重複を検査対象にする。
- `[N] DES-003` DDD / EDA は語彙そのものを禁止しない。mandatory section、mandatory process、標準前提化だけを検出対象にする。
- `[N] DES-004` Epic handoff は Issue-local `draft-design` / `draft-plan` path index、canonical placeholder boundary、handoff-ready / execution-ready 分離、Option B の structural blocker / reviewer finding 分離を持つ。
- `[N] DES-005` 日本語ファースト検査は本文 guidance の存在と原文保持境界を検査する。path、command、identifier、固定語、外部固有名詞の英語は許容する。
- `[N] DES-006` 自然言語の意味品質は machine-only 判定にしない。構造欠落は tests / smoke、意味的十分性は fresh reviewer finding として扱う。
- `[N] DES-007` `validate` と focused test の結果、未実施または失敗の理由と次アクションは `report.md` に記録する。
- `[N] DES-008` 未開始 Issue の canonical `design.md` / `plan.md` に `artifact_state: "draft-before-issue-start"` や pre-start draft body が残らないことを検査する。
- `[N] DES-009` Issue-local `draft-design` / `draft-plan` artifact path index が report / handoff package に残ることを検査する。
- `[N] DES-010` `new artifact draft-design` / `draft-plan` は canonical docs を変更せず、missing / invalid / stale `.assurance.json` では no-write fail-closed する。
- `[N] DES-011` Strict / Critical readiness は draft artifact の存在だけでは成立しない。specialist / manual fallback evidence と fresh reviewer pass を必要とする。
- `[N] DES-012` raw manual smoke workspace、logs、captures、temporary files は commit しない。必要な証跡は `report.md` へ要約する。

## 要件から設計への追跡
| 要件 | 設計 ID | 検証レベル |
|---|---|---|
| `I275-AC-001` | `DES-001` | machine test + smoke read-through |
| `I275-AC-002` | `DES-002` | machine test + reviewer |
| `I275-AC-003` | `DES-003` | machine test + reviewer |
| `I275-AC-004` | `DES-004` | machine test + smoke read-through |
| `I275-AC-005` | `DES-005` | machine test + reviewer |
| `I275-AC-006` | `DES-006` | reviewer + report evidence |
| `I275-AC-007` | `DES-007` | report evidence |
| `I275-AC-008` | `DES-008` | machine test / grep |
| `I275-AC-009` | `DES-009` | machine test + report evidence |
| `I275-AC-010` | `DES-010` | CLI runtime test |
| `I275-AC-011` | `DES-011` | domain / CLI workflow test |
| `I275-EC-001` | `DES-006` | reviewer boundary |
| `I275-EC-002` | `DES-003` | negative assertion boundary |
| `I275-EC-003` | `DES-005` | allow-list boundary |
| `I275-EC-004` | `DES-012` | git status / report evidence |

## Machine / Smoke / Reviewer の分担
| 分担 | 扱うもの | 扱わないもの |
|---|---|---|
| machine tests | ファイル存在、リンク導線、required headings、path index、canonical non-mutation、fail-closed、readiness gate の構造条件 | prose 全体の品質、文脈上の説得力 |
| smoke read-through | workflow docs、skills、templates が導線として読めること、manual evidence が要約されていること | raw manual workspace の追跡 |
| fresh reviewer | 意味的十分性、日本語ファーストの過不足、DDD / EDA 語彙の妥当性、false-positive risk | runtime の成功証跡の代替 |

## 変更対象と既存カバレッジ
| 対象 | 既存状態 | 今回の設計上の扱い |
|---|---|---|
| `tests/unit/infra/test_init_update.py` | provider docs / templates / skills の構造 assertion が集約されている | scope-layering、DDD / EDA non-mandatory、日本語ファースト、handoff package、Issue placeholder の不足を補う |
| `tests/cli_runtime/test_new.py` | `draft-design` / `draft-plan` の profile template、canonical state 除去、fail-closed を既に扱う | canonical non-mutation と no-write fail-closed が不足していれば補強する |
| `tests/unit/domain/test_workflow_state.py` | report evidence gate、Grade Specialist Evidence Gate を扱う | Strict / Critical が draft artifact path だけで ready にならないことを固定する |
| `tests/cli_runtime/test_workflow.py` | guidance-level blocking を扱う | grade evidence / assurance / workflow status の補助検証に使う |
| `tests/cli_runtime/test_validate.py` | delegated draft metadata の validate を扱う | semantic wording ではなく構造破綻だけを扱う |

## 非目標
- 自然言語品質を brittle な正規表現だけで合否判定しない。
- DDD / EDA の語彙そのものを禁止しない。
- 英字率や英語 token 数で日本語ファーストを判定しない。
- 新しい `compose-draft`、actor別 draft command、runtime readiness command をこの Issue の既定成果にしない。
- `validate` に semantic reviewer の責務を移さない。
- `iss-00276` が担当する final PR delivery をこの Issue で行わない。

## 実装計画への引き渡し
- まず既存 coverage を characterization し、既存 test で閉じられる要件は no-op evidence として `report.md` に残す。
- 構造的 gap がある場合だけ最小の Red を追加し、provider docs / templates / skills / runtime の該当面だけを修正する。
- runtime code 変更は、tests が canonical mutation、write-before-fail、stale assurance acceptance、draft-only readiness acceptance などの実挙動 gap を示した場合だけ許可する。
- 実装完了前に focused tests、`./spec-dock/scripts/spec-dock validate`、fresh `spec-reviewer` を通し、結果を `report.md` へ記録する。
