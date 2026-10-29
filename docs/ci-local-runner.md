# 手元のMac miniのランナー

Provider CIの重いジョブ（`provider-tests` と `Provider distribution parity (ubuntu-latest)`）は、利用者のMac miniの上のLinux VMで動かせます。切り替えはリポジトリの変数 `SPEC_DOCK_CI_RUNNER` で行い、未設定か `hosted` ならGitHubのランナー、`local` なら手元のランナーです。macOSの配布チェック、`validate`、`check`、`release-tag` は常にGitHubのランナーで動きます。仕様は [iss-00454](../spec-dock/initiatives/init-00079-minor-bugfix-maintenance/epics/epic-00080-minor-bug-fixes/issues/iss-00454-local-mac-runner-ci/requirement.md) が正本です。

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
