---
種別: artifact
ID: "20260920t064301z"
タイトル: "Specification Review Findings Analysis"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-09-20"
親: ["iss-00405"]
template: "blank"
authority: "evidence"
derived_from: []
reflected_to: []
---

# Issue #405 仕様レビュー指摘分析

## レビュー識別と証拠batch

- identity: iss-00405 / 要件設計計画の整合性・実装受入可能性。一般的改善・アーキテクチャ提案は範囲外。
- active reviewer session: `iss-405-spec-review`
- provenance: `chatgpt-spec-review-strict`の初回fresh run。仕様作成session `issue-405-cleanup-spec-authoring`とは別会話。
- reviewed SHA: `0db10f2766fc2a7b48c75774c5d8dc86ce2d3a6e`
- model/effort: GPT-5.6 Sol / Pro。初回UI picker双方verified。
- raw result: [spec-review-round-1.json](spec-review-round-1.json)。無改変回答をschema検証済み。fail / P1 4件 / P2 2件。
- authority: 最新ユーザー指示（#405を親Epic配下に追加しcleanupを計画、今回P1修正と再review）、親R1〜R10/ADR、子R/D/P、処置正本CSV、従属handoff/map。
- evidence: 同SHAの文書、`tests/unit/infra/test_init_update.py`のprovider/dogfood直接比較、`.github/workflows/provider-ci.yml`のpull_request trigger。SpecDock validate nodes=237、HTML 2図/zoom検証、ZIP配置一致。Product実装・testsは本仕様レビューでは未実行。並行検証laneなし。batchは全6指摘を含みcoverage gapなし。
- parent policy: P0/P1だけblocking。P2/P3はrecord-onlyで修正・backlog化・再review条件化しない。ユーザーは範囲内仕様修正、commit/push、同一reviewer再reviewを許可済み。

## 全指摘の判断（修正前）

| ID | 元分類 | 妥当性・到達条件・影響 | 最初の誤り / 主route | 最小対応・検証 |
|---|---|---|---|---|
| R1 | P1 | 妥当。457faf31はコード調査基点で、採用仕様を含まない。仕様正本と呼ぶと実装者の参照先が食い違う。 | 記録上の基点混同 / documentation-correction | コード調査基点と現在のcanonical仕様を区別。実装開始時のclean HEADと同SHAのreview証跡を固定。文書横断scanと再review。 |
| R2 | P1 | 妥当。S4全test_init_update実行はS2変更後の未同期mirrorでparity failure。S5入口Green要求が循環。 | plan順序 / documentation-correction | 当該suiteの全実行をS5同期直後へ移す。S4は同期非依存focused検証、S4+S5をparity Green後のworking checkpointとする。テスト削除・skip・弱化なし。 |
| R3 | P1 | 妥当。CIはpull_requestのみ。PRが存在しないS6ではplatform evidenceが得られない。 | plan順序 / documentation-correction | S6はlocal証拠、S7でPR作成・CI・review・最終Report順序を明示。CI pendingと完了を区別し、最終handoffはchecks Greenのまま。 |
| R4 | P1 | 妥当。旧親の#396完結文は最新ユーザーの#405追加指示以前の記録。 | 親履歴の未同期 / documentation-correction | 親の履歴一文だけ#396主要移行+#405最終cleanupへ訂正。親R1〜R10/ADR、Product範囲・保証は不変。子にも現在の親子関係を記録。 |
| R5 | P2 | 妥当。checkpoint表とS1本文が相違。安全なworking commit経路あり。 | plan記載 / record-only | 非blocking参考情報。修正しない。 |
| R6 | P2 | 妥当。S4全skill表現とmanaged-only CSVが相違。正本CSVによる安全な実装経路あり。 | plan表現 / record-only | 非blocking参考情報。修正しない。 |

## 認可と保証

4群とも既存のユーザー意図を記録へ反映する訂正であり、Product契約やsource-of-truthの所有モデルを変更しない。コード監査SHAは履歴証拠として保存し、仕様正本は既定どおりcanonical R/D/P。親の実装先更新はユーザーの#405作成指示に一意に基づく。新機能、data/security/public API/recovery/risk、保持test保証は変更しない。新しい人間判断は不要。

対応後はSpecDock validate、diff check、HTML validator、対象のregular blob確認、clean HEAD/upstream一致を再確認し、同identity・同reviewerへ全対象再reviewを依頼する。元JSONは変更しない。pass前に合格を記録しない。
