---
種別: レポート（Epic）
ID: "epic-00059"
タイトル: "Dependency metadata unification and command mutation"
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-12"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00059 Dependency metadata unification and command mutation — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - `iss-00060` で `.meta.json` schema / reader contract、`iss-00061` で mutation contract、`iss-00062` で downstream parity / hard cutover judgment、`iss-00063` で final regression parity / close record / final reviews まで完了した。
  - close 後 residual として `iss-00064` を起票し、利用者向け docs/help/skill の runtime path / `.meta.json` contract / command discovery の整合、installer の legacy template `deps.json` cleanup hardening、manual confirmation を完了した。
  - 本 epic の core runtime close 条件は `iss-00063` 時点で満たされており、`iss-00064` で close 後の docs/help alignment residual も解消済みである。
- 次のマイルストーン:
  - なし（epic close 完了）。
- ブロッカー:
  - なし。

## 決定事項（ADRリンク） (必須)
- ADR 追加なし。
- `.meta.json` を単一 SoT とし、hard cutover judgment は T3 issue `report.md`、E-AC-005 final closure は T4 issue `report.md` を正本にする owner split を採用した。

## 完了した Issue / PR / Release (必須)
- `iss-00060-meta-json-dependency-schema-and-reader-alignment`: Done
- `iss-00061-dependency-mutation-command-contract`: Done
- `iss-00062-downstream-parity-and-cutover-readiness`: Done
- `iss-00063-final-regression-parity-and-cutover-closure`: Done
- `iss-00064-update-user-facing-docs-help`: Done

## 受け入れ条件（E-AC）の達成状況 (必須)
- `E-AC-001`: Pass（証拠: `iss-00060` schema/read contract、epic requirement の `.meta.json` SoT 定義）
- `E-AC-002`: Pass（証拠: `iss-00061` mutation contract と fail-closed validation regression）
- `E-AC-003`: Pass（証拠: `iss-00062/report.md` の hard cutover judgment / docs update / manual fix / `validate` / `sync` evidence）
- `E-AC-004`: Pass（証拠: `iss-00062/report.md` S01 delete scrub parity と targeted regression）
- `E-AC-005`: Pass（証拠: `iss-00063/report.md` S02/S03/S04/S99、QG1 pass、final SG1 pass）

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - dogfooding checked-in data は `.meta.json` 単一 SoT へ cut over 済み。
- 監視値（エラー率/レイテンシなど）:
  - 該当なし（focused regression / dogfooding command evidence ベース）。
- 障害/アラート:
  - なし。

## フォローアップ（別Issue化） (必須)
- `iss-00064-update-user-facing-docs-help`:
  - 扱い:
    - T4 close 後に判明した docs/help alignment residual を epic 内 follow-up として処理済み。
  - 解消内容:
    - user-facing docs/help/skill の runtime path / `.meta.json` contract / command discovery を current implementation に整合。
    - installer の legacy template `deps.json` cleanup を harden し、focused regression と手動確認で再発防止を確認。
  - 状態:
    - 完了済み。現時点で未処理の follow-up はなし。

## 省略/例外メモ (必須)
- `python -m unittest discover -v` の full baseline は本 epic close 条件には含めず、issue-scoped focused regression と dogfooding command evidence を採用した。
- `iss-00064` は core runtime の close verdict を差し替えるものではなく、close 後 residual の docs/help alignment と installer hardening を補完する issue として扱った。
