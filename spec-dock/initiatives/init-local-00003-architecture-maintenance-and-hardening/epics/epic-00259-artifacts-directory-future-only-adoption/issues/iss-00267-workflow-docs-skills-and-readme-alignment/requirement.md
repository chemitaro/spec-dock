---
種別: 要件定義書（Issue）
ID: "iss-00267"
タイトル: "Workflow docs skills and README alignment"
関連GitHub: ["#267"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00259", "init-local-00003"]
Issue Grade: "standard"
---

# iss-00267 Workflow docs skills and README alignment — Issue 要件定義

## 目的
Shipped workflow docs、rules、README、template guidance、repo-local / installed skills を `new artifact` / `artifacts/` future surface に揃え、remaining `new doc` references を removed / legacy / historical として分類する。

## 上位 trace
- Epic requirements: E-RQ-002, E-RQ-008.
- Epic acceptance criteria: E-AC-003, E-AC-008.
- Depends on: `iss-00263`, `iss-00266`.

## スコープ
- 必須:
  - Provider-side docs under `src/spec_dock/assets/spec_dock/docs/` を更新する。
  - Provider-side install_root skills under `src/spec_dock/assets/install_root/.agents/skills/` を更新する。
  - README / guide / workflow / rules / template guidance の command examples を `new artifact` に揃える。
  - remaining `new doc` references を removed-command tests、legacy/historical examples、または削除対象として分類する。
  - Dogfooding mirror は provider-side source と整合する範囲で確認/更新する。
- 対象外:
  - Runtime behavior implementation。
  - new scaffold behavior implementation。
  - dogfooding command smoke。

## 受け入れ条件
- AC-267-001 guidance:
  - 新規 working artifact creation の guidance は `new artifact` / `artifacts/` を示す。
- AC-267-002 legacy wording:
  - `discussions/` は historical / legacy compatible surface として説明され、新規作成先として推奨されない。
- AC-267-003 new doc classification:
  - `new doc` references は削除済み command、legacy historical reference、または runtime removal test として分類されている。
- AC-267-004 skills:
  - shipped skills and repo-local mirror は future delegated output boundary と矛盾しない。
- AC-267-005 docs/spec alignment:
  - docs が accepted ADR / Epic requirement/design/plan と一致する。

## 検証期待
- `rg "new doc|new artifact|discussions|artifacts"` classification evidence.
- Provider/mirror comparison where applicable.
- docs/spec `spec-reviewer` alignment。

## 依存
- `iss-00263`, `iss-00266`。
