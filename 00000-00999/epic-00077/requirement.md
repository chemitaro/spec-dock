---
種別: 要件定義書（Epic）
ID: "epic-00077"
タイトル: "Legacy hidden workspace coexistence and migration"
関連GitHub: ["#77"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-04-15"
親: ["init-local-00003"]
---

# epic-00077 Legacy hidden workspace coexistence and migration — 要件定義（WHAT / WHY）

## 目的（Initiative との紐づき）
- initiative goal / metric:
  - `init-local-00003` の architecture hardening として、legacy hidden workspace `.spec-dock/` と現行 `spec-dock/` の非互換性を truthfully 扱う installer/migration contract を固定する。
  - 誤った rename 誘導を除去し、manual migration と明示的 cleanup による安全な cutover contract を導入する。
- この epic が提供する能力:
  - `spec-dock/` を legacy `.spec-dock/` と共存させて install/update できる。
  - installer と runtime は legacy data を current data として読まない。
  - migration は manual/documented flow として扱い、`doctor`/`validate` で状態確認できる。

## 背景・現状
- 現状の挙動:
  - `src/spec_dock/cli.py` の `_install_spec_dock()` は、legacy `.spec-dock/` が存在し `spec-dock/` が未作成のとき install を reject し、rename を要求する。
  - 同ファイルの `_require_specdock()` は、`spec-dock/` がなく legacy `.spec-dock/` があるとき rename を要求する。
- 現状の課題:
  - legacy `.spec-dock/` と現行 `spec-dock/` は format/contract が互換でないため、rename guidance は誤りである。
  - rename すると非互換 data を current workspace と誤認しやすく、manual migration boundary が失われる。
  - install 前に止める contract のままだと、新 workspace を先に作ってから manual migration する正しい流れへ進めない。
- この epic で固定する結論:
  - 新 target contract は `spec-dock/` install coexistence、manual migration、manual deletion である。
  - auto-migration、dual-read、legacy auto-delete は採用しない。

## ユースケース
- happy path:
  - maintainer が legacy `.spec-dock/` を持つ repo で `spec-dock init` を実行し、新しい `spec-dock/` を install する。
  - maintainer が legacy data を参照しながら、必要な node/doc/content を current `spec-dock/` へ manual で移す。
  - maintainer が `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock doctor` で current workspace の整合と cleanup readiness を確認し、最後に `.spec-dock/` を manual で削除する。
- exception / operation scenario:
  - repo に `.spec-dock/` だけが存在し `spec-dock/` がない場合、runtime は rename を要求せず、新 workspace install と manual migration を案内する。
  - repo に両方が存在する場合、runtime は `spec-dock/` だけを current SoR として扱い、legacy `.spec-dock/` は存在診断対象としてのみ扱う。

## Epic requirements
- E-RQ-001:
  - installer contract は legacy `.spec-dock/` の存在を理由に `spec-dock/` install を拒否しないこと。
  - `_install_spec_dock()` は rename guidance を廃止し、`spec-dock/` が未存在なら legacy coexistence 下でも install を継続できること。
- E-RQ-002:
  - current workspace lookup は legacy `.spec-dock/` を current `spec-dock/` とみなさないこと。
  - `_require_specdock()` は `spec-dock/` 未存在かつ legacy 存在時に rename を要求せず、`spec-dock init` 実行と manual migration を案内すること。
- E-RQ-003:
  - data boundary は `spec-dock/` を current source of truth、legacy `.spec-dock/` を migration source candidate として固定すること。
  - installer/runtime/tests/docs は legacy data を dual-read しないこと。
  - migration は explicit/manual flow とし、CLI が legacy data を自動変換・自動吸収・自動削除しないこと。
- E-RQ-004:
  - observability contract は `validate` と `doctor` を分離すること。
  - `validate` は current `spec-dock/` graph/artifact のみを検証し、legacy `.spec-dock/` contents を current validation input として読まないこと。
  - `doctor` は legacy coexistence/migration state を診断し、install required / cleanup pending / clean の判断材料を出せること。
- E-RQ-005:
  - epic は `iss-00078` の single-issue で閉じること。
  - docs / tests / dogfooding expectations は new contract に揃い、spec review で implementation-ready と判定できること。

## Epic acceptance criteria
- E-AC-001:
  - Given:
    - repo root に legacy `.spec-dock/` があり、`spec-dock/` は未作成である
  - When:
    - `spec-dock init` または install path を実行する
  - Then:
    - install は rename 指示で止まらず、current `spec-dock/` を新規作成できる
    - legacy `.spec-dock/` はそのまま残る
  - 観測点:
    - `tests/test_cli.py`
    - `tests/test_init_update.py`
- E-AC-002:
  - Given:
    - repo root に legacy `.spec-dock/` があるが、`spec-dock/` は存在しない
  - When:
    - current workspace を要求する path を実行する
  - Then:
    - error は rename を要求しない
    - `spec-dock init` による coexistence install と manual migration を案内する
  - 観測点:
    - `_require_specdock()` contract tests
    - installer/runtime error message assertions
- E-AC-003:
  - Given:
    - repo root に `spec-dock/` と legacy `.spec-dock/` の両方が存在する
  - When:
    - validate / sync / active / other current runtime paths を使う
  - Then:
    - runtime は `spec-dock/` だけを current SoR として扱う
    - legacy `.spec-dock/` は current data source として読まれず、dual-read fallback も発生しない
    - legacy `.spec-dock/` は自動削除されない
  - 観測点:
    - `tests/test_init_update.py`
    - `tests/cli_runtime/test_validate.py`
    - relevant command regressions
- E-AC-004:
  - Given:
    - new `spec-dock/` install 後に maintainer が manual migration を行った
  - When:
    - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock doctor` を実行する
  - Then:
    - `validate` は current `spec-dock/` の整合性だけを評価する
    - `doctor` は legacy coexistence の有無と cleanup readiness を observability として返す
    - legacy only 状態は install required として fail できる
    - coexistence 状態は current workspace が valid なら manual cleanup pending warning で観測できる
  - 観測点:
    - `tests/cli_runtime/test_validate.py`
    - `tests/cli_runtime/test_runtime_doctor_s04.py`
    - `tests/cli_runtime/test_runtime_validate_s02.py`
- E-AC-005:
  - Given:
    - epic/issue spec、installer docs、test plan を確認する
  - When:
    - implementation readiness を review する
  - Then:
    - single-issue plan `iss-00078` だけで実装に着手できる
    - rename guidance 廃止、manual migration、manual deletion、doctor/validate observability が矛盾なく固定されている
    - front matter は `approved`、review target は spec-reviewer pass になっている
  - 観測点:
    - epic / issue requirement.md
    - epic / issue design.md
    - epic / issue plan.md

## スコープ
- MUST:
  - `_install_spec_dock()` の coexistence install contract
  - `_require_specdock()` の no-rename guidance contract
  - `validate` と `doctor` の migration observability contract
  - installer/docs/tests/dogfooding の整合
  - single-issue execution contract
- MUST NOT:
  - legacy `.spec-dock/` rename 推奨
  - legacy/current dual-read
  - auto-migration engine の導入
  - legacy auto-delete
- OUT OF SCOPE:
  - legacy format を解析して自動変換する generic migrator
  - manual migration content の完全自動化
  - multi-step rollback engine

## 境界
- Always:
  - current SoR は `spec-dock/` のみ
  - legacy `.spec-dock/` は detection/diagnostics/manual reference のみ
  - migration は human-driven/manual
  - delete は human-triggered/manual
- Ask:
  - manual migration guide の wording/detail は implementation で docs review しながら最小限に詰める
  - `doctor` warning 文言の細部は実装で調整してよいが、install required と cleanup pending の区別は崩さない
- Never:
  - rename で非互換 data を current workspace に見せかけない
  - legacy data を current graph validation に混ぜない
  - `--force` や update path で legacy deletion を黙って行わない

## 非機能要件
- reliability / consistency:
  - coexistence install は legacy directory の有無にかかわらず deterministic に動作すること
  - validate/doctor の診断基準は docs/test/runtime で一致すること
- operations:
  - maintainer が install required、cleanup pending、clean を command output で判断できること
- security:
  - legacy data を current data と誤読して destructive mutation しないこと

## 依存 / 影響範囲
- impacted components:
  - `src/spec_dock/cli.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py`
  - `tests/test_cli.py`
  - `tests/test_init_update.py`
  - `tests/cli_runtime/test_validate.py`
  - `tests/cli_runtime/test_runtime_doctor_s04.py`
- external dependency:
  - なし
- compatibility:
  - legacy `.spec-dock/` の中身は current format と互換でない前提で扱う

## 未確定事項
- なし:
  - rename guidance 廃止、manual migration、manual cleanup、single-issue execution は確定
