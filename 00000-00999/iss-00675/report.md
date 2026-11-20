---
種別: レポート（Issue）
ID: "iss-00675"
関連GitHub: ["#675"]
最終更新: "2026-11-20"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high、standard、固定 04963648b）：合格。P0 0、P1 0、P2 0、P3 1（0.9.9 の節の注が『これから』の `Unscoped` の行の変化を示さない。配るバイトの説明の欠けなので直した、c447b4433）。結果 `.workbench/spec-review/iss-00675/round-1.json`、応答 `review-response.md`。
- 仕様のレビュー round-2（同じレビュアー、固定 c447b4433、S-01 の後、clean）：**合格**。P0〜P3 0。結果 `round-2.json`、検査 `round-2.check.json`（valid、status pass）。
- 合格した文書の sha256：requirement.cue `dd5cbde1e923cbd9d0c6efe9d8d9a874f15228da42daf9417b562f0f817e42db`、design.cue `9b1880b7d1a01bdbef5634b9b9ec9e0f78a4e25542130b36a53832de24cc344f`、plan.cue（S-01 の status を done にした後）`f667d2d0a03ae9b40378c61df34d30e1e0f72dc193f3d622d1403f0a715e0bb5`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.10 のリリースの変更を作った（`git diff a6000d8cd 44cad5e3c`、13ファイル）。機能のコードは変えていない。

- S-01（タスク担当）：`migration.md`（提供側と dogfood はバイト一致）の「## 0.9.9 への更新」の直後に「## 0.9.10 への更新」を足し、0.9.9 の節の『これから』の項目の直後に 0.9.10 の注を1項目足した（04963648b、仕様のレビューの P3 の直し c447b4433）。中身は iss-00673・iss-00674・iss-00676 の report.md の案内の文と `git diff v0.9.9 a6000d8cd`。0.9.9 からは配布資産が4つ（canonical.md、reference_cli.md、migration.md、版のファイル）変わる。
- S-02（実装担当、96f55fc71）：版を 0.9.10 にし（`pyproject.toml`、`uv.lock`、版のファイルの提供側と dogfood）、`test_issue670_release_0_9_9.py` の版固定を外した。
- S-03（実装担当、44cad5e3c）：`static-inventory.json` の2行の `sha256` を今のハッシュ（migration.md `5a8a1108…`、版のファイル `cd8f34a6…`）にし、v0.9.9 のバイトのハッシュ（`3c636c95…`、`050990d5…`）を `known_old_sha256` の末尾に足した。canonical.md と reference_cli.md の行は #677 のまま。fixture `tests/fixtures/issue675/` の4つは v0.9.9 のタグのバイトと一致する（タスク担当が `cmp` で確かめた）。統合テスト `tests/integration/test_issue675_release_0_9_10.py`（版、節の語、0.9.9 の節は注の1行だけが増えたこと、inventory、0.9.9 の consumer の `installation update` で4つだけ変わる）。
- S-04（タスク担当）：`git archive 44cad5e3c` から作った wheel（sha256 `1c83f8a1757f0ed52dc208e060be5e5ac895da86bb41e749f253b66fab9114bb`）を隔離した一時の venv に入れ、`spec-dock --version` が `spec-dock 0.9.10` を返した。同じ venv で `canonical check --dry-run --offline` が、この worktree（0.9.10）、spec-dock の main のチェックアウト（版のファイル 0.9.9）、orca-web と company-os（0.9.0）で valid=true、failures=0。道具の環境は 0.9.9 のまま。

### 実装担当

- Codex GPT-6.2 Sol / medium（launch.effective：codex・gpt-6.2-sol・medium、計画と一致）。確認の画面で止まらず、S-02・S-03 を1回で終えた。
- 基準（c447b4433）：リリースの統合テストで、S-01 で migration.md のバイトが変わったことによる既知の失敗 30 件。実装後：指定の11ファイル 35 passed、ほかのリリースの統合テスト 15 passed、`uv lock --check`、`make lint` 合格。

### マージの後の配布の手順（統括）

0.9.9 の実際の手順から書いた。根拠：v0.9.9 は PR #671 のマージのコミット 83b8ee95f を指す軽量タグ（`git for-each-ref refs/tags/v0.9.9` が commit 型）で、`.github/workflows/release-tag.yml` の run 44492637365（2026-11-19T09:01Z、success）が自動で作った。uv tool の receipt の wheel は、iss-00670 の report.md の手順で v0.9.9 から作った `spec_dock-0.9.9-py3-none-any.whl`。

1. タグ：この PR をマージすると、`release-tag.yml`（main への push で `pyproject.toml` の版の変化を見る）が `v0.9.10` を**自動で**そのマージのコミットに作る。手でタグを作らない。`git fetch --tags origin` の後に `git rev-parse v0.9.10^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.10 <マージのコミット>` と `git push origin refs/tags/v0.9.10`。
2. wheel：タグのきれいな取り出しから作る。`mkdir -p /private/tmp/spec-dock-v0.9.10-src && git archive --prefix=src/ v0.9.10 | tar -x -C /private/tmp/spec-dock-v0.9.10-src`、続けて `cd /private/tmp/spec-dock-v0.9.10-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.10-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.10-dist/spec_dock-0.9.10-py3-none-any.whl`、`spec-dock --version` が `spec-dock 0.9.10`。リリースしたタグの wheel だけを入れる。常駐のダッシュボードは60秒ごとの版の確認で自動で起動し直す。画面で、『これから』で指揮の線が出て子の数の札がないこと、エージェントの種類が名前で出ること（Antigravity・Gemini は orca-web main `4ad7471` 以降）を確かめる。Antigravity を使うなら、作業用のworktreeで `spec-dock canonical status` の `tools.antigravity` を見て、示された1行をユーザーの設定に足す（利用者が手で）。
4. 各リポジトリの `installation update`：**必須ではない**。
   - 0.9.10 の inventory は 0.9.9〜0.9.0 のバイトを `known_old_sha256` で受け入れる。S-04 で、版のファイルが 0.9.9（spec-dock の main）と 0.9.0（orca-web、company-os）のチェックアウトが 0.9.10 の wheel で valid=true になることを確かめた。
   - 機能はパッケージ（ランタイムと画面）が届ける。配布資産で変わるのは文書（canonical.md の Antigravity の項、reference_cli.md の C45、migration.md）と版のファイルだけ。
   - 各リポジトリの手元の `docs/canonical.md` に Antigravity の案内を載せたいとき、または版をそろえたいときだけ、パッケージを 0.9.10 にしてから各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする。この repo の dogfood は、この PR で 0.9.10 になる（canonical.md と reference_cli.md は #677 で済み）。

### 次の版の移行の注記に要る契約の変更

なし。

## Verification

- 最終品質ゲート iss-00675-fqg-1 attempt 1（44cad5e3c）：**合格**。
  - レビュー（quality-gate-reviewer opus / medium、second opinion なし）：P0〜P3 0、coverage complete。範囲は `a6000d8cd..44cad5e3c`。
  - `make lint`：exit 0。`uv run pytest`：exit 0（4444 passed / 7 skipped、56分19秒）。
  - closure：worktree の `.workbench/final-quality-gate/iss-00675-fqg-1/closure.md`（Git の外）。
  - 区切りのレビューは、計画どおりなし。記録だけのコミットはない（記録は Git の外）。
- PR #680（https://github.com/chemitaro/spec-dock/pull/680）：head は 44cad5e3c（合格のコミット）。記録のコミットはない。CI は合格。observer の結果は exit 0、observable_ci PASS、merge_readiness READY、mergeStateStatus CLEAN（2026-11-20T08:24Z UTC）。マージは統括。

## 逸脱と判断

- 仕様のレビューの P3（round-1）も、配るバイトの説明の欠けなので、直してから合格させた。
- 逸脱なし（実装担当は計画どおり Codex GPT-6.2 Sol / medium）。

## Residual Risks / Follow-ups

- `work finish iss-00675` は実行していない（マージの後に統括が行う）。
- マージの後のタグの確かめ、wheel、導入、必要なら配布資産の更新は、統括が行う（上の手順）。
