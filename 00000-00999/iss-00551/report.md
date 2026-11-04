---
種別: レポート（Issue）
ID: "iss-00551"
関連GitHub: ["#551"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

配布するスキルと文書に、人のタスクの規則と使い方を書いた。コードの振る舞いは変えていない。

- スキル（`install_root/.agents/skills/spec-dock/SKILL.md` と dogfood の写し）に「人のタスク」の節を足した：登録しない場面（会話で答えが返るもの、PR のマージ待ち、作業者から統括への問い）、登録する場面と `todo add --by agent --role --kind`（`--body`、`--reply-to`、`--effort`、`decide` の選択肢と推奨、`--blocks`）、束（`--kind checklist --item`、答えのたびにサブタスクを閉じ、返事の終わりに `todo show <親>`）、閉じ方（`todo done --record`、統括が始めるときに `todo list`）、秘密と `--worktree` の扱い。
- `docs/todo.md` を足した（使い方、記録の形、設定の3段と見本、集約、外部の道具の読み方）。`docs/README.md`、`docs/guide.md` の Current に載せ、`docs/canonical.md` に `todos/` の説明と `TODO_*` のエラーと次の1手を足した。
- dogfood の写しと `static-inventory.json`（SKILL.md、README.md、guide.md、canonical.md の sha256 と `known_old_sha256`、`todo.md` の新しい行）を合わせた。
- テスト：`tests/unit/infra/test_issue551_todo_rules.py`（規則の語、`todo.md` の配布とリンク、`canonical.md` の `TODO_*` が `reference_cli.md` にあること、写しと sha256、`installation init`）。`test_authoring_kit_assets.py` の Current の一覧と、`test_issue413_assets.py` の件数（95→96、96→97）を直した。

コミット：`6ab66dd02`（実装）、`863c0a9a4`（コードのレビューの P3 の修正）、`996652619`（件数の期待値）。

### 仮の判断・Epic との違い

- 規則で、エージェントが選べる種類を `decide`、`check`、`operate`、`act`、`checklist` と書いた（`todo` は人だけで、`--by agent --kind todo` は `TODO_INVALID`）。
- 束にも `--body` が要る（候補の wheel で確かめて、スキルと `todo.md` の例に反映した）。
- Epic D-17 の `migration.md` は、リリースの Issue（iss-00553）が書く。

## Verification

- 仕様のレビュー（spec-reviewer opus/medium）：1回目で合格（P0 0、P1 0、P2 1、P3 2）。P2（候補 wheel での確かめ）と P3 は仕様に反映した。記録は `.workbench/spec-review/iss-00551/`。
- 候補の wheel（`spec_dock-0.6.0`、一時の環境）と隔離した利用者のリポジトリ（一時のディレクトリ、ローカルの bare を origin、`XDG_STATE_HOME` も一時）：`installation init` でスキルの節と `todo.md` が入ること、`canonical link --no-schedule` の後、規則のとおりの `todo add --by agent`（束と `decide`）、サブタスクの `todo done --record`、親を閉じる前の `TODO_SUBTASKS_OPEN`、`todo show` の残り、`todo check` の成功を確かめた。
- コードのレビュー（code-reviewer sonnet/high、決まりの面と仕様の面の2人、`0534cfe29..6ab66dd02`）：どちらも合格（決まりの面は指摘0、仕様の面は P3 2）。P3 はどちらも `863c0a9a4` で直した。記録は `.workbench/code-review/iss-00551/`。
- 最終品質ゲート（quality-gate-reviewer opus/high、1人、`996652619`）：
  - レビューの側：合格。coverage_complete、P0 0、P1 0、P2 0、P3 1。
  - テストの側：合格。`make lint` は終了コード0。`uv run pytest` は終了コード0（3610 passed、7 skipped、33分58秒）。
  - 試行1（`863c0a9a4`）は `test_issue413_assets.py` の件数の2件が失敗したので、期待値を直して試行2をやり直した。記録は `.workbench/final-quality-gate/iss-00551-g1/closure.md`。ChatGPT のレーンは使っていない（無効）。
- `spec-dock scope check iss-00551`：誤り0、警告0。
- PR：https://github.com/chemitaro/spec-dock/pull/561（head `996652619`）。CI（Actions と Commit Status）は通過、GitHub は MERGEABLE／CLEAN（2026-11-04T07:34Z の観測）。マージは利用者が行う。`work finish` は未実行。

## Residual Risks / Follow-ups

- ゲートの情報だけの指摘（直していない）：P3、`canonical.md` の `TODO_REGISTRY_UNREADABLE` の次の1手が、CLI の `spec-dock canonical status` と少し違う（`dashboard list` と `canonical link` を案内している）。
- iss-00549、iss-00550 とは別の Issue（#535、#552 など）が、`static-inventory.json` と共通の文書を変えるときは、後にマージするほうが取り込み直して sha256 を計り直す。

次の版の移行の注記に要る契約の変更（iss-00553 の `migration.md` 向け）：
- コマンドと契約は変わらない（コマンドの数は71のまま）。
- 配布の文書とスキルが変わる：`docs/todo.md` が新しく入る（配布物が1つ増える）。`SKILL.md`、`docs/README.md`、`docs/guide.md`、`docs/canonical.md` が変わる。各リポジトリでは `installation update` で入れ替わる（`installation uninstall` が退役させる配布物の数も1つ増える）。
