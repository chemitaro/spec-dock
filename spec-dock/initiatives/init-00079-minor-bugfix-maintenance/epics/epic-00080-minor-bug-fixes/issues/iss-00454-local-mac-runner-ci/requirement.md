---
種別: 要件定義書（Issue）
ID: "iss-00454"
タイトル: "Run Spec Dock CI On Local Mac Mini Runner"
関連GitHub: ["#454"]
状態: "draft"
最終更新: "2026-10-29"
親: ["epic-00080", "init-00079"]
---

# iss-00454 Run Spec Dock CI On Local Mac Mini Runner — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

表示名：spec-dock の CI を、手元の Mac mini のランナーで動かす

> 背景と「決めること」は、統括が利用者の依頼（2026-10-26）から書いた。合意した判断以降は、実装担当が調べた事実と利用者の判断をもとに固めた。

## 目的

spec-dock の GitHub Actions のジョブを、GitHub がホストするランナーではなく、利用者の Mac mini の上のランナー（self-hosted runner）で動かす。

## 背景

- 今は、すべてのワークフロー（`ci.yml`、`provider-ci.yml`、`commit-identity.yml`、`release-tag.yml` など）が `runs-on: ubuntu-latest` か `macos-latest` で、GitHub のランナーで動いている（2026-10-26 に、ジョブのランナーの名前とグループで確かめた）。
- 利用者は、退去費用のリポジトリ（`chemitaro/taikyohiyou_project`、非公開）で、すでに Mac mini のランナーを使っている。同じように、spec-dock も手元で動かしたい。
- 退去費用の仕組み（読むだけで確かめた。`/Volumes/990p2t/workspace/product/taikyohiyou_project/docs/runbooks/ci-vm-runner-operations.md`）：
  - Mac mini の上の Lima/VZ の Linux ARM64 の仮想マシン `ci-shadow` が、リポジトリ専用のランナー `ci-shadow-linux-arm64`（ラベル `[self-hosted, Linux, ARM64, ci-shadow]`）を動かす。
  - Mac の LaunchAgent `com.taikyohiyou.ci-vm-watch` が、ジョブがあるときだけ仮想マシンを起こし、なくなれば止める。
  - ワークフローの門番（gatekeeper）が、同じリポジトリから、書き込み権限のある人が出した PR だけを手元のランナーに送り、fork や bot の PR は GitHub のランナーで動かす。
  - 一部のジョブ（外部の GCP を使うもの、frontend など）は、GitHub のランナーに残している。

## 大事な違い（安全）

- **spec-dock は公開のリポジトリである**（退去費用は非公開）。公開のリポジトリで手元のランナーを使うと、だれでも fork から PR を出せるので、その PR のコードが Mac mini の上で動くおそれがある。GitHub も、公開のリポジトリで self-hosted runner を使うことを勧めていない。
- そのため、手元のランナーでは、信頼できる PR と push（同じリポジトリの、書き込み権限のある人のもの）だけを動かし、fork などは GitHub のランナーで動かすか、動かさない仕組みが要る。Mac mini の資格情報（`gh` の認証など）や、利用者のファイルに、ジョブから届かないようにする。

## 決めること（実装担当が調べて案を出し、統括を通して利用者に確かめる）

決定は「合意した判断」に記録した。

- どのジョブを手元で動かすか（すべてか、一部か）。`provider-ci.yml` は Linux（`ubuntu-latest`）と macOS（`macos-latest`）の両方で配布を確かめている。spec-dock は Linux と macOS の両方に対応するので、両方の確かめを残す方法（macOS は Mac mini 自身、Linux は仮想マシン、など）。
- ランナーをどこで動かすか（Mac mini の macOS に直に置くか、退去費用と同じく仮想マシンの中か）。退去費用の仮想マシンとランナーは、退去費用の持ち物なので、そのまま共用してよいかも決める（GitHub の個人のアカウントのランナーは、リポジトリごとに登録する）。
- fork などの PR の扱い（GitHub のランナーに回す、承認が要るようにする、動かさない）。
- 手元のランナーが止まっているときの扱い（待つか、GitHub のランナーに回すか）。

## 調べた事実（2026-10-26〜29）

- F1：公開のリポジトリでは、GitHub の標準のランナーは無料である。手元で動かしても費用は減らない。
- F2：GitHub は、公開のリポジトリで self-hosted runner を使うことを勧めていない。`pull_request` のワークフローは PR 側のファイルで動くので、fork の PR がワークフローを書き換えて手元のランナーを指せる。ワークフローの中の振り分けだけでは防げない。
- F3：`/Volumes/990p2t` は所有者の権限が無効である。Mac に直にランナーを置くと、別の macOS の利用者にしても、このボリュームを読み書きできる。
- F4：Lima の既定のネットワークでは、VM から `192.168.5.2` で Mac の `127.0.0.1` に届く。これを止める `hostLoopback: false` は Lima 2.3（2026-10-29 時点で beta）からである。
- F5：ランナーの開始前のフック（`ACTIONS_RUNNER_HOOK_JOB_STARTED`）が失敗すると、ジョブは手順に入る前に失敗する。ランナー側の設定なので、PR がワークフローを書き換えても外せない。
- F6：`GITHUB_TOKEN` では、ランナーが動いているかを API で見られない。自動で GitHub のランナーに戻すには、管理者の権限の PAT を秘密情報に置く必要がある。
- F7：Lima の `plain: true` は、共有の mount、ポート転送、containerd、guest agent をまとめて止める（Lima 2.2.1）。
- F8：GitHub のランナーでの時間（直近8回の成功、2026-10-29 に計測）：`provider-tests` 250〜454秒、Linux の配布の確かめ 69〜119秒、macOS の配布の確かめ 145〜268秒。`validate` と `check` は約10秒。
- F9：macOS の VM には、ホストを守る仕組み（tart の softnet）に root の SUID が要り、softnet の既定では VM から Mac の側の口に届く。イメージは数十GB、Apple の使用許諾は1台で2つまで、macOS とランナーの更新の保守が増える。

## 合意した判断（利用者、2026-10-26。統括を通して確認）

利用者の方針：「なるべくローカルの VM で動作するようにする。1分以内のジョブは GitHub の環境に残してもよい」。F1 と F2 は、利用者に伝えたうえでの判断である。

- D0：進める。
- D1：1分を超えるジョブを手元で動かす。`provider-tests` と、配布の確かめの Linux を、手元の Linux の VM（ARM64）で動かす。x86_64 の Linux での確かめがなくなることは、利用者が受け入れたリスクとする。配布の確かめの macOS も手元で動かす方向とし、macOS の VM は段階2とする。1分以内のジョブ（`ci.yml` の `validate`、`commit-identity.yml` の `check`、振り分けのジョブ）と、書き込みの権限が要る `release-tag` は GitHub に残す。
- D2：spec-dock 専用の新しい Lima/VZ の Linux ARM64 の VM。共有の mount なし、ポート転送なし、sudo なしのランナーの利用者、VM の中の nftables で Mac、LAN、Tailscale への接続を止める。資格情報を入れない。退去費用の `ci-shadow` は共用しない。
- D3：三重にする。①ワークフローの振り分けのジョブ、②ランナー側の開始前のフック、③リポジトリの設定で外の人の fork の PR を承認制にする（③は利用者の操作）。
- D4：リポジトリの変数 `SPEC_DOCK_CI_RUNNER` で切り替える。未設定か `hosted` なら GitHub、`local` なら手元。手元が止まっているときは、ジョブは待つ。利用者が変数を `hosted` に戻して、ジョブを再実行する。自動では戻さない（F6）。
- D5：VM は常に起動しておく。Mac の LaunchAgent が止まった VM を起こし、VM の中では systemd でランナーを常駐させる。ジョブの後に作業場所を消すフックを置く。
- D6：Lima の正式版（2.2.1）と、VM の中の nftables で Mac への接続を止める。
- 追加：切り替えの前後で、`provider-tests` と Linux の配布の確かめの時間を測り、GitHub の時間と並べて報告書に書く。遅くても、方針どおり手元で動かす。
- D7（利用者、2026-10-29。統括を通して確認）：段階2（macOS の VM）はこの Issue では作らない。macOS の配布の確かめは GitHub に残す。段階2の Issue は統括が後で作り、この Issue の報告書に、段階2で要ること（F9）を申し送る。
- D8（利用者、2026-10-29。統括を通して確認）：1つの VM（CPU 6、メモリ 8GiB）の中に、別々の sudo なしの利用者のランナーを2つ置く。1つの PR の2つの手元のジョブが並んで動く。
- D9（利用者、2026-10-29。統括を通して確認）：利用者の環境を変える手順 S1〜S7 を承認した。S1・S2・S3・S5 は実装担当が行う。ランナーの登録（S4）、fork の PR の承認の設定（S6）、変数の切り替え（S7）は、実装担当が示したコマンドを利用者が実行し、結果を確かめてから次へ進む。S6 は変える前の値を報告書に残す。

## 観測可能な要件

- RQ-454-01：変数 `SPEC_DOCK_CI_RUNNER` が未設定か `hosted` のとき、Provider CI の今のジョブはすべて今と同じ GitHub のランナーで動き、チェックの名前は変わらない。振り分けのチェック `route` が1つ増える。
- RQ-454-02：変数が `local` で、PR が同じリポジトリの、作者と送り手が人（`User`）、作者の関係が `OWNER`・`MEMBER`・`COLLABORATOR` の PR のとき、`provider-tests` と `Provider distribution parity (ubuntu-latest)` は手元のランナーで動く。そのジョブのログに、開始前のフックが許可した記録が残る。`Provider distribution parity (macos-latest)`（D7）、`validate`、`check`、`release-tag` は GitHub のランナーで動く。
- RQ-454-03：fork、bot、外の人の PR と、`pull_request` 以外のイベントは、振り分けで GitHub のランナーに残る。ワークフローを書き換えて手元のランナーを指しても、開始前のフックがジョブを手順の前に失敗にする。外の人の fork の PR のワークフローは、承認があるまで始まらない（D3 ③）。
- RQ-454-04：変数が `hosted`・`local` 以外の値なら、振り分けは失敗し、`provider-tests` と配布の確かめは「スキップ」ではなく失敗になる。
- RQ-454-05：VM は Mac のファイルを共有せず、VM の口を Mac に転送しない。ランナーの利用者は sudo できず、管理のグループに入らない。VM から、Mac、LAN、Tailscale、リンクローカル、IPv6 への新しい接続は、相手が待ち受けていても拒否され、DNS とインターネットには届く。
- RQ-454-06：Mac の資格情報（`gh` の認証、SSH の秘密鍵、キーチェーン）は VM、ジョブ、リポジトリに入らない。VM にある資格情報は、ランナー自身の登録の情報だけである。登録のトークンは、ファイル、引数、ログに残さない。
- RQ-454-07：手元のジョブが終わると、そのランナーの作業場所には、ツールのキャッシュ（`_tool`）だけが残る。
- RQ-454-08：Mac に利用者がログインしている間、VM が止まると Mac の LaunchAgent が5分以内に起こし、ランナーは VM の起動で自動で待ち受けに戻る。
- RQ-454-09：手元が止まったときは、変数を `hosted` に戻し、run を取り消してからすべてのジョブを再実行すると、GitHub のランナーで動く。手順は文書にある。
- RQ-454-10：退去費用のリポジトリ、`ci-shadow`、そのランナー、その LaunchAgent、その Lima は変わらない。

## スコープ

- 対象：Provider CI の振り分け、手元のランナーのゲートとフック、VM の設定と VM の中の設定、ランナーの登録、Mac の側の導入と LaunchAgent、テスト、CI の文書と手元のランナーの手順書、利用者の環境の段階1（Lima、VM、ランナーの登録、LaunchAgent、承認の設定、変数）。
- 対象外：段階2（macOS の VM、D7）、`ci.yml`・`commit-identity.yml`・`release-tag.yml` のランナー、退去費用の環境（F4 の件を含む）、`~/.claude/settings.json`、`~/.codex/config.toml`、Homebrew、自動の切り戻し。

## 失敗・境界条件

- 手元のランナーが止まっていると、手元に振り分けたジョブは待つ（GitHub の上限は24時間）。自動で GitHub に戻さない。VM は動いていてランナーだけが止まった場合、Mac の再起動の後に利用者がログインしていない場合、VM が壊れた場合も同じで、RQ-454-09 の切り戻しで回復する。
- 失敗したジョブだけの再実行では、振り分けのジョブは再評価されない。変数を変えた後は、すべてのジョブを再実行する。
- 開始前のフックの判定に使うのは、ランナーが書いたイベントの内容と既定の変数だけである。ジョブがイベントのファイルを別の場所に向けたら拒否する。PR が変えられるファイルは判定に使わない。
- 信頼する作者の PR のコードは、ランナーの利用者として、ランナーの設定（フックを指す設定を含む）を書き換えられ、その改変は後のジョブにも残る。信頼する作者を信頼することが前提であり、疑わしいときは変数を `hosted` に戻して VM を作り直す。
- ランナーの利用者のホームのキャッシュ（uv、pip など）はジョブをまたいで残る。
- LAN は私用の範囲のアドレスであることを前提にする。家の公開の IP を経由した Mac への経路は扱わない。
- 外付けのボリュームがまだないとき、LaunchAgent は何もせずに次の回を待つ。

## 受け入れ条件

- AC-454-01（RQ-454-01、04）：振り分けのテストで、未設定・空・`hosted` はすべて GitHub、未知の値は失敗（終了コード2、出力なし）になる。ワークフローのテストで、2つのジョブが振り分けの結果に依存し、振り分けが失敗しても実行される（スキップされない）形で、チェックの名前が変わらない。変数が未設定の状態で、この Issue の PR の CI が GitHub のランナーで通る。マージの前に変数を未知の値にした run で、`provider-tests` と2つの配布の確かめが作られて成功しない（conclusion が failure。matrix の fail-fast で取り消された配布の確かめは cancelled でもよい。どちらも成功ではなく、素通りしない）。
- AC-454-02（RQ-454-02）：変数を `local` にした後、この Issue の PR の `provider-tests` と `Provider distribution parity (ubuntu-latest)` のジョブのランナーの名前が `spec-dock-ci-1` か `spec-dock-ci-2`（D8）で、すべてのチェックが成功する。両方のランナーのジョブのログに `SpecDock runner admitted a same-repository pull request job` が出る。
- AC-454-03（RQ-454-03）：テストで、fork、bot、外の人、別のリポジトリ、`pull_request` 以外のイベント、読めないイベント、別の場所のイベントのファイルを、フックが拒否し、振り分けが GitHub に残す。VM の中に置いたフックを、ランナーの利用者として、fork の PR のイベントで実行すると失敗し、同じリポジトリの PR のイベントで成功する。実際の fork の PR での確かめは、作れなければ「未確認」と書く。
- AC-454-04（RQ-454-05）：VM に共有の mount とポート転送がなく、guest agent と container の実行環境（docker など）が動いていない。VM の中でランナーの利用者として、`sudo -n true` が失敗し、Mac が待ち受けている口（VM から見た Mac、Mac の LAN の IP、Mac の Tailscale の IP）、リンクローカル、IPv6 への接続が、VM の拒否の規則で拒否され（規則の数え上げが増える）、`https://github.com` に届く。
- AC-454-05（RQ-454-06）：VM の中に `gh` の認証のファイルと、Mac の SSH の秘密鍵がない。登録のスクリプトがトークンを標準入力と環境変数で渡すことをテストで確かめ、ランナーの記録（`_diag`、journal）にトークンが出ない。リポジトリの差分に、トークンと秘密情報がない。
- AC-454-06（RQ-454-07）：フックのテストで、作業場所に `_tool` だけが残り、想定外の場所では何も消さずに失敗する。実際の手元のジョブの後に、作業場所を確かめる。
- AC-454-07（RQ-454-08）：ジョブのないときに VM を止めると、5分以内に LaunchAgent が起こし、ランナーが GitHub で online に戻る。
- AC-454-08（RQ-454-09）：切り戻しの手順が手順書にある。マージの前（変数がこの PR にしか効かない間）に、ランナーを止めて手元のジョブが待つことを確かめ、手順どおりに切り戻して、再実行のジョブが GitHub のランナーで動くことを確かめる。
- AC-454-09（RQ-454-10）：退去費用の LaunchAgent の plist、その専用の Lima の `limactl`、その監視のスクリプトの SHA256 と、`ci-shadow` の `lima.yaml` の更新時刻が、作業の前後で同じである。
- AC-454-10（RQ-454-03）：リポジトリの設定の fork の PR の承認が `all_external_contributors` である（利用者が確かめる）。
- AC-454-11（RQ-454-01〜10 の横断、合意の「追加」）：`make lint` と `uv run pytest` が通る。報告書に、GitHub と手元の時間を並べる。

## 制約・前提

- 退去費用のリポジトリ、その仮想マシン、そのランナー、その LaunchAgent は、利用者の確認なしに変えない。読むのはよい。
- 利用者の環境（`~/Library/LaunchAgents/`、仮想マシン、ランナーの登録、GitHub のリポジトリの設定）を変える手順は、計画を示して利用者が認めてから行う。ランナーの登録のトークンの発行、リポジトリの変数と設定は、利用者の操作である（手元の `gh` の PAT では 403）。
- 資格情報を、ジョブ、仮想マシン、コンテナ、リポジトリに写さない。秘密情報をコミットしない。
- 今の CI の確かめ（lint、全体のテスト、両方の OS の配布の確かめ、仕様の検査、コミットの作者の確かめ、版のタグ）は、どれも落とさない。
- Epic #424 の PR の CI を止めない。変数は、新しい `provider-ci.yml` を持つ PR だけに効く。
