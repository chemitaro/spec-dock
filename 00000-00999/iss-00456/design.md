---
種別: 設計書（Issue）
ID: "iss-00456"
タイトル: "Flatten Specs In Canonical Migration Script"
関連GitHub: ["#456"]
状態: "draft"
最終更新: "2026-10-29"
依存: ["requirement.md"]
親: ["epic-00424", "init-00423"]
---

# iss-00456 Flatten Specs In Canonical Migration Script — 設計

詳細: [Design Guide](../../../docs/authoring/design.md)

## 設計目標

- **D1 写しは1つの関数**：入れ子のツリーを平らなカタログに写す規則（パスの対応、捨てるもの、平らにできないもの、リンクの書き換え）を1か所に置き、`plan`、`build-canonical`（先端と履歴の各コミット）、`move-local`、`adopt-worktree` が同じ結果を使う。`adopt-worktree` の C が見つかるのは、同じ入力から同じツリーができるからである。
- **D2 写しは中身だけで決まる**：書き換えの結果は、写すツリー（仕様のツリーの中のファイル、`.meta.json`、`idmap.json`）だけで決まり、仕様のツリーの外のファイルの有無によらない。有無は、一覧（書き換えられないリンク、移行の前から切れているリンク）にだけ使う。履歴のコミットでは、外のツリーを読まずに写せる。
- **D3 戻すのは同じ書き換えの逆の対応**：`export-legacy` は、リンクの書き換えの部品を、逆のパスの対応で使う。
- **D4 足すだけ、本文に触れない**：`register` は本文を読まず、書かない。I-8 の統括の判断（足すだけ、消す前の一致の確かめ、`undo` は作ったものだけ）を守る。
- **D5 パッケージを読み込まない**：写した値は定数として持ち、テストでパッケージと比べる。
- **D6 本物のリポジトリに書かない**：読むだけのサブコマンド（`plan`、`verify`、`--apply` のない各サブコマンド）は、対象のリポジトリの `.git` にオブジェクトも参照も書かない。写した中身を書くのは、使い捨てのクローンの中だけである。

## Current / Target

| 部分 | Current（`95bbb7a1c`） | Target |
|---|---|---|
| 本文の印 | `register` が足し、`verify` が照らし、`undo` が外す。`analyze` が `SLUG_MARKER_CONFLICT` | なし。本文を読まない（GraphQL の `body` もない） |
| 作った Issue の見つけ直し | 種類のラベル、題名、印 | 種類のラベル、題名、作成者（`GET /user`）、作成の時刻 ≥ 予定の記録の時刻。2件以上で止まる |
| 作る Issue の本文 | 印の1行 | 送らない（`title` と `labels` だけ） |
| `build-canonical` | subtree split の先端に `rename_path`（ローカルの ID の名前の置き換え）を当てる。履歴は元のまま（入れ子、`.meta.json` あり） | 各コミットに平らにする写しを当てて作り直す。先端は厳しく（止まる）、履歴は平らにできないパスを落とす |
| `move-local` | `rename_path` で入れ子のまま移す | 平らにする写しのパスの対応で移し、リンクを書き換える |
| `adopt-worktree` | C は `M:spec-dock/initiatives` を `rename_path` したツリー（`.meta.json` あり）。X は入れ子 | C は M に写しを当てたツリー。X は作業の状態に写しを当てたツリー |
| `export-legacy` | カタログが入れ子のまま。slug は本文の印。`<ID>-` で始まる名前でディレクトリを探す | `<区切り>/<ID>/` を GitHub の親子で入れ子に戻し、slug は11章の規則。リンクを戻し、`rules.md` を置き直す。戻せないものは止まる |
| `verify` | 構造と印を照らし、canonical の `.meta.json` を探す | 構造を照らし、canonical の `.meta.json` と置き場の外れを探す |
| 写した値 | C1（種類、ラベル、slug の正規表現、印）、C2、C3、C5、C6、C7 | 印と slug の正規表現を消す。`CANONICAL_ID_RE`、区切り、従来の題名の規則と slug の作り方、従来の `rules.md` の先を足す |

## 責務・Interface

すべて `scripts/migrate-to-canonical/migrate.py` の中（モジュールの外には公開しない。テストは `tests/support/migration_repo.migrate_module()` で読む）。

### 写した値（テストでパッケージと比べる）

```python
# C1（domain/ids.py の CANONICAL_ID_RE）
CANONICAL_ID_RE = re.compile(r"^(init|epic|iss)-(?:[0-9]{5}|[1-9][0-9]{5,})$")
# C3（domain/canonical_layout.py、I-16）
BUCKET_SIZE = 1000
def scope_bucket(number: int) -> str:          # number < 1 は ValueError
    width = max(ID_WIDTH, len(str(number))); lower = number - number % BUCKET_SIZE
    return f"{lower:0{width}d}-{lower + BUCKET_SIZE - 1:0{width}d}"
def scope_relative(scope_id: str) -> str:      # "<区切り>/<ID>"。CANONICAL_ID_RE に合わなければ ValueError
# 従来モード（domain/ids.py の INPUT_TITLE_RE と derive_input_slug_from_title、application/scope_scaffold.py）
LEGACY_TITLE_RE = re.compile(r"^[A-Za-z0-9]+(?: [A-Za-z0-9]+)*$")
def legacy_slug(title: str) -> str             # 題名が規則に合えば小文字・空白をハイフン、合わなければ "untitled"
LEGACY_CHILD_RULES = {"initiative": ("epics", "spec-dock/docs/rules/initiative/epics.md"),
                      "epic": ("issues", "spec-dock/docs/rules/epic/issues.md")}
```

- 消す：`SLUG_RE`、`_LINE_BREAK`、`_MARKER_LINE`、`SLUG_MARKER_*`、`read_slug_marker`、`format_slug_marker`、`append_slug_marker`、`_remove_marker`、`rename_path`、`State.renames`（ID の置き換えは `idmap.json` から直接求める）。

### 平らにする写し

```python
NESTED_DIRECTORIES = ("epics", "issues")
FLATTEN_NESTED_FILE = "FLATTEN_NESTED_FILE"      # (a) epics/・issues/ の直下の、rules.md でも子の Scope でもないもの
FLATTEN_OUTSIDE_SCOPE = "FLATTEN_OUTSIDE_SCOPE"  # (b) どの Scope にも入らないファイル
FLATTEN_SCOPE_UNMAPPED = "FLATTEN_SCOPE_UNMAPPED"  # (c) ID を決められない Scope
FLATTEN_DUPLICATE_ID = "FLATTEN_DUPLICATE_ID"    # (d) 同じ ID になる2つ以上のディレクトリ

@dataclass(frozen=True)
class Layout:
    """1つの入れ子のツリー（パスは spec-dock/initiatives からの相対）の、Scope のディレクトリと新しい ID。"""
    places: Mapping[str, str]              # 写せる Scope のディレクトリ -> カタログの中の場所（scope_relative(ID)、または仮の場所）
    unmapped: Mapping[str, dict[str, Any]] # 写せない Scope のディレクトリ -> 異常（(c)、(d)）
    pending: Mapping[str, str]             # 仮の場所に写した Scope のディレクトリ -> ローカルの ID（plan だけ）

def nested_layout(metas: Mapping[str, bytes], idmap: Mapping[str, Mapping[str, Any]]) -> Layout:
    """metas は Scope のディレクトリの候補 -> .meta.json の中身。置き場の規則で Scope を決め、ID を求める。"""
```

- Scope のディレクトリ：`.meta.json` を持ち、直下にあるか、Scope のディレクトリの直下の `epics/` か `issues/` のすぐ下にあるディレクトリ（親が Scope でなければ Scope ではない）。
- 新しい ID：`.meta.json` の `type`、`id`、`github.issue_number` だけを読む（`parse_scopes` の schema 3 の必須の項目の検査はしない。履歴の古い `.meta.json` も読めるようにするため）。`id` がローカル（`<種類>-local-<数>`）なら `idmap.json` の `id`。そうでなければ、`type` が種類で、`id` が `CANONICAL_ID_RE` に合い、その番号が `github.issue_number`（1以上の整数）と同じとき、その `id`。どちらでもなければ (c)。2つ以上のディレクトリが同じ ID になれば、すべて (d)。
- `idmap` の代わりに、`plan` は `analysis.local_plan` から作った対応（結び付く番号のものは `{"id": …}`、新しく作る予定のものは `{"relative": "pending/<ローカルの ID>"}`）を渡す。`relative` を持つ Scope は、その仮の場所に写し、`Layout.pending` に入れる（異常にしない）。

```python
DROPPED = "dropped"   # 写さない（.meta.json、epics/rules.md、issues/rules.md）

class FlatMap:
    """入れ子 -> 平らのパスの対応（spec-dock/initiatives からの相対）。"""
    def __init__(self, layout: Layout) -> None
    def file(self, path: str) -> str | Literal["dropped"] | dict[str, Any]   # 写す先、捨てる、平らにできない（異常）
    def directory(self, path: str) -> str | None   # "" はツリーの根。epics/・issues/ は親の <区切り>/<ID>。決まらなければ None
    def dropped_rule(self, path: str) -> bool       # 捨てる epics/rules.md・issues/rules.md か

class NestMap:
    """平ら -> 入れ子のパスの対応（export-legacy）。nested は ID -> 入れ子のディレクトリ。"""
    def __init__(self, nested: Mapping[str, str]) -> None
    def file(self, path: str) -> str | dict[str, Any]
    def directory(self, path: str) -> str | None
```

- `FlatMap.file`：`.meta.json` は `dropped`。最も深い Scope のディレクトリ S（`Layout.places` と `Layout.unmapped` の両方から探す）からの残り R について、S が写せなければ S の異常、R が `epics/rules.md` か `issues/rules.md` なら `dropped`、R の最初が `epics` か `issues` なら (a)、S がなければ (b)、ほかは `<S の場所>/R`。
- `FlatMap.directory`：根は根。最も深い S からの残り R が空なら S の場所、R が `epics` か `issues` そのものなら同じ（親の Scope）、R が `epics/…` なら None、ほかは `<S の場所>/R`。

### リンクの書き換え

```python
@dataclass(frozen=True)
class Link:
    file: str            # 新しい位置（リポジトリからの相対）
    text: str            # 元の文字列
    rewritten: str | None  # 書き換えた文字列（書き換えなければ None）
    before: str          # 元の位置から解決した先（リポジトリからの相対）
    after: str | None    # 新しい位置から開く先（決まらなければ None）

def rewrite_links(payload: bytes, *, symlink: bool, old: str, new: str,
                  target: Callable[[str], str | None]) -> tuple[bytes, list[Link]]:
    """old/new はリポジトリからの相対のパス。target は元の先（リポジトリからの相対）を新しい先に写す。"""
```

- 対象：シンボリックリンク（中身が相対のパス）と、名前が `.md` の普通のファイルの `[…](先)`、`![…](先)`、`[…]: 先`、名前が `.html` か `.htm` の普通のファイルの `href="先"` と `src="先"`（`'` で囲んだものも。2026-10-29 の統括の判断）。Markdown の `<…>` で囲んだ先と、先の後の題（`"…"`）を扱う。URL（`<英字>:`）、`#` で始まるもの、`/` で始まるもの、Markdown の ``` と ~~~ の囲みと、` の個数によらないコードの範囲の中は除く（4つの空白のコードのブロックは見分けない）。UTF-8 で読めない文書は書き換えない（そのまま写す）。
- 元の先：`#`、`?` の前の部分を、元の位置のディレクトリから字面で正規化したもの（`posixpath.normpath`）。リポジトリの外（`..` で始まる）なら対象外。
- 新しい先（`target`）：元の先が仕様のツリーの中なら、捨てる `rules.md` はそのシンボリックリンクの先（仕様のツリーの外に出るまでたどる。たどれなければ None）、ほかは `FlatMap.file` か `FlatMap.directory`（ファイルとして写せなければディレクトリとして）。仕様のツリーの外なら元の先のまま。
- 書き換え：新しい位置から元の文字列で開く先が新しい先と同じなら、そのまま。違えば、新しい先への相対のパス（`posixpath.relpath`）に、元の末尾の `/` と `#`・`?` の後を付けた文字列にする。新しい先が None なら、そのまま（書き換えられないリンクの候補）。
- 同じ中身の書き換えの結果は、（blob、元のパス、新しいパス、各リンクの新しい先）で覚えて、履歴の各コミットで使い回す。
- 逆の書き換え（`export-legacy`）でも同じ部品を使うので、往復で字面が戻らないのは、正規化していない元の文字列、捨てた `rules.md` へのリンク、`epics/`・`issues/` のディレクトリへのリンクの3種類だけである（どれも同じ先を開く）。

```python
@dataclass
class LinkReport:
    rewritten: int
    unrewritable: list[dict[str, str]]   # 移行の前は開けたのに、写した後に開けない
    broken_before: list[dict[str, str]]  # 移行の前から開けない（数えない）

def link_report(links: Iterable[Link], before: PathSet, after: PathSet) -> LinkReport
```

- `PathSet` は、ファイルのパスと、その親のディレクトリの集まり（リポジトリからの相対）。`build-canonical` と `plan` の `before` は既定のブランチのコミットのツリー全体、`after` はその仕様のツリーの外と、写した後のファイル（`spec-dock/initiatives/<写した先>`）である。

### ツリーの写し

```python
@dataclass
class Flattened:
    entries: list[TreeEntry]          # 写した後（パスは spec-dock/initiatives からの相対）
    problems: list[dict[str, Any]]    # 平らにできないもの（strict なら止める）
    dropped: Counter[str]             # 履歴で落としたパスの数（異常のコードごと）
    links: list[Link]

class TreeFlattener:
    """1つのリポジトリ（作業用のクローン）の中で、ツリーの写しと blob の書き込みを、覚えながら行う。"""
    def __init__(self, repo: Path, idmap: Mapping[str, Mapping[str, Any]], scratch: Path | None) -> None
    def flatten(self, entries: Sequence[TreeEntry], *, strict: bool) -> Flattened
```

- `flatten` は、`.meta.json` の blob を読んで `nested_layout` を作り、各項目を `FlatMap.file` で写し、`.md`、`.html`、`.htm` とシンボリックリンクの中身を `rewrite_links` で書き換える。`scratch` があるとき（使い捨てのクローンの中）だけ、変わった中身を `git hash-object -w --no-filters --stdin-paths` でまとめて書き、項目の oid にする。`scratch` が None のとき（`plan`、本物のリポジトリを読むとき）は、何も書かず、変わった項目の oid は `git hash-object --stdin`（`-w` なし）と同じ値をメモリーの上で求める（`blob <長さ>\0` の SHA-1。リポジトリが SHA-256 なら None にして、比べ合わせに使わない）。`strict=False` のとき、平らにできない項目は落として `dropped` に数える。`strict=True` のときも同じ結果を作り、`problems` に入れる（呼ぶ側が止める）。

### サブコマンドの変更

- `plan`：今の出力に `data.flatten`（`problems`、`pending`、`links`（`rewritten`、`unrewritable`、`broken_before`））を足し、平らにできないものを異常（`FLATTEN_*`。`blocking` は偽で、`register` を止めない）に入れる。平らにできないものがあれば終了コード1。写しは `TreeFlattener(target.project, 置き換えの予定, scratch=None)` で行い、`.git` に書かない。
- `register`：`registration_plan` から `issue.marker` を消す。作成は `{"title", "labels"}` だけを送る。`_find_created(scope, since)` は R-456-03 の条件で探し、`list[Facts]` を返す。2件以上なら `Refused`（何も書いていない）か `Stopped`（書いた後）で、番号の一覧と次の1手を付けて止まる。`since` は、その Scope の、結果の記録のない作成の予定のうち最も古いものの時刻の5分前である（時計のずれの幅）。中断の後の再実行で、予定の記録があり結果の記録がないときは、作る前にまず探す（予定の記録がなければ探さずに作る。予定の記録がないのに作られた Issue はありえないため）。
- `Facts`：`body` を消し、`author`（login）と `created_at` を足す。GraphQL の項目は `author { login } createdAt`。今の利用者は `GET /user` の `login` を1回だけ読む。
- `verify`：印の照合を消し、`_canonical_layout(target, analysis)` を足す。origin の canonical（`ls-remote` であれば、使い捨てのクローン `Workspace.fetch_canonical` に取って読む。手元の追跡の参照は古いことがあるので使わない。origin になければ手元のカタログの作業ツリー。どちらもなければ今のとおり「確かめていない」）の、管理ファイルと `.runtime/` のほかの各パスが `<区切り>/<ID>/…`（区切りと ID が合い、`<ID>/` のすぐ下に `epics/`・`issues/` がない）であること、`.meta.json` の各 Scope の `scope_relative(新しい ID)` があることを確かめ、違いを不一致にする。
- `undo`：`issue.marker` の取り消しを消す（古い記録の `issue.marker` は、ほかの未知の操作と同じく飛ばす）。`_created_without_record` は `_find_created` と同じ条件（基準はその予定の時刻の5分前）と、今のとおり開いている Issue だけで探し、2件以上なら止まる。
- `build-canonical`：
  1. 先端の仕様のツリーを `TreeFlattener.flatten(strict=True)` で写し、`problems` があれば `Refused`（何も push しない）。リンクの一覧（`link_report`）を出す。
  2. 作業用のクローンで subtree split を行い、`git rev-list --reverse --topo-order --parents` の順に、各コミットのツリーを `flatten(strict=False)` で写し、元のコミットの生のヘッダーから `tree` と `parent` を差し替え、`gpgsig`、`gpgsig-sha256`、`mergetag` を外して、`git hash-object -t commit -w --stdin` で書く。親は作り直した親に置き換える。
  3. 作り直した先端のツリーが、手順1の写しと同じことを確かめる（違えば `Refused`）。その上に管理ファイルを足すコミットを作る（作成者と日時は今のとおり split の先端から）。
  4. `data.history` に、コミットの数、落としたコミットの数、落としたパスの数（コードごと）と例（コードごとに5つまで）を出す。`build.json` の項目は今のまま。
  - 手順1も、使い捨てのクローンの中で行う（本物の `.git` に書かない）。
- `move-local`：Scope の候補を、切り替え前のコミット（`legacy_commit`）の `.meta.json` と、そのチェックアウトのブランチの作業の記録 `adopt/<ブランチ>.json` の `metadata` だけから集めて `nested_layout` を作る（同じディレクトリで2つの出所の ID が違えば `Refused`）。各ファイルを `FlatMap.file` で写し、異常か `dropped` があれば、何も移さずに `Refused`。`.md`、`.html`、`.htm` とシンボリックリンクは書き換えた中身で写し先に作り、元を消す（ほかは今のとおり `rename`）。
- `adopt-worktree`：
  1. `flatten(M の仕様のツリー, strict=False)` のツリーを書き、それを持つ canonical のコミットを C とする（なければ `Refused`）。
  2. 作業の状態の項目（今のとおり）を `flatten(strict=True)` で写し、`problems` があれば `Refused`。写したツリーで X（親は C）を作り、C を merge base として3者マージする（今のとおり）。
  3. 消す前の一致：作業の状態の各ファイルについて、写した後の項目（パスと mode と oid）が、push した canonical の同じパスと同じか、分岐点の同じパスの元の項目と同じなら一致。`.meta.json` と捨てる `rules.md` は一致として消す。消す直前の「途中で変わっていないか」の確かめは、今のとおり元の oid で行う（両方を持つ）。
- `export-legacy`（今の `_scope_directories` の `<ID>-` の名前による探し方は消し、`nest_plan` に置き換える）：
  1. canonical の先端のツリー（管理ファイル、`.runtime/`、`.meta.json` を除く）と、GitHub の種類のラベルの付いた Issue を読む。
  2. `nest_plan(...)` で、各 Scope の入れ子のディレクトリを決め、R-456-08 の止まる条件を異常（`SCOPE_DIRECTORY_MISSING`、`SCOPE_ISSUE_MISSING`、`SCOPE_KIND_CHANGED`、`SCOPE_DIRECTORY_MISPLACED`、`KIND_LABEL_MULTIPLE`、`PARENT_MISSING`、`PARENT_CONFLICT`（外のリポジトリの親）、`KIND_RULE`、`CATALOG_PATH_OUTSIDE_SCOPE`）として集める。1つでもあれば `Refused`（`--apply` の有無によらない）。
  3. `NestMap` と `rewrite_links` で各ファイルを写し、各 Initiative と Epic に `LEGACY_CHILD_RULES` のシンボリックリンクを置き、`.meta.json` を今のとおり作る（slug は切り替え前の `.meta.json`、なければ `legacy_slug(題名)`）。`data.links` に、`plan` と同じ形の一覧を出す。

## data / failure

- 作業の記録（`undo.jsonl`、`idmap.json`、`build.json`、`adopt/`）の形は、足すだけ（`build.json` の `layout_ids`）。I-8 で作った記録は、そのまま読める（`issue.marker` の記録は `undo` が飛ばす）。
- 終了コードは今のとおり：0 問題なし、1 読むだけで問題を見つけた、2 書く前に止まった、3 書いた後に止まった。
- 失敗の扱い：

| 場面 | 結果 | 次の1手 |
|---|---|---|
| 先端に平らにできないもの（`plan`） | 終了コード1、`FLATTEN_*` の異常 | 従来モードの SpecDock のコマンドで直し（ファイルを Scope の中へ移す、仮置きのディレクトリを消す）、マージしてから `plan` |
| 同じ（`build-canonical`） | 終了コード2、何も push しない | 同じ |
| 書き換えられないリンク | 一覧と警告。終了コードは変えない | 一覧のリンクを直すか、切れることを受け入れる（予行演習で0件を確かめる） |
| 見つけ直しで2件以上 | 終了コード2（このときまでに書いていれば3）、番号の一覧 | 残す1つのほかから種類のラベルを外すか閉じて、同じ `register --apply` |
| `move-local` で位置を決められないファイル | 終了コード2、何も移さない | ファイルを Scope の中に移すか消して、もう一度 |
| `adopt-worktree` の作業の状態に平らにできないもの | 終了コード2、何も書かない | 同じ |
| C が見つからない | 終了コード2（今のとおり） | `build-canonical` を作り直した後なら、同じ `idmap.json` で行う |
| `export-legacy` の止まる条件 | 終了コード2、何も書かない、異常の一覧 | GitHub かカタログで直してから、もう一度 |

## 変更対象

- 変える：`scripts/migrate-to-canonical/migrate.py`、`scripts/migrate-to-canonical/README.md`。
- テスト：`tests/unit/infra/test_migration_contract_copies.py`（印と slug の比べ合わせを消し、ID、区切り、従来の題名と slug、`rules.md` の先を足す）、`tests/integration/migration/test_migrate_register.py`、`test_migrate_plan.py`、`test_migrate_canonical.py`、`test_migrate_checkouts.py`、新しい `tests/integration/migration/test_migrate_flatten.py`（写しとリンクの書き換えの単位の確かめと、リンクの多いリポジトリでの確かめ）、`tests/support/migration_repo.py`（入れ子の定数はそのまま。平らにした場所を求める助けを足す）、`tests/support/fake_github.py`（`FakeIssue` に `author` と `created_at` を足し、GraphQL と REST で返す。足すだけ）。
- 変えない：`src/spec_dock/` のすべて、Epic の文書、ほかの Issue の Scope、従来モードのテスト。

## 移行・互換性・rollback

- このスクリプトは、本物では I-10 と I-12 で初めて書く。それより前の記録はない（I-8 は本物に書いていない）ので、印の記録との互換は要らない。印を足した本物の Issue もない。
- 区切りは I-16 と同じ計算にする。I-16 がマージされる前は、写した計算を値の例で確かめ、マージの後に、パッケージの `scope_bucket` と比べるテストを足す。I-16 の公開の形が変わったら、写しをそれに合わせる。
- rollback：この PR を `git revert` すれば、I-8 の版に戻る。版3の spec-dock の運用には影響しない（スクリプトはまだ本物で使っていない）。

## testability

- 単位：`scope_bucket`、`scope_relative`、`nested_layout`、`FlatMap`、`NestMap`、`rewrite_links`、`link_report` は、純粋な関数として、git なしで確かめる（`test_migrate_flatten.py`）。
- 結合：一時のリポジトリ（`tests/support/migration_repo.build_legacy`）と偽の `gh`。リンクの多い仕様のツリーを作る助け（`linked_specs()`）を足し、`build-canonical` の後の canonical を、作業ツリーとして取り出し、すべてのシンボリックリンクと Markdown のリンクを、実際のファイルシステムで開いて確かめる（`os.path.exists` と、Markdown のリンクの字面の解決）。
- 履歴：最初のコミットに仮置きのディレクトリ（`epics/new-epic/requirement.md`）と、`idmap.json` にないローカルの Scope を置き、次のコミットで消した一時のリポジトリで、`build-canonical` のすべてのコミットのツリーが平らで `.meta.json` がないこと、`data.history` の数を確かめる。
- 見つけ直し：作成の予定だけを記録した `undo.jsonl` と、偽の `gh` の Issue（作成者、作成の時刻を変える）で、拾う、拾わない、2件で止まるを確かめる。
- 予行演習（自動のテストの外。報告書に書く）：
  1. 本物の spec-dock の `origin/main` を、内蔵のディスクの一時ディレクトリ（`/private/tmp`）に `--no-local` で写した bare の origin と、そのクローンを作る。`XDG_STATE_HOME` と作業の記録の置き場（`--state-dir`）を一時ディレクトリにする。
  2. `plan` は、本物の GitHub を読むだけで、本物の main のチェックアウトに対して行う（`--apply` を付けない。前後で参照とオブジェクトの数が変わらないことを確かめる）。
  3. `register` の本番がまだないので、以後は、本物の `.meta.json` から作った偽の GitHub（`tests/support/fake_github.FakeGithub`）を、移行のスクリプトにはその場で渡し（`main(runner=…)`）、`spec-dock` の CLI には `PATH` の先頭の偽の `gh`（`install_fake_gh` と同じ形）で見せる。偽の GitHub の上で `register --apply` を行い、`build-canonical --apply`、`cut --apply` を bare の origin に push し、切り替えのブランチを使い捨てのクローンの既定のブランチに早送りで取り込む（PR のマージの代わり）。
  4. `move-local --apply` の後、このブランチの wheel（一時の venv）の `canonical link --no-schedule` でカタログを開き、`canonical check` を通す。開いたチェックアウトの `spec-dock/initiatives` を通して、すべてのシンボリックリンクを実際のファイルシステムで、Markdown と HTML のリンクを字面で確かめ、移行の前に開けたもので開けないものを数える（0件が合格。0件でなければ止まって統括に聞く）。
  5. `export-legacy --apply` で戻し、戻したブランチで従来モードの `workspace validate` を通し、`.meta.json` と、往復で字面が戻らないリンクを数える。時間を測る。
  6. 一時ディレクトリを消す。
- 従来モードの回帰：`uv run pytest` の全体。`export-legacy` の結果は、このブランチのパッケージの従来モードの `workspace validate` で確かめる。`tests/support/fake_github.py` の足した項目（`createdAt`、`author`、REST の `created_at`、`user`）が、偽の GitHub を使うほかのテスト（canonical のスナップショット、同期、status など）の結果を変えないことを、全体のテストで確かめ、報告書に書く。
- 読むだけの確かめ：`plan` の前後で、対象のリポジトリの参照、作業ツリーの状態、`git count-objects -v` が変わらないことをテストで確かめる。

## risk

| リスク | 影響 | 対処 |
|---|---|---|
| リンクの書き換えが、リンクでない文字列を変える | 仕様の中身が変わる | コードの中を除き、元の位置から解決できる相対のパスだけを対象にし、新しい位置で同じ先なら変えない。先端のファイルの中身が、書き換えたリンクのほかは元と一致することをテストで確かめる |
| 履歴の作り直しが遅い（spec-dock は約2,000コミット） | 予行演習と本番が長引く | 書き換えの結果と blob の書き込みを覚えて使い回し、blob をまとめて書く。予行演習で時間を測り、報告書に書く |
| 履歴で落としたものが canonical の履歴にない | 古い履歴を canonical で追えない | 元のリポジトリの既定のブランチの履歴に残る（統括の判断）。落とした数と例を出力に示す |
| 往復で、正規化していない元のリンク（`./a/../b` など）の文字列が戻らない | 戻した文書の字面が変わる | 書き換えるのは、新しい位置で開けないリンクだけ。予行演習で、往復で字面が戻らないリンクを数えて報告書に書く |
| 見つけ直しの時刻の比べ方が、時計のずれで外れる | 作った Issue を拾えず、重複して作る | 予定の記録は作る直前に書き、GitHub の作成の時刻は秒の単位で「同じか後」で比べる。ずれで拾えない場合も、`undo` で外せる（作った記録があれば） |
| I-16 の公開の形がこの写しと違う | 区切りがずれ、CLI がカタログを読めない | I-16 の設計の値で写し、マージの後にパッケージと比べるテストで確かめる |
| 仕様のツリーの外から中を指すリンク（`docs/issue-plans/iss-00413-external-cli-state/artifacts/source-basis.md` など） | `cut` の後に切れる | この Issue の範囲の外（写すのは仕様のツリーの中だけ）。I-10 への引き渡しに書く |
