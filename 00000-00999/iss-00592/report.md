---
種別: レポート（Issue）
ID: "iss-00592"
関連GitHub: ["#592"]
最終更新: "2026-11-14"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様レビュー round-1（spec-reviewer opus / high）：合格（P0 0・P1 0・P2 4・P3 2）。合格の後、統括の連絡（2026-11-14、orca-web の iss-00035 で「Orca で開く」を小さなボタンに作り直す）を受けて仕様を変え、P2/P3 も合わせて直した（`review-response.md`）。
- 仕様レビュー round-2（同じレビュアー）：**合格**（P0 0・P1 0・P2 1・P3 2）。検査 `round-2.check.json`（valid、pass）。
  - P2：S-05 で空の `XDG_STATE_HOME` ではリポジトリが出ない → 実装担当への依頼で、iss-00591 の S-05 と同じく道具の環境の状態の置き場を（サーバーの記録とログを除いて）一時の `XDG_STATE_HOME` に写すと指示する（計画の「試し専用の一時の場所」の中の扱い）。
  - P3：見出しの行の高さ → `.pn-orca` を 24px にし、行の高さは閉じるの 32px のまま、と読む（D-04）。
  - P3：今の orca-web の main の open-button は幅 260・高さ 26 → S-05 のときの orca-web の main の版を記録し、はみ出すなら report に記す。
- 合格した文書の sha256：requirement.cue `da41ab88ef83ee338aea2367ec4ed568d4e4d4a4c05a61e6302f9a24ab0140a3`、design.cue `b7bb0b5d5516b6fe529ddca6587161b2c8c35c9810c2164aa701975251cc02e2`、plan.cue `ebf4fff8cea44cb21eb418505881287d4960000375ca3a793c2b77857c8a84ad`、explanation.html `a55de777619835714fdf30498633c29d3a1503ad5c8b8d706fb0ad7d948e236e`。開始のコミット `67abbe6c1`（clean）。
- 結果の場所：この Issue の worktree の `.workbench/spec-review/iss-00592/`。
- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `67abbe6c1..0bfa2424f`、観点 functional-correctness・requirements-closure・test-adequacy・security-baseline）：**合格**（attempt 2、`0bfa2424f`）。P0〜P3 0、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3871 passed / 7 skipped）。closure は worktree の `.workbench/final-quality-gate/iss-00592-fqg-1/closure.md`。
  - attempt 1（`c2e68535a`）：review pass（P3 1：配る文書の config_problems の文）、test lane fail（配る文書を変えたのにドッグフードの写し `spec-dock/docs/reference_cli.md` を合わせておらず 3 failed）。`0bfa2424f` で写しを合わせ、P3 の文も直した（`review-response.md`）。
- 注：plan.cue は合格の後、手順の status だけを done に書き換えている（中身は合格のまま）。

## 実装の記録

記録の詳細は worktree の `.workbench/implement/iss-00592/{start.md,steps.md}`。開始のコミット `67abbe6c1` の基準：`make lint` 合格、`uv run pytest` 3847 passed / 7 skipped。

- impl-sol（Codex gpt-6.1-sol / medium、dispatch `ctx_62e522b9d825`、launch.effective codex・gpt-6.1-sol・medium）
  - S-01（`70d09a8c4`）：`views/_shared/orca_logic.js`（`slotWorktree`、`marksKey`、`openTarget`、`themeOf`）。T-01。
  - S-02（`07b0c8396`）：`views/_shared/orca_marks.js`（`paintOrcaMarks`、`createOpenButton`）、`app.css` の置き場の規則。T-02。`make lint` 合格、`uv run pytest` 3856 passed / 7 skipped。
- impl（Claude Opus 5.5 / medium、dispatch `ctx_4a3e453b2b2e`、launch.effective claude・opus・medium）
  - S-03（`41f847979`）：構造の図（箱の `.gx-marks` に max 2、枠の `.gx-fh` に max 3）とボード（札の下の段に max 4）の置き場、描き直しの後と知らせでの描き、`createOrcaWatch`、印の押しで `preferTab("agents")`。T-03。
  - S-04（`8ec21ece5`）：横の欄の作り直さない見出しの行（`.pn-hl`、`.pn-orca`、閉じる）と表紙、見出しの印（max 4）、`createOpenButton`、明暗の見張り、`preferTab`、`refreshOrca`。T-04。`make lint` 合格、`uv run pytest` 3869 passed / 7 skipped。
  - S-05：実機の確かめ（下の節）。コードの変更なし。
- owner（タスク担当）
  - S-06：配る文書 `reference_cli.md` の「ダッシュボードのサーバーの契約」に「orca-web との連携」の項と、設定の3段の `orca_web` の節を足し、`static-inventory.json` の sha256 を合わせた。T-05（`tests/unit/infra/test_dashboard_orca_docs.py`）。

## 実機の確かめ（S-05、T-06）

記録と写しは worktree の `.workbench/iss-00592/s05/`（`records.md`、`before/`、`after/`、`after-tailnet/`、`stop.md`）。写しにはリポジトリの名前と Scope の題名が写るので、report には貼らず、場所と事実だけを書く。実際の IP、ユーザー名、ホームのパスは、写しにも記録の JSON にも写っていないことを実装担当が確かめた。

- 試し：S-04 の終わり `8ec21ece5` の wheel（0.9.2）を隔離した venv に入れ、`XDG_STATE_HOME`（道具の環境の状態の置き場の登録簿・カタログ・スナップショットの写し。サーバーの記録とログは除く）と `XDG_CONFIG_HOME`（`orca_web.port` だけの config.json）を一時の場所にして、ポート 18592、`--tailscale`。直す前は開始のコミット `67abbe6c1` の wheel をポート 18596 で同じ手順。試しの orca-web は orca-web main `373a2c7`（iss-00035 の小さなボタンを含む）の `dist/` をポート 8892、`ORCA_WEB_READ_ORIGINS` に試しの2つの SpecDock のオリジン、設定と送信の記録の置き場を一時の場所にして起動（送信は既定で止まったまま）。常駐の 47800 と 8791 には触れていない。
- 写し：構造の図・ボード・横の欄（iss-00592 を選んだ状態）を、1440・1000・390、明暗で、直す前と後。headless Chrome 157（CDP、`Browser.close`）。
- 印：箱（max 2）は「印1つと +3」で箱に収まる（`.gx-marks` のはみ出しは全写しで 0）。札と横の欄の見出し（max 4）は4つ。写した範囲に worktree を持つ枠はなかった。max は写しで変える必要がなかった。
- 横の欄の見出しの行：ボタンの iframe は 72×24（orca-web の sm の既定。SpecDock は幅を決めない）で、閉じるの左に縦の中心をそろえて並ぶ。行の高さ（44）と閉じるの位置は直す前と同じ。幅 390px では iframe が隠れ、src がない（読み込まない）。
- 30 秒（同じ Scope を選んだまま）：iframe の文書の読み込み 1回、要約の GET 3回（10 秒に1回）。127.0.0.1 と tailnet のオリジンの両方で同じ。
- `?embed=1`：印は出て、ボタンは出ない。
- 試しの orca-web を止めたとき：印もボタンもなく（置き場は空）、図の箱とボードの札が描かれ、横の欄も開く。
- 本人の確かめのため、試しの SpecDock（18592）と試しの orca-web（8892）は動かしたまま。止め方は `stop.md`。

## 逸脱と判断

- 仕様のレビューの round-1 の合格の後に、統括の連絡（orca-web の iss-00035 のボタンの作り直し）で仕様を変え、round-2 で合格し直した。
- D-03 の「onClick（と onTap）」：図の箱の中の印の押しは pointer の `onTap` が受け、横の欄の見出しの印の押しは横の欄が自分で受ける（構造の図とボードで同じになるように）。graph の `onClick` には足していない（実装担当の解釈。意味は仕様のまま）。
- S-05 の状態の置き場：round-2 の P2 のとおり、空の置き場ではなく道具の環境の状態の置き場の写しを使った。
- 実装担当の値は計画どおり。逸脱なし。

## Outcome

PR #597（https://github.com/chemitaro/spec-dock/pull/597、head `0bfa2424f47382f763510c2a9208c6688746c304`）。マージは統括が行う。

## Verification

## Residual Risks / Follow-ups
