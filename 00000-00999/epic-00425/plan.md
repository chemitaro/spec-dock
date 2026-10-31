---
種別: 計画書（Epic）
ID: "epic-00425"
タイトル: "Switch Spec Documents To CUE And HTML Explanations"
関連GitHub: ["#425"]
状態: "draft"
最終更新: "2026-10-31"
依存: ["requirement.md", "design.md"]
親: ["init-00423"]
---

# epic-00425 Switch Spec Documents To CUE And HTML Explanations — 計画

詳細: [Scope Layering Guide](../../../docs/authoring/scope-layering.md)

## 目標

`requirement.md` の受け入れ条件 AC-01〜AC-18 を満たす。具体的には、次の順に進める。

1. CUE の型（I-1）と、それを使う検査（I-2）、作るときの一式（I-3）を作る。
2. 説明資料のデザインシステムと図の部品（I-4）、CUE の描画（I-5）を作る。
3. ガイドとスキルをまとめ、版を出す（I-6）。
4. spec-dock に入れ、実際の Issue を CUE の仕様で回す（I-7）。

実装は、Issue ごとに、別の worktree で、この Epic の議論に参加していない実装担当のエージェントが行う。この計画書は、`requirement.md` と `design.md` とあわせて読めば、ほかの資料なしで各 Issue を始められるように書く。I-7 の導入は、統括が利用者の承認を得て行う。

## 実装担当への共通の指示

各 Issue の担当は、始める前に次を読む。

1. リポジトリの `AGENTS.md`（提供側と利用側の区別、層の置き場、テストの置き場、コミットとPRの規則、canonical モードの仕様の扱い）。
2. `.agents/skills/spec-dock/SKILL.md`。
3. この Epic の `requirement.md`、`design.md`（担当する契約 K1〜K6）、この計画書（担当する Issue の節と「Issue をまたぐ契約」）。
4. 説明資料 `explanation.html`（議論の経緯。正本ではない）。

作業のしかた：

- Issue ごとに、作業用の worktree とブランチを1つ使い、PRを1つ作る。`spec-dock work start <ID>` で始め、`spec-dock work finish` で終える。
- この Epic とその Issue の仕様は、今までどおり Markdown で書く（`requirement.md` の対象外）。最初に、その Issue の `requirement.md`、`design.md`、`plan.md` を、この計画書の節から書く。Epic の目的、Issue の分け方、契約は変えない。変える必要を見つけたら、止まって Epic の文書の変更を提案する。
- `cue` は、テストと手元の確かめのために、版を固定して入れる。利用者の環境（Homebrew など）に入れるときは、統括に頼む。
- 配布資産を変える PR は、dogfood の写し（`spec-dock/` の下）も同じ PR で更新する（`design.md` の「移行・互換性・rollback」）。新しい雛形は `spec-dock/templates/cue/` に置き、今の `spec-dock/templates/<種類>/` の `.md` の雛形は I-7 まで変えない。
- テストは、外のネットワークを使わない。GitHub は偽の `gh` で置き換える。ブラウザーの検査も、ネットワークを止めて行う。
- 毎回、`make lint` と `uv run pytest` を通す。Markdown の Scope の回帰（AC-12）を壊してはならない。
- してはならないこと：
  - 利用者のツールの設定、利用者の policy（`~/.agents/libexec/claude-model-effort/policy.md`）、利用者のスキル（`~/.agents/skills/japanese-explanatory-html/`）を変える。デザインシステムは写して使い、元を変えない。
  - spec-dock の本物のカタログで、I-7 より前に CUE の Scope を作る。
  - 本物の GitHub に、試しの Issue を作る（I-7 でだけ、統括が行う）。
- コミットは、日本語の Conventional Commits にする。PRはマージできる状態で止め、マージは人が行う。

## 順序・依存

### Issue の一覧

| 番号 | 題名（作成時の英語の題名） | 担当する契約 | 依存 | Planning Level |
|---|---|---|---|---|
| I-1 | Define CUE Spec Schema V1 | K1、K2、K6 の型の版 | なし | strict |
| I-2 | Add Scope Check With CUE | K3（`scope check`、`work finish`、`scope show`、`workspace validate`・`doctor`、説明資料の形の検査）、K1 の評価の呼び出し | I-1 | strict |
| I-3 | Scaffold CUE Scopes With Assurance | K4 | I-1、I-2、I-4 | strict |
| I-4 | Ship Explanation Design System | K5 のデザインシステム、薄い説明資料、図の部品 | なし | standard |
| I-5 | Render CUE Specs As HTML | K5 の CUE の描画 | I-2、I-4 | standard |
| I-6 | Document CUE Authoring And Release | ガイド、スキル、版 | I-1〜I-5 | standard |
| I-7 | Adopt CUE Specs In Spec Dock | dogfooding（R-J1） | I-6 | standard |

- Planning Level は、失敗したときの影響と戻しにくさで選んだ。
  - I-1 は、すべての CUE の Scope が従う型で、出した版は変えられない（K6）ので strict にした。
  - I-2 は、`work finish` を止める条件を変え、誤って止めると作業が終えられなくなるので strict にした。
  - I-3 は、`scope create` の必須の引数という、配られる CLI の契約を変え、GitHub に書く前の止め方を誤ると、半端な Issue が残るので strict にした。
  - I-4、I-5、I-6 は、読むだけの描画と文書で、戻しやすいので standard にした。
  - I-7 は、本物のカタログと GitHub に書くが、新しい Scope を作るだけで既存の Scope に触れず、戻しやすいので standard にした。
- この Epic の Issue は、Markdown の Scope なので、Planning Level を今までどおり `plan.md` の文章で扱う（R-H1）。

### 進め方

```text
I-1 ── I-2 ──┬──────── I-3 ──┐
             │          │    ├── I-6 ── I-7
I-4 ─────────┼──────────┘    │
             └──────── I-5 ──┘
```

- I-1 と I-4 は、並べて進めてよい。
- I-2 は I-1 の型を使う。説明資料の形の検査は、`design.md` の K5 の形に従って作るので、I-4 を待たない。I-3 は、I-1 の雛形、I-2 の `cue` の呼び出し、I-4 の薄い説明資料の雛形を使う。
- I-5 は、I-2 の評価の呼び出しと、I-4 のデザインシステムを使う。I-3 と並べて進めてよい。
- I-6 は、すべての後に、ガイドとスキルをまとめ、版を上げる。
- I-7 は、版を利用者の環境に入れた後に、統括が行う。

### Issue をまたぐ契約

| 契約 | 持ち主 | 使う側 | `design.md` |
|---|---|---|---|
| K1 評価の単位（ファイルの並べ方、`-t kind`、`schema` による版の選択、`_rank`） | I-1（呼び出しの部品は I-2） | I-2、I-3、I-5 | 責務・Interface 1 |
| K2 型の骨組み（番号のキー、`findings` の形、規則の名前、レベルの段階） | I-1 | I-2、I-5、I-6 | 責務・Interface 2 |
| K3 検査の結果の形（エラーのコード、JSON、`assurance.source`） | I-2 | I-3、I-5、I-6、epic-00427 | 責務・Interface 3 |
| K4 雛形の置き場（`templates/cue/`）と置き換えの印 | I-3 | I-6、I-7 | 責務・Interface 4 |
| K5 デザインシステムの置き場、薄い説明資料の形、図の部品の読み込み先、描画の入口 | I-4（描画の入口は I-5） | I-2（形の検査）、I-3（雛形）、I-5、epic-00427 | 責務・Interface 5 |
| K6 型の版の置き場と、リポジトリの型の置き場 | I-1 | I-2、I-6 | 責務・Interface 6 |

## 実装step

各 Issue の節は、その Issue の要件定義書の材料である。「受け入れ」は、その Issue の受け入れ条件にそのまま使う。

### I-1 Define CUE Spec Schema V1

- **価値**：CUE の Scope が従う型の版1ができる。保証レベルで必須の項目が変わり、つながりの抜けが `findings` に出る。この Epic の要（利用者の方針）。
- **作るもの**：
  - パッケージの `cue/v1/`：`schema`、`kind`、`assurance`、要件、設計、手順、テスト、`execution`、`findings` の型（K2）。種類ごとの違い（Epic と Initiative の切り分け）。
  - R-B3 の表の規則（`design.md` の規則の表）。
  - 3つの種類の雛形の CUE（`requirement.cue`、`design.cue`、`plan.cue`）の中身。置き換えの印を含む（印の扱いは I-3）。雛形は、置き換えた後に、そのまま型に通る。
  - 見本の Scope（テスト用）。レベルごと、規則ごとに、通るものと通らないもの。Epic と Initiative の `slices` による読み替え（R-B3 の注）の見本。
  - Provider CI（`.github/workflows/provider-ci.yml`）に、版を固定した `cue` の導入を足す（checksum を確かめる）。`cue` を要するテストは、ないときに失敗にする。
- **受け入れ**：
  - R-B3 の表の全ての組（規則 × 4つのレベル）で、違反する見本が、出す段階では `findings` に出て、出さない段階では出ない（AC-03）。
  - 見本の `assurance.level` を standard から strict に変えると、strict で必須の項目がない見本が誤りになる（AC-04）。
  - `execution` のつながりの違反が `findings` に出て、モデルと推論の名前はどんな文字列でも誤りにならない（AC-06）。
  - リポジトリの型の見本（`package spec`）を加えると、その制約と規則が加わる（AC-08）。
  - 雛形の CUE に見本の値を入れたものが、3つの種類で型に通る。
- **注意**：型の項目は最小から始める。迷う項目は任意にし、I-7 で直す。型を書く前に、型の項目の一覧と、レベルごとの必須の表を Issue の設計書に書き、統括の確認を受ける（利用者の方針で、この Epic の要のため）。

### I-2 Add Scope Check With CUE

- **価値**：`spec-dock scope check <ID>` で、CUE の Scope を、インターネットなしで検査できる。`work finish` が誤りの残る Scope を閉じない。`scope show --json` が保証レベルを返す。
- **作るもの**：
  - `infra/`：`cue` を呼ぶ部品（版の確かめ、引数の並び、時間の上限、誤りの文の解析）。
  - `application/`：K1 の評価、`findings` の読み取り、説明資料の形の検査（`design.md` の K5 の「薄い説明資料の形」のとおり）。
  - `canonical_workspace.py`：`workspace validate` と `doctor` の、形式ごとの必須のファイルの組。
  - `runtime/cli/`：`scope check <ID> [--json]`。
  - `canonical_work.py`：`work finish` の検査（何かを書く前）。
  - `canonical_scope_read.py`：`scope show` の `assurance`。
- **受け入れ**：
  - AC-02（`scope show` の `assurance`。`cue`、`unset`、`unreadable`）、AC-05、AC-07、AC-16。
  - `cue` がない、古い、時間切れのとき、入れ方を示して止まる（偽の `cue` で確かめる）。
  - Markdown の Scope では、成功で「CUE の Scope ではない」と示す。両方があれば止まる。
  - Markdown の Scope の `work finish` が、今と同じに動く（回帰のテストが変更なしで通る）。
  - AC-12 の `workspace validate`・`doctor` の部分、AC-17。

### I-3 Scaffold CUE Scopes With Assurance

- **価値**：`scope create` と `scope import github` で、保証レベルと理由を指定して、5つのファイルの一式を持つ Scope を作れる。
- **作るもの**：
  - `canonical_scope_create.py`：`--assurance`、`--assurance-reason` を必須にし、引数の段階で止める。理由を CUE の文字列に変えて置き換える。
  - 配布資産の雛形 `spec-dock/templates/cue/<種類>/`：3つの種類の `requirement.cue`、`design.cue`、`plan.cue`（I-1 の中身）、`explanation.html`（I-4 の薄い形）、`report.md`。`static-inventory.json` に足し、dogfood の写しを同じ PR で足す。今の `.md` の雛形は変えない（外すのは I-7）。
  - `templates/cue/<種類>/` がないとき、GitHub に書く前に止まり、`installation update` を示す。
- **受け入れ**：
  - AC-01。作った直後の Scope が、`scope check` で、雛形の説明資料の警告（Epic では誤り）だけを示す。
  - 引用符、改行、バックスラッシュを含む理由が、CUE の文字列として正しく入る。
  - 指定がないと、GitHub に何も書かずに止まる（偽の `gh` に要求が届かない）。
  - 既にディレクトリがある Scope を `scope import github` で補うとき、雛形を足さない。
  - AC-18。

### I-4 Ship Explanation Design System

- **価値**：説明資料が、Markdown だけを持つ薄い HTML で書け、どのチェックアウトから開いても描ける。図の部品を手元から配れる。
- **作るもの**：
  - 配布資産 `spec-dock/design-system/`（dogfood の写しを同じ PR で足す）：利用者のスキルのデザインシステム（`ds.css`、`ds.js`、`marked` とその利用許諾）の写し。`ds.js` の、図の部品の読み込み先を、ページが示す手元の場所、CDN の順に試すように直す。
  - パッケージの中の図の部品：`@plantuml/core` と highlight.js（版を固定。利用許諾を同梱）。
  - 薄い説明資料の雛形（`design.md` の K5 の形）。
  - ブラウザーでの描画の検査の手順（手元で任意。R-E4）。
- **受け入れ**：
  - AC-10、AC-11。
  - 薄い説明資料を、`spec-dock/initiatives/` からも `spec-dock/.canonical/` からも開いて、同じに描ける。
  - スマートフォンの幅（390px）で、横にはみ出さない。

### I-5 Render CUE Specs As HTML

- **価値**：1つの Scope の CUE の要件・設計・計画を、人が読める HTML に、その場で描ける。ダッシュボード（epic-00427）が呼べる。
- **作るもの**：
  - `application/`：`render_scope_html(<Scope>) -> str`（K1 の評価の JSON を、決まった並びの Markdown にし、K5 の薄い HTML に包む）。要件ごとに、設計、手順、テストを番号のリンクで結ぶ。`findings` をページの初めに示す。手順の状態を見せる。
  - `runtime/cli/`：`scope render <ID>`（標準出力）。
- **受け入れ**：
  - AC-09。
  - 同じ入力から、いつも同じ HTML ができる（決まった並び）。
  - 文章の項目の Markdown が描かれ、HTML の特殊な文字は、Markdown の外では逃がされる。

### I-6 Document CUE Authoring And Release

- **価値**：エージェントが、ガイドとスキルだけで、CUE の仕様を書き、検査し、計画を更新できる。版を出す。
- **作るもの**：
  - `docs/authoring/`：CUE の書き方（型、番号、つながり、保証レベルの選び方と書き換え、計画の台帳、`execution`、リポジトリの型）、説明資料の書き方。Issue Plan Guide、overview、scope-layering の Planning Level の記述を、保証レベルに直す（Markdown の Scope では今の書き方が残ることも書く）。過去の「Assurance」との区別。
  - `spec-dock` スキル：短い整理と、ガイドへのリンク。`scope create` の新しい必須の引数。
  - 版を上げる（番号は I-6 で決める）。上げるときの文書に、CLI の契約の変更を書く。
- **受け入れ**：
  - AC-13（白紙のエージェントでの試行）、AC-12、AC-15。

### I-7 Adopt CUE Specs In Spec Dock

- **価値**：spec-dock リポジトリで、新しい Scope を CUE で作り、実用に耐えるかを確かめる。
- **作るもの**：
  - 利用者の承認を得て、新しい版を利用者の環境に入れ、spec-dock の配布資産を `installation update` で上げる（PR）。同じ PR で、今の `.md` の雛形 `spec-dock/templates/<種類>/` を外す（提供側も）。`cue` の導入は、利用者に頼む。
  - 実際の Issue を1つ以上、CUE の仕様で作ってから閉じるまで回す。見つかった問題を、型とガイドの改善の Issue として返す。
- **受け入れ**：
  - AC-14。
  - 回した Issue の記録（何が書きやすく、何が書きにくかったか、型の直し）が、この Epic の `report.md` にある。

## 検証

- 各 Issue の受け入れと、`make lint`、`uv run pytest`。
- I-6 で、Markdown と CUE の Scope が並ぶ見本のリポジトリで、全体をつないで確かめる（AC-12）。
- I-7 で、本物の spec-dock で確かめる（AC-14）。

## rollback

- I-1〜I-6 は、PRごとに戻せる。配布資産は、版を戻して `installation update` で戻す。
- I-7 の後に問題があれば、前の版を入れ直す。作った CUE の Scope は、カタログに残る（`design.md` の rollback）。戻すかどうかは利用者が決める。

## exit / handoff

- AC-01〜AC-18 を満たし、I-7 の記録が `report.md` にある。
- epic-00427 に、K3（検査の結果の形）と K5（描画の入口、デザインシステムの置き場、図の部品）を渡す。epic-00427 の要件の見直し（`.md` と `.cue` の表示、報告の HTML、進み具合の図、Artifact の一覧、Tailscale での公開）を、統括が始める。

## モデルと推論

`~/.agents/libexec/claude-model-effort/policy.md` の §4 を、各 Issue の Planning Level に当てはめた。各 Issue の担当は、仕様化と実装を1つのセッションで続けて行う（§4 の `develop`）。仕様は Epic の文書から具体化するので、未確定のまま任せる扱いにはしない。

- 実装：
  - I-1、I-2、I-3：opus / high（strict）。
  - I-4、I-5、I-6、I-7：opus / medium（standard）。
- 例外：I-1 の型の設計は opus / xhigh（理由：すべての CUE の Scope が従い、出した版を変えられない。§3 H の横断的な設計）。I-1 は、型の設計から実装まで1つのセッションで行うので、セッションの全体を opus / xhigh で起動する。
- レビュアー（strict の Issue）：spec-reviewer opus / xhigh、code-reviewer opus / high、quality-gate-reviewer opus / xhigh と sonnet / high。
- レビュアー（standard の Issue）：spec-reviewer opus / high、code-reviewer opus / high、quality-gate-reviewer opus / high。
- 統括：opus / high。
