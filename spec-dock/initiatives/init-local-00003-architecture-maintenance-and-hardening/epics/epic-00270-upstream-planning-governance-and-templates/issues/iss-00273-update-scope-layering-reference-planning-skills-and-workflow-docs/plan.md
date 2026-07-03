---
種別: 実装計画書（Issue）
ID: "iss-00273"
タイトル: "Update Scope Layering Reference Planning Skills And Workflow Docs"
関連GitHub: ["#273"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-02"
依存: ["requirement.md", "design.md"]
親: ["epic-00270", "init-local-00003"]
---

# iss-00273 Scope-layering reference と planning guidance 更新 — 実装計画

## 実行方針
- この Issue は docs / skills / templates / tests の guidance 更新であり、PR は作成しない。
- 実装は `doc-writer` を主担当に委任する。tests / scaffold assertion を変更する step は `code-reviewer` と `qa-reviewer` を final gate に含める。
- 親 Codex が直接変更する場合は、`report.md` に Parent Implementation Exception を事前記録する。
- 各 step の観測結果、Red / Green、reviewer 指摘、採用判断は `report.md` に記録する。

## Spec-Locked Closure Index
| Closure ID | 要件 | 閉じる内容 | 検証 |
|---|---|---|---|
| `C273-001` | `I273-AC-001` | `docs/authoring/scope-layering.md` が narrow reference として存在する。 | file existence, focused pytest, read-through |
| `C273-002` | `I273-AC-002`, `I273-EC-001` | workflow / phase / skill / template が全文重複せず thin link で誘導する。 | grep, spec-reviewer |
| `C273-003` | `I273-AC-003` | planning / clarification skills が source-grounded、一問ずつ、知識外部化を案内する。 | skill grep, spec-reviewer |
| `C273-004` | `I273-AC-004`, `I273-EC-002` | raw artifact / delegated draft は evidence-only として扱われる。 | negative grep, spec-reviewer |
| `C273-005` | `I273-AC-005`, `I273-EC-004` | 日本語ファースト guidance があり、識別子翻訳強制になっていない。 | grep, existing Japanese-primary checks |
| `C273-006` | `I273-AC-006` | Initiative / Epic templates の接続点が実 reference へつながる。 | focused pytest, mirror parity |
| `C273-007` | `I273-AC-007` | focused checks、validate、diff check が通る。 | pytest, validate, diff check |
| `C273-008` | `I273-AC-008` | Epic handoff が `draft-design` / `draft-plan` path index または fallback evidence を含む。 | workflow / skill grep |
| `C273-009` | `I273-AC-009` | pre-start canonical Issue `design.md` / `plan.md` 本文化を促さない。 | wording grep, spec-reviewer |
| `C273-010` | `I273-EC-003` | DDD / EDA mandatory wording を入れない。 | negative grep |

## 実装ステップ
| Step | 目的 | 主担当 | Closure | 主な検証 |
|---|---|---|---|---|
| `S00` | 計画正規化と evidence adoption | main orchestrator | all preflight | `deps check`, `assurance verify`, fresh `spec-reviewer` |
| `S01` | Red / characterization assertion を追加 | `dev-coder` または Parent Implementation Exception | `C273-001`, `C273-006`, `C273-008` | focused pytest expected Red |
| `S02` | `scope-layering.md` を provider / dogfooding mirror に追加 | `doc-writer` | `C273-001`, `C273-004`, `C273-005`, `C273-010` | file existence, read-through |
| `S03` | workflow docs に thin links と draft handoff boundary を追加 | `doc-writer` | `C273-002`, `C273-004`, `C273-008`, `C273-009` | workflow grep |
| `S04` | phase / authoring docs に最小リンクを追加 | `doc-writer` | `C273-002`, `C273-004` | docs grep |
| `S05` | planning / clarification skills を更新 | `doc-writer` | `C273-003`, `C273-004`, `C273-005`, `C273-008`, `C273-009` | skill grep |
| `S06` | Initiative / Epic templates の final thin link と mirror を同期 | `doc-writer` | `C273-006`, `C273-010` | focused pytest, mirror parity |
| `S07` | drift / wording cleanup | `doc-writer` | `C273-002`, `C273-004`, `C273-005`, `C273-010` | targeted negative grep, `git diff --check` |
| `S90` | 統合検証と report 更新 | main orchestrator | `C273-007` | pytest, validate, grep, diff check |
| `S99` | final Spec / Code / QA review と `issue finish` | main orchestrator | all | reviewer pass, `issue finish` |

## Step Contract

### S00: 計画正規化
- 実施:
  - `deps check iss-00273` で前段完了を確認する。
  - `assurance classify --stage requirement` / `assurance compose --artifact all` / `assurance verify` を実施する。
  - pre-start seed、system-architect draft、implementation-planner draft の採否を `report.md` EAL / Delegated Draft Evidence に記録する。
  - 正規 `design.md` / `plan.md` が Issue 固有であることを fresh `spec-reviewer` に確認させる。
- 停止条件:
  - `iss-00272` が finish 済みでない。
  - 正規 `design.md` / `plan.md` が template-only のまま。

### S01: Red / characterization assertion
- 変更候補:
  - `tests/unit/infra/test_init_update.py`
- 期待:
  - 既存状態では `scope-layering.md` が存在せず、template test も `docs/authoring/scope-layering.md` 不在を期待しているため Red になる。
- 注意:
  - dogfooding 固有 Issue ID を shipped template assertion に入れない。
  - Red が不適切な箇所は inspect-only evidence に切り替え、理由を `report.md` に残す。

### S02: Scope-layering reference
- 変更対象:
  - `src/spec_dock/assets/spec_dock/docs/authoring/scope-layering.md`
  - `spec-dock/docs/authoring/scope-layering.md`
- 内容:
  - Initiative / Epic / Issue の責務、decision radius、authority flow、anti-rules。
  - artifact authority flow。
  - Japanese-first guidance と identifier preservation。
  - DDD / EDA non-mandatory policy。

### S03: Workflow docs
- 変更対象:
  - `workflow_initiative.md`, `workflow_epic.md`, `workflow_issue.md`, `workflow_spec_authoring.md`, 必要なら `workflow_clarification.md`。
  - dogfooding mirror の同名 docs。
- 内容:
  - `authoring/scope-layering.md` への thin link。
  - `workflow_epic.md` の handoff package に Issue-local `draft-design` / `draft-plan` path index、skip / fallback evidence、canonical placeholder boundary を追加。
  - `workflow_issue.md` に parent envelope を再定義しない boundary を追加。

### S04: Phase / authoring docs
- 変更対象:
  - `phase_plan.md`, `phase_plan_initiative.md`, `phase_plan_epic.md`, `phase_plan_issue.md`, 必要な `phase_requirement.md` / `phase_design.md`。
  - `authoring/issue-plan.md`, `authoring/decision-routing.md`。
- 内容:
  - reference への薄い導線。
  - phase docs 内に責務表全文を複製しない。

### S05: Skills
- 変更対象:
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-initiative-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-epic-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-issue-planning/SKILL.md`
  - `src/spec_dock/assets/install_root/.agents/skills/spec-dock-clarification/SKILL.md`
  - `spec-dock-epic-execution` は `iss-00274` 境界を侵さない範囲だけ。
- 内容:
  - source-grounded read-first。
  - 調査で分かることを人間に聞かない。
  - 一問ずつの interview。
  - artifact externalization と EAL adoption。
  - Epic planning では pre-start canonical Issue `design.md` / `plan.md` 本文化を避け、Issue-local `draft-design` / `draft-plan` を渡す。

### S06: Templates and mirror
- 変更対象:
  - provider Initiative / Epic templates。
  - dogfooding mirror templates。
  - `tests/unit/infra/test_init_update.py`。
- 内容:
  - 前段 Issue が準備した接続点を actual reference link へ接続する。
  - full table を template に複製しない。

### S07: Drift control
- targeted grep:
  - `docs/authoring/scope-layering.md|authoring/scope-layering.md`
  - `draft-design|draft-plan|Issue-local`
  - `artifact.*canonical authority|authority: accepted|adoption_status: adopted`
  - `DDD / EDA を必須前提にする|mandatory DDD|mandatory EDA`
  - `iss-00271|iss-00272|iss-00273` in shipped templates。

### S90: Verification
- 実行:
  - `uv run pytest tests/unit/infra/test_init_update.py -k spec_document_templates_keep_policy_out_of_scaffold`
  - `uv run pytest tests/unit/infra/test_init_update.py -k checked_in_dogfooding_mirror_templates_match_provider_assets`
  - `uv run pytest tests/unit/infra/test_init_update.py`（shared assertion 影響が広い場合）
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - targeted `rg` inspections。
- skip 可能:
  - runtime command behavior を変更していない場合、`tests/cli_runtime/test_new.py` は未実施理由を記録してよい。

### S99: Final gate
- required reviewers:
  - `spec-reviewer`: requirement / design / plan / report / docs / skills / templates alignment。
  - `code-reviewer`: tests / scaffold assertion の妥当性。
  - `qa-reviewer`: AC/EC coverage と追加 integration test の要否。
- 完了:
  - `report.md` に全 Closure の evidence、reviewer pass、no PR 方針を記録する。
  - `./spec-dock/scripts/spec-dock issue finish` で `iss-00274` へ渡す。

## 禁止変更
- runtime command behavior。
- Issue profile templates。
- `.meta.json` / dependency graph の手編集。
- `.assurance.json` の手編集。
- PR 作成、push、merge、GitHub mutation。
- full responsibility table の各 surface への複製。

## Handoff
- `iss-00274` は `docs/authoring/scope-layering.md`、workflow_epic handoff wording、skills の draft artifact boundary を前提に Epic execution readiness を更新する。
- `iss-00275` は reference / link / authority flow / Japanese-first guidance を smoke checks の対象にする。
