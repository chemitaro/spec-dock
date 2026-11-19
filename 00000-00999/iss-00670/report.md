---
種別: レポート（Issue）
ID: "iss-00670"
関連GitHub: ["#670"]
最終更新: "2026-11-19"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high、standard）：合格。P0 0、P1 0、P2 0、P3 1（『これから』では指揮していない worktree とエージェントのいない worktree が出ないことを 0.9.9 の節が書いていなかった。配るバイトの説明の欠けなので直した、bfc10313b）。結果 `.workbench/spec-review/iss-00670/round-1.json`、応答 `review-response.md`。
- 仕様のレビュー round-2（同じレビュアー）：**合格**。P0〜P3 0。結果 `.workbench/spec-review/iss-00670/round-2.json`、検査 `round-2.check.json`（valid、status pass）。固定したコミット bfc10313b（S-01 の後、clean）。
- 合格した文書の sha256：requirement.cue `244815af4c1d09f186a78e4588f63fd24e1828448b311ed04e882559d1ed2746`、design.cue `bf35aee670b200f740a56641b9ceaec3139f8d075f7a3d1b5e5ba6b49475ccaf`、plan.cue `bff170d5aeebbd933ffd4d5eb01dada01e5fc03fc4a71ce0b358f52d076756aa`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.9 のリリースの変更を作った（`git diff c2163d912 71384fa1e`、11ファイル）。機能のコードは変えていない。

- S-01（タスク担当）：`migration.md`（提供側と dogfood はバイト一致）の「## 0.9.8 への更新」の直後に「## 0.9.9 への更新」を足した（ccf197498、仕様のレビューの P3 の直し bfc10313b）。中身は iss-00668 の report.md の「移行の案内に書く文」（Unscoped の行、Primary・Unlinked、git worktree list、薄く畳む、『これから』の数、1つの worktree に1項目）と `git diff v0.9.8 c2163d912`。
- reference_cli.md は変えていない（『指揮の帯』も帯の札も書かれておらず、構造の API は契約にしない画面の中の JSON と書かれている）。
- S-02（実装担当、5e999d887）：版を 0.9.9 にし（`pyproject.toml`、`uv.lock`、版のファイルの提供側と dogfood）、`test_issue663_release_0_9_8.py` の版固定を外した。
- S-03（実装担当、71384fa1e）：`static-inventory.json` の2行の `sha256` を今のハッシュ（migration.md `3c636c95…`、版のファイル `050990d5…`）にし、v0.9.8 のバイトのハッシュ（`ae9e47b6…`、`ff35aa97…`）を `known_old_sha256` の末尾に足した。fixture `tests/fixtures/issue670/` の2つは v0.9.8 のタグのバイトと一致する（タスク担当が `cmp` で確かめた）。統合テスト `tests/integration/test_issue670_release_0_9_9.py`。
- S-04（タスク担当）：`git archive 71384fa1e` から作った wheel（sha256 `ed60a5583953277de60b36a7519b6d5091642575df2baf2499332a35a64345aa`）を隔離した venv（`/private/tmp/spec-dock-iss00670-1795074434/venv`）に入れ、`spec-dock --version` が `spec-dock 0.9.9` を返した。同じ venv で `canonical check --dry-run --offline` が、この worktree（0.9.9）、spec-dock の main のチェックアウト（版のファイル 0.9.8）、orca-web と company-os（0.9.0）で valid=true、failures=0。道具の環境は 0.9.8 のまま。

### 実装担当

- Codex GPT-6.1 Sol / medium（dispatch ctx_ad8ac60689d7、launch.effective：codex・gpt-6.1-sol・medium）。止まらずに S-02・S-03 を終えた（今回は sandbox の拒否なし）。方針の表の実装担当は GPT-6.2 Sol だが、依頼書（本人の指示 2026-11-13）の gpt-6.1-sol を使った。
- 基準（bfc10313b）：`test_issue663`・`test_issue645` で 4 failed / 3 passed（S-01 で migration.md のバイトが変わったことによる既知の失敗）。実装後：リリースの統合テスト10ファイルで 31 passed。`uv lock --check`、`make lint` は合格。記録 `.workbench/implement/iss-00670/start.md`。

### マージの後の配布の手順（統括）

0.9.8 の実際の手順から書いた。根拠：v0.9.8 は PR #666 のマージのコミット 1cfce6f96 を指す軽量タグ（`git for-each-ref refs/tags/v0.9.8` が commit 型）で、`.github/workflows/release-tag.yml` の run 44184615882（2026-11-17T21:54Z、success）が自動で作った。uv tool の receipt（`~/.local/share/uv/tools/spec-dock/uv-receipt.toml`）の wheel は `/private/tmp/spec-dock-v0.9.8-dist/spec_dock-0.9.8-py3-none-any.whl`。iss-00663 の report.md。

1. タグ：この PR をマージすると、`release-tag.yml`（main への push、`release-tag-decision.py` が `pyproject.toml` の版の変化を見る）が `v0.9.9` を**自動で**そのマージのコミットに作る。手でタグを作らない。`git fetch --tags origin` の後に `git rev-parse v0.9.9^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.9 <マージのコミット>` と `git push origin refs/tags/v0.9.9`。
2. wheel：タグのきれいな取り出しから作る。`mkdir -p /private/tmp/spec-dock-v0.9.9-src && git archive --prefix=src/ v0.9.9 | tar -x -C /private/tmp/spec-dock-v0.9.9-src`、続けて `cd /private/tmp/spec-dock-v0.9.9-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.9-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.9-dist/spec_dock-0.9.9-py3-none-any.whl`、`spec-dock --version` が `spec-dock 0.9.9`。リリースしたタグの wheel だけを入れる。常駐のダッシュボードは60秒ごとの版の確認で自動で起動し直す。画面で、構造の図と『横断の構造』の行の頭が `Unscoped` で先頭に `Primary`、Scope に紐づかない worktree が `Unlinked`、『これから』で線がなく数が付くことを確かめる。
4. 各リポジトリの `installation update`：**必須ではない**。
   - 0.9.9 の inventory は 0.9.8〜0.9.0 のバイトを `known_old_sha256` で受け入れる。S-04 で、版のファイルが 0.9.8（spec-dock の main）と 0.9.0（orca-web、company-os）のチェックアウトが 0.9.9 の wheel で valid=true になることを確かめた。
   - 変更はパッケージが配る画面と構造の API にだけあり、配布資産を更新しなくても届く。変わる配布資産は migration.md と版のファイルだけ。
   - 版をそろえたいときだけ、パッケージを 0.9.9 にしてから各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする。この repo の dogfood は、この PR で 0.9.9 になる。

### 次の版の移行の注記に要る契約の変更

なし。

## Verification

- 最終品質ゲート iss-00670-fqg-1 attempt 1（71384fa1e）：**合格**。
  - レビュー（quality-gate-reviewer opus / medium、second opinion なし）：P0〜P3 0、coverage complete。範囲は `c2163d912..71384fa1e`。
  - `make lint`：exit 0。`uv run pytest`：exit 0（4355 passed / 7 skipped、51分36秒）。
  - closure：`.workbench/final-quality-gate/iss-00670-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00670`）。
  - 区切りのレビューは、計画どおりなし。記録だけのコミットはない（記録は Git の外）。

## 逸脱と判断

- 仕様のレビューの P3（round-1）も、配るバイトの説明の欠けなので、直してから合格させた。
- 実装担当のモデル：方針の表（GPT-6.2 Sol）ではなく、依頼書の GPT-6.1 Sol を使った（本人の指示が優先）。

## Residual Risks / Follow-ups

- `work finish iss-00670` は実行していない（マージの後に統括が行う）。
- マージの後のタグの確かめ、wheel、導入、必要なら配布資産の更新は、統括が行う（上の手順）。
