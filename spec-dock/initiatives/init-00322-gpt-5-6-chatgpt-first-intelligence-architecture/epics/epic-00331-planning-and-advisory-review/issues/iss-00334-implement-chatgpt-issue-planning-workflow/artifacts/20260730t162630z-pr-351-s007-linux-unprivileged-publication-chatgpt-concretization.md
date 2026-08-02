# Oracle Browser Transcript

Conversation: https://chatgpt.com/g/g-p-69fd45693ed48191a7defd8273c37115-for-codex-app/c/6a6b7882-5754-83ee-b428-e4944648a257

## Prompt

Required repository connector context:
- @GitHub chemitaro/spec-dock
- Current branch: iss-00334-implement-chatgpt-issue-planning-workflow
- Default branch: main
- MUST inspect this GitHub repository with the GitHub connector before answering.
- First inspect the current branch. If the current branch does not exist or cannot be opened, inspect the default branch instead.
- Hard failure condition: if the GitHub connector/app is unavailable, or if the repository, current branch, and default branch cannot be accessed, return immediately with exactly: repository access failed.
- Do not continue from attached files, prompt context, memory, or general knowledge when repository access fails.
- Attached files and prompt-provided context are supplementary only after repository access succeeds.

Use the attached prompt as the complete bounded task brief. Inspect the required current GitHub branch first, then the attached local S007 source and tests. Return only the requested implementation work packet.

## Answer

# S007 implementation work packet — unprivileged Linux Candidate publication

## Repository gate

* Repository: `chemitaro/spec-dock`
* Branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
* Observed branch HEAD: `91715eecf306bd0c978da922f87193151764cdcd`
* Required HEAD comparison: `identical`, `ahead_by=0`, `behind_by=0`
* Review basis after the GitHub gate: the attached uncommitted S007 source and tests. 

## Finding assessment

**Confirmed as a compatibility defect.**

The local S007 implementation correctly changes publication from a mutable staged pathname to the verified staged descriptor, but its Linux backend uses `linkat(staged_fd, "", ..., AT_EMPTY_PATH)`.  Linux documents `AT_EMPTY_PATH` as capability-gated, while also documenting `/proc/self/fd/<fd>` plus `AT_SYMLINK_FOLLOW` as the alternative when the caller lacks `CAP_DAC_READ_SEARCH`. Newer kernels can relax the capability requirement when open-time and link-time credentials match, but relying on that makes behavior kernel-version and credential-history dependent. ([man7.org][1])

The existing mocked syscall-call test verifies argument wiring only; it cannot establish real unprivileged execution. 

## Selected primitive

Keep the existing ordinary named staged file and publish on Linux with exactly:

`linkat(AT_FDCWD, "/proc/self/fd/<staged_fd>", destination_fd, destination_name, AT_SYMLINK_FOLLOW)`

Concrete private constants and values:

* `AT_FDCWD = -100`
* `AT_SYMLINK_FOLLOW = 0x00000400`
* Source argument: `os.fsencode(f"/proc/self/fd/{staged_descriptor}")`
* Destination remains relative to the already guarded `destination_descriptor`.

Do not resolve the proc link with `readlink()`. Pass the proc-fd path directly to `linkat()`. `/proc/self/fd/N` denotes the process’s open descriptor, and `AT_SYMLINK_FOLLOW` makes `linkat()` link its underlying file; therefore publication remains bound to the verified open-file identity rather than the swappable staged name. This is an inference directly supported by the proc-fd and `linkat` contracts. ([man7.org][2])

`linkat()` naturally preserves no-replace behavior: it atomically creates the new hard-link name and returns `EEXIST` rather than overwriting an existing destination. ([man7.org][1])

## Bounded alternatives

* **Retain `AT_EMPTY_PATH`: rejected.** It works without the capability only under newer same-credential kernel behavior and is therefore not a sufficient cross-runner contract.
* **Linux `O_TMPFILE`: rejected for S007.** It would remove the staged pathname entirely, but requires Linux-specific stage creation, changes `_OwnedEntry` and cleanup ownership, and depends on filesystem-specific `O_TMPFILE` support. It would still normally use proc-fd publication for capability-free compatibility. ([man7.org][3])
* **Identity-check followed by staged-path `renameat2`: prohibited.** A rename would again consume the mutable source pathname after the identity check.

## Implementation scope

Change only `_link_exclusive_linux_at()` in both mirrored runtime sources:

* `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py`
* `spec-dock/scripts/spec_dock_runtime/infra/issue_planning_candidate.py`

Keep these S007 elements unchanged:

* `_publish_verified_fd_no_replace_at()` dispatch
* Darwin `fclonefileat(staged_fd, destination_fd, final_name, 0)`
* named `O_CREAT | O_EXCL` private staging
* deterministic ZIP construction and validation
* staged-descriptor identity checks
* post-publication descriptor reopening and byte/hash verification
* directory `fsync`
* public exception classes, status, reason and schema
* cleanup ownership rules

The two runtime mirrors must remain byte-identical.

## Failure mapping

Inside `_link_exclusive_linux_at()`:

* Missing libc `linkat` symbol → `NotImplementedError`.
* `EEXIST` → `FileExistsError`.
* Every other errno, including `ENOENT`, `EACCES`, `EPERM`, `ENOSYS`, `EXDEV`, `EROFS`, `EMLINK` or unsupported hard links → `OSError`.

The existing caller must continue mapping:

* `FileExistsError` → `CandidateCollision`
* `NotImplementedError` or any other `OSError` → `CandidatePublicationFailed("Candidate publication failed")`

There must be **no fallback** to `staged.name`, `renameat2`, copying, or any other pathname-authoritative publication. Missing or inaccessible procfs therefore fails closed.

## Cleanup implications

A successful Linux call creates a second name for the already verified staged inode; it does not copy or rewrite bytes. Consequently, Candidate hash, byte count and deterministic identity remain unchanged.

Retain the local S007 cleanup sequence:

1. Open the final entry with `O_NOFOLLOW`.
2. Verify its bytes and SHA-256 against the derived Candidate identity.
3. Remove the private staged name only when `_owned_entry_matches()` still proves ownership.
4. On any post-link verification or directory-sync failure, remove the final entry only when the captured `published_entry` still matches it.
5. Preserve any attacker-created replacement staged name rather than deleting it.

If the original named staged inode is completely unlinked before publication, proc-fd hard-linking can return `ENOENT`; that is the required fail-closed outcome.

## Required Linux assumptions

* Linux provides `linkat()` with `AT_SYMLINK_FOLLOW`.
* Procfs is mounted and the process can traverse `/proc/self/fd`.
* The output filesystem supports hard links.
* Stage and final entry are on the same mounted filesystem, inherently satisfied because the stage is created through the output-directory descriptor.
* The process owns or otherwise has permission to hard-link the mode-`0600` staged inode.
* The staged inode retains at least one filesystem link until publication; rename is safe, complete unlink causes closed failure.
* The supported durability model assumes ordinary local POSIX filesystem behavior; no new network-filesystem recovery protocol is introduced.

## Verification changes

### 1. Update the mocked call contract

Change the Linux expected call in `test_fd_publication_backends_pass_verified_descriptor_to_os_primitive` from:

`(11, b"", 22, b"candidate.zip", 0x00001000)`

to:

`(-100, b"/proc/self/fd/11", 22, b"candidate.zip", 0x00000400)`

Keep the Darwin expectation unchanged.

### 2. Add a real Linux syscall test

Add a Linux-only test named along the lines of:

`test_linux_proc_fd_publication_is_real_unprivileged_descriptor_bound_and_no_replace`

The test must:

1. Skip only on non-Linux platforms.
2. Read `CapEff` from `/proc/self/status`.
3. Assert `os.geteuid() != 0`.
4. Assert capability bit 2, `CAP_DAC_READ_SEARCH`, is clear. Do not skip when either assertion fails; Linux CI must not produce a privileged false green.
5. Create an ordinary named stage using `os.open(..., O_RDWR | O_CREAT | O_EXCL, 0o600, dir_fd=output_fd)`.
6. Write and `fsync()` known bytes.
7. Rename that stage to another name and create different sentinel bytes at the original staged name.
8. Invoke the real `_link_exclusive_linux_at()` without mocking `ctypes`, libc, `linkat`, or the backend dispatcher.
9. Assert the final file contains the original descriptor bytes, not the replacement bytes.
10. Assert final `st_dev` and `st_ino` equal `os.fstat(staged_fd)`.
11. Invoke the primitive again for the same final name, assert `FileExistsError`, and assert the existing final bytes are unchanged.
12. Close descriptors in `finally`.

This test simultaneously proves real proc-fd publication, absence of the relevant capability, descriptor authority after source-name replacement, and no-replace behavior.

### 3. Retain higher-level regressions

The existing S007 tests must continue proving:

* post-match staged-name swapping publishes the verified descriptor;
* racing destination collision preserves the existing final entry;
* backend failure uses no pathname fallback;
* success removes only the owned stage;
* failure removes only owned stage/final entries;
* Darwin dispatch and arguments are unchanged.

Run:

```text
uv run pytest tests/unit/infra/test_issue_planning_candidate.py
make lint
uv run pytest
```

The exact-head Provider CI already executes the complete pytest suite on `ubuntu-latest`, so the Linux-only real-primitive test belongs in that required path.

External Linux ABI references were retrieved on July 31, 2026; execution against the actual CI kernel and filesystem remains the required final verification.

[1]: https://man7.org/linux/man-pages/man2/link.2.html "link(2) - Linux manual page"
[2]: https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html?utm_source=chatgpt.com "proc_pid_fd(5) - Linux manual page"
[3]: https://www.man7.org/linux/man-pages/man2/open.2.html?utm_source=chatgpt.com "open(2) - Linux manual page"
