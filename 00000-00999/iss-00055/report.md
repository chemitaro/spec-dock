---
種別: 実装報告書（Issue）
ID: "iss-00055"
タイトル: "Close Linked Github Issues From Specdock Command"
関連GitHub: ["#55"]
状態: "draft | approved"
作成者: "Codex CLI"
最終更新: "2026-04-09"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00054", "init-local-00002"]
---

# iss-00055 Close Linked Github Issues From Specdock Command — 実装報告（LOG）

## 実装サマリー (任意)
- S01 として close use case / gateway seam / result contract を provider-side runtime に追加した。
- linked issue 不在、already-closed success/no-op、read-after-close race 正規化、non-cascade、`gh issue close` adapter 契約をテストで固定した。

## 実装記録（セッションログ） (必須)

### 2026-04-09 05:40 - 07:25

#### 対象
- Step: S01
- AC/EC: AC-001, EC-001, EC-002, EC-003

#### 実施内容
- `close_node` application use case を追加し、`IssueGateway.issue_close` seam と `CloseNodeRequest/Result` を導入した。
- `gh issue close` adapter を `infra/github_cli.py` に追加し、bootstrap から `close_node` を呼べるようにした。
- S01 review cycle に合わせて、`node_id` / `github_issue` 解決、already-closed success/no-op、read-after-close race、gh failure、initiative/epic non-cascade、adapter command 契約の tests を追加した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.cli_runtime.test_runtime_close_s12

OK (15 tests)

python -m unittest -v tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04 tests.cli_runtime.test_runtime_close_s12

OK (39 tests)

spec review (S01)

pass

qa review (first pass)

fail

qa findings reflected and tests rerun

green

qa review (final)

pass

implementation review (final)

pass
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/contracts.py` - close request/result contract と use case slot を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/ports.py` - `IssueGateway.issue_close` seam を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/close_node.py` - close use case を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/github_cli.py` - `gh issue close` adapter を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py` - runtime wiring を追加
- `tests/cli_runtime/test_runtime_close_s12.py` - S01 seam / QA regression tests を追加

#### コミット
- pending

#### メモ
- spec reviewer は S01 scope adherence を `pass`。
- qa reviewer は一度 `post-failure OPEN recheck` と bootstrap close wiring coverage の不足で `fail`。指摘反映後の再レビューで `pass`。
- implementation reviewer は最終的に `pass`。reviewer session が不安定だったため、途中で read-only 補助レビューも併用して blocker の有無を確認した。

## 遭遇した問題と解決 (任意)
- 問題: reviewer session が途中で停止・消失することがあった
  - 解決: 不要 session を close し、fresh reviewer で再実行した

## 学んだこと (任意)
- `close_node` は `set_active` / `check_deps` と同じ target resolve contract を踏襲できる
- close failure は fallback read が `CLOSED` のときだけ success/no-op に正規化すべき

## 今後の推奨事項 (任意)
- S02 では parser / registry / renderer と end-to-end runtime tests を先に固定する

## 省略/例外メモ (必須)
- `code_reviewer` session が不安定だったため、再実行と read-only 補助レビューを併用した。最終 verdict は `pass`。
