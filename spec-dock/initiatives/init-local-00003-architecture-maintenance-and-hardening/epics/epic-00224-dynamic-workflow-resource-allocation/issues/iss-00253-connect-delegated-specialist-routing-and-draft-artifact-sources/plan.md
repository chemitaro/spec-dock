---
種別: 実装計画書（Issue）
ID: "iss-00253"
タイトル: "Connect Delegated Specialist Routing And Draft Artifact Sources"
Issue Grade: "strict"
状態: "approved"
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

実装は Red -> Green -> preservation -> docs -> final handoff の順に進める。`iss-00253` では個別 PR を作成せず、M99 は `iss-00254` へ渡す local closure checkpoint とする。

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

## 2.1 Spec-Locked Closure Index

| ID | 対象 | Close 条件 | 主な検証 |
|---|---|---|---|
| C-001 | AC-001 | Issue `draft-design` が `authorized_profile` の design profile template を使う | CLI success test |
| C-002 | AC-002 | Issue `draft-plan` が `authorized_profile` の plan profile template を使う | CLI success test |
| C-003 | AC-003 | missing / invalid / stale contract、unsupported profile、missing / non-file / symlink escape / empty profile template が discussion allocation 前に no-write fail-closed する | CLI fail/no-write tests |
| C-004 | AC-004 | `draft-requirement` と Initiative / Epic draft behavior が退行しない | preservation tests |
| C-005 | AC-005 | profile-sourced draft に legacy thin normalization が適用されない | content assertions |
| C-006 | AC-006 | generated draft が authority / reviewer pass / phase completion / implementation readiness を自己主張しない | content assertions |
| C-007 | AC-007 | `assurance compose` profile template behavior が退行しない | compose regression tests |
| C-090 | M90 | docs / rules impact が必要な範囲で更新または no-op 判断される | docs inspection |
| C-095 | M95 | strict reviewer gates が fresh pass する | qa/code/spec review |
| C-099 | M99 | local handoff checkpoint が clean commit になり、個別 PR を作らず次 issue に渡せる | final commands + report |

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
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/artifact_store.py`
- `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/infra/assurance_store.py`
- `tests/cli_runtime/test_new.py`
- `tests/cli_runtime/test_assurance_compose.py`
- `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
- `spec-dock/docs/rules/issue/discussions.md`
- active issue `discussions/rules.md`

## 5. 禁止変更

- canonical issue `design.md` / `plan.md` を `new doc` で更新しない。
- missing assurance で Standard fallback を作らない。
- G1/G3 の guidance / evidence gate をこの Issue に混ぜない。

## 6. Review / commit gate

- success path と fail-closed path は同じ Epic PR 内で閉じる。
- M99 では test command、no-write確認、docs parity を `report.md` に記録する。

## 6.1 実装ステップ / 実行ステップ契約

### S00 Baseline / characterization

- 変更対象: なし。
- 目的: 現行 `new doc draft-*` routing、profile template loader、assurance verifier、既存 tests を確認する。
- close: 現行 Issue draft design/plan が common issue template + thin normalization route であること、`ArtifactStore.load_profile_artifact_template()` と `AssuranceStore.verify_contract()` が再利用可能であることを `report.md` に記録する。

### S01 Profile draft success path

- 変更対象:
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/application/create_node.py`
  - `src/spec_dock/assets/spec_dock/scripts/spec_dock_runtime/cli/bootstrap.py`
  - `tests/cli_runtime/test_new.py`
- Red:
  - Standard / Strict / Critical Issue `draft-design` / `draft-plan` が profile template heading / section を含むことを期待し、現行 common template route で失敗させる。
- Green:
  - Issue design/plan draft だけ profile-aware route に入り、profile template body を render する。
- close: C-001, C-002, C-005, C-006。

### S02 Assurance fail-closed / no-write path

- 変更対象:
  - `create_node.py`
  - `tests/cli_runtime/test_new.py`
  - `assurance_store.py` は narrow helper が必要な場合のみ。
- Red:
  - missing `.assurance.json`、invalid JSON / invalid schema、stale source binding が no-write で失敗することを期待し、現行 success で失敗させる。
- Green:
  - `AssuranceStore.verify_contract()` を discussion filename allocation 前に呼び、valid 以外は non-zero failure にする。
- close: C-003。

### S03 Template validation reuse

- 変更対象:
  - `artifact_store.py` は既存 loader で足りない場合のみ。
  - `tests/cli_runtime/test_new.py`
  - `tests/cli_runtime/test_assurance_compose.py`
- Red:
  - missing / symlink escape / non-file / empty profile template が no-write fail-closed することを期待する。
- Green:
  - `ArtifactStore.load_profile_artifact_template()` を `new doc` route から再利用し、compose regression を維持する。
- close: C-003, C-007。

### S04 Preservation path

- 変更対象:
  - `create_node.py`
  - `tests/cli_runtime/test_new.py`
- Red/Green:
  - Issue `draft-requirement`、Initiative / Epic `draft-design` / `draft-plan`、discussion filename grammar、same-second suffix allocation が既存どおりであることを確認する。
- close: C-004。

### S90 Docs / rules impact

- 変更対象:
  - `src/spec_dock/assets/spec_dock/docs/rules/issue/discussions.md`
  - `spec-dock/docs/rules/issue/discussions.md`
  - active issue `discussions/rules.md`
- 検証:
  - `rg -n "draft-design|draft-plan|templates/issue" src/spec_dock/assets/spec_dock/docs spec-dock/docs`
  - Issue `draft-design` / `draft-plan` が profile-aware source へ変わること、Initiative / Epic と `draft-requirement` は scope canonical source を維持することを docs/rules に反映する。
  - active issue の `discussions/rules.md` は G2 実装中の delegated draft authoring surface として更新対象に含める。
- close: C-090。

### S95 Strict review gate

- 必須 reviewer:
  - `qa-reviewer`
  - `code-reviewer`
  - `spec-reviewer`
- close: C-095。

### S99 Local handoff gate

- 必須コマンド:
  - `uv run pytest tests/cli_runtime/test_new.py tests/cli_runtime/test_assurance_compose.py`
  - `./spec-dock/scripts/spec-dock validate`
  - `git diff --check`
  - `make lint`
- close:
  - `report.md` に Red / Green / no-write / reviewer / commit candidate を記録する。
  - 個別 PR を作成せず、commit 後の HEAD を `iss-00254` の starting point にする。

## 7. Epic branch baton / PR policy

- この Issue では個別 PR を作成しない。
- M99 は `iss-00254` に渡せる local closure checkpoint とする。
- PR Delivery Gate / Merge Preparation Gate はこの Issue では実行せず、G4 完了後の Epic 最終品質ゲートに集約する。
- M99 通過後、draft routing success / fail-closed path、preservation tests、report evidence を commit し、その HEAD から `iss-00254` の branch を開始する。
- G3 に evidence gate を渡すため、draft が authority / reviewer pass / phase completion を自己主張しないことを report に明記する。
