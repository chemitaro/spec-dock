# 手元のMac miniのランナー

Provider CIの重いジョブ（`provider-tests` と `Provider distribution parity (ubuntu-latest)`）は、利用者のMac miniの上のLinux VMで動かせます。切り替えはリポジトリの変数 `SPEC_DOCK_CI_RUNNER` で行い、未設定か `hosted` ならGitHubのランナー、`local` なら手元のランナーです。macOSの配布チェック、`validate`、`check`、`release-tag` は常にGitHubのランナーで動きます。仕様は [iss-00454](https://github.com/chemitaro/spec-dock/issues/454) が正本です。

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

ファイルはLimaの利用者のホーム（ランナーの利用者が書けない場所）に置きます。`guest-setup.sh` は、置き場所が他の人に書けると実行を拒否します。登録の後に `guest-setup.sh` をやり直した場合は、`sudo systemctl restart 'actions.runner.chemitaro-spec-dock.*'` でランナーを読み直させます。

登録はリポジトリの管理者の認証で行います。トークンは標準入力でVMへ渡し、ファイルや引数に残しません。

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

```bash
limactl shell spec-dock-ci -- sudo nft list chain inet spec_dock_egress output   # counterの前の値
limactl shell spec-dock-ci -- sudo -u spec-dock-runner-1 sh -c '
  sudo -n true 2>/dev/null && echo "NG: sudo" || echo "ok: no sudo"
  for target in 192.168.5.2:LOOPBACK_PORT MAC_LAN_IP:ANY_PORT MAC_TAILSCALE_IP:TAILSCALE_PORT 169.254.169.254:80; do
    curl -sS -m 5 "http://$target" -o /dev/null 2>&1 | grep -q "No route to host" && echo "ok: $target refused" || echo "NG: $target"
  done
  curl -sS -m 5 -6 https://github.com -o /dev/null 2>&1 | grep -q -E "No route to host|Network is unreachable|Could not resolve" && echo "ok: IPv6 refused" || echo "NG: IPv6"
  curl -sS -m 10 -o /dev/null -w "github %{http_code}\n" https://github.com'
limactl shell spec-dock-ci -- sudo nft list chain inet spec_dock_egress output   # counterが増えたこと
limactl list --json spec-dock-ci   # mountsとportForwardsが空
limactl shell spec-dock-ci -- sh -c 'pgrep -l lima-guestagent; command -v docker containerd podman; true'   # 何も出ない
```

開始前フックは、forkのイベントで失敗し、同じリポジトリのイベントで成功することを確かめます。イベントは、ランナーが書く場所に置きます。

```bash
limactl shell spec-dock-ci -- sudo -u spec-dock-runner-1 sh -c '
  dir=$HOME/actions-runner/_work/_temp/_github_workflow; mkdir -p "$dir"
  for head in chemitaro/spec-dock someone/spec-dock; do
    printf "%s" "{\"repository\":{\"full_name\":\"chemitaro/spec-dock\"},\"sender\":{\"type\":\"User\"},\"pull_request\":{\"author_association\":\"OWNER\",\"user\":{\"type\":\"User\"},\"head\":{\"repo\":{\"full_name\":\"$head\"}},\"base\":{\"repo\":{\"full_name\":\"chemitaro/spec-dock\"}}}}" > "$dir/event.json"
    GITHUB_EVENT_NAME=pull_request GITHUB_EVENT_PATH=$dir/event.json GITHUB_REPOSITORY=chemitaro/spec-dock \
      /opt/spec-dock-ci/job-started.sh; echo "head=$head exit=$?"
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

3. 対象のrunを取り消し、**すべてのジョブ**を再実行します。失敗したジョブだけの再実行では `route` が再評価されず、同じ手元のランナーを待ちます。

   ```bash
   gh run cancel RUN_ID --repo chemitaro/spec-dock
   gh run rerun RUN_ID --repo chemitaro/spec-dock
   ```

## 保守

- ランナーはGitHubの自動更新で新しい版になります。古いままだとジョブを受けられなくなります。
- VMのapt自動更新は続けます。needrestartの設定で、ランナーのサービスだけを自動の再起動から外しています。
- VMを作り直すときは、ジョブがないことを確かめてから、GitHubのSettings → Actions → Runnersで二つのランナーを削除し、`limactl delete -f spec-dock-ci` の後に「導入」をやり直します。

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
