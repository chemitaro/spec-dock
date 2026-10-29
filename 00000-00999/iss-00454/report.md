---
種別: レポート（Issue）
ID: "iss-00454"
タイトル: "Run Spec Dock CI On Local Mac Mini Runner"
関連GitHub: ["#454"]
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- リポジトリ：Provider CI に `route` を足し、変数 `SPEC_DOCK_CI_RUNNER` が `local` で信頼する同じリポジトリの PR のときだけ、`provider-tests` と `Provider distribution parity (ubuntu-latest)` を手元のランナーに送る形にした。ゲートとフック（`.github/scripts/ci-runner-job-gate.py`）、VM と VM の中の設定、登録、Mac の側の導入（`.github/runner/`）、手順書（`docs/ci-local-runner.md`）、テストを足した。PR #458。
- 利用者の環境（段階1、D9 の承認の後）：専用の Lima 2.2.1（`~/Library/Application Support/spec-dock-ci-vm/lima/`、SHA256SUMS で確認）、VM `spec-dock-ci`（`LIMA_HOME=/Volumes/990p2t/vm/spec-dock-ci-lima`、Ubuntu 24.04 ARM64、vz、plain、CPU 6、8GiB、40GiB）、VM の中の nftables・ランナーの利用者2つ・フック、LaunchAgent `com.chemitaro.spec-dock-ci-vm`。ランナーの登録（S4）と fork の PR の承認（S6）は利用者が行った。
- S6：変える前の値は `{"approval_policy":"first_time_contributors"}`、後は `all_external_contributors`。戻すときは `approval_policy=first_time_contributors` で同じ PUT。
- 段階2（macOS の VM）は作っていない（D7）。macOS の配布の確かめは GitHub に残る。
- 実機で分かって直したこと：plain モードでは VM の DNS は `192.168.5.2:53` だけが答える（`192.168.5.3` は応答なし）ので、許可を `192.168.5.2` の53番にした。規則を読み込んだ瞬間に既存の SSH の返りが止まったので `tcp sport 22 accept`（22番は root の sshd だけが使える）を足した。

## Verification

| AC | 結果 | 証拠 |
|---|---|---|
| 01 | テストは通過。実機は、変数が未設定の run（40853980916、40859634671、40874540057）で `route` を含むすべてのジョブが `GitHub Actions` のランナーで成功。不正な値の run は（S7 の後に記入） | `tests/integration/test_issue454_runner_gate.py` |
| 02 | （S7 の後に記入） | |
| 03 | テストで、fork・bot・外の人・別のリポジトリ・`pull_request` 以外・読めないイベント・別の場所のイベントのファイルを拒否。VM に置いたフックを `spec-dock-runner-1` として実行し、同じリポジトリ＝許可（0）、fork＝拒否（1）、別の場所のファイル＝拒否（1）、push＝拒否（1）。実際の fork の PR は作れないので**未確認** | VM での実行（2026-10-29T10:2x Z） |
| 04 | ランナーの利用者として `sudo -n true` は失敗。`192.168.5.2:9222`（Mac の Chrome のデバッグの口）、`192.168.5.2:5432`、`192.168.0.43:6768`（Mac の LAN の IP の Orca）、`100.85.74.8:8766`（Mac の Tailscale の IP）、`169.254.169.254:80`、`192.168.5.2:22` の6つはすべて接続できず、拒否の規則の counter がちょうど6増えた。IPv6 は VM にアドレスも経路もなく、リテラルの宛先にも届かない。`https://github.com`・`https://pypi.org` は 200。`limactl list --json` で plain=true、mounts・portForwards なし、containerd は system・user とも false。`lima-guestagent` はプロセス・実行ファイル・unit とも無い。docker・containerd・podman・nerdctl は無い | VM での実行 |
| 05 | VM に `gh` の hosts.yml・`.netrc`・`.git-credentials` は無い。秘密鍵は VM 自身の sshd のホスト鍵だけ。差分にトークンの形の文字列は無い。**登録のトークンの件**（下の Notes）を直した後、`_diag`・journal・`/var/log` にトークンの値は無い | VM での検索 |
| 06 | テストで `_tool` だけが残り、想定外の `RUNNER_TEMP` では何も消さない。VM で掃除のフックを実行し、作業場所が空になった。実際のジョブの後は（S7 の後に記入） | |
| 07 | ジョブの無いときに `limactl stop`（10:42:41Z）→ LaunchAgent が62秒後に起動 → 2つのランナーが `Connected to GitHub`・`Listening for Jobs`、nftables も起動時に読み込み | `ensure-vm.log`、VM の journal |
| 08 | 手順書にある。リハーサルは（S7 の後に記入） | `docs/ci-local-runner.md` |
| 09 | 前（09:41:33Z）と後で、退去費用の LaunchAgent の plist、専用の `limactl`、`ci_vm_host_watch.py` の SHA256 と、`ci-shadow/lima.yaml` の更新時刻が同じ | |
| 10 | 利用者（統括を通して）が `all_external_contributors` を確かめた | |
| 11 | 最終品質ゲート（下）。時間の表は（S7 の後に記入） | |

GitHub のランナーでの時間（この PR、run 40859634671）：`route` 5秒、`provider-tests` 475秒、Linux の配布 114秒、macOS の配布 169秒。直近8回の他の PR：`provider-tests` 250〜454秒、Linux の配布 69〜119秒。

### 最終品質ゲート

- 1回目（`0c26a77e`）：`make lint` 通過、`uv run pytest` 2993 passed・8 skipped。Spec（opus/xhigh）P1 1件（P-1：root がランナーの利用者の書ける `installdependencies.sh` を実行）、P2 3件、P3 3件。Standards（sonnet/high）P0/P1 なし、P2 2件、P3 9件。
- P-1 と、同じ原因の P-2・T-1 を直した（`640781c8`：root の持ち物の展開から依存を導入、unit を root の文面で書き `svc.sh` を使わない）。VM に反映し、2つのランナーが新しい unit で `Listening for Jobs`。
- 2回目（`640781c8`）：Spec の再レビューで P-1・P-2 は fixed、新しい P0/P1 なし。`make lint` と `uv run pytest` は（記入）。

## Residual Risks / Follow-ups

- 信頼する作者の PR のコード（とその依存）は、ランナーの利用者として `.env` やランナーの本体を書き換え、開始前のフックを外せる（P-4）。差し替えたフックが同じ許可の行を出せば、ログでの検知も効かない。前提は信頼する作者を信頼すること。疑わしいときは変数を `hosted` に戻し、VM を作り直す。作り直しの周期は決めていない。
- x86_64 の Linux での確かめが、変数が `local` の間はなくなる（D1、受け入れたリスク）。
- 段階2（D7）で要ること：tart（FSL-1.1、OpenAI 著作）と softnet（root の SUID、sudo のパスワードが1回）、softnet の既定で VM から届く Mac の側の口（bridge の gateway）を止める設定、数十GB のイメージ、Apple の使用許諾（1台で2つまで）、sudo できない利用者でのランナー、macOS とランナーの更新の保守、Linux の VM と合わせたメモリ（16GB 前後）。
- 申し送り（ゲートの P2/P3、未対応）：T-2 nftables.conf を置く前に検証する（構文エラーのファイルが残ると次の起動で遮断なし）／P-3 手順書の curl の判定（curl 8 は「Couldn't connect」としか出さないので、counter で判定する形に直す。IPv6 は github.com に AAAA が無いので、リテラルで試す）／Q-1 テストで `--no-same-owner` と `svc.sh` 不使用をより強く確かめる／Q-2 root が `.env` を grep で読む（FIFO で止められる）／T-3 壊れたキャッシュの再取得／T-4・P-6 登録と導入の再実行・作り直しの手順／T-5 `host-install.sh` の途中失敗／T-6 launchd の終了で hostagent が巻き込まれないか（実機では VM は動き続けている）／T-7 event.json とジョブの突き合わせ／T-8 シェルの振る舞いのテスト／T-9 読めないイベントの理由の文／T-10 `route` の checkout の `persist-credentials: false` と `timeout-minutes`／T-11 リポジトリ名の直書き／P-5 route のテストの追加／P-7 DNS で LAN や tailnet の名前を引ける（接続は拒否）。
- Lima 2.3 が正式版になったら `hostLoopback: false` を足す。
- Lima のイメージのキャッシュが `~/Library/Caches/lima/` に残る（約3.5GiB の変換済みの raw）。

## Notes

### 登録のトークンが VM の記録に残った件（2026-10-29、直した）

- 最初の `register-runner.sh` は `sudo --preserve-env=ACTIONS_RUNNER_INPUT_TOKEN` を使い、sudo が渡した環境変数の値を VM の journal と `/var/log/auth.log` に記録した。確かめのときにその行を表示したので、値は担当の会話の記録にも出た。
- 影響：登録のトークンは、このリポジトリに新しいランナーを登録することだけに使え、発行から1時間（10:37Z ごろ発行）で切れる。VM の記録はランナーの利用者には読めない。Mac の資格情報は関係しない。
- 対応：VM の該当の行を消し、journal を回して古い記録を消した。スクリプトを pipe で渡す形に直し（`0c26a77e`）、偽の値で sudo の記録に値が出ないことを VM で確かめた。期限の後（20:40 JST 以降）に、利用者がランナーの一覧を確かめ、spec-dock-ci-1（id 21）と spec-dock-ci-2（id 22）の2つだけで、どちらも online、知らないランナーは無かった（統括が確認）。
