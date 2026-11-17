---
種別: レポート（Issue）
ID: "iss-00621"
関連GitHub: ["#621"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、同じレビュアー、2人目なし）：round-1 合格（P0 0、P1 0、P2 3、P3 2）。5件とも直した（`.workbench/spec-review/iss-00621/review-response.md`：iss-00616 への `markIds` の口、0人の worktree の札の高さの受入、Epic R-14 の実データの親子の順、S-03 の直してよい理由、仕様のレビューの記録の位置）。round-2 **合格**（P0〜P3 すべて0）。結果はこの worktree の `.workbench/spec-review/iss-00621/round-{1,2}.json` と `.check.json`（reviewed_sha `edfabc759`）。
- **合格した文書の sha256**：requirement.cue `07a0c0733908444f533302c9cb16a1d8e0e428b219dfadb1a3568114fcf4df6b`、design.cue `ab4dc444699c87032298221c44f820073fb417319044bf57bcd8842182f3dcde`、plan.cue `9c3773cb2405ac311a605ae322122ffe4133e99ebe705baeb7ec96b3c2827877`、explanation.html `d686e24d2dbf732e4c1a9ec9821d8456e1616a2b0004fac9ce3e4d56cd1bce42`。
- **仕様の変更（実機の確かめから、2026-11-17）**：枠の見出しの worktree の印が見出しの右の端（幅の広い枠では画面の外）に出たので、題名の広がりを自分の幅までにして印を題名のすぐ後に続ける（requirement.cue の decisions と R-01 の受入4、design.cue D-04、plan.cue T-04）。round-3 **合格**（P0 0、P1 0、P2 1：直しの手順が台帳にない → S-02 を doing、S-03 を todo に開き直した。P3 0）。結果 `.workbench/spec-review/iss-00621/round-3.json`（reviewed_sha `ce999075e`）。
- **今の合格した文書の sha256**（round-3、S-02・S-03 の status の開き直しの前）：requirement.cue `8703d689ccec242a9cc6f1cd704c976197c57d07f9ca8b66ee9e40a0502f6dc5`、design.cue `e9edb9e92b162c813656f4eebba4b605262fa6b410ae95d5eb7b9ab134225c4a`、plan.cue `5a936266977ec84859305278992ae32e44f614d7036d5cac93b5782951810e7a`。その後の変更は plan.cue の手順の status だけ。

## 実装の記録

- 開始のコミット `edfabc759`（origin/main、iss-00620・iss-00614・iss-00627 の後）。
- 開始の基準（`.workbench/implement/iss-00621/start.md`）：S-01 の節目の4ファイルが 63 passed。
- S-01（`dd775ba8d` テスト先行 → `99b375648`）：T-01・T-02（`test_dashboard_orca_marks_js.py`）、T-03（`test_dashboard_orca_views_js.py` の `run_panel`）を書いて落ちることを確かめ、D-01（`orca_marks.js` の WeakMap の記録、`markAgentAt`・`markIds`）、D-02（`panel.js` の `openAgent`）で通した。節目 67 passed。
- S-02（`688d9eca0` テスト先行 → `31bb71d04`）：T-04〜T-06 を書いて落ちることを確かめ、D-03（graph・allgraph・board・panel の押し）、D-04（`draw.js` の枠の見出しと木の枠の箱の `wtMark`、`graph.css` の `.gx .gx-fh > .wt { flex: none; }`）、D-05（`parts.js` の `.sd-card__agents`、`parts.css`）で通した。今の `preferTab("agents")` を固定していた静的な検査と札の HTML の検査は、R-02・R-05 の置き換えに合わせて直した。節目（S-01 の4ファイル＋`test_dashboard_screens_js.py`＋`tests/unit/presentation/`）262 passed。構造の図の golden と線の検査も通る。
- S-03（`124f9b9c7`）：`make lint` 合格（ruff check・format・mypy）。全体の `uv run pytest` は 4073 passed、7 skipped（1898秒）。dashboard の資産は `static-inventory.json` に載っていないので、sha256 の直しは要らなかった。
- 仕様の変更（round-3）の直し（`ce999075e` の上に、`3dfc3e083` テスト先行 → `797690b4f`）：T-04 に、`graph.css` の `.gx :is(.gx-ini, .gx-epic) > .gx-fh > .gx-fttl { max-width: max-content; }` が配置の規則（`max-width: none`）より後にあることの静的な検査を足して落ちることを確かめ、その規則を配置の規則のすぐ後に足して通した。`make lint` 合格、全体の `uv run pytest` 4081 passed、7 skipped（1956秒）。S-02・S-03 を done にした。

## 逸脱と判断

- 2026-11-17 S-01 の担当：plan.cue では impl-sol（Codex GPT-6.1 Sol / medium）だが、Codex が chat-scratch の symlink の拒否で止まったので、統括が了承済みの取り決めどおり、Claude Opus 5.5 / medium（impl-claude）が S-01 から S-03 まで引き継いだ。
- 2026-11-17 実装の判断（D-01 の足し）：`buildMarks` の結果に `marks` の配列がないとき（結合テストの偽の部品 `tests/js/fake_dom.mjs` の `fakeOrca` がそうだった）は、`built.marks.map` が例外を出して置き場を空にしていたので、印はそのまま描き、記録は空の並びにする（押しても F-01 でタブを開くだけ）。印の表示を落とさないための守り。
- 2026-11-17 実装の判断（D-04）：`.gx .gx-fh > .wt { flex: none; }` を足した（設計の「足りなければ」の規則）。題名だけが縮み、worktree の印が縮まず題名の行に残ることを CSS で固める。実機の確かめは S-04。
- 2026-11-17 実装の判断（D-05）：`.sd-card__meta:not(:has(> :not(.sd-orca:empty))) { display: none; }` は残した（置き場が meta の外へ出て効かなくなるが、消しても HTML は同じで、既存の静的な検査を変えずに済む）。T-03 の node のテストは、計画のとおり `test_dashboard_orca_views_js.py` の `run_panel` に、エージェントのいる構造を足して書いた（`El.prototype.querySelector` をその中だけ足した）。

- 2026-11-17 タスク担当：最終品質ゲートの観点の `ui-behavior`（plan.cue）は、レビューの契約の観点にないので `e2e-user-flow` に置き換えた（意味は同じ：画面の動き）。

## 実機の確かめ（S-04、2026-11-17）

- 試しのサーバー：この worktree の `797690b4f` の wheel を隔離した venv（`.workbench/iss-00621/venv`）に入れ、この PC の状態の置き場の写し（`.workbench/iss-00621/state`）と `XDG_CONFIG_HOME` の試しの設定（`orca_web.port` 18821）で `spec-dock dashboard serve --offline --tailscale --port 18621`。試しの orca は `relay_orca.py`（GET だけで常駐の orca-web 8791 を中継し CORS の頭を足す。iss-00629 の写し）を 127.0.0.1 と tailnet の 18821 に。常駐の 47800 と 8791 の設定、道具の環境には触れていない。エージェントには何も送っていない。
- 試しの送り先（統括が用意）：taikyohiyou_project の作業中の Epic epic-02233（worktree `worktree/epic-02233`）に、親 A（`…be2027b0`）→ 子 B（`…36a945a8`）と、関係のない C（`…9af19d61`）。同じ箱の2人：spec-dock の iss-00621（タスク担当 `…97b7f902` → 実装担当 `…44e2ac2c`）。
- 道具：`.workbench/iss-00621/tools/probe.mjs`（headless Chrome、`--disable-features=MacAppCodeSignClone`、CDP の `Browser.close` で閉じる。印の中心を `Input.dispatchMouseEvent` で押す）。結果 `.workbench/iss-00621/shots2/results.json`、写し `shots2/*.png`（1440・390 × 明・暗）。

| 確かめ（受入） | 1440 明 | 1440 暗 | 390 明 | 390 暗 |
|---|---|---|---|---|
| R-01 枠の見出しの `.wt`（title「worktree：worktree/epic-02233」、`.gx-agents` の外、題名と同じ行） | ○ | ○ | ○ | ○ |
| R-01 題名の右の端から印まで（8px 以内） | 6.2px | 6.2px | 5.2px | 5.2px |
| R-01 『横断の構造』の枠の見出しの `.wt` | ○ | ○ | ○ | ○ |
| R-03 枠の印の並び（C, A, B ＝ 関係なしが左、親 → 子が右。Epic R-14 の受入3） | ○ | ○ | ○ | ○ |
| R-02 構造の図の枠の2つ目の印 → A のチャット（`/embed/agent?id=`） | ○ | ○ | ○ | ○ |
| R-02 横の欄の見出しの3つ目の印 → B | ○ | ○ | ○ | ○ |
| R-02 spec-dock の iss-00621 の箱の2つ目の印 → 実装担当 | ○ | ○ | ○ | ○ |
| R-02 ボードの札の2つ目の印 → A | ○ | ○ | ○ | ○ |
| R-02 『横断の構造』の枠の2つ目の印 → A | ○ | ○ | ○ | ○ |
| R-05 札の `.sd-card__agents`（meta の外、`display: flex`、印が札の縁の内） | ○ | ○ | ○ | ○ |
| R-05 印のない札の専用の行が見えない（35枚のうち出ている行 3、印のない出ている行 0） | ○ | ○ | ○ | ○ |
| 線の検査（リポジトリの構造の図 taikyohiyou・spec-dock、『横断の構造』の全体）の違反 | 0 | 0 | 0 | 0 |
| ブラウザーのエラー（ダッシュボード） | 0 | 0 | 0 | 0 |

- 印の並びは、要約の `agents` の順（A, B, C）ではなく、部品の `buildMarks` の順（C, A, B）で、SpecDock が並べ替えていない（R-03）。spec-dock の箱も、親（タスク担当）→ 子（実装担当）。
- 1440 暗では、試しの中継が、開いたチャットの中の orca-web の部品（`/embed/send-dom.js`・`send-view.js`）の読み込みで接続を切った（ERR_CONNECTION_RESET）。ダッシュボードのエラーではなく、試しの中継（同時の読み込み）の問題。
- 『+N』の押し（選びを変えない）は、5人以上のいる worktree がないので実機では写していない。node のテスト（T-01・T-03）で確かめた。
- 直す前（`ce999075e`）の写し（`.workbench/iss-00621/shots/`）で、枠の見出しの `.wt` が見出しの右の端（1440 で x=1614、画面の外）に出ていたので、仕様を直して（round-3）`797690b4f` で直した。

## Residual Risks / Follow-ups
