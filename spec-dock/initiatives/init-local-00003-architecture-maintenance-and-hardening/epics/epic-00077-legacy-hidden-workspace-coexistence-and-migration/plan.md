---
種別: 計画書（Epic）
ID: "epic-00077"
タイトル: "Legacy hidden workspace coexistence and migration"
関連GitHub: ["#77"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-04-15"
依存: ["requirement.md", "design.md"]
親: ["init-local-00003"]
---

# epic-00077 Legacy hidden workspace coexistence and migration — 計画（Issues / Order）

## この計画で閉じる E-RQ / E-AC
- E-RQ:
  - E-RQ-001
  - E-RQ-002
  - E-RQ-003
  - E-RQ-004
  - E-RQ-005
- E-AC:
  - E-AC-001
  - E-AC-002
  - E-AC-003
  - E-AC-004
  - E-AC-005

## Issue 分割方針
- slicing principle:
  - 本 epic は single-issue で閉じる
  - installer gate、manual migration contract、doctor/validate observability、docs/tests parity を `iss-00078` に集約する
- rationale:
  - rename guidance 廃止と coexistence/migration observability は同じ installer boundary を共有する
  - dual-read を禁止する contract は installer/runtime/docs/tests を分けると責務境界が曖昧になる
- exceptions:
  - なし

## Issue 一覧（順序 / tranche 付き）
- iss-00078:
  - 目的:
    - legacy `.spec-dock/` coexistence install と manual migration contract を end-to-end で固定する
  - deliverable:
    - `_install_spec_dock()` rename blocker removal
    - `_require_specdock()` no-rename/manual-migration guidance
    - current SoR を `spec-dock/` に固定する runtime contract
    - `doctor` / `validate` の migration observability contract
    - `tests/test_cli.py` / `tests/test_init_update.py` / runtime tests 更新
    - installer/docs wording 更新
  - tranche:
    - tranche-1 / now
  - closes:
    - E-RQ-001
    - E-RQ-002
    - E-RQ-003
    - E-RQ-004
    - E-RQ-005
    - E-AC-001
    - E-AC-002
    - E-AC-003
    - E-AC-004
    - E-AC-005
  - depends on:
    - なし

## 統合チェックポイント
- G1 requirement/design readiness:
  - epic/issue requirement/design/plan が `approved` で揃い、spec-reviewer pass 対象として実装判断が残っていない
- G2 installer/runtime readiness:
  - coexistence install、no-rename guidance、no-dual-read、no-auto-delete が code/test/docs で一貫している
- G3 observability readiness:
  - `validate` と `doctor` の役割分離が command evidence で確認できる
- G9 final epic spec review:
  - `iss-00078` の report と final review だけで epic close readiness を判定できる

## 品質ゲート
- spec gate:
  - `iss-00078` 着手前に spec-reviewer pass を取得する
- implementation gate:
  - installer targeted tests が pass
  - runtime doctor/validate targeted tests が pass
  - `./spec-dock/scripts/spec-dock validate` が pass
- docs gate:
  - rename guidance が除去されている
  - manual migration/manual deletion wording が user-facing docs と spec で整合している
- observability gate:
  - legacy only / coexistence pending cleanup / clean current only を command output で区別できる

## ロールアウト / docs impact
- rollout order:
  - spec approval
  - installer gate correction
  - runtime observability correction
  - docs refresh
  - targeted regressions and final review
- contract / docs refresh:
  - rename guidance 廃止
  - coexistence install 許可
  - manual migration 明記
  - manual deletion 明記
  - doctor/validate の役割明記

## Issue readiness contract
- Issue に要求する最低条件:
  - `_install_spec_dock()` と `_require_specdock()` の target behavior が requirement/design/plan に明示されている
  - manual migration は auto/dual-read でないことが requirement/design/plan の全てで一致している
  - `tests/test_cli.py`、`tests/test_init_update.py`、runtime doctor/validate tests が verification surface として plan に載っている
  - SG1/RG1/QG1 の review timing が issue plan に定義されている

## final exit contract
- E-AC closure:
  - installer が coexistence install を許可している
  - runtime が rename を要求せず、legacy を current SoR として読まない
  - `doctor`/`validate` による migration observability が揃っている
  - docs/tests が new contract に揃っている
- integration / rollout complete:
  - `iss-00078` report に implementation evidence、review verdict、command/test results が記録されている
- docs impact resolved:
  - rename guidance 廃止と manual migration contract が provider/dogfooding docs に反映されている

## 依存 / ブロッカー
- D-001:
  - installer と runtime で legacy coexistence の診断方針がずれると review で fail になる
- D-002:
  - `doctor` の warning/finding contract を曖昧にすると cleanup readiness の運用がぶれる

## 未確定事項
- なし:
  - epic は `iss-00078` 単独で進める
