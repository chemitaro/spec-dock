---
種別: 要件定義書（Issue）
ID: "iss-00078"
タイトル: "Installer coexistence contract and migration flow"
関連GitHub: ["#78"]
状態: "approved"
作成者: "iwasawayuuta"
最終更新: "2026-04-15"
親: ["epic-00077", "init-local-00003"]
---

# iss-00078 Installer coexistence contract and migration flow — 要件定義（WHAT / WHY）

## 目的
- legacy `.spec-dock/` と現行 `spec-dock/` が非互換である前提を installer/runtime/docs/tests に反映し、rename guidance を廃止する。
- `spec-dock/` coexistence install、manual migration、manual deletion、`doctor`/`validate` observability を 1 issue で実装完了できる契約へ固定する。

## 背景・現状
- 現状の挙動:
  - `src/spec_dock/cli.py::_install_spec_dock()` は、legacy `.spec-dock/` が存在して `spec-dock/` がないとき次の error で install を止める。
  - `legacy '.spec-dock' exists. Please rename it before installing: mv .spec-dock spec-dock`
  - `src/spec_dock/cli.py::_require_specdock()` は、`spec-dock/` がなく legacy `.spec-dock/` があるとき rename を要求する。
- 現状の課題:
  - rename によって non-compatible legacy data を current workspace と誤認させる。
  - install 前に止めるため、正しい migrate flow である「new install -> manual migration -> validate/doctor -> manual delete」へ進めない。
  - runtime boundary と observability が未定義のため、maintainer が cleanup readiness を判断しにくい。
- 再現手順:
  1. repo root に legacy `.spec-dock/` だけがある状態を作る。
  2. install path を実行すると rename guidance で fail する。
  3. current workspace required path を実行すると rename guidance で fail する。
- 観測点:
  - CLI:
    - `spec-dock init`
    - `spec-dock update`
    - current workspace を要求する installer/runtime path
    - `./spec-dock/scripts/spec-dock validate`
    - `./spec-dock/scripts/spec-dock doctor`
  - Tests:
    - `tests/test_cli.py`
    - `tests/test_init_update.py`
    - `tests/cli_runtime/test_validate.py`
    - `tests/cli_runtime/test_runtime_doctor_s04.py`
  - Log/command output:
    - installer error text
    - doctor warning/finding text
- 情報源:
  - `src/spec_dock/cli.py`
  - active epic spec docs
  - existing runtime doctor/validate tests

## 対象ユーザー / 利用シナリオ（必要時）
- 主な利用者:
  - legacy `.spec-dock/` から新 `spec-dock/` へ切り替える maintainer
  - installer/runtime contract をレビューする implementer/reviewer
- 代表シナリオ:
  - legacy `.spec-dock/` を残したまま `spec-dock/` を install したい
  - current `spec-dock/` だけを検証し、legacy cleanup のタイミングを `doctor` で判断したい

## スコープ
- MUST:
  - `_install_spec_dock()` を coexistence install に変更する
  - `_require_specdock()` の rename guidance を manual migration guidance に置き換える
  - current runtime が `spec-dock/` だけを current SoR として扱うことを固定する
  - `doctor`/`validate` に migration state observability を追加する
  - relevant docs/tests を更新する
- MUST NOT:
  - legacy `.spec-dock/` rename 推奨
  - legacy/current dual-read
  - auto-migration
  - auto-delete
- OUT OF SCOPE:
  - generic migration engine
  - legacy data 自動変換
  - legacy data の完全自動検証

## 境界
- Always:
  - current SoR は `spec-dock/`
  - migration は human が manual で行う
  - delete は human が manual で行う
  - `validate` は current `spec-dock/` だけを評価する
- Ask:
  - manual migration docs の wording/detail は実装レビューで詰める
  - doctor message wording は実装で調整してよいが、state distinction は崩さない
- Never:
  - rename で互換性があるかのように案内しない
  - legacy `.spec-dock/` を current data source として読まない
  - `--force` を legacy delete の隠れた trigger にしない

## 非交渉制約
- `_require_specdock()` と `_install_spec_dock()` を明示的に変更対象へ含める。
- migration flow は `install new spec-dock/ -> manual migration -> validate/doctor -> manual delete legacy` に固定する。
- spec-reviewer pass を target gate とし、front matter は implementation-ready になった時点で `approved` とする。

## 前提
- legacy `.spec-dock/` の内部 format は current `spec-dock/` と互換ではない。
- maintainer は legacy content を読みながら current workspace に必要な内容を manual で移せる。

## 受け入れ条件
- AC-001:
  - Actor:
    - maintainer
  - Given:
    - repo root に legacy `.spec-dock/` があり、`spec-dock/` は存在しない
  - When:
    - install path を実行する
  - Then:
    - `spec-dock/` install は rename guidance で止まらない
    - legacy `.spec-dock/` は unchanged のまま残る
  - 観測点:
    - `tests/test_cli.py`
    - `tests/test_init_update.py`
- AC-002:
  - Actor:
    - maintainer
  - Given:
    - repo root に legacy `.spec-dock/` があり、`spec-dock/` は存在しない
  - When:
    - `_require_specdock()` を通る current-workspace-required path を実行する
  - Then:
    - error は rename を要求しない
    - `spec-dock init` で new workspace を install し、その後 manual migration するよう案内する
  - 観測点:
    - installer/runtime error message tests
- AC-003:
  - Actor:
    - maintainer
  - Given:
    - repo root に `spec-dock/` と legacy `.spec-dock/` の両方がある
  - When:
    - current runtime commands を実行する
  - Then:
    - current runtime は `spec-dock/` だけを読み書きする
    - legacy `.spec-dock/` は detection 対象にとどまり、current data としては読まれない
    - legacy `.spec-dock/` は自動削除されない
  - 観測点:
    - `tests/test_init_update.py`
    - `tests/cli_runtime/test_validate.py`
- AC-004:
  - Actor:
    - maintainer
  - Given:
    - `spec-dock/` の manual migration が完了し、legacy `.spec-dock/` はまだ残っている
  - When:
    - `./spec-dock/scripts/spec-dock validate` と `./spec-dock/scripts/spec-dock doctor` を実行する
  - Then:
    - `validate` は current `spec-dock/` が valid なら pass する
    - `doctor` は cleanup pending を warning として返し、legacy delete が manual であると案内する
  - 観測点:
    - `tests/cli_runtime/test_validate.py`
    - `tests/cli_runtime/test_runtime_doctor_s04.py`
- AC-005:
  - Actor:
    - maintainer
  - Given:
    - repo root に legacy `.spec-dock/` だけがあり、new `spec-dock/` は未 install である
  - When:
    - `./spec-dock/scripts/spec-dock doctor` を実行する
  - Then:
    - doctor は install required finding を返し、rename ではなく new install と manual migration を案内する
  - 観測点:
    - `tests/cli_runtime/test_runtime_doctor_s04.py`
    - command output assertions
- AC-006:
  - Actor:
    - reviewer
  - Given:
    - issue docs / tests / user-facing guidance を確認する
  - When:
    - implementation readiness を判断する
  - Then:
    - S01/S02/S03/S04/S90/S99 の execution contract が明確である
    - spec-reviewer pass に必要な主要判断が残っていない
  - 観測点:
    - issue requirement/design/plan

## 例外・エッジケース
- EC-001:
  - 条件:
    - legacy `.spec-dock/` と `spec-dock/` が共存しているが current `spec-dock/` は invalid
  - 期待:
    - `validate` は current workspace error で fail する
    - legacy `.spec-dock/` を fallback として読まない
  - 観測点:
    - runtime validate regressions
- EC-002:
  - 条件:
    - `spec-dock update` または `--force` を使う
  - 期待:
    - current `spec-dock/` だけを対象にし、legacy `.spec-dock/` は自動削除しない
  - 観測点:
    - installer/update regressions
- EC-003:
  - 条件:
    - maintainer が migration 前に `doctor` を実行する
  - 期待:
    - install required と cleanup pending を混同しない出力が返る
  - 観測点:
    - doctor runtime tests

## 入力→出力例（必要時）
- EX-001:
  - Input:
    - legacy `.spec-dock/` only + `spec-dock init`
  - Output:
    - new `spec-dock/` created
    - legacy `.spec-dock/` unchanged
- EX-002:
  - Input:
    - legacy `.spec-dock/` only + current workspace required path
  - Output:
    - error: `spec-dock/` missing, install new workspace and migrate manually
- EX-003:
  - Input:
    - coexistence state + valid current workspace + `doctor`
  - Output:
    - warning: legacy workspace still present, cleanup is manual after migration confirmation

## 用語（ドメイン語彙）
- TERM-001:
  - current workspace:
    - runtime が source of truth として扱う `spec-dock/`
- TERM-002:
  - legacy workspace:
    - non-compatible historical hidden directory `.spec-dock/`
- TERM-003:
  - cleanup pending:
    - current `spec-dock/` は valid だが legacy `.spec-dock/` がまだ残っている状態

## 未確定事項
- なし:
  - manual migration / no-dual-read / no-auto-delete は確定
