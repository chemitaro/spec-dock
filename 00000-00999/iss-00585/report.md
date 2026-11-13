---
種別: レポート（Issue）
ID: "iss-00585"
関連GitHub: ["#585"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：**合格**。P0・P1・P2 なし、P3 1（D-04 の配布の手順の根拠に、main への push でタグを自動で作る `.github/workflows/release-tag.yml` がない）。結果 `.workbench/spec-review/iss-00585/round-1.json`、検査 `round-1.check.json`（valid、status pass）。P3 は文書を変えず、配布の手順（report.md）に反映する。
- 合格した文書の sha256：requirement.cue `15a4db888d8382664a46598f96bb4b4f09f1219ae9823e12c03091015db00661`、design.cue `106270847ebb3f031f9c2d324fb7f2db9981e639a70b925fd4e7b5d58c508e71`、plan.cue `7864e35ac16f4bd1bdf94385dc85aad3c74566cebbc73b361c029ddc8824a386`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.1 のリリースの変更を作った。機能のコードは変えていない。マージ、タグ、導入、配布は統括が行う。

- S-01（タスク担当、6b258977b）：`migration.md`（提供側と dogfood の写しはバイト一致）の「## 0.9.0 への更新」の直後に「## 0.9.1 への更新」を足した。`git log v0.9.0..origin/main` は PR #584（iss-00583）だけで、変わったのは dashboard の `layout.js`・`graph.js`（コメント）とテスト。節には、塊を先に置きつながりのない Scope を空きに詰めること、最上位も見える幅で折り返すこと（0.9.0 の節の「倍率が最大」を改める）、契約の変更がないこと、変わる配布資産は2つ、更新、自動の起動し直し、戻し方を書いた。
- S-02（実装担当 Codex、2891e8c19）：版を 0.9.1 に（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood）。`test_issue580_release_0_9_0.py` の版固定を外した。
- S-03（実装担当 Codex、61d7c3c99）：`static-inventory.json` の2行の `sha256` を今のハッシュにし、v0.9.0 のバイトのハッシュを `known_old_sha256` に足した。fixture `tests/fixtures/issue585/`（v0.9.0 のタグのバイトと一致することをタスク担当が `cmp` で確かめた）、統合テスト `tests/integration/test_issue585_release_0_9_1.py`。
- S-04（タスク担当）：コミット 61d7c3c99 の `git archive` から `uv build --wheel` で作った wheel（sha256 `07ac04a1…a6ee`）を隔離した venv（`/private/tmp/spec-dock-iss00585-1794611285/venv`）に入れ、`spec-dock --version` が `spec-dock 0.9.1`。同じ venv で、この worktree の `canonical check --dry-run --offline` が valid=true、failures=0。道具の環境（uv tool）は 0.9.0 のまま。

### 実装担当

- Codex GPT-6.1 Sol / medium（`worker-start` の `launch.effective`：agent codex、model gpt-6.1-sol、effort medium。dispatch ctx_7453e02d8931）。逸脱なし。
- 実装担当は plan.cue の status を Codex のサンドボックスで書けなかった（Operation not permitted）。タスク担当が書いた。

### マージの後の配布の手順（統括）

0.9.0 の実際の手順（v0.9.0 = PR #582 のマージのコミット 982932e47 の軽いタグ、uv tool の receipt の wheel `/private/tmp/spec-dock-v0.9.0-dist/spec_dock-0.9.0-py3-none-any.whl`、epic-00573 の report.md）から：

1. タグ：PR をマージすると、`.github/workflows/release-tag.yml`（main への push で `pyproject.toml` の版が変わり、タグがなければ、そのマージのコミットに軽いタグ `v<版>` を作って push する）が `v0.9.1` を**自動で**作る。v0.9.0 もこの流れ（Release tag の run 42151510479、成功）でできた。統括は手でタグを作らず、`git fetch --tags origin` の後に `git rev-parse v0.9.1^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、マージのコミットに `git tag v0.9.1 <マージのコミット>`、`git push origin refs/tags/v0.9.1`。
2. wheel：タグのきれいな取り出しから作る。例 `git archive --prefix=src/ v0.9.1 | tar -x -C /private/tmp/spec-dock-v0.9.1-src`、`cd /private/tmp/spec-dock-v0.9.1-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.1-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.1-dist/spec_dock-0.9.1-py3-none-any.whl`、`spec-dock --version` が `spec-dock 0.9.1`。常駐のダッシュボードは60秒ごとの版の確認で自動で起動し直す（`dashboard service install` は要らない）。画面（http://100.85.74.8:47800/）で構造の図を確かめる。リリースしたタグの wheel だけを入れる。
4. 各リポジトリの `installation update`：**必須ではないが、版をそろえるために勧める**。理由：0.9.1 の inventory は 0.9.0 の2つのバイトを `known_old_sha256` で受け入れるので、0.9.0 の配布資産のままでも 0.9.1 の `canonical check` は通る。構造の図の直しはパッケージが配る画面にあり、配布資産の更新なしで届く。ただし CI の見本は版のファイルの版の SpecDock を入れるので、更新しないと CI は 0.9.0 のまま（違いはダッシュボードだけで、CI の検査には影響しない）。0.9.0 のときと同じく、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする（0.9.0 では7つのリポジトリ、利用者がマージ）。PC のパッケージを 0.9.1 にしてから更新する（0.9.0 のパッケージは 0.9.1 の資産を知らない変更として止める）。

### 次の版の移行の注記に要る契約の変更

なし。

## Verification

- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `3055648c8..61d7c3c99`）：**合格**（attempt 1）。P0〜P3 すべて 0、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3772 passed / 7 skipped、30分）。closure `.workbench/final-quality-gate/iss-00585-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00585`）。区切りのレビューは計画どおりなし。
- 実装担当の報告：対象の統合テスト3ファイル 10 passed、`make lint`、`uv lock --check` 合格、全体 3772 passed / 7 skipped。
- wheel：隔離した venv で `spec-dock --version` が `spec-dock 0.9.1`（Outcome の S-04）。
- `spec-dock scope check iss-00585`：誤り0、警告0。

## Residual Risks / Follow-ups

- `work finish iss-00585` は実行していない（マージの後に統括が行う）。
- マージの後：タグの確かめ、wheel、導入、配布資産の更新は統括が行う（上の手順）。
