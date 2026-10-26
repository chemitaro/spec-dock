---
種別: 実装計画書（Issue）
ID: "iss-00430"
タイトル: "Add Periodic Canonical Sync"
関連GitHub: ["#430"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00430 Add Periodic Canonical Sync — 実装計画

詳細: [Issue Plan Guide](../../../../../../docs/authoring/issue-plan.md)

## Planning Level

- **選んだ level**：strict（Epic の `plan.md` の指定）。
- **理由**：定期の同期は、利用者の仕様のファイルを、人の操作なしにコミットし、統合し、push する唯一の経路である。誤りは、複数のPCにまたがる仕様の喪失になり、気づきにくく、戻しにくい。状態の置き場の形式（C9）と、I-5、I-11 が使う公開の形を、ここで固定する。
- **risk factor**：作業ツリーへの書き込み（早送り、`restore`）、GitHub への push、利用者の環境のジョブ（launchd、systemd、常駐のプロセス）、並行の Issue（I-4、I-8）との共有のファイル。
- **critical にしない理由**：保存の経路は、作業ツリーを消す操作を、HEAD との差と編集中のファイルとの重なりを確かめた後にしか行わず、push は強制しない。迷う場面（競合の表せない形、書き換え、削除、保留）は一時停止か保留で止まるので、利用者の判断なしに戻せないデータの喪失は起きない設計である。I-10 の前は、利用者の環境に登録もジョブもない。
- **再評価の条件**：秘密情報を扱う範囲が広がる、強制の push や履歴の書き換えが要る、利用者のツールの設定を変える必要が出たときは、critical への引き上げを統括に相談する。

## 目標

`requirement.md` の AC-430-01〜21 を満たし、PR をマージできる状態（CI が通っている）で止まる。I-5 と I-11 が、`design.md` の「公開の形」を変えずに使える。

## 順序・依存

- 起点：`origin/main` の `d5c8cc943`（I-1、I-2、I-7 が入っている）。
- 実装の順は、純粋な規則 → 状態の置き場 → Git の操作 → 1つのカタログの周期 → コマンドの入口 → `canonical link` の手順6・7 → 定期の実行 → accept、restore、resume、remove → status → RST-1 → 配布資産と一覧のテスト、である。各 step を Red → Green → Refactor で進め、区切りでコミットする。
- 並行：I-4（`iss-00431`）と I-8（`iss-00435`）が別の worktree で進む。`cli/catalog.py`、`commands/canonical_dispatch.py`、コマンドの数と一覧のテスト、`static-inventory.json`、`docs/reference_cli.md` で衝突しうる。先に `main` に入った方を、`origin/main` の merge で取り込む（rebase しない）。コマンドの数は、`main` の今の数に、この Issue の5つを足して直す。
- 最終の品質の関門の前に、`origin/main` をこのブランチに merge する。

## 実装step

| step | 内容 | 確かめるAC |
|---|---|---|
| S1 | `domain/canonical_sync_rules.py`：`select_paths`、`classify_holds`、`SECRET_PATTERNS`、`resolve_conflicts`、`conflict_copy_name`、`pc_name` を、テストを先に書いて作る | AC-430-01（名前と段）、13、14 |
| S2 | `domain/canonical_sync_state.py`（`CatalogSyncState`、`SyncRegistry`、`AcceptedChanges`、`RunnerRecord`、`state_key`、`holds_under`）と `domain/canonical_scheduler.py`（`select_scheduler`、plist、ユニット、引用、起動し直しの1行） | AC-430-09（選び方）、20 |
| S3 | `infra/canonical_state.py`、`infra/canonical_registry.py`：一時ファイルと `rename`、短い排他、`cycle.lock`、ログの切り替え、壊れたファイルの扱い | AC-430-07、20 |
| S4 | `infra/canonical_git.py` に同期の操作を足す（一時のインデックスの保存、`merge-tree`、解決、`commit-tree`、早送り、push と dry-run、祖先、差分、`restore`、無視されたファイル、途中の操作）。一時の bare のリポジトリで確かめる | AC-430-01、05、06 |
| S5 | `application/canonical_sync.py`：`sync_catalog`、`run_cycle`、`refresh_structures`。保存、保留、統合、持ち越し、書き換えと削除の検出、push、記録 | AC-430-01〜06、10、11、13、19 |
| S6 | `cli/catalog.py`、`cli/options.py`、`commands/canonical_dispatch.py`：`canonical sync`（`--registered` はリポジトリによらない振り分け）と、accept、restore、resume、remove の入口、引数の誤り、ヘルプ。コマンドの数と一覧のテストを52に直す | AC-430-18、19 |
| S7 | `infra/runtime_environment.py` の C11 の追加と `detect_service_manager`。`infra/canonical_scheduling.py` と3つの実装（launchd、systemd、loop）、`run_loop`、`detach`、`spec_dock_executable` | AC-430-09 |
| S8 | `application/canonical_schedule.py` と `canonical_link.py` の手順6・7、`--no-schedule`、移動の扱い、警告、`request_sync_now` | AC-430-07、12、16、20 |
| S9 | `application/canonical_hold.py`（accept、restore）、`canonical_resume.py`、`canonical_remove.py` | AC-430-02、03、08、14 |
| S10 | `canonical_status.py` の `sync`、`snapshot`、`changes`、`git`、未pushの警告 | AC-430-11、12、15 |
| S11 | RST-1（`canonical_catalog.py` の作りかけの観察と次の1手） | AC-430-17 |
| S12 | 配布資産 `docs/reference_cli.md`（C46 の更新と C48〜C52）、`static-inventory.json`、版3の回帰のテスト（新しいコマンドが `CANONICAL_NOT_MIGRATED`） | AC-430-18 |
| S13 | 独立レビュー②（`code-review` の Standards と Spec）と、その指摘の分析と修正 | すべて |
| S14 | 実機の確かめ（macOS の launchd、OrbStack の Ubuntu、Docker）と後片付け | AC-430-21 |
| S15 | `origin/main` の merge、最終の品質の関門（push した SHA で `make lint`、`uv run pytest`、新しい2つのサブエージェントのレビュー）、`report.md`、PR、CI | すべて |

- 各 step のテストは、`design.md` の testability の表の置き場に書く。テストは外のネットワークを使わない（偽の `gh`、bare のリポジトリ、一時の `XDG_STATE_HOME`、偽の定期の実行）。
- 実装の途中で、Epic の契約（C1〜C11）や Issue の分け方を変える必要が見つかったら、推測で埋めずに Orca の `ask` で統括に聞く。

## 検証

- **毎回**：変えた範囲のテストを、step ごとに走らせる。全体の `uv run pytest` と `make lint` は、最終の品質の関門で、push した SHA で1回走らせる（統括の依頼の「トークンの節約」。Epic の「毎回 `make lint` と `uv run pytest` を通す」は、PR ごとに関門で満たす）。
- **negative test**：要件の「失敗・境界条件」の各行に、少なくとも1つのテストを置く（カタログがない、読めない、途中の操作、形式、git の版、origin につながらない、`gh` につながらない、排他、周期の重なり、表せない競合、push の拒否、認証の失敗、ジョブの登録の失敗、常駐のプロセスの停止、壊れた `state.json` と登録簿、サンドボックスの代わりの書けない場所）。
- **従来モードの回帰（AC-15）**：`git diff origin/main -- tests/` で、変えた既存のテストが、許された区分（コマンドの数と一覧、配布資産の値、文書の中身）と canonical モードのテストだけであることを確かめ、報告書に一覧で書く。従来のソース（`direct_*.py`、`work_start.py`、`worktree_observation.py` など）に差分がないことを確かめる。
- **書かないことの確かめ**：`canonical status` の前後で、リポジトリ、カタログ、`.git`、状態の置き場の `tree_digest` が同じであること。
- **実機**：`design.md` の testability の「実機の確かめ」。結果と未確認のものを報告書に書く。

## rollback

- マージの前：ブランチを捨てるか、コミットを revert する。
- マージの後で、I-10 の前：PR を `git revert` する。利用者の環境には、登録簿もジョブもない（テストと実機の確かめは一時の置き場で行う）。
- I-5、I-11 がこの部品を使った後：forward recovery で、この部品を直す PR を作る。公開の形を変える必要は、Epic の `design.md` とこの `design.md` を先に直す。
- 実機の確かめで作ったもの（一時のリポジトリ、テスト用のジョブ、plist、仮想マシン、コンテナ、イメージ）は、確かめた後に消す。
- **migration**：N/A。状態の置き場の形式は版1で始まり、利用者の環境にはまだ何もない（0.3.0 の前）。

## security / privacy / operability

- **security**：秘密情報らしいファイルを保存しない（保留）。ログにファイルの中身を書かない。資格情報を仮想マシンやコンテナに写さない。push は強制しない。
- **privacy**：macOS のプライバシーの保護の許可を、SpecDock は変えない。案内だけを示す。
- **operability**：`canonical status` が、定期の実行の有無、最後の成功と失敗、一時停止、保留、未pushを示す。ログは 1 MiB で切り替える。
- **observability**：`canonical sync --json` の `data.catalogs[]` と `data.repositories[]`、`state.json`、ログ。

## 統括の判断（2026-10-26、Orca の `ask` の答え）

この答えを Epic の文書より優先する正本とする。新しいコード（Q6、Q1）の Epic の12章への追記は、統括が後で行う。

- **Q1**：`canonical restore <パス>` は、`state.json` の `holds` にあるパスだけを対象にし、ほかは何も書かずに `CANONICAL_NOT_HELD`（終了コード3）で止まる。パスなしは、保留中の削除をすべて HEAD から戻す。
- **Q2**：大量の削除は、その周期で選んだ削除ではなく、今の作業ツリーにある、`origin: command` の束にない削除のすべてで数え、閾値を超えたらすべてを保留する（止まる側）。
- **Q3**：`resume --adopt-remote` の後で共通の祖先がないときは、`merge-tree --allow-unrelated-histories` で L と R を統合する（同じパスは段の規則で R を元の名前、L を別名ファイル。何も消さない）。`--allow-unrelated-histories` は、resume が `state.json` に残す一度きりの印があるときだけ使い、ほかは `merge_failed` で一時停止のまま。「親を L と R の2つにする」は R2 で置き換えた。
- **Q4**：同じカタログの周期の重なりを、`<根>/catalogs/<鍵>/cycle.lock` への `flock(LOCK_EX|LOCK_NB)` で防ぎ、取れなければ `skipped` でそのカタログを飛ばす（カタログの排他とは別）。
- **Q5**：`state.json` の `push_auth` がないか `result` が `unknown` のとき、その周期で `push --dry-run` を行う。`canonical link` の手順7で `state.json` を作るときは、`push_auth` を `unknown` にする。
- **Q6**：新しいコード（`design.md` の14章）を、この Issue の `design.md` に、名前、終了コード、次の1手の表で書く。status の一時停止と保留は、既存の `CANONICAL_PAUSED` と `CANONICAL_SAVE_HELD` を警告として使う。
- **Q7**：`canonical sync --registered` のカタログの結果を `ok`、`skipped`、`paused`、`error` に分け、`paused` と `error` を失敗とする（`skipped` は失敗にしない）。
- **Q8**：実機の launchd は、`canonical link --no-schedule` で用意し、別の名前（`local.specdock.test.iss-00430`）のジョブを、内蔵のディスクの一時ディレクトリの plist から、名前と置き場所を引数で注入したスケジューラーの部品を呼ぶ小さな Python の駆動で bootstrap する。`ProgramArguments` は本物の `spec-dock canonical sync --registered --state-root <一時>`。終わったら `bootout` と削除。
- **Q9**（修正）：GitHub に新しいリポジトリやブランチを作らない。実際の push は一時の bare のリポジトリにだけ行う。利用者の `gh` の認証が launchd のジョブの中まで届くことは、そのテスト用のジョブの中で、本物の URL（`https://github.com/chemitaro/spec-dock.git`）への、存在しない一時の参照名（例 `refs/heads/tmp/iss-00430-dry-run`）の `git push --dry-run` だけで確かめる。本物の URL を origin にしたカタログで `canonical sync` を動かしてはならない。
- **Q10**：C11 の systemd と linger は、`detect_runtime_environment()` には足さず、`RuntimeEnvironment` に既定 None の項目を足し、`canonical link` の手順6と `canonical status` だけが呼ぶ `detect_service_manager(environment)` で埋める（注入できる）。

### 2回目（文書の独立レビュー①の後、2026-10-26）

- **R1**：`canonical link --no-schedule` は、`state.json` に `"schedule": "none"` を記録し、`link_after_command` はその印があれば手順6を行わない。`--no-schedule` なしの `canonical link` は印を消して登録する。`state.json` の版は1のまま。
- **R2**：`resume --adopt-remote` の後は、L と R を統合した、親が R だけのコミット C を作り、`reset --keep` で手元のブランチを移し、push は R からの早送りにする。GitHub が消した古い履歴は送らない。Q3 の「2つの親」は、これで置き換える。さらに、C を push する前に、R から C への差分に保留の規則（秘密情報らしいもの、大きすぎるファイル、大量の削除）を当て、当たったら push せずに保留（一時停止のまま）にする（L で変えたファイルが R で消されていると、「変更が残る」規則で戻ってくるため）。テストを足す。
- **R3**：Epic の「戻し方」の順を、「`export-legacy --apply` で戻すブランチを作って push した後、戻す PR をマージする前（各チェックアウトがまだ版4のうち）に、各クローンで `canonical remove --yes`」にする（案A）。I-3 のコードは変えない。ほかのPCのクローンも、戻す PR を取り込む前に remove する必要がある。Epic の「戻し方」の直しは統括が行い、I-3 の報告書にこの順を書く。
- そのほかのレビューの指摘（restore の取り直し、基準のないクローン、手順の順 6a→7→6b→6c、古い仕組みのジョブの外し方、登録簿の git と実行ファイルを書き換えないこと、ジョブの `PATH` の `gh`、`merge-tree` の `path~<名前>` の検出、remove と移動の `cycle.lock`）は、案のとおりでよい（同じ答え）。

### 文書の独立レビュー①の指摘の対応（2026-10-26）

| 指摘 | 重さ | 対応 |
|---|---|---|
| 1 基準のないクローンが消された canonical を作り直す | blocker | 手順7で手元の HEAD を基準にし、周期は手元が初期のコミットだけのときにだけ作る（AC-430-24） |
| 2 restore が作り直したファイルを上書きする | blocker | 排他の中で取り直し、今も当たる保留だけを戻す（AC-430-26） |
| 3 手順6と7の順 | major | 6a→7→6b→6c、`<根>` の排他を 6a から 6b まで持つ |
| 4 `--no-schedule` の持続 | major | R1（AC-430-25） |
| 5 取り込み直しが古い履歴を送る | major | R2（AC-430-22） |
| 6 remove と移動と周期の並行 | major | `cycle.lock` を取ってから（AC-430-28） |
| 7 選び直しで古いジョブが残る | major | 選び直す前に前の仕組みを外す（AC-430-25） |
| 8 周期の結果の分け方 | major | `design.md` 8章の表 |
| 9 表せない競合 | major | 解決後のツリーのパスを L、R、別名ファイルと比べて `merge_failed`（AC-430-22） |
| 10 受け入れ条件の抜け | major | AC-430-22〜28 を足し、AC-430-15 の確かめ方を書いた |
| 11 実機の launchd が空の登録簿を読む | major | 駆動で一時の登録簿に載せる |
| 12 環境で git と実行ファイルが入れ替わる | major | 記録したものが使える間は書き換えない |
| 13 版3との書き分け | minor | AC-430-18 を書き分けた。戻し方は R3。版3の回帰は新しいテスト `test_issue430_legacy.py` で確かめる |
| 14 実機の範囲 | minor | AC-13 は I-5、systemd から GitHub への push の認証は未確認として残す（要件の制約） |
| 15 常駐のプロセスの起動とログ | minor | 起動の試し直し、出力を `DEVNULL` に |
| 16 途中で止められたとき | minor | 失敗の表を直し、`--registered` の1回の実行も SIGTERM を周期の終わりまで遅らせる |
| 17 同時の link のジョブの登録 | minor | 3と同じ |
| 18 ジョブの `PATH` の `gh` | minor | `gh` のディレクトリを足す |
| 19 シグネチャと番号 | minor | 直した |
| 20 plan の判断の記録 | minor | 「検証」と「Planning Level」に書いた |
| 21 残るリスク | minor | `design.md` の risk に足した。予行演習の手順7が状態の置き場に書くのは Epic の決めたとおり（`--no-schedule` でも基準を記録する）で、報告書で統括に伝える |

### 実装の独立レビュー②の指摘の対応（2026-10-26、`dedfdcc03`）

Standards（ST）と Spec（SP）の2つのサブエージェントのレビューを、まとめて分析して直した。統括の判断が要るものはなかった。

| 指摘 | 重さ | 対応 |
|---|---|---|
| SP-1、ST-1 `--dry-run` が無視されて保存、push、上書きする | P0、P1 | 4つのコマンドで `--dry-run` を、`sync` と `resume` で `--offline` を使い方の誤りにした。テストを足した |
| SP-2、ST-2 接続できない周期が、書き換えられた追跡の参照を取り込む | P1 | 基準の子孫のときだけ統合する。テストを足した |
| SP-3 `remote_deleted` のもう1台が再開できない | P1 | GitHub に戻っていれば `--adopt-remote` で再開する。テストを足した |
| SP-4 2回目の link が `state.json` を書き直す | P1 | 変わらなければ書かない。読み取り専用の状態の置き場で通るテストを足した |
| ST-3 入れ子のリポジトリで保存が止まる | P2 | ファイルとシンボリックリンクだけを保存する |
| ST-4、SP-11 周期の記録が並行の `schedule` を上書きする | P2、P3 | 読み直した値を残す |
| ST-5、SP-5 一時停止の理由が消える | P2 | 止まったときの `last_error` を残し、結果のコードを理由にした |
| ST-6 壊れた登録簿と状態でトレースバック | P2 | 既存のコードに変えた |
| ST-7 常駐のプロセスが黙って止まる | P2 | 周期の例外をログに書いて続ける |
| ST-8 殺された周期の lock で以降が失敗する | P2 | 周期の初めに一時のインデックスと lock を消す。`ExitTimeOut` は Epic の plist の形を変えないため足さない（risk に記録） |
| ST-9 launchd の登録と解除の脆さ | P2 | `bootstrap` の試し直し、`bootout` の拒否を誤りにする |
| SP-6 remove の途中の失敗でジョブが残る | P2 | ジョブを外してから登録簿を書く |
| SP-7 予定だけの remove が状態の置き場に書く | P3 | `--yes` のときだけ `cycle.lock` を取る |
| SP-8 ジョブの登録の失敗が `failed` になる | P3 | 効果を `unknown`（ファイルは書いたかもしれない）にして `partial` |
| SP-9 確かめた中身とコミットする中身がずれうる | P3 | 確かめたバイト列をコミットする |
| SP-10 登録済みに `--no-schedule` を付けても外れない | P3 | 残るリスクとして記録（外すのは `canonical remove`） |
| SP-12 取り込み直しが許可済みのものをもう一度保留する | P3 | 直さない。GitHub が消したものが戻る場面なので、もう一度確かめるのが止まる側として正しい |
| ST の P3（終了の要求の後の手順7、remove の確かめの順、`scandir`、`write_atomic` の fsync、一時ファイル、未使用の引数、docstring） | P3 | 直した。push の拒否が続いたときの `ok` は 8章の表のとおりで変えない |
| SP の AC の不足（名前の変更の競合、`held` の持ち越し、初期のコミットの作り直し、記録した実行ファイル、スナップショットが残ること） | — | テストを足した |

### 最終品質ゲート1の指摘の対応（`09a229731`、2026-10-26）

ゲート1は不合格（`make lint` の mypy がテストの型の誤りで失敗。レビューの P1 が2件）。全体の `uv run pytest` は通っていた（2905 passed、8 skipped）。

| 指摘 | 重さ | 対応 |
|---|---|---|
| lint：テストの3つのファイルの型の誤り | 失敗 | 直した |
| ST-1 確かめたバイト列のコミットが `.gitattributes` のフィルタを通らない（eol で毎分の空のコミット、LFS や git-crypt の平文） | P1 | `hash-object --path` でフィルタを当て、親と同じツリーならコミットしない。テストを足した |
| SP-1 期限の切れた削除の許可が残り、後の大量の削除が保留されない | P1 | 今は削除されていない許可を周期が消す。テストを足した |
| ST-2 `merge.verifySignatures` と `merge.autoStash` で取り込みが止まる | P2 | 早送りで無効にした。テストを足した |
| SP-2 別の `PATH` の link がジョブの `gh` のディレクトリを書き直す | P2 | 置いてあるジョブの `PATH` の `gh` を残す。テストを足した |
| SP-3 `canonical sync --json` の形が `data.result.catalogs` | P2 | Epic の12章のとおり `data.catalogs[]` と `data.repositories[]` にした（`CanonicalCycleData`） |
| ST-3、SP-8 systemd の `KillMode` と launchd の `ExitTimeOut` | P2、P3 | Epic のユニットと plist の形を変えないので直さず、risk に記録して統括に報告 |
| ST-4、SP-5 ログと移動の排他の取り合い | P3 | ログを専用の lock ファイルにした |
| ST-5、SP-9 外したカタログの状態を周期が作り直す、remove の書き込みの確かめの順 | P3 | 周期が登録簿を読み直して飛ばす。remove は排他の前に書き込みの可否を確かめる |
| SP-4 `--no-schedule` で main を動かすと基準が移らない | P3 | 予定のときにも状態を移す。テストを足した |
| SP-6 直した後も `push_auth: failed` が残る | P3 | `failed` の間も毎周期 dry-run で確かめる。テストを足した |
| SP-7 表にないコード、`run_cycle` の例外の記録 | P3 | `design.md` の14章に足した。例外はログと `data.catalogs[].error` に残す（`state.json` には書かない。壊れた周期の途中の状態を書かないため） |
| ST-6 エディタの一時ファイル | P3 | C5（I-2）の `.gitignore` の話なので申し送る |
| ST-7、SP-10 読めない束のログ、許可と比べる中身とコミットする中身 | P3 | ログに書く。許可と比べる blob を、コミットするバイト列から求める |
| `--loop` と `--detach` の CLI のテスト | P3 | 足した |

### 最終品質ゲート2の指摘の対応（`c68698ad8`、2026-10-26）

ゲート2は不合格（Spec のレビューの P1 が2件）。`make lint` と全体の `uv run pytest` は通っていた（2913 passed、8 skipped）。Standards のレビューには P0 と P1 がなかった。

| 指摘 | 重さ | 対応 |
|---|---|---|
| SP-1 取り込み直しで止まった大量の削除が `accept --deletions` で解けない | P1 | 取り込み直しの間は削除の許可を消さない。テストを足した |
| SP-2 SSH や非公開の https の認証の失敗が「接続の失敗」になり、`push_auth` に記録されない | P1 | `ls-remote` と `fetch` の失敗も認証の失敗として判定する。偽の `ssh` のテストを足した |
| SP-3 状態のない周期が書き換えを取り込む | P2 | 手順7と同じ規則で基準を決める。テストを足した |
| SP-4 バスに届かないだけで `loop` に選び直す | P2 | 不明として前の選択を保つ。テストを足した |
| ST-1 予期しない例外が `state.json` に残らない | P2 | `SYNC_FAILED` を記録する。テストを足した |
| ST-2、SP-5 `.runtime/` を `.gitignore` の1行だけで守っている | P2、P3 | 保存から常に除き、取り込みに含まれていれば止まる。テストを足した |
| ST-3 SIGKILL で残った `index.lock` | P2 | 途中の操作（`CANONICAL_GIT_IN_PROGRESS`）として扱い、消し方を案内する |
| ST-4 push が `HEAD` を送る | P3 | 確かめた SHA を送る |
| ST-5 外のパスの `restore` が汎用の誤り | P3 | `CANONICAL_NOT_HELD` にした。テストを足した |
| ST-7 同じ周期で認証を2回確かめる | P3 | push した周期は dry-run をしない |
| SP-6 `canonical status` の `HELP_EFFECTS` | P3 | Epic の12章の文にした |
| SP-7 `--offline` の link が周期を頼む | P3 | すぐの実行を頼まない。テストを足した |
| ST-9 の `$` の引用、ST-10 の表の名前 | P3 | 直した |
| ST-6 別のリポジトリの link と remove の競合、ST-8 launchd の `kickstart` の終了コード、ST-9 の層の分け方 | P3 | 直さずに残るリスクとして報告書に書く |

### 最終品質ゲート3の指摘の対応（`3d321b13a`、2026-10-26）

ゲート3は不合格（Standards の P1 が1件、Spec の P0 が1件と P1 が1件）。`make lint` と全体の `uv run pytest` は通っていた（2921 passed、8 skipped）。

| 指摘 | 重さ | 対応 |
|---|---|---|
| Standards ST-1、Spec SP-1 無視されたローカルのファイルが早送りで黙って上書きされる | P1、P0 | 重なりの確かめに無視されたファイルを入れ、早送りに `--no-overwrite-ignore` を付けた。テストを足した |
| Spec SP-2 ディレクトリの名前の変更と新しいファイルの衝突で `merge_failed` から抜けられない | P1 | `merge.directoryRenames=false` で統合する。テストを足した |
| Standards ST-2、Spec SP-3 `core.fileMode=false` で実行ビットを付けてしまう | P2 | `git add` が決めたモードを使う。テストを足した |
| Spec SP-4 カタログが別のブランチにあるときの remove | P3 | 書く前に止まる。テストを足した |
| Spec SP-5 systemd の `Environment=` の `$`、`refresh_structures` を直接呼ぶテスト | P3 | `$$` は `ExecStart=` の中だけにした。テストを足した |
| Standards ST-3 端末の Ctrl-C が git の子プロセスを止める、常駐のプロセスが止める要求を各カタログに渡さない | P3 | 直さずに残るリスクとして報告書に書く（データは失われず、次の保存と統合で戻る） |
| Standards ST-4 中断した remove が空の状態のディレクトリを残す | P3 | 直さない（害は小さい） |

### 最終品質ゲート4の指摘の対応（`10d08b4e4`、2026-10-26）

ゲート4は不合格（Standards の P1 と Spec の P1。同じもの）。`make lint` と全体の `uv run pytest`（2926 passed、8 skipped）は通ったが、実行中に作業ツリーを直したため、この SHA の証拠としては使わない。

| 指摘 | 重さ | 対応 |
|---|---|---|
| Spec SP-1、Standards ST-2 書き換えで止まった後にブランチが消されると `resume` が堂々巡りになる | P1 | 引数を今の GitHub の状態で決める。テストを足した |
| Spec SP-2、Standards ST-1 ディレクトリをファイルや外を指すリンクに置き換えると周期全体が止まる | P2 | Git の報告で削除を判定し、親がリンクかファイルのパスは削除とする。テストを2つ足した |
| Spec SP-3 確かめた後に消えたファイルが削除として保存されうる | P3 | 確かめたバイト列で保存する |
| Spec SP-4、Standards ST-3 取り込み直しの許可の比べ方 | P3 | 作業ツリーのフィルタなしの blob で比べる |
| Standards ST-4 翻訳された Git のメッセージ | P3 | 判定に使う呼び出しを `LC_ALL=C` で行う |
| Standards ST-5 application の `subprocess`、`request_sync_now` の実行ファイル | P3 | 直さずに残るリスクとして報告書に書く |

### 最終品質ゲート5の指摘の対応（`cf874bdbd`、2026-10-26）

ゲート5は不合格（Spec の P0 が2件と P1 が1件、Standards の P1 が1件）。`make lint` と全体の `uv run pytest`（2930 passed、8 skipped。実行の後も HEAD と作業ツリーは同じ）は通っていた。

| 指摘 | 重さ | 対応 |
|---|---|---|
| Spec SP-1 ファイルをディレクトリに置き換えると、中の保留中の秘密情報が `git add` で広がって push される | P0 | 削除は名前のとおりに外し、選んだパスの外が変わるツリーはコミットしない。テストを足した |
| Spec SP-2 `restore` が、戻す場所の新しいファイルやディレクトリを消す | P0 | 場所と親を確かめて、当たれば戻さない。テストを足した |
| Spec SP-3 ディレクトリをファイルに置き換えると、保留中の大量の削除が push される | P1 | SP-1 と同じ守りで、ファイルの保存を持ち越す。テストを足した |
| Standards ST-1 取り込み直しで、直したが未保存のファイルを許可すると古い秘密情報が push される | P1 | push する中身で許可と比べる。テストを足した |
| Standards ST-3 一度も取得していないカタログを remove できない | P3 | 初期のコミットだけなら未pushとしない。テストを足した |
| Spec SP-4 remove が周期を10秒しか待たない | P3 | 150秒にした |
| Standards ST-2 `merge_failed` を直した後に2回の resume が要ることがある | P2 | 直さずに残る（I-9 の「同期が止まったとき」に、待ってからもう一度 `resume` することを書く） |
| Standards ST-4、ST-5、ST-6 | P3 | 直さずに残るリスクとして報告書に書く（ST-6 の `--detach` の CLI のテストは足してある） |

### 最終品質ゲート6の指摘の対応（`40beddba3`、2026-10-26）

ゲート6は不合格（Spec の P1 が1件、Standards の P1 が1件）。`make lint` と全体の `uv run pytest`（2935 passed、8 skipped。実行の後も HEAD と作業ツリーは同じ）は通っていた。

| 指摘 | 重さ | 対応 |
|---|---|---|
| Spec SP-1 基準のないとき（remove の後のリンクし直し、状態を失った周期とmainの `git fetch`）に、書き換えの後の追跡の参照を基準にして、GitHub が落とした履歴を push し直す | P1 | `initial_baseline` を、手元の HEAD（初期のコミットだけなら追跡の参照）にした。要求と設計を直し、2つの道のテストを足した（直す前は失敗した） |
| Standards ST-1 別の状態の置き場からの `canonical link` が、1つだけのジョブの `--state-root` を黙って付け替える | P1 | ジョブが記録した根を読み、違って登録があれば何も書く前に `CANONICAL_STATE_ROOT_MISMATCH` で止める。remove はジョブを外さず、status は警告を示す。テストを足した |
| Standards ST-2 周期の記録が止まっても status が警告しない | P2 | 最後の周期が5分より古ければ `CANONICAL_SYNC_NOT_CONFIRMED` を示す。テストを足した |
| Standards ST-3 選んだ削除が保存の前に作り直されると、確かめていない中身が入る | P2 | 選んだ削除は名前で外す（`save_commit(deletions=...)`）。テストを足した |
| Standards ST-4 SSH の origin のテストが手順7で本物の `gh api` を呼ぶ | P2 | `SyncPair` は手順7の `gh api` を既定で失敗させ、`isolate_user_state` は `GH_TOKEN` などを外す |
| Spec SP-3 保存のメッセージの件数が、持ち越したパスを含む | P3 | 実際にコミットした件数にした。テストを足した |
| Spec SP-4 clean の filter のあるファイルを許可しても、取り込み直しが保留のまま | P3 | 作業ツリーのファイルがコミットする中身と同じときは、filter なしの値で比べる。テストを足した（直す前は失敗した） |
| Standards ST-6 移動の状態が読めないとき `LOCAL_IO_FAILED`、`move_catalog_state` の assert | P3 | `CANONICAL_STATE_UNREADABLE` にし、assert をやめた |
| Standards ST-7 `.runtime` の `merge_failed` と、取り込み直しの大量の削除の次の1手 | P3 | 専用の次の1手を足し、status は一時停止の次の1手にそれを使う |
| Spec SP-2 `--offline` の link でも最初の周期が動く | P3 | 設計に書いた（`--offline` はこのコマンドの通信だけを止める） |
| Standards ST-5 `REMOVE_CYCLE_WAIT` の説明 | P3 | 説明を実際に合わせた（値は150秒のまま。待ちきれなければ何も書かずに `CANONICAL_LOCK_BUSY`） |

## exit / handoff

- **完了の条件**：AC-430-01〜20 をテストで確かめ、AC-430-21 の実機の結果（または未確認）を報告書に書き、最終の品質の関門に合格し、PR がマージできる状態（CI が通っている）で止まる。マージは人が行い、`work finish` は統括の指示で行う。
- **後の Issue への引き渡し**：
  - I-5：`request_sync_now`、`read_catalog_state`、`CatalogSyncState`（`last_cycle.finished_at`、`remote_contains_head`、`holds`）、`holds_under`、`origin: finish` の束の扱い（`design.md` 13章）。
  - I-11：`refresh_structures` の中の手順7の拡張の場所、`RepositoryResult.dashboards_written`、`update_catalog_state` と `state.json` の `dashboard`、`canonical remove` にダッシュボードの5つのファイルを足すこと。
  - I-9：`docs/canonical.md` の「同期が止まったとき」（`resume` の2つの引数）、AGENTS.md の破壊的なコマンドへの `canonical remove`、新しいコードの一覧の確認。
  - 統括：`design.md` の14章のコードの Epic の12章への追記、`state.json` の3つの追加の項目（`adopt_remote_pending`、`schedule`、`last_error.at`）とジョブの `PATH` の `gh` の Epic の5章への追記、R2 と R3 の Epic の文書への反映。
- **残るリスク**：`report.md` に書く（実機で確かめられなかったもの、Linux の Codex のサンドボックスでの `flock` など）。
