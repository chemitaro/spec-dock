---
種別: 設計書（Issue）
ID: "iss-00416"
タイトル: "Restore Active Scope Links For Human Navigation"
関連GitHub: ["#416"]
状態: "draft"
最終更新: "2026-10-13"
依存: ["requirement.md"]
親: ["epic-00080", "init-00079"]
---

# iss-00416 Restore Active Scope Links For Human Navigation — 設計

詳細: [Design Guide](../../../../../../docs/authoring/design.md)

## 設計目標

- 直接記録を publish / 削除した操作の最後に、3つの閲覧用リンクを1回だけ同期する（RQ-416-01/02）。
- リンクの読み書きを1つの infra adapter に閉じ込め、選択判定の経路からは参照しない（RQ-416-03）。
- 役割ごとの単一 `rename` で置き換え、multifile transaction・snapshot・rollback を持たない（制約）。
- 3つのリンク名と既知の旧生成物6件以外に触れない（RQ-416-05）。

## Current / Target

| 観点 | Current（0e7dc868） | Target |
|---|---|---|
| `work start` 成功 | `selection.publish` のみ | 続けて3リンクを直接対象と祖先へ同期 |
| `active clear` / `work finish` で記録を削除 | `selection.clear` のみ | 続けて3リンクを `system/active-none/<role>` へ同期 |
| `active set @current`（同じ直接対象） | `unchanged`、書込なし | リンクが既に正しければ `unchanged`。ずれていれば修復して `succeeded`（Q3） |
| `active show` などの読み取り | 書込なし | 変更なし（リンクを読まず、書かない） |
| 旧 `active/` の旧生成物（`context-pack.md` 等6件） | 触れない | リンク同期時に削除（ファイル・symlink のみ） |
| 旧 `active/` の未知ファイル | 触れない | 触れない |
| `cli_text.render_active_show_text` | 未使用。旧 fallback と `active set <target>` を案内 | 未使用の旧 renderer（`render_active_show_text` / `ActiveViewResult` 系）を除去 |

## 責務・Interface

### 役割の決定（domain）

`domain/active_links.py`（新規、純関数）:

```python
Role = Literal["initiative", "epic", "issue"]

@dataclass(frozen=True)
class LinkPlan:
    role: Role
    target: str  # spec-dock/ からの相対 POSIX path（例: "initiatives/init-.../epics/epic-..."）

def plan_links(chain: tuple[tuple[str, str], ...] | None) -> tuple[LinkPlan, ...]:
    """chain は (kind, spec-dock 相対 path) の祖先→直接対象の列。None は未選択。
    役割が chain にあればその path、無ければ "system/active-none/<role>"。常に3件を返す。"""
```

### リンクの同期（infra）

`infra/active_links.py`（新規）:

```python
LEGACY_GENERATED = ("context-pack.md", "current-runbook.json", "current-runbook.md",
                    "initiative.path", "epic.path", "issue.path")

@dataclass(frozen=True)
class LinkOutcome:
    role: Role
    status: Literal["planned", "succeeded", "unchanged", "skipped"]
    reason: str | None  # skipped のときだけ（"occupied" / "active_not_directory" / "target_missing" / OSError 要約）

@dataclass(frozen=True)
class LegacyOutcome:
    name: str
    status: Literal["planned", "succeeded", "skipped"]
    reason: str | None  # skipped のときだけ（"not_a_file" / OSError 要約）

def sync_active_links(
    specdock_dir: Path, plans: tuple[LinkPlan, ...], *, dry_run: bool
) -> tuple[tuple[LinkOutcome, ...], tuple[LegacyOutcome, ...]]
```

手順:

0. `git ls-files -- spec-dock/active` が空であること（追跡ファイルがあれば `skipped("tracked")`）と、`git check-ignore --no-index` で `spec-dock/active/<role>` と旧生成物の名前が Git に無視されることを確かめる（application 側で実施）。無視されない名前があれば、何も書かず何も消さずに全役割 `skipped("not_ignored")`。リンクで worktree を dirty にして次の Start（clean 前提）を妨げないため。
1. `spec-dock` と `spec-dock/active` を `O_DIRECTORY | O_NOFOLLOW` で開き、以降の stat・readlink・symlink・rename・unlink はすべてこの fd を起点（`dir_fd`）に行う。検査後に root が差し替えられても、書込・削除は検査したディレクトリの中に留まる（FQG-416-001）。`active` が無ければ `mkdir(dir_fd=...)` してから開く。以下は fd 上の観測として読む。`spec-dock/active` を `lstat`。存在しなければ `mkdir`（mode 0o755）。シンボリックリンク・ディレクトリ以外なら全役割 `skipped("active_not_directory")`。
2. 役割ごとに、リンク文字列を `os.path.relpath(specdock_dir / plan.target, specdock_dir / "active")` で求める（例: `../initiatives/...`、`../system/active-none/issue`）。
3. リンク先ディレクトリが存在しなければ `skipped("target_missing")`。
4. `active/<role>` を `lstat`:
   - 不在: 作成する。
   - シンボリックリンクで `readlink` が一致: `unchanged`。
   - シンボリックリンクで不一致: 置き換える。
   - それ以外（実体ファイル・ディレクトリ）: `skipped("occupied")`。読まない・変更しない。
5. 置き換え・作成は `active/.<role>.<token>.tmp` に `symlink` してから `os.replace` で `active/<role>` に移す。失敗時は一時リンクだけを `unlink` する（best effort）。
6. `LEGACY_GENERATED` の各名前を `lstat` し、不在なら何もしない（結果に出さない）。通常ファイルまたはシンボリックリンクなら `unlink`（リンク先は辿らない）して `succeeded`。ディレクトリなどそれ以外は `skipped("not_a_file")`。中身は読まない。1 の判定で `active` が使えない場合は行わない。
7. `dry_run=True` のときは 1〜4 の観測だけを行い、書くはずの役割を `planned`、既に一致する役割を `unchanged` として返す。

役割ごとに独立した `rename` なので、3つの間の原子性は持たない。途中で失敗しても、成功した役割は戻さない。

### 呼び出し（application）

`application/active_links.py`（新規、薄い orchestration）:

```python
def links_for_selection(context, views, scope_id: str | None) -> tuple[LinkPlan, ...]
def apply_links(context, plans, *, dry_run) -> tuple[tuple[Effect, ...], tuple[Diagnostic, ...]]
```

- `scope_id` から `ancestors_for` と ScopeView の path（`spec-dock/` 相対）で chain を作る。導出に失敗したら未選択と同じ fallback にはせず、全役割を warning にする。
- `LinkOutcome` を effect / warning に変換する（下記）。

呼び出し点:

| 呼び出し元 | 時機 | 対象 |
|---|---|---|
| `work_start.start_work` | `selection.publish` が `succeeded` になり、`WorkTargetStore` と Start lock を出たあと | 新しい直接対象 |
| `work_start.start_work`（dry-run） | planned effects の最後 | 新しい直接対象（`planned`） |
| `direct_active.clear_direct` | 1件以上 `selection.clear` が `succeeded` のあと | 未選択（fallback） |
| `direct_active.clear_direct` | 選択が元から空で、解除対象が無く `unchanged` になる直前 | 未選択（修復。書いたら `succeeded`） |
| `direct_active.clear_direct`（dry-run） | planned effects の最後 | 未選択 |
| `direct_finish` | `selection.clear` が `succeeded` のあと | 未選択 |
| `direct_finish`（dry-run） | `selection.clear` を planned にしたときだけ、planned effects の最後 | 未選択 |
| `direct_active.set_direct` | 同じ直接対象で `unchanged` を返す直前（Q3） | 現在の直接対象 |
| `direct_active.set_direct`（dry-run） | 同上。書かずに `planned`、何も要らなければ `unchanged` | 現在の直接対象 |

扱わない経路: `work start` の `unchanged`（早期 return）、選択が残る `active clear` の `unchanged`、`selection.*` が `failed` / `unknown` / `not_attempted` の経路、読み取りコマンド。

`work start` のリンク先は、checkout 後の候補 tip から読んだ `candidate.views` で求める。ScopeView の `path` は解決済みの絶対 path なので、`spec-dock/` 配下であることを確かめてから相対化する。


### 出力（presentation）

Q1 推奨案:

- 成功: `Effect("active.link", "succeeded" | "unchanged", "<role>")`。`--dry-run` では書く役割だけを `planned` で出し、既に一致する役割は出さない（`planned` 結果は `planned` 以外の effect を持てないため）。
- 旧生成物の削除: `Effect("active.legacy.remove", "succeeded", "<name>")`。dry-run では `planned`。`skipped` は `Diagnostic("ACTIVE_LEGACY_NOT_REMOVED", ...)` を warnings に入れる。
- `skipped`: effect には出さず、`Diagnostic("ACTIVE_LINK_NOT_UPDATED", "<role>: <reason>", {"role": role, "reason": reason})` を warnings に入れる。status / exit は選択側の結果のまま（exit 0）。
- 理由: `OperationResult` は `succeeded` に `failed` effect を許さず、`partial` は exit 6 と recovery を要求する。閲覧用リンクの失敗で agent に回復手順を走らせない。

`set_direct`（Q3）: リンクを1件以上書くか旧生成物を1件以上削除したら `succeeded`、すべて `unchanged` なら従来どおり `unchanged`。catalog の説明文を「同じ直接対象では選択を変えず、閲覧用リンクだけを修復する」に更新する。

## data / failure

| 状況 | 振る舞い |
|---|---|
| `active/` が無い | 作成する |
| `active` がシンボリックリンク・ファイル | 全役割 warning、書込・削除なし |
| 旧生成物が通常ファイル・symlink | 削除（effect） |
| 旧生成物と同名のディレクトリ | warning、変更なし |
| `active/<role>` が実体 | その役割 warning、変更なし |
| リンク先が無い（`active-none` 欠落、Scope 削除） | その役割 warning |
| `symlink` / `replace` の OSError | その役割 warning、一時リンクを消す。他の役割は続ける |
| 祖先の導出失敗 | 全役割 warning |
| `active/` が Git に無視されない、または配下に追跡ファイルがある | 全役割 warning、書込・削除なし |
| リンク先の観測で権限エラーなど | その役割 warning（例外として上へ伝えない） |
| 想定外の OSError | application 層で全役割 warning に変換し、選択の結果は変えない |
| 選択効果が失敗・unknown | リンク処理なし |

永続的な状態は追加しない。リンク自体が唯一の結果であり、次の選択操作で上書きされる。

## 変更対象

変更する:

- `src/spec_dock/runtime/domain/active_links.py`（新規）
- `src/spec_dock/runtime/infra/active_links.py`（新規）
- `src/spec_dock/runtime/application/active_links.py`（新規）
- `src/spec_dock/runtime/application/{work_start,direct_active,direct_finish}.py`（呼び出し追加）
- `src/spec_dock/runtime/cli/catalog.py`（`active set` の説明、Q3）
- `src/spec_dock/runtime/presentation/cli_text.py`、`application/contracts.py`（未使用の旧 active renderer / 型の除去）
- `src/spec_dock/assets/spec_dock/system/{README.md,active-none/README.md}` と `static-inventory.json` の hash
- `src/spec_dock/assets/install_root/.agents/skills/spec-dock/SKILL.md`（`active set` が同じ直接対象でリンクを修復すること、Start / Clear / Finish が閲覧用リンクを同期し、リンクは正本ではないこと）
- tests（`tests/unit/domain`、`tests/unit/infra`、`tests/cli_runtime/test_issue413_active.py` ほか）

変更しない:

- `WorkTargetStore`、Start lock、直接記録の schema
- `spec-dock/.gitignore`（`active/` は無視済み）
- `active show`、`scope *`、`workspace *` の読み取り経路
- 旧 writer と legacy reader

## 移行・互換性・rollback

- 移行: 不要。既存 worktree は次の `work start` / `active clear` / `work finish`、または `active set @current`（Q3）でリンクが作られる。
- 旧 consumer: 旧 writer が作った `active/{initiative,epic,issue}` はシンボリックリンクなので置き換え対象。既知の旧生成物6件は削除する（Q4）。これは AC-413-36 の保全範囲を狭める変更であり、report に記録する。
- 既存テスト `test_active_clear_preserves_legacy_manifests_projections_and_cache_bytes` の fixture は `active/` を Git に無視させないため、新契約でも `not_ignored` で何も書かず、`active/` 全体の digest 不変がそのまま成り立つ。変更せずに残す。`active/` を無視させた場合の削除と保全（既知旧生成物の削除、同名ディレクトリ・未知名・`.work/` の不変）は `tests/cli_runtime/test_issue416_active_links.py` で別に確認する。`test_active_set_existing_direct_...` も同じ理由で変更不要。リンクが既に正しい場合の `unchanged` と修復時の `succeeded` は Issue 416 のテストで確認する。
- rollback: 削除した旧生成物は復元しない（現行が更新しない派生物のため）。このリンク機能を戻しても、リンクは Git 無視の派生物なので残置しても無害。コード revert のみで戻せる。

## testability

- domain: `plan_links` の役割割当（Initiative / Epic / Issue 直接、未選択）。
- infra: tmp dir で 作成 / 一致 unchanged / 置換 / 実体 occupied / `active` が symlink / target_missing / dry-run 無書込 / 置換中 OSError で一時リンクが残らない / 旧生成物の削除（ファイル・symlink は削除してリンク先は残る、ディレクトリは不変）/ 未知名は不変。
- cli_runtime: `work start`（Issue・Epic 直接）、`active clear`、`work finish`、dry-run、`active show` 無書込、旧ファイル保全、Q3 の修復、warning 時の exit 0。
- fresh wheel: 外部 console で `work start` → `ls -l spec-dock/active` → `active clear` を確認。

## risk

- Start の後段に書込が増える: lock の外で行い、Start の排他時間を延ばさない。
- 同じ worktree での並行操作によるリンクのずれ: 正本ではないことを README と RQ-416-03 で明示し、Q3 の修復手段で回復する。
- Issue 413 D-01「第二の閲覧状態を増やさない」との関係: リンクは状態として読まれないため、選択状態は増えない。この Issue で D-01 の閲覧側の判断を上書きすることを report に記録する。
