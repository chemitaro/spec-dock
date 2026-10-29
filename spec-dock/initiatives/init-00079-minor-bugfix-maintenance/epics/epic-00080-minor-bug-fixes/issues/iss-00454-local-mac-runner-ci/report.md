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

詳細: [Report Guide](../../../../../../docs/authoring/report.md)

## Outcome

- リポジトリ：Provider CI に `route` を足し、変数 `SPEC_DOCK_CI_RUNNER` が `local` で信頼する同じリポジトリの PR のときだけ、`provider-tests` と `Provider distribution parity (ubuntu-latest)` を手元のランナーに送る形にした。ゲートとフック（`.github/scripts/ci-runner-job-gate.py`）、VM と VM の中の設定、登録、Mac の側の導入（`.github/runner/`）、手順書（`docs/ci-local-runner.md`）、テストを足した。PR #458。
- 利用者の環境（段階1、D9 の承認の後）：専用の Lima 2.2.1（`~/Library/Application Support/spec-dock-ci-vm/lima/`、SHA256SUMS で確認）、VM `spec-dock-ci`（`LIMA_HOME=/Volumes/990p2t/vm/spec-dock-ci-lima`、Ubuntu 24.04 ARM64、vz、plain、CPU 6、8GiB、40GiB）、VM の中の nftables・ランナーの利用者2つ・フック、LaunchAgent `com.chemitaro.spec-dock-ci-vm`。ランナーの登録（S4）と fork の PR の承認（S6）は利用者が行った。
- S6：変える前の値は `{"approval_policy":"first_time_contributors"}`、後は `all_external_contributors`。戻すときは `approval_policy=first_time_contributors` で同じ PUT。
- 段階2（macOS の VM）は作っていない（D7）。macOS の配布の確かめは GitHub に残る。
- 実機で分かって直したこと：plain モードでは VM の DNS は `192.168.5.2:53` だけが答える（`192.168.5.3` は応答なし）ので、許可を `192.168.5.2` の53番にした。規則を読み込んだ瞬間に既存の SSH の返りが止まったので `tcp sport 22 accept`（22番は root の sshd だけが使える）を足した。

## Verification

| AC | 結果 | 証拠 |
|---|---|---|
| 01 | テストは通過。変数が未設定の run（40853980916、40859634671、40874540057）で、`route` を含むすべてのジョブが `GitHub Actions` のランナーで成功。不正な値（`invalid`）：最初の形（`a7c80b3c`、run 40878463664 の attempt 2）では `route` だけが失敗し、`provider-tests` と配布の確かめは**作られず、チェックも出なかった**（AC 不成立）。`421f80f6` で直した後の run 40891266768 の attempt 2（14:43Z）では、`route` が failure、`provider-tests` と `Provider distribution parity (ubuntu-latest)` が failure、`(macos-latest)` が cancelled（3つとも GitHub のランナーで作られ、最初の手順「Stop when route did not choose the runners」が失敗。macOS は matrix の fail-fast で取り消し）。attempt 3（変数 `local`、14:45Z）はすべて成功（`provider-tests`＝spec-dock-ci-1 241秒、Linux の配布＝spec-dock-ci-2 70秒） | run 40878463664、40891266768 の attempt 2・3 |
| 02 | 変数を `local`（12:44:33Z、利用者）にした後の run 40877741196（`e92ceb99`）で、`Provider distribution parity (ubuntu-latest)` が `spec-dock-ci-1`、`provider-tests` が `spec-dock-ci-2` で成功。`route`・macOS の配布・`validate`・`check` は GitHub のランナーで成功。両方の手元のジョブのログに `A job started hook has been configured by the self-hosted runner administrator` と `SpecDock runner admitted a same-repository pull request job` がある。VM の中の両方の `.env` にフックの2行がある | run 40877741196 のジョブ 123460877440・123460877546 |
| 03 | テストで、fork・bot・外の人・別のリポジトリ・`pull_request` 以外・読めないイベント・別の場所のイベントのファイルを拒否。VM に置いたフックを `spec-dock-runner-1` として実行し、同じリポジトリ＝許可（0）、fork＝拒否（1）、別の場所のファイル＝拒否（1）、push＝拒否（1）。実際の fork の PR は作れないので**未確認** | VM での実行（2026-10-29T10:2x Z） |
| 04 | ランナーの利用者として `sudo -n true` は失敗。`192.168.5.2:9222`（Mac の Chrome のデバッグの口）、`192.168.5.2:5432`、`192.168.0.43:6768`（Mac の LAN の IP の Orca）、`100.85.74.8:8766`（Mac の Tailscale の IP）、`169.254.169.254:80`、`192.168.5.2:22` の6つはすべて接続できず、拒否の規則の counter がちょうど6増えた。IPv6 は VM にグローバルのアドレスも経路もなく、リテラルの宛先（`[2606:4700:4700::1111]:80`）にも届かない（AC の文面の「規則の counter が増える」ではなく、経路がないことで満たした。規則は経路ができたときの守りとして残る）。`https://github.com`・`https://pypi.org` は 200。`limactl list --json` で plain=true、mounts・portForwards なし、containerd は system・user とも false。`lima-guestagent` はプロセス・実行ファイル・unit とも無い。docker・containerd・podman・nerdctl は無い | VM での実行 |
| 05 | VM に `gh` の hosts.yml・`.netrc`・`.git-credentials` は無い。秘密鍵は VM 自身の sshd のホスト鍵だけ。差分にトークンの形の文字列は無い。**登録のトークンの件**（下の Notes）を直した後、`_diag`・journal・`/var/log` にトークンの値は無い | VM での検索 |
| 06 | テストで `_tool` だけが残り、想定外の `RUNNER_TEMP` では何も消さない。VM で掃除のフックを実行し、作業場所が空になった。run 40877741196 の後、両方のランナーの `_work` は `_tool` だけで、ログに `SpecDock runner removed the job files under …/_work` がある | 同じ run |
| 07 | ジョブの無いときに `limactl stop`（10:42:41Z）→ LaunchAgent が62秒後に起動 → 2つのランナーが `Connected to GitHub`・`Listening for Jobs`、nftables も起動時に読み込み | `ensure-vm.log`、VM の journal |
| 08 | 手順書にある。リハーサル（run 40878463664、`a7c80b3c`）：2つのランナーを止めて push すると、`route` の後、手元の2つのジョブは `queued`（ラベル `self-hosted, Linux, ARM64, spec-dock-ci`、ランナーなし）で待ち、GitHub には回らなかった（13:04Z）。利用者が変数を変え、run を取り消し（attempt 1 は cancelled）、`hosted` にしてすべて再実行すると、attempt 3 で `route`・`provider-tests`・2つの配布の確かめがすべて GitHub のランナーで成功した（14:10〜14:17Z）。その後、変数は `local`（14:21:51Z）に戻した | run 40878463664 の attempt 1・3 |
| 09 | 前（09:41:33Z）と、作業の終わり（14:51:45Z）で、退去費用の LaunchAgent の plist、専用の `limactl`、`ci_vm_host_watch.py` の SHA256 と、`ci-shadow/lima.yaml` の更新時刻が同じ | |
| 10 | 利用者（統括を通して）が `all_external_contributors` を確かめた | |
| 11 | 最終品質ゲート（下）。時間の表は上 | |

手元で最初に動かした run 40875990010（`cfd6fed8`）は、振り分けとフックは正しく働いたが、VM の環境の違いで2つのジョブが失敗した。①setup-python の Python は RPATH が `/opt/hostedtoolcache/Python/3.11.18/arm64/lib` に固定で、ランナーの `_work/_tool` では `libpython3.11.so.1.0` が見つからず、環境を空にして動かすテストと `uv build` が失敗した。②Ubuntu 24.04 の git 2.43 の `git subtree split` は、作業ツリーのないクローンでは prefix がないとして止まり、移行のテストが失敗した（Mac の git 2.54 では通ることを同じ手順で確かめた）。root の持ち物の `/opt/hostedtoolcache` に Python 3.11.18（SHA256 を確認）と uv 0.13.6 を置いて `AGENT_TOOLSDIRECTORY` で指し、git を `ppa:git-core/ppa` の 2.56.0 にして直した（`e92ceb99`）。

| ジョブ | GitHub（この PR、run 40859634671） | 手元（run 40877741196） |
|---|---|---|
| `provider-tests` | 475秒 | 210秒 |
| `Provider distribution parity (ubuntu-latest)` | 114秒 | 61秒 |
| `Provider distribution parity (macos-latest)` | 169秒 | 209秒（GitHub のまま） |
| `route` | 5秒 | 5秒（GitHub のまま） |

GitHub のランナーでの時間（この PR、run 40859634671）：`route` 5秒、`provider-tests` 475秒、Linux の配布 114秒、macOS の配布 169秒。直近8回の他の PR：`provider-tests` 250〜454秒、Linux の配布 69〜119秒。

### 最終品質ゲート

- 1回目（`0c26a77e`）：`make lint` 通過、`uv run pytest` 2993 passed・8 skipped。Spec（opus/xhigh）P1 1件（P-1：root がランナーの利用者の書ける `installdependencies.sh` を実行）、P2 3件、P3 3件。Standards（sonnet/high）P0/P1 なし、P2 2件、P3 9件。
- P-1 と、同じ原因の P-2・T-1 を直した（`640781c8`：root の持ち物の展開から依存を導入、unit を root の文面で書き `svc.sh` を使わない）。VM に反映し、2つのランナーが新しい unit で `Listening for Jobs`。
- 2回目（`640781c8`）：Spec の再レビューで P-1・P-2 は fixed、新しい P0/P1 なし（P2 1件、P3 2件）。`make lint` 通過、`uv run pytest` 2994 passed・8 skipped。
- 手元の run で見つかった VM の環境の違いを直した（`e92ceb99`。Python の置き場所と git の版）。
- 3回目（`a7c80b3c`、前のゲートからの差分。その前の `cfd6fed8` と後の `a7c80b3c` の差は report.md だけ）：`make lint` 通過、`uv run pytest` 2994 passed・8 skipped。Spec（opus/xhigh）新しい P0/P1 なし（P2 2件、P3 4件）。Standards（sonnet/high、`0c26a77e` からの差分のコード）新しい P0/P1 なし（P3 5件）。R-1（`/opt/hostedtoolcache` の権限が root の umask に依存）は、VM で `/opt/hostedtoolcache` と `/opt/spec-dock-ci` に group・other の書ける項目と root 以外の持ち物が0、root の umask が 0022 であることを確かめた。
- 切り戻しのリハーサルで、変数が不正なときにチェックが出ないことが分かった（上の表の AC-454-01・08）。`provider-ci.yml` を直した（`route` の出力がなければ GitHub のランナーに戻り、最初の手順で失敗する）。
- 4回目（`421f80f6`、`a7c80b3c` からの差分）：`make lint` 通過、`uv run pytest` 2994 passed・8 skipped。Spec（opus/xhigh）新しい P0/P1 なし（P3 3件：V-1 route が出力の後に失敗した場合の記述、V-2 報告書の文、V-3 確かめの run の選び方）。Standards（sonnet/high）新しい P0/P1 なし（P3 3件：W-1 式の評価をテストしない、W-2 `if` の書き方の混在、W-3 route の失敗で macOS のランナーを1手順使う）。その後のコミットは report.md と requirement.md の AC の文だけ。

## Residual Risks / Follow-ups

- 信頼する作者の PR のコード（とその依存）は、ランナーの利用者として `.env` やランナーの本体を書き換え、開始前のフックを外せる（P-4）。差し替えたフックが同じ許可の行を出せば、ログでの検知も効かない。前提は信頼する作者を信頼すること。疑わしいときは変数を `hosted` に戻し、VM を作り直す。作り直しの周期は決めていない。
- x86_64 の Linux での確かめが、変数が `local` の間はなくなる（D1、受け入れたリスク）。
- 段階2（D7）で要ること：tart（FSL-1.1、OpenAI 著作）と softnet（root の SUID、sudo のパスワードが1回）、softnet の既定で VM から届く Mac の側の口（bridge の gateway）を止める設定、数十GB のイメージ、Apple の使用許諾（1台で2つまで）、sudo できない利用者でのランナー、macOS とランナーの更新の保守、Linux の VM と合わせたメモリ（16GB 前後）。
- 申し送り（3回目のゲート、未対応）：R-1・U-5 `guest-setup.sh` に `umask 022` と権限の検査を足す（今の VM は安全を確認済み）／R-2 root の `python3 -m pip` に `-I`／R-3・U-2 root が信頼する PyPI（uv をハッシュで固定しない）と PPA。PPA の git が apt の自動更新から外れるかの確認／R-4 手元の uv は 0.13.6 のまま（更新の手順が要る）／U-1 `mktemp` の後始末の trap／U-3 `.env` や unit を変えた後のランナーの再起動と、値を変えたときの重複行／U-4 テストの正規表現の範囲。
- 申し送り（1・2回目のゲートの P2/P3、未対応）：T-2 nftables.conf を置く前に検証する（構文エラーのファイルが残ると次の起動で遮断なし）／P-3 手順書の curl の判定（curl 8 は「Couldn't connect」としか出さないので、counter で判定する形に直す。IPv6 は github.com に AAAA が無いので、リテラルで試す）／Q-1 テストで `--no-same-owner` と `svc.sh` 不使用をより強く確かめる／Q-2 root が `.env` を grep で読む（FIFO で止められる）／T-3 壊れたキャッシュの再取得／T-4・P-6 登録と導入の再実行・作り直しの手順／T-5 `host-install.sh` の途中失敗／T-6 launchd の終了で hostagent が巻き込まれないか（実機では VM は動き続けている）／T-7 event.json とジョブの突き合わせ／T-8 シェルの振る舞いのテスト／T-9 読めないイベントの理由の文／T-10 `route` の checkout の `persist-credentials: false` と `timeout-minutes`／T-11 リポジトリ名の直書き／P-5 route のテストの追加／P-7 DNS で LAN や tailnet の名前を引ける（接続は拒否）。
- 範囲外の既存の問題（報告だけ）：`scripts/migrate-to-canonical/README.md` は「git 2.38 以上」としているが、git 2.43 の `git subtree split` は、作業ツリーのないクローン（`build-canonical` の使い捨てのクローン）で prefix がないとして止まる（VM で再現、git 2.54 と 2.56 では通る）。必要な版の下限が、書いてあるより高い可能性がある。
- route が出力を書いた後に失敗する稀な場合は、2つのジョブは route が選んだランナー（手元を含む）で作られ、最初の手順で失敗する（V-1。安全の問題はないが、そのとき VM が止まっていると最長24時間待つ）。
- 手元の時間は、Mac で同時に全体のテストを走らせていた run 40891266768（attempt 1）では `provider-tests` 293秒・Linux の配布 92秒と、ほかの回（210〜241秒、61〜70秒）より遅かった。
- 07 の証拠は、unit を root の文面に書き換える前の VM の再起動である。書き換えた後は、ランナーの再起動（12:35Z、12:57Z）で2つとも `Listening for Jobs` に戻ることを確かめたが、VM そのものの再起動はしていない。
- Lima 2.3 が正式版になったら `hostLoopback: false` を足す。
- Lima のイメージのキャッシュが `~/Library/Caches/lima/` に残る（約3.5GiB の変換済みの raw）。

## Notes

### 登録のトークンが VM の記録に残った件（2026-10-29、直した）

- 最初の `register-runner.sh` は `sudo --preserve-env=ACTIONS_RUNNER_INPUT_TOKEN` を使い、sudo が渡した環境変数の値を VM の journal と `/var/log/auth.log` に記録した。確かめのときにその行を表示したので、値は担当の会話の記録にも出た。
- 影響：登録のトークンは、このリポジトリに新しいランナーを登録することだけに使え、発行から1時間（10:37Z ごろ発行）で切れる。VM の記録はランナーの利用者には読めない。Mac の資格情報は関係しない。
- 対応：VM の該当の行を消し、journal を回して古い記録を消した。スクリプトを pipe で渡す形に直し（`0c26a77e`）、偽の値で sudo の記録に値が出ないことを VM で確かめた。期限の後（20:40 JST 以降）に、利用者がランナーの一覧を確かめ、spec-dock-ci-1（id 21）と spec-dock-ci-2（id 22）の2つだけで、どちらも online、知らないランナーは無かった（統括が確認）。
