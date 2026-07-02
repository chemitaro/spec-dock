---
種別: 設計書（Issue）
ID: "iss-00273"
タイトル: "Update Scope Layering Reference Planning Skills And Workflow Docs"
関連GitHub: ["#273"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00273 Scope-layering reference と planning guidance 更新 — Issue 設計

## 位置づけ
- この Issue は、Initiative / Epic / Issue の責務境界、decision radius、artifact authority、handoff flow を、1つの狭い provider-side reference と薄い参照で運用できるようにする。
- Runtime command behavior の変更、Issue profile template の変更、PR 作成は扱わない。
- `assurance classify --stage requirement` の runtime authorized profile は `standard` だが、Issue requirement と Epic plan は `strict` 相当の specialist evidence を要求しているため、system-architect / implementation-planner draft と fresh reviewer gate を維持する。

## 正本と権限境界
| Surface | 権限 | この Issue の扱い |
|---|---|---|
| `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` | scope responsibility / decision routing reference | 新規 provider-side reference として作成する。長い責務モデルはここに集約する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_*.md` | lifecycle / scope-specific governance | reference への thin link と、その workflow 固有の意味だけを追加する。 |
| `src/spec_dock/assets/spec_dock/docs/phase_*.md` / `docs/authoring/*.md` | phase minimum / authoring contract | scope-layering が必要な箇所に薄く接続し、field-level 契約を再定義しない。 |
| `src/spec_dock/assets/install_root/.agents/skills/*` | agent operational first-read spine | source-grounded clarification、artifact authority、日本語ファースト、draft handoff の入口を追加する。 |
| `src/spec_dock/assets/spec_dock/templates/{initiative,epic}/` | authoring scaffold | `iss-00271` / `iss-00272` の接続点へ dangling でない thin link を追加する。 |
| `artifacts/`, research, interview, delegated draft | evidence only | canonical docs、accepted ADR、`report.md` EAL、fresh reviewer gate に採用されるまで authority を持たない。 |

Provider 側の source of truth は `src/spec_dock/assets/...` に置く。Dogfooding 側の `spec-dock/docs/...` / `spec-dock/templates/...` は確認・同期対象であり、provider 実装の正本ではない。

## 要件対応
| 要件 | 設計対応 |
|---|---|
| `I273-AC-001` | `docs/authoring/scope-layering.md` を追加し、Initiative / Epic / Issue の責務、decision radius、authority flow、anti-rules を狭く説明する。 |
| `I273-AC-002` | workflow docs / phase docs / skills / templates には全文を複製せず、thin link と local implication だけを置く。 |
| `I273-AC-003` | planning / clarification skills に、source-grounded read、調査で分かることを質問しない、一問ずつの interview、採用知識の外部化を明示する。 |
| `I273-AC-004` | raw `artifacts/`、research、interview、delegated draft は canonical authority ではないことを reference / workflow / skills に明示する。 |
| `I273-AC-005` | 日本語ファースト authoring を docs / skills / artifact guidance へ反映し、識別子や固有名詞の過翻訳は避ける。 |
| `I273-AC-006` | Initiative / Epic templates の scope-layering 接続点を実 reference へ接続し、dangling link を残さない。 |
| `I273-AC-007` | focused pytest、link / grep inspection、`validate` で reference 存在、主要リンク、重複回避、authority leak 欠如を確認する。 |
| `I273-AC-008` | Epic planning handoff に Issue-local `draft-design` / `draft-plan` path index、または blocked / fallback evidence を含める。 |
| `I273-AC-009` | Issue Start 前に canonical Issue `design.md` / `plan.md` 本文を作らず、pre-start seed は Issue-local artifacts として扱う境界を明記する。 |

## 採用する設計判断
- `D273-001`: `scope-layering.md` は operational reference であり、ADR の代替ではない。ADR は durable decision record のまま維持する。
- `D273-002`: workflow docs は lifecycle authority、phase docs は authoring gate、skills は operational entrypoint、templates は scaffold として分離する。
- `D273-003`: delegated draft / research / interview は evidence-only であり、canonical adoption は EAL と fresh reviewer gate を経由する。
- `D273-004`: Grill With Docs 的なインタビューは、SpecDock の active docs、parent docs、artifacts、ADR、report EAL、一問ずつの interview lifecycle に合わせて表現する。
- `D273-005`: 日本語ファーストは本文・説明・判断理由の方針であり、path、command、code identifier、SpecDock 固定語、外部固有名詞は原文保持を許容する。
- `D273-006`: Epic planning handoff は、canonical Issue docs を事前本文化せず、Issue-local `draft-design` / `draft-plan` の path index と採用待ち状態を渡す。

## 変更対象
| 対象 | 変更意図 |
|---|---|
| `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md` | scope ownership、decision radius、authority flow、anti-rules を集約する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` | Initiative planning から reference へ薄く誘導する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` | Epic handoff に `draft-design` / `draft-plan` path index と canonical placeholder boundary を追加する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` | Issue が parent envelope を再定義しないこと、draft artifact 採用後に canonical docs へ進むことを明示する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_clarification.md` | source-grounded grill loop と artifact adoption / 日本語ファーストを接続する。 |
| `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md` | delegated evidence / report evidence gate と scope-layering reference の発見性を上げる。 |
| `src/spec_dock/assets/spec_dock/docs/phase_*.md`, `docs/authoring/*.md` | 必要箇所だけ reference へ接続し、重複説明は避ける。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-{initiative,epic,issue}-planning/SKILL.md` | scope-layering reference、source-grounded authoring、draft artifact boundary を first-read guidance に加える。 |
| `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md` | 一問ずつの interview、調査優先、artifact 外部化、日本語ファーストを補強する。 |
| `src/spec_dock/assets/spec_dock/templates/initiative/*`, `src/spec_dock/assets/spec_dock/templates/epic/*` | 前段 Issue の接続点へ実 reference link を追加する。 |
| `spec-dock/docs/...`, `spec-dock/templates/...` | dogfooding mirror として provider 変更と同期する。 |
| `tests/unit/infra/test_init_update.py` | reference 存在、thin link、forbidden wording、provider/mirror parity を固定する。 |

## 禁止領域
- `src/spec_dock/assets/spec_dock/templates/issue*` と Issue profile templates。
- runtime command behavior、dependency algorithm、`.meta.json` 直編集、`.assurance.json` 手編集。
- full responsibility table を各 workflow / phase / skill / template に複製すること。
- DDD / EDA を SpecDock の標準アーキテクチャとして記述すること。
- `artifacts/` を accepted authority と誤認させる文言。
- PR 作成、GitHub mutation、merge 操作。

## 検証設計
- focused test:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
- 必要時の broad check:
  - `uv run pytest tests/unit/infra/test_init_update.py`
- SpecDock:
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
- targeted inspection:
  - reference link と `draft-design` / `draft-plan` guidance の存在。
  - authority leak、DDD / EDA mandatory、dogfooding-specific ID、識別子翻訳強制の不在。

## リスクと対策
| リスク | 対策 |
|---|---|
| reference が大きくなり workflow docs の代替になってしまう | `scope-layering.md` は responsibility / routing / anti-rules に限定し、lifecycle detail は workflow docs に残す。 |
| thin link が少なすぎて発見できない | workflow / phase / skill / template の入口に最小リンクを置く。 |
| link を増やしすぎて重複が増える | full table は reference のみに置き、他 surface は 1-3 文の local implication に留める。 |
| template contract を再設計して前段 Issue の範囲を超える | 前段で用意した接続点への link 追加に限定し、再設計が必要なら停止して再計画する。 |
| runtime behavior 変更が必要になる | `iss-00274` / `iss-00275` へ回し、この Issue では guidance と tests に留める。 |

## 後続へのバトン
- `iss-00274` は、この Issue の `scope-layering.md`、draft artifact boundary、handoff-ready / execution-ready 語彙を使って Epic execution readiness を更新する。
- `iss-00275` は、reference / link / authority flow を smoke tests と品質ゲートの対象にする。
