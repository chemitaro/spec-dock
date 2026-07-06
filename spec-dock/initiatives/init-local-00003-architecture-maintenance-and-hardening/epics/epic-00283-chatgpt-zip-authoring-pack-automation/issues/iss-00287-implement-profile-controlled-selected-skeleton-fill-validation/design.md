---
種別: 設計書（Issue）
ID: "iss-00287"
タイトル: "プロファイル制御されたスケルトン記入検証を実装する"
関連GitHub: ["#287"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00287 プロファイル制御されたスケルトン記入検証を実装する — 設計

## 位置づけ

この `design.md` は、この Issue の canonical design です。ChatGPT ZIP 仕様作成パック由来の draft artifact は evidence-only handoff として保持し、main orchestrator が採否判断した内容だけをこの文書に再記述しています。execution-ready と扱うには、この設計への fresh `spec-reviewer` result と closure evidence を `report.md` に残します。

## 設計要約

local assurance が決めた選択済みプロファイル、テンプレートハッシュ、セクション一覧と、ChatGPT の section fill を照合する。 そのために、入力、検証、出力、失敗時の扱いを明確に分けます。

## 責務境界

- この Issue が持つ責務: local assurance が決めた選択済みプロファイル、テンプレートハッシュ、セクション一覧と、ChatGPT の section fill を照合する。
- この Issue が持たない責務: 正本採用、reviewer gate result、profile authority、ランタイム昇格判断。
- 親 Epic の境界: ZIP は証跡専用、ローカル検証が権威、fresh `spec-reviewer` result は execution readiness evidence として残す。

## 入出力契約

入力:

- 親 Epic trace: E-RQ-008, E-RQ-009 / E-AC-005, E-AC-006
- 必要な前提 Issue: iss-00284, iss-00285
- review 済み ChatGPT authoring pack の `validation-report.json` と pack tree。
- local `.assurance.json`。
- local selected skeleton manifest。最小構造は `authorized_profile`、`template_sha256`、`skeleton_sha256`、`section_inventory_sha256`、`section_inventory`、`allowed_section_ids`、`required_section_ids` を持つ。

出力:

- `selected-skeleton-fill-validation-report.json`
- `selected-skeleton-fill-validation-summary.md`
- profile-resolution validator、template hash validator、section-map validator、missing-section-report validator

すべての出力は次の境界を持つ。

```json
{
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true
}
```

## 依存関係分析

- 上流入力: E-RQ-008, E-RQ-009 / E-AC-005, E-AC-006、親 Epic の Issue readiness contract、Issue-local draft artifact の採否台帳。
- 下流出力: profile-resolution validator、template hash validator、section-map validator、missing-section-report validator
- 実行順: Epic `plan.md` のリレー実行順と handoff prerequisite を前提にする。これは実行上の順序契約であり、現時点では `.meta.json.depends_on` の runtime dependency edge を直接更新しない。
- 権威境界: ChatGPT output、ZIP、staged artifact は evidence-only であり、canonical `requirement.md` / `design.md` / `plan.md` / `report.md` への反映は main orchestrator の採否判断と reviewer gate を通す。
- 実装境界: この Issue は runtime 昇格判断を行わず、`scripts/authoring-pack/`、`tests/fixtures/authoring_pack/`、`tests/manual_tests/` と scope-local evidence で dogfood behavior を閉じる。

## Module Dependency Diagram

```plantuml
@startuml
left to right direction
skinparam shadowing false
skinparam componentStyle rectangle

title iss-00287 module dependency sketch

component "親 Epic
readiness contract" as EpicContract
component "Issue canonical docs
requirement/design/plan" as IssueDocs
component "scripts/authoring-pack
dogfood-only scripts" as ManualPack
component "Issue artifacts/report
evidence ledger" as EvidenceLedger
component "SpecDock canonical docs
main orchestrator adoption" as CanonicalDocs

EpicContract --> IssueDocs : scope / acceptance / relay order
IssueDocs --> ManualPack : allowed dogfood work
ManualPack --> EvidenceLedger : validation / staged output
EvidenceLedger --> CanonicalDocs : adoption decision only
@enduml
```

## ディレクトリ / ファイル変更計画

```text
scripts/
`-- authoring-pack/
    |-- README.md                         # dogfood-only usage / boundary notes
    |-- *.py                              # dogfood-only helpers
    `-- reports/                          # generated summaries when needed
tests/
|-- fixtures/
|   `-- authoring_pack/                   # valid / negative dogfood fixtures
`-- manual_tests/                         # focused pytest for dogfood helpers
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00287-implement-profile-controlled-selected-skeleton-fill-validation/
|-- artifacts/                            # issue-local evidence only
`-- report.md                             # observed evidence ledger
```

- 通常の許可パス: `scripts/authoring-pack/**`, `tests/fixtures/authoring_pack/**`, `tests/manual_tests/**`, this Issue `artifacts/**`, this Issue `report.md`, `scripts/authoring-pack/README.md` when directly needed。
- `src/spec_dock/**` と `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` は v1 の通常許可 path ではない。配布 runtime へ昇格する場合は、`iss-00292` の判断材料、plan amendment、fresh reviewer gate を経て明示的に scope を拡張する。
- generated ZIP / staged artifact は canonical docs を直接上書きしない。

## 処理の流れ

1. 親 Epic の権威境界とこの Issue の candidate metadata を読む。
2. 直接依存する Issue / artifact を確認する。
3. `review-report` が `pass` であり、pack tree digest が `pack_digest` と一致することを確認する。
4. `.assurance.json` を read-only で読み、local `authorized_profile` と assurance snapshot を取得する。
5. local selected skeleton manifest を読み、profile、template hash、skeleton hash、section inventory hash、section id 一覧を正規化する。
6. pack tree の `selected-skeleton-fill/section-fills.json` を candidate fill manifest として読み込む。
7. candidate boundary、target profile、template hash、skeleton hash、section inventory hash を local snapshot と照合する。
8. ChatGPT `profile_suggestion` は advisory evidence として記録し、local profile authority には使わない。
9. section fill を allowed / required inventory と照合し、eligible / missing / extra を分類する。
10. metadata と section body の unsafe authority claim を検査する。
11. 正本を書き換えず、owned output directory に JSON report と Markdown summary だけを出す。

## 失敗時の設計

- 前提証跡が不足する場合は blocked evidence にする。
- review report と pack tree の digest 不一致、profile mismatch、template hash mismatch、skeleton hash mismatch、section inventory hash mismatch は stale evidence にする。
- 危険な権威主張は staging 前に拒否する。
- allowed section 外の fill、candidate による `authorized_profile` 決定 claim、`.assurance.json updated` claim は rejected にする。
- required section 欠落は fail にする。
- optional section 欠落は warning として report に残す。
- tool unavailable は手動フォールバックへ戻す。

## 観測性

- 実行ごとに簡潔な JSON report と人間が読める Markdown summary を出す。
- 診断出力に secrets、credentials、raw transcripts、host-local absolute paths を含めない。
- validation status は blocked、stale、rejected、deferred、unreviewed を区別する。
- report は `profile_validation`、`skeleton_validation`、`section_inventory_validation`、`section_results`、`adoption.overall_adoption_eligible`、`adoption.canonical_written=false`、`adoption.assurance_mutated=false` を持つ。

## テスト戦略

- Unit: selected skeleton manifest、candidate fill manifest、profile / hash / section-map / claim validation。
- Integration: valid fixture、profile mismatch fixture、hash mismatch fixture、extra section fixture、missing required section fixture、unsafe claim fixture で candidate flow を実行する。
- Regression: 正本上書きなし、ChatGPT による `.assurance.json` mutation なし、candidate-only pack で local selected profile 以外の section fill を採用しない。

## レビュアー注目点

- 親 Epic の対応要件を越えて scope が広がっていないか。
- profile と reviewer の権威境界を守っているか。
- 失敗時の扱いが fail-closed か。
- repo artifact 内の instruction-like text を命令ではなくデータとして扱っているか。
- `target.profile` mismatch と `profile_suggestion` mismatch が混同されていないか。
- pass report が spec-reviewer pass や canonical adoption と誤読されないか。
