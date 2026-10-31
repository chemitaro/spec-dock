---
種別: 設計書（Issue）
ID: "iss-00477"
関連GitHub: ["#477"]
状態: "approved"
最終更新: "2026-11-01"
依存: ["requirement.md"]
---

# iss-00477 Document CUE Authoring And Release — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- ガイドとスキルを、型（`src/spec_dock/cue/v1/`）とランタイムの定数に、テストで縛る。書いた名前やコードが実物とずれたら落ちる（F-01）。
- ガイドの見本を、本物の `cue` で検査する。写せば通る見本にする（F-02）。
- 既存の Markdown の Scope 向けの節、見出し、語は残し、CUE の Scope の節を足す（F-03）。
- 版を上げる変更を、版の3か所と目録に閉じる（F-05）。

## Current / Target

| | 今 | この Issue の後 |
|---|---|---|
| CUE の書き方 | 雛形の注と、I-1〜I-5 の設計書・報告にしかない | `docs/authoring/cue.md` |
| 説明資料の書き方 | 雛形と I-4 の報告にしかない | `docs/authoring/explanation.md` |
| Planning Level の記述 | Markdown の `plan.md` の書き方だけ | CUE の Scope は保証レベル、Markdown は今のまま、と両方を書く |
| `spec-dock` スキル | `scope create` の必須の引数を知らない | 短い節とガイドへのリンク |
| `canonical.md` の表 | partial（6）の場合がない。`SCOPE_KIND_CHANGED` の手順が CUE の Scope と食い違う。`ASSURANCE_*` の行を縛るテストがない | 直し、テストで縛る |
| 版 | 0.3.0 | 0.4.0 と、`migration.md` の「0.4.0 への更新」 |

## 責務・Interface

### D-01 `docs/authoring/cue.md`（R-01）

節の並び：

1. `## CUE の Scope とは`：見分け方（`requirement.cue` があれば CUE の Scope）、5つのファイル、Markdown の Scope との共存、両方があれば `SCOPE_FORMAT_CONFLICT`。
2. `## 評価の単位`：K1 の `cue export` の並びをそのまま示す。`package spec`、`import` を書かない、種類はタグで GitHub から来る。
3. `## 保証レベル`：4つの値、選び方（影響と回復の難しさ。工数で選ばない）、`reason`、作るときに必須、途中で上げ下げしてよい、正本は `requirement.cue` だけ、親の計画に子のレベルを書かない、`scope show --json` の `assurance.source`。モデルと推論の対応表を SpecDock は持たない。過去の Assurance との区別へのリンク。
4. `## 文書と項目`：`requirement.cue`、`design.cue`、`plan.cue` の項目の表（必須、任意、番号の形）。保証レベルで必須になる項目の表（`acceptance` は standard から、`impact`・`recovery` は strict から、`rollback` は critical で手順か切り分けがあるとき）。型にない項目を足してよい。文章の項目は Markdown。
5. `## つながりの規則`：8つの規則の表（名前、内容、出る段階）。Epic・Initiative の `slices` による読み替え。`dropped` の手順は数えないが参照は調べる。
6. `## 計画の台帳`：`status`（`todo`、`doing`、`done`、`dropped`）、`after`、作業しながら直接書き換える、専用のコマンドはない。
7. `## 実行の割り当て`：`execution.sessions`、`reviews`、手順の `session`、`execution-reference`、モデルと推論は文字列。
8. `## リポジトリの型`：`spec-dock/cue/*.cue`、`package spec`、`_rank` は読むだけ、`_specdock` を使わない、規則の名前を重ねない。
9. `## 検査と表示`：`scope check <ID> [--json]`、`scope show`、`scope render`、`work finish` の検査、結果のコードの表（コード、重さ、意味、次の1手）。
10. `## cue を入れる`：v0.17.1 以上、`go install cuelang.org/go/cmd/cue@v0.17.1` の例、Markdown の Scope には要らない。
11. `## 見本（Issue、standard）`：3つのコードの囲み。各囲みは ```` ```cue ```` で始め、1行目を `// requirement.cue` などのファイル名の注にする（テストが、この注でファイルに分ける）。
12. `## 書く順番`：エージェントの手順（`scope create` → 要件 → 設計 → 計画 → `scope check` → 作業中に `status` を更新 → `work finish`）。

### D-02 `docs/authoring/explanation.md`（R-02）

節：置き場と名前、薄い形（3つの条件）、雛形の印、CUE との関係（下書きが先でよい、CUE を書いた後は CUE が正本）、書く内容（柔軟、Epic は必ず書き換える）、検査（`EXPLANATION_MISSING`、`EXPLANATION_SKELETON`、`EXPLANATION_INVALID` と重さ）、図とコード（PlantUML、`ds-vendor-base`、CDN）、ブラウザーでの確かめ（手元で任意、`tests/browser/` は提供側のリポジトリの道具）、`scope render` との違い。

### D-03 既存のガイド（R-03）

- `overview.md`：`## CUE の Scope と保証レベル` を `## Planning Level` の前に足す。2つのガイドへリンクし、`## Planning Level` は Markdown の Scope 向けだと1文を足す。冒頭の「Markdown で書き始める」は、CUE の Scope への案内を1文足す。
- `issue-plan.md`：冒頭に、この Guide は Markdown の `plan.md` 向けで、CUE の Scope は `cue.md` の保証レベルと計画の台帳に従う、と1段落足す。`## Planning Levelの選び方` は変えず、その前に `## 保証レベル（CUE の Scope）` を足す。
- `scope-layering.md`：`## 親 scope を再定義しない` の後に `## 保証レベル（CUE の Scope）` を足す（一段上で決める、親は子の ID だけを書く、Epic・Initiative の計画は `slices`）。
- `historical.md`：過去の Assurance と新しい保証レベルの区別の1段落を足す。
- 既存の authoring のテストのうち、リンクの集合を完全一致で比べる `test_authoring_overview_navigation_links_to_all_current_guides` と `test_template_readme_navigation_catalogs_exact_scope_docs_and_current_artifacts` の期待に、新しいリンクを足す（統括の許可）。

### D-04 `templates/README.md`（R-04）

`## CUE の Scope の雛形` を足す：`cue/{initiative,epic,issue}/{requirement.cue,design.cue,plan.cue,explanation.html,report.md}`、印、2つの引数、`templates/cue/` がないときの `SCOPE_TEMPLATES_OUTDATED`、2つのガイドへのリンク。今の一覧の行（`.md` の雛形）は残す。

### D-05 スキル（R-05）

`## 仕様の扱い（canonical モード）` の後に `## CUE の Scope と説明資料` を足す（10行ほど）。`AGENTS.md` と共有する「仕様の扱い」の節は変えない（`test_issue436_agent_rules.py` が一致を求める）。

### D-06 `canonical.md` と復旧の文（R-06）

- `SCOPE_CHECK_FAILED` の行の終了コードに「6（partial。保存を待つ間に開き直された CUE の Scope の `work finish`。束を書いた後）」を足す。
- `SCOPE_KIND_CHANGED` の行と `SCOPE_KIND_CHANGED_RECOVERY` を、次の手順に直す：種類のラベルを戻す。種類を変えるのが意図なら、`spec-dock scope create <新しい種類> --assurance <値> --assurance-reason <理由>` で作り直す（新しい Scope は CUE の Scope）。古い Markdown の要件・設計・計画は、新しい `requirement.cue`、`design.cue`、`plan.cue` に書き写し、`requirement.md` などをそのまま移さない（並ぶと `SCOPE_FORMAT_CONFLICT`）。`artifacts/`、`discussions/` などのほかのファイルは移す。古い Scope を `spec-dock scope delete` する。
- 冒頭に、0.4.0 から新しい Scope は CUE の Scope になり、書き方は `authoring/cue.md` にある、と1文足す。
- 新しいテスト：CUE の部品のモジュール（`canonical_scope_create.py`、`scope_check.py`、`canonical_scope_check.py`、`scope_render.py`、`infra/cue_tool.py`）の公開のコードの定数が、`canonical.md` の表か `cue.md` のコードの表にあり、次の1手が空でない。`canonical.md` の表にある `ASSURANCE_*` の行を名指して確かめる。

### D-07 版（R-07）

- `pyproject.toml` の `version = "0.4.0"`、`uv lock` で `uv.lock` の自分の版だけを変える。
- `system/spec-dock-version` を `0.4.0`（提供側と写し）。目録の `sha256` を新しくし、`0.3.0\n` の値を `known_old_sha256` に足す。
- `migration.md` に `## 0.4.0 への更新` を足す。
- ルートの `README.md`：「全53コマンド」を「全55コマンド」、`## 2つのモード（0.3.0）` の後に、0.4.0 の CUE の Scope と `cue` の必須を1段落と、`migration.md` の節へのリンク。
- 新しいテスト：3つの版の一致と、`migration.md` の節の語。

### D-08 つないだ統合テスト（R-08）

`tests/cli_runtime/test_issue477_mixed_repository.py`。`WriteWorld`（偽の GitHub、本物の Git のカタログ、偽の定期の実行）で、Initiative、Epic、Markdown の Issue を置き、`scope create issue --assurance standard ...` で CUE の Issue を作る。作った CUE の Issue に `cue.md` の見本の3つのファイルと書き換えた説明資料を置く（ガイドの見本が、作った Scope でも通ることを兼ねる）。AC-08 の各コマンドを順に流す。`work finish` は I-2 のテストと同じ時計の差し替えと同期の呼び出しを使う。

### D-09 白紙のエージェントでの試行（R-09）

- 候補の wheel を、この worktree の外の一時の場所に作り、一時の venv に入れる。
- 試行のための一時のリポジトリ（schema 4、偽の `gh`、カタログのリンク）を、テストの補助（`WriteWorld` と同じ組み立て）を使う小さな台本で作る。台本は `.workbench/` に置き、コミットしない。
- サブエージェント（opus / medium、新しいもの）に渡すのは、一時のリポジトリの道筋、候補の `spec-dock` の道筋、`cue` の道筋、「`.agents/skills/spec-dock/SKILL.md` と `spec-dock/docs/authoring/` だけを読む」という指示、作業（ある Issue の CUE の要件・設計・計画を書き、`scope check` に通し、手順を `doing`・`done` に更新し、もう一度通す）だけ。この会話、Epic・Issue の設計書、提供側のソースは渡さず、読まないよう指示する。
- 結果（迷った点）で、ガイドを直す。直したら、テストを流し直す。

## data / failure

- ガイドとスキルは文書で、データを持たない。ランタイムの変更は、復旧の文の文字列だけ。
- 版の食い違い（F-05）：テストで3か所を照らす。
- 見本の検査は、本物の `cue` を要する（`cue` がなければ、I-1 の方針どおり失敗にする）。

## 変更対象

- 提供側：`src/spec_dock/assets/spec_dock/docs/authoring/{cue,explanation}.md`（新しい）、`overview.md`、`issue-plan.md`、`scope-layering.md`、`historical.md`、`docs/canonical.md`、`docs/migration.md`、`templates/README.md`、`system/spec-dock-version`、`assets/static-inventory.json`、`assets/install_root/.agents/skills/spec-dock/SKILL.md`、`runtime/application/canonical_errors.py`（文だけ）。
- dogfood の写し：`spec-dock/docs/...`、`spec-dock/templates/README.md`、`spec-dock/system/spec-dock-version`、`.agents/skills/spec-dock/SKILL.md`。
- `pyproject.toml`、`uv.lock`、`README.md`。
- テスト：`tests/unit/infra/test_issue477_authoring_docs.py`（新しい）、`tests/cli_runtime/test_issue477_mixed_repository.py`（新しい）、既存の `test_authoring_kit_assets.py`（リンクの集合の期待2か所）、`tests/integration/test_issue413_assets.py`（資産の数）。
- 変えないもの：型、検査、作成、描画の振る舞い。今の `.md` の雛形。`AGENTS.md`。

## 移行・互換性・rollback

- 文書と版だけの変更で、PR を戻せば元に戻る。版のタグはマージの後に統括が作るので、この PR はタグを作らない（`release-tag.yml` が 0.4.0 への上げで動くかは、マージの後に統括が確かめる）。
- 配布資産の更新は、利用者が `installation update` で取り込む。新しい2つのガイドは、目録に足すので、`installation update` で入る。

## testability

- 文書とランタイムの照合：AC-01〜AC-07 を、新しい `test_issue477_authoring_docs.py` で確かめる。規則の名前と段階は `rules.cue` を読んで、コードはランタイムの定数を読んで照らす（文字を写さない）。
- 見本の検査：`cue.md` の見本を一時の Scope に置き、`check_scope_documents` を本物の `cue` で呼ぶ。
- 統合：AC-08 を `test_issue477_mixed_repository.py` で確かめる。
- 回帰：既存のテストを変えずに（許した2つの種類の変更を除き）全体を流す。

## risk

- **ガイドが長すぎる**：エージェントが読む量が増える。スキルは短くし、ガイドの節を分け、表で示す。白紙の試行で確かめる。
- **既存のテストの縛りが強い**：見出しや語を変えると落ちる。足すだけにする。
- **並行の作業との衝突**：`static-inventory.json`、資産の数、`canonical.md` は、ほかの Issue も変えうる。衝突したら `origin/main` をマージして解消する。
- **白紙の試行の環境**：一時のリポジトリの組み立てがテストの補助に依る。組み立てが崩れたら、試行の前に直し、組み立ての手順を `report.md` に残す。
