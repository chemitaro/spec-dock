---
種別: 要件定義書（Issue）
ID: "iss-00431"
タイトル: "Read Scopes From GitHub In Canonical Mode"
関連GitHub: ["#431"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00424", "init-00423"]
---

# iss-00431 Read Scopes From GitHub In Canonical Mode — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：canonical モードで、Scope とその周りを読むコマンドを、GitHub の構造のスナップショットとカタログから動かす（Epic の I-4）

## 目的

canonical モードで、Scope とその周りを読むコマンドが、すべて動く。

- 材料：Epic の `plan.md` の「I-4 Read Scopes From GitHub In Canonical Mode」の節（価値、作るもの、受け入れ、I-1 から引き継ぐ直し、I-2 から引き継ぐもの）と、Epic の `design.md` の担当の章（6章と12章の I-4 の行、2章の C10（`ensure_fresh(display)` と着手の判定）、3章の「SpecDock のほかのコマンドから」（`CANONICAL_NOT_LINKED`、`require_linked`））。Issue をまたぐ契約は、Epic の `plan.md` の「Issue をまたぐ契約」の表に従う。
- 依存：I-1（`iss-00428`）、I-2（`iss-00429`）。Planning Level：standard（理由は `plan.md`）。
- この Issue は、契約 C1、C2、C10（I-1）と、C3 の `catalog_tree` と `require_linked`（I-2）を、変えずに使う。新しく、スナップショットからの着手の判定の部品（`domain/canonical_readiness.py`）の持ち主になる。I-5（`work start`）と I-11（ダッシュボード）が使う。
- Epic の文書で決まっていなかった点は、統括の判断（2026-10-26。`plan.md` の「統括の判断」）を正本とする。

## 背景

- I-1 が、宣言の版4による canonical モードの判定、振り分けの表 `CANONICAL_HANDLERS`、GitHub の構造の表し方と構造のスナップショット（`StructureSnapshot`、`ScopeNode`、`ensure_fresh`）を置いた。I-2 が、カタログとリンク（`canonical link`）、状態の表示（`canonical status`）、名前で Scope のディレクトリを探す `CatalogTree`、リンクが正しいことを確かめる `require_linked` を置いた。
- それでも、版4のリポジトリでは、Scope を読むコマンド（`scope show` など）が `CANONICAL_NOT_IMPLEMENTED` で止まる。従来の読む処理は `.meta.json` を読むので、canonical モードでは使えない。
- この Issue は、読むコマンドの構造（題名、状態、親子、依存）を構造のスナップショットから、内容の場所をカタログから求めるようにする。書くコマンド（I-5）と、ダッシュボード（I-11）が使う、着手の判定の部品もここで作る。
- 関係者：
  - 利用者とエージェント：canonical モードで、今と同じコマンドで、GitHub の題名と状態、ディレクトリの場所、スナップショットの取得の時刻が見えること（R-E4）。GitHub につながらなくても、古いスナップショットで示されること。
  - 後の Issue の実装担当：着手の判定の部品と、読む側の部品（Scope の一覧の組み立て、選択の確かめ）を、`design.md` だけで使えること。
  - 移行していないリポジトリ（版3）：今と同じに動くこと（AC-15）。

## 観測可能な要件

### R-431-01 構造はスナップショット、内容はカタログから読む

- canonical モードの読むコマンドは、構造（題名、種類、状態、親子、依存、作業中の印）を、`ensure_fresh(display)` で確かめた構造のスナップショットから読む（C10）。`.meta.json` を読まない。
- 対象のリポジトリは、`origin` のリモートが指す GitHub のリポジトリである（I-1 の `repository_for_checkout`）。
- Scope のディレクトリは、カタログの中で名前で探す（`CatalogTree`）。示す場所は、このチェックアウトのリンクを通した `spec-dock/initiatives/<カタログの中の相対パス>` である。
- 仕様のファイル（ディレクトリ、Artifact、`spec-dock/active/` のリンクの先）を使うコマンドは、最初に `require_linked` で確かめる。リンクやカタログが正しくなければ、自分では直さずに `CANONICAL_NOT_LINKED`（終了コード3、`recovery` に `spec-dock canonical link`）で止まる。マウントしたチェックアウトでは `CANONICAL_FOREIGN_CHECKOUT`、git が古ければ `CANONICAL_GIT_TOO_OLD` で止まる。仕様のファイルを使わないコマンド（`dependency list`、`dependency check`、`branch …`、`worktree …` の `--expect-current`、`installation … --expect-current`）は、リンクを求めない。
- 構造を示すコマンドの JSON は、`data.snapshot` に `fetched_at` と `stale` を持つ（Epic の12章）。
- GitHub につながらないとき、スナップショットがあれば、それで示し、`warnings` に `GITHUB_SNAPSHOT_STALE`（取得の時刻）を入れる。スナップショットがなければ、元の失敗のコード（`GITHUB_UNAVAILABLE`、`GITHUB_RATE_LIMITED`、`GITHUB_ACCESS_DENIED` など）で止まる。
- 共通の `--offline` を付けたときは、GitHub に何も送らず、今のスナップショットで示す（`stale` は真、`GITHUB_SNAPSHOT_STALE` を警告に入れる）。スナップショットがなければ、`PRECONDITION_FAILED`（終了コード3、「offline mode cannot fetch required GitHub state」。今の文と同じ）で止まる。`--source github --offline` は、今と同じく `PRECONDITION_FAILED` で止まる。
- カタログに同じ ID のディレクトリが2つ以上あっても、その Scope の場所を「あいまい」（null）として示し、ほかの読み取りを止めない。そのディレクトリそのものが要るとき（Artifact、`active set`）だけ、`PRECONDITION_FAILED` で止まる。

### R-431-02 Scope の表示（`scope show`、`scope list`）

- 今と同じ選択子（ID、`gh:owner/repo#n`、`@current` などの選択の役）で対象を決める。`--kind`、`--parent`、`--state`、`--expect-current`、`--expect-backend` も今と同じ意味で受け付ける。
- 各 Scope について、ID、種類、GitHub の題名、親の ID、GitHub の参照、Issue の番号と URL、状態（`open`、`completed`、`not-planned`、閉じた理由がそれ以外か無いときの `unknown`）と `state_reason`、作業中の印、ディレクトリの場所（見つからなければ null）を示す。

### R-431-03 依存と着手の判定（`dependency list`、`dependency check`）

- 依存は GitHub の blocked by である。`declared` は対象が宣言した Scope の依存、`effective` は対象と祖先が宣言した Scope の依存である（今の規則）。Scope でない同じリポジトリの Issue への依存は、別の欄に、番号、題名、状態で示す。
- `dependency check` は、着手の判定の部品（R-431-04）の結果を示す。`--source` を付けなければスナップショット（`display`）で判定する。`--source github` は、変わったかの確かめを待たずに全体を取り直してから判定する。明示の `--source local` は `CANONICAL_NOT_APPLICABLE`（終了コード3）で止まる。

### R-431-04 着手の判定の部品（I-5、I-11 が使う）

- スナップショットと Scope の ID から、状態（`READY`、`BLOCKED`、`DOING`、`DONE`、`UNKNOWN`）と、着手できるか（`ready`）と、止めている理由の一覧（ブロッカーの Scope、Scope でない Issue の番号）と、`UNKNOWN` の理由の一覧（異常のコード）を返す。すべての Scope の判定も一度に返せる。
- 規則は今と同じである：対象と祖先が `open`、前提（対象と祖先が宣言した Scope の依存）が `completed`。加えて、Scope でない同じリポジトリの依存は、開いていれば止める（閉じていれば理由を問わず止めない）。
- 対象、祖先に異常（別のリポジトリの親・子・依存、印、種類、親子、依存の異常）があるとき、または依存先がスナップショットにない、もしくは異常のために ID が決まらないときは、`UNKNOWN` にし、`ready` を偽にする。
- 状態の優先は、`DONE`（閉じた。理由を問わない）> `UNKNOWN` > `DOING`（`spec-dock:in-progress`）> `BLOCKED` > `READY` とする。`ready` は `DOING` を見ない。
- 配下からの集計（Epic と Initiative の状態を配下から求めること）は作らない（epic-00427 の範囲）。

### R-431-05 選択（`active show`、`active set`、`active clear`）

- 選択の記録は今と同じ `spec-dock/.agent/work-target/` を読み書きし、記録の形式を変えない。選択の確かめ（Scope の ID と GitHub の参照の一致、祖先の鎖）は、スナップショットの Scope で行う。
- `active show` は、今の選択の表示に加えて、選んだ Scope の場所とスナップショットの取得の時刻を示す。
- `active set` と `active clear` が `spec-dock/active/` に置くリンクの先は、`../initiatives/<カタログの中の相対パス>` である（そのチェックアウトのリンクを通るので、作業用のworktreeでも開く）。選び直しは今と同じく `work start` だけが行う。
- `active set` は、選んだ Scope と、その祖先のすべてのディレクトリがカタログにあることを、リンクを書く前に確かめる。どれかがなければ `LOCAL_TARGET_NOT_FOUND`（終了コード4）で止まり、ぶら下がるリンクを作らない。

### R-431-06 Artifact（`artifact list`、`artifact show`）

- Scope の Artifact を、カタログの中の Scope のディレクトリの `artifacts/` から、実際のパス（リンクをたどらない守った開き方）で読む。示す内容（ID、種類、場所）は今と同じで、場所は、mainのチェックアウトでも作業用のworktreeでも `spec-dock/initiatives/…` である。`@root` は今と同じく `spec-dock/artifacts/` を読む。

### R-431-07 ブランチ（`branch show`、`branch create`、`branch switch`）

- 既定のブランチ名は、`<ID>-<slug>` で、slug は GitHub の本文の印から求める。
- `branch create` と `branch switch` は、今と同じブランチの操作（作成は既存の参照を変えない、切り替えはきれいな作業ツリーで、StartLock の中で、選択の記録を変えない）を行う。従来の基点のコミットの `.meta.json` の照合は行わない。代わりに、対象のコミットのツリーに `spec-dock/initiatives` があれば、書く前に `CANONICAL_BASE_HAS_SPECS`（終了コード3、次の1手「切り替えの後のコミットを基点にする」）で止まる。

### R-431-08 worktree（`worktree list`、`worktree show`、`worktree bootstrap`、`worktree remove`、`worktree create --expect-current`）と `workbench copy`

- `worktree list` と `worktree show` は、今の項目に加えて、カタログのworktreeを「カタログ」と示す。
- `worktree remove` と `worktree bootstrap` は、カタログのworktreeを対象にしたら、何もせずに `CANONICAL_CATALOG_PROTECTED`（終了コード3、次の1手「取り外すなら `spec-dock canonical remove`」）で止まる（カタログの中で `make init` を動かさない）。
- `--expect-current` は、どのコマンドでも、スナップショットの Scope で選択を確かめる。`worktree create --expect-current` と、版4の `installation show`、`update`、`uninstall` の `--expect-current` も、`CANONICAL_NOT_IMPLEMENTED` ではなく、この確かめを行ってから今の処理をする。
- `workbench copy` は `CANONICAL_WORKBENCH_SHARED`（終了コード3）で止まり、どのworktreeからも同じカタログの `.workbench` が見えるので写す必要がない、と示す。

### R-431-09 workspace（`workspace sync`、`workspace validate`、`workspace doctor`）

- `workspace sync` は、構造をスナップショットから読み、同じクローンのworktree（カタログのworktreeを除く）の選択を観察する。`--source github` は全体を取り直す。明示の `--source local` は `CANONICAL_NOT_APPLICABLE` で止まる。ダッシュボードは作らない。宣言が版3のworktree（移行前のブランチ）も、選択の記録の形式は同じなので、同じように観察する。観察できないworktreeは、今と同じく `WORKTREE_SELECTION_UNAVAILABLE` の行にする。`--allow-invalid` は、今と同じく受け付けるだけで、結果を変えない。
- `workspace validate` は、Epic の6章の検査をすべて行う：種類と階層の規則、本文の印と slug、ID の重複、依存の循環、Scope のディレクトリがちょうど1つあること、入れ子と GitHub の親子のずれ（警告。次の1手は `spec-dock scope move <ID>`）、Issue のないディレクトリ、必要な文書（`requirement.md`、`design.md`、`plan.md`、`report.md`）、`.meta.json` がないこと、別名ファイル（警告）、Scope でない Issue への依存（警告）。誤りは `findings`（終了コード7）、警告は `warnings` に入れる。`--ci` は `CANONICAL_NOT_APPLICABLE` で止まり、`spec-dock canonical check` を案内する。
- `workspace doctor` は、今の項目（構造の誤り、選択の確かめ、GitHub の確かめ）と、`canonical status` と同じ項目を示す。診断なので、リンクを求めない。リンクやカタログが正しくないときは、カタログを使う検査を行わず、`CANONICAL_NOT_LINKED` を `findings` に入れ、`canonical status` の項目で示す。

### R-431-10 `canonical status` の `structure` と `--structure`（I-2 から引き継ぐもの）

- `canonical status` に `--structure` を足す。付けたときだけ、`display` の新しさでスナップショットを確かめ、`structure` の項目に、入れ子と GitHub の親子のずれ（Scope ごとに、今の場所、期待する場所、次の1手 `spec-dock scope move <ID>`）と、スナップショットの取得の時刻を示す。付けないときは、GitHub に問い合わせず、項目を `{"status": "not_checked", "next_step": null}` にする。付けたときの項目は、`status`（`ok` か `problem`）、`next_step`、`snapshot`（`fetched_at`、`stale`、`repository`）、`misplaced`（`scope_id`、`path`、`expected`、`next_step` の一覧）を持つ。確かめられなかったとき（リンクがない、GitHub につながらずスナップショットもない）は、`status` を `unavailable` にし、`code` と `next_step` を示す。
- 問題があっても、`canonical status` の結果は今と同じく `succeeded` で、問題を `warnings` と項目に示す。

### R-431-11 読むだけ

- 読むだけのコマンド（`scope show`、`scope list`、`dependency list`、`dependency check`、`active show`、`artifact list`、`artifact show`、`branch show`、`worktree list`、`worktree show`、`workspace sync`、`workspace validate`、`workspace doctor`、`canonical status`）は、リポジトリ、カタログ、`.git`、GitHub に何も書かない。書いてよいのは、状態の置き場の `snapshot.json` と `probe.json` だけである。

### R-431-12 I-1 から引き継ぐ直し

- `application/canonical_errors.github_error_result` と、`runtime_dispatch` の `except GithubStructureError` のテストを足す（`partial` の終了コード6、`failed` の5、`retry_at` の文）。
- `infra/github_structure.py` の GraphQL のレート制限で、待ち時間0を60秒にしないように直す（`is None` で比べる）。
- `tests/unit/infra/test_github_snapshot.py` の、2つ目のファイルの書き込みの失敗のテストを、`commit_refresh` で `probe.json` の書き込みを失敗させる形に直す。

## スコープ

- 対象：上の要件の、canonical モードのコマンドの処理、着手の判定の部品、`--source` の既定の扱い、`canonical status --structure`、I-1 から引き継ぐ直し、それらのテスト。
- 対象外：
  - 書くコマンド（`scope create` など、`dependency add`、`artifact create`、`work start`、`work finish`、`scope move`）と、書き込みの反映（I-5）。
  - 配下からの状態の集計、ダッシュボード（I-11、epic-00427）。
  - `canonical status` の `sync`、`snapshot`、`dashboard` の項目（I-3、I-11）。
  - 利用者の文書と `help` の文書の更新（I-9）。配布資産は変えない。
- 親契約として維持する境界：
  - C1、C2、C3、C10 の公開の形を変えない。
  - 従来モードの処理、`.meta.json` の読み書きのコード、版3の振る舞いのテストを変えない（AC-15）。従来の部品は、変えずに呼ぶ。
  - 選択の記録の形式と StartLock を変えない。

## 失敗・境界条件

| 場面 | 振る舞い |
|---|---|
| リンクやカタログがない、正しくない（仕様のファイルを使うコマンド） | `CANONICAL_NOT_LINKED`（3）。書かない |
| GitHub につながらない、スナップショットあり | 古いスナップショットで示し、`GITHUB_SNAPSHOT_STALE` の警告 |
| GitHub につながらない、スナップショットなし | `GITHUB_UNAVAILABLE`（5）など、元の失敗のコード |
| `--source github` で取り直しに失敗 | 元の失敗のコードで止まる（`decision` と同じ） |
| 対象の Scope がスナップショットにない | `SCOPE_NOT_FOUND`（4） |
| Scope のディレクトリが2つ | 名前で探す部品の `ScopeDirectoryAmbiguous` を `PRECONDITION_FAILED`（3）。`workspace validate` は誤りとして示す |
| Scope のディレクトリがない | 表示は場所を null にする。Artifact と `active set` は `LOCAL_TARGET_NOT_FOUND`（4）。`workspace validate` は誤り |
| 明示の `--source local`、`workspace validate --ci` | `CANONICAL_NOT_APPLICABLE`（3） |
| `worktree remove` の対象がカタログ | `CANONICAL_CATALOG_PROTECTED`（3）。書かない |
| `workbench copy` | `CANONICAL_WORKBENCH_SHARED`（3） |
| `branch create` / `switch` の対象のコミットに `spec-dock/initiatives` | `CANONICAL_BASE_HAS_SPECS`（3）。書かない |
| 異常のある Scope、別のリポジトリの依存、スナップショットにない依存先 | 着手の判定は `UNKNOWN`、`ready` は偽 |

## 受け入れ条件

テストは、外のネットワークを使わない（偽の `gh`、一時ディレクトリの bare のリポジトリ、`XDG_STATE_HOME` を一時ディレクトリに）。

- **AC-431-01**（R-E4）：偽の `gh` と一時のカタログで、`scope show` と `scope list` が、GitHub の題名と状態、ディレクトリの場所（`spec-dock/initiatives/…`）、`data.snapshot.fetched_at` を示す。題名を GitHub で変えた後の取り直しで、表示が新しい題名になる。
- **AC-431-02**（AC-16 の一部）：構造が変わっていないとき、`scope show` と `scope list` を続けて実行しても、偽の `gh` の記録に、条件付きの確かめ（304）のほかの要求がない（GraphQL の全体の読み取りがない）。
- **AC-431-03**：GitHub につながらないとき、スナップショットがあれば `succeeded` で示し、`warnings` に `GITHUB_SNAPSHOT_STALE` と取得の時刻が入る。スナップショットがなければ `GITHUB_UNAVAILABLE`（終了コード5）で止まる。`--offline` では、偽の `gh` に要求を送らずにスナップショットで示し、なければ `PRECONDITION_FAILED` で止まる。カタログに同じ ID のディレクトリが2つあっても、`scope list` は止まらず、その Scope の `path` を null にする。
- **AC-431-04**：リンクのないチェックアウトで、仕様のファイルを使うコマンド（`scope show` など）が `CANONICAL_NOT_LINKED`（終了コード3、`recovery` に `spec-dock canonical link`）で止まる。
- **AC-431-05**：`dependency list` が blocked by から `declared` と `effective` と Scope でない依存を示し、`dependency check` が着手の判定を示す。`--source github` は全体を取り直す（GraphQL の要求が1回以上ある）。明示の `--source local` は `CANONICAL_NOT_APPLICABLE`。`--source github --offline` は `PRECONDITION_FAILED`。
- **AC-431-06**（着手の判定の部品）：スナップショットだけを入力にした単体のテストで、`READY`、`BLOCKED`（開いた Scope の前提、閉じた祖先、開いた Scope でない依存）、`DOING`、`DONE`（`completed` と `not_planned`）、`UNKNOWN`（別のリポジトリの親・子・依存、印の異常、スナップショットにない依存先）が、それぞれ決まる。結果に、ブロッカーの一覧と `UNKNOWN` の理由の一覧が入る。閉じた Scope でない依存（理由を問わない）は止めない。前提の Scope の `not_planned` は止める。
- **AC-431-07**：作業用のworktreeで、選択がある状態の `active set` の後の `spec-dock/active/` のリンクが、`../initiatives/…` を指し、その Scope のディレクトリを開く。`active clear` の後は、今と同じ `system/active-none/<役>` を指す。`active show` が、選んだ Scope の場所と取得の時刻を示す。祖先のディレクトリがないときの `active set` は `LOCAL_TARGET_NOT_FOUND` で止まり、リンクを変えない。選択の記録は、canonical の `work start` が I-5 まで使えないので、テストの部品が `WorkTargetStore` で直接書く。
- **AC-431-08**：`artifact list` と `artifact show` が、カタログの Scope のディレクトリの Artifact を、mainのチェックアウトと作業用のworktreeの両方で、`spec-dock/initiatives/…` の場所で示す。
- **AC-431-09**：`branch show` の既定の名前が `<ID>-<slug>`（slug は GitHub の印）である。`branch create` と `branch switch` が今と同じ操作を行い、対象のコミットのツリーに `spec-dock/initiatives` があれば `CANONICAL_BASE_HAS_SPECS` で止まり、参照と HEAD を変えない。
- **AC-431-10**：`worktree list` と `worktree show` がカタログのworktreeを示す。`worktree remove` と `worktree bootstrap` がカタログを対象にすると `CANONICAL_CATALOG_PROTECTED` で止まり、カタログとその登録が残る。`workbench copy` が `CANONICAL_WORKBENCH_SHARED` で止まる。`worktree create --expect-current` と、版4の `installation show --expect-current` が、選択の一致で通り、不一致で `PRECONDITION_FAILED` になる。
- **AC-431-11**：`workspace validate` が、6章の検査の項目をすべて見つける（項目ごとに作った異常で確かめる）。入れ子のずれは警告で、`details.next_step` が `spec-dock scope move <ID>` である。誤りがなければ `valid: true`。`--ci` は `CANONICAL_NOT_APPLICABLE` で止まり、`spec-dock canonical check` を示す。
- **AC-431-12**：`workspace sync` が、スナップショットの Scope の状態と、各worktreeの選択を示し、カタログのworktreeを観察の行に入れない。`--source github` は取り直す。明示の `--source local` は止まる。`workspace doctor` が `canonical status` と同じ項目を示し、リンクのないチェックアウトでも止まらずに `CANONICAL_NOT_LINKED` を `findings` に示す。
- **AC-431-13**：`canonical status --structure` が、入れ子のずれを `structure` の項目と `warnings`（`details.next_step` に `spec-dock scope move <ID>`）に示す。`--structure` を付けないときは、偽の `gh` に要求を送らず、項目が `not_checked` である。
- **AC-431-14**（R-431-11）：読むだけのコマンドの実行の前後で、カタログと `.git`（`tree_digest`）と、チェックアウトの `git status` が変わらず、偽の `gh` に書き込みの要求がない。
- **AC-431-15**（AC-15）：版3の振る舞いを確かめる今のテストが、Epic の `design.md` の testability の「従来モードの回帰」で許された変更のほかは、変更なしで通る。`--source` の既定の変更の後も、版3の `dependency check` と `workspace sync` の値、`--help` の文、JSON の出力が変わらないことをテストで確かめる。I-1 と I-2 の canonical のテストのうち、この Issue のコマンドが `CANONICAL_NOT_IMPLEMENTED` になることを確かめていたものは、版3のテストではなく canonical のテストとして直し、`report.md` に一覧で書く。
- **AC-431-16**（R-431-12）：I-1 から引き継ぐ3つの直しに、それぞれテストがある（`github_error_result` と dispatch の `partial` の6、`failed` の5、`retry_at`。待ち時間0の GraphQL のレート制限で60秒待たない。`probe.json` の書き込みの失敗で、メモリーの値、`persisted=False`、`local_writes` が1回だけ）。
- **AC-431-17**：`make lint` と `uv run pytest` が通る。

## 制約・前提

- Epic の目的、Issue の分け方、Issue をまたぐ契約（C1〜C11）を変えない。
- 従来モード（宣言の版3）の処理、`.meta.json` の読み書きのコード、版3の振る舞いを確かめるテストを変えない（AC-15）。変えてよいテストは、Epic の `design.md` の testability の「従来モードの回帰」に挙げたものだけで、変えたものは `report.md` に一覧で書く。
- 本物の GitHub に、ラベル、sub-issue、依存、`spec-dock/canonical` ブランチを作らない。本物の spec-dock のリポジトリで canonical のコマンドを実行しない。利用者の状態の置き場（`~/.local/state/spec-dock/`）とツールの設定を変えない。
- 並行の I-3（`iss-00430`）と I-8（`iss-00435`）と、`cli/catalog.py`、`commands/canonical_dispatch.py`、`application/canonical_status.py`、コマンドの一覧のテストで衝突しうる。先に `main` に入った方を、`origin/main` のマージで取り込む。
