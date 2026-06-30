---
種別: 実装計画書（Issue）
ID: "iss-00253"
タイトル: "Connect Delegated Specialist Routing And Draft Artifact Sources"
Issue Grade: "strict"
状態: "draft"
作成者: "iwasawayuuta"
最終更新: "2026-07-01"
関連Requirement: ["requirement.md"]
関連Design: ["design.md"]
関連Report: ["report.md"]
親: ["epic-00224", "init-local-00003"]
---

# iss-00253 Connect Delegated Specialist Routing And Draft Artifact Sources — Issue 実装計画書（Strict）

## 1. 実装戦略

`test_new.py` の旧期待値を red にし、Issue draft design/plan だけを profile-aware routing へ切り替える。requirement draft と Initiative / Epic draft は preservation tests で守る。

## 2. マイルストーン

| Milestone | 成果 | 検証 |
|---|---|---|
| M0 | 現行 `new doc draft-*` routing と tests の baseline | inspection |
| M1 | classified Issue design/plan draft の profile template success path | CLI tests |
| M2 | missing / invalid / stale `.assurance.json` no-write fail-closed | CLI tests |
| M3 | `draft-requirement` と Initiative / Epic draft preservation | regression tests |
| M4 | template loader / path guard reuse | unit or CLI tests |
| M90 | docs / rules update | docs inspection |
| M95 | strict spec review | spec-reviewer pass |
| M99 | issue-local handoff gate | `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py`, validate |

## 3. Behavior Backlog

| Behavior | 内容 | Closure |
|---|---|---|
| B-001 | Standard Issue draft design uses standard profile design template | AC-001 |
| B-002 | Strict Issue draft plan uses strict profile plan template | AC-002 |
| B-003 | missing / invalid / stale contract fails before write | AC-003 |
| B-004 | requirement / initiative / epic drafts preserve old behavior | AC-004 |
| B-005 | legacy thin normalization is bypassed for profile drafts | AC-005 |
| B-006 | draft does not self-claim authority or reviewer pass | AC-006 |
| B-007 | assurance compose profile template behavior still passes | AC-007 |

## 4. 変更対象

- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/test_assurance_compose.py`
- issue discussion docs / rules

## 5. 禁止変更

- canonical issue `design.md` / `plan.md` を `new doc` で更新しない。
- missing assurance で Standard fallback を作らない。
- G1/G3 の guidance / evidence gate をこの Issue に混ぜない。

## 6. Review / commit gate

- success path と fail-closed path は同じ Epic PR 内で閉じる。
- M99 では test command、no-write確認、docs parity を `report.md` に記録する。

## 7. Epic branch baton / PR policy

- この Issue では個別 PR を作成しない。
- M99 は `iss-00254` に渡せる local closure checkpoint とする。
- M99 通過後、draft routing success / fail-closed path、preservation tests、report evidence を commit し、その HEAD から `iss-00254` の branch を開始する。
- G3 に evidence gate を渡すため、draft が authority / reviewer pass / phase completion を自己主張しないことを report に明記する。
