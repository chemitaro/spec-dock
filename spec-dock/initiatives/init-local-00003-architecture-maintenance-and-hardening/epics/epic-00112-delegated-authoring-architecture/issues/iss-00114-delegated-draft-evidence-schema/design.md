---
種別: 設計書（Issue）
ID: "iss-00114"
タイトル: "Delegated Draft Evidence Schema"
関連GitHub: ["#114"]
状態: "draft"
作成者: "Codex"
最終更新: "2026-05-23"
依存: ["requirement.md"]
親: ["epic-00112", "init-local-00003"]
---

# iss-00114 Delegated Draft Evidence Schema — 設計（HOW）

## 親 Diagram 参照
- Epic diagram:
  - `epic-00112/design.md` の component/module、provider dependency、draft lifecycle を参照する。
- 再利用する決定:
  - AD-001 Draft evidence, not authority。
  - AD-003 Role skill is canonical, host adapter is thin。
  - AD-005 Provider-first。

## 目的・制約
- 目的:
  - delegated draft lifecycle、structured draft artifact、report evidence、report template / active-none surfaces を固定する。
- 必須 / 禁止:
  - 必須: `src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md; src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md; src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md` を provider source として更新し、dogfooding mirrors は parity surface として確認する。
  - 禁止: write-capable delegation / runtime validation / `.github/agents` support の導入。
- 前提:
  - Depends on: iss-00113

## 既存実装 / 規約の理解
- 参照した実装 / docs:
  - `src/spec_dock/assets/spec_dock/docs/`
  - `src/spec_dock/assets/install_root/`
  - `spec-dock/docs/`, `.agents/`, `.codex/`
  - `tests/test_init_update.py`
- 現状理解:
  - provider assets が shipped source of truth。dogfooding workspace は検証面。
- 採用するパターン:
  - provider-first update、dogfooding parity inspection、fresh reviewer gate。
- 採用しないもの:
  - runtime enforcement first、host-specific long instruction duplication。
- 影響範囲:
  - src/spec_dock/assets/spec_dock/docs/workflow_spec_authoring.md; src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md; src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md; dogfooding mirrors

## 採用方針 / トレードオフ
- 論点:
  - docs/skill/template のどこに contract を置くか。
- 決定:
  - 正本 contract は provider assets に置き、dogfooding mirror は validation surface とする。
  - 実行時 enforcement より、v0 では Markdown contract + reviewer + tests/evidence を優先する。

## 依存関係分析
- file 依存:
  - 親 Epic requirement/design/plan に依存する。
  - この Issue の対象ファイルは後続 Issue の前提になる。
- 上流 / 前提:
  - iss-00113
- 下流 / 依存先:
  - 後続 Issues as defined in `epic-00112/plan.md`。
- 実装起点:
  - Provider-side source of truth から開始する。
- 順序への影響:
  - provider update -> dogfooding mirror/parity -> tests/validate/sync -> report/review。

## Module Dependency Diagram
- タイトル:
  - Draft evidence schema provider-to-consumer dependency
- 答える問い:
  - どの artifact を正本として変更し、どこで parity を確認するか。
- 範囲:
  - この Issue の docs / skills / adapters / templates surface。
- 含めない詳細:
  - exhaustive installer copy graph。
- 更新条件:
  - 対象ファイルや provider/consumer boundary が変わるとき。

### UML（module dependency / package dependency delta）
```plantuml
@startuml
skinparam monochrome true
left to right direction
rectangle "Provider source" as Provider
rectangle "Dogfooding mirror" as Consumer
rectangle "Tests / validation" as Tests
Provider --> Consumer : "refresh / parity"
Tests --> Provider : "assert contract"
Tests --> Consumer : "assert or inspect parity"
@enduml
```

## インターフェース契約
- API / function / protocol / data boundary:
  - No public runtime API change unless explicitly discovered during implementation.
  - Contract surface is Markdown / skill / host adapter content.

## ディレクトリ / ファイル変更計画
```text
.
|-- src/spec_dock/assets/...   # 変更: provider-side source of truth for Draft evidence schema
|-- spec-dock/...              # 変更/確認: dogfooding consumer parity
`-- tests/...                  # 変更/確認: managed asset or content assertion as needed
```

## 要件 → 設計マッピング
- AC-001 -> provider source of truth update and target file diff.
- AC-002 -> validate / sync / parity evidence.
- AC-003 -> final `spec-reviewer` pass.
- EC-001 -> documented uncertainty / approved no-op path.
- EC-002 -> provider/consumer parity handling.

## テスト戦略
- 単体:
  - Content checks where existing test patterns support them.
- 統合:
  - `python -m unittest discover -v` or targeted tests if blast radius is narrow.
  - `./spec-dock/scripts/spec-dock validate` and `sync`.
- E2E / manual:
  - Inspect provider/consumer diff and report evidence.

## 要件 / 例外 -> verification mapping
- AC-001 -> target file inspection / diff.
- AC-002 -> validate / sync output.
- AC-003 -> reviewer pass.
- EC-001 -> report evidence for no-op or uncertainty.
- EC-002 -> diff/parity evidence.

## リスク / 移行 / ロールバック
- リスク:
  - Provider and dogfooding mirror drift.
  - Over-scoping into runtime validation or write-capable delegation.
- ロールバック:
  - Revert this Issue's docs/skills/templates/adapters changes by commit.

## 未確定事項
- なし。


## Parent Epic Contract Details
- Required draft lifecycle states:
  - `requested`, `produced`, `integrated`, `partially_integrated`, `rejected`, `superseded`, `blocked`, `stale`.
- Required failure-mode fields:
  - expected verdict
  - allowed next action
  - report evidence path
  - promotion eligibility
- Required failure modes:
  - missing consent
  - missing/stale previous reviewer pass
  - requirement gap during design
  - design gap during plan
  - role unavailable
  - forbidden action attempt
  - stale draft
  - superseded draft
  - missing draft evidence when delegated use is claimed
  - reviewer unavailable/denied/waived/provisional
- Required report surfaces:
  - `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/report.md`
  - `src/spec_dock/assets/spec_dock/system/active-none/{initiative,epic,issue}/report.md`
  - dogfooding mirrors under `spec-dock/templates/**/report.md` and `spec-dock/system/active-none/**/report.md`
