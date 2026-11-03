---
種別: レポート（Issue）
ID: "iss-00527"
関連GitHub: ["#527"]
最終更新: "2026-11-04"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

iframe 埋め込みの試作（製品のコードなし）。PC の Chrome（ヘッドレス、iPhone の幅と触る操作の模擬）では、D-08、D-09、D-15 のとおりに動くことを確かめた。ただし D-15 に、直すべき穴が1つある（全画面遷移のあと SpecDock が黙る）。PC の Safari は自動操作が使えず未実施。iPhone の実機は利用者の確かめ待ち。

- 試しの仕組み（Artifact）：`artifacts/20261103t151442z--embed-lab.py`（親と子の2つのサーバー、1ファイル）、`artifacts/20261103t151442z-01--chrome-check.mjs`（Chrome を CDP で操る確かめ）、`artifacts/20261103t151442z-02--result-chrome.json`（結果の生データ）。
- 仕様のレビュー：spec-reviewer（opus / medium）が pass（P0・P1 なし、P2 が2件、P3 が1件）。P2 の1件は下の「Safari」、もう1件は「許さない起点の親」の確かめ方で、どちらも本報告に反映した。

## 確かめ方の前提と限界（証拠と仮定）

- 子の図は採用した試作（d2）そのものではなく、D-08 の指の操作だけを入れた最小の図（12個の箱）を使った。d2 の `ROUTER` や画面は載せていない。d2 は、`grep` で `gesturestart` が0件、`pointerdown`/`pointermove` は1本指のドラッグだけで、2本指の拡大縮小は `wheel` だけだった（試作の記述にある「2本指のつまみ」は未実装）。
- 親は `http://127.0.0.1:18527`、子は `http://localhost:18528`（ホスト名も違う本物のクロスオリジン）。Tailscale の IP では待ち受けていない。
- Chrome の触る操作の模擬は、Pointer Events の touch を出すが、iOS Safari の `gesturestart` と、ページ全体の拡大の挙動は再現しない。よって指の操作の結論は **Chrome の範囲だけ**で、Safari と iPhone の結論ではない。
- 許さない起点の親からの埋め込みは、手元に別のホスト名がないため、`frame-ancestors 'self'` だけの道（`/embed-strict`）で「許されない親」を代用した。起点の判定の正規表現は単体で確かめた。実際の別起点（Tailscale の IP の親）は iPhone の手順で確かめられる。

## 項目ごとの結果

凡例：○ 期待どおり、△ 期待どおりだが設計に直しが要る、－ 未実施、待 利用者の確かめ待ち。

| # | 項目 | PC Chrome | PC Safari | iPhone |
|---|---|---|---|---|
| 1 | 許した起点の親（127.0.0.1）が `?embed=1` の子を埋め込める。`X-Frame-Options` なし | ○ | － | 待 |
| 2 | `frame-ancestors 'self'` だけの子は、別起点の親の枠で表示されない（子から何も届かない） | ○ | － | 待 |
| 3 | 指：1本指のタップで選択、同じ箱の2回目のタップで移動（D-08） | ○ | － | 待 |
| 4 | 指：1本指のドラッグで図を動かす | ○（dx=80, dy=48） | － | 待 |
| 5 | 指：2本指のつまみで拡大（`touch-action: none` + Pointer Events） | ○（1.0→2.6、同時のポインター2、ページ全体の拡大 `visualViewport.scale` は 1 のまま） | － | 待 |
| 6 | Safari の `gesturestart` を止めてもページ全体の拡大と競合しない | 発火しないので判定不能 | － | 待（最重要） |
| 7 | `/files/` の資料（`sandbox allow-scripts allow-popups`、`allow-same-origin` なし）が、親→子→資料の入れ子でも `frame-ancestors` を通って表示される | ○ | － | 待 |
| 8 | 資料から親の DOM に触れない／`localStorage` が使えない／API（CORS なし）の `fetch` と `import()` が読めない | ○（全部 BLOCKED）。資料の起点は `null` | － | 待 |
| 9 | `/ds/`：`fetch`、`import()`（CORS が要る道）とスタイルが固有でない起点の資料から読める。`../../../design-system/ds.css` の写しも効く | ○ | － | 待 |
| 10 | トップで開いた資料と SVG も、起点が `null`（sandbox が効く）。`nosniff` あり | ○ | － | 待 |
| 11 | `hello`→`ready`→`navigated`（始まり）。`hello` の前は SpecDock は知らせを送らない（debug は除く） | ○ | － | 待 |
| 12 | `event.source` が親でない（きょうだいの枠からの偽の `hello`）は捨てる。受け入れた `hello` は1回だけ | ○ | － | 待 |
| 13 | 親からの `navigate`（枠を作り直さない）と `theme`。`navigated` で親が `replaceState`、親の URL が追従 | ○ | － | 待 |
| 14 | 履歴：iframe の中の `pushState` が共通の履歴に入り、親の戻る（`history.back()`）で iframe が戻る（`popstate`） | ○ | － | 待 |
| 15 | 履歴：iframe の中の通常のリンク（全画面遷移）も履歴に入り、戻るで戻る | ○（読み込み 1→2→3） | － | 待 |
| 16 | 全画面遷移のあと、親が `hello` を再送しないと SpecDock は `ready` も `navigated` も送らない | △ 沈黙した（下の提案 P-1） | － | 待 |
| 17 | 親が `load` ごとに `hello` を再送すると、遷移のたびに `ready` と `navigated` が揃う | ○ | － | 待 |

観測した見出し（`curl`、試しのサーバー）：`/embed` は `Content-Security-Policy: frame-ancestors 'self' http://127.0.0.1:* http://localhost:* http://100.85.74.8:*`、`/` と `/embed-strict` は `frame-ancestors 'self'`、`/…/files/…` は `sandbox allow-scripts allow-popups; frame-ancestors …` と `X-Content-Type-Options: nosniff`、`/ds/` は `Access-Control-Allow-Origin: *`、`/api/…` は CORS なし。

## 設計（D-08、D-09、D-15）への直しの提案

Epic の文書は変えていない。次は提案で、採否は統括が決める。

- **P-1（D-15、重要）**：iframe の中で全画面遷移（通常のリンク）が起きると、新しい文書は `hello` を覚えていないので、親が再送しない限り何も送らない（項目16）。次のどちらかを書く。
  - (a) 親は iframe の `load` のたびに `hello` を送る（項目17で動作を確認）。SpecDock は `ready` のあと、現在の画面の `navigated` を続けて送る（試作はそうした）。
  - (b) 画面の移動を、枠の中でも `pushState` の移動にそろえ、全画面遷移を起こさない。
  (a) は親に1行の決まりを足すだけなので、(a) を勧める。`reference_cli.md` の契約に、「`ready` のあと、現在の画面の `navigated` を1回送る」と「親は load ごとに hello」を書く。
- **P-2（D-15）**：`navigate` と画面内の移動は、`pushState` で共通の履歴に積まれる（項目14）。「親は `replaceState` だけ」は、そのとおりで足りる。親の URL は戻るのたびに `navigated` で追従する（項目13）。変更は不要。確認の記述として残してよい。
- **P-3（D-09）**：資料を入れ子（親→子→資料）で表示するとき、`frame-ancestors` は祖先すべてに掛かる（項目7）。資料の応答の `frame-ancestors` にも、子の画面と同じ許可リストを付ける（現在の記述は「そこから開く資料は」と書いてあるので、そのまま満たす）。資料の道にだけ `'self'` を付け忘れないよう、テストで「資料も同じ許可リストを持つ」ことを確かめる。
- **P-4（D-09）**：`/ds/` は `import()` と `fetch` に CORS が要り、`<link rel=stylesheet>` と `<script src>` には不要だった。D-09 は `/ds/` と `/vendor/` に `Access-Control-Allow-Origin: *` を付けるので足りる。API の道には付けないこと（項目8）を、テストの項目に明記する。
- **P-5（D-08、要判断）**：採用した試作（d2）には2本指のつまみと `gesturestart` の抑止がない（`wheel` と1本指のドラッグだけ）。D-08 に書いたとおり実装するのは #532 の仕事なので、#532 の受け入れの条件に「2本指のつまみで図だけが拡大し、ページ全体は拡大しない（iPhone の実機）」を足す。最小の実装は `embed-lab.py` の図（Pointer Events の2本指の計算と `gesturestart`/`gesturechange`/`gestureend` の `preventDefault`）が参考になる。
- **P-6（D-08）**：図の上に重ねる操作ボタンの帯と、図の箱が重なると、タップが帯に取られる（試しの最初の失敗で観測）。図の領域の上に帯の高さの余白を取る。

## iPhone の実機の確かめ（利用者にお願いする）

iPhone と Mac が同じ Tailscale のネットワークにあること。

1. Mac で、試しのサーバーを Tailscale の IP で起動する（`tailscale ip -4` で自分の IP を確かめる。ここでは `100.85.74.8`）。この Issue のチェックアウトで：
   ```sh
   cd <iss-00527 のチェックアウト>/spec-dock/initiatives/00000-00999/iss-00527/artifacts
   python3 20261103t151442z--embed-lab.py --bind 100.85.74.8 --tailscale-ip 100.85.74.8
   ```
   親 `18527`、子 `18528`（変えるなら `--parent-port`、`--child-port`）。**終わったら、端末で Ctrl-C して止める**（常駐させない。F-01）。確かめ後の止まりの確認は `lsof -nP -iTCP:18527 -iTCP:18528 -sTCP:LISTEN` が空であること。
2. iPhone の Safari で、次の順に開く。
   - A（枠に入れた状態）：`http://100.85.74.8:18527/`
   - B（拒否の確認）：`http://100.85.74.8:18527/?src=/embed-strict`
   - C（子だけ）：`http://100.85.74.8:18528/embed?embed=1`
   - D（偽の知らせ）：`http://100.85.74.8:18527/?rogue=1`
   - E（再送なし）：`http://100.85.74.8:18527/?autohello=0`
   親の画面の下の黒い欄が知らせの記録（緑の文字）。子の画面の左下に `scale= t= taps= vv=` が出る。
3. チェックリスト（A の画面で。結果を ○／× と、気づきで返してください）。
   - [ ] 親の黒い欄に `sent hello`、`recv ready`、`recv navigated` が出る
   - [ ] 図の箱を1回タップ → 黄色になり `taps` が増える。同じ箱をもう一度タップ → 画面が移り、親の URL の `?p=` が変わる
   - [ ] 1本指で図をドラッグ → 図だけが動き、ページ全体が動かない（外側が引っ張られない）
   - [ ] 2本指で広げる → **図だけ**が拡大する。ページ全体（親も含む）が拡大しない。左下の `vv=` が `1` のまま
   - [ ] 2本指でつまむ → 図だけが縮小する
   - [ ] 拡大の途中で指を離したあと、ページ全体が拡大していない（もし拡大していたら、`vv=` の値を書いてください）
   - [ ] 「全体を収める」「＋」「－」のボタンが効く
   - [ ] 「通常のリンク（全画面遷移）」→ 黒い欄に `hello` の再送と `ready` が出る。Safari の戻るボタンで子の画面が戻る
   - [ ] 「pushState で移る」→ 戻るボタンで戻る
   - [ ] 「外へ(_blank)」が新しいタブで開く（ポップアップを止められない）
   - [ ] 「資料を開く」→ 資料が枠に出て、`parentDom` と `localStorage` が `BLOCKED`、`fetchApi` が `BLOCKED`、`fetchDsCss` と `importDsJs` が `OK`、`cssApplied` が `'ds-loaded'`
   - [ ] B：枠の中が空かエラー（子の図が出ない）。黒い欄に `recv` が出ない
   - [ ] D：黒い欄に `rogue-sent` が出て、そのあと子から `recv` に `drop:not-parent` の記録が出る（`debug` の `m`）。受け入れた `hello` は1回だけ
   - [ ] E：`hello` ボタンを押すまで `ready` が来ない。通常のリンクで遷移した後は何も来ない
   - [ ] C（子だけ）：2本指のつまみで図だけが拡大する。ページ全体が拡大するなら、枠の外でも起きるか
   - [ ] Mac の Safari でも A を開き、親の黒い欄の流れが同じ（自動操作が使えず、PC Safari は未実施のため。Mac の「開発」メニューで Web インスペクタを使ってもよい）
4. 終わったら、結果を ○／× と気づきで返してください。サーバーは Ctrl-C で止める。

## Verification

- `spec-dock scope check iss-00527`：誤り 0、警告 0（要件、設計、計画、説明資料）。
- spec-reviewer（opus / medium）：pass（`.workbench/spec-review/iss-00527/round-1.json`、P0・P1 なし）。
- PC Chrome（156、ヘッドレス、`--disable-features=MacAppCodeSignClone`、CDP の `Browser.close` で終了）：`node chrome-check.mjs` の結果が `artifacts/…-02--result-chrome.json`。エラーなし。
- 後始末：試しのサーバー、Chrome、一時の user-data-dir を止めて消した。`lsof` で 18527、18528、19527 の待ち受けなし、`pgrep` で `embed-lab`、`safaridriver`、Chrome の `remote-debugging-port=19527` なし。Tailscale の IP では一度も待ち受けていない。
- 製品のコード、テスト、Epic の文書、ほかの Scope は変えていない。コミットと PR はない。

## Residual Risks / Follow-ups

- iPhone の実機（特に項目6、`gesturestart` と、2本指のつまみでのページ全体の拡大）は未確認。ここが外れると D-08 の指の操作の記述を直す。
- PC の Safari は、`safaridriver` で `POST /session` に応答がなく（Safari の「リモートオートメーションを許可」が無効と推定。未確認）、自動では確かめられなかった。上のチェックリストの最後の項目で手で確かめられる。
- Chrome の touch の模擬は、タップの遅延（300ms）、スクロールの慣性、iOS のアドレスバーの伸縮による `visualViewport` の変化を再現しない。
- 試作の図は d2 の図ではない。d2 の図の重い DOM（約300本の線）での指の追従の滑らかさは、#532 の実装後に別に確かめる。
- Epic との食い違いは見つけていない（D-15 の穴は提案 P-1 として書いた）。
