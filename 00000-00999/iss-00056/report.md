---
種別: 実装報告書（Issue）
ID: "iss-00056"
タイトル: "Delete Local Spec Nodes With Safeguards And Epic Final Closeout"
関連GitHub: ["#56"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-10"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00054", "init-local-00002"]
---

# iss-00056 Delete Local Spec Nodes With Safeguards And Epic Final Closeout — 実装報告（LOG）

## 実装サマリー (任意)
- iss-00056 の実装を開始し、S01 の destructive preflight / selector / guardrail 契約から着手した。
- issue55 の close capability を前提に、delete command の安全境界を先に固定してから local delete へ進む方針である。

## 実装記録（セッションログ） (必須)

### 2026-04-09 08:45 - 10:25

#### 対象
- Step: S01 I1
- AC/EC: EC-001, EC-002, EC-003, EC-005, EC-006, EC-007, EC-008, EC-009

#### 実施内容
- `iss-00056` を active set + checkout し、requirement/design/plan を再読して S01 I1 の bounded slice を確定した。
- S01 I1 は delete command の selector / preflight / guardrail 契約だけを先に固定し、まだ actual delete や final close-out には入らない方針とした。
- dev_coder に S01 I1 の test-first 実装を委任した。
- top-level `delete` command の parser / registry / command wrapper / renderer を追加し、selector / preflight / guardrail 契約を provider-side runtime に導入した。
- `--json` field matrix、selector precedence、`--force` positive path、issue + `--recursive` accepted no-op を tests で固定した。
- spec review 指摘に合わせて、S01 I1 の staged implementation note として `confirmation_required` interim placeholder を requirement/design/plan に明記した。

#### 実行コマンド / 結果
```bash
./spec-dock/scripts/spec-dock active set --id iss-00056 --checkout

spec-dock: ok (active set) target=iss-00056 initiative=init-local-00002 epic=epic-00054 issue=iss-00056
spec-dock: ok (active checkout) branch=iss-00056-delete-local-spec-nodes-with-safeguards-and-epic-final-closeout

python -m unittest -v tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_runtime_shell_s11 tests.cli_runtime.test_runtime_close_s12 tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_close

OK (76 tests)

implementation review (S01 I1)

pass

qa review (S01 I1)

pass

spec review (S01 I1)

pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - delete request/result/use case slot を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` - selector/preflight/guardrail 用の delete use case を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - delete use case wiring を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` - top-level `delete` parser を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py` - `delete` command registration を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/delete.py` - delete command args / run path を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - delete text/json rendering を追加
- `tests/cli_runtime/test_runtime_delete_s13.py` - S01 I1 selector/preflight/guardrail regression tests を追加
- `tests/cli_runtime/test_runtime_shell_s11.py` - delete command wrapper smoke test を追加
- `spec-dock/active/issue/requirement.md` - staged implementation note を追記
- `spec-dock/active/issue/design.md` - interim placeholder semantics を追記
- `spec-dock/active/issue/plan.md` - S01 I1 interim observation を追記
- `spec-dock/active/issue/report.md` - issue56 の着手ログと S01 I1 実装記録を更新

#### コミット
- `7f7865dc06b7330dfc22b29f01e4e4caff92c448`

#### メモ
- implementation review は pass。non-blocking として `confirmation_required` の interim semantics は S01 I2/S02 で正規化が必要とコメントされた。
- qa review は pass。前回 blocker だった `--json` field matrix と preflight pass の見え方は解消済み。
- spec review は pass。issue docs に staged implementation note を追加したことで、S01 I1 の interim semantics が docs と整合した。
- S01 I1 の範囲上、actual delete / subtree metadata barrier / required remote close set / partial failure handling は未着手であり、次の S01 I2 で扱う。

### 2026-04-09 10:30 - 11:10

#### 対象
- Step: S01 I2
- AC/EC: EC-004, EC-007, EC-008, EC-009

#### 実施内容
- subtree-wide metadata validation と required remote close barrier を bounded scope で追加した。
- would-match target invalid metadata、subtree-wide invalid metadata aggregation、canonical remote issue identifier dedupe/order、already-closed noop bucket、remote close failure abort を tests で固定した。
- actual local delete / partial failure / dependency scrub はこの slice では未実装のまま据え置いた。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_runtime_shell_s11 tests.cli_runtime.test_runtime_close_s12 tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_close

OK (81 tests)

implementation review (S01 I2)

pass

qa review (S01 I2)

pass

spec review (S01 I2)

pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` - metadata validation / required remote close barrier / active snapshot restore path を追加
- `tests/cli_runtime/test_runtime_delete_s13.py` - metadata_validation_failed / remote_close_failed / dedupe-ordering / already-closed noop / restore regression tests を追加
- `spec-dock/active/issue/report.md` - S01 I2 実装記録を追記

#### コミット
- `09a12f0c4ddad538f42348abb99be2d5b69bf25c`

#### メモ
- implementation review は pass。non-blocking として `graph.nodes_by_id` ベースの selector/close-set resolve は後続 slice で `.meta.json` authoritative read へ寄せる余地があるとコメントされた。
- qa review は pass。`metadata_validation_failed` / `remote_close_failed` の JSON field matrix と remote failure で local delete 未開始を確認した。
- spec review は pass。S01 I2 の bounded scope と issue docs の barrier contract が整合していることを確認した。
- actual local delete / partial failure / dependency scrub は未着手であり、次の S02/S03 で扱う。

### 2026-04-09 11:15 - 16:40

#### 対象
- Step: S02
- AC/EC: AC-001, EC-010

#### 実施内容
- issue target delete の success path を provider-side runtime に追加し、`delete iss-00056 --yes` / `--id` / `--github-issue` / issue + `--recursive` accepted no-op を end-to-end で通した。
- S02 の review loop で見つかった blocker を順に解消した。
- parent target が S02 で remote close / subtree metadata validation へ入らないよう early-stop へ修正した。
- forced issue delete が active target を削除した場合に active を clear し、失敗時は snapshot から survivor を復旧する best-effort repair を入れた。
- `already_closed` remote issue success path、remote close failure で local delete 未開始、Windows read-only `.meta.json` を含む local delete retry、post-close local delete failure の `local_delete_partial_failure` を tests で固定した。
- `local_delete_partial_failure` を S02 の issue-target partial-failure slice として requirement / plan に明記し、review scope と contract を整合させた。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_shell_s11 tests.cli_runtime.test_runtime_close_s12 tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_close

Ran 98 tests in 3.711s
OK

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=17

implementation review (S02)

pass

qa review (S02)

pass

spec review (S02)

pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` - issue target delete success path、post-delete active repair、local delete partial failure を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - delete use case に必要な active snapshot / node repo seam を公開
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - delete path の active store / node repo wiring を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_repo.py` - read-only file を含む tree delete retry を追加
- `tests/cli_runtime/test_runtime_delete_s13.py` - success / already-closed / remote-close-failed / active repair / local delete partial failure / JSON matrix regression tests を追加
- `tests/cli_runtime/test_delete.py` - command-level delete E2E と gh stub strictness / read-only delete retry test を追加
- `spec-dock/active/issue/requirement.md` - `local_delete_partial_failure` に post-delete active repair failure を含める契約を明記
- `spec-dock/active/issue/plan.md` - S02 gate に issue-target partial-failure slice と JSON / remote-failure coverage を追加
- `spec-dock/active/issue/report.md` - S02 実装記録を追記

#### コミット
- `8a62e363da65bbad8f91772f6032f621abc1b4c9`

#### メモ
- implementation review は pass。non-blocking として force-required partial failure guidance で `--force` を保持する改善余地が残るとコメントされた。
- qa review は pass。non-blocking として clear fallback branch と `fs_repo.delete_tree` 異常系 coverage の追加余地が残るとコメントされた。
- spec review は pass。S02 scope に issue-target partial-failure を明示したことで、review gate と contract の不整合は解消した。
- S02 では parent recursive delete / dependency scrub / epic final close-out は未着手のままであり、S03 で扱う。

### 2026-04-09 16:45 - 20:10

#### 対象
- Step: S03 I1
- AC/EC: AC-002, EC-010

#### 実施内容
- parent recursive delete を provider-side runtime に追加し、epic / initiative target の subtree local delete を deepest-first、同一 depth では lexical order で実行する contract を実装した。
- subtree 内 linked GitHub issue 群は remote close-only の barrier を先に通し、1 件でも failure があれば local subtree removal を開始しないよう固定した。
- force path では boundary dependency conflict を override した上で、surviving initiative / epic / issue の `deps.json` から deleted subtree への参照を scrub する経路を追加した。
- dependency scrub は local node id、numeric issue number、repo-scoped issue ref、canonical GitHub issue URL を扱い、survivor context で曖昧な numeric ref は保持するようにした。
- local subtree delete の partial failure では deleted / remaining node ids、active restore result、dependency scrub failures、recovery guidance を structured payload で返すようにした。
- partial failure guidance は元の invocation semantics を維持し、`--recursive` / `--force` を伴っていた delete は retry command に同じ flag を残すよう修正した。
- code review 指摘に対応し、force path の deps topology load failure を generic exception へ落とさず requirement vocabulary に沿った `metadata_validation_failed` へ fail-closed mapping する path を追加した。
- topology load failure では remote close / local delete を開始しないことを tests で固定した。

#### 実行コマンド / 結果
```bash
python -m py_compile src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py tests/cli_runtime/test_runtime_delete_s13.py

success

python -m unittest -v tests.cli_runtime.test_runtime_delete_s13 tests.cli_runtime.test_delete tests.cli_runtime.test_runtime_shell_s11 tests.cli_runtime.test_runtime_close_s12 tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_close

Ran 108 tests in 3.213s
OK

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=17

implementation review (S03 I1)

pass

qa review (S03 I1)

pass

spec review (S03 I1)

pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` - parent recursive delete、dependency scrub、topology load failure fail-closed、partial failure guidance を追加
- `tests/cli_runtime/test_runtime_delete_s13.py` - parent recursive delete / dependency scrub / topology load failure / partial failure guidance の regression tests を追加
- `spec-dock/active/issue/report.md` - S03 I1 実装記録を追記

#### コミット
- `63bdf8b60a9256007c96fbef6d2814d91b7f788f`

#### メモ
- implementation review は一度 fail。topology load failure が structured result 契約と requirement vocabulary を破る P1 指摘に対し、`metadata_validation_failed` へ fail-closed mapping を追加し、fresh rerun で pass となった。
- qa review は pass。non-blocking として raw int dependency ref 専用回帰、`json_store` 経由 scrub path、childless parent の `--recursive` 専用回帰に追加余地が残る。
- spec review は pass。non-blocking として partial failure retry guidance は invocation semantics を保持すべきと指摘され、`--recursive` / `--force` を復元する形へ修正済み。
- S03 I1 完了時点で parent recursive delete / partial failure / dependency scrub / topology load failure fail-closed のコア契約は固定された。残りは commit、`sync --github`、`iss-00056` close、epic final close-out evidence である。

### 2026-04-09 20:15 - 20:35

#### 対象
- Step: S90 / S99 / final close-out
- AC/EC: AC-003

#### 実施内容
- S03 I1 の実装差分を commit し、delete command の parent recursive delete / dependency scrub / topology fail-closed / docs parity を確定した。
- `./spec-dock/scripts/spec-dock close --id iss-00056` を実行し、linked GitHub issue `#56` を CLOSED へ遷移させた。
- `./spec-dock/scripts/spec-dock sync --github` を実行し、dogfooding workspace の index / tree / deps / dashboard を更新して `iss-00056` の local status を `done` へ同期した。
- 続けて `./spec-dock/scripts/spec-dock close --id epic-00054` と `./spec-dock/scripts/spec-dock sync --github` を実行し、epic `#54` の close-out と progress snapshot 更新まで完了した。

#### 実行コマンド / 結果
```bash
git commit -m "feat(runtime): 親ノード削除とclose-out契約を追加する" -m "- parent recursive delete と dependency scrub を追加する
- topology load failure の fail-closed と retry guidance を整える
- delete / close-out の dogfooding docs と report を更新する

Refs: #56"

[iss-00056-delete-local-spec-nodes-with-safeguards-and-epic-final-closeout 63bdf8b] feat(runtime): 親ノード削除とclose-out契約を追加する

./spec-dock/scripts/spec-dock close --id iss-00056

spec-dock: ok (close) target=iss-00056 node=iss-00056 kind=issue github=#56 state=CLOSED already_closed=false

./spec-dock/scripts/spec-dock sync --github

spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md

./spec-dock/scripts/spec-dock close --id epic-00054

spec-dock: ok (close) target=epic-00054 node=epic-00054 kind=epic github=#54 state=CLOSED already_closed=false

./spec-dock/scripts/spec-dock sync --github

spec-dock: ok (sync) wrote=spec-dock/.agent/index-all.json,spec-dock/.agent/tree-all.json,spec-dock/.agent/index.json,spec-dock/.agent/tree.json,spec-dock/tree-all.puml,spec-dock/tree.puml,spec-dock/.agent/deps-issues.json,spec-dock/deps-issues.puml,spec-dock/dashboard.md
```

#### 変更したファイル
- `spec-dock/.agent/index-all.json` - `iss-00056` を `done`、`epic-00054` を GitHub CLOSED / progress done=2 へ同期
- `spec-dock/tree-all.puml` - `iss-00056 [DONE]` を反映
- `spec-dock/dashboard.md` - ready board を再生成
- `spec-dock/active/issue/report.md` - final close-out evidence を追記
- `spec-dock/active/epic/report.md` - epic close-out evidence を追記

#### コミット
- `63bdf8b60a9256007c96fbef6d2814d91b7f788f`

#### メモ
- final close-out 後の `spec-dock/.agent/index-all.json` では `iss-00056.status=done`、`iss-00056.github.state=CLOSED`、`epic-00054.github.state=CLOSED`、`epic-00054.progress.done=2` を確認した。
- non-blocking の残件は raw int dependency ref 専用 scrub 回帰、`json_store` 経路 scrub 回帰、childless parent の `--recursive` 専用回帰であり、issue acceptance には影響しない。

## 遭遇した問題と解決 (任意)
- 問題: spec review で `confirmation_required` の意味論が requirement と衝突すると指摘された
  - 解決: issue docs に S01 I1 staged implementation note を追加し、interim placeholder と final 正規化タイミングを明記した

## 学んだこと (任意)
- S01 のような staged delivery では、temporary status semantics も docs 契約へ明示しないと spec review で詰まる
- delete 系の destructive command では text 表現だけでなく JSON field matrix の required/forbidden を先に固定する価値が高い

## 今後の推奨事項 (任意)
- S01 I2 では subtree-wide metadata validation と remote-close barrier を先に固定する
- selector 解決は `graph.nodes_by_id` ベースから requirement の basename token discovery へ寄せる余地が残る

### 2026-04-10

#### 対象
- Step: S04 I1
- AC/EC: live-manual-defect-01

#### 実施内容
- live manual test `mt-08` で見つかった defect-1 を受けて、`delete_node()` の graph 構築前 `load_node_records()` 失敗を delete 専用に補足する remediation を追加した。
- selector が `<target>` / `--id` のときだけ canonical node id から target-local directory を再特定し、target `.meta.json` が missing / unreadable / malformed / non-object の場合は `metadata_validation_failed` の structured result へ正規化するようにした。
- あわせて application regression と actual runtime regression を追加し、target-local metadata edge でも `--json` contract が plain error text へ崩れないことを固定する準備を入れた。

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` - target-local metadata parse failure の fallback normalize を追加
- `tests/cli_runtime/test_runtime_delete_s13.py` - graph 構築前 load failure の application regression を追加
- `tests/cli_runtime/test_delete.py` - actual runtime `delete --id ... --yes --json` regression を追加

#### メモ
- remediation は delete command 専用の wrapper seam に閉じ、unrelated malformed node による全体 load failure の扱いは従来どおり fail-closed に残した。
- manual rerun / validate / commit evidence はこの後続けて積む想定であり、S04 report は remediation entrypoint と defect traceability を先に残している。

### 2026-04-10 16:20 - 16:50

#### 対象
- Step: S04 I1 / S04 I2 / close-out
- AC/EC: live-manual-defect-01

#### 実施内容
- target-local metadata remediation を live rerun に合わせて補強し、`load_node_records()` が `RuntimeError` を返したときに、exception message 内の target `.meta.json` path から canonical target directory を逆引きできる fallback を追加した。
- これにより、directory discovery が曖昧なときでも `<target>` / `--id` の delete 専用 wrapper seam で `metadata_validation_failed` を structured result へ正規化できるようにした。
- runtime regression と CLI regression を更新し、graph build 前 load failure と live-like ambiguous directory 条件を固定した。
- live manual `mt-08` は fresh workspace を working tree installer (`PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli init/update`) で作り直して rerun し、target metadata edge が structured JSON へ正規化されることを確認した。

#### 実行コマンド / 結果
```bash
python -m py_compile \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py \
  tests/cli_runtime/test_runtime_delete_s13.py \
  tests/cli_runtime/test_delete.py

python -m unittest -v \
  tests.cli_runtime.test_runtime_delete_s13 \
  tests.cli_runtime.test_delete \
  tests.cli_runtime.test_runtime_shell_s11 \
  tests.cli_runtime.test_runtime_close_s12 \
  tests.cli_runtime.test_runtime_active_s06 \
  tests.cli_runtime.test_runtime_deps_s04 \
  tests.cli_runtime.test_close

./spec-dock/scripts/spec-dock validate
```

- `py_compile`: success
- targeted/full regression subset: `Ran 111 tests ... OK`
- dogfooding validate: `spec-dock: ok (validate) nodes=17`
- live manual rerun evidence:
  - `manual-tests/reports/2026-04-10-epic-00054-github-lifecycle-live-manual/evidence/mt-08-topology-metadata-edges-rerun.txt`
  - target metadata edge now returns structured `metadata_validation_failed` JSON with `target_id=iss-00048` and `offending_node_ids=["iss-00048"]`

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` - exception message の `.meta.json` path から target-local metadata failure を逆引きする fallback を追加
- `tests/cli_runtime/test_runtime_delete_s13.py` - ambiguous directory 条件でも target-local metadata normalization が効く regression を追加
- `tests/cli_runtime/test_delete.py` - readonly metadata setup に沿う actual runtime regression を維持
- `manual-tests/reports/2026-04-10-epic-00054-github-lifecycle-live-manual/execution-log.md` - mt-08 rerun pass を追記
- `manual-tests/reports/2026-04-10-epic-00054-github-lifecycle-live-manual/checklist.md` - mt-08 status を pass へ更新
- `manual-tests/reports/2026-04-10-epic-00054-github-lifecycle-live-manual/summary.md` - final verdict を pass へ更新
- `spec-dock/active/issue/report.md` - S04 remediation / rerun close-out evidence を追記

#### メモ
- `uvx --from /srv/mount/spec-dock` は uncommitted working-tree change を manual verification 用 SUT へ反映しなかったため、working tree verification では `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli init/update` を使った。
- `.meta.json` が `444` である点は readonly metadata permission contract と整合するため、manual setup observation として残し、blocking defect からは外した。

### 2026-04-10 17:00 - 17:40

#### 対象
- Step: S04 follow-up remediation / review-closeout
- AC/EC: live-manual-defect-01

#### 実施内容
- code review fail を受け、target-local metadata fallback の candidate selection を再度補強した。
- `initiatives/<init>` / `initiatives/<init>/epics/<epic>` / `initiatives/<init>/epics/<epic>/issues/<issue>` の canonical tree placement だけを fallback 候補に通す helper を追加し、stale / non-canonical な duplicate-like directory が混ざっても structured `metadata_validation_failed` contract が崩れないようにした。
- CLI regression は `--id` に加えて positional target (`delete iss-00056 --yes --json`) も追加し、manual defect-1 の selector variation を自動回帰へ固定した。
- full regression / validate / fresh review cycle を再実施し、implementation / QA / spec の 3 review すべてを pass に戻した。

#### 実行コマンド / 結果
```bash
python -m py_compile \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py \
  tests/cli_runtime/test_runtime_delete_s13.py \
  tests/cli_runtime/test_delete.py

python -m unittest -v \
  tests.cli_runtime.test_runtime_delete_s13 \
  tests.cli_runtime.test_delete \
  tests.cli_runtime.test_runtime_shell_s11 \
  tests.cli_runtime.test_runtime_close_s12 \
  tests.cli_runtime.test_runtime_active_s06 \
  tests.cli_runtime.test_runtime_deps_s04 \
  tests.cli_runtime.test_close

./spec-dock/scripts/spec-dock validate
```

- `py_compile`: success
- targeted/full regression subset: `Ran 113 tests ... OK`
- dogfooding validate: `spec-dock: ok (validate) nodes=17`
- implementation review: `pass`
- QA review: `pass`
- spec review: `pass`

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/delete_node.py` - canonical tree placement filter を追加し、target-local metadata fallback の stale/non-canonical candidate 混入を除外
- `tests/cli_runtime/test_runtime_delete_s13.py` - canonical/non-canonical duplicate-like directory regression を追加
- `tests/cli_runtime/test_delete.py` - positional target `--json` regression を追加
- `spec-dock/active/issue/report.md` - S04 follow-up remediation と final review 結果を追記

#### メモ
- non-blocking として、`load_node_records()` が `.meta.json` path を含まない generic runtime error を返し、canonical directory が複数ある異常環境では structured fallback が成立しない余地は残るが、今回の defect-1 scope と acceptance には影響しない。
- live manual summary / execution log の final verdict は `pass` のままで、blocking defect は解消済みと判断した。

### 2026-04-10 18:10 - 18:40

#### 対象
- Step: PR #57 review triage / blocker fix
- AC/EC: review-feedback-triage

#### 実施内容
- PR `#57` の Copilot / Codex review を取得し、今回必須で対応するものと proposal を切り分けた。
- 必須対応と判定したのは 2 点である。
  - `delete <target> --yes` の positional target を `123` / `#123` / URL も受け付けるように読める docs mismatch
  - repo-local dogfooding runtime に `delete` surface が未反映で、`spec-dock/docs/reference_github.md` と実装がずれている parity gap
- proposal と判定したのは 1 点である。
  - delete remote-close barrier で `issue_close` failure 後に post-failure `issue_view_snapshot` を再確認する改善提案
- blocker fix として provider/dogfooding docs の `delete <target>` 記述を node id only に修正し、あわせて `PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli update .` で dogfooding workspace を refresh して repo-local runtime parity を回復した。

#### 分析結果
- Copilot comment 1 / 3:
  - 判定: blocker
  - 理由: `delete <target>` は実装上 node id positional alias であり、数字 / URL を受け付けると読む余地がある docs は誤案内になる。
- Copilot comment 2 / 3:
  - 判定: blocker
  - 理由: dogfooding docs が top-level `delete` を案内しているのに、repo-local runtime copy に parser/registry/delete command が無い状態は parity 不整合である。
- Codex P2 comment:
  - 判定: proposal
  - 理由: race hardening の改善提案であり、現 requirement/design の acceptance や current blocker には含まれない。現時点では checks failure でも contract mismatch でもない。

#### 実行コマンド / 結果
```bash
PYTHONPATH=/srv/mount/spec-dock/src python -m spec_dock.cli update .

./spec-dock/scripts/spec-dock --help
./spec-dock/scripts/spec-dock delete --help
./spec-dock/scripts/spec-dock validate
```

- `spec-dock: ok (update) -> /srv/mount/spec-dock`
- repo-local runtime help に `delete` が現れることを確認
- repo-local `delete --help` が表示されることを確認
- dogfooding validate は継続して成功

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/docs/reference_github.md` - `delete <target>` の target syntax を実装どおり node id only へ修正
- `spec-dock/docs/reference_github.md` - dogfooding docs 側も同じ wording に修正
- `spec-dock/scripts/spec_dock_runtime/**` - refresh により repo-local runtime parity を回復
- `spec-dock/active/issue/report.md` - review triage と blocker/proposal の判定を追記

#### メモ
- Codex の P2 は follow-up 候補として残すが、今回の PR blocker ではない。
- review 指摘は「docs mismatch は修正」「proposal は今回は見送る」の方針で整理した。

## 省略/例外メモ (必須)
- なし
