# 手元のMac miniのランナー

Provider CIの重いジョブは、利用者のMac miniの上のVMで動かせます。`provider-tests` と `Provider distribution parity (ubuntu-latest)` はLinux VM（段階1）、`Provider distribution parity (macos-latest)` はmacOS VM（段階2）です。切り替えはリポジトリの変数で、Linuxは `SPEC_DOCK_CI_RUNNER`、macOSは `SPEC_DOCK_CI_MACOS_RUNNER` です。どちらも未設定か `hosted` ならGitHubのランナー、`local` なら手元のランナーで、互いに独立です。`validate`、`check`、`release-tag` は常にGitHubのランナーで動きます。仕様は [iss-00454](../spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00454-local-mac-runner-ci/requirement.md)（Linux）と [iss-00463](../spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00463-local-macos-vm-ci/requirement.md)（macOS と共通の直し）が正本です。

この文書の「構成」から「撤去」まではLinux VMの手順です。macOS VMは末尾の「macOS VM（段階2）」にまとめます。開始前と後のフック、信頼の判定、`route`、作り直しの方針は共通です。

## 安全の仕組み

SpecDockは公開リポジトリです。forkのPRはワークフローを書き換えて手元のランナーを指せるため、次の三つを重ねます。

1. `route` ジョブ（GitHubのランナー）が、同じリポジトリから人が出し、作者が `OWNER`・`MEMBER`・`COLLABORATOR` のPRだけを手元に振り分けます。
2. ランナーの開始前フック `/opt/spec-dock-ci/job-started.sh` が、同じ条件を満たさないジョブを最初のステップの前に失敗させます。判定はランナーが決まった場所に書いたイベントだけを読むので、信頼しないPRがワークフローを書き換えても外せません。
3. リポジトリの設定で、外部の人のforkのPRのワークフローは承認が必要です（`all_external_contributors`）。

VMはMacのファイルを共有せず（Limaの `plain: true`、mountなし、ポート転送なし、guest agentなし）、ランナーの利用者はsudoできません。VMの中のnftablesが、Mac（`192.168.5.2`。plainモードではDNSの53番だけを許可）、LAN、Tailscale、リンクローカル、IPv6への新しい接続を拒否します。VMにMacの `gh` の認証、SSHの秘密鍵、キーチェーンを入れません。VMの中の資格情報は、ランナー自身の登録情報だけです。

信頼する作者のPRのコードは、ランナーの利用者として、VMの中のランナーの設定（フックを指す `.env` を含む）を変えられ、その変更は後のジョブにも残ります。権限を与える人を信頼する運用が前提です。手元のジョブのログの `Set up runner` に `SpecDock runner admitted a same-repository pull request job` が毎回出ることを確かめ、出ない場合や疑わしい場合は変数を `hosted` に戻し、VMを作り直します。VMにはdockerなどのcontainerの実行環境を入れません。

## 構成

| 要素 | 場所 |
|---|---|
| Lima 2.2.1（専用） | `~/Library/Application Support/spec-dock-ci-vm/lima/` |
| VM `spec-dock-ci` | `LIMA_HOME=/Volumes/990p2t/vm/spec-dock-ci-lima`、設定は [.github/runner/spec-dock-ci.lima.yaml](../.github/runner/spec-dock-ci.lima.yaml) |
| LaunchAgent | `~/Library/LaunchAgents/com.chemitaro.spec-dock-ci-vm.plist`。ログインと5分ごとに、止まったVMを起動するだけ |
| LaunchAgentのログ | `~/Library/Application Support/spec-dock-ci-vm/ensure-vm.log`、`ensure-vm.err` |
| ランナー | VMの中の `spec-dock-runner-1`・`-2` 利用者。名前 `spec-dock-ci-1`・`-2`、ラベル `self-hosted, Linux, ARM64, spec-dock-ci`。systemdで常駐 |
| フック | VMの中の `/opt/spec-dock-ci/`（[.github/runner/](../.github/runner/) からコピー） |
| ツール | VMの中の `/opt/hostedtoolcache`（rootの持ち物）にPython 3.11とuvを置き、ランナーの `AGENT_TOOLSDIRECTORY` で指す。setup-pythonのPythonは、GitHubのランナーと同じこの場所でしか `libpython` を見つけられないため。gitは、GitHubのUbuntuのイメージと同じく `ppa:git-core/ppa` から入れる（Ubuntu 24.04の2.43の `git subtree` は、作業ツリーのないクローンで split できない） |

退去費用のVM `ci-shadow`、そのLima、そのLaunchAgentとは別のものです。互いに変更しません。

以下の例では、次の二つを前提にします。

```bash
export LIMA_HOME=/Volumes/990p2t/vm/spec-dock-ci-lima
limactl() { "$HOME/Library/Application Support/spec-dock-ci-vm/lima/bin/limactl" "$@"; }
```

## 導入

リポジトリのルートで実行します。利用者の環境を変える操作なので、利用者の承認を得てから行います。

```bash
sh .github/runner/host-install.sh lima
mkdir -p "$LIMA_HOME"
limactl create --name spec-dock-ci .github/runner/spec-dock-ci.lima.yaml
limactl start spec-dock-ci
limactl shell spec-dock-ci -- mkdir -p -m 700 spec-dock-runner
limactl copy .github/runner/*.sh .github/runner/nftables.conf .github/scripts/ci-runner-job-gate.py spec-dock-ci:spec-dock-runner/
limactl shell spec-dock-ci -- sh -c 'chmod 644 ~/spec-dock-runner/*'
limactl shell spec-dock-ci -- sudo sh spec-dock-runner/guest-setup.sh
```

ファイルはLimaの利用者のホーム（ランナーの利用者が書けない場所）に置きます。`guest-setup.sh` は、置き場所が他の人に書けると実行を拒否します。何度実行してもよく、登録済みのランナーの `.env` か systemd の unit が変わったときは、そのランナーを再起動します。最後に `/opt/spec-dock-ci` と `/opt/hostedtoolcache` に、root 以外の持ち物や group・other の書ける項目がないことを確かめ、あれば失敗します。

登録はリポジトリの管理者の認証で行います。トークンは標準入力でVMへ渡し、ファイルや引数に残しません。`register-runner.sh` は登録済みのランナーを飛ばすので、途中で失敗したときはそのままやり直せます（すべて登録済みならトークンは要りません）。

```bash
gh api -X POST repos/chemitaro/spec-dock/actions/runners/registration-token --jq .token \
  | limactl shell spec-dock-ci sudo /opt/spec-dock-ci/register-runner.sh
sh .github/runner/host-install.sh agent
gh api repos/chemitaro/spec-dock/actions/permissions/fork-pr-contributor-approval
gh api -X PUT repos/chemitaro/spec-dock/actions/permissions/fork-pr-contributor-approval \
  -f approval_policy=all_external_contributors
```

## 確かめ

VMの中で、ランナーの利用者として確かめます。接続の拒否は、Macで実際に待ち受けている口に対して試します（待ち受けていない口では、拒否の規則がなくても失敗するためです）。Macで `lsof -nP -iTCP -sTCP:LISTEN` を見て、`127.0.0.1` の口、全体（`*`）の口、TailscaleのIPの口を一つずつ選び、下の `LOOPBACK_PORT` などに入れます。

curl の出力は、規則で拒否されても経路がなくても「Couldn't connect to server」なので、判定は拒否の規則の counter の増え方で行います。一つの宛先ごとに、試す前と後の counter を比べます。

```bash
count() {
  limactl shell spec-dock-ci -- sudo nft list chain inet spec_dock_egress output \
    | awk '{ for (i = 1; i < NF; i++) if ($i == "packets") total += $(i + 1) } END { print total + 0 }'
}
limactl shell spec-dock-ci -- sudo -u spec-dock-runner-1 sh -c 'sudo -n true 2>/dev/null && echo "NG: sudo" || echo "ok: no sudo"'
for target in http://192.168.5.2:LOOPBACK_PORT http://MAC_LAN_IP:ANY_PORT http://MAC_TAILSCALE_IP:TAILSCALE_PORT \
  http://169.254.169.254:80 'http://[2606:4700:4700::1111]:80'; do
  before=$(count)
  limactl shell spec-dock-ci -- sudo -u spec-dock-runner-1 curl -sS -m 5 -o /dev/null "$target" 2>/dev/null \
    && echo "NG: $target answered"
  [ "$(count)" -gt "$before" ] && echo "ok: $target refused by the rules" || echo "check: $target was not counted"
done
limactl shell spec-dock-ci -- ip -6 route show default   # 何も出なければ、IPv6はcounterの前に経路がなくて失敗する
limactl shell spec-dock-ci -- sudo -u spec-dock-runner-1 curl -sS -m 10 -o /dev/null -w "github %{http_code}\n" https://github.com
limactl list --json spec-dock-ci   # mountsとportForwardsが空
limactl shell spec-dock-ci -- sh -c 'pgrep -l lima-guestagent; command -v docker containerd podman; true'   # 何も出ない
lsof -nP -iTCP:53 -iUDP:53   # Macで。127.0.0.1:53 に待ち受けがないこと（VMのDNSはLimaが自分で受ける）
```

IPv4 の宛先は「ok」になります。IPv6 は、VM にIPv6の経路がない間は counter が増えず「check」になり、そのときは `ip -6 route show default` が空であることで確かめます（経路ができたら、規則が拒否して counter が増えます）。

VM の DNS は Lima の DNS（`192.168.5.2` の53番）で、Mac のリゾルバーで名前を引きます。そのため、VM から LAN や tailnet の名前を引けます（接続は規則で拒否されます）。これは残るリスクです。

開始前フックは、forkのイベントで失敗し、同じリポジトリのイベントで成功することを確かめます。イベントは、ランナーが書く場所に置きます。

```bash
limactl shell spec-dock-ci -- sudo -u spec-dock-runner-1 sh -c '
  dir=$HOME/actions-runner/_work/_temp/_github_workflow; mkdir -p "$dir"
  for head in chemitaro/spec-dock someone/spec-dock; do
    printf "%s" "{\"repository\":{\"full_name\":\"chemitaro/spec-dock\"},\"sender\":{\"type\":\"User\"},\"pull_request\":{\"number\":1,\"author_association\":\"OWNER\",\"user\":{\"type\":\"User\"},\"head\":{\"repo\":{\"full_name\":\"$head\"}},\"base\":{\"repo\":{\"full_name\":\"chemitaro/spec-dock\"}}}}" > "$dir/event.json"
    GITHUB_EVENT_NAME=pull_request GITHUB_EVENT_PATH=$dir/event.json GITHUB_REPOSITORY=chemitaro/spec-dock \
      GITHUB_REF=refs/pull/1/merge /opt/spec-dock-ci/job-started.sh; echo "head=$head exit=$?"
  done
  rm -rf "$HOME/actions-runner/_work/_temp"'
```

切り替えはリポジトリの管理者が行います。

```bash
gh variable set SPEC_DOCK_CI_RUNNER --repo chemitaro/spec-dock --body local
```

この変数は、新しい `provider-ci.yml` を持つPRのrunにだけ効きます。PRのジョブの `runner_name` が `spec-dock-ci-1` か `spec-dock-ci-2` であることを、run のジョブ一覧で確かめます。

## 手元が止まったとき

手元に振り分けたジョブは、ランナーが戻るまで待ちます（GitHubの上限は24時間）。自動でGitHubへは戻しません。

1. LaunchAgentのログと `limactl list` でVMの状態を確かめ、直せるならVMを起動します。ランナーはVMの起動で待ち受けに戻ります。
2. すぐにGitHubで動かす場合は、変数を戻します。

   ```bash
   gh variable set SPEC_DOCK_CI_RUNNER --repo chemitaro/spec-dock --body hosted
   ```

3. 対象のrunを取り消し、取り消しが終わってから、**すべてのジョブ**を再実行します。失敗したジョブだけの再実行では `route` が再評価されず、同じ手元のランナーを待ちます。取り消しの途中（`status` が `completed` になる前）の再実行は拒否されます。

   ```bash
   gh run cancel RUN_ID --repo chemitaro/spec-dock
   gh run view RUN_ID --repo chemitaro/spec-dock --json status --jq .status   # completed になるまで待つ
   gh run rerun RUN_ID --repo chemitaro/spec-dock
   ```

`route` が出力を書いた後に失敗するという稀な場合も、ジョブは `route` の選んだ手元のランナーを待ちます。同じ手順で回復します。

## 保守

- ランナーはGitHubの自動更新で新しい版になります。古いままだとジョブを受けられなくなります。
- VMのapt自動更新は続けます。`ppa:git-core/ppa` の git も自動更新の対象に入れています（`/etc/apt/apt.conf.d/51spec-dock-git-ppa`）。needrestartの設定で、ランナーのサービスだけを自動の再起動から外しています。
- VMの中のrootが信頼するものは、Ubuntuのアーカイブ、`ppa:git-core/ppa`（Launchpadの署名）、GitHubのrelease（ランナーとPython。SHA256を固定）、`files.pythonhosted.org` の uv の wheel（SHA256を固定。PyPIでの版の解決はしない）です。
- uv の版を上げるときは、PyPIの `https://pypi.org/pypi/uv/<版>/json` から Linux aarch64 の wheel の URL と SHA256 を読み、`.github/runner/settings.sh` の `UV_VERSION`、`UV_WHEEL_URL`、`UV_WHEEL_SHA256` を変えて、「導入」のコピーと `guest-setup.sh` をやり直します（変数を `hosted` にしてから）。Python の版も同じ形で上げます。
- Lima 2.3 が正式版になったら、`host-install.sh` の `LIMA_VERSION` を上げ（前の `~/Library/Application Support/spec-dock-ci-vm/lima` を消してから `lima` をやり直す）、`spec-dock-ci.lima.yaml` に `hostLoopback: false` を足して VM を作り直します。VM から Mac の `127.0.0.1` に届く経路を、VM の外で止められます。
- Lima のイメージのキャッシュ（`~/Library/Caches/lima`、約3.5GiB）は、退去費用の Lima と共用でありうるので、まとめて消しません。

## 作り直しの方針

段階1（このLinux VM）と段階2（macOS VM）で共通です。

- 普段の更新は、VMの中の自動の更新に任せます。
- Ubuntu、macOS、GitHub Actions のランナーの大きな版の更新のときに、VMを作り直します。
- 信頼する作者のPRのコードは、ランナーの利用者の権限でランナーの設定を書き換えられ、その改変は後のジョブに残ります。手元のジョブのログに許可の行が出ないなど、疑わしいことがあれば、変数を `hosted` に戻し、VMを作り直します。

Linux VM を作り直す手順：

1. 変数を `hosted` にし、手元のジョブがないことを確かめます。
2. GitHubのSettings → Actions → Runnersで `spec-dock-ci-1`・`-2` を削除します。
3. `limactl stop spec-dock-ci`、`limactl delete -f spec-dock-ci` を実行します（LaunchAgent は VM がない間は待つだけです）。
4. 「導入」の `mkdir -p "$LIMA_HOME"` 以降と登録をやり直します（`host-install.sh lima` と `agent` は不要です）。「確かめ」の後に変数を `local` に戻します。

## 撤去

1. 変数を `hosted` にするか削除します（`gh variable delete SPEC_DOCK_CI_RUNNER --repo chemitaro/spec-dock`）。
2. GitHubのSettings → Actions → Runnersで `spec-dock-ci-1`・`-2` を削除します。
3. LaunchAgentを止めて削除します。

   ```bash
   launchctl bootout "gui/$(id -u)/com.chemitaro.spec-dock-ci-vm"
   rm ~/Library/LaunchAgents/com.chemitaro.spec-dock-ci-vm.plist
   ```

4. VMとLimaを削除します（`limactl delete -f spec-dock-ci`、`$LIMA_HOME`、`~/Library/Application Support/spec-dock-ci-vm/`）。
5. forkのPRの承認の設定を、導入の前に読んだ値に戻すかを決めます。

## macOS VM（段階2）

### 違い

| 観点 | Linux VM | macOS VM |
|---|---|---|
| 道具 | 専用の Lima 2.2.1 | tart 2.41.1 と softnet 0.24.1（どちらも FSL-1.1-ALv2、OpenAI。Homebrew を使わない） |
| Mac・LAN・tailnet を止める場所 | VM の中の nftables（VM の root なら外せる） | Mac の側の softnet。`--net-softnet-block='out @host'` で Mac の側の口への新しい接続を止め、LAN・CGNAT（Tailscale）・リンクローカル・IPv6 は softnet の既定で届かない。VM の root でも外せない |
| DNS | Lima の DNS（Mac のリゾルバー） | 公開の DNS（1.1.1.1、1.0.0.1）。Mac の側の口を止めるので Mac の DNS は使えず、LAN や tailnet の名前も引けない |
| イメージ | Ubuntu の cloud image（digest 固定） | `ghcr.io/cirruslabs/macos-tahoe-vanilla`（digest 固定、macOS 26.6.2、取得 24GB、ディスク 50GB の疎なファイル） |
| ランナー | `spec-dock-runner-1`・`-2`（systemd） | `spec-dock-runner` 1つ（root の書いた LaunchDaemon `com.chemitaro.spec-dock-ci-runner-1`）。名前 `spec-dock-ci-macos-1`、ラベル `self-hosted, macOS, ARM64, spec-dock-ci-macos` |
| ツール | `/opt/hostedtoolcache` の Python 3.11.18 と uv | `/Users/runner/hostedtoolcache` の Python 3.11.9（Python.org の署名つきの pkg）と uv。git は Xcode のコマンドラインツール |
| 常駐 | LaunchAgent が5分ごとに止まった VM を起こす | LaunchAgent が `tart run` を前面で動かし続ける（KeepAlive） |
| 資源 | CPU 6、8GiB、40GiB | CPU 4、6GiB、50GB |

VM の管理者 `admin` は、Mac の専用の鍵（`~/Library/Application Support/spec-dock-ci-macos-vm/ssh/`）だけで SSH でき、パスワードは誰も知らない乱数です。パスワードの SSH、自動ログイン、画面共有は止め、Gatekeeper を戻します。ランナーの利用者は管理者のグループに入らず、SSH もできません。tart の guest agent は入れず、Mac のディレクトリも共有しません。

macOS VM の中の root が信頼するものは、Apple のソフトウェア・アップデート（コマンドラインツール）、GitHub の release（ランナーと Python。SHA256 を固定）、Python Software Foundation の pkg の署名、Python の `setup.sh` が入れる pip と certifi（PyPI）、`files.pythonhosted.org` の uv の wheel（SHA256 を固定）です。

以下の例では、次の三つを前提にします。

```bash
export TART_HOME=/Volumes/990p2t/vm/spec-dock-ci-tart
tart() { "$HOME/Library/Application Support/spec-dock-ci-macos-vm/tart.app/Contents/MacOS/tart" "$@"; }
vm() { sh .github/runner/macos/host-ssh.sh "$@"; }
```

### 導入

リポジトリのルートで、利用者の承認を得てから、この順に実行します。Mac の sudo は2行目の1回だけです。

```bash
sh .github/runner/macos/host-install.sh tools   # tart と softnet を取り、SHA256 を確かめて置く
sudo install -d -o root -g wheel -m 755 /usr/local/libexec/spec-dock-ci-macos-vm && sudo install -o root -g wheel -m 4755 "$HOME/Library/Application Support/spec-dock-ci-macos-vm/softnet" /usr/local/libexec/spec-dock-ci-macos-vm/softnet
sh .github/runner/macos/host-install.sh vm      # イメージを取り（24GB）、CPU とメモリを決め、管理の鍵を作る
sh .github/runner/macos/host-install.sh agent   # LaunchAgent。ここで VM が起動する
sh .github/runner/macos/host-install.sh key     # 最初の1回だけ、イメージの admin のパスワードで鍵を置く
sh .github/runner/macos/host-install.sh guest   # VM の中に置いて guest-setup.sh を実行する
```

softnet の SUID は、所有者の権限が無効な `/Volumes/990p2t` では効かないので、内蔵のディスクに置きます。`host-run-macos-vm.sh` は softnet が root の SUID でなければ VM を起動しません（softnet なしの既定の NAT では、VM から Mac と LAN に届くため）。

登録はリポジトリの管理者の認証で行います。トークンは標準入力で VM へ渡します。

```bash
gh api -X POST repos/chemitaro/spec-dock/actions/runners/registration-token --jq .token \
  | sh .github/runner/macos/host-ssh.sh sudo /opt/spec-dock-ci/register-runner.sh
```

### 確かめ

Mac で、softnet が規則つきで動いていることを見ます。

```bash
ps -axo command | grep -E '[s]oftnet .*--block out @host'
```

VM の中で、ランナーの利用者として確かめます。Mac で `lsof -nP -iTCP -sTCP:LISTEN` を見て、全体（`*`）の口と Tailscale の IP の口を選びます。VM から見た Mac の側の口（gateway）は、VM の中の `route -n get default` の `gateway` です。

```bash
vm 'sudo -u spec-dock-runner sh -c "
  sudo -n true 2>/dev/null && echo NG: sudo || echo ok: no sudo
  id -Gn | tr \" \" \"\\n\" | grep -q -x admin && echo NG: admin || echo ok: not admin
  for target in http://GATEWAY:ANY_PORT http://MAC_LAN_IP:ANY_PORT http://MAC_TAILSCALE_IP:TAILSCALE_PORT \
    http://169.254.169.254:80 \"http://[2606:4700:4700::1111]:80\"; do
    curl -sS -m 5 -o /dev/null \"\$target\" 2>/dev/null && echo \"NG: \$target\" || echo \"ok: \$target\"
  done
  curl -sS -m 10 -o /dev/null -w \"github %{http_code}\\n\" https://github.com"'
tart get spec-dock-ci-macos   # CPU 4、メモリ 6144
vm 'pgrep -l tart-guest-agent; ls /etc/kcpassword 2>&1; true'   # agent は無く、kcpassword も無い
```

softnet は宛先で止めるので、curl は待ち受けている口でも届きません（counter はありません。止めているのは Mac の側です）。VM の root でも外せないことは、`vm sudo route -n add -host MAC_LAN_IP GATEWAY` のように経路を足してから同じ curl を試して確かめ、`vm sudo route -n delete -host MAC_LAN_IP` で戻します。

開始前フックは、Linux と同じイベントで確かめます（`limactl shell spec-dock-ci -- sudo -u spec-dock-runner-1` を `vm sudo -u spec-dock-runner` に読み替え、`$HOME` は `/Users/spec-dock-runner`）。

切り替えはリポジトリの管理者が行います。

```bash
gh variable set SPEC_DOCK_CI_MACOS_RUNNER --repo chemitaro/spec-dock --body local
```

PR の macOS のジョブの `runner_name` が `spec-dock-ci-macos-1` であることを確かめます。

### 手元の macOS が止まったとき

macOS のジョブは、ランナーが戻るまで待ちます。LaunchAgent のログ（`~/Library/Application Support/spec-dock-ci-macos-vm/run-vm.log`、`run-vm.err`）と `tart list` で状態を見ます。すぐに GitHub で動かすときは、macOS の変数だけを戻し、Linux と同じく run を取り消してからすべてのジョブを再実行します。

```bash
gh variable set SPEC_DOCK_CI_MACOS_RUNNER --repo chemitaro/spec-dock --body hosted
```

### 保守

- VM の中の macOS の更新は、自動の更新に任せます（再起動の後、LaunchDaemon がランナーを起こします）。ジョブの途中で再起動した run は、再実行で回復します。
- macOS の大きな版、ランナーの大きな版のときは、VM を作り直します。
- tart と softnet を上げるときは、`.github/runner/macos/settings.sh` の版と SHA256（GitHub の release の digest）を変え、LaunchAgent を止めてから `~/Library/Application Support/spec-dock-ci-macos-vm/{tart.app,softnet}` を消して `tools` と softnet の sudo の行をやり直し、LaunchAgent を戻します。
- イメージを上げるときは、`IMAGE` の digest を変えて VM を作り直します。古いイメージのキャッシュは `tart list` で名前を確かめてから `tart prune --entries=caches` で消します。
- Python と uv は、Linux と同じ形で `settings.sh` の値を変えて `guest` をやり直します。

macOS VM を作り直す手順：

1. `SPEC_DOCK_CI_MACOS_RUNNER` を `hosted` にし、手元のジョブがないことを確かめます。
2. GitHub の Settings → Actions → Runners で `spec-dock-ci-macos-1` を削除します。
3. `launchctl bootout "gui/$(id -u)/com.chemitaro.spec-dock-ci-macos-vm"`、`tart delete spec-dock-ci-macos` を実行します。
4. `rm ~/Library/LaunchAgents/com.chemitaro.spec-dock-ci-macos-vm.plist ~/Library/Application\ Support/spec-dock-ci-macos-vm/ssh/known_hosts` の後、「導入」の `vm` 以降と登録をやり直します（`tools` と sudo の行は不要）。「確かめ」の後に変数を `local` に戻します。

### 撤去

1. `SPEC_DOCK_CI_MACOS_RUNNER` を `hosted` にするか削除します。
2. GitHub の Settings → Actions → Runners で `spec-dock-ci-macos-1` を削除します。
3. `launchctl bootout "gui/$(id -u)/com.chemitaro.spec-dock-ci-macos-vm"` と、その plist を消します。
4. `tart delete spec-dock-ci-macos`、`/Volumes/990p2t/vm/spec-dock-ci-tart`、`~/Library/Application Support/spec-dock-ci-macos-vm/` を消します。
5. `sudo rm -r /usr/local/libexec/spec-dock-ci-macos-vm` で softnet を消します。
