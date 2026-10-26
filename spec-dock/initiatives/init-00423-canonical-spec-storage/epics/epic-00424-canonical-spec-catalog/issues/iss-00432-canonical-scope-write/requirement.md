---
種別: 要件定義書（Issue）
ID: "iss-00432"
タイトル: "Write Scopes To GitHub In Canonical Mode"
関連GitHub: ["#432"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00424", "init-00423"]
---

# iss-00432 Write Scopes To GitHub In Canonical Mode — 要件定義

詳細: [Requirement Guide](../../../../../../docs/authoring/requirement.md)

表示名：canonical モードで、Scope を書くコマンドを、GitHub の構造とカタログに書くようにする（Epic の I-5）

## 目的

canonical モードで、Scope の作成、取り込み、題名の変更、親の変更、完了、削除、依存の変更、Artifact の作成、作業の開始と終了ができる。

- 材料：Epic の `plan.md` の「I-5 Write Scopes To GitHub In Canonical Mode」の節（価値、作るもの、受け入れ、I-4 から引き継ぐもの）と、Epic の `design.md` の担当の章（6章と12章の I-5 の行、2章の GitHub の構造の「書く」表と C10 の書き込みの反映と `decision` の新しさ、3章の「SpecDock のほかのコマンドから」（`link_after_command`）、4章（排他と変更の束を書く側）、5章の「`work finish` での保存の確認」）。Issue をまたぐ契約は、Epic の `plan.md` の「Issue をまたぐ契約」の表に従う。
- 依存：I-3（`iss-00430`）、I-4（`iss-00431`）。どちらも `main` にある。Planning Level：strict（理由は `plan.md`）。
- この Issue は、C1、C10（I-1）、C3、C4、C6（I-2）、C9 とすぐの実行の頼み方（I-3）、着手の判定の部品と読む側の部品（I-4）を、変えずに使う。Epic の文書が I-5 に任せた2つの追加（C1 の `update_issue` の `body` と読み直しの `state_reason`、C10 の反映できない変更の扱い）だけを行う。
- Epic の文書で決まっていなかった点は、統括の判断（2026-10-26。`plan.md` の「統括の判断」）を正本とする。

## 背景

- I-1 が GitHub の構造の表し方と構造のスナップショット（`ensure_fresh`、書き込みの反映 `reflect`）と、GitHub の呼び出しの部品（`GithubStructureClient`。書き込みの間の1秒、結果が分からない書き込みの読み直し）を置いた。I-2 がカタログとリンク、カタログの排他と変更の束（`catalog_changes`）、`link_after_command` を、I-3 が定期の同期と状態の置き場（`state.json`、`request_sync_now`）を、I-4 が読むコマンドと着手の判定の部品（`evaluate_readiness`）を置いた。
- それでも、版4のリポジトリでは、書くコマンド（`scope create` など16個）が `CANONICAL_NOT_IMPLEMENTED` で止まる。従来の書く処理は `.meta.json` を書くので、canonical モードでは使えない。
- この Issue は、構造の変更を GitHub に、内容の変更をカタログに書くようにする。GitHub に書く判断は、必ず確かめてから行い（R-I4）、結果が分からない書き込みを重ねない。`work finish` は、仕様の変更が GitHub の canonical に届いたことを確かめてから Issue を閉じる（R-C6、AC-13）。
- 関係者：
  - 利用者とエージェント：今と同じコマンドで、canonical モードの Scope を作り、変え、作業を始めて終えられること。失敗したときに、次の1手が示されること。
  - 定期の同期（I-3）：コマンドがカタログに書いた変更が、変更の束として1つのコミットで保存されること。
  - 後の Issue：I-6（日本語の題名）が、この Issue の `scope create`、`scope import`、`scope edit` に題名の規則を足す。I-9 が、文書とコマンドの一覧を仕上げる。
  - 移行していないリポジトリ（版3）：今と同じに動くこと（AC-15）。

## 観測可能な要件

### R-432-01 書く前に確かめる（すべての GitHub に書くコマンド）

- GitHub に書くコマンドは、書く前に、`ensure_fresh(decision)` で構造のスナップショットを確かめる（変わったかの確かめを必ず行い、変化があるか `fetched_at` から5分を超えていれば全体を取り直す）。さらに、判断に使う Issue を `GET …/issues/{n}` で読み直し、判断に親子や依存を使うコマンドは、その関係（親、子、依存）も読み直す。読み直した値で判断し、スナップショットにも反映する（R-I4）。`scope delete` は、生き残る Scope からの依存を漏れなく見つけるため、変わったかの確かめを待たずに全体を取り直す。読み直すものは `design.md` の表のとおりである。
- GitHub につながらない、レート制限、権限がないときは、何も書かずに、元の失敗のコード（`GITHUB_UNAVAILABLE`、`GITHUB_RATE_LIMITED`、`GITHUB_ACCESS_DENIED` など）で止まる。共通の `--offline` を付けたときも、何も書かずに `PRECONDITION_FAILED`（終了コード3、「offline mode cannot fetch required GitHub state」）で止まる。
- 止まる条件（引数、対象と親の解決、種類と階層の規則、状態の規則、循環、カタログのリンクと形式の版、作業ツリーの前提）は、すべて最初の書き込みの前に確かめる。そこで止まるときは `failed` で、効果はない。
- 書き込みは、1つずつ順に送り、続けて送るときは1秒以上の間をおく（I-1 の部品）。書き込みが成功するたびに、その結果を構造のスナップショットに反映する（R-I3）。次の `scope show` などは、取り直しなしで新しい構造を示す。
- 反映できない変更（相手の番号がスナップショットにない、など）は、当てずに飛ばし、スナップショットを古いものとして扱い、次の `ensure_fresh` で全体を取り直させる。コマンドの結果は失敗にせず、`warnings` に `GITHUB_SNAPSHOT_STALE` を入れる。
- 書き込みの結果が分からないとき（応答が失われた、読めない）は、送った値をすべて比べて読み直す。それでも分からなければ、同じ書き込みを重ねずに、`partial`（終了コード6）で、その効果を `unknown`、残りの効果を `not_attempted` として返し、`recovery` に、GitHub の今の状態を確かめてから行う次の1手を入れる。
- `--expect-current` と `--expect-backend` は、今と同じ意味で、確かめたスナップショットの Scope で確かめる。

### R-432-02 カタログに書く（すべてのカタログに書くコマンド）

- カタログに書くコマンド（`scope create`、`scope import github`、`scope move`、`scope delete`、Scope の `artifact create`、`artifact import file`、`work finish`）は、最初に `require_linked` で確かめる（`@root` の Artifact はカタログに書かないので、リンクを求めない）。リンクやカタログが正しくなければ、何も書かずに `CANONICAL_NOT_LINKED`（終了コード3、`recovery` に `spec-dock canonical link`）で止まる。マウントしたチェックアウトでは `CANONICAL_FOREIGN_CHECKOUT`、git が古ければ `CANONICAL_GIT_TOO_OLD` で止まる。
- カタログの形式の版が、この SpecDock が書ける版（1）でないときは、GitHub にも書く前に `CANONICAL_FORMAT_UNSUPPORTED`（終了コード3）で止まる。
- カタログへの書き込みは、カタログの排他（C4。待つのは10秒まで）の中で行い、書いたパスと消したパスを、`origin: command` の変更の束に残す（`work finish` は `origin: finish`）。排他が取れなければ `CANONICAL_LOCK_BUSY`（終了コード3）で止まる。排他の中ではネットワークを使わない。SpecDock のコマンドはカタログでコミットしない。
- 書くのは、リンクを通さないカタログの実際のパスである。示す場所は、このチェックアウトのリンクを通した `spec-dock/initiatives/<カタログの中の相対パス>` である。

### R-432-03 Scope の作成（`scope create initiative|epic|issue`）

- 引数は今と同じ（`--backend github`、Epic と Issue は `--parent`、`--title`、`--slug`）。題名と slug の規則は、今の規則（`resolve_input_title_and_slug`）のまま（日本語の題名は I-6）。`--yes` のない非対話の実行は、今と同じく `CONFIRMATION_REQUIRED`（終了コード3）で止まる。
- 親は、今と同じ選択子で決め、種類が規則（Epic の親は Initiative、Issue の親は Epic）に合い、親とその祖先が開いていて、親のディレクトリがカタログにあることを、書く前に確かめる。親は読み直す。
- GitHub に、次の順に書く：種類のラベルがなければ作る → Issue を作る（題名、本文の末尾の slug の印、種類のラベル）→ 親への sub-issue。その後、カタログの排他の中で、Scope のディレクトリをテンプレートから一度に公開し（ID は作った Issue の番号）、変更の束を書く。`.meta.json` は作らない。
- テンプレートを写すときは、前付けの `タイトル:` と `親:` の行を除く（Epic の6章）。見出しの題名は、作成時の題名のまま残す。Artifact の規則のリンク（`artifacts/rules.md` など）は、今と同じ相対のリンクを置く。
- Issue を作った後に失敗したときは、`partial`（終了コード6）で、`recovery` に `spec-dock scope import github <種類> gh:<owner>/<repo>#<番号> …`（親、題名、slug を含む）を返す。その `scope import github` で、足りないものを足して完了できる。Issue を作ったかどうか分からないとき（`GITHUB_CREATE_IDENTITY_UNKNOWN`）は、作られた Issue を探してから `scope import github` を使うよう示す。

### R-432-04 Scope の取り込み（`scope import github initiative|epic|issue`）

- 引数は今と同じ（GitHub の参照、Epic と Issue は `--parent`、`--title`、`--slug`、`--github-repo`）。別のリポジトリの Issue は、何も書かずに止まる。PR は取り込まない。
- Issue と、その親、子、依存を読み直し、足りないものだけを、次の順に足す：種類のラベル（ラベル自体がなければ作る）→ 本文の slug の印（`PATCH` の `body`。印がすでにあれば本文を書かない）→ 親への sub-issue → カタログの Scope のディレクトリ。何度実行しても同じ結果になり、足すものがなければ `unchanged` を返す。
- slug は、本文の印があればそれを使う。印がなければ `--slug`、それもなければ `--title` から今の規則で作る。`--title` は slug の材料にだけ使い、GitHub の題名は変えない（統括の判断）。
- 止まる条件（書く前）：別の種類のラベルがある、種類のラベルが2つ以上、印が2つ以上か規則外、印と `--slug` が違う、GitHub の親が `--parent` と違う（次の1手は「`--parent` を GitHub の親にして取り込み、その後で必要なら `spec-dock scope move <ID> --parent <親>`、または GitHub で親を直してから取り込む」）、Initiative に親がある、親の種類が規則に合わない、親かその祖先が閉じている、カタログに同じ ID のディレクトリがあり slug が違う、同じ ID のディレクトリが2つ以上。

### R-432-05 題名の変更（`scope edit`）

- `PATCH` で GitHub の題名だけを変える。カタログのファイルは変えない。対象は読み直す。題名が同じなら書かずに `unchanged` を返す。題名の規則は今のまま（空でない）。

### R-432-06 親の変更とディレクトリの合わせ（`scope move`、新設）

- 新しいコマンド `spec-dock scope move <target> [--parent <parent>]` を足す（コマンドの数は52から53）。
- `--parent` があれば、親の種類の規則、対象自身や子孫を親にしないこと、新しい親とその祖先が開いていることを確かめ、対象と新しい親を読み直してから、`POST …/sub_issues` の `replace_parent: true` で付け替える。すでにその親なら書かない。Initiative は `--parent` を受け付けない。
- その後（`--parent` がなくても）、カタログの排他の中で、対象のディレクトリを、GitHub の親（読み直した値）のディレクトリの下（Initiative はカタログの直下）へ移し、移した先と元の場所を変更の束に書く。すでにその場所なら移さない。移す先に同じ名前があれば、書く前に止まる。
- 移した後、このチェックアウトの選択が移した Scope かその子孫なら、`spec-dock/active/` のリンクを新しい場所に直す。ほかのworktreeの選択が移した範囲にあれば、警告と次の1手（そのworktreeで `spec-dock active set <ID>`）を返す。
- 対象と親のディレクトリがカタログになければ、書く前に `LOCAL_TARGET_NOT_FOUND`（終了コード4）で止まる。
- 版3のリポジトリでは、`CANONICAL_NOT_MIGRATED`（終了コード3）で止まる。

### R-432-07 完了と再開（`scope close`、`scope reopen`）

- 状態の規則は今と同じ：`scope close` は、`--reason completed` のとき子孫がすべて `completed` であること、対象の状態が分かること、閉じた理由が違わないこと。加えて、`--reason completed` のとき、対象か子孫に別のリポジトリの子（`SUB_ISSUE_FOREIGN_REPOSITORY`）か、異常のために ID が決まらない子があれば、完了を確かめられないので、書く前に止まる（`work finish` も同じ）。`scope reopen` は、祖先がすべて開いていること。子孫と祖先は、GitHub の親子（スナップショット）から求める。対象は読み直す。
- 今と同じく状態を `PATCH` する（`close` は `state: closed` と `state_reason: completed|not_planned`、`reopen` は `state: open`）。結果が分からないときの読み直しは、`state_reason` も比べる。`--yes` のない非対話の実行は、今と同じく止まる。

### R-432-08 削除（`scope delete`）

- 引数と止まる条件は今と同じ（`--backup-dir` は必須で絶対パスで、まだないこと。子孫があれば `--recursive`、選択がその中にあれば `--clear-active`、生き残る Scope からの依存があれば `--detach-dependencies`。`--yes` のない非対話は止まる）。
- 次の順に行う：対象のディレクトリ（子孫を含む）を `--backup-dir` に写して中身を確かめる → `--clear-active` なら選択を外す → カタログの排他の中でディレクトリを消し、削除を変更の束に書く → `--detach-dependencies` なら、生き残る Scope からの blocked by を外す → 対象を GitHub の親から外す → 削除する各 Scope（子孫から）の種類のラベルを外す。Issue 自体は閉じも消しもしない。GitHub の書き込みを最後にするのは、途中で止まっても、対象がまだ Scope であり、同じ `scope delete` をもう一度実行すれば続きから整う（ディレクトリがすでにないときは、バックアップと削除を `unchanged` として飛ばす）ようにするためである。
- 子孫のディレクトリが対象のディレクトリの下にない（入れ子がずれている）ときは、書く前に止まり、`spec-dock scope move <ID>` を示す。

### R-432-09 依存の変更（`dependency add`、`dependency remove`）

- `--from` と `--to` は、今と同じく Scope に決まる。両端を読み直す。
- `dependency add` は、循環や規則の違反になるとき、書く前に止まる（`PRECONDITION_FAILED`、終了コード3、違反のコードと相手を示す）。すでにあれば書かずに `unchanged`。`POST …/dependencies/blocked_by`（本文の `issue_id` は依存先の Issue の id）で足す。
- `dependency remove` は `DELETE …/dependencies/blocked_by/{依存先の id}` で外す。ないときは、今と同じく `--missing-ok` なら `unchanged`、なければ `SCOPE_NOT_FOUND`（終了コード4）。
- `.meta.json` を書かない。結果は、今と同じ `declared`、`effective` と `changed` に、`data.snapshot` を足す。

### R-432-10 Artifact の作成（`artifact create`、`artifact import file`）

- Scope の Artifact は、カタログの Scope のディレクトリの `artifacts/` に、今と同じ名前の規則と書き方（上書きしない、共有の番号を使わない、テンプレートの置き換え、取り込む元のファイルの確かめ）で公開し、変更の束を書く。示す場所は `spec-dock/initiatives/…/artifacts/<名前>` である。
- 構造は `display` の新しさで読む（GitHub に書かない）。`@root` は、今と同じく、このチェックアウトの `spec-dock/artifacts/` に書く（カタログではない）。

### R-432-11 作業の開始（`work start`）

- 引数とブランチの扱いは今と同じ（新しいブランチは `--base`、既存のブランチは `--branch` を明示し `--base` なし、`--switch-active`、作業ツリーがきれいなこと、同じクローンの別のworktreeが同じ Scope を選んでいれば `SCOPE_ALREADY_SELECTED`、同じブランチを別のworktreeがチェックアウトしていれば `BRANCH_IN_USE`、`StartLock` の中でのチェックアウトと選択の記録）。既定のブランチ名は `<ID>-<slug>`（slug は GitHub の印）。
- 基点のコミット（既存のブランチなら、その先頭）のツリーから `.meta.json` を読まない。ツリーに `spec-dock/initiatives` があれば、書く前に `CANONICAL_BASE_HAS_SPECS`（終了コード3）で止まる。
- 着手の判定は、`decision` の新しさのスナップショットで、I-4 の `evaluate_readiness` で行う。対象と、対象と祖先の Scope でない依存先を読み直す。進むのは、`ready` が真（ブロッカーも判定できない理由もない）のときだけである。そうでなければ（`BLOCKED`、`UNKNOWN`、`DONE`、作業中の印があってブロッカーもある場合）、`READINESS_NOT_SATISFIED`（終了コード3）で止まり、ブロッカーと理由を示す。`ready` が真で `DOING`（`spec-dock:in-progress` がある）のときは、止めずに、警告 `SCOPE_IN_PROGRESS` を返して進める（統括の判断 Q1。`details` に担当者と、分かれば印を付けた時刻、次の1手は「別のPCで作業中でないか利用者に確かめる。古い印なら `spec-dock work finish` か GitHub でラベルを外す」）。
- リンクやカタログがないことは、`work start` の書く前の条件にしない。選択を記録して `StartLock` を放した後に、`link_after_command` で、このチェックアウトのリンクを整える（R-B4）。その失敗は `work start` の結果を変えず、警告と次の1手で返す。
- 続けて、リンクが正しければ `spec-dock/active/` のリンクを今と同じく整える（リンクがなければ飛ばして警告を返す）。最後に作業中の印を付ける（ラベル `spec-dock:in-progress`。ラベル自体がなければ作る。担当者に自分のログイン名を足す）。印の失敗は `work start` の結果を変えず、警告だけにし、警告の `details` に、失敗した書き込みとその状態（`failed` か `unknown`）を入れる。
- 結果の形は今と同じ（`scope_id`、`started`、`branch_before`、`branch_after`、`selection_token`）。

### R-432-12 作業の終了（`work finish`）

- 引数は今と同じ（`--yes` が必須）。対象の状態の規則は今と同じ（状態が分からなければ止まる、`not-planned` は再開が要る、子孫がすべて `completed`）。
- Issue を閉じる前に、その Scope の仕様の変更が GitHub の canonical に届いたことを確かめる（Epic の5章、R-C6）：
  1. Scope の下に保留（`state.json` の `holds`）があれば、書く前に `CANONICAL_SAVE_HELD`（終了コード3）で止まり、保留の種類ごとの解き方を示す。同期が一時停止しているときは、確かめられないので、書く前に `CANONICAL_SAVE_UNCONFIRMED` で止まる。
  2. カタログの排他の中で、Scope の場所（ディレクトリがなくても、カタログの中の場所）の下の未保存の変更（削除を含む）を集め（`.git` に書かない読み方）、あれば `origin: finish` の変更の束を書く。ディレクトリがないことを理由に、確かめを飛ばさない。
  3. 定期の実行に、すぐの実行を頼む（I-3 の `request_sync_now`。失敗してよい）。
  4. 状態の置き場の `state.json` を2秒ごとに読み、180秒まで（統括の判断 Q2：引数で変えない固定の値）、次のすべてを待つ：書いた束が `consumed_changesets` にある（束がなければこの条件はない）、`last_cycle.finished_at` が待ち始めた時刻より後、Scope の下に未保存の変更がない（毎回、読むだけで確かめる）、`state.json` の `head` がカタログの今の HEAD と同じで `remote_contains_head` が真、Scope の下に保留がない。待つ間に保留が現れたら、待たずに `CANONICAL_SAVE_HELD` で止まる。
  5. 確かめられなければ、Issue を閉じずに `CANONICAL_SAVE_UNCONFIRMED` で止まり、`recovery` に `spec-dock canonical status` を入れる。束を書いた後なら `partial`（終了コード6。束を `succeeded`、Issue を閉じることを `not_attempted`）、書いていなければ `failed`（終了コード3）とする。
- 他のクローンの push を取り込んだだけで、自分は push しなかった場合も、`remote_contains_head` で確かめられて閉じる（AC-13）。
- 確かめた後、閉じる前に、`ensure_fresh(decision)` と対象の読み直しをもう一度行い、状態の規則を確かめ直す（待つ間に他の人が閉じたり、子が開き直されたりしても、古い値で書かないため）。ここで止まるときは、束を書いていれば `partial`（6）で、`recovery` に `spec-dock work finish <ID> --yes` を入れる。
- その後、今と同じく Issue を閉じ（`completed`。すでに閉じていれば書かない）、作業中のラベルを外し（失敗は警告だけ）、選択が対象かその子孫なら選択を外し、`spec-dock/active/` のリンクを今と同じく戻す。

### R-432-13 I-4 から引き継ぐ直し

- **ブランチの失敗の後の再観察**：canonical の `branch create` と `branch switch` が Git の失敗やチェックアウトの後の確かめで止まるとき、効果の判定を従来の `branch_operations` と同じにする（作成：失敗の後に参照を読み直し、あれば作成済み、固定した基点と同じなら `succeeded`、なく結果が確かなら `failed`、ほかは `unknown`。切り替え：失敗の後に、目的のブランチと先頭にいてきれいなら `succeeded`、元のブランチと先頭にいてきれいで結果が確かなら `failed`、ほかは `unknown`）。読み直しそのものの失敗で効果を失わない。切り替えの後に作業ツリーがきれいであることを確かめる。
- **`--expect-current` の競合**（統括の判断 Q3）：`worktree remove` と `worktree bootstrap` は、canonical で取り込んで確かめた同じ選択の記録で、従来の内側の処理を呼ぶ。`worktree create --expect-current` と版4の `installation … --expect-current` は、従来の処理を呼ぶ直前に記録を読み直して、確かめた記録と同じであることを確かめる。docstring を実際の保証に合わせる。
- **`worktree remove` とリンク**（統括の判断 Q4）：対象のworktreeの無視されたものが、正しいリンク `spec-dock/initiatives` だけのときは、`--discard-ignored` なしで消す（リンクだけが消え、カタログは残る）。ほかの無視されたものが1つでもあれば、今と同じく `--discard-ignored` を求める（選択を持つworktreeは、無視された `spec-dock/active/` と `spec-dock/.agent/` があるので、今と同じく求める）。

### R-432-14 C1 と C10 の追加（Epic が I-5 に任せたもの）

- `GithubStructureClient.update_issue` に `body` を足す。結果が分からないときの読み直しは、送った値（題名、本文、状態、`state_reason`）をすべて比べる。本文は改行を `\n` にそろえて比べる。
- 書き込みの反映は、スナップショットにない番号に当たる変更を当てずに飛ばし、スナップショットを古いものとして扱う（次の `ensure_fresh` が、どの新しさの段階でも、全体を取り直す）。`snapshot.json` と `probe.json` の形式の版は変えない。

### R-432-15 答えないコマンドを残さない

- この Issue の後、版4のリポジトリで `CANONICAL_NOT_IMPLEMENTED` で止まるコマンドはない（コマンドの一覧のテストで確かめる）。

## スコープ

- 対象：上の要件の、canonical モードの書くコマンドの処理、`scope move` の新設（`cli/catalog.py`、`--help`、配布資産の `docs/reference_cli.md` と `static-inventory.json`）、C1 と C10 の追加、I-4 から引き継ぐ直し、それらのテスト。
- 対象外：
  - 日本語の題名と `SLUG_REQUIRED`（I-6）。
  - ダッシュボード（I-11）、使い方の文書とエージェント向けの規則（I-9）。`SCOPE_IN_PROGRESS` でエージェントが利用者に確かめる規則は、I-9 の規則の節に書く（統括の判断 Q1）。
  - `work finish` の待ち時間を変える引数（統括の判断 Q2）。
  - 本物の GitHub での確かめ（I-10）。
- 親契約として維持する境界：
  - C1、C2、C3、C4、C6、C9、C10 と I-4 の部品の公開の形を変えない（Epic が I-5 に任せた追加のほか）。
  - 従来モードの処理、`.meta.json` の読み書きのコード、版3の振る舞いのテストを変えない（AC-15）。従来の部品は、変えずに呼ぶ。
  - 選択の記録の形式と `StartLock` を変えない。テンプレートの配布資産の中身を変えない。

## 失敗・境界条件

| 場面 | 振る舞い |
|---|---|
| GitHub につながらない、レート制限、権限なし（書く前） | 何も書かずに元のコード（5）。`--offline` は `PRECONDITION_FAILED`（3） |
| リンクやカタログが正しくない（カタログに書くコマンド） | `CANONICAL_NOT_LINKED`（3）。GitHub にも書かない |
| カタログの形式の版が書けない | `CANONICAL_FORMAT_UNSUPPORTED`（3）。GitHub にも書かない |
| カタログの排他が取れない（GitHub に書いた後） | `partial`（6）。`recovery` に、同じコマンド（`scope import github`、`scope move` など、続きから整うもの）を示す |
| Issue を作った後の失敗 | `partial`（6）と `scope import github` の案内 |
| Issue を作ったか分からない | `partial`（6）、`GITHUB_CREATE_IDENTITY_UNKNOWN`。作られた Issue を探して `scope import github` |
| 書き込みの結果が分からず、読み直しでも分からない | `partial`（6）、`GITHUB_EFFECT_UNKNOWN`。同じ書き込みを重ねない |
| 書いた結果をスナップショットに反映できない | 結果は変えず、`GITHUB_SNAPSHOT_STALE` の警告。次の `ensure_fresh` が取り直す |
| 依存の追加が循環になる | 書く前に `PRECONDITION_FAILED`（3） |
| `work start` の基点に `spec-dock/initiatives` | `CANONICAL_BASE_HAS_SPECS`（3）。書かない |
| `work start` の対象が `DOING` | 警告 `SCOPE_IN_PROGRESS` で進む |
| `work start` の後のリンクや作業中の印の失敗 | 結果は変えず、警告 |
| `work finish` で保留がある | `CANONICAL_SAVE_HELD`（3。待つ間に現れて束を書いた後なら `partial` の6） |
| `work finish` で保存を確かめられない | Issue を閉じずに `CANONICAL_SAVE_UNCONFIRMED`（束を書いた後は6、書いていなければ3） |
| `work finish` の後の作業中のラベルの削除の失敗 | 結果は変えず、警告 |
| 対象や親のディレクトリがない（`scope move`、`scope create` の親） | `LOCAL_TARGET_NOT_FOUND`（4）。書かない |
| `scope delete` の対象のディレクトリがない | バックアップと削除を `unchanged` として飛ばし、GitHub の書き込みだけを行う（途中で止めた後のやり直し） |
| 版3で `scope move` | `CANONICAL_NOT_MIGRATED`（3） |

## 受け入れ条件

テストは、外のネットワークを使わない（偽の `gh`、一時ディレクトリの bare のリポジトリ、`XDG_STATE_HOME` を一時ディレクトリに）。

- **AC-432-01**（書く順と束）：偽の `gh` と一時のカタログで、`scope create`（3つの種類）、`scope import github`、`scope edit`、`scope move`、`scope close`、`scope reopen`、`scope delete`、`dependency add`、`dependency remove`、`artifact create`、`artifact import file` が、`design.md` の順に GitHub に書き（偽の `gh` の記録の書き込みの順と本文で確かめる。`sub_issue_id` と `issue_id` は番号ではなく Issue の id）、カタログに書くものは、カタログの排他の中で書いて、`origin: command` の変更の束を残す（束の `paths` と `deletions` で確かめる）。`.meta.json` を作らない。作った Scope のディレクトリの文書の前付けに `タイトル:` と `親:` の行がない。
- **AC-432-02**（書く前の確かめ）：各書くコマンドが、書く前に変わったかの確かめ（条件付きの要求）を行い、判断に使う Issue を `GET` で読み直す（偽の `gh` の記録で確かめる）。偽の `gh` を接続できないようにすると、書き込みの要求もカタログの変化もなく、`GITHUB_UNAVAILABLE`（5）で止まる。`--offline` は `PRECONDITION_FAILED`（3）で止まる。スナップショットにない古い状態（GitHub だけで閉じた親、GitHub の画面だけで変えた親や依存）は、読み直しで見つかり、書く前に止まるか、読み直した値で正しく書く。
- **AC-432-03**（すぐの反映。AC-16 の一部）：変わったかの確かめの間隔（60秒）の中で、`scope create` の後の `scope show` が、偽の `gh` に GraphQL の全体の読み取りを送らずに、新しい Scope を示す。`scope edit`、`dependency add` の後の表示も、取り直しなしで新しい値を示す。
- **AC-432-04**（作成の後の失敗）：Issue を作った後の sub-issue の失敗と、カタログの排他の失敗で、`scope create` が `partial`（6）と、`recovery` に `scope import github` を返す。その案内のとおりの `scope import github` が、Issue を重ねて作らずに完了させる（偽の `gh` の Issue の数で確かめる）。Issue を作る要求の応答を失わせると、`GITHUB_CREATE_IDENTITY_UNKNOWN` の `partial` になる。
- **AC-432-05**（取り込み）：印のない既にある Issue の `scope import github` が、本文の `PATCH` で印を足し、ラベル、親、ディレクトリを足す。Scope でない子を持つ Issue の取り込みで、`GITHUB_SNAPSHOT_STALE` の警告が出ない。印がすでにあれば本文を書かない。2回目は書き込みの要求なしで `unchanged`。止まる条件（別の種類、印と `--slug` の違い、違う親）で、何も書かない。
- **AC-432-06**（反映できない変更）：スナップショットにない番号に当たる変更の反映が、例外を出さずに飛ばされ、コマンドが成功のまま `GITHUB_SNAPSHOT_STALE` を警告に入れ、次の `display` の読み取りが全体を取り直す（単体と CLI のテスト）。
- **AC-432-07**（閉じると開く）：`scope close` が子孫の未完了と、別のリポジトリの子で止まり、`completed` と `not-planned` を `state_reason` で書く。結果が分からないときの読み直しが `state_reason` を比べ、違えば `GITHUB_EFFECT_UNKNOWN` の `partial` になる（単体のテスト）。`scope reopen` が閉じた祖先で止まる。
- **AC-432-08**（依存）：`dependency add` が、循環になるとき書く前に止まり、偽の `gh` に書き込みがない。正しい追加と削除が blocked by に反映され、`dependency remove --missing-ok` がないときは書かずに `unchanged`。
- **AC-432-09**（移動）：`scope move --parent` が `replace_parent: true` で付け替え、ディレクトリを新しい親の下へ移し、束の `paths` に新しい場所、`deletions` に古い場所が入る。`--parent` なしは、GitHub の画面で変えた親に合わせてディレクトリだけを移す。同じ場所なら `unchanged`。選択した Scope を移すと、`spec-dock/active/` のリンクが新しい場所を開く。版3では `CANONICAL_NOT_MIGRATED`。
- **AC-432-10**（削除）：`scope delete` が、バックアップの後に、依存を外し、親から外し、種類のラベルを外し、ディレクトリを消し、削除を束に書く。Issue は閉じない。止まる条件（`--backup-dir` なし、`--recursive`、`--clear-active`、`--detach-dependencies`、入れ子のずれた子孫）で何も書かない。GitHub の書き込みの途中で止めた後、同じ `scope delete` で完了する。
- **AC-432-11**（Artifact）：`artifact create` と `artifact import file` が、mainのチェックアウトと作業用のworktreeの両方で、カタログの Scope の `artifacts/` に公開し、束を書き、場所を `spec-dock/initiatives/…` で示す。`@root` は今と同じく `spec-dock/artifacts/` に書き、束を書かない。
- **AC-432-12**（作業の開始）：`work start` が、新しいブランチと既存のブランチで、今と同じ効果（ブランチ、チェックアウト、選択の記録、`spec-dock/active/` のリンク）に加えて、作業中のラベルと担当者を付け、作業用のworktreeでもリンクが整う。基点に `spec-dock/initiatives` があると `CANONICAL_BASE_HAS_SPECS` で止まり、参照、HEAD、選択を変えない。`BLOCKED`、`UNKNOWN`、作業中の印があって前提が未完了の Scope は `READINESS_NOT_SATISFIED` で止まる。前提が満たされた `DOING` は `SCOPE_IN_PROGRESS` の警告（担当者を含む）で進む。印を付ける要求を失敗させても、結果は `succeeded` で、警告に失敗した書き込みが入る。リンクのないチェックアウトでも、`work start` がリンクを作って進む。
- **AC-432-13**（作業の終了。AC-13）：未保存の変更があるとき、`work finish` が `origin: finish` の束を書き、同期の周期を待ち、push が確かめられてから Issue を閉じ、作業中のラベルを外し、選択を外す。同期が来ない（時刻を注入して180秒を過ぎる）と、Issue を閉じずに `CANONICAL_SAVE_UNCONFIRMED`（6）で止まる。Scope の下に保留があると `CANONICAL_SAVE_HELD` で止まる。Scope のディレクトリを手で消した未保存の削除も、保存を待ってから閉じる。待つ間に GitHub で対象が閉じられたり子が開き直されたりしたら、閉じる前の確かめ直しで止まる。もう1つのクローンの push を取り込んだだけで自分は push しなかった場合も、確かめられて閉じる。
- **AC-432-14**（I-4 から引き継ぐ直し）：`branch create` と `branch switch` の Git の失敗とチェックアウトの後の確かめの失敗で、効果の判定が従来と同じになる（項目ごとのテスト）。`worktree remove` と `worktree bootstrap` が、確かめた記録で従来の内側の処理を呼び、その後に選択が変わると書く前に止まる。`worktree create --expect-current` は、従来の処理の直前の読み直しで不一致なら止まる。無視されたものが正しいリンクだけの作業用のworktreeが、`--discard-ignored` なしで消え、カタログは残る。ほかの無視されたファイルがあれば、今と同じく止まる。
- **AC-432-15**（答えないコマンドを残さない）：版4のリポジトリで、すべての公開のコマンドが `CANONICAL_NOT_IMPLEMENTED` 以外で答える（コマンドの一覧のテスト）。`scope move` が `help`、`completion`、`--help` の Target/Reads/Writes/Does not の節に出て、効果の要約が Epic の12章の文（「Change or re-align a Scope parent in GitHub and move its directory to match.」）である。
- **AC-432-16**（AC-15）：版3の振る舞いを確かめる今のテストが、Epic の `design.md` の testability の「従来モードの回帰」で許された変更（コマンドの数と一覧、配布資産の一覧と値、文書の中身）のほかは、変更なしで通る。I-1〜I-4 の canonical のテストのうち、この Issue のコマンドが `CANONICAL_NOT_IMPLEMENTED` になることを確かめていたものは、canonical のテストとして直し、`report.md` に一覧で書く。`git diff --name-only origin/main -- src/` に、`design.md` の「置き場」の表のほかのファイルがない（従来のモジュールに差分がない）。
- **AC-432-17**：`make lint` と `uv run pytest` が通る。

## 制約・前提

- Epic の目的、Issue の分け方、Issue をまたぐ契約（C1〜C11）を変えない。Epic が I-5 に任せた C1 と C10 の追加だけを行う。
- 従来モード（宣言の版3）の処理、`.meta.json` の読み書きのコード、版3の振る舞いを確かめるテストを変えない（AC-15）。
- 本物の GitHub に、ラベル、sub-issue、依存、`spec-dock/canonical` ブランチを作らない。本物の spec-dock のリポジトリで canonical のコマンドを実行しない。利用者の状態の置き場（`~/.local/state/spec-dock/`）、`~/Library/LaunchAgents/`、`~/.config/systemd/user/`、ツールの設定を変えない。テストは `tests/conftest.py` の2段の防ぎの中で書く。
- 並行の I-11（`iss-00438`）と、`cli/catalog.py`、`commands/canonical_dispatch.py`、コマンドの一覧のテストで衝突しうる。先に `main` に入った方を、`origin/main` のマージで取り込む。
