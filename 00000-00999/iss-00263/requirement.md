---
種別: 要件定義書（Issue）
ID: "iss-00263"
タイトル: "New artifact command and new doc removal"
関連GitHub: ["#263"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00263 New artifact command and new doc removal — Issue 要件定義

## 目的
`spec-dock new artifact <type>` を runtime command として追加し、`new doc` を parser / help / registry から完全削除する。あわせて draft-requirement/design/plan の issue-scope `.assurance.json` / authorized profile preflight を `new artifact` 経由へ移行する。

## 上位 trace
- Epic requirements: E-RQ-001, E-RQ-003, E-RQ-004, E-RQ-005.
- Epic acceptance criteria: E-AC-001, E-AC-002, E-AC-003, E-AC-004, E-AC-006, E-AC-009.
- Epic design decisions: D-000, D-001, D-002, D-003.
- Depends on: `iss-00262` and accepted Epic ADR `artifacts/20260701t072851z-adr-artifact-domain-filename-template-contract.md`.

## スコープ
- 必須:
  - `CreateArtifactDocRequest/Result` と `create_artifact_doc` use case を追加する。
  - Epic ADR で確定済みの artifact type catalog、filename parser / generator、artifact id、collision handling、malformed candidate detection の command-time implementation を追加する。
  - `spec-dock new artifact <type> --{initiative|epic|issue} <id> --title "..." [--slug ...]` を追加する。
  - `new doc` は alias/shim/custom migration hint なしで parser/help/registry から削除する。
  - old node で `artifacts/` がない場合も on-demand に direct child Markdown artifact を作成できる。
  - no-overwrite / collision handling / no-write failure を守る。
  - draft-* は issue scope only とし、initiative/epic scope は preflight no-write で失敗する。
  - draft-* は独自の draft-only content templates を使わず、既存の requirement/design/plan template contract と Issue grade/profile-aware selection を使う。
  - missing/stale/invalid authorized profile は no-write fail-closed になる。
- 対象外:
  - new node scaffold default 変更。
  - validate/sync/ADR mirror の artifacts-aware 化。
  - delegated authoring diff guard 移行。

## 受け入れ条件
- AC-263-001 blank command:
  - `new artifact blank --issue <id> --title ...` が `<issue>/artifacts/<timestamp>-<slug>.md` を作成し、filename に `blank` を含めない。
- AC-263-002 typed command:
  - `new artifact research --epic <id> --title ...` が typed filename を作成する。
- AC-263-003 full catalog:
  - supported catalog 全 type が CLI/domain/template routing で扱われ、unknown type は no-write で fail する。
- AC-263-004 new doc removal:
  - `new --help` に `doc` が出ず、`new doc ...` は unknown subcommand / argparse error 相当で失敗し、custom migration hint は出ない。
- AC-263-005 draft safety:
  - `draft-requirement`, `draft-design`, `draft-plan` は issue scope で既存 requirement/design/plan template と profile-aware selection を使い、invalid profile は no-write fail-closed になる。
- AC-263-006 unsupported draft scope:
  - `new artifact draft-* --initiative/--epic` は書き込み前に失敗する。
- AC-263-007 old node setup:
  - legacy node lacking `artifacts/` に artifact を作成でき、既存 `discussions/` は移動/rename/delete/link rewrite されない。

## 検証期待
- CLI runtime tests for success, help, unknown command, negative no-write, old-node on-demand, draft assurance/profile paths.
- `uv run pytest tests/cli_runtime` focused lane。

## 依存
- `iss-00262`。
- Epic-level artifact domain / filename / draft template ADR。
