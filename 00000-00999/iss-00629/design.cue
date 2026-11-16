package spec

// 設計（Issue）。型 specdock/v1。

goals: [
	"リポジトリの枠の組み立て（compose.js）の中で、親の図と子の枠を1つの並びにして見える幅で折り返す。それ以外の組み立て（木、出し入れ、中身の種類、寸法、帯、出力の形）は iss-00614 D-03 のまま",
	"最初の表示を『幅に合わせる』にする。『収める』・拡大・移動・保存は変えない",
	"中の構造の図（layout.js、routeLayout に渡す幅）は変えず、線の検査の単体との比べを保つ",
]

current: """
	- `views/allgraph/compose.js` の `measure`：中身（`bodyOf`）を見出し・警告・帯の下に置き、出す子の枠を、中身の下（中身の高さが0でなければ `REPO.pad` を空けて）の棚 `pack(子, bodyWidth(width, depth))` に並べる。親の図の右は、子の枠が狭くても空いたまま。
	- `pack(items, limit)` は左から右へ `REPO.gap` を空けて並べ、`x > 0` で limit を超えるなら次の行（1つで超えるものはその行に1つ）。最上位も同じ `pack(tops, width − 2·REPO.margin)`。
	- `views/allgraph.js` の `initialView`：スマホ（`isPhone()`、root の幅 ≤ 640）は `s = 0.74`、`tx = 4`。PC は `s = min(1, max(0.88, (view.clientWidth − 16) ÷ 世界の幅))`、`tx = max(0, (view.clientWidth − 世界の幅·s) ÷ 2)`。どちらも `ty = barBottom() + 8`。世界が広いと 88% で横にはみ出し、中央に寄る。
	- `A.fitted` は画面を離れる（dispose）ときだけ false に戻り、範囲の切り替えや更新では最初の表示をやり直さない。倍率と位置は保存しない（graph.js も同じ）。
	"""

target: """
	- compose.js：中身の種類が `graph` の枠は、`[中身, ...出す子の枠]` を1つの並びとして `pack(…, bodyWidth(width, depth))` で並べる。graph でない枠は今のまま。
	- allgraph.js：`initialView` の PC の分岐を『幅に合わせる』（`s = min(1, (view.clientWidth − 16) ÷ 世界の幅)`、`tx = 8`）にする。
	"""

design: {
	"D-01": {
		title: "枠の中の並び（compose.js の measure と place）"
		text: """
			`measure(key, depth)` で、出す子の枠 `shown` と中身 `body`（`bodyOf` は変えない）が決まった後：

			- `limit = bodyWidth(width, depth)`。
			- 中身の種類が `graph` のとき：`flow = pack([body, ...shown], limit)`。中身は `flow.at[0]`（常に `{x: 0, y: 0}`）、子の枠 i は `flow.at[i + 1]`。中身の並びの上端は `bodyY`（見出し + 警告 + 帯。今と同じ）。枠の高さ `h = bodyY + flow.h + REPO.pad`、幅 `w = max(REPO.headW, flow.w) + 2·REPO.pad`。
			- 中身の種類が `graph` でないとき（loading・failed・empty・quiet）：今のまま。`shelf = pack(shown, limit)`、`shelfY = bodyY + body.h + (body.h > 0 ? REPO.pad : 0)`、`h = (shown があれば shelfY + shelf.h、なければ bodyY + body.h) + REPO.pad`、`w = max(REPO.headW, body.w, shelf.w) + 2·REPO.pad`（body.w は 0）。
			- `place`：子の枠 i の左上は、graph のとき `(x1 + REPO.pad + flow.at[i + 1].x, y1 + bodyY + flow.at[i + 1].y)`、graph でないとき今のまま `(x1 + REPO.pad + shelf.at[i].x, y1 + shelfY + shelf.at[i].y)`。出力の `body` は `{kind, x: x1 + REPO.pad, y: y1 + bodyY, w, h}` で今と同じ値（中身は並びの先頭なので）。
			- `pack` は変えない。子の枠が中身と同じ行に入るのは、`body.w + REPO.gap + 子の幅 ≤ limit`（2つ目以降も同じ累積）のときだけ。中身が limit より広いとき（F-01）は、`x > 0` の判定で子はすべて次の行から並ぶ。
			- 行の高さはその行のいちばん高いもの（pack のまま）。同じ行の子の枠は、その行の上端（中身の上端と同じ y）にそろう。
			- 木、出し入れ（next の規則）、`bodyOf` の表、寸法の定数 `REPO`、`bodyWidth`、最上位の `pack`、出力の形（`frames`・`order`・`width`・`height`、`head`・`warn`・`band`・`body`）は変えない。先頭のコメントの説明を新しい並びに合わせる。
			"""
		satisfies: ["R-01", "F-01"]
	}
	"D-02": {
		title: "帯の高さ（変えない作りの確かめ）"
		text: """
			帯の高さ `bandH` は今どおり `bodyY = REPO.head + warnH + bandH` に入る。並び（中身と子の枠）は `bodyY` から始まるので、帯の高さ h を渡すと、中身と、子の枠と、その子孫のすべてが h だけ下がり、枠が h 高くなる。帯の四角 `band` は今どおり `warn.y2` から h の高さ。帯を渡さないときと 0 のときの出力は同じ。
			"""
		satisfies: ["R-02"]
	}
	"D-03": {
		title: "最初の表示（allgraph.js の initialView）"
		text: """
			```js
			function initialView() {
			  const v = A.el.view;
			  const L = worldSize();
			  const top = barBottom() + 8;
			  if (isPhone()) {
			    A.s = 0.74;
			    A.tx = 4;
			  } else {
			    A.s = Math.min(1, (v.clientWidth - 16) / L.width); // fit the width: no part of the world past the view
			    A.tx = 8;
			  }
			  A.ty = top;
			}
			```
			- 倍率の下限は置かない（世界の幅だけで決まる。実データの PC の幅では 40% 以上）。`fitScale`・`minScale`・`fit`・`zoomAt` と『収める』の道具は変えない。拡大・縮小の下限 `minScale()` は『収める』の倍率に合わせて今どおり。
			- 呼ぶ時と回数（`A.fitted`、`whenStyled`）は変えない。範囲の切り替え・更新・配置のやり直しでは最初の表示をやり直さない（今のまま。R-03 の最後の受入はこの動きの確かめ）。
			- 関数の上のコメントに、最初の表示は PC で幅に合わせ（iss-00629）、スマホは構造の図と同じ、と書く。
			"""
		satisfies: ["R-03"]
	}
	"D-04": {
		title: "実機の確かめ（線の検査、写し、測り）"
		text: """
			iss-00614 の S-06 の道具（`relay_orca.py`、`shoot.mjs`、`node_audit.mjs`）を `.workbench/iss-00629/tools/` に写して使う（元は変えない）。
			- 候補のコミットを `git archive` から wheel にし、隔離した venv、iss-00614 の状態の置き場の写し（`.workbench/iss-00629/state`）、試しの `XDG_CONFIG_HOME`（orca_web.port を試しの中継に向ける）で、`spec-dock dashboard serve --offline --tailscale --port <空いた番号>` を立てる。常駐の 47800・8791、道具の環境、iss-00614 の試しの 18614・18799 には触れない。
			- headless Chrome（`--disable-features=MacAppCodeSignClone`、CDP `Browser.close`）で 1440・1000・390 × 明・暗 × 3範囲：最初の表示の倍率と、世界の右端が図の領域に収まるか、ブラウザーのエラー、横のスクロール、道具の帯と見出しの重なり、『収める』の倍率、倍率 100% での edgeAudit を、リポジトリごとに単体の構造の図（`/r/<鍵>/`、同じ範囲・幅）の edgeAudit と比べる。
			- node（`.workbench/iss-00629/tools/measure.mjs`）で、開始のコミットと候補のコミットの compose の世界の寸法と『収める』の倍率を、同じ実データの写しで比べる（R-01 の最後の受入）。
			- 数と写しは report.md と、この Scope の artifacts（`artifact import file`）に残す。本人が見る URL と止め方を report.md に書き、本人の確かめまで残す。
			"""
		satisfies: ["R-01", "R-03", "R-04"]
	}
}

compatibility: "compose の公開の入出力の形と、出し入れ・寸法・帯の決まりは変わらない。子の枠の位置だけが、親の図の右に空きがあるときに変わる。最初の表示は PC で倍率が下がることがある（88% の下限をやめる）が、横にはみ出さない。保存の形は変わらない。"

risks: [
	"実データでは親の図がほとんど見える幅に近いので、並びの得（世界の寸法の変化）は小さい。統括の決定どおり、得は測って書くだけにする",
	"最初の表示の倍率が PC の幅で 47〜59% になる（今は 88% 以上）。文字が小さく感じる場合は、本人の確かめで扱う（統括に報告）",
	"epic-00615（iss-00617）が帯の高さを足すとき、並びは bodyY からなので、帯は中身と子の枠を一緒に下げる（D-02）",
]
