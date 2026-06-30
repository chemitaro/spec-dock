---
種別: 要件定義書（Issue）
ID: "iss-00255"
タイトル: "Add Grade Aware Issue Authoring Smoke Tests"
関連GitHub: ["#255"]
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
親: ["epic-00224", "init-local-00003"]
---

# iss-00255 Add Grade Aware Issue Authoring Smoke Tests — Issue 要件定義

## 1. 目的

R0 / G1 / G2 / G3 で追加する grade-aware Issue authoring workflow が、個別には正しく見えても統合時に崩れないことを smoke test と docs parity inspection で固定する。特に、template materialization、readiness preflight、draft routing、delegated evidence、fresh review / report gate が同じ Epic 設計に沿って動くことを確認する。

## 2. 背景

Epic #224 の追加 corrective tranche は、Issue #247 後の manual test で見つかった readiness false positive と、GPT-5.5 Pro 分析で具体化された grade-aware authoring gap を閉じる。R0〜G3 はそれぞれ責務を分けて実装するため、G4 で代表的な grade / artifact / evidence 組み合わせを横断確認し、抜け漏れや重複実装を検出できる状態にする。

## 3. 観測可能な成果

- Lite では途中 commit gate や full static analysis 必須が混入していないことを確認できる。
- Standard / Strict / Critical では M99 に static analysis / lint / tests / report / commit gate があることを確認できる。
- classified Issue の `draft-design` / `draft-plan` が `authorized_profile` に対応する profile template を source にすることを確認できる。
- missing / invalid / stale `.assurance.json` では draft generation が no-write fail-closed になることを確認できる。
- placeholder / heading-only / stale evidence の readiness false positive regression を検出できる。
- provider source と dogfooding mirror の docs / template parity を確認できる。

## 4. スコープ

対象:

- grade-aware Issue authoring smoke tests
- profile template routing smoke
- readiness false-positive regression smoke
- provider / dogfooding docs parity inspection
- R0〜G3 の cross-slice acceptance evidence

対象外:

- R0〜G3 の本体ロジック実装
- live GitHub repository を必須とする external integration
- production telemetry backend
- automatic Lite default 有効化

## 5. 親 Epic との対応

- `E-AC-006`
- `E-AC-022`
- Epic design: `Issue Authoring Smoke / Parity Gate`
- Epic plan: `G4`

## 6. 受け入れ条件

- AC-001: Lite profile の代表 fixture で、途中 commit gate と full static analysis 必須が混入していないことを確認できる。
- AC-002: Standard / Strict / Critical profile の代表 fixture で、M99 に静的解析 / lint / tests / report / commit gate が存在することを確認できる。
- AC-003: `draft-design` / `draft-plan` が `authorized_profile` の profile template から生成されることを確認できる。
- AC-004: `.assurance.json` missing / invalid / stale の場合、draft generation は no-write fail-closed になり、理由が観測できる。
- AC-005: placeholder / heading-only / stale evidence を含む Issue が execution-ready にならないことを確認できる。
- AC-006: delegated specialist evidence、Evidence Adoption Ledger、fresh `spec-reviewer` evidence の最低限の組み合わせを smoke で確認できる。
- AC-007: provider 側 `src/spec_dock/assets/spec_dock/...` と dogfooding 側 `spec-dock/...` の関連 docs / templates が意図した差分だけで整合している。
- AC-008: G4 の結果が `report.md` に、実行コマンド、結果、未実施理由、残リスクとして記録できる。

## 7. 制約

- G4 は R0〜G3 の実装漏れを smoke で検出する closure slice であり、主要ロジックを G4 に寄せない。
- G4 は hermetic tests を優先し、live GitHub や外部サービスを必須にしない。
- G4 は Lite を重くしない。Lite の軽量性は regression 対象として守る。
