---
種別: 実装報告書（Issue）
ID: "iss-00062"
タイトル: "Downstream parity and cutover readiness"
関連GitHub: ["#62"]
状態: "draft"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00059", "init-local-00003"]
---

# iss-00062 Downstream parity and cutover readiness — 実装報告（LOG）

## 実装サマリー (任意)
- active initiative / epic / issue と `iss-00060` / `iss-00061` の docs / report / provider-side source を突き合わせ、`iss-00062` の実質的な未解消ギャップを `delete_node.py` の legacy scrub、repo-wide manual fix、cutover evidence owner、template/init-update legacy seed に整理した。
- active issue の requirement / design / plan を現行実装に合わせて補正し、scaffold/template cutover parity と prerequisite authority を追加して、実装開始前の契約を固定した。
- review 観点では blocking finding は残しておらず、実装着手の前提は `delete scrub -> targeted parity regression lock -> docs/scaffold/report schema -> manual fix + evidence` で合意可能な状態に整えた。

## 実装記録（セッションログ） (必須)

### 2026-04-10 00:00 - 00:00

#### 対象
- Step: implementation readiness / spec review loop
- AC/EC: AC-001, AC-002, AC-003, AC-004, AC-005, EC-001, EC-002, EC-003, EC-004, EC-005

#### 実施内容
- active initiative / epic / issue と `iss-00060` / `iss-00061` の requirement / design / plan / report を読み、T1/T2 で reader/mutation contract が完了していることを確認した。
- provider-side source と tests を確認し、`.meta.json` SoT は `deps_reader.py` と downstream reader consumer で成立済みであり、`delete_node.py` の dependency scrub だけが `deps.json` を直接扱う current gap だと特定した。
- checked-in dogfooding data に加えて provider templates / `tests/test_init_update.py` にも legacy `deps.json` seed が残ることを確認し、hard cutover readiness の scope に含めた。
- active issue の requirement / design / plan を補正し、upstream prerequisite authority を `iss-00060` / `iss-00061` の report と provider-side source/tests に固定した。
- spec reviewer に review を依頼し、blocking finding なしの pass を確認した。

#### 実行コマンド / 結果
```bash
sed -n '1,220p' spec-dock/active/context-pack.md
sed -n '1,260p' spec-dock/active/{initiative,epic,issue}/{requirement,design,plan}.md
sed -n '1,220p' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00060-meta-json-dependency-schema-and-reader-alignment/{requirement,design,plan,report}.md
sed -n '1,220p' spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00061-dependency-mutation-command-contract/{requirement,design,plan,report}.md
rg -n "load_issue_depends_on_map|depends_on|deps.json|delete_node|set_active|sync_state|validate_tree" src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime src/spec_dock/assets/spec_dock/docs spec-dock/docs tests/cli_runtime tests/test_init_update.py
find spec-dock -name deps.json | sort
git diff -- spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/{requirement,design,plan}.md

- `iss-00060` / `iss-00061` の reader/mutation contract 完了と issue-level report evidence を確認
- current implementation gap を `delete_node.py` の legacy scrub と template/init-update legacy seed に絞り込み
- active issue requirement/design/plan を現状実装へ整列
- spec review: pass
```

#### 変更したファイル
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/requirement.md` - As-Is、scope、AC/EC、prerequisite authority を現行実装と cutover scope に合わせて補正
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/design.md` - current implementation 理解、scaffold/template contract、conditional modify 範囲を明文化
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/plan.md` - S03 を docs/scaffold/report schema lock に拡張し、AC/EC mapping と review gate を整列
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00059-dependency-metadata-unification-and-command-mutation/issues/iss-00062-downstream-parity-and-cutover-readiness/report.md` - implementation readiness / spec review loop の記録を追加

#### コミット
- なし（実装準備のみ。コミット未作成）

#### メモ
- current provider-side runtime では `set_active` / `sync` / `validate` は shared topology reader で揃っているため、S02 は再実装より targeted regression lock が主目的である。
- current issue の実質的な code gap は `delete_node.py` の `deps.json` scrub 残存であり、`tests/cli_runtime/test_runtime_delete_s13.py` の legacy fixture 置換が主な着手点になる。
- hard cutover readiness には checked-in dogfooding data だけでなく provider templates / init-update coverage の legacy seed cleanup も含める前提にした。

---

### 2026-04-10 00:00 - 00:00

#### 対象
- Step: S01
- AC/EC: AC-001, EC-001

#### 実施内容
- `delete_node.py` の surviving dependency scrub を `deps.json` から `.meta.json` SoT へ切り替え、recovery guidance も `.meta.json.depends_on` 基準に更新した。
- runtime delete stub と focused tests を更新し、surviving node の dependency scrub が `.meta.json` に対して行われることを固定した。
- CLI-level targeted regression を追加し、delete 後の `validate` / `sync` / `active set` で deleted node が dependency として再観測されないことを確認した。
- RG1 implementation review を実施し、blocking finding なしの pass を確認した。非 blocking の residual risk として、`remove_issue_dependency` 未実装 port の専用テスト不足、および `node_repo is None` fallback が application 側書き込みを使う点を記録した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.cli_runtime.test_validate -v

- Ran 151 tests in 37.585s
- OK
- RG1 implementation review: pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` - surviving dependency scrub を `.meta.json` SoT に切り替え、`remove_issue_dependency` 優先経路と guidance 文言を追加
- `tests/cli_runtime/test_runtime_delete_s13.py` - delete runtime stub を `.meta.json` scrub 契約へ寄せ、legacy `deps.json` fixture を置換
- `tests/cli_runtime/test_delete.py` - post-delete downstream regression を追加し、`validate` / `sync` / `active set` で deleted node 非再観測を固定

#### コミット
- 未実施

#### メモ
- residual risk (non-blocking): `node_repo` が存在するのに `remove_issue_dependency` 未実装の場合の専用テストは未追加
- residual risk (non-blocking): `ports.node_repo is None` fallback は application 側 `_write_meta_payload` を使うため、`fs_repo.remove_issue_dependency` の read-only/atomic 契約を直接通らない

---

### 2026-04-10 00:00 - 00:00

#### 対象
- Step: S02
- AC/EC: AC-002, EC-004

#### 実施内容
- `active` / `sync` / `validate` の shared topology reader 前提を再確認し、mismatch は見つからなかったため、最小差分として regression test のみ追加した。
- `test_runtime_active_s06.py` で `active set` が blocked failure でも topology reader 経由で依存解決していることを呼び出し回数で固定した。
- `test_runtime_deps_s04.py` で `collect_sync_state` が shared topology reader の `issue_depends_on_map` を取り込み、`deps_state` に反映することを固定した。
- RG1 implementation review と QG1 QA review を実施し、いずれも pass を確認した。non-blocking の residual risk として、`calls == 1` の厳密アサーションの brittleness、`sys.path` 差し替え import の保守性、warning 伝播 / `sync --force` 分岐の reader 契約を今回新規拡張していない点を記録した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_sync tests.cli_runtime.test_validate tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_runtime_validate_s02 -v
python -m unittest tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 -v

- focused suite: Ran 138 tests in 35.344s
- focused suite: OK
- flaky check subset: Ran 37 tests in 0.703s
- flaky check subset: OK
- RG1 implementation review: pass
- QG1 QA review: pass
```

#### 変更したファイル
- `tests/cli_runtime/test_runtime_active_s06.py` - `active set` blocked failure 時でも topology reader が使われることを呼び出しカウントで固定
- `tests/cli_runtime/test_runtime_deps_s04.py` - `collect_sync_state` が shared topology reader の dependency map を `deps_state` に反映する回帰を追加

#### コミット
- 未実施

#### メモ
- non-blocking: `calls == 1` の厳密アサーションは将来の内部実装変更で brittle になる可能性がある
- non-blocking: `test_runtime_deps_s04.py` の `sys.path` 一時差し替え import は機能上問題ないが、将来のテスト構成変更時に影響を受けやすい
- `validate` 側の shared topology reader 接続確認は既存回帰依存で、今回差分では新規強化していない

---

### 2026-04-10 00:00 - 00:00

#### 対象
- Step: S03
- AC/EC: AC-004, AC-005, EC-003, EC-005

#### 実施内容
- provider-side `reference_deps.md` / `reference_sync.md` / `workflow_issue.md` と dogfooding mirror を更新し、hard cutover entry 条件、manual fix、`validate` / `sync` evidence、T3/T4 owner split、fixed-key contract を明文化した。
- provider / dogfooding の templates から legacy `deps.json` seed を削除し、`tests/test_init_update.py` に docs mirror parity と non-seed regression を追加した。
- focused tests、provider/mirror diff、S03 必須文言の存在確認を実施し、SG1/spec review は pass と判断した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.test_init_update.TestInitUpdate.test_init_creates_expected_structure tests.test_init_update.TestInitUpdate.test_init_does_not_seed_legacy_node_deps_json_templates tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_mirror_templates_match_provider_assets tests.test_init_update.TestInitUpdate.test_reference_sync_doc_matches_bundled_asset tests.test_init_update.TestInitUpdate.test_reference_deps_doc_matches_bundled_asset tests.test_init_update.TestInitUpdate.test_workflow_issue_doc_matches_bundled_asset tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_numeric_deps_overlap_parity tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_scoped_deps_ref_parity tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_subprocess_numeric_deps_ref_foreign_only_fail_closed_parity -v
diff -u src/spec_dock/assets/spec_dock/docs/reference_deps.md spec-dock/docs/reference_deps.md
diff -u src/spec_dock/assets/spec_dock/docs/reference_sync.md spec-dock/docs/reference_sync.md
diff -u src/spec_dock/assets/spec_dock/docs/workflow_issue.md spec-dock/docs/workflow_issue.md
python - <<'PY'
# SG1-check: required phrases present
PY

- focused suite: Ran 9 tests
- focused suite: OK
- provider/mirror docs diff: 3件とも差分なし
- SG1-check: pass
- SG1 spec review: pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/reference_deps.md` - hard cutover entry contract と T3/T4 split を追記
- `src/spec_dock/assets/spec_dock/docs/reference_sync.md` - hard cutover verification contract と evidence 記録要件を追記
- `src/spec_dock/assets/spec_dock/docs/workflow_issue.md` - issue-level hard cutover evidence contract と fixed-key 群を追加
- `spec-dock/docs/reference_deps.md` - provider-side 正本と同期
- `spec-dock/docs/reference_sync.md` - provider-side 正本と同期
- `spec-dock/docs/workflow_issue.md` - provider-side 正本と同期
- `src/spec_dock/assets/spec_dock/templates/{initiative,epic,issue}/deps.json` - legacy seed を削除
- `spec-dock/templates/{initiative,epic,issue}/deps.json` - checked-in mirror から legacy seed を削除
- `tests/test_init_update.py` - docs mirror parity と non-seed regression を追加

#### コミット
- 未実施

#### メモ
- residual risk: focused coverage のみ実行しており、S03 変更範囲に対する全体回帰は S04 final gate へ残している
- residual risk: `workflow_issue.md` は汎用 contract を追加したが、fixed-key の実運用確認は S04 の report 記録で最終確認する

---

## 遭遇した問題と解決 (任意)
- 問題: active issue docs の As-Is に `deps_reader.py` / docs の旧前提が残っており、`iss-00060` / `iss-00061` の実装済み事実と一致していなかった
  - 解決: upstream report と provider-side source/tests を権威ソースに据え、current gap を `delete scrub` と `template/init-update legacy seed` に絞り直した

## 学んだこと (任意)
- T3 issue は downstream command 全体を作り直す段階ではなく、T1/T2 で既に揃っている read/mutation contract の上で残差を閉じる段階である
- hard cutover readiness は runtime parity だけでは足りず、seed data と operator workflow まで同じ契約へ揃える必要がある

## 今後の推奨事項 (任意)
- 実装着手は `delete scrub` を最優先にし、その後は active/sync/validate を regression lock として確認する
- S03 では `workflow_issue.md` の owner split と `tests.test_init_update` の scaffold coverage を先に固定し、S04 の manual fix / judgment で迷いを残さない

## 省略/例外メモ (必須)
- 該当なし
