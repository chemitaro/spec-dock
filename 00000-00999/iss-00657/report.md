---
種別: レポート（Issue）
ID: "iss-00657"
関連GitHub: ["#657"]
最終更新: "2026-11-18"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

流れる指揮の線の点を、組の間 24px の大小2つの点（頭 3.5px・不透明、6px 後ろの尾 2px・.45）にし、2px ずつずらした止めた絵12枚を 0.1秒ずつ見せて 20px/秒で流すようにした。波紋は 3.6秒（2つ目は 1.8秒遅れ）。減らす設定では1枚だけを見せ、組の形で向きを示す。iss-00646 の方式（線ごとの小さな SVG、合成スレッドの opacity の切り替え、動かす間・画面の外・裏で止める）はそのまま。

### 動きの数（前と後）

| | 前（iss-00646、`106f214e8`） | 後（この Issue） |
|---|---|---|
| 点（組）の間 | 8px（`0.1 7.9`） | 24px（`0.1 23.9`） |
| 組の形 | 同じ点（太さ 2） | 頭 3.5（不透明）＋ 6px 後ろの尾 2（.45）。選んだ線は 4.5・3 |
| 1回のずれ | 2px | 2px |
| 枚数 | 4 | 12 |
| 1枚の時間 | 0.05秒 | 0.1秒 |
| 速さ | 40px/秒 | 20px/秒 |
| 1周（同じ絵に戻る） | 0.2秒（5Hz） | 1.2秒 |
| 波紋 | 2.4秒、2つ目 1.2秒遅れ | 3.6秒、2つ目 1.8秒遅れ |

## Verification

（実機の確かめと最終品質ゲートは下の節）

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし）：round-1 **合格**（P0 0、P1 0、P2 0、P3 2）。結果はこの worktree の `.workbench/spec-review/iss-00657/round-1.json` と `.check.json`（reviewed_sha `92e26aff7`）。
- **合格した文書の sha256**（round-1）：requirement.cue `aca76082fdfcbfb61d2e42371c1c0859e986ecc294d89dfc42178cc6d7befa50`、design.cue `3a60e697ea020e411df3126c9975a08bc075d9c12d20e5f9142d6aeb97ef6886`、plan.cue `4d0db401af4407580aaaf45c1a78c331dea6989a9f957caf92fb1d2a8e9d883a`、explanation.html `99b230ea7085ae1c6c8534ef191a427e4e4987fc5b3ca1242ba8cc7616a044fa`。
- P3（記録のみ）：選んだ線の頭 4.5px と『1.5倍の比』の言い方の小さな食い違い（3.5 × 1.5 = 5.25。4.5 は頭と尾の差を 1.5 倍にした値に近い）。R-02 の受入の『尾のずれ』は CSS ではなく node の出力で比べる。

## 実装の記録

- 開始のコミット：`106f214e8`（iss-00648 #658 のマージの後の origin/main）。D-01 の前提（端の層の `stubs` が空、切り替えの絵は本体だけ）を読み直し、設計どおりと確かめた。
- impl-sol（Codex GPT-6.1 Sol / medium、dispatch `ctx_a56c97c57020`、launch.effective codex gpt-6.1-sol / medium）：最初のコマンドの前に chat-scratch の symlink の拒否（`symlinked writable roots are not supported`）で止まり、何も変えなかった。計画の rationale と統括の了承どおり worker-stop した。
- impl-claude（dispatch `ctx_ed8bf297caa1`、launch.effective claude-opus-5-5 / medium）が S-01〜S-03 を行った。
  - S-01 `9eef2b099`：`MOTION`・`dotsHtml`・`bodyHtml` と T-01。Red 6 failed → Green 17 passed。
  - S-02 `136c054b7`：`graph.css` と T-02・T-03（MOTION と CSS の写しの数の一致の検査を足した）。Red 3 failed → 節目 392 passed。
  - S-03 `1e8905882`：lint のための直し（テストの float の比較と整形）。全体の `uv run pytest` は `136c054b7` で 4258 passed・7 skipped。
- `static-inventory.json`：dashboard の資産は載っていない（変更なし）。
- PR の前に origin/main（iss-00650 #659 まで）を取り込んだ：`1f723bfcb`（競合なし）。

## 実機の確かめ（S-04、2026-11-18）

- 試しのサーバー：前は `106f214e8` を `git archive` して隔離した venv に入れ、ポート 18667（127.0.0.1 だけ）。後はこの worktree を隔離した venv に editable で入れ、ポート 18657（`--tailscale`）。どちらも同じ状態の置き場の写しと、常駐の orca-web を GET で読むだけの中継（18857）を使う。headless Chrome は `--disable-features=MacAppCodeSignClone`。常駐の 47800・8791 の設定、道具の環境には触れていない。
- 測りのときの指揮の組：流れる線 6〜7本、波紋 3〜4つ。切り替えの絵は前 24〜28枚、後 72〜84枚。
- TaskDuration（統括の台本と同じ条件。前と後を交互に3回、秒／10秒）：

| 画面 | 前・動きあり | 後・動きあり | 前・減らす設定 | 後・減らす設定 |
|---|---|---|---|---|
| 横断の構造（`/graph`） | 0.01・0.01・0.01 | 0.02・0.02・0.02 | 0.02・0.02・0.12 | 0.02・0.02・0.02 |
| spec-dock の構造の図 | 0.02・0.01・0.02 | 0.02・0.02・0.02 | 0.01・0.01・0.01 | 0.02・0.01・0.01 |

  受入（横断 0.11秒以下、単体 0.07秒以下）を満たす。横断の初めの見え方では線の一部が画面の外で止まる（`motion.off` 13）。線を図の中央に動かしてから測っても、後は 0.026〜0.028（前 0.017〜0.019）。
- ドラッグ（CDP の Input.dispatchMouseEvent で約4秒）：前も後も長いタスク（50ms 超）0、60 コマ/秒。ただしその間の主スレッドの TaskDuration は、横断の構造で前 0.38・0.39・0.41 から後 0.61・0.62・0.69 秒に増えた（単体の図は 0.22 → 0.25）。合成のレイヤーが流れる線1本につき 5 から 13 に増えた分と読む（受入の外。下の残りに書く）。
- 検査：両方の画面で `specdockEdgeAudit()` の違反0、`specdockCmdAudit()` の `boxOverlaps`・`edgeOverlaps`・`heads` 0、`spotDrift` 0、`spotMissing` 0、`motion.phases` は流れる線 × 12、ブラウザーのエラー0。
- 連続の写し（この worktree の `.workbench/iss-00657/shots/`）：アニメーションを止めて同じ時刻にそろえる方法で、1440×900（deviceScaleFactor 2、ホップの弧は4倍の拡大）。
  - `hop-before-after.png`：上が前、下が後。0.1秒ごとの10枚。前は 8px の同じ点が 0.1秒で半周ずつ入れ替わり、どの点がどこへ行ったか追えない。後は大小の組が子の向きへ 2px ずつ進むのが追える。
  - `before-hop.gif`（0.05秒ごと）・`after-hop.gif`（0.1秒ごと）、`before-one-light-*`・`after-one-{light,dark}-*`（長い線）。
  - `hop-reduce-dark.png`：前の減らす設定（同じ点で向きが分からない）、後の減らす設定（大きな点が子の側で向きが分かる）、後の暗いテーマ。
- 本人が見る試しの URL：tailnet の 18657 の `/graph`（横断の構造）と `/r/github.com/chemitaro/spec-dock/graph`。止め方：この worktree の `.workbench/iss-00657/state/dashboard/server.json` の pid（または `pkill -f "port 18657 --state-root"`）、前のサーバー `pkill -f "port 18667 --state-root"`、中継 `pkill -f "relay_orca.py .* 18857"`。

## Epic の文書（S-05）

epic-00615 の requirement.cue の R-05 の text（点の組・12枚・20px/秒・波紋 3.6秒・減らす設定の組の形）と decisions（iss-00657 の決定の1行。iss-00646 の行は残す）、design.cue の D-04 の動きの行を書き換えた。`spec-dock scope check epic-00615` は誤り0・指摘0。

## 最終品質ゲート（2026-11-18、合格）

- 合格のコミット `1f723bfcb`（origin/main `afe2df5c2` の取り込み。base `106f214e8`）。レビュー（quality-gate-reviewer opus / medium、functional-correctness・requirements-closure・test-adequacy・e2e-user-flow）P0〜P3 すべて0、網羅は完全。`make lint` exit 0、`uv run pytest` 4264 passed・7 skipped。この worktree の `.workbench/final-quality-gate/iss-00657/closure.md`。記録だけのコミットはない（記録は Git の外）。

- **PR**：https://github.com/chemitaro/spec-dock/pull/660（head `1f723bfcb`、`Refs #657`）。CI（Actions と Commit Status）合格、merge_readiness READY（2026-11-18）。マージは統括。

## 逸脱

- S-01 の担当の交代（impl-sol → impl-claude）：上の実装の記録のとおり。統括の了承済みの手順。

## Residual Risks / Follow-ups

- ドラッグ中の主スレッドの時間が、横断の構造で約 1.6倍（0.4 → 0.65秒／4秒）。長いタスクとコマの落ちはない。気になるなら、動かす間（`is-still`）は切り替えの絵を1枚に減らす（ほかの11枚を `display: none`）などで層を減らす案がある（別の Issue）。
- 凡例の指揮の線の見本（`.lg-cmd`、2px の点線）は、組の形にしていない（範囲の外）。
