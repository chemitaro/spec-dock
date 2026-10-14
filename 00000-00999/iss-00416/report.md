---
種別: レポート（Issue）
ID: "iss-00416"
タイトル: "Restore Active Scope Links For Human Navigation"
関連GitHub: ["#416"]
最終更新: "2026-10-14"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00080", "init-00079"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

- `work start` の成功後、`active clear`（選択が空になったとき）、選択を解除した `work finish` の後、`active set @current` で、Git 無視の相対リンク `spec-dock/active/{initiative,epic,issue}` を直接対象の連鎖、または `system/active-none/<role>` に揃えるようにした。
- リンクの結果は `active.link` の effect と `ACTIVE_LINK_NOT_UPDATED` の warning で報告する。失敗は warning だけで、選択の status / exit は変わらない（Q1）。
- 書くのは3つのリンク名だけ。実体の同名ファイル・ディレクトリ、`active` 自体の symlink、Git に無視されない `active/` には書かない。旧 writer の既知生成物（`context-pack.md`、`current-runbook.{json,md}`、`{initiative,epic,issue}.path`）を含め、役割名以外は変更・削除しない（Q4、FQG-416-007 を受けて削除から変更）。
- provider 資産（`system/README.md`、`system/active-none/README.md`、`docs/reference_cli.md`、`docs/cli-redesign-guide.html`、installed skill `spec-dock`）と catalog の説明を更新し、`static-inventory.json` の sha256 と `known_old_sha256` を更新した。
- 未使用の旧 active テキスト renderer（`cli_text.render_active_{show,set,clear}_text`）を除去した。
- `branch switch` も clone の Start lock を取ってから checkout し、確認まで保持するようにした（Q5、RQ-416-07）。取れなければ `START_LOCK_BUSY`（exit 3）で何も変えずに止まる。`--lock-timeout` を `branch switch` でも受け付ける。これで SpecDock の checkout とリンク同期が重ならない。lock は `.git` を読み取り専用で開いた `flock` だけで、Git にファイルや設定を書かない。同じ Issue・ノードの重複選択は、従来どおり Start lock の中の全 worktree 観測（`SCOPE_ALREADY_SELECTED`、Scope ID と GitHub 番号で比較）で SpecDock が防ぎ、同じ branch の重複は Git に任せる。Issue 413 の「排他は Start だけ」はこの範囲に広げた。
- Issue 413 設計 D-01 の「第二の閲覧状態を増やさない」のうち、人間の閲覧手段を廃止した部分を本 Issue で上書きした。リンクは選択判定に読まれないため、選択状態は増えていない。AC-413-36 の保全は維持した。

## Verification

- TDD（Red → Green）: domain 2件、infra 11件、CLI 10件の新規テスト（`tests/unit/{domain,infra}/test_active_links.py`、`tests/cli_runtime/test_issue416_active_links.py`）。
- Q5（Red → Green）: `tests/cli_runtime/test_issue416_branch_lock.py`（option の受理・拒否、lock 保持中の `branch switch` が `START_LOCK_BUSY` で branch・作業ツリー・`.git` のファイル集合を変えないこと、dry-run は lock を取らないこと、lock が空けば checkout すること）と、`branch switch` の checkout 中のリンク修復が `start_in_progress` で書かないことのテスト（`7e37b754` では失敗することを確認）。
- fresh wheel（Q5、`/private/tmp/spec-dock-416q5`）: 別 process が `.git` に `flock` を保持している間の `branch switch --lock-timeout 0` が exit 3 `START_LOCK_BUSY`、effects 空、branch 不変、`.git` 配下のファイル集合不変。解放後は `succeeded`。`branch create --lock-timeout` は exit 2。
- `make lint`: ruff check / format / mypy が成功。
- `uv run pytest`（Q5 実装後の `30a3de21` のコード）: 1954 passed、1 skipped。
- `uv run pytest tests/unit tests/cli_runtime`: 1686 passed、1 skipped（実装途中の snapshot。最終 candidate の全体結果は PR に記録する）。
- fresh wheel（`spec_dock-0.2.4`）の外部 console を、`gh` stub を使う hermetic consumer で実行: `work start` で3リンク作成と `git status` clean、`workspace validate` 成功、`active set @current` で欠けたリンクの修復と `context-pack.md` の不変（Q4 変更後に再確認）、2回目は `unchanged`、`active clear --all` で fallback へ戻ることを確認した。
- dogfood: 候補 console の `active set @current` をこの worktree で実行し、`spec-dock/active/issue` が本 Issue を指すこと、`workspace validate` が成功し追跡ファイルが変わらないことを確認した。
- 既存のリンクを置いた状態で、インストール済み console の `workspace validate`、`workspace doctor`（`--raw` 含む）、`workspace sync`、`scope list`、`installation show` が成功し、Scope の重複が無いことを確認した。

## Final Quality Gate

- 1回目（`e7400e66`、GPT-6 Pro）: fail。P1 が3件、P2 が2件。
  - FQG-416-001（検査後の root 差し替えで外部へ書込・削除）: fd 起点の操作に変更して修正。
  - FQG-416-002（リンク先の観測エラーが選択の status / exit を変える）: 役割ごとの例外処理に入れ、application 層でも OSError を warning に変換して修正。
  - FQG-416-003（ignore 規則に一致する追跡ファイルを変更）: `git ls-files` による追跡確認を加えて修正。
  - FQG-416-004（P2、空選択の `clear --from` が修復しない）: AC-416-03 の未達なので修正。
  - FQG-416-005（P2、Start dry-run が checkout 前の path を使う）: 残余リスクとして記録（下記）。
- 2回目（`a9e2ec78`、同じ会話）: fail。前回の P1 3件は closed。新しい P1 が1件。
  - FQG-416-006（役割名の確認後に並行 Start が置いた実体をリンクで置換）: 書込が必要なときだけ Start lock を待たずに取り、その中で観測し直して書くように変更。古いリンクの置換は退避して確かめる方式にし、lock を取らない並行 writer の実体も置換・削除しないようにした。
- 3回目（`5f4a6515`、同じ会話）: fail。FQG-416-006 は closed。新しい P1 が1件。
  - FQG-416-007（旧生成物の削除が、Start lock を取らない並行 `branch switch` の置いた追跡ファイルを消し得る）: 名前と種類では区別できず、Git はファイルを書いてから index を更新するため確認の窓を閉じられない。利用者判断（2026-10-13）で Q4 を「旧生成物は削除しない」に変更し、削除処理を取り除いた。

- 4回目（`7e37b754`、同じ会話）: fail。FQG-416-007 は closed。新しい P1 が1件、P3 が1件。
  - FQG-416-008（Start lock を取らない並行 `branch switch` が置いた追跡済みの役割 symlink を、リンク同期が書き換え得る）: 利用者判断（2026-10-14、Q5）で、`branch switch` も Start lock を取るように変更した。Git には何も書かない方式を選び、`index.lock` 等は採用しなかった。
  - FQG-416-009（P3、plan step 5 に旧生成物削除の記述）: 既存 step を書き換えない方針に従い、plan 末尾の step 11 で訂正した。

## Residual Risks / Follow-ups

- `work start --dry-run` のリンク計画は、checkout 前の Scope path で評価する。候補 tip で Scope ディレクトリが移動している場合だけ、計画と本実行のリンク先がずれ得る（FQG-416-005）。本実行は候補 tip の path を使う。

- SpecDock を経由しない Git 操作（直接の `git checkout` など）と別 clone は排他の対象外（RQ-416-05、Q5）。別 clone 間で同じ Issue の選択を防ぐには、GitHub 上の宣言など別の仕組みが要る（必要なら別 Issue）。
- `branch switch` は、他の worktree の Start / switch が lock を持つ間、最大 `--lock-timeout`（既定5秒）待つ。
- 同じ worktree での並行操作や branch 切替の後、リンクが古くなる・dangling になることがある。`active set @current` または `active clear --all` で揃え直す。
- 旧 consumer には、旧 writer の古い `context-pack.md` などが残る。README で案内するが、利用者が不要なら手で消す。
- この worktree と他の dogfood worktree の静的投影（`spec-dock/system/`、`.agents/skills/`）は未更新。インストール済み package の更新（利用者判断）の後、`installation update` で反映する。
