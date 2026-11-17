---
種別: レポート（Issue）
ID: "iss-00663"
関連GitHub: ["#663"]
最終更新: "2026-11-18"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high、standard）：合格。P0 0、P1 0、P2 0、P3 1（片付けの候補の欄の段を描き直しで保つ直しを #659 の項に書いていた。正しくは #662（iss-00656 の R-09）。配るバイトの事実の誤りなので直した、6aba2177a）。結果 `.workbench/spec-review/iss-00663/round-1.json`、応答 `review-response.md`。
- 仕様のレビュー round-2（同じレビュアー）：**合格**。P0〜P3 0。結果 `.workbench/spec-review/iss-00663/round-2.json`、検査 `round-2.check.json`（valid、status pass）。固定したコミット 6aba2177a（S-01 の後、clean）。
- 合格した文書の sha256：requirement.cue `f1b231c2d8f078fc51b7c0903faeebd650ee3b4e9b65c409176f82cd06bd8895`、design.cue `1e0b825466159cd0c16bd71cd1562198eb0329272a0cda4940ddca8ec0fbb09d`、plan.cue `5b7e16202f1f20c1d87ebdfb7e24e187b4c4724346ff6d389b7509099a641354`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.8 のリリースの変更を作った（`git diff fa9824cb9 7b3c25650`、11ファイル）。機能のコードは変えていない。PR はまだ作っていない（統括の決定、下の「待ち」）。

- S-01（タスク担当）：`migration.md`（提供側と dogfood はバイト一致）の「## 0.9.7 への更新」の直後に「## 0.9.8 への更新」を足した（dcd52eaf6、仕様のレビューの P3 の直し 6aba2177a）。
- reference_cli.md は変えていない（契約と画面の道、書かれた操作が変わらない）。
- S-02（実装担当、3b094a06d）：版を 0.9.8 にし（`pyproject.toml`、`uv.lock`、版のファイルの提供側と dogfood）、`test_issue645_release_0_9_7.py` の版固定を外した。
- S-03（実装担当、7b3c25650）：`static-inventory.json` の2行の `sha256` を今のハッシュ（migration.md `ae9e47b6…`、版のファイル `ff35aa97…`）にし、v0.9.7 のバイトのハッシュ（`6ecfd102…`、`6c38d2d8…`）を `known_old_sha256` の末尾に足した。fixture `tests/fixtures/issue663/` の2つは v0.9.7 のタグのバイトと一致する（タスク担当が `cmp` で確かめた）。統合テスト `tests/integration/test_issue663_release_0_9_8.py`。
- S-04（タスク担当）：`git archive 7b3c25650` から作った wheel（sha256 `d7f02ec73e2d7f4829d8dbee9f763c9b0b71b3103669e49c80515032d039f346`）を隔離した venv（`/private/tmp/spec-dock-iss00663-1794943381/venv`）に入れ、`spec-dock --version` が `spec-dock 0.9.8` を返した。同じ venv で、この worktree（0.9.8）と orca-web（版のファイル 0.9.0）の `canonical check --dry-run --offline` が valid=true、failures なし。道具の環境は 0.9.7 のまま。

### 実装担当

- 最初に Codex GPT-6.1 Sol / medium（ctx_83bcb0a37734、launch.effective：codex・gpt-6.1-sol・medium）を起動した。chat-scratch の symlink の拒否で起動前に止まり、変更はなかった。計画の rationale（統括が了承済み）どおり停止し、Claude Opus 5.5 / medium（ctx_d36d406b2621、launch.effective：claude・claude-opus-5-5・medium）に切り替えた。
- 基準（6aba2177a）：リリースの統合テスト8ファイルで 16 failed / 9 passed（S-01 で migration.md のバイトが変わったことによる既知の失敗）。実装後：9ファイルで 28 passed。`uv lock --check`、`make lint` は合格。

### 最初のゲートの後の取り込み（統括の決定 2026-11-18）

最初のキャンペーン iss-00663-fqg-1 の全テストで、範囲外の既存の不安定なテスト1件が落ちた（Verification）。統括は選択肢 C を選んだ。iss-00664（PR #665、テストだけの直し。原因は #661 からのテストの時間の扱いで、画面の不具合ではない）をマージした後、origin/main（8c43b7695）を取り込み（7cb666057）、新しいキャンペーン iss-00663-fqg-2 でゲートをやり直した。

### マージの後の配布の手順（統括）

0.9.7 の実際の手順から書いた。根拠は次のとおり。
- v0.9.7 は PR #647 のマージのコミット 60197049e を指す軽量タグ。`release-tag.yml`（main への push、`release-tag-decision.py` が `pyproject.toml` の版の変化を見る）が自動で作った（`git for-each-ref refs/tags/v0.9.7`）。
- uv tool の receipt（`~/.local/share/uv/tools/spec-dock/uv-receipt.toml`）の wheel は `/private/tmp/spec-dock-v0.9.7-dist/spec_dock-0.9.7-py3-none-any.whl`。
- iss-00645 の report.md。

1. タグ：PR #666 をマージすると、`.github/workflows/release-tag.yml` が `v0.9.8` を**自動で**そのマージのコミットに作る。統括は手でタグを作らない。`git fetch --tags origin` の後に、`git rev-parse v0.9.8^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.8 <マージのコミット>` と `git push origin refs/tags/v0.9.8` を実行する。
2. wheel：タグのきれいな取り出しから作る。`mkdir -p /private/tmp/spec-dock-v0.9.8-src && git archive --prefix=src/ v0.9.8 | tar -x -C /private/tmp/spec-dock-v0.9.8-src`、続けて `cd /private/tmp/spec-dock-v0.9.8-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.8-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.8-dist/spec_dock-0.9.8-py3-none-any.whl` を実行し、`spec-dock --version` が `spec-dock 0.9.8` を返すことを確かめる。リリースしたタグの wheel だけを入れる。常駐のダッシュボードは、60秒ごとの版の確認で自動で起動し直す（`dashboard service install` は要らない）。画面で次を確かめる。
   - 構造の図と『横断の構造』で、指揮の線がホップの弧と矢じりで描かれ、点の組がゆっくり流れる。図を動かすと線が止まる。
   - 矢印キー・`+`・`-`・`0`・マウスのホイールで動かし、拡大・縮小できる。
   - Scope の欄の見出しが2行になり、帯の印から開くチャットが欄いっぱいに出る。
4. 各リポジトリの `installation update`：**必須ではない**。理由は次のとおり。
   - 0.9.8 の inventory は 0.9.7〜0.9.0 のバイトを `known_old_sha256` で受け入れる。今の配布資産のままで 0.9.8 の `canonical check` は通る。S-04 で、版のファイルが 0.9.0 の orca-web が 0.9.8 の wheel で valid=true になることを確かめた。
   - 変更はパッケージが配る画面にだけあり、配布資産を更新しなくても届く。変わる配布資産は migration.md と版のファイルだけ。
   - 0.9.1〜0.9.7 のときも、各リポジトリは更新しなかった（2026-11-18 の時点で、orca-web と company-os の版のファイルは 0.9.0 のまま）。

   版をそろえたいとき（配る文書の migration.md を新しくしたいとき）だけ、PC のパッケージを 0.9.8 にしてから、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする。この repo の dogfood は、この PR で 0.9.8 になる。

### 次の版の移行の注記に要る契約の変更

なし。

## Verification

- 最終品質ゲート iss-00663-fqg-1 attempt 1（7b3c25650）：**閉じていない**。
  - レビュー（quality-gate-reviewer opus / medium）：合格。P0〜P3 0、coverage complete（`attempts/01/review.check.json`）。
  - `make lint`：exit 0。
  - `uv run pytest`：exit 1。1 failed / 4308 passed / 7 skipped（30分46秒）。落ちたのは `tests/unit/presentation/test_dashboard_allgraph_command_screen.py::test_the_motion_stills_and_watches_on_the_cross_repository_structure`（shots[1] の still が True）。この PR はダッシュボードの資産とテストを変えていない。開始のコミット fa9824cb9 のきれいな取り出しで単独に5回走らせると4回落ちた。HEAD では3回のうち2回落ちた（`attempts/01/baseline/note.md`）。
  - キャンペーン：`.workbench/final-quality-gate/iss-00663-fqg-1/`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00663`）。
- 最終品質ゲート iss-00663-fqg-2 attempt 1（7cb666057、origin/main 8c43b7695 を取り込んだ後）：**合格**。
  - レビュー（quality-gate-reviewer opus / medium、second opinion なし）：P0〜P3 0、coverage complete。範囲は `fa9824cb9..7cb666057` のこの Issue の変更。取り込んだ PR #665 は範囲外。
  - `make lint`：exit 0。`uv run pytest`：exit 0（4309 passed / 7 skipped、29分43秒）。
  - closure：`.workbench/final-quality-gate/iss-00663-fqg-2/closure.md`（同じ worktree）。
  - 区切りのレビューは、計画どおりなし。
- PR #666（https://github.com/chemitaro/spec-dock/pull/666）：head は 7cb666057（合格のコミット）。記録のコミットはない（記録は Git の外）。CI：（observer の結果を待つ）

## 逸脱と判断

- 実装担当の切り替え：Codex GPT-6.1 Sol / medium が chat-scratch の symlink の拒否で止まったので、計画の rationale（統括が了承済み）どおり Claude Opus 5.5 / medium に切り替えた（Outcome の「実装担当」）。
- 最初のゲートで落ちた既存の不安定なテストは、統括の決定（C）で iss-00664 が直した。取り込みのマージ 7cb666057 の文は Git の既定（英語）。前例（iss-00645 のブランチ）と同じなので、そのまま受け入れた。
- 仕様のレビューの P3（round-1）も、配るバイトの事実の誤りなので、直してから合格させた。

## Residual Risks / Follow-ups

- `work finish iss-00663` は実行していない（マージの後に統括が行う）。
- マージの後のタグの確かめ、wheel、導入、必要なら配布資産の更新は、統括が行う（上の手順）。
