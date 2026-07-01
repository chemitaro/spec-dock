---
種別: 設計書（Issue）
ID: "iss-00262"
タイトル: "Artifact templates and rules"
Issue Grade: "standard"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Plan: ["plan.md"]
関連Report: ["report.md"]
親: ["epic-00259", "init-local-00003"]
---

# iss-00262 Artifact templates and rules — 設計ドラフト

## 設計要約
- Provider-side `templates/artifacts/` を future working artifact templates の正本にする。
- `blank` は filename token ではなく template/frontmatter identity として扱う。
- draft-* は issue profile-aware template routing へ接続できるように source boundary を定義し、preflight 実行は `iss-00263` に残す。

## 変更面
- Provider source:
  - `src/spec_dock/assets/spec_dock/templates/artifacts/`
  - `src/spec_dock/assets/spec_dock/templates/README.md`
  - `src/spec_dock/assets/spec_dock/docs/rules/**` または equivalent rules source.
- Dogfooding mirror:
  - `spec-dock/templates/` and docs mirror は provider update/verification 対象。
- Tests:
  - template presence / source routing / README structural assertions.

## 設計契約
- DES-262-001: supported catalog 全 type に template または explicit routing がある。
- DES-262-002: `scratch` は future artifact template catalog に含めない。
- DES-262-003: ADR template は future `artifacts/` original と accepted ADR authority を表現できる。
- DES-262-004: `artifacts/rules.md` は future default と legacy preservation を同時に説明する。
- DES-262-005: draft-* template routing は issue scope `.assurance.json` / authorized profile preflight を前提にする。

## テスト戦略
- Structural tests for expected template files/routing.
- README/rules inspection with `rg`.
- Rendering tests are allowed if existing template renderer has a focused test seam.

## 後続 Issue への引き渡し
- `iss-00263` は templates/routing を command rendering に使う。
- `iss-00264` は `artifacts/rules.md` を scaffold default に使う。
