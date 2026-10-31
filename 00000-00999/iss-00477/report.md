---
種別: レポート（Issue）
ID: "iss-00477"
関連GitHub: ["#477"]
最終更新: "2026-11-01"
依存: ["requirement.md", "design.md", "plan.md"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

（最終品質ゲートの後に追記する。）

## Verification

### 白紙のエージェントでの試行（AC-09、Epic の AC-13）

- **使ったもの**：候補の wheel（`d53b24d64` からの `c4ba92ceb` を、worktree の外の一時の場所で `uv build`、一時の venv に入れた `spec-dock 0.4.0`）、`cue` v0.17.1、テストの補助で組んだ一時のリポジトリ（schema 4、本物の Git のカタログとリンク、ファイルに状態を持つ偽の `gh`、`HOME`・`XDG_*` を一時の場所に、`GIT_ALLOW_PROTOCOL=file`、`GH_TOKEN` などを外す）。提供側の `spec-dock/docs/`、`design-system/`、`templates/`、`.agents/skills/spec-dock/` を写した。組み立ての台本は worktree の `.workbench/trial_setup.py`（コミットしない）。渡す前に、`source env.sh` の後で `scope show`、`scope check` が動き、`gh` が偽物であることを確かめた。
- **試行者**：新しいサブエージェント（opus / medium）。渡したのは、一時のリポジトリの道筋、環境のファイル、「リポジトリの中の `.agents/skills/spec-dock/SKILL.md`、`spec-dock/docs/`、`spec-dock/templates/`、`--help` だけを読む」という指示、課題（`import` コマンドの要件・設計・計画を書く、検査に通す、説明資料を書く、計画を台帳として更新する、strict に上げて直す、`scope show` と `scope render`）だけ。この会話、Epic・Issue の設計書、提供側のソースは渡していない。
- **結果**：5つの段階のすべてで、最後は誤り0・指摘0・警告0（`GITHUB_SNAPSHOT_STALE` を除く）になった。
  - 要件 R-01・R-02、失敗の条件 F-01・F-02、設計 D-01〜04、手順 S-01〜05、テスト T-01〜04 を書き、1回目の `scope check` で誤り0・指摘0（説明資料の雛形の警告だけ）。
  - 説明資料を書き換え、印を消して警告0。
  - 計画を台帳として更新（done、doing、dropped、手順の追加、F-03 の追加）し、通った。
  - strict に上げると `CUE_INVALID` 6件（`impact`・`recovery`）→ 直すと `failure-without-test` 1件 → テストを足して通った。
  - `scope show --json` は strict、`source=cue`。`scope render` は終了コード0。
- **迷った点と、直したガイド**（`2e2178477`）：
  1. 親が Markdown の Scope のときに、任された範囲をどこで確かめるか → `cue.md`「書く順番」1 に書いた。
  2. 葉の `--help` に `--json`、`--offline`、`--timeout` が出ない → `cue.md`「検査と表示」に、共通の引数であることを書いた（help に出ないのは既存の CLI の作りで、この Issue では変えていない）。
  3. 「インターネットは要らない」と `GITHUB_SNAPSHOT_STALE` の関係、要約の `warnings=N` に数えないこと → `cue.md` に書いた。
  4. 空の文書が誤りなしで通る → `cue.md` の規則の節と「書く順番」6 に注意を書いた（型は変えていない。I-7 で型を直すかを決める材料）。
  5. 形の誤りがある間は、つながりの指摘が出ない → `cue.md` に書いた。
  6. `CUE_INVALID` の `file` が型のファイルを指す → `cue.md` のコードの表に書いた。
  7. 規則の「要件」に `F-` を含むか → `cue.md` に、`R-` だけで、`F-` は strict からの `failure-without-test` だけと書いた。
  8. 作業中に見つけた失敗の条件、`dropped` の理由、説明資料への反映 → `cue.md`「計画の台帳」に書いた。
  9. `<head>` の `<title>` と案内のコメントの扱い → `explanation.md`「薄い形」に書いた。
  10. GitHub の題名（export）と課題（import）が食い違った → 試行の組み立ての題名の選び方の誤り（台本の問題）。ガイドの問題ではないので直していない。
  11. `GITHUB_SNAPSHOT_STALE` が出たり出なかったりする → 3 と同じく書いた。
- **未確認**：直した後のガイドで、もう一度、白紙の試行はしていない。

## Residual Risks / Follow-ups

（最終品質ゲートの後に追記する。）
