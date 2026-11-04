---
種別: レポート（Issue）
ID: "iss-00568"
関連GitHub: ["#568"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

ダッシュボードの古さを、「最後に GitHub の構造を確かめた時刻」＝ スナップショットの `fetched_at` と probe の `checked_at`（`last_error` がないときだけ）の新しいほう、で判定するようにした。上の帯の「N分前に取得」、古さの警告、API の `snapshot`、`dashboard summary` は同じ時刻を使う（`structure_confirmed_at` の1か所）。probe が失敗しているとき、probe.json がないか壊れているとき、時刻が未来のときは、`fetched_at` だけで判定する。PR の状態の古さは変えていない。

契約の変更（次の版の移行の注記用）：`dashboard summary` の `fetched_at`／`stale`、API の `snapshot.fetched_at`／`age_seconds`／`stale` の意味が「最後に構造を確かめた時刻」になった。欄の名前と型は同じ。reference_cli.md に反映した。

コミット：f2ed8f26879807849071ae5b9a04ca3db78ef99d

## Verification

- 仕様のレビュー（spec-reviewer opus/medium）：P0・P1 なし（P2 が1件、情報のみ）。
- コードのレビュー（code-reviewer sonnet/high）：指摘 0件。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人）：f2ed8f2 で合格。P0/P1 なし、coverage 完全、P3 が1件。
- テスト lane（同じコミット）：`make lint` exit 0、`uv run pytest` exit 0（3706 passed, 7 skipped）。
- 新しいテスト：純関数の表と不正・未来の時刻、モデル、サーバーの API と `dashboard summary` の一致、probe の更新の反映、probe の失敗・破損。
- 記録：`.workbench/final-quality-gate/iss-00568/closure.md`

## Residual Risks / Follow-ups

- P3（FQG-001）：スナップショットが読めない間は、キャッシュに残った直前の probe の時刻で判定する。スナップショットが読めない状態は別の警告（SNAPSHOT_UNREADABLE）が出るので、影響は小さい。直さない。
- 画面の JavaScript は変えていない（欄の名前が同じため）。ツールチップの文言は「構造を取得した時刻」のまま。
