---
種別: レポート（Issue）
ID: "iss-00632"
関連GitHub: ["#632"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー）：round-1 不合格（P1 1：failed のリポジトリが空の枠になる、P2 2：まとめの行の pointer-events、実機の稼働の印の用意、P3 1：節目のコマンドの -k）→ 直した（`.workbench/spec-review/iss-00632/review-response.md`）。round-2 **合格**（P0 0、P1 0、P2 1、P3 1）。結果 `.workbench/spec-review/iss-00632/round-{1,2}.json` と `.check.json`（reviewed_sha `3f5f8d8e9`）。
- **合格した文書の sha256**：requirement.cue `559d71833c58b7dd4e56fb0578276dcae26da3c5df0aa7062658e85507ef0a68`、design.cue `9ccbc79de4f294f6cf490e97700a1b3893d69162fe2f78dac2c72f97d2e5724a`、plan.cue `26d946fa8559d33ba2e4f7e7cf2fc6585ed83fab6529a5cd86a5e1b2c7cc9028`。
- round-2 の P2（`.ax-sum` を none にしても親の `.gx-left` が auto なので帯の空きが図に届かない）は、実装で `.gx-left` を none、`.gx-next` と `.ax-sum li` を auto にして満たす（R-03 の意味のまま。『逸脱と判断』に書く）。P3（R-01 と判断A の文に failed の例外が書かれていない）は、R-02・F-01・D-02 が決める（failed は知らせのすべてを枠に残す）ので文書は変えない。

## 実装の記録

- 開始のコミット `3f5f8d8e9`（origin/main）。
- 逸脱 codex-symlink-refusal：S-01 の impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_6e27e955ef46、launch codex / gpt-6.1-sol / medium）は、chat-scratch の writable root の symlink（UnsupportedOperation）で手元のコマンドを起動できず、変更なしで止まった（worker_done failed、HEAD `3f5f8d8e9`・worktree clean を確かめた）。plan の rationale と統括の了承どおり Claude Opus 5.5 / medium に切り替え、同じ値のタスク担当のこのセッションが S-01 を行った（別のセッションは起こしていない）。
- S-01（Claude Opus 5.5 / medium、このセッション）：Red `15426f7ae`（`tests/js/dashboard_allgraph_notices.mjs`・`test_dashboard_allgraph_notices.py`、7件が落ちる）→ Green `619edc5b9`（logic.js D-01、notices.js D-02。節目の17件合格）。
- S-02（同上）：Red `359eba439`（`dashboard_allgraph_screen.mjs` にまとめの行の写しと `view.sum` の口、`test_dashboard_allgraph_screen.py` に T-03・T-04、既存の知らせの検査を新しい置き場に直す。7件が落ちる）→ Green `2d4b52ed9`（allgraph.js・allgraph.css D-03。節目の62件合格）。
- S-03：`6f0ad7f84`（ruff の import と書式）。`make lint` pass。static-inventory.json は dashboard の資産を持たないので変わらない。全体の `uv run pytest` は最終品質ゲートのテストの列で走らせた（ほかの worktree の全体のテストが並行して重く、手元の先の実行は 30 分の上限で止められたため。同じコミットで2回走らせない）。

## 逸脱と判断

- round-2 の仕様レビューの P2（R-03）：`.ax-sum` を none にしても、親の `.gx-left` が `.gx-bar > *` の auto のままだと帯の空きが図に届かない。`.gx[data-screen="allgraph"] .gx-left` を none、`.gx-next`（状態のチップ。今までどおり押せる）と `.ax-sum li` を auto にした（横断の構造だけ。各リポジトリの構造の図は変えない）。実機で、行の上はその行に、行の右の空きは図（`.gx-view`）に当たることを確かめた。
- 実機で見つけて直した（設計の範囲の内の判断）：まとめの行が `.gx-left` の幅を広げ、1440 で道具の列（拡大・収める・範囲）が次の行へ落ちた。`.ax-sum` を `width: 0; min-width: 100%` にして、まとめの行は状態のチップの列の幅に収め（長ければ省略、全文は title）、帯の幅を変えないようにした。1440 では道具の列がチップと同じ行（上端 68px）に戻った。1000 では直す前から道具の列がチップの下の行にある（上端 168px、直す前と同じ）。
- 仕様レビュー round-2 の P3（R-01 と判断A の文に failed の例外がない）は、R-02・F-01・D-02 が決めているので文書を変えていない。
- 計画の S-01 の impl-sol は上の逸脱のとおり。

## 最終品質ゲート

- キャンペーン iss-00632-fqg-1（quality-gate-reviewer opus / medium、second opinion なし、範囲 `3f5f8d8e9..6f0ad7f84`、観点 functional-correctness・requirements-closure・test-adequacy・compatibility-regression、test_commands `make lint`・`uv run pytest`）：attempt 01（`6f0ad7f84`）で **合格**。review lane P0〜P3 0、coverage complete。`make lint` exit 0、`uv run pytest` exit 0（4101 passed、7 skipped）。closure は worktree の `.workbench/final-quality-gate/iss-00632-fqg-1/closure.md`。
- PR の直前に origin/main を fetch し、新しいコミットがないことを確かめた（合格のコミットが PR の head）。

## 実機の確かめ（S-04、タスク担当）

- 試しのサーバー：直した後は `2d4b52ed9` の資産（`6f0ad7f84` と同じ。後はテストの書式だけ）の wheel を隔離した venv（`.workbench/iss-00632/venv-after`）に入れ、この PC の状態の置き場の写し（iss-00629 の写し、`.workbench/iss-00632/state-after`）と `XDG_CONFIG_HOME` の試しの設定（`orca_web.port` 18832）で `spec-dock dashboard serve --offline --tailscale --port 18632`。直す前は開始のコミット `3f5f8d8e9` の wheel を 127.0.0.1 の 18631 に。試しの orca は `relay_orca.py`（GET だけで常駐の orca-web を中継し CORS の頭を足す）を 127.0.0.1 と tailnet の 18832 に。常駐の 47800 と 8791、道具の環境には触れていない。
- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）、`.workbench/iss-00632/tools/measure632.mjs`。最初の表示を測った後、倍率 100% にし、稼働の印（`.orca-mark`）の数が2回続けて同じになってから測る。数字は [直す前](artifacts/20261117t050606z-01--measure-before.json)・[直した後](artifacts/20261117t050606z-02--measure-after.json)。

| 組（`/graph`） | 1440・1000・390 × これから・いま・全体 × 明・暗（18） |
|---|---|
| edgeAudit の total の違反（boxHits・ownHits・overlaps・diagonal・portShare・trunkOverlaps・frameExits・failed・missing・markOverflow） | 直す前・直した後ともすべて0 |
| 縮めた枠のはみ出し（scrollHeight > clientHeight） | 直す前・直した後ともすべて0（縮めた枠は これから 6・いま 42・全体 12） |
| 稼働の印の数 | これから 5〜6・いま 33〜34・全体 37〜38（0 の組なし） |
| まとめの行 | 直す前 なし → 直した後 2行（構造が更新されていません：9つ、PR の状態が分かりません：9つ） |
| 知らせの行のある枠 | 直す前 9 → 直した後 0（この写しには読めないリポジトリがない） |
| 最初の表示の上端がまとめの行の下 + 8 以上 | すべての組で満たす |
| まとめの行のポインター | 行の上はその行、行の右の空きは図（`.gx-view`）に当たる（18組すべて） |

- 縮めた枠の測り直し（R-04）：直す前（`3f5f8d8e9`）から allgraph.js の `checkRows` が `compactNeeds`・`headsDiffer`・`tallNeeds` で測り直しており（iss-00627 `10610ce89`）、18組ではみ出し0。この Issue ではその仕組みを変えていない。
- 写し（最初の表示）：直す前 [1440 明 これから](artifacts/20261117t050604z--before-allgraph-1440-light-next.png)（各枠の見出しの下に「6時間前から更新されていません…」「PR の状態が分かりません。」が繰り返す）→ 直した後 [1440 明 これから](artifacts/20261117t050605z--after-allgraph-1440-light-next.png)、[1440 暗 全体](artifacts/20261117t050605z-01--after-allgraph-1440-dark-all.png)、[390 明 これから](artifacts/20261117t050605z-02--after-allgraph-390-light-next.png)、[390 暗 いま](artifacts/20261117t050606z--after-allgraph-390-dark-now.png)。まとめの行は状態のチップの下に2行で、長い行は省略（…）される。枠の見出しのすぐ下から図が始まり、1つの枠で 48px（知らせ2行）詰まった。
- 試しの URL（本人の確かめ用、確かめまで残す）：tailnet の 18632 番の `/graph`（URL は統括への報告で伝える）。止め方：`kill $(lsof -tnP -iTCP:18632 -sTCP:LISTEN) $(lsof -tnP -iTCP:18832 -sTCP:LISTEN)`（またはタスク担当・統括に頼む）。直す前の 18631 は確かめの後に止めた。

## 次の提案

- 1000 の幅では、直す前から道具の列がチップの下の行に落ちる（チップの列と道具の列が1行に入らない）。まとめの行はその下に出るので、最初の表示の上端が少し下がる。チップの文字を詰めるか、道具の列をまとめるかは別の Issue で検討するとよい。
- iss-00629 の report の「allgraph.js は #630 の測り直しを使っていない」は誤り（`10610ce89` で入っていた）。統括の了解の記録はこの Issue の requirement.cue の background と decisions にある。

## Outcome

『横断の構造』で、文の決まった種類の知らせ（構造が古い、スナップショットの異常、構造の異常、PR の状態が分からない）を、状態のチップの下に種類ごとに1行でまとめ、当てはまるリポジトリの名前を並べた。リポジトリの枠には、読めなかった理由など、そのリポジトリにだけある知らせだけが残る（図を描けないリポジトリは知らせのすべてが残る）。縮めた枠の測り直しは iss-00627 で既に入っており、実機で働いていることを確かめた。

## Verification

- 仕様のレビュー合格（round-2）。最終品質ゲート合格（`6f0ad7f84`、review P0〜P3 0、`make lint`・`uv run pytest` 4101 passed）。
- 実機：18組すべてで edgeAudit の違反0・縮めた枠のはみ出し0、まとめの行2行、知らせの行のある枠 9 → 0、最初の表示がまとめの行の下、帯の空きが図に届く。
- PR https://github.com/chemitaro/spec-dock/pull/639（head `6f0ad7f84`）。CI（Actions と Commit Status）は observable_ci PASS、merge_readiness READY（2026-11-17T06:03Z、`.workbench/iss-00632/pr-checks.json`）。マージは統括が行う。

## Residual Risks / Follow-ups

- まとめの行の種類が多いと上の帯が高くなる（最大6行。ふつうは1〜2行）。
- 試しのサーバー 18632・18832 は本人の確かめまで残す。
