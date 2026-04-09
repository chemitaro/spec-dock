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
- `c6434363fd69345a6e6ad77c0c265b9cc4802580`

#### メモ
- spec reviewer は S01 scope adherence を `pass`。
- qa reviewer は一度 `post-failure OPEN recheck` と bootstrap close wiring coverage の不足で `fail`。指摘反映後の再レビューで `pass`。
- implementation reviewer は最終的に `pass`。reviewer session が不安定だったため、途中で read-only 補助レビューも併用して blocker の有無を確認した。

## 遭遇した問題と解決 (任意)
- 問題: reviewer session が途中で停止・消失することがあった
  - 解決: 不要 session を close し、fresh reviewer で再実行した

### 2026-04-09 08:05 - 09:10

#### 対象
- Step: S02
- AC/EC: AC-001, AC-002

#### 実施内容
- top-level `close` command を parser / registry / command wrapper / CLI renderer に接続した。
- provider-side と dogfooding 側の `reference_github.md` を更新し、close-only / non-cascade / no local mutation / `sync --github` confirmation path を明記した。
- command-level E2E として `--id` / `--github-issue` に加え、positional issue number、canonical URL、`close -> sync --github` による `done` 観測まで tests を追加した。

#### 実行コマンド / 結果
```bash
python -m unittest -v tests.cli_runtime.test_runtime_close_s12 tests.cli_runtime.test_runtime_shell_s11 tests.cli_runtime.test_close tests.cli_runtime.test_runtime_active_s06 tests.cli_runtime.test_runtime_deps_s04

OK (55 tests)

implementation review (S02)

pass

qa review (S02)

pass

spec review (S02)

pass

./spec-dock/scripts/spec-dock validate

spec-dock: ok (validate) nodes=17
```

#### 変更したファイル
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/parser.py` - top-level `close` parser を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/registry.py` - `close` command registration を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/commands/close.py` - close command args / run path を追加
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/presentation/cli_text.py` - close success/no-op renderer を追加
- `src/spec_dock/assets/spec_dock/docs/reference_github.md` - close command contract と confirmation path を追記
- `spec-dock/docs/reference_github.md` - dogfooding docs parity を更新
- `tests/cli_runtime/test_runtime_shell_s11.py` - close command wrapper smoke test を追加
- `tests/cli_runtime/test_close.py` - close command E2E / sync confirmation tests を追加

#### コミット
- `8c5deac08f51e234a36b1826d984b790cd74bf27`

#### メモ
- implementation review は pass。non-blocking comment として positional target の command-level coverage 追加提案があり、`tests/cli_runtime/test_close.py` に反映した。
- qa review は pass。non-blocking note として positional node-id、explicit error path、`already_closed=true` の command-level 表示 coverage が残留リスクとして記録されたが、blocking finding はなかった。
- spec review は pass。issue docs と close-only / non-cascade / no local mutation / `sync --github` confirmation path の整合が確認された。
- `close` command 自体は local tree / docs / generated artifacts を直接変更せず、`sync --github` 実行後に `iss-00055` が `done` として観測されることを test で固定した。

## 学んだこと (任意)
- `close_node` は `set_active` / `check_deps` と同じ target resolve contract を踏襲できる
- close failure は fallback read が `CLOSED` のときだけ success/no-op に正規化すべき

## 今後の推奨事項 (任意)
- S02 では parser / registry / renderer と end-to-end runtime tests を先に固定する

## 省略/例外メモ (必須)
- `code_reviewer` session が不安定だったため、再実行と read-only 補助レビューを併用した。最終 verdict は `pass`。
