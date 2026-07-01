---
種別: 設計書（Issue）
ID: "iss-00261"
タイトル: "Artifact domain model and filename contract"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00261 Artifact domain model and filename contract — 設計ドラフト

## 設計要約
- Future `Artifact` と legacy `DiscussionDoc` を domain level で分離する。
- 新規 artifact domain module が type catalog、filename parse/generate、artifact id、collision suffix、malformed candidate detection を所有する。
- Existing `discussion_docs.py` は legacy validation owner として残し、この Issue では緩めない。

## 変更面
- Provider source:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/artifacts.py` を追加する想定。
  - `domain/__init__` 相当の export が必要なら最小追加する。
- Tests:
  - `tests/unit/domain/` または既存 domain runtime lane に artifact domain tests を追加する。
- 禁止:
  - command / template / validation runtime への接続は後続 Issue に残す。

## 設計契約
- DES-261-001: `ArtifactType` catalog は future creation surface の単一 source として使える pure domain contract にする。
- DES-261-002: Blank filename は `blank` token を含めず、frontmatter/template identity で blank を表す前提を domain が支える。
- DES-261-003: Typed filename と blank filename は parse/generate が round-trip する。
- DES-261-004: Artifact id namespace は legacy discussion doc id namespace と分離する。
- DES-261-005: malformed / duplicate detection は validate Issue で再利用できる pure helper にする。

## テスト戦略
- Unit tests:
  - supported/unsupported type catalog.
  - typed and blank parse/generate round-trip.
  - collision suffix.
  - malformed timestamp/type/slug.
  - duplicate artifact id detection.
  - legacy discussion examples remain untouched.

## 後続 Issue への引き渡し
- `iss-00262` は type names and filename expectations を template catalog に使う。
- `iss-00263` は parse/generate and collision helper を command creation に使う。
- `iss-00265` は malformed / duplicate helper を validation に接続する。
