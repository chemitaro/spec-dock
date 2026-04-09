---
種別: 実装報告書（Issue）
ID: "iss-00056"
タイトル: "Delete Local Spec Nodes With Safeguards And Epic Final Closeout"
関連GitHub: ["#56"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-09"
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
- pending

#### メモ
- implementation review は pass。non-blocking として `confirmation_required` の interim semantics は S01 I2/S02 で正規化が必要とコメントされた。
- qa review は pass。前回 blocker だった `--json` field matrix と preflight pass の見え方は解消済み。
- spec review は pass。issue docs に staged implementation note を追加したことで、S01 I1 の interim semantics が docs と整合した。
- S01 I1 の範囲上、actual delete / subtree metadata barrier / required remote close set / partial failure handling は未着手であり、次の S01 I2 で扱う。

## 遭遇した問題と解決 (任意)
- 問題: spec review で `confirmation_required` の意味論が requirement と衝突すると指摘された
  - 解決: issue docs に S01 I1 staged implementation note を追加し、interim placeholder と final 正規化タイミングを明記した

## 学んだこと (任意)
- S01 のような staged delivery では、temporary status semantics も docs 契約へ明示しないと spec review で詰まる
- delete 系の destructive command では text 表現だけでなく JSON field matrix の required/forbidden を先に固定する価値が高い

## 今後の推奨事項 (任意)
- S01 I2 では subtree-wide metadata validation と remote-close barrier を先に固定する
- selector 解決は `graph.nodes_by_id` ベースから requirement の basename token discovery へ寄せる余地が残る

## 省略/例外メモ (必須)
- なし
