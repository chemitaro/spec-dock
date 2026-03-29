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
- pending: S01 commit after report update

#### メモ
- full baseline (`python -m unittest discover -v`) は着手前から unrelated failures=106 のため、S01 では対象 suite に絞って検証した。
- reviewer verdict は S99 final diff review quality gate でも再記録する。

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
