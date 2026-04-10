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
