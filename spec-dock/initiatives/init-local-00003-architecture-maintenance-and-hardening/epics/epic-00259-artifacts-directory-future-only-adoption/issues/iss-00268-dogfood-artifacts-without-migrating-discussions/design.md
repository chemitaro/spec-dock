---
種別: 設計書（Issue）
ID: "iss-00268"
タイトル: "Dogfood artifacts without migrating discussions"
Issue Grade: "standard"
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00268 Dogfood artifacts without migrating discussions — 設計

## 目的と判断
この Issue は provider 実装を追加する Issue ではなく、この repo の dogfooding workspace で Epic 00259 の完成動作を実証する evidence Issue である。対象は active Issue `iss-00268` 自身とする。理由は、現時点で `iss-00268` には legacy `discussions/` が存在し、`artifacts/` はまだ存在しないため、`new artifact` による on-demand `artifacts/` 作成と legacy `discussions/` non-migration を最小の副作用で観測できるからである。

Epic report closeout はこの Issue の成果物だが、main orchestrator の直接編集境界により、Epic-level report の恒久更新は `doc-writer` に委任する。main orchestrator は Issue-level docs、command execution、evidence integration、reviewer gate orchestration を担当する。

## 現行構造
- Active Issue:
  - `spec-dock/active/issue` -> `iss-00268-dogfood-artifacts-without-migrating-discussions`
  - `discussions/` exists as legacy / preservation surface.
  - `artifacts/` is absent before dogfooding smoke and should be created on demand by `new artifact`.
- Epic scope:
  - Epic-level `artifacts/` already contains accepted ADRs and historical delegated draft evidence.
  - Epic-level `discussions/` contains prior interview / discussion evidence and must not be moved.
- Runtime behavior already implemented by prior Issues:
  - `new artifact` command and `new doc` removal: `iss-00263`.
  - future scaffold artifacts default: `iss-00264`.
  - validation / sync / ADR mirror: `iss-00265`.
  - delegated authoring artifacts boundary: `iss-00266`.
  - docs/skills guidance: `iss-00267`.

## 変更方針
- Baseline snapshot:
  - Record `iss-00268` legacy `discussions/` files and directory/symlink state before artifact creation.
  - Record that `iss-00268/artifacts/` does not exist before smoke if true.
- Artifact command smoke:
  - Create one `blank` artifact under `iss-00268/artifacts/` for raw/freeform dogfood evidence.
  - Create one typed non-ADR artifact under `iss-00268/artifacts/`; use `research` for source-grounded dogfooding evidence.
  - Verify filenames follow artifact grammar and files are direct children of `artifacts/`.
- Safe draft smoke:
  - Use Issue-scope `new artifact draft-requirement --issue iss-00268` after assurance verification.
  - Confirm it writes an artifact draft and does not write canonical `requirement.md`.
  - Do not run delegated authoring diff guard smoke unless needed; delegated boundary was already covered by `iss-00266`, and generating an additional delegated draft is not required when draft smoke satisfies AC-268-005.
- Non-migration evidence:
  - Compare before/after `discussions/` path list and symlink state.
  - Treat additions/changes under `artifacts/` as expected and any move/delete/rename/link rewrite under `discussions/` as blocking.
- Validate / sync:
  - Run `./spec-dock/scripts/spec-dock validate`.
  - Run `./spec-dock/scripts/spec-dock sync`.
  - Inspect generated/projection output enough to confirm canonical docs, future artifacts, and legacy discussions remain distinct.
- Epic closeout:
  - Delegate Epic `report.md` updates to `doc-writer` after dogfooding evidence exists.
  - Record all executable Issue commits / closes and this Issue dogfooding evidence.
  - Prepare Epic-wide review gate before the single Epic PR.

## 設計契約
| ID | 契約 | 対応 AC | 対象面 | 検証 |
|---|---|---|---|---|
| DES-268-001 | active Issue `iss-00268` is the dogfood target, and `new artifact` creates `artifacts/` on demand | AC-268-001, AC-268-002 | runtime command smoke | command output / path inspection |
| DES-268-002 | before/after evidence proves legacy `discussions/` paths are not moved, renamed, deleted, or symlink-rewritten | AC-268-003 | dogfooding workspace | sorted path snapshot comparison |
| DES-268-003 | blank and typed artifacts are direct-child Markdown files with generated artifact IDs / filenames | AC-268-001, AC-268-002 | `artifacts/` | filename/frontmatter inspection |
| DES-268-004 | draft smoke uses Issue-scope `draft-requirement` and does not mutate canonical docs | AC-268-005 | draft artifact command | command output / canonical diff inspection |
| DES-268-005 | validate and sync pass after dogfood artifact creation | AC-268-004 | validation / projection | command output |
| DES-268-006 | Epic report closeout is delegated to `doc-writer` and captures all Issue completion evidence before the Epic PR | AC-268-006 | Epic report | doc-writer evidence / reviewer gate |
| DES-268-007 | no provider runtime/source/test changes are made in this Issue unless a dogfood failure proves a prior Issue incomplete | AC-268-006 | repo diff | diff inspection |

## 対象ファイル / 生成物
- Dogfooding artifacts:
  - `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00259-artifacts-directory-future-only-adoption/issues/iss-00268-dogfood-artifacts-without-migrating-discussions/artifacts/*.md`
- Read-only baseline target:
  - same Issue `discussions/*.md` and `discussions/rules.md`
- Issue-level evidence:
  - this Issue's `design.md`, `plan.md`, `report.md`, `.assurance.json`
- Epic closeout delegated target:
  - `spec-dock/active/epic/report.md`

## 非対象 / 禁止事項
- Provider runtime/source/test implementation changes.
- Legacy `discussions/` migration, move, rename, delete, symlink rewrite, or content rewrite.
- `new doc` restoration or compatibility shim.
- Per-Issue PR creation.
- Epic PR creation before Epic-wide final review gates pass.

## テスト / レビュー戦略
- Command evidence:
  - `new artifact blank`, `new artifact research`, `new artifact draft-requirement`.
  - `validate`, `sync`, and focused path/frontmatter inspections.
- Snapshot evidence:
  - before/after sorted `discussions/` path list.
  - before/after `artifacts/` path list.
- Review:
  - `spec-reviewer` validates dogfooding evidence sufficiency and Epic closeout alignment.
  - `qa-reviewer` validates Epic-wide evidence and test/verification coverage before PR.
  - `code-reviewer` is required for Epic-wide diff review because the overall Epic contains runtime/test changes from earlier Issues, even if Issue 268 itself is docs/evidence/dogfood only.

## 後続への引き渡し
- This is the final executable Issue of Epic 00259.
- After Issue finish and commit, run Epic-wide PR preparation flow and create one Epic-level PR only if final gates pass.
