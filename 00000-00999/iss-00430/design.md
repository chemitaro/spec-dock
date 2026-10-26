---
種別: 設計書（Issue）
ID: "iss-00430"
タイトル: "Add Periodic Canonical Sync"
関連GitHub: ["#430"]
状態: "draft"
最終更新: "2026-10-26"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00430 Add Periodic Canonical Sync — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

この設計書は、Epic の `design.md` の5章（定期の同期の全体）、3章の手順6・7・`--no-schedule`・`canonical remove`、2章の C10 のうち周期の手順7、4章の変更の束を読む側を、この repo のコードの置き場と公開の形に落とす。Epic の文書が決めた振る舞いは言い換えず、ここでは置き場、関数、データの形、判断の細部を決める。統括の判断（`plan.md`）を Epic の文書より優先する。

## 設計目標

- **編集を失わない**：保存、統合、取り込みの各段で、作業ツリーのファイルを消す、上書きする操作を、HEAD との差を確かめた後にしか行わない。迷ったら保留か一時停止にする（統括の指示）。
- **純粋な規則と Git の操作を分ける**：保存するパスの選び方、保留の判定、競合の解決の計画、別名ファイルの名前、定期の実行の選び方とジョブのファイルの中身は `domain/` の純粋な関数にし、時刻、PC名、環境を引数で受ける。Git とファイルとプロセスの操作は `infra/`、順序と失敗の扱いは `application/` に置く。
- **後の Issue が変えずに使える公開の形**：I-5（`work finish`）と I-11（ダッシュボード）が使う部品を、この設計書の「公開の形」に固定する。
- **テストが外に出ない**：時刻、PC名、環境の判定、定期の実行（launchd、systemd、常駐のプロセス）、GitHub の呼び出し、spec-dock の実行ファイルのパスは、すべて注入できる。

## Current / Target

### Current（`origin/main` = `d5c8cc943`、2026-10-26）

- I-1：`infra/state_root.resolve_state_root`、`infra/github_snapshot`（`ensure_fresh`、`SnapshotStore`、`FreshSnapshot`）、`infra/github_structure`（`GithubApi`、`GithubRepository`、`repository_for_checkout`）。
- I-2：`canonical link`（手順1〜5と8）、`canonical status`（`sync`、`snapshot`、`changes` の `holds` と `blocking` は「未対応」）、`link_after_command`、`require_linked`、`CatalogLock`、`catalog_changes`、`Changeset`（版1）、`run_catalog_git`（C6）、`RuntimeEnvironment`（C11。OS、コンテナ、git）。`canonical_link.link_checkout` の docstring に「I-3 が `schedule: bool = True` と手順6・7を足す」とある。
- I-7：`canonical check`。公開のコマンドは47個。
- 定期の同期、登録簿、`state.json`、定期の実行の部品は、まだない。

### Target

```text
spec-dock canonical link [--no-schedule]
  手順1〜5（I-2） → 手順6a 登録簿 → 6b ジョブ → 7 基準 → 6c すぐの実行と15秒の待ち → 手順8（I-2）

launchd / systemd timer / loop runner（60秒ごと）
  spec-dock canonical sync --registered --state-root <根>
    for 登録簿のカタログ:            （1つの失敗で止めない）
      cycle.lock → 1 前提 → 2 ls-remote/fetch/書き換えの検出（排他の外）
                 → CatalogLock → 3 保存 → 4 統合（排他の中）
                 → 5 push（排他の外。拒否なら2へ、2回まで） → 6 state.json
    for 登録簿の repository:        7 ensure_fresh(repository, "cycle")（I-11 がダッシュボードを足す）

spec-dock canonical accept|restore|resume|remove|status
```

## 責務・Interface

### 1. 置き場の一覧

| 置き場 | 中身 | 層 |
|---|---|---|
| `domain/canonical_sync_rules.py` | 保存するパスの選び方、保留の判定、秘密情報の正規表現、競合の解決の計画、別名ファイルの名前、PC名 | 純粋 |
| `domain/canonical_sync_state.py` | `CatalogSyncState`（`state.json` 版1）、`SyncRegistry`（登録簿 版1）、`AcceptedChanges`（`accepted.json` 版1）、`RunnerRecord`（`runner.json`）、状態の鍵 | 純粋 |
| `domain/canonical_scheduler.py` | 定期の実行の選び方、plist と systemd のユニットの中身、systemd の引用 | 純粋 |
| `infra/canonical_state.py` | 状態の置き場のファイル：`state.json` の読み書き（一時ファイルと `rename`、カタログごとの短い排他）、`cycle.lock`、ログと切り替え、`runner.*` と `kick` のパス | infra |
| `infra/canonical_registry.py` | 登録簿の読み書き（`<根>` のディレクトリへの `flock`） | infra |
| `infra/canonical_scheduler_launchd.py`、`canonical_scheduler_systemd.py`、`canonical_scheduler_loop.py` | 登録、解除、すぐの実行、観察。常駐のプロセスの `runner.lock`、`runner.json`、`kick`、`--detach` の起動、周期の繰り返しと止め方 | infra |
| `infra/canonical_scheduling.py` | `scheduler_for(kind, …)` の工場（テストが差し替える）と `SchedulerSpec`、`Scheduler` の型 | infra |
| `infra/canonical_git.py`（足す） | 変更の一覧、一時のインデックスでの保存、`merge-tree`、解決の書き込み、`commit-tree`、早送り、push と `--dry-run`、祖先の判定、差分のパス、HEAD からの戻し、blob の値、追跡の数、push の URL | infra |
| `infra/runtime_environment.py`（足す） | `RuntimeEnvironment.systemd_user`、`linger`（既定 None）、`detect_service_manager` | infra |
| `application/canonical_sync.py` | `canonical sync` の振り分け、1つのカタログの周期 `sync_catalog`、全体の周期 `run_cycle`、手順7 `refresh_structures`、`--loop` と `--detach` | application |
| `application/canonical_schedule.py` | `canonical link` の手順6と7（`plan_schedule`、`apply_schedule`）、公開の `request_sync_now` | application |
| `application/canonical_hold.py` | `canonical accept`、`canonical restore` | application |
| `application/canonical_resume.py` | `canonical resume` | application |
| `application/canonical_remove.py` | `canonical remove` | application |
| `application/canonical_link.py`（変える） | `schedule: bool = True` と手順6・7の差し込み、`--no-schedule` | application |
| `application/canonical_status.py`（変える） | `sync_item`、`snapshot_item`、`changes` の `holds` と `blocking`、`git` の登録簿の git、未pushの警告 | application |
| `application/canonical_catalog.py`（変える） | RST-1：作りかけのカタログの観察に `in_progress` を足し、`occupied_next_step` を直す | application |
| `application/canonical_errors.py`（足す） | 下の「コード」の表の定数と次の1手 | application |
| `cli/catalog.py`、`cli/options.py`、`commands/canonical_dispatch.py` | 5つのコマンド、引数、ヘルプ、振り分け | cli / commands |
| `assets/spec_dock/docs/reference_cli.md`、`assets/static-inventory.json` | 5つのコマンドの行（C48〜C52）と `canonical link` の行の更新、`sha256` と `known_old_sha256` | 配布資産 |

### 2. 状態の置き場のデータ（C9。Epic の 5章の形のまま）

`<根>` は `resolve_state_root(override=--state-root)`。すべてのファイルは、同じディレクトリの一時ファイルに書いて `fsync` してから `rename` する。読む側は排他を取らない。

- **鍵**：`state_key(catalog) = sha256(os.fsencode(realpath(catalog))).hexdigest()[:16]`。
- **`<根>/canonical-registry.json`**（`SyncRegistry`）：`{"version": 1, "scheduler": "launchd"|"systemd"|"loop"|null, "catalogs": [{"catalog", "main_checkout", "repository"|null, "git", "registered_at"}]}`。`catalog` は実際のパス。`repository` は `github.com/<owner>/<repo>`（`repository_for_checkout` で決まらないときは null。手順7でそのカタログを飛ばす）。書くときは `<根>` のディレクトリを読み取りで開いて `flock(LOCK_EX)`（10秒まで）。知らない版、壊れた JSON は `RegistryUnreadable` で、書き換えない。
- **`<根>/catalogs/<鍵>/state.json`**（`CatalogSyncState`）：Epic の 5章の項目に、次の3つを足す（C9 の持ち主として決める。版は1のまま）。
  - `adopt_remote_pending: bool`（既定 false）：`resume --adopt-remote` が残す一度きりの「取り込み直し」の印（統括の判断 R2）。次の周期が、R を親にした1つのコミットで取り込み直し、push した後に false に戻す。
  - `schedule: "none" | null`：`canonical link --no-schedule` の印（統括の判断 R1）。`link_after_command` は、この印があれば手順6を行わない。`--no-schedule` なしの `canonical link` が null に戻す。
  - `last_error.at`：失敗の時刻。
  - `push_auth` がないか `result` が `unknown` なら、その周期で `push --dry-run` を行う（統括の判断 Q5）。
  - `dashboard` は I-11 のもので、I-3 は読んだ値をそのまま書き戻す（中身を解釈しない）。
  - 知らない版、壊れた JSON は `StateUnreadable`。周期はそのカタログを `error` で飛ばし、ファイルを上書きしない。
- **書く排他**：`state.json` の読み直しと書き込みは、`<根>/catalogs/<鍵>` のディレクトリへの短い `flock`（10秒まで）の中で行う（`update_catalog_state(root, catalog, mutate)`）。`cycle.lock`（周期の重なりを防ぐファイル `<根>/catalogs/<鍵>/cycle.lock` への `flock(LOCK_EX|LOCK_NB)`。統括の判断 Q4）とは別のものにする（同じプロセスの中で、2つの `flock` が衝突しないため）。
- **`<カタログ>/.runtime/accepted.json`**（`AcceptedChanges`）：`{"version": 1, "paths": {"<パス>": "<blob の値>"}, "deletions": ["<パス>"]}`。カタログの排他の中で書く。保存したパスの項目は、周期が消す。
- **ログ** `<根>/canonical-sync.log`：1行に、UTC の時刻、カタログ、結果、件数、コード。ファイルの中身とパスの中身は書かない（パスは書く）。書く前に 1 MiB を超えていれば `canonical-sync.log.1` に `rename` する。
- **常駐のプロセス**：`<根>/runner.lock`（`flock(LOCK_EX|LOCK_NB)` を終わるまで持つ）、`<根>/runner.json`（`{"version": 1, "pid", "started_at", "spec_dock_version"}`）、`<根>/kick`（あれば消してすぐに周期）。

### 3. 純粋な規則（`domain/canonical_sync_rules.py`）

- `QUIET = 30秒`、`MAX_WAIT = 5分`、`MASS_DELETE_COUNT = 20`、`MASS_DELETE_MIN = 5`、`MASS_DELETE_RATIO = 0.10`、`MAX_FILE_BYTES = 10 MiB`、`SECRET_PATTERNS`（Epic の 5章の5つの正規表現を bytes で）。
- `CatalogChange(path, kind: "modified"|"added"|"deleted", mtime: datetime | None)`。
- `select_paths(changes, *, pending_since, now) -> Selection(selected: tuple[str, ...], pending_since: dict[str, str])`：`pending_since` に、初めて見たパスの時刻を足し、変わっていないパスを消す。選ぶのは、`mtime` が `now - QUIET` 以前のもの、削除で `pending_since` から `QUIET` たったもの、`pending_since` から `MAX_WAIT` たったもの。未来の `mtime` は `now` とみなす。
- `classify_holds(candidates, *, deletions, tracked_count, accepted_paths, accepted_deletions) -> dict[パス, 種類]`（`candidates` は `HoldCandidate(path, size, blob, content)`。`blob` は許可のあるパスだけ求める）：
  - 大量の削除：`deleted` から `command_deletions`（`origin: command` の束が `paths` か `deletions` で覆うパス）と、`accepted.deletions` にあるものを除いた数 n が、`n >= 20` か `n >= 5 and n >= 0.10 * tracked_count` なら、その n 件をすべて `mass_delete` で保留する（統括の判断 Q2。`deleted` は今の作業ツリーのすべての削除）。
  - 大きすぎる：`size > MAX_FILE_BYTES` のファイルは、許可の blob と今の blob が同じでなければ `too_large`。
  - 秘密情報：中身が `SECRET_PATTERNS` のどれかに当たるファイルは、許可の blob と同じでなければ `secret`。大きすぎるファイルの中身は読まない。シンボリックリンクは中身を見ない。
- `resolve_conflicts(entries, *, pc, now, taken) -> Resolution(updates, removals, copies)`：`entries` は `merge-tree` の `<モード> <オブジェクト> <段>\t<パス>`。パスごとに、段2と段3があれば、パスに段3、別名ファイルに段2。段2だけなら段2、段3だけなら段3。段1だけ（両方で削除）なら、そのパスを消す。
- **表せない競合**：解決した後のツリーのパスが、L のツリー、R のツリー、別名ファイルのどれにもないパス（ディレクトリとファイルの衝突で Git が作る `path~<名前>` など）を含むとき、または解決の書き込みを Git が拒否したときは、統合を作らず `merge_failed` で一時停止する（application が確かめる）。
- `conflict_copy_name(path, *, pc, now, taken) -> str`：`<本体>.conflict-<PC名>-<YYYYMMDDTHHMMSSZ>[.<拡張子>]`。拡張子は最後の `.` の後ろ。`.` が先頭にしかない名前と `.` のない名前は、名前の全体を本体にする。`taken` にあれば、本体の後に `-2`、`-3`。
- `pc_name(hostname) -> str`：最初の `.` より前を小文字にし、`a-z0-9-` 以外を `-`、連続する `-` をまとめ、前後の `-` を除き、32文字まで。空なら `pc`。

### 4. 定期の実行の選び方とジョブの中身（`domain/canonical_scheduler.py`）

- `select_scheduler(system, *, systemd_present, systemd_user, previous) -> "launchd"|"systemd"|"loop"`：`previous` があり使えるならそれ（`launchd` は macOS、`systemd` は `systemd_user` が真、`loop` は Linux）。なければ Epic の順。
- `LAUNCHD_LABEL = "io.github.chemitaro.spec-dock.canonical-sync"`、`SYSTEMD_SERVICE = "spec-dock-canonical-sync.service"`、`SYSTEMD_TIMER = "spec-dock-canonical-sync.timer"`。
- `launchd_plist(spec, *, label) -> bytes`（`plistlib`）、`systemd_units(spec) -> (service_text, timer_text)`。中身は Epic の 5章のとおり。`SchedulerSpec(executable, state_root, git_dir, home, gh_dir=None)`（`log` は `<根>/canonical-sync.log`）。`PATH` は `git_dir`、続けて `gh_dir`（`canonical link` のときの `PATH` の `gh` のディレクトリ。git と同じか、ないときは入れない）、その後に launchd は `/usr/bin:/bin:/usr/sbin:/sbin`、systemd は `/usr/local/bin:/usr/bin:/bin`（Epic の5章に `gh` のディレクトリを足した。手順7の `gh` が見つからないのを防ぐ。統括の了承済み）。
- `systemd_quote(value)`：`%` を `%%` に。空白、`"`、`\`、`'` を含む値は、`"` で囲み、`\` と `"` を `\` で逃がす。
- `restart_line(state_root) -> str`：`spec-dock canonical sync --registered --loop --detach --state-root <根>`（シェルの引用は `shlex.quote`）。

### 5. 定期の実行の部品（`infra/canonical_scheduling.py` と3つの実装）

```python
class Scheduler(Protocol):
    kind: SchedulerKind
    def needs_change(self, spec: SchedulerSpec) -> bool: ...      # 書く必要があるか（読むだけ）
    def write_paths(self, spec: SchedulerSpec) -> tuple[Path, ...]: ...  # 書く場所（書き込みの可否の確かめ用）
    def ensure(self, spec: SchedulerSpec) -> Literal["created", "updated", "unchanged"]: ...
    def kick(self, spec: SchedulerSpec) -> None: ...               # すぐの実行。失敗は SchedulerError
    def remove(self, spec: SchedulerSpec) -> bool: ...             # 外した（True）、なかった（False）
    def observe(self, spec: SchedulerSpec) -> SchedulerObservation: ...  # installed, active, detail（読むだけ）

def scheduler_for(kind: SchedulerKind, *, state_root: Path, environment: RuntimeEnvironment) -> Scheduler: ...
```

- **launchd**（`LaunchdScheduler(label, agents_dir, uid, runner, sleep)`。`bootstrap` は1秒おきに3回まで試す。`bootout` の拒否（読み込まれていない以外の失敗）は `SchedulerError` にし、plist を消さない。`print` で分からないときも、`bootstrap` の前に `bootout` を試す。既定は `LAUNCHD_LABEL`、`~/Library/LaunchAgents`、`os.getuid()`）：`ensure` は、plist のバイトが同じで、`launchctl print gui/<uid>/<label>` が「ない」（終了コード113）でなければ `unchanged`（サンドボックスの中で `print` が失敗しても、書かない）。違えば、一時ファイルと `rename` で plist を書き、読み込まれていれば `bootout` し、`bootstrap gui/<uid> <plist>`。`kick` は `kickstart gui/<uid>/<label>`（`-k` を付けない）。`remove` は `bootout`（ないときの失敗は無視）と plist の削除。実機の確かめは、`label` と `agents_dir` を引数で渡す（統括の判断 Q8）。
- **systemd**（`SystemdScheduler(unit_dir, service, timer, runner)`。既定は `${XDG_CONFIG_HOME:-~/.config}/systemd/user`）：`ensure` は、2つのファイルが同じで `systemctl --user is-active <timer>` が `active` なら `unchanged`。違えば書いて `daemon-reload`、続けて `enable --now <timer>`。`kick` は `start --no-block <service>`。`remove` は `disable --now <timer>`、ファイルの削除、`daemon-reload`。
- **記録した `PATH`**：`recorded_search_path(spec)` は、置いてあるジョブの `PATH` を返す。手順6は、その中に今も `gh` があるディレクトリがあれば、それを `gh_dir` にする（ほかの `PATH` の `canonical link` で、ジョブを書き直さないため）。
- **記録した実行ファイル**：`recorded_executable(spec)`（読むだけ）は、置いてあるジョブの実行ファイル（plist の `ProgramArguments[0]`、ユニットの `ExecStart` の最初の語）を返す。手順6は、それが今もあって実行できるなら、`spec.executable` をそれにしてから `needs_change` を確かめる（エージェントの `PATH` や開発用の venv の `spec-dock` で、ジョブを書き換えないため）。
- **loop**（`LoopScheduler(state_root, executable, spawn)`）：`running()` は `runner.lock` を `LOCK_EX|LOCK_NB` で取れるか（取れたらすぐ放す。ファイルがなければ動いていない。ファイルを作らない）。常駐のプロセスの側は、起動のときに `runner.lock` を0.2秒おきに5回まで試す（`running()` の一瞬の確かめと重なって、起動したばかりのものが終わらないため）。`ensure` は動いていれば `unchanged`、いなければ `detach` で `created`。`kick` は動いていれば `kick` を作り、いなければ `detach`。`remove` は、動いていれば `runner.json` の `pid` に SIGTERM（`runner.lock` が取れない間だけ送る。番号の使い回しの誤送信を防ぐ）。
- **`detach`**：`[executable, "canonical", "sync", "--registered", "--loop", "--state-root", 根]` を、`start_new_session=True`、標準入力と出力を `DEVNULL`、作業ディレクトリをホームにして起動し、待たない。ログは周期が `append_log` で書く（ログの切り替えの後も、新しいファイルに書くため）。
- **SIGTERM**：`--loop` でない `canonical sync --registered` も、SIGTERM と SIGINT を受けたら、今のカタログの周期を終えてから止まる（launchd の `bootout` や systemd の停止で、統合の途中で止まらないため）。
- **常駐のプロセス**（`run_loop(root, *, cycle, clock, sleep, signals)`）：`runner.lock` が取れなければ終了コード0で `unchanged`。取れたら `runner.json` を書き、SIGTERM と SIGINT で「止める」の印を立てる処理を入れ、`cycle()` → 最大60秒を2秒ごとに「止める」と `kick` を見て待つ、を繰り返す。周期の途中で合図が来ても、その周期を終えてから止まる。終わるとき `runner.json` を消し、`runner.lock` を放す。
- **実行ファイル**：`spec_dock_executable()` は、`sys.argv[0]` を `realpath` でたどり、実行できるファイルならそれ、そうでなければ `PATH` の `spec-dock` の実際のパス。見つからなければ `SchedulerError`（手順6の `CANONICAL_SCHEDULER_FAILED`）。テストは差し替える。

### 6. C11 の追加（`infra/runtime_environment.py`）

- `RuntimeEnvironment` に `systemd_present: bool | None = None`、`systemd_user: bool | None = None`、`linger: bool | None = None`、`user: str | None = None` を足す（既定 None。I-2 の生成とテストの部品はそのまま動く）。
- 「Failed to connect to bus」が試し直しの後も続くときは、`systemd_user` を False ではなく None（不明）にする。`select_scheduler` は、不明の間は前に選んだ `systemd` を保つ（サンドボックスや `su` でバスに届かないだけで、仕組みを選び直さない）。`systemd_quote` は `$` も `$$` にする。
- `detect_service_manager(environment, *, root=Path("/"), runner=subprocess.run, sleep=time.sleep) -> RuntimeEnvironment`：Linux のときだけ、`/run/systemd/system` の有無、`systemctl --user is-system-running`（出力の1行目が `running` か `degraded` なら真。標準エラーに `Failed to connect to bus` があれば、1秒おきに5回まで試し直す）、`loginctl show-user <user> -p Linger --value`（`yes` なら真、`no` なら偽、失敗なら None）を埋めて返す。macOS では何もしない。`detect_runtime_environment` は呼ばない（統括の判断 Q10）。

### 7. 同期の Git の操作（`infra/canonical_git.py` に足す。すべて `run_catalog_git` を通す）

| 関数 | Git | 備考 |
|---|---|---|
| `reset_index(catalog)` | `reset -q` | 本当のインデックスを HEAD にそろえる。作業ツリーには触れない |
| `list_changes(catalog)` | `status --porcelain=v2 -z --untracked-files=all` | `CatalogChange` の一覧。`mtime` は `lstat`。名前の変更の記録は、両方のパスに分ける |
| `tracked_count(catalog)` | `ls-files -z` | |
| `blob_of(catalog, path)` | `hash-object --no-filters -- <ファイル>` | 許可と比べる値 |
| `save_commit(catalog, paths, *, message, parent)` | `GIT_INDEX_FILE=<カタログ>/.runtime/index.tmp`：`read-tree HEAD`、`add -A`（パスは `--pathspec-from-file`）、`write-tree`、`commit-tree -p <parent>`、`update-ref refs/heads/spec-dock/canonical <新> <parent>`、`reset -q` | 一時のインデックスは最後に消す |
| `is_ancestor(catalog, a, b)` | `merge-base --is-ancestor`（終了コード0と1。ほかは `GitProcessError`） | |
| `merge_tree(catalog, left, right, *, allow_unrelated)` | `merge-tree --write-tree -z [--allow-unrelated-histories] L R` | 終了コード0、1、2以上を `MergeTreeResult(code, tree, entries, message)` で返す |
| `write_resolution(catalog, tree, resolution)` | 一時のインデックスに `read-tree <tree>`、`update-index -z --index-info`、`write-tree` | |
| `commit_merge(catalog, tree, left, right, *, message)` | `commit-tree -p L -p R` | |
| `changed_paths(catalog, a, b)` | `diff --name-only -z --no-renames a b` | 早送りの前に、作業ツリーの変更と重なるかを確かめる |
| `fast_forward(catalog, target)` | `merge --ff-only --no-edit <target>` | |
| `commit_on(catalog, tree, parent, *, message)` | `commit-tree -p <parent>` | 取り込み直しの C（親は R だけ） |
| `reset_keep(catalog, target)` | `reset -q --keep <target>` | 取り込み直しで手元のブランチを C へ移す。編集中のファイルと衝突すれば、Git が何も変えずに拒否する |
| `push_canonical(catalog, *, dry_run)` | `push --porcelain [--dry-run] origin HEAD:refs/heads/spec-dock/canonical` | `PushResult`：`pushed`、`up_to_date`、`rejected`（先に進まれた）、`auth_failed`、`failed` |
| `push_url(catalog)` | `remote get-url --push origin` | `https` か `ssh` かの判定 |
| `restore_from_head(catalog, paths)` | `restore --source=HEAD --worktree`（パスは `--pathspec-from-file`） | インデックスに触れない |
| `ignored_files(catalog)` | `ls-files -z --others --ignored --exclude-standard` | `.runtime/` の下を除いて返す（`canonical remove`） |
| `operation_in_progress(catalog)` | 管理ディレクトリの `MERGE_HEAD`、`CHERRY_PICK_HEAD`、`REVERT_HEAD`、`rebase-merge/`、`rebase-apply/` | ファイルを見るだけ |

- 認証の失敗の判定は、標準エラーの `Authentication failed`、`could not read Username`、`terminal prompts disabled`、`Permission denied (publickey)`、`The requested URL returned error: 403` で行う。
- `merge-tree` の `-z` の出力は、`<ツリー>\0`、競合の情報（`<モード> <オブジェクト> <段>\t<パス>\0` の並び）、空の `\0`、情報のメッセージである。

### 8. 1つのカタログの周期（`application/canonical_sync.sync_catalog`）

`SyncContext(state_root, clock, hostname, environment, github_api_factory, log)` を受け、`CatalogResult` を返す。

1. **`cycle.lock`**：取れなければ `skipped`（`skipped_reason: "cycle_busy"`）。状態は書かない。
2. **前提**（Epic 手順1）：`state.json` を読む（読めなければ `error`、上書きしない）。`paused` なら `paused` で飛ばす。カタログのディレクトリがない、読めない（`PermissionError` か `Operation not permitted`）、`spec-dock/canonical` にいない、途中の操作がある、形式が書けない、登録簿の git が 2.38 より古いとき、それぞれのコードを `last_error` に書いて `error` で飛ばす。読めないときの `program` は `[realpath(sys.executable), 登録簿の git]`。
3. **GitHub の確かめ**（Epic 手順2。排他の外）：`remote_canonical`（I-2）。`absent` で基準があれば `paused: "remote_deleted"`。`absent` で基準がないときは、手元の canonical が初期のコミットだけ（`is_initial_commit`、I-2）なら R なし（作成の続き）、そうでなければ `paused: "remote_deleted"`（GitHub で消されたものを作り直さない）。接続の失敗なら、`last_error` に `GITHUB_UNAVAILABLE` を書き、取得済みの `refs/remotes/origin/spec-dock/canonical` が基準の子孫のときだけ、それを R として3と4を行う（子孫でなければ R なしで3だけ。追跡の参照はmainのチェックアウトの `git fetch` でも動くため。レビュー② SP-2）。5は行わない。`present` なら `fetch_canonical`（I-2）の後に R を読み、基準があって `is_ancestor(基準, R)` が偽（基準のオブジェクトがない場合を含む）なら `paused: "remote_rewritten"`。そうでなければ基準を R にする（記録は6で）。
4. **保存**（Epic 手順3。`CatalogLock(timeout=0)` の中。取れなければ `skipped`、`skipped_reason: "lock_busy"`）：
   - `reset_index` → `list_changes` → 変更の束を名前の順に読む（読めない束は残し、ログに書く。`consumed_changesets` にある名前は飛ばす）。
   - 束ごとに、束の `paths` と `deletions` が覆う変更（パスが同じか、その下）を選ぶ。`origin: command` の束が覆う削除は、大量の削除の数に入れない。
   - 束にないものは `select_paths` で選ぶ。
   - `classify_holds` で保留を除く（束の分も含む）。保留は `holds` に、初めて保留した時刻を `since` にして記録する。
   - 束ごとに1つ、残りの選んだパスで1つ、`save_commit` でコミットする。メッセージは `spec-dock: save <件数> files (<PC名>)`。コミットしたパスを `pending_since` と `accepted.json` から消す。束のファイルを消し、名前を `consumed_changesets`（直近100件）に足す。
5. **統合**（Epic 手順4。同じ排他の中）：L = HEAD。
   - R がない、または `is_ancestor(R, L)` なら何もしない。
   - `is_ancestor(L, R)` なら、`changed_paths(L, R)` と、作業ツリーの変更（未保存と保留）が重なる（同じパスか、一方が他方の下）か確かめる。重なれば `blocking` に記録（保留にあるパスは `held`、ほかは `local_edit`）して取り込まない。重ならなければ `fast_forward(R)`。それでも失敗したら、`blocking` に Git の出力を `last_error`（`CANONICAL_SYNC_BLOCKED`）として残す。
   - 分岐していれば `merge_tree(L, R, allow_unrelated=state.adopt_remote_pending)`。0ならそのツリー、1なら `resolve_conflicts` → `write_resolution`。2以上、解決の書き込みの失敗、表せない競合（3の「表せない競合」）なら `paused: "merge_failed"` と Git の出力。`commit_merge`（親は L と R、メッセージ `spec-dock: merge (<PC名>)`）の後、上と同じ重なりの確かめをしてから `fast_forward(<その統合のコミット>)`。別名ファイルを `conflicts` に足す。
   - **取り込み直し**（`adopt_remote_pending`。統括の判断 R2）：L が R の祖先でなければ、上の統合のツリーで、親を R だけにしたコミット C（メッセージ `spec-dock: adopt remote (<PC名>)`）を作る。R から C への差分（追加と変更のファイルの中身、削除の数）に `classify_holds` を当て、当たれば C を作らずに `paused: "remote_rewritten"` に戻し、`holds` と `last_error`（`CANONICAL_SAVE_HELD`）を書く。ただし、当たったパスがすべて作業ツリーで編集中（利用者が直している、消している）なら、一時停止にせず、`blocking`（`held`）に記録して何も push せずに持ち越す（その変更が保存された後の周期で、もう一度確かめる）。当たらなければ、重なりの確かめの後に `reset --keep C` で手元のブランチと作業ツリーを C へ移す（Git が編集中のファイルとの衝突を拒否したら、何もせずに `blocking`）。push は R からの早送りになる。push が成功したら `adopt_remote_pending` を false に戻す。L が R の祖先なら、ふつうの早送りで、印を戻す。
   - `conflicts` から、別名ファイルがもうないものを消す。
6. **push**（Epic 手順5。排他の外）：L が R より進んでいれば（R がないときを含む）`push_canonical`。`rejected` なら手順3（取得）からやり直す（2回まで）。`pushed` なら基準を HEAD に、`push_auth` を `ok` に。`auth_failed` なら `push_auth` を `failed` にし、URL の種類の次の1手を書く。送らなかった周期で `push_auth` が未記録か `unknown` なら `push_canonical(dry_run=True)` を行い、`ok`（成功か `rejected`）、`failed`（認証）、`unknown`（そのほか）を書く。
7. **記録**（Epic 手順6）：`update_catalog_state` で、`head`、`last_seen_remote`、`remote_contains_head`（HEAD が基準の祖先か同じ）、`unpushed_since`（含まれなくなった最初の時刻。含まれたら null）、`pending_since`、`holds`、`blocking`、`conflicts`、`consumed_changesets`、`last_cycle`、`last_success_at`（`ok` のとき）、`last_error`（`ok` のとき null）を書く。ログに1行書く。

- 保存の対象は、普通のファイルとシンボリックリンクだけである。入れ子のリポジトリ（`git status` の `sub/`）やソケットは保存せず、ほかのパスの保存を止めない。保留の規則で確かめた中身は、そのバイト列のままコミットする（確かめた後に書き換えられても、確かめていない中身を保存しない。レビュー② SP-9）。周期の初めに、殺された周期が残した一時のインデックスとその lock を消す（カタログの排他の中なので安全）。
- 確かめたバイト列は `hash-object -w --stdin --path=<パス>` で書く（カタログの `.gitattributes` の eol や clean フィルタが `git add` と同じに効く）。書いたツリーが親と同じならコミットを作らない（eol の変換などで、毎周期の空のコミットを作らないため）。早送りには `-c merge.verifySignatures=false -c merge.autoStash=false` を足す（利用者の設定で取り込みが止まらず、共有の stash に何も積まないため）。許可した削除のうち、今は削除されていないもの（戻した、作り直した）は、周期が許可から消す（後の同じ大量の削除を、もう一度保留するため）。`push_auth` が `failed` の間は、毎周期 dry-run で確かめ直す。`--registered` の周期は、`cycle.lock` を取った後に登録簿を読み直し、外されたカタログを `skipped`（`unregistered`）にする。ログは専用の lock ファイルで排他し、`<根>` のディレクトリの排他は使わない（`canonical link` の手順6a〜6bとの取り合いを避けるため）。
- `ls-remote` と `fetch` の失敗が認証の失敗（SSH の鍵、非公開の https）なら、接続の失敗ではなく `push_auth: failed` と `CANONICAL_PUSH_AUTH_FAILED`（URL の種類の次の1手）にし、保存はローカルに積む。`state.json` のない周期（状態の置き場を消した、根が違う）は、手順7と同じ規則（取得する前の追跡の参照、なければ初期のコミットでない手元の HEAD）で基準を決めてから確かめる。`.runtime/` は、カタログの `.gitignore` の行がなくても保存せず、取り込むコミットが `.runtime/` に触れていれば `merge_failed` で止まる。取り込み直しの間（`adopt_remote_pending`）は、許可した削除を消さない（R の側の削除は作業ツリーに現れないため）。予期しない例外も `last_error`（`SYNC_FAILED`）に記録する。push は確かめた SHA を送る。管理ディレクトリの `index.lock` は途中の操作として扱う。
- 早送りと取り込み直しの前の重なりの確かめには、無視されたファイル（`.runtime/` を除く）も入れる。Git の早送りと `reset --keep` は、無視されたファイルを確かめずに置き換えるためである。早送りには `--no-overwrite-ignore` も付ける。確かめたバイト列のモードは、一時のインデックスで `git add` が決めたもの（`core.fileMode` に従う）を使う。`merge-tree` は `-c merge.directoryRenames=false` で呼ぶ（相手がディレクトリの名前を変えても、こちらの新しいファイルは書いた場所に残り、作られたパスのために止まらない）。`canonical remove` は、カタログが別のブランチにある、ほかの場所にある、マウントされている（`occupied`、`elsewhere`、`foreign`）ときは、書く前に `CANONICAL_PATH_OCCUPIED` で止まる。`systemd_quote` が `$` を `$$` にするのは `ExecStart=` の中だけである。
- 変更の種類は Git の報告を優先する。作業ツリーで削除と報告されたパス、親がシンボリックリンクかファイルになったパスは削除として扱い、リンクの先を読まない。確かめた後で `git add` の前に消えたファイルは、削除ではなく確かめたバイト列で保存する。認証の失敗を見分ける Git の呼び出し（`ls-remote`、`fetch`、push）は `LC_ALL=C` で行う。`canonical resume` の引数は、止まった理由ではなく今の GitHub の状態で決める（canonical があれば `--adopt-remote`、なければ `--push-local`）。取り込み直しの保留で許可と比べる値は、`accept` と同じく作業ツリーのファイルのフィルタなしの blob とする。
- 一時停止の間の周期は、止まったときの `last_error` を消さない。手で実行した `canonical sync` は、止まった理由を `error.code` にして返す。周期の記録は、`canonical link` が持つ `schedule` を、書く直前に読み直した値のまま残す。
- 結果：`ok`（エラーなし）、`skipped`、`paused`、`error`。出来事ごとの扱いは次の表のとおり（`ok` のときだけ `last_error` を null にし、`last_success_at` を進める）。

| 出来事 | result | `last_error.code` | 効果 |
|---|---|---|---|
| 変更なし、保存、統合、push の成功 | ok | null | あれば `canonical.save`、`merge`、`push` |
| 取り込みが編集中のファイルと重なり、持ち越した | ok | null（`blocking` に記録） | 保存の分だけ |
| push が2回のやり直しの後も拒否された | ok | null（次の周期に任せる。`unpushed_since` が進む） | 保存の分だけ |
| 変更の束が読めない | ok | null（束は残し、ログに書く） | |
| origin につながらない | error | `GITHUB_UNAVAILABLE` | 保存（と取得済みの R への統合）の分 |
| push の認証の失敗 | error | `CANONICAL_PUSH_AUTH_FAILED` | 保存の分 |
| そのほかの push の失敗（`[remote rejected]` を含む） | error | `GITHUB_UNAVAILABLE` | 保存の分 |
| 重なりの確かめの後に、早送りを Git が拒否した | error | `CANONICAL_SYNC_BLOCKED` | 保存の分 |
| 前提（手順1）を満たさない | error | 各コード | なし |
| 一時停止の中、または新たに一時停止 | paused | 理由（`remote_rewritten` など）か `CANONICAL_SAVE_HELD` | なし（新たな一時停止の前の保存はある） |
| 排他か周期の重なり | skipped | （記録しない） | なし |

- 手で実行した `canonical sync`（引数なし）が一時停止のカタログに当たると、効果がなければ `failed`（終了コード3、`error.code` は一時停止の理由、`recovery` は `spec-dock canonical status`）になる。`CatalogResult` は `catalog`、`result`、`saved_commit`（最後の保存のコミット）、`merged`、`pushed`、`conflicts`、`holds`、`blocking`、`skipped_reason`、`paused`、`error`、`effects`（`canonical.save`、`canonical.merge`、`canonical.push` の `succeeded`）を持つ。

### 9. 全体の周期と手順7（`run_cycle`、`refresh_structures`）

- `run_cycle(entries, ctx) -> CycleResult(catalogs, repositories)`：`entries` を登録簿の順に `sync_catalog` する。例外は、そのカタログの `error`（`last_error`）に変えて続ける。
- `refresh_structures(entries, ctx) -> list[RepositoryResult]`：すべてのカタログの後に、`repository` が null でないものを、最初に現れた順で1回ずつ、`ensure_fresh(repository, "cycle", state_root=根, api=ctx.github_api_factory(main_checkout))`。`FreshSnapshot.probe` を `probe`（`unchanged`、`changed`、`failed`）に、`refreshed` をそのまま。例外も `failed` にする。`RepositoryResult(repository, probe, refreshed, dashboards_written=0)`。**I-11 は、この関数の中、`ensure_fresh` の後に、そのリポジトリのカタログごとのダッシュボードを足す**（手順7の拡張の場所）。
- `canonical sync`（引数なし）は、`require_linked`（I-2）でこのクローンのカタログを確かめ、登録簿の項目があればそれを、なければ今の `PATH` の git とこのチェックアウトから作った項目を1つだけ処理する。
- `canonical sync --registered` は、`REPOSITORY_INDEPENDENT_HANDLERS` に置く（`--registered` でないときは None を返して、通常の振り分けに任せる）。登録簿が読めなければ `failed`（`CANONICAL_REGISTRY_UNREADABLE`、終了コード3）。
- 結果の状態は、要件 R-430-12 のとおり。`effects` は各カタログの `effects`。

### 10. `canonical link` の手順6と7（`application/canonical_schedule.py`）

`link_checkout(…, schedule: bool = True)`、`link_after_command(…, schedule: bool = True)` に足し、`run_canonical_link` は `schedule=not namespace.no_schedule` を渡す。

- **予定**（書く前。`_refuse_unwritable` の確かめに入れる）：`plan_schedule(layout, environment, state_root, *, schedule) -> SchedulePlan`。登録簿の項目が今の値（カタログ、mainのチェックアウト、`repository`、git）と違う、または移動の古い項目がある → `canonical.registry` を書く（`<根>`）。`scheduler.needs_change(spec)` → `canonical.scheduler` を書く（`write_paths`）。基準がない → `canonical.baseline` を書く（`<根>/catalogs/<鍵>`）。`schedule=False` では、基準だけ。
- **順**：手順5のリンクの後に、6a 登録簿 → 7 基準 → 6b ジョブ（`ensure`）→ 6c すぐの実行と待ち。ジョブを作ると最初の周期がすぐに動く（launchd の `RunAtLoad`、loop の起動）ので、基準を先に記録する（Epic の手順6と7の中身は同じ）。6b が失敗しても、基準は残る。6a から 6b までは `<根>` の排他を持ち、同時の `canonical link` がジョブの登録を競わないようにする。8（ツールの設定）は I-2 のまま最後。
- **6a**：`update_registry`。`observation.moved` のときは、登録のパス（動かす前のカタログのパス）の項目を消し、その状態のディレクトリを、`cycle.lock` を取ってから新しい鍵へ移す（新しい鍵の状態がないときだけ）。`scheduler` は `select_scheduler(..., previous=登録簿の scheduler)`。`repository` は、登録簿に記録した値があればそれ、なければ（null を含む）`repository_for_checkout(main, timeout=…)`（失敗は null）。`git` は、登録簿に記録した git が今もあり 2.38 以上ならそのまま、そうでなければ今の `PATH` の git にする。
- **6b**：`scheduler_for(kind).ensure(spec)`。選び直したとき（登録簿の `scheduler` があり、今の選択と違う）は、先に前の仕組みの `remove` を行う。失敗は `CANONICAL_SCHEDULER_FAILED`（`partial`、終了コード6、`recovery` は `spec-dock canonical link`）。
- **7**：`update_catalog_state` で、`state.json` がなければ作り（`push_auth: {"result": "unknown"}`）、`last_seen_remote` がなければ、`refs/remotes/origin/spec-dock/canonical` の値を、それもなく手元の canonical があれば手元の HEAD を書く（GitHub で消された canonical を、最初の周期が作り直さないため）。`--no-schedule` なら `schedule: "none"` を、そうでなければ null を書く。
- `canonical link --offline` は、手順6のすぐの実行を頼まない（周期の push を起こさない）。
- `link_after_command` は、`state.json` に `schedule: "none"` があれば手順6を行わない（手順7は行う。統括の判断 R1）。
- **6c**：6a か 6b で何かを書いたときだけ、`kick` して、`FIRST_RUN_WAIT = 15秒` まで0.25秒ごとに `state.json` を読み、`last_cycle.finished_at` が頼んだ時刻以後になるのを待つ。`kick` の失敗は警告に変える。
- **警告**：記録が見えない → `CANONICAL_SYNC_NOT_CONFIRMED`（macOS では、プライバシーとセキュリティで、spec-dock の Python と git に、フルディスクアクセスかリムーバブルボリュームへのアクセスを許可する次の1手）。`last_error.code == OS_ACCESS_DENIED` → `OS_ACCESS_DENIED`（同じ案内と `program`）。`push_auth.result == failed` → `CANONICAL_PUSH_AUTH_FAILED`。`systemd` で `linger` が偽 → `CANONICAL_LINGER_DISABLED`。`loop` → `CANONICAL_RUNNER_RESTART`（起動し直しの1行）。
- `link_after_command`（`worktree create` の後）も同じ経路を通る。そこでの失敗は、I-2 のとおり、呼び出し元の結果を変えずに警告で返す。

### 11. accept、restore、resume、remove

- **`canonical accept [<パス>…] [--deletions]`**：どちらもなければ使い方の誤り。`require_linked` → `catalog_changes` と同じカタログの排他（10秒）。パスは `normalize_catalog_path`（C4）で確かめ、カタログの中の普通のファイルかシンボリックリンクでなければ `CANONICAL_PATH_NOT_FOUND`（終了コード3、何も書かない）。`blob_of` を `accepted.json` の `paths` に書く。`--deletions` は、`state.json` の `holds` の `mass_delete` のパスを `deletions` に足す（なければ `unchanged`）。`state.json` は書かない。
- **`canonical restore [<パス>…]`**：`require_linked` → 排他。排他の中で `list_changes` を取り直し、保留が今も当たるかを確かめる：`mass_delete` は今も削除されていること、`secret` と `too_large` は今の中身がまだその保留に当たること（`classify_holds` を、そのパスだけで当て直す）。パスがあれば、すべてが `holds` にあって今も当たること（なければ `CANONICAL_NOT_HELD`、何も書かない）と、HEAD に版があること（なければ `CANONICAL_NOT_RESTORABLE`、何も書かない。新しいファイルを消さないため）を確かめてから `restore_from_head`。パスがなければ、今も削除されている `mass_delete` のパスをすべて（なければ `unchanged`）。`state.json` は書かない（次の周期が保留を数え直す）。
- **`canonical resume [--adopt-remote | --push-local]`**：`remote_deleted` で止まっていても、GitHub にもう canonical がある（ほかのPCが `--push-local` で作り直した）ときは、`--adopt-remote` で再開する（レビュー② SP-3）。`require_linked`、`cycle.lock`（10秒待つ。取れなければ `CANONICAL_LOCK_BUSY`）。`paused` がなければ `unchanged`。理由と引数が合わなければ `CANONICAL_PAUSED`（正しい引数を次の1手にする、終了コード3）。`--adopt-remote`：`ls-remote` と `fetch`（排他の外）で R を読み、`last_seen_remote = R`、`paused = null`、`adopt_remote_pending = true`。R がなければ `CANONICAL_PAUSED`（`--push-local` を案内）。`--push-local`：`ls-remote` で、まだないことを確かめ（あれば `CANONICAL_PAUSED` で `--adopt-remote` を案内）、`push_canonical` で作り、`last_seen_remote = HEAD`、`paused = null`。
- **`canonical remove [--yes]`**：`resolve_layout`、StartLock（5秒）、`cycle.lock`（10秒待つ。進んでいる周期の終わりを待ち、その後の周期を止めるため。取れなければ `CANONICAL_LOCK_BUSY`）。その中で、書く前に、すべての止まる条件を確かめる：カタログがあれば `list_changes` が空で、未pushのコミット（`unpushed` が0でない、または追跡の参照がなく HEAD がある）がないこと（`CANONICAL_UNSAVED_CHANGES`）、`ignored_files` が空であること（`CANONICAL_IGNORED_FILES_PRESENT`。一覧を `details.paths` に）。書く場所に書けること（`CANONICAL_SANDBOX_DENIED`）。`--yes` がなければ、外すものを `planned` の効果で返す。`--yes` では、カタログの排他の中で、各チェックアウト（`list_worktrees` で見えるもの）の正しいリンクを消す（`canonical.link.remove`）→ `git worktree unlock` と `git worktree remove`（`git.worktree.remove`）→ `info/exclude` の3行を消す（`git.info.exclude`。ほかの行は残す）→ 登録簿の項目と状態のディレクトリ（`canonical.registry`、`canonical.state`）→ ほかに登録がなければ `scheduler.remove` と登録簿の `scheduler` を null に（`canonical.scheduler`）。途中の失敗は `partial`（終了コード6、`recovery` は `spec-dock canonical status` で確かめてから `spec-dock canonical remove --yes`）。

### 12. `canonical status` の項目（`application/canonical_status.py`）

- **`sync`**：`{"status", "next_step", "state_root", "registered", "scheduler", "job": {"installed", "active", "detail"}, "linger", "push_auth", "last_cycle", "last_success_at", "last_error", "paused"}`。警告の順：一時停止（`CANONICAL_PAUSED`、理由と `resume` の引数）→ 登録簿にない（`CANONICAL_SYNC_NOT_SCHEDULED`、`spec-dock canonical link`）→ ジョブがない、動いていない（`launchd` と `systemd` は `CANONICAL_SYNC_NOT_SCHEDULED`、`loop` は `CANONICAL_RUNNER_STOPPED` と起動の1行）→ linger（`CANONICAL_LINGER_DISABLED`）→ 認証（`CANONICAL_PUSH_AUTH_FAILED`）→ 最後の失敗（`CANONICAL_SYNC_FAILED`、`details.cause` に元のコード、次の1手は `last_error.next_step`）→ 登録されているのに周期の記録がない（`CANONICAL_SYNC_NOT_CONFIRMED`）。`detect_service_manager` を呼ぶのはここと手順6だけ。
- **`changes`**：`holds`（`[{path, kind, since, next_step}]`）、`blocking`（`[{path, reason}]`）、`unpushed_since`。保留があれば `CANONICAL_SAVE_HELD`（種類ごとの解き方）。未pushが10分を超えたら `CANONICAL_UNPUSHED_STALE`（次の1手 `gh auth status` と `spec-dock canonical status` の `sync`）。統合を止めているパスがあれば `CANONICAL_SYNC_BLOCKED`。
- **`git`**：`registered: {"path", "version", "supported"}`（登録簿の git の `--version`）。
- **`snapshot`**：`{"status", "next_step", "repository", "path", "fetched_at", "checked_at", "anomalies", "last_error"}`。`SnapshotStore(根, repository).load()` で読むだけ（取り直さない）。
- 時刻は注入できる（`_now`）。状態の置き場には書かない。

### 13. 公開の形（I-5、I-11 が変えずに使う）

| 部品 | 形 | 使う側 |
|---|---|---|
| `application.canonical_schedule.request_sync_now(state_root, *, environment=None) -> bool` | 登録簿の `scheduler` の `kick`。登録簿がない、読めない、失敗は False（例外にしない） | I-5（`work finish`） |
| `infra.canonical_state.read_catalog_state(state_root, catalog) -> CatalogSyncState \| None` | `state.json` を読むだけ。ないときは None、壊れているときは `StateUnreadable` | I-5、I-11 |
| `infra.canonical_state.update_catalog_state(state_root, catalog, mutate) -> CatalogSyncState` | 短い排他の中で読み直し、`mutate` を当てて書く | I-11（`dashboard`） |
| `domain.canonical_sync_state.CatalogSyncState` | `last_cycle.finished_at`、`remote_contains_head`、`head`、`holds`、`paused`、`dashboard` など、Epic の 5章の項目 | I-5、I-11 |
| `domain.canonical_sync_state.holds_under(state, prefix) -> tuple[Hold, ...]` | Scope のディレクトリの下の保留 | I-5（`CANONICAL_SAVE_HELD`） |
| `application.canonical_sync.refresh_structures(entries, ctx)` と `RepositoryResult.dashboards_written` | 手順7の拡張の場所 | I-11 |
| `infra.canonical_registry.read_registry(state_root) -> SyncRegistry` | 登録簿を読むだけ | I-11、I-9 |
| 変更の束の `origin: finish` | 保留の規則をすべて当て、束のパスは30秒を待たない | I-5 |

### 14. コード（C8。この Issue が持ち主。Epic の12章への追記は統括。統括の判断 Q6）

| コード | 終了コード | 出る場面 | 次の1手 |
|---|---|---|---|
| `CANONICAL_SYNC_NOT_SCHEDULED` | —（警告） | 登録簿にない（`--no-schedule` を含む）、ジョブがない | `spec-dock canonical link`（`--no-schedule` なしで）で定期の同期を登録する |
| `CANONICAL_SYNC_NOT_CONFIRMED` | —（警告） | 手順6の直後の1回の記録が15秒で見えない、登録したのに記録がない | macOS：システム設定の「プライバシーとセキュリティ」で、示した Python と git にフルディスクアクセスかリムーバブルボリュームへのアクセスを許可し、`spec-dock canonical status` で確かめる。Linux：ログ（`<根>/canonical-sync.log`）を確かめる |
| `CANONICAL_PUSH_AUTH_FAILED` | —（警告） | `push_auth.result` が `failed` | `https`：`gh auth setup-git`。`ssh`：定期の実行には SSH のエージェントが渡らないことがあるので、`https` と `gh` の認証を使う |
| `CANONICAL_LINGER_DISABLED` | —（警告） | systemd で linger が `no` | `loginctl enable-linger <ユーザー>`（管理者の権限が要ることがある） |
| `CANONICAL_RUNNER_RESTART` | —（警告） | `loop` を使う `canonical link` | 起動し直しの1行を devcontainer の `postStartCommand` か起動のスクリプトに足す（足さなくても、次の `spec-dock canonical link` で動き直す） |
| `CANONICAL_RUNNER_STOPPED` | —（警告） | `loop` で常駐のプロセスが動いていない | 起動し直しの1行を実行する |
| `CANONICAL_UNPUSHED_STALE` | —（警告） | 未pushが10分を超えた | `gh auth status` と接続を確かめ、`spec-dock canonical status` の `sync` を見る |
| `CANONICAL_SYNC_BLOCKED` | —（警告。`last_error` にも） | 取り込みが編集中のファイルに当たっている | 示したファイルの編集を終えると、遅くとも5分で保存されて統合される。保留なら `changes.holds` の解き方 |
| `CANONICAL_SYNC_FAILED` | —（警告） | `state.json` の `last_error` | `details.cause` のコードの次の1手 |
| `CANONICAL_PAUSED` | 3（`resume` の引数の誤り）／警告（status） | 一時停止 | `spec-dock canonical status` で理由を見て、文書の「同期が止まったとき」に従い、`spec-dock canonical resume --adopt-remote` か `--push-local` |
| `CANONICAL_SAVE_HELD` | —（status の警告。`work finish` の 3 は I-5） | 保留がある | 大量の削除は `spec-dock canonical accept --deletions` か `spec-dock canonical restore`、秘密情報は中身を直すか `spec-dock canonical accept <パス>`、大きすぎるファイルは小さくするか `spec-dock canonical accept <パス>` |
| `CANONICAL_SCHEDULER_FAILED` | 6（partial） | 手順6のジョブの登録の失敗 | 示した出力を確かめて `spec-dock canonical link` |
| `CANONICAL_NOT_HELD` | 3 | 保留にないパスの `restore` | `spec-dock canonical status` の `changes.holds` のパスを指定する |
| `CANONICAL_NOT_RESTORABLE` | 3 | HEAD に版のない保留のパスの `restore` | ファイルを自分で直すか消す。保存してよければ `spec-dock canonical accept <パス>` |
| `CANONICAL_PATH_NOT_FOUND` | 3 | カタログにないパスの `accept` | カタログの中の、今あるファイルのパスを指定する |
| `CANONICAL_REGISTRY_UNREADABLE` | 3 | 登録簿が壊れている、知らない版 | 示したファイルを確かめ、退避してから `spec-dock canonical link` |
| `CANONICAL_STATE_UNREADABLE` | —（`last_error` と status の警告） | `state.json` が壊れている、知らない版 | 示したファイルを確かめ、退避してから `spec-dock canonical link` |
| `CANONICAL_GIT_IN_PROGRESS` | —（`last_error`） | カタログで merge などの途中 | `git -C <カタログ> merge --abort` などで途中の操作を終える |
| `GIT_FAILED`、`LOCAL_IO_FAILED` | —（`last_error`）／5（コマンド） | 周期やコマンドの中の、予期しない Git の失敗とファイルの読み書きの失敗 | `spec-dock canonical status` とログ（`<根>/canonical-sync.log`）を確かめる |
| `SYNC_FAILED` | —（`data.catalogs[].error`） | 1つのカタログの周期の中の予期しない例外（ほかのカタログは続ける） | ログを確かめる |
| `CANONICAL_REMOVE_FAILED` | 6（partial）／5 | `canonical remove --yes` の途中の失敗 | `spec-dock canonical status` で確かめてから `spec-dock canonical remove --yes` |
| 既存：`CANONICAL_NOT_LINKED`、`CANONICAL_GIT_TOO_OLD`、`CANONICAL_FORMAT_UNSUPPORTED`、`OS_ACCESS_DENIED`、`GITHUB_UNAVAILABLE`、`CANONICAL_LOCK_BUSY`、`CANONICAL_UNSAVED_CHANGES`、`CANONICAL_IGNORED_FILES_PRESENT`、`CANONICAL_SANDBOX_DENIED`、`START_LOCK_BUSY` | Epic の12章 | 周期の `last_error`、`resume`、`remove`、手順6 | Epic の12章のとおり |

### 15. コマンドの一覧と引数（`cli/catalog.py`）

| コマンド | 引数 | `HELP_EFFECTS`（Epic の12章） | 変える種類 |
|---|---|---|---|
| `canonical link` | `--no-schedule` を足す | Find or create this clone's catalog, link this checkout, and register periodic sync. | 変える |
| `canonical sync` | `--registered`、`--state-root PATH`、`--loop`、`--detach` | Save, merge and push the catalog once; `--registered` processes every registered catalog; `--loop` keeps running as the resident runner where systemd is unavailable. | 変える |
| `canonical accept` | `paths*`、`--deletions` | Allow held changes to be saved by the next sync. | 変える |
| `canonical restore` | `paths*` | Restore held deletions or paths from the catalog HEAD; no commit. | 変える |
| `canonical resume` | `--adopt-remote`、`--push-local`（どちらか1つ） | Resume a paused catalog after the user decided how to treat the remote. | 変える |
| `canonical remove` | 共通の `--yes`、`--dry-run` | Remove this clone's catalog, links and sync registration after confirming nothing is unsaved. | 変える（確認が要る） |

- `--dry-run` は `canonical sync`、`accept`、`restore`、`resume` では使い方の誤りとして拒否し、`--offline` は `canonical sync` と `resume` で拒否する（予定を示す形を持たないので、黙って保存、push、上書きしないため。実装のレビュー② SP-1）。`canonical link` と `canonical remove` の `--dry-run` は予定を返す。
- 使い方の誤り（`parser.error`、`USAGE_ERROR`）：`--loop` は `--registered` と一緒にだけ、`--detach` は `--loop` と一緒にだけ、`--state-root` は絶対パス、`resume` の2つの引数は同時に使えない、`accept` は `paths` か `--deletions` が要る。
- 公開のコマンドは52個（47 + 5）。`--help` の Target、Reads、Writes、Does not、Preconditions、Confirmation、JSON を、今のコマンドと同じ形で書く。

## data / failure

### データの境界

| データ | 書くもの | 読むもの |
|---|---|---|
| 登録簿 | `canonical link`（手順6）、`canonical remove` | 定期の同期、`canonical status`、`request_sync_now` |
| `state.json` | 定期の同期、`canonical link`（手順7と移動）、`canonical resume`、I-11（`dashboard`） | `canonical status`、`accept --deletions`、`restore`、I-5 |
| `cycle.lock` | 定期の同期、`canonical resume` | — |
| ログ | 定期の同期 | 人 |
| `runner.*`、`kick` | 常駐のプロセス、`request_sync_now`（`kick`） | `canonical status`、`canonical remove`、`loop` の部品 |
| ジョブのファイル | `canonical link`、`canonical remove` | OS |
| カタログのコミット、`origin` の canonical | 定期の同期、`resume --push-local` | — |
| `.runtime/accepted.json` | `canonical accept`、定期の同期（保存したものを消す） | 定期の同期 |
| `.runtime/changesets/` | SpecDock のコマンド（I-2 の部品） | 定期の同期（消す） |
| `.runtime/index.tmp` | 定期の同期 | — |

### 失敗の扱い

| 出来事 | 動き |
|---|---|
| 手順1〜6の途中の例外 | そのカタログの `last_error` に書いて `error`。作業ツリーに書く操作は、早送り（`merge --ff-only`）、`reset --keep`、`restore`（明示の指示）だけである。どれも、Git が書く前に編集中のファイルとの衝突を確かめる。ただし、作業ツリーへの反映の途中でプロセスが殺されると、中途半端になりうる（そのときも、未保存の編集は上書きされない。次の周期の保存が、HEAD との差を保存し直す）。SIGTERM では周期の終わりまで止まらない。`update-ref` は古い値を確かめて進める |
| 保存のコミットの後、統合の前に失敗 | コミットはローカルに残る。次の周期が続きを行う |
| 統合のコミットの後、早送りの前に失敗 | 統合のコミットは参照から外れたまま捨てられる（作業ツリーと HEAD は L のまま）。次の周期が作り直す |
| push の失敗 | 保存はローカルに残る。`unpushed_since` が進み、10分で警告 |
| `state.json` の書き込みの失敗 | その周期の記録を失うだけで、Git の状態は正しい。次の周期で書き直す。基準は push と取得の度に求め直す |
| 手順6の途中の失敗 | `partial`（終了コード6）、効果ごとの `succeeded` と `not_attempted`、`recovery` は `spec-dock canonical link` |
| `canonical remove` の途中の失敗 | `partial`（終了コード6）。消したリンクやカタログは、`canonical link` でもう一度作れる（コミットは `.git` と GitHub に残る） |

## 変更対象

- **足す**：「責務・Interface」の1の表のファイルと、テスト（`tests/unit/domain/test_canonical_sync_rules.py`、`test_canonical_sync_state.py`、`test_canonical_scheduler.py`、`tests/unit/infra/test_canonical_state.py`（登録簿を含む）、`test_canonical_schedulers.py`、`test_canonical_git_sync.py`、`test_runtime_environment_service.py`、`tests/cli_runtime/test_issue430_canonical_sync.py`、`test_issue430_canonical_hold.py`、`test_issue430_canonical_resume.py`、`test_issue430_canonical_remove.py`、`test_issue430_canonical_link_schedule.py`、`test_issue430_canonical_status.py`、`test_issue430_legacy_and_public.py`、`tests/support/canonical_sync.py`（偽の定期の実行、注入した時刻、2つのクローン））。
- **変える**：`canonical_link.py`（`schedule`、手順6・7）、`canonical_status.py`（同期の項目）、`canonical_catalog.py`（RST-1）、`canonical_errors.py`（コード）、`canonical_dispatch.py`（5つの処理と `canonical sync --registered`）、`cli/catalog.py`、`cli/options.py`、`runtime_environment.py`（C11）、`canonical_git.py`（足すだけ）、配布資産 `docs/reference_cli.md` と `static-inventory.json`、コマンドの数と一覧のテスト（47 → 52）、`test_issue428_canonical_mode.py` の `_leaf_arguments`（canonical モードのテスト）。
- **変えない**：従来モードの処理と `.meta.json` のコード、版3の振る舞いのテスト、C4・C5・C6・C10 の部品（`run_catalog_git`、`CatalogLock`、`Changeset`、`ensure_fresh` など）、`StartLock`、選択の記録、利用者のツールの設定、利用側の `spec-dock/`。

## 移行・互換性・rollback

- 版3のリポジトリでは、新しいコマンドは `dispatch()` の今の分岐で `CANONICAL_NOT_MIGRATED` になる。`canonical sync --registered` は登録簿を読むだけなので、版3のリポジトリには触れない（版3のリポジトリは登録されない）。
- 状態の置き場の形式（登録簿、`state.json`、`accepted.json`、`runner.json`）は版1で始める。利用者の環境にはまだ何もない（0.3.0 の前）ので、移行はない。
- rollback：PR を `git revert` すれば戻る。I-10 の前は、本物の環境に登録もジョブもない。I-10 の後に戻すときは、各チェックアウトで `canonical remove --yes` を先に行う（ジョブと登録簿を外すため）。

## testability

### 2台のPCの代わり（`tests/support/canonical_sync.py`）

- I-2 の `tests/support/canonical_repo.py`（`bare_remote`、`clone`、`add_worktree`、`environment`、`isolate_user_state`）の上に、`linked_pair(tmp_path)`（同じ bare から2つのクローンを作り、両方で `canonical link --no-schedule` を済ませる）、`advance(seconds)`（注入した時刻を進める）、`FakeScheduler`（`ensure`、`kick`、`remove`、`observe` の呼び出しを記録し、`kick` で周期をその場で1回動かすかどうかを選べる）を置く。
- 時刻は `canonical_sync.SYNC_CLOCK`（`now()`、`sleep()`）を差し替え、PC名は `canonical_sync.hostname` を差し替える。ファイルの `mtime` は実時刻なので、時刻を進めて30秒と5分を試す。
- 定期の実行は `canonical_scheduling.scheduler_for` を差し替える。spec-dock の実行ファイルは `canonical_scheduling.spec_dock_executable` を差し替える。`FIRST_RUN_WAIT` は0にするか、偽の `kick` で記録を作る。
- GitHub は I-1 の `tests/support/fake_github.py`（`install_fake_gh`）。`repository_for_checkout` は、origin が bare のパスなので、テストで差し替える。

### テストの安全策（`tests/conftest.py`）

- `canonical link` は手順6で定期の実行を登録するので、どのテストも本物の launchd、systemd、切り離した常駐のプロセスに触れてはならない。`tests/conftest.py` が、セッションの単位で（`monkeypatch` の外で）`canonical_scheduling.scheduler_for`、`spec_dock_executable`、`runtime_environment.detect_service_manager`、`canonical_schedule.FIRST_RUN_WAIT` を偽物に替え、さらにテストごとに記録する偽物を置く。テストの中の `monkeypatch.undo()` の後も偽物に戻る（実装の途中に、既存のテストの `undo()` が差し替えを戻し、本番の名前のジョブが一時的に読み込まれたため。報告書）。
- 本物の `LaunchdScheduler` と `SystemdScheduler` は、コマンドの実行器を注入して、単体のテストで直接作る。

### 受け入れ条件との対応

| AC | テスト |
|---|---|
| AC-430-01 | `test_issue430_canonical_sync.py`：同じファイル、変更と削除、拡張子なしと `.` で始まる名前。`test_canonical_sync_rules.py`：`conflict_copy_name`、`resolve_conflicts`、`pc_name` |
| AC-430-02 | `test_issue430_canonical_hold.py`：25件の削除、`accept --deletions`、`restore`、`origin: command` と `finish` の束 |
| AC-430-03 | `test_issue430_canonical_resume.py`：強制 push、削除、共通の祖先のない履歴、`--adopt-remote`、`--push-local`、`git clean -ffdx` の後 |
| AC-430-04 | `test_issue430_canonical_sync.py`：未保存と保留のファイルに当たる早送りと統合 |
| AC-430-05 | `test_issue430_canonical_sync.py`：失敗するフックと `commit.gpgSign=true` |
| AC-430-06 | `test_issue430_canonical_sync.py`：テストが `CatalogLock` を持つ、本当のインデックスの `git add` |
| AC-430-07 | `test_issue430_canonical_link_schedule.py`：`FakeScheduler` の `spec.state_root` と、`XDG_STATE_HOME` を消した `sync --registered` |
| AC-430-08 | `test_issue430_canonical_remove.py` |
| AC-430-09 | `tests/unit/infra/test_canonical_schedulers.py`（常駐のプロセス）、`test_runtime_environment_service.py`、`test_canonical_scheduler.py`、`test_issue430_canonical_sync.py`（`--loop`、`--detach`） |
| AC-430-10 | `test_issue430_canonical_sync.py`：偽の `gh` の要求の記録、`gh` の失敗 |
| AC-430-11 | `test_issue430_canonical_sync.py`：dry-run が bare のリポジトリに届くこと（`push_auth` が `ok`）と、認証の失敗（`push_canonical` の結果を `auth_failed` に差し替える）。`test_canonical_git_sync.py`：標準エラーからの認証の失敗の判定 |
| AC-430-12 | `test_issue430_canonical_link_schedule.py` |
| AC-430-13 | `test_canonical_sync_rules.py`：`select_paths`。`test_issue430_canonical_sync.py`：束 |
| AC-430-14 | `test_canonical_sync_rules.py`：`classify_holds`。`test_issue430_canonical_hold.py` |
| AC-430-15 | `test_issue430_canonical_status.py`（前後の `tree_digest` で書かないことを確かめる。origin の URL を存在しないパスに変えても、同じ結果を返し、偽の `gh` の要求の記録が空であることで、問い合わせないことを確かめる） |
| AC-430-16 | `test_issue430_canonical_link_schedule.py` |
| AC-430-17 | `test_issue429_canonical_link.py` と `test_issue429_canonical_status.py` に足す（canonical モードのテスト） |
| AC-430-18 | 既存の回帰テスト、`test_issue428_legacy_outputs.py` の版3のコマンドの表に新しいコマンドが当たること（新しいテスト `test_issue430_legacy.py`） |
| AC-430-19 | `test_issue430_canonical_sync.py` |
| AC-430-20 | `test_issue430_canonical_sync.py`、`test_canonical_state.py`（公開の部品を直接呼ぶ） |
| AC-430-22 | `test_issue430_canonical_resume.py`（取り込み直しと保留）、`test_issue430_canonical_sync.py`（ディレクトリとファイルの衝突） |
| AC-430-23 | `test_issue430_canonical_sync.py`（push の拒否を偽の `push_canonical` で2回起こす、origin を一時的に読めないパスにする、メッセージと作者） |
| AC-430-24 | `test_issue430_canonical_link_schedule.py`、`test_issue430_canonical_resume.py` |
| AC-430-25 | `test_issue430_canonical_link_schedule.py` |
| AC-430-26 | `test_issue430_canonical_hold.py` |
| AC-430-27 | `test_issue430_canonical_sync.py`、`test_canonical_state.py` |
| AC-430-28 | `test_issue430_canonical_remove.py`（テストが `cycle.lock` を持つ間の remove、途中の失敗を差し替えで起こす） |
| AC-430-21 | 実機の確かめ（報告書） |

### 実機の確かめ（報告書に書く）

- **macOS**：wheel を一時の venv に入れ、内蔵のディスク（`/private/tmp` の下）と外付けのボリューム（scratchpad の下）の一時のリポジトリと一時の bare のリポジトリで、`canonical link --no-schedule`。小さな Python の駆動で、一時の状態の置き場の登録簿に、そのカタログを `update_registry` で載せ、`LaunchdScheduler(label="local.specdock.test.iss-00430", agents_dir=<内蔵のディスクの一時ディレクトリ>)` で bootstrap し、`ProgramArguments` を本物の `spec-dock canonical sync --registered --state-root <一時>` にする。60秒の周期の保存と push、外付けのボリュームの読めないときの `OS_ACCESS_DENIED` と案内を確かめる。同じジョブの中で、本物の URL の存在しない参照名への `git push --dry-run` で、利用者の `gh` の認証が届くことを確かめる（統括の判断 Q9）。終わったら `launchctl bootout`、plist と一時ディレクトリを消す。
- **Linux（systemd）**：`orb create ubuntu:noble specdock-i3-test`、`apt-get install -y git`、wheel を入れ、中で作った一時の bare のリポジトリと2つのクローンで、`SystemdScheduler(unit_dir=<一時>)` ではなく本物の `~/.config/systemd/user` に置く `canonical link`（仮想マシンの中だけ）。タイマーの周期の保存と push、2つのクローンの間の競合（AC-02、AC-03 の代わり）、linger の警告を確かめる。確かめた後に `orb delete -f`。
- **Docker（systemd なし）**：`docker run --rm` のコンテナで、中でクローンした一時のリポジトリで `canonical link` が `loop` を選んで常駐のプロセスを起動すること、2つ目が何もしないこと、`kill` の後の `canonical status` の `CANONICAL_RUNNER_STOPPED` と、もう一度の `canonical link` で動き直すことを確かめる。確かめた後にコンテナとイメージを消す。
- どれも、利用者の `gh` の資格情報を写さない。確かめられないものは「未確認」と書く。

## risk

| リスク | 影響 | 軽減 |
|---|---|---|
| 統合の誤りで、ファイルが消える、古い版で上書きされる | 大 | 早送りと統合の前に、作業ツリーの変更との重なりを確かめる。競合は段の規則だけで解き、両方の版を残す。表せない競合は一時停止。各競合の種類をテストで固める |
| 30秒の規則で書きかけを保存する | 中 | 束のパスはコマンドの排他で守る。人の書きかけは、保存されても次の保存で直る（失われない） |
| 大量の削除が少しずつ保存される | 中 | 今のすべての削除で数える（統括の判断 Q2） |
| 秘密情報の誤判定で、文書が止まる | 低 | トークンの全体の形だけに当てる。`accept` で外せる |
| 同じカタログの周期が重なる | 中 | `cycle.lock`（統括の判断 Q4） |
| 定期の実行が黙って動かない（プライバシーの保護、linger、コンテナの起動し直し） | 中 | 手順6の直後の1回の確かめ、`canonical status` の警告 |
| launchd、systemd の操作が利用者の環境を変える | 中 | 決めた名前のジョブだけを触る。テストは偽物、実機は別の名前のジョブ |
| `kick` や `detach` の誤送信（番号の使い回し） | 低 | `runner.lock` が取れない間だけ SIGTERM を送る |
| 人やエージェントがカタログで手で `git commit` した変更 | 中 | 保留の規則を通らずに push される（手で行ったコミットは利用者の意思とみなす）。文書（I-9）で、カタログで Git を使わないよう書く |
| 開発用の venv や worktree の下の `spec-dock` がジョブの実行ファイルになる | 低 | 最初の登録のときだけ。記録したものが使える間は書き換えない。報告書に残す |
| systemd の既定の `KillMode=control-group` では、停止の SIGTERM が子の git にも届く（`--registered` の周期の遅延は Python のプロセスにしか効かない）。launchd も `ExitTimeOut` の既定 20 秒で SIGKILL する | 低 | Epic の5章のユニットと plist の形を変えないので、`KillMode` と `ExitTimeOut` は足さない（統括に報告）。途中で止まった早送りは、未保存の編集を上書きしない。次の保存と統合で、どちらの版も残る形に戻る |
| エディタの一時ファイル（Emacs の `.#…`、vim の `.swp`）が、30秒を超えると保存される | 低 | canonical の中身（C5、I-2）の `.gitignore` に既定の規則がない。C5 の持ち主と I-9 の文書に申し送る |
| 登録済みのカタログに `--no-schedule` を付けても、登録は外れない | 低 | 印は付くが、ジョブはそのカタログを処理し続ける。外すのは `canonical remove`。報告書に残す |
| launchd の `bootout` の後、`ExitTimeOut` を超える周期が SIGKILL される | 低 | 周期は SIGTERM でカタログの区切りまで止まらない。殺されても、一時のインデックスと lock は次の周期が消す。作業ツリーの途中の反映は、次の保存が直す |
| 並行の Issue（I-4、I-8）との衝突 | 低 | 共有のファイルは `origin/main` の merge で解く |
