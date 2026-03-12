---
種別: 実装報告書（Issue）
ID: "issue-25"
タイトル: "巨大な app.py を複数 module に分割し tests/test_cli.py を領域別に再編する"
関連GitHub: ["https://github.com/chemitaro/spec-dock/issues/25"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-03-12"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["#25"]
---

# issue-25 巨大な app.py を複数 module に分割し tests/test_cli.py を領域別に再編する — 実装報告（LOG）

## 実装サマリー
- `S01` として、runtime の pure core のうち `ids / graph / validation` を `domain` 層へ additive に抽出した。
- `app.py` は staged delegation owner のまま残し、validation seam は `domain.validation.validate_graph_and_deps()` にそろえた。

## 実装記録（セッションログ）

### 2026-03-12 02:35 - 03:08

#### 対象
- Step: S01
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `domain/ids.py`, `domain/models.py`, `domain/tree.py`, `domain/validation.py` を追加し、pure helper / dataclass / graph build / structural validation を抽出した。
- legacy `ids.py` は thin wrapper として維持し、既存 import 面を壊さず `domain/ids.py` へ委譲する形へ変更した。
- `app.py` には `_build_graph_from_nodes()` mapper を追加し、`_validate_nodes()` と `_validate_github_issue_numbers_unique()` を domain validation へ委譲する構成へ切り替えた。
- `tests/test_runtime_domain_s01.py` を追加し、pure core test / delegation smoke / no-I/O import assertion を導入した。
- `code_reviewer` と `consultant` で S01 をレビューし、`validate_graph_and_deps()` を live seam に使う微修正まで反映した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_runtime_domain_s01 \
  tests.test_cli.TestCli.test_validate_detects_duplicate_github_issue_numbers_with_paths \
  tests.test_cli.TestCli.test_validate_detects_issue_initiative_id_mismatch

Ran 10 tests in 0.274s
OK

python -m unittest -v tests.test_runtime_domain_s01

Ran 9 tests in 0.011s
OK

python -m unittest discover -v

Ran 171 tests in 21.114s
OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - domain graph / validation への委譲 seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/ids.py` - legacy wrapper 化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/__init__.py` - domain package 追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/ids.py` - pure ids helper を移設
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py` - `SpecNodeSeed` / `SpecNode` / `SpecGraph` / `ValidationReport`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/tree.py` - `build_graph()`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - structural validation / github issue uniqueness validation
- `tests/test_runtime_domain_s01.py` - S01 focused tests

#### コミット
- `8c7ab7257408b16bb1a9ef30e2671cb7da9f4658` `feat(runtime): domain層へpure coreを抽出して検証委譲を導入`

#### メモ
- `validate_graph_and_deps()` は S01 では structural-only とし、deps pure rule は計画どおり `S03` へ残した。
- `tests/test_runtime_domain_s01.py` は一時的な focused test file として追加し、正式な test tree split は計画どおり後続 step で扱う。

---

### 2026-03-12 03:08 - 03:28

#### 対象
- Step: S02
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `application/validate_tree.py`、`application/contracts.py`、`application/ports.py` を追加し、validate の最初の consumer slice を導入した。
- `infra/contracts.py` に `StoredMetaRecord`、`presentation/contracts.py` に `CliText`、`presentation/cli_text.py` に `render_validate_text()` を追加した。
- `app.py` の validate 経路のみを新 use case + renderer に委譲し、`app.py` は staged delegation owner のまま維持した。
- `tests/test_runtime_validate_s02.py` を追加し、use case、reader seam、renderer、exit `0/1`、stdout/stderr split、legacy delegated validate smoke を固定した。
- `consultant` と `code_reviewer` で S02 スコープレビューを行い、過剰抽象化に入らず validate slice に閉じたことを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_runtime_validate_s02 \
  tests.test_cli.TestCli.test_validate_detects_broken_parent_id \
  tests.test_cli.TestCli.test_validate_detects_issue_initiative_id_mismatch \
  tests.test_cli.TestCli.test_validate_reports_invalid_meta_json_shape \
  tests.test_cli.TestCli.test_validate_detects_duplicate_github_issue_numbers_with_paths \
  tests.test_cli.TestCli.test_validate_and_sync_fail_fast_on_legacy_meta_json \
  tests.test_cli.TestCli.test_validate_and_sync_fail_fast_when_dot_meta_and_legacy_coexist

Ran 13 tests in 0.904s
OK

python -m unittest discover -v

Ran 178 tests in 22.140s
OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - validate path を use case + renderer へ委譲
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `ValidateTreeRequest` / `ValidationResult`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - validate 用最小 reader seam
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/validate_tree.py` - validate use case
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py` - `StoredMetaRecord`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/contracts.py` - `CliText`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - `render_validate_text()`
- `tests/test_runtime_validate_s02.py` - S02 focused tests

#### コミット
- 未実施

#### メモ
- `app.py` から `SpecGraph` や `_Node` を application へ渡さず、`StoredMetaRecord` 境界に留めた。
- validate の failure path は既存どおり main の `error: ...` 包装を維持し、renderer は stdout/stderr の正本だけを持つ形にした。

---

## 遭遇した問題と解決
- 問題: 初回実装では `app.py` の live seam が `validate_graph()` 直結で、将来の `application/validate_tree.py -> validate_graph_and_deps()` 形と少しずれていた。
  - 解決: `consultant` 指摘を踏まえ、`_validate_nodes()` の委譲先を `validate_graph_and_deps()` に寄せ、smoke test も更新した。

## 今後の推奨事項
- `S02` では `domain.validation.validate_graph_and_deps()` を最初の consumer とする `application/validate_tree.py` を導入し、legacy delegated validate path を閉じる。
- `S03` では `validate_graph_and_deps()` の deps 側中身を pure に拡張し、S01 で固定した seam をそのまま利用する。

## 省略/例外メモ
- 該当なし
