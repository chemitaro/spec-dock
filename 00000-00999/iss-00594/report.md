---
種別: レポート（Issue）
ID: "iss-00594"
関連GitHub: ["#594"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：不合格。P1 1（R-02 の主な語「仕様と報告」が節の文字列に無い）。requirement.cue の語を節の文「仕様（要件・設計・計画）と報告」に合わせて直した（`.workbench/spec-review/iss-00594/review-response.md`）。
- 仕様のレビュー round-2（同じレビュアー）：**合格**。P0〜P3 すべて 0。結果 `.workbench/spec-review/iss-00594/round-2.json`、検査 `round-2.check.json`（valid、status pass）。固定したコミット 8a5f71bad（S-01 の後）。
- 合格した文書の sha256：requirement.cue `173416d427c1e25b586a488078051048e767e0e76f71a5e8505521eff19e3fb1`、design.cue `126dfaf4e514a57a65c9458394b84bfd164d64215604564eca6fdf8901027209`、plan.cue `b1e73dad980c9fc235ecaa251900228a42270916c37dfe89d8831e8de19bc42c`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.2 のリリースの変更を作った。機能のコードは変えていない。マージ、タグ、導入、配布は統括が行う。

- S-01（タスク担当、8a5f71bad）：`migration.md`（提供側と dogfood の写しはバイト一致）の「## 0.9.1 への更新」の直後に「## 0.9.2 への更新」を足した。`git log v0.9.1..origin/main` は PR #588（iss-00587）と #590（iss-00589）で、変わったのは dashboard の資産と `runtime/application/dashboard_scope_details.py`（ダッシュボードの Scope の JSON の説明資料の項目に `skeleton` を足す）とテスト。節には、欄（ボードと図で同じ欄、タブの並び、説明資料を最初に、広い欄、詳しい画面への道、スマホの3段）、文書のタブ（仕様と報告の2つ、1行の切り替え、検査の帯、枠の高さ）、CLI の契約の変更がないこと、変わる配布資産は2つ、更新（0.9.1・0.9.0 のどちらからも上がる）、自動の起動し直し、戻し方を書いた。
- S-02（実装担当 Codex、49f541af5）：版を 0.9.2 に（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood）。`test_issue585_release_0_9_1.py` の版固定を外した。
- S-03（実装担当 Codex、c73ec459e）：`static-inventory.json` の2行の `sha256` を今のハッシュにし、v0.9.1 のバイトのハッシュを `known_old_sha256` に足した（0.9.0 は残る）。fixture `tests/fixtures/issue594/`（v0.9.1 のタグのバイトと一致することをタスク担当が `cmp` で確かめた）、統合テスト `tests/integration/test_issue594_release_0_9_2.py`。
- S-04（タスク担当）：コミット c73ec459e の `git archive` から `uv build --wheel` で作った wheel（sha256 `99b9a91b…e215`）を隔離した venv（`/private/tmp/spec-dock-iss00594-1794643397/venv`）に入れ、`spec-dock --version` が `spec-dock 0.9.2`。同じ venv で、この worktree の `canonical check --dry-run --offline` が valid=true、failures=0。道具の環境（uv tool）は 0.9.1 のまま。

### 実装担当

- Codex GPT-6.1 Sol / medium（`worker-start` の `launch.effective`：agent codex、model gpt-6.1-sol、effort medium。dispatch ctx_1049a1eebad0）。逸脱なし。plan.cue の status はタスク担当が書いた。

### マージの後の配布の手順（統括）

0.9.1 の実際の手順（v0.9.1 = PR #586 のマージのコミット 928460f48 に `release-tag.yml` が自動で作った軽いタグ（Release tag の run 43531042874、成功）、uv tool の receipt の wheel `/private/tmp/spec-dock-v0.9.1-dist/spec_dock-0.9.1-py3-none-any.whl`、iss-00585 の report.md）から：

1. タグ：PR をマージすると、`.github/workflows/release-tag.yml`（main への push で `pyproject.toml` の版が変わり、タグがなければ、そのマージのコミットに軽いタグ `v<版>` を作って push する）が `v0.9.2` を**自動で**作る。統括は手でタグを作らず、`git fetch --tags origin` の後に `git rev-parse v0.9.2^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.2 <マージのコミット>`、`git push origin refs/tags/v0.9.2`。
2. wheel：タグのきれいな取り出しから作る。`git archive --prefix=src/ v0.9.2 | tar -x -C /private/tmp/spec-dock-v0.9.2-src`、`cd /private/tmp/spec-dock-v0.9.2-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.2-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.2-dist/spec_dock-0.9.2-py3-none-any.whl`、`spec-dock --version` が `spec-dock 0.9.2`。常駐のダッシュボードは60秒ごとの版の確認で自動で起動し直す（`dashboard service install` は要らない）。画面（http://100.85.74.8:47800/）で、ボードと構造の図の欄、文書のタブ、スマホのシートを確かめる。リリースしたタグの wheel だけを入れる。
4. 各リポジトリの `installation update`：**必須ではない**。理由：0.9.2 の inventory は 0.9.1 と 0.9.0 の2つのバイトを `known_old_sha256` で受け入れるので、今の配布資産のままで 0.9.2 の `canonical check` は通る。欄と文書のタブの変更はパッケージが配る画面にあり、配布資産の更新なしで届く。0.9.1 のときも各リポジトリは更新せず、6つのリポジトリ（company-os、input-devices、housing-lifecycle、taikyohiyou_project、orca-web、yubisaki）の版のファイルは 0.9.0 のまま（2026-11-14 に確かめた）。版をそろえたいときだけ、PC のパッケージを 0.9.2 にしてから、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする（CI の見本は版のファイルの版の SpecDock を入れるので、更新しないと CI は 0.9.0 のまま。違いはダッシュボードだけで、CI の検査には影響しない）。この repo の dogfood は、この PR で 0.9.2 になる。

### 次の版の移行の注記に要る契約の変更

なし。

## Verification

- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `89f51588a..c73ec459e`）：**合格**（attempt 1）。P0〜P2 0、P3 1（節が ADR を省いて「2つ」と書く。記録だけ）、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3804 passed / 7 skipped、30分）。closure `.workbench/final-quality-gate/iss-00594-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00594`）。区切りのレビューは計画どおりなし。
- 実装担当の報告：対象の統合テスト3ファイル 10 passed、`make lint`、`uv lock --check` 合格、全体 3804 passed / 7 skipped。
- wheel：隔離した venv で `spec-dock --version` が `spec-dock 0.9.2`（Outcome の S-04）。
- PR #595（https://github.com/chemitaro/spec-dock/pull/595、head c73ec459e）：CI 合格（Provider CI、SpecDock check、Commit identity。observer の結果 OBSERVED_CI_PASS、merge_readiness READY、2026-11-14T08:54Z、`.workbench/coding-task/iss-00594/ci2.json`。最初の observer は provider-tests の30分の間に無通知の上限 600 秒で止まった（exit 4、`ci.json`）ので、上限 3000 秒でやり直した）。

## 逸脱と判断

- S-01 のコミットの件名と本文は git-autocommit が作った（Co-Authored-By はない。0.9.1 と同じ）。
- CI の observer の再起動（上の Verification）。
- 最終品質ゲートの P3 1 は記録だけ（closure.md）。

## Residual Risks / Follow-ups

- `work finish iss-00594` は実行していない（マージの後に統括が行う）。
- マージの後：タグの確かめ、wheel、導入、必要なら配布資産の更新は統括が行う（上の手順）。
