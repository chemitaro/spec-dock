---
種別: 要件定義書（Issue）
ID: "iss-00428"
タイトル: "Add Canonical Mode And GitHub Structure Snapshot"
関連GitHub: ["#428"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00424", "init-00423"]
---

# iss-00428 Add Canonical Mode And GitHub Structure Snapshot — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

表示名：canonical モードの判定と、GitHub の構造のスナップショットを足す（Epic の I-1）

## 目的

canonical モードの土台になる、モードの判定と、GitHub の構造の読み書きができる。構造は一括で取得して使い回し、GitHub に負荷をかけない。利用者から見える変化はまだない（版3のリポジトリで目に見える違いは、`installation show` が宣言を `known-old` と示す1点だけ。統括の判断 C、2026-10-26）。

- 材料：Epic の `plan.md` の「I-1 Add Canonical Mode And GitHub Structure Snapshot」の節と、Epic の `design.md` の1章、2章（構造のスナップショットを含む）、6章の I-1 の行。Issue をまたぐ契約は、Epic の `plan.md` の「Issue をまたぐ契約」の表に従う。
- 依存：なし。Planning Level：strict（理由は `plan.md`）。
- この Issue は、契約 C1（構造の表し方、`StructureSnapshot`、`ScopeNode`、GitHub の呼び出しの部品）、C2（宣言の版4とモードの判定、`dispatch()` の振り分けの入口）、C10（構造のスナップショット）の持ち主である。後の Issue（I-2〜I-11、次の Epic epic-00425）は、ここで作る部品を変えずに使う。

## 背景

- Epic は、仕様の構造の正本を GitHub Issue に移し、構造を一括で取得して使い回す（Epic の R-A2、R-I1〜R-I6）。移行の間、SpecDock 0.3.0 は、宣言の版3のリポジトリを今のまま（従来モード）、版4のリポジトリを canonical モードで扱う（R-A5、R-A6）。
- 今のコードは、宣言の版が整数の3でなければ止まる（`application/project_context.py` の `read_workspace_declaration`）。GitHub は `infra/github_lifecycle.py` の `GithubIssueGateway` が、取得、作成、状態の変更だけを、再試行なしで扱う。構造は、コマンドのたびに `.meta.json` から読み、保存して使い回すことはしない。
- 後の Issue は、モードの振り分けの入口、構造の表し方、GitHub の呼び出しの部品、構造のスナップショットがないと始められない。この Issue は、それらを、利用者の動きを変えずに足す。
- 関係者：
  - 利用者：移行していないリポジトリ（版3）で、今と同じに動くこと（AC-15）。
  - 後の Issue の実装担当：ここで決めた部品の公開の形（モジュール、関数、型、エラーのコード）を、`design.md` だけで使えること。
  - 次の Epic（epic-00425）：`snapshot.json` の版1の形式を読む。

## 観測可能な要件

### R-428-01 モードの判定（契約 C2）

- 宣言 `spec-dock/workspace.json` の `schema_version` が整数の3なら従来モード、整数の4なら canonical モードと判定する。それ以外（5 などの整数、真偽値、文字列、ない）は、今と同じく `PRECONDITION_FAILED`（終了コード3）で止まる。
- `writer_protocol` の扱いは今と同じ（既知の2つの値だけを受け付け、書き込みには `specdock.worktree-writer/v1` を求める）で、版3と版4の両方に当てる。

### R-428-02 振り分けの入口（契約 C2）

- `dispatch()` は、`resolve_context` の前に呼ぶ振り分けの表を持つ。リポジトリによらないコマンド（I-3 の `canonical sync --registered`）と、宣言を自分で調べるコマンド（I-7 の `canonical check`）を、後の Issue がここに登録する。この Issue では、登録するコマンドはない。
- `dispatch()` は、宣言の版で、従来の処理か canonical の処理を選ぶ。振り分けは `dispatch()` の1か所に集める。
- canonical モードで、canonical の処理をまだ持たないコマンドは、何も書かずに `CANONICAL_NOT_IMPLEMENTED`（終了コード3）で止まり、`recovery` に「SpecDock 0.3.0 を待つ」を入れる。
- canonical モードの `workspace migrate` は、何も書かずに `CANONICAL_NOT_APPLICABLE`（終了コード3）で止まる。宣言を書き換えない。
- `canonical` グループのコマンドは、版3のリポジトリでは `CANONICAL_NOT_MIGRATED`（終了コード3）で止まる。この規則は入口として作る（コマンドそのものは I-2 以降が足す）。

### R-428-03 配布資産と `installation`

- 配布資産 `spec-dock/workspace.json` を版4にする。`installation init` は版4の宣言を置き、次の1手として `spec-dock canonical link` を示す。
- `installation show`、`installation update`、`installation uninstall` は、版3と版4の両方の宣言を受け付け、今と同じに動く。版3のリポジトリの `installation show` は、配布資産の宣言が版4になったので、宣言を `known-old` と示す（`init_only` なので `update` は宣言を書き換えない）。ただし、版4で `--expect-current` を付けた組み合わせは、選択と Scope の解決が canonical の部品を要るので、この Issue では `CANONICAL_NOT_IMPLEMENTED` で止まる（canonical の処理は I-4。統括の判断、2026-10-26）。

### R-428-04 構造の表し方（契約 C1）

- 種類はラベル `spec-dock:initiative`、`spec-dock:epic`、`spec-dock:issue` のちょうど1つで表す。作業中の印はラベル `spec-dock:in-progress` である。ラベルの色と説明は固定の値を持つ。
- slug は、本文の `<!-- spec-dock:slug=<slug> -->` だけの行で表す。本文を `\r?\n` で行に分け、行末の空白を除いて数え、本文のどこにあってもちょうど1つでなければならない。作るときは、本文の末尾に置く。
- ID は、種類の接頭辞（`init-`、`epic-`、`iss-`）に、5桁にそろえた Issue の番号を付けたもの（今の `domain/ids.py` の `format_id`）である。
- 親子は sub-issue、依存は blocked by で表す。Initiative には親がなく、Epic の親は Initiative、Issue の親は Epic である。

### R-428-05 全体の読み取り

- GitHub のリポジトリごとに、種類のラベルを持つ Issue（開いたものも閉じたものも）の構造（番号、Issue の id、種類、題名、状態、ラベル、担当者、slug、親子、依存）を、GraphQL で一括して読む。3つの種類のラベルは1回の問い合わせでまとめて指定し、ページ送りで最後まで読む。子と依存が100を超える Issue だけ、REST で残りを読む。
- 読んだ結果から、構造のスナップショットを作る。規則の違反（種類のラベルが2つ以上、印がない、印が2つ以上、slug が規則に合わない、親の種類が規則に合わない、循環など）は、その Issue を異常として返す。Scope でない同じリポジトリの Issue への依存は `external` に入れる。
- 親、子、依存先が別のリポジトリの Issue のときは、番号で取り違えないよう、スナップショットのどの関係（`parent`、`sub_issues`、`blocked_by`、`blocking`、`external`）にも入れず、異常として記録する（統括の判断、2026-10-26）。

### R-428-06 変わったかの確かめ

- 種類のラベルごとの一覧に、前に記録した `ETag` を付けた条件付きの要求を送る（3回）。304 は、`gh` の終了コードではなく、状態行で判定する。
- 304 のときは全体を取り直さず、主のレート制限を消費する要求を送らない。

### R-428-07 一部の読み取りと書き込み（REST）

- Epic の `design.md` 2章の表の操作（Issue、親、子、依存、ラベル、自分のログイン名の読み取りと、Issue の作成、題名と状態の変更、親子、依存、ラベル、担当者の書き込み）を、型の付いた関数として提供する。
- `sub_issue_id` と `issue_id` には、Issue の番号ではなく、Issue の id（数値）を送る。
- 親の取得の404は「親なし」、ラベルの取得の404は「ラベルなし」という正常な答えとして扱う。
- レート制限（403 か 429 で、`retry-after`、`x-ratelimit-remaining: 0`、または本文の「rate limit」）では、読み取りは待って3回まで再試行し、書き込みは再試行せずに `GITHUB_RATE_LIMITED` で止まる。500番台の読み取りは、1秒、2秒、4秒の間をおいて3回まで再試行する。
- 要求は1つずつ順に送る。1つのコマンドの中で書き込みを続けるときは、書き込みの間を1秒以上あける。時刻と待ちは注入できる。
- 結果が分からない書き込みは、読み直して確かめ、それでも分からなければ、結果が不明であること（終了コード6の材料）を返す。

### R-428-08 構造のスナップショット（契約 C10）

- 置き場は `<状態の置き場>/github/<ホスト>/<owner>/<repo>/` で、`snapshot.json`（版1）と `probe.json`（版1）を置く。状態の置き場は `${XDG_STATE_HOME:-$HOME/.local/state}/spec-dock/` である。明示の値（I-3 の `--state-root`）を渡せば、それを使う（根の求め方の持ち主は I-1。統括の判断 A6）。
- 書くときは、ディレクトリへの `flock` の中で、一時ファイルに書いてから `rename` する。読むときは排他を取らない。GitHub との通信は排他の外で行う。
- `ensure_fresh(level)` は、3つの新しさの段階（`display`、`decision`、`cycle`）で、確かめと取り直しを、Epic の `design.md` 2章の表のとおりに決める。
- 新しい `ETag` は、全体の取り直しが成功したときだけ記録する。
- SpecDock のコマンドが GitHub に書いた結果は、すぐにスナップショットに反映し、`local_writes` に記録する。全体の取り直しを書き込むときは、取り直しを始めた時刻より後の書き込みの反映を消さない。
- 状態の置き場に書けないときは、スナップショットをそのプロセスのメモリーの上だけで持ち、失敗しない。
- `decision` では、判断に使う Issue を GitHub から読み直し、違っていれば読み直した値をスナップショットに反映する。

### R-428-09 テストの共通の部品

- 偽の GitHub（`gh` の実行器と、`PATH` に置く `gh` の実行ファイル）が、GraphQL の問い合わせ（複数のラベルの OR）、ページ送り、sub-issue、blocked by、ラベル、担当者、条件付きの要求と 304、レート制限の応答、500番台の応答を返し、受けた要求を記録する。後の Issue が、同じ部品を使う。

## スコープ

### 対象

- `application/project_context.py` の宣言の読み取りとモードの判定。
- `commands/runtime_dispatch.py` のモードの振り分けと、リポジトリによらないコマンドの振り分けの入口。canonical モードの振り分けの表と、`workspace migrate` の拒否。
- `installation` の版4の扱いと、配布資産 `spec-dock/workspace.json` の版4（`static-inventory.json` の値を含む）。
- `domain/canonical_structure.py`、`infra/github_structure.py`、`infra/github_snapshot.py`、状態の置き場の根を求める部品。
- テストの共通の部品（偽の GitHub）と、この Issue の受け入れのテスト。

### 対象外

- `canonical` グループのコマンド（I-2 以降）。カタログとリンク（I-2）。定期の同期と登録簿、`state.json`（I-3）。
- Scope を読むコマンドと書くコマンドの canonical の処理（I-4、I-5）。日本語の題名（I-6）。ダッシュボード（I-11）。
- 利用者向けの文書と規則の節（I-9）。
- spec-dock の利用側の配布資産の更新（I-9 が `installation update` で行う）。

### 親契約として維持する境界

- 従来モード（版3）の処理と、`.meta.json` を読み書きするコードを変えない。版3の振る舞いを確かめるテストは、Epic の `design.md` の testability の「従来モードの回帰」に挙げたものと、統括の判断（2026-10-26。`installation init` が版4を書くことに伴い、init で作った作り物に従来のコマンドを当てるテストは、init の直後に宣言を版3に戻す。確かめる中身は変えない）のほかは変えない（AC-15）。対象の4件は `design.md` の testability に挙げる。
- 読むだけのコマンドが書いてよいのは、状態の置き場の `snapshot.json` と `probe.json` だけである（Epic の `design.md` 2章）。
- 利用者のツールの設定、`~/.local/state/spec-dock/`、本物の GitHub への書き込み、利用者のほかのリポジトリに触れない。

## 失敗・境界条件

- 宣言が版5、真偽値、文字列、壊れている、ない：今と同じく止まる（版3の扱いも変えない）。
- `workspace validate --ci` と `workspace doctor --raw`：今は作業ツリーの宣言を `resolve_context` で確かめない（`--ci` は HEAD のコミットの宣言を読み、`--raw` は壊れた宣言や知らない版でも診断する）。作業ツリーの宣言が版4と読めるときだけ canonical の処理へ送り、それ以外（版3、壊れた宣言、ない）は今と同じ従来の処理へ送る。
- GitHub につながらない（`gh` がない、時間切れ、500番台が続く）：`display` は今のスナップショットで続けて `GITHUB_SNAPSHOT_STALE` を警告に入れ、スナップショットがなければ `GITHUB_UNAVAILABLE` で止まる。`decision` は書く前に止まる。`cycle` は記録だけを残して止まらない。
- 取り直しの途中で失敗した：`ETag` を進めない。次の確かめは「変化あり」になる。
- レート制限：読み取りは60秒までの待ちで3回まで再試行し、60秒より長い待ちが要るときは待たずに `GITHUB_RATE_LIMITED` で止まる。書き込みはすぐに `GITHUB_RATE_LIMITED` で止まる。
- 結果が分からない書き込み：読み直して確かめ、分からなければ結果が不明として返す（Issue の作成では、作った Issue を特定できないことを返す）。
- 状態の置き場に書けない（サンドボックスの中など）、排他が取れない、ファイルが壊れている、版が違う：書けないときはメモリーの上で続け、読めないときは「ない」として取り直す。どれも失敗にしない。
- 取り直しの途中に、同じリポジトリへの書き込みの反映があった：反映を消さない。
- GraphQL の応答の `errors`、想定と違う形の応答：レート制限なら上の扱い、それ以外は失敗として返し、スナップショットを書かない。

## 受け入れ条件

Epic の `plan.md` の I-1 の「受け入れ」を、テストで確かめられる形にしたものである。

- **AC-428-01（AC-15）**：版3の宣言では、すべてのコマンドが今と同じに動く。版3の振る舞いを確かめる今のテストが、許された変更（`design.md` の testability の4件を含む）のほかは変更なしで通る。
- **AC-428-02**：版4の宣言を読むと canonical モードと判定し、canonical の処理を持たないコマンド（`workspace validate --ci` と `workspace doctor --raw` を含む）は `CANONICAL_NOT_IMPLEMENTED`（終了コード3、`recovery` あり）で、何も書かずに止まる。版5、真偽値、文字列の版と、知らない `writer_protocol` の版4は、今と同じく `PRECONDITION_FAILED` で止まる。
- **AC-428-03**：版4の `workspace migrate` は `CANONICAL_NOT_APPLICABLE`（終了コード3）で止まり、宣言のバイト列を変えない。
- **AC-428-04**：`canonical` で始まるコマンドの経路を版3の宣言で通すと `CANONICAL_NOT_MIGRATED` で止まり、リポジトリによらないコマンドの入口は `resolve_context` より前に呼ばれる（振り分けの単体テスト）。
- **AC-428-05**：`installation init` が版4の宣言を置き、警告に次の1手 `spec-dock canonical link` を示す。`installation show`、`update`、`uninstall` が版4の宣言で動く（`update` は `--dry-run` と適用、`uninstall` は適用）。古い `writer_protocol` の版4では、`update` が今と同じく止まる。版4で `--expect-current` を付けると `CANONICAL_NOT_IMPLEMENTED` で止まる。
- **AC-428-06**：偽の GitHub の上で、全体の取り直しが、ラベル、親子、依存、印から正しいスナップショットを作る。規則の違反（種類のラベルが2つ、印がない、印が2つ、Epic の親が Issue、循環）を異常として返す。Scope でない依存先は `external` に入る。別のリポジトリの親、子、依存先は、どの関係にも入らず異常になる。本文の印は `\r\n` の本文と、本文の途中の印でも読める。
- **AC-428-07**：`ensure_fresh` が、Epic の `design.md` 2章の表のとおりに、確かめと取り直しを決める。時刻を注入して、60秒、5分、30分の境の前後を確かめる。
- **AC-428-08**：304 のときは取り直さず、主のレート制限を消費する要求（GraphQL と、304 以外の応答の要求）を送らない（偽の GitHub の要求の記録で確かめる）。取り直しに失敗したときは `ETag` を進めない。
- **AC-428-09**：取り直しの途中に書き込みの反映があっても、その反映が消えない。状態の置き場に書けないとき、メモリーの上で動き、失敗しない。
- **AC-428-10**：`sub_issue_id` と `issue_id` に、番号ではなく Issue の id（数値）を送る（偽の GitHub が受けた本文で確かめる）。
- **AC-428-11**：親の取得の404を「親なし」、ラベルの取得の404を「ラベルなし」として扱う。403 と `retry-after` の応答で、読み取りは待って再試行し、書き込みは `GITHUB_RATE_LIMITED` で止まる。1つのコマンドの中の書き込みの間が1秒以上ある（注入した時計で確かめる）。
- **AC-428-12**：`make lint` と `uv run pytest` が通る。
- **AC-428-13**：結果が分からない書き込みは、読み直して確かめ、効果が見えれば成功として返し、見えなければ `GITHUB_EFFECT_UNKNOWN`（終了コード6の材料）を返す。Issue の作成は `GITHUB_CREATE_IDENTITY_UNKNOWN`（終了コード6の材料）を返す。
- **AC-428-14**：500番台の読み取りは1秒、2秒、4秒の間をおいて3回まで再試行し、続けば `GITHUB_UNAVAILABLE`。要る待ちが60秒を超えるレート制限は、待たずに `GITHUB_RATE_LIMITED`（再試行してよい時刻付き）。GraphQL の `errors` は、レート制限なら待って再試行し、それ以外は失敗として返し、スナップショットを書かない。
- **AC-428-15**：全体の読み取りが、ページ送りで最後まで読み、関係（100を超える）とラベル（20を超える）を REST で1つずつ補う。壊れた、または版の違う `snapshot.json` は取り直す。並んで走った古い取り直しは、新しいものを上書きしない。メモリーとファイルが同じ時刻なら、メモリーの反映が使われる。
- **AC-428-16（統括の判断 C）**：変更の前と後で、版3のリポジトリの `workspace validate`、`workspace validate --ci`、`workspace doctor`、`installation update`（宣言を書き換えない）の結果が同じである。spec-dock 自身の CI の手順 `.github/scripts/specdock-ci-validate.sh <worktree> <worktree> <HEAD>` が、最終の品質の関門の SHA で通る。

## 制約・前提

- Python 3.10 以上、macOS と Linux。テストは外のネットワークを使わない（GitHub は偽の `gh`、状態の置き場は `XDG_STATE_HOME` を一時ディレクトリに）。
- GitHub の二次のレート制限（Epic の `requirement.md` の制約・前提）に従う。304 は主のレート制限に数えない（調査の記録）。
- 層の置き場は `AGENTS.md` に従う（`domain/` は純粋な規則、`infra/` は GitHub とファイル、`application/` と `commands/` は振り分け）。
- 宣言の版4の canonical モードは、この Issue の後も 0.3.0（I-9）までは使えない。この間に `installation init` で作ったリポジトリは、ほとんどのコマンドが `CANONICAL_NOT_IMPLEMENTED` で止まる（Epic の計画のとおり）。
