# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a56dd39-df18-83e8-9a57-78e0f860a8f9

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

Use the attached prompt file as the task brief. Inspect the attached implementation, tests, and canonical Issue documents, then return the requested concrete repair design.

## Answer

# Executive recommendation

Inspecting the specified GitHub branch and PR #323 shows that the **regular-file leaf path is already descriptor-bound**, but the recursive directory and symlink branches are not. At the connector snapshot, PR #323 is open at head `82874bf35d2f4b4a3b360bb08d7c26ffe0935210`; the requested branch is accessible.

The smallest complete repair is:

> **Convert the private Workbench recursive merge core—not the wider filesystem layer—to descriptor-relative traversal, inspection, and mutation.**

For every recursive frame, hold:

* one verified source-directory descriptor across source enumeration and all child source operations;
* one verified destination-directory descriptor across destination inspection and all child mutations;
* verified child directory descriptors for the entire recursive child call;
* leaf descriptors for the duration of file copy.

Use pathnames only to acquire and verify the initial roots and, where the destination root is absent, its parent. After a directory descriptor has been acquired, use only a single child basename plus `dir_fd`.

Changing only `Path.mkdir()`, `Path.unlink()`, and `Path.symlink_to()` would close the most obvious external-write windows, but it would leave recursive inspection, source `readlink`, and child-directory reopening bound to mutable pathnames. That is not a complete repair.

This design follows the attached brief. 

## Why the current implementation is incomplete

The current regular-file implementation already follows the right pattern:

* open and verify the source file;
* open and verify the destination parent;
* inspect and unlink the destination through `dir_fd`;
* create the replacement with `O_CREAT | O_EXCL | O_NOFOLLOW`;
* copy bytes and metadata through descriptors.

The remaining recursive code still:

* creates a missing root through `destination.mkdir(...)`;
* enumerates through `source.iterdir()`;
* creates nested directories through `destination.mkdir()`;
* replaces destination symlinks through `destination.unlink()`;
* reads source links through `source.readlink()`;
* creates destination links through `destination.symlink_to(...)`.

That conflicts with the canonical Issue 316 safety contract: destination traversal symlinks must not be followed, external link targets must not be read, deleted, or written, and runtime races must become failures rather than successes.  The repair must remain focused because Issue 319 also requires provider-first changes, exact dogfood projection, and no general filesystem framework.

# Exact invariants

## I-1. Descriptor authority

Once a source or destination directory is successfully opened and identity-verified, its descriptor—not its visible pathname—is the authority for the current recursion frame.

A later rename or replacement of the visible path must not redirect any operation to the replacement.

## I-2. Per-frame descriptor lifetime

For each `_merge_workbench_directory` invocation:

* `source_directory_fd` remains open from before enumeration until all enumerated entries have been processed.
* `destination_directory_fd` remains open over all destination inspections and mutations for those entries.
* The caller owns these two descriptors.
* A child-directory branch opens child descriptors and closes them after the recursive call.
* `os.scandir(fd)` must not be assumed to close the supplied descriptor.

At recursion depth `d`, this normally means approximately two held directory descriptors per depth, plus transient leaf descriptors.

## I-3. Basename-only descendant access

After root acquisition, descendant operations receive a single entry name such as `"nested"` or `"analysis.txt"`.

They must not receive or reconstruct an absolute or multi-component destination pathname for filesystem access.

## I-4. Source preparation precedes destination mutation

For each source entry, establish enough source state before changing the destination:

* source directory: open and identity-verify the child source-directory descriptor;
* source regular file: open and identity-verify the source-file descriptor;
* source symlink: obtain the link text with `os.readlink(name, dir_fd=source_parent_fd)` and revalidate the link identity;
* unsupported entry: fail.

Thus a source-side failure should occur before the corresponding destination entry is removed or created.

This does not create a tree-wide preflight transaction: a failure in a later entry can still follow mutations to earlier entries.

## I-5. No symlink target dereference

* Directory opens require `O_DIRECTORY | O_NOFOLLOW`.
* Regular-file opens require `O_NOFOLLOW`.
* Entry inspection uses `os.stat(..., follow_symlinks=False)`.
* Source symlinks are read as link text only.
* Destination symlink replacement unlinks the link object, never its target.
* Destination creation is relative to a verified parent descriptor.

## I-6. Collision semantics remain unchanged

The existing source-wins rules remain authoritative:

| Source                  | Destination          | Result                                      |
| ----------------------- | -------------------- | ------------------------------------------- |
| directory               | missing              | create directory, recurse                   |
| directory               | directory            | recurse, retaining destination-only entries |
| directory               | file/symlink/other   | collision failure; do not delete            |
| regular file            | missing/file/symlink | create or replace leaf                      |
| regular file            | directory/other      | collision failure                           |
| symlink                 | missing/file/symlink | create or replace symlink object            |
| symlink                 | directory/other      | collision failure                           |
| unsupported source type | any                  | failure; do not skip                        |

These are the accepted Issue 316 semantics.

## I-7. `mutation_started` changes only after a successful mutation

Set `mutation_started[0] = True` immediately after, and only after:

* successful `os.mkdir`;
* successful `os.unlink`;
* successful exclusive destination-file creation;
* successful `os.symlink`.

Consequences:

* failed capability checks, opens, stats, reads, identity checks, mkdirs, unlinks, file creates, or symlink creates do not themselves change the flag;
* if a successful unlink is followed by a failed replacement create, the flag is `True`;
* if a successful directory create is followed by a failed child open or verification, the flag is `True`;
* the flag never returns to `False`;
* no rollback is added.

## I-8. Missing-leaf creation is authoritative at the creation syscall

A pre-create missing check is diagnostic. The authoritative result is:

* `O_CREAT | O_EXCL` for a regular file;
* `os.mkdir` for a directory;
* `os.symlink` for a symlink.

If another entry appears before file or symlink creation, the creation syscall must fail rather than overwrite it.

## I-9. Opaque-copy and metadata behavior remain unchanged

* Do not filter by extension, name, MIME type, contents, or secret-like data.
* Preserve regular-file bytes, permission bits, and timestamps through the existing descriptor operations.
* Do not add directory metadata copying, ACL copying, xattr copying, ownership copying, or a new publication protocol.
* Preserve the source Workbench and destination-only entries.

The existing tests already assert opaque files and regular-file bytes/mode/mtime.

## I-10. Fail closed when required descriptor primitives are unavailable

There must be no fallback to `Path.mkdir`, `Path.unlink`, `Path.readlink`, `Path.symlink_to`, or full-path child opens.

An unavailable primitive produces `WorkbenchFilesystemError`, retaining the current `mutation_started` value.

## I-11. Provider remains authoritative

Modify the provider file first:

```text
src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/fs_cli.py
```

Then reproduce it through the approved projection into:

```text
spec-dock/scripts/spec_dock_runtime/infra/fs_cli.py
```

The two files are currently the same Git blob, so the repair must preserve exact parity.

# Proposed descriptor topology

## Root acquisition

Conceptually:

```python
def copy_workbench(source: Path, destination: Path) -> None:
    mutation_started = [False]
    _require_workbench_descriptor_support()

    source_identity = _capture_directory_identity(source)
    source_fd = _open_verified_directory(source, source_identity)

    try:
        destination_kind, destination_identity = _inspect_path(destination)

        if destination_kind == "directory":
            assert destination_identity is not None
            destination_fd = _open_verified_directory(
                destination,
                destination_identity,
            )

        elif destination_kind == "missing":
            parent_identity = _capture_directory_identity(destination.parent)
            parent_fd = _open_verified_directory(
                destination.parent,
                parent_identity,
            )
            try:
                destination_fd = _create_and_open_directory_at(
                    parent_fd,
                    destination.name,
                    mutation_started,
                )
            finally:
                os.close(parent_fd)

        else:
            raise RuntimeError(
                "workbench copy destination is not a directory"
            )

        try:
            _merge_workbench_directory(
                source_fd,
                destination_fd,
                mutation_started,
            )
        finally:
            os.close(destination_fd)
    finally:
        os.close(source_fd)
```

The initial path checks remain useful for stable error classification, but the opened descriptors become authoritative.

For an absent root destination, hold the root destination-parent descriptor only until the new root directory has been safely created and opened. Once `destination_fd` exists, the parent descriptor can be closed.

## Recursive frame

```python
def _merge_workbench_directory(
    source_directory_fd: int,
    destination_directory_fd: int,
    mutation_started: list[bool],
) -> None:
    with os.scandir(source_directory_fd) as entries:
        names = sorted(entry.name for entry in entries)

    for name in names:
        _merge_workbench_entry(
            source_directory_fd,
            destination_directory_fd,
            name,
            mutation_started,
        )
```

Do not use `DirEntry.is_dir()`, `is_file()`, or cached `stat()` information as the authority. Materialize only the names, then perform a fresh:

```python
os.stat(name, dir_fd=source_directory_fd, follow_symlinks=False)
```

for each entry immediately before processing it.

Python supports passing a directory descriptor to `os.scandir()` on Unix, and relative `dir_fd` operations map to the POSIX `*at` family. ([Python documentation][1])

## Directory source entry

```python
source_kind, source_identity = _inspect_entry_at(source_parent_fd, name)

source_child_fd = _open_verified_directory_at(
    source_parent_fd,
    name,
    source_identity,
)
try:
    destination_kind, destination_identity = _inspect_entry_at(
        destination_parent_fd,
        name,
    )

    if destination_kind == "missing":
        destination_child_fd = _create_and_open_directory_at(
            destination_parent_fd,
            name,
            mutation_started,
        )
    elif destination_kind == "directory":
        destination_child_fd = _open_verified_directory_at(
            destination_parent_fd,
            name,
            destination_identity,
        )
    else:
        raise RuntimeError("workbench copy entry type collision")

    try:
        _merge_workbench_directory(
            source_child_fd,
            destination_child_fd,
            mutation_started,
        )
    finally:
        os.close(destination_child_fd)
finally:
    os.close(source_child_fd)
```

The source child descriptor is opened before creating the destination child. This avoids changing the destination when the source child was already replaced or malformed.

# Safely creating a missing destination directory

A narrowly scoped helper should own the complete `mkdir → inspect → open → verify` sequence.

```python
def _create_and_open_directory_at(
    parent_fd: int,
    name: str,
    mutation_started: list[bool],
) -> int:
    _assert_entry_missing_at(parent_fd, name)

    os.mkdir(name, 0o777, dir_fd=parent_fd)
    mutation_started[0] = True

    status = os.stat(
        name,
        dir_fd=parent_fd,
        follow_symlinks=False,
    )
    if not stat.S_ISDIR(status.st_mode):
        raise RuntimeError(
            "workbench copy created directory identity changed"
        )

    return _open_verified_directory_at(
        parent_fd,
        name,
        _descriptor_identity(status),
    )
```

And:

```python
def _open_verified_directory_at(
    parent_fd: int,
    name: str,
    expected: DirectoryIdentity,
) -> int:
    fd = os.open(
        name,
        _directory_open_flags(),
        dir_fd=parent_fd,
    )
    try:
        status = os.fstat(fd)
        if (
            not stat.S_ISDIR(status.st_mode)
            or _descriptor_identity(status) != expected
        ):
            raise RuntimeError(
                "workbench copy directory identity changed"
            )
    except BaseException:
        os.close(fd)
        raise
    return fd
```

Important details:

1. `os.mkdir` is relative to the already verified parent descriptor; the parent pathname is not reopened.
2. `mutation_started` changes immediately after `mkdir` succeeds.
3. `os.stat(..., follow_symlinks=False)` rejects a replacement symlink as a directory.
4. The open uses `O_DIRECTORY | O_NOFOLLOW`.
5. `fstat` confirms that the opened descriptor is the object observed by the relative no-follow stat.
6. If verification fails, do not remove the created directory. Existing behavior promises no rollback.
7. Use mode `0o777`, allowing the process umask to produce the effective directory permissions, matching ordinary `Path.mkdir()` behavior.

`os.mkdir` supports `dir_fd`, and `os.stat` supports both `dir_fd` and `follow_symlinks=False` on supported Unix platforms. ([Python documentation][1])

## Unavoidable directory-create residual

Standard Python 3.10 does not expose a portable operation that both creates a directory and returns its descriptor atomically. Therefore, a window remains between successful `mkdir` and the following `stat/open`.

The proposed sequence prevents a symlink replacement from being followed. It cannot absolutely prove that the directory opened is the exact inode originally created if a same-privilege adversary replaces it with another real directory before the first post-create stat.

Closing that stronger race would require a different, nonportable publication protocol or platform-specific system calls. It is outside this P1, which is specifically about preventing pathname-parent redirection and symlink traversal.

# Destination file and symlink replacement

## Common verified unlink

Use a private helper:

```python
def _unlink_verified_entry_at(
    parent_fd: int,
    name: str,
    expected: PathIdentity,
) -> None:
    actual = os.stat(
        name,
        dir_fd=parent_fd,
        follow_symlinks=False,
    )
    if _descriptor_identity(actual) != expected:
        raise RuntimeError("workbench copy path identity changed")

    os.unlink(name, dir_fd=parent_fd)
```

The caller sets `mutation_started[0] = True` only after the helper returns.

This unlinks a symlink object rather than its target and cannot be redirected through a swapped parent pathname.

### Residual leaf race

The no-follow `stat` and `unlink` remain separate system calls. A concurrent process can replace the leaf between them, causing the replacement leaf in the **same held directory** to be removed.

There is no standard portable unlink-by-inode operation. The important security property for this repair is that the operation remains confined to the held directory and never follows a symlink target outside it. Issue 316 already declines to promise complete concurrent-mutation elimination or tree transactions.

## Regular-file branch

Refactor the already safe implementation so it receives held parent descriptors and a basename rather than reopening source and destination parents by full path:

```python
source_fd = _open_verified_regular_source_at(
    source_parent_fd,
    name,
    source_identity,
)
try:
    source_status = os.fstat(source_fd)

    if destination_identity is not None:
        _unlink_verified_entry_at(
            destination_parent_fd,
            name,
            destination_identity,
        )
        mutation_started[0] = True

    _assert_entry_missing_at(destination_parent_fd, name)

    destination_fd = _open_exclusive_regular_file(
        destination_parent_fd,
        name,
    )
    mutation_started[0] = True
    try:
        _copy_descriptor_bytes(source_fd, destination_fd)
        os.fchmod(
            destination_fd,
            stat.S_IMODE(source_status.st_mode),
        )
        os.utime(
            destination_fd,
            ns=(
                source_status.st_atime_ns,
                source_status.st_mtime_ns,
            ),
        )
    finally:
        os.close(destination_fd)
finally:
    os.close(source_fd)
```

The existing `O_CREAT | O_EXCL | O_NOFOLLOW` behavior remains authoritative when a leaf appears after the missing check.

## Symlink branch

Read and validate the source link before destination mutation:

```python
def _read_verified_symlink_at(
    parent_fd: int,
    name: str,
    expected: PathIdentity,
) -> str:
    before = os.stat(
        name,
        dir_fd=parent_fd,
        follow_symlinks=False,
    )
    if (
        not stat.S_ISLNK(before.st_mode)
        or _descriptor_identity(before) != expected
    ):
        raise RuntimeError("workbench copy source identity changed")

    target = os.readlink(name, dir_fd=parent_fd)

    after = os.stat(
        name,
        dir_fd=parent_fd,
        follow_symlinks=False,
    )
    if _descriptor_identity(after) != expected:
        raise RuntimeError("workbench copy source identity changed")

    return target
```

Then:

```python
link_target = _read_verified_symlink_at(
    source_parent_fd,
    name,
    source_identity,
)

if destination_kind in {"file", "symlink"}:
    assert destination_identity is not None
    _unlink_verified_entry_at(
        destination_parent_fd,
        name,
        destination_identity,
    )
    mutation_started[0] = True

_assert_entry_missing_at(destination_parent_fd, name)

os.symlink(
    link_target,
    name,
    dir_fd=destination_parent_fd,
)
mutation_started[0] = True
```

`os.readlink`, `os.symlink`, and `os.unlink` support descriptor-relative operation on Unix. ([Python documentation][1])

If a leaf appears after the missing check:

* `os.symlink` fails with an existence error;
* it does not overwrite or follow the appearing leaf;
* `mutation_started` is `False` for an initially missing destination;
* it is `True` if an old destination was already successfully unlinked.

A pre/post stat cannot eliminate an exact ABA replacement of a source symlink. It does ensure that ordinary source changes are detected and that no target is dereferenced.

# Traversal and inspection scope

## Recommended boundary

Move these operations to descriptor-relative APIs:

* recursive source enumeration;
* source child inspection;
* destination child inspection;
* source child-directory open;
* destination child-directory open;
* source regular-file open;
* source symlink read;
* destination directory creation;
* destination file/symlink unlink;
* destination file creation;
* destination symlink creation.

Keep these existing pathname operations:

* lexical containment and ancestry preflight before merge;
* initial source-root identity capture;
* initial destination-root or destination-parent identity capture;
* content-free diagnostic paths and result presentation.

This keeps the patch local to the Workbench merge adapter without weakening the actual mutation boundary.

## Residual TOCTOU if only obvious mutations change

Replacing only:

```python
destination.mkdir()
destination.unlink()
destination.symlink_to(...)
```

would leave several material inconsistencies.

### Path-based recursive reopening

After a child directory has been created safely, the existing recursive call would inspect and enumerate it again by full path. A swap between creation and recursion could redirect traversal.

### Mismatched destination inspection and mutation

`_inspect_path(destination)` could inspect a newly substituted visible directory, while the later mutation targets an older held directory descriptor—or vice versa. Collision decisions would no longer describe the object actually mutated.

### Source parent replacement

`source.iterdir()`, `_inspect_path(source_entry)`, and `source.readlink()` could operate through a replaced source parent. That can cause external or unrelated source data to be read even if destination writes are descriptor-bound.

### Directory identity checks remain advisory

Repeated pathname identity checks do not bind a subsequent operation. There is always another interval between the last check and the next pathname resolution.

Therefore, the repair should be **localized to the recursive merge implementation but complete within that implementation**: traversal, inspection, opening, and mutation all become descriptor-relative.

# Proposed helper and function responsibility changes

| Function/helper                                                    | New responsibility                                                    |
| ------------------------------------------------------------------ | --------------------------------------------------------------------- |
| `_require_workbench_descriptor_support()`                          | Validate all required flags and fd capabilities before mutation       |
| `_inspect_entry_at(parent_fd, name)`                               | No-follow relative stat; return kind and identity                     |
| `_assert_entry_missing_at(parent_fd, name)`                        | Relative diagnostic missing check                                     |
| `_open_verified_directory_at(parent_fd, name, expected)`           | No-follow directory open and `fstat` verification                     |
| `_create_and_open_directory_at(parent_fd, name, mutation_started)` | Relative mkdir, flag update, no-follow inspect/open/verify            |
| `_open_verified_regular_source_at(parent_fd, name, expected)`      | Relative no-follow source-file open and verification                  |
| `_unlink_verified_entry_at(parent_fd, name, expected)`             | Relative no-follow identity check followed by unlink                  |
| `_read_verified_symlink_at(parent_fd, name, expected)`             | Relative readlink with pre/post identity validation                   |
| `_copy_regular_file(...)`                                          | Accept parent fds/name; do not open parent paths                      |
| `_merge_workbench_directory(...)`                                  | Accept borrowed source/destination directory fds; enumerate source fd |
| `_merge_workbench_entry(...)`                                      | Accept parent fds and one basename; apply collision matrix            |

Do not introduce:

* a descriptor object hierarchy;
* a generic secure-filesystem service;
* a reusable transaction framework;
* an extension mechanism;
* a new third-party dependency.

Path-oriented helpers used by ancestry/inventory guards may remain. Path-oriented merge helpers that become unused should be removed rather than retained as alternate mutation paths.

# Python 3.10, macOS, and Linux compatibility

## Required feature gate

At or before merge entry, verify the equivalent of:

```python
required_dir_fd_functions = {
    os.open,
    os.stat,
    os.mkdir,
    os.unlink,
    os.readlink,
    os.symlink,
}

if not required_dir_fd_functions <= os.supports_dir_fd:
    fail_closed()

if os.stat not in os.supports_follow_symlinks:
    fail_closed()

if os.scandir not in os.supports_fd:
    fail_closed()

if not hasattr(os, "O_DIRECTORY"):
    fail_closed()

if not hasattr(os, "O_NOFOLLOW"):
    fail_closed()
```

Python documents `os.supports_dir_fd`, `os.supports_fd`, and the Unix-only nature of many descriptor-relative forms. ([Python documentation][1])

`os.open` accepts `dir_fd`, while `O_DIRECTORY` and `O_NOFOLLOW` are platform extension constants only when supplied by the host C library. ([Python documentation][1])

## `O_CLOEXEC`

Continue treating `O_CLOEXEC` as optional:

```python
flags |= getattr(os, "O_CLOEXEC", 0)
```

Python-created descriptors are normally non-inheritable, but retaining the current optional flag is harmless and explicit.

## `os.scandir(fd)`

Use it only to obtain the names snapshot:

```python
with os.scandir(source_fd) as entries:
    names = sorted(entry.name for entry in entries)
```

Do not rely on `DirEntry` cached type or stat information. Concurrent changes can make cached information stale, and each entry needs a fresh relative no-follow stat immediately before processing.

## `os.utime(fd, ns=...)`

The existing descriptor form should remain. Python supports file descriptors and nanosecond timestamps for `os.utime`; using the source `st_atime_ns` and `st_mtime_ns` avoids float conversion. ([Python documentation][1])

## Fallback policy

No pathname fallback is justified.

The supported product platforms are macOS and Linux; a host lacking the required secure descriptor operations should fail the Workbench copy rather than silently use a weaker implementation. A Windows-compatible fallback is outside the current platform contract.

Actual execution on Python 3.10 and both operating-system families remains a required verification item; API availability alone does not prove filesystem behavior.

# Ordered implementation sequence

1. **Add the capability gate.**
   Make it fail before root destination creation whenever possible. Add focused tests that monkeypatch each required capability/flag as unavailable.

2. **Add the minimal `*_at` helpers.**
   Implement entry inspection, directory open, directory create/open, regular-file source open, verified unlink, and symlink read. Keep messages content-free.

3. **Bind root descriptors.**
   Open and verify the source root. For an existing destination, open and verify it. For a missing destination, hold the verified parent fd through relative mkdir and child-directory open.

4. **Change recursive function signatures.**
   `_merge_workbench_directory` receives source and destination fds. It snapshots sorted source names with `os.scandir(source_fd)`. `_merge_workbench_entry` receives the two parent fds and one name.

5. **Convert the directory branch.**
   Open source child first. Open or create destination child relative to the held destination parent. Recurse with child descriptors.

6. **Adapt the regular-file branch.**
   Preserve the current descriptor copy implementation, but stop reopening source and destination parents by full pathname.

7. **Convert the symlink branch.**
   Read source link text relative to the source fd. Verify and unlink the destination relative to the destination fd. Create with `os.symlink(..., dir_fd=...)`.

8. **Remove dead pathname merge paths and update fault boundaries.**
   Existing tests that monkeypatch `Path.mkdir` or `Path.symlink_to` must target the new helper or corresponding `os.*` call. Do not weaken assertions merely because the private boundary changed.

9. **Update provider first, then project to dogfood.**
   Assert byte equality and SHA-256 equality of the mirrored runtime files.

10. **Run focused gates.**
    At minimum:

    ```bash
    uv run pytest tests/unit/infra/test_runtime_fs_cli_workbench.py
    uv run pytest tests/unit/application/test_workbench.py
    uv run pytest tests/cli_runtime/test_workbench.py
    make lint
    git diff --check
    ```

11. **Run repository-level gates and installed verification.**
    Follow the Issue 319 order: unit, CLI runtime, integration, full pytest, configured lint, broader Ruff gates, installed scenario, provider/dogfood parity, PR CI, and fresh review.

# Focused adversarial and regression matrix

| Case                                             | Injection point                                                        | Required result                                                                                        |                                                                              |
| ------------------------------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| Root destination-parent swap                     | After parent fd verification, immediately before relative root `mkdir` | No entry in external symlink target; any created `.workbench` is in the held/displaced original parent |                                                                              |
| Root create then injected failure                | Immediately after successful root `mkdir`                              | Error with `mutation_started=True`; external tree unchanged; no rollback claim                         |                                                                              |
| Nested destination-parent swap                   | After nested parent fd is held, before child mkdir/file/symlink create | Mutations remain in held nested directory; external target unchanged                                   |                                                                              |
| New-directory symlink substitution               | After `mkdir`, before child open                                       | `O_NOFOLLOW                                                                                            | O_DIRECTORY`open fails;`mutation_started=True`; external directory untouched |
| New-directory real-directory substitution        | After `mkdir`, before post-create stat/open                            | Document current portable limitation; ensure no pathname-parent redirection                            |                                                                              |
| Existing destination directory swap              | After relative stat, before child open                                 | Open/fstat identity mismatch; no mutation for that entry                                               |                                                                              |
| Source parent swap during enumeration            | After source fd open, before/during `scandir`                          | Entries come from held source directory; replacement external source is not read                       |                                                                              |
| Source directory child swap                      | After source child identity capture, before open                       | Open/fstat mismatch; no corresponding destination mutation                                             |                                                                              |
| Source symlink parent swap                       | Before relative `readlink`                                             | Link text is read from held source directory, not replacement path                                     |                                                                              |
| Source symlink changes during read               | Between pre-stat and post-stat                                         | Failure; no corresponding destination mutation unless prior entries already changed                    |                                                                              |
| Existing symlink/file changed before unlink      | Before verified relative unlink                                        | Identity mismatch; `mutation_started` unchanged for that entry                                         |                                                                              |
| Missing symlink destination appears              | Immediately before `os.symlink`                                        | `EEXIST`; `mutation_started=False`; appearing entry and external target unchanged                      |                                                                              |
| Leaf inserted after successful unlink            | Before file or symlink replacement create                              | Create fails; `mutation_started=True`; inserted symlink target unchanged                               |                                                                              |
| Destination parent swapped before symlink create | After parent fd acquired                                               | Link is created only in held parent; external target directory unchanged                               |                                                                              |
| Regular file missing-leaf symlink insertion      | Before exclusive create                                                | Existing test remains: failure, `mutation_started=False`, external bytes unchanged                     |                                                                              |
| Regular file insertion after unlink              | Before exclusive create                                                | Existing test remains: failure, `mutation_started=True`, external bytes unchanged                      |                                                                              |
| Directory → file/symlink collision               | Before any deletion                                                    | Failure, destination data retained, no new mutation                                                    |                                                                              |
| File/symlink → directory collision               | Before any deletion                                                    | Failure, destination subtree retained                                                                  |                                                                              |
| Destination-only entries                         | Normal recursive merge                                                 | Retained                                                                                               |                                                                              |
| Repeated copy                                    | No concurrent mutation                                                 | Idempotent result                                                                                      |                                                                              |
| Empty source                                     | Missing destination                                                    | Empty destination directory safely created                                                             |                                                                              |
| Unsupported source entry                         | FIFO or another special entry                                          | Failure; do not skip                                                                                   |                                                                              |
| Byte/mode/mtime                                  | Binary regular file with fixed metadata                                | Destination bytes, mode, and mtime match                                                               |                                                                              |
| Mid-copy failure                                 | Second file or mid-write                                               | Partial mutation retained; `mutation_started=True`; raw body/error not exposed                         |                                                                              |
| Required primitive absent                        | Capability monkeypatch                                                 | Fail closed; no pathname fallback                                                                      |                                                                              |
| Descriptor cleanup                               | Success and every injected failure point                               | Every opened child/leaf/root fd closed exactly once                                                    |                                                                              |
| Provider/dogfood parity                          | After projection                                                       | Exact file bytes and inventory match                                                                   |                                                                              |
| Python/platform lanes                            | Python 3.10 Linux and macOS                                            | Focused descriptor tests pass; no unsupported-path fallback                                            |                                                                              |

Existing tests already cover several regular-file races, descriptor-bound visible-parent replacement, metadata, collision behavior, and no-rollback fault semantics.

The current missing-root parent test swaps before the existing revalidation rather than in the vulnerable interval after the final check and before `mkdir`; replace or supplement it with a hook immediately around the real descriptor-relative `os.mkdir` call.

The current failed-symlink-create test monkeypatches `Path.symlink_to`; it must move to `os.symlink` or the new private helper while preserving the `mutation_started=False` assertion.

# Failure modes and expected state

| Failure point                                  |                            Mutation state | Filesystem expectation                            |
| ---------------------------------------------- | ----------------------------------------: | ------------------------------------------------- |
| Capability check                               |               unchanged, normally `False` | no destination change                             |
| Root/source directory open or identity check   |                                 unchanged | no destination change                             |
| Source enumeration/inspection/open/readlink    |               unchanged for current entry | earlier entries may remain                        |
| Destination inspection or child-directory open |               unchanged for current entry | earlier entries may remain                        |
| `mkdir` fails                                  |                                 unchanged | no created directory                              |
| `mkdir` succeeds, child verification fails     |                                    `True` | created/displaced directory may remain            |
| Verified unlink fails                          |                 unchanged for that unlink | existing leaf remains unless concurrently changed |
| Unlink succeeds, create fails                  |                                    `True` | old leaf is gone; no rollback                     |
| Exclusive file create fails                    | unchanged unless unlink already succeeded | appearing entry retained                          |
| Destination file created, copy/metadata fails  |                                    `True` | partial file may remain                           |
| Symlink creation fails                         | unchanged unless unlink already succeeded | no link created by this operation                 |
| Later recursive entry fails                    |   `True` if any earlier mutation occurred | earlier mutations remain                          |

# Alternatives rejected

## Add more pathname identity checks

Every final check is followed by another pathname resolution. This narrows but does not close the race.

## Change only `mkdir`, `unlink`, and `symlink_to`

This leaves path-based enumeration, inspection, source `readlink`, and recursive child reopening. It does not establish an inspected-object/mutated-object boundary.

## Open the destination parent separately for each leaf

A fresh open can bind to a path replacement. The recursion frame should acquire the parent once and retain it across inspection and mutation.

## Retain full-path source file and symlink operations

Identity checks reduce the risk but still allow the parent path to be replaced between checks and the operation. Source descendants should use the held source-directory fd too.

## Use `shutil.copytree` or another high-level recursive primitive

It cannot express the required collision matrix and descriptor-bound destination ancestry while retaining destination-only entries.

## Use a pathname fallback on unsupported hosts

That silently restores the vulnerability. Fail closed instead.

## Introduce Linux-only `openat2`, `renameat2`, `O_PATH`, or `O_TMPFILE`

Those could strengthen selected races but would not satisfy the Python 3.10/macOS contract and would materially expand the patch.

## Introduce a generic secure-filesystem abstraction

The accepted design explicitly localizes Workbench copy to a small guarded traversal and rejects a speculative framework.

## Add rollback or whole-tree atomicity

That changes the accepted public failure contract and substantially expands complexity. The command explicitly reports partial mutation instead.

# Assumptions

* The supported runtime is Python 3.10+ on POSIX macOS and Linux.
* The adversary may rename entries, replace visible paths with symlinks, and substitute leaves using the same user privileges.
* The key safety requirement is that no operation be redirected through a replaced parent pathname or symlink target outside the held destination directory.
* Descriptor-bound continuation in a directory that has been renamed away is acceptable and is consistent with the existing regular-file test, which expects a copy to continue in the held displaced directory rather than the replacement external directory.
* Concurrent mutation does not receive serializable, transactional, or rollback semantics.
* Directory mode remains ordinary `mkdir` plus umask; regular-file mode and timestamps retain the existing descriptor-copy behavior.

# Uncertainty and unverified claims

* No patch was produced and no tests were run as part of this consultation.
* The brief’s “2606 passed, 76 skipped” result is prompt-provided historical evidence, not an independently rerun result on the current head. 
* The GitHub observations above are a connector snapshot from July 15, 2026; branch head and review state can change after that observation.
* Actual Python 3.10 execution and real macOS filesystem behavior remain follow-up verification gates.
* The standard-library `mkdir → open` sequence cannot atomically bind the newly created directory inode. The proposed design prevents symlink following and parent-path redirection but retains the real-directory substitution limitation described above.
* `stat → unlink` and `stat → readlink → stat` retain same-directory leaf races, including possible ABA replacement. They cannot redirect mutation through a symlink target, but they are not full concurrent-mutation exclusion.
* The separate uploaded `設計判断と提案.txt` concerns exception/failure taxonomy rather than this filesystem race and was not used as authority for this repair. 

The resulting repair unit should therefore be limited to **descriptor-bound recursive Workbench traversal and entry mutation, corresponding focused tests, provider-to-dogfood projection, and the required quality reruns**.

[1]: https://docs.python.org/3.10/library/os.html "os — Miscellaneous operating system interfaces — Python 3.10.20 documentation"
