---
種別: 設計書（Issue）
ID: "iss-00293"
タイトル: "最終品質ゲートとマージ可能な Pull Request を作成する"
関連GitHub: ["#293"]
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-07"
依存: ["requirement.md"]
親: ["epic-00283", "init-local-00003"]
---

# iss-00293 最終品質ゲートとマージ可能な Pull Request を作成する — Issue 設計

## 設計方針

この Issue は、Epic 全体の最終統合ゲートとして設計する。個別実装 slice の所有権は `iss-00284` から `iss-00292` に残し、この Issue はそれらをまとめて検証し、Pull Request がレビュー可能かつ mergeable になる状態へ運ぶ。

PR はこの Issue で一度だけ作成または更新する。先行 Issue の完了は、`issue finish` と各 `report.md` の証跡で確認する。これにより、実装中の認知負荷を「今の Issue を完了して次へ渡す」ことに絞り、PR 作成、CI、レビュー指摘対応、手動テスト証跡を最後に集約する。

## ワークフロー設計

```text
iss-00284 implementation -> issue finish -> issue start iss-00285
iss-00285 implementation -> issue finish -> issue start iss-00286
iss-00286 implementation -> issue finish -> issue start iss-00287
iss-00287 implementation -> issue finish -> issue start iss-00288
iss-00288 implementation -> issue finish -> issue start iss-00289
iss-00289 implementation -> issue finish -> issue start iss-00290
iss-00290 implementation -> issue finish -> issue start iss-00291
iss-00291 implementation -> issue finish -> issue start iss-00292
iss-00292 implementation -> issue finish -> issue start iss-00293
iss-00293 quality gate -> manual tests -> PR -> review/CI fix loop -> mergeable
```

先行 Issue は PR を作らない。各 Issue は自身の完了証跡を残し、次の Issue へ実行コンテキストを渡す。最後の `iss-00293` が、全体をレビュー単位としてまとめる。

## 不具合修正ループ

1. 不具合またはレビュー指摘を `report.md` に記録する。
2. Epic スコープ内の修正であることを確認する。
3. 最小差分で修正する。
4. 関連テスト、`spec-dock validate`、必要な手動確認を再実行する。
5. 変更を push し、PR の状態を再確認する。

修正が Epic スコープを超える場合は、この Issue で抱え込まず、残課題として明記する。
