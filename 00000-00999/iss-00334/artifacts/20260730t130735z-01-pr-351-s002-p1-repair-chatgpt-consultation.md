---
種別: artifact
ID: "20260730t130735z-01"
タイトル: "PR 351 S002 P1 Repair ChatGPT Consultation"
状態: "archived"
作成者: "iwasawayuuta"
最終更新: "2026-07-30"
親: ["iss-00334"]
template: "blank"
authority: "advisory"
derived_from:
  - "PR #351 Review 4818771681"
  - "ChatGPT session iss00334-pr351-s002-p1-repair-2"
reflected_to:
  - "20260730t115808z-pr-repair-batch-pr-351-repair-batch.md"
  - "U002 and U003 repair units"
---

# 20260730t130735z-01 PR 351 S002 P1 Repair ChatGPT Consultation

## Identity

- repository: `chemitaro/spec-dock`
- branch: `iss-00334-implement-chatgpt-issue-planning-workflow`
- HEAD: `6c9302ab08c7f352e85a199b65bdeb522376171c`
- PR: `351`
- exact branch inspected: yes
- default branch fallback: no
- model evidence: `requested=Pro`, `resolved=Pro`, `verified=yes`

## Consultation recovery

- initial session `iss00334-pr351-s002-p1-repair` failed before submission because seven attachments did not become ready within the five-minute wrapper limit.
- metadata showed `promptSubmitted=false`; the failed session is not adopted.
- compact fresh session `iss00334-pr351-s002-p1-repair-2` used the bounded brief plus the two P1 source files and completed.
- operational issue: the specified `chatgpt-use` wrapper can time out during attachment readiness for seven files totaling about 189 KB. Compacting to three attachments succeeded.

## Advisory findings

### F002 Candidate output directory TOCTOU

- P1 confirmed.
- validation returns only path/device/inode and closes the descriptor.
- publication later uses pathname-based `mkdtemp`, ZIP access, rename, and recursive cleanup; writes can occur after path replacement and before revalidation.
- smallest safe direction:
  - reopen the directory at publication entry and compare descriptor identity to the guard;
  - perform private staging, file creation, fsync, no-replace publish, and cleanup descriptor-relative;
  - use the existing byte-snapshot reviewer;
  - keep current Candidate schema, bytes, identity, collision behavior, Darwin/Linux support, and public application API.
- rejected: additional pathname revalidation, global lock, `/proc/self/fd`, long-lived descriptor ownership across Oracle transport, pathname `shutil.rmtree`.

### F003 Archive apply preimage revalidation

- P1 confirmed for canonical targets; companion scope narrowed to absence/content drift at the transaction boundary.
- archive mode bypasses the git-bound stale check, and later snapshots can silently become rollback authority without comparison to operation evidence.
- smallest safe direction:
  - validate internal coherence between pre-apply bytes and blob OIDs;
  - derive optional companion preimage from `expected_head`;
  - snapshot canonical targets and companion at one transaction boundary;
  - compare existence, bytes, and blob OIDs before any managed write;
  - return existing `stale/apply_target_changed` on mismatch without restore;
  - persist only already-matched snapshots as rollback backup.
- rejected: adopting the new snapshot as baseline, post-write detection, schema field expansion, repository-wide locking, git-bound-only comparison.

### F004 Information-insufficient transport

- P2, non-blocking.
- keep as a separate follow-up; do not modify source, skill, schema, or acceptance criteria in S002.

## Integrated recommendation

- keep F002 and F003 as independent repair units with independent Red/Green tests.
- implement provider sources/tests first; synchronize dogfood projection mechanically after both units.
- run focused candidate/apply suites, required integration, byte parity, lint, ordinary fast pytest, validate, and fresh PR observation.
- do not modify Oracle, Prompt, wrapper, browser, local Oracle configuration behavior, canonical planning docs, or public command/schema contracts.

## Freshness boundary

This consultation becomes stale if the head, finding inventory, family grouping, proposed S002 strategy, or relevant source behavior changes before worker handoff.
