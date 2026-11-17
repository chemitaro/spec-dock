---
種別: レポート（Issue）
ID: "iss-00634"
関連GitHub: ["#634"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：合格。P0 0、P1 0、P2 0、P3 2（migration.md の 0.9.6 の節で reference_cli.md の節名の誤りと、木の表示の線の言い切り。配るバイトの事実の誤りなので直した、e7bc4167b）。結果 `.workbench/spec-review/iss-00634/round-1.json`。
- 仕様のレビュー round-2（同じレビュアー）：**合格**。P0〜P3 0。結果 `.workbench/spec-review/iss-00634/round-2.json`、検査 `round-2.check.json`（valid、status pass）。固定したコミット e7bc4167b（S-01 の後、clean）。
- 合格した文書の sha256：requirement.cue `917e62d290ef7251ace4ad4651d63ba34bcb419adf71756b91632f7a26bfdb26`、design.cue `69937f7ba69d2e599086244121d547a2241c6874470d7353478d4fa5804779d6`、plan.cue `a1dac95cfdf668fdfb43494a31f666caeb94d0da200795a5c5f498773605490a`（以後 plan.cue は手順の status だけを書き換える）。

- 仕様の変更（統括の指示 msg_bd5763cd5228・msg_d59cd06a98b7）：0.9.6 に #636（iss-00635、tier と段の札の除去）を入れる。origin/main を取り込み（合流 3b45ff8a5）、migration.md の 0.9.6 の節と要件・設計・計画を直した（32e3257ed）。
- 仕様のレビュー round-3（同じレビュアー）：合格。P0 0、P1 0、P2 2（S-04 の status の誤りと、ゲート・T-04 の差分の基準。どちらも plan.cue で直した）。結果 `round-3.json`。
- 仕様のレビュー round-4（同じレビュアー）：**合格**。P0〜P3 0。結果 `.workbench/spec-review/iss-00634/round-4.json`、検査 `round-4.check.json`（valid、status pass）。固定したコミット 32e3257ed。
- 合格した文書の sha256（round-4）：requirement.cue `62b47da1efa4b2e628251011b28292fca42b4c4396bfa1c89d20d3df551cf366`、design.cue `b9bff008ef9671f74f125abcdd034db9ee2d14a19ad3f4743295c3e83e465256`、plan.cue `985c6af9c08ccdbfb50462dc4f1d885a3b8175863fe6125ffd66303582a975aa`（以後 plan.cue は手順の status だけを書き換える）。

- 仕様の変更（統括の指示 msg_dabb1c03680a）：0.9.6 に #637（iss-00621）も入れる。origin/main を取り込み（合流 dba84e9b7）、migration.md の 0.9.6 の節（d50bde195）と要件・設計・計画を直した。
- 仕様のレビュー round-5（同じレビュアー）：**合格**。P0 0、P1 0、P2 0、P3 1（requirement.cue の background の変わった dashboard の資産の一覧に #637 のファイルがない。受入と実装に効かないので記録だけ）。結果 `.workbench/spec-review/iss-00634/round-5.json`、検査 `round-5.check.json`。固定したコミット d50bde195。
- 今の合格した文書の sha256（round-5）：requirement.cue `b6d00a1aeca686617e898f0e0b7fa0fa6bb7c6301909ed227bd6d0d44e2b35ac`、design.cue `93fe94ec1a84107a5c3d25a990296b747964a81bf2ce4b44b19965bc2e2d5547`、plan.cue `69e214b1b670498772e240967aed87aab53b66627f6f614d3ced5e3acb4ba688`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.6 のリリースの変更を作った。機能のコードは変えていない。マージ、タグ、導入、配布は統括が行う。0.9.6 には、初めの依頼の #626・#628・#630・#631 に加え、統括の指示で #636（iss-00635）と #637（iss-00621）を入れた。この Issue の差分は `git diff 3f5f8d8e9 HEAD` で読む（12ファイル）。

- S-01（タスク担当）：`migration.md`（提供側と dogfood の写しはバイト一致）の「## 0.9.5 への更新」の直後に「## 0.9.6 への更新」を足した（74ee5b4fa、仕様のレビューの P3 の直し e7bc4167b、#636 の取り込みの後 32e3257ed、#637 の取り込みの後 d50bde195）。節には次を書いた。
  - 『横断の構造』（/graph）：タブの順、チェックアウトの入れ子のまま1枚、既定は『これから』、`specdock.allgraph.v1`、最初は幅に合わせる、スマホは 74%。
  - 枠と線（#630）：見出しの行の高さが少し詰まり（22px・18px・Epic の上 8px）、線が箱と見出しに重ならない（木の表示では線どうしの近づきが一部に残る）。2行の縮めた枠の測り直し。
  - #636：一覧の API から `tier` をなくした（`parent` は残る、v1 のままの版の規則の例外）。枠の見出しの段の札をなくした。
  - #637：作業中の Epic・Initiative の枠の worktree の印、押した印のエージェントのチャットを開く、ボードの札のエージェントの行。
  - そのほか：契約、変わる配布資産は3つ、更新、自動の起動し直し、戻し方。
- 合流：origin/main を2回取り込んだ（3b45ff8a5 で #636、dba84e9b7 で #637。衝突なし）。
- S-02（実装担当、1e9b79d41）：版を 0.9.6 にした（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood）。`test_issue623_release_0_9_5.py` の版固定を外した。
- S-03（実装担当、478bdcb14、合わせ 8be45952f・9f718011f）：`static-inventory.json` の2行の `sha256` を今のハッシュにし（migration.md、版のファイル `fd512333…`）、v0.9.5 のバイトのハッシュ（`9ea0ec4a…`、`8780409d…`）を `known_old_sha256` の末尾に足した。reference_cli.md の行は #628・#636 で済んでいる。fixture は `tests/fixtures/issue634/` の3つで、v0.9.5 のタグのバイトと一致することをタスク担当が `cmp` で確かめた。統合テストは `tests/integration/test_issue634_release_0_9_6.py`。
- S-04（タスク担当）：`git archive 9f718011f` から `uv build --wheel` で wheel を作った（sha256 `00a5daa4…34cf`）。隔離した venv（`/private/tmp/spec-dock-iss00634-1794891099/venv`）に入れて確かめた。
  - `spec-dock --version` が `spec-dock 0.9.6` を返した。
  - 同じ venv で、この worktree と orca-web（版のファイル 0.9.0）の `canonical check --dry-run --offline` が valid=true、failures=0 を返した。
  - 道具の環境（uv tool）は 0.9.5 のまま。

### 実装担当

- Codex GPT-6.1 Sol / medium（dispatch ctx_db01c4cba73a、launch.effective：codex・gpt-6.1-sol・medium）。今回は chat-scratch の symlink の拒否は起きず、Codex が S-02・S-03 と2回の合わせ（ctx_78aed8d5c4fa、ctx_d6508e908d00、同じ terminal の続き）をした。切り替えはしていない。plan.cue の status はタスク担当が書いた。

### マージの後の配布の手順（統括）

0.9.5 の実際の手順から書いた。根拠は次のとおり。
- v0.9.5 は PR #625 のマージのコミット 0c0e06951 に `release-tag.yml` が自動で作ったタグ（`git rev-parse v0.9.5^{commit}`）。
- uv tool の receipt の wheel は `/private/tmp/spec-dock-v0.9.5-dist/spec_dock-0.9.5-py3-none-any.whl`。
- iss-00623 の report.md。#626〜#637 のマージでも release-tag.yml は成功し、版が変わらないのでタグを作らなかった。

1. タグ：PR をマージすると、`.github/workflows/release-tag.yml` が `v0.9.6` を**自動で**そのマージのコミットに作る（main への push で `pyproject.toml` の版が変わり、そのタグがないとき）。統括は手でタグを作らない。`git fetch --tags origin` の後に、`git rev-parse v0.9.6^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.6 <マージのコミット>` と `git push origin refs/tags/v0.9.6` を実行する。
2. wheel：タグのきれいな取り出しから作る。`mkdir -p /private/tmp/spec-dock-v0.9.6-src && git archive --prefix=src/ v0.9.6 | tar -x -C /private/tmp/spec-dock-v0.9.6-src`、続けて `cd /private/tmp/spec-dock-v0.9.6-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.6-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.6-dist/spec_dock-0.9.6-py3-none-any.whl` を実行し、`spec-dock --version` が `spec-dock 0.9.6` を返すことを確かめる。リリースしたタグの wheel だけを入れる。常駐のダッシュボードは、60秒ごとの版の確認で自動で起動し直す（`dashboard service install` は要らない）。画面で次を確かめる。
   - 横断の画面の上の帯に『横断の概況』『横断の構造』『人のタスク』があり、`/graph` が『これから』で入れ子の枠を描き、枠の見出しに段の札がない。
   - `curl -s http://127.0.0.1:47800/api/v1/repositories` の各リポジトリに `parent` があり、`tier` がない。
   - 作業中の Epic の枠に worktree の印があり、稼働の印を押すと押したエージェントのチャットが開く。
4. 各リポジトリの `installation update`：**必須ではない**。理由は次のとおり。
   - 0.9.6 の inventory は 0.9.5〜0.9.0 のバイトを `known_old_sha256` で受け入れる。今の配布資産のままで 0.9.6 の `canonical check` は通る。S-04 で、版のファイルが 0.9.0 の orca-web が 0.9.6 の wheel で valid=true になることを確かめた。
   - 変更はパッケージが配る画面と API にあり、配布資産を更新しなくても届く。
   - 0.9.1〜0.9.5 のときも、各リポジトリは更新しなかった（orca-web と company-os の版のファイルは 0.9.0 のまま）。

   版をそろえたいとき（配る文書の migration.md と reference_cli.md を新しくしたいとき）だけ、PC のパッケージを 0.9.6 にしてから、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする。この repo の dogfood は、この PR で 0.9.6 になる。

### 次の版の移行の注記に要る契約の変更

なし（`tier` の除去は 0.9.6 の節に書いた）。

## Verification


## Residual Risks / Follow-ups
