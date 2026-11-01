---
種別: レポート（Issue）
ID: "iss-00489"
関連GitHub: ["#489"]
最終更新: "2026-11-01"
依存: ["requirement.cue", "design.cue", "plan.cue"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

iss-00487 の「CUE の仕様の試し」の改善の提案5つを実装した（保証レベル standard）。

- **R-01（高）既定値のある列挙の誤り**：`scope_check._shape_errors` が、見出し `N errors in empty disjunction` のある項目で、`conflicting values` の行とほかの理由の行（out of bound など）が両方あれば、`conflicting values` を独立の診断にせず、残す診断の `details.cue_related` に CUE の原文のまま入れる。`status: "doin"` は、許す値を示す1件の `CUE_INVALID` になる。項目の名前で決め打ちしないので、リポジトリの型が足した同じ形の項目にも効く（テストで確認）。選言でない誤りは今のまま。`cue_output` は全文を持つ。
- **R-02（中）`CUE_INVALID` の `hint` を日本語に**：評価の誤り、型だけが場所を示す誤り、`schema` の誤り、項目のない文法の誤りの4通り。`message` と `cue_message` は変えない。
- **R-03（中）Issue の CUE 雛形**：`templates/cue/issue/plan.cue` の手順とテストの例を1行の形にし、`status` を `title` と `realizes` のすぐ後に置く理由をコメントに書いた。dogfood の写し、`static-inventory.json`（`sha256` と `known_old_sha256` に今の版 `08b4c2fd…`）を更新。`installation update` が今の版を新しい版に置き換えることをテストで確認。
- **R-04（低）`SPEC_NO_TESTS`**：K3 の形（誤りと警告）は変えず、警告を1つ足した。Issue、評価が通る、保証レベル light、`tests` が空のときだけ出る。警告だけなので検査は成功のまま。K3 の形を変えないので、統括への確認は要らなかった。
- **R-05、F-01（低）`scope render --design-system inline`**：`ds.css` を `<style>` に、`marked.umd.js` と `ds.js` をこの順に base64 の `data:` の `<script src>` に埋め込む（`</script>` を含む中身を書き換えずに入れられ、`marked` が先にあるので `ds.js` は `vendor/` を読みに行かない）。既定は `file` で今のまま。`render_scope_html`（K5）には既定値つきの `embed_design_system: Path | None = None` を足しただけ。`inline` でデザインシステムがなければ `DESIGN_SYSTEM_MISSING`（終了コード3）で止まり、HTML を出さない。`--json` は `design_system`（`file`/`inline`）を足し、`inline` では `design_system_base` が `null`。
- ガイド：`cue.md`（結果の表に `SPEC_NO_TESTS`、`cue_related`、`--design-system inline`）、`reference_cli.md`（C55 の引数）、`canonical.md`（`DESIGN_SYSTEM_MISSING` の行）と各写し、目録。`scope check`/`scope render` の葉の help の JSON 説明。

判断したこと（統括に報告）：

- 依頼の「3つの種類すべて」の雛形の `status`：Epic と Initiative の `plan.cue` は手順（`steps`）と `status` を持たない（型が `slices` だけを許し、`steps` を書くと誤り）。Issue の雛形だけを変えた。
- 提案5は「埋め込み」だけを足し、「相対の道筋」は足していない。`scope render` は標準出力に出すので、出力の場所が分からず、相対の道筋を決められないため。

コミット：`ccb8f5aa4`（実装）、`e673b46b6`（help の JSON 説明。コードのレビューの P3 への対応）。PR：https://github.com/chemitaro/spec-dock/pull/490（head `e673b46b6`、マージできる状態で停止。`work finish` はマージの後に統括が行う）。

## Verification

- `spec-dock scope check iss-00489`：誤り0、警告0。`scope render iss-00489`（既定と `--design-system inline`）：終了コード0。
- 仕様のレビュー（spec-review、spec-reviewer opus / high、CUE の3ファイルを sha256 で固定）：1回目で合格（P0/P1 0、P2 3、P3 1）。P2/P3 は妥当で安く直せたので、合格の後に仕様に反映した（D-07 の回帰テストの範囲、R-03 の受け入れの条件を「例の行が `#Step` に合う」に、`canonical.md` を範囲に、文法の誤りの `hint`）。
- コードのレビュー（code-review、code-reviewer opus / high、2人、`c43aadd5b..ccb8f5aa4`）：standards 合格（P3 1：help の JSON 説明に `cue_related` がない → `e673b46b6` で直した）、spec 合格（指摘0）。
- 実ブラウザー（T-11）：`--design-system inline` で描いた iss-00489 の HTML を、`node tests/browser/explanation-check.mjs --file <page> --cdn-from-package`（ネットワークを遮断した headless Chrome）で開き、`VALIDATED`（`ready: true`、例外0、390px で横にはみ出さない）。HTML の `file:` は仕様の本文の中だけ。
- `ccb8f5aa4` で `uv run pytest`（全体）：4047 passed、8 skipped（21分51秒）。
- PR #490 の CI（github-pr-checks、2026-11-01T02:53:47Z）：`OBSERVED_CI_PASS`、終了コード0。SpecDock check、Commit identity、Provider CI がすべて success。merge_readiness は READY。観測の範囲は Actions と Commit Status。
- 最終品質ゲート（final-quality-gate、quality-gate-reviewer opus / high、1人、campaign `iss-00489-fqg-1`、attempt 01、`e673b46b6`）：
  - レビューの側：合格。P0/P1 0、網羅は完全、P3 1（FQG-001：全枝が `conflicting values` の選言（制約のない列挙）をまとめないことを確かめるテストがない。実装は条件で守っている。ゲートの規則で直していない）。
  - テストの側：合格。`make lint` 終了コード0（ruff check、ruff format check、mypy すべて pass）、`uv run pytest` 終了コード0（4047 passed、8 skipped、21分33秒）。証拠は worktree の `.workbench/final-quality-gate/iss-00489-fqg-1/`（`closure.md`、`attempts/01/`）。

## Residual Risks / Follow-ups

- `cue` の誤りの文の形（`N errors in empty disjunction`、`conflicting values`）が将来の版で変わると、まとめが効かなくなる。そのときは今と同じ2件に戻るだけで、誤りは失われない。
- 埋め込んだ HTML は約 400KB。図の部品（PlantUML、highlight.js）は埋め込まず、今までどおり CDN から読むので、オフラインでは図が描けない（本文とスタイルは描ける）。
- `CUE_INVALID` 以外のコード（`EXPLANATION_*`、`SCOPE_DOCUMENT_MISSING`、`ASSURANCE_UNREADABLE` など）の `hint` は英語のまま（範囲の外）。揃えるなら別の Issue。
- FQG-001（P3）：制約のない列挙の選言の誤りがまとめられないことを確かめるテストを足すとよい（今の実装は守っている）。
- 未確認：`--design-system inline` の HTML を、実際に別の PC に写して開くこと（同じ PC の、デザインシステムの道筋を持たないページとして確かめた）。

## CUE の仕様で書いて気づいたこと

- 仕様のレビューで、P2 として「受け入れの条件が文字どおりには成り立たない」（雛形の例のコメントを外しても、`R-01` がないので `unknown-reference` が出る）が見つかった。CUE の検査はつながりを見るが、受け入れの条件の文の検証可能性は見ないので、レビューは今も要る。
- 台帳の `status` を `sed` で一括に書き換えたとき、`after: ["S-02", …]` を持つ別の手順の行まで当たった。1手順1行の形は書き換えやすいが、行に別の手順の番号が入るので、キーで当てる（`^\t"S-0n"`）必要がある。
- 今回の R-01 の直しで、`status` の打ち間違いが1件の誤りになった。
