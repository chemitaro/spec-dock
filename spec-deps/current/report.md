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
- `1372b19f8b35930d1185893d567f19f495d92f0b` `feat(active): S05のactive show read sliceを導入`

#### メモ
- `load_active_manifest_no_migrate()` は S05 の user-facing path では使っていない。
- `all-null` `.agent/active.json` は cleared state として扱い、legacy fallback を起こさないようにした。

---

### 2026-03-12 09:15 - 10:20

#### 対象
- Step: S06
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `application/set_active.py` に `active set` / `active clear` の write path を導入し、guard / order / rollback を application 層へ移した。
- `domain/active.py` を追加し、active manifest の patch / restore に必要な pure helper を分離した。
- `S04` で導入した topology provider を readiness guard に再利用し、invalid/cyclic topology を readiness 判定より前に fail-fast する順序を固定した。
- `commit_active_state()` の rollback 範囲を step 7-9 failure に限定し、pre-step7 failure では snapshot/restore を走らせないようにした。
- `infra/git_cli.py` を追加し、branch decision / checkout pre-write の切り出しを行った。
- `tests/test_runtime_active_s06.py` を追加し、blocked/unknown/force、pre-step7 no-rollback、patch failure rollback、active clear を focused に固定した。
- 初回 review では、`initiative` / `epic` の non-issue target が `guard_reason=\"unknown\"` かつ blockers 空のときに通ってしまう P1 指摘を受けた。
- `application/set_active.py` を修正し、non-issue でも `deps.ready` を正本に guard するよう統一し、focused test を追加して再レビューを pass させた。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_runtime_active_s06

Ran 6 tests ... OK

python -m unittest -v tests.test_runtime_active_s06 \
  tests.test_cli.TestCli.test_active_set_without_github_blocks_unknown_issue_even_without_deps \
  tests.test_cli.TestCli.test_active_set_epic_and_initiative_use_v2_deps_guard

Ran 8 tests ... OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - `active set` / `active clear` を use case へ委譲
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - S06 用 DTO を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - active write / git port 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/set_active.py` - active write use case / rollback 制御 / guard fix
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/active.py` - active patch / restore helper を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/tree.py` - active selection helper を拡張
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py` - snapshot / restore / write seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/contracts.py` - active write rollback DTO を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/git_cli.py` - git checkout / branch seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - active set/clear text path を追加
- `tests/test_runtime_active_s06.py` - S06 focused tests
- `tests/test_cli.py` - active set/clear CLI regression を更新

#### コミット
- `8e2c74e2495edbcb30846bef105c89454b9a9e22` `feat(active): S06のactive set/clear write sliceを導入`

#### メモ
- non-issue target でも `deps.ready` を使って `unknown` を拒否するようにしたため、dependency closure が空でも status 不明なら active mutation を止める。
- 今回は focused tests までを再実行し、全件 `discover` は未再実行。

## 今後の推奨事項
- `S07` では `sync` の preflight / artifact write を `S04` / `S06` の shared seam に再接続する。
- `S07` で active auto-update は `ActiveUpdateOutcome` と artifact write failure の境界を明確にしたまま導入する。

---

### 2026-03-12 10:25 - 11:45

#### 対象
- Step: S07
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `application/sync_state.py` を追加し、`collect_sync_state()`、`maybe_auto_update_from_branch()`、`write_sync_artifacts()`、`sync_after_import()` を導入した。
- `S06` の `commit_active_state()` を再利用し、branch 由来 active update を artifact write より前に適用する流れを固定した。
- `infra/artifact_writer.py`, `infra/json_store.py`, `infra/clock.py` を追加し、artifact write と timestamp 取得の責務を分離した。
- `presentation/json_state.py`, `presentation/markdown.py`, `presentation/puml.py`, `presentation/cli_text.py` を拡張し、JSON / markdown / PUML / text の renderer 所有境界を整理した。
- `tests/test_runtime_sync_s07.py` を追加し、sync use case、cycle fail-fast、force placeholder、artifact failure contract、legacy delegated smoke を focused に固定した。
- 初回 review では、artifact writer の途中失敗が `failed_before_write` と誤分類される P1 指摘を受けた。
- `application/sync_state.py` を修正し、writer 実行中の例外は `failed_partial_or_stale` として再分類し、pre-write failure だけを `failed_before_write` に残すようにした。
- `tests/test_cli.py` の関連 setup を `--force` 前提へ補正し、S06 で導入した unknown readiness block と衝突しないよう整理した。
- 修正後の再レビューで重大指摘なしの pass を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_runtime_sync_s07 -v

Ran 9 tests ... OK

python -m unittest discover -v

Ran 211 tests in 32.716s
OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - S07 用 DTO を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - sync / artifact ports を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` - sync pipeline を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/active.py` - sync path から再利用する helper を拡張
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_writer.py` - artifact writer を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/clock.py` - clock seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/json_store.py` - JSON store seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/contracts.py` - artifact bundle 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/json_state.py` - sync JSON renderer を拡張
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/markdown.py` - markdown renderer を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py` - PUML renderer を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - sync text renderer を追加
- `tests/test_runtime_sync_s07.py` - S07 focused tests
- `tests/test_cli.py` - sync / active setup regression を更新

#### コミット
- `f63bd9831e4914ceac22be3baaff1a751b19a5d7` `feat(sync): S07のsyncスライスとartifact書き込み契約を導入`

#### メモ
- artifact writer の途中失敗は部分書き込みの可能性を失わないよう `failed_partial_or_stale` に固定した。
- pre-write failure は `failed_before_write` のまま維持している。

## 今後の推奨事項
- `S08` では create core を no-write preflight と planned write に分けて固定する。
- `S09` では `new doc` を node create から独立枝として閉じる。

---

### 2026-03-12 11:50 - 12:35

#### 対象
- Step: S08
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `application/create_node.py` を追加し、`plan_node_creation()` / `CreatePlan` / `execute_create_plan()` / `CreateNodeResult` を導入した。
- `infra/fs_repo.py` と `infra/template_scaffolder.py` を追加し、scaffold copy / meta write の責務を分離した。
- no-write preflight を `planned_paths` 全体へ適用し、collision 時は fail-fast で書き込みなしに統一した。
- `copy_scaffolded_tree -> write_meta` の順序を core と focused test の両方で固定した。
- `app.py` は staged delegation owner のまま維持し、`new initiative|epic|issue` のみ新 core へ委譲した。
- `tests/test_runtime_new_s08.py` を追加し、planning/execution/order/collision/default mode/reuse seam/renderer/delegation smoke を回帰化した。
- `code_reviewer` による S08 scope review を行い、重大指摘なしで pass を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_runtime_new_s08 -v

Ran 9 tests ... OK

python -m unittest discover -v

Ran 220 tests ... OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - new node path を create core へ委譲
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `CreatePlan` / `CreateNodeResult` などを追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - create 用 port 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - create core を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` - fs write seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/template_scaffolder.py` - scaffold copy / render seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py` - create で使う github helper を拡張
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - new node text renderer を追加
- `tests/test_runtime_new_s08.py` - S08 focused tests

#### コミット
- `a92445c4dad818c9c989351b213e6730e08cc523` `feat(new): S08のnew node coreを導入`

#### メモ
- `app.py` の旧 `_new_*` 実装本体は rollback しやすさのため残し、先頭 return で新 core に委譲する形にしている。
- `github_mode=\"link_existing\"` は S08 で契約だけ整え、主な再利用は S10 側で行う前提。

---

### 2026-03-12 12:40 - 13:20

#### 対象
- Step: S09
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `CreateDiscussionDocRequest` / `CreateDiscussionDocResult` を追加し、`new doc` を node create と別枝の use case として切り出した。
- `application/create_node.py` に `plan_discussion_doc()` と `create_discussion_doc()` を追加し、共有シーケンス判定、duplicate/overflow fail-fast、template load/render/write を実装した。
- `presentation/cli_text.py` に `render_new_doc_text()` を追加し、`new doc` の result/text 契約を固定した。
- `app.py` は staged delegation owner のまま維持し、`_new_doc()` のみ新 core へ委譲した。
- `tests/test_runtime_new_doc_s09.py` を追加し、sequence/path/content/type parity/no-write/invalid slug/renderer/delegation/new-node非退行を focused に固定した。
- `code_reviewer` による S09 scope review を行い、重大指摘なしで pass を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_runtime_new_doc_s09 -v

Ran 8 tests ... OK

python -m unittest discover

Ran 228 tests ... OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - `new doc` を use case へ委譲
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `CreateDiscussionDoc*` 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - `new doc` core を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - `render_new_doc_text()` を追加
- `tests/test_runtime_new_doc_s09.py` - S09 focused tests

#### コミット
- `cc5069bd122960d9bbe3ba66cc10e70fd4c8e557` `feat(new): S09のnew doc coreを導入`

#### メモ
- `scope_node_id` は canonical id 前提で、CLI 経由では `app.py` 側で解決済みの値だけを use case に渡している。
- `app.py` の旧 `_new_doc` 本体は staged rollback 用に残している。

---

### 2026-03-12 13:25 - 14:20

#### 対象
- Step: S10
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `application/import_node.py` を追加し、`import` 専用 use case と `sync_after_import()` を導入した。
- `resolve_parent_for_import()` を実装し、`parent_id` 未指定時は `load_active_manifest_no_migrate() -> ActiveSelection -> resolve_parent_from_active()` の鎖で親解決するようにした。
- duplicate guard と no-write preflight を GitHub lookup より前へ配置し、offline/degraded な状況でも deterministic に duplicate/collision を返すよう修正した。
- `build_linked_create_request()` で `CreateNodeRequest(github_mode=\"link_existing\")` へ変換し、`plan_node_creation()` / `execute_create_plan()` を再利用する形へ統一した。
- `app.py` は staged delegation owner のまま維持し、`import` を `application/import_node.py` へ委譲した。
- `presentation/cli_text.py` に `render_import_text()` を追加し、import 結果の text 契約を固定した。
- `tests/test_runtime_import_s10.py` を追加し、parent fallback、duplicate/no-write、import->sync、artifact path/content、negative path、no_migrate chain、reuse seam、renderer、legacy delegated smoke を focused に固定した。
- 初回 review では duplicate/collision preflight が `issue_view_minimal()` より後ろにある P1 指摘を受けた。
- `application/import_node.py` と `tests/test_runtime_import_s10.py` を修正し、duplicate/collision ケースでは `view_calls == []` であることまで含めて再レビューを pass させた。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_runtime_import_s10

Ran 9 tests ... OK

python -m unittest discover -v

Ran 237 tests ... OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - import path を use case へ委譲
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - S10 用 DTO を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - import 用 port 契約を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/import_node.py` - import core と sync_after_import を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/tree.py` - `resolve_parent_from_active()` を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - import text renderer を追加
- `tests/test_runtime_import_s10.py` - S10 focused tests

#### コミット
- `7722d79c1ae5fa77b7d85320c0cb47d9d09be2e6` `feat(import): s10のimport coreとsync連携を導入`

#### メモ
- `post_import_sync` の artifact 書き込み失敗は `ImportNodeResult.post_import_sync.artifact_failure` と warning で表現し、CLI 終了コード変更は今回扱っていない。
- `load_active_manifest_no_migrate()` の user-facing consumer は import parent fallback のみに限定している。

---

### 2026-03-12 14:25 - 15:30

#### 対象
- Step: S11
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- `cli/*` と `commands/*` を追加し、parser/help/dispatch ownership を `cli` 側へ移した。
- `application/contracts.py` に `UseCases` facade を追加し、`commands/*` は request normalization + renderer selection に限定した。
- `app.py` を thin entrypoint 化し、`registry -> parser -> bootstrap -> dispatch` の起動に責務を縮小した。
- `commands/sync.py` は staged coexistence のため facade 経由 legacy 委譲を維持した。
- `tests/test_runtime_shell_s11.py` を追加し、parser/help/dispatch / wrapper / staged delegation の focused regression を固定した。
- 初回 review では `deps --json` が stderr warning を出してしまう P2 指摘を受けた。
- `commands/deps.py` を修正し、JSON mode では `CliText.warnings=[]` として stdout-only 契約を守るようにした。text モードの warning は維持した。
- 修正後の focused tests と full `discover` を通し、再レビューで pass を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_runtime_shell_s11

Ran 6 tests ... OK

python -m unittest discover -v

Ran 244 tests ... OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/app.py` - thin entrypoint 化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - `UseCases` facade を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - bootstrap 用 port 契約調整
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/__init__.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/dispatch.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/__init__.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/contracts.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/targets.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/new.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/import_cmd.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/active.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/sync.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/deps.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/validate.py`
- `tests/test_runtime_shell_s11.py` - S11 focused tests
- `tests/test_runtime_validate_s02.py` - ownership 変更に合わせて更新
- `tests/test_cli.py` - `deps --json` stdout-only 契約を更新

#### コミット
- `7e600f6d92b1a6f8cd00ae45a96cda4166e9ed0d` `feat(cli): s11のshell integrationを正本化`

#### メモ
- `commands/*` は `UseCases facade + application DTO + presentation renderer + commands/contracts` のみに依存する方針へ揃えた。
- `sync` は意図的に staged coexistence を残し、最終 detach は後続 step に残している。

---

### 2026-03-12 15:35 - 16:10

#### 対象
- Step: S12
- AC/EC: AC-003, AC-005, EC-001

#### 実施内容
- `tests/test_cli.py` を S12 inventory guard として追加し、split 後 test tree の critical inventory を package discovery 前提で固定した。
- `tests/test_init_update.py` を追加し、installer regression を runtime split 後も独立 top-level module として維持した。
- runtime focused test 群を `tests/cli_runtime/`, `tests/domain_runtime/`, `tests/presentation_runtime/` へ再配置し、`tests/__init__.py` と各 package `__init__.py` で regular package discovery に統一した。
- 初回 review では `tests/cli_runtime/test_runtime_validate_s02.py`、`test_runtime_deps_s04.py`、`test_runtime_active_s05.py`、`test_runtime_new_s08.py`、`test_runtime_new_doc_s09.py` が S12 inventory/grouping guard から漏れている P1 指摘を受けた。
- `tests/test_cli.py` を修正し、上記 5 モジュールを inventory と command-group sentinel checks の両方へ追加して、分割後 critical inventory coverage を完全化した。
- 修正後に focused suite と full discover を通し、`code_reviewer` の再レビューで pass を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.test_cli tests.cli_runtime.test_runtime_validate_s02 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_runtime_active_s05 tests.cli_runtime.test_runtime_new_s08 tests.cli_runtime.test_runtime_new_doc_s09

Ran 37 tests ... OK

python -m unittest discover -v

Ran 247 tests ... OK
```

#### 変更したファイル
- `tests/__init__.py` - regular package discovery 用 package init を追加
- `tests/test_cli.py` - S12 inventory / grouping guard を追加
- `tests/test_init_update.py` - installer regression を top-level module へ分離
- `tests/cli_runtime/__init__.py`
- `tests/cli_runtime/harness.py`
- `tests/cli_runtime/test_active.py`
- `tests/cli_runtime/test_deps.py`
- `tests/cli_runtime/test_import.py`
- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/test_runtime_active_s05.py`
- `tests/cli_runtime/test_runtime_active_s06.py`
- `tests/cli_runtime/test_runtime_deps_s04.py`
- `tests/cli_runtime/test_runtime_import_s10.py`
- `tests/cli_runtime/test_runtime_new_doc_s09.py`
- `tests/cli_runtime/test_runtime_new_s08.py`
- `tests/cli_runtime/test_runtime_shell_s11.py`
- `tests/cli_runtime/test_runtime_validate_s02.py`
- `tests/cli_runtime/test_sync.py`
- `tests/cli_runtime/test_validate.py`
- `tests/cli_runtime/test_wrappers.py`
- `tests/domain_runtime/__init__.py`
- `tests/domain_runtime/test_runtime_domain_s01.py`
- `tests/domain_runtime/test_runtime_domain_s03.py`
- `tests/presentation_runtime/__init__.py`
- `tests/presentation_runtime/test_runtime_sync_s07.py`
- `tests/test_runtime_active_s05.py` - deleted
- `tests/test_runtime_active_s06.py` - deleted
- `tests/test_runtime_deps_s04.py` - deleted
- `tests/test_runtime_domain_s01.py` - deleted
- `tests/test_runtime_domain_s03.py` - deleted
- `tests/test_runtime_import_s10.py` - deleted
- `tests/test_runtime_new_doc_s09.py` - deleted
- `tests/test_runtime_new_s08.py` - deleted
- `tests/test_runtime_shell_s11.py` - deleted
- `tests/test_runtime_sync_s07.py` - deleted
- `tests/test_runtime_validate_s02.py` - deleted

#### コミット
- 未実施

#### メモ
- `tests/test_cli.py` は inventory 存在確認に加えて sentinel method の存在も確認し、単なる path existence ではなく split coverage guard として機能させている。
- S12 では runtime code 変更は行わず、test tree の再配置と discovery 契約の固定に限定した。

---

### 2026-03-12 16:15 - 17:20

#### 対象
- Step: S13
- AC/EC: AC-001, AC-005, EC-001

#### 実施内容
- layered runtime (`commands/application/infra/presentation/cli`) から legacy helper 直依存を外し、`infra/json_store.py`, `infra/clock.py`, `infra/github_cli.py`, `presentation/markdown.py`, `presentation/puml.py` を正本 owner とする方向へ整理した。
- `io_json.py`, `github.py`, `render_md.py`, `render_puml.py` は互換 shim として残し、旧 entry/legacy path からの後方互換を維持しつつ、layered path からは直接参照しない構造へ切り替えた。
- `tests/cli_runtime/test_runtime_shell_s11.py` に final API call-site / no legacy helper direct import / layer direction assertion の structural checks を追加した。
- `tests/cli_runtime/test_new.py` は readonly lock seam の owner 変更に合わせて `infra/fs_repo.py` 側を観測点へ更新した。
- `tests/domain_runtime/test_runtime_domain_s03.py` に layer detachment 後も `domain` が pure であることの回帰を維持する assertion を追加した。
- 初回 review では layer-boundary import guard が fully-qualified import (`spec_dock_runtime.io_json`) と `from .. import io_json` を十分に検出できない P2 指摘を受けた。
- `tests/cli_runtime/test_runtime_shell_s11.py` を修正し、`_iter_import_modules()`, `_normalize_import_module()`, `_import_root()` を導入して fully-qualified / relative import を共通正規化するよう改善した。
- 再 review で no blocking findings / pass を確認した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.cli_runtime.test_runtime_shell_s11 tests.cli_runtime.test_runtime_import_s10 tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.presentation_runtime.test_runtime_sync_s07 tests.domain_runtime.test_runtime_domain_s01 tests.domain_runtime.test_runtime_domain_s03

Ran 53 tests ... OK

python -m unittest -v tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_import_scan_detects_legacy_helper_import_styles tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_import_root_normalizes_fully_qualified_layer_modules tests.cli_runtime.test_runtime_shell_s11.RuntimeShellS11Tests.test_final_api_call_site_and_structural_regression

Ran 3 tests ... OK

python -m unittest discover -v

Ran 247 tests ... OK

rg -n "^from \\.\\.(io_json|github|render_md|render_puml|active|nodes|ids) import|^from \\.(io_json|github|render_md|render_puml|active|nodes|ids) import" src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli

(no output)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` - `infra/clock.py` 正本へ切替
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - layered bootstrap から legacy `io_json.py` 直依存を除去
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/github.py` - compatibility shim 化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/active_store.py` - `infra/json_store.py` / `infra/clock.py` 正本へ切替
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/clock.py` - time helper 正本化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/deps_reader.py` - `infra/json_store.py` 正本へ切替
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/derived_state_reader.py` - `infra/json_store.py` 正本へ切替
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` - `infra/json_store.py` / `infra/clock.py` 正本へ切替
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py` - GitHub helper 正本化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/json_store.py` - JSON read/write helper 正本化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/io_json.py` - compatibility shim 化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/markdown.py` - markdown renderer 正本化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/puml.py` - puml renderer 正本化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/render_md.py` - compatibility shim 化
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/render_puml.py` - compatibility shim 化
- `tests/cli_runtime/test_new.py` - readonly lock seam regression を owner 更新
- `tests/cli_runtime/test_runtime_shell_s11.py` - helper detachment / layer boundary structural regressions を追加
- `tests/domain_runtime/test_runtime_domain_s03.py` - pure domain regression を補強

#### コミット
- 未実施

#### メモ
- rollback basis はこの step 以降 staged seam ではなく commit 単位 (`git revert / commit rollback`) を前提に扱う。
- `app.py` には互換用 legacy 実装が残るが、`main` の shell path は thin entrypoint のまま維持し、layered path からの legacy helper direct import は構造テストで禁止している。

## 省略/例外メモ
- 該当なし
