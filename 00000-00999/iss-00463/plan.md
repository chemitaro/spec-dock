---
種別: 実装計画書（Issue）
ID: "iss-00463"
タイトル: "Run macOS CI On Local Mac Mini VM"
関連GitHub: ["#463"]
状態: "draft"
最終更新: "2026-10-30"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00463 Run macOS CI On Local Mac Mini VM — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- 選んだ level：`strict`。
- 理由：公開のリポジトリの PR のコードを、利用者の Mac の上の VM で動かす範囲を広げる。Mac に SUID root の実行ファイルを足す。段階1の動いている VM とランナーを変える。失敗すると、安全の境界（Mac の口、資格情報）を損なうか、CI が止まる。
- risk factor：softnet の SUID、VM のイメージの出どころ、VM の管理者の既定のパスワード、段階1の VM の変更、CI の切り替え。
- 再評価の条件：VM から Mac の口や LAN に届く、資格情報が VM やログに出る、知らない人のコードが手元で動く、のどれかが起きたら `critical` に上げ、両方の変数を `hosted` に戻してから扱う。

## 目標

Requirement の AC-463-01〜12 を満たす。macOS の変数が未設定の間は今と同じに動き、`local` にすると信頼する PR の macOS の配布の確かめが手元の macOS の VM で通る。段階1の申し送りは、直したか、理由を残したかのどちらかになる。

## 順序・依存

1. 調べて設計し、統括に確かめる（この文書と design.md。環境は変えない）。
2. 統括の返事を待つ間に、リポジトリの中だけで直せる申し送り（スクリプト、手順書、テスト）を TDD で直す。段階1の VM には反映しない。
3. 返事の後に、macOS の振り分けと macOS の VM のスクリプトを作る（決定が変われば合わせる）。
4. コミット、通常の push。この時点の CI は GitHub のランナーで動く（AC-463-01）。
5. 利用者の環境（承認の後、下の E0〜E8 の順）。
6. 本物の PR の CI で、macOS のジョブが手元で通ることと、切り戻しを確かめる。
7. 最終品質ゲート → PR → マージは人。

2 と 3 は 1 の後。5 は 4 の後。E0（段階1の VM への反映）と E1〜E4（macOS の VM）は互いに独立だが、メモリと Mac の負荷を見るため順に行う。

## 利用者の環境を変える手順（統括を通して利用者の承認を得てから行う）

「実行」は、担当が自分の端末で行うものと、利用者が行うもの（統括がクリップボードで1つずつ渡す）を分ける。

| 段 | 実行 | コマンド（要点） | 変えるもの | sudo | 戻し方 | ディスク・メモリ |
|---|---|---|---|---|---|---|
| E0a | 利用者 | `gh variable set SPEC_DOCK_CI_RUNNER --repo chemitaro/spec-dock --body hosted` | リポジトリの変数 | なし | `--body local` | — |
| E0b | 担当 | 新しい `.github/runner/*` と gate を VM の `~/spec-dock-runner/` に `limactl copy`、`limactl shell spec-dock-ci -- sudo sh spec-dock-runner/guest-setup.sh` | VM の中：`/opt/spec-dock-ci/*`（`python3` のリンクを含む）、`/opt/hostedtoolcache` の uv、`/etc/apt/apt.conf.d/51spec-dock-git-ppa`、ランナーの `.env`、2つのランナーの再起動 | VM の中だけ（Lima の利用者はパスワードなしの sudo） | main の版の `.github/runner/` で guest-setup をやり直す | 変化なし |
| E0c | 担当 | Linux の LaunchAgent の plist に `AbandonProcessGroup` を足す：前の plist を `~/Library/Application Support/spec-dock-ci-vm/` に控え、`launchctl bootout gui/$UID/com.chemitaro.spec-dock-ci-vm`、書き換え、`plutil -lint`、`launchctl bootstrap` | `~/Library/LaunchAgents/com.chemitaro.spec-dock-ci-vm.plist` | なし | 控えを戻して bootout・bootstrap | — |
| E0d | 担当 | 2つのランナーが online、フックの確かめ（VM の中） | なし | — | — | — |
| E0e | 利用者 | `gh variable set SPEC_DOCK_CI_RUNNER --repo chemitaro/spec-dock --body local` | リポジトリの変数 | なし | `--body hosted` | — |
| E1 | 担当 | `sh .github/runner/macos/host-install.sh tools`（tart 2.41.1 と softnet 0.24.1 の release を取り、SHA256 を確かめて展開） | `~/Library/Application Support/spec-dock-ci-macos-vm/{tart.app,softnet}` | なし | そのディレクトリを消す | 内蔵 約80MB |
| E2 | 利用者 | `sudo install -d -o root -g wheel -m 755 /usr/local/libexec/spec-dock-ci-macos-vm && sudo install -o root -g wheel -m 4755 "$HOME/Library/Application Support/spec-dock-ci-macos-vm/softnet" /usr/local/libexec/spec-dock-ci-macos-vm/softnet` | `/usr/local/libexec/spec-dock-ci-macos-vm/softnet`（SUID root） | **要る（パスワード1回）** | `sudo rm -r /usr/local/libexec/spec-dock-ci-macos-vm` | 内蔵 約10MB |
| E3 | 担当 | `sh .github/runner/macos/host-install.sh vm`（`TART_HOME=/Volumes/990p2t/vm/spec-dock-ci-tart`、`tart clone ghcr.io/cirruslabs/macos-tahoe-vanilla@sha256:eeec54bf… spec-dock-ci-macos`、`tart set --cpu 4 --memory 6144`、VM 専用の SSH の鍵と known_hosts を同じ場所に作る） | `/Volumes/990p2t/vm/spec-dock-ci-tart/`、`~/Library/Application Support/spec-dock-ci-macos-vm/ssh/` | なし | `tart delete spec-dock-ci-macos`、`TART_HOME` と `ssh/` を消す | 外付け 取得24GB、保存 約50GB（取得の後に `tart prune` でキャッシュを消す） |
| E4 | 担当 | `sh .github/runner/macos/host-install.sh agent`（LaunchAgent `com.chemitaro.spec-dock-ci-macos-vm`、KeepAlive。VM が起動する） | `~/Library/LaunchAgents/com.chemitaro.spec-dock-ci-macos-vm.plist`、`…/spec-dock-ci-macos-vm/host-run-macos-vm.sh`、ログ | なし | `launchctl bootout gui/$UID/com.chemitaro.spec-dock-ci-macos-vm` と plist を消す | メモリ 6GiB（常時）、CPU 4 |
| E5 | 担当 | 最初の1回だけ `admin`／`admin` で SSH し、鍵を置く。`scp` で `.github/runner/macos/*` と共用のフックと gate を VM の `~/spec-dock-runner/`（700）に置き、`sudo sh ~/spec-dock-runner/guest-setup.sh` | VM の中だけ（DNS、admin の固め、ランナーの利用者、Python、uv、コマンドラインツール、ランナー、フック、LaunchDaemon） | VM の中だけ | VM を消して E3 から | VM のディスク +約8GB |
| E6 | 担当 | 隔離とフックの確かめ（AC-463-03、04、05） | なし | — | — | — |
| E7 | 利用者 | `gh api -X POST repos/chemitaro/spec-dock/actions/runners/registration-token --jq .token \| sh .github/runner/macos/host-ssh.sh sudo /opt/spec-dock-ci/register-runner.sh` | GitHub のランナー `spec-dock-ci-macos-1`、VM の中の登録の情報 | VM の中だけ | GitHub の Settings → Runners で削除、VM の中で `config.sh remove` | — |
| E8 | 利用者 | `gh variable set SPEC_DOCK_CI_MACOS_RUNNER --repo chemitaro/spec-dock --body local`（確かめと切り戻しのリハーサルで、統括を通して `hosted` と `local` を切り替える） | リポジトリの変数 | なし | `--body hosted` か `gh variable delete` | — |

合計の見込み：Mac の内蔵のディスク 約90MB、外付け 約50GB（作業の途中は最大 約75GB）、常時のメモリ 6GiB（段階1と合わせて 14GiB）。Mac の sudo は E2 の1回だけ。退去費用の環境と `~/.ssh`、`~/.claude`、`~/.codex` は変えない。

## 実装step

1. 申し送り（返事を待つ間、リポジトリだけ）：テストを先に書き、`ci-runner-job-gate.py`（T-7、T-9）、`provider-ci.yml`（T-10、V-1 のコメント）、`.github/runner/guest-setup.sh`（R-1、R-2、R-3、U-1、U-2、U-3、Q-2、T-2、T-3）、`register-runner.sh`（T-4、T-8 のためにスクリプトの場所から settings を読む）、`host-install.sh`（T-5、T-6）、`job-started.sh`（共用の Python のリンク）、テスト（U-4、Q-1、T-8、T-11、P-5）、手順書（R-3、R-4、P-3、P-6、P-7、V-1、Lima 2.3、Lima のキャッシュ、作り直しの方針）。
2. macOS（返事の後）：`route` に macOS の変数、`.github/runner/macos/` の6つのファイル、テスト `test_issue463_macos_runner.py`、手順書の macOS の節、`docs/ci.md` の表。
3. 環境：上の E0〜E8。
4. 確かめ：下の「検証」。
5. 報告書：AC ごとの証拠、時間の表、申し送りの対応表、環境の変更の時刻。

## 検証

- AC-463-01、03、05、06、10、12：`uv run pytest tests/integration/test_issue454_runner_gate.py tests/integration/test_issue463_macos_runner.py`、`make lint`、`uv run pytest`。両方の変数が未設定の push の run（GitHub のランナー）。
- AC-463-02：E8 の後、この PR の run のジョブの `runner_name` と時間を GitHub の API で読む。ログの許可の行。
- AC-463-04：E6 で、VM の中のランナーの利用者として `sudo -n true`、`id -Gn`、`su admin`（パスワードを知らないので失敗）、Mac の待ち受けの口（`lsof -nP -iTCP -sTCP:LISTEN` から、`127.0.0.1` と全体と Tailscale の IP の口を1つずつ）、gateway のどれかの口、`169.254.169.254:80`、IPv6 のリテラル、`https://github.com` を試す。VM の中の root で gateway への経路を足しても届かないことを試す。Mac の `ps` で softnet の引数を見る。`tart get` と VM の中で guest agent が無いこと。
- AC-463-07：ジョブのないときに VM の中で `sudo shutdown -h now` → LaunchAgent が起こし、ランナーが online に戻る時間を測る。
- AC-463-08：macOS のランナーを止めて push し、macOS のジョブが待つことを見る → 利用者が `hosted` にし、run を取り消し、完了を待ってからすべてを再実行 → GitHub のランナーで通る → `local` に戻す。
- AC-463-09：作業の前と後に、退去費用のファイルの SHA256 と更新時刻を記録する。
- AC-463-10：申し送りの対応表と、段階1の VM での確かめ（権限の検査、uv のハッシュ、PPA の自動更新の対象、`.env` に重複がない、ランナーの再起動、T-6 の plist）。

## rollback

- CI：macOS の変数を `hosted` にする（ワークフローを戻さずに GitHub に戻る）。Linux は `SPEC_DOCK_CI_RUNNER` で同じ。
- 環境：上の表の「戻し方」を逆の順で行う。段階1の VM は、main の版のスクリプトで guest-setup をやり直せば、前の形に戻る（`/opt/spec-dock-ci/python3` のリンクは残っても害がない）。
- 安全の事故：両方の変数を `hosted` にし、該当の VM を作り直す。

## exit / handoff

- 完了の条件：AC-463-01〜12 の証拠が報告書にあり、最終品質ゲートが通り、PR がマージできる状態で、両方の変数が利用者の決めた値になっている。`work finish` は行わない。
- 残るリスク：softnet の SUID、イメージの出どころ、P-4 の改変の残り、macOS の自動の更新による再起動、git の版の違い、メモリ。
- 引き渡し：PR の URL、最終の SHA、ゲートの結果、`report.md`、利用者に判断してほしいこと（作り直しの周期、Lima 2.3 への移行の時期）。
