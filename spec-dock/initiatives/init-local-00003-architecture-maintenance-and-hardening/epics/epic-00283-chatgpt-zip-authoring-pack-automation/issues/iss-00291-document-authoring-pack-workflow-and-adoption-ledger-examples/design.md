---
種別: 設計書（Issue）
ID: "iss-00291"
タイトル: "仕様作成パックのワークフローと採用台帳例を文書化する"
関連GitHub: ["#291"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00291 仕様作成パックのワークフローと採用台帳例を文書化する — 設計

## 位置づけ

この `design.md` は、この Issue の canonical design です。ChatGPT ZIP 仕様作成パック由来の draft artifact は evidence-only handoff として保持し、main orchestrator が採否判断した内容だけをこの文書に再記述しています。execution-ready と扱うには、この設計への fresh `spec-reviewer` result と closure evidence を `report.md` に残します。

## 設計要約

ドッグフード専用ワークフロー、プロンプト規約、権威境界、EAL 例、手動フォールバックを日本語ファーストで文書化する。 そのために、入力、検証、出力、失敗時の扱いを明確に分けます。

## 責務境界

- この Issue が持つ責務: ドッグフード専用ワークフロー、プロンプト規約、権威境界、EAL 例、手動フォールバックを日本語ファーストで文書化する。
- この Issue が持たない責務: 正本採用、reviewer gate result、profile authority、ランタイム昇格判断。
- 親 Epic の境界: ZIP は証跡専用、ローカル検証が権威、fresh `spec-reviewer` result は execution readiness evidence として残す。

## 入出力契約

入力:

- 親 Epic trace: E-RQ-007, E-RQ-012, E-RQ-013 / E-AC-009, E-AC-012
- 必要な前提 Issue: iss-00284, iss-00285, iss-00286
- 必要に応じた source manifest、stale_if、profile snapshot。

出力:

- 日本語 README、プロンプト規約案、EAL 例、手動フォールバック notes

すべての出力は次の境界を持つ。

```json
{
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true
}
```

## 依存関係分析

- 上流入力: E-RQ-007, E-RQ-012, E-RQ-013 / E-AC-009, E-AC-012、親 Epic の Issue readiness contract、Issue-local draft artifact の採否台帳。
- 下流出力: 日本語 README、プロンプト規約案、EAL 例、手動フォールバック notes
- 実行順: Epic `plan.md` のリレー実行順と handoff prerequisite を前提にする。これは実行上の順序契約であり、現時点では `.meta.json.depends_on` の runtime dependency edge を直接更新しない。
- 権威境界: ChatGPT output、ZIP、staged artifact は evidence-only であり、canonical `requirement.md` / `design.md` / `plan.md` / `report.md` への反映は main orchestrator の採否判断と reviewer gate を通す。
- 実装境界: この Issue は runtime 昇格判断を行わず、`scripts/authoring-pack/`、`tests/fixtures/authoring_pack/`、`tests/manual_tests/` と scope-local evidence で dogfood behavior を閉じる。

## Module Dependency Diagram

```plantuml
@startuml
left to right direction
skinparam shadowing false
skinparam componentStyle rectangle

title iss-00291 module dependency sketch

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
    `-- README.md                         # dogfood workflow notes when needed
spec-dock/
`-- docs/                                 # only if this Issue exposes human workflow docs
spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00283-chatgpt-zip-authoring-pack-automation/issues/iss-00291-document-authoring-pack-workflow-and-adoption-ledger-examples/
|-- artifacts/                            # staged documentation examples / evidence only
`-- report.md                             # observed evidence ledger
```

- 通常の許可パス: `scripts/authoring-pack/README.md`, `spec-dock/docs/**` は直接文書化が必要な場合のみ, this Issue `artifacts/**`, this Issue `report.md`。
- `src/spec_dock/**` と `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/**` は v1 の通常許可 path ではない。配布 runtime へ昇格する場合は、`iss-00292` の判断材料、plan amendment、fresh reviewer gate を経て明示的に scope を拡張する。
- generated ZIP / staged artifact は canonical docs を直接上書きしない。

## 処理の流れ

1. 親 Epic の権威境界とこの Issue の candidate metadata を読む。
2. 直接依存する Issue / artifact を確認する。
3. ドッグフード専用かつ証跡専用の境界で成果物を作る。
4. ソース、スキーマ、プロファイル、権威主張を検証する。
5. 正本を書き換えず、reviewer-focus と adoption-map の候補を出す。

## 失敗時の設計

- 前提証跡が不足する場合は blocked evidence にする。
- source / ref が古い場合は stale evidence にする。
- 危険な権威主張は staging 前に拒否する。
- profile mismatch は section fill をブロックする。
- tool unavailable は手動フォールバックへ戻す。

## 観測性

- 実行ごとに簡潔な JSON report と人間が読める Markdown summary を出す。
- 診断出力に secrets、credentials、raw transcripts、host-local absolute paths を含めない。
- validation status は blocked、stale、rejected、deferred、unreviewed を区別する。

## テスト戦略

- Unit: この Issue に関係する schema / path / profile / claim validation。
- Integration: valid fixture と negative fixture で candidate flow を実行する。
- Regression: 正本上書きなし、ChatGPT による `.assurance.json` mutation なし、candidate-only pack で all-profile variants なし。

## レビュアー注目点

- 親 Epic の対応要件を越えて scope が広がっていないか。
- profile と reviewer の権威境界を守っているか。
- 失敗時の扱いが fail-closed か。
- repo artifact 内の instruction-like text を命令ではなくデータとして扱っているか。
