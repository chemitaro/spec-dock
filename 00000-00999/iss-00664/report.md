---
種別: レポート（Issue）
ID: "iss-00664"
関連GitHub: ["#664"]
最終更新: "2026-11-18"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

**原因はテストの不安定さで、利用者に見える不具合ではない。#661（iss-00655、`b472b32eb`）から落ち始めた。**

- `views/allgraph.js` の `whenStyled` は、画面の CSS が効く（`.gx` が position: absolute）まで requestAnimationFrame で待ち、`performance.now()` で 3000ms を過ぎると打ち切って `initialView()`・`applyT()` を呼ぶ。`applyT()` は毎回 `motion.moved()` を呼び、is-still を付けて 300ms の時計を始める。
- ハーネス（`tests/js/dashboard_allgraph_command_screen.mjs`）は CSS の効いた状態を与えないので、描くたびに待ちの連鎖が残り、どれも打ち切りまで続く。`A.el` はモジュールの変数なので、前の run（`cross`〜`sheet`）で始まった連鎖も、次の run の画面で打ち切られる。計測では、motion run の step 1 の中で、打ち切り（経過 3035〜3201ms）が 7〜18回起きていた。
- 打ち切りが motion run の step 1（偽の時計を 400ms 進める）の後に来ると、is-still が付き、外す時計は偽の時計の上で待ったままになり、`shots[1].still` が True になる。来る時刻は、機械の速さと先の run の長さ（実時間）で決まる。
- #661 は、ハーネスの `performance.now` に偽の時計の進み（skew）を足した（ホイールの一続きの判定のため）。これで打ち切りまでの実時間が縮み、前の run の連鎖の打ち切りが motion run に入るようになった。Linux の CI は速く、入らなかったと読む。
- ブラウザーでは CSS がすぐ効くので、待ちは最初の絵で終わる（実機で確かめた。下の表）。

### 各マージでの落ちた回数（単独10回、macOS の手元、2026-11-18）

| マージ | 内容 | 落ちた回数 |
|---|---|---|
| `92e26aff7`（#649） | iss-00646（このテストを足した） | 0/10 |
| `106f214e8`（#658） | iss-00648 | 0/10 |
| `afe2df5c2`（#659） | iss-00650 | 0/10 |
| `3f0e1e9e0`（#660） | iss-00657（点の切り替え 12枚×0.1秒） | 0/10 |
| `b472b32eb`（#661） | iss-00655（ハーネスの `performance.now` に skew） | **9/10** |
| `fa9824cb9`（#662） | iss-00656 | **6/10** |

### 直し方（テストだけ、画面のコードは変えない）

- ハーネスに `run.styled` を足した（兄弟の `dashboard_allgraph_screen.mjs`・`dashboard_graph_command_screen.mjs` と同じ決まり。`getComputedStyle` が `.gx` に position: absolute を返す）。
- motion run と input run（iss-00655。最初の見え方を前提にする）に `styled: True` を付けた。最初の見え方は最初の描画で決まり、前の run から残った待ちも、その run の最初の絵で終わる。

## Verification

- T-01：`test_the_motion_stills_and_watches_on_the_cross_repository_structure` を単独に20回、**0/20 落ち**。
- T-02：`whenStyled` の打ち切りを一時的に 0ms と 1e9ms に変えて、このテストのファイル（23件）が両方で通る（戻した）。
- T-04：上の表。
- `make lint`：通過。`uv run pytest`（全体、手元の macOS）：4306 passed・7 skipped（1802秒）。GitHub CI（PR #665）もすべて pass。
- T-03（実機、1440×900 の headless Chrome、`--disable-features=MacAppCodeSignClone`、CDP の Browser.close で閉じた）：この worktree の editable の venv の `spec-dock dashboard serve --offline --port 18664`（127.0.0.1 だけ、iss-00657 の状態の置き場の写し）と、常駐の orca-web を GET で読むだけの中継（18864）。`/graph` で各操作の直後と 0.6秒後：

| 操作 | 直後 is-still・動く絵 | 0.6秒後 is-still・動く絵 | 0.3秒で見えた絵の種類 |
|---|---|---|---|
| 読み込み後 | false・24 | false・24 | 3 |
| ドラッグの後 | true・0 | false・24 | 3 |
| ホイールの後 | true・0 | false・24 | 4 |
| キー（→）の後 | true・0 | false・12（画面の外の絵は is-off） | 4 |

  ブラウザーのエラー 0。常駐の 47800・8791、道具の環境には触れていない。

## レビュー記録

- spec-review（spec-reviewer opus / medium、standard、2人目なし）：round-1 **合格**（P0 0・P1 0・P2 1・P3 1）。この worktree の `.workbench/spec-review/iss-00664/round-1.json`・`.check.json`。合格した文書の sha256：requirement.cue `bc4ad008…`、design.cue `3de8bd6c…`、plan.cue `be3eef49…`、explanation.html `dcea2358…`。P2 は下の残りの1つ目、P3 は説明資料と S-03 の状態の食い違い（後で S-03 を done にした）。
- 最終品質ゲート（quality-gate-reviewer opus / medium）：attempt 01 で **合格**（`01f6f14b1`、P0/P1 0、P3 1）。closure：この worktree の `.workbench/final-quality-gate/iss-00664/closure.md`。
- 実装：方針と同じセッションの例外（Claude Opus 5.5 / medium、変更がテスト2ファイルで調査と一体のため）。コミット `01f6f14b1`、PR #665。

## Residual Risks / Follow-ups

- styled を付けない他の run（`cross`〜`sheet`）でも、前の run から残った待ちが実時間で打ち切られる仕組みは残る。今のそれらの検査は打ち切りの有無に左右されないので、この Issue では変えない（spec-review の P2）。
- 画面の側では、`whenStyled` の連鎖が、作り直した画面（`A.el` が新しい）でも続く。ブラウザーでは CSS がすぐ効くので利用者には見えない。直すなら、連鎖を始めたときの `A.el` と違えば止める、の小さな変更になる（範囲外、記録だけ）。
