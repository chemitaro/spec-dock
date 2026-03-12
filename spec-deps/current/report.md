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
- `a54803591b561f8f90be8f62a7bd5564d64969ba` `feat(runtime): validateのS02 sliceをapplication層へ分離`

#### メモ
- `app.py` から `SpecGraph` や `_Node` を application へ渡さず、`StoredMetaRecord` 境界に留めた。
- validate の failure path は既存どおり main の `error: ...` 包装を維持し、renderer は stdout/stderr の正本だけを持つ形にした。

---

## 遭遇した問題と解決
- 問題: 初回実装では `app.py` の live seam が `validate_graph()` 直結で、将来の `application/validate_tree.py -> validate_graph_and_deps()` 形と少しずれていた。
  - 解決: `consultant` 指摘を踏まえ、`_validate_nodes()` の委譲先を `validate_graph_and_deps()` に寄せ、smoke test も更新した。
- 問題: 初回の S03 着手時に `domain/deps.py` が graph-only で dependency topology を導出する前提になっており、`SpecGraph` の入力契約と衝突した。
  - 解決: discussion 003 で整理した Option B を採用し、`issue_depends_on_map` の正本を `application / infra` 側へ移し、S03 は supplied topology を受ける pure rule のみを実装する形へ設計と計画を修正した。

---

### 2026-03-12 06:10 - 07:10

#### 対象
- Step: S03
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `domain/models.py` に `NodeId`, `IssueSnapshot`, `IssueStatusSnapshot`, `ProgressMap`, `DepsNodeState`, `DepsState`, `DepsEvaluation`, `TargetDepsInspection`, `ActiveSelection`, `BranchDecision` を追加し、S03 pure core の DTO を固定した。
- `domain/status.py` を新規追加し、`resolve_issue_statuses()` と `build_progress_map()` を no-I/O pure function として実装した。
- `domain/deps.py` を新規追加し、`evaluate_readiness()`, `inspect_target_deps()`, `build_effective_deps_map()`, `build_deps_state()`, `validate_deps_cycles()`, `collect_reachable_issue_ids()` を Option B 契約どおり supplied topology 前提で実装した。
- 旧前提の S03 下書きは放棄し、graph から dependency topology を compile しない pure domain のみへ作り直した。
- `tests/test_runtime_domain_s03.py` を追加し、status source 選択、progress 集計、explicit `issue_depends_on_map` 入力、active decoration、parent merge、cycle validation、no shell I/O import を固定した。
- `code_reviewer` による S03 scope review を行い、重大指摘なしで pass を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_runtime_domain_s03

Ran 8 tests in 0.011s
OK

python -m unittest -v tests.test_runtime_domain_s03 tests.test_runtime_domain_s01 tests.test_runtime_validate_s02

Ran 24 tests ... OK

python -m unittest discover -v

Ran 186 tests in 21.525s
OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/models.py` - S03 DTO を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/status.py` - pure status / progress rule を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/deps.py` - pure deps / readiness / cycle validation rule を追加
- `tests/test_runtime_domain_s03.py` - S03 focused tests

#### コミット
- `d42b3a820bb9c21f3bb41123d982b06d48cfdbe4` `feat(runtime): S03のpure domainルールとfocused testを導入`

#### メモ
- `build_effective_deps_map()` は parent merge を pure path に閉じており、S04 の topology provider が issue-only map を返す場合は issue key 部分だけを自然に消費する。
- live consumer 接続は計画どおり `S04` 以降へ残し、S03 では `app.py` / `application` / `presentation` を変更していない。

---

### 2026-03-12 07:15 - 08:15

#### 対象
- Step: S04
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `application/check_deps.py` と `application/status_context.py` を追加し、`deps check` の read-side use case と status source 正規化 seam を導入した。
- `infra/deps_reader.py` を追加し、canonical `issue_depends_on_map` の first consumer として `deps check` へ topology provider を接続した。
- `application/validate_tree.py` と `domain/validation.py` を更新し、topology reader が束縛されている場合のみ `validate_graph_and_deps(graph, issue_depends_on_map=...)` を使う internal reconnect を導入した。
- `presentation/json_state.py` を追加して `deps check --json` の ownership を移し、`presentation/cli_text.py` には text 側の rendering を追加した。
- `app.py` は staged delegation owner のまま保ち、`deps check` の経路だけを `application/check_deps.py` へ委譲した。
- `tests/test_runtime_deps_s04.py` を追加し、use case/result、status context、topology reader、validate reconnect、legacy delegated deps smoke を固定した。
- `tests/test_cli.py` の `deps check` 関連 regression を更新し、cycle fail-fast、json/text path、source selection、stderr/stdout の観測点を S04 契約に合わせた。
- `code_reviewer` による S04 scope review を行い、重大指摘なしで pass を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_runtime_deps_s04

Ran 5 tests ... OK

python -m unittest -v tests.test_runtime_deps_s04 tests.test_runtime_validate_s02 tests.test_runtime_domain_s03

Ran 20 tests in 0.031s
OK

python -m unittest discover -v

Ran 191 tests ... OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - `deps check` を use case + renderer へ委譲
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `CheckDepsRequest` / `DepsCheckResult` など S04 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - `DepsTopologyReader` など read-side ports を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/validate_tree.py` - topology reconnect を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/check_deps.py` - deps use case を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/status_context.py` - issue status source 正規化 seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - optional topology を受ける validate 境界へ更新
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py` - `DepsTopologyLoadResult` など infra 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py` - topology provider を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/derived_state_reader.py` - cached status reader を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py` - github status reader を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py` - active manifest load seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - deps text renderer を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` - deps json renderer を追加
- `tests/test_runtime_deps_s04.py` - S04 focused tests
- `tests/test_cli.py` - deps CLI regression を更新

#### コミット
- `74f57b9901d411861bd7fcdd7a0d8bd18c19ca37` `feat(deps): S04のdeps checkスライスとtopology providerを導入`

#### メモ
- `deps check` では topology invalid/cycle を reachable/unreachable にかかわらず fail-fast とし、`active set` / `sync` 側の再利用は計画どおり後続 step へ残した。
- `validate_tree()` の reconnect は internal seam に留めており、S04 の primary user-facing review scope は `deps check` のまま維持している。

---

### 2026-03-12 08:20 - 09:10

#### 対象
- Step: S05
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `application/set_active.py` に `show_active()` の read path を導入し、`active show` のみを `application` へ切り出した。
- `infra/active_store.py` を read-only の migration-capable loader として拡張し、`.agent/active.json`、`.work/active.json`、`.work/current.json` の優先順と no write-back を `load_active_manifest()` に閉じた。
- `presentation/cli_text.py` に `render_active_show_text()` を追加し、`active show` の text 出力を use case から分離した。
- `app.py` は staged delegation owner のまま維持し、`active show` の経路だけを新 use case + renderer に委譲した。
- `tests/test_runtime_active_s05.py` を追加し、agent manifest read model、legacy priority、no write-back、zero-input/exit 0、legacy delegated smoke を固定した。
- 初回 review では `.agent/active.json` の `all-null` cleared manifest を invalid 扱いして stale legacy fallback が起きうる P1 指摘を受けた。
- `infra/active_store.py` を修正し、`initiative/epic/issue` がすべて `null` の manifest を valid cleared state として `source=\"agent.active\"` のまま扱うように変更し、focused test を追加して再レビューを pass させた。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_runtime_active_s05

Ran 5 tests ... OK

python -m unittest -v tests.test_runtime_active_s05 tests.test_runtime_deps_s04 tests.test_runtime_validate_s02 tests.test_runtime_domain_s03

Ran 25 tests in 0.033s
OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - `active show` を use case + renderer へ委譲
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `ActiveViewEntry` / `ActiveViewResult` など S05 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - active read port 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py` - `show_active()` の read path を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py` - migration-capable read loader と cleared manifest fix
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py` - active manifest read DTO を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - `render_active_show_text()` を追加
- `tests/test_runtime_active_s05.py` - S05 focused tests

#### コミット
- 未実施

#### メモ
- `load_active_manifest_no_migrate()` は S05 の user-facing path では使っていない。
- `all-null` `.agent/active.json` は cleared state として扱い、legacy fallback を起こさないようにした。

## 今後の推奨事項
- `S06` で `S04` の topology provider を `active set` の readiness guard に再利用し、fail-fast 順序を command 契約へ持ち上げる。
- `S06` では `active clear` の cleared manifest と `S05` の read loader が矛盾しないことを継続的に確認する。

## 省略/例外メモ
- 該当なし
