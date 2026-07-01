---
種別: 設計書（Issue）
ID: "iss-00263"
タイトル: "New artifact command and new doc removal"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00263 New artifact command and new doc removal — 設計ドラフト

## 設計要約
- `new artifact` は `new doc` wrapper ではなく別 request/result/use case として追加する。
- `new doc` は parser/help/registry から削除し、custom migration hint を追加しない。
- draft-* creation は issue scope only とし、assurance/profile preflight failure は no-write fail-closed にする。

## 変更面
- Provider source:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
  - `application/contracts.py`, `application/create_node.py` or new artifact use case module.
  - presentation output module if needed.
  - assurance/profile helper reuse path.
- Tests:
  - `tests/cli_runtime/` for command behavior.
  - focused unit tests for request/use case no-write paths.

## 設計契約
- DES-263-001: command shape is `new artifact <type> --{initiative|epic|issue} <id> --title ... [--slug ...]`.
- DES-263-002: exactly one scope flag is accepted.
- DES-263-003: successful creation writes exactly one Markdown direct child under `<scope>/artifacts/`.
- DES-263-004: old nodes lacking `artifacts/` get on-demand setup without touching `discussions/`.
- DES-263-005: unsupported type, invalid slug, invalid scope, overwrite, missing profile, stale profile, and unsupported draft scope fail before writing.
- DES-263-006: `new doc` is absent from help and parser; the failure is normal unknown subcommand/argparse behavior.

## テスト戦略
- CLI happy paths for blank and typed artifacts.
- Full catalog parser/routing coverage.
- `new doc` help absence and invocation failure.
- no-write negative tests for unknown type, invalid scope, old-node setup failure, draft preflight failure.
- Draft issue-scope profile acceptance and initiative/epic unsupported failure.

## 後続 Issue への引き渡し
- `iss-00264` depends on command old-node setup and rules expectations.
- `iss-00265` validates the layouts created by this command.
- `iss-00266` reuses artifact output boundary for delegated authoring.
