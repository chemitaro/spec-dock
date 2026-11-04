---
種別: レポート（Epic）
ID: "epic-00547"
関連GitHub: ["#547"]
最終更新: "2026-11-05"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

エージェントが人に頼むタスクと、人が自分で登録するタスク（人のタスク）を、各リポジトリのカタログ（`todos/`）に唯一の正本として置き、`spec-dock todo` の CLI で登録・一覧・完了でき、全リポジトリを集約して見られるようにした。ダッシュボードに人のタスクの画面と、構造の図・ボード・詳しい画面・概況の印を足した。CLI は 0.7.0、画面は 0.8.0 で配り、7つのリポジトリが 0.8.0 である。PR のマージは利用者が行った。

## Outcome

- 子の Issue はすべて閉じた：#549（記録の形と CLI の中核）、#550（集約と `dashboard summary` の数）、#551（配布するスキルと文書の規則）、#553（0.7.0）、#554（ダッシュボードの画面）、#555（画面の版。epic-00427 の #536 の 0.8.0 で兼ねた）。
- 利用者と決めたこと（requirement.cue の decisions）：保存先はカタログ（GitHub Issue にしない）、記録するのは1回の会話で終わらないものだけ、マージ待ちはタスクにしない、期限の既定は4時間、件数の目安は親20・サブタスク30で警告だけ、設定は初めの値 < 利用者の設定 < リポジトリの設定、人が Scope を止めることは印だけ（状態と `work start` は変えない）、画面は見るだけ、個人のタスク管理とは CLI の一覧の JSON でつなぐ。
- 運用はすでに始まっている：2026-11-05 の時点で taikyohiyou_project に開いた人のタスクが5件あり、ダッシュボードの人のタスクの画面に出ている。

## Verification

- 各 PR：仕様のレビュー、コードのレビュー、最終品質ゲート（P0・P1 なし）、`make lint` と `uv run pytest`、CI の合格を各 Issue の report.md に残した。
- 統括の運用の確かめ（`iss-00553/report.md`、0.7.0）：main のチェックアウトで登録したタスクが別の worktree の `todo list` に出る（R-01）、`todo list --all-repositories` が登録簿の7リポジトリを返す（R-10）、配布したスキルに規則がある（R-14）。
- 統括のブラウザーでの確かめ（2026-11-05、0.8.0）：`/todos` と `/r/<repo>/todos` を PC 幅と 390px で開き、「止めている」「あとで」の分け、期限、止めている Scope の印が出ること、例外0を確かめた。

## Residual Risks / Follow-ups

- Company OS の受付簿（`content/office/intake.md`）の移し替えは、しばらく使って良ければ Company OS の側で行う（利用者の決定）。
- 画面からの書き込み（完了・延期・登録）、知らせ（Telegram）、`resolve_when` による自動の完了は、この Epic の外（必要になったら判断する）。
- iPhone の Safari での人のタスクの画面は、実機では確かめていない。
