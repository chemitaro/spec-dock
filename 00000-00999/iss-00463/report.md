---
種別: レポート（Issue）
ID: "iss-00463"
タイトル: "Run macOS CI On Local Mac Mini VM"
関連GitHub: ["#463"]
最終更新: "2026-10-30"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# Result Summary

## 保留（2026-10-30 利用者の決定）

- **決定**：iss-00463 は今は進めない。PR は作らず、ホスト・VM・ランナー・LaunchAgent・リポジトリ変数は何も変えていない（設計の環境変更 E0〜E8 は未実行）。
- **理由**：spec-dock は公開リポジトリで、GitHub の通常のランナー（`macos-latest` を含む）は無料・無制限。spec-dock の CI は GitHub に戻し、段階1（iss-00454）の Lima VM も止める。手元の CI が要るのは非公開リポジトリだけ。
- **再開するときの前提**（新しい Issue として立てる）：
  - ランナーと実行環境を複数のリポジトリで共有し、リソース管理を共通にする（リポジトリごとの環境設定をしない、複数種類の VM が同時に起動して足りなくなるのを避ける）。
  - VM はジョブごとの使い捨てにする。
  - CI が走っていないときのメモリ消費は0、ストレージは必要なときに必要なだけ。
- **将来の材料**（調べた事実は [requirement.md](requirement.md) の G1〜G10、方式は [design.md](design.md)）：
  - tart 2.41.1＋softnet 0.24.1（openai/tart・openai/softnet、FSL-1.1-ALv2、配布物の SHA256 を固定）。`--net-softnet-block='out @host'` で VM から Mac 側への新規接続を止め、Mac→VM の SSH の返りは通す。softnet は IPv4 のみ通し、規則は IP 単位。gateway を止めると Mac の DNS も使えないので VM は公開 DNS を使う。softnet は内蔵ディスク上で setuid root が要る。
  - イメージ `ghcr.io/cirruslabs/macos-tahoe-vanilla@sha256:eeec54bf…6640`（取得24GB、admin/admin・自動ログイン・画面共有が初期値なので固める必要あり）。
  - 隔離の確かめ方：VM から Mac 側の口・LAN・IPv6 へ届かないこと、公開 DNS と GitHub へは届くことを VM の中から curl 等で確かめる（plan.md の E6）。
  - 下書きの実装：`.github/runner/macos/`、`.github/runner/lib.sh`、`ci-runner-job-gate.py` の `SPEC_DOCK_CI_MACOS_RUNNER`、段階1の申し送りの直し（このブランチ `chemitaro/local-macos-vm-ci` にコミット済み、main には入れていない）。

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## Residual Risks / Follow-ups
