---
種別: レポート（Issue）
ID: "iss-00655"
関連GitHub: ["#655"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

## Verification

## レビュー記録

- 仕様のレビュー（spec-reviewer opus / high、standard、2人目なし）：round-1 不合格（P1 1、P2 2、P3 1。main#view のフォーカス、Firefox の横のホイール、画面が隠れているときのテスト、T-03 の符号）→ 全部直した（この worktree の `.workbench/spec-review/iss-00655/review-response.md`）→ round-2 **合格**（P0〜P3 すべて0）。結果は `.workbench/spec-review/iss-00655/round-2.json` と `.check.json`（reviewed_sha `92e26aff7`）。
- **合格した文書の sha256**（round-2）：requirement.cue `58e360d8446f9de5ef53d3493611e2e6522b779b0c98e71366d39477d93e0a1a`、design.cue `a25ff30b4df79205fa712a02ab7e1ccbc2ee809490a571a4f3114e2687b932d6`、plan.cue `a70cd6027249a905b298766576680b2e4a1d44c0491b6cc9b5ac6e94d02a2f6e`、explanation.html `58c1d8099ffb0f8133ee54654a34b994aec3a1bbbb7adf17e82405e0681f4b44`。Epic epic-00654 の requirement.cue `fed47250…f278`、design.cue `539998af…7340`、plan.cue `7262bbbd…60a5`。
- 仕様の変更（2026-11-18）：実機の CDP の値の食い違いへの統括の決定（msg_e0c1b3a11a47、A ＋一続きの判定の引き継ぎ）で、D-02・R-02・F-01・T-01・D-06・explanation.html を直した。round-3 合格（P2 2）→ P2 を直して round-4 **合格**（P0〜P3 すべて0、reviewed_sha `25d5e48d2`。結果は `.workbench/spec-review/iss-00655/round-4.json` と `.check.json`）。セッションの値と手順の割り当ては変えていない。
- **今の合格の sha256**（round-4）：requirement.cue `4aefb2376a2f41326f2486d8b8d23a7f285faac3aa527cb7f2928cd337777732`、design.cue `87ce59e8a4973d7e9690ace66dc92b280d5df9de2ade646701a4dfedf7e95844`、plan.cue `4dbcadfe45ba0a2bed302a8aaaf0327ccd0e0cdbb84d5564a306ca40a8762f64`、explanation.html `51789b8a344fd342f5eb3242e1eab4ab7e227c39419a558e38896fdc9d1a3f62`。Epic の文書は round-2 と同じ。
- 開始のコミット：`92e26aff7256a9a32ba6edd5bc7f790ed8e4f149`。

## 実装の記録

- impl-sol（Codex、dispatch `ctx_28d4b720342b`、launch.effective codex gpt-6.1-sol / medium）：chat-scratch の symlink の拒否（`symlinked writable roots are not supported`）で、何も変えずに止まった。worker-stop した。
- impl-claude（dispatch `ctx_dd801e932b08`、launch.effective claude / claude-opus-5-5 / medium）が S-01〜S-03 を行った。開始のコミット `92e26aff7`（基準：画面のテスト2ファイル 49 passed）。
  - S-01 `cee2f3cdd`：`views/graph/view_input.js`（新、D-01〜D-03）と T-01・T-02（`tests/js/dashboard_view_input.mjs`・`tests/unit/presentation/test_dashboard_view_input.py`）。Red（モジュールなし、10 error）→ Green 10 passed。
  - S-02 `25d5e48d2`：D-04（`bindViewInput`、graph.js・allgraph.js のつなぎ、今の wheel の処理を消した）、D-05（aria-label）、T-03。Red（graph 5・allgraph 2 fail）→ Green。今のテストの期待は変えず、画面の台本に wheel の値・キーの shift・`on: main/input`・viewHidden・keyPrevented・label を足した。
  - 仕様の変更の直し `4f29a42c9`：一続きの wheel の判定を両向きに引き継ぐ（D-02 の改訂）。Red（stroke 1 fail）→ Green。画面の台本の `advance` が `performance.now` も進めるようにした（しないと、間をあけた wheel が本物の時計で一続きと判定される）。
  - S-03：`make lint` 合格、全体 `uv run pytest` 4253 passed・7 skipped（`4f29a42c9`）。ログは `.workbench/implement/iss-00655/`。`static-inventory.json` に dashboard の資産は載っていない（変更なし）。
- origin/main の取り込み：`c607dc2ec`（#658 iss-00648 ほか、競合なし）、`b50c11ddb`（#659 iss-00650、画面のテスト3ファイルの競合を両方残して解いた）。

## 逸脱と判断

- S-01 の担当の交代（`deviation: codex-confirmation-takeover` 相当、chat-scratch の symlink の拒否）：計画の rationale と統括の了承のとおり impl-claude が S-01 から引き継いだ。
- 実装担当のコミットは git-commit skill を通さず直接作った（実装担当の報告）。メッセージの形（Conventional Commits の日本語、箇条書き）は守っている。
- 仕様の変更（2026-11-18、統括の決定 msg_e0c1b3a11a47）：実機の CDP の値の性質を受け、一続きの判定の引き継ぎを両向きにした（レビュー記録を参照）。
- 実機の確かめは headless の Chrome で行った（D-06 の改訂で headless でよいとした）。

## 実機の確かめ（S-04、2026-11-18、`4f29a42c9`）

- 試しのサーバー：この worktree を隔離した venv（`.workbench/iss-00655/venv`、editable）に入れ、iss-00646 の試しの状態の置き場の写し（`.workbench/iss-00655/state`）で、ポート 18655、`--tailscale`。orca-web は常駐の 8791 を GET で読むだけの中継（`relay_orca.py`、18855、127.0.0.1 と tailnet）。Chrome 157 を headless で `--disable-features=MacAppCodeSignClone`、CDP 9655、1440×900。常駐の 47800・8791 の設定、道具の環境には触れていない。
- 台本：`.workbench/iss-00655/check.mjs`（結果 `one.json`・`all.json`）、`still.mjs`。写しは `.workbench/iss-00655/shots/`（`{one,all}-{0-start,1-after-wheel,2-after-arrows,3-after-fit}.png`）。

| 操作（CDP） | spec-dock の構造の図 | 横断の構造 |
|---|---|---|
| mouseWheel deltaY −120（カーソル 720,500） | 88% → 101%（×1.15）、カーソルの下の点のずれ 0px | 59% → 68%（×1.15）、ずれ 0.002px |
| もう一度 −120 / +120 | ×1.15 / ×0.8696（1/1.15）、ずれ 0 | 同じ、ずれ ≤0.001px |
| 速く回す（−120 を 40ms ごとに3つ） | ×1.5209（1.15³） | ×1.5209 |
| 2本指を模した wheel（deltaX 3、deltaY 7、前から 400ms あけて） | 拡大率そのまま、(−3, −7) 動く | 同じ |
| 一続き（deltaX 2・deltaY 10 を 40ms ごとに4つ、続けて deltaX 0・deltaY 40） | 拡大率そのまま、(−8, −80) 動く（最後の 40 も動かすを引き継ぐ） | 同じ |
| Shift＋deltaY 120 | 横に −120、縦 0 | 同じ |
| Ctrl＋deltaY −10（ピンチ） | ×1.1052（exp(0.1)、今と同じ） | 同じ |
| → ↓ ← ↑（フォーカスは body） | tx −80、ty −80、tx +80、ty +80 | 同じ |
| Shift＋→ | tx −320 | 同じ |
| `+` / `-` | ×1.25 / ×0.8（中央） | 同じ |
| `0` | 収める（101%系 → 32%） | 収める（→ 12%） |
| 検索の input にフォーカスして → | 動かない | （検索の欄なし） |

- 届いた wheel の値（CDP の性質）：CDP の Input.dispatchMouseEvent（mouseWheel）は、どんな deltaY（7、10、12.5、40、±120）でも `deltaMode` 0、`wheelDeltaY` ±120 を渡す。そのため deltaX 0・deltaY 12.5 の合成の wheel（前の wheel から 400ms あけた一続きの初め）は、らしいマウスのホイールとして ×0.8696 に縮小した。統括の決定（A、2026-11-18）のとおり、本物のマウスとトラックパッドは本人が試しの URL で確かめる（統括が頼む）。
- 動かす間の止める扱い（iss-00646）：両方の画面で、ホイールの 50ms 後と → の直後に `.gx-view` に `is-still` があり、600ms 後には外れている。
- 検査：両方の画面で `specdockEdgeAudit()` の違反0（単体は boxHits・overlaps など違反の数がすべて0、横断は total 0）、`specdockCmdAudit()` の `boxOverlaps`・`edgeOverlaps`・`heads`・`spotDrift` 0、ブラウザーのエラー0。`.gx-view` の aria-label は D-05 の文。
- 本人が見る試しの URL：tailnet の 18655 の `/graph`（横断の構造）と `/r/github.com/chemitaro/spec-dock/graph`。止め方：`pkill -f "port 18655 --state-root"` と `pkill -f "relay_orca.py .* 18855"`（Chrome は CDP の Browser.close で閉じた）。

- 最終のコミット `b50c11ddb` でも同じ台本で、両方の画面の数（×1.15、ずれ ≤0.002px、(−3,−7)、一続き (−8,−80)、×1.5209、Shift −120、ピンチ ×1.1052、矢印 ±80・320、+ ×1.25、- ×0.8、0 で収める）、線の検査の違反0、cmdAudit 0、エラー0 を確かめた（`.workbench/iss-00655/final/`）。

## 最終品質ゲート（2026-11-18、合格）

- **合格のコミット** `b50c11ddbf44dbbe9c400889385450764c272946`（base `92e26aff7`）。レビュー（quality-gate-reviewer opus / medium、4観点）P0〜P3 すべて0、網羅は完全。`make lint` exit 0、`uv run pytest` 4281 passed・7 skipped。この worktree の `.workbench/final-quality-gate/iss-00655/closure.md`。attempt 01（`c607dc2ec`）も合格したが、origin/main が進んだので取り込み直してやり直した。記録だけのコミットはない（記録は Git の外）。

- **PR**：https://github.com/chemitaro/spec-dock/pull/661（head `b50c11ddb`、`Refs #655`）。CI（Commit identity の check、SpecDock check、Provider CI の route・provider-tests・Provider distribution parity の ubuntu と macos）すべて合格、merge_readiness READY、mergeable（2026-11-18）。マージは統括。

## Residual Risks / Follow-ups

- 本物のマウス・トラックパッドの値は手元で測れていない（CDP の合成の値は `wheelDeltaY` ±120 に固定）。マウスのホイールが 120 の倍数にならない環境では動かすに倒れ（今と同じ動き）、トラックパッドの一続きの初めの1つがちょうど deltaY 40（`wheelDeltaY` 120）で deltaX 0 だと、その一続きが拡大・縮小になる。本人の確かめで食い違えば、見分けの決まりを直す別の Issue にする。
