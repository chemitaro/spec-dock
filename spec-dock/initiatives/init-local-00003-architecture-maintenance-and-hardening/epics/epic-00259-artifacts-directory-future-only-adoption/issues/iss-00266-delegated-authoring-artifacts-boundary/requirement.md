---
種別: 要件定義書（Issue）
ID: "iss-00266"
タイトル: "Delegated authoring artifacts boundary"
関連GitHub: ["#266"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00266 Delegated authoring artifacts boundary — Issue 要件定義

## 目的
system-architect / implementation-planner / delegated authoring output の permission boundary、diff guard、validation、report evidence guidance を scope-local `artifacts/` direct child に切り替える。

## 上位 trace
- Epic requirements: E-RQ-005, E-RQ-008.
- Epic acceptance criteria: E-AC-006, E-AC-008.
- Epic design decisions: D-003, D-006.
- Depends on: `iss-00263`, `iss-00265`.

## スコープ
- 必須:
  - delegated authoring domain/application contract を `scope_dir / "artifacts"` direct child Markdown 1件へ変更する。
  - symlink, nested path, non-Markdown, existing update, delete, rename/copy, mixed staged/unstaged, unmerged, out-of-scope, forbidden root を拒否する。
  - required provenance fields と supported roles を維持する。
  - `discussions/` delegated output は future path として fail し、legacy/historical evidence としてだけ扱う。
  - report Evidence Adoption Ledger / Delegated Draft Evidence guidance を artifacts output に合わせる。
- 対象外:
  - `new artifact` command の一般作成実装。
  - docs/skills 全面改訂。
  - existing legacy discussion evidence の移動。

## 受け入れ条件
- AC-266-001 allow:
  - diff guard は exactly one new direct-child Markdown under target `artifacts/` を許可する。
- AC-266-002 reject:
  - forbidden paths / side effects / existing updates / canonical docs writes は fail-closed になる。
- AC-266-003 provenance:
  - created_by_role, scope_id, source_paths, intended_targets, adoption_status, reflected_to, diff_guard_result が validation される。
- AC-266-004 discussions future fail:
  - future delegated output to `discussions/` は compliant output として採用されない。
- AC-266-005 report guidance:
  - report ledger は artifacts draft adoption / rejection / diff guard result を記録できる。

## 検証期待
- Unit tests for delegated_authoring domain/application.
- Scripted diff-guard tests for positive and negative side effects.
- Docs/spec alignment inspection for report guidance。

## 依存
- `iss-00263`, `iss-00265`。
