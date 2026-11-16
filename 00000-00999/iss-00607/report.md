---
種別: レポート（Issue）
ID: "iss-00607"
関連GitHub: ["#607"]
最終更新: "2026-11-16"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー round-1（spec-reviewer opus / high）：**合格**（P0・P1 なし、P2 1・P3 4）。結果 `.workbench/spec-review/iss-00607/round-1.json`、検査 `round-1.check.json`（valid、status pass）（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00607`）。
- 合格した文書の sha256：requirement.cue `e2ac949f4c4aa348e505acc934f79b49a82c68d37c87efefeeb97cf32032eaa0`、design.cue `161aecb2e073445a8e648aef2b74ee538682293ee9b34bfbfdc76aa2be2aa5e1`、plan.cue `5f61813b3971eb36261215a1881e45f775f79b12b3c18dc0f872c5b30d5ffe4d`。
- P2・P3 は文書を変えず、実装担当への指示（意味を保つ解釈）で扱う（下の「逸脱と判断」）。

## 逸脱と判断

- 仕様のレビューの P2（T-06 の線の確かめ）：toolbar の harness（`tests/js/dashboard_graph_toolbar.mjs`）を、世界の `.gx-edges` の HTML（または layout の edges）も返すように広げ、版3に deps none を保存した状態で線（is-done を含む）があることを確かめる。テストだけの変更。
- P3（注釈と字の検査）：prefs.js の注釈は `deps` の字を使わずに書く（例 "the old line choice"）。graph.js の字の検査は S-03 で書く。
- P3（これからの線）：`test_dashboard_graph_range.py` の deps none の検査は、deps なしの組（これからで端が done の線がない）に書き換える。
- P3（時系列の series）：`test_weeks_of_the_chosen_kinds_add_up` の all・issue・none は Scope の種類で、deps と関係ないので触らない。
- 最終品質ゲート（quality-gate-reviewer opus / medium、second opinion なし、範囲 `bf21a961a..3dab89a64`）：**合格**（attempt 1）。P0〜P3 すべて0、coverage complete。test lane：`make lint` exit 0、`uv run pytest` exit 0（3956 passed / 7 skipped、1706s）。closure `.workbench/final-quality-gate/iss-00607-fqg-1/closure.md`（worktree `/Volumes/990p2t/workspace/worktrees/orca/spec-dock/iss-00607`）。レビューの間にタスク担当が S-05 の記録を書いて authority の sha256 がずれ、最初の検査が valid false になったので、固定した内容に戻して再検証した（`review-response.md`）。

## 実装の記録

- 逸脱 codex-symlink-refusal：plan の impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_01b9a40e9a88）が chat-scratch の symlink の拒否で起動できず変更なしで failed を返したので、plan の rationale と統括の了承どおり Claude Opus 5.5 / medium が S-01〜S-02 を担当した。
- 基準（開始のコミット `bf21a961a`）：`make lint` pass。`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py tests/unit/presentation/test_dashboard_graph_range.py tests/unit/presentation/test_dashboard_graph_toolbar.py` 68 passed。
- S-01（Red、`bedd72949`）：test_dashboard_graph_js.py（small・context に deps wait・none の組を足し deps なしと同じを確かめる、restorePrefs の opts が {mode, range} だけ、prefs.js に deps の字がない、node の確かめの組み合わせに deps がない）と test_dashboard_graph_range.py（cases を deps なしにして layout-before.json の deps all の組とだけ比べ、VARIANTS に deps wait・none を足す、これからの線の検査を deps なしの組に書き換える。記録用の `request_before` は開始時の組 `recorded_cases` のまま）。直す前のコードで意図した 6 件が落ちた（6 failed, 50 passed）。fixture は書き換えていない。時系列の series のテストは触っていない。
- S-02（Green、`424ba72eb`）：layout.js（D-01：DEFAULTS と options の注釈から deps、pairs の none・wait の分かれ道を消す）、prefs.js（D-02：VALID・restorePrefs から deps を消し、注釈は deps の字を使わずに直す）、dashboard_graph_check.mjs（組み合わせから deps をなくす。組の数の検査を 6 + 7 × 3 に直す）。節目のテスト：js・range はすべて通過、edgeAudit の違反0（T-04）。toolbar の 3 件（`saves_four_keys[nest|tree]`、`moves_a_saved_version_2_to_version_3`）は graph.js の savePrefs が deps を書く前提の古い期待で落ちる。graph.js と toolbar のテストは S-03 の範囲なので触っていない。`make lint` pass。
- S-03（Red `08feef3e4`、Green `f244c49ce`、整形 `3dab89a64`。Claude Opus 5.5 / medium、impl-ui）：toolbar の harness が世界の `.gx-edges` の線の HTML（`edges`）を返すように広げた（P2）。test_dashboard_graph_toolbar.py に、帯に deps の group・3つの文字がなく `data-act` の順が縮小〜見せる範囲で終わり、凡例が線を説明し続けること（T-05）と、版3に deps none を保存した run と deps なしの run の線・世界が同じで is-done・is-wait を含むこと（T-06）を足した。保存の期待を3つの鍵 `{mode, range, legend}` に書き換え、legacy の run の deps のクリックを消した。test_dashboard_graph_js.py に graph.js に `deps` の字がない検査を足した（T-03）。直す前のコードで落ちたのは意図した3件（帯の2件と graph.js の字）。保存の3つの鍵と線の検査は、S-02 で V.opts に deps が入らなくなり `JSON.stringify` が undefined の deps を落とすため、直す前でも通った。graph.js は D-03（renderTools の「依存の線」の group と onClick の deps の分かれ道を消す）と D-02（savePrefs が `{mode, range, legend}` を書く）。graph.css・凡例・選んだ箱の強調は変えていない（開始のコミットからの graph.css の差分なし）。節目のテスト 73 passed。
- S-04：`make lint` pass（初回は ruff format check が toolbar のテストの長い行で fail、`ruff format` で直して `3dab89a64`）。全体の `uv run pytest`：3956 passed, 7 skipped, 0 failed（1805.58s、約30分）。ログは `.workbench/implement/iss-00607/{lint.log,pytest-full.log}`。

## 実データの写し（S-05、タスク担当）

- この PC の状態の置き場の写し（`.workbench/iss-00607/state`）を、隔離した venv の `spec-dock dashboard serve --port 18607 --offline --state-root …` で配った。直す前は開始のコミット `bf21a961a` の wheel（127.0.0.1 だけ、写した後に止めた）、直した後は `3dab89a64` の wheel（`--tailscale`）。常駐の 47800 と道具の環境には触れていない。
- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close` で閉じた）で、spec-dock と housing-lifecycle × 全体・いま・これから × 1440・390 × 明・暗 の24通りを、直す前と後の両方で測り、「いま」の16枚を写した（スクリプト `.workbench/iss-00607/shoot.mjs`）。
- **edgeAudit の違反はすべて0**（前後とも24通り）。線の数は前後で同じ（spec-dock 全体 211・いま 5・これから 0、housing-lifecycle 全体 134・いま 36・これから 11）。ページの横はみ出しなし。ブラウザーのエラーは、どの通りも Orca の印の読み込み（`127.0.0.1:8791/embed/agent-marks.js` の CORS、この試しの origin を Orca 側が許していない）の4件だけで、構造の図のエラーは0（直す前も同じ）。
- 道具の帯：直す前は role=group が「見せる範囲」「依存の線」の2つ、後は「見せる範囲」だけ（`data-act="deps"` 0）。1440 で幅 825px → 519px（1行）、**390 で縦の高さ 339px → 239px**（幅 32px のまま）。
- 直した後の写しで、1440 の帯の上に「構造が46分前から更新されていません」「PR の状態が分かりません」の知らせが出ているのは、写した状態の置き場が時間とともに古くなったためで、この変更とは関係ない。
- 写し：spec-dock 1440 明 いま [前](artifacts/20261116t084227z--before-spec-dock-1440-light-now.png)・[後](artifacts/20261116t084228z--after-spec-dock-1440-light-now.png)、spec-dock 390 明 いま [前](artifacts/20261116t084227z-01--before-spec-dock-390-light-now.png)・[後](artifacts/20261116t084228z-01--after-spec-dock-390-light-now.png)、housing-lifecycle 1440 暗 いま [前](artifacts/20261116t084227z-02--before-housing-lifecycle-1440-dark-now.png)・[後](artifacts/20261116t084228z-02--after-housing-lifecycle-1440-dark-now.png)、housing-lifecycle 390 暗 いま [前](artifacts/20261116t084227z-03--before-housing-lifecycle-390-dark-now.png)・[後](artifacts/20261116t084228z-03--after-housing-lifecycle-390-dark-now.png)。全部の数字 [前](artifacts/20261116t084227z-04--before-result.json)・[後](artifacts/20261116t084228z-04--after-result.json)。
- 試しの URL（本人の確かめ用、確かめまで残す）：tailnet `http://100.85.74.8:18607/`（spec-dock は `/r/github.com/chemitaro/spec-dock/`、housing-lifecycle は `/r/github.com/chemitaro/housing-lifecycle/`）。止め方：`lsof -nP -iTCP:18607 -sTCP:LISTEN` の PID に `kill <PID>`（またはこのセッションに頼む）。

## Outcome

構造の図の道具の帯から依存の線の切り替え（待っている線｜すべての線｜線なし）を消した。依存の線は常にすべての線の描き方（終わった依存は薄く、待っている依存は目立つ）で出る。見えない相手との線、これからの終わった端の線は今どおり描かない。保存は `specdock.graph.v3` のまま `{mode, range, legend}` になり、前の deps は読まずに捨てる。390px の道具の帯は 339px → 239px に短くなった。

## Verification

- 仕様のレビュー合格（round-1）、最終品質ゲート合格（`3dab89a64`、make lint・全体の pytest 3956 passed）。
- PR #608（head `3dab89a64`）：CI すべて成功（check ×2、route、spec-dock-check、provider-tests、Provider distribution parity ubuntu・macos）、mergeStateStatus CLEAN（2026-11-16）。
- 実データの48通り（前後 × 24）で edgeAudit の違反0、構造の図のエラー0、線の数は前後で同じ（上の S-05）。

## Residual Risks / Follow-ups

- 逸脱：impl-sol を Codex から Claude Opus 5.5 / medium に切り替えた（codex-symlink-refusal。iss-00603 と同じ原因で、Codex の実装担当は chat-scratch の symlink を直すまで使えない）。
- 配布の手引き・リリースノート（線の切り替えがなくなり、前の「待っている線」「線なし」の選択は捨てられること）は次のリリースの Issue で書く。
- 試しの Orca の印は、試しの origin（18607）を Orca 側が許していないので出ない（CORS。前後とも同じで、この変更とは関係ない）。
