---
種別: 実装報告書（Issue）
ID: "iss-00035"
タイトル: "Sync ADR Symlink Mirror"
関連GitHub: ["#35"]
状態: "draft | approved"
作成者: "Copilot CLI"
最終更新: "2026-03-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00035 Sync ADR Symlink Mirror — 実装報告（LOG）

## 実装サマリー (任意)
- S01 として、ADR mirror の source preflight と basename collision fail-fast を追加した。
- `sync` は initiative / epic / issue の `discussions/*.md` から有効な ADR 原本だけを候補化し、衝突時は active 更新や artifact write より前に `failed_before_write` で終了する。
- S02 として、successful sync 時に `spec-dock/adrs/<basename>` の flat symlink mirror を clear-then-rebuild で再生成し、rename / delete 後の stale entry を残さないようにした。
- S03 として、symlink unsupported 環境だけを warning success に分類し、empty `spec-dock/adrs/` を残す fallback を追加した。非分類の symlink/write failure は hard failure のまま維持した。

## 実装記録（セッションログ） (必須)

### 2026-03-29 02:26 - 02:42

#### 対象
- Step: S01
- AC/EC: AC-001, EC-001, EC-002, EC-004, EC-005

#### 実施内容
- `sync_state.py` に ADR mirror source preflight を追加し、timestamp basename・ADR front matter・`親[0]` と scope path の一致を満たす原本だけを採用するようにした。
- legacy ADR、malformed front matter、unrelated markdown、parent mismatch、malformed `種別` を除外する targeted tests を追加した。
- basename collision は `_sync_impl()` 内で active auto update より前に検出し、`failed_before_write` として返すようにした。
- `spec-dock/adrs/` の既存状態と active state が collision failure で不変であることを test で固定した。
- `code_reviewer` によるレビューで 2 件（preflight timing / `種別` 判定厳格化）の指摘を受け、DevCoder に修正を指示して再レビュー pass を得た。

#### 実行コマンド / 結果
```bash
python -m unittest tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_collect_adr_mirror_sources_filters_to_valid_multi_scope_adr_inputs \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_fails_before_write_on_adr_mirror_basename_collision_and_preserves_adrs \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_active_update_then_artifact_failure_is_non_atomic \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_artifact_failure_contract_when_active_not_updated \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_prewrite_failure_contract_is_failed_before_write

Ran 5 tests in 0.039s
OK

python -m unittest tests.presentation_runtime.test_runtime_sync_s07

Ran 28 tests in 0.090s
OK

code_reviewer (S01 scope)
- initial review_status=fail
- re-review review_status=pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` - ADR mirror source selection と collision preflight を追加
- `tests/presentation_runtime/test_runtime_sync_s07.py` - S01 の source selection / collision preservation regression tests を追加

#### コミット
- `3112bbd23cb562eb6333d0b45e43ef2e92fabeb5` `feat(runtime): ADRミラー原本の事前検査を追加`

#### メモ
- full baseline (`python -m unittest discover -v`) は着手前から unrelated failures=106 のため、S01 では対象 suite に絞って検証した。
- reviewer verdict は S99 final diff review quality gate でも再記録する。

---

### 2026-03-29 02:42 - 02:53

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002, EC-003

#### 実施内容
- successful sync のみを対象に `spec-dock/adrs/` mirror rebuild helper を追加し、valid ADR source から flat な relative symlink 群を生成するようにした。
- `spec-dock/adrs/` は success path で clear-then-rebuild されるため、rename / delete 後に stale symlink や手動残骸が残らないことを固定した。
- S01 の collision fail-fast は維持しつつ、preflight 済み source 群を success path の mirror rebuild に引き渡す形へ整理した。
- `code_reviewer` で S02 scope review を行い、review_status=pass を得た。

#### 実行コマンド / 結果
```bash
python -m unittest tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_fails_before_write_on_adr_mirror_basename_collision_and_preserves_adrs \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_builds_flat_adr_mirror_symlinks_on_success \
  tests.cli_runtime.test_sync.TestCliSync.test_sync_builds_flat_adr_mirror_and_clears_stale_entries_after_rename_and_delete

Ran 3 tests in 0.475s
OK

python -m unittest tests.presentation_runtime.test_runtime_sync_s07

Ran 29 tests in 0.094s
OK

code_reviewer (S02 scope)
- review_status=pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` - flat mirror rebuild と stale cleanup success path を追加
- `tests/presentation_runtime/test_runtime_sync_s07.py` - runtime-level success path mirror assertions を追加
- `tests/cli_runtime/test_sync.py` - repeated sync で rename / delete stale cleanup を確認する CLI regression test を追加

#### コミット
- `8cafe55e7fcd8cda23f3711a10a1b7836204e5e1` `feat(runtime): sync成功時にADRミラーを再構築`

#### メモ
- S03 fallback は未着手のため、symlink unsupported / write failure は現時点では hard failure のまま。

---

### 2026-03-29 02:53 - 03:21

#### 対象
- Step: S03
- AC/EC: AC-003, EC-006

#### 実施内容
- ADR mirror rebuild 前に symlink capability probe を追加し、`ENOSYS` / `EOPNOTSUPP` / `ENOTSUP` / `winerror == 1314` だけを unsupported classifier として扱うようにした。
- unsupported classifier の場合は empty `spec-dock/adrs/` を残して warning code `adr_mirror_symlink_unsupported` を積み、`sync` 自体は success のままにした。
- non-classified probe failure と actual mirror symlink write failure は hard failure のままであることを regression test で固定した。
- no-ADR source の場合は不要な warning を出さないよう補正した。
- `code_reviewer` は pass、`qa_reviewer` は 2 回の指摘（actual mirror write failure coverage / classified branch coverage）を経て final pass を得た。

#### 実行コマンド / 結果
```bash
python -m unittest tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_warns_and_succeeds_with_empty_adrs_when_symlinks_are_unsupported \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_leaves_empty_adrs_without_warning_when_no_adr_sources_exist \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_keeps_symlink_probe_failures_hard_when_not_classified_as_unsupported \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_sync_keeps_actual_adr_mirror_symlink_failures_hard_after_probe_success \
  tests.presentation_runtime.test_runtime_sync_s07.TestRuntimeSyncS07.test_is_environment_symlink_unsupported_covers_remaining_classified_branches

Ran 5 tests in 0.051s
OK

python -m unittest -v tests.presentation_runtime.test_runtime_sync_s07

Ran 34 tests in 0.098s
OK

code_reviewer (S03 scope)
- initial review_status=pass with non-blocking note
- re-review review_status=pass

qa_reviewer (S01-S03 cumulative scope)
- initial review_status=fail
- re-review review_status=pass with non-blocking note
- final review_status=pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/sync_state.py` - unsupported classifier / warning-success fallback / empty-source no-warning branchを追加
- `tests/presentation_runtime/test_runtime_sync_s07.py` - S03 の fallback, hard-fail, classified-branch coverage tests を追加

#### コミット
- pending: S03 commit after report update

#### メモ
- QA 指摘はすべて DevCoder に戻して修正し、レビュー loop を完了した。

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
- baseline の unrelated failures は既知として扱い、本 issue の targeted tests で step verification を行った。
