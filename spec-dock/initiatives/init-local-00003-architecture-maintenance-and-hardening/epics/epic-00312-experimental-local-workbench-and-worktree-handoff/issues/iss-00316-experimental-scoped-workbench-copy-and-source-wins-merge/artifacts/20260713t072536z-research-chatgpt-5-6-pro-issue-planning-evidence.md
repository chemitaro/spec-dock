# 暫定結論

GitHub コネクタによる現行ブランチの確認は成功しました。`iss-00316-experimental-scoped-workbench-copy-and-source-wins-merge` には Issue #316 の node と計画用スケルトンが存在しますが、`requirement.md` は未具体化、`design.md`／`plan.md` は assurance compose 前の placeholder です。Issue #315 は完了済みで、Issue #316 の依存先として記録されています。したがって、現時点は **Issue planning evidence を作成できるが、正本採用・review pass・execution-ready を主張できない状態**です。

以下は、添付 planning brief を task contract とした **evidence-only の日本語候補**です。正本へ反映する場合は、まず `requirement.md` を具体化し、`assurance classify --stage requirement` と `assurance compose --artifact all` を経て profile 別テンプレートを materialize し、その後 fresh `spec-reviewer` を通す必要があります。 

`information_insufficient` に該当する material な product decision 不足は検出していません。exact symbol、error/result field、resolver 抽出単位、cross-platform symlink test 範囲は Issue-local choice として残ります。

---

# 1. リポジトリ確認結果

| 確認事項               | 現行ブランチでの事実                                                                      | 計画への含意                                                  |
| ------------------ | ------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Issue 状態           | #316 は open。node は `iss-00316` で、親は `epic-00312`、依存は `iss-00315`                | W1 完了後の W2 として計画可能                                      |
| CLI                | `worktree` には create/list/show/remove があるが、`workbench` group はない                | `workbench copy` を新規追加                                  |
| Registry           | `worktree_commands` は登録済みだが、workbench command module はない                        | `commands/workbench.py` と registry entry が必要            |
| Target selector    | stable ID、absolute path、basename を解決。ambiguous basename、branch-only、missing を区別 | selector semantics を複製せず再利用                             |
| Target inventory   | current、main、path existence、bare、managed classification 等を保持                    | copy 固有 eligibility を application で追加                   |
| Scope repository   | `NodeRepository.load_node_records(specdock_dir)` が利用可能                          | source/target の SpecDock tree を別々にロード                   |
| W1 opaque boundary | metadata walk は `.workbench` を top-down で prune                                 | copy command 自身だけが explicit operation として Workbench を読む |
| Filesystem port    | 現在は `path_exists` と `remove_target` のみ                                          | 最小の recursive merge operation を追加                       |
| Provider/dogfood   | 現在の provider と dogfood parser は同じ SHA                                           | provider-first、通常 update による projection を維持             |
| Final delivery     | Issue #319 が 315–318 全てに依存                                                      | #316 では PR を作らず、#319 に delivery を relay                 |

根拠として、現行 parser には `workbench` group がなく、registry にも workbench command 登録がありません。

既存 selector は ID、absolute path、basename を扱い、ambiguous target、branch-only、not found を安定して区別しています。既存テストでも、この三形式と ambiguity／branch rejection が固定されています。

`NodeRepository` は任意の `specdock_dir` から record をロードでき、`.workbench` を metadata traversal から除外済みです。一方、FilesystemGateway は copy operation をまだ持ちません。

provider と dogfood の parser は現時点で同一 SHA `ac83b4e...` です。Issue #316 でもこの provider-authority／consumer-projection 関係を維持するのが妥当です。

---

# 2. `requirement.md` 候補

## 2.1 目的

> Current worktree の一つの Initiative／Epic／Issue に属する scoped `.workbench/` を、利用者が明示した場合に限り、同一 Git repository の別 linked worktree に one-shot copy できるようにする。
> Copy は source と target で同じ scope ID を独立解決し、destination-only entry を保持しながら同一 relative path では source を優先する。Workbench の non-canonical、disposable、no-sync という権限境界は変更しない。

親 Epic は、current source、一つの scope ID、一つの same-repository target、root exclusion、独立 scope 解決、無分類 copy、source-wins、no-sync を固定しています。

## 2.2 観測可能な成果

完了後に観測できること:

* `spec-dock workbench copy --scope <id> --to <target> [--json]` が利用できる。
* Target は既存 worktree command と同じ stable ID、absolute path、basename で選択できる。
* Source と target で directory slug が異なっても、同じ scope ID の実ディレクトリが独立に解決される。
* Source `.workbench` の entry が target scope 直下の `.workbench` に recursive merge される。
* Destination-only entry は保持され、同一 relative leaf は source の内容または link object になる。
* 同一入力での再実行は、並行 mutation がなければ同じ target tree を生成する。
* 成功・失敗の text／JSON が experimental、non-canonical、disposable、one-shot、no-sync を明示する。

完了後に観測できてはいけないこと:

* `--from`、root Workbench、date bucket、任意 path を選ぶ copy route。
* Cross-repository copy、automatic hook、watcher、sync、copy-back。
* Extension、language、MIME、secret、archive、`.env`、nested `.git` による選別。
* File contents、secret-like value、全 entry list の出力。
* Copy 成功から canonical adoption、review pass、durable evidence、synchronization が導かれること。

## 2.3 Issue 種類と推奨 grade

該当候補:

* [x] 新規振る舞いの追加
* [x] CLI／script 挙動変更
* [x] 既存 workspace との互換性を伴う変更
* [x] filesystem path containment に関係する変更
* [ ] metadata schema／migration
* [ ] GitHub state mutationを実装する変更
* [ ] workflow／skill policy 変更

推奨 profile は **`strict`** です。公開 CLI、既存 worktree selector との互換性、destination overwrite、symlink／path containment、部分失敗を扱うため、Standard より強い closure、failure、compatibility、review gate が必要です。

Critical への引き上げ条件は、arbitrary host path、cross-repository transfer、automatic copy、canonical tree overwrite、境界外 write を許す必要が判明した場合です。現在の親契約どおり、明示 one-shot、same-repository、scope-local、disposable Workbench に閉じる限りは strict 候補とします。最終 profile は assurance classification の結果が authority です。Strict planning では closure index、delegation、step-local tests、S90、S99 が必須です。

## 2.4 親 trace

| Issue requirement | 内容                                                                                                                                    | 親 trace                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------- |
| `RQ-316-001`      | 明示 one-shot command。Source は current、scope と target は各一件。`--from` なし                                                                  | E-RQ-006、007、014             |
| `RQ-316-002`      | Stable ID／absolute path／basename の target semantics を共有し、missing、ambiguous、branch-only、path-missing、bare、same-current を mutation 前に拒否 | E-RQ-008、011                 |
| `RQ-316-003`      | Scope ID を source／target で独立解決し、source slug／relative path を転写しない                                                                      | E-RQ-008、011                 |
| `RQ-316-004`      | Source scoped `.workbench` が存在しない場合は `no_source`。Target を変更せず root fallback もしない                                                      | E-RQ-011、012                 |
| `RQ-316-005`      | 通常の recursive filesystem copy とし、semantic content classifier を持たない                                                                    | E-RQ-009                     |
| `RQ-316-006`      | Destination-only を保持し、同一 relative leaf は source wins。再実行は冪等                                                                           | E-RQ-010                     |
| `RQ-316-007`      | Source descendant symlink は非 dereference copy。Scope／Workbench root escape と destination symlink ancestry write を防止                    | E-RQ-011                     |
| `RQ-316-008`      | I/O／type collision failure を成功にせず、tree-wide transaction／rollback は実装しない                                                               | E-RQ-012                     |
| `RQ-316-009`      | Help、text、JSON に experimental 等を明記し、contents を出力しない                                                                                   | E-RQ-016                     |
| `RQ-316-010`      | Provider authority、dogfood parity、Issue #319 への deferred delivery を維持                                                                 | E-RQ-017、Epic W2/W5 boundary |

## 2.5 対象範囲

**In scope**

* `workbench copy` parser、registry、command handler。
* Request／result／error contract と bootstrap wiring。
* Existing worktree target selector の最小抽出または公開化。
* Source／target scope record の独立解決。
* Safe recursive source-wins merge port／adapter。
* Path containment、symlink non-dereference、destination ancestry guard。
* Help／text／JSON。
* Provider runtime、dogfood projection、focused tests。
* Manual two-linked-worktree handoff。
* Issue-local report、review、commit、push、Issue Finish、Issue #319 への relay evidence。

**Out of scope**

* Root Workbench／date bucket／arbitrary path copy。
* Cross-repository copy、copy-back、watcher、background sync。
* Manifest、catalog、session、TTL、retention、copy history。
* Secret scan、content allowlist／denylist、archive inspection。
* Tree-wide transaction、backup、rollback log。
* Copy countersや全 entry accounting。
* Artifact import、ChatGPT preservation workflow。
* Epic-level final reference documentation、Epic PR、merge preparation。

**Unchanged**

* `worktree create/list/show/remove` の公開 semantics。
* `.workbench` の Git-ignore／opaque discovery contract。
* Node metadata schema、artifact grammar、active state、sync output。
* Scope delete／worktree remove の既存挙動。
* `spec-dock update` の Workbench preservation。

## 2.6 受け入れ条件

| ID           | 操作                                                                                                       | 期待結果・観測点                                                                                                                    |
| ------------ | -------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `AC-316-001` | `workbench copy --help` と parser negative cases を確認                                                      | `--scope`、`--to`、`--json` のみ。`--from`、root/date/path route なし。Help に experimental／non-canonical／disposable／one-shot／no-sync |
| `AC-316-002` | Target を stable ID、absolute path、basename で選択し、missing／ambiguous／branch-only／stale／bare／same-current も試す | 有効三形式は同じ worktree に解決。無効 case は copy 開始前に stable error。Target filesystem は未変更                                               |
| `AC-316-003` | Source と target に同じ ID、異なる directory slug の scope を用意                                                    | Source path を転写せず、両 tree で解決した各 scope direct child を使用                                                                      |
| `AC-316-004` | Source scoped `.workbench` がない状態で実行                                                                      | `no_source`。Target `.workbench` がない場合は作成せず、既存の場合も byte-for-byte 不変。Root fallback なし                                         |
| `AC-316-005` | Source-only、destination-only、same-relative-path leaf を含めて実行し再実行                                          | Destination-only を保持、source-only を追加、same leaf は source wins。再実行結果は同じ                                                       |
| `AC-316-006` | Python、config、binary、archive、`.env`、nested `.git` を含めて実行                                                 | Command 固有の semantic filtering や内容解析なし。Copy 後 bytes／tree shape が一致                                                          |
| `AC-316-007` | Source symlink、destination symlink ancestry、scope／Workbench root escape fixture を試す                      | Source link は link object として複製。境界外を read/write せず、external sentinel 不変                                                     |
| `AC-316-008` | Permission、copy primitive、type collision fault を注入                                                       | Success を返さず `copy_failed`。自動 rollback なし。部分変更の可能性を明示し、contents は表示しない                                                      |
| `AC-316-009` | 成功／各失敗の text と JSON を確認                                                                                  | Stable code、scope／target identity、experimental 等を表示。File body、secret sentinel、全 path list は含まない                             |
| `AC-316-010` | Provider → dogfood update、fresh consumer、manual linked-worktree scenario を実行                             | Runtime parity、既存 Workbench preservation、manual handoff／rerun が成立。PR は作らず #319 向け relay evidence を残す                        |

これらは親 E-AC-003〜009 の Issue-local closure に対応します。

## 2.7 例外・エッジケース

| ID           | 条件                                                      | 期待される扱い                                                                    | Mutation           |
| ------------ | ------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------ |
| `EC-316-001` | Scope が root、date、path、ADR ID、invalid ID                | `invalid_scope:unsupported`                                                | なし                 |
| `EC-316-002` | Target missing／ambiguous／branch-only                    | Existing selector-compatible error                                         | なし                 |
| `EC-316-003` | Target path missing、bare、same current                   | `target_not_eligible` + stable reason                                      | なし                 |
| `EC-316-004` | Source／target scope missing、ambiguous、inventory invalid | `invalid_scope` + `side`／`reason`                                          | なし                 |
| `EC-316-005` | Source `.workbench` missing                             | `no_source`                                                                | なし                 |
| `EC-316-006` | Source／target scopeまたは Workbench root が symlink／escape  | `unsafe_path`                                                              | なし                 |
| `EC-316-007` | Destination directory ancestry に symlink                | その symlink を辿らず、安全な leaf replacement が成立しない場合は `unsafe_path`／`copy_failed` | 開始前または部分           |
| `EC-316-008` | Directory／non-directory type mismatch                   | `copy_failed:type_collision`。Destination subtree を暗黙削除しない                  | 先行 entry は部分変更の可能性 |
| `EC-316-009` | Copy 中の I/O failure                                     | `copy_failed`。自動 retry／rollback なし                                         | 部分変更の可能性           |
| `EC-316-010` | 実行中の concurrent source／target mutation                  | 成功保証対象外。観測した I/O／state failure を返す                                         | 不定、rollback なし     |

---

# 3. `design.md` 候補

## 3.1 主要設計契約

| Design ID     |   固定度 | 契約                                                                                                     |
| ------------- | ----: | ------------------------------------------------------------------------------------------------------ |
| `DES-316-001` | `[N]` | Public surface は `workbench copy --scope <id> --to <target> [--json]`。Source は current runtime context |
| `DES-316-002` | `[P]` | Existing worktree inventory／target resolver を application-level で最小再利用し、selector logic を複製しない          |
| `DES-316-003` | `[N]` | Source／target SpecDock tree で scope ID を独立解決する                                                         |
| `DES-316-004` | `[N]` | Target eligibility、scope、containment、`no_source` の全 preflight 完了まで target を変更しない                       |
| `DES-316-005` | `[P]` | Infra に専用の小さな recursive source-wins merge primitive を置く                                                |
| `DES-316-006` | `[N]` | Source symlink は非 dereference、destination ancestry は lstat-based guard、境界外 read/write なし               |
| `DES-316-007` | `[P]` | Compact stable error catalog と content-free text／JSON result                                           |
| `DES-316-008` | `[N]` | Provider が実装 authority、dogfood は通常 update で生成／検証                                                       |
| `DES-316-009` | `[N]` | No transaction、no sync、no manifest、no counters、delivery は #319                                         |

## 3.2 レイヤ構成

```text
cli/parser.py
  └─ workbench copy parser
cli/registry.py
  └─ commands.workbench registration

commands/workbench.py
  ├─ WorkbenchCopyArgs
  ├─ request construction
  └─ text / JSON renderer selection

application/workbench_copy.py
  ├─ target selection
  ├─ target eligibility
  ├─ source/target SpecDock location
  ├─ independent scope resolution
  ├─ no_source / containment preflight
  └─ filesystem merge orchestration

application/worktree.py
  └─ existing inventory / selector helpers exposed for reuse
     または
application/worktree_target.py
  └─ neutral minimal extraction

application/contracts.py
  ├─ WorkbenchCopyRequest
  ├─ WorkbenchCopyResult
  └─ WorkbenchCopyError

application/ports.py
  └─ FilesystemGateway.merge_workbench_tree(...)

infra/fs_cli.py
  └─ non-dereferencing recursive merge implementation

presentation/cli_text.py
  ├─ success text / JSON
  └─ error text / JSON

cli/bootstrap.py
  └─ port + use-case wiring
```

現行 command handler は typed args → use case → text/JSON renderer という形を採っています。この形をそのまま workbench command に適用するのが最小です。

## 3.3 Request／result 候補

```python
@dataclass(frozen=True)
class WorkbenchCopyRequest:
    scope_id: str
    target: str
```

Source root と SpecDock path は caller input にせず、既存 `Ports.repo_root`／`Ports.specdock_dir` から取得します。これにより `--from` や arbitrary source path が型境界へ入ることを防ぎます。Bootstrap は現在この二つを runtime context に保持しています。

```python
@dataclass(frozen=True)
class WorkbenchCopyResult:
    scope_id: str
    source_worktree: WorktreeRecordView
    target_worktree: WorktreeRecordView
    source_scope_path: Path
    target_scope_path: Path
    source_workbench_path: Path
    target_workbench_path: Path
    warnings: list[str]
```

Result に file count、overwrite count、entry list、hash manifest は含めません。

JSON 共通 semantic fields 候補:

```json
{
  "status": "ok",
  "command": "copy",
  "experimental": true,
  "canonical": false,
  "disposable": true,
  "one_shot": true,
  "sync": false
}
```

## 3.4 Scope ID contract

既存 `domain.ids.parse_id()` を再利用し、新しい regex を作らない候補です。`parse_id` は canonical node ID grammar を処理できるため、prefix が `init`／`epic`／`iss` の場合だけ許可し、`adr` は scope 対象外として拒否します。Numeric shorthand は受けず、exact full ID を要求します。

解決手順:

1. `parse_id(scope_id)`。
2. Prefix が `init`／`epic`／`iss` 以外なら `invalid_scope:unsupported`。
3. Source `NodeRepository.load_node_records(source_specdock_dir)`。
4. Target `NodeRepository.load_node_records(target_specdock_dir)`。
5. 各 inventory で `record.id == scope_id` かつ kind が対応する record を exactly one 解決。
6. Source record path を target path として再利用しない。

Production loader は duplicate ID を record return 前に拒否します。そのため production の duplicate は `invalid_scope:inventory_invalid` へ翻訳し、fake port／defensive case で複数 match が返った場合のみ `reason=ambiguous` とする候補です。

## 3.5 Target SpecDock location

`"spec-dock"` を target path に hard-code しない候補です。

```python
source_repo_root = ports.repo_root
source_specdock_dir = ports.specdock_dir

specdock_relative = source_specdock_dir.relative_to(source_repo_root)
target_specdock_dir = target_worktree.path / specdock_relative
```

この計算前に source SpecDock が source repo 内に containment されることを確認します。Target SpecDock が存在しない、または対象 scope がない場合は target scope missing として mutation 前に失敗します。

Target が同一 repository である根拠は、current repository に対する `git worktree list --porcelain` の record からのみ選択することです。Git adapter は path、head、branch、detached、bare、locked を既に取得しています。

## 3.6 Target selector／eligibility

Selector semantics:

* Stable ID: 許可。
* Absolute path: canonical comparisonで許可。
* Directory basename: 一意なら許可。
* Branch name: 拒否。
* Missing／ambiguous: 拒否。
* Managed classification unavailable／external worktree: **許可**。同一 Git worktree inventory に載ることが repository identity であり、`SPEC_DOCK_WORKTREE_ROOT` の classification は copy eligibility にしない。
* Main worktree: Current でなければ許可。
* Current worktree: 拒否。
* Path missing／bare: 拒否。
* Detached／locked: 親契約に禁止がないため、それだけでは拒否しない。通常 filesystem failure は別途伝播。

既存 runtime は worktree root classification が利用できなくても list／show と selector を成立させています。

## 3.7 Preflight と mutation ordering

```text
1. Runtime ports の存在確認
2. Scope ID grammar / supported kind
3. Git worktree inventory
4. Target selector resolution
5. same-current / path-missing / bare eligibility
6. Source SpecDock relative location導出
7. Source scope independent resolution
8. Target scope independent resolution
9. Source/target scope containment
10. Source .workbench lstat
11. missingなら no_source
12. Source Workbench root / target destination root safety
13. Filesystem merge開始
14. Structured result
```

Step 1〜12 では target filesystem を変更しません。Target `.workbench` は merge 呼出し後、必要な場合だけ作成します。

## 3.8 Recursive merge adapter

Port 候補:

```python
class FilesystemGateway(Protocol):
    def path_exists(self, path: Path) -> bool: ...
    def remove_target(self, path: Path) -> None: ...
    def merge_workbench_tree(
        self,
        *,
        source_root: Path,
        destination_root: Path,
        source_scope_root: Path,
        target_scope_root: Path,
    ) -> None: ...
```

責任を command handler に置かず、`infra/fs_cli.py` の dedicated operation に閉じます。現状の adapter は `lstat` を用いた path existence／unlink／rmtree の基礎を持っています。

### Entry matrix 候補

| Source entry                        | Destination entry          | 動作                                                                |
| ----------------------------------- | -------------------------- | ----------------------------------------------------------------- |
| directory                           | missing                    | directory を作り recurse                                             |
| directory                           | real directory             | destination-only child を残して recurse                               |
| directory                           | symlink／non-directory      | Symlink を辿らず `copy_failed:type_collision`                         |
| regular／ordinary leaf               | missing                    | Standard copy primitive で copy                                    |
| regular／ordinary leaf               | non-directory leaf／symlink | Destination leaf を `lstat` 後に非 dereference removeし、source leafで置換 |
| regular／ordinary leaf               | directory                  | `copy_failed:type_collision`。Destination subtreeを暗黙削除しない          |
| symlink                             | missing／non-directory leaf | `readlink` した link text を link object として配置                       |
| symlink                             | directory                  | `copy_failed:type_collision`                                      |
| unsupported／unhandled special entry | 任意                         | Standard primitive の failure として command failure。Skipしない          |

この matrix は次を同時に満たします。

* Destination-only subtree を保持する。
* Same-relative leaf では source wins。
* Existing destination symlink を filesystem traversal として使用しない。
* Directory／leaf collision を黙って destructive replacement しない。
* Content／extension／secret classifier を作らない。

`shutil.copytree(..., dirs_exist_ok=True, symlinks=True)` を単独使用すると既存 destination symlink ancestry を経由し得るため、source entry を `follow_symlinks=False` で走査し、destination parent を `lstat` で検証する小さな wrapper が必要です。これは generic filesystem framework に拡張しません。

## 3.9 Symlink／containment contract

* Source scope、target scope、source Workbench root、target Workbench root は lexical containment と physical containment の両方を確認。
* Scope root または Workbench root 自体が symlink の場合は拒否。
* Source traversal は `os.scandir` 等の `follow_symlinks=False` 相当を使用。
* Source descendant symlink は target text を解決せず `readlink` し、link object として再作成。
* Destination の各 parent component は `lstat` し、directory として進む位置に symlink がある場合は recurse しない。
* Source leaf と衝突する destination symlink は、symlink 自身だけを unlink して source leaf に置換できる。
* External symlink target は read／delete／write しない。
* TOCTOU の完全排除、filesystem transaction、concurrent mutation protection は non-goal。Race で検証前提が崩れた場合は copy failure。

## 3.10 Error catalog 候補

既存 selector code は維持し、Workbench 固有 code を少数に限定します。

| Code                        | Stable fields                                           | 用途                                                        |
| --------------------------- | ------------------------------------------------------- | --------------------------------------------------------- |
| `git_worktree_list_failed`  | `target`                                                | Existing inventory failure                                |
| `target_not_found`          | `target`                                                | Existing selector                                         |
| `ambiguous_target`          | `target`, `candidates`                                  | Existing selector                                         |
| `unsupported_branch_target` | `target`                                                | Existing selector                                         |
| `target_not_eligible`       | `target`, `worktree`, `reason`                          | `same_worktree`／`path_missing`／`bare_worktree`            |
| `invalid_scope`             | `scope_id`, `side`, `reason`                            | `unsupported`／`not_found`／`ambiguous`／`inventory_invalid` |
| `no_source`                 | `scope_id`, `source_path`                               | Missing scoped Workbench                                  |
| `unsafe_path`               | `scope_id`, `side`, `reason`                            | containment／symlink root／ancestry                         |
| `copy_failed`               | `scope_id`, `target_path`, `reason`, `mutation_started` | I/O／type collision／runtime race                           |

Raw file contents、entry list、source bytes は error object に含めません。Raw `OSError` text は host path や sensitive filename を含み得るため、public JSON には直接入れず、stable reason と generic message を優先します。

## 3.11 Compatibility／migration

* Database／metadata／workspace migration: なし。
* Existing Workbench content: 移動、rename、削除なし。
* Existing worktree commands: selector refactor後も text／JSON／error semantics を維持。
* Existing W1 discovery opacity: 維持。
* Package dependency: 追加なし。
* Owner、ACL、xattr、device fidelity: 保証外。
* Failure rollback: なし。再実行は利用者の明示操作。
* Reference docs／Epic PR: Issue #319 に relay。

---

# 4. `plan.md` 候補 — Strict／Spec-Locked TDD

Issue plan policy は、closure index、step-local delegation、具体テストケース、report destination、review／commit gate、S90、S99 を要求しています。

## 4.1 Spec-Locked Closure Index

| Closure ID | Spec link                  | Observable input／state                           | Locked expectation                                    | Guarded bug class                           | Required | Evidence level         | Owner       |
| ---------- | -------------------------- | ------------------------------------------------ | ----------------------------------------------------- | ------------------------------------------- | -------: | ---------------------- | ----------- |
| `C316-01`  | AC-316-001／DES-316-001     | CLI help／invalid option                          | Exactly one scope／target、no `--from`、root非対応          | Public contract drift                       |      yes | red-required           | S02／S06     |
| `C316-02`  | AC-316-002／DES-316-002     | ID／path／basename、invalid targets                 | Existing selector parity、pre-mutation rejection       | Resolver duplication／same-worktree mutation |      yes | characterization + red | S01／S03     |
| `C316-03`  | AC-316-003／DES-316-003     | Same ID、different slug                           | Independent source／target scope resolution            | Source path transposition                   |      yes | red-required           | S03         |
| `C316-04`  | AC-316-004／DES-316-004     | Missing source `.workbench`                      | `no_source`、target unchanged、no root fallback         | Accidental target creation                  |      yes | red-required           | S03         |
| `C316-05`  | AC-316-005／DES-316-005     | Mixed source／destination tree                    | Destination-only preserve、source leaf wins、idempotent | Wholesale replacement／stale target content  |      yes | red-required           | S04         |
| `C316-06`  | AC-316-006／DES-316-005     | Binary／archive／`.env`／nested `.git`              | No semantic filtering、byte-preserving ordinary copy   | Allowlist／secret filtering                  |      yes | red-required           | S04         |
| `C316-07`  | AC-316-007／DES-316-006     | Source symlink／destination symlink ancestry      | No dereference、no boundary escape                     | External read/write／symlink traversal       |      yes | red-required           | S05         |
| `C316-08`  | AC-316-008／DES-316-004〜006 | I/O／type collision fault                         | Failure not success、no rollback claim                 | Hidden partial failure                      |      yes | red-required           | S05         |
| `C316-09`  | AC-316-009／DES-316-007     | Text／JSON success and errors                     | Experimental markers、stable codes、no contents         | Authority overclaim／secret disclosure       |      yes | contract-first         | S02／S06     |
| `C316-10`  | AC-316-010／DES-316-008〜009 | Provider／dogfood／fresh consumer／manual worktrees | Parity、preservation、relay to #319、no PR               | Dogfood-only implementation／delivery drift  |      yes | manual + review        | S07／S90／S99 |

## 4.2 実装順序

```text
S00 Baseline / assurance readiness
  ↓
S01 Existing target selector extraction
  ↓
S02 Thin vertical happy path
  ↓
S03 Target / scope / no_source preflight
  ↓
S04 Recursive merge / content opacity
  ↓
S05 Symlink / containment / failure
  ↓
S06 Output contract / regression closure
  ↓
S07 Provider-dogfood / installed / manual scenario
  ↓
S90 Docs impact resolution
  ↓
S99 Final QA / code / spec / relay
```

## 4.3 S00 — Planning adoption、assurance、baseline

**Goal:** 現行 branch、親 trace、W1 completion、Issue dependency、baseline tests を固定する。

* Depends on: Issue #315 completion。
* Unblocks: S01。
* Delegated role: `repo-analyst` と strict planning specialist。
* Allowed paths: Issue #316 `requirement.md`、compose 後の `design.md`／`plan.md`、`report.md`、scope-local evidence artifact。
* Forbidden: Production code、dogfood projection、review-pass self-claim。
* Evidence:

  * Current parser／registry／ports／infra inventory。
  * Existing worktree target tests。
  * `requirement.md` concrete risk facts。
  * `assurance classify`／`compose` の実行結果。
* Concrete cases:

  * `tc-s00-001` characterization: Existing ID／path／basename selector tests が baseline pass。
  * `tc-s00-002` inspect: Provider／dogfood relevant runtime SHA／diff inventory。
* Gate:

  * Fresh requirement、design、plan `spec-reviewer`。
  * Production no-op。
  * Planning artifact commit candidateと clean-tree evidence。

## 4.4 S01 — Existing target selector の最小抽出

**Goal:** Workbench copy が target semantics を複製せず利用できる application-level boundary を作る。

* Depends on: S00。
* Unblocks: S02、S03。
* Delegated role: `dev-coder`。
* Candidate paths:

  * `application/worktree.py`
  * 必要なら `application/worktree_target.py`
  * `tests/cli_runtime/test_worktree.py`
  * selector-focused unit test。
* Forbidden:

  * Stable ID generation、classification、list/show/remove output semantics の変更。
  * Copy command の先行実装。
* TDD mode: characterization-first。
* Concrete cases:

  * `tc-s01-001`: ID／absolute path／basename の既存 result が抽出前後で一致。
  * `tc-s01-002`: Ambiguous basename と branch-only code が不変。
  * `tc-s01-003`: `SPEC_DOCK_WORKTREE_ROOT` 不在でも external linked target を解決可能。
* Verification:

  * Existing worktree focused suite。
  * `git diff --check`。
  * Ruff／mypy affected paths。
* Step gate:

  * Fresh `code-reviewer`、P0/P1 なし。
  * Report update → commit candidate `refactor(worktree): target selectorを共有化` → clean check。

## 4.5 S02 — Thin vertical happy path

**Goal:** Parser → command → application → filesystem → presentation を通す最小 end-to-end Green。

* Depends on: S01。
* Unblocks: S03〜S06。
* Delegated role: `dev-coder`。
* Candidate paths:

  * `cli/parser.py`
  * `cli/registry.py`
  * new `commands/workbench.py`
  * `application/contracts.py`
  * new `application/workbench_copy.py`
  * `application/ports.py`
  * `cli/bootstrap.py`
  * `infra/fs_cli.py`
  * `presentation/cli_text.py`
  * new `tests/cli_runtime/test_workbench.py`
* Minimal Green:

  * Current source／one target／one scope。
  * Existing source Workbench の single file。
  * Empty target Workbench。
  * Success text／JSON semantic markers。
* Concrete cases:

  * `tc-s02-001` Red: `workbench copy` が parser 上未認識。
  * `tc-s02-002` Green: Target scope に single source file が作られる。
  * `tc-s02-003`: JSON が `experimental=true`、`canonical=false`、`one_shot=true`、`sync=false` を持つ。
* Forbidden:

  * Root copy、error catalog 全拡張、generic filesystem framework。
* Step gate:

  * Focused CLI Green。
  * Fresh `code-reviewer`。
  * Report → commit candidate `feat(workbench): scoped copyの最小経路を追加` → clean check。

## 4.6 S03 — Target／scope／`no_source` preflight

**Goal:** Mutation 前に全 selector／scope failure を安定して閉じる。

* Depends on: S02。
* Unblocks: S04、S05。
* Delegated role: `dev-coder`。
* Primary paths: `application/workbench_copy.py`、contracts、application tests、CLI tests。
* Concrete cases:

  * `tc-s03-001`: Same ID、source slug `alpha`、target slug `renamed` でも target側 record pathを使用。
  * `tc-s03-002`: Source scope missing と target scope missing を `side` 付きで区別。
  * `tc-s03-003`: `no_source` で absent target Workbench を作らない。
  * `tc-s03-004`: `no_source` で existing target sentinel bytes を変えない。
  * `tc-s03-005`: Target path missing／bare／same-current は filesystem gateway 未呼出し。
  * `tc-s03-006`: Root/date/path/ADR scope input を拒否。
* Verification:

  * Fake-port application tests。
  * CLI target selector matrix。
  * No mutation call probes。
* Gate:

  * Error catalog diff review。
  * Fresh `code-reviewer`。
  * Commit candidate `feat(workbench): copy preflightをfail-closedにする`。

## 4.7 S04 — Recursive source-wins merge／content opacity

**Goal:** Merge semantics と ordinary opaque copy を adapter-level で閉じる。

* Depends on: S03。
* Unblocks: S05。
* Delegated role: `dev-coder`。
* Primary paths: `application/ports.py`、`infra/fs_cli.py`、new infra tests。
* Concrete cases:

  * `tc-s04-001`: Source-only追加、destination-only保持、same file overwrite。
  * `tc-s04-002`: Nested directory merge と repeat-run tree equality。
  * `tc-s04-003`: Binary、archive、`.env`、Python、config、nested `.git` の bytes一致。
  * `tc-s04-004`: Destination file／symlink leaf は source leaf で置換される。
  * `tc-s04-005`: Directory／non-directory mismatch は type collision failure。Destination subtree を削除しない。
  * `tc-s04-006`: Empty existing source Workbench は success、empty target root を作成。
* Forbidden:

  * Extension／MIME／secret／special-entry allowlist。
  * Copy manifest、hash database、per-entry counters。
* Verification:

  * Infra focused tests。
  * Application focused tests。
  * Repeat-run tree snapshot。
* Gate:

  * Fresh `code-reviewer`。
  * Commit candidate `feat(workbench): source-wins recursive mergeを実装`。

## 4.8 S05 — Symlink、containment、I/O failure

**Goal:** Copy operation が source／target scope 外を読書きしないことを固定する。

* Depends on: S04。
* Unblocks: S06。
* Delegated role: `dev-coder`。
* Concrete cases:

  * `tc-s05-001`: Source descendant symlink を `lstat`／`readlink` で同じ link textとして複製。
  * `tc-s05-002`: Source Workbench root symlink と target Workbench root symlink を pre-mutation reject。
  * `tc-s05-003`: Destination ancestry symlink が external directoryを指しても external sentinel不変。
  * `tc-s05-004`: Source directory／destination symlink collisionで link先へ recurseしない。
  * `tc-s05-005`: Copy primitive fault後は `copy_failed`、successなし、partial mutation warning。
  * `tc-s05-006`: Public errorにsource bytes／secret sentinelを含めない。
* Cross-platform:

  * Symlink unavailable host は OS integration case を明示 skip。
  * Fake `lstat`／adapter tests で guard decision は全 host で検証。
* Gate:

  * Fresh `code-reviewer`。
  * Security/path reviewer focusを明示。
  * Commit candidate `fix(workbench): symlink経由の境界外書込みを防止`。

## 4.9 S06 — Help／text／JSON／regression closure

**Goal:** Public contract と既存 runtime compatibility を閉じる。

* Depends on: S03〜S05。
* Unblocks: S07。
* Delegated role: `dev-coder`。
* Concrete cases:

  * `tc-s06-001`: Help に experimental／non-canonical／disposable／one-shot／no-sync。
  * `tc-s06-002`: `--from`、root/date/path route がない。
  * `tc-s06-003`: 全 error code の JSON shape と text shape。
  * `tc-s06-004`: Secret sentinel／file body／full entry listing が stdout／stderr／JSON にない。
  * `tc-s06-005`: Existing worktree create/list/show/remove regression。
  * `tc-s06-006`: Validate／sync／deps が copied Workbench 内容を discovery しない。
* Gate:

  * Public contract-focused `code-reviewer`。
  * Commitまたは、既存 S02〜S05で充足済みなら explicit approved-no-op。

## 4.10 S07 — Provider／dogfood／installed consumer／manual handoff

**Goal:** Provider implementation が consumer surface と実 worktree scenario で成立することを確認する。

* Depends on: S06。
* Unblocks: S90／S99。
* Delegated role: `dev-coder`。
* Allowed:

  * Provider runtime。
  * Normal update で生成される dogfood runtime。
  * Installer／parity tests。
* Forbidden:

  * Dogfood-only primary patch。
  * Final reference docs／Epic PR。
* Concrete cases:

  * `tc-s07-001`: Provider と dogfood の changed runtime files が byte-identical。
  * `tc-s07-002`: Fresh consumer init後に `workbench copy --help` が利用可能。
  * `tc-s07-003`: Existing consumer updateが root／scoped Workbench sentinelsを保持。
  * `tc-s07-004`: Manual two-linked-worktree scenario。
* Manual scenario:

  1. Source／target linked worktreeに同じ scope ID、異なる directory slugを用意。
  2. Sourceに `same.txt`、binary、`.env`、nested `.git`、symlinkを置く。
  3. Targetに異なる `same.txt` と `target-only.txt` を置く。
  4. Basename selectorで copyし、absolute path selectorで再実行。
  5. `target-only`保持、`same.txt` source-wins、binary hash一致、link object一致、target slug側に配置、再実行差分なしを確認。
  6. Same-currentと`no_source`をnegative確認。
* Gate:

  * Fresh `code-reviewer`。
  * Provider/dogfood parity evidence。
  * Commit candidate `test(workbench): installed handoffとparityを固定`。

Issue #315 でも provider-first、通常 update、dogfood parity、step reviewer／commit／clean check が用いられています。

## 4.11 S90 — Docs impact resolution

**Owner:** `doc-writer`。

候補判断:

* CLI help、success／failure text、JSON は Issue #316 で必須。
* Public reference docs、Epic-level Workbench guide、final migration／rollout説明は Issue #319 が所有。
* 既存 public guide が command inventory を列挙しており、新 command 欠落が誤解を生む場合だけ、experimental one-shot copy の最小記述を provider authority に追加する。
* Docsを変更する場合は normal update でdogfoodへ投影しbyte parityを確認。
* No-op の場合も inspected files、defer先 #319、non-blocking rationale を report に残す。

Gate:

* Fresh `spec-reviewer` docs/spec alignment。
* Commitまたは approved-no-op。
* Issue #317／#318／#319 の未実装機能を先行記述しない。

## 4.12 S99 — Final quality、delivery relay、Issue Finish

実行候補:

1. 全 focused Workbench copy tests。
2. Existing worktree／validate／sync／deps regression。
3. `uv run pytest tests/unit`。
4. `uv run pytest tests/cli_runtime`。
5. Integration追加要否を `qa-reviewer` が判断。必要なら manual scenario を automated integrationへ昇格。
6. `make lint`。現在の lint gate は Ruff check、Ruff format check、mypyです。
7. Provider／dogfood byte parity、fresh init／update preservation。
8. Manual two-worktree handoff。
9. `./spec-dock/scripts/spec-dock validate` と `sync`、tracked diff確認。
10. Fresh `qa-reviewer`、issue-wide `code-reviewer`、`spec-reviewer`。Blocking finding は修正して再review。
11. Report の closure、TDD、delegation、commit、docs、manual、review ledger を確定。
12. Current branchをpush。
13. **Per-Issue PRは作らない**。
14. `deferred_to: iss-00319`、dependency edge、pushed head、commit一覧、remaining risk、no merge-prepared claim を report に記録。
15. Active Issue #316 を確認後、`./spec-dock/scripts/spec-dock issue finish`。
16. Issue #319 の依存状態に #316 completion が反映されることを確認。

通常の `issue finish` は引数なしであり、GitHub issue closeとactive clearを行うだけで、commit／push／PR／test／reviewの完了を保証しません。そのため delivery evidence は先に閉じます。

Issue #319 は #316 を含む 315–318 全てに依存しています。

---

# 5. Concrete test matrix

新規 test file 候補:

* `tests/cli_runtime/test_workbench.py`
* `tests/unit/application/test_workbench_copy.py`
* `tests/unit/infra/test_runtime_fs_cli_workbench_copy.py`

| ID       | Layer        | Scenario                                                | Expected                                       |
| -------- | ------------ | ------------------------------------------------------- | ---------------------------------------------- |
| `CLI-01` | CLI          | `workbench copy --help`                                 | Required flagsと全semantic marker                |
| `CLI-02` | CLI          | `--from`、missing scope／target、extra positional          | Parser failure、mutationなし                      |
| `TGT-01` | App/CLI      | Stable ID／absolute path／basename                        | 同一 target                                      |
| `TGT-02` | App/CLI      | Duplicate basename                                      | `ambiguous_target`                             |
| `TGT-03` | App/CLI      | Missing／branch-only                                     | `target_not_found`／`unsupported_branch_target` |
| `TGT-04` | App          | Path missing／bare                                       | `target_not_eligible`                          |
| `TGT-05` | App          | Current targetを別 selector表現で指定                          | `same_worktree`                                |
| `TGT-06` | App/CLI      | Managed classification unavailableだがvalid linked target | Copy可能                                         |
| `SCP-01` | App          | Same ID、different slug                                  | Independent path resolution                    |
| `SCP-02` | App          | Source scope missing                                    | `invalid_scope side=source`                    |
| `SCP-03` | App          | Target scope missing                                    | `invalid_scope side=target`                    |
| `SCP-04` | App          | Root/date/path/ADR／invalid ID                           | `invalid_scope reason=unsupported`             |
| `SCP-05` | App          | Duplicate／invalid metadata inventory                    | Stable inventory-invalid failure               |
| `SRC-01` | App          | Source Workbench absent、target absent                   | `no_source`、target未作成                          |
| `SRC-02` | App          | Source Workbench absent、target existing                 | Sentinel bytes不変                               |
| `MRG-01` | Infra        | Source-only／dest-only／same file                         | Add／preserve／overwrite                         |
| `MRG-02` | Infra        | Nested merge、repeat                                     | Tree equality、idempotent                       |
| `MRG-03` | Infra        | Binary／archive／`.env`／nested `.git`                     | Bytes一致、filterなし                               |
| `MRG-04` | Infra        | Source leaf／destination symlink leaf                    | Symlinkを辿らずleaf置換                              |
| `MRG-05` | Infra        | Directory／leaf mismatch                                 | Type collision failure、subtree保持               |
| `MRG-06` | Infra        | Empty source directory                                  | Success、empty target root                      |
| `PTH-01` | Infra        | Source descendant symlink                               | Same link text、non-dereference                 |
| `PTH-02` | App/Infra    | Scope／Workbench root symlink                            | Pre-mutation `unsafe_path`                     |
| `PTH-03` | Infra        | Destination ancestry symlink→external                   | External sentinel不変                            |
| `PTH-04` | Infra/App    | Injected copy fault                                     | `copy_failed`、successなし                        |
| `OUT-01` | Presentation | Success text／JSON                                       | Scope／target／semantic fieldsのみ                 |
| `OUT-02` | Presentation | Failure with secret-named/file sentinel                 | Contents／full listingなし                        |
| `CMP-01` | Regression   | Existing worktree suite                                 | 公開selector/output不変                            |
| `CMP-02` | Regression   | Validate／sync／deps after copy                           | Workbench remains opaque                       |
| `CMP-03` | Distribution | Provider／dogfood／fresh update                           | Byte parity、sentinel preservation              |
| `MAN-01` | Manual       | Two linked worktrees、different slug、rerun               | Full handoff contract pass                     |

---

# 6. 仮定

1. `ports.repo_root` と `ports.specdock_dir` は runtime が解決した現在の repository／SpecDock pathであり、copy request の user input にはしない。
2. Target は SpecDock-managed worktree に限定せず、current repository の `git worktree list` record に存在する linked worktreeなら対象にできる。
3. Main worktreeは、current worktreeでない場合はtargetになり得る。
4. Detached／locked はそれだけでは copy blocker にしない。Bare、path missing、same-currentは blocker。
5. Emptyだが存在する source `.workbench` は成功対象。
6. Directory／non-directory type mismatch は destructive replacementせずcopy failureとする。Leaf同士はsource wins。
7. Idempotencyはsource／targetのconcurrent mutationがない条件。
8. Copy counters、manifest、partial entry list は不要。
9. `domain.ids.parse_id` を使い、Initiative／Epic／Issueのfull IDだけを受け付ける。
10. Issue #319 が final public docs、Epic-level distribution verification、PR deliveryを所有する。

---

# 7. 不確実性・後続検証対象

| 項目                    | 現時点の候補                                             | 後続検証                                                             |
| --------------------- | -------------------------------------------------- | ---------------------------------------------------------------- |
| Authorized profile    | Task contractに従い strict 候補                         | `assurance classify` が critical を要求した場合はcomposeし直す               |
| Resolver extraction   | Existing `application/worktree.py` helperの公開化が最小   | Neutral `worktree_target.py` が既存error couplingを減らすかcode review   |
| Cross-type collision  | Directory／leaf mismatchはfailure                    | Fresh spec reviewでsource-winsとdestination-only preservationの解釈確認 |
| Error field名          | `code`、`reason`、`side`、`mutation_started`          | Presentation contract review                                     |
| Output path           | Existing worktree identity + target Workbench path | Absolute／repo-relativeの最小公開範囲をreview                             |
| Symlink tests         | Fake-port tests + supported-host integration       | Windows等のskip policyをQA判断                                        |
| S90 docs              | Minimal updateまたはapproved-no-op、final docsは#319    | Existing reference docs inventory後に確定                            |
| Full integration test | Manual scenario必須                                  | Automated integration昇格はQA判断                                     |

これらは implementation detail／verification scope の不確実性であり、親 product contractを変更するものではありません。

---

# 8. 棄却候補

| Alternative                                                     | 棄却理由                                                           |
| --------------------------------------------------------------- | -------------------------------------------------------------- |
| `worktree copy` として追加                                           | Workbench capability と worktree lifecycle の責任が混ざる              |
| `--from`／source path option                                     | Current-source fixed contractを破る                               |
| Source scope directoryをtargetへ文字列転写                             | Branch間rename／slug差を壊す                                         |
| Root／date／relative path copy                                    | 親のroot exclusion違反                                             |
| Workbench用にtarget selectorを複製                                   | Existing stable ID／ambiguity semanticsからdriftする                |
| `SPEC_DOCK_WORKTREE_ROOT` managed classificationをeligibilityにする | Valid external linked worktreeを不当に除外                           |
| `shutil.copytree(...dirs_exist_ok=True...)` 単独                  | Destination symlink ancestryを安全に扱えない                           |
| Destination `.workbench` wholesale replacement                  | Destination-only preservation違反                                |
| Directory／leaf collisionでtarget subtreeを暗黙削除                    | Destination-only data lossとtype collision failure contractに反する |
| Extension／MIME／secret scan                                      | Opaque content contract違反                                      |
| Detailed copied／overwritten counters                            | Adapter complexityとpartial accountingを増やす                      |
| Tree-wide preflight／transaction／rollback                        | 明示的non-goal                                                    |
| Dogfood runtimeを直接primary実装                                     | Provider authority違反                                           |
| Issue #316でPR作成                                                 | Reviewed Epic delivery boundary違反                              |
| Success outputでcanonical／reviewedを示す                            | Workbench authority isolation違反                                |

---

# 9. Reviewer focus

## `spec-reviewer`

* E-RQ-006〜012、014、016以外の親境界を再定義していないか。
* Root、sync、copy-back、classifier、catalog、transactionが混入していないか。
* Directory／leaf type collisionの扱いがsource-winsとdestination-only preservationの両方に整合するか。
* Strictが適切か、critical escalationが必要か。
* S90／S99とIssue #319の責任分担が明確か。
* Evidence-only candidateをcanonical adoption済みとして扱っていないか。

## `code-reviewer`

* Target selector logicが複製されず、existing semanticsを維持しているか。
* Source／target scopeを本当に別 inventoryから解決しているか。
* Target SpecDock pathを`"spec-dock"` hard-codeで作っていないか。
* `no_source`以前にtarget directoryを作っていないか。
* `Path.exists()`だけでbroken symlinkを見落としていないか。
* Source traversalがsymlinkをdereferenceしていないか。
* Destination parent symlinkを`mkdir(exist_ok=True)`やcopy primitiveが辿っていないか。
* Raw `OSError`、filename、contentsがpublic outputへ漏れていないか。
* Copy failureをsuccess／warning-onlyにしていないか。
* No rollbackの境界が誤ってatomicity claimになっていないか。

## `qa-reviewer`

* AC／EC／closureとtest matrixが一対一以上で追跡可能か。
* Pre-mutation failureでfilesystem gateway未呼出しを確認しているか。
* Same-currentをselector表現違いでも検出しているか。
* Different slug independent resolutionがintegration levelで実証されているか。
* Source-only／destination-only／same-leaf／idempotencyが同じfixtureで確認できるか。
* Binary／`.env`／nested `.git`／symlinkを含むか。
* External sentinelで境界外writeを検出できるか。
* Provider／dogfood／installed consumer／manual scenarioが揃うか。
* Existing worktree、W1 opacity、validate／sync／deps regressionがあるか。

---

# 10. 証跡境界

本回答で行ったこと:

* GitHub connectorから現行ブランチの Issue、親 Epic、runtime、tests、planning policyを確認。
* Requirement／design／plan候補、error catalog、test matrix、strict micro-batchを作成。
* Repository上の既存 symbolに基づいて変更面を特定。

本回答で行っていないこと:

* Repository fileの変更。
* `assurance classify`／`compose`。
* Test、lint、manual worktree scenarioの実行。
* Reviewer invocationまたはpass。
* Commit、push、Issue Finish、PR。
* Canonical adoption、execution-ready、Issue completion、merge-readyの判定。

GitHub connectorの確認時点は **2026年7月13日** です。以後のbranch更新は未確認です。Issue #316 reportへ取り込む場合、この出力は delegated planning evidence として最初は `unreviewed`／adoption-ineligible に置き、current diff、fresh review、Evidence Adoption Ledgerを経て採否を記録するのが適切です。Report scaffold自体も、delegated evidenceをledgerなしでauthority化しない契約を持っています。
