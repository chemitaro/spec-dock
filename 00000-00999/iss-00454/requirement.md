---
種別: 要件定義書（Issue）
ID: "iss-00454"
タイトル: "Run Spec Dock CI On Local Mac Mini Runner"
関連GitHub: ["#454"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00080", "init-00079"]
---

# iss-00454 Run Spec Dock CI On Local Mac Mini Runner — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：spec-dock の CI を、手元の Mac mini のランナーで動かす

> この文書は、統括が利用者の依頼（2026-10-26）から書いた下書きである。実装担当が、調べた事実と設計の選択肢をもとに、要件を固める。

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

- どのジョブを手元で動かすか（すべてか、一部か）。`provider-ci.yml` は Linux（`ubuntu-latest`）と macOS（`macos-latest`）の両方で配布を確かめている。spec-dock は Linux と macOS の両方に対応するので、両方の確かめを残す方法（macOS は Mac mini 自身、Linux は仮想マシン、など）。
- ランナーをどこで動かすか（Mac mini の macOS に直に置くか、退去費用と同じく仮想マシンの中か）。退去費用の仮想マシンとランナーは、退去費用の持ち物なので、そのまま共用してよいかも決める（GitHub の個人のアカウントのランナーは、リポジトリごとに登録する）。
- fork などの PR の扱い（GitHub のランナーに回す、承認が要るようにする、動かさない）。
- 手元のランナーが止まっているときの扱い（待つか、GitHub のランナーに回すか）。

## 制約・前提

- 退去費用のリポジトリ、その仮想マシン、そのランナー、その LaunchAgent は、利用者の確認なしに変えない。読むのはよい。
- 利用者の環境（`~/Library/LaunchAgents/`、仮想マシン、ランナーの登録、GitHub のリポジトリの設定）を変える手順は、計画を示して利用者が認めてから行う。ランナーの登録の手続き（登録のトークンの発行など）で、利用者の操作が要るところは、利用者に頼む。
- 資格情報を、ジョブ、仮想マシン、コンテナ、リポジトリに写さない。秘密情報をコミットしない。
- 今の CI の確かめ（lint、全体のテスト、配布の確かめ、仕様の検査、コミットの作者の確かめ、版のタグ）は、どれも落とさない。
- Epic #424 の作業（I-5、I-11 など）が並行して PR を出している。切り替えの途中で、それらの PR の CI が止まったり、通らなくなったりしないようにする。

## 観測可能な要件

（実装担当が書く。）

## スコープ

（実装担当が書く。）

## 失敗・境界条件

（実装担当が書く。）

## 受け入れ条件

（実装担当が書く。）
