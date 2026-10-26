---
種別: 要件定義書（Issue）
ID: "iss-00430"
タイトル: "Add Periodic Canonical Sync"
関連GitHub: ["#430"]
状態: "draft"
最終更新: "2026-10-26"
親: ["epic-00424", "init-00423"]
---

# iss-00430 Add Periodic Canonical Sync — 要件定義

詳細: [Requirement Guide](../../../docs/authoring/requirement.md)

表示名：60秒ごとの保存、取り込み、push を行う `canonical sync` と、その登録、保留、再開、取り外しを足す（Epic の I-3）

## 目的

保存、取り込み、push が、人もエージェントも意識せずに、60秒ごとに行われる。競合しても、GitHub が書き換えられても、編集は失われない。

- 材料：Epic の `plan.md` の「I-3 Add Periodic Canonical Sync」の節（価値、作るもの、受け入れ、実機の確かめ）と、Epic の `design.md` の担当の章（5章の全体、3章の手順6・7・`--no-schedule`・`canonical remove`、2章の C10 のうち周期の手順7の `ensure_fresh(repository, cycle)`、4章の変更の束を読む側、6章と12章の I-3 の行）。Issue をまたぐ契約は、Epic の `plan.md` の「Issue をまたぐ契約」の表に従う。
- 依存：I-2（`iss-00429`。PR #447 で `main` に入った）。Planning Level：strict（理由は `plan.md`）。
- この Issue は、契約 C9（状態の置き場の根以外のすべて：登録簿、`state.json` の形式と意味、基準、すぐの実行の頼み方）の持ち主で、C11 に systemd のユーザーと linger の判定を足す。根の求め方 `resolve_state_root` は I-1 のものを使い、C4（束の形式）、C5、C6、C10 は持ち主の部品をそのまま使う。
- Epic の文書で決まっていなかった点は、統括の判断（2026-10-26。`plan.md` の「統括の判断」）を正本とする。

## 背景

- I-2 で、クローンごとのカタログ（mainのチェックアウトの `spec-dock/.canonical`、`spec-dock/canonical` のworktree）と、各チェックアウトのリンク `spec-dock/initiatives` ができた。人、エージェント、SpecDock のコマンドは、リンクを通して普通のファイルとして仕様を書く。SpecDock のコマンドはコミットせず、変更の束（`<カタログ>/.runtime/changesets/`）を残す（C4）。
- まだ、カタログの変更を保存（コミット）し、GitHub の canonical と統合し、push するものがない。この Issue がその唯一の経路（定期の同期）を作る（Epic の G4、R-C1）。
- 利用者は同じ仕様を複数のPC（クローン）で編集し、エージェントが同時に書く。保存の誤りは仕様の喪失になるので、競合、大量の削除、リモートの書き換えでは、消さずに残し、止まる（Epic の risk の最上位）。
- 定期の実行は、macOS は launchd、systemd の動く Linux はユーザーのタイマー、systemd のないコンテナは SpecDock 自身の常駐のプロセスで動かす（R-C7）。`spec-dock canonical link` の1回で登録する（約束2）。

## 観測可能な要件

### R-430-01 `spec-dock canonical sync` の1回の周期（R-C1〜R-C3、R-C5、Epic 5章）

- `canonical sync`（引数なし）はこのクローンのカタログを、`canonical sync --registered` は登録簿のすべてのカタログを、順に処理する。1つのカタログの失敗で、ほかのカタログを止めない。`--registered` はリポジトリによらずに動く（`--project` もリポジトリもいらない）。
- 1つのカタログについて、Epic の 5章の手順1〜6を、この順に行う：前提の確かめ、GitHub の確かめ（`ls-remote`、`fetch`、書き換えの検出）、保存、統合、push、記録。すべてのカタログの後に、登録簿の `repository` ごとに1回、`ensure_fresh(repository, cycle)` を行う（手順7。ダッシュボードは I-11）。
- 保存、取り込み、push のどれも、強制しない。`rebase` と強制の push を使わない。カタログに、競合のマーカーとマージの途中の状態を残さない。
- 変更のない周期は、コミットしない。
- カタログに対する Git の呼び出しは、すべて I-2 の `run_catalog_git`（C6）を通す。リポジトリのフック（`pre-commit`、`post-checkout`、`post-merge`、`pre-push`）と署名の設定（`commit.gpgSign=true`）があっても、同期は止まらない。
- 同じカタログの周期は重ならない。別の周期がそのカタログを処理しているときは、そのカタログを飛ばす（統括の判断 Q4）。

### R-430-02 保存するパスの選び方（R-C2、R-D1）

- 変更の束にあるパス（ディレクトリならその下のすべて）は、30秒を待たずに、束ごとに1つのコミットで保存する。保存したら束のファイルを消す。束にあるパスが今はなく、HEAD にもなければ、無視する。
- そのほかの変更は、最後の変更から30秒以上たったものを保存する。変わり続けるものも、最初に変更を見つけてから5分たったら保存する。削除は、最初に見つけた時刻から数える。
- コミットのメッセージは `spec-dock: save <件数> files (<PC名>)`、作者は利用者の Git の設定のとおりとする。
- カタログに書く SpecDock のコマンドが排他を持っている間（書きかけの束）は、そのカタログを保存しない。誰かがカタログで `git add` していても、保存と統合は止まらない。

### R-430-03 保留（R-C4）

- 次のものは、保存しないで保留し、状態とログに記録する。中身はログに書かない。
  - **大量の削除**：今の作業ツリーにある、`origin: command` の束にない削除のすべてが、20件以上、または5件以上かつ HEAD で追跡しているファイルの10%以上のとき、それらの削除をすべて（統括の判断 Q2）。
  - **秘密情報らしいもの**：中身が、Epic の 5章の正規表現（トークンの全体の形）のどれかに当たるファイル。接頭辞だけでは当てない。
  - **大きすぎるファイル**：10 MiB より大きいファイル。
- `origin: command` の束の削除は保留しない。`origin: finish` の束の変更には、すべての保留の規則を当てる。
- `spec-dock canonical accept <パス>…` は、そのパスの今の中身（blob の値）を許可として記録する。中身が変われば許可は効かない。`--deletions` は、今保留している削除の一覧を許可する。どちらもコミットしない。
- `spec-dock canonical restore [<パス>…]` は、保留中のパスを HEAD の内容に戻す。パスを付けないときは、保留中の削除をすべて戻す。保留にないパスは、何も書かずに `CANONICAL_NOT_HELD` で止まる（統括の判断 Q1）。コミットしない。
- restore は、カタログの排他の中で作業ツリーを取り直し、今も保留に当たるものだけを戻す。大量の削除は今も削除されているパスだけ、秘密情報と大きすぎるファイルは今の中身がまだその保留に当たるものだけである。前の周期の後に作り直された、または直されたファイルは上書きしない（パスを付けたときは、何も書かずに `CANONICAL_NOT_HELD` で止まる）。

### R-430-04 統合と競合（R-C3）

- 手元の HEAD（L）と GitHub の canonical（R）について：R が L の祖先なら何もしない。L が R の祖先なら早送りする。分岐していれば、作業ツリーに触れずに統合する。
- 同じファイルの競合では、元の名前に R（先に push された版）を、別名ファイルに L を置く。別名ファイルの名前は Epic の 5章の規則（拡張子のないファイルと `.` で始まるファイルは、名前の全体を本体とする）。変更と削除の競合では、変更を残す。名前の変更が絡む競合も、同じ段の規則で扱う。
- 統合の結果が、編集中のファイル（未保存か保留）に当たるときは、何も壊さずにその周期の取り込みをやめ、当たったパスと理由を `blocking` に記録し、次の周期でもう一度試す。
- 統合できない（共通の祖先がない、など）ときは、`merge_failed` で一時停止する。

### R-430-05 書き換えと削除の検出、一時停止と再開（R-C5）

- 基準（最後に確かめた GitHub の canonical のコミット）があり、取得した R がその子孫でないとき（強制 push、共通の祖先のない履歴）、取り込まずに `remote_rewritten` で一時停止する。GitHub の canonical が消えて、基準があるときは、`remote_deleted` で一時停止する。
- GitHub に canonical がなく、基準もないときは、手元の canonical が初期のコミットだけのとき（新しいリポジトリの作成の続き）だけ push する。手元に中身があれば、GitHub で消されたものを作り直さず、`remote_deleted` で一時停止する（I-2 の統括の判断 A4 と同じ扱い）。
- 一時停止したカタログは、保存も push もしない。ファイルは編集でき、失われない。
- 基準は状態の置き場に置く。カタログを `git clean -ffdx` で消して `canonical link` で作り直した後も、基準が残り、検出が働く。
- `spec-dock canonical resume --adopt-remote`（`remote_rewritten`、`merge_failed`）は、基準を今の GitHub の canonical に置き直し、一度きりの「取り込み直し」の印を残して再開する。次の周期は、L と R を段の規則で統合した中身を、親を R だけにした1つのコミット C にし（共通の祖先がなくても統合する）、手元のブランチを C へ移してから、R からの早送りで push する。手元にしかない中身は消えず、GitHub が消した古い履歴は送らない（統括の判断 R2。Q3 の「2つの親」を置き換えた）。
- C を push する前に、R から C への差分に保留の規則（秘密情報らしいもの、大きすぎるファイル、大量の削除）を当てる。当たったら、C を作らず push もせず、一時停止のままにし、当たったパスを `holds` に、`CANONICAL_SAVE_HELD` を `last_error` に記録する。利用者がファイルを直すか `accept` してから、もう一度 `resume --adopt-remote` する（統括の判断 R2）。当たったパスがすべて作業ツリーで編集中（利用者が直している、消している）なら、一時停止にせず、何も push せずに `blocking` で持ち越し、その変更の保存の後に確かめ直す。
- `spec-dock canonical resume --push-local`（`remote_deleted`）は、手元の canonical を GitHub に作り直して再開する。

### R-430-06 push と push の認証（R-C6）

- L が R より進んでいれば、強制しない push を行う。先に進まれて拒否されたら、取得からやり直す（1つの周期で2回まで）。成功したら、基準を HEAD にする。
- ネットワークの断絶では、保存をローカルに積み、次の周期で push する。
- `canonical link` の後の最初の周期では、送るものがなくても `push --dry-run` で認証を確かめ、`push_auth` に記録する（統括の判断 Q5）。push が認証で失敗したときも記録する。`canonical status` は、リモートが `https` なら `gh auth setup-git`、`ssh` なら `https` と `gh` の認証を使う次の1手を示す。

### R-430-07 状態の置き場（C9）

- 根は I-1 の `resolve_state_root` で求める。`--state-root <絶対パス>` があればそれを使う。
- 登録簿 `<根>/canonical-registry.json`、カタログごとの状態 `<根>/catalogs/<鍵>/state.json`、ログ `<根>/canonical-sync.log`（1 MiB で1世代を残して切り替える）、常駐のプロセスの記録 `<根>/runner.lock`、`runner.json`、`kick` を、Epic の 5章の形式で置く。
- `canonical link` は、そのとき求めた根の絶対パスを、定期の実行の引数（`--state-root <絶対パス>`）に書く。`XDG_STATE_HOME` のない定期の実行の環境でも、`canonical link` のときと同じ登録簿と状態を読む。
- `state.json` を書くのは、定期の同期、`canonical link`、`canonical resume` だけである。ほかのコマンドは読むだけ。

### R-430-08 定期の実行（R-C7、C11）

- `canonical link` が次の順で仕組みを選び、登録簿の `scheduler` に記録する：macOS は `launchd`。Linux で `/run/systemd/system` があり、`systemctl --user is-system-running` が `running` か `degraded` なら `systemd`（「Failed to connect to bus」なら1秒おきに5回まで試し直す）。それ以外の Linux は `loop`（常駐のプロセス）。一度選んだら、`canonical remove` の後か、選んだ仕組みが使えなくなったときだけ選び直す。
- launchd、systemd のジョブの形（ラベル、ファイルの場所、引数、作業ディレクトリ、`PATH`、周期）は Epic の 5章のとおりとする。
- 常駐のプロセス（`canonical sync --registered --loop`）は、1つの環境に1つだけ動き（2つ目は終了コード0で何もせずに終わる）、60秒ごとに1周期を動かし、`kick` で待たずに周期を動かし、SIGTERM と SIGINT では、周期の途中ならその周期を終えてから止まる。`--detach` は、切り離して起動して、すぐに終わる。
- **すぐの実行の頼み方**：`launchd` は `kickstart`、`systemd` は `start --no-block`、`loop` は `kick` のファイル（動いていなければ `--detach` で起動）。失敗しても無視してよい（I-5 の `work finish` が使う）。
- C11 に、systemd のユーザーの判定（試し直しを含む）と linger の判定を足す。どちらも注入でき、`canonical link` の手順6と `canonical status` だけが求める（統括の判断 Q10）。

### R-430-09 `canonical link` の手順6と7、`--no-schedule`（Epic 3章）

- **手順6**：登録簿にカタログを足し（mainのチェックアウトを動かした後なら、古いパスの項目を消し、古い状態を新しい鍵へ移す）、選んだ仕組みのジョブがなければ作り、作った、または登録を足したときは、すぐに1回実行させ、最大15秒、状態の置き場の記録を待つ。仕組みを選び直したときは、前の仕組みのジョブを外す。登録簿の git とジョブの実行ファイルは、記録したものが今もあり、使える（git は 2.38 以上）なら書き換えない（エージェントの `PATH` や開発用の環境で入れ替わらないため）。ジョブの `PATH` には、git のディレクトリに続けて、`gh` のディレクトリも入れる（手順7の `gh` のため）。記録が見えないとき（macOS のプライバシーの保護など）、読めなかったとき（`OS_ACCESS_DENIED`）、push の認証に失敗したとき、linger がないとき、常駐のプロセスの環境（起動し直しの1行）は、原因と次の1手を `warnings` に返す。
- **手順7**：カタログを作った、または基準がないときは、手元の HEAD（このチェックアウトが持つ GitHub の履歴）を基準として記録する。手元の HEAD が初期のコミットだけのとき（新しいリポジトリの作成の続き）は、取得した `origin/spec-dock/canonical`（なければなし）にする。追跡の参照は、mainのチェックアウトの `git fetch` やリンクし直しの取得で、もう書き換えの後を指していることがあり、それを基準にすると GitHub が落としたコミットを push し直すため（最終品質ゲート6 SP-1）。手元にしかないコミットがあるときは `remote_rewritten` で一時停止し、`resume --adopt-remote` が何も失わずに再開する。
- 利用者の定期のジョブは1つなので、ジョブが別の状態の置き場（別の `XDG_STATE_HOME`）の、登録のあるカタログを同期しているときは、`canonical link` は何も書く前に `CANONICAL_STATE_ROOT_MISMATCH`（終了コード3）で止まり、`canonical remove` はそのジョブを外さず、`canonical status` は警告を示す（最終品質ゲート6 ST-1）。
- 順は、リンクの後に、登録簿 → 基準（手順7）→ ジョブ → すぐの実行と待ち、とする（ジョブを作ると最初の周期がすぐに動くので、基準を先に記録する）。その後にツールの設定の判定を行う。何度実行しても同じ結果になり、2回目は手順6と7で何も書かない。手順6と7の途中の失敗は、それまでの効果を示した `partial`（終了コード6）で返す。
- 書く場所（状態の置き場、ジョブの置き場）に書けないときは、何も書く前に `CANONICAL_SANDBOX_DENIED` で止まる。登録とジョブがそろっていてリンクを置くだけなら、サンドボックスの中でも通る。
- `canonical link --no-schedule` は、手順6を行わない（登録簿に載せず、ジョブを作らず、起動もしない）。手順7の基準は記録し、`state.json` に「定期の実行なし」の印（`"schedule": "none"`）を残す。登録されていないカタログは、そのチェックアウトでの `canonical sync` が処理する。`--no-schedule` を付けない `canonical link` は、印を消して登録する（統括の判断 R1）。
- `worktree create` の後のリンク（I-2 の `link_after_command`）にも、同じ手順6と7が効く。ただし、「定期の実行なし」の印があれば手順6を行わない（統括の判断 R1）。

### R-430-10 `spec-dock canonical remove`（R-B8）

- 対象はこのクローン。`--yes` がなければ、予定だけを示して何もしない（`planned`）。
- 未保存の変更か未pushのコミットがあると `CANONICAL_UNSAVED_CHANGES`、カタログの中に `.runtime/` 以外の無視されたファイルがあると `CANONICAL_IGNORED_FILES_PRESENT`（ファイルの一覧を示す）で、書く前に止まる。
- 外すもの：同じクローンのすべてのチェックアウトの正しいリンク（実体は消さない）、カタログのworktree（unlock して `git worktree remove`）、`info/exclude` の3行、登録簿の項目と状態の置き場のカタログの記録、定期の実行（ほかに登録されたカタログがないときだけ。常駐のプロセスなら止める）。
- 消さないもの：ローカルと GitHub の `spec-dock/canonical`、構造のスナップショット。ダッシュボードの5つのファイルを消すのは I-11 が足す。

### R-430-11 `spec-dock canonical status` の同期の項目（R-B7、R-C6）

- `sync`：定期の実行の仕組みと、その有無と状態（常駐のプロセスなら動いているか）、登録簿に載っているか（載っていなければ「定期の実行なし」と次の1手）、linger（Linux の systemd）、push の認証の結果、最後に成功した同期の時刻、最後の失敗と理由、一時停止の理由。
- `changes`：I-2 の項目に、保留（種類ごとの解き方）、統合を止めているパスとその理由を足す。未pushのコミットが10分を超えたら警告する。
- `git`：I-2 の項目に、登録簿の git（定期の実行が使う git）のパスと版を足す。
- `snapshot`：構造のスナップショットの場所、取得の時刻、最後の確かめの時刻、異常の数。
- 読むだけである。リポジトリ、カタログ、`.git`、状態の置き場、GitHub に書かない。GitHub とリモートに問い合わせない（launchd、systemd の状態を読むコマンドは使う）。

### R-430-12 `canonical sync` の出力（Epic 12章）

- `data.catalogs[]` は、`catalog`、`saved_commit`、`merged`、`pushed`、`conflicts`、`holds`、`blocking`、`skipped_reason`、`paused` を持ち、`data.repositories[]` は、`repository`、`probe`（`unchanged`、`changed`、`failed`）、`refreshed`、`dashboards_written` を持つ。
- カタログの結果は `ok`、`skipped`（排他や周期の重なりで飛ばした）、`paused`、`error` のどれかである。すべて `ok` か `skipped` なら、効果があれば `succeeded`、なければ `unchanged`。`paused` か `error` が1つでもあれば、どこかで効果（保存、統合、push）があれば `partial`（終了コード6）、なければ `failed`（終了コード3）とする（統括の判断 Q7）。

### R-430-13 I-2 から引き継いだ作りかけのカタログの次の1手（RST-1）

- 別の `canonical link` がカタログを作っている最中（管理ディレクトリに `index` がまだなく、`index.lock` がある）に、もう1つの `canonical link` や `canonical status` を実行したとき、「消す」次の1手より先に、「しばらく待って同じコマンドを実行する」を示す。作りかけが残ったまま（`index.lock` もない）なら、今までどおり、確かめてから消す次の1手を示す。

## スコープ

### 対象

- 新しいコマンド `canonical sync`、`canonical accept`、`canonical restore`、`canonical resume`、`canonical remove`（`cli/catalog.py` の一覧、引数、ヘルプ）と、振り分けの表への登録。`canonical link` の `--no-schedule` と手順6・7、`HELP_EFFECTS` の文を Epic の12章のものにする。
- 状態の置き場の部品（登録簿、`state.json`、ログ、常駐のプロセスの記録）、定期の実行の選び方と launchd、systemd、常駐のプロセスの登録、解除、すぐの実行、観察。
- 純粋な規則（保存するパスの選び方、保留の判定、競合の段からの解決の計画、別名ファイルの名前、PC名、状態と登録簿のモデル、定期の実行の選び方とジョブのファイルの中身）。
- `infra/canonical_git.py` への同期の Git の操作の追加（一時のインデックスでの保存、`merge-tree`、`commit-tree`、早送り、push、書き換えの検出、変更の一覧）。
- C11 の systemd のユーザーと linger の判定。
- `canonical status` の `sync`、`snapshot`、`changes` の `state.json` の部分、`git` の登録簿の git、未pushの警告。
- RST-1 の次の1手。
- 配布資産 `docs/reference_cli.md` の新しいコマンドの行と、`static-inventory.json`。
- コマンドの数と一覧を確かめるテストの更新（47 から 52）。

### 対象外

- ダッシュボードの作り直し、`state.json` の `dashboard` の中身、`canonical status` の `dashboard`、`canonical remove` でダッシュボードを消すこと（I-11）。
- `canonical status --structure` と `structure`（I-4）。
- `work finish` の保存の確認と、`work start` からの `link_after_command`（I-5）。この Issue は、I-5 が使う公開の形（すぐの実行の頼み方、`state.json` を読む部品）を作る。
- 利用者向けの文書（`docs/canonical.md` の「同期が止まったとき」を含む）、規則の節、AGENTS.md の破壊的なコマンドへの `canonical remove` の追加（I-9）。利用側の `spec-dock/` の配布資産の更新（I-9、I-10）。

### 親契約として維持する境界

- 従来モード（版3）の処理と、`.meta.json` を読み書きするコードを変えない。版3の振る舞いを確かめるテストは、Epic の `design.md` の testability の「従来モードの回帰」に挙げたもの（コマンドの数と一覧、配布資産の一覧と値、文書の中身）のほかは変えない（AC-15）。版3のリポジトリで新しいコマンドは `CANONICAL_NOT_MIGRATED` で止まる（`canonical sync --registered` は、登録簿にある版4のカタログだけを処理する）。
- C4、C5、C6、C10 の部品と、I-2 の `canonical link` の手順1〜5と8の振る舞いを変えない（RST-1 の次の1手の文を除く）。
- 読むだけのコマンドは、リポジトリ、カタログ、`.git`、GitHub に書かない。`canonical status` は状態の置き場にも書かない。
- `StartLock` と選択の記録の形式を変えない。利用者のツールの設定のファイルを書き換えない。
- テストと実機の確かめで、利用者の `~/.local/state/spec-dock/`、`~/Library/LaunchAgents/`、`~/.config/systemd/user/`、`~/.claude/settings.json`、`~/.codex/config.toml`、本物の GitHub（ラベル、sub-issue、依存、リポジトリ、ブランチの作成）、利用者のほかのリポジトリに触れない。本物の spec-dock のリポジトリで `canonical` のコマンドを実行しない。

## 失敗・境界条件

- **カタログがない、読めない、別のブランチ、マージの途中、形式が書けない、`paused`、登録簿の git が古い**：そのカタログを飛ばし、理由を状態に記録する（`CANONICAL_NOT_LINKED`、`OS_ACCESS_DENIED`、`CANONICAL_GIT_IN_PROGRESS`、`CANONICAL_FORMAT_UNSUPPORTED`、`CANONICAL_GIT_TOO_OLD`）。読めない（`Operation not permitted`）ときは、拒否されたプログラム（spec-dock の Python と、記録した git）を記録する。外付けのボリュームが外れているときも、記録だけを残す。
- **GitHub（origin）につながらない**：接続の失敗として記録し、保存と、手元の取得済みの R との統合だけを行う。コミットはローカルに積む。
- **GitHub の構造（gh）につながらない**：手順7の失敗は `probe.json` に記録するだけで、手順1〜6の結果を変えない。
- **カタログの排他が取れない、同じカタログの別の周期が動いている**：そのカタログを `skipped` で飛ばす。
- **競合の解決が段の規則で表せない**（ディレクトリとファイルの衝突など）：統合を作らず、`merge_failed` で一時停止する（消さない）。
- **push が先に進まれて拒否され続ける**：2回やり直した後は、次の周期に任せる。
- **push の認証の失敗**：保存はローカルに積み、`push_auth` に記録する。
- **新しいリポジトリの作成の続き**（GitHub に canonical がなく、基準もない）：保存してから push で作る。
- **ジョブの登録の失敗**（`launchctl bootstrap` の拒否など）：`canonical link` は `partial`（終了コード6）と `CANONICAL_SCHEDULER_FAILED`、次の1手 `spec-dock canonical link` を返す。
- **常駐のプロセスが止まっている**（コンテナの起動し直し）：`canonical status` が `CANONICAL_RUNNER_STOPPED` と起動の1行を示す。次の `canonical link` で動き直す。
- **linger がない SSH のサーバー**：`canonical link` と `canonical status` が `loginctl enable-linger <ユーザー>` を示す。SpecDock は linger を変えない。
- **状態の置き場が壊れている**（読めない JSON、知らない版）：周期は、壊れた `state.json` を上書きせずにそのカタログを飛ばし、`canonical status` が原因を示す。壊れた登録簿では、`--registered` は何も処理せずに `failed` で止まる。

## 受け入れ条件

各条件は、外のネットワークを使わないテスト（一時の bare のリポジトリ、偽の `gh`、注入した時刻と環境の判定と定期の実行の偽物、一時の `XDG_STATE_HOME`）で確かめる。実機の確かめ（AC-430-21）だけは報告書に書く。

- **AC-430-01（AC-03）**：2つのクローンで同じファイルを変え、両方で `canonical sync` を（必要な回数）実行すると、両方の作業ツリーに、先に push された版が元の名前で、後の版が別名ファイルで残り、競合のマーカーがない。変更と削除の競合では、変更が残る。拡張子のないファイルと `.` で始まるファイルの別名が、規則どおりになる。
- **AC-430-02（AC-10）**：カタログで25件を削除して `canonical sync` すると、削除は保留されて push されず、`state.json` の `holds` に `mass_delete` として残る。`canonical accept --deletions` の後の `canonical sync` で保存され、push される。`canonical restore` で、保留中の削除が HEAD の内容に戻る。`origin: command` の束の25件の削除は保留されずに保存され、`origin: finish` の束の削除は保留される。
- **AC-430-03（AC-11）**：bare のリポジトリで canonical を強制 push で書き換えると、`canonical sync` は取り込まずに `remote_rewritten` で一時停止し、手元のファイルも HEAD も変えない。ブランチを消したときは `remote_deleted`、共通の祖先のない履歴に置き換えたときも一時停止する。`resume --adopt-remote` と `resume --push-local` が、R-430-05 のとおりに再開し、何も消さない。カタログを `git clean -ffdx` で消して `canonical link` で作り直した後も、基準が残り、書き換えを検出する。
- **AC-430-04**：取り込む変更が、手元の未保存のファイルか保留のファイルに当たるとき、`canonical sync` は作業ツリーも HEAD も壊さずに取り込みを次の周期へ持ち越し、`state.json` の `blocking` に、そのパスと理由（`local_edit`、`held`）を記録する。そのファイルを保存した後の周期で、統合される。
- **AC-430-05**：テストのリポジトリに、必ず失敗する `pre-commit`、`post-checkout`、`post-merge`、`pre-push` を置き、`commit.gpgSign=true` を設定しても、保存、統合、push が成功する。
- **AC-430-06**：テストがカタログの排他を持っている間（書きかけの束）の `canonical sync` は、そのカタログを `skipped` にして何も保存しない。誰かがカタログの本当のインデックスに `git add` していても、統合と保存が止まらない。
- **AC-430-07**：`canonical link` が定期の実行に渡す引数に `--state-root <link のときの根の絶対パス>` が入り、`XDG_STATE_HOME` のない環境でその引数のまま `canonical sync --registered` を実行すると、同じ登録簿と状態を読み書きする。
- **AC-430-08（R-B8）**：`canonical remove` は、未保存の変更か未pushのコミットがあると `CANONICAL_UNSAVED_CHANGES`、`.runtime/` 以外の無視されたファイルがあると `CANONICAL_IGNORED_FILES_PRESENT` で、何も書かずに止まる。`--yes` がないと `planned` で何もしない。`--yes` では、R-430-10 のものを外し、ブランチと構造のスナップショットを残す。ほかのカタログが登録されていれば、定期の実行を外さない。
- **AC-430-09（R-C7）**：常駐のプロセスは、2つ目が終了コード0で何もせずに終わり、`kick` で60秒を待たずに周期を動かし、SIGTERM で周期を終えてから止まる。環境の判定を注入して、macOS で `launchd`、systemd の Linux で `systemd`、systemd のない Linux で `loop` が選ばれる。「Failed to connect to bus」の後に試し直して `systemd` を選ぶ。
- **AC-430-10（AC-16 の一部）**：構造が変わっていないとき（新しいスナップショットと、304 を返す偽の `gh`）、1周期が `gh` に送る要求は、304 の確かめだけである。偽の `gh` がつながらなくても、カタログの保存と push の結果は変わらない。手順7は、すべてのカタログの後に、リポジトリごとに1回だけ行い、カタログが一時停止や飛ばされていても行う。
- **AC-430-11**：`canonical link` の後の最初の周期が、送るものがなくても `push --dry-run` を行い、結果を `push_auth` に記録する。認証に失敗する origin では `push_auth.result` が `failed` になり、`canonical status` が、URL の種類に合った次の1手を示す。
- **AC-430-12**：`canonical link --no-schedule` は、登録簿に載せず、偽の launchd、systemd、常駐のプロセスに何も届かない（作成、起動、すぐの実行のどれも）。基準は記録され、そのチェックアウトでの `canonical sync` が、そのカタログを処理する。`canonical status` の `sync` が「定期の実行なし」と次の1手を示す。
- **AC-430-13（R-C2、R-D1）**：注入した時刻で、最後の変更から30秒未満のファイルは保存されず、30秒以上で保存される。変わり続けるファイルは、最初に見つけてから5分で保存される。削除は、最初に見つけてから30秒で保存される。変更の束のパスは、30秒を待たずに、束ごとに1つのコミットで保存され、束のファイルが消える。
- **AC-430-14（R-C4）**：トークンの全体の形に当たるファイルは `secret` で、10 MiB を超えるファイルは `too_large` で保留され、接頭辞だけのファイルは保存される。`canonical accept <パス>` の後は保存され、許可の後に中身を変えると、もう一度保留される。保留にないパスの `canonical restore` は `CANONICAL_NOT_HELD` で止まり、何も書かない。
- **AC-430-15（R-B7、R-C6）**：`canonical status` が、`sync`、`snapshot`、`changes`（保留、`blocking`）、`git`（登録簿の git）を返し、問題ごとに次の1手を示す。未pushのコミットが10分を超えると警告する。実行の前後で、リポジトリ、カタログ、`.git`、状態の置き場が変わらず、`gh` とリモートに要求を送らない。
- **AC-430-16（Epic 3章の手順6・7）**：偽の定期の実行で、`canonical link` が登録簿にカタログを載せ、ジョブを作り、すぐの実行を1回頼み、記録を待つ。記録が見えないとき、`OS_ACCESS_DENIED` のとき、push の認証の失敗のとき、linger がないとき、`loop` のときに、それぞれのコードと次の1手を `warnings` に返す。2回目の `canonical link` は手順6と7で何も書かず、すぐの実行も頼まない。ジョブの登録に失敗すると `partial`（終了コード6）と `CANONICAL_SCHEDULER_FAILED` を返す。書く場所に書けないときは、何も書く前に `CANONICAL_SANDBOX_DENIED` で止まる。mainのチェックアウトを動かした後の `canonical link` が、古い登録簿の項目を消し、基準を新しい鍵へ移す。
- **AC-430-17（RST-1）**：管理ディレクトリに `index` がなく `index.lock` がある作りかけのカタログで、`canonical link` と `canonical status` が「しばらく待って同じコマンドを実行する」を先に示し、何も消さない。`index.lock` もないときは、今までの「確かめてから消す」次の1手を示す。
- **AC-430-18（AC-15）**：版3の振る舞いを確かめる今のテストが、許された変更（コマンドの数と一覧、配布資産の値、文書の中身）のほかは変更なしで通る。版3のリポジトリで、`canonical sync`（`--registered` なし）、`accept`、`restore`、`resume`、`remove` が `CANONICAL_NOT_MIGRATED` で止まり、何も書かない。`canonical sync --registered` はリポジトリによらずに登録簿だけを読み、版3のリポジトリに触れない。公開のコマンドは52個になる。
- **AC-430-19（R-430-12）**：2つのカタログを登録し、片方を一時停止にした `canonical sync --registered` が、もう片方を処理し、`partial` か `failed` を、R-430-12 の規則どおりに返す。`data.catalogs[]` と `data.repositories[]` が、決めた項目を持つ。
- **AC-430-20（C9 の公開の形）**：I-5 と I-11 が使う公開の部品（すぐの実行の頼み方、`state.json` を読む部品と書く部品、手順7の拡張の場所）を、テストが直接呼んで確かめる。すぐの実行の頼み方は、定期の実行の失敗を例外にしない。
- **AC-430-22（統合できない競合と取り込み直し）**：ディレクトリとファイルの衝突など、段の規則で表せない競合（Git が `path~<名前>` などの新しいパスを作るもの）では、`merge_failed` で一時停止し、何もコミットしない。`resume --adopt-remote` の後の周期が、親を R だけにした1つのコミットを作り、手元にしかない中身を残し、消された古い履歴を push しない。R から C への差分に秘密情報らしいもの、大きすぎるファイル、大量の削除があれば、push せずに一時停止のままにし、`holds` と `CANONICAL_SAVE_HELD` を記録する。
- **AC-430-23（push とネットワーク）**：先に進まれて拒否された push を、取得から2回までやり直す。origin につながらない周期は、保存をローカルに積んで `last_error` に `GITHUB_UNAVAILABLE` を書き、つながった次の周期で push する。変更のない周期はコミットしない。保存のコミットのメッセージが `spec-dock: save <件数> files (<PC名>)` で、作者が利用者の Git の設定である。
- **AC-430-24（基準のないクローン）**：GitHub の canonical が消され、手元に中身のある canonical があって基準のないクローンで、`canonical link` が手元の HEAD を基準にし、周期が `remote_deleted` で一時停止して push しない。手元が初期のコミットだけのときは push で作る。GitHub が履歴を巻き戻した後に、状態を失った周期（mainの `git fetch` で追跡の参照が先に動いた）と、`canonical remove` の後のリンクし直しが、落とされたコミットを push せずに `remote_rewritten` で一時停止する。
- **AC-430-25（`--no-schedule` の持続と選び直し）**：`--no-schedule` で用意したクローンの `worktree create` が、手順6を行わない。`--no-schedule` なしの `canonical link` の後は登録される。仕組みを選び直すと、前の仕組みのジョブが外れる。記録した git と実行ファイルが使えるなら、別の `PATH` の `canonical link` でも、登録簿とジョブを書き換えない。
- **AC-430-26（restore の安全）**：保留の後に作り直したファイルと、直して保留に当たらなくなったファイルを、`canonical restore` が上書きしない。
- **AC-430-27（壊れた状態とログ）**：壊れた `state.json` のカタログを、周期が上書きせずに `error` で飛ばし、`canonical status` が原因を示す。壊れた登録簿で `canonical sync --registered` が何も処理せずに `CANONICAL_REGISTRY_UNREADABLE`（終了コード3）で止まる。ログが 1 MiB を超えると1世代を残して切り替わる。
- **AC-430-28（remove と周期の並行、途中の失敗）**：周期がカタログを処理している間の `canonical remove` は、その周期の終わりを待ってから確かめて書く。`canonical remove --yes` の途中の失敗は `partial`（終了コード6）と、効果ごとの結果を返す。
- **AC-430-21（実機の確かめ）**：macOS の launchd（外付けのボリュームと内蔵のディスクの一時のリポジトリ、テスト用の別の名前のジョブ、一時の状態の置き場、一時の bare のリポジトリへの push、本物の URL への存在しない参照名の `push --dry-run` での認証の確かめ、プライバシーの保護の案内）、Linux の systemd のタイマー（OrbStack の Ubuntu の仮想マシン。一時の bare のリポジトリで、AC-02、AC-03 の代わり）、systemd のないコンテナ（Docker。中でクローンした一時のリポジトリで、常駐のプロセスと、起動し直しの後の `canonical link`）の結果を報告書に書く。確かめられなかったことは「未確認」と書く。

## 制約・前提

- Linux と macOS、Python 3.10 以上、Git 2.38 以上（`merge-tree --write-tree`）。手元は Git 2.54.0。
- 定期の同期の周期は60秒、保存の待ちは30秒と5分、保留の閾値（20件、5件かつ10%、10 MiB）、push のやり直しは2回、最初の1回の待ちは15秒、ログは 1 MiB（Epic の 5章）。
- 状態の置き場とジョブの置き場は、テストでは一時ディレクトリにし、ジョブの登録は注入した偽物で行う。
- 実機の確かめでは、GitHub に新しいリポジトリやブランチを作らない。実際の push は一時の bare のリポジトリにだけ行い、利用者の `gh` の認証の到達は、テスト用のジョブの中から、本物の URL（`https://github.com/chemitaro/spec-dock.git`）の存在しない参照名への `git push --dry-run` だけで確かめる。本物の URL を origin にしたカタログで `canonical sync` を動かさない（統括の判断 Q9）。
- AC-13 の `work finish` の保存の確認は I-5 が持つ。この Issue の Linux の実機の確かめは、AC-02 と AC-03 の代わりだけを行う。Epic の未確認の事項「systemd のユーザーのタイマーからの、GitHub への push の認証」は、統括の判断 Q9 のため（Linux から GitHub に push しない）、未確認のまま残る。
- 作業の間、spec-dock のリポジトリは従来モード（宣言の版3）のままである。仕様の文書は、今までどおりコードと一緒にコミットする。

## 未解決事項

利用者と統括の判断が要るものは、今はない（統括の判断 Q1〜Q10、R1〜R3 で決めた）。実装の途中で、Epic の契約を変える必要が見つかったら、推測で埋めずに統括に聞く。
