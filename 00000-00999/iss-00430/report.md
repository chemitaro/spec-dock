---
種別: レポート（Issue）
ID: "iss-00430"
タイトル: "Add Periodic Canonical Sync"
関連GitHub: ["#430"]
最終更新: "2026-10-26"
依存: ["requirement.md", "design.md", "plan.md"]
親: ["epic-00424", "init-00423"]
---

# Result Summary

詳細: [Report Guide](../../../docs/authoring/report.md)

## Outcome

Epic の I-3 として、カタログの保存、統合、push を60秒ごとに行う定期の同期と、その登録、保留への答え、再開、取り外しを足した。契約 C9（状態の置き場の根以外）を持ち、C11 に systemd のユーザーと linger の判定を足した。公開の形は `design.md` の13章のとおりである。

- **`canonical sync`**（Epic の5章の手順1〜7）：1つのカタログの周期を `cycle.lock` の中で、前提 → `ls-remote` と `fetch` と書き換えの検出（排他の外）→ 保存と統合（カタログの排他の中）→ push（排他の外、拒否なら2回までやり直す）→ `state.json` の順に行う。`--registered` は登録簿のすべてのカタログを、1つの失敗でほかを止めずに処理し、最後にリポジトリごとに1回 `ensure_fresh(repository, "cycle")` を行う（ダッシュボードは I-11）。`--loop` は systemd のない環境の常駐のプロセス（1つだけ動き、`kick` ですぐ動き、SIGTERM で周期を終えてから止まる）、`--detach` は切り離して起動する。
  - 保存：変更の束は束ごとに1つのコミットですぐに、ほかは30秒か5分の規則で、一時のインデックスで保存する。保留（今の作業ツリーのすべての削除で数える大量の削除、トークンの全体の形の秘密情報、10 MiB を超えるファイル）は保存しない。確かめたバイト列のままコミットする。
  - 統合：早送りか `merge-tree`。同じファイルの競合は先着（R）を元の名前に、手元を別名ファイルに置き、変更と削除では変更を残す。段の規則で表せない競合（Git が `path~<名前>` を作るもの）は `merge_failed` で止まる。編集中か保留のファイルに当たる取り込みは、何も壊さずに `blocking` に記録して持ち越す。
  - 書き換えと削除：基準の子孫でない R は `remote_rewritten`、基準があって GitHub にないときは `remote_deleted` で止まる。基準がなく手元に中身があるときも作り直さずに止まる。基準のないときは手元の HEAD（初期のコミットだけなら追跡の参照）を基準にする。取り込み直しが終わるまでは push しない。接続できない周期は、追跡の参照が基準の子孫のときだけ統合する。
- **`canonical link` の手順6と7**：登録簿 → 基準 → ジョブ（launchd、systemd のユーザーのタイマー、常駐のプロセス）→ すぐの実行と最大15秒の待ち、の順。記録が見えない、読めない（`OS_ACCESS_DENIED`）、push の認証の失敗、linger がない、常駐のプロセス（起動し直しの1行）を警告で示す。2回目は何も書かない。`--no-schedule` は基準だけを記録し、`state.json` に印を残して、後の `worktree create` でも登録しない（統括の判断 R1）。mainの移動の後は古い項目を消し、基準を新しい鍵へ移す。記録した git とジョブの実行ファイルは、使える間は書き換えない。
- **`canonical accept`、`restore`**：許可は blob の値で `accepted.json` に記録し、中身が変われば効かない。`restore` は、排他の中で取り直して、今も保留に当たるものだけを HEAD から戻す（作り直した、直したファイルは上書きしない。HEAD にないファイルは消さない）。
- **`canonical resume`**：`--adopt-remote` は、親を R だけにした1つのコミットで手元の中身を重ね直し、GitHub が消した古い履歴を送らない。その前に R からの差分に保留の規則を当て、当たれば止まったままにする（統括の判断 R2）。`--push-local` は GitHub の canonical を作り直す。ほかのPCが作り直した後の `remote_deleted` は `--adopt-remote` で再開する。
- **`canonical remove`**：未保存、未push、`.runtime/` 以外の無視されたファイルがあれば書く前に止まり、`--yes` がなければ予定だけを返す。リンク、カタログ、除外の3行、ジョブ（ほかの登録がないとき）、登録簿と状態を外し、ブランチと構造のスナップショットは残す。
- **`canonical status`**：`sync`、`snapshot`、`changes` の保留と `blocking`、`git` の登録簿の git、10分を超えた未pushの警告を足した。何も書かず、GitHub とリモートに問い合わせない。
- **RST-1（I-2 から）**：別の link が作成中（`index.lock` がある）のカタログでは、「しばらく待って同じコマンドを実行する」を先に示す。
- **新しいコード**：`design.md` の14章の表（統括の判断 Q6。Epic の12章への追記は統括）。
- **配布資産**：`docs/reference_cli.md` の C46 の更新と C48〜C52、`static-inventory.json`。公開のコマンドは52個。利用側の `spec-dock/` は変えていない（I-9、I-10）。
- 実現しなかったこと：なし（この Issue の範囲で）。ダッシュボード（I-11）、`work finish` の保存の確認（I-5）、使い方の文書（I-9）は計画どおり対象外。

### 起きたこと：テストが本番の名前の launchd のジョブを一時的に読み込んだ（2026-10-26）

- 実装の途中、既存の I-2 のテストの1つが `monkeypatch.undo()` で、私が置いたテスト用の偽のスケジューラーへの差し替えまで戻した。その後の `canonical link` の手順6が本物の `launchctl bootstrap` を呼び、本番の名前 `io.github.chemitaro.spec-dock.canonical-sync` のジョブを、利用者の gui ドメインに数分間読み込んだ。plist は pytest の一時の `HOME` の下（利用者の `~/Library/LaunchAgents` ではない）、中身は pytest を引数付きで呼ぶもの、状態の置き場もテストの一時ディレクトリだった。
- 直ちに `launchctl bootout` で外し、本番の名前のジョブがないこと（`print` が 113）、`~/Library/LaunchAgents` と `~/.local/state/spec-dock` に何もないこと、同期のプロセスがないことを確かめ、統括に知らせた（msg_7b278f22e3ca）。統括も同じことを確かめた。

### 防ぎ（`tests/conftest.py`）

- **1段目**：テストのセッションの単位で（`monkeypatch` の外で）、スケジューラーの工場、spec-dock の実行ファイル、systemd の判定、15秒の待ちを偽物に替える。テストの中の `undo()` の後も偽物に戻る。テストごとにも記録する偽物を置く。
- **2段目**（統括の指示）：セッションの間、`PATH` の先頭に、呼ばれたら必ず失敗して呼ばれたことを記録する `launchctl`、`systemctl`、`loginctl` の偽物を置き、1度でも呼ばれたらセッションを失敗にする。本物のスケジューラーの単体のテストは、コマンドの実行器を注入して作る。
- 実機の確かめ（別の名前のジョブ）は、この防ぎの外で、明示して行った（下）。

### 起きたこと：テストの1つが手順7で本物の `gh api` を呼んでいた（最終品質ゲート6 Standards ST-4）

- 私が足した `test_an_ssh_origin_refusing_the_key_is_recorded_as_push_auth_failed` は、origin を `git@github.com:example/repo.git` にしていたため、周期の手順7（構造のスナップショット）が本物の `gh api` を `example/repo` に向けて呼んでいた（テストは外に出ない、という決まりに反する。書き込みはなく、読み取りの要求だけ）。
- 防ぎ：`SyncPair` は手順7の `gh api` を既定で失敗させ（必要なテストは自分の偽物を置く）、`isolate_user_state` は `GH_TOKEN`、`GITHUB_TOKEN`、`GH_HOST` などを外す（`gh` の設定は一時の `XDG_CONFIG_HOME` の下になる）。

## Verification

### テスト

- この Issue のテスト：`tests/cli_runtime/test_issue430_*.py`（同期、保留、再開、取り外し、手順6と7、status、版3と公開の部品）、`tests/unit/domain/test_canonical_sync_rules.py`、`test_canonical_sync_state.py`、`test_canonical_scheduler.py`、`tests/unit/infra/test_canonical_state.py`、`test_canonical_git_sync.py`、`test_canonical_schedulers.py`、`test_runtime_environment_service.py`。AC と置き場の対応は `design.md` の testability の表のとおり。
- 最終品質ゲートの `make lint` と全体の `uv run pytest` は、下の「最終品質ゲート」に書く。

### 最終品質ゲート

- 合格した SHA：`a6d81cc84528b7549c78d1d210cef5d2073a8b19`（ゲート10、2026-10-26）。その後のコミットは、この Issue の文書だけ（ゲートはやり直していない）。
- `make lint`：終了コード0（ruff check、ruff format check、mypy がすべて pass）。
- `uv run pytest`：2950 passed、8 skipped、終了コード0（約14分。実行の前後で HEAD と作業ツリーは同じ）。
- レビュー：新しく起こした Standards と Spec のレビューのエージェント（Claude のみ。ChatGPT は使わない）が、`origin/main...a6d81cc84` の差分（主に前の合格からの差分）と、この Issue と Epic の文書をもとにレビューし、どちらも `pass`（P0/P1 なし）。
- PR #452 の CI：`a6d81cc84` で CI、Provider CI（ubuntu-latest のテスト、macOS と Ubuntu の配布の一致）、Commit identity がすべて success。GitHub のマージの状態は READY（観測できる Actions と Commit Status の範囲。外部の CheckRun は数えていない）。
- それまでの経過：ゲート1（`09a229731`）〜7（`9fd6666e2`）は不合格で、指摘の P0/P1 を直し、そのたびに新しいレビューでやり直した。ゲート8（`dd603e74`）は合格したが、PR の Provider CI が ubuntu-latest で6件失敗した（2回目の `canonical link` がジョブを書き直す。merged /usr の `/bin/gh` を記録した gh と取り違えていた）。直した `0e2571f0b` のゲート9は、足したテストが本物の `/usr/bin` に頼る P1 で不合格になり、`a6d81cc84` で根本から直してゲート10に合格した。各ゲートの指摘と対応は `plan.md` の表のとおり。ゲート7と9の lint とテストは、実行の途中で作業ツリーを直したので証拠にしていない。

### 変えた既存のテスト（`git diff origin/main -- tests/`。AC-15）

版3の振る舞いを確かめるテストは変えていない。従来モードのソース（`direct_*.py`、`work_start.py`、`worktree_observation.py` など）にも差分はない。

| ファイル | 変えたこと | 区分 |
|---|---|---|
| `tests/cli_runtime/test_cli_vnext_contract.py` | 数を52にし、一覧に5つのコマンドを足した。テスト名を `..._52_leaf_design` にした | コマンドの数と一覧 |
| `tests/cli_runtime/test_help_completion_vnext.py`、`test_issue413_contract.py`、`tests/integration/test_cli_docs_vnext.py` | 数を52にした | コマンドの数（文書を含む） |
| `tests/cli_runtime/test_issue428_canonical_mode.py` | `_leaf_arguments` に5つのコマンドを足した | canonical モードのテスト |
| `tests/cli_runtime/test_issue429_canonical_link.py` | 最初の link の効果に手順6と7の3つを足し、作成中のカタログのテスト（RST-1）を足した | canonical モードのテスト（I-2） |
| `tests/cli_runtime/test_issue429_canonical_status.py` | `sync` と `snapshot` が実装されたことと、未登録の警告を期待に足し、状態の置き場を「書かない」を前後の digest で確かめる形にした | canonical モードのテスト（I-2） |

### 実機の確かめ（2026-10-26）

- **macOS、launchd**（wheel を内蔵のディスクの一時の venv に入れ、`XDG_STATE_HOME` も一時。統括の判断 Q8）：内蔵のディスク（`/private/tmp`）の2つのクローンと、外付けのボリューム（scratchpad）の1つのクローンを、一時の bare のリポジトリから作り、`canonical link --no-schedule` で用意した。Python の駆動で一時の登録簿に3つを載せ、別の名前のジョブ `local.specdock.test.iss-00430` を、内蔵のディスクの一時ディレクトリの plist から `LaunchdScheduler` で bootstrap した（`ProgramArguments` は本物の `spec-dock canonical sync --registered --state-root <一時>`）。内蔵のディスクのクローンと外付けのボリュームのクローンで書いた仕様が、ジョブの周期で保存、統合、push され、もう1つのクローンに届いた。3つの `state.json` は `ok`、`push_auth` は `ok` だった。
- **利用者の `gh` の認証がジョブの中まで届くこと**（統括の判断 Q9）：別の名前のジョブ `local.specdock.test.iss-00430.auth` の中から、本物の URL `https://github.com/chemitaro/spec-dock.git` の存在しない参照名 `refs/heads/tmp/iss-00430-dry-run` への `git push --dry-run` が、終了コード0で通った。直後の `git ls-remote` で、その参照が GitHub に作られていないことを確かめた。本物の URL を origin にしたカタログで `canonical sync` は動かしていない。
- 後片付け：2つのテスト用のジョブを `launchctl bootout` で外し、plist と一時ディレクトリを消した。本番の名前のジョブ、`~/Library/LaunchAgents` の spec-dock のもの、`~/.local/state/spec-dock` がないことを確かめた。
- **Linux、systemd のユーザーのタイマー**（OrbStack 2.2.5 の Ubuntu 24.04 の仮想マシン `specdock-i3-test`、Git 2.43.0、Python 3.12.3）：仮想マシンの中で作った一時の bare のリポジトリと2つのクローンで、本物の `canonical link`（仮想マシンの中にだけタイマーを置く）を行った。`systemd` が選ばれ、タイマーが動き、直後の1回の記録も15秒以内に見えた（警告なし。linger は yes だったので、linger の警告は出ない）。片方の書き込みが100秒以内にもう片方に届き（AC-02 の代わり）、同じファイルを両方で変えると、両方のクローンに先着の版と別名ファイル（`doc.conflict-specdock-i3-test-<時刻>.md`、中身は後の版）が残り、競合のマーカーがなく、作業ツリーはきれいだった（AC-03 の代わり）。資格情報は写していない。確かめた後に仮想マシンを消した。
- **Docker、systemd のないコンテナ**（`ubuntu:24.04`、中でクローンした一時のリポジトリ）：`canonical link` が `loop` を選んで常駐のプロセスを1つ起動し、`CANONICAL_RUNNER_RESTART` で起動し直しの1行を示した。2つ目の `--loop` は終了コード0の `unchanged` で何もしなかった。周期で書き込みが保存され push された。常駐のプロセスを止めた（コンテナの起動し直しの代わり）後、`canonical status` が `CANONICAL_RUNNER_STOPPED` を示し、もう一度の `canonical link` で動き直した。コンテナは `--rm` で消え、取得したイメージを消した。
- **未確認**：
  - macOS のプライバシーの保護で読めないときの `OS_ACCESS_DENIED` と案内（外付けのボリュームのカタログも、この環境のジョブから読めたため、拒否を再現できなかった。案内の内容はテストで確かめた）。
  - systemd のユーザーのタイマーからの、GitHub への push の認証（統括の判断 Q9 のため、Linux からは GitHub に push しない。Epic の「未確認の事項」に残る）。
  - linger が `no` の実機での警告（仮想マシンは yes だった。判定と警告はテストで確かめた）。
  - Linux の Codex のサンドボックス（Landlock）の中の `flock`（I-2 から引き続き未確認）。
  - launchd の `bootout` の直後の `bootstrap` の EIO（試し直しを入れたが、実機では再現していない）。

## Residual Risks / Follow-ups

- **I-5 へ**：`request_sync_now`、`read_catalog_state`、`CatalogSyncState`（`last_cycle.finished_at`、`remote_contains_head`、`holds`）、`holds_under`、`origin: finish` の束の扱い（`design.md` の13章）。
- **I-11 へ**：`refresh_structures` の中の手順7の拡張の場所、`RepositoryResult.dashboards_written`、`update_catalog_state` と `state.json` の `dashboard`、`canonical remove` にダッシュボードの5つのファイルを足すこと。
- **I-9 へ**：`docs/canonical.md` の「同期が止まったとき」（`resume` の2つの引数、`remote_deleted` で GitHub に戻っているときの `--adopt-remote`）、AGENTS.md の破壊的なコマンドへの `canonical remove`、カタログで手で `git commit` しないこと（手で行ったコミットは保留の規則を通らない）。
- **統括へ**：
  - Epic の12章への新しいコード（`design.md` の14章）の追記、Epic の5章への `state.json` の3つの項目（`adopt_remote_pending`、`schedule`、`last_error.at`）とジョブの `PATH` の `gh` のディレクトリの追記、R2 と R3 の Epic の文書への反映。
  - **R3 の戻し方の順**：「`export-legacy --apply` で戻すブランチを作って push した後、戻す PR をマージする前（各チェックアウトがまだ版4のうち）に、各クローンで `spec-dock canonical remove --yes`」。ほかのPCのクローンも、戻す PR を取り込む前に remove する必要がある（版3のチェックアウトでは canonical のコマンドが止まるため）。
  - 予行演習の `canonical link --no-schedule` も、手順7の基準を、そのときの `XDG_STATE_HOME`（既定は利用者の状態の置き場）に記録する（Epic の決めたとおり）。予行演習で状態の置き場に触れないなら、`XDG_STATE_HOME` を一時ディレクトリにして実行する必要がある。
- 受け入れた結果（最終品質ゲート6 SP-1）：基準のない周期（状態の置き場を消した、根が違う）や、`--no-schedule` から通常の `canonical link` への切り替えのとき、手元に未pushのコミットがあると、GitHub が書き換えられていなくても `remote_rewritten` で止まる。`resume --adopt-remote` で何も失わずに再開する（GitHub が落とした履歴を push し直すより安全な側）。
- **統括の判断を求める（最終品質ゲート8 Standards ST-1、P2）**：GitHub が手元の HEAD の祖先へ巻き戻し、`resume --adopt-remote` の取り込み直しが保留の修正を待っている間に、GitHub でブランチが消されて `remote_deleted` になると、案内どおりの `resume --push-local` が手元の HEAD をそのまま送り、GitHub が消した履歴（秘密情報のコミットを含みうる）が戻る。案：`adopt_remote_pending` か前の理由が `remote_rewritten` のときは `--push-local` を拒否する、または履歴を持たないコミットで作り直す。書き換えの後に削除された場合の `--push-local`（印なし）は、今のテストが意図した動作として固定している。
- 直さずに残るもの（最終品質ゲート10）：テストの `FakeScheduler("loop")` は本物の loop と違い、記録した PATH と `path_tail` を返す（ST-1）。本物の launchd と systemd の後ろとファイルの形で gh の場所の読み戻しを通すテストはない（ST-2。レビューの一時の確かめで、空白や `%`、`$` を含む名前も含めて28の場合が安定した）。
- 直さずに残るもの（最終品質ゲート8）：カタログのツリーにサブモジュールがあると取り込み直しの周期が毎回 `GIT_FAILED`（ST-2）。取り込み直しの保留にも、status の `changes.holds` が通常の保留の次の1手を示す（SP-3）。新しいリポジトリで保存の後の最初の push も失敗すると、次の周期が `remote_deleted` で止まり、`resume --push-local` で戻す（SP-4）。
- 直さずに残るもの（最終品質ゲート7）：カタログの排他で飛ばされ続けた周期にも、`CANONICAL_SYNC_NOT_CONFIRMED` がプライバシーの案内を示す（ST-2）。SIGKILL で止まった loop の `runner.json` が残り、`canonical status` がちょうど `runner.lock` を持った瞬間の `remove` が、再利用された PID に SIGTERM を送りうる狭い競合（ST-3）。毎周期の `git reset -q` は、カタログで手でステージした内容を捨てる（ST-4。設計どおり。カタログで手で Git を使わないことは I-9 へ）。
- 残るリスク（`design.md` の risk）：登録済みのカタログに `--no-schedule` を付けても登録は外れない（SP-10）。launchd の `ExitTimeOut` を超える周期の SIGKILL（次の周期が一時のインデックスと lock を消す）。開発用の venv の `spec-dock` が最初の登録でジョブの実行ファイルになりうる。
