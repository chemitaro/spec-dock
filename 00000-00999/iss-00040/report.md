---
種別: 実装報告書（Issue）
ID: "iss-00040"
タイトル: "Sync Fail Closed Hardening And Test Realignment"
関連GitHub: ["#40"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-03-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00033", "init-local-00003"]
---

# iss-00040 Sync Fail Closed Hardening And Test Realignment — 実装報告（LOG）

## 実装サマリー (任意)
- `iss-00040` の requirement / design / plan と関連 discussions を、current stale-contract cluster と dogfooding parity drift を含む前提で更新した。
- 全体回帰の再現結果と issue scope の判断材料を記録し、spec review に渡せる状態まで正本を整備した。

## 実装記録（セッションログ） (必須)

### 2026-03-29 05:54 - 06:20

#### 対象
- Step: spec authoring pre-implementation
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003

#### 実施内容
- active initiative / epic / issue docs と workflow / phase docs を確認した。
- `python -m unittest discover -v` と representative targeted tests を実行し、current stale-contract cluster を再現した。
- issue discussions 2 本を作成し、research / scope decision を記録した。
- `spec-dock/active/issue/{requirement,design,plan}.md` を broader scope 前提で更新した。
- spec reviewer にレビュー依頼を送った。

#### 実行コマンド / 結果
```bash
python -m unittest discover -v
python -m unittest tests.cli_runtime.test_active.TestCliActive.test_active_set_accepts_explicit_id_flag -v
python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_github_ready_when_deps_closed -v
python -m unittest tests.cli_runtime.test_wrappers.TestCliRulesContract.test_scaffold_docs_point_to_runtime_commands_and_rules_docs -v
python -m unittest tests.domain_runtime.test_runtime_domain_s01.TestRuntimeDomainS01.test_validate_graph_and_deps_detects_structural_error -v
python -m unittest tests.test_init_update.TestInitUpdate.test_checked_in_dogfooding_runtime_mirror_match_provider_assets -v

- full suite は 524 tests 中 107 failures で終了した。
- representative failures は `--no-github` reject、`origin` missing、wrapper docs expectation mismatch、validation ordering mismatch、parity drift を示した。
- issue docs / discussions は更新済み。
```

#### 変更したファイル
- `spec-dock/active/issue/requirement.md` - issue requirement を broader stale-contract cluster 前提で更新
- `spec-dock/active/issue/design.md` - fixture strategy / parity recovery / verification mapping を設計
- `spec-dock/active/issue/plan.md` - execution steps と review gates を分解
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/discussions/20260329t053816z-01-research-active-and-deps-test-failure-clustering.md` - 調査ログ
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/discussions/20260329t053816z-disc-test-realignment-scope-and-acceptance.md` - scope decision
- `spec-dock/active/issue/report.md` - この記録

#### コミット
- なし

#### メモ
- 初回 spec review 前の記録。

---

### 2026-03-29 06:09 - 06:20

#### 対象
- Step: SG1 spec review fix / re-review
- AC/EC: AC-001, AC-002, AC-003, AC-004, EC-001, EC-002, EC-003

#### 実施内容
- spec reviewer の fail 指摘に従い、issue requirement / plan に close criteria と legacy-compat evidence を追加した。
- epic plan の ownership 競合を sub-agent で解消し、`iss-00038` と `iss-00040` の責務境界を明記した。
- discussion status を `completed` へ更新し、再レビューを実施した。
- 最終 review_status=`pass` を確認した。
- final pass 後の non-blocking note だった epic gate-5 への legacy-compat evidence 追記も反映した。

#### 実行コマンド / 結果
```bash
spec review: fail -> fix -> re-review -> pass

- 初回指摘:
  - epic plan に iss-00040 ownership を反映
  - AC-004 close criteria の固定
  - legacy-compat evidence の execution contract 追記
- 再レビュー結果:
  - review_status=pass
  - その後の non-blocking note（epic gate-5 への legacy-compat evidence 追記）も反映済み
```

#### 変更したファイル
- `spec-dock/active/issue/requirement.md` - AC-004 の close criteria を固定、未確定事項を解消
- `spec-dock/active/issue/design.md` - helper 方針を確定し未確定事項を解消
- `spec-dock/active/issue/plan.md` - legacy-compat evidence と final exit contract を強化
- `spec-dock/active/epic/plan.md` - `iss-00038` / `iss-00040` の ownership と gates を整理
- `spec-dock/initiatives/init-local-00003-architecture-maintenance-and-hardening/epics/epic-00033-github-backed-identity-and-adr-mirror-workflow/issues/iss-00040-sync-fail-closed-hardening-and-test-realignment/discussions/20260329t053816z-disc-test-realignment-scope-and-acceptance.md` - status を `completed` へ更新
- `spec-dock/active/issue/report.md` - この記録

#### コミット
- なし

#### メモ
- final spec reviewer verdict: `pass`
- final follow-up:
  - epic gate-5 の legacy-compat evidence 追記まで反映済み

---

### 2026-03-29 06:20 - 06:35

#### 対象
- Step: SG1 spec rework / pending re-review
- AC/EC: AC-004, EC-001

#### 実施内容
- spec reviewer から reviewer timing、AC-004 の premature closure、true runtime defect 発見時の escalation ambiguity について fail 指摘を受けた。
- `spec-dock/active/issue/plan.md` で AC-004 を S05 close に固定し、per-step approval loop と stop/escalation rule を明記した。
- `spec-dock/active/issue/requirement.md` で Ask 境界を stop/escalation rule に置き換え、runtime rollback 禁止と human judgment 必須を固定した。
- docs 修正後のため、spec re-review が必要な状態で記録した。

#### 実行コマンド / 結果
```bash
spec review: fail

- 指摘:
  - step ごとの reviewer timing / approval loop が plan に明示されていない
  - AC-004 が S01 baseline で close 扱いになっている
  - true runtime defect 発見時の requirement/design/plan boundary が曖昧
- 対応:
  - requirement / plan を修正
  - 再レビュー待ち
```

#### 変更したファイル
- `spec-dock/active/issue/plan.md` - per-step approval loop、AC-004 close timing、stop/escalation rule を修正
- `spec-dock/active/issue/requirement.md` - Ask 境界を stop/escalation rule へ修正
- `spec-dock/active/issue/report.md` - この記録

#### コミット
- なし

#### メモ
- この時点では spec reviewer 再承認は未取得。

---

### 2026-03-29 06:35 - 06:41

#### 対象
- Step: SG1 spec re-review after docs fixes
- AC/EC: AC-004, EC-001

#### 実施内容
- reviewer timing / AC-004 / escalation 修正後の docs で spec re-review を依頼した。
- spec reviewer から pass を受領し、material な追加指摘がないことを確認した。
- issue spec は implementation 開始可能となり、以降は S02 へ進行できる状態とした。

#### 実行コマンド / 結果
```bash
spec review: re-review -> pass

- docs fixes 後に再レビュー依頼
- review_status=pass
- material findings なし
- implementation は S02 へ進行可能
```

#### 変更したファイル
- `spec-dock/active/issue/report.md` - この記録

#### コミット
- なし

#### メモ
- docs 修正に対する spec re-review は完了済み。

---

### 2026-03-29 06:41 - 07:05

#### 対象
- Step: S02 CLI fixture realignment
- AC/EC: AC-004, EC-001

#### 実施内容
- `tests/cli_runtime/harness.py`、`tests/cli_runtime/test_active.py`、`tests/cli_runtime/test_deps.py`、`tests/cli_runtime/test_sync.py` の CLI fixture realignment を実施した。
- 現行 runtime contract は維持したまま、legacy local compat coverage を explicit fixture で復元した。
- deps の local-only / fallback 系が imported id と削除済み GitHub metadata に依存しないように補正し、kind ごとに authentic な legacy local id を materialize する compat helper へ調整した。
- ready-path の deps test で弱まっていた exit-code coverage を元の期待値まで戻した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_no_deps_is_ready -v
python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_accepts_explicit_id_flag -v
python -m unittest tests.cli_runtime.test_deps.TestCliDeps.test_deps_check_without_github_falls_back_to_unknown_when_snapshot_missing -v
python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_deps tests.cli_runtime.test_sync -v

- deps の final review-fix loop targeted rerun は 3 件とも pass。
- `python -m unittest tests.cli_runtime.test_active tests.cli_runtime.test_deps tests.cli_runtime.test_sync -v` は `Ran 109 tests ... OK` で pass。
```

#### 変更したファイル
- `tests/cli_runtime/harness.py` - legacy local compat fixture materialization を per-kind の authentic local id 生成へ修正
- `tests/cli_runtime/test_active.py` - current runtime contract を維持したまま explicit legacy local compat coverage へ整列
- `tests/cli_runtime/test_deps.py` - deps local-only / fallback coverage を true `*-local-*` fixture 基準へ修正し、ready-path exit-code assertion を復元
- `tests/cli_runtime/test_sync.py` - CLI fixture realignment に追随して legacy local compat coverage を明示化
- `spec-dock/active/issue/report.md` - この記録

#### レビューループ
- 初回 code review は fail。deps の local-only tests が、削除済み GitHub metadata を持たない imported id のままで、true `*-local-*` compat fixture を使えていない点を指摘された。
- 追補後の code review も fail。local compat helper が GitHub number suffix を温存しており authentic な legacy local id を生成できていない点と、ready-path の deps test で exit-code coverage が弱まっていた点を指摘された。
- 最新修正で、compat materialization を kind ごとの authentic local id 割り当てへ変更し、ready-path の exit-code assertion も復元した。
- 最終 `code_reviewer` verdict は `pass`。

#### コミット
- なし

#### メモ
- commit は未実施のため、このログ時点の commit 情報は pending / none 扱い。

---

### 2026-03-29 07:05 - 07:18

#### 対象
- Step: S03 wrapper/domain expectation realignment
- AC/EC: AC-004, EC-001

#### 実施内容
- `tests/cli_runtime/test_wrappers.py` と `tests/domain_runtime/test_runtime_domain_s01.py` の stale test expectation を、現行 runtime / docs contract に合わせて再整列した。
- production / runtime code は変更せず、wrapper / domain 側の期待値だけを current contract に追従させた。
- wrapper tests に残っていた reject 済みの local-only `new ... --no-github` 前提を除去した。
- `workflow_issue.md` の expectation で旧 `new issue --no-github ...` 例を必須視していた前提を解消した。
- wrapper discussion filename expectation を旧 sequential numbering から、現行の timestamp-prefix 形式へ更新した。
- domain validation expectation を、旧 structural mismatch error ではなく、現行 fail-closed の missing-github-linkage-first ordering に合わせて修正した。

#### 実行コマンド / 結果
```bash
python -m unittest tests.cli_runtime.test_wrappers tests.domain_runtime.test_runtime_domain_s01 -v

- `python -m unittest tests.cli_runtime.test_wrappers tests.domain_runtime.test_runtime_domain_s01 -v` は `Ran 15 tests ... OK` で pass。
```

#### 変更したファイル
- `tests/cli_runtime/test_wrappers.py` - wrapper docs / local-only invocation / discussion filename expectation を current runtime contract へ更新
- `tests/domain_runtime/test_runtime_domain_s01.py` - validation ordering expectation を fail-closed missing-github-linkage-first に更新
- `spec-dock/active/issue/report.md` - この記録

#### レビューループ
- 初回 code review は `pass`。ただし non-blocking note として、`workflow_issue.md` に対する stale `new issue --no-github ...` 例の negative coverage を明示する `assertNotIn` 追加が提案された。
- follow-up fix で当該 `assertNotIn` を追加し、wrapper docs expectation の stale example 不在を明示した。
- 再レビュー後の最終 `code_reviewer` verdict は `pass`。

#### コミット
- なし

#### メモ
- S03 は wrapper / domain expectation の realignment のみで、runtime behavior 自体の変更は行っていない。

---

## 遭遇した問題と解決 (任意)
- 問題:
  - 初回 spec review で issue close criteria と epic ownership の曖昧さを指摘された。
  - 追加で、reviewer timing / AC-004 close timing / escalation boundary の曖昧さを指摘された。
  - 解決:
    - issue requirement / plan / epic plan を段階的に補強した。
    - 最新の docs 修正に対する spec re-review で pass を取得し、implementation を S02 へ進められる状態にした。

## 学んだこと (任意)
- stale-contract cluster は production bug と同じくらい full suite の signal を壊すため、issue docs で scope を明示しておく価値が高い。
- current-contract tests と legacy-compat tests の fixture 戦略を分離しないと、epic-level contract change に追随し続けられない。

## 今後の推奨事項 (任意)
- 実装時は `active` / `deps` / `sync` / `wrappers` / `domain` / parity の順で targeted rerun を進める。
- close 判定時は AC-004 に従い、remaining failures があれば scope 外判定と参照 issue を report に残す。

## 省略/例外メモ (必須)
- SG1 docs scope はコミット済み。
- S02 の実装 / テスト修正は完了済みで、code review も pass 済み。
- S02 / S03 の commit はこの report 更新後に実施する前提のため、この時点では未実施。
- 以降の later steps は未着手。
