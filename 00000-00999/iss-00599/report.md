---
種別: レポート（Issue）
ID: "iss-00599"
関連GitHub: ["#599"]
最終更新: "2026-11-15"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：**合格**。P0 0、P1 0、P2 1、P3 0。結果 `.workbench/spec-review/iss-00599/round-1.json`、検査 `round-1.check.json`（valid、status pass）。固定したコミット 0d17b2229（S-01 の後）。
  - P2（記録だけ）：R-02 の文の「orca-web がないときは印もタブも出ず」が、配る文書の挙動（worktree の記録がある Scope では、エージェントのタブが理由の知らせとともに出る）と食い違う。migration.md の節（S-01）は配る文書の挙動に合わせて書いた（印と「Orca で開く」は出ず、タブは記録がある Scope でだけ理由の知らせを示す）。要件の文は合格の後なので変えない。
- 合格した文書の sha256：requirement.cue `282db6f26935e0c9995101d3c49460f42a56fb301aafdece84bc4ec308b7aa6d`、design.cue `37cb8d36f4e8f9df3f703270bbd01c1cc7d1dab50f90887e8a6a30792376fda2`、plan.cue `510cf0f6d8ceff3eeb482b7a5cfe78546fb52d4cc5c1e22d9fc7fe7e10acf732`（以後 plan.cue は手順の status だけを書き換える）。

## Outcome

SpecDock 0.9.3 のリリースの変更を作った。機能のコードは変えていない。マージ、タグ、導入、配布は統括が行う。

- S-01（タスク担当、0d17b2229）：`migration.md`（提供側と dogfood の写しはバイト一致）の「## 0.9.2 への更新」の直後に「## 0.9.3 への更新」を足した。`git log --first-parent v0.9.2..origin/main` は PR #596（iss-00591）、#597（iss-00592）、#598（iss-00593）。節には、orca-web との連携（稼働の印、「Orca で開く」、エージェントのタブ、対応の決め方）、`config.json` の `orca_web` の節（`enabled` 既定 true、`port` 既定 8791、壊れた節は連携しない側）、orca-web の `ORCA_WEB_READ_ORIGINS` の前提、orca-web がないときの動き（印とボタンは出ず図とボードはそのまま。タブは worktree の記録がある Scope で理由の知らせだけ）、送信は orca-web の `sendEnabled` で決まること、CLI の契約の変更がないこと（ダッシュボードの JSON に項目が足されるだけ）、変わる配布資産は3つ（migration.md、版のファイル、#597 で変わった reference_cli.md）、更新、自動の起動し直し、戻し方を書いた。根拠は iss-00591〜00593 の report.md と配る `reference_cli.md` の「orca-web との連携」の節。
- S-02（実装担当 Codex、af025ff0d）：版を 0.9.3 に（`pyproject.toml`、`uv.lock`、`system/spec-dock-version` の提供側と dogfood）。`test_issue594_release_0_9_2.py` の版固定を外した。
- S-03（実装担当 Codex、33786fbc6）：`static-inventory.json` の2行の `sha256` を今のハッシュにし、v0.9.2 のバイトのハッシュを `known_old_sha256` に足した（reference_cli.md の行は #597 で済みのため変えない）。fixture `tests/fixtures/issue599/`（3つ。v0.9.2 のタグのバイトと一致することをタスク担当が `cmp` で確かめた）、統合テスト `tests/integration/test_issue599_release_0_9_3.py`（0.9.2 の consumer が3つのファイルだけ変わって上がる）。
- S-04（タスク担当）：コミット 33786fbc6 の `git archive` から `uv build --wheel` で作った wheel（sha256 `7caad0b2…add68`）を隔離した venv（`/private/tmp/spec-dock-iss00599-1794679199/venv`）に入れ、`spec-dock --version` が `spec-dock 0.9.3`。同じ venv で、この worktree の `canonical check --dry-run --offline` が valid=true、failures=0。道具の環境（uv tool）は 0.9.2 のまま。

### 実装担当

- Codex GPT-6.1 Sol / medium（`worker-start` の `launch.effective`：agent codex、model gpt-6.1-sol、effort medium。dispatch ctx_7ce8c2272f28）。逸脱なし。plan.cue の status はタスク担当が書いた。

### マージの後の配布の手順（統括）

0.9.2 の実際の手順（v0.9.2 = PR #595 のマージのコミット 2265e8fc1 に `release-tag.yml` が自動で作ったタグ（Release tag の run 43578058892、成功）、uv tool の receipt の wheel `/private/tmp/spec-dock-v0.9.2-dist/spec_dock-0.9.2-py3-none-any.whl`、iss-00594 の report.md）から：

1. タグ：PR をマージすると、`.github/workflows/release-tag.yml`（main への push で `pyproject.toml` の版が変わり、タグがなければ、そのマージのコミットに `v<版>` を作って push する）が `v0.9.3` を**自動で**作る。統括は手でタグを作らず、`git fetch --tags origin` の後に `git rev-parse v0.9.3^{commit}` がマージのコミットと一致することを確かめる。ワークフローが失敗したときだけ、`git tag v0.9.3 <マージのコミット>`、`git push origin refs/tags/v0.9.3`。
2. wheel：タグのきれいな取り出しから作る。`mkdir -p /private/tmp/spec-dock-v0.9.3-src && git archive --prefix=src/ v0.9.3 | tar -x -C /private/tmp/spec-dock-v0.9.3-src`、`cd /private/tmp/spec-dock-v0.9.3-src/src && uv build --wheel --out-dir /private/tmp/spec-dock-v0.9.3-dist`。
3. 導入：`uv tool install --force /private/tmp/spec-dock-v0.9.3-dist/spec_dock-0.9.3-py3-none-any.whl`、`spec-dock --version` が `spec-dock 0.9.3`。常駐のダッシュボードは60秒ごとの版の確認で自動で起動し直す（`dashboard service install` は要らない）。リリースしたタグの wheel だけを入れる。画面（http://100.85.74.8:47800/）で、orca-web（8791）が動いていれば稼働の印、「Orca で開く」、エージェントのタブを確かめる。orca-web の `ORCA_WEB_READ_ORIGINS` に `http://127.0.0.1:47800` と Tailscale のオリジンが入っていること、送信を使うなら orca-web の `sendEnabled` を確かめる。`config.json` の変更は要らない（節がなければ既定で連携する）。
4. 各リポジトリの `installation update`：**必須ではない**。理由：0.9.3 の inventory は 0.9.2・0.9.1・0.9.0 のバイトを `known_old_sha256` で受け入れるので、今の配布資産のままで 0.9.3 の `canonical check` は通る。連携の変更はパッケージが配る画面とサーバーにあり、配布資産の更新なしで届く。0.9.1・0.9.2 のときも各リポジトリは更新せず、6つのリポジトリ（company-os、input-devices、housing-lifecycle、taikyohiyou_project、orca-web、yubisaki）の版のファイルは 0.9.0 のまま（2026-11-15 に確かめた）。版をそろえたいとき（配る文書の migration.md と reference_cli.md を新しくしたいとき）だけ、PC のパッケージを 0.9.3 にしてから、各リポジトリで `spec-dock installation update --target <チェックアウト> --backup-dir <新しい外のディレクトリ> --yes` を実行し、通常の PR でコミットする（CI の見本は版のファイルの版の SpecDock を入れるので、更新しないと CI は 0.9.0 のまま。違いはダッシュボードだけで、CI の検査には影響しない）。この repo の dogfood は、この PR で 0.9.3 になる（`spec-dock/docs/reference_cli.md` は #597 で済み）。

### 次の版の移行の注記に要る契約の変更

なし。

## Verification

- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `a793c3025..33786fbc6`）：**合格**（attempt 1）。P0〜P3 0、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3912 passed / 7 skipped、29分）。closure `.workbench/final-quality-gate/iss-00599-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00599`）。区切りのレビューは計画どおりなし。
- 実装担当の報告：対象の統合テスト4ファイル 13 passed、`make lint`、`uv lock --check` 合格、全体 3912 passed / 7 skipped。
- wheel：隔離した venv で `spec-dock --version` が `spec-dock 0.9.3`（Outcome の S-04）。
- PR #600（https://github.com/chemitaro/spec-dock/pull/600、head 33786fbc6 = 合格のコミット、記録のコミットなし）：CI 合格（observer の結果 OBSERVED_CI_PASS、merge_readiness READY、2026-11-14T18:44Z UTC、`.workbench/coding-task/iss-00599/ci.json` の最後の行）。

## 逸脱と判断

- 仕様のレビューの P2（R-02 の文の「タブも出ず」）は記録だけ。migration.md の節は配る文書の挙動に合わせた。依頼書の「orca-web がないときは印もタブも出ず」も同じ理由で、タブについては正確な挙動を書いた。

## Residual Risks / Follow-ups

- `work finish iss-00599` は実行していない（マージの後に統括が行う）。
- マージの後：タグの確かめ、wheel、導入、必要なら配布資産の更新は統括が行う（上の手順）。
