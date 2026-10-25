---
種別: 要件定義書（Issue）
ID: "iss-00434"
タイトル: "Add Default Branch Spec Check And Workflow"
関連GitHub: ["#434"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00424", "init-00423"]
---

# iss-00434 Add Default Branch Spec Check And Workflow — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

表示名：既定のブランチの検査のコマンドと、検査のワークフローの見本を足す（Epic の I-7）

## 目的

既定のブランチに仕様が入ったPRを、CIで見つけられる。各プロダクトは見本を写すだけで使える。

- 材料：Epic の `plan.md` の「I-7 Add Default Branch Spec Check And Workflow」の節（価値、作るもの、受け入れ、注意）と、Epic の `design.md` の8章（既定のブランチの検査）、1章の版3の止まり方とその例外、12章の `canonical check` と `CANONICAL_CHECK_FAILED` の行、「変更対象」の I-7 の行。Issue をまたぐ契約は、Epic の `plan.md` の「Issue をまたぐ契約」の表に従う。
- 依存（`plan.md` の I-番号）：I-1（契約 C2 の `REPOSITORY_INDEPENDENT_HANDLERS` を使う）。Planning Level：standard（理由は `plan.md`）。
- この Issue は、契約 C7（版のファイル、検査のワークフローの見本、`.github/scripts/specdock-ci-check.sh`）の持ち主である。I-8（`cut`）、I-9、I-10、I-12、I-13（0.4.0）は、ここで決める公開の形（`design.md` の「C7 の公開の形」）を変えずに使う。

## 背景

- Epic は、仕様の内容の正本を `spec-dock/canonical` ブランチに移し、既定のブランチと、そこへ入るPRのツリーに、仕様のパスを1つも置かない（Epic の R-A4）。人やエージェントが誤って仕様のファイルをコードのブランチに入れても、PRの段階で見つけて止める仕組みが要る（R-F1〜R-F3、AC-12）。
- 今のCIは、各リポジトリが SpecDock の特定のコミットを入れて `spec-dock workspace validate --ci` を実行している（Epic の `design.md` の Current の表）。これは仕様が既定のブランチにある前提の検査で、切り替えの後は使えない。各リポジトリの切り替えのPRで、新しい検査のワークフローに置き換える（R-J5。置き換えは I-8 の `cut` と、I-10、I-12 の担当）。
- 検査のワークフローは、SpecDock の版を上げても書き換えずに済むよう、入れる版をリポジトリの版のファイルで決め、版のタグから入れる（R-F2、Epic の `design.md` 8章「版の固定」）。版のタグは、spec-dock の既定のブランチで `pyproject.toml` の版が 0.3.0 以上に上がったときに、ワークフロー `release-tag.yml` が作る。
- 関係者：
  - 各プロダクトのリポジトリ（R-J1）：見本を `.github/workflows/` に写し、既定のブランチの名前を合わせるだけで検査が動くこと。
  - 人とエージェント：PRの検査の結果から、どのパスをどう直せばよいかが分かること（R-H2）。
  - 後の Issue の実装担当（I-8、I-9、I-10、I-12、I-13）：版のファイル、見本、`specdock-ci-check.sh`、`canonical check` の出力の形を、`design.md` だけで使えること。
  - 利用者：移行していないリポジトリ（宣言の版3）の動きが、何も変わらないこと（AC-15）。

## 観測可能な要件

### R-434-01 `spec-dock canonical check`（Epic の R-F1）

- チェックアウトの、指定したコミット（既定は `HEAD`）のツリーを調べる。作業ツリーとインデックスは読まない。カタログ、ネットワーク、GitHub のトークン、状態の置き場がなくても動き、何も書かない。
- 次の6つを調べる（Epic の `design.md` 8章）。
  1. `spec-dock/initiatives` そのものと、その下のパスがない（ファイル、シンボリックリンク、gitlink を含む）。
  2. `spec-dock/.canonical` そのものと、その下のパスがない。
  3. `spec-dock/` の下に `.meta.json` がない。
  4. `spec-dock/workspace.json` があり、版が4で、`writer_protocol` が既知である。
  5. 配布資産が、このパッケージの資産か、既知の古い版と一致する（今の `installation show` の判定）。`spec-dock/.gitignore` に、Epic の `design.md` 3章の無視の3行がある。
  6. `spec-dock/system/spec-dock-version` が、動いている SpecDock の版と同じ（違えば警告）。
- 1〜5の問題は、1件ずつ、パスと次の1手を付けて返す。1件でもあれば `CANONICAL_CHECK_FAILED`（終了コード7）で終わり、見つけた問題をすべて並べる。6は警告で、終了コードを変えない。ただし、版のファイルも配布資産なので、中身がこのパッケージの知らないもの（このパッケージの版でも既知の古い版でもない）なら、5の失敗にもなる。
- 宣言の版が3のときも、`CANONICAL_NOT_MIGRATED` で止めずに、調べること4の失敗の1件（パスと次の1手付き）として返し、ほかの調べることも続ける（Epic の `design.md` 1章の版3の止まり方の例外。撤去の後も同じ。I-1 の `plan.md` の統括の判断 B）。
- 作業ツリーの宣言の版やモードに関係なく、同じ動きをする。そのため、`dispatch()` の `resolve_context` より前に呼ぶ表 `REPOSITORY_INDEPENDENT_HANDLERS`（契約 C2）に登録する。

### R-434-02 版のファイル（契約 C7）

- 配布資産 `spec-dock/system/spec-dock-version` を足す。中身は、このパッケージの版の文字列の1行（例 `0.2.4` と改行）で、`pyproject.toml` の版と同じである。
- 静的資産なので、`installation init` が置き、`installation update` が版に合わせて書き換える（Epic の `design.md` 8章「版の固定」）。

### R-434-03 検査のワークフローの見本（Epic の R-F2）

- 配布資産 `spec-dock/docs/ci/spec-dock-check.yml` を足す。中身は Epic の `design.md` 8章の見本である。PRと既定のブランチへの push で動き、`spec-dock/system/spec-dock-version` の版のタグから SpecDock を入れて、`spec-dock canonical check --json` を実行する。
- 各リポジトリへは、I-8 の `cut` が、これを `.github/workflows/spec-dock-check.yml` に写し、既定のブランチの名前の1か所だけを書き換える。

### R-434-04 spec-dock 自身の検査のスクリプト（契約 C7）

- `.github/scripts/specdock-ci-check.sh` を足す。今の `specdock-ci-validate.sh` と同じ方法（固定した SHA のソースから wheel を作り、外の環境に入れる）で SpecDock を入れ、最後に `spec-dock --project <対象> canonical check --json` を実行し、その終了コードで終わる。
- spec-dock 自身の `.github/workflows/spec-dock-check.yml` と `ci.yml` の変更は、この Issue では行わない（I-10 の切り替えのPRで行う。それまでは、既定のブランチに仕様があり、検査が失敗するため）。

### R-434-05 版のタグ（Epic の `design.md` 8章「版のタグ」）

- spec-dock のリポジトリに `.github/workflows/release-tag.yml` を置く。既定のブランチ（`main`）への push で動き、push の前後（`github.event.before` と `github.sha`）で `pyproject.toml` の版が変わっていて、新しい版が 0.3.0 以上で、タグ `v<版>` がないときだけ、そのコミットにタグを作る。0.2.4 などの過去の版にはタグを作らない。
- 判定は、パッケージを読み込まない1つのスクリプトで行い、ワークフローはその結果に従ってタグを作るだけにする。

## スコープ

### 対象

- `canonical check` の処理（`application/canonical_check.py`）、コミットのツリーの読み取り、CLI の一覧と `--help`、振り分けの表への登録、文字と JSON の出力。
- 新しいコマンドを足したことによる、リポジトリのルートの `README.md` のコマンドの数（44 → 45）。
- 配布資産：`spec-dock/system/spec-dock-version`、`spec-dock/docs/ci/spec-dock-check.yml`、`static-inventory.json` の更新。新しいコマンドを足したことによる `spec-dock/docs/reference_cli.md` と `spec-dock/docs/README.md` のコマンドの数と一覧の行。
- spec-dock のリポジトリの `.github/scripts/specdock-ci-check.sh`、`.github/workflows/release-tag.yml`、版のタグの判定のスクリプト。
- この Issue の受け入れのテストと、新しいコマンドを足したことに伴うコマンドの数と一覧のテストの更新。

### 対象外

- spec-dock 自身の `.github/workflows/spec-dock-check.yml` の追加と、`ci.yml` の変更（I-10）。
- 各リポジトリへの見本の組み込み（I-8 の `cut`、I-10、I-12）。
- 版を 0.3.0 にすること（I-9）、0.4.0 にすること（I-13）。
- 配布資産 `spec-dock/.gitignore` への無視の3行の追加（I-2。契約 C3）。
- 利用者向けの使い方の文書（`spec-dock/docs/canonical.md` など。I-9）。
- 利用側の `spec-dock/`（この repo の dogfooding の workspace）への `installation update`（I-9、I-10）。
- 本物の GitHub Actions での動きの確かめ（I-10）。

### 親契約として維持する境界

- 従来モード（版3）の処理、`.meta.json` を読み書きするコード、版3の振る舞いを確かめるテストを変えない（AC-15）。変えてよいテストは、Epic の `design.md` の testability の「従来モードの回帰」に挙げた区分（コマンドの数と一覧、配布資産の一覧と値、文書の中身）だけで、変えたものは `report.md` に一覧で書く。
- `.github/scripts/specdock-ci-validate.sh` と `ci.yml` を変えない（今のCIを壊さない）。
- 契約 C2（`REPOSITORY_INDEPENDENT_HANDLERS` の形）と C3（無視の3行の値）を変えない。C3 の定数がまだ `main` にないので、この Issue は Epic の `design.md` 3章の値を写して持つ。I-2 と I-7 のうち、後から `main` に入る側が、`origin/main` のマージで C3 の定数に置き換える。
- 読むだけのコマンドは、リポジトリ、`.git`、カタログ、状態の置き場、GitHub に何も書かない。
- 利用者のツールの設定、`~/.local/state/spec-dock/`、本物の GitHub への書き込み、利用者のほかのリポジトリに触れない。

## 失敗・境界条件

- 指定したコミットがない（コミットのないリポジトリ、存在しない名前、コミットでないもの）：調べずに `PRECONDITION_FAILED`（終了コード3）で止まり、次の1手を示す。
- Git のリポジトリの外、`--project` が Git の worktree のルートでない：今のコマンドと同じく止まる。
- `--expect-current` と `--expect-backend`：コミットのツリーの検査では確かめられないので、`PRECONDITION_FAILED` で止まり、次の1手（その引数を外す）を示す（`workspace validate --ci` と同じ扱い）。
- `--dry-run`：受け付け、今の読むだけのコマンドの規則（通るときは `planned` と `can_apply`、`blockers`）に従う。何も書かない。
- 宣言がない、JSON でない、辞書でない、通常のファイルでない（シンボリックリンク、gitlink）、版が3でも4でもない、`writer_protocol` が既知でない：調べること4の失敗の1件として返し、ほかの調べることを続ける。
- 配布資産がない、知らない中身、通常のファイルでない：調べること5の失敗として、資産ごとに1件ずつ返す。`init_only` の資産（`spec-dock/workspace.json`）は、利用者が持つ中身なので、資産の照合をせず、調べること4で確かめる。
- `spec-dock/.gitignore` に無視の3行の一部がない、または `!/initiatives/` が `/initiatives` より前にある（実体のディレクトリの中の新しいファイルを無視してしまう）：調べること5の失敗の1件として返す。
- 版のファイルがない：調べること5の失敗として返し、6の警告は出さない。中身が既知（このパッケージの版か、既知の古い版）で、動いている版と違う：6の警告だけ。中身が知らないもの：5の失敗（前後の空白を除いた版の文字列が動いている版と違えば、6の警告も）。
- 宣言が版4で、`writer_protocol` が古い既知の値（`specdock.writer/v1`）：Epic の「既知である」のとおり通す（宣言の読み取りの `read_workspace_declaration` と同じ範囲）。
- 仕様のパスが数千あっても、すべてを1件ずつ返す（CI で、外すべきパスがすべて分かるようにする）。
- 版のタグの判定：push の前のコミットがない（`0000…`、読めない）、版の文字列が `X.Y.Z` の形でない、版が変わっていない、0.3.0 より小さい、タグがすでにある：どれもタグを作らない。

## 受け入れ条件

Epic の `plan.md` の I-7 の「受け入れ」を、テストで確かめられる形にしたものである。

- **AC-434-01**：一時のリポジトリで、次のそれぞれを含むコミットを `canonical check` が見つけ、パスと次の1手を付けた失敗として返し、終了コード7（`CANONICAL_CHECK_FAILED`）で終わる。
  - 仕様のパス（`spec-dock/initiatives` の下のファイル、`spec-dock/initiatives` のシンボリックリンク、gitlink）。
  - `spec-dock/.canonical` の下のパスと、`spec-dock/.canonical` の gitlink。
  - `spec-dock/` の下の `.meta.json`。
  - 版3の宣言（`CANONICAL_NOT_MIGRATED` で止まらず、失敗の1件として返り、ほかの問題も並ぶ）。
  - 壊れた配布資産（中身を変えたもの、消したもの、シンボリックリンクにしたもの）。
  - 無視の3行の欠け。
- **AC-434-02**：正しいツリー（仕様のパスがなく、版4の宣言と、パッケージの配布資産と、無視の3行を持つ）では、終了コード0で通る。既知の古い版の配布資産は失敗にしない。
- **AC-434-03**：`canonical check` は `REPOSITORY_INDEPENDENT_HANDLERS` に登録され、`resolve_context` を呼ばずに動く。作業ツリーの宣言が版3、版4、ない、壊れているのどれでも、コミットのツリーだけで判定する。
- **AC-434-04**：ネットワークと GitHub のトークンなしで動く（`gh` を `PATH` から外し、`GH_TOKEN` と `GITHUB_TOKEN` をなくし、`XDG_STATE_HOME` を一時ディレクトリにして実行し、状態の置き場にもリポジトリと `.git` にも何も書かないことを確かめる）。
- **AC-434-05**：版のファイルが既知の中身で、動いている SpecDock の版と違うと、警告（次の1手付き）を返し、終了コードを変えない。知らない中身なら、調べること5の失敗にもなる。
- **AC-434-06**：配布資産の版のファイルの中身が `pyproject.toml` の版と同じである（単体テスト）。見本のワークフローが、Epic の `design.md` 8章の手順（版のファイルの版のタグから入れて `canonical check --json` を実行する）を持ち、既定のブランチの名前の行がちょうど1つある。
- **AC-434-07**：`.github/scripts/specdock-ci-check.sh` が、一時のリポジトリで、ソースから作った wheel で `canonical check` を実行し、正しいツリーで終了コード0、仕様のパスを含むツリーで終了コード7を返す。ソースの SHA の食い違い、汚れたソースは、作る前に止まる。対象のリポジトリを変えない。
- **AC-434-08**：版のタグの判定のスクリプトが、版が変わり、0.3.0 以上で、タグがないときだけタグを返し、ほかの場合（今の 0.2.4 のまま、0.2.5 への変更、版が変わらない、タグがある、前のコミットがない）は返さない。`release-tag.yml` は、`main` への push でだけ動き、判定がタグを返したときだけ、そのタグを作って push する手順を持つ（ワークフローの中身で確かめる）。本物の GitHub Actions での動きは、I-9（0.3.0）のマージの後に確かめる（この Issue では未確認）。
- **AC-434-09**：見本のワークフローの手順のコマンドを、見本から取り出して、一時のリポジトリで実行する（結合テスト）。Install の手順は、`pipx` を受けた引数を記録する偽物に置き換え、版のファイルから組み立てた要求（`spec-dock @ git+https://github.com/chemitaro/spec-dock@v<版>`）を確かめる。Check の手順は、手元で作った wheel を入れた環境で実行し、正しいツリーで0、仕様のパスのあるツリーで7になる。実機では、一時の `PIPX_HOME` の `pipx` で、一時のクローンの版のタグから入れる形を確かめる（`report.md`）。本物の GitHub Actions での動きは、この Issue では「未確認」とし、I-10 で確かめる。
- **AC-434-10（AC-15）**：版3の振る舞いを確かめる今のテストが、許された変更のほかは変更なしで通る。`make lint` と `uv run pytest` が通る。

## 制約・前提

- Python 3.10 以上、macOS と Linux。テストは外のネットワークを使わない。
- 層の置き場は `AGENTS.md` に従う（`application/` に検査の手順、`infra/` に Git の読み取り、`presentation/` に出力、`commands/` に振り分けの表）。
- PyPI には出していないので、検査のワークフローは版のタグから入れる（Epic の `design.md` の「設計の判断」）。版のタグは、0.3.0（I-9）のマージの後に初めて作られる。それまでは、見本の手順は版のタグの代わりに手元の wheel で確かめる。
- GitHub の必須の検査（ブランチの保護、ルールセット）は設定しない（R-F3）。
- I-2 の配布資産 `spec-dock/.gitignore` の無視の3行が `main` に入るまで、本物の配布資産だけのツリーは、`canonical check` の調べること5で「無視の3行がない」と失敗する。これは正しい動きで、版4のリポジトリが本物になる I-10 より前に I-2 が入る（Epic の計画の順序）。
