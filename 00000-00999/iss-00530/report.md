---
種別: レポート（Issue）
ID: "iss-00530"
関連GitHub: ["#530"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

利用者が明示して入れたときだけ入るダッシュボードの常駐（`spec-dock dashboard service install`／`status`／`uninstall`）と、常駐から動く `dashboard serve --service`（ロックの待ち、Tailscale の住所の取り直し、版の更新での終了コード75）を作った。前面の `serve` は版の更新を API と標準エラーで知らせる。公開のコマンドは 58 → 61。

## Outcome

- ファイルの形：`runtime/domain/dashboard_service.py`（`DashboardServiceSpec` は同期の `SchedulerSpec` を広げる。launchd の plist は `KeepAlive`・`RunAtLoad`・`ThrottleInterval` 10、systemd の単位は `Restart=always`・`RestartSec=10`・`WantedBy=default.target`、記録した引数の読み戻し `service_settings`）。
- 管理の側の部品：`runtime/infra/dashboard_service.py`。`DashboardLaunchdService` は同期の `LaunchdScheduler` を継ぎ（plist の中身を作るところを `_payload` に分けた。同期の振る舞いは変えていない）、`DashboardSystemdService` は `SystemdScheduler` を継いで単位1つ（timer なし）にした。工場 `dashboard_service_for`、`installed_version()`。
- コマンド：`runtime/application/dashboard_service.py`（`install`、`status`、`uninstall`）。`dashboard_commands.serve` に `--service`（ヘルプと補完に出さない）と `--state-root`、待ちの輪（`ServeTiming`）。`infra/dashboard_server.py` に `defer_tailscale` と `add_tailscale()`。`application/dashboard_http.py` の `/api/v1/repositories` の `server` に `installed_version` と `restart_required`。
- テストの守り：`tests/conftest.py` のセッションの守りと各テストの工場（`tests/support/dashboard_service.py` の `FakeServices`）で、`dashboard_service_for` と `detect_environment` を差し替える。設定のファイルは一時のディレクトリに書き、`launchctl`／`systemctl` は記録する偽物が答える。本物の launchd と systemd には登録していない。
- 文書：`reference_cli.md`（C59〜C61、C55 の `--state-root`、「ダッシュボードの常駐の契約」の節）、`docs/README.md`、README、`cli-redesign-guide.html`（配布と dogfood の写し）。`static-inventory.json` の3行の sha256 を更新し、main の値を `known_old_sha256` に足した。

### 0.6.0 の移行の注記（#534）に要る契約の変更

- 増えたコマンド3つ：`dashboard service install [--port N] [--tailscale]`、`dashboard service status`、`dashboard service uninstall`（公開 61）。`install`／`uninstall` は `--dry-run` も `--yes` も受け付けない。
- `dashboard serve` に `--state-root ROOT`（絶対の道。相対は `DASHBOARD_STATE_ROOT_INVALID`、終了コード2）と内部の `--service`。
- 新しい失敗コード：`DASHBOARD_SERVICE_UNSUPPORTED`（終了コード3）、`DASHBOARD_SERVICE_FAILED`（終了コード3）、`DASHBOARD_STATE_ROOT_INVALID`（終了コード2）。`serve --service` は版が変わると CLI の JSON を書かずに終了コード75で終わる。
- 利用者の PC に入り得るファイル（`install` を実行したときだけ）：`~/Library/LaunchAgents/io.github.chemitaro.spec-dock.dashboard.plist`（launchd）か `${XDG_CONFIG_HOME:-~/.config}/systemd/user/spec-dock-dashboard.service`、launchd の記録 `<state_root>/dashboard/service.log`。`uninstall` で消える。
- `/api/v1/repositories` の `server` に `installed_version` と `restart_required` が増えた（項目の追加なので版は変えない）。
- 戻すときは、常駐を入れていれば先に `dashboard service uninstall`。

### 作業者の判断（仕様の decisions にも書いた）

- systemd の単位の出力は journal に任せる（`StandardOutput=append:` は道の引用符を解かない）。`service.log` は launchd だけ。
- `install` は、別の状態の置き場で入れた常駐があっても書き直す（利用者ごとに1つ。`status` が記録した置き場を示す）。
- systemd のユーザーの管理が一時的に応えないときも、単位のファイルがあれば `status` に見え、`uninstall` で外す。
- 起動の版は `serve` の最初に読んだ版で、在りかの記録と API の `version` にも同じ値を使う（ロックを待ってから引き継いだ常駐も、最初の確かめで古い版と分かる）。

## Verification

- `spec-dock scope check iss-00530`：誤り 0、警告 0。
- 仕様のレビュー（spec-reviewer opus/high）：1回目で pass（P0・P1 なし、P2 5件、P3 1件）。P2 のうち「systemd の判定が付かないときの uninstall」と「`--dry-run` の扱い」は実装と仕様で扱った。記録は `.workbench/spec-review/iss-00530/`（`round-1.json`、`review-response.md`）。
- コードのレビュー（code-reviewer opus/high、standards と spec の2人、77b10aeb1）：両方 pass（P0・P1・P2 なし、P3 3件）。3件とも直した（9e6c727f2）：`--service` を補完から外す、前面の `installed_version` を読むたびに新しくする（起動の版に戻れば `restart_required` が false）、HTML の C55 と `DASHBOARD_STATE_ROOT_INVALID` の記述。記録は `.workbench/code-review/iss-00530/`。
- 新しいテスト：`tests/unit/domain/test_dashboard_service.py`（T-01）、`tests/unit/infra/test_dashboard_service_managers.py`（T-02、T-03）、`tests/cli_runtime/test_issue530_dashboard_service.py`（T-04〜T-06、T-10 の一部）、`tests/cli_runtime/test_issue530_serve_service.py`（T-07〜T-09、T-11。T-11 は子のプロセスで `serve --service --state-root` が別のサーバーのロックの間は終わらずに待ち、SIGTERM で0）。コマンドの数を縛るテストを 61 に直した。
- 本物の launchd と systemd への登録、ログインし直しての起動は確かめていない（利用者の登録を変えないため）。

## Final Quality Gate

（ゲートの結果をここに書く）

## Pull Request

（PR の URL と CI をここに書く）

## Residual Risks / Follow-ups

- 画面の帯での起動し直しの促し（Epic D-14）は画面の資源の担当（#544 か後続）。この Issue は API の `server.installed_version`／`restart_required` を足しただけ。
- Epic R-28 の受け入れ「ログインし直すとサーバーが動く」「パッケージを更新すると新しい版で動く」は、#534 の配布の後に利用者の PC（launchd）で確かめる必要がある。
- 別の状態の置き場で入れ直した後の `uninstall` は、前の置き場の `service.log` を消さない（仕様のレビューの P3）。
- 常駐で番号が使われているときは、終了コード3で終わり、launchd／systemd が10秒ごとに起動し直す（`status` は `running: false`、理由は `service.log` か journal）。
