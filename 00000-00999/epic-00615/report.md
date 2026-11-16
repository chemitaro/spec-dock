---
種別: レポート（Epic）
ID: "epic-00615"
関連GitHub: ["#615"]
最終更新: "2026-11-17"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

（Epic の完了時に書く）

## Verification

（Epic の完了時に書く）

## レビュー記録

### 仕様のレビュー（2026-11-17、合格）

- レビュアー：spec-reviewer（Opus 5.5 / high）1人。保証レベル standard なので、2人目（ChatGPT）は置いていない。
- 結果：合格（P0 0、P1 0、P2 4、P3 3）。結果のファイルは main のチェックアウトの `.workbench/spec-review/epic-00615/round-1.json`（検査 `round-1.check.json`、`status: pass`）。
- 合格した文書の sha256：
  - `requirement.cue` 46cb958ede1f7d482ff9a35087f964b8ba96f73a6107494d126211a383076411
  - `design.cue` c505d45cf4dec4dc21d149783b1d8fe71cb74bf97e33caff1eff12b55f501a31
  - `plan.cue` 4e826eb1d4edb195f38fd9ec6827494e6abbb71e33c15e0a6d97763c74dbab66
  - `explanation.html` 961d5195dc8f35e70ba075481392f896672018b9ad43dbe29dab4efe68d7e18c
- `spec-dock scope check epic-00615`：誤り0、警告0。

### 子の Issue への申し送り（P2・P3。止めない指摘。Issue の仕様で決める）

- **iss-00617（P2）**：R-11 は「指揮している親」がいるときだけ枠を出すが、D-06 は `band > 0`（子だけでも）で出すと読める。R-11 に合わせ、帯に親がいるときだけ入れ物の枠を出す（子だけのときは、その子は全体の帯「ほかの場所」）。
- **iss-00616（P2）**：両端が帯の同じ項目に入る組（main のチェックアウトの統括と、同じ main のチェックアウトの worker）の描き方が決まっていない。R-04 の「同じ居場所」に帯の項目も含め、線を引かず、帯の中の親の印に電波の輪を付ける形を推す。R-01 の受け入れの合成の入力では、報告書の実データどおり同じ居場所の組を2組（同じ worktree の Issue の組、main のチェックアウトの組）にする。
- **iss-00616（P2）**：リポジトリの構造の図で、両端ともほかのリポジトリにいる組（報告書の tenting-cradle の組など）まで帯に出る。少なくとも一方の端がこのリポジトリにいる組だけを図に出す絞りを足すことを推す（目的が「この図の Scope の仕事をだれが指揮しているか」のため）。
- **iss-00617（P2）**：『横断の構造』では、途中の枠に帯が出入りすると後ろの枠が動き、R-09 の「箱を画面の上で動かさない」を全部の箱には満たせない。補いの基準（画面のいちばん上の見えている枠）より下の箱が動くことを許すか、帯の高さを、指揮があるリポジトリに限って先に確保するかを、Issue の仕様で決める。
- **iss-00616（P3）**：D-04 の色相 50〜58° のうち、暗いテーマの `--sd-blocked`（約43.4°）から10°離すには約53.4°以上が要る。明るいテーマのコントラストは図の背景 `--ds-bg-2`（#f6f7f9）と比べる（例の #a89200 は約2.9:1 で足りない）。
- **iss-00616（P3）**：帯の端を印の下の辺にすると、制御点を端の上に持ち上げる曲線は帯の中へ戻る。帯から出る線は、制御点を下に置く（下へ垂れる弧）。
- **iss-00616（P3）**：構造の `worktrees.status` が ok でない（読めない）と `matchWorktrees` が対応を作らず、このリポジトリのエージェントが全部帯に「ほかのリポジトリ」として出る。この状態では、稼働の印と同じく線と帯を出さない（F-01 に足す）ことを推す。

## Residual Risks / Follow-ups

- orca-web の iss-00043 への依存は、リポジトリをまたぐので GitHub の blocked-by に登録できない（`spec-dock dependency add --to gh:chemitaro/orca-web#43` は `SCOPE_NOT_FOUND`）。`plan.cue` の `prerequisites` に書いた。orca-web の iss-00043 も本人の順序で iss-00614 の後に始める。
- orca-web の epic-00004 の `plan.cue` の `slices` には iss-00043 がまだない（この依頼の範囲外のため書いていない）。
