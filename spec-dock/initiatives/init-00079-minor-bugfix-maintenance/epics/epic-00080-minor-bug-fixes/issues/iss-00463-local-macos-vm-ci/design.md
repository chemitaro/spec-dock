---
種別: 設計書（Issue）
ID: "iss-00463"
タイトル: "Run macOS CI On Local Mac Mini VM"
関連GitHub: ["#463"]
状態: "draft"
最終更新: "2026-10-30"
依存: ["requirement.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00463 Run macOS CI On Local Mac Mini VM — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

- 段階1と同じ守り（route、開始前のフック、承認制、変数での切り替え）に、macOS の配布の確かめを載せる。判定は `ci-runner-job-gate.py` の `decide` の1か所のまま。
- VM から Mac の口、LAN、tailnet に届かない制限を、VM の外（Mac の側）で行う。VM の中の root を奪われても外れない。
- ランナーは sudo できない利用者で動かし、VM の管理者にもなれないようにする。
- 段階1の申し送りを、同じスクリプトとテストで直し、両方の VM で同じ形にする。

## 選んだ案と比べた案（統括の確認待ち）

| 観点 | A：tart＋softnet（案） | B：Lima の macOS ゲスト | C：UTM などの GUI の道具 | D：Mac に直に置く |
|---|---|---|---|---|
| 使用許諾 | FSL-1.1-ALv2（OpenAI）。個人の CI は可（G1） | Apache-2.0 | Apache-2.0 など | — |
| Mac の口を止める場所 | Mac の側（softnet、`out @host`）。VM の root でも外せない（G2、G3） | VM の中の規則だけ。Lima 2.3 の `hostLoopback: false` は beta（G9） | vmnet の共有で Mac と LAN に届く。VM の中の規則だけ | 隔離なし（段階1の F3） |
| LAN・tailnet | softnet の既定で届かない | VM の中の規則 | VM の中の規則 | 届く |
| Mac の側に要るもの | tart.app と softnet（SUID root。sudo のパスワード1回） | 段階1の Lima をそのまま使える | GUI のアプリ | — |
| 成熟 | macOS の CI で広く使われる | 実験的。画面を切れない。sudo にパスワード | CLI が弱い | — |
| イメージ | vanilla（24GB の取得、50GB の疎なディスク、G6） | IPSW（約18GB）から自動で作る | IPSW から手で作る | — |

案は A。Mac の口を VM の外で止められるのは A だけで、段階1の Linux の VM（VM の中の nftables）より守りが強い。B は追加の道具が要らないが、Mac の `127.0.0.1` の口（Chrome のデバッグの口など）を VM の中の規則だけで守ることになり、VM の root を奪われると届く。

### 常に起動するか、ジョブのときだけか（案：常に起動）

- 常に起動（案）：VM のメモリ 6GiB をいつも使う（段階1の 8GiB と合わせて 14GiB）。Mac に GitHub の資格情報を置かない。段階1の D5 と同じ。
- ジョブのときだけ：待ちのジョブを知るには、Mac で GitHub の API を読む資格情報が要り（段階1の F6）、起動の約1分がジョブに足される。退去費用の仕組みはこの形だが、資格情報を常駐の処理に持たせることになる。
- ジョブごとに作り直す：登録のたびに管理者の権限のトークンが Mac に要る。P-4 の残りの改変を消せる利点はあるが、この Issue では扱わない。

### 切り替えの変数（案：macOS 用の変数を別に置く）

- 案：新しいリポジトリの変数 `SPEC_DOCK_CI_MACOS_RUNNER`（未設定か `hosted` で GitHub、`local` で手元）。macOS の VM だけが止まったときに、Linux を手元に残したまま macOS だけを GitHub に戻せる。マージの後も、利用者が `local` にするまで今と同じに動く。
- 比べた案：`SPEC_DOCK_CI_RUNNER=local` で両方を手元にする。変数が1つで済むが、マージした時点で macOS のジョブが手元を待ち、macOS の VM の故障で Linux まで戻すことになる。
- 信頼する PR の判定、承認制、開始前のフックは、段階1と同じものを使う。

## Current / Target

Current：`route` は `SPEC_DOCK_CI_RUNNER` で Linux の2つのジョブだけを手元に送る。macOS の配布の確かめは常に `macos-latest`。

Target：

```text
PR (pull_request)
  └─ route（GitHub, ubuntu-latest）
       ci-runner-job-gate.py route  ← vars.SPEC_DOCK_CI_RUNNER, vars.SPEC_DOCK_CI_MACOS_RUNNER, イベント
       runners = {"ubuntu-latest": <Linux のラベル or 名前>, "macos-latest": <macOS のラベル or 名前>}
  ├─ provider-tests                     runs-on: runners['ubuntu-latest']
  └─ Provider distribution parity (os)  runs-on: runners[matrix.os]

Mac mini
  LaunchAgent com.chemitaro.spec-dock-ci-macos-vm（KeepAlive）
    host-run-macos-vm.sh → tart run --no-graphics --net-softnet --net-softnet-block='out @host' spec-dock-ci-macos
  ~/Library/Application Support/spec-dock-ci-macos-vm/tart.app（tart 2.41.1、SHA256 を確かめる）
  /usr/local/libexec/spec-dock-ci-macos-vm/softnet（softnet 0.24.1、root:wheel 4755）
  TART_HOME=/Volumes/990p2t/vm/spec-dock-ci-tart
    └─ VM spec-dock-ci-macos（macOS 26.6.2、CPU 4、6GiB、50GB）
         DNS は 1.1.1.1 と 1.0.0.1（G4）
         admin：Mac の専用の鍵だけで SSH。パスワードは不明の乱数。自動ログインと画面共有を止める
         spec-dock-runner（標準の利用者、管理者ではない）→ LaunchDaemon com.chemitaro.spec-dock-ci-runner
         /opt/spec-dock-ci（root の持ち物）：job-started.sh、job-completed.sh、ci-runner-job-gate.py、python3 へのリンク
         /Users/runner/hostedtoolcache（root の持ち物）：Python 3.11.9 と uv（setup-python が見つける）
         git：Xcode のコマンドラインツール
```

## 責務・Interface

| 要素 | 責務 | Interface |
|---|---|---|
| `ci-runner-job-gate.py decide` | 信頼する PR かの判定（段階1と同じ）に、`GITHUB_REF` が `refs/pull/<payload の番号>/merge` であることを足す（T-7） | 理由の文字列か `None` |
| `route` | `SPEC_DOCK_CI_RUNNER` で Linux、`SPEC_DOCK_CI_MACOS_RUNNER` で macOS を選ぶ。どちらかが未知の値なら終了コード2で出力なし | `GITHUB_OUTPUT` に `runners=<JSON>` |
| `admit` | 段階1と同じ。macOS ではホームが `/Users/<利用者>` になるだけ | 終了コード0／1 |
| `provider-ci.yml` | `route` に macOS の変数を渡す。route の checkout は `persist-credentials: false`、2つのジョブに `timeout-minutes`（T-10） | ジョブの名前は今と同じ |
| `.github/runner/job-started.sh` | 両方の VM で共用。`/opt/spec-dock-ci/python3`（root の作ったリンク）を `-I` で使う。Linux は `/usr/bin/python3`、macOS は `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11` を指す。macOS の `/usr/bin/python3` は `DEVELOPER_DIR` などの環境で別の実体に向く shim なので使わない | ランナーの `.env` |
| `.github/runner/job-completed.sh` | 両方の VM で共用（段階1と同じ） | 同上 |
| `.github/runner/macos/settings.sh` | macOS の版とハッシュ（ランナー 2.338.2 の osx-arm64、Python 3.11.9、uv 0.13.6 の wheel、tart、softnet、イメージの digest）、名前、ラベル | sh で読む |
| `.github/runner/macos/host-install.sh` | Mac の側：`tools`（tart と softnet を取り、SHA256 を確かめて置く。softnet の SUID の配置は sudo の1行を表示するだけ）、`vm`（イメージを digest で clone、CPU とメモリを設定、管理の鍵を作る）、`agent`（LaunchAgent） | 引数1つ |
| `.github/runner/macos/host-run-macos-vm.sh` | LaunchAgent から呼ばれ、外付けのボリュームと VM があれば `tart run` を前面で実行する。なければ待って終わる | なし |
| `.github/runner/macos/guest-setup.sh` | VM の中の root の準備。DNS、admin の固め（鍵だけの SSH、乱数のパスワード、自動ログインと画面共有の停止）、Gatekeeper を戻す、自動の更新、コマンドラインツール、Python（pkg の署名と SHA256）、uv（wheel のハッシュ固定）、ランナーの利用者、ランナー（SHA256）、フック、LaunchDaemon、権限の検査。何度実行してもよい | `ssh admin@VM sudo sh ~/spec-dock-runner/guest-setup.sh` |
| `.github/runner/macos/register-runner.sh` | 段階1と同じ形（標準入力のトークンを pipe で渡す）。macOS では `launchctl bootstrap system` で LaunchDaemon を起動 | 標準入力1行 |

ラベルは `self-hosted, macOS, ARM64, spec-dock-ci-macos`、名前は `spec-dock-ci-macos-1`。段階1のラベル `spec-dock-ci` と退去費用の `ci-shadow` とは重ならない。

不変条件：VM に Mac のディレクトリを共有しない（`tart run` に `--dir` を付けない）。tart の guest agent を入れない。ランナーの利用者は `admin` グループに入らない。`/opt/spec-dock-ci`、`/Users/runner`、`/Library/LaunchDaemons` の項目は root の持ち物で、group と other が書けない（guest-setup の最後に検査し、外れたら失敗する。Linux も同じ、R-1）。

## 段階1の申し送りの直し方

| 記号 | 直し方 | どこに効くか |
|---|---|---|
| R-1、U-5 | `umask 022`、置き場所を `install -d -m 755` で作る、最後に権限の検査 | 両方の guest-setup |
| R-2 | root の pip を `python3 -I -m pip`、`cd /` の後で実行 | 両方 |
| R-3、U-2 | uv を wheel の SHA256 で固定（`--require-hashes --no-deps --only-binary :all:`）。PPA の git は unattended-upgrades の対象に足す（`/etc/apt/apt.conf.d/51spec-dock-git-ppa`）。PyPI と PPA を信頼することは手順書に書く | Linux（macOS は uv だけ） |
| R-4 | uv の更新の手順（settings の版とハッシュを変えて guest-setup をやり直す）を手順書に書く | 手順書 |
| U-1、T-3 | `mktemp` に trap、展開は完了の印のファイルで判定、キャッシュの SHA256 が合わなければ1回だけ取り直す | 両方 |
| U-3、Q-2 | `.env` はランナーの利用者が自分で書き換える（同じ鍵の行を消して足す）。root は `.env` を読まない。変わったら、登録済みのランナーを再起動する | 両方 |
| U-4、Q-1、T-8 | テストを、root の行が利用者のホームのファイルを実行しないことの広い検査、`--no-same-owner` の確認、スタブでの実行（登録のトークン、置き場所の検査）に直す | テスト |
| T-2 | `nft -c -f` で検証してから `/etc/nftables.conf` に置く | Linux |
| T-4、P-6 | 登録は、登録済み（`.runner` がある）のランナーを飛ばす。作り直しの手順を直す | 両方、手順書 |
| T-5 | `host-install.sh` は一時の場所に展開してから移す。親のディレクトリを作る | 両方 |
| T-6 | Linux の LaunchAgent に `AbandonProcessGroup` を足す（launchd がジョブの終わりに hostagent を巻き込まない）。macOS は tart を前面で動かすので不要 | Linux の plist |
| T-7 | `GITHUB_REF` と payload の PR の番号の突き合わせ | ゲート |
| T-9 | 読めないイベントの理由を「イベントのファイルを読めない」にする | ゲート |
| T-10 | 上の表 | ワークフロー |
| T-11 | リポジトリ名の直書きは残し、すべての場所が同じ名前であることをテストで確かめる | テスト |
| P-3 | 手順書の確かめを、nft の counter の増分と IPv6 のリテラルで判定する形にする | 手順書 |
| P-5 | route のイベント4種と読めない JSON、admit の `GITHUB_EVENT_PATH` なし、`_work` のリンク、`provider-tests` に `name:` がないことのテスト | テスト |
| P-7 | Linux は Lima の DNS のまま、手順書に「Mac の 53番に待ち受けがないことの確かめ」と残るリスクを書く。macOS は公開の DNS なので引けない | 手順書 |
| V-1 | ワークフローのコメントと手順書の記述を直す。待ちの上限（24時間）は変わらないので手順書の切り戻しで扱う | 文書 |
| Lima 2.3 | 正式版の後に `hostLoopback: false` を足す手順を手順書の保守に書く（今は入れない） | 手順書 |
| Lima のキャッシュ | `~/Library/Caches/lima` は退去費用の Lima と共用でありうるので消さない。手順書に書く | 手順書 |

## data / failure

| 失敗 | 振る舞い | 回復 |
|---|---|---|
| macOS の変数が不正 | `route` が失敗し、3つのジョブが GitHub のランナーで作られて最初の手順で失敗する（段階1と同じ形） | 変数を直し、すべてのジョブを再実行 |
| 手元の macOS のランナーが止まっている | macOS のジョブは待つ（最長24時間） | VM を直す。または macOS の変数を `hosted` にし、run を取り消して、すべてのジョブを再実行 |
| softnet が使えない（SUID が外れた、版が合わない） | `tart run` が失敗し、LaunchAgent が繰り返す。VM は動かない（softnet なしでは起動しない） | softnet を置き直す |
| 外付けのボリュームがない | `host-run-macos-vm.sh` は待つと記録して終了0。launchd が間をあけて呼び直す | 次の回に起こす |
| VM の中の自動の更新で再起動 | VM の中で macOS が再起動し、LaunchDaemon がランナーを起こす。`tart run` は動き続ける | なし |
| 古いイベントのファイルが残る | `GITHUB_REF` の番号と合わなければ拒否（T-7） | なし |

## 変更対象

- 変える：`.github/scripts/ci-runner-job-gate.py`、`.github/workflows/provider-ci.yml`、`.github/runner/`（共用のフック、Linux の申し送りの直し、`macos/` を新規）、`tests/integration/test_issue454_runner_gate.py`（申し送りのテスト）、`tests/integration/test_issue463_runner_scripts.py`（新規。共用のシェルの関数、登録、Mac の側の導入を実行で確かめる）、`tests/integration/test_issue463_macos_runner.py`（新規）、`.github/runner/lib.sh`（新規。両方の VM で共用のシェルの関数）、`docs/ci.md`、`docs/ci-local-runner.md`。
- 変えない：`ci.yml`、`commit-identity.yml`、`release-tag.yml`、製品のコード（`src/`）、同梱の資産、退去費用の環境。

## 移行・互換性・rollback

- 移行：PR を push（macOS の変数は未設定なので今と同じ）→ 段階1の申し送りを段階1の VM に反映（`SPEC_DOCK_CI_RUNNER` を `hosted` にしてから、終わったら `local`）→ 利用者の環境の段階2 → 隔離とフックの確かめ → macOS の変数を `local` → この PR の CI を手元で確かめる → 切り戻しのリハーサル → 人がマージ。
- 互換性：チェックの名前は変わらない。`SPEC_DOCK_CI_RUNNER` の意味は変わらない。`job-started.sh` の Python の指し先が変わるので、段階1の VM でも guest-setup をやり直してリンクを作る（やり直す前に新しい `job-started.sh` が置かれることはない。どちらも guest-setup が置く）。
- rollback：macOS の変数を `hosted` にする。さらに戻すときは、この PR を revert する。環境の戻し方は手順書に書く（ランナーの削除、LaunchAgent の削除、`tart delete`、`TART_HOME` の削除、softnet と tart の削除）。

## testability

- 振り分けと判定：`tests/integration/test_issue463_macos_runner.py` が、変数の組み合わせ、`GITHUB_REF` の突き合わせを、スクリプトを別のプロセスで動かして確かめる。
- シェル：登録のスクリプトを、`sudo`・`config.sh`・`launchctl`／`systemctl` のスタブで実行し、トークンが引数に出ないことを確かめる。置き場所の検査、`.env` の書き換え（重複しない）、キャッシュの取り直しを、一時のディレクトリで実行して確かめる（Mac の上の pytest で動く部分だけ。GNU の `stat` に依存する部分は関数に切り出してスタブする）。
- 実機：VM の中でランナーの利用者として、sudo、管理者になれないこと、Mac と LAN と Tailscale への接続、IPv6、インターネット、フックの判定を確かめる。Mac で `ps` の softnet の引数を見る。PR の実際のジョブのランナーの名前と時間を GitHub の API で読む。

## risk

- softnet は Mac の上の SUID root の実行ファイルで、Mac の攻撃面が増える。OpenAI の公開のソースと release の SHA256 で確かめ、root の持ち物の場所に置く。版の更新は手で行う。
- イメージは Cirrus Labs（OpenAI）の作ったもので、digest で固定する。中の `admin` は guest-setup で固めるまで既定のパスワードである。最初の起動から固めるまでの間も、VM は Mac 以外から届かない（vmnet の NAT と softnet）。
- 信頼する作者のコードの改変が後のジョブに残る（段階1の P-4 と同じ）。
- macOS の VM の自動の更新が、ジョブの途中で VM を再起動しうる。その run は失敗し、再実行で回復する。
- Xcode のコマンドラインツールの git は GitHub の macOS（Homebrew の git）と版が違う。
- メモリ：2つの VM で 14GiB。Mac の利用と重なると遅くなりうる。測って報告書に書く。
