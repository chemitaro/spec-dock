---
種別: レポート（Issue）
ID: "iss-00476"
関連GitHub: ["#476"]
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md", "plan.md"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

1つの CUE の Scope の要件・設計・計画を HTML に描く入口を足した（epic-00425 の I-5、Epic の R-F1・AC-09、契約 K5 の描画の入口）。

- `src/spec_dock/runtime/presentation/spec_page.py`：評価の JSON から、決まった並びの Markdown（検査の結果、保証レベル、要件、失敗・境界条件、設計、計画、その他の項目）を作り、I-4 の薄い説明資料と同じ形の HTML に包む。副作用のない部品。番号のリンクを両方向に張り、手順の状態と数を示す。文章でない値は逃がし、`<script>` の区切りを壊さない。
- `src/spec_dock/runtime/application/scope_render.py`：`render_scope_html(ScopeRenderSource, *, design_system_base, vendor_base, timeout=30.0) -> str`（ダッシュボード epic-00427 の入口）と `render_scope`（`RenderedScope`）。評価は I-2 の `check_scope_documents` を1回使う。保証レベルは I-2 と同じく `requirement.cue` だけから読む。
- `src/spec_dock/runtime/application/canonical_scope_render.py`：公開の葉 `spec-dock scope render <ID>`（54 → 55）。標準出力に HTML だけを出す。`--json` は `data.result.html`。警告 `SCOPE_RENDER_INCOMPLETE`、`DESIGN_SYSTEM_MISSING`、止まるコード `SCOPE_NOT_CUE`（7）を足した。
- 配布資産：`docs/reference_cli.md`（C55 と関数の入口の説明）、`docs/README.md`、`docs/cli-redesign-guide.html`、`docs/canonical.md`（エラーの表に3行）、`static-inventory.json`。dogfood の写し `spec-dock/docs/` も同じ PR で更新した。
- コミット：`1252f78e6`（描画の部品と入口）、`55f2c92fc`（CLI の葉と文書）、`df015b6d2`（コードレビューの指摘の修正）。

## Verification

- 仕様のレビュー（spec-reviewer opus/high）：1回目 P1 1、P2 3、P3 3（前付けの題名の逃がし、`--json` の秘匿化、`<!--` の扱い、`valid` の意味ほか）→ 仕様とコードを直し、2回目で合格（P0〜P3 なし）。結果は worktree の `.workbench/spec-review/iss-00476/`。
- コードレビュー（code-reviewer opus/high、標準と仕様の2人）：どちらも pass。指摘 P2 3、P3 1（囲いの補いがバッククォートを含む情報文字列を誤る、保証レベルの読み元、テキストの警告に次の1手がない、CLI 参照の入口の記述）をすべて直した（`df015b6d2`）。分析は `.workbench/code-review/iss-00476/review-response.md`。
- 最終品質ゲート（campaign `iss-00476-fqg-1`、quality-gate-reviewer opus/high 1人）：合格の SHA `df015b6d254520e768078607d56ab22a4d77dfd8`。
  - レビュー：pass、観点（functional-correctness、requirements-closure、test-adequacy）をすべて評価し終えた。P0 0、P1 0、P2 0、P3 2（情報のみ。下の「残ったリスク」）。
  - `make lint`：exit 0（ruff check、ruff format、mypy）。
  - `PATH="$PWD/.workbench/bin:$PATH" uv run pytest`：exit 0、3915 passed、8 skipped。
  - 記録は `.workbench/final-quality-gate/iss-00476-fqg-1/closure.md`。
- 手元の任意の確かめ：見本の Scope（`issue-strict-complete`）のページを、headless の Chrome で開き、`ds.js` が本文、表紙の題名、手順の表を描くことを DOM で確かめた（ネットワークを止めた検査ではない）。同梱の `marked` で、生の HTML の見出しと逃がしが意図どおりに解釈されることも確かめた。
- `cue` は v0.17.1 を、この worktree の無視されている `.workbench/bin/` に入れて使った。

## Residual Risks / Follow-ups

- **未確認**：ブラウザーでの描画は目で確かめていない（DOM の確かめだけ）。スマートフォンの幅、図の部品を手元から配った描画（`vendor_base` を渡した場合）は確かめていない。図は描画のページに出ないので、影響は小さい。
- PR #484（https://github.com/chemitaro/spec-dock/pull/484）の CI：head `df015b6d2` で、観測できた Actions と Commit Status がすべて成功、GitHub の状態は OPEN・MERGEABLE・CLEAN（2026-10-31T14:31Z の観測）。外部の CheckRun は観測の対象外。
- P3（情報のみ、直していない）：
  - FQG-001：文章の項目の各行の行末の空白を削るので、行末の2つの空白による強制改行が失われる。
  - FQG-002：schema 3 のリポジトリで `scope render` が `CANONICAL_NOT_MIGRATED` で止まることのテストがない（実装は `scope check` と同じ道を通る）。
- `ds.js` の Markdown の解釈が変わると描画が変わる。生の HTML の見出しと普通の Markdown だけを使い、`ds.js` の独自の指示は使っていない。
- 文章の項目の生の HTML は、説明資料と同じく消毒しない（`<script>` の区切りを壊すものだけを逃がす）。前付けの題名は、特殊な文字を全角の文字にして見せる。
- `scope render` は公開の葉が1つ増える CLI の契約の変更である（I-6 の版の文書で扱う）。
- I-3（#474）と共有のファイル（`catalog.py`、葉の数のテスト、CLI 参照、`static-inventory.json`）が先にマージされたら、衝突の解消が要る。
