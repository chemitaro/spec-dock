# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a568e30-eb30-83e8-8b54-23f229b69ec4

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00319-installed-runtime-dogfood-parity-final-quality-and-mergeable-pr
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached prompt as the task brief. Inspect the attached source and tests, then provide the requested concrete repair design without a patch.

## Answer

# 結論

2026年7月14日に GitHub connector で `chemitaro/spec-dock` の PR #323 を確認し、指定ブランチの head `90a7adf3f5f1342162e7f952050e108793e32414` に固定して、provider 実装、dogfood ミラー、関連テストを検査しました。PR は GitHub 上では `mergeable=true` ですが、対象の二件はどちらも有効な **P1・merge-blocking** です。

修復は一つの大きな変更ではなく、次の **二つの順序付き repair unit** に分けるのが適切です。

1. **Workbench leaf publication repair**

   * regular-file leaf の destination create/write を、検証済み親 directory descriptor に対する `O_CREAT | O_EXCL | O_NOFOLLOW` create に置き換える。
2. **Artifact parent binding repair**

   * destination parent の directory descriptor を安全に取得し、temp staging、Linux/macOS publication、directory fsync、post-confirmation、temp cleanup の全工程で同じ descriptor を使い続ける。

両者の根本原因は同じですが、Workbench は source-wins overwrite と `mutation_started`、Artifact は no-overwrite publication、cleanup state、committed warning、Linux/macOS 分岐を持ちます。共通 abstraction を先に作るより、各モジュール内の小さい private helper として閉じる方が変更範囲と誤結合を抑えられます。

なお、head の CI と Provider CI は成功していますが、それは二件の race を感知するテストが存在しない状態での成功であり、P1 の反証にはなりません。

タスクの要求・制約は添付 brief に従っています。

---

# 1. Finding の妥当性と merge-blocking 判定

## 1.1 Workbench: destination symlink race

**判定: 有効、P1、merge-blocking。**

現在の regular-file branch は、親 directory と source identity を pathname で再確認した後、

```python
_assert_path_missing(destination)
mutation_started[0] = True
shutil.copy2(source, destination, follow_symlinks=False)
```

を実行しています。missing 判定と `copy2` が destination を open する間に symlink を挿入できるため、`copy2` は symlink 自体ではなく、その target を open・truncate できます。

`follow_symlinks=False` が制御するのは **source が symlink の場合の挙動**であり、destination の no-follow create を保証する引数ではありません。`copy2` は destination pathname を通常のファイルコピー先として扱い、既存 destination を置換します。([Python documentation][1])

provider と dogfood の `fs_cli.py` は同一 blob SHA であり、dogfood にも同じ欠陥があります。

### 既存テストの不足

現在のテストは、symlink を `_assert_path_missing` の**実行前**に挿入し、その assertion が拒否することを確認しています。判定が成功した**後**、実際の create/open の直前に挿入するケースは再現していません。

したがって、このテスト群は race window を閉じているのではなく、その手前の検査が機能することだけを証明しています。

---

## 1.2 Artifact: destination parent symlink race

**判定: 有効、P1、merge-blocking。**

現在は destination parent の ancestry を pathname で検査した後、別の pathname lookup として次を実行しています。

```python
tempfile.mkstemp(
    prefix=".spec-dock-import-",
    suffix=".tmp",
    dir=destination.parent,
)
```

その後も、

* Linux publication で `os.open(destination.parent, ...)`
* macOS helper 内で `os.open(destination.parent, ...)`
* directory fsync で parent path を再度 open
* post-confirmation で destination path を open
* cleanup で `temp_path.lstat()` / `temp_path.unlink()`

と、同じ親 pathname を繰り返し再解決しています。

`tempfile.mkstemp` 自体の exclusive creation は安全ですが、Python 3.10 の API には `dir_fd` 引数がありません。`dir=destination.parent` は pathname を再解決するため、親が symlink に差し替えられれば、temp file の作成時点ですでに repository 外へ出られます。([Python documentation][2])

provider と dogfood の publisher も同一 blob SHA です。

既存 Artifact テストは、検証済み temp descriptor と temp pathname の差し替え耐性を確認していますが、destination parent 自体の差し替えは確認していません。

---

# 2. Root-cause grouping と repair-unit の分割

## 共通 root cause

両方とも次の構造です。

```text
pathname による検査
    ↓
race window
    ↓
同じ pathname の再解決を伴う mutation
```

つまり、問題は「検査回数が足りない」ことではなく、**検査した filesystem object と、実際に mutation する filesystem object が descriptor で結び付いていないこと**です。

正しい security boundary は次です。

```text
pathname を安全に open
    ↓
fstat で期待 identity を確認
    ↓
その descriptor を保持
    ↓
basename + dir_fd だけで全 mutation
```

チェック後の open が危険であることは Python の公式ドキュメントでも注意されており、対応 API では `dir_fd`、`follow_symlinks=False`、descriptor operation を使う必要があります。([Python documentation][3])

## 二つの ordered unit を推奨する理由

### Unit A — Workbench leaf repair

対象:

* `fs_cli.py`
* regular-file source leaf
* destination leaf unlink/create/write
* `mutation_started`
* Workbench regression tests
* provider/dogfood mirror

この unit は小さく、Linux/macOS 共通の Python `os.*` API だけで閉じます。

### Unit B — Artifact parent lifecycle repair

対象:

* `binary_artifact_publisher.py`
* directory descriptor acquisition
* temp creation
* Linux hard-link publication
* macOS `fclonefileat`
* fsync
* confirmation
* cleanup
* Artifact regression tests
* provider/dogfood mirror

こちらは platform-specific publication と committed/cleanup contract を含むため、Workbench と同じ commit に混ぜるとレビュー単位が大きくなります。

## 推奨順序

**Workbench → Artifact** とします。

Workbench でまず、

* verified parent fd
* exclusive leaf create
* descriptor copy
* deterministic race injection

という最小パターンを確立します。その後、Artifact のより長い descriptor lifecycle を独立してレビューします。

ただし、片方だけを修正した状態は merge-ready ではありません。二 unit の完了後にのみ full gate と PR review を再実行します。

---

# 3. Workbench ordinary-file copy の最小安全設計

## 3.1 Security boundary

regular-file leaf の処理開始時に destination parent を一度だけ open し、既存の `destination_parent_identity` と `fstat` 結果を比較します。

```python
flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
if hasattr(os, "O_CLOEXEC"):
    flags |= os.O_CLOEXEC

destination_parent_fd = os.open(destination_parent, flags)

status = os.fstat(destination_parent_fd)
if (status.st_dev, status.st_ino, status.st_mode) != destination_parent_identity:
    raise RuntimeError("workbench copy directory identity changed")
```

open 前に親が差し替えられていれば identity mismatch になります。open 後に親 pathname が差し替えられても descriptor は元の directory object に結び付いているため、その後の mutation は外部 symlink target にリダイレクトされません。

Python 3.10 では `os.open(..., dir_fd=...)`、`os.stat(..., dir_fd=..., follow_symlinks=False)`、`os.unlink(..., dir_fd=...)` が Unix で利用できます。実行時には `os.supports_dir_fd` などを確認し、必要な primitive がなければ安全でない pathname fallback を使わず fail closed にします。([Python documentation][3])

`O_DIRECTORY` または `O_NOFOLLOW` が利用不能な場合も、対象 platform を安全に実装できないため fallback しません。これらの flag は platform の C library が提供する場合にのみ Python に存在します。([Python documentation][3])

## 3.2 Source descriptor

source regular file も、実際に bytes を読む前に descriptor として固定します。

```python
source_fd = os.open(
    source,
    os.O_RDONLY | os.O_NOFOLLOW | optional_cloexec,
)
source_status = os.fstat(source_fd)
```

確認事項:

* `stat.S_ISREG(source_status.st_mode)`
* `(st_dev, st_ino, st_mode)` が既存の `source_identity` と一致

これにより、identity check 後に source pathname が別ファイルや symlink に差し替えられても、検証した inode 以外を読みません。

source descriptor は destination の unlink/create より前に取得するのがよいです。source が不正なら destination を変更せずに失敗できます。

## 3.3 Existing destination の削除

既存 destination が regular file または symlink の場合、親 descriptor に対して相対操作します。

```python
actual = os.stat(
    destination.name,
    dir_fd=destination_parent_fd,
    follow_symlinks=False,
)
```

既存 identity と一致することを確認してから、

```python
os.unlink(destination.name, dir_fd=destination_parent_fd)
mutation_started[0] = True
```

とします。

`unlink` は symlink target を辿りません。検査直後に leaf が差し替えられても、外部 target を削除・上書きすることはありません。別 process が directory を挿入すれば `unlink` が失敗し、fail closed になります。

## 3.4 Exclusive/no-follow creation

最終 destination file は次の形で直接作成します。

```python
destination_fd = os.open(
    destination.name,
    os.O_WRONLY
    | os.O_CREAT
    | os.O_EXCL
    | os.O_NOFOLLOW
    | optional_cloexec,
    0o600,
    dir_fd=destination_parent_fd,
)
mutation_started[0] = True
```

重要なのは次の組合せです。

* `O_CREAT | O_EXCL`

  * leaf が file、symlink、その他何であっても既に存在すれば失敗。
* `O_NOFOLLOW`

  * symlink leaf を open しない。
* `dir_fd`

  * destination parent pathname を mutation 時に再解決しない。
* 初期 mode `0o600`

  * copy 途中の不完全な内容を広い permission で公開しない。

`_assert_path_missing()` は事前診断として残しても構いませんが、security boundary として扱ってはいけません。authoritative な missing/no-replace 判定は `os.open(... O_EXCL ...)` の成功または `EEXIST` です。

## 3.5 Bytes copy

`shutil.copy2` は使わず、descriptor 間で copy します。

```python
while True:
    chunk = os.read(source_fd, chunk_size)
    if not chunk:
        break
    _write_all(destination_fd, chunk)
```

これにより、bytes copy 中に source/destination pathname を再解決しません。

`shutil.copyfileobj` を fd wrapper 経由で使うことも可能ですが、既に Artifact publisher に `_write_all` 相当の pattern があるため、短い `os.read` / `os.write` loop の方が failure boundary を明確にできます。

## 3.6 Metadata

`shutil.copy2` は `copystat` を通じて mode、timestamps、および一部 platform では extended attributes を pathname ベースでコピーします。安全な fd copy の後に `shutil.copystat(source, destination)` を呼ぶと、そこで destination pathname race が再導入されます。([Python documentation][1])

最小設計では次を descriptor に対して行います。

```python
os.fchmod(destination_fd, stat.S_IMODE(source_status.st_mode))
os.utime(
    destination_fd,
    ns=(source_status.st_atime_ns, source_status.st_mtime_ns),
)
```

`os.fchmod` と fd を受ける `os.utime` は Python 3.10 の Unix API で利用できます。([Python documentation][3])

### Extended attributes

ここは human decision が必要です。

* **推奨最小契約:** bytes、regular-file type、permission mode、mtime を維持する。
* xattrs、BSD flags、ACL の完全な `copy2` parity は今回の P1 修復から外す。
* xattrs parity が製品契約なら、fd を受ける API が platform ごとに利用可能かを確認し、別の明示テストを追加する。
* pathname `copystat` fallback は採用しない。

## 3.7 Error と cleanup

| 状況                                                              | `mutation_started` | 結果                                      |
| --------------------------------------------------------------- | -----------------: | --------------------------------------- |
| destination parent fd の open/identity failure                   |            `False` | `WorkbenchFilesystemError`              |
| source fd の open/identity failure                               |            `False` | 同上                                      |
| missing destination に race leaf が挿入され、exclusive open が `EEXIST` |            `False` | 外部 target 不変                            |
| existing destination を unlink 後、race leaf により create が失敗        |             `True` | 外部 target 不変                            |
| destination fd 作成後の read/write/metadata failure                 |             `True` | partial file を残し、rollback しない           |
| fd close                                                        |          `finally` | source、destination、parent の全 fd を close |

現在も Workbench は mid-copy rollback を行わないため、destination fd 作成後に partial file が残る挙動は既存 semantics と整合します。

## 3.8 Symlink source branch

この P1 の直接対象は ordinary file ですが、同じ destination parent fd を leaf branch 全体で使えるなら、symlink object 作成も次に寄せるのが小さい追加 hardening です。

```python
os.symlink(
    link_target,
    destination.name,
    dir_fd=destination_parent_fd,
)
```

これにより、symlink source の意味は変えず、destination parent の pathname 再解決を避けられます。

directory creation と recursive directory traversal まで fd 化するのは、今回の最小 leaf repair より広い変更です。今回の reviewer acceptance が「ordinary-file P1 のみ」なら別 unit に広げず、残存 pathname operation として明示的に記録します。

---

# 4. Artifact staging/publication の最小安全設計

## 4.1 Descriptor lifecycle

publisher 内で次の state を保持します。

```python
destination_directory_fd: int | None
destination_directory_identity: tuple[int, int, int] | None
temp_fd: int | None
temp_name: str | None
```

`temp_path: Path` は内部 state から除きます。temp file は `directory_fd + basename` でのみ参照します。

descriptor は次の全工程が終わるまで保持します。

```text
secure directory open
→ temp create
→ source copy
→ file fsync
→ staged hash
→ source revalidation
→ formal publication
→ directory fsync
→ destination confirmation
→ temp cleanup
→ directory fd close
```

## 4.2 Destination parent の secure open

Artifact では repository root から destination parent までを component-by-component に open する private helper を推奨します。

概念形は次です。

```python
root_fd = os.open(
    repo_root,
    O_RDONLY | O_DIRECTORY | O_NOFOLLOW | optional_cloexec,
)

current_fd = root_fd
for component in destination.parent.relative_to(repo_root).parts:
    next_fd = os.open(
        component,
        O_RDONLY | O_DIRECTORY | O_NOFOLLOW | optional_cloexec,
        dir_fd=current_fd,
    )
    status = os.fstat(next_fd)
    if not stat.S_ISDIR(status.st_mode):
        fail
    close(current_fd)
    current_fd = next_fd

return current_fd
```

追加条件:

* lexical containment は従来どおり先に確認する。
* `repo_root` は `lstat` identity と open 後の `fstat` identity を比較する。
* component は `.`、`..`、separator を含まない単一 name とする。
* 各 open で `O_NOFOLLOW | O_DIRECTORY` を必須にする。
* 必要な `dir_fd` support がなければ `publication_unsupported` で fail closed にする。
* absolute parent path を後から reopen しない。

この helper は `_guard_directory_ancestry` の security role を置き換えます。既存 guard を early validation として残してもよいですが、mutation authority はこの directory fd です。

## 4.3 `temp_create` hook の配置

既存 deterministic hook を維持するため、順序を次にします。

```text
source fd open
→ inject("temp_create")
→ secure destination directory open
→ exclusive temp create at directory fd
```

したがって、`temp_create` hook が `artifacts/` を rename し、同じ path に external directory への symlink を置いた場合、続く `O_NOFOLLOW` component open が失敗し、temp file は一つも作成されません。

hook が `OSError` を投げた既存 fault test は、従来どおり `temp_create_failed / not_created` にします。hook が filesystem swap だけを行い、secure parent open が拒否した場合は `destination_ineligible / not_created` とします。

## 4.4 Temp file creation

`tempfile.mkstemp` には `dir_fd` がないため、basename を生成して `os.open` します。

```python
for _attempt in range(MAX_TEMP_NAME_ATTEMPTS):
    temp_name = f".spec-dock-import-{secrets.token_hex(16)}.tmp"
    try:
        temp_fd = os.open(
            temp_name,
            os.O_RDWR
            | os.O_CREAT
            | os.O_EXCL
            | os.O_NOFOLLOW
            | optional_cloexec,
            0o600,
            dir_fd=destination_directory_fd,
        )
    except FileExistsError:
        continue
    break
else:
    raise _PublishFailure("temp_create_failed")
```

性質:

* `O_RDWR`: staged hash で同じ fd を read するため。
* `O_EXCL`: name collision 時に上書きしない。
* `O_NOFOLLOW`: temp basename が symlink なら拒否。
* `0o600`: 現行 `mkstemp` と同等の private staging permission。
* 外部 dependency は不要。

## 4.5 Publication 前の parent identity revalidation

`before_publication` hook は publication helper の中ではなく、caller 側で次の順にします。

```text
inject("before_publication")
→ visible destination parent を secure re-walk
→ held directory fd の identity と比較
→ descriptor-bound publication
```

parent が staging 後に差し替えられていた場合:

* formal destination は作らない。
* `_PublishFailure("destination_ineligible")`
* temp は held directory fd を使って cleanup。
* cleanup 成功なら `cleanup_state="removed"`。

この revalidation は mutation boundary ではありません。security は held fd が担い、revalidation は「現在の repo-relative path が引き続き同じ directory を指す」という結果 semantics を守るために行います。

## 4.6 Linux publication

signature を次に変更します。

```python
_publish_no_replace(
    temp_fd: int,
    destination_directory_fd: int,
    destination_name: str,
)
```

Linux branch は現在の descriptor publication を維持し、parent reopen だけを除去します。

```python
os.link(
    f"/proc/self/fd/{temp_fd}",
    destination_name,
    dst_dir_fd=destination_directory_fd,
    follow_symlinks=True,
)
```

Python 3.10 の `os.link` は `dst_dir_fd` と `follow_symlinks` をサポートします。([Python documentation][3])

意味:

* source は検証済み staged descriptor の inode。
* destination は held directory fd 内の単一 basename。
* `FileExistsError` は `destination_exists`。
* `/proc/self/fd` が利用不能、cross-device、primitive unsupported は現行どおり `publication_unsupported`。
* `os.replace` や pathname temp name からの hard link は使わない。

## 4.7 macOS publication

現在の helper は内部で `destination.parent` を pathname open しています。これを廃止し、caller が保持する directory fd を直接受け取ります。

shape:

```python
_clone_macos_descriptor(
    source_fd: int,
    destination_directory_fd: int,
    destination_name: str,
)
```

呼び出す C API shape は維持します。

```python
fclonefileat(
    source_fd,
    destination_directory_fd,
    os.fsencode(destination_name),
    0,
)
```

変更点は、helper 内で directory を open/close しないことです。directory fd の ownership は `publish()` に残します。

errno mapping は現行を維持します。

* `EEXIST` → `destination_exists`
* unsupported errno → `publication_unsupported`
* その他 → `publication_failed`

## 4.8 Directory fsync

現在の `_fsync_directory(destination.parent)` は parent pathname を reopen します。

次に変更します。

```python
def _fsync_directory(directory_fd: int) -> bool:
    try:
        inject("directory_fsync")
        os.fsync(directory_fd)
    except OSError:
        return False
    return True
```

失敗時は既存どおり `directory_fsync_failed` warning です。

## 4.9 Post-publication confirmation

destination は held directory fd に対して開きます。

```python
descriptor = os.open(
    destination_name,
    O_RDONLY | O_NOFOLLOW | optional_cloexec,
    dir_fd=destination_directory_fd,
)
```

その descriptor を `_hash_descriptor` に渡します。

これにより、post-confirmation 中にも `destination.parent` を再解決しません。

別 process が formal destination leaf 自体を publication 後に置換した場合は、現在と同じく、

* read failure → `destination_read_failed`
* hash difference → `destination_mismatch`

という committed warning contract を維持できます。既存 warning と committed result の構造は contracts に定義されています。

## 4.10 Temp cleanup

cleanup も directory fd 相対で行います。

```python
path_status = os.stat(
    temp_name,
    dir_fd=destination_directory_fd,
    follow_symlinks=False,
)
descriptor_status = os.fstat(temp_fd)
```

identity が一致した場合だけ、

```python
os.unlink(temp_name, dir_fd=destination_directory_fd)
```

を実行します。

結果:

* temp name が既にない → `removed`
* temp name が別 inode に置換されている → `retained`
* unlink failure → `retained`
* parent pathname が rename/symlink swap されていても、元の verified directory 内の temp を正しく cleanup

現行の staged-path replacement test が期待する `temp_cleanup_retained` semantics を維持できます。

## 4.11 Post-publication parent change

publication 直前の revalidation と実際の syscall の間に directory pathname を rename する race 自体を、portable Python で完全に禁止することはできません。ただし mutation は held fd 内に限定されるため、差し替えた external symlink targetには書きません。

publication 後に visible parent identity を secure re-walk して確認し、異なっていれば次のどちらかが必要です。

### 最小変更案

既存 `destination_read_failed` warning を用い、

* `committed=True`
* destination hash/count は staged 値
* public result は warning 付き

とする。

### より正確な案

`destination_parent_changed` の committed warning を新設する。

後者の方が診断上は正確ですが、public JSON warning enum の追加になります。今回の「public behavior を可能な限り維持する」という制約から、**本 repair unit では前者を推奨**し、warning taxonomy の精緻化は human decision とします。

---

# 5. Deterministic regression tests

## 5.1 Workbench tests

### Test W-RACE-1: missing leaf、check 後の symlink 挿入

推奨名:

```text
test_copy_workbench_regular_file_rejects_symlink_inserted_before_exclusive_create
```

構成:

1. source regular file に `b"source bytes"`。
2. destination leaf は missing。
3. external file に `b"external sentinel"`。
4. exclusive destination helper を monkeypatch。
5. helper 内で real `os.open` の直前に `destination/leaf -> external` を作る。
6. real exclusive/no-follow helper を呼ぶ。

assert:

* `WorkbenchFilesystemError`
* `mutation_started is False`
* destination leaf は挿入された symlink のまま
* external は `b"external sentinel"` のまま
* source bytes が external に現れない

### Test W-RACE-2: unlink 後の symlink 挿入

推奨名:

```text
test_copy_workbench_regular_file_rejects_symlink_inserted_after_destination_unlink
```

構成:

* destination に既存 regular file。
* unlink 成功後、exclusive create の直前に external への symlink を挿入。

assert:

* `mutation_started is True`
* external sentinel 不変
* symlink target に source bytes が書かれていない

### Test W-RACE-3: destination parent の差し替え

推奨名:

```text
test_copy_workbench_regular_file_uses_verified_destination_parent_descriptor
```

構成:

* parent fd の取得後、actual leaf create の直前に visible destination directory を rename。
* 元 path に external directory への symlink を作成。
* operation は held dirfd に対して実行。

assert:

* external sentinel 不変
* external に source leaf が作られない
* post-operation identity check を採用した場合は `mutation_started=True` で失敗

### Test W-META-1: descriptor metadata

* binary bytes
* source mode、たとえば `0o640`
* fixed mtime

を設定し、destination の bytes、mode、mtime が一致することを確認します。

### 既存 fault tests の更新

現在、mid-copy fault と unlink 後の copy failure は `shutil.copy2` を monkeypatch しています。新実装後は dead test になるため、新しい `_copy_regular_file_descriptors` または `_write_all` boundary に差し替えます。

維持すべき assertions:

* first file はコピー済み
* second file の fault で `mutation_started=True`
* raw body/error detail は public exception に出ない
* unlink 後に copy が失敗した場合の state が正確

---

## 5.2 Artifact tests

### Test A-RACE-1: `temp_create` 時の parent symlink swap

推奨名:

```text
test_publish_rejects_destination_parent_symlink_swap_before_staging
```

既存 `fault_injector("temp_create")` を利用します。

hook:

1. `artifacts/` を `displaced-artifacts/` へ rename。
2. 元の `artifacts/` に external directory への symlink を作成。
3. exception は投げず return。

assert:

* `BinaryArtifactPublishError.code == "destination_ineligible"`
* `cleanup_state == "not_created"`
* `committed is False`
* external sentinel 不変
* external に formal destination がない
* external に `.spec-dock-import-*` がない
* displaced original directory に temp がない

### Test A-RACE-2: publication 前の parent symlink swap

推奨名:

```text
test_publish_rejects_destination_parent_swap_after_staging_before_publication
```

`before_publication` hook で同じ swap を行います。

assert:

* `code == "destination_ineligible"`
* `cleanup_state == "removed"`
* external sentinel 不変
* external に formal destination なし
* displaced original directory の temp が cleanup 済み
* source bytes 不変

### Test A-RACE-3: syscall 直前の parent swap

Linux では `os.link` wrapper 内で、real `os.link` の直前に parent を swap します。

assert:

* `dst_dir_fd` は secure open で取得した同じ fd
* external に write なし
* formal link は held directory object に作られる
* post-publication visible-parent check により committed warning が付く

これは「revalidation 直後に swap」という残る最小 race window に対して、security が pathname identity ではなく descriptor binding に依存していることを証明します。

### Test A-LINUX-1: held fd の使用

`os.link` を recording wrapper にし、

```python
destination_path == destination.name
dst_dir_fd == expected_directory_fd
follow_symlinks is True
```

を確認します。

`os.open(destination.parent, ...)` が publication phase で呼ばれていないことも記録できます。

### Test A-MACOS-1: held fd の使用

`sys.platform = "darwin"` とし、C wrapper boundary を monkeypatch して、

```text
source_fd
held destination_directory_fd
destination.name bytes
flags=0
```

が渡ることを確認します。

これは API shape の unit test であり、実 syscall の検証ではありません。

### Test A-CLEANUP-1: displaced parent 内の cleanup

parent rename 後も temp cleanup が held fd で行われることを確認します。

* temp original inode → unlink 成功 → `removed`
* temp name replacement → identity mismatch → `retained`
* external directory 内の同名ファイルは一切触らない

### 既存テストの更新

次の monkeypatch signature を更新します。

```python
_publish_no_replace(temp_fd, directory_fd, destination_name)
```

対象:

* destination mutation warning test
* publication unsupported test
* staged pathname replacement test

post-confirmation failure testは、absolute path に一致する `os.open` monkeypatch ではなく、既存 `fault_injector("post_confirmation")` で失敗させます。新実装では open 対象が `destination.name + dir_fd` になるためです。

---

# 6. Quality gates

Issue 319 の既存計画でも、focused → unit → CLI runtime → integration → full → static → Linux CI の順序が authority とされています。

## Repair Unit A 後

```bash
uv run pytest tests/unit/infra/test_runtime_fs_cli_workbench.py
uv run pytest tests/unit/application/test_workbench.py
uv run pytest tests/cli_runtime/test_workbench.py
make lint
git diff --check
```

provider/dogfood:

```bash
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py \
  spec-dock/scripts/spec_dock_runtime/infra/fs_cli.py
```

加えて両 file の SHA-256 一致を記録します。

## Repair Unit B 後

```bash
uv run pytest tests/unit/infra/test_binary_artifact_publisher.py
uv run pytest tests/unit/application/test_binary_artifact_import_ports.py
uv run pytest tests/unit/commands/test_artifact_import_chatgpt_output.py
uv run pytest \
  tests/cli_runtime/test_artifact_import_chatgpt_output.py \
  tests/cli_runtime/test_artifact_import_s04.py
make lint
git diff --check
```

provider/dogfood:

```bash
cmp -s \
  src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py \
  spec-dock/scripts/spec_dock_runtime/infra/binary_artifact_publisher.py
```

Issue 319 の計画も provider authority を先に更新し、dogfood を exact projection として同期し、dogfood-only edit を禁止しています。

## 二 unit 完了後の full gates

```bash
uv run pytest tests/unit
uv run pytest tests/cli_runtime
uv run pytest tests/integration
uv run pytest
make lint
uv run ruff check .
uv run ruff format --check .
git diff --check
```

その後:

* fresh candidate wheel
* installed runtime smoke
* exact provider/dogfood parity
* PR Ubuntu CI
* fresh Codex review
* unresolved review thread 0
* mergeability/base drift 再確認

を final head で行います。

## Python 3.10 gate

package contract は Python `>=3.10` で、Ruff/mypy も Python 3.10 を対象にしています。

したがって、少なくとも二つの focused infra test file は Python 3.10 interpreter でも実行します。特に確認するものは、

* `dir_fd`
* fd を受ける `os.utime`
* `os.supports_dir_fd`
* platform flag availability

です。

## macOS gate

現在の Provider CI は `ubuntu-latest`、Python 3.11 の full pytest だけです。

macOS support を merge criterion とするなら、次のどちらかが必要です。

1. `macos-latest` で Artifact publisher focused test を追加する。
2. 実 macOS host で `test_binary_artifact_publisher.py` を実行し、result を final evidence に残す。

mock された `fclonefileat` unit testだけでは、実 filesystem・errno・APFS behavior を証明できません。

---

# 7. Rejected alternatives

## `_assert_path_missing()` をもう一度呼ぶ

最後の check と open の間に、常に新しい race window が残ります。

## `shutil.copy2(..., follow_symlinks=False)` を維持する

destination no-follow を提供しません。source symlink policy の引数です。([Python documentation][1])

## `Path.open("xb")` または full-path `os.open(... O_EXCL ...)`

final leaf symlink raceは閉じますが、destination parent が check 後に symlink へ差し替えられる race を残します。`dir_fd` が必要です。

## `O_NOFOLLOW` だけを付ける

既存 regular file を open・truncate できます。missing/no-replace boundary には `O_CREAT | O_EXCL` が必要です。

## `mkstemp(dir=destination.parent)` の前後で identity を確認する

前の確認と `mkstemp`、または `mkstemp` と後の確認の間に race が残ります。temp staging 自体を held fd に対して行う必要があります。

## staging だけ `mkstemp`、publication だけ dirfd

parent swap が staging 前に起きれば、temp bytes は既に external directory に書かれています。

## publication 時に destination parent を新しく open

現在の Linux/macOS code と同じ late-open 問題です。staging で検証・保持した directory fd を使わなければなりません。

## `os.replace` / pathname rename

* no-overwrite semantics を壊しやすい
* existing formal artifact を置換し得る
* staged descriptor ではなく temp pathname に publication を再依存させる

ため不適切です。

## safe copy 後の `shutil.copystat`

metadata phase で destination pathname を再度開き、race を再導入します。

## cleanup、fsync、confirmation だけ absolute path を使う

publication が安全でも、

* 外部 directory を fsync
* 外部同名 file を hash
* 外部 temp file を unlink

する別の境界破りになります。全工程で同じ directory fd が必要です。

## `/proc/self/fd/<directory_fd>/<name>` を全 platform 共通経路にする

Linux 固有で、macOS support を壊します。Python の `dir_fd` API を使うべきです。

## Linux `O_TMPFILE` や `linkat(AT_EMPTY_PATH)` への全面変更

Linux では有力ですが macOS 非対応で、Python 3.10 の標準 API だけでは扱いにくく、今回の最小修復を超えます。

## Workbench と Artifact の共通 filesystem abstraction

同じ root cause でも、overwrite、no-overwrite、cleanup、committed state が異なります。まず各 module の短い private helper として実装し、重複が確定してから別 issue で抽象化すべきです。

---

# 8. リスク、仮定、human decision

## 仮定

* 対象 platform は Linux と macOS の POSIX filesystem。
* 攻撃モデルには、同一 user 権限の別 process による rename、symlink insertion、leaf replacement を含む。
* directory fd が指す directory object を authority とし、その後の pathname 差し替えによる external symlink target への redirect を防ぐことが主たる security requirement。
* Artifact import の no-overwrite、bytes unchanged、cleanup state、content-free error contract は維持する。

## Human decision 1: Workbench metadata

次のどちらを acceptance とするかを明示する必要があります。

* bytes + mode + mtime を required
* xattrs / ACL / BSD flags まで `copy2` parity を required

P1修復としては前者を推奨します。

## Human decision 2: post-publication parent change

* 既存 `destination_read_failed` warning を再利用する。
* `destination_parent_changed` warning を新設する。

最小 public-contract change は前者、診断精度は後者です。

## Human decision 3: macOS actual gate

macOS support を明記する以上、実 `fclonefileat` path の focused execution を merge 前に必須とするか決定が必要です。推奨は必須です。

## Human decision 4: Workbench directory/symlink branchesの追加 hardening

今回の P1 は ordinary-file `copy2` leaf です。ただし source inspection 上、directory `mkdir` と symlink object creation には pathname operation が残っています。ordinary-file unit に、

* leaf unlink
* regular-file create
* symlink create

までを含めるのは小さい拡張です。recursive directory creationまで descriptor 化するのは別 repair unit とした方が安全です。

## 残存する別問題

directory parent fd binding は、同一 user が検証済み temp inode の内容を publication 前に書き換える問題を解決しません。temp pathname replacement には descriptor publication が効きますが、同じ inode への writable access は別の threat です。これは今回の二 P1 とは異なる repair family として扱うべきです。

---

# 9. 不確実性・未検証主張

* この回答では patch を作成していません。
* tests をローカル実行していません。確認したのは branch head の source/tests と、GitHub 上の既存 CI success metadata です。
* `fclonefileat` の実 macOS filesystem behavior はこの調査では実行検証していません。現在の ctypes call shape を維持する設計であり、実 macOS gate が後続検証対象です。
* directory rename が publication syscall と同時に起きる場合、portable Python 3.10 だけで pathname membership をロックすることはできません。held fd により external symlink target への redirect を防ぎ、pre/post identity revalidation で result semantics を検査する設計です。
* GitHub connector と Python 3.10 公式ドキュメントの参照内容は、Codex による独立実装検証済みではありません。

補足の `設計判断と提案.txt` は exception/failure taxonomy を扱う別テーマで、本 filesystem race の設計根拠には使用していません。

最終的な実装順序は、**Workbench descriptor-bound exclusive leaf create → Artifact held-parent-fd lifecycle → provider/dogfood exact projection → focused/full/Linux/macOS gates → fresh review** が最も小さく、検証可能で、二件の P1 を別々に閉じられる構成です。

[1]: https://docs.python.org/3.10/library/shutil.html "https://docs.python.org/3.10/library/shutil.html"
[2]: https://docs.python.org/3.10/library/tempfile.html "https://docs.python.org/3.10/library/tempfile.html"
[3]: https://docs.python.org/3.10/library/os.html "https://docs.python.org/3.10/library/os.html"
