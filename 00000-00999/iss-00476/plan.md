---
種別: 実装計画書（Issue）
ID: "iss-00476"
関連GitHub: ["#476"]
状態: "approved"
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md"]
---

# iss-00476 Render CUE Specs As HTML — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- **standard**（Epic の計画書で決めた値）。
- 理由：読むだけの描画で、何も書かず、PR を戻せば元に戻る。公開の葉が1つ増える CLI の契約の変更を含むが、足すだけで、今のコマンドの動きは変えない。
- risk factor：`render_text` の変更が、ほかのコマンドの出力に効かないこと。I-3 と共有のファイル（`catalog.py`、葉の数のテスト、CLI 参照）で衝突すること。
- 再評価の条件：I-2 の部品や、ほかのコマンドの契約を変える必要が出たら、統括に聞く。

## 目標

`requirement.md` の AC-01〜AC-10 を満たし、Epic の AC-09 を満たす描画の入口を、ダッシュボード（epic-00427）に渡せる状態にする。

## 順序・依存

- 依存：I-2（#473、マージ済み）、I-4（#475、マージ済み）。
- 並行：I-3（#474）が `catalog.py` などを変える。衝突したら `origin/main` をマージして解消する。
- 順序：ページの部品（S-01）→ 入口（S-02）→ コマンド（S-03）→ 文書（S-04）→ 全体の確かめ（S-05）。

## 実装step

テスト駆動（Red → Green → Refactor）で、受け入れ条件ごとに進める。

- **S-01 ページの部品**（`runtime/presentation/spec_page.py`、`tests/unit/presentation/test_spec_page.py`）：AC-03、AC-04、AC-06、AC-07 と、AC-01 の HTML の形。手で作った評価の JSON で確かめる。
- **S-02 入口**（`runtime/application/scope_render.py`、`tests/unit/application/test_scope_render.py`）：AC-01、AC-05（関数の側）、AC-08。本物の `cue` と見本の Scope、偽の `cue`。
- **S-03 コマンド**（`canonical_scope_render.py`、`catalog.py`、`canonical_dispatch.py`、`runtime_dispatch.py`、`envelope.py`、`tests/cli_runtime/test_issue476_scope_render.py`、葉の数のテスト）：AC-02、AC-05（コマンドの側）、AC-08（`SCOPE_NOT_CUE`）、AC-09。
- **S-04 文書**：配布資産の `reference_cli.md`（C55）、`README.md`、`cli-redesign-guide.html`、`canonical.md`（エラーの表）、`static-inventory.json`、dogfood の写し。
- **S-05 全体の確かめ**：`make lint`、`uv run pytest`（`cue` v0.17.1 を PATH に通す）（AC-10）。

コミットは、S-01〜S-02、S-03〜S-04 の区切りで、コードだけを入れる（仕様はコミットしない）。

## 検証

- 受け入れ条件ごとのテスト（上の S-01〜S-03）。
- `make lint`、`uv run pytest`（全体）。Markdown の Scope の回帰のテストは変えない。
- 手元の任意の確かめ：見本の Scope の `scope render` の出力をブラウザーで開き、描けることを見る（自動の検査はしない。できなければ report に「未確認」と書く）。

## rollback

- この PR を戻す。データの移行はない。

## exit / handoff

- 完了：AC-01〜AC-10、最終品質ゲートの合格、PR がマージできる状態。
- epic-00427 へ：入口 `render_scope_html(ScopeRenderSource, *, design_system_base, vendor_base)` と、止まるときのコード（`SCOPE_NOT_CUE` と K3 のコード）、`RenderedScope.complete`。
- 残るリスク：`ds.js` の解釈の変化（design の risk）。
