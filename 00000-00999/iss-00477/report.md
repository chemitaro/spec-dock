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

エージェントが `spec-dock` スキルとガイドだけで CUE の仕様を書き、検査し、計画を更新できるようにし、I-1〜I-5 をつないで確かめ、0.4.0 の準備をした（epic-00425 の I-6）。

- **ブランチとコミット**：`chemitaro/iss-00477`、base `d53b24d64`（origin/main）。
  - `10142ee97` ガイド、スキル、`canonical.md`、`migration.md`、`README.md`、復旧の文、版 0.4.0、目録、文書の縛りのテスト
  - `c4ba92ceb` Markdown と CUE の混在リポジトリの統合テスト
  - `2e2178477` 白紙の試行で直したガイド
  - `dc0fd9d72` コードのレビューの P3 の修正（最終品質ゲートの合格のコミット）
- **新しいガイド**（提供側と dogfood の写し、目録に追加）：`docs/authoring/cue.md`（CUE の Scope、評価の単位、保証レベル、項目、レベルごとの必須、8つの規則の表、計画の台帳、`execution`、リポジトリの型、検査と表示、結果のコードの表、`cue` の入れ方、書く順番、standard の Issue の見本）、`docs/authoring/explanation.md`（置き場、薄い形、印、CUE との関係、検査の重さ、図、ブラウザーでの確かめ）。
- **既存のガイド**：`overview.md`（`## CUE の Scope と保証レベル`、Planning Level は Markdown の Scope 向けと明記）、`issue-plan.md` と `scope-layering.md`（`## 保証レベル（CUE の Scope）`）、`historical.md`（過去の Assurance との区別）。既存の見出しと語はすべて残した。
- **`templates/README.md`**：`## CUE の Scope の雛形`（5つのファイル、印、2つの必須の引数、`SCOPE_TEMPLATES_OUTDATED`、2つのガイド）。
- **スキル**：`## CUE の Scope と説明資料`（版4だけ、版3は `CANONICAL_NOT_MIGRATED`、必須の引数、`scope check`、`scope render`、台帳の更新、`work finish` の検査、ガイドの道筋）。
- **`canonical.md`**：冒頭に 0.4.0 の CUE の Scope の1文。`SCOPE_CHECK_FAILED` の行に 6（partial、待つ間の開き直し）。`SCOPE_KIND_CHANGED` の行を、CUE で作り直し、`.md` を移さず書き写し、`SCOPE_FORMAT_CONFLICT` を避け、`scope delete <今の ID>` する手順に直した。ランタイムの `SCOPE_KIND_CHANGED_RECOVERY` も同じ内容に直した（文だけ）。
- **版**：`pyproject.toml`、`uv.lock`、`system/spec-dock-version`（提供側と写し）を 0.4.0。目録は、書き換えた9つの既存の配布資産の `d53b24d64` の `sha256` を `known_old_sha256` に足し、新しい2つのガイドを足した。`migration.md` に `## 0.4.0 への更新`、ルートの `README.md` に `## CUE の仕様（0.4.0）` と「全55コマンド」（統括の許可の範囲）。
- **版のタグ**：この PR のマージで `release-tag.yml` が `v0.4.0` を自動で作る（ワークフローは変えていない。統括の確認）。

### 変えた既存のテストと理由（統括の許可、2026-11-01）

| ファイル | 変えたこと | 理由 |
|---|---|---|
| `tests/unit/infra/test_authoring_kit_assets.py` | `overview.md` のリンクの集合の期待に `cue.md`、`explanation.md` を足した。`templates/README.md` のリンクの集合の期待に `../docs/authoring/cue.md`、`../docs/authoring/explanation.md` を足した | 新しいガイドへのリンク（許可(1)） |
| `tests/cli_runtime/test_issue455_flat_ids.py` | 定数 `RECOVERY` の文字列を新しい復旧の文に置き換えた（比べ方は変えていない） | `SCOPE_KIND_CHANGED` の文を直すため（許可） |
| `tests/integration/test_issue413_assets.py` | 資産の数 110→112、111→113 | 新しい2つのガイドを目録に足したため（I-3、I-4 の前例と同じ形） |

## Verification

### 最終品質ゲート（`final-quality-gate`、campaign `iss-00477-g1`）：合格

- 合格のコミット：`dc0fd9d72da6a5ad2e2a339c8d5e20d04e5bd976`（clean、attempt 01）。
- レビュー（quality-gate-reviewer opus / high、1人、観点 functional-correctness、requirements-closure、test-adequacy）：pass、網羅は完全、P0 0・P1 0・P2 0・P3 2（下の Residual）。
- テスト：`make lint` exit 0。`env PATH=<worktree>/.workbench/bin:$PATH uv run pytest -p no:cacheprovider` exit 0（4023 passed、8 skipped、21分07秒）。`cue` は v0.17.1 を worktree の無視されている `.workbench/bin` に入れて使った。1回目は利用者の PATH の空白（VS Code の項目）で `env` が分かれて exit 127 になったので、空白の項目を除いた PATH で同じ命令を流し直した。
- 記録：worktree の `.workbench/final-quality-gate/iss-00477-g1/`（`campaign.json`、`attempts/01/`、`closure.md`）。ChatGPT のレーンは使っていない（無効）。
- それより前に、`c4ba92ceb` での全体のテストで `test_issue413_assets.py` の34件が落ちた。テストの途中でガイドを書き換え、目録と一時的に食い違ったためで、同じファイルは前後と合格のコミットで通っている。

### PR と CI

- PR：https://github.com/chemitaro/spec-dock/pull/486（`chemitaro/iss-00477` → `main`、head `dc0fd9d72da6a5ad2e2a339c8d5e20d04e5bd976`、`Refs #477`、`Refs #425`）。
- CI（`github-pr-checks`、2026-10-31T17:22Z の観測、Actions と Commit Status）：Provider CI（run 41223248366）、SpecDock check（41223248428）、Commit identity（41223248454、push 41223208135）がすべて success。GitHub は OPEN、非 draft、MERGEABLE、CLEAN（`OBSERVED_CI_PASS`、`READY`）。外部の CheckRun は観測の範囲外。
- マージは人が行う。`spec-dock work finish` は、マージの後に統括の指示で行う（未実行）。

### それまでの確かめ

- 仕様のレビュー（spec-reviewer opus / high）：第1回 fail（P1 1、P2 4、P3 1。既存テストの RECOVERY、known_old_sha256、版3の境界、自動のタグ、試行の環境、delete の ID）→ 統括の判断を得て直した。第2回 pass（P3 1。文言を直した）。記録は worktree の `.workbench/spec-review/iss-00477/`。
- コードのレビュー（code-reviewer opus / high、規約と仕様の2人、`2e2178477`）：どちらも pass。P3 3件（README のテストの範囲、リポジトリの型の見本が Epic にも効く）を `dc0fd9d72` で直した。見本は本物の `cue` で Issue と Epic を評価して確かめた。
- 受け入れ条件とテスト：AC-01〜AC-07 は `tests/unit/infra/test_issue477_authoring_docs.py`（17件。規則の名前を1つの段階で変えると落ちることを手で確かめた）、AC-08 は `tests/cli_runtime/test_issue477_mixed_repository.py`、AC-09 は下の試行、AC-10 は上のゲート。

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

- **最終品質ゲートの P3（情報のみ、直していない）**：FQG-001 `issue-plan.md` と `scope-layering.md` は `cue.md` にだけリンクし、`explanation.md` にはリンクしない（R-03 の「2つのガイドへつなぐ」に対し、`overview.md` は両方へつなぐ）。FQG-002 `cue.md` のコード表の一部の行は、`canonical.md` の表との和集合でしか縛られていない。
- **葉の `--help` に共通の引数が出ない**：`--json`、`--offline`、`--timeout` は、葉の help の一覧に出ない（既存の CLI の作り）。ガイドに書いて補った。help に出すかは別の Issue で決める。
- **空の CUE の文書が検査に通る**：要件が1つもなくても誤りにならない（型 v1 の作り）。ガイドに注意を書いた。型で止めるかは I-7 の実際の Issue で決める材料。
- **統括・利用者へ**：マージで `v0.4.0` が自動で作られたことの確かめ。I-7 での `installation update` と `.md` の雛形の撤去。利用者の手順（`coordinate` など）の `scope create` に `--assurance`・`--assurance-reason` を足すこと。
- **未確認**：直した後のガイドでの2回目の白紙の試行。Linux での全体のテスト（PR の CI で確かめる）。本物のカタログと GitHub での CUE の Scope の作成（I-7）。
