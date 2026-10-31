---
種別: 実装計画書（Issue）
ID: "iss-00477"
関連GitHub: ["#477"]
状態: "approved"
最終更新: "2026-11-01"
依存: ["requirement.md", "design.md"]
---

# iss-00477 Document CUE Authoring And Release — 実装計画

詳細: [Issue Plan Guide](../../../docs/authoring/issue-plan.md)

## Planning Level

- **standard**（Epic の計画書で決めた値）。
- 理由：文書と版の変更で、振る舞いを変えるランタイムの変更は復旧の文だけ。PR を戻せば元に戻る。版のタグはマージの後に統括が作る。
- risk factor：ガイドが型・ランタイムとずれること、既存のテストの縛り、共有のファイル（目録、資産の数、`canonical.md`）での衝突。
- 再評価の条件：型、検査、作成、描画の振る舞いを変える必要が出たら、統括に聞く。

## 目標

`requirement.md` の AC-01〜AC-10 を満たし、Epic の AC-12、AC-13、AC-15 の証拠を残す。

## 順序・依存

- 依存：I-1〜I-5（マージ済み）。
- 順序：S-01 → S-02 → S-03 → S-04 → S-05 → S-06 → S-07。S-03 と S-04 は並べてよい。S-06 は S-02〜S-05 の後（ガイドが揃ってから試す）。

## 実装step

テスト駆動（Red → Green → Refactor）で進める。

- **S-01 文書の縛りのテスト（Red）**：`tests/unit/infra/test_issue477_authoring_docs.py` に AC-01〜AC-07 のテストを書き、落ちることを確かめる。
- **S-02 新しいガイド**：`cue.md`（見本を含む）、`explanation.md`。目録と写し。AC-01、AC-02 を Green にする。
- **S-03 既存のガイド、雛形の一覧、スキル**：`overview.md`、`issue-plan.md`、`scope-layering.md`、`historical.md`、`templates/README.md`、スキル。既存のテストのリンクの集合の期待を直す。AC-03〜AC-05。
- **S-04 canonical.md と復旧の文**：表の2行、冒頭の1文、`SCOPE_KIND_CHANGED_RECOVERY`。AC-06。
- **S-05 版**：`pyproject.toml`、`uv.lock`、`spec-dock-version`、目録、`migration.md`、`README.md`、資産の数。AC-07。
- **S-06 つないだ統合テスト**：`tests/cli_runtime/test_issue477_mixed_repository.py`。AC-08。
- **S-07 白紙のエージェントでの試行**：設計 D-09 のとおり。結果でガイドを直し、`report.md` に書く。AC-09。
- **S-08 全体の確かめ**：`make lint`、`PATH="$PWD/.workbench/bin:$PATH" uv run pytest`。カタログのリンクのある worktree では、既知の12件（`test_authoring_kit_assets.py` のリンクを辿るテスト）が環境で落ちるので、全体はリンクのない clean な clone で流す（I-2〜I-5 と同じ）。AC-10。

## 検証

- 受け入れ条件：S-01 と S-06 のテスト、S-07 の記録。
- regression：既存のテストの全体。変えた既存のテストは、リンクの集合の期待と資産の数だけ。
- negative：ガイドの記述を型・ランタイムと照らすテストは、名前を1つ変えると落ちることを手で確かめる。
- レビュー：`spec-review`（opus / high）、`code-review`（opus / high）、`final-quality-gate`（opus / high、1人）。

## rollback

- PR を戻す。版のタグは作っていないので、戻すのは PR だけ。マージの後にタグを作った後で問題が出たら、0.4.1 で直す（forward recovery）。

## exit / handoff

- PR をマージできる状態で止める。`spec-dock work finish` はしない。
- 統括へ：版のタグの作成、I-7 での `installation update` と `.md` の雛形の撤去、利用者の手順（`coordinate` など）の `--assurance` の追加。
