---
種別: レポート（Issue）
ID: "iss-00640"
関連GitHub: ["#640"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## PR

- https://github.com/chemitaro/spec-dock/pull/643（head `c8d2679f8`）。CI はすべて pass（provider-tests・Provider distribution parity（macOS・ubuntu）・check・spec-dock-check・route）、mergeable CLEAN（2026-11-17）。マージは統括が行う。

## Outcome

幅 1000 前後では、状態の札と道具の列は1行に入らない（帯 976px に対し、札 779 + 道具 428、構造の図は 748 + 519）。1行にするには札か道具の文字を消すほかないので、決まった形（札を1行目、道具を2行目の右寄せ）を選んだ（requirement.cue の decisions）。
構造の図は既にその形だったので変えていない。横断の構造では、札とまとめの行が1つの列にあるため道具の列がまとめの行の下（4行目）に落ちていた。PC だけ `.gx-left` を `display: contents` にし、まとめの行を `order: 1; flex-basis: 100%` にして、札 → 道具 → まとめの行の順に並べた（allgraph.css の7行。DOM・JavaScript・スマホの並びは変えていない）。

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー）：round-1 **合格**（P0 0、P1 0、P2 1：F-01 の欄を開いた形とまとめなしの形を確かめる検査がない、P3 1：641 の境目は小数の幅で隙間ができる）。合格の後、P2 は実機の確かめ（R-04・D-04・T-03）に2つの形を足し、P3 は条件を `@container app not (max-width: 640px)` にして直した。round-2 **合格**（指摘0）。結果 `.workbench/spec-review/iss-00640/round-{1,2}.json` と `.check.json`、応答 `review-response.md`（reviewed_sha `0ef2dfeae`、文書は sha256 で固定）。
- round-2 の間に worktree の tests/ を書き始めた（S-01 の Red）。レビューした3つの文書の sha256 は round-2 の後も同じ（`review-response.md`）。
- round-2 の後に、実機で「知らせのない状態の置き場」をこの PC の写しから作れないと分かり、R-04 の受け入れと D-04 の「まとめなしの形」を「実機の頁で `.ax-sum` を hidden にした形」に直した（意味は同じ。測りの手段の言い換え）。最終品質ゲートはこの後の sha256 で固定した。

## 実装の記録

- 開始のコミット `0ef2dfeae`（origin/main）。実装はタスク担当（Claude Opus 5.5 / medium、このセッション）。変更が画面の CSS の数行で、テストで確かめられる計算の変更がない（`barBottom()` は変えず、検査の写しを足すだけ）ので、Codex の実装担当は起こしていない（plan の execution の rationale）。
- S-01：Red `01c83d6db`（T-01 が落ち、T-02 は検査の写しの変更だけで通ることを確かめた：30件中1件が落ちる）→ Green `c8d2679f8`（allgraph.css D-01。節目の54件合格）。
- S-02：`make lint` pass。static-inventory.json は dashboard の資産を持たないので変わらない。全体の `uv run pytest` は最終品質ゲートのテストの列。

## 最終品質ゲート

- キャンペーン iss-00640-fqg-1（quality-gate-reviewer opus / medium、second opinion なし、範囲 `0ef2dfeae..c8d2679f8`、観点 functional-correctness・requirements-closure・test-adequacy・compatibility-regression、test_commands `make lint`・`uv run pytest`）：attempt 01（`c8d2679f8`）で **合格**。review lane P0〜P3 0、coverage complete。`make lint` exit 0、`uv run pytest` exit 0（4168 passed、7 skipped）。
- 同じコミットのテストの列の最初の実行は、道具の背景の実行の上限（30分）で 96% の地点で止められた（結果なし、ログは `attempts/01/killed-run/`）。上限を2時間にして、全体をやり直した。
- closure は worktree の `.workbench/final-quality-gate/iss-00640-fqg-1/closure.md`。PR の直前に origin/main を fetch し、新しいコミットがないことを確かめた（合格のコミットが PR の head）。

## 実機の確かめ（S-03、タスク担当）

- 試しのサーバー：直す前は開始のコミット `0ef2dfeae` の wheel を隔離した venv（`.workbench/iss-00640/venv-base`）で 127.0.0.1 の 18641 に、直した後は `c8d2679f8` の wheel（`.workbench/iss-00640/venv`）で `--tailscale` の 18640 に。どちらもこの PC の状態の置き場の写し（iss-00616 の写し）を `--state-root` に、`XDG_CONFIG_HOME` の試しの設定（`orca_web.port` 18840）で `dashboard serve --offline`。試しの orca は `relay_orca.py`（GET だけで常駐の orca-web を中継）を 127.0.0.1 と tailnet の 18840 に。常駐の 47800・8791、道具の環境には触れていない。
- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）、`.workbench/iss-00640/tools/measure640.mjs`。数字は [直す前](artifacts/20261117t082914z-01--m-base.json)・[直した後](artifacts/20261117t082914z-02--m-after.json)。上端・下端は画面の y（px）、『これから』。

| 画面・幅 | 札（上〜下） | 道具（上〜下、右端） | まとめの行（上〜下、幅） | 帯の下端 |
|---|---|---|---|---|
| 横断 1000 直す前 | 68〜100 | **168〜200**、988 | 108〜160、779 | 200 |
| 横断 1000 直した後（明・暗） | 68〜100 | **108〜140**、988 | 148〜200、976 | 200 |
| 横断 1280・1440 直した後 | 68〜100 | 68〜100（同じ行）、帯の右端 | 108〜160、帯の幅 | 160 |
| 構造の図 1000・1280（前後で同じ） | 169〜201 | 209〜241、988・1268 | — | 241 |
| 構造の図 1440（前後で同じ） | 169〜201 | 169〜201（同じ行） | — | 201 |
| 390（横断・構造の図） | 札・まとめの行・道具の矩形と最初の表示が、直す前とすべて同じ | | | |

- F-01：Scope の欄を開いた 1440（帯 774）では、札が2行に折り返し（68〜138）、道具が次の行の右寄せ（146〜178、右端 786 = 帯の右端）、まとめの行がその下（186〜238）。まとめの行を hidden にすると、帯は 1000 で 68〜140（札と道具の2行）、1440 で 68〜100（1行）。
- 最初の表示：すべての組で ty = 帯の最も下の下端（図の領域の座標）+ 8（横断 1000：200 − 56 + 8 = 152、1280・1440：112）。
- 線の検査：横断の構造の 1000・1280・1440・390 × これから・いま・全体 × 明暗の24組で、edgeAudit の total の違反（boxHits・ownHits・overlaps・diagonal・portShare・trunkOverlaps・frameExits・failed・missing・markOverflow）がすべて0、横のスクロールなし、頁の例外0。
- 写し：[直す前 横断 1000](artifacts/20261117t082912z--base-allgraph-1000-light.png)（道具がまとめの行の下）→ [直した後 横断 1000 明](artifacts/20261117t082912z-01--after-allgraph-1000-light.png)・[暗](artifacts/20261117t082912z-02--after-allgraph-1000-dark.png)、[1280](artifacts/20261117t082913z--after-allgraph-1280-light.png)、[1440](artifacts/20261117t082913z-01--after-allgraph-1440-light.png)、[390](artifacts/20261117t082913z-02--after-allgraph-390-light.png)、[構造の図 1000](artifacts/20261117t082913z-03--after-graph-1000-light.png)、[欄を開いた 1440](artifacts/20261117t082914z--after-allgraph-1440-panel.png)。
- 試しの URL（本人の確かめ用、確かめまで残す）：tailnet の 18640 番の `/graph`（URL は統括への報告で伝える）。止め方：`kill $(lsof -tnP -iTCP:18640 -sTCP:LISTEN) $(lsof -tnP -iTCP:18840 -sTCP:LISTEN)`。直す前の 127.0.0.1 の 18641 も比べるために残す（同じ止め方で 18641）。

## 逸脱と判断

- 計画で Codex の実装担当を起こさなかった（上の『実装の記録』。依頼書の「テストで確かめられる計算は Codex をなるべく」に当たる変更がない）。
- 仕様の文書の round-2 の後の言い換え（上の『レビュー記録』）。
- 横断の構造の PC で、まとめの行の幅が札の列の幅（779）から帯の幅に広がった（requirement.cue の decisions。省略が減る）。

## Residual Risks / Follow-ups

- Scope の欄を開くと帯が狭くなり行が増えるが、最初の表示はその時に置き直さないので、図の上端が帯の下に少し隠れる（欄を開く前からの振る舞い。[写し](artifacts/20261117t082914z--after-allgraph-1440-panel.png)）。必要なら別の Issue で、帯の高さの変化（ResizeObserver）で、読者が動かしていない間だけ置き直すとよい。
- 1000 前後で1行に並べたいなら、道具の文字（収める・入れ子）を印だけにする案がある（構造の図で約 100px 減り、1280 で1行に入る）。この Issue では札と道具の文字を変えていない。
