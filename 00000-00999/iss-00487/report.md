---
種別: レポート（Issue）
ID: "iss-00487"
関連GitHub: ["#487"]
最終更新: "2026-11-01"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

epic-00425 の I-6（iss-00477）のレビューで残った3つの直しを行った。spec-dock で初めて、CUE の仕様（`requirement.cue`、`design.cue`、`plan.cue`、`explanation.html`、`report.md`）で始めから終わりまで回した Issue である。

- **R-01 ガイドの相互リンク**：`issue-plan.md` と `scope-layering.md` の「保証レベル（CUE の Scope）」の節が、`cue.md` に加えて `explanation.md` へもリンクする。配布の資産と dogfood の写し（`spec-dock/docs/authoring/`）を同じ中身にし、`static-inventory.json` の `sha256` を更新し、前の中身を `known_old_sha256` に足した（`cue.md` も同じ）。
- **R-02 `cue.md` の表のテスト**：`cue.md` の「検査と表示」の表のコードの集合が、`scope_check` と `canonical_scope_check` の公開のコードと等しいこと、`cue` の道具の失敗のコードの「止まる（N）」が実装の終了コードと合うことを、`cue.md` 単独で確かめるテストを足した。
- **R-03 葉の `--help` の共通の引数**：葉の parser に「common options」の組を、表示だけの項目（`default=SUPPRESS`、`_common_*` の dest）として足した。その葉で受け付けるものだけを出す判定は `accepts_common_option` にまとめ、`parse_vnext` の4つの拒否（`--yes`、`--dry-run`、`--offline`、`--lock-timeout`）も同じ関数を使う。解析の経路（共通の引数を先に取り除く）と既定値は変えていない。`--timeout` の既定は葉ごとに表示する（`worktree bootstrap` は 300）。
- **R-04**：`cue.md` の「葉の `--help` の一覧には出ませんが、使えます」を、「common options」に出るという説明に直した。
- **R-05**：下の「CUE の仕様の試し」。

コミット：`155d144d8`（`feat(cli): ヘルプにコマンド別の共通オプションを表示`）。PR：（下の Verification）。

## Verification

- `spec-dock scope check iss-00487`：誤り0、警告0。`spec-dock scope render iss-00487`：終了コード0、HTML を描けた。
- 仕様のレビュー（spec-review、spec-reviewer opus / medium、CUE の4ファイルを sha256 で固定）：1回目で合格。P0/P1 0、P3 1（R-02 の本文は「止まるコードの終了コード」、受け入れの条件は `cue` の道具の失敗のコードだけ、と範囲が食い違う。実装は受け入れの条件の範囲）。
- コードのレビュー（code-review、code-reviewer sonnet / high、`7f3cf7d3c..155d144d8`、axis both）：合格。指摘0。
- 最終品質ゲート（final-quality-gate、quality-gate-reviewer opus / high、1人、campaign `iss-00487-fqg-1`、attempt 01、`155d144d8`）：
  - レビューの側：合格。P0/P1 0、網羅は完全、P3 1（FQG-001。下の Residual Risks）。
  - テストの側：GATE_TEST_LANE_RESULT
- 先に同じコミットで `uv run pytest -x`：4029 passed、8 skipped（21分39秒）。

## Residual Risks / Follow-ups

- **FQG-001（P3）**：変更する葉に `-y` を argparse の表示用の項目として足したため、短いフラグのまとめ書き（`-yy`）が使い方の誤りから受理に、`-yh`/`-hy` が help の表示に変わる。`--yes` の効果は付かない（安全側）。直すなら、`-y` を argparse に登録せず、`--yes` の説明に「`-y` でも同じ」と書く。ゲートの規則で P3 は直していない。
- `--color` は受け付けるが、今の実装で色を付ける処理は見当たらない。help は「text color mode」とだけ書いた。
- コマンドの補完（`completion_script`）は `--lock-timeout` を `work start` だけに出し、`branch switch` に出さない（解析は両方で受け付ける）。この Issue の範囲の外。

## CUE の仕様の試し

### 書きやすかったこと

- **雛形のコメント**：各項目のコメントが、必須の項目と保証レベルでの違いを書いていて、`cue.md` の表と合わせれば迷わなかった。3つの CUE のファイルを書いて、最初の `scope check` が誤りなしで通った。
- **番号のキー**：`"R-01": {...}` の形は、参照（`realizes`、`verifies`、`satisfies`）を文字列で書くだけで、つながりを検査が見てくれる。Markdown の表よりつながりの抜けを気にしなくてよい。
- **計画の台帳**：手順を1行1つの構造で書くと、`status` を機械的に書き換えやすい。
- **`execution`**：セッションとレビューのモデルと推論を、構造で1か所に書けた。レビューの `after` で、どの手順の後のレビューかを書けるのが便利。
- **説明資料**：`ds-source` の中の Markdown だけを書き換えればよく、雛形の印を消すまで警告が出るので、書き忘れない。
- **固定**：仕様のレビューで、CUE のファイルを `sha256` で固定するのは手順が1つ増えるだけだった。

### 書きにくかったこと

- **`status` の位置が自由**：手順ごとに `status` を書く位置がずれ、一括で書き換えたとき、自分の誤りで同じ手順に `status` が2つ入った。値が違えば `CUE_INVALID` で止まるが、同じ値なら CUE は黙ってまとめる。
- **既定値との衝突の文**：`status: "doin"`（打ち間違い）で、`CUE_INVALID` が2件出た。1件目「conflicting values "todo" and "doin"」は、既定値 `todo` との衝突を言っていて紛らわしい。2件目の「out of bound =~"^(todo|doing|done|dropped)$"」が本当の手がかりだった。
- **light でのテスト**：light では `requirement-without-test` が出ないので、テストのない要件（R-05 の report）も通る。設計どおりだが、テストの欄を書くかどうかの判断は書き手に任される。
- **空の文書が通る**：雛形のまま（要件0）でも `scope check` は誤りなしで通る（設計どおり。`cue.md` にも書いてある）。

### `scope check` と `scope render`

- `scope check` の誤りは、ファイル、行、列、項目（`steps."S-06".status`）を示し、直す手がかりとして十分だった。つながりの指摘（`SPEC_FINDINGS`）は日本語の文と、どのファイルの何を直すかの `hint` があり、すぐ直せた。一方で、`CUE_INVALID` の `hint` は英語で、指摘の日本語と混じる。
- `scope render` は、保証レベル、要件、設計、計画の順で、読みやすい1枚の HTML になった。デザインシステムを `file://` の絶対の道筋で読むので、別の機械に渡すとスタイルが外れる（手元で見る用途なら問題ない）。

### 改善の提案（優先度つき）

1. **高**：既定値のある列挙（`status`）の誤りで、既定値との「conflicting values」の行を、out of bound の行にまとめるか、後ろに回す（`scope check` の誤りの整理。型は変えない）。
2. **中**：`CUE_INVALID` の `hint` を、`SPEC_FINDINGS` と同じく日本語にする（`scope check` の表示）。
3. **中**：雛形の手順の例に、`status` を `title` と `realizes` のすぐ後に書く並びを示す（一括で書き換えやすい。雛形の変更）。
4. **低**：light でも、`tests` が空のときに「テストが1つもない」ことを情報として示す（指摘ではなく情報。型の規則の追加）。
5. **低**：`scope render` に、デザインシステムを埋め込む、または相対の道筋で書く選択肢を足す。

### 手間の目安

- 仕様（3つの CUE、説明資料）を書いて `scope check` を通すまで約15分。同じ規模の Markdown の仕様（`requirement.md`、`design.md`、`plan.md`）より短く感じた。主な理由は、つながりの確かめを検査に任せられること。
- 台帳の更新と検査の繰り返しは、1回あたり数秒（`scope check` は手元だけで動く）。
