---
種別: レポート（Epic）
ID: "epic-00067"
タイトル: "Installed layout aligned asset source structure for agent tooling"
状態: "approved"
作成者: "Codex CLI"
最終更新: "2026-04-13"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["init-local-00003"]
---

# epic-00067 Installed layout aligned asset source structure for agent tooling — レポート（進捗 / 決定 / 結果）

## 進捗サマリー (必須)
- 現在地（何が完了し、何が未完か）:
  - `iss-00068` から `iss-00072` までの current issue docs は `approved` で揃っており、foundation / packaging / installer cutover / verification parity / final closeout の証跡が各 issue report に揃っている。
  - `iss-00072` は prep / S01 / S02 / S90-S99 の closeout chain を完了し、current authority assumptions retirement、current closeout docs reconciliation、fresh dogfooding convergence、final close gate の証跡を issue report に固定した。
  - 本 epic の requirement / design / plan と issue evidence chain は整合済みで、`E-AC-001` から `E-AC-007` まで Pass として close できる。
- 次のマイルストーン:
  - なし。epic-00067 は close-ready / closed state に到達している。
- ブロッカー:
  - acceptance blocker はなし。
  - `iss-00071` report が記録している historical full-suite residual 1 件
    - `tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression`
    - は known residual として残るが、issue-71 で epic scope 外の runtime layering regression として切り分け済みであり、epic acceptance / closeout の blocker ではない。

## 決定事項（ADRリンク） (必須)
- 該当する独立 ADR は未作成:
  - authority / layout / packaging / cleanup / future host extension の決定は `requirement.md` / `design.md` / `plan.md` に固定した。
  - current decision record は `design.md` の `Directory contract`、`Installer contract`、`Packaging contract`、`Legacy authority retirement`、`Flow-D future host extension` を参照する。

## 完了した Issue / PR / Release (必須)
- `iss-00068-install-root-tree-and-asset-classification`: Done
  - 証拠: `issues/iss-00068-install-root-tree-and-asset-classification/report.md` の `## 実装サマリー`、S01/S02/S90-S99
  - 代表コミット: `ff6a997`, `d6c6f4e`
- `iss-00069-package-data-and-installed-artifact-parity`: Done
  - 証拠: `issues/iss-00069-package-data-and-installed-artifact-parity/report.md` の `## package-parity-evidence`
  - 代表コミット: `2fe79aa`, `b6c2ba0`, `be2e813`
- `iss-00070-installer-source-discovery-and-managed-ownership`: Done
  - 証拠: `issues/iss-00070-installer-source-discovery-and-managed-ownership/report.md` の `## handoff-validation-evidence`
  - 代表コミット: `8d3e0e8`, `936e5fd`, `9a91f3e`, `4007144`
- `iss-00071-verification-dogfooding-and-update-parity`: Done
  - 証拠: `issues/iss-00071-verification-dogfooding-and-update-parity/report.md` の `## checkout-verification`、`## runtime-command-verification`、`## installed-package-verification`、`## dogfooding-parity`、`## upstream-handoff-consumed`
  - 代表コミット: `9a225d2`, `dab7519`, `7324dd4`, `9870f17`, `e61dc6c`
- `iss-00072-legacy-authority-retirement-and-final-spec-close`: Done
  - 証拠: `issues/iss-00072-legacy-authority-retirement-and-final-spec-close/report.md` の `## authority-uniqueness`、`## historical-boundary`、`## future-host-extension`、`## upstream-prerequisites`、`## final-close-gate`
  - 代表コミット: `2933f3e`, `68f2a08`, `3968323`

## 受け入れ条件（E-AC）の達成状況 (必須)
- `E-AC-001`: Pass
  - 証拠: `iss-00068` report の `## 実装サマリー` と S01/S02 記録、`src/spec_dock/assets/install_root/` 配下の `.agents/`、`.codex/`、`.github/`、`.github/workflows/` 実在 tree
- `E-AC-002`: Pass
  - 証拠: `iss-00070` report の `## handoff-validation-evidence`、`iss-00071` report の `## checkout-verification` と `## runtime-command-verification`
- `E-AC-003`: Pass
  - 証拠: `iss-00070` report の workflow sync / obsolete cleanup 回帰、`iss-00071` report の `## installed-package-verification` と `## dogfooding-parity`
- `E-AC-004`: Pass
  - 証拠: epic `requirement.md` / `design.md` / `plan.md` で architecture gap、target state、installer policy、future host extension、legacy authority retirement は説明済み
  - 追加証拠: `iss-00072` report の `## historical-boundary`、`## upstream-prerequisites`、`## final-close-gate` により current docs corpus と final close contract が issue evidence chain へ接続済み
- `E-AC-005`: Pass
  - 証拠: epic `requirement.md` の `E-RQ-008` / `E-AC-005`、epic `design.md` の `Flow-D future host extension` は `.agents` shared + sibling host root 追加モデルを明示し、Claude Code を scope 外として固定している
  - 追加証拠: `iss-00072` report の `## future-host-extension` により current host model と将来 host 追加境界が final close gate に接続済み
- `E-AC-006`: Pass
  - 証拠: `iss-00069` report の `## package-parity-evidence`、`iss-00071` report の `## installed-package-verification`
- `E-AC-007`: Pass
  - 証拠: `iss-00070` で installer/manifest authority を `install_root` へ切替済み、`src/spec_dock/assets/install_root/.agents/host-adapters/meta.json` が current authoritative manifest、`iss-00072` S01 で `AGENTS.md` と `tests/test_init_update.py` の current authority assumptions を整理済み
  - 追加証拠: `iss-00072` report の `## authority-uniqueness` と `## final-close-gate` により `install_root` が唯一の current authority で、legacy `codex_skills` は physical tree が削除済みで historical records 上の言及だけが残ることを確認済み

## ロールアウト結果（必要なら） (任意)
- 段階公開の状況:
  - 本 epic は repo-local scaffold / installer / docs contract の更新であり、外部向けの段階公開は実施していない。
- 監視値（エラー率/レイテンシなど）:
  - 代替観測として `iss-00071` report の `validate` / `sync` / `sync --github` / installed-package smoke / checked-in parity を rollout evidence として扱う。
- 障害/アラート:
  - informational full-suite sweep では上記 1 件の known residual failure が残るが、issue-71 で epic scope 外の runtime layering regression として切り分け済みであり、epic acceptance blocker ではない。

## フォローアップ（別Issue化） (必須)
- 別Issue化が必要な epic acceptance follow-up はなし。
- historical full-suite residual 1 件は known residual として残るが、本 epic の acceptance / closeout を妨げない。必要な場合は runtime layering 側の別文脈で扱う。

## 省略/例外メモ (必須)
- `src/spec_dock/assets/codex_skills/` は current repo から退役済みであり、physical legacy tree は削除された。
- `src/spec_dock/assets/install_root/` が唯一の current authority であり、legacy `codex_skills` は source-of-truth として参照しない。
- issue-72 完了により epic closeout verdict は `approved` とする。
