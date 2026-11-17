---
種別: レポート（Issue）
ID: "iss-00645"
関連GitHub: ["#645"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high、standard）：合格。P0 0、P1 0、P2 1（migration.md の 0.9.7 の節の「親がないときは画面は 0.9.6 と同じ」が、組によらない変更と食い違う。配る文書の事実の誤りなので直した、a472d607a）、P3 0。結果 `.workbench/spec-review/iss-00645/round-1.json`、応答 `review-response.md`。
- 仕様のレビュー round-2（同じレビュアー）：**合格**。P0〜P3 0。結果 `.workbench/spec-review/iss-00645/round-2.json`、検査 `round-2.check.json`（valid、status pass）。固定したコミット a472d607a（S-01 の後、clean）。
- 合格した文書の sha256：requirement.cue `01389f8921d780d6b6ac38f4eeb4c13a5e7e46342d48be865f22abc122a87f65`、design.cue `03f6258f41a42403c5dd2eec9674c9eb4627064bc0395c1f040732fd15a66342`、plan.cue `a1a396dee36560db549e77fbebbdc6ec9c61e33f0bac589e267374128b376870`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.7 のリリースの変更を作った。機能のコードは変えていない。マージ、タグ、導入、配布は統括が行う。この Issue の差分は `git diff 2fa809271 HEAD`（11ファイル）。

- S-01（タスク担当）：`migration.md`（提供側と dogfood の写しはバイト一致）の「## 0.9.6 への更新」の直後に「## 0.9.7 への更新」を足した（76a2b6861、仕様のレビューの P2 の直し a472d607a）。指揮の線（黄色、点の流れ、弧、working・waiting・done、`prefers-reduced-motion`）、『指揮の帯』（main のチェックアウト・ほかのリポジトリ・ほかの場所）、orca-web の `parent`（iss-00043 以降）の前提、箱の底のエージェントの行、見出しの文字が線の上、知らせのまとめ（#639）、帯の並び（#643）、木の表示の線（#641）、契約の変更なし、変わる配布資産は2つ、更新、自動の起動し直し、戻し方を書いた。
- reference_cli.md は変えていない（`git diff v0.9.6 2fa809271` に runtime と配る静的資産の変更がなく、契約と画面の道が変わらない）。
- S-02（実装担当、d6cd2de10）：版を 0.9.7 にした（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood）。`test_issue634_release_0_9_6.py` の版固定を外した。
- S-03（実装担当、64fd56c67）：`static-inventory.json` の2行の `sha256` を今のハッシュにし（migration.md `6ecfd102…`、版のファイル `6c38d2d8…`）、v0.9.6 のバイトのハッシュ（`8a16dc86…`、`fd512333…`）を `known_old_sha256` の末尾に足した。fixture は `tests/fixtures/issue645/` の2つで、v0.9.6 のタグのバイトと一致することをタスク担当が `cmp` で確かめた。統合テストは `tests/integration/test_issue645_release_0_9_7.py`。
- S-04（タスク担当）：`git archive 64fd56c67` から `uv build --wheel` で wheel を作った（sha256 `33100d63…3419`）。隔離した venv（`/private/tmp/spec-dock-iss00645-1794912708/venv`）に入れて確かめた。
  - `spec-dock --version` が `spec-dock 0.9.7` を返した。
  - 同じ venv で、この worktree と orca-web（版のファイル 0.9.0）の `canonical check --dry-run --offline` が valid=true、failures=0 を返した。
  - 道具の環境（uv tool）は 0.9.6 のまま。

### 実装担当

- Codex GPT-6.1 Sol / medium（dispatch ctx_3858d3f9916c、launch.effective：codex・gpt-6.1-sol・medium）。chat-scratch の symlink の拒否は起きず、切り替えはしていない。基準（開始のコミット 2fa809271）で節目の7ファイル 22 passed、実装後の8ファイル 25 passed、`uv lock --check`・`make lint` 合格（`.workbench/implement/iss-00645/`）。plan.cue の status はタスク担当が書いた。

### マージの後の配布の手順（統括）

0.9.6 の実際の手順から書いた。根拠は次のとおり。
- v0.9.6 は PR #638 のマージのコミット 4c49b68b6 に `release-tag.yml` が自動で作ったタグ（`git rev-parse v0.9.6^{commit}`）。
- uv tool の receipt の wheel は `/private/tmp/spec-dock-v0.9.6-dist/spec_dock-0.9.6-py3-none-any.whl`。
- iss-00634 の report.md。#639〜#644 のマージでは版が変わらないのでタグは作られていない。

1. タグ：PR をマージすると、`.github/workflows/release-tag.yml` が `v0.9.7` を**自動で**そのマージのコミットに作る（main への push で `pyproject.toml` の版が変わり、そのタグがないとき）。統括は手でタグを作らない。`git fetch --tags origin` の後に、`git rev-parse v0.9.7^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.7 <マージのコミット>` と `git push origin refs/tags/v0.9.7` を実行する。
2. wheel：タグのきれいな取り出しから作る。`mkdir -p /private/tmp/spec-dock-v0.9.7-src && git archive --prefix=src/ v0.9.7 | tar -x -C /private/tmp/spec-dock-v0.9.7-src`、続けて `cd /private/tmp/spec-dock-v0.9.7-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.7-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.7-dist/spec_dock-0.9.7-py3-none-any.whl` を実行し、`spec-dock --version` が `spec-dock 0.9.7` を返すことを確かめる。リリースしたタグの wheel だけを入れる。常駐のダッシュボードは、60秒ごとの版の確認で自動で起動し直す（`dashboard service install` は要らない）。画面で次を確かめる。
   - orca-web が `agents[].parent` を返す状態で、構造の図に指揮の線と『指揮の帯』（main のチェックアウトの統括）が出て、working の子への線に点が流れる。
   - 『横断の構造』に、リポジトリの枠をまたぐ線と、枠の見出しの下の帯が出て、見出しの文字が線の上に読める。知らせが上の帯の下に種類ごとに1行でまとまる。
4. 各リポジトリの `installation update`：**必須ではない**。理由は次のとおり。
   - 0.9.7 の inventory は 0.9.6〜0.9.0 のバイトを `known_old_sha256` で受け入れる。今の配布資産のままで 0.9.7 の `canonical check` は通る。S-04 で、版のファイルが 0.9.0 の orca-web が 0.9.7 の wheel で valid=true になることを確かめた。
   - 変更はパッケージが配る画面にだけあり、配布資産を更新しなくても届く。変わる配布資産は migration.md と版のファイルだけ。
   - 0.9.1〜0.9.6 のときも、各リポジトリは更新しなかった（orca-web と company-os の版のファイルは 0.9.0 のまま）。

   版をそろえたいとき（配る文書の migration.md を新しくしたいとき）だけ、PC のパッケージを 0.9.7 にしてから、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする。この repo の dogfood は、この PR で 0.9.7 になる。

### 次の版の移行の注記に要る契約の変更

なし。


## Verification

- 最終品質ゲート：**合格**（attempt 1）。
  - レビュアー：quality-gate-reviewer opus / medium。second opinion はない。範囲は `2fa809271..64fd56c67`。
  - 結果：P0〜P3 は0、coverage complete。
  - test lane：`make lint` exit 0、`uv run pytest` exit 0（4216 passed / 7 skipped、33分）。
  - closure：`.workbench/final-quality-gate/iss-00645-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00645`）。
  - 区切りのレビューは、計画どおりなし。
- wheel：隔離した venv で `spec-dock --version` が `spec-dock 0.9.7` を返した（Outcome の S-04）。
- PR #647（https://github.com/chemitaro/spec-dock/pull/647）：head は 64fd56c67（合格のコミット）。記録のコミットはない（記録は Git の外）。CI は下に追記する。

## 逸脱と判断

- S-03 のコミット 64fd56c67 の文が英語（`test: add 0.9.7 release upgrade coverage`）。`git-autocommit` が生成した。リポジトリの規則は日本語。履歴を書き換えず、そのまま受け入れた（タスク担当の判断）。
- 最終品質ゲートの review の最初の検査が、valid=false になった。キャンペーンを固定した後に、タスク担当が plan.cue の status を書き換え、authority の sha256 が合わなくなったため。指摘ではない。plan.cue を固定したバイトに戻して検査し直し、合格を確かめた。closure の後に status（S-02〜S-04 done）を書き直した。
- 仕様のレビューの P2（round-1）も、配るバイトの事実の誤りなので、直してから合格させた。

## Residual Risks / Follow-ups

- `work finish iss-00645` は実行していない（マージの後に統括が行う）。
- マージの後のタグの確かめ、wheel、導入、必要なら配布資産の更新は、統括が行う（上の手順）。
