---
種別: レポート（Issue）
ID: "iss-00437"
タイトル: "Migrate Spec Dock To Canonical Storage"
関連GitHub: ["#437"]
最終更新: "2026-10-25"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

spec-dock 自身を canonical モード（宣言の版4）に切り替えた（2026-10-30）。I-10 は統括のエージェントが利用者の前で行う Issue なので、要件・設計・計画は Epic の `plan.md` の「### I-10 Migrate Spec Dock To Canonical Storage」の節を正本とし、この Issue の `requirement.md`・`design.md`・`plan.md` は具体化していない。

- 切り替えの PR：#469（マージ `1c064f9ef`、2026-10-30T04:22Z）。`migrate.py cut` のコミット `47fedd982` で `spec-dock/initiatives/` を既定のブランチから外し（3123ファイル）、`build-canonical` が作った `spec-dock/canonical`（`61d1d0911`、265 Scope、リンク 502件を書き換え、書き換えられないリンク0件）を push した。宣言を版4にし、`spec-dock-check.yml`（`.github/scripts/specdock-ci-check.sh`）を足し、`ci.yml` を消した。
- マージの後、main のチェックアウトで取り込み、Git で追跡していなかったファイル126個を `move-local` でカタログへ移し、`canonical link` で定期の同期（LaunchAgent `io.github.chemitaro.spec-dock.canonical-sync`）を登録した。最初の同期と push の認証の確かめが成功した。
- 作業用の worktree：`spec-dashboard`（epic-00427）は取り込みとリンクまで済ませた。`local-macos-vm-ci`（#463）と `schema1-preserving-migration-20261004` は、ブランチのコードの変更が main とぶつかるので取り込みを中止し、版3のまま残した（仕様の中身はカタログに取り込み済み。片付けは epic-00512 の #514）。
- 切り替えの後の運用の振り返りで問題がなく、利用者が I-12（#439）に進むと決めた（2026-11-01）。

## Verification

- `migrate.py plan`（対象 `573902fd7`）：止める異常0。題名の食い違い35件は GitHub を正とし、ローカルの Scope 2件は #39 と新しい #468 に置き換え、#250 は閉じた #224 の下のままにした。
- 本物の GitHub で `register --apply`（695件の書き込み）と `verify`（不一致0）。凍結の後の再実行で、書き込み0、不一致0。
- 予行演習（写しのクローン、bare の origin、一時の `XDG_STATE_HOME`）：`build-canonical`、`cut`、取り込み、`move-local`、`canonical link --no-schedule`、`canonical sync`、`canonical check` が成功。`export-legacy` で戻した `.meta.json` 265件は、ローカルの ID の置き換えのほかに違い0件で、従来モードの `workspace validate` が通った。
- PR #469 の CI（`SpecDock check` ほか）が成功した（AC-12 の spec-dock の分）。
- 切り替えの後：`canonical status` の項目はすべて ok、構造の異常0件、`workspace validate` 成功。ダッシュボードが GitHub の題名（日本語を含む）で作り直されたことを確かめた（AC-17）。main のチェックアウトの外の worktree で Claude Code がカタログを読むための `~/.claude/settings.json` の1行は、利用者が足し、`canonical status` の `tools.claude_code` が `configured: true` になった。
- 運用の記録（`iss-00439/report.md` の「運用の点検」）：2026-10-30T04:23Z〜2026-11-02 の周期 3750 回はすべて ok、保存と push 117 回、遠くの変更の取り込み1回（成功）。
- ついでに確かめること（親子と依存の変更で Issue の `updated_at` が変わるか）：I-10 の登録のときには記録しなかった。2026-11-02 に、`scope move` で #506〜#511 の親を epic-00080 から #512 に付け替えた記録で確かめた。#506 は 10:08:27Z に `parent_issue_removed`、10:08:28Z に `parent_issue_added` があったが、`updated_at` は 08:35:48Z のまま変わらなかった。親の #512 も `sub_issue_added`（10:09Z）の後、`updated_at` は作成の時刻（10:07:46Z）のままだった。**親子の変更では Issue の `updated_at` は変わらない**。変わったかの確かめ（`updated_at` を見る）では親子の変更を見つけられないので、30分ごとの取り直しは今のまま要る（Epic の「未確認の事項」から外す）。依存（blocked by）の変更は確かめていない。

## Residual Risks / Follow-ups

- 版3のまま残した worktree 2つ（`local-macos-vm-ci`、`schema1-preserving-migration-20261004`）は、0.5.0 では中で SpecDock のコマンドが動かない。epic-00512 の #514 で、#463 の再開のしかたと合わせて扱いを決める。
- 依存（blocked by）の変更で `updated_at` が変わるかは確かめていない。30分ごとの取り直しが両方を拾うので、動きには影響しない。
- 本物の git 2.30〜2.33 での移行のスクリプトの確かめはしていない（スクリプトは 0.5.0 で撤去し、版のタグ `v0.4.2` に残る）。
