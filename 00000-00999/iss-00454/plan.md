---
種別: 実装計画書（Issue）
ID: "iss-00454"
タイトル: "Run Spec Dock CI On Local Mac Mini Runner"
関連GitHub: ["#454"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md", "design.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00454 Run Spec Dock CI On Local Mac Mini Runner — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- 選んだ level：`strict`（統括の指定）。
- 理由：公開のリポジトリの CI の実行の場所を変え、利用者の Mac の上で PR のコードを動かす。失敗すると、並行する Epic #424 の PR の CI が止まり、また安全の境界（資格情報、Mac の口）を損なうおそれがある。
- risk factor：F2 の公開のリポジトリの self-hosted runner、利用者の環境の変更、CI の切り替え。
- 再評価の条件：資格情報や Mac のファイルに VM から届くことが分かった、知らない人のコードが手元で動いた、などの安全の事故が起きたら `critical` に上げ、変数を `hosted` に戻してから扱う。

## 目標

Requirement の AC-454-01〜11 を満たす。変数が未設定の間は今と同じに動き、`local` にすると信頼する PR の重いジョブが手元の VM で通る。

## 順序・依存

1. リポジトリの変更（振り分け、フック、VM の設定、テスト、文書）。外の環境に依存しない。
2. 文書と変更のレビュー、コミット、通常の push。この時点の CI は GitHub のランナーで動く（AC-454-01）。
3. 利用者の環境の段階1（承認の後）：S1 Lima → S2 VM → S3 VM の中の設定 → 隔離の確かめ → S4 登録（利用者の操作）→ S5 LaunchAgent → S6 承認の設定（利用者の操作）。
4. フックの確かめ（VM の中）→ S7 変数を `local`（利用者の操作）→ この PR の CI を再実行して手元で通す → 変数を不正な値にした run（AC-454-01）と、切り戻しのリハーサル（AC-454-08）→ 変数を `local` に戻す。変数の操作は利用者が行う。
5. 最終品質ゲート → PR → マージは人。

3 の S6 は、ほかと並べて進めてよい。4 は 3 のすべてに依存する。

## 実装step

1. `ci-runner-job-gate.py` に `route` と `admit` を置き、判定を `decide` の1か所にする。
2. `provider-ci.yml` に `route` のジョブを足し、2つのジョブを `needs: route`、`if: ${{ !cancelled() }}`、`runs-on` を `route` の出力（出力がなければ GitHub のランナー）にし、最初の手順で `route` の失敗を失敗にする。名前は変えない。`permissions: contents: read` を足す。
3. `.github/runner/` に VM、nftables、VM の中の設定、登録、フック、Mac の側の導入を置く。
4. テスト：振り分けと判定の正と負、ワークフローの文面、VM の設定の文面、掃除のフックの正と負。
5. 文書：`docs/ci.md` の表と、`docs/ci-local-runner.md`（構成、導入、確かめ、切り戻し、作り直し、撤去）。
6. 環境の段階1を、手順書のとおりに行い、手順書との違いがあれば手順書を直す。

## 検証

| AC | 確かめ方 |
|---|---|
| 01 | テスト。変数が未設定の push の CI で、ジョブのランナーの名前が `GitHub Actions`。マージの前に変数を `invalid` にして run を作り、3つのジョブの conclusion が failure（名前は今と同じ）であることを API で読む |
| 02 | 変数を `local` にした後の run で、ジョブの `runner_name` を API で読む。すべて成功。両方のランナーのジョブのログに許可の行がある。VM の中の両方の `.env` にフックの2行がある |
| 03 | テスト（負の例10種、イベント4種、別のリポジトリ、読めない JSON）。VM の中で `sudo -u spec-dock-runner-1` としてフックを fork のイベントと同じリポジトリのイベントで実行。実際の fork の PR は作れなければ未確認 |
| 04 | 陽性の対照：Mac で実際に待ち受けている口（`127.0.0.1:9222`、`*:6768`、Tailscale の IP の口）を確かめてから、VM の中でランナーの利用者として `curl` し、`192.168.5.2`・Mac の LAN の IP・Mac の Tailscale の IP・`169.254.169.254`・IPv6 のどれもが「No route to host」（admin-prohibited）で失敗し、nftables の counter が増えることを見る。`sudo -n true` が失敗。`https://github.com` に届く。`limactl list --json` で mounts と portForwards が空。`lima-guestagent` と docker・containerd がない |
| 05 | VM の中で `gh` の設定、`~/.ssh` の秘密鍵を探す。`_diag` と journal にトークンの値がない（登録の直後に、そのトークンの先頭の数文字で検索し、検索の文字列は記録しない）。差分を秘密情報の形で検索 |
| 06 | テスト。実際のジョブの後に `_work` の中身を見る |
| 07 | ジョブのないときに `limactl stop`、5分以内に Running、ランナーが online（利用者が Settings で確かめるか、ジョブの受け付けで確かめる） |
| 08 | マージの前に、ランナーのサービスを止めて変数 `local` で run を作り、ジョブが Queued で待つことを見る。変数を `hosted`、`gh run cancel`、`gh run rerun`（すべて）で、ジョブの `runner_name` が GitHub のものになることを API で読む。変数を `local` に戻し、ランナーを起動する |
| 09 | 前後で比べる：`~/Library/LaunchAgents/com.taikyohiyou.ci-vm-watch.plist`、`~/Library/Application Support/taikyohiyou-ci-vm/lima/bin/limactl`、同じ場所の `ci_vm_host_watch.py` の SHA256 と、`/Volumes/990p2t/workspace/worktrees/ci-vm-iss-02162/ci-shadow/lima.yaml` の更新時刻 |
| 10 | 利用者が `gh api .../fork-pr-contributor-approval` を読む |
| 11 | `make lint`、`uv run pytest`。時間の表 |

regression：チェックの名前、ほかのワークフロー、全体のテスト。

negative test：振り分けの未知の値、信頼しない PR の振り分けとフック、掃除のフックの想定外の場所。

migration failure：変数を `local` にした後に手元のジョブが失敗・待ちになったら、変数を `hosted` に戻し、run を取り消して、すべてのジョブを再実行する（forward recovery）。この手順は AC-454-08 で、マージの前に一度リハーサルする。

## rollback

- 条件：手元のジョブが通らない、VM が安定しない、安全の懸念が見つかった。
- 順序：①変数を `hosted`（利用者）②run を取り消してすべて再実行 ③必要ならランナーを GitHub から削除、VM を停止・削除、LaunchAgent を削除 ④承認の設定を前の値に戻すか残すかを利用者が決める ⑤ワークフローを revert する PR。
- 担当：①②④は利用者、③⑤は実装担当（承認の後）。

## security / privacy / operability

- security：三重の守り（D3）、VM の隔離（plain、nftables、sudo なし）、登録のトークンを残さない、`permissions: contents: read`。確かめは AC-454-03〜05。
- privacy：VM は Mac のファイルを共有しない。PR のログは今と同じに GitHub に残る。
- operability：LaunchAgent のログ（`~/Library/Application Support/spec-dock-ci-vm/ensure-vm.{log,err}`）、ランナーのログ（VM の中の `journalctl -u actions.runner.*`、`_diag`）。手順書に確認と回復を書く。

## exit / handoff

- 完了：AC-454-01〜11 の証拠が `report.md` にあり、D7・D8 の回答が文書に反映され、PR がマージできる状態で、CI が通っている。マージと `work finish` は人と統括。
- 残余リスク：信頼する作者のコードによる VM の中の改変、x86_64 の確かめの欠落、1台の VM への集中、段階2（D7）。
- 引き渡し：段階2の別の Issue、VM の作り直しの周期、Lima 2.3 の正式版が出たときの `hostLoopback: false` の追加。
