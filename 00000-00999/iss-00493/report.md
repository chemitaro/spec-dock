---
種別: レポート（Issue）
ID: "iss-00493"
関連GitHub: ["#493"]
最終更新: "2026-11-01"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

（実装の後に書く）

## 要件を足した理由

統括が書いた `requirement.cue` の R-01、R-02 に、実装担当が R-03、R-04、F-01 を足した。カタログの `.gitignore` ではなく同期の規則で除外する設計（design.cue の compatibility）にしたため、同期の規則が保存しないファイルが、ほかの経路でどう見えるかを決める必要が出た。

- R-03：保存しないファイルを未保存と数え続けると、Finder が Scope のフォルダーに `.DS_Store` を作るたびに、`work finish` の保存の確かめ（`canonical_work._unsaved_places`）が最大180秒待って `CANONICAL_SAVE_UNCONFIRMED` で止まる。`canonical status` の `changes.unsaved` も 0 にならない。
- R-04：R-02 の案内で保存済みの不要なファイルをまとめて消すと、大量の削除の保留（20件以上、または5件以上かつ1割以上）に当たり、`canonical accept --deletions` が要る。不要なファイルの削除は仕様の中身を失わないので、数えない。
- F-01：未保存と数えなくなると、`canonical remove` の未保存の確かめを通り抜け、`git worktree remove`（`--force` なし）が未追跡のファイルで失敗する。リンクなどを消す前に止める必要がある。

## 仕様のレビュー

- 1回目（2026-11-01、spec-reviewer opus/high）：合格。P0 0、P1 0、P2 1、P3 2。結果は Workbench の `.workbench/spec-review/iss-00493/round-1.json`。
  - P2（未追跡の不要なファイルが、取り込む変更と重なると取り込みを待ち続ける。新しい版どうしでも起きうる）：design.cue の risks を正確に書き直し、範囲の外として残した（手元の不要なファイルを消せば進む）。
  - P3（R-04 の「削除が保存される」のテストがない）：T-05 に同期での確かめを足した。
  - P3（この節がなかった）：この節を書いた。

## Verification

（実装の後に書く）

## Residual Risks / Follow-ups

- 取り込む変更がある不要なファイルのパスに、手元の未追跡の不要なファイルがあると、取り込みは `blocking`（`local_edit`）で待ち続ける。手元のファイルを消せば進む。自動で消して取り込む扱いは別の Issue の候補。
