---
種別: レポート（Issue）
ID: "iss-00609"
関連GitHub: ["#609"]
最終更新: "2026-11-16"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：**合格**。P0 0、P1 0、P2 0、P3 0。結果 `.workbench/spec-review/iss-00609/round-1.json`、検査 `round-1.check.json`（valid、status pass）。固定したコミット 5b87bbd32（S-01 の後、clean）。
- 合格した文書の sha256：requirement.cue `f548639fd5bf093f6189119bf63e1dc851c1ced792ca6de9b33edce58e0ccb84`、design.cue `d3c9258cf44b56946a020a8f34f0aa5aec22b7cfb6906397121dbd7d7029c73f`、plan.cue `674b9181980fb722d746879ee73a48243e3e59a244d6b946f37e00c7122ffca2`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.4 のリリースの変更を作った。機能のコードは変えていない。マージ、タグ、導入、配布は統括が行う。

- S-01（タスク担当、5b87bbd32）：`migration.md`（提供側と dogfood の写しはバイト一致）の「## 0.9.3 への更新」の直後に「## 0.9.4 への更新」を足した。`git log --first-parent v0.9.3..origin/main` は PR #604・#605（iss-00602）、#606（iss-00603）、#608（iss-00607）。節には、道具の帯の変更（「終わったものも」「片付けの候補を畳む」「待っている線｜すべての線｜線なし」がなくなり「全体｜いま｜これから」と「収める」になる。各範囲の意味、線はいつもすべての線）、保存のキー `specdock.graph.v3` と版2からの移し替え（showDone が真なら全体、それ以外はいま、fold と線の選びは捨てる、版1は mode と legend だけ）、エージェントのタブの直し（iss-00602 の report.md の5点と欄の足のリンク）、契約の変更がないこと、変わる配布資産は3つ（migration.md、版のファイル、#604・#605 で変わった reference_cli.md）、更新、自動の起動し直し、戻し方を書いた。根拠は iss-00602・00603・00607 の report.md と仕様、`git show v0.9.3` と今の graph.js・graph/prefs.js。統括の訂正（msg_deb57611cc88）どおり、節の中身は依頼書の「必ず書くこと」に従った。
- S-02（実装担当、e06e70ddc）：版を 0.9.4 に（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood）。`test_issue599_release_0_9_3.py` の版固定を外した。
- S-03（実装担当、112bbff13）：`static-inventory.json` の2行の `sha256` を今のハッシュ（migration.md `47902bb9…`、版のファイル `a61cc7a9…`）にし、v0.9.3 のバイトのハッシュ（`8c598cf0…`、`38ecaa1e…`）を `known_old_sha256` に足した（reference_cli.md の行は #604 で済みのため変えない）。fixture `tests/fixtures/issue609/`（3つ。v0.9.3 のタグのバイトと一致することをタスク担当が `cmp` で確かめた）、統合テスト `tests/integration/test_issue609_release_0_9_4.py`（0.9.3 の consumer が3つのファイルだけ変わって上がる）。
- S-04（タスク担当）：コミット 112bbff13 の `git archive` から `uv build --wheel` で作った wheel（sha256 `921a1b4b…3a2e`）を隔離した venv（`/private/tmp/spec-dock-iss00609-1794824985/venv`）に入れ、`spec-dock --version` が `spec-dock 0.9.4`。同じ venv で、この worktree と orca-web（版のファイル 0.9.0）の `canonical check --dry-run --offline` が valid=true、failures=0。道具の環境（uv tool）は 0.9.3 のまま。

### 実装担当

- 初めに Codex GPT-6.1 Sol / medium（dispatch ctx_fe2e2216dbb7、launch.effective：codex・gpt-6.1-sol・medium）を起動した。Codex は chat-scratch の書き込み先がシンボリックリンクの下にある拒否（symlinked writable roots are not supported）でふつうのコマンドを実行できず、ファイルを変えずに止まった。**逸脱（計画の取り決め、統括が了承済み）**：worker-stop し、HEAD が 5b87bbd32 のままで未コミットがないことを確かめ、Claude Opus 5.5 / medium（dispatch ctx_3dc6e1ebc9e8、launch.effective：claude・claude-opus-5-5・medium）に切り替えた。plan.cue の status はタスク担当が書いた。

### マージの後の配布の手順（統括）

0.9.3 の実際の手順（v0.9.3 = PR #600 のマージのコミット 16f0cf122 に `release-tag.yml` が自動で作ったタグ（Release tag の run 43628327570、成功）、uv tool の receipt の wheel `/private/tmp/spec-dock-v0.9.3-dist/spec_dock-0.9.3-py3-none-any.whl`、iss-00599 の report.md）から：

1. タグ：PR をマージすると、`.github/workflows/release-tag.yml`（main への push で `pyproject.toml` の版が変わり、タグがなければ、そのマージのコミットに `v<版>` を作って push する）が `v0.9.4` を**自動で**作る。統括は手でタグを作らず、`git fetch --tags origin` の後に `git rev-parse v0.9.4^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.4 <マージのコミット>`、`git push origin refs/tags/v0.9.4`。
2. wheel：タグのきれいな取り出しから作る。`mkdir -p /private/tmp/spec-dock-v0.9.4-src && git archive --prefix=src/ v0.9.4 | tar -x -C /private/tmp/spec-dock-v0.9.4-src`、`cd /private/tmp/spec-dock-v0.9.4-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.4-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.4-dist/spec_dock-0.9.4-py3-none-any.whl`、`spec-dock --version` が `spec-dock 0.9.4`。常駐のダッシュボードは60秒ごとの版の確認で自動で起動し直す（`dashboard service install` は要らない）。リリースしたタグの wheel だけを入れる。画面（http://100.85.74.8:47800/）で、構造の図の道具の帯が「全体｜いま｜これから」と「収める」になり、前の「終わったものも」の選びが範囲に移ったことを確かめる。
4. 各リポジトリの `installation update`：**必須ではない**。理由：0.9.4 の inventory は 0.9.3〜0.9.0 のバイトを `known_old_sha256` で受け入れるので、今の配布資産のままで 0.9.4 の `canonical check` は通る（S-04 で、版のファイル 0.9.0 の orca-web が 0.9.4 の wheel で valid=true を確かめた）。変更はパッケージが配る画面にあり、配布資産の更新なしで届く。0.9.1〜0.9.3 のときも各リポジトリは更新せず、company-os と orca-web の版のファイルは 0.9.0 のまま（2026-11-16 に確かめた）。版をそろえたいとき（配る文書の migration.md と reference_cli.md を新しくしたいとき）だけ、PC のパッケージを 0.9.4 にしてから、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする。この repo の dogfood は、この PR で 0.9.4 になる。

### 次の版の移行の注記に要る契約の変更

なし。

## Verification

- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `3d5ff4961..112bbff13`）：**合格**（attempt 1）。P0〜P3 0、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3962 passed / 7 skipped、28分）。closure `.workbench/final-quality-gate/iss-00609-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00609`）。区切りのレビューは計画どおりなし。
- 実装担当の報告：対象の統合テスト5ファイル 16 passed、`make lint`、`uv lock --check` 合格、全体 3962 passed / 7 skipped。
- wheel：隔離した venv で `spec-dock --version` が `spec-dock 0.9.4`（Outcome の S-04）。
- PR #610（https://github.com/chemitaro/spec-dock/pull/610、head 112bbff13 = 合格のコミット、記録のコミットなし）：CI 合格（observer の結果 OBSERVED_CI_PASS、merge_readiness READY、2026-11-16T11:18Z UTC、`.workbench/coding-task/iss-00609/ci.json`）。

## 逸脱と判断

- 実装担当を Codex から Claude Opus 5.5 / medium に切り替えた（上の「実装担当」）。
- 依頼書の「手本」の行の誤り2点は統括の訂正（msg_deb57611cc88）に従った。

## Residual Risks / Follow-ups

- `work finish iss-00609` は実行していない（マージの後に統括が行う）。
- マージの後：タグの確かめ、wheel、導入、必要なら配布資産の更新は統括が行う（上の手順）。
