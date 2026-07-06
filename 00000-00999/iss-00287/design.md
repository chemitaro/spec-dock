---
種別: 設計書（Issue）
ID: "iss-00287"
タイトル: "プロファイル制御されたスケルトン記入検証を実装する"
関連GitHub: ["#287"]
状態: "draft"
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
- 必要に応じた source manifest、stale_if、profile snapshot。

出力:

- profile-resolution validator、template hash validator、section-map validator、missing-section-report validator

すべての出力は次の境界を持つ。

```json
{
  "authority": "evidence_only",
  "adoption_status": "unreviewed",
  "bundle_generation_not_promotion": true
}
```

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
