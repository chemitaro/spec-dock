---
種別: レポート（Issue）
ID: "iss-00623"
関連GitHub: ["#623"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：合格。P0 0、P1 0、P2 1、P3 1（migration.md の『これから』の説明と入れ子の枠の印の位置。どちらも正しい指摘なので直した、6320fc92d）。結果 `.workbench/spec-review/iss-00623/round-1.json`。
- 仕様のレビュー round-2（同じレビュアー）：**合格**。P0〜P3 0。結果 `.workbench/spec-review/iss-00623/round-2.json`、検査 `round-2.check.json`（valid、status pass）。固定したコミット 6320fc92d（S-01 の後、clean）。
- 合格した文書の sha256：requirement.cue `065783af43cd99c117313f40d9f1d75579f84cd6dc7d3e67223abb5a2e95efb3`、design.cue `35e2072ba2c19bd8ba7ed8bfe4d7e8c2b608ee4622162c18c16a4f5b77a531df`、plan.cue `a7547592f708c8393d0ea8aff0e6933975dda8ea9397d8e81bbe39767757e43a`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.5 のリリースの変更を作った。機能のコードは変えていない。マージ、タグ、導入、配布は統括が行う。

- S-01（タスク担当、cd6e4caed、仕様のレビューの P2・P3 の直し 6320fc92d）：`migration.md`（提供側と dogfood の写しはバイト一致）の「## 0.9.4 への更新」の直後に「## 0.9.5 への更新」を足した。`git log --first-parent v0.9.4..origin/main` は PR #618（iss-00611）、#619（iss-00613）、#622（iss-00620）。節には次を書いた。
  - 『これから』：中に見える Scope がない親を出さない。子を持つ開いた子の中に見えるものがなければ、親も子も出ない。子のない開いた Scope、子のない開いた子孫を持つ親、focus は出る。
  - `GET /api/v1/repositories` の `parent`・`tier`：道は返さない。画面はまだ使わない。
  - エージェントの行：箱ではほかの印の下、入れ子の枠では見出しの下・要約の行の上に置く。上限と「+N」はなくなり、折り返して箱が縦に伸びる。『後に続く』は残る。ボードと横の欄は変わらない。
  - そのほか：契約の変更がないこと、変わる配布資産は3つ、更新、自動の起動し直し、戻し方。
- S-02（実装担当、9be5846fd）：版を 0.9.5 にした（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood）。`test_issue609_release_0_9_4.py` の版固定を外した。
- S-03（実装担当、1a3352430）：`static-inventory.json` の2行の `sha256` を今のハッシュにした（migration.md `9ea0ec4a…`、版のファイル `8780409d…`）。v0.9.4 のバイトのハッシュ（`47902bb9…`、`a61cc7a9…`）を `known_old_sha256` の末尾に足した。reference_cli.md の行は #619 で済んでいる。fixture は `tests/fixtures/issue623/` の3つで、v0.9.4 のタグのバイトと一致することをタスク担当が `cmp` で確かめた。統合テストは `tests/integration/test_issue623_release_0_9_5.py`。
- S-04（タスク担当）：`git archive 1a3352430` から `uv build --wheel` で wheel を作った（sha256 `38bbf32e…c7`）。隔離した venv（`/private/tmp/spec-dock-iss00623-1794858238/venv`）に入れて確かめた。
  - `spec-dock --version` が `spec-dock 0.9.5` を返した。
  - 同じ venv で、この worktree と orca-web（版のファイル 0.9.0）の `canonical check --dry-run --offline` が valid=true、failures=0 を返した。
  - 道具の環境（uv tool）は 0.9.4 のまま。

### 実装担当

- 初めに Codex GPT-6.1 Sol / medium（dispatch ctx_e8c10898f8f0、launch.effective：codex・gpt-6.1-sol・medium）を起動した。Codex は chat-scratch の書き込み先がシンボリックリンクの下にある拒否（symlinked writable roots are not supported）でコマンドを実行できず、ファイルを変えずに止まった。
- **逸脱（計画の取り決め、統括が了承済み）**：worker-stop し、HEAD が 6320fc92d のままで未コミットがないことを確かめてから、Claude Opus 5.5 / medium（dispatch ctx_930f46455e34、launch.effective：claude・claude-opus-5-5・medium）に切り替えた。plan.cue の status はタスク担当が書いた。

### マージの後の配布の手順（統括）

0.9.4 の実際の手順から書いた。根拠は次のとおり。
- v0.9.4 は PR #610 のマージのコミット 2c7427a97 に `release-tag.yml` が自動で作ったタグ。
- uv tool の receipt の wheel は `/private/tmp/spec-dock-v0.9.4-dist/spec_dock-0.9.4-py3-none-any.whl`。
- iss-00609 の report.md。

1. タグ：PR をマージすると、`.github/workflows/release-tag.yml` が `v0.9.5` を**自動で**作る。このワークフローは、main への push で `pyproject.toml` の版が変わり、その版のタグがなければ、そのマージのコミットに `v<版>` を作って push する。#618・#619・#622 のマージでも、このワークフローは成功し、版が変わらないのでタグを作らなかった。統括は手でタグを作らない。`git fetch --tags origin` の後に、`git rev-parse v0.9.5^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.5 <マージのコミット>` と `git push origin refs/tags/v0.9.5` を実行する。
2. wheel：タグのきれいな取り出しから作る。`mkdir -p /private/tmp/spec-dock-v0.9.5-src && git archive --prefix=src/ v0.9.5 | tar -x -C /private/tmp/spec-dock-v0.9.5-src` を実行し、続けて `cd /private/tmp/spec-dock-v0.9.5-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.5-dist` を実行する。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.5-dist/spec_dock-0.9.5-py3-none-any.whl` を実行し、`spec-dock --version` が `spec-dock 0.9.5` を返すことを確かめる。リリースしたタグの wheel だけを入れる。常駐のダッシュボードは、60秒ごとの版の確認で自動で起動し直す（`dashboard service install` は要らない）。画面（http://100.85.74.8:47800/）で次を確かめる。
   - orca-web の構造の図の「これから」で、init-00002 が中のない枠として出ない。
   - エージェントのいる箱で、稼働の印が専用の行に折り返して収まる。
   - `curl -s http://127.0.0.1:47800/api/v1/repositories` の各リポジトリに `parent`・`tier` がある。
4. 各リポジトリの `installation update`：**必須ではない**。理由は次のとおり。
   - 0.9.5 の inventory は 0.9.4〜0.9.0 のバイトを `known_old_sha256` で受け入れる。今の配布資産のままで 0.9.5 の `canonical check` は通る。S-04 で、版のファイルが 0.9.0 の orca-web が 0.9.5 の wheel で valid=true になることを確かめた。
   - 変更はパッケージが配る画面と API にあり、配布資産を更新しなくても届く。
   - 0.9.1〜0.9.4 のときも、各リポジトリは更新しなかった。

   版をそろえたいとき（配る文書の migration.md と reference_cli.md を新しくしたいとき）だけ、PC のパッケージを 0.9.5 にしてから、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする。この repo の dogfood は、この PR で 0.9.5 になる。

### 次の版の移行の注記に要る契約の変更

なし。

## Verification

- 最終品質ゲート：**合格**（attempt 1）。
  - レビュアー：quality-gate-reviewer opus / medium。second opinion はない。範囲は `7f7dd2b1d..1a3352430`。
  - 結果：P0〜P3 は0、coverage complete。
  - test lane：`make lint` exit 0、`uv run pytest` exit 0（4013 passed / 7 skipped、31分）。
  - closure：`.workbench/final-quality-gate/iss-00623-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00623`）。
  - 区切りのレビューは、計画どおりなし。
- 実装担当の報告：対象の統合テスト6ファイルで 19 passed。`make lint`、`uv lock --check` が合格。全体で 4013 passed / 7 skipped。
- wheel：隔離した venv で `spec-dock --version` が `spec-dock 0.9.5` を返した（Outcome の S-04）。
- PR #625（https://github.com/chemitaro/spec-dock/pull/625）：head は 1a3352430（合格のコミット）。記録のコミットはない。

## 逸脱と判断

- 実装担当を Codex から Claude Opus 5.5 / medium に切り替えた（上の「実装担当」）。
- 仕様のレビューの P2・P3（ブロックしない）も、配るバイトの事実の誤りなので直してから合格させた。

## Residual Risks / Follow-ups

- `work finish iss-00623` は実行していない（マージの後に統括が行う）。
- マージの後のタグの確かめ、wheel、導入、必要なら配布資産の更新は、統括が行う（上の手順）。
