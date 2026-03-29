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
- 実装・テスト修正・commit 自体はまだ未着手。
