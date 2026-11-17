---
種別: レポート（Issue）
ID: "iss-00629"
関連GitHub: ["#629"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- 仕様レビュー（spec-reviewer opus / high、S-01 の前）：round-1 は P1 1・P3 2（最初の表示が読み込み中の世界で決まる。直して D-03・R-03・T-03 を改めた）、round-2 で合格（P0〜P3 すべて 0）。結果：`.workbench/spec-review/iss-00629/round-2.json`、`round-2.check.json`、対応の記録 `review-response.md`。
- **合格した文書の sha256**：requirement.cue `ff0f1e4150fc748448eda9cfaf91875f4cfe0876f1a969d9e9ad9286f24fd960`、design.cue `058b8e396fe54094a0928b14376cc63606ca750458dafe61c08a488a75046d42`、plan.cue `d0fd02dc6282893a2760b8dd221020d6c5c4532d45f96f65b3aafeed83d9b4b1`。P2/P3 の残り 0。

## 実装の記録

- 開始のコミット `5c0ebb91652dd2c8f1006fb76e7816b24653ab53`（main、#628 のマージ）。
- 逸脱 codex-symlink-refusal：plan の impl-sol（codex gpt-6.1-sol / medium、dispatch ctx_9f6d526ca862、launch.effective codex / gpt-6.1-sol / medium）は、Orca の chat-scratch の writable root の symlink による UnsupportedOperation で、コマンドを1つも実行できずに止まった（変更なし）。plan の rationale と統括の了承どおり、待たずに worker-stop し、HEAD が開始のコミットのままで未コミットがないことを確かめ、Claude Opus 5.5 / medium（dispatch ctx_b9b776df685d、launch.effective claude / opus / medium）に切り替えた。impl-claude と同じ値なので、S-01〜S-02 を1つのセッションにまとめた。
- S-01 `ddcbd3710`（compose.js：graph の親は `[図, ...子の枠]` を `bodyWidth` で pack。graph でない親は今のまま。T-01・T-02 の node のテスト、`check_no_overlap` の『子は親の図の下』を『図と重ならない』に替え、行の幅の確かめを足した）。
- S-02 `d8d72ac82`（allgraph.js：`initialView` の PC を `s = min(1, (幅 − 16) ÷ 世界の幅)`・`tx = 8`。`A.fitted` をやめ `A.moved` を `zoomAt`・`fit`・`keepAbovePanel`・`centerOn`・ドラッグ・ピンチ・ホイールの移動で立て、動かすまで `draw()` ごとに幅に合わせ直す。偽の DOM の harness に CSS が効いた状態・rAF・構造の答えを遅らせる仕組みを足し、T-03 を4件足した。`fake_dom.mjs` は変えていない）。
- どちらもテストが先に正しい理由で落ちることを確かめてから直した（実装担当の記録 `.workbench/implement/iss-00629/`）。基準：開始のコミットで `make lint` 合格、対象の pytest 27 passed。HEAD `d8d72ac82` で `make lint` 合格、対象 35 passed、全体の `uv run pytest` 4060 passed・7 skipped。開始のコミットでの全体の pytest の基準は、外から止められて取り終えていない（止まるまで失敗0。HEAD で失敗0なので比べは要らない）。
- dashboard の資産は `static-inventory.json` に入っていない（sha256 の更新なし）。

## Outcome

- R-01（枠の中で親の図と子の枠を見える幅で並べる）：node のテストで、親の図の右に入る子は同じ行に、入らない子は次の行に置かれることを確かめた。実データ（この PC の9つの登録の写し）では、どの親の図も、子の枠が右に入るほど狭くない（housing-lifecycle 2024 px、input-devices 2332 px で、使える幅 1344 px を超える）。そのため、9つの枠の位置は開始のコミットと1つも変わらない（1440・1000・390 × 3範囲。下の表）。得は、プロダクトのように狭い図を持つ親が現れたときに出る。
- R-03（最初の表示）：PC の幅では、世界の幅を図の領域に合わせ、左上から縦に読み進める。『これから』の最初の倍率は 1440 で 59%、1000 で 47%（iss-00614 の『収める』は 11%・9%）。
- R-04：線の検査で、単体と比べた新しい違反は0。

## Verification

### 世界の寸法（node、開始と今のコミット、同じ実データの写し）

`measure.log`（[artifacts/20261117t003726z--measure.log](artifacts/20261117t003726z--measure.log)）。開始のコミット（base）と今（src）で、どの組も枠の位置と寸法が1つも変わらない。

| 幅 | 範囲 | 世界（前・後） | 『収める』の見込み |
|---|---|---|---|
| 1440 | これから | 2412×6788 | 約 11% |
| 1440 | いま | 2780×14114 | 約 5% |
| 1440 | 全体 | 13450×34695 | 約 2% |
| 1000 | これから | 2104×8015 | 約 9% |
| 390 | これから | 2104×10341 | 約 6% |

### 実機（headless Chrome、1440・1000・390 × 明・暗 × 3範囲の18組）

- 候補のコミット `d8d72ac82` を `git archive` から wheel にし、隔離した venv、iss-00614 の状態の置き場の写し、試しの `XDG_CONFIG_HOME`（orca_web.port 18829）で `spec-dock dashboard serve --offline --tailscale --port 18629` を立てた。試しの orca は、iss-00614 の `relay_orca.py`（常駐の orca-web を GET で読むだけの中継）を写して tailnet の 18829 で立てた。常駐の 47800・8791、道具の環境、iss-00614 の 18614・18799 には触れていない。数は [result.json](artifacts/20261117t003725z-03--result.json)。
- 最初の表示（読み込みと配置が落ち着いた後の transform。明・暗で同じ）：

| 幅 | 範囲 | 世界の幅 | 最初の倍率 | 世界の右端 / 図の領域の幅 |
|---|---|---|---|---|
| 1440 | これから | 2412 | 59.0% | 1432 / 1440 |
| 1440 | いま | 2770 | 51.4% | 1432 / 1440 |
| 1440 | 全体 | 13698 | 10.4% | 1432 / 1440 |
| 1000 | これから | 2104 | 46.8% | 992 / 1000 |
| 1000 | いま | 2426 | 40.6% | 992 / 1000 |
| 1000 | 全体 | 13364 | 7.4% | 992 / 1000 |
| 390 | これから | 2104 | 74%（スマホ） | 1561 / 390（横の移動で読む） |
| 390 | いま・全体 | 2426・12666 | 74%（スマホ） | 横の移動で読む |

  PC の幅（1440・1000）では、どの範囲でも横にはみ出さない。『全体』は、taikyohiyou_project の折り返せない Initiative の塊（約 13300 px）のために 7〜10% になる。
- 18組すべてで、ブラウザーのエラー0、ページの横のスクロールなし、道具の帯と枠の見出しの重なり0、『収める』の後にすべての枠が図の領域に収まる（『収める』の倍率は iss-00614 と同じ：1440 で 11%・5%・2%）。
- 選び：1440 明『これから』で housing-lifecycle の iss-00018 を押すと横の欄が開き、選ばれた箱はそれだけで、『詳しい画面』でそのリポジトリの詳しい画面へ移った。
- 線の検査（倍率 100%、稼働の印の要約を待ってから）と単体の構造の図の比べ（[own-compare.json](artifacts/20261117t003725z-04--own-compare.json)）。違反が0でない組だけを挙げる（『これから』はすべての幅で0）。明・暗で同じ数：

| リポジトリ | 範囲 | 画面の幅（中の幅） | 横断の構造 | 単体の構造の図 | 新しい違反 |
|---|---|---|---|---|---|
| housing-lifecycle | 全体 | 1440（1344） | boxHits 6 | boxHits 6 | 0 |
| taikyohiyou_project | 全体 | 1440（1312） | overlaps 2 | overlaps 2 | 0 |
| taikyohiyou_project | 全体 | 1000（872） | overlaps 1 | overlaps 1 | 0 |
| taikyohiyou_project | いま | 390（360） | overlaps 8 | overlaps 8 | 0 |
| taikyohiyou_project | 全体 | 390（360） | overlaps 1 | overlaps 1 | 0 |

  既存の違反は iss-00614 と同じ組・同じ数で、iss-00627 で直す。
- 写し：[1440 明 これから 最初の表示](artifacts/20261117t003724z--allgraph-1440-light-next-first.png)、[1440 暗 全体 最初の表示](artifacts/20261117t003724z-01--allgraph-1440-dark-all-first.png)、[1000 明 いま 最初の表示](artifacts/20261117t003725z--allgraph-1000-light-now-first.png)、[390 明 これから 最初の表示](artifacts/20261117t003725z-01--allgraph-390-light-next-first.png)、[1440 明 これから 収める](artifacts/20261117t003725z-02--allgraph-1440-light-next.png)。
- 試しの URL（本人の確かめ用、確かめまで残す）：tailnet の 18629 番の `/graph`（URL は統括への報告で伝える）。試しの orca は 18829。止め方：`kill $(lsof -tnP -iTCP:18629 -sTCP:LISTEN) $(lsof -tnP -iTCP:18829 -sTCP:LISTEN)`（またはタスク担当・統括に頼む）。

## Residual Risks / Follow-ups

- 実データでは、枠の並びの得はまだ出ない（どの親の図も、子の枠が右に入るほど狭くない）。全体を1画面に収めた倍率を大きくするには、見える幅を超えて並べる必要がある。統括は本人の決まり（iss-00583）を理由に採らなかった。本人が望めば、横に読む並び（タスク担当の試算で、枠の並びだけなら 21.6%）を別に検討する。
- 『全体』の最初の倍率は、PC でも 7〜10% になる。原因は、taikyohiyou_project の1つの Initiative の塊の幅（約 13300 px）で、この画面ではなく構造の図の配置の側にある。
- スマホは今どおり 74%・左寄せで、横の移動で読む（統括への確認 msg_09212d9431f7）。
- 既存の線の違反（上の表）は iss-00627 で直す。
