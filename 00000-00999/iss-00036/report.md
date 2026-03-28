---
種別: 実装報告書（Issue）
ID: "iss-00036"
タイトル: "Timestamp Based Discussion and ADR Naming"
関連GitHub: ["#36"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-03-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00036 Timestamp Based Discussion and ADR Naming — 実装報告（LOG）

## 実装サマリー (任意)
- `new doc` の discussion doc family を timestamp-prefix basename へ切り替え、`doc_id` を slugless identity として分離した。
- same-second collision では create lock 内で `-01-` からの suffix を family 全体で割り当て、`01..99` 枯渇時は explicit failure にした。

## 実装記録（セッションログ） (必須)

### 2026-03-29 00:00 - 00:56

#### 対象
- Step: S01, S02
- AC/EC: AC-001, AC-002, EC-001, EC-003, EC-004

#### 実施内容
- provider runtime の discussion doc filename allocator を連番から UTC timestamp 形式へ変更した。
- `doc_id` を `<ts>-<kind>` / `<ts>-<nn>-<kind>` の slugless identity に切り替え、write path は継続して `discussions/` に固定した。
- same-second collision を scope 内 discussion-doc family 全体で吸収する suffix allocator を追加し、`01..99` 枯渇時の fail-fast を実装した。
- CLI / runtime focused tests を timestamp contract に更新し、same-second suffix allocation・cross-type collision・suffix exhaustion を deterministic clock で検証した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_runtime_new_doc_s09

FAILED
- 既知の unrelated baseline failure が継続:
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_new_node_non_regression_for_shared_file_edits
  RuntimeError: GitHub linkage is mandatory for issue; local_only is not supported.
- 今回の S01/S02 変更対象の new-doc tests は pass。

python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09

FAILED
- 同じ既知の unrelated baseline failure 1 件のみ継続。
- `tests.cli_runtime.test_new` は pass。

python -m unittest \
  tests.cli_runtime.test_new.TestCliNew.test_new_doc_adr_increments_id_within_scope_discussions \
  tests.cli_runtime.test_new.TestCliNew.test_new_doc_scope_shorthand_resolves_local_ids \
  tests.cli_runtime.test_new.TestCliNew.test_new_doc_uses_timestamp_family_across_discussion_types \
  tests.cli_runtime.test_new.TestCliNew.test_new_doc_stdout_uses_slugless_id_and_discussions_path \
  tests.cli_runtime.test_new.TestCliNew.test_new_doc_ignores_nonconforming_files_for_timestamp_allocation \
  tests.cli_runtime.test_new.TestCliNew.test_new_doc_preserves_legacy_files_without_reusing_sequence_names \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_timestamp_regression_and_planning \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_generated_path_name_content_regression \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_doc_type_parity_template_selection_regression \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_suffix_exhaustion_fail_fast_no_write \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_parallel_new_doc_allocates_unique_suffixes

OK (11 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - timestamp basename / slugless `doc_id` / same-second suffix allocation / exhaustion failure を実装
- `tests/cli_runtime/test_new.py` - CLI の timestamp basename / slugless id / discussions path expectations へ更新
- `tests/cli_runtime/test_runtime_new_doc_s09.py` - deterministic clock で S01/S02 runtime regressions を更新
- `spec-dock/active/issue/report.md` - 本セッションの実装ログを追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- baseline で既知と共有されていた `test_new_node_non_regression_for_shared_file_edits` の failure は今回も unchanged。S01/S02 の targeted coverage は別コマンドで green を確認した。

---

### 2026-03-29 00:57 - 01:10

#### 対象
- Step: S01, S02 follow-up
- AC/EC: AC-001, AC-002, EC-001, EC-003

#### 実施内容
- discussion doc create 時の本文日付を `ports.clock.today()` ではなく、`doc_id` / filename timestamp と同じ UTC instant から導出するように修正した。
- create-side discussion filename parser を `01..99` suffix のみ受理する形へ絞り、既存の malformed `-00-` filename が suffix slot を消費しないようにした。
- 回帰 coverage を追加し、CLI では non-UTC clock mismatch 時の本文日付整合、runtime では malformed `-00-` filename ignore を固定した。

#### 実行コマンド / 結果
```bash
python -m unittest \
  tests.cli_runtime.test_new.TestCliNew.test_new_doc_renders_body_date_from_same_utc_instant_as_doc_id \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_timestamp_regression_and_planning

OK (2 tests)

python -m unittest \
  tests.cli_runtime.test_new.TestCliNew.test_new_doc_renders_body_date_from_same_utc_instant_as_doc_id \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_timestamp_regression_and_planning \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_generated_path_name_content_regression \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_doc_type_parity_template_selection_regression \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_suffix_exhaustion_fail_fast_no_write \
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_parallel_new_doc_allocates_unique_suffixes

OK (6 tests)

python -m unittest tests.cli_runtime.test_new

OK (33 tests)

python -m unittest tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09

FAILED
- 既知の unrelated baseline failure 1 件のみ継続:
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_new_node_non_regression_for_shared_file_edits
  RuntimeError: GitHub linkage is mandatory for issue; local_only is not supported.
- `tests.cli_runtime.test_new` は引き続き pass。
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - UTC instant 共有による discussion date/timestamp 整合と `01..99` suffix parser へ修正
- `tests/cli_runtime/test_new.py` - CLI で本文日付が `doc_id` と同じ UTC instant から描画される回帰 test を追加
- `tests/cli_runtime/test_runtime_new_doc_s09.py` - malformed `-00-` suffix を create-side allocation が無視する回帰を追加
- `spec-dock/active/issue/report.md` - follow-up fix と test results を追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- full targeted pair 実行時の failure は既知の baseline 1 件のみで、今回の S01/S02 follow-up 修正対象とは無関係。

---

### 2026-03-27 HH:MM - HH:MM

#### 対象
- Step: S01, S02, ...
- AC/EC: AC-___, EC-___

#### 実施内容
- ...

#### 実行コマンド / 結果
```bash
<command>

<result>
```

#### 変更したファイル
- `path/to/file1` - ...
- `path/to/file2` - ...

#### コミット
- <hash> <message>

#### メモ
- ...

---

### 2026-03-27 HH:MM - HH:MM

#### 対象
- Step: ...
- AC/EC: ...

#### 実施内容
- ...

---

## 遭遇した問題と解決 (任意)
- 問題: ...
  - 解決: ...

## 学んだこと (任意)
- ...
- ...

## 今後の推奨事項 (任意)
- ...
- ...

## 省略/例外メモ (必須)
- 該当なし
