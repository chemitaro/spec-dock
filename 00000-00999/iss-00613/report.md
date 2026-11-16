---
種別: レポート（Issue）
ID: "iss-00613"
関連GitHub: ["#613"]
最終更新: "2026-11-16"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## Residual Risks / Follow-ups

## レビュー記録

- 2026-11-16 仕様レビュー round-1（spec-reviewer opus / high、standard）：**合格**（P0 0、P1 0、P2 1、P3 1）。結果 `.workbench/spec-review/iss-00613/round-1.json`、検査 `round-1.check.json`（valid、status pass）。worktree は iss-00613 の作業ツリー。
  - 合格した文書の sha256：requirement.cue `441a8c203fed6b7376cf50c3b360436a1322fe75149668c53b00db445d8195fa`、design.cue `5e568ea7c724d40429b3c5df102cf681045410f62a46623a5f0ce3c415e1f838`、plan.cue `dcb412467eaaba85f8b31818fef66e3abb81ae411852923c75d900782c269521`。
  - P2（同じ道の2つの出すリポジトリの中の子で、親の候補が同じ長さになりうる）と P3（T-07 が文書の決め方と道を返さないことを確かめる対象に含まない）は記録だけ。P2 は実装の裁量として、同じ長さなら `shown` の並びの先のものを採る（決まった結果にする）よう実装担当に伝える。
- 開始のコミット `2c7427a97ff97bd3b7ffc463401f3cffffab36e1`。
- 逸脱 codex-symlink-refusal（タスク担当の記録）：impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_153998eba943、launch.effective codex / gpt-6.1-sol / medium）は、手元のコマンドの実行の前に chat-scratch の writable root の symlink による UnsupportedOperation で止まり、変更なしで escalation を返した。plan の rationale と統括の了承どおり、待たずに worker-stop し、Claude Opus 5.5 / medium（dispatch ctx_2ba710432d6b、launch.effective claude / claude-opus-5-5 / medium）に切り替えた。

## 実装の記録

実装担当：Claude Opus 5.5 / medium（impl-sol の代わり、dispatch ctx_2ba710432d6b）。開始のコミット `2c7427a97ff97bd3b7ffc463401f3cffffab36e1`（clean、仕様の sha256 は合格の値と一致）。

- 基準（開始時）：`make lint` 合格。`uv run pytest tests/unit/application` 275 passed（25.6秒）。
- S-01（Red）`8030dc000`：`tests/unit/application/test_dashboard_nesting.py`（T-01〜T-05、12件）と `tests/unit/application/test_dashboard_repositories_nesting.py`（T-06、7件＋ realpath が読み直しの1回だけであることの確かめ）。開始のコミットでは `dashboard_nesting` がなく、集めの段で落ちることを確かめた。
- S-02（Green）`034f2c51c`：`runtime/application/dashboard_nesting.py`（D-01）、`DashboardSite` の `_Listing.nesting` と `nested_repositories()`（D-02）、`_repositories` の `parent`・`tier`（D-03）。新しいテスト 20 passed、`tests/unit/application` 295 passed（27.7秒）、`make lint` 合格。
  - 判断（仕様レビューの P2）：同じ道の2つの出すリポジトリの中の子は、`shown` の並びの先のものを親にする（長さが真に長いときだけ親を替える）。テスト `test_a_child_of_two_repositories_at_the_same_path_takes_the_first_shown` を足した。
  - 判断：絶対の道かは `Path(...).is_absolute()` で見る（ruff の PTH 規則）。正規化は設計どおり `os.path.realpath`。
- S-03 `6252dbef8`：配る側の `reference_cli.md` の API の項目に `parent`・`tier`・決め方・道を返さないことを足し、`static-inventory.json` の sha256 を `249f76e9…37cf33` に、前の `4c4bbf4a…69e1` を `known_old_sha256` に足した。T-07 は `tests/unit/infra/test_issue613_repository_nesting_docs.py`（仕様レビューの P3 の決め方と道を返さないことの文も確かめる）。`make lint` 合格。
  - 全体の `uv run pytest`：3 failed、3981 passed、7 skipped（3149秒）。失敗の3つ（`test_issue550_todo_aggregate.py::test_the_shipped_reference_and_the_help_name_the_new_contract`、`test_issue440_release_0_5_0.py` と `test_issue513_release_0_5_1.py` の `…dogfood_copy_matches`）は、dogfood の写し `spec-dock/docs/reference_cli.md` が配る側と同じバイトであることを求める既存のテスト。仕様は写しの更新を範囲外にしているため、タスク担当を通して統括に相談した。
- 逸脱と判断 dogfood-copy-sync `275a5f79c`：統括の決定（msg_22f5fbc7ac2b、(a)）により、この1ファイルに限り範囲を広げ、dogfood の写し `spec-dock/docs/reference_cli.md` を配る側と同じバイトにした。理由は、写しと配る側の一致を求める既存のテスト3件（上の失敗）。前例は `0bfa2424f`、`787a05147`（写しも同じ変更で合わせていた）。開始のコミットで2つは同じバイトだったことを確かめた。
  - 落ちた3件（と T-07、0.5.0・0.5.1 のテストの残り）18 passed。`make lint` 合格。
- 判断（統括、2026-11-17、msg_22f5fbc7ac2b）：配る側の `reference_cli.md` を変えると、dogfood の写しと配る側の一致を求める既存のテスト3件が落ちるため、写し `spec-dock/docs/reference_cli.md` を配る側と同じバイトにコミットする（前例 0bfa2424f・787a05147）。requirement の excludes と依頼書の範囲から、この1ファイルに限って外れる逸脱として、統括が了承した。
  - 写しを合わせた後の全体の `uv run pytest`（HEAD `275a5f79c`）：3984 passed、7 skipped（1952.8秒）。S-03 を done にした。

## 実機の確かめ（S-04、タスク担当）

- 候補 `ee33f0679`（origin/main の iss-00611 を取り込んだ後）を `git archive` で書き出して wheel にし、隔離した venv（作業ツリーの `.workbench/iss-00613/real/venv`、spec-dock 0.9.4 の版の表示のまま）に入れた。この PC の状態の置き場から登録簿（9行）と `catalogs/` を一時の置き場 `.workbench/iss-00613/real/state` に写し（隠す印のファイルはこの PC にない）、`spec-dock dashboard serve --port 18613 --offline --state-root <一時の置き場>` で立てた。常駐のダッシュボード（47800）と道具の環境には触れていない（確かめの後も 47800 は同じ PID で待ち受けていた）。確かめの後に 18613 のサーバーを止めた。
- `GET /api/v1/repositories` の結果（`unknown_count` 0、9つ、並びは鍵の順で今と同じ）：

| リポジトリ（github.com/chemitaro/…） | parent | tier |
|---|---|---|
| company-os | null | [] |
| generic-mona | input-devices | [プロダクト] |
| housing-lifecycle | company-os | [事業] |
| input-devices | company-os | [事業] |
| orca-web | null | [] |
| spec-dock | null | [] |
| taikyohiyou_project | housing-lifecycle | [プロダクト] |
| tenting-cradle | input-devices | [プロダクト] |
| yubisaki | input-devices | [プロダクト] |

- 道が出ないこと：応答の JSON に `/Users/`、`/Volumes/`、`/private/`、`.canonical`、`workspace` の文字が0件。登録簿の9行の `catalog`・`main_checkout`・`git` の値（27個）も、応答に1つも現れなかった。

## 最終品質ゲート

- origin/main（iss-00611、PR #618、`d9bb6164d`）を取り込んだ `ee33f0679` を候補にした（取り込んだ変更は dashboard の layout.js と graph のテストだけで、この Issue の範囲と重ならない）。
- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `2c7427a97..ee33f0679`、観点 functional-correctness・requirements-closure・test-adequacy・security-baseline。plan の `security` は security-baseline として扱った）：**合格**（attempt 1）。P0〜P3 すべて0、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3998 passed / 7 skipped、1718.57s）。closure は作業ツリーの `.workbench/final-quality-gate/iss-00613-fqg-1/closure.md`。

## Outcome

`GET /api/v1/repositories` の各リポジトリが、今の7つの項目の後ろに `parent`（いちばん近い出す祖先の鍵か null）と `tier`（段の札の配列）を返す。決め方は純粋な関数 `runtime/application/dashboard_nesting.py` の `repository_nesting` 1か所で、`DashboardSite` が一覧を読み直すときに1回だけ道を正規化して覚える。応答に道は出ない。配る側の `reference_cli.md` の契約、目録の sha256、dogfood の写しを合わせた。画面は変えていない（iss-00614）。

## Verification

- 単体・HTTP のテスト（`test_dashboard_nesting.py`、`test_dashboard_repositories_nesting.py`、`test_issue613_repository_nesting_docs.py`）、`make lint`、全体の `uv run pytest`（最終品質ゲートで 3998 passed）。
- 実機：上の「実機の確かめ」。

## Residual Risks / Follow-ups

- 大文字と小文字を区別しないファイルシステムで、登録の道の大文字が違うと親子を見落としうる（平らに出るだけ。design.cue の risks）。
- 絶対の道でない行の中のものは、さらに外の出す祖先から札を数えるので、その行のディレクトリの名前が札に出る（F-05 の仕様どおり。実際の登録では起こらない）。
- 次：iss-00614（画面）が `parent`・`tier` を読む。

## PR と CI

- PR #619（https://github.com/chemitaro/spec-dock/pull/619）、head `ee33f0679`（合格したコミット。記録だけのコミットはない）。CI（watch-pr-checks の最終の観測）：observable_ci PASS、merge_readiness READY（Provider CI、SpecDock check、Commit identity すべて success）。マージは統括が行う。
