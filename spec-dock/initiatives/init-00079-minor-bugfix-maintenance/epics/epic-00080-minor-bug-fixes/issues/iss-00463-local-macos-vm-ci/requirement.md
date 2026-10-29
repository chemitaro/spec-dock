---
種別: 要件定義書（Issue）
ID: "iss-00463"
タイトル: "Run macOS CI On Local Mac Mini VM"
関連GitHub: ["#463"]
状態: "draft"
最終更新: "2026-10-30"
親: ["epic-00080", "init-00079"]
---

# iss-00463 Run macOS CI On Local Mac Mini VM — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

表示名：macOS の配布の確かめを、手元の Mac mini の macOS の仮想マシンで動かす（iss-00454 の段階2）

> 背景と「決めること」は、統括が iss-00454 の報告書と利用者の決定（2026-10-29）から書いた。「調べた事実」以降は、実装担当が調べた事実をもとに書いた。「合意した判断」は、統括を通して利用者に確かめたものだけを書く。

## 目的

iss-00454（段階1）で、Provider CI の重いジョブのうち Linux のものは、手元の Mac mini の Linux の仮想マシン `spec-dock-ci` で動くようになった。この Issue では、残りの macOS の配布の確かめ（`Provider distribution parity (macos-latest)`、GitHub で約2.5〜4.5分）も、手元の macOS の仮想マシンで動かす。あわせて、段階1の申し送り（安全と保守の細かい直し）を片付ける。

## 背景

- 利用者の方針（2026-10-26）：「なるべく手元の仮想マシンで動かす。1分以内のジョブは GitHub に残してもよい」。macOS の確かめは1分を超えるので、手元に移す対象である。
- 利用者の決定（2026-10-29）：macOS の仮想マシンは、段階1とは別の Issue にする（この Issue）。段階1の細かい申し送りも、この Issue にまとめる。
- 段階1の設計、手順書、スクリプト、決定は、`iss-00454-local-mac-runner-ci` の `requirement.md`、`design.md`、`report.md` と、`.github/runner/` にある。

## 段階1の担当が調べて分かったこと（iss-00454 の報告書、G5 と D7）

- 候補の tart は FSL-1.1 の使用許諾である（OpenAI 著作。個人の CI は許可の範囲）。
- ホストを守る softnet は、root の SUID を付ける。sudo のパスワードを1回入力する必要がある。
- softnet の既定では、仮想マシンから Mac の側の口（bridge の gateway）に届く。別に止める設定が要る。
- 基本のイメージは数十GB である（Lima の macOS 27 の IPSW だけで約18GB）。
- Apple の使用許諾では、1台の Mac で動かせる macOS の仮想マシンは2つまでである。
- tart の基本のイメージは、sudo できる管理者の利用者を持つ。sudo できない利用者でランナーを動かすように、作り直す必要がある。
- macOS とランナーの更新の保守が、Linux の仮想マシンとは別に増える。
- Linux の仮想マシンと合わせると、メモリを16GB 前後使う（Mac mini は 32GB）。

## 調べた事実（2026-10-30。公開の文書とソースと、読むだけのコマンド）

- G1（使用許諾）：tart 2.41.1 と softnet 0.24.1 の LICENSE は、どちらも FSL-1.1-ALv2、著作者は OpenAI。禁止は「他者に商用の製品やサービスとして提供して競合する使い方」だけで、個人の CI は許可の範囲。公開から2年後に Apache-2.0 になる。
- G2（softnet の規則）：softnet 0.24.1 のソース（`lib/proxy/vm.rs`、`rules.rs`）では、VM が始める IPv4 の通信は、利用者の規則（最長一致、同じ範囲なら block が勝つ）→ 合わなければ「グローバルなアドレスなら許可」→「bridge の gateway（Mac の側の口）なら許可」→ それ以外は破棄、の順で決まる。LAN（192.168.0.0/16 など）、CGNAT の範囲（100.64.0.0/10。Tailscale）、リンクローカル、マルチキャストは既定で届かない。IPv4 と ARP 以外（IPv6 を含む）は通さない。規則は IP の範囲だけで、口の番号では書けない。
- G3（Mac の側の口を止める規則）：`--net-softnet-block='out @host'`（softnet 0.22.0 以降の向きつきの規則）は、VM から Mac の側の口への新しい接続だけを止め、Mac から VM への SSH の返りは通す（`test_directional_egress_block_does_not_block_reply_to_unmatched_inbound_flow`）。向きのない `@host` は返りも止めるので使わない。
- G4（DNS）：softnet は DHCP で gateway を DNS として配り、`.internal` 以外の問い合わせは gateway への通常の通信として規則に従う。G3 で gateway を止めると、DNS は VM の中で公開の DNS（例：1.1.1.1）を指す必要がある。その結果、VM から LAN や tailnet の名前は引けない。
- G5（softnet の権限）：softnet は vmnet の口と DHCP の設定のために root で始まり、そのあと呼んだ利用者に権限を落とす。SUID か、パスワードなしの sudo が要る。`/Volumes/990p2t` は所有者の権限が無効（段階1の F3）なので、SUID のファイルは内蔵のディスクに置く。
- G6（イメージ）：`ghcr.io/cirruslabs/macos-tahoe-vanilla`（2026-10-30 の digest `sha256:eeec54bfe1f076e27786c5d92b89187a05b1d109b5071eb2dcdf02d596e34640`）は、取得が約24.0GB、ディスクは50GB（疎なファイル）。macOS 26.6.2。中身は、利用者 `admin`（パスワード `admin`、パスワードなしの sudo）、自動ログイン、画面共有、SSH、Gatekeeper の無効化だけで、Homebrew や tart の guest agent は無い（`templates/vanilla-tahoe.pkr.hcl`）。base のイメージ（26.4GB）は Homebrew、gitlab-runner、buildkite-agent などを足し、`/Users/runner` を `admin` のホームへのリンクにするので使わない。
- G7（GitHub の macOS）：直近の成功した run 40911949638 の macOS の配布の確かめは、`macos-26-arm64` のイメージ、CPython 3.11.9、Homebrew の git 2.56.0 で、pytest は159秒。配布の確かめのテストが使う外部のコマンドは `git` と `uv` だけ。
- G8（setup-python の macOS）：macOS の Python は `/Users/runner/hostedtoolcache` にしか置けない（作り直しできない形）。`actions/python-versions` の macOS の 3.11 は 3.11.9 が最後で、中身は Python Software Foundation の署名と Apple の公証つきの pkg（`/Library/Frameworks` に入る）。tar の SHA256 は `8039644e…7bbeff`（公開の `hashes.sha256` と一致）。
- G9（Lima の macOS ゲスト）：Lima 2.1 以降で「実験的」。画面を切れない。sudo はパスワードが要り、変えられない。Mac の口（192.168.5.2）を止めるのは VM の中の規則だけで、`hostLoopback: false` の Lima 2.3 は 2026-10-30 時点で beta（2.3.0-beta.1）。
- G10（ホスト）：Mac mini は Apple M4（10コア）、メモリ 32GB、macOS 27.2。内蔵のディスクの空きは84GiB、`/Volumes/990p2t` の空きは1.1TiB。tart と softnet は入っていない。段階1の VM は CPU 6、8GiB。

## 決めること（実装担当が調べて案を出し、統括を通して利用者に確かめる）

決定は「合意した判断」に記録する。実装担当の案は [design.md](design.md) の「選んだ案と比べた案」にある。

- 仮想マシンの道具（tart か、ほかか）と、ホストを守るネットワークの設定。
- 仮想マシンを常に起動するか、ジョブのときだけ起こすか（メモリの使い方）。
- fork などの PR の扱いと、切り替えの変数は、段階1と同じ仕組み（route、開始前のフック、`SPEC_DOCK_CI_RUNNER`）を使うか。
- 利用者の操作が要る手順（sudo のパスワード、ランナーの登録）。

## 合意した判断

（統括の返事の後に書く。）

## 仮想マシンを作り直す方針（利用者の決定、2026-10-29）

- 普段の更新は、仮想マシンの中の自動の更新に任せる。
- Ubuntu、macOS、GitHub Actions のランナーの大きな版の更新のときに、仮想マシンを作り直す。
- 信頼する作者の PR のコードが、ランナーの利用者の権限でランナーの設定を書き換えうる（iss-00454 の報告書の P-4）。疑わしいことがあれば、変数を `hosted` に戻し、仮想マシンを作り直す。
- この方針を、段階1と段階2の手順書に書く。

## 段階1から引き継ぐ申し送り（iss-00454 の報告書。この Issue で直す）

- `guest-setup.sh` に `umask 022` と権限の検査を足す（R-1、U-5）。root の `python3 -m pip` に `-I` を付ける（R-2）。
- root が信頼する PyPI（uv をハッシュで固定していない）と PPA の扱い。PPA の git が apt の自動更新から外れるかを確かめる（R-3、U-2）。手元の uv の更新の手順（R-4）。
- `mktemp` の後始末の trap（U-1）。`.env` や unit を変えた後のランナーの再起動と、値を変えたときの重複行（U-3）。テストの正規表現の範囲（U-4）。
- `nftables.conf` を置く前に検証する（T-2。構文エラーのファイルが残ると、次の起動で通信の制限がなくなる）。
- 手順書の curl の判定を、counter で判定する形に直す。IPv6 はリテラルで試す（P-3）。
- テストで `--no-same-owner` と `svc.sh` を使わないことを、より強く確かめる（Q-1）。root が `.env` を grep で読むこと（Q-2）。
- 壊れたキャッシュの再取得（T-3）。登録と導入の再実行と、作り直しの手順（T-4、P-6）。`host-install.sh` の途中の失敗（T-5）。launchd の終了で hostagent が巻き込まれないか（T-6）。
- event.json とジョブの突き合わせ（T-7）。シェルの振る舞いのテスト（T-8）。読めないイベントの理由の文（T-9）。
- route の checkout の `persist-credentials: false` と `timeout-minutes`（T-10）。リポジトリ名の直書き（T-11）。route のテストの追加（P-5）。DNS で LAN や tailnet の名前を引けること（P-7。接続は拒否されている）。
- route が出力を書いた後に失敗する稀な場合に、仮想マシンが止まっていると最長24時間待つこと（V-1）。
- Lima 2.3 が正式版になったら `hostLoopback: false` を足す。Lima のイメージのキャッシュ（約3.5GiB）の扱い。

## 観測可能な要件

- RQ-463-01：macOS の切り替えの変数が未設定か `hosted` のとき、`Provider distribution parity (macos-latest)` は今と同じ GitHub のランナーで動く。チェックの名前は変わらない。Linux の2つのジョブは、今と同じく `SPEC_DOCK_CI_RUNNER` だけで決まる。
- RQ-463-02：macOS の切り替えの変数が `local` で、PR が段階1と同じ「信頼する同じリポジトリの PR」のとき、`Provider distribution parity (macos-latest)` は手元の macOS の VM のランナーで動き、通る。ジョブのログに開始前のフックの許可の行が残る。
- RQ-463-03：fork、bot、外の人の PR と、`pull_request` 以外のイベントは、振り分けで GitHub に残る。ワークフローを書き換えて手元の macOS のランナーを指しても、開始前のフックがジョブを手順の前に失敗にする。前のジョブのイベントのファイルが残っていても、今のジョブのものでなければ許可しない（T-7）。
- RQ-463-04：変数が `hosted`・`local` 以外の値なら、振り分けは失敗し、手元に送りうるジョブは「スキップ」ではなく失敗になる。
- RQ-463-05：macOS の VM は Mac のファイルを共有せず、Mac とクリップボードや guest agent でつながらない。ランナーの利用者は sudo できず、管理者のグループに入らず、管理者の利用者にもなれない（パスワードを知らない）。VM から、Mac の側の口（どの口番号でも）、LAN、Tailscale、リンクローカル、IPv6 への新しい接続は届かず、公開の DNS とインターネットには届く。この制限は Mac の側で行い、VM の中の root でも外せない。
- RQ-463-06：Mac の資格情報（`gh` の認証、SSH の秘密鍵、キーチェーン）は VM、ジョブ、リポジトリに入らない。VM にある GitHub の資格情報は、ランナー自身の登録の情報だけである。登録のトークンは、ファイル、引数、ログに残さない。Mac から VM の管理者に入る鍵は、この VM のためだけに作り、Mac の外に出さない。
- RQ-463-07：手元の macOS のジョブが終わると、そのランナーの作業場所には、ツールのキャッシュ（`_tool`）だけが残る。
- RQ-463-08：Mac に利用者がログインしている間、macOS の VM が止まると、Mac の LaunchAgent が5分以内に起こし、ランナーは VM の起動で自動で待ち受けに戻る。
- RQ-463-09：手元の macOS が止まったときは、macOS の変数を `hosted` に戻し、run を取り消してからすべてのジョブを再実行すると、macOS のジョブが GitHub のランナーで動く。手順は文書にある。
- RQ-463-10：退去費用のリポジトリ、`ci-shadow`、そのランナー、その LaunchAgent、その Lima は変わらない。段階1の VM、ランナー、LaunchAgent は、`SPEC_DOCK_CI_RUNNER` を `hosted` にしている間だけ変える。
- RQ-463-11：段階1の申し送り（上の一覧）は、直したか、直さない理由と残るリスクを報告書に書いたかの、どちらかである。
- RQ-463-12：作り直しの方針が、段階1と段階2の手順書にある。

## スコープ

- 対象：Provider CI の振り分け（macOS）、開始前と終わりのフック（両方の VM で共用）、macOS の VM の作り方と VM の中の設定、ランナーの登録、Mac の側の導入（tart、softnet、LaunchAgent）、テスト、CI の文書と手順書、利用者の環境の段階2、段階1の申し送りの直しと、その段階1の VM への反映。
- 対象外：`ci.yml`・`commit-identity.yml`・`release-tag.yml` のランナー、退去費用の環境、`~/.claude/settings.json`、`~/.codex/config.toml`、自動の切り戻し、Lima 2.3 の導入（正式版になってから。手順書に書く）、ジョブごとに VM を作り直す仕組み（ジョブごとの登録に管理者の資格情報が Mac に要るため）。

## 失敗・境界条件

- 手元の macOS のランナーが止まっていると、手元に振り分けた macOS のジョブは待つ（GitHub の上限は24時間）。自動で GitHub に戻さない。RQ-463-09 の切り戻しで回復する。
- 失敗したジョブだけの再実行では、振り分けのジョブは再評価されない。変数を変えた後は、すべてのジョブを再実行する。
- 開始前のフックの判定に使うのは、ランナーが決まった場所に書いたイベントと既定の変数だけである。PR が変えられるファイルは判定に使わない。
- 信頼する作者の PR のコードは、ランナーの利用者として、ランナーの設定を書き換えられ、その改変は後のジョブにも残る。疑わしいときは変数を `hosted` に戻して VM を作り直す。
- 家の公開の IP を経由した Mac への経路は扱わない（段階1と同じ）。公開の IP はグローバルなアドレスなので、softnet は通す。
- 外付けのボリュームがないとき、LaunchAgent は VM を起こさずに待つ。
- Apple の使用許諾（1台で2つまで）の範囲で、macOS の VM は1つだけ動かす。
- macOS の VM の中の Python と git は、GitHub の macOS と同じ版にそろえるとは限らない（Python 3.11.9 は同じ。git は Xcode のコマンドラインツールのもの）。版の違いで落ちたテストは、原因を報告書に書く。

## 受け入れ条件

- AC-463-01（RQ-463-01、04）：振り分けのテストで、macOS の変数が未設定・空・`hosted` なら `macos-latest`、`local` で信頼する PR なら手元の macOS のラベル、未知の値なら失敗（終了コード2、出力なし）になる。Linux の振り分けのテストは今と同じ結果である。ワークフローのテストで、チェックの名前が変わらない。両方の変数が未設定の状態で、この Issue の PR の CI が GitHub のランナーで通る。
- AC-463-02（RQ-463-02）：macOS の変数を `local` にした後、この Issue の PR の `Provider distribution parity (macos-latest)` のジョブのランナーの名前が `spec-dock-ci-macos-1` で、成功する。ログに `SpecDock runner admitted a same-repository pull request job` が出る。時間を GitHub の時間と並べて報告書に書く。
- AC-463-03（RQ-463-03）：テストで、fork、bot、外の人、別のリポジトリ、`pull_request` 以外のイベント、読めないイベント、別の場所のイベントのファイル、`GITHUB_REF` が payload の PR の番号と合わないイベントを、フックが拒否し、振り分けが GitHub に残す。macOS の VM の中に置いたフックを、ランナーの利用者として、fork の PR のイベントで実行すると失敗し、同じリポジトリの PR のイベントで成功する。
- AC-463-04（RQ-463-05）：VM の設定（`tart get`）で共有のディレクトリがなく、VM に tart の guest agent が無い。VM の中でランナーの利用者として、`sudo -n true` が失敗し、管理者のグループに入っていない。Mac が待ち受けている口（VM から見た Mac の側の口、Mac の LAN の IP、Mac の Tailscale の IP）、リンクローカル、IPv6 のリテラルへの接続が失敗し、`https://github.com` に届く。VM の中の root で経路や DNS を変えても、Mac の側の口に届かない（softnet の規則は VM の外にある）。Mac で、softnet の動いている引数に `--block out @host` があることを確かめる。
- AC-463-05（RQ-463-06）：VM の中に `gh` の認証のファイルと、Mac の SSH の秘密鍵がない。登録のスクリプトがトークンを標準入力から pipe で渡すことを、テストで（スタブを使って実行で）確かめる。ランナーの記録と VM の記録（`_diag`、`/var/log`、統一ログの `sudo`）にトークンが出ない。リポジトリの差分に、トークンと秘密情報がない。
- AC-463-06（RQ-463-07）：実際の手元の macOS のジョブの後に、作業場所が `_tool` だけである。フックのテストで、`_work` がシンボリックリンクのときに何も消さずに失敗する。
- AC-463-07（RQ-463-08）：ジョブのないときに VM を止めると、5分以内に LaunchAgent が起こし、ランナーが GitHub で online に戻る。
- AC-463-08（RQ-463-09）：切り戻しの手順が手順書にある。macOS のランナーを止めて手元のジョブが待つことを確かめ、手順どおりに切り戻して、再実行の macOS のジョブが GitHub のランナーで動くことを確かめる。
- AC-463-09（RQ-463-10）：退去費用の LaunchAgent の plist、その専用の `limactl`、その監視のスクリプトの SHA256 と、`ci-shadow` の `lima.yaml` の更新時刻が、作業の前後で同じである。段階1の VM、ランナー、LaunchAgent を変えたときの、変数を `hosted` にした時刻と `local` に戻した時刻を報告書に書く。
- AC-463-10（RQ-463-11）：申し送りの一覧の各項目に、直したコミットと確かめ（テストか実機）、または直さない理由が報告書にある。段階1の VM に反映した項目は、VM で確かめた結果がある。
- AC-463-11（RQ-463-12）：両方の手順書に作り直しの方針がある。
- AC-463-12（横断）：`make lint` と `uv run pytest` が通る。

## 制約・前提

- 段階1の仮想マシン `spec-dock-ci`、そのランナー、LaunchAgent は、CI が止まらないように変える。変えるときは、変数を `hosted` に戻してから行い、終わったら `local` に戻す。
- 退去費用のリポジトリ、その仮想マシン `ci-shadow`、そのランナー、その LaunchAgent は変えない。
- 利用者の環境を変える手順は、一覧（コマンド、変えるファイル、戻し方）を統括に示し、利用者の承認を得てから行う。利用者が実行するコマンドは、統括がクリップボードに入れて、1つずつ実行してもらう。
- 資格情報を、仮想マシン、ジョブ、リポジトリに写さない。秘密情報をコミットしない。
- 今の CI の確かめ（lint、全体のテスト、両方の OS の配布の確かめ、仕様の検査、コミットの作者の確かめ、版のタグ）は、どれも落とさない。
