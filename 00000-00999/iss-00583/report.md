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
- CP-1（code-reviewer opus / medium、範囲 `982932e47..6d7b2758f`、S-01・S-02）：**合格**。P0〜P3 すべて0。結果 `.workbench/code-review/iss-00583/cp1-round-1.json`、検査 `cp1-round-1.check.json`（valid、status pass）。タスク担当が実データ（housing-lifecycle）を node で並べ、epic-00313 の枠の高さが 971→869px（幅1424）、1073→971px（幅984）に下がることを確かめた。

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

## 実データの写し（S-05、タスク担当）

作業ツリーのコード（直す前は `982932e47`、直した後は `96e10c32f`）を `uv run spec-dock dashboard serve --port 18583 --offline --state-root <.workbench/iss-00583/state>` で配り、headless Chrome（`--disable-features=MacAppCodeSignClone`、`Browser.close` で閉じた）で写した。数字は [直す前](artifacts/20261113t154034z-01--before-result.json)、[直した後](artifacts/20261113t154034z-02--after-result.json)、[epic-00313 に絞った後](artifacts/20261113t154034z-03--after-focus313-result.json)。

| リポジトリ | 幅 | 見える幅 | 全体の幅（前 → 後） | 最上位の行（Initiative の数：行の幅） | 写し（前 / 後） |
|---|---|---|---|---|---|
| housing-lifecycle | 1440 | 1424 | 5724 → 2700 | 前 [4:5676, 5:4204] → 後 [1, 1, 1, 1, 1, 4:986] | [前](artifacts/20261113t154030z--before-housing-lifecycle-1440.png) / [後](artifacts/20261113t154032z-02--after-housing-lifecycle-1440.png) |
| housing-lifecycle | 1000 | 984 | 4636 → 2306 | 前 [4:4588, 5:3738] → 後 [1, 1, 1, 1, 1, 3:736, 1] | [前](artifacts/20261113t154030z-02--before-housing-lifecycle-1000.png) / [後](artifacts/20261113t154033z--after-housing-lifecycle-1000.png) |
| housing-lifecycle | 390 | 374 | 2434 → 2114 | 縦積み（9行）のまま | [前](artifacts/20261113t154031z-01--before-housing-lifecycle-390.png) / [後](artifacts/20261113t154033z-01--after-housing-lifecycle-390.png) |
| spec-dock | 1440 | 1424 | 1406 → 1406 | 1つずつ3行のまま | [前](artifacts/20261113t154030z-01--before-spec-dock-1440.png) / [後](artifacts/20261113t154031z-03--after-spec-dock-1440.png) |
| spec-dock | 1000 | 984 | 2102 → 1156 | 前 [2:2102, 1] → 後 1つずつ3行 | [前](artifacts/20261113t154031z--before-spec-dock-1000.png) / [後](artifacts/20261113t154032z--after-spec-dock-1000.png) |
| spec-dock | 390 | 374 | 1156 → 1156 | 縦積みのまま | [前](artifacts/20261113t154031z-02--before-spec-dock-390.png) / [後](artifacts/20261113t154032z-01--after-spec-dock-390.png) |

- 要望 2（R-02）：2つ以上の Initiative が並ぶ行は、どれも見える幅に収まる（1424 に 986、984 に 736）。見える幅を超える残りは、1つで見える幅より広い Initiative（中の塊を折り返せない。最大 2652）の行だけ。
- 要望 1（R-01）：epic-00313 に絞った写し（[1440](artifacts/20261113t154033z-02--after-focus313-housing-lifecycle-1440.png)、[1000](artifacts/20261113t154034z--after-focus313-housing-lifecycle-1000.png)）で、つながりのない 332、331、330、329、328 が、背の高い塊（325〜326）の右の列に縦に積まれ、本人の写しの左下の大きな空白がなくなった。node で測った epic-00313 の枠の高さは、幅1424で 971 → 869px、幅984で 1073 → 971px。
- edgeAudit の違反（AUDIT_KEYS）は、前も後も、どの写しでも0。ブラウザーのエラーは0。
- 本人の写しは housing-lifecycle（init-00001）のもの。company-os のスナップショットには Scope がなかった。

## 逸脱と判断

- iss-00575 R-01（最上位は倍率が最大の切れ目）を改め、最上位もほかの段と同じく見える幅で折り返す（R-02、D-05）。理由：本人の要望（2026-11-13）は、100% で画面の幅に収まる折り返し。候補を見える幅以下に限る案も考えたが、横長の画面ではほとんどの場合に最も広い候補（見える幅での折り返し）が選ばれ、違いが残らないので、規則を1つにした。iss-00575 R-03（大きさが変わり終わってからの並べ直し）は graph.js の側でそのまま残る。
- iss-00575 R-02、iss-00556 D-03、iss-00560 の「活動順を変えない」を改める（R-01、D-01、D-03）。理由：本人の要望（塊を左に、ばらばらを右の空きへ）。塊どうし、1つどうしの活動順は保つ（F-03）。塊のない段は今までと同じ（F-02）。

- S-01 のテストデータを補正：推薦順位は番号だけではなく先で待つ件数を優先するため、当初の合成構造では4列の塊が先に来た。背の高い棚の空きを検証するため、背の高い塊と2つの鎖の入口の活動状態を明示し、開始コミットの資産で高さを測り直した（幅1440：971px → 補正後1073px）。これは合成データと比較基準の対応の補正であり、活動順の規則や受け入れ条件は変更していない。実装後は869px。

- S-03：`test_initiatives_wrap_where_the_whole_shows_largest` を `test_initiatives_wrap_at_the_width_seen` に改め、2×2という倍率由来の期待を、1400 / 1920 の各行が見える幅以内であるという R-02 の期待へ変更。`test_without_a_height_the_top_level_wraps_at_the_width_seen` は `test_height_does_not_change_top_level_rows` に改め、同じ幅で高さあり / なしの全座標が一致することと、幅省略時も高さが影響しないことを追加。広げ直しの固定テストの幅1400での行数を2から4へ変更（自然な枠幅のままでは1行1つしか入らないため）。鎖は1行を保つ期待を維持し、単独 Initiative が次の棚の左端、28px下に来ることを明示した。いずれも承認済みの iss-00575 の判断の変更（R-02 / D-05 / D-06）による。

- S-04：`test_frames_follow_activity_and_boxes_put_done_below` の最上位だけを `[init-00001, epic-00020, epic-00030, init-00060]` から `[epic-00030, init-00060, epic-00020, init-00001]` に更新。依存の塊30→60が先、単独20はその右の空き、背の高い単独1は下の棚に入る（D-01 / D-03）。同じ置き場の中の活動順、内側の Epic、Issue の完了順、木の順序の期待は維持。コメントにも理由を追記。

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

- S-01 補正コミット：`fdebf71ad3f767841df00cf7ac483640b336e774`（parent は `ae70717625c87e76f633d59146c1eae390d715ea`）。補正後 Red は 6 failed / 4 passed / 28 deselected（1.38秒）。

### S-02（Green、CP-1）

- childrenBlock が、従来の components の番号と gridBlock のキーを維持して塊と単独を分離。全体が畳まれるものは従来どおり最後のチップに集約。packPlaces が塊の棚と、既存の右の列 → 新しい右の列 → 左から塊の下の行 → 残りの棚を選ぶ。塊だけの高さを選択の上限に使用。
- ctx.wraps には棚・塊の置き場・右の列・下の行・残りの棚の要素番号を保存。gaps のある回は ctx.breaks の番号を再使用。描くときは lineBlock が子の最大から棚の高さを測り、広げた単独の下端が次の棚を押し下げる。
- wr / wc と元の grid のキーを保持し、新たな下の行は `cp<段>~<棚>~<置き場>~<行>`（x）、塊の置き場は `pr<段>~<棚>~<置き場>`（y）、右の列は `pv<段>~<棚>~<列>`（y）。既存の axisOf に適合し、間は gap を使用。下の行は従来の棚と同じく末尾へ順に追加し、埋まった行を閉じて次の行へ進む、と解釈した。
- 新規10件：`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py -k 'single_issues or packed_siblings or widening_keeps_packed or a_tall_single or packed_structures'` が 10 passed / 28 deselected（1.55秒）。ログ `s-02-focused-corrected.log`。高さは幅1000 / 1440 / 1920で 971 / 869 / 869px（開始コミットの補正後データは1175 / 1073 / 869px）。出力 `after-pack.json`。
- 節目の `uv run pytest tests/unit/presentation/test_dashboard_graph_js.py`：37 passed / 1 failed（39.82秒）。唯一の失敗は、S-04で更新する既存 `test_frames_follow_activity_and_boxes_put_done_below` の最上位の読み順（従来は単独の init-00001 が先、今は epic-00030 → init-00060 の依存の塊が先）。この CP-1 では期待をまだ変えず、S-04に残した。ログ `s-02-graph.log`。新規合成構造・代表構造の edgeAudit、250件の1秒制限、塊のない段、木の表示、その他の既存テストは合格。
- `make lint`：exit 0（ruff / format / mypy、`s-02-lint.log`）。`git diff --check`：合格。利用箇所を検索し、旧 shelfBlock の利用は childrenBlock だけ、wraps の利用は layout 内の再配置とテストの観測だけと確認。router.js の規則は変更なし。
- CP-1 の前なので widestRoom / shelved と高さの従来動作は保持（S-03 の担当分）。S-03 / S-04 / S-05 は未着手。コミットと Scope check の結果は後記。

- S-02 コミット / CP-1 HEAD：`6d7b2758f335eb00b88b1a5322d97668edad3e55`（parent `fdebf71ad3f767841df00cf7ac483640b336e774`）。`spec-dock scope check iss-00583`：valid、errors=0、warnings=0。コミット後のブランチは指定どおり、Git の作業ツリーはクリーン。
- CP-1 のレビュー範囲は `982932e47ca2c8c2befe24c1b3623e10931d2a94..6d7b2758f335eb00b88b1a5322d97668edad3e55`。S-01 / S-02 完了、タスク担当のレビューと返答待ち。

- CP-1：担当者から合格の連絡（`msg_2a8eb007a37c`、code-reviewer opus / medium、P0〜P3すべて0、`.workbench/code-review/iss-00583/cp1-round-1.json`）。テストデータ補正も了承済み。S-03 / S-04 の継続承認。push は担当者が行う。

### S-03（最上位も見える幅で折り返し）

- childrenBlock が最上位でも avail を packBlock にそのまま渡し、widestRoom / shelved を削除。options.height は渡してよいが配置には使わない。JSDoc、graph.js の seenHeight の2行のコメント、node 確認の同趣旨のコメントを更新。graph.js はコメント行を除いた比較でコードが一致することを確認した。
- 幅と高さのテスト：`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py -k 'initiatives_wrap_at or height_does_not or a_chain_of_initiatives or rows_stay_when'` は Red 3 failed / 1 passed（0.29秒、`s-03-red.log`）→ Green 4 passed（0.22秒、`s-03-green.log`）。変更前は幅1400の行が1634pxで1352pxの範囲を超えていた。
- 節目 `uv run pytest tests/unit/presentation/test_dashboard_graph_js.py`：37 passed / 1 failed（36.98秒、`s-03-graph.log`）。残る1件は CP-1 でも記録した旧読み順の期待で、S-04で更新する。
- `make lint`：exit 0（`s-03-lint.log`）。`git diff --check` 合格。src の views と tests を検索し、widestRoom / shelved / opts.height / 倍率で最上位を選ぶ古い説明が残っていないことを確認。

- S-03 コミット：`125df986a2a51aa7779d28e5676a1461ad7935f2`（parent `6d7b2758f335eb00b88b1a5322d97668edad3e55`）。Scope check valid、errors=0、warnings=0、Gitクリーン。ただし git-autocommit が今回だけ英語の文を生成したため、日本語の指定に合わない。共有認可契約 A2 では履歴の書き換えは通常認可の外なので、修正方法を担当者に確認する。日本語訳案 `.workbench/implement/iss-00583/s-03-message-ja.txt`。自分から push は実施していない。

- 担当者の明示許可 `msg_1b53921b2472` に従い、未公開の S-03 のメッセージだけを amend。現在の S-03 コミットは `d011cef068703c788b387922b3fd004d9894c115`（parent は変わらず `6d7b2758f335eb00b88b1a5322d97668edad3e55`）。旧 `125df986a` と Git の tree が一致し、差分を変えていないことを確認。既存の Co-Authored-By 等の行はなかった。push なし。

### S-04（残る読み順の期待値と全体の検証）

- 変更は前から記録していた1つの旧読み順の期待と、その理由のコメントだけ。API 文書を node で配置した `activity-after.json` を使い、塊30→60、空きの単独20、下の単独1という受け入れの規則との対応を確認。内側の Epic / Issue の読み順と木の順は変更していない。
- S-03 の実行に残った1 failed（Red）から、`uv run pytest tests/unit/presentation/test_dashboard_graph_js.py -k frames_follow_activity_and_boxes_put_done_below` が 1 passed / 37 deselected（0.29秒）へ。
- `make lint`：exit 0（ruff / format / mypy 合格、`s-04-lint.log`）。`spec-dock scope check iss-00583`：valid、errors=0、warnings=0。全体 `uv run pytest`：exit 0、3769 passed / 7 skipped（1824.13秒、`s-04-pytest.log`）。構造グラフ38件もすべて合格。開始コミットは3759 passed / 7 skippedで、追加10件を含めて失敗なし。
- `.workbench/implement/iss-00583` の適用済み草稿4つと診断用の中間出力だけを整理。基準のJS資産、比較入力・出力、再現用 plugin、測定スクリプト、ベースラインと各ステップのログは検証証拠として保持。

- 最終検証：`make lint` と `uv run pytest`（全体）が両方合格。既存の失敗は開始時から0件。ソース・テストを固定して最後の1回を完了まで待ち、静かな出力を理由に再実行していない。S-01〜S-04 の status を done にした。最終コミットと Scope check の結果は後記。

- S-04 コミット / 実装完了 HEAD：`96e10c32f7754299336a376df5add564b98163e3`（parent `d011cef068703c788b387922b3fd004d9894c115`）。ブランチ `chemitaro/iss-00583`、Git の作業ツリーはクリーン、author / committer の設定は `chemitaro <84865385+chemitaro@users.noreply.github.com>`。
- 最後のメッセージは git-autocommit が生成した日本語文を使用。生成器の prompt が scope の省略を許しており、2つの候補に scope がなかったので、確認で確定しなかった。今回の明示指定 `type(scope):` を優先し、生成された本文を維持して既知の `dashboard-graph` だけを付け、通常の `git commit -F` で確定。ツールの設定・実装と Git の履歴は変更していない。
- 最終 Scope check：valid、errors=0、warnings=0。`make lint` と全体 `uv run pytest` は合格、既存の失敗なし。担当した S-01〜S-04 を完了し、S-05、コードレビュー、最終品質ゲート、PR はタスク担当へ引き渡す。実装担当から push、merge、work finish は行っていない。

| ステップ | コミット |
|---|---|
| S-01（Red） | `ae70717625c87e76f633d59146c1eae390d715ea` |
| S-01 の活動順のデータ補正（開始コミットで Red 再確認） | `fdebf71ad3f767841df00cf7ac483640b336e774` |
| S-02（CP-1 合格） | `6d7b2758f335eb00b88b1a5322d97668edad3e55` |
| S-03 | `d011cef068703c788b387922b3fd004d9894c115` |
| S-04 | `96e10c32f7754299336a376df5add564b98163e3` |
