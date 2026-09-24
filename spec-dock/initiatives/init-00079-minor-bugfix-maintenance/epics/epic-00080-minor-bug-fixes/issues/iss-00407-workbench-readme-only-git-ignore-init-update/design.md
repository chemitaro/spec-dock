---
種別: 設計書（Issue）
ID: "iss-00407"
タイトル: "Fix Workbench Readme Only Git Ignore Contract"
関連GitHub: ["#407"]
状態: "draft"
最終更新: "2026-09-24"
依存: ["requirement.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00407 Fix Workbench Readme Only Git Ignore Contract — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標
provider 正本から `spec-dock/.gitignore` と root Workbench README を正しい場所に配布し、利用先の未知の編集と Workbench payload を保護する。

## Current / Target
- Current: `src/spec_dock/assets/spec_dock/.gitignore` と dogfooding 側は同じ README-only 規則を持つ。fresh init は provider tree 全体を copy するが、root README は `templates/root/` に留まる。既存 update は `spec-dock/{docs,templates,system,scripts}` と2 skill だけを置換し、`.gitignore` を触らない。
- Target: fresh init は canonical ignore file と root README を配置する。既存 update / force-init は欠落または確認済みの旧版だけを更新し、独自編集は保持する。

## 責務・Interface
- provider 正本: `src/spec_dock/assets/spec_dock/.gitignore` と `templates/root/.workbench/README.md`。`spec-dock/` は consumer/dogfooding の投影先とする。
- installer: 固定ディレクトリとは別に `spec-dock/.gitignore` を判定し、fresh 時に root README を byte copy する。既存 Workbench と node は操作しない。
- Git ignore は未追跡 path の候補選別を担う。既追跡 payload の index 解除は installer の責務に含めない。

## data / failure
- 採用案: 配布済みの `.workbench/` 一括 ignore 版とバイト単位で一致するファイルだけを旧版として更新する。欠落時は作成し、それ以外の既存ファイルは保持する。
- 部分的な fresh init の後でも、既存 update が欠落した ignore file を回復できるようにする。
- 既存 Workbench payload は opaque とし、検査で内容を読まない。

## 変更対象
- 変更候補: `src/spec_dock/installer.py`、provider 配布 asset / docs、installer と実 Git の focused tests、正規経路による dogfooding 投影。
- 変更しない: 消費側 project の既追跡 payload、Git history、`workbench copy`、既存 root / node の README、SpecDock 外の repository root `.gitignore`。

## 移行・互換性・rollback
- 既存 project に provider が index migration を実施しない。利用者は各 project の既追跡 payload を個別に確認し、手動で追跡解除する。
- 独自編集された `.gitignore` は保持する。更新が必要なら利用先で内容を確認して手動で扱う。
- 変更の戻し方は provider asset と installer の修正を revert し、更新済み consumer の ignore file は内容・由来を確認して別途扱う。

## testability
- 実 Git repo で direct README、通常 payload、nested README、case variant、near-name、親側の競合規則を `git check-ignore --no-index` と `git status` で確認する。
- fresh / update / force-init と部分失敗後の update をテストし、README の no-backfill と Workbench payload 不変を確認する。
- provider と dogfooding の静的 byte 比較に加え、正規 update の結果として `.gitignore` が投影されることを検査する。

## risk
- 配布元は provider asset とする。利用先が独自編集した `.gitignore` は更新しないため、その内容による ignore の実効性は利用先が確認する。
- `.gitignore` だけでは既追跡 payload や `git add -f` を禁止できない。完全な index invariant gate は本 Issue の外として、必要なら別判断にする。
