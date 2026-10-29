---
種別: 設計書（Issue）
ID: "iss-00454"
タイトル: "Run Spec Dock CI On Local Mac Mini Runner"
関連GitHub: ["#454"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00454 Run Spec Dock CI On Local Mac Mini Runner — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

- 信頼する同じリポジトリの PR の重いジョブだけを手元の VM に送り、それ以外は今と同じに GitHub で動かす。
- 振り分けを PR に書き換えられても、手元で知らないコードが動かないようにする（ランナー側で止める）。
- VM から Mac のファイル、資格情報、Mac の口、LAN に届かないようにする。
- 切り替えと切り戻しを、リポジトリの変数1つで行う。最初の PR は変数が未設定のまま、今と同じに動く。

## Current / Target

Current：`provider-ci.yml` の `provider-tests` は `ubuntu-latest`、`provider-distribution-parity` は `ubuntu-latest` と `macos-latest` の matrix。ほかのワークフローもすべて GitHub のランナー。

Target：

```text
PR (pull_request)
  └─ route（GitHub, ubuntu-latest）
       ci-runner-job-gate.py route  ← vars.SPEC_DOCK_CI_RUNNER と GitHub が書いたイベント
       出力 runners = {"ubuntu-latest": <labels>, "macos-latest": "macos-latest"}
  ├─ provider-tests                     runs-on: runners['ubuntu-latest']
  └─ Provider distribution parity (os)  runs-on: runners[matrix.os]

Mac mini
  LaunchAgent com.chemitaro.spec-dock-ci-vm（5分ごと、止まっていれば limactl start）
  専用の Lima 2.2.1（~/Library/Application Support/spec-dock-ci-vm/lima）
  LIMA_HOME=/Volumes/990p2t/vm/spec-dock-ci-lima
    └─ VM spec-dock-ci（Ubuntu 24.04 ARM64, vz, plain）
         nftables：外向きは DNS とインターネットだけ
         spec-dock-runner-1 / -2（sudo なし）→ actions.runner.chemitaro-spec-dock.spec-dock-ci-{1,2}.service
         /opt/spec-dock-ci（root の持ち物）：job-started.sh → ci-runner-job-gate.py admit、job-completed.sh
```

## 責務・Interface

| 要素 | 責務 | Interface |
|---|---|---|
| `ci-runner-job-gate.py decide` | 信頼する PR かの判定（1か所）。同じリポジトリ、`pull_request`、base と head が同じリポジトリ、作者と送り手が `User`、作者の関係が `OWNER`・`MEMBER`・`COLLABORATOR` | 理由の文字列か `None` |
| `route` サブコマンド | 振り分け。`local` かつ判定が通るときだけ Linux を手元のラベルにする | 環境変数 `SPEC_DOCK_CI_RUNNER`、`GITHUB_EVENT_PATH` など。`GITHUB_OUTPUT` に `runners=<JSON>`。未知の値は終了コード2 |
| `admit` サブコマンド | ランナーの開始前のフック。イベントのファイルは、ランナーの利用者のホーム（`pwd` で引く）の `actions-runner/_work/_temp/_github_workflow/event.json` に決め、`GITHUB_EVENT_PATH` がそこを指さなければ拒否する | 終了コード0で実行（許可の行を標準出力）、1で拒否（理由を標準エラー） |
| `provider-ci.yml` | 振り分けの結果でランナーを選ぶ。リポジトリ名は `chemitaro/spec-dock` に固定（fork の側の変数では手元に行かない） | ジョブの名前は今と同じ |
| `.github/runner/spec-dock-ci.lima.yaml` | VM の形（plain、mount なし、SSH の鍵を読まない、image の digest を固定） | `limactl create` |
| `.github/runner/nftables.conf` | 外向きの接続の制限（root だけが変更できる） | `/etc/nftables.conf` |
| `.github/runner/guest-setup.sh` | VM の中の root の準備（パッケージ、nftables、利用者、ランナーの tar の SHA256 の確かめ、フック、needrestart）。何度実行してもよい。置き場所とファイルが root か実行者の持ち物で、ほかの人が書けないときだけ動く。root は、ランナーの利用者が書けるファイルを実行も利用もしない（依存の導入は root の持ち物の `/opt/spec-dock-ci/runner-dist-<版>` から、systemd の unit は root が自分の文面で書き、`svc.sh` とそのひな形を使わない） | Lima の利用者のホームから `sudo sh ~/spec-dock-runner/guest-setup.sh` |
| `.github/runner/register-runner.sh` | 登録のトークンを標準入力から読み、pipe でランナーの利用者のシェルに渡し、そこで `ACTIONS_RUNNER_INPUT_TOKEN` にして `config.sh` を動かす（sudo の記録に値が出ない）。guest-setup が書いた unit を `systemctl enable --now` | 標準入力1行 |
| `job-started.sh` / `job-completed.sh` | ジョブの前の判定（`python3 -I` で、利用者の site-packages や `PYTHONPATH` を読まない）と、後の作業場所の掃除（`_tool` だけを残す） | ランナーの `.env` の `ACTIONS_RUNNER_HOOK_JOB_*` |
| `host-install.sh` / `host-ensure-vm.sh` | Mac の側の Lima の導入（SHA256SUMS で確かめる）と LaunchAgent | `lima`、`agent` |

VM のツールは GitHub のランナーにそろえる：setup-python の Python は `/opt/hostedtoolcache` の下でしか `libpython` を見つけられない（RPATH）ので、root の持ち物のその場所に Python 3.11 と uv を置き、ランナーの `AGENT_TOOLSDIRECTORY` で指す（ジョブは書き換えられない）。git は `ppa:git-core/ppa` から入れる。

不変条件：VM に docker、podman、containerd を入れない（ジョブの手順の前に PR の指定で container を動かす経路を作らない）。nftables の拒否の規則は counter を持ち、確かめで増えたことを観測できる。

ラベル `spec-dock-ci` は、このリポジトリのランナーだけに付ける。退去費用の `ci-shadow` のラベルとは重ならない。

## data / failure

| 失敗 | 振る舞い | 回復 |
|---|---|---|
| 変数の値が不正 | `route` が失敗し、`if: !cancelled()` のため2つのジョブは `fromJSON` の失敗で失敗になる（スキップにならない） | 変数を直し、すべてのジョブを再実行 |
| 手元のランナーが止まっている（ランナーだけ、VM、Mac の未ログイン、VM の故障のどれでも） | ジョブは待つ（最長24時間） | VM を直す。または変数を `hosted` にし、run を取り消して、すべてのジョブを再実行 |
| fork などがワークフローを書き換えて手元を指す（イベントのファイルの場所を変えるものを含む） | `admit` が手順の前に失敗にする | 何もしない。承認制（D3 ③）で、外の人の run は承認まで始まらない |
| 掃除のフックが想定外の `RUNNER_TEMP` を見る | 何も消さずに失敗（ジョブも失敗） | VM の中を調べる |
| 外付けのボリュームがない | `host-ensure-vm.sh` は待つと記録して終了0 | 次の回に起こす |
| VM の自動更新でランナーが再起動 | needrestart の設定でランナーを外す | 次の VM の起動で読み直す |

判定に使うのは、ランナーが決まった場所に書いたイベントと既定の変数だけである（判定はランナーのこの振る舞いに依存する）。PR の中のファイルは、`route` の実行（GitHub のランナー）に使うが、手元での実行の可否は `admit` が VM の中のコピーで決める。

## 変更対象

- 変える：`.github/workflows/provider-ci.yml`（`route` のジョブを足す）、`.github/scripts/ci-runner-job-gate.py`（新規）、`.github/runner/`（新規）、`tests/integration/test_issue454_runner_gate.py`（新規）、`docs/ci.md`、`docs/ci-local-runner.md`（新規）。
- 変えない：`ci.yml`、`commit-identity.yml`、`release-tag.yml`、製品のコード（`src/`）、同梱の資産、退去費用の環境。

## 移行・互換性・rollback

- 移行：PR を push（変数は未設定なので今と同じ）→ 利用者の環境の段階1 → フックの確かめ → 変数を `local` → この PR の CI を手元で確かめる → 人がマージ。マージの前は、変数は新しいワークフローを持つこの PR にだけ効く。Epic #424 の PR には、マージの後に、その PR の次の run から効く。
- 互換性：チェックの名前は変わらない。`provider-ci.yml` に `permissions: contents: read` を足した（今のジョブは書き込みを使わない）。
- rollback：変数を `hosted` にする（ワークフローを戻さずに GitHub に戻る）。さらに戻すときは、この PR を revert する。環境の戻し方は手順書に書く（ランナーの削除、VM の削除、LaunchAgent の削除、承認の設定を前の値に戻す）。

## testability

- 振り分けと判定：`tests/integration/test_issue454_runner_gate.py` がスクリプトを別のプロセスで動かし、イベントの JSON と変数の組み合わせで出力と終了コードを確かめる。
- ワークフローと VM の設定：同じテストが文面を確かめる（ランナーの名前を直接書かない、`needs` と `!cancelled()`、ほかのワークフローが GitHub のまま、plain と mount なし、ブロックする範囲）。
- 掃除のフック：一時のディレクトリで実行し、残るものと、想定外の場所で消さないことを確かめる。
- 実機：VM の中でランナーの利用者として、sudo、Mac と LAN と Tailscale への接続、インターネット、フックの判定を確かめる。この PR の実際のジョブのランナーの名前と時間を GitHub の API で読む。

## risk

- 公開のリポジトリで self-hosted runner を使う（F2）。三重の守りと VM の隔離で抑えるが、信頼する作者のコードは、ランナーの利用者の権限で VM の中（フックを指す `.env`、ランナーの本体を含む）を変えられ、その後のジョブに残る。検知は、手元のジョブのログの許可の行（毎回）。疑わしいときは VM を作り直す。
- fork のジョブはフックで拒否される前に、アクションの取得（`Set up job`）までは進む。取得したアクションは掃除のフックで消す。docker がないので、container のアクションは動かない。
- x86_64 の Linux での確かめがなくなる（D1、利用者が受け入れた）。
- ランナーが1台の VM に集まるので、PR が重なると待つ。
- VZ の vsock の経路は nftables の外である。plain のため guest agent は動かない（F7）。VM の中で guest agent が動いていないことを実機で確かめる。
- ランナーの版は GitHub の自動の更新に任せる（古いままだとジョブを受けられなくなる）。
