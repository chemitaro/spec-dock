# ディスカッション用シート（spec-dock v2 設計）

このフォルダは、`spec-dock` を **「単一 Issue の current/completed 移動」モデル**から、
**「Initiative → Epic → Issue (+ADR/Report/PUML等) を階層ツリーで常置し、現在地はポインタで示し、状態/集計は自動生成」**モデルへ更新するための、意思決定用シートです。

使い方（おすすめ）:
1. `01_*.md` から順に読み、**「ユーザー回答欄」**を埋める
2. 各シートの最後の「結論」へ決定事項を転記する
3. 決定が出揃ったら、実装タスク（CLI/テンプレ/生成物/移行）に落とす

シート一覧:
- `01_tree_root_location.md` — 仕様ツリー本体の置き場所・名前（`work` を避けたい問題）
- `02_current_pointer_design.md` — current initiative/epic/issue を固定パスで明示する設計（symlink/manifest）
- `03_source_of_truth_and_sync.md` — 状態の正（GitHub vs ローカル）と `sync` の深さ（Project/labels 等）

