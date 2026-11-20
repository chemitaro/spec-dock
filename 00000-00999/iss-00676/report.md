---
種別: レポート（Issue）
ID: "iss-00676"
関連GitHub: ["#676"]
最終更新: "2026-11-20"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## 開始のコミット

`83b8ee95f8fbcc06b601fd5ab3a02018b0995ee4`（origin/main の 0.9.9、worktree はきれい）。

## 診断（2026-11-20、タスク担当）

- 再現：この worktree のソース（0.9.9 と同じ）で、状態の置き場の写しを使い、別のポートでダッシュボードを立てた。orca-web の要約は、CDP の Fetch で中継して読んだ（常駐の orca-web は Origin `http://127.0.0.1:47800` だけを許すため）。CDP で範囲を切り替えて `specdockCmdAudit()` を取った。
  - `/graph`：next は links 0・arcs 0。now と all は links 8・arcs 2。
  - `/r/github.com/chemitaro/spec-dock/`：next は 0・0。now と all は links 7・arcs 1。
- `paintCommand` に一時の計測を入れて確かめた（計測は戻した）。`/graph` の next では、`commandPairs` が8組を返し、`unknown` は false、worktree は52件が対応していた。それでも `crossPlace` の `pairs` は0組だった（`for (const pair of next ? [] : pairs)`）。
- 結論：計算の退行ではない。2つの決定が重なっていた。`/graph` の既定の範囲は epic-00612 で『これから』と決まっている。iss-00668 の決定（統括 msg_e863b639b47f）で、『これから』では指揮の線を引かない。`/r/<repo>/` の既定は『いま』（layout.js の `DEFAULTS`）なので、そちらでは線が出ていた。
- 反証の試み：次の2つを一時的に当てて既存のテストへの影響を数えた（どちらも戻した）。
  - A（`/graph` の既定を『いま』にする）：allgraph の画面のテストが5件落ちる。
  - C（crossPlace の next の分岐を外す）：テストが5件落ちる。
- 本人の決定は B（両方の画面の『これから』で線を引く）。統括の設計の決定は requirement.cue の decisions にある。

## レビュー記録

- 仕様のレビュー：合格。spec-reviewer opus / high、1回目。結果は `.workbench/spec-review/round-1b.json`（1回目の結果のファイル `round-1.json` は、題名の長さの形式の誤りで検査に落ちたので書き直した。機械的なやり直しで、別の回ではない）。P0 0、P1 0、P2 2、P3 1。合格の sha256：
  - requirement.cue `a43c8b1328635d06d8474a0f0553985ff2deb1584c76f359057c21b6a230c7f2`
  - design.cue `f4422b4e12547c1f9b376827f98114ca4ce5ff27896bc17d40d45e3ac5220abe`
  - plan.cue `045d114a1c0149eae356184aea65b6d6cb0c2f78618c881db50e87ff87755208`
- P2・P3 は直さず、受入の読み方を次の「逸脱と判断」に書いた。

## 逸脱と判断

- P2（R-01 の motion・heads）：『いま』と同じ値になることは、『これから』で隠れた Scope を含まない組の入力で確かめる。隠れた Scope の子については、祖先の枠に落ちた分を線の本数で確かめる（T-03 のとおり）。
- P2（F-02 の番号）：この Issue の F-02（F-05 の組み直しの上限を『これから』でも守る）は、『これから』での画面のテストで確かめる。同じ入力のとき描き直さないこと、組み直しが2回までであることを見る。iss-00617 の F-02（unknown のときの見送り）は今のまま確かめる。
- P3（R-04 の『合う』）：`/graph` は全部のリポジトリの組を描く。そのため `/graph` の『いま』の links は、各 `/r/<repo>/` の組を重なりを除いて合わせた数と比べる。実機では、`/graph` の『これから』の links が 0 より多いことと、『いま』と『これから』の差が隠れた Scope の分で説明できることを確かめる。

## Outcome

## Verification

## Residual Risks / Follow-ups
