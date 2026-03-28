---
種別: 実装報告書（Issue）
ID: "iss-00036"
タイトル: "Timestamp Based Discussion and ADR Naming"
関連GitHub: ["#36"]
状態: "draft"
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

### 2026-03-29 01:11 - 01:35

#### 対象
- Step: S03
- AC/EC: AC-003, EC-002

#### 実施内容
- validation の discussion-doc scan を sequential duplicate 前提から timestamp contract 前提へ更新した。
- valid timestamp names は新 contract として検査し、legacy sequential names (`NNN-type-slug.md`) は grandfathered artifact として許容するようにした。
- timestamp/discussion-doc intent を持つ malformed filenames は explicit validation error とし、`rules.md` のような unrelated files は ignore する境界を追加した。
- duplicate detection を new contract に合わせて更新し、unsuffixed timestamp slot と suffixed timestamp slot の重複を reject するようにした。
- validate tests を S03 観点で追加・更新し、legacy grandfathering / malformed candidates / duplicate timestamp slot / duplicate suffix slot を固定した。

#### 実行コマンド / 結果
```bash
python -m unittest \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_grandfathers_legacy_discussion_names_and_ignores_unrelated_files \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_rejects_malformed_discussion_doc_candidates \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_detects_duplicate_discussion_timestamp_slot \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_detects_duplicate_discussion_timestamp_suffix_slot

FAILED (9 failures)
- Red確認: validate はまだ legacy duplicate sequence を reject し、malformed / timestamp-slot duplicate を検出できなかった。

python -m unittest \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_grandfathers_legacy_discussion_names_and_ignores_unrelated_files \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_rejects_malformed_discussion_doc_candidates \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_detects_duplicate_discussion_timestamp_slot \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_detects_duplicate_discussion_timestamp_suffix_slot

OK (4 tests)

python -m unittest tests.cli_runtime.test_validate

OK (30 tests)

python -m unittest tests.cli_runtime.test_validate tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09

FAILED
- 既知の unrelated baseline failure 1 件のみ継続:
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_new_node_non_regression_for_shared_file_edits
  RuntimeError: GitHub linkage is mandatory for issue; local_only is not supported.
- `tests.cli_runtime.test_validate` / `tests.cli_runtime.test_new` の coverage では今回の S03 変更は green。

python -m unittest tests.cli_runtime.test_new

OK (33 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - timestamp discussion-doc validation、legacy grandfathering、malformed candidate error、timestamp slot duplicate detection を実装
- `tests/cli_runtime/test_validate.py` - S03 用の validate regressions を追加し、旧 sequential duplicate 期待を新 contract へ更新
- `spec-dock/active/issue/report.md` - S03 の実装ログを追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- known baseline failure は `tests.cli_runtime.test_runtime_new_doc_s09` の既知 1 件のみで、今回の validation 変更とは無関係。
- S03 の review-ready evidence は full validate module green と、新規 S03 targeted tests green で補完した。

---

### 2026-03-29 01:36 - 01:50

#### 対象
- Step: S03 follow-up
- AC/EC: AC-003, EC-002

#### 実施内容
- malformed discussion filename candidate 判定を date-only prefix (`YYYYMMDD-...`) と compact timestamp-like prefix (`YYYYMMDDHHMMSSz-...`) まで広げ、discussion doc family への intent が見える場合は validation error にした。
- valid upper-bound collision suffix (`-99-`) を positive coverage で固定した。
- `research` が timestamp / legacy の両方で引き続き discussion-doc family として validate されることを positive coverage で固定した。

#### 実行コマンド / 結果
```bash
python -m unittest \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_rejects_malformed_discussion_doc_candidates \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_accepts_high_end_discussion_timestamp_suffix \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_accepts_research_discussion_docs

OK (3 tests)

python -m unittest tests.cli_runtime.test_validate

OK (32 tests)

python -m unittest tests.cli_runtime.test_validate tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09

FAILED
- 既知の unrelated baseline failure 1 件のみ継続:
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_new_node_non_regression_for_shared_file_edits
  RuntimeError: GitHub linkage is mandatory for issue; local_only is not supported.
- `tests.cli_runtime.test_validate` は green。combined command の failure は今回の S03 validation follow-up 変更とは無関係。
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - malformed discussion-doc candidate 判定を date-only / compact timestamp-like prefixes まで拡張
- `tests/cli_runtime/test_validate.py` - malformed candidate regressions と `-99-` / `research` positive coverage を追加
- `spec-dock/active/issue/report.md` - S03 review follow-up を追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- combined command の既知 baseline failure は unchanged。今回追加した S03 follow-up coverage は targeted / full validate module の両方で green を確認した。

---

### 2026-03-29 01:51 - 02:05

#### 対象
- Step: S03 remaining review findings
- AC/EC: AC-003, EC-002

#### 実施内容
- malformed discussion filename candidate 判定を timestamp-intent token に限定し、`20260329todo.md` のような arbitrary date-prefixed file は ignore しつつ、`20260329x123456z-adr-kickoff.md` や `20260329t12345z-adr-kickoff.md` のような timestamp contract typo は reject するように絞り込んだ。
- same timestamp で unsuffixed 1件 + distinct suffixed files (`-01-`, `-99-`) の混在が valid であることを validate coverage に追加した。
- 既存の legacy sequential grandfathering と unrelated `rules.md` ignore が崩れていないことを focused/full validate 実行で再確認した。

#### 実行コマンド / 結果
```bash
python -m unittest \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_grandfathers_legacy_discussion_names_and_ignores_unrelated_files \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_rejects_malformed_discussion_doc_candidates \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_accepts_mixed_same_timestamp_unsuffixed_and_suffixed_slots

OK (3 tests)

python -m unittest tests.cli_runtime.test_validate

OK (33 tests)

python -m unittest tests.cli_runtime.test_validate tests.cli_runtime.test_new tests.cli_runtime.test_runtime_new_doc_s09

FAILED
- 既知の unrelated baseline failure 1 件のみ継続:
  tests.cli_runtime.test_runtime_new_doc_s09.TestRuntimeNewDocS09.test_new_node_non_regression_for_shared_file_edits
  RuntimeError: GitHub linkage is mandatory for issue; local_only is not supported.
- `tests.cli_runtime.test_validate` は green。combined command の failure は今回の S03 remaining review findings 対応とは無関係。
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - malformed timestamp-intent classifier を discussion-doc intent に限定し、over-match を回避
- `tests/cli_runtime/test_validate.py` - timestamp typo regressions、same-timestamp mixed-slot positive case、unrelated date-prefixed ignore coverage を追加
- `spec-dock/active/issue/report.md` - S03 remaining review findings 対応ログを追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- 指示どおり focused/full validate を再実行し、combined command でも既知 baseline failure 1 件のみ unchanged を確認した。

---

### 2026-03-29 02:06 - 02:15

#### 対象
- Step: S03 remaining review findings follow-up
- AC/EC: AC-003, EC-002

#### 実施内容
- malformed discussion filename candidate 判定で discussion kind token を case-insensitive に見つけるようにし、`20260329t123456z-ADR-kickoff.md` / `20260329t123456z-01-NOTE-memo.md` のような uppercase kind typo を explicit validation error にした。
- timestamp token の直後に空 separator slot がある `20260329t123456z--adr-kickoff.md` も malformed discussion-doc candidate として reject するように補強した。
- unrelated `rules.md` / `20260329todo.md` ignore と legacy sequential grandfathering が維持される前提で negative coverage を追加した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_validate

OK (33 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - malformed candidate 判定に uppercase discussion kind typo / empty separator slot を追加
- `tests/cli_runtime/test_validate.py` - malformed `--` separator と uppercase kind typo の negative coverage を追加
- `spec-dock/active/issue/report.md` - S03 follow-up log を追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- 今回の指示に従い `python -m unittest tests.cli_runtime.test_validate` を再実行し green を確認した。combined command は未再実行のため、この entry では追加の baseline failure は観測していない。

---

### 2026-03-29 02:16 - 02:25

#### 対象
- Step: S03 latest remaining review findings
- AC/EC: AC-003, EC-002

#### 実施内容
- malformed discussion filename candidate 判定を timestamp-intent / legacy-sequence-intent prefixで fail-closed に寄せ、unknown kind token (`...-bogus-...`) と malformed suffix token (`...-0a-...`) を明示的に reject するようにした。
- unrelated `rules.md` と `20260329todo.md` の ignore は維持したまま、review 指摘の 3 ケースを validate negative coverage に追加した。

#### 実行コマンド / 結果
```bash
python -m unittest \
  tests.cli_runtime.test_validate.TestCliValidate.test_validate_rejects_malformed_discussion_doc_candidates

OK (1 test)

python -m unittest tests.cli_runtime.test_validate

OK (33 tests)
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - timestamp/legacy discussion filename malformed candidate 判定を fail-closed 化
- `tests/cli_runtime/test_validate.py` - unknown kind token / malformed suffix token regressionsを追加
- `spec-dock/active/issue/report.md` - S03 latest follow-up log を追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- 今回の確認は validate の focused/full suite のみ実行。既知の unrelated baseline failure については再観測していない。

---

### 2026-03-29 02:26 - 02:35

#### 対象
- Step: S03 last remaining review finding
- AC/EC: AC-003, EC-002

#### 実施内容
- malformed discussion filename candidate 判定で `YYYYMMDDt...` / `YYYYMMDDT...` prefix の timestamp-intent を、`t/T` の後に time digits が続く near-miss まで広げた。
- これにより `20260329t123456zz-adr-kickoff.md` と `20260329t1234z-adr-kickoff.md` を unrelated file ではなく malformed discussion filename として reject するようにした。
- `20260329todo.md` のような plain date-prefixed word は引き続き ignore される前提のまま、focused negative coverage を追加した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_validate

OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - `t/T` separated timestamp-intent near-miss を malformed candidate 判定に追加
- `tests/cli_runtime/test_validate.py` - review 指摘 2 ケースの negative coverage を追加
- `spec-dock/active/issue/report.md` - S03 final follow-up log を追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- 今回の verification は依頼どおり `tests.cli_runtime.test_validate` のみ再実行した。

---

### 2026-03-28 00:00 - 00:00

#### 対象
- Step: S03 latest QA review follow-up
- AC/EC: AC-003, EC-002

#### 実施内容
- `tests.cli_runtime.test_validate` の malformed discussion filename coverage に、timestamp suffix width contract `01..99` の near-miss regression を追加した。
- 具体的には single-digit suffix `-1-` と three-digit suffix `-100-` を malformed として reject し続けることを固定した。
- 実装は変更せず、既存 validation contract が期待どおり fail-closed であることを確認した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_validate

OK
```

#### 変更したファイル
- `tests/cli_runtime/test_validate.py` - `01..99` contract 境界外 near-miss (`-1-`, `-100-`) の regression coverage を追加
- `spec-dock/active/issue/report.md` - 本 QA follow-up evidence を追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- 今回は validation contract coverage gap の補完のみで、provider-side 実装コードの変更は不要だった。

---

### 2026-03-29 02:36 - 02:45

#### 対象
- Step: S03 latest remaining review findings follow-up
- AC/EC: AC-003, EC-002

#### 実施内容
- malformed discussion filename candidate 判定で、`YYYYMMDDt/T` の後に少なくとも 1 桁の時刻数字が続く prefix を fail-closed に扱い、`20260329t123456z_adr-kickoff.md` と `20260329t123456z01-adr-kickoff.md` を malformed discussion filename として reject するようにした。
- legacy / discussion-kind prefix の malformed underscore variants (`001_adr-kickoff.md`, `adr_kickoff.md`) も explicit validation error として reject するように補強した。
- validate negative coverage を review 指摘 4 ケースへ拡張し、full validate module を再実行した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_validate

OK
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - timestamp-intent / malformed underscore variants の fail-closed 判定を補強
- `tests/cli_runtime/test_validate.py` - review 指摘 4 ケースの negative coverage を追加
- `spec-dock/active/issue/report.md` - 本 follow-up log を追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- 指示どおり `python -m unittest tests.cli_runtime.test_validate` のみ再実行し、green を確認した。

---

### 2026-03-29 02:46 - 03:05

#### 対象
- Step: S90
- AC/EC: docs impact resolution / parity verification

#### 実施内容
- provider-side naming / workflow docs を timestamp-based discussion naming contract に更新し、discussion doc family・`discussions/` original location・`<ts>-<kind>-<slug>.md` と same-second collision suffix `-<nn>-` を明文化した。
- `reference_naming.md` に `doc_id` と filename stem の境界、legacy sequential docs の grandfathering、unrelated files ignore と malformed candidate fail-closed の validation 境界を追加した。
- `workflow_adr.md` で ADR original が mirror / sync に関係なく `discussions/` に残ることを明記し、Issue / Epic / Initiative workflow と `rules/*/discussions.md` に timestamp-prefixed original の案内を揃えた。
- dogfooding mirror 側の対象 docs を provider-side と同内容へ更新し、timestamp contract の parity を揃えた。

#### 実行コマンド / 結果
```bash
git --no-pager diff -- src/spec_dock/assets/spec_dock/docs/reference_naming.md src/spec_dock/assets/spec_dock/docs/workflow_adr.md src/spec_dock/assets/spec_dock/docs/workflow_issue.md src/spec_dock/assets/spec_dock/docs/workflow_epic.md src/spec_dock/assets/spec_dock/docs/workflow_initiative.md src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md spec-dock/docs/reference_naming.md spec-dock/docs/workflow_adr.md spec-dock/docs/workflow_issue.md spec-dock/docs/workflow_epic.md spec-dock/docs/workflow_initiative.md spec-dock/docs/rules/issue/discussions.md spec-dock/docs/rules/epic/discussions.md spec-dock/docs/rules/initiative/discussions.md

OK
- targeted docs diff に timestamp naming contract への更新のみが出力された。

git --no-pager grep -n "NNN-type-slug\.md\|3 桁固定\|001..999" -- src/spec_dock/assets/spec_dock/docs/reference_naming.md src/spec_dock/assets/spec_dock/docs/workflow_adr.md src/spec_dock/assets/spec_dock/docs/workflow_issue.md src/spec_dock/assets/spec_dock/docs/workflow_epic.md src/spec_dock/assets/spec_dock/docs/workflow_initiative.md src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md spec-dock/docs/reference_naming.md spec-dock/docs/workflow_adr.md spec-dock/docs/workflow_issue.md spec-dock/docs/workflow_epic.md spec-dock/docs/workflow_initiative.md spec-dock/docs/rules/issue/discussions.md spec-dock/docs/rules/epic/discussions.md spec-dock/docs/rules/initiative/discussions.md

OK
- obsolete sequential naming contract text は targeted docs から消えていることを確認した。

cmp -s src/spec_dock/assets/spec_dock/docs/reference_naming.md spec-dock/docs/reference_naming.md && cmp -s src/spec_dock/assets/spec_dock/docs/workflow_adr.md spec-dock/docs/workflow_adr.md && cmp -s src/spec_dock/assets/spec_dock/docs/workflow_issue.md spec-dock/docs/workflow_issue.md && cmp -s src/spec_dock/assets/spec_dock/docs/workflow_epic.md spec-dock/docs/workflow_epic.md && cmp -s src/spec_dock/assets/spec_dock/docs/workflow_initiative.md spec-dock/docs/workflow_initiative.md && cmp -s src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md spec-dock/docs/rules/issue/discussions.md && cmp -s src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md spec-dock/docs/rules/epic/discussions.md && cmp -s src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md spec-dock/docs/rules/initiative/discussions.md

OK
- provider / dogfooding parity 対象 8 ファイルは byte-for-byte 一致した。
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/reference_naming.md` - timestamp basename / collision suffix / `doc_id` / legacy-validation boundary を明文化
- `src/spec_dock/assets/spec_dock/docs/workflow_adr.md` - ADR output naming と `discussions/` original location を timestamp contract に更新
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` - issue discussions bullet を timestamp-prefixed original contract に更新
- `src/spec_dock/assets/spec_dock/docs/workflow_epic.md` - epic discussions bullet を timestamp-prefixed original contract に更新
- `src/spec_dock/assets/spec_dock/docs/workflow_initiative.md` - initiative discussions bullet を timestamp-prefixed original contract に更新
- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md` - issue discussion storage note を timestamp contract に更新
- `src/spec_dock/assets/spec_dock/docs/rules/epic/discussions.md` - epic discussion storage note を timestamp contract に更新
- `src/spec_dock/assets/spec_dock/docs/rules/initiative/discussions.md` - initiative discussion storage note を timestamp contract に更新
- `spec-dock/docs/reference_naming.md` - provider-side との parity 更新
- `spec-dock/docs/workflow_adr.md` - provider-side との parity 更新
- `spec-dock/docs/workflow_issue.md` - provider-side との parity 更新
- `spec-dock/docs/workflow_epic.md` - provider-side との parity 更新
- `spec-dock/docs/workflow_initiative.md` - provider-side との parity 更新
- `spec-dock/docs/rules/issue/discussions.md` - provider-side との parity 更新
- `spec-dock/docs/rules/epic/discussions.md` - provider-side との parity 更新
- `spec-dock/docs/rules/initiative/discussions.md` - provider-side との parity 更新
- `spec-dock/active/issue/report.md` - S90 docs impact evidence と parity verification を追記

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- docs-only 変更のため unit test は追加していない。targeted diff / grep / cmp で contract 更新と provider-dogfooding parity を確認した。

---

### 2026-03-29 03:06 - 03:20

#### 対象
- Step: S99
- AC/EC: AC-001, AC-002, AC-003, AC-004

#### 実施内容
- S99 の implementation snapshot は、discussion filename hardening の本体として create / validate / `doctor` の整合、malformed / duplicate filename guidance、repo-backed doctor malformed-filename regression、guidance timestamp-contract parity 修正までを含む 15 ファイル差分である。
- latest final-gate review では 3 件の concrete blocker が残っていた: canonical report の exact snapshot evidence stale、shipped guidance contract が旧 sequential naming のまま、repo-backed doctor malformed filename regression 不足。
- この report entry は次回 rerun 前の latest truth に合わせ、exact snapshot evidence を更新しつつ、guidance/doc parity と doctor regression 補強を current snapshot の一部として記録する。

#### 実行コマンド / 結果
```bash
git --no-pager diff --stat

spec-dock/active/issue/design.md 48 +++++--
spec-dock/active/issue/plan.md 61 ++++----
spec-dock/active/issue/report.md 96 ++++++++-----
spec-dock/active/issue/requirement.md 20 ++-
create_node dogfooding 202 +++++++++++++++++++-------
doctor dogfooding 17 ++-
validation dogfooding 147 ++++++++++++++++---
create_node provider 48 +++++--
doctor provider 17 ++-
validation provider 41 +++++-
test_new 63 ++++++++-
test_runtime_doctor_s04 273 +++++++++++++++++++++++++-----------
test_runtime_new_doc_s09 272 ++++++++++++++++++++++++++++++++++-
test_validate 3 +
test_init_update 3 +
15 files changed, 1060 insertions(+), 251 deletions(-)

git --no-pager status --short

M spec-dock/active/issue/design.md
M spec-dock/active/issue/plan.md
M spec-dock/active/issue/report.md
M spec-dock/active/issue/requirement.md
M spec-dock/scripts/spec_dock_runtime/application/create_node.py
M spec-dock/scripts/spec_dock_runtime/application/doctor.py
M spec-dock/scripts/spec_dock_runtime/domain/validation.py
M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py
M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py
M tests/cli_runtime/test_new.py
M tests/cli_runtime/test_runtime_doctor_s04.py
M tests/cli_runtime/test_runtime_new_doc_s09.py
M tests/cli_runtime/test_validate.py
M tests/test_init_update.py
```

- reviewer status against the exact snapshot above:
  - `code_reviewer` `iss00036-code-review-s99-r8` -> latest recorded verdict は `pass` だが、current snapshot では canonical docs repair 後の rerun 未実施
  - `qa_reviewer` `iss00036-qa-review-s99-r8` -> latest recorded verdict は `pass` だが、current snapshot では canonical docs repair 後の rerun 未実施
  - `spec_reviewer` `iss00036-spec-review-s99-r6` -> `fail`（P1: canonical issue contract に doctor guidance / post-lock corruption hardening が未追跡、P1: canonical report に exact current diff/status evidence が欠落）。本修正後の rerun は未実施

#### 変更したファイル
- `spec-dock/active/issue/design.md` - canonical design snapshot in scope
- `spec-dock/active/issue/plan.md` - canonical plan snapshot in scope
- `spec-dock/active/issue/report.md` - canonical report snapshot in scope
- `spec-dock/active/issue/requirement.md` - canonical requirement snapshot in scope
- `spec-dock/scripts/spec_dock_runtime/application/create_node.py` - dogfooding runtime create-path hardening in scope
- `spec-dock/scripts/spec_dock_runtime/application/doctor.py` - dogfooding runtime doctor guidance in scope
- `spec-dock/scripts/spec_dock_runtime/domain/validation.py` - dogfooding runtime validation hardening in scope
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py` - provider runtime create-path hardening in scope
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py` - provider runtime doctor guidance in scope
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - provider runtime validation hardening in scope
- `tests/cli_runtime/test_new.py` - CLI new-doc regression evidence in scope
- `tests/cli_runtime/test_runtime_doctor_s04.py` - doctor regression evidence in scope
- `tests/cli_runtime/test_runtime_new_doc_s09.py` - runtime new-doc / post-lock corruption regression evidence in scope
- `tests/cli_runtime/test_validate.py` - validate regression evidence in scope
- `tests/test_init_update.py` - parity/update regression evidence in scope

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- exact snapshot evidence は上記 15 ファイル差分に固定した。
- current truth は「spec fail / code+QA latest recorded pass but exact-snapshot rerun pending」であり、final approval state ではない。
- 次の reviewer rerun では、この canonical doc repair を含む snapshot に対して verdict を取り直す必要がある。

---

### 2026-03-29 03:21 - 03:32

#### 対象
- Step: S99 final gate review follow-up
- AC/EC: AC-001, AC-002, AC-003, AC-004

#### 実施内容
- provider-side discussion filename validation を補強し、discussion doc-type token を含む malformed basename（例: `foo-adr-kickoff.md`, `bogus-01-adr-kickoff.md`）が validate / doctor / create pre-lock / create post-lock rescan の全経路で explicit failure になるようにした。dogfooding runtime も同内容へ更新した。
- shipped `scripts/README.md` の guidance を provider / dogfooding mirror で更新し、`rules.md` のような unrelated files は ignore、legacy sequential docs は grandfathered、しかし malformed discussion filename candidates は explicit failure という runtime contract に揃えた。
- regression coverage を `test_validate` / `test_new` / `test_runtime_new_doc_s09` / `test_runtime_doctor_s04` / `test_init_update` に追加し、review 指摘だった malformed filename candidates と shipped scripts README parity を固定した。
- reviewer status の current truth を更新した: r10 QA は improvement findings 付きで pass、r10 code review は P1 runtime bug（malformed candidate 判定が狭い）と P2 shipped guidance drift で fail。今回の patch はその指摘を解消するもので、review rerun はまだ pending。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_runtime_doctor_s04 tests.cli_runtime.test_new tests.test_init_update

OK (137 tests)

python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 tests.cli_runtime.test_validate

OK (48 tests)

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=8

git --no-pager diff --stat

.../issues/iss-00036-timestamp-based-discussion-and-adr-naming/design.md    |  48 ++++--
.../issues/iss-00036-timestamp-based-discussion-and-adr-naming/plan.md      |  61 ++++---
.../issues/iss-00036-timestamp-based-discussion-and-adr-naming/report.md    | 179 ++++++++++++++++---
.../iss-00036-timestamp-based-discussion-and-adr-naming/requirement.md      |  20 ++-
spec-dock/scripts/README.md                                                 |  21 ++-
spec-dock/scripts/spec_dock_runtime/application/create_node.py              | 202 ++++++++++++++++------
spec-dock/scripts/spec_dock_runtime/application/doctor.py                   |  17 +-
spec-dock/scripts/spec_dock_runtime/domain/validation.py                    | 147 ++++++++++++++--
spec-dock/templates/README.md                                               |  13 +-
src/spec_dock/assets/spec_dock/scripts/README.md                            |  21 ++-
.../assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py   |  48 +++++-
.../assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py        |  17 +-
.../assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py         |  41 ++++-
src/spec_dock/assets/spec_dock/templates/README.md                          |  13 +-
tests/cli_runtime/harness.py                                                |  30 +++-
tests/cli_runtime/test_new.py                                               |  70 +++++++-
tests/cli_runtime/test_runtime_doctor_s04.py                                | 332 +++++++++++++++++++++++++++---------
tests/cli_runtime/test_runtime_new_doc_s09.py                               | 284 +++++++++++++++++++++++++++++-
tests/cli_runtime/test_validate.py                                          |   5 +
tests/test_init_update.py                                                   |   4 +
20 files changed, 1303 insertions(+), 270 deletions(-)

git --no-pager status --short

M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/design.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/plan.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/report.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/requirement.md
 M spec-dock/scripts/README.md
 M spec-dock/scripts/spec_dock_runtime/application/create_node.py
 M spec-dock/scripts/spec_dock_runtime/application/doctor.py
 M spec-dock/scripts/spec_dock_runtime/domain/validation.py
 M spec-dock/templates/README.md
 M src/spec_dock/assets/spec_dock/scripts/README.md
 M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
 M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py
 M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py
 M src/spec_dock/assets/spec_dock/templates/README.md
 M tests/cli_runtime/harness.py
 M tests/cli_runtime/test_new.py
 M tests/cli_runtime/test_runtime_doctor_s04.py
 M tests/cli_runtime/test_runtime_new_doc_s09.py
 M tests/cli_runtime/test_validate.py
 M tests/test_init_update.py
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py` - provider malformed discussion filename candidate 判定を review 指摘ケースまで拡張
- `spec-dock/scripts/spec_dock_runtime/domain/validation.py` - dogfooding runtime parity 更新
- `src/spec_dock/assets/spec_dock/scripts/README.md` - provider shipped guidance を runtime contract に同期
- `spec-dock/scripts/README.md` - dogfooding shipped guidance parity 更新
- `tests/cli_runtime/test_validate.py` - malformed `foo-adr-*` / `bogus-01-adr-*` validate regressions を追加
- `tests/cli_runtime/test_new.py` - CLI new-doc が同 malformed candidates を reject することを固定
- `tests/cli_runtime/test_runtime_new_doc_s09.py` - create pre-lock / post-lock malformed candidate regressions を拡張
- `tests/cli_runtime/test_runtime_doctor_s04.py` - repo-backed doctor regression に同 malformed candidates を追加
- `tests/test_init_update.py` - shipped `scripts/README.md` の provider↔dogfooding parity を enforcement 対象へ追加
- `spec-dock/active/issue/report.md` - latest S99 snapshot / review status / verification evidence を更新

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- verification は user 指定の 3 コマンドをそのまま実行し、すべて green だった。
- exact snapshot evidence（`git diff --stat` / `git status --short`）はこの entry の更新後に合わせて refresh している。final approval は未取得で、r10 findings 対応後の reviewer rerun が必要。

---

### 2026-03-29 04:25 - 04:35

#### 対象
- Step: S99 final gate review follow-up (template README / canonical report refresh)
- AC/EC: AC-001, AC-002, AC-003, AC-004

#### 実施内容
- `src/spec_dock/assets/spec_dock/templates/README.md` を runtime contract に同期し、discussion docs について「unrelated files は ignore」「legacy sequential docs は grandfathered」「discussion-doc intent を持つ malformed basename は explicit failure」を明記した。
- `spec-dock/templates/README.md` を同内容へ更新し、provider asset と dogfooding mirror の guidance parity を維持した。
- `tests/cli_runtime/harness.py` の discussion guidance contract assertion を強化し、`templates/README.md` / `scripts/README.md` の両方で unrelated-file guidance・legacy grandfathering・malformed explicit failure・代表例が必須になるようにして docs drift を再発防止した。
- canonical report の latest S99 evidence を current exact snapshot に更新し、reviewer truth を r11 QA pass / r11 code pass（non-blocking docs finding は本 patch で解消済み）/ r7 spec fail（この patch 前は exact-snapshot closure evidence と reviewer truth refresh が未充足）へ揃えた。fresh rerun はまだ pending なので final approval は主張しない。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_runtime_doctor_s04 tests.cli_runtime.test_new tests.test_init_update

Ran 137 tests in 15.772s
OK

python -m unittest tests.cli_runtime.test_runtime_new_doc_s09 tests.cli_runtime.test_validate

Ran 48 tests in 25.017s
OK

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=8

./spec-dock/scripts/spec-dock sync --github

spec-dock: sync: active unchanged (matched id in branch: iss-00036)
spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md

git --no-pager diff --stat

.../issues/iss-00036-timestamp-based-discussion-and-adr-naming/design.md    |  48 ++++--
.../issues/iss-00036-timestamp-based-discussion-and-adr-naming/plan.md      |  61 ++++---
.../issues/iss-00036-timestamp-based-discussion-and-adr-naming/report.md    | 279 +++++++++++++++++++++++++++---
.../iss-00036-timestamp-based-discussion-and-adr-naming/requirement.md      |  20 ++-
spec-dock/scripts/README.md                                                 |  21 ++-
spec-dock/scripts/spec_dock_runtime/application/create_node.py              | 202 ++++++++++++++++------
spec-dock/scripts/spec_dock_runtime/application/doctor.py                   |  17 +-
spec-dock/scripts/spec_dock_runtime/domain/validation.py                    | 147 ++++++++++++++--
spec-dock/templates/README.md                                               |  14 +-
src/spec_dock/assets/spec_dock/scripts/README.md                            |  21 ++-
.../assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py   |  48 +++++-
.../assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py        |  17 +-
.../assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py         |  41 ++++-
src/spec_dock/assets/spec_dock/templates/README.md                          |  14 +-
tests/cli_runtime/harness.py                                                |  58 ++++++-
tests/cli_runtime/test_new.py                                               |  70 +++++++-
tests/cli_runtime/test_runtime_doctor_s04.py                                | 332 +++++++++++++++++++++++++++---------
tests/cli_runtime/test_runtime_new_doc_s09.py                               | 284 +++++++++++++++++++++++++++++-
tests/cli_runtime/test_validate.py                                          |   5 +
tests/test_init_update.py                                                   |   4 +
20 files changed, 1433 insertions(+), 270 deletions(-)

git --no-pager status --short

M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/design.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/plan.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/report.md
 M spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00036-timestamp-based-discussion-and-adr-naming/requirement.md
 M spec-dock/scripts/README.md
 M spec-dock/scripts/spec_dock_runtime/application/create_node.py
 M spec-dock/scripts/spec_dock_runtime/application/doctor.py
 M spec-dock/scripts/spec_dock_runtime/domain/validation.py
 M spec-dock/templates/README.md
 M src/spec_dock/assets/spec_dock/scripts/README.md
 M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py
 M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/doctor.py
 M src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/domain/validation.py
 M src/spec_dock/assets/spec_dock/templates/README.md
 M tests/cli_runtime/harness.py
 M tests/cli_runtime/test_new.py
 M tests/cli_runtime/test_runtime_doctor_s04.py
 M tests/cli_runtime/test_runtime_new_doc_s09.py
 M tests/cli_runtime/test_validate.py
 M tests/test_init_update.py
```

- reviewer status against the exact snapshot above:
  - `qa_reviewer` r11 -> `pass`（findings なし）。ただしこの template README / report refresh patch を含む exact snapshot への fresh rerun は未実施
  - `code_reviewer` r11 -> `pass`。残っていた non-blocking docs drift finding（template README wording mismatch）は本 patch で解消済み。fresh rerun は未実施
  - `spec_reviewer` r7 -> `fail`。理由はこの patch 前の canonical report が exact current snapshot の final-gate evidence と reviewer truth closure をまだ十分に示していなかったため。本 patch 後の rerun は未実施

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/templates/README.md` - provider template README を runtime filename contract に同期
- `spec-dock/templates/README.md` - dogfooding mirror parity を維持
- `tests/cli_runtime/harness.py` - README guidance contract assertion を強化して docs drift を検知
- `spec-dock/active/issue/report.md` - latest S99 snapshot / verification evidence / reviewer truth を current exact snapshot に refresh

#### コミット
- なし（do not commit 指示のため未実施）

#### メモ
- test 追加は行っていないため件数は前回 final-gate rerun と同じく 137 tests / 48 tests のまま。
- exact snapshot evidence は上記 `git diff --stat` / `git status --short` を current report 更新後の状態に合わせて refresh 済みである。
- reviewer reruns はこの patch 適用後に取り直す必要があるため、issue closure / final approval はまだ pending。

---

## 省略/例外メモ (必須)
- 該当なし
