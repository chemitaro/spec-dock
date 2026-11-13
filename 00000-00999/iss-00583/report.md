---
種別: レポート（Issue）
ID: "iss-00583"
関連GitHub: ["#583"]
最終更新: "2026-11-13"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## レビュー記録

- round-1（spec-reviewer opus / high）：合格（P0・P1 なし、P2 1・P3 3）。`.workbench/spec-review/iss-00583/round-1.json`。P2・P3 を任意で反映（`review-response.md`）。
- round-2（同じレビュアー）：**合格**。P0・P1・P2 なし、P3 1（graph.js のコメントを直す決定と、excludes・rollback の記述の食い違い。文書は合格の後に変えないため、記録だけ）。結果 `.workbench/spec-review/iss-00583/round-2.json`、検査 `round-2.check.json`（valid、status pass）。
- 合格した文書の sha256：requirement.cue `780d1e9f749e61cc8edf673dd812b052b4c846317ab36821c7fa3ba36bb84565`、design.cue `3afa08458126b757338ffc125f1d7599430bb22291537857e8c78c5a4fb3e96f`、plan.cue `5c37fddd54524b402fe15b5cb49d7a39453515ccc25145953dff52a20845892b`。
- 注：round-2 の P3 のとおり、graph.js はコメントだけを直し、コードは変えない（requirement の constraints と D-05 が正）。

## 原因

タスク担当が、作業を始めたコミット `982932e47` の `views/graph/layout.js` を読み、実データ（この PC の構造のスナップショット）を node で並べて確かめた。

- 空白（要望 1）：`childrenBlock` は、依存でつながったまとまり（塊）と、つながりのない1つの Scope を区別せず、活動順に一列に並べ、`shelfBlock` で幅を超えるところで折り返すだけ。棚の高さは棚の中で一番高いものに合わせる。housing-lifecycle の epic-00313 では、つながりのない 332、331、330… が1行目に並び、その右の 6 つから 1 つへ集まる背の高い塊に合わせて1行目が伸び、左下が空く（本人の写し `epic-00573/.workbench/iss-00583-before.png`）。
- はみ出し（要望 2）：依存のせいではない。最上位だけ `widestRoom`（iss-00575 R-01）が「全体を画面に収めたときの倍率が最大になる切れ目」を選び、候補は 100% で見える幅を超えてよい。node で housing-lifecycle を並べた結果：

| 見える幅 × 高さ | 高さあり（widestRoom）の全体 | 高さなし（見える幅で折り返し）の全体 | 最上位の行 |
|---|---|---|---|
| 1424 × 792 | 4980 × 2445 | 2682 × 4958 | [4, 5] |
| 984 × 692 | 4076 × 2981 | 2298 × 6084 | [4, 5] |
| 374 × 736 | 2106 × 12974 | 2106 × 12974 | 1つずつ |

  spec-dock でも 984 × 692 で 2102 × 1341（高さなしは 1156 × 1931、行 [2, 1]）。高さなしでも見える幅を超える分は、1つの Initiative の中の折り返せない鎖の幅による（塊は分けない）。

## 直す前の写し

作業を始めたコミット `982932e47` のコードで、`.workbench/iss-00583/state`（この PC の状態の置き場の写し）を `uv run spec-dock dashboard serve --port 18583 --offline --state-root …` で配り、headless Chrome で写した（S-05 で、後の写しと並べて Artifact に取り込む）。

| リポジトリ | 幅 | 見える幅 | 全体の幅 × 高さ |
|---|---|---|---|
| spec-dock | 1440 | 1424 | 1406 × 1497 |
| spec-dock | 1000 | 984 | 2102 × 1362 |
| spec-dock | 390 | 374 | 1156 × 4715 |
| housing-lifecycle | 1440 | 1424 | 5724 × 2591 |
| housing-lifecycle | 1000 | 984 | 4636 × 3031 |
| housing-lifecycle | 390 | 374 | 2434 × 13029 |

ブラウザーのエラーは、どれも0。

## 逸脱と判断

- iss-00575 R-01（最上位は倍率が最大の切れ目）を改め、最上位もほかの段と同じく見える幅で折り返す（R-02、D-05）。理由：本人の要望（2026-11-13）は、100% で画面の幅に収まる折り返し。候補を見える幅以下に限る案も考えたが、横長の画面ではほとんどの場合に最も広い候補（見える幅での折り返し）が選ばれ、違いが残らないので、規則を1つにした。iss-00575 R-03（大きさが変わり終わってからの並べ直し）は graph.js の側でそのまま残る。
- iss-00575 R-02、iss-00556 D-03、iss-00560 の「活動順を変えない」を改める（R-01、D-01、D-03）。理由：本人の要望（塊を左に、ばらばらを右の空きへ）。塊どうし、1つどうしの活動順は保つ（F-03）。塊のない段は今までと同じ（F-02）。

## Outcome

## Verification

## Residual Risks / Follow-ups

## 実装の記録

### 開始時

- ブランチ `chemitaro/iss-00583`、開始 `982932e47ca2c8c2befe24c1b3623e10931d2a94`、変更なし。requirement / design / plan の SHA-256 は round-2 の合格記録と一致。
- ベースライン：`make lint` exit 0（ruff / format / mypy 合格）、`uv run pytest` exit 0（3759 passed / 7 skipped、1855.02秒）。既存の失敗なし。詳細 `.workbench/implement/iss-00583/start.md` と同じ場所の `baseline-lint.log`・`baseline-pytest.log`。
- pstack の bug-fix、原因の修正、証明、振る舞いのテスト、段階的なコミットの参照を確認。実装担当は委譲しない。

### S-01（Red）

- 合成の Epic（単独5つ、鎖2つ、6つから1つへの塊、4列2行の塊）、低い塊の下を埋める Epic、背の高い単独枠を含む Initiative をテストに追加。開始コミットの合成 Epic の高さは、幅1000 / 1440 / 1920で 1175 / 971 / 769px（高さ900）。幅1440の 971px を比較基準としてテストに固定。
- `uv run pytest tests/unit/presentation/test_dashboard_graph_js.py -k 'single_issues or packed_siblings or widening_keeps_packed or a_tall_single or packed_structures'`：6 failed / 4 passed / 28 deselected（1.40秒）。971pxから縮まない、右の列や塊の下に入らない、背の高い枠が塊と同じ棚に来る、という意図した失敗。ログ `s-01-red.log`。
- node の確認に routeLayout が採用した配置と path の取得を加え、gaps なし / 採用した配置の重なりと、広げ直しの前後の置き場を観測。audit の幅1000・1440・1920（高さあり）を追加し、250件の測定対象数を 16 + 4×8 から 16 + 7×8 へ更新（検査条件の追加であり、制限の緩和なし）。
- `make lint`：exit 0。`spec-dock scope check iss-00583`：valid、errors=0、warnings=0（status のみ更新）。コミットは後記。

- S-01 コミット：`ae70717625c87e76f633d59146c1eae390d715ea`（テストのみ。Red の証拠を先に保存）。

### S-01 補正（活動順の前提）

- 初回のテストデータでは、推薦順位（先で待つ件数）により4列の塊が先になり、幅1440の最初の棚が低い棚になっていた。初回 Green は 4 failed / 6 passed。規則に反する結果ではなく、狙った棚を作れていないテストの誤りだった。
- 背の高い塊と2つの短い鎖の入口を作業中として活動順を明示。単独5つのうち作業中が1つという条件、依存の構造、幅、受け入れの強さは保持。広げ直しのテストでも、先の棚に詰めて後の棚と重ならない前提を作るため、入口の活動状態を明示した。
- 開始コミットの layout.js / router.js / series.js を Git から読み出した `.workbench/implement/iss-00583/baseline-assets` に対して、補正後の同じ API 文書を測定。幅1000 / 1440 / 1920の高さは 1175 / 1073 / 869px（高さ900）。比較の期待値を971から1073へ変更したのは、活動状態を明示したデータに対応させるため。開始コミットのコードは変えていない。出力 `corrected-before.json`。
- 補正後の Red は同じ assets を選ぶ一時 pytest plugin `baseline_assets.py` で確認（元の pytest コマンドに `-p baseline_assets` と PYTHONPATH を付加）。ログ `s-01-corrected-red.log`。コミットは後記。
